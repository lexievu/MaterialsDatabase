#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 18:36:39 2019

@author: thv20
"""

import numpy as np
import matplotlib.pyplot as plt
import collections
from chemicals import *
import math
from matplotlib import figure


def remove_single_mentions(alist, bins='auto'):
    hist, bin_edges = np.histogram(alist, bins=bins)
    temp = []
    # temp = copy.deepcopy(alist)
    if len(alist) == 1:
        return alist
    for i in range(len(hist)):
        if hist[i] > 1:
            temp = temp + [x for x in alist if x > bin_edges[i] and x < bin_edges[i + 1]]

    return temp


def remove_outliers(all_num, method='std'):
    '''
    Input: list of all numbers
    Output: remove the outliers, defined as numbers outside 2 standard deviations of the mean
    '''
    outliers_removed = []
    if len(all_num) == 1:
        return all_num

    if method == 'std':
        mean = np.mean(all_num)
        std = np.std(all_num)
        outliers_removed = [x for x in all_num if x < (mean + 2 * std)]
        outliers_removed = [x for x in outliers_removed if x > (mean - 2 * std)]

    elif method == 'iqr':
        q1, q3 = np.percentile(all_num, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outliers_removed = [x for x in all_num if x > lower_bound]
        outliers_removed = [x for x in outliers_removed if x < upper_bound]

    return outliers_removed


def mean(nums):
    '''
    Input: list of floats 
    Output: mean + standard error
    '''

    if len(nums) == 1:
        return (nums[0], 0)

    mean = np.mean(nums)
    error = np.std(nums) / np.sqrt(len(nums))

    return (mean, error)


def median(nums):
    '''
    Input: list of floats 
    Output: median + standard error
    '''

    median = np.median(nums)
    error = 1.253 * np.std(nums) / np.sqrt(len(nums))

    return (median, error)


def plot_hist(data, expected=None, mode='median', title='', xlabel='', ylabel='', unit='', bins=20):
    if mode == 'median':
        mean_m = median(data)
    else:
        mean_m = mean(data)
    plt.hist(data, bins=bins)
    plt.axvline(x=mean_m[0], linestyle='--', color='b', \
                label=str(round(mean_m[0], 1)) + '$\pm$' + str(round(mean_m[1], 1)) + unit)
    plt.axvspan(mean_m[0] - mean_m[1], mean_m[0] + mean_m[1], alpha=0.2, color='b')

    if title != '':
        plt.title(title)
    if xlabel != '':
        plt.xlabel(xlabel)
    if ylabel != '':
        plt.ylabel(ylabel)

    if expected != None:
        plt.axvline(expected, linestyle='--', color='k', \
                    label='Expected: ' + str(expected) + unit)

    def calc_yticks(data):
        occurence = np.histogram(data)[0]
        if len(range(0, math.ceil(max(occurence)) + 1, 1)) > 10:
            return (range(0, math.ceil(max(occurence)) + 1, 5))
        elif len(range(0, math.ceil(max(occurence)) + 1, 1)) < 10:
            return (range(0, math.ceil(max(occurence)) + 1, 1))

    occurence = np.histogram(data)[0]
    if len(range(0, math.ceil(max(occurence)) + 1, 1)) < 20:
        plt.yticks(calc_yticks(data))

    plt.legend()

    return mean_m


def plot_scatter(data_dict, all_data=None, expected=None, title=None, paper_no=None, materials=None, yrange=None,
                 ylabel='Curie Temperature (K)', height_to_width_ratio = 1):
    w,h = figure.figaspect(height_to_width_ratio)
    
    sorted_dict = collections.OrderedDict(sorted(data_dict.items(), key=lambda kv: kv[1]))
    fig = plt.figure(figsize = (w,h))
    ax = fig.add_subplot(111)
    if paper_no is None:
        paper_no = {}
    for (i, k) in list(zip(range(len(sorted_dict.keys())), list(sorted_dict.keys()))):
        if k not in paper_no.keys():
            paper_no[k] = 1
        ax.scatter([i], [data_dict[k][0]], color='C' + str(i % 10),
                   marker='o', s=25 + 5 * paper_no[k], alpha=(0.2 + 0.8 * (1 - 1 / (paper_no[k]))))
        ax.errorbar([i], [data_dict[k][0]], data_dict[k][1], capsize=(50 + paper_no[k]) / 10, color='C' + str(i % 10))

        if all_data != None:
            ax.scatter(i * np.ones(len(all_data[k])), all_data[k],
                       label=k, s=5, marker='o', color='C' + str(i % 10), alpha=0.1, edgecolor=None)
        if expected != None:
            ax.scatter([i], [mat[1] for mat in expected if mat[0] == k][0], marker='^', color='k')

    if yrange != None:
        plt.ylim(yrange)
    # ax.set_xticks(range(len(sorted_dict.keys())))
    # ax.set_xticklabels(list(sorted_dict.keys()))
    if ylabel:
        plt.ylabel(ylabel, fontsize = 16/(3/height_to_width_ratio))
        
    if title != None: 
        plt.title(title, fontsize = 20/(3/height_to_width_ratio))
        
    ax.tick_params(axis = 'x', labelsize = 10/(3/height_to_width_ratio))
    ax.tick_params(axis = 'y', labelsize = 10/(3/height_to_width_ratio))

    plt.xticks(range(len(sorted_dict.keys())),
               [write_chemical_latex(x) for x in list(sorted_dict.keys())], rotation=60)
