# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


class ESearch:
    FIELDNAMES = ['headword', 'gw', 'cf', 'forms_n', 'norms_n', 'senses_mng']

    def __init__(self):
        self.client = Elasticsearch()

    def _execute(self, word, fieldname):
        '''
        Given a word and a fieldname, return all matching entries in the local
        ElasticSearch DB.
        '''
        search = Search(using=self.client, index="oracc").query(
                                    "match",
                                    **{fieldname: word})
        results = search.scan()
        return results

    def _execute_general(self, word):
        '''
        Given a word, return all matching entries in the local ElasticSearch DB.
        '''
        search = Search(using=self.client, index="oracc").query(
                                            "multi_match",
                                            query=word,
                                            fields=self.FIELDNAMES
                                            )
        results = search.scan()
        return results

    def _get_results(self, results):
        '''
        Get the required information from each result and compile it in a list.

        Currently returns the whole result document.
        '''
        # TODO investigate why some entries don't have certain attributes!
        result_list = [hit.to_dict() for hit in results]
        # This is probably better as a comprehension at the moment,
        # but in the future we might want some more elaborate processing
        # result_list = []
        # for hit in results:
        #    result_list.append({'headword': hit.headword if hasattr(hit, "headword") else None,
        #                        'gw': hit.gw if hasattr(hit, "gw") else None,
        #                        'cf': hit.cf if hasattr(hit, "cf") else None})
        #    result_list.append(hit.to_dict())
        return result_list

    def run(self, word, fieldname=None):
        '''Find matches for the given word (optionally in a specified field).'''
        if fieldname is None:
            return self._get_results(self._execute_general(word))
        else:
            return self._get_results(self._execute(word, fieldname))

    def list_all(self, start=None, count=None):
        '''Get a list of all entries.'''
        search = Search(using=self.client, index="oracc").query("match_all")
        if start is None or count is None:
            results = search.scan()
        else:
            results = search[start:start+count]
        return self._get_results(results)
