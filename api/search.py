# -*- coding: utf-8 -*-
import itertools

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search


class ESearch:
    FIELDNAMES = ["gw", "cf", "forms_n", "norms_n", "senses_mng"]
    TEXT_FIELDS = ["gw"]  # fields with text content on which we can sort
    UNICODE_FIELDS = ["cf"]  # fields which may contain non-ASCII characters

    def __init__(self, index_name="oracc"):
        self.client = Elasticsearch()
        self.index = index_name

    def test_connection(self):
        print("test search connection")

    def _execute(self, word, fieldname):
        """
        Given a word and a fieldname, return all matching entries in the local
        ElasticSearch DB.
        """
        search = Search(using=self.client, index=self.index).query(
            "match", **{fieldname: word}
        )
        results = search.scan()
        return results

    def _execute_general(
        self, phrase, sort_by="gw", direction="asc", count=None, after=None
    ):
        """
        Given a phrase of space-separated words, return all matching entries in
        the local ElasticSearch DB.

        This works by forming sub-queries for each of the words in the phrase,
        and then taking the set of all results.
        """
        # Create one subquery for each word. This is necessary because the
        # multi_match query doesn't support prefix-style matching for multiple
        # words, so we need to run multiple queries and combine them.
        # See Issue #17 for more details.
        subqueries = [
            Q("multi_match", query=word, fields=self.FIELDNAMES, type="phrase_prefix")
            for word in phrase.split()
        ]

        # To combine, we pass these subqueries as "must" arguments to a bool
        # query. This essentially gets the intersection of their results.
        search = (
            Search(using=self.client, index=self.index)
            .query(
                "bool",
                must=subqueries,
            )
            .sort(
                self._sort_field_name(sort_by, direction),
            )
        )
        return self._customise_and_run(search, count, after)

    def _get_results(self, results):
        """
        Get the required information from each result and compile it in a list.

        Currently returns the whole result document along with the sort score.

        This method effectively sorts by _score but done this way since we need to be within a search query to use .sort() for ES
        """

        result_list = [
            # Add a key called "sort" to each hit, containing its sort "score"
            dict(
                **hit.to_dict(),
                sort=str(hit.meta.sort),
                instances_count=len(hit.instances),
            )
            for hit in results
        ]
        # this sorts the results by number of hits (after the search has been done)
        sorted_result_list = sorted(
            result_list,
            key=lambda x: (-x["instances_count"],),
        )

        # This is probably better as a comprehension at the moment,
        # but in the future we might want some more elaborate processing
        # result_list = []
        # for hit in results:
        #    result_list.append({'headword': hit.headword if hasattr(hit, "headword") else None,
        #                        'gw': hit.gw if hasattr(hit, "gw") else None,
        #                        'cf': hit.cf if hasattr(hit, "cf") else None})
        #    result_list.append(hit.to_dict())
        return sorted_result_list

    def run(self, word, fieldname=None, **args):
        """Find matches for the given word (optionally in a specified field)."""
        if fieldname is None:
            return self._get_results(self._execute_general(word, **args))
        else:
            return self._get_results(self._execute(word, fieldname))

    def list_all(self, sort_by="gw", direction="asc", count=None, after=None):
        """Get a list of all entries."""
        search = (
            Search(using=self.client, index=self.index)
            .query("match_all")
            .sort(
                self._sort_field_name(sort_by, direction),
            )
        )
        results = self._customise_and_run(search, count, after)
        return self._get_results(results)

    def _customise_and_run(self, search, count, after):
        """
        Execute an ES search appropriately, depending on the specified
        customisation.
        """
        if after is not None:
            search = search.extra(search_after=[after])
            # TODO Should we require count to be given here? Otherwise, the
            # default behaviour below (10 hits) could be surprising.
            if count is not None:  # if not given, we will only retrieve 10 hits
                search = search.params(size=count)
            # ES doesn't allow the scan/scroll API to be used with search_after
            results = search.execute().hits
        elif count is not None:
            # If count is specified, only get that many results
            results = search[0:count]
        else:
            # When scanning, we must explicitly ask to preserve sorting order!
            results = search.params(preserve_order=True).scan()
        return results

    def _sort_field_name(self, field, direction):
        """Build the argument to sort based on a field name and a direction."""
        return "{}{}{}".format(
            # A - indicates descending sorting order in the ElasticSearch DSL
            "-" if direction == "desc" else "",
            # The base field name
            field,
            # Potentially, a suffix for the field:
            # Text-valued fields cannot be sorted on directly; we must instead
            # sort on the automatically-created X.keyword field. For fields that
            # contain non-ASCII characters, we use the X.sort field instead.
            # TODO Since the suffixes don't change, we can store them in a dict
            # instead of building them every time.
            ".sort"
            if field in self.UNICODE_FIELDS
            else (".keyword" if field in self.TEXT_FIELDS else ""),
        )

    def suggest(self, word, size):
        """Get search suggestions matching a given word.

        This will return terms found in the indexed data which are close to the
        query word. This is useful for correcting misspellings.
        Note that this does not return the query word itself, even if it is
        found in the data.
        """
        search = Search(using=self.client, index=self.index)
        # Use one term suggester per searchable field, as we can't have multiple
        # fields in each suggester
        # we currently don't get all but it's unlikely that beyond the first 200 suggestions/completions will be helpful
        for field_name in self.FIELDNAMES:
            search = search.suggest(
                "sug_{}".format(field_name),
                word,
                term={
                    "field": field_name,
                    # so small words match:
                    "min_word_length": 3,
                    "size": size,
                },
            )
        suggestion_results = search.execute().suggest.to_dict().values()
        sorted_suggestions = sorted(
            suggestion_results,
            key=lambda x: (
                x[0]["options"][0]["score"] if x[0]["options"] else 0,
                -x[0]["options"][0]["freq"] if x[0]["options"] else 0,
                len(x[0]["text"]),
            ),
        )

        # The format of the response is a little involved: the results for each
        # suggester are in a list of lists (to account for multiple query terms,
        # even thougth we're not allowing that). Therefore, we need two steps
        # of flattening to get a single results list.
        all_suggestions = [
            option["text"]
            for suggestion in sorted_suggestions
            for option in suggestion[0]["options"]
        ]
        # Remove duplicate results (use a dictionary vs a set to preserve order)
        return list(dict.fromkeys(all_suggestions))

    def complete(self, word, size):
        """Get completions for a given word.

        This will return terms and guidewords found in the indexed data which are completions
        of the query. This is useful for finding a range of results from limited input.
        Note that this does not return the query itself, even if it is
        found in the data.
        """
        search = Search(using=self.client, index=self.index)
        search = search.suggest(
            "sug_complete",
            word,
            completion={
                "field": "completions",
                "skip_duplicates": True,
                "size": size,
            },
        )
        completion_results = search.execute().suggest.to_dict()["sug_complete"]

        sorted_results = sorted(
            completion_results[0]["options"],
            key=lambda x: (
                x["_score"],
                len(x["text"]),
                -len(x["_source"].get("instances", [])),
            ),
        )

        all_completions = [option["text"] for option in sorted_results]

        return all_completions
