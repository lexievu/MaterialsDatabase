#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 14:42:53 2019

@author: thv20

Import the file

>>> import doc_processing.temperature as tmp
>>> tmp.find_temperature('The Curie temperature of the material is 400 K.')
OUT: [' 400 K.']
"""

import collections
import re

import numpy as np

TEMPERATURE_UNITS = ['K', 'C', 'F']


def find_temperature(text, units=None):
    """
    :param: text: string
    :param: unit: None, string or list of string
                  If not specified, the units is then set to TEMPERATURE_UNITS, specified at the top of this file
    
    :return: list of strings of temperature

    Example:

    >>> from doc_processing.temperature import find_temperature
    >>> find_temperature('The Curie temperature of the material is 400 K.')
    OUT: [' 400 K.']

    >>> find_temperature(' 100 K ', 'C')
    OUT: []

    >>> find_temperature(' 100 K ', 'K')
    OUT: [' 100 K ']
    """

    if units is None:
        units = TEMPERATURE_UNITS

    if type(units) == str:
        units = [units]

    base_pattern = '\W\d*[.]?\d*(?:[ ]?and[ ]?|[ ]?to[ ]?|[ ]?±[ ]?|[ ]?-[ ]?|[ ]?–[ ]?|)?\d+[.]?\d*[^A-Za-z0-9μ]?'
    unit_pattern = '(?:'
    for i in range(len(units)):
        if i != len(units) - 1:
            unit_pattern = unit_pattern + units[i] + '\W' + '|'
        else:
            unit_pattern = unit_pattern + units[i] + '\W' + ')'

    pattern = base_pattern + unit_pattern

    return re.findall(pattern, text)


def get_number(text):
    """
    Get numbers in a body of text
    :param text: string
    :return: numpy array of floats

    Example:
    >>> from doc_processing.temperature import get_number
    >>> get_number(' 100 to 200 K ')
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


def get_number_from_list(alist, normalized_unit=None):
    """
    Return an array of numbers from a list of strings
    :param alist: list of strings
    :param normalized_unit: None or string
                            If not specified, it will be set to None
                            If normalized_unit == None, the temperatures will be extracted as they are
                            If normalized_unit == 'K', the temperatures will be converted to kelvin
                            If normalized_unit is set to any other value, an error will be raised
    :return: numpy array of number

    Example:
    >>> from doc_processing.temperature import get_number_from_list
    >>> get_number_from_list([' 50 K ', '100 to 200°C'])
    Out: array([ 50., 100., 200.])

    >>> get_number_from_list([' 50 K ', '100 to 200°C'], normalized_unit='K')
    Out: array([ 50.  , 373.15, 473.15])

    >>> get_number_from_list([' 50 K ', '100 to 200°C'], normalized_unit='C')
    ValueError: normalized_unit 'C' is not recognised.The only recognised values are None or 'K'
    """
    result = np.array([])
    for el in alist:
        if normalized_unit is None:
            result = np.append(result, get_number(el))
        elif normalized_unit == 'K':
            result = np.append(result, convert_to_kelvin(el))
        else:
            raise ValueError('normalized_unit \'' + normalized_unit + '\' is not recognised.'
                                                                      'The only recognised values are None or \'K\'')
    return result


def get_unit(text):
    """
    Extract temperature unit from text
    :param text: string
                 The text from which the temperature unit is searched for
    :return: string
             The unit ('C', 'F' or 'K')
             If the unit is not found, an empty list will be returned.
    """
    pattern = '(?:'
    for i in range(len(TEMPERATURE_UNITS)):
        if i != len(TEMPERATURE_UNITS) - 1:
            pattern = pattern + TEMPERATURE_UNITS[i] + '|'
        else:
            pattern = pattern + TEMPERATURE_UNITS[i] + ')'

    pattern = pattern + '(?:\W|\Z)'

    if re.findall(pattern, text):
        return re.findall('[CFK]', re.findall(pattern, text)[0])[0]
    else:
        return []


def sort_by_temperature(temperatures):
    """
    Sort a dictionary by temperature (value)
    :param temperatures: dictionary
                         keys should be the chemical formulae of the compounds
                         values should be in the form of (average temperature, error)
    :return: an OrderedDict, ordered by temperature
    """
    sorted_dict = collections.OrderedDict(sorted(temperatures.items(),
                                                 key=lambda kv: kv[1]))
    return sorted_dict


def convert_to_kelvin(text):
    """
    Convert a temperature measured in K, C or F to Kelvin
    :param text: string
    :return: numpy array of floates mentioned in the text

    Example:
    >>> from doc_processing.temperature import convert_to_kelvin
    >>> convert_to_kelvin(' 100 K ')
    Out: array([100.])

    >>> convert_to_kelvin(' 100°F ')
    Out: array([310.92777778])

    >>> convert_to_kelvin(' 100°C ')
    Out: array([373.15])

    >>> convert_to_kelvin(' 50 to 100°C ')
    Out: array([323.15, 373.15])
    """
    if get_unit(text) == 'K':
        return get_number(text)  # 1 K = 1 K
    elif get_unit(text) == 'C':
        return get_number(text) + 273.15
    elif get_unit(text) == 'F':
        return (get_number(text) - 32) * (5 / 9) + 273.15
    else:
        raise ValueError(get_unit(text) + ' is not a recognised unit. The only units '
                                          'recognised are K, C and F.')
