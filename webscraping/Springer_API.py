#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 15:21:06 2019

@author: thv20
"""

import requests
import json
from urllib.request import quote 
import pathlib
from elsapy import log_util
import urllib
import datetime
import os
import time
from bs4 import BeautifulSoup

logname = 'springer' + str(datetime.date.today())

logger = log_util.get_logger(logname)

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'


class Springer_API: 
    base_url = 'http://api.springernature.com/'
    data = None 
    soups = None
    
    def __init__ (self, local_dir = None):
        self.local_dir = pathlib.Path(local_dir)
    
    def gen_query(self, q, s = 1, p = 50): 
        '''
        Input allowed: https://dev.springernature.com/adding-constraints
                    p is the number of results returned
        Return: string
        '''    
        self.query = 'q=' + quote(q) + '&s=' + quote(str(s)) + '&p=' + quote(str(p))
        return self.query
    
    def gen_link(self, api_key=None, collection = 'metadata', resultformat = 'json'):
        '''
        Input: https://dev.springernature.com/restfuloperations
        Return: String
        '''
        if api_key is None: 
            raise ValueError('API must be specified. Springer API key can be obtained from https://dev.springernature.com/. You would need to sign up/sign in, then click on Applications on the top panel.')

        self.api_key = api_key
        restful = collection + '/' + resultformat +'?'
        self.url = self.base_url + restful + self.query + '&api_key=' + self.api_key
        return self.url
    
    def load (self):
        '''
        Input: none 
        Return: the json of the url
            If there was an error, the function would return False. 
        '''
        if not os.path.exists('SpringerNature_query'):
            os.makedirs('SpringerNature_query')
        
        try: 
            res = requests.get(self.url)
            res_json = json.loads(res.text)
            
            self.data = res_json
            
            logger.info ("Data loaded for " + self.url)
            
            with open(os.path.join('SpringerNature_query', self.data['query'] + '.json'), 'w') as f:
                json.dump(res_json, f, indent = 5)
                
            return res_json
        except (requests.HTTPError, requests.RequestException) as e:
            for elm in e.args:
                logger.warning(elm)
            return False
    
    def local_dir(self, path_str):
        """
        Set the local path to write data to
        Input: string
        Output: none
        """
        self.local_dir = pathlib.Path(path_str)
    
    def write (self, sort_keys = True, indent = 5): 
        '''
        Input: none
        If data exists for the entity, writes it to disk as a .JSON file 
            with the url-encoded URI as the filename and returns True. Else, returns
            False. 
        '''
        
        if self.data != None: 
            dataPath = self.local_dir / (urllib.parse.quote_plus(self.url)+'.json')
            with dataPath.open(mode='w') as dump_file:
                json.dump(self.data, dump_file, sort_keys = sort_keys, indent = indent)
                dump_file.close()
            logger.info('Wrote ' + self.url + ' to file')
            return True
        else: 
            logger.warning('No data to write for ' + self.uri)
            return False
        
    def get_link_to_text(self, write = True): 
        if not os.path.exists('SpringerNature_links'):
            os.makedirs('SpringerNature_links')
        
        link = []
        for r in self.data['records']:
            link.append(r['url'][0]['value'])
        
        if write == True: 
            with open(os.path.join('SpringerNature_links', urllib.parse.quote_plus(self.query) + '.txt'), 'w') as file:
                for l in link: 
                    file.write("%s \n" %l)    
            
        return link
        
    def get_full_text(self, write = True, sleep = 1):
        '''
        Input: write(bool): whether to save BeautifulSoup object to a text file
              sleep (int): seconds of break between calls 
        Output: the responses collected. The responses are written into text file 
        '''
        
        self.responses = {}
        
        for r in self.data['records']:
            self.responses[r['identifier']] = requests.get(r['url'][0]['value'], headers = {'User-agent': USER_AGENT})
            time.sleep(sleep)
            
        self.soups = {}
        
        for k in self.responses.keys():
            self.soups[k] = BeautifulSoup(self.responses[k].text, 'html.parser')
            if write == True: 
                if not os.path.exists(os.path.join('SpringerNature_soups', self.data['query'])):
                    os.makedirs(os.path.join('SpringerNature_soups', self.data['query']))
                with open(os.path.join('SpringerNature_soups', self.data['query'], urllib.parse.quote_plus(k) + '.txt'), 'w', encoding='utf-8') as f:
                    f.write(self.soups[k].prettify())
            
        return self.responses
    
    def write_soups(self): 
        '''
        output: none
        Soups are written to text file
        '''
        if self.soups == None: 
            return False
        else: 
            for k in self.soups.keys():
                self.soups[k] = BeautifulSoup(self.responses[k].text, 'html.parser')
                if write == True: 
                    if not os.path.exists(os.path.join('SpringerNature_soups', self.data['query'])):
                        os.makedirs(os.path.join('SpringerNature_soups', self.data['query']))
                    with open(os.path.join('SpringerNature_soups', self.data['query'], urllib.parse.quote_plus(k) + '.txt'), 'w', encoding='utf-8') as f:
                        f.write(self.soups[k].prettify())
            return True
            
    def gen_citation(self, number): 
        '''
        Generate citations for an article 
        '''
        
        result = []
        if self.data['records'][number]['title']:
            result.append(self.data['records'][number]['title'])
        else: 
            result.append('')
            
        if self.data['records'][number]['doi']:
            result.append(self.data['records'][number]['doi'])
        else: 
            result.append('')
            
        if self.data['records'][number]['creators']:
            result.append([c['creator'] for c in self.data['records'][number]['creators']])
        else: 
            result.append('')
            
        if self.data['records'][number]['publicationName']: 
            result.append(self.data['records'][number]['publicationName'])
        else: 
            result.append('')
            
        if self.data['records'][number]['volume']:
            result.append(self.data['records'][number]['volume'])
        else: 
            result.append('')
            
        if self.data['records'][number]['startingPage'] and self.data['records'][number]['endingPage']:
            result.append(self.data['records'][number]['startingPage'] + '-' + self.data['records'][number]['endingPage'])
        else: 
            result.append('')
        
        if self.data['records'][number]['coverDate']:
            result.append(self.data['records'][number]['coverDate'])
        else: 
            result.append('')
            
        result.append(str(datetime.date.today()))
        
        return result 