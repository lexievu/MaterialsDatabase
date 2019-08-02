#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 10:43:40 2019

ElsevierDoc, which is a subclass of Doc

@author: thv20

To import this file, call

>>> from doc_processing.elsevier_doc import ElsevierDoc
"""

from doc_processing.document import *
from datetime import date


class ElsevierDoc(Doc):
    def __init__(self, elsapy_data):
        """
        Create an ElsevierDoc object, which is a subclass of Doc
        :param elsapy_data: elsapy.Elsentity object
        """
        self.elsapy_data = elsapy_data
        if 'originalText' in self.elsapy_data.keys():
            if type(self.elsapy_data['originalText']) != dict:
                self.text = self.elsapy_data['originalText']
            
        if 'coredata' in self.elsapy_data.keys():
            if 'dc:title' in self.elsapy_data['coredata'].keys():
                self.title = self.elsapy_data['coredata']['dc:title']
                
            if 'prism:doi' in self.elsapy_data['coredata'].keys():
                self.doi = self.elsapy_data['coredata']['prism:doi']
                
            if 'dc:creator' in self.elsapy_data['coredata'].keys():
                if type(self.elsapy_data['coredata']['dc:creator'])  == list:
                    self.authors = [x['$'] for x in self.elsapy_data['coredata']['dc:creator']]
                else: 
                    self.authors = self.elsapy_data['coredata']['dc:creator']['$']
                
            if 'prism:publicationName' in self.elsapy_data['coredata'].keys():
                self.journal = self.elsapy_data['coredata']['prism:publicationName']
                
            if 'prism:volume' in self.elsapy_data['coredata'].keys():
                self.volume = self.elsapy_data['coredata']['prism:volume']
                
            if 'prism:pageRange' in self.elsapy_data['coredata'].keys():
                self.page = self.elsapy_data['coredata']['prism:pageRange']
                
            if 'prism:coverDate' in self.elsapy_data['coredata'].keys():
                self.coverDate = self.elsapy_data['coredata']['prism:coverDate']
        self.accessDate = str(date.today())

    def is_elsevier(self):
        return True

    def is_springer(self):
        return False
