# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


class ESearch:
    FIELDNAMES = ['headword', 'gw', 'cf']

    def __init__(self):
        self.client = Elasticsearch()

    def _execute(self, fieldname, word):
        '''
        Given a word and an entries fieldname, return all matching entries in
        the local ElasticSearch DB.
        '''
        search = Search(using=self.client,
                        index="oracc").query(
                            "nested",
                            path="entries",
                            inner_hits={},
                            query=Q("match",
                                    **{"entries.{}".format(fieldname): word}))
        results = search.execute()
        return results

    def _execute_general(self, word):
        '''
        Given a word, return all matching entries in the local ElasticSearch DB.
        '''
        # Build the subqueries searching the individual fields for the word
        subqueries = [
            Q("match", **{"entries.{}".format(fieldname): word})
            for fieldname in self.FIELDNAMES
        ]
        # And combine them in a bool query (within a nested query)
        search = Search(using=self.client, index="oracc").query(
                                            "nested",
                                            path="entries",
                                            inner_hits={},
                                            query=Q("bool", should=subqueries)
                                            )
        results = search.execute()
        return results

    def _get_results(self, results):
        '''
        Compile list of results.
        '''
        # Currently returns the summary for each hit
        result_list = []
        for glossary_results in results.hits.hits:
            for hit in glossary_results['inner_hits']['entries'].hits:
                result_list.append(hit.summary)
        return result_list

    def run(self, fieldname, word):
        return self._get_results(self._execute(fieldname, word))

    def run_general(self, word):
        return self._get_results(self._execute_general(word))
