#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:53:33 2019

@author: thv20
"""

import re
import numpy as np
import collections

SKYRMION_SIZE_UNITS = ['Å', 'Angstrom', 'nm', 'μm', 'um', 'μ m']

def find_size(text, units=SKYRMION_SIZE_UNITS):
    """
    :param: text (string)
    :param: units (list of strings): units that are used for skyrmion size
    :return: list of strings: the mentions of size in text

    >>> from doc_processing.skyrmion_size import find_size
    >>> find_size('The skyrmion size in the material is between 50 and 100 nm.')
    OUT: [' 50 and 100 nm.']
    """

    base_pattern = '\W\d*[.]?\d*(?:[ ]?and[ ]?|[ ]?to[ ]?|[ ]?±[ ]?|[ ]?-[ ]?|[ ]?–[ ]?|)?\d+[.]?\d*[^A-Za-z0-9μ]?'
    pattern = u''
    for i in range(len(units)):
        if i < len(units) - 1:
            pattern = pattern + base_pattern + units[i] + '\W|'
        else:
            pattern = pattern + base_pattern + units[i] + '\W'
    return re.findall(pattern, text)


def get_number(text):
    """
    Get numbers in a body of text
    :param text: string
    :return: numpy array of floats

    Example:
    >>> from doc_processing.skyrmion_size import get_number
    >>> get_number(' 100 to 200 nm')
    Out: array([100., 200.])
    """
    if len(re.findall('\d+[.,]?\d*', text)) > 0:
        text = text.replace(',', '.')
        if '±' in text:
            return np.array([float(''.join(re.findall('\d+[.,]?\d*', text)[0]))])
        elif 'and' in text or 'to' in text or '-' in text:
            return np.array([float(f.replace(',', '.')) for f in re.findall('\d+[.,]?\d*', text)])
        else:
            return np.array([float(f.replace(',', '.')) for f in re.findall('\d+[.,]?\d*', text)])
    else:
        return None

def get_number_from_list(alist):
    """
    Return an array of numbers from a list of strings
    :param alist: list of strings
    :return: numpy array of number

    Example:
    >>> from doc_processing.skyrmion_size import get_number_from_list
    >>> get_number_from_list(['100 to 200 nm', '50 um'])
    Out: array([100., 200.,  50.])
    """
    result = np.array([])
    for el in alist:
        result = np.append(result, get_number(el))
    return result

def get_unit(text, units=SKYRMION_SIZE_UNITS):
    """
    Return a string (the unit), given a string
    :param text: string
    :param units: units to look from.
                  If not specified, the units are set to those in SKYRMION_SIZE_UNITS list on top of this file
                  If the string does not contain any unit specified, it will make a guess of the unit
    :return: string, which should be the unit

    Example:
    >>> from doc_processing.skyrmion_size import get_unit
    >>> get_unit('The skyrmion size in the material is 50nm.')
    Out: 'nm'
    >>> get_unit(' 70 km ')
    Out: 'km'
    """
    pattern = ''
    for u in units:
        if u == units[0]:
            pattern = pattern + u
        else:
            pattern = pattern + '|' + u

    if re.findall(pattern, text):
        return re.findall(pattern, text)[0]
    else:
        if re.findall('\d', text) and re.findall('\D+\Z', text):
            return ''.join([x[:-1] for x in re.findall('\D+\Z', text)][0].split())
        else:
            return None


def convert_to_nm(text, roundto=2):
    """
    This function converts a recognised unit of length to nm
    :param text: string
    :param roundto: integer, to what decimal place should the result be rounded to
    :return: str

    Example:
    >>> from doc_processing.skyrmion_size import convert_to_nm
    >>> convert_to_nm(' 100 um ')
    OUT: array([100000.])
    >>> convert_to_nm(' 1.15981705987201 um ')
    OUT: array([1159.82])
    >>> convert_to_nm(' 100 to 200 Å ')
    OUT: array([10., 20.])

    If the unit is not one of the recognised units, an error will be raised.

    Example:
    >>> convert_to_nm(' 70 km ')
    OUT: ValueError: ('Initial unit  km is not recognised',
                      'SKYRMION_SIZE_UNITS', ['Å', 'Angstrom', 'nm', 'μm', 'um', 'μ m'])
    """
    if get_unit(text) == 'nm':
        number = get_number(text)  # 1 nm = 1 nm
        return np.round(number, roundto)
    elif get_unit(text) == 'μm' or get_unit(text) == 'um' or get_unit(text) == 'μ m':
        number = get_number(text) * 1000  ## 1 micron = 1000 nm
        return np.round(number, roundto)
    elif get_unit(text) == 'Å' or get_unit(text) == 'Angstrom':
        number = get_number(text) * 0.1  ## 1 Angstrom = 0.1 nm
        return np.round(number, roundto)
    else:
        raise ValueError('Initial unit  ' + get_unit(text) + ' is not recognised',
                         'SKYRMION_SIZE_UNITS', SKYRMION_SIZE_UNITS)


def convert_to_Angstrom(text, roundto=2):
    """
    This function only convert nm to Angstrom
    :param text: string
    :param roundto: int
    :return: numpy array of float

    Example:
    >>> convert_to_Angstrom(' 100 nm ')
    OUT: array([1000.])
    >>> convert_to_Angstrom(' 100 km ')
    OUT: ValueError: ('Initial unit is not recognised.
                       SKYRMION_SIZE_UNITS = ', ['Å', 'Angstrom', 'nm', 'μm', 'um', 'μ m'])
    """
    if get_unit(text) == 'Å':
        return get_number(text)
    elif get_unit(text) == 'nm':
        number = get_number(text) * 10  ## 1 nm = 10 Angstrom
        return np.round(number, roundto)
    elif get_unit(text) == 'um' or get_unit(text) == 'μm' or get_unit(text) == 'μ m':
        number = get_number(text) * 10000  ## 1 um = 10,000 Angstrom
        return np.round(number, roundto)
    else:
        raise ValueError('Initial unit is not recognised. SKYRMION_SIZE_UNITS = ', SKYRMION_SIZE_UNITS)
