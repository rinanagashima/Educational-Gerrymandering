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

def calculate_gini(diversity_indices):
    total = 0
    n = len(diversity_indices)
    for i, xi in enumerate(diversity_indices[:-1]):
        # Calculate the absolute difference between xi and each element in the slice
        differences = np.abs(xi - np.array(diversity_indices[i+1:]))
        total += np.sum(differences)
    return total / (2* n**2 * np.mean(diversity_indices))

