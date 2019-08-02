# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 17:39:15 2019

@author: huong
"""

import nltk  # natural language processing toolkits
import temperature as tmp
import datetime
import chemicals as chem
import skyrmion_size as sks
from abc import ABC, abstractmethod
import csv
import os
import re

SPLIT_UNITS = ["K", "h", "V", "wt", "wt.", "MHz", "kHz", "GHz", "Hz", "days", "weeks",
               "hours", "minutes", "seconds", "T", "MPa", "GPa", "at.", "mol.",
               "at", "m", "N", "s-1", "vol.", "vol", "eV", "A", "atm", "bar",
               "kOe", "Oe", "h.", "mWcm−2", "keV", "MeV", "meV", "day", "week", "hour",
               "minute", "month", "months", "year", "cycles", "years", "fs", "ns",
               "ps", "rpm", "g", "mg", "mAcm−2", "mA", "mK", "mT", "s-1", "dB",
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
               "cd", "mcd", "mHz", "m−3", "ppm", "phr", "mL", "ML", "mlmin−1", "MWm−2",
               "Wm−1K−1", "Wm−1K−1", "kWh", "Wkg−1", "Jm−3", "m-3", "gl−1", "A−1",
               "Ks−1", "mgdm−3", "mms−1", "ks", "appm", "ºC", "HV", "kDa", "Da", "kG",
               "kGy", "MGy", "Gy", "mGy", "Gbps", "μB", "μL", "μF", "nF", "pF", "mF",
               "A", "Å", "A˚", "μgL−1", "MGOe", "AMFs"]


class Doc:
    """
    This is a general document class for analysing a single article.
    Potential development:
        - Include language modelling
        - More natural language processing
    """

    # Generate file information
    text = None
    title = None
    doi = None
    authors = None
    journal = None
    volume = None
    page = None
    coverDate = None
    accessDate = None

    def __init__(self):
        """
        Subclass: ElsevierDoc and SpringerDoc

        The file is initialised by initialising ElsevierDoc and SpringerDoc objects
        ElservierDoc is in file elsevier_doc.py
        SpringerDoc is in file springer_doc.py

        """
        pass

    # TODO: Understand how abstract code work such that when Doc is called, subclass document will be called
    # @abstractmethod
    # def isElsevier(self):
    #    pass

    # @abstractmethod
    # def isSpringer(self):
    #    pass

    def add_text(self, text):
        self.text = text

    @property
    def get_text(self):
        """
        :return: Text of the document

        Example:
        >>> els_doc = ElsevierDoc(els_data)
        >>> els_doc.get_text
        """
        return self.text

    def ie_preprocess(self, text=None, sentence_segmentation='y', tokenization='y', pos_tagging='y'):
        '''
        Function perform 3 functions: 
            1, Sentence segmentation
            2, Tokenization 
            3, Part-of-speech tagging

        Example:
        >>> els_doc = ElsevierDoc(els_data)
        >>> els_doc.ie_preprocess()
        '''
        if text is None:
            text = self.text
        if sentence_segmentation == 'y':
            sentences = nltk.sent_tokenize(text)
            if tokenization == 'y':
                sentences = [nltk.word_tokenize(s) for s in sentences]
                if pos_tagging == 'y':
                    sentences = [nltk.pos_tag(s) for s in sentences]
            return sentences
        else:
            return self.text

    def find_sentences(self, keywords, material=None, text=None, quantitative=True, material_in_sentence=True):
        """
        Purpose: To find sentences in text that contain one of the relevant keywords
        :param text: string or None. The text from which relevant sentences are found
        :param keywords: list of strings. The keywords to be found from the sentences
                        If a keyword contain the phrase AND (e.g. "skyrmion AND size",
                        then both keys must be found in the same sentence
        :param material: string. Name of materials.
                        If material is specified, only accept sentences with the exactly materials mentioned
                        If not specified, material is set to None
        :param quantitative: str. Whether or not what we're looking for is a quantitative value
                        If not specified, quantitative is set to 'y'
        :return: list of relevant sentences (list of strings)

        #TODO: if 'AND' not in k for k in keywords
        #TODO: if 'NOT' in k for k in keywords
        """
        if text is None:
            text = self.text
        sentences = nltk.sent_tokenize(text)
        result = []

        # TODO: Optimize this somehow. for loops are pretty inefficient and I'm using two of them
        for k in keywords:
            # if 'AND' in k:
            keys = re.split('[ ]?AND[ ]?', k)
            if material is not None:
                # TODO: Accept equivalent material names
                keys.append(material)
            for sent in sentences:
                # If we are not looking for a quantity, then remove the requirement for re.search('\d', sent)
                if quantitative:
                    if len(sent) < 1500 and all(word in sent for word in keys) and re.search('\d', sent):
                        # for s in re.findall('.*?[K]{1}\W', sent):
                        if material_in_sentence:
                            if self.find_chemical(sent):
                                result.append(sent)
                        else:
                            result.append(sent)
                else:
                    if len(sent) < 1500 and all(word in sent for word in keys):
                        # for s in re.findall('.*?[K]{1}\W', sent):
                        if material_in_sentence:
                            if self.find_chemical(sent):
                                result.append(sent)
                        else:
                            result.append(sent)

                    ### Maybe we should remove the sentence from sentences if it has already been appended to result

        return result

    def get_curie_temperatures(self, material=None, filename=None, exclude_thinfilm='y',
                               keywords=None, write='y', rewrite='n', text=None, material_in_sentence=True):
        """

        :param material: None or str type, the name of the materials to extract temperature from
                        If not specified, material is set to None
        :param filename: None of str type, the name of the file to write the results to
                        If not specified, filename is set to None
        :param exclude_thinfilm: str type, whether or not we should exclude mentions of thin films
                        If not specified, the variable is set to 'y' (in which case, thin film mentions would be excluded
        :param keywords: The list of keywords that are used to search for Curie temperature
                        If not specified, the keywords variable is set to None.
                        This will then be initialized in the code as ['Tc', 'T_c', 'T c', 'TC', 'T_C',
                                                    'T C', 'Curie temperature', 'transition temperature AND ferromagnet',
                                                    'ferromagnetic order', 'FM order']
        :param write: str type, whether or not the result should be written out to a .csv file
                    If not specified, write is 'y'
        :param rewrite: str type, whether or not the .csv file should be re-written
                        (if re-written, then old data will be deleted)
                        If not specified, rewrite is 'n'
        :param text: None or str type, the text from which Curie temperatures are extracted from
                    If text is None, then we will look for Curie temperature from self.text
                    If not specified, text is set to None.
        :return: dictionary: keys are the compound formulae,
                            values are a list containing the temperature, sentence and citation
        """

        if keywords is None:
            keywords = ['Tc', 'T_c', 'T c', 'TC', 'T_C', 'T C', 'Curie temperature',
             'transition temperature AND ferromagnet', ' ferromagnetic order', ' FM order']

        # TODO: Specify whether or not the file should be rewrite (as requested by variable rewrite
        if text is None:
            text = self.text

        if type(text) != str:
            # If the text given is not a string, then return an empty list
            return []
        else:
            # If material is not mentioned in the article,
            # then replace the material with the most common materials in article
            chemicals = self.find_chemical(text=text)
            if material is None or (material not in chemicals and material not in self.title):
                if chemicals:
                    material = max(set(chemicals), key=chemicals.count)

            # TODO: Specify whether or not material name must be present in sentence
            sentences = []
            # Relevant sentences are found
            sentences = self.find_sentences(keywords=keywords, text=text, material_in_sentence=material_in_sentence)  # , material)

            # If it's an Elsevier file, remove the weird long sentence at the start
            if self.isElsevier():
                # isElsevier is defined in ElsevierDoc (in elsevier_doc.py file)
                sentences = [s for s in sentences if len(s) < 1100]

            if write == 'y':
                if filename is None:
                    filename = 'Curie_temperature_records' + str(datetime.date.today()) + '.csv'

                if '.csv' not in filename:
                    filename = filename + '.csv'
                # Check if directory exists; if not, create a new folder 
                if not os.path.exists('Data/Curie Temperature'):
                    os.makedirs('Data/Curie Temperature')

                columns = ['Compound', 'Extracted Temperature (K)', 'Sentence', 'Title',
                           'DOI', 'Author(s)', 'Journal', 'Volume', 'Page',
                           'Cover Date', 'Access Date']

                if not os.path.exists('Data/Curie Temperature/' + filename) or rewrite == 'y':
                    with open('Data/Curie Temperature/' + filename, 'w') as f:
                        writeo = csv.writer(f)
                        writeo.writerow(columns)

            curie_temperature = []

            for sent in sentences:
                #print(sent)
                if exclude_thinfilm == 'y':
                    if 'nanostruct' in sent or 'wire' in sent or 'film' in sent \
                            or 'quantum dot' in sent or 'substrate' in sent:
                        continue
                if len(self.find_chemical(sent)) == len(tmp.get_number_from_list(tmp.find_temperature(sent))):
                    #print(self.find_chemical(sent))
                    #print(tmp.get_number_from_list(tmp.find_temperature(sent)))
                    for i, chem in enumerate(self.find_chemical(sent)):
                        #print(tmp.find_temperature(sent))
                        write_out = [chem, tmp.get_number_from_list(tmp.find_temperature(sent))[i],
                                     sent, self.title, self.doi, self.authors,
                                     self.journal, self.volume, self.page, self.coverDate,
                                     self.accessDate]
                        curie_temperature.append(write_out)

                        if write == 'y':
                            with open('Data/Neel Temperature/' + filename, 'a') as f:
                                if material == 'Fe0.5Co0.5Si':
                                    print(write_out)
                                writeo = csv.writer(f)
                                writeo.writerow(write_out)
                    # Else, assign the temperature to the chemical name most mentioned / the chemical we're looking for
                else:
                    for s in re.findall('.*?[K]{1}\W', sent):
                        if 'nanostruct' in s or 'wire' in s or 'film' in s or 'quantum dot' in s:
                            print(s)
                        if self.has_keywords(sentence=s, keywords=keywords):
                            for t in tmp.get_number_from_list(tmp.find_temperature(s, unit='K')):
                                if self.find_chemical(s, sorted='n'):
                                    write_out = [max(set(self.find_chemical(s, sorted='n')),
                                                     key=self.find_chemical(s, sorted='n').count),
                                                 t, sent, self.title, self.doi, self.authors,
                                                 self.journal, self.volume, self.page, self.coverDate,
                                                 self.accessDate]
                                else:
                                    write_out = [None, t, sent, self.title, self.doi, self.authors,
                                                 self.journal, self.volume, self.page, self.coverDate,
                                                 self.accessDate]

                                curie_temperature.append(write_out)

                                if write == 'y':
                                    with open('Data/Curie Temperature/' + filename, 'a') as f:
                                        if material == 'Fe0.5Co0.5Si':
                                            print(write_out)
                                        writeo = csv.writer(f)
                                        writeo.writerow(write_out)

            return curie_temperature

    def get_neel_temperature(self, material=None, filename=None, exclude_thinfilm='y',
                             keywords=None,
                             write='n', rewrite='n'):
        # TODO: Double check with get_curie_temperature

        if keywords is None:
            keywords = ['Tn', 'T_n', 'T n', 'TN', 'T_N', 'T N', 'Neel temperature', 'Néel temperature',
                        'antiferromagnet AND transition temperature', 'AFM order', 'antiferromagnetic order']

        if type(self.text) != str:
            return []
        else:
            # If material is not mentioned in the article,
            # then replace the material with the most common materials in article
            chemicals = self.find_chemical()
            if material not in chemicals and material not in self.title:
                if chemicals:
                    material = max(set(chemicals), key=chemicals.count)

            sentences = self.find_sentences(keywords, material)

            # If it's an Elsevier file, remove the weird long sentence at the start
            if self.isElsevier():
                sentences = [s for s in sentences if len(s) < 1500]

            if write == 'y':
                if filename is None:
                    filename = 'Neel_temperature_records' + str(datetime.date.today()) + '.csv'

                if '.csv' not in filename:
                    filename = filename + '.csv'
                # Check if directory exists; if not, create a new folder
                if not os.path.exists('Data/Neel Temperature'):
                    os.makedirs('Data/Neel Temperature')

                columns = ['Compound', 'Extracted Temperature (K)', 'Sentence', 'Title',
                           'DOI', 'Author(s)', 'Journal', 'Volume', 'Page',
                           'Cover Date', 'Access Date']

                if not os.path.exists('Data/Neel Temperature/' + filename) or rewrite == 'y':
                    with open('Data/Neel Temperature/' + filename, 'w') as f:
                        writeo = csv.writer(f)
                        writeo.writerow(columns)

            neel_temperature = []

            for sent in sentences:
                if exclude_thinfilm == 'y':
                    if 'nanostruct' in sent or 'wire' in sent or 'film' in sent \
                            or 'quantum dot' in sent or 'substrate' in sent:
                        continue
                # If the number of chemicals is equal to the number of temperature mentions
                # Assign the first temperature to the first chemical, etc
                # TODO: For the case of e.g. Co2 MnSn => ['MnSn', 'Co2 MnSn']
                if len(self.find_chemical(sent)) == len(tmp.get_number_from_list(tmp.find_temperature(sent))):
                    for i, chem in enumerate(self.find_chemical(sent)):
                        write_out = [chem, tmp.get_number(tmp.find_temperature(sent))[i],
                                     sent, self.title, self.doi, self.authors,
                                     self.journal, self.volume, self.page, self.coverDate,
                                     self.accessDate]
                        neel_temperature.append(write_out)

                        if write == 'y':
                            with open('Data/Neel Temperature/' + filename, 'a') as f:
                                if material == 'Fe0.5Co0.5Si':
                                    print(write_out)
                                writeo = csv.writer(f)
                                writeo.writerow(write_out)
                # Else, assign the temperature to the chemical name most mentioned / the chemical we're looking for
                else:
                    for s in re.findall('.*?[K]{1}\W', sent):
                        if 'nanostruct' in s or 'wire' in s or 'film' in s or 'quantum dot' in s:
                            print(s)
                        if self.has_keywords(sentence=s, keywords=keywords):
                            for t in tmp.find_temperature(s, unit='K'):
                                for num in tmp.get_number(t):
                                    if self.find_chemical(s, sorted='n'):
                                        write_out = [max(set(self.find_chemical(s, sorted='n')),
                                                         key=self.find_chemical(s, sorted='n').count),
                                                     num, sent, self.title, self.doi, self.authors,
                                                     self.journal, self.volume, self.page, self.coverDate,
                                                     self.accessDate]
                                    else:
                                        write_out = [material, num, sent, self.title, self.doi, self.authors,
                                                     self.journal, self.volume, self.page, self.coverDate,
                                                     self.accessDate]

                                    neel_temperature.append(write_out)

                                    if write == 'y':
                                        with open('Data/Neel Temperature/' + filename, 'a') as f:
                                            if material == 'Fe0.5Co0.5Si':
                                                print(write_out)
                                            writeo = csv.writer(f)
                                            writeo.writerow(write_out)
            return neel_temperature

    @staticmethod
    def has_keywords(sentence, keywords):
        """
        Function checking whether or not one of the keywords are in a sentence
        :param sentence: str
        :param keywords: list of str
        :return: boolean: True if the sentence contain a keyword, no if not
        """
        for k in keywords:
            if 'AND' in keywords:
                return all(word in sentence for word in re.split('[ ]?AND[ ]?', k))
            elif k in sentence:
                return True
        return False

    def find_chemical(self, text=None, sorted=False):
        """
        :param: text: string or None type
        :param: sorted: boolean (True or False): If true, an OrderedDict will be returned.
                                                If false, the result will be a list of strings
        :return: list of strings: list of chemicals recognised from text

        Limitations: Chemical must contain 2 or more elements.
            One of the elements must contain a lower-case letter (e.g. Fe, Si, etc.)

        These limitations are acceptable for the materials that we care about, but this function is
        definitely not general.

        if text == None:
            text = self.text

        if type(text)!= str:
            return []

        ### This is a lot slower than using re
        result = [m[0] for m in MaterialsTextProcessor().process(text)[1]]

        counter = collections.Counter(result)
        sorted_counter = sorted(counter.items(), key = lambda kv: kv[1])
        sorted_dict = collections.OrderedDict(sorted_counter)
        self.chemicals = set(list(sorted_dict.keys()))
        return (sorted_dict)


        """

        if text is None:
            text = self.text

        if type(text) != str or text == '':
            return []

        if not sorted:
            result = chem.find_chemical(text, sorted_dict='n')
        else:
            result = chem.find_chemical(text)

        #temp = re.findall(
        #    '\A[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\W|'
        #    '[(]?[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\W|'
        #    '[(]?[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\Z',
        #    text)
        #result = []

        #for t in temp:
        #    if t[-1 ] == '.':
        #        t = t[:-1]
        #    if (not re.search('\D+[.]{1}', t)) and not re.search('[a-z]{1}[a-z]{1}',
        #                                                         t) and 'GPa' not in t and 'MPa' not in t and \
        #            (re.search('[A-Z][a-z]', t)) and \
        #            not re.search('[A-Z][a-z]{2,100}', t):
        #        if (''.join(re.findall('[A-Z(][A-Za-z0-9().]*[A-Za-z0-9)]', t))) not in SPLIT_UNITS:
        #            result.append(''.join(re.findall('[A-Z(][A-Za-z0-9().]*[A-Za-z0-9)]', t)))

        # if self.isSpringer:
        #temp = re.findall('\W[A-Z][A-Za-z()]*[ ]?\d?', text)
        #beg = 0
        ## temp1 = re.findall('\A[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\W|\W[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\W|\W[A-Z]{1}[A-Za-z0-9().]*[A-Z]{1}[A-Za-z0-9().]*\Z', text)
        #for i in range(len(temp) - 1):
        #    if text.find(temp[i], beg) + len(temp[i]) == text.find(temp[i + 1], beg):
        #        if re.search('[A-Z][a-z]', ''.join((temp[i] + temp[i + 1]).split())) and not re.search('[a-z]{2}',
        #                                                                                               ''.join((
        #                                                                                                               temp[
        #                                                                                                                   i] +
        #                                                                                                               temp[
        #                                                                                                                   i + 1]).split())):
                    # beg = text.find(temp[i + 1]) + len (temp[i+1])
                    # print(beg)
        #            result.append(''.join((temp[i] + temp[i + 1]).split()))
                    # result.append(temp[i] + temp[i+1])
                    # temp[i] = temp[i] + temp[i+1]
            # return temp
            # print(result)
        # counter = collections.Counter(result)
        # sorted_counter = sorted(counter.items(), key = lambda kv: kv[1])
        # sorted_dict = collections.OrderedDict(sorted_counter)
        # self.chemicals = list(sorted_dict.keys())
        # return (sorted_dict)
        #if return_position == 'n':
        #    return result
        #else:
        #    result_with_position = []
        #    for chemical in result:
        #        result_with_position.append((chemical, text.find(chemical), text.find(chemical) + len(chemical)))
        #    return result_with_position

        return result

        # return (collections.OrderedDict(sorted(counter.items(), key = lambda kv: kv[1])))

    def get_skyrmion_size(self, material=None, filename=None, exclude_thinfilm='y', \
                          keywords=None, write='y', rewrite='n'):

        if keywords is None:
            keywords = ['skyrmion AND size', 'skyrmion AND radius', 'skyrmion AND diameter',
                        'heli AND wavelength', 'helical pitch', 'helical period']

        if type(self.text) != str:
            return []
        else:
            ### If material is not mentioned in the article, then ignore the article
            chemicals = self.find_chemical()
            if material is not None:
                if material not in chemicals and material not in self.title:
                    if chemicals:
                        material = max(set(chemicals), key=chemicals.count)
            else:
                material = max(set(chemicals), key=chemicals.count)

            sentences = self.find_sentences(keywords, material)

            # If it's an Elsevier file, remove the weird long sentence at the start
            if self.isElsevier():
                sentences = [s for s in sentences if len(s) < 1500]

            if write == 'y':
                if filename is None:
                    filename = 'skyrmion_size_records' + str(datetime.date.today()) + '.csv'

                if '.csv' not in filename:
                    filename = filename + '.csv'
                # Check if directory exists; if not, create a new folder 
                if not os.path.exists('Data/Skyrmion_Size'):
                    os.makedirs('Data/Skyrmion_Size')

                columns = ['Compound', 'Original Skyrmion Size', 'Original Unit',
                           'Skyrmion Size (nm)', 'Sentence', 'Title',
                           'DOI', 'Author(s)', 'Journal', 'Volume', 'Page',
                           'Cover Date', 'Access Date']

                if not os.path.exists('Data/Skyrmion_Size/' + filename) or rewrite == 'y':
                    with open('Data/Skyrmion_Size/' + filename, 'w') as f:
                        writeo = csv.writer(f)
                        writeo.writerow(columns)

            skyrmion_size = []

            for sent in sentences:
                if exclude_thinfilm == 'y':
                    if 'nanostruct' in sent or 'wire' in sent or 'film' in sent or 'quantum dot' in sent:
                        continue

                if 'nanoparticle' in sent or 'grain size' in sent or 'particle size' in sent or 'cell size' in sent or 'nanodisk' in sent:
                    continue

                for size in sks.find_size(sent):

                    if self.find_chemical(sent, sorted='n'):
                        write_out = [max(set(self.find_chemical(sent, sorted='n')),
                                         key=self.find_chemical(sent, sorted='n').count),
                                     sks.get_number(size), sks.get_unit(size), sks.convert_to_nm(size),
                                     sent, self.title, self.doi, self.authors,
                                     self.journal, self.volume, self.page, self.coverDate,
                                     self.accessDate]
                    else:
                        write_out = [material, sks.get_number(size), sks.get_unit(size), sks.convert_to_nm(size),
                                     sent, self.title, self.doi, self.authors,
                                     self.journal, self.volume, self.page, self.coverDate,
                                     self.accessDate]

                    skyrmion_size.append(write_out)

                    if write == 'y':
                        with open('Data/Skyrmion_Size/' + filename, 'a') as f:
                            if material == 'Fe0.5Co0.5Si':
                                print(write_out)
                            writeo = csv.writer(f)
                            writeo.writerow(write_out)
            return skyrmion_size

    # TODO: Find magnetic domains of material from text
    # def find_magnetism(self, text):
    #    sentences = nltk.sent_tokenize(text)
    #    for s in sentences:
    #        if self.find_chemical(s):
    #            if 'antiferromagnet' in text:
    #                
    #            elif 'ferromagnet' in text:

    #            elif 'ferrimagnet' in text:

    #            else:
