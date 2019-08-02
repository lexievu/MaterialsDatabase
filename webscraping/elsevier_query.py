#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 09:28:42 2019

Elsevier util functions 

@author: thv20
"""

from elsapy.elsclient import ElsClient
from elsapy.elssearch import ElsSearch
from elsapy.elsdoc import FullDoc
import time 
import os
from urllib.parse import quote


class Elsevier_query:
    els_api_key = None
    
    def __init__(self, query, els_api_key=None,  material=None, num_res=100, local_dir=os.getcwd(),
                 sleep=1, index='sciencedirect'):
        """

        :param query: string: what you want to search for (e.g. 'Curie temperature', 'skyrmion size', etc)
        :param els_api_key: string: Elsevier API key from https://dev.elsevier.com
        :param material: string or None: material names to search for
        :param num_res: int: the number of responses
        :param local_dir: string: if not specified, the default will be the current directory
        :param sleep: float: resting time between accessing files from Elsevier
        :param index: specify the index (e.g. 'sciencedirect','scorpus', etc. see more on https://dev.elsevier.com/

        :return: None

        The result is written in a folder called 'Elsevier soups' in local directory
        """

        if els_api_key is None: 
            raise ValueError('API must be specified. Elservier API key can be obtained from https://dev.elsevier.com/')

        self.els_api_key = els_api_key

        self.client = ElsClient(api_key=self.els_api_key, num_res=num_res,
                                local_dir=local_dir)

        if material is None:
            self.search = ElsSearch(query=quote(query), index=index)
        else:
            self.search = ElsSearch(query=quote(material + ' ' + query), index=index)
        self.search.execute(els_client=self.client)
        
        self.doc = []
        
        if not os.path.exists(os.getcwd() + '/Elsevier soups/' + material + ' ' + query):
            os.makedirs(os.getcwd() + '/Elsevier soups/' + material + ' ' + query)
            print(material)
        
        if 'error' not in self.search.results[0].keys():
            for r in self.search.results: 
                
                self.client.local_dir = 'Elsevier soups/' + material + ' ' + query
                self.doc.append(FullDoc(doi=r['prism:doi']))
    
            for d in self.doc:
                d.read(els_client=self.client)
                time.sleep(sleep)
                d.write()
