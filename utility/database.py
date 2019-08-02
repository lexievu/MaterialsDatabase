#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 16:28:28 2019

@author: thv20
"""

import pandas as pd
import re


class Database_reader:
    '''
    Class specific to reading 'materials.csv'
    materials.csv is a file containing non-centrosymmetric compounds structural information
    '''

    def __init__(self, file_name='materials.csv', *args, **kwargs):
        """
        *args and **kwargs are specific to pd.read_csv function
        :return: None

        Example of usage:

        >>> database = Database_reader('materials.csv')
        """

        self.database = pd.read_csv(file_name, *args, **kwargs)
        for c in self.database.columns:
            if 'Unnamed:' in c:
                self.database = self.database.drop(columns=c)

    @property
    def get(self):
        """
        Getting the full database
        :return: pandas dataframe

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.get

        Out: Point group  ...  Structural measurement temperature/K
        0           1  ...                                   100

        [1 rows x 11 columns]
        """
        return self.database

    @property
    def get_columns(self):
        """
        :return: The names of the columns

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.get_columns
        Out: Index(['Point group', 'SG #', 'Space Group', 'Compound', 'Magnet in Title',
           'Magnet in Journal', 'Magnet in Title or Journal?',
           'Skyrmions? Bloch/Neel/Anti/None/Unknown', 'Structural Paper Title',
           'Reference', 'Structural measurement temperature/K'],
            dtype='object')
        """
        return self.database.columns

    @property
    def get_compounds(self):
        """
        Return the list of compounds that are non-centrosymmetric
        :return: list of compound names

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.get_compounds[:1]
        Out: ['(Pr0.33 Mn0.67)']
        """
        return list(set(self.database['Compound'].tolist()))

    def find_articles(self, compounds):
        """
        Find structural articles for a given compound name
        :input: compounds (list of str)
        :rtype: dictionary of articles, with keys being the compound names

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.find_articles(['Fe Ge'])

        Out: {'Fe Ge': [[1744,
               'Magnetic structures of cubic Fe Ge studied by small-angle neutron scatttering',
               'Journal of Physics: Condensed Matter (1989) 1, (*) p6105-p6122'],
              [1751,
               'Magnetic properties of Cr1-x Fex Ge',
               'Journal of the Physical Society of Japan (1983) 52, (9) p3163-p3169']]}

        """

        result = {}

        for compound in compounds:
            result[compound] = []
            indexs = self.database['Compound'].index[self.database['Compound'] == compound].tolist()
            for index in indexs:
                result[compound].append([index, self.database['Structural Paper Title'][index],
                                  self.database['Reference'][index]])

        return result

    def contain(self, elements, relation='and'):
        """
        Return a list of compounds in database that contain the elements
        relation can be specified as 'and' or 'or'

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.contain (['Fe', 'Ge', 'Si'])
        Out: ['Mn Fe (P0.63 Si0.26 Ge0.11)',
             'Mn Fe (P0.749 Si0.141 Ge0.11)',
             'Mn Fe (P0.671 Si0.219 Ge0.11)',
             'Mn Fe (P0.71 Si0.18 Ge0.11)']
        """
        all_c = self.get_compounds
        if relation == 'and':
            return [c for c in all_c if all(cs in c for cs in elements)]
        elif relation == 'or':
            return [c for c in all_c if any(cs in c for cs in elements)]
        else:
            raise ValueError('relation should only be either \'and\' or \'or\'.')

    def elements_no(self, number=2):
        """
        Input: number of elements
        :return: list of materials with the corresponding number of elements

        Example:
        >>> database = Database_reader('materials.csv')
        >>> database.elements_no(8)
        Out: ['(Rb0.19 Ba0.3 Mn1.1) (Fe (C N)6) (H2 O)0.48',
             'H2 (Si W10.125 Mo1.875 O40) (Cu ((C H3)2 N C H O)3 (H2 O))2 (H2 O)6',
             'K9 ((C H3)2 N H2)8 (Fe6 W30 (Si O4)3 O96 (O H)9 (H3 C C O O)2 (H2 O)2) (H2 O)39',
             'K (Fe1.04 Li0.96) (Si0.4 Al1.6) Si3 O10 (O H)0.46 F1.54']
        """

        return [m for m in self.get_compounds if len(set(re.findall('[A-Z][a-z]?', m))) == number]

    def get_spacegroup(self, compounds):
        """
        Function to get the space groups of a list of compounds

        :param compounds:
        :return: dictionary with keys being the chemical formula and the values
                is (name of space group, space group number)

        Example:
        >>> database.get_spacegroup(['Fe Ge', 'Mn Si'])
        Out: {'Fe Ge': ('P 21 3', 198), 'Mn Si': ('P 21 3', 198)}
        """
        result = {}
        for c in compounds:
            #c = ' '.join(re.findall('[A-Z][^A-Z]*', c))
            result[c] = (list(self.get[self.get.Compound == c]['Space Group'].items())[0][1],
                          list(self.get[self.get.Compound == c]['SG #'].items())[0][1])

        return result
