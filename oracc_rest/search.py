# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


class ESearch:
    FIELDNAMES = ['headword', 'gw', 'cf', 'forms_n', 'norms_n', 'senses_mng']

    def __init__(self):
        self.client = Elasticsearch()

    def _execute(self, word, fieldname):
        '''
        Given a word and an entries fieldname, return all matching entries in
        the local ElasticSearch DB.

        Currently returns at most 10(?) hits.
        '''
        search = Search(using=self.client, index="oracc").query(
                                    "match",
                                    **{"entries.{}".format(fieldname): word})
        results = search.execute()
        return results

    def _execute_general(self, word):
        '''
        Given a word, return all matching entries in the local ElasticSearch DB.

        Currently returns at most 100 hits.
        '''
        search = Search(using=self.client, index="oracc").query(
                                            "multi_match",
                                            query=word,
                                            fields=self.FIELDNAMES
                                            )
        results = search[:100].execute()
        return results

    def _get_results(self, results):
        '''
        Compile list of the headword, guideword and cuniform for each result.
        '''
        result_list = []
        for hit in results:
            # TODO investigate why some entries don't have certain attributes
            result_list.append({'headword': hit.headword if hasattr(hit, "headword") else None,
                                'gw': hit.gw if hasattr(hit, "gw") else None,
                                'cf': hit.cf if hasattr(hit, "cf") else None})
        return result_list

    def run(self, word, fieldname=None):
        '''Find matches for the given word (optionally in a specified field).'''
        if fieldname is None:
            return self._get_results(self._execute_general(word))
        else:
            return self._get_results(self._execute(word, fieldname))

    def list_all(self):
        '''Get a list of all entries.

        Currently returns at most 100 hits.'''
        search = Search(using=self.client, index="oracc").query("match_all")
        results = search[:100].execute()
        return self._get_results(results)
