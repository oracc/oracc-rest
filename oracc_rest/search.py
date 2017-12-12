# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


class ESearch:
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

    def _get_results(self, results):
        '''
        Compile list of results.
        '''
        result_list = []
        for glossary_results in results.hits.hits:
            for hit in glossary_results['inner_hits']['entries'].hits:
                result_list.append(hit.summary)
        return result_list

    def run(self, fieldname, word):
        return self._get_results(self._execute(fieldname, word))
