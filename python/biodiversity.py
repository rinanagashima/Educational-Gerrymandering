# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 19:07:26 2024

@author: rinan

This file constructs and tests the Shannon diversity index 
and the Simpson diversity index, both measures of biodiversity.
"""


import math
import numpy as np


"""
# Define a dummy 'part' dictionary with made-up data
part = {
    "black population": {"node1": 20, "node2": 30, "node3": 25},
    "white population": {"node1": 50, "node2": 20, "node3": 30},
    "hispanic population": {"node1": 30, "node2": 40, "node3": 35},
    "asian population": {"node1": 10, "node2": 5, "node3": 15},
    "native american population": {"node1": 2, "node2": 3, "node3": 2},
    "native hawaiian population": {"node1": 1, "node2": 2, "node3": 1},
    "multiracial population": {"node1": 5, "node2": 7, "node3": 6},
    "population": {"node1": 118, "node2": 107, "node3": 114}
}
"""


# Define a function for Shannon's Diversity Index
def calculate_shannon_diversity(proportions, num_races):
    shannon_diversity = -sum(p * math.log(p) for p in proportions if p > 0)
    #shannon_diversity = shannon_sum / math.log(num_races)
    return shannon_diversity

# Define a function for Simpson's Diversity Index
def calculate_simpson_diversity(proportions):
    simpson_diversity = 1 - sum(p**2 for p in proportions)
    return simpson_diversity

def calculate_dissimilarity(diversity_indices):
    # Calculate the mean and standard deviation
    mean_diversity = np.mean(diversity_indices)
    std_dev_diversity = np.std(diversity_indices)
    
    # Calculate dissimilarity for each partition
    dissimilarities = np.mean([(index - mean_diversity) / std_dev_diversity for index in diversity_indices])
    
    return dissimilarities


