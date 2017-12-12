# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


class ESearch:
    FIELDNAMES = ['headword', 'gw', 'cf', 'forms.n', 'norms.n', 'senses.mng']
    NESTED_FIELDS = ["entries.{}".format(field) for field in FIELDNAMES]

    def __init__(self):
        self.client = Elasticsearch()

    def _execute(self, word, fieldname):
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
        search = Search(using=self.client, index="oracc").query(
                                            "nested",
                                            path="entries",
                                            inner_hits={},
                                            query=Q("multi_match",
                                                    query=word,
                                                    fields=self.NESTED_FIELDS)
                                            )
        results = search.execute()
        return results

    def _get_results(self, results):
        '''
        Compile list of the headword, guideword and cuniform for each result.
        '''
        result_list = []
        for glossary_results in results.hits.hits:
            for hit in glossary_results['inner_hits']['entries'].hits:
                result_list.append({'headword': hit.headword,
                                    'gw': hit.gw,
                                    'cf': hit.cf})
        return result_list

    def run(self, word, fieldname=None):
        '''Find matches for the given word (optionally in a specified field).'''
        if fieldname is None:
            return self._get_results(self._execute_general(word))
        else:
            return self._get_results(self._execute(word, fieldname))
