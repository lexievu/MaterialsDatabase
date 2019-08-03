#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 17:12:52 2019

@author: thv20

To import function in file
>>> import doc_processing.chemicals as ch
>>> ch.find_chemical('MnSi orders below T c =29.6K [11] helimagnetically.')
Out: ['MnSi']
"""

import collections
import csv
import os
import re

import numpy as np
import pandas as pd
from mat2vec.processing.process import MaterialsTextProcessor
from pymatgen.core.composition import Composition

# The following units are not accepted as chemical formulae
NOT_CHEMICALS = ["K", "h", "V", "wt", "wt.", "MHz", "kHz", "GHz", "Hz", "days", "weeks",
                 "T", "MPa", "GPa", "N", "A", "kOe", "Oe", "h.", "mWcm−2", "keV", "MeV", "meV",
                 "mAcm−2", "mA", "mK", "mT", "s-1", "dB",
                 "Ag-1", "mAg-1", "mAg−1", "mAg", "mAh", "mAhg−1", "m-2", "mJ", "kJ",
                 "m2g−1", "THz", "KHz", "kJmol−1", "Torr", "gL-1", "Vcm−1", "mVs−1",
                 "J", "GJ", "mTorr", "bar", "cm2", "mbar", "kbar", "mmol", "mol", "molL−1",
                 "MΩ", "Ω", "kΩ", "mΩ", "mgL−1", "moldm−3", "m2", "m3", "cm-1", "cm",
                 "Scm−1", "Acm−1", "eV−1cm−2", "cm-2", "sccm", "cm−2eV−1", "cm−3eV−1",
                 "kA", "s−1", "emu", "L", "cmHz1", "gmol−1", "kVcm−1", "MPam1",
                 "cm2V−1s−1", "Acm−2", "cm−2s−1", "MV", "ionscm−2", "Jcm−2", "ncm−2",
                 "Jcm−2", "Wcm−2", "GWcm−2", "Acm−2K−2", "gcm−3", "cm3g−1", "mgl−1",
                 "mgml−1", "mgcm−2", "mΩcm", "cm−2s−1", "cm−2", "ions", "moll−1",
                 "nmol", "psi", "mol·L−1", "Jkg−1K−1", "km", "Wm−2", "mass", "mmHg",
                 "mmmin−1", "GeV", "m−2", "m−2s−1", "Kmin−1", "gL−1", "ng", "hr", "w",
                 "mN", "kN", "Mrad", "rad", "arcsec", "Ag−1", "dpa", "cdm−2",
                 "mHz", "mL", "ML", "mlmin−1", "MWm−2",
                 "Wm−1K−1", "Wm−1K−1", "kWh", "Wkg−1", "Jm−3", "m-3", "gl−1", "A−1",
                 "Ks−1", "mgdm−3", "mms−1", "ks", "appm", "ºC", "HV", "kDa", "Da", "kG",
                 "kGy", "MGy", "Gy", "mGy", "Gbps", "μB", "μL", "μF", "nF", "pF", "mF",
                 "A", "Å", "A˚", "μgL−1", "MGOe", "AMFs", "TC", "Tc", "TN", "Tn"]

ELEMENTS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K",
            "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
            "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
            "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
            "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr",
            "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf",
            "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og", "Uue"]


def find_chemical(text, sorted_dict=False):
    """
    :param: text (str)
    :param: sorted_dict: whether or not the result is returned as a sorted dictionary (sort by frequency)
                    if sorted_dict = 'n' then the result is return as an unsorted list
    :return: list of chemicals (str)

    Limitations: Chemical must contain 2 or more elements.
        One of the elements must contain a lower-case letter (e.g. Fe, Si, etc.)

    These limitations are acceptable for the materials that we care about, but this function is
    definitely not general.

    Example:
    >>> from doc_processing.chemicals import find_chemical
    >>> find_chemical('MnSi orders below T c =29.6K [11] helimagnetically.')
    Out: ['MnSi']

    >>> find_chemical('Very recently Mn0.75Fe0.25Si (which is higher than the critical concentration '
                      'xcr =0.19 for Fe in MnSi to give T c =0K) has been studied in the light of '
                      'spin fluctuations assisted QPT.')
    Out: ['Mn0.75Fe0.25Si', 'Fe', 'MnSi']

    >>> find_chemical('Si addition decreases Tc by 17K) to that of Tc from 320K for x=0 to 318K '
                      'for x=1 of Mn4FeGe3-x Si x in Ref.')
    Out: ['Si', 'Mn4FeGe3-xSix']

    >>> find_chemical(' Mn. Mn. Mn. MnSi ', sorted_dict=True)
    Out: OrderedDict([('MnSi', 1), ('Mn', 3)])
    """
    assert type(text) == str, "Input (parameter text) must be of string type."

    # The bit of code below try to match to chemicals written in the form Cu 2 OSeO 3

    temp = [x for x in re.findall('[ ]?[(]?[A-Z][a-z()]*[ ]?|'
                                  '(?:\d+[.]?\d*[)]?|[-+]?[xy])', text)
            if not re.search('[a-z]{2}', x)]

    beg = 0
    position = 0  # where the previous word ends
    temp2 = []  # Eliminates phrases that are either not a chemical element or not a part of a bigger phrase

    for i in range(len(temp)):
        # If the phrase is found where the previous phrase ends, then add that phrase to the end of the previous phrase
        if text.find(temp[i], beg) == position and position != 0:
            if i > 0 and len(temp2) > 0:  # and not (re.search('\d',temp[i-1]) and re.search('\d', temp[i])):
                temp2[-1] = (temp2[-1] + temp[i])
                beg = beg + len(temp[i])
                position = beg

        # If the phrase ends where the next phrase starts, then add the phrase to temp2
        elif (i != len(temp) - 1) and (text.find(temp[i], beg) + len(temp[i]) == text.find(temp[i + 1], beg)) \
                and not re.search('\d', temp[i]):

            temp2.append(temp[i])
            beg = text.find(temp[i + 1], beg)  # + len(temp[i+1])
            position = beg

        # If the phrase is a chemical element, add it to temp2
        elif any(el for el in ELEMENTS if re.findall('(?:\A|\W)' + el + '(?:\W|\Z)', temp[i])) and temp[
            i] not in NOT_CHEMICALS:
            temp2.append(temp[i])
            beg = text.find(temp[i], beg) + len(temp[i])

        # Otherwise, if the phrase is found but does not meet any of the other requirements
        elif text.find(temp[i], beg) != -1:
            beg = text.find(temp[i], beg) + len(temp[i])

    # Cleaning up phrases to get relevant results
    temp3 = []

    for i, t in enumerate(temp2):

        # 1. If a closing bracket is not followed by a number, then split the inside and outside of bracket
        #    then save the part that is a chemical formula
        if ')' in t and '(' in t:
            if not re.search('[(][A-Za-z0-9.]+[)]\d', t):
                for part in t.split('('):
                    if re.search('[A-Z][a-z]', part):
                        temp2[i] = part
                        t = part

        # 2. If the phrase starts with a number, then it is not a chemical formula
        if re.findall('\A\d', ''.join(re.findall('[A-Za-z0-9.()]', temp2[i]))):
            continue

        # 3. If the phrase begins with a lowercase x or y, then remove this x or y (due to matching for x or y in
        #                                                                           subscript)
        if re.findall('\A[xy]', ''.join(temp2[i].split())):
            temp2[i] = temp2[i][1:]

        # 4. If the phrase does not contain an element symbol with an uppercase and a lowercase letter,
        #    then ignore it
        if not re.search('[A-Z][a-z]', t):
            continue

        if ')' in t and '(' not in t:
            temp2[i] = temp2[i].replace(')', '')
        if t[0] == '.':
            temp2[i] = t[1:]
        if t[-1] == '.':
            temp2[i] = t[:-1]
        if '(' in t and ')' not in t:
            temp2[i] = temp2[i].replace('(', '')

        if ''.join(re.findall('[A-Za-z0-9.()-+]', temp2[i])) not in NOT_CHEMICALS:
            temp3.append(''.join(temp2[i].split()))

    result = temp3

    if sorted_dict:
        counter = collections.Counter(result)
        sorted_counter = sorted(counter.items(), key=lambda kv: kv[1])
        sorted_dict = collections.OrderedDict(sorted_counter)
        return sorted_dict
    else:
        return result


def find_overlap(text, list_1, list_2):
    """
    A function written to help with find_chemicals - No longer in use
    It returns the elements in list_1 that does not overlap with the elements in list 2
    :param text: string:
    :param list_1:
    :param list_2:
    :return:
    """
    result = list_1
    for a2 in list_2:
        beg = 0
        for a1 in list_1:
            start1, end1 = text.find(a1, beg), text.find(a1, beg) + len(a1)
            start2, end2 = text.find(a2, beg), text.find(a2, beg) + len(a2)

            beg = start1

            if start1 >= start2 and end1 <= end2:
                result.remove(a1)
                continue
    return result


def write_chemical_latex(chemical):
    result = ''
    chemical = chemical.replace(' ', '')
    # Break the chemical into phrases where each phrase contain one single element
    for phrase in re.findall('[A-Z][^A-Z]*', chemical):
        if len(re.findall('\d+[.]?\d*', phrase)) > 0:
            phrase = re.findall('\D+', phrase)[0] + '$_{' \
                     + re.findall('\d+[.]?\d*', phrase)[0] + '}$'
        result = result + phrase
    if chemical[-1] == ')':
        result = result + ')'
    return result


class Material:
    def __init__(self, name):
        self.dict_repr = Composition(name).get_el_amt_dict()
        self.normalized = MaterialsTextProcessor().normalized_formula(name)
        self.curie_T = []

        if not os.path.exists(os.path.join('Materials', self.write_chemical())):
            os.makedirs(os.path.join('Materials', self.write_chemical()))

        if os.path.exists(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv')):
            self.load_Curie_T()

        # TODO: Write a function to collect the mentions of magnetic domain in material
        ### VALUE = number of times mentioned to have a certain magnetic domain
        self.antiferromagnet = None
        self.ferromagnet = None
        self.ferrimagnet = None

    def isequal(self, name):
        if self.normalized == MaterialsTextProcessor().normalized_formula(name):
            return True
        else:
            return False

    def add_Curie_T_mentions(self, curie_mention):
        """
        curie_mention is in the form of [get_number(t), s,self.title, self.doi, self.authors, \
                                         self.journal, self.volume, self.page,self.coverDate,\
                                         self.accessDate]
        """
        self.curie_T.append(curie_mention)
        return True

    def mean_Curie_T(self):
        all_T = [t[0] for t in self.curie_T]
        self.curie_T_mean, self.curie_T_ste = (np.mean(all_T), np.std(all_T) / np.sqrt(len(all_T)))
        return self.curie_T_mean, self.curie_T_ste

    def write_chemical(self):
        result = ''
        for k in self.dict_repr.keys():
            result = result + k + self.dict_repr[k]
        return result

    def write_Curie_T(self):
        """
        Write to file in current_dir/Materials/__name__/curie_temperature.csv
        """

        columns = ['Compound', 'Extracted Temperature (K)', 'Sentence', 'Title',
                   'DOI', 'Author(s)', 'Journal', 'Volume', 'Page',
                   'Cover Date', 'Access Date']

        # if not os.path.exists(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv'))  #Curie
        # Temperature/'+ filename):

        ### OVERWRITE EXISTING FILE 
        with open(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv'), 'w') as f:
            write = csv.writer(f)
            write.writerow(columns)

        for curie_mention in self.curie_T:
            write_out = self.write_chemical() + curie_mention

            with open(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv'), 'a') as f:
                writeo = csv.writer(f)
                writeo.writerow(write_out)

    def load_Curie_T(self):
        if os.path.exists(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv')):
            database = pd.read_csv(os.path.join('Materials', self.write_chemical(), 'curie_temperature.csv'))
            self.curie_T = database.values.tolist()
            return True
        else:
            return False
