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

import re
import numpy as np
import collections

TEMPERATURE_UNITS = ['K', 'C', 'F']

def find_temperature (text, unit = 'K'): 
    """
    :param: text: string
    :param: unit: string: default to 'K'
    
    :return: list of strings of temperature

    Example:

    >>> from doc_processing.temperature import find_temperature
    >>> find_temperature('The Curie temperature of the material is 400 K.')
    OUT: [' 400 K.']
    """
    if unit == 'K':
        return re.findall(u'\W\d*[.,]?\d*[ ]?[±]?[ ]?\d+[.,]?\d*.?K[^/A-Za-z0-9]|'\
                          '\W\d*[.,]?\d*[ ]?and?[ ]?\d+[.,]?\d*.?K[^/A-Za-z0-9]|'\
                          '\W\d*[.,]?\d*[ ]?to?[ ]?\d+[.,]?\d*.?K[^/A-Za-z0-9]|' \
                          '\W\d*[.,]?\d*[ ]?–?[ ]?\d+[.,]?\d*.?K[^/A-Za-z0-9]|' \
                          '\W\d*[.,]?\d*[ ]?[-]?[ ]?\d+[.,]?\d*.?K[^/A-Za-z0-9]', text)
    else: 
        return re.findall(u'\W\d+[.,]?\d*.?K\W|\W\d+[.,]?\d*.{0,2}C\W|\W\d+[.,]?\d*.{0,2}F\W', text)

def get_number(text):
    if len(re.findall('\d+[.,]?\d*', text)) > 0:
        text = text.replace(',', '.')
        if '±' in text: 
            return np.array([float(''.join(re.findall('\d+[.,]?\d*', text)[0]))])
        elif 'and' in text or 'to' in text or '-' in text:
            return np.array([float(f.replace(',', '.')) for f in re.findall('\d+[.,]?\d*', text)])
        else:
            #return np.array([float(''.join(re.findall('\d+[.,]?\d*', text)))])
            return np.array([float(f.replace(',', '.')) for f in re.findall('\d+[.,]?\d*', text)])
    else: 
        return None

def get_number_from_list(alist):
    result = np.array([])
    for el in alist:
        result = np.append(result, get_number(el))
    return result

def get_unit(text):
    return ''.join(re.findall('[cCfFkK]', text))

def get_all_num(list_of_texts, unit = 'K'): 
    '''
    Input: list of texts (list of strings)
    Output: list of number 
    '''
    all_num = []
    for text in list_of_texts: 
        temp = find_temperature(text, unit = unit)
        temp_num = []
        for t in temp: 
            temp_num.append(get_number(t))
        all_num = all_num + list(dict.fromkeys(temp_num))    
    return all_num

def mean (nums): 
    '''
    Input: list of floats 
    Output: mean + standard error
    '''
    
    if len(nums) == 1: 
        return (nums[0], 0)
    
    mean = np.mean(nums)
    error = np.std(nums)/np.sqrt(len(nums))
    
    return (mean, error)

def median (nums): 
    '''
    Input: list of floats 
    Output: median + standard error
    '''
    
    median = np.median(nums)
    error = 1.253*np.std(nums)/np.sqrt(len(nums))
    
    return (median, error)

def sort_by_temperature(temperatures): 
    '''
    Input: dictionary, values (temperature, error)
    Output: sorted dictionary by temperature
    '''
    sorted_dict = collections.OrderedDict(sorted(temperatures.items(),\
                                                 key=lambda kv: kv[1]))
    
    return sorted_dict
    
