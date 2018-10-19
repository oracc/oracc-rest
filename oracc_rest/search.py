# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


class ESearch:
    FIELDNAMES = ['headword', 'gw', 'cf', 'forms_n', 'norms_n', 'senses_mng']
    TEXT_FIELDS = ['gw']  # fields with text content on which we can sort
    UNICODE_FIELDS = ['cf']  # fields which may contain non-ASCII characters

    def __init__(self):
        self.client = Elasticsearch()

    def _execute(self, word, fieldname):
        """
        Given a word and a fieldname, return all matching entries in the local
        ElasticSearch DB.
        """
        search = Search(using=self.client, index="oracc").query(
                                    "match",
                                    **{fieldname: word})
        # To ensure that each result has a "sort" value (for consistency with
        # the other search modes), we sort by _doc, which is meaningless but
        # efficient, as suggested in the docs:
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-sort.html
        results = search.sort("_doc").scan()
        return results

    def _execute_general(self, word, sort_by="cf", dir="asc",
                         count=None, after=None):
        """
        Given a word, return all matching entries in the local ElasticSearch DB.
        """
        search = (
                Search(using=self.client, index="oracc").query(
                                            "multi_match",
                                            query=word,
                                            fields=self.FIELDNAMES
                                            )
                .sort(self._sort_field_name(sort_by, dir))
                )
        return self._customise_and_run(search, count, after)

    def _get_results(self, results):
        """
        Get the required information from each result and compile it in a list.

        Currently returns the whole result document along with the sort score.
        """
        result_list = [
            # Add a key called "sort" to each hit, containing its sort "score"
            dict(**hit.to_dict(), sort=str(hit.meta.sort))
            for hit in results
        ]
        # This is probably better as a comprehension at the moment,
        # but in the future we might want some more elaborate processing
        # result_list = []
        # for hit in results:
        #    result_list.append({'headword': hit.headword if hasattr(hit, "headword") else None,
        #                        'gw': hit.gw if hasattr(hit, "gw") else None,
        #                        'cf': hit.cf if hasattr(hit, "cf") else None})
        #    result_list.append(hit.to_dict())
        return result_list

    def run(self, word, fieldname=None, **args):
        """Find matches for the given word (optionally in a specified field)."""
        if fieldname is None:
            return self._get_results(self._execute_general(word, **args))
        else:
            return self._get_results(self._execute(word, fieldname))

    def list_all(self, sort_by="cf", dir="asc", count=None, after=None):
        """Get a list of all entries."""
        search = (
                Search(using=self.client, index="oracc")
                .query("match_all")
                # TODO We should maybe sort on a tie-breaker field (eg _id) too...
                .sort(self._sort_field_name(sort_by, dir))
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

    def _sort_field_name(self, field, dir):
        """Build the argument to sort based on a field name and a direction."""
        return "{}{}{}".format(
            # A - indicates descending sorting order in the ElasticSearch DSL
            "-" if dir == 'desc' else "",
            # The base field name
            field,
            # Potentially, a suffix for the field:
            # Text-valued fields cannot be sorted on directly; we must instead
            # sort on the automatically-created X.keyword field. For fields that
            # contain non-ASCII characters, we use the X.sort field instead.
            # TODO Since the suffixes don't change, we can store them in a dict
            # instead of building them every time.
            ".sort" if field in self.UNICODE_FIELDS else (
                ".keyword" if field in self.TEXT_FIELDS else "")
        )
