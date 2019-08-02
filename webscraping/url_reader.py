# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 18:32:27 2019

@author: huong
"""

import requests 
from bs4 import BeautifulSoup
import time
import numpy as np
from elsevier import *
from springer import * 
from chemdataextractor.reader.acs import *
from chemdataextractor.reader.rsc import *
from chemdataextractor.doc.document import *

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'

class URL_reader:
    def __init__ (self):
        pass
    
    def read_url(self, url, headers = {'User-Agent': USER_AGENT} ):
        """
        Input: url as a string
        Output: BeautifulSoup object
        """
        
        response = requests.get(url, headers = headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup
    
    def read_urls(self, urls, sleep=10, no_of_links=10, headers={'User-Agent': USER_AGENT}):
        """
        Input: urls as a dictionary
        Output: dictionary of soups
        """
        
        soups = {}
        for (i, k) in enumerate (urls): 
            for j in np.arange(0, len(urls[k])):
                if j == 0: 
                    soups[k] = []
                soups[k].append(self.read_url(urls[k][j][0], headers=headers))
                time.sleep(sleep)
                if j == no_of_links - 1: 
                    break
                
        return soups
    
    def detect(self, soup):
        '''
        Input: soup is a BeautifulSoup object 
        Output: string with the name of the website
        '''
        
        if '<meta content="https://www.sciencedirect.com' in str(soup): 
            return 'elsevier'
        
        elif '<meta content="https://link.springer.com' in str(soup):
            return 'springer'
        
        elif 'wgroup:string:ACHS website Group' in str(soup): 
            return 'acs' 
        
        elif '<meta content="https://pubs.rsc.org' in str(soup):
            return 'rsc'
        
        else:
            return 'other'
        
    def parse(self, url,headers = {'User-Agent': USER_AGENT}): 
        '''
        Input: soup as a BeautifulSoup object
        Output: Document
        '''
        soup = self.read_url(url, headers = headers)
        
        website = self.detect(soup)
        
        if website == 'elsevier': 
            elsevier = ElsevierHtmlReader()
            return elsevier.parse(str(soup))
            
        if website == 'springer': 
            springer = SpringerMaterialsHtmlReader()
            return springer.parse(str(soup))
            
        if website == 'acs': 
            acs = AcsHtmlReader()
            return acs.parse (str(soup))
        
        if website == 'rsc': 
            rsc = RscHtmlReader()
            return rsc.parse(str(soup))
        
        return Document()
    
    def parse_from_soup(self, soup): 
        website = self.detect(soup)
        
        if website == 'elsevier': 
            elsevier = ElsevierHtmlReader()
            return elsevier.parse(str(soup))
            
        if website == 'springer': 
            springer = SpringerMaterialsHtmlReader()
            return springer.parse(str(soup))
            
        if website == 'acs': 
            acs = AcsHtmlReader()
            return acs.parse (str(soup))
        
        if website == 'rsc': 
            rsc = RscHtmlReader()
            return rsc.parse(str(soup))
        
        return Document()