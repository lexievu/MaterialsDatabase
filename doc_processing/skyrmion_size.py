#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:53:33 2019

@author: thv20
"""

import re

SKYRMION_SIZE_UNITS = ['Å', 'nm', 'μm', 'um', 'μ m']


def find_size(text, units=SKYRMION_SIZE_UNITS):
    """
    Input:
        text (string)
        units (list of strings): units that are used for skyrmion size
    Output:
        list of strings: the mentions of size in text
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
    if len(re.findall('\d+[.,-]?\d*', text)) > 0:
        text = text.replace(',', '.').replace('-', '.')
        if '±' in text:
            return float(''.join(re.findall('\d+[.,]?\d*', text)[0]))
        else:
            return float(''.join(re.findall('\d+[.,]?\d*', text)))
    else:
        return None


def get_unit(text, units=SKYRMION_SIZE_UNITS):
    for u in units:
        if u in text:
            return u

    return [x[:-1] for x in re.findall('\D+\Z', text)][0]


def convert_to_nm(text, roundto=2):
    if get_unit(text) == 'nm':
        number = get_number(text)  # 1 nm = 1 nm
        unit = 'nm'
        return (str(round(number, roundto)))
    elif get_unit(text) == 'μm':
        number = get_number(text) * 1000  ## 1 micron = 1000 nm
        unit = 'nm'
        return (str(round(number, roundto)))
    elif get_unit(text) == 'Å':
        number = get_number(text) * 0.1  ## 1 Angstrom = 0.1 nm
        unit = 'nm'
        return (str(round(number, roundto)))
    else:
        raise ValueError('Initial unit  ' + get_unit(text) + ' is not recognised')


def convert_nm_to_Angstrom(text, roundto=2):
    if get_unit(text) == 'Å':
        return text
    elif get_unit(text) != 'nm':
        raise ValueError('Initial unit is not nm')
    else:
        number = get_number(text) * 10  ## 1 nm = 10 Angstrom
        unit = 'Å'
        return (str(round(number, roundto)) + unit)
