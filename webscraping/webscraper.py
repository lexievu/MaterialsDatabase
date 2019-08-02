# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 17:51:51 2019

@author: huong
"""

import re 
import requests 
from bs4 import BeautifulSoup
import numpy as np
import time
from urllib.request import quote
from random import seed
from random import random

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'

class G_scholar_scraper: 
    def __init__ (self): 
        pass
    
    def extract_G_soup(self, url, headers = {'User-Agent': USER_AGENT}):
        '''
        Input: a Google Scholar link
        Output: the HTML file of the Google Scholar link cite as a BeautifulSoup object 
        '''
        response = requests.get(url, headers = headers)
        raw = BeautifulSoup(response.text, 'html.parser')
        
        return raw
    
    def get_titles (self, soup):
        '''
        Input: a BeautifulSoup object
        Output: all the journal titles in Google Scholar website
        '''
        journal_titles = []
        
        for h3 in soup.find_all('h3'):
            journal_titles.append(h3.get_text())
            
        return journal_titles
    
    def get_links (self, soup):
        '''
        Input: a BeautifulSoup object
        Output: a list of links 
        '''
        
        journal_urls = []
        
        for h3 in soup.find_all('h3'): 
            journal_urls.append(h3.a['href'])
        
        return journal_urls
        
    def get_bib (self, soup):
        '''
        Input: a BeautifulSoup object
        Output: a list of citations
        '''
        bibs = []
        for div in soup.find_all('div',{'class': 'gs_a'}):
            bibs.append(div.get_text())
        
        return bibs
    
    def get_all(self, soup): 
        '''
        Input: a BeautifulSoup object
        Output: a list of (link, title, bib info)
        '''
        journal_urls = []
        journal_titles = []
        for h3 in soup.find_all('h3'):
            journal_urls.append(h3.a['href'])
            journal_titles.append(h3.get_text())
        
        bibs = self.get_bib(soup)
        
        return list(zip(list(zip(journal_urls, journal_titles)), bibs))
            
    
    def _extract_G_scholar(self, url, no_of_links = 10): 
        '''
        This function extracts all the links to scientific journals from a Google Scholar link.
        
        Input: url as a string 
        Output: a list of (URLs,citation)
        '''
        response = requests.get(url)
        raw = BeautifulSoup(response.text,'html.parser')
        
        all_a = raw.find_all('a') # This extracts all the a elements in HTML file 
        all_citation = raw.find_all('div', {'class':'gs_a'}) #This extracts all the citations
        
        journal_urls = []
        citations = []
        
        for a in all_a: 
            if 'href="https://' in str(a) and not 'href="https://accounts.google.com' in str(a): 
                m = re.search('https://(.+?)"', str(a))
                journal_urls.append(m.group(0)[:-1])
                
        for c in all_citation: 
            citations.append(c.get_text().replace('\xa0',' '))
        
        if len(journal_urls) > no_of_links:
            return list(zip(journal_urls[:no_of_links-1], citations[:no_of_links-1]))
        
        else: 
            return list(zip(journal_urls, citations))
    
    def gen_G_scholar_url (self, query, curie = 'n', remove_whitespace ='y'): 
        '''
        This function takes a query in form of a string and produce the Google Scholar link
        
        Input: query as a string
        Output: Google Scholar link as a string 
        '''
        if remove_whitespace == 'y': 
            query = ''.join(query.split(' '))
        
        if curie == 'y': 
            query = '"Curie" temperature ' + query
        
        GOOGLE_SCHOLAR_URL = "https://scholar.google.com"
        searchstr = '/scholar?q='+quote(query)
        url = GOOGLE_SCHOLAR_URL + searchstr    
        
        return (url)
    
    def extract_G_scholar(self, compounds, curie = 'n', sleep = 10,return_soup = 'y', headers = {'User-Agent': USER_AGENT}): 
        '''    
        Input: 
                compounds: a list of compounds (list of string)
                curie: string. if curie = 'y', the search term will be 'curie temperature' + compound name
                sleep: int. Time between search.
                return_soup: string. Whether the BeautifulSoup objects are returned
        Output: 
                journal_urls: a dictionary, key being the compound name and items are (journal links, citations)
        '''
        seed(1)
        
        gs_urls = []
        for c in compounds: 
            gs_urls.append(self.gen_G_scholar_url(c, curie))
        
        journal_urls = {}
        journal_soups = {}
        for i in np.arange(0, len(gs_urls)):
            journal_soups[compounds[i]] = self.extract_G_soup(gs_urls[i], headers = headers)
            journal_urls[compounds[i]] = self.get_all(journal_soups[compounds[i]])
            time.sleep(sleep + 2*random()) 
            
        if (return_soup == 'y'): 
            return (journal_urls, journal_soups)
        else: 
            return journal_urls