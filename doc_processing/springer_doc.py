#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 15:11:44 2019

@author: thv20
"""

### SpringerDoc, which is a subclass of Doc

from doc_processing.document import *
from datetime import date


class SpringerDoc(Doc):
    def __init__(self, springer_data_record, springer_soup):
        """
        Create a SpringerDoc object, which is a subclass of Doc
        :param springer_data_record: dictionary
        :param springer_soup: BeautifulSoup object
        """
        self.record = springer_data_record
        self.springer_soup = springer_soup

        self.text = ''

        for section in self.springer_soup.find_all('section'):
            for para in section.find_all('p'):
                self.text = self.text + ' '.join(para.get_text(' ', strip=True).split())

        if 'title' in self.record.keys():
            self.title = self.record['title']

        if 'doi' in self.record.keys():
            self.doi = self.record['doi']

        if 'creators' in self.record.keys():
            self.authors = [c['creator'] for c in self.record['creators']]

        if 'publicationName' in self.record.keys():
            self.journal = self.record['publicationName']

        if 'volume' in self.record.keys():
            self.volume = self.record['volume']

        if 'startingPage' in self.record.keys() and 'endingPage' in self.record.keys():
            self.page = self.record['startingPage'] + '-' + self.record['endingPage']

        if 'coverDate' in self.record.keys():
            self.coverDate = self.record['coverDate']

        self.accessDate = str(date.today())

    def is_elsevier(self):
        return False

    def is_springer(self):
        return True
