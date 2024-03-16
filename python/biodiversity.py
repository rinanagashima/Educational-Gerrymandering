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
    shannon_sum = -sum(p * math.log(p) for p in proportions if p > 0)
    shannon_diversity = shannon_sum / math.log(num_races)
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
    dissimilarities = [(index - mean_diversity) / std_dev_diversity for index in diversity_indices]
    
    return dissimilarities


"""
# Initialize the list to hold Shannons and Simpsons diversity index for each partition (plan)
shannons_diversity_indices = []
simpsons_diversity_indices = []

# placeholder for results
result = []

# for each burst:
for i in range(num_bursts):
    print("Burst:", i)
    
    # Initialize the lists for the diversity indices of each partition in the current burst
    list_of_shannons = []
    list_of_simpsons = []
    
    chain = MarkovChain(
        proposal = proposal1, 
        # school capacity constraint
        constraints=[capacities],
        accept = accept.always_accept, 
        initial_state = initial_partition, 
        total_steps = burst_length) 
    
    # for each partition (plan) in each burst, which is equal to the burst length:
    for part in chain:  
        # initialize proportions
        proportions = []
        # Here we calculate the racial distribution for each SAB
        # First, list the populations by race for every node in the plan
        blackpop = list((part["black population"].items())) 
        whitepop = list((part["white population"].items())) 
        hispanicpop = list((part["hispanic population"].items())) 
        asianpop = list((part["asian population"].items())) 
        nativeamericanpop = list((part["native american population"].items())) 
        nhpipop = list((part["native hawaiian population"].items())) 
        multiracepop = list((part["multiracial population"].items())) 
        population = list((part["population"].items())) 
        # initialize the distributions list
        distributions = []
        # For loop for every sab in the plan
        for a, b, c, d, e, f, g, h in zip(blackpop, whitepop, hispanicpop, asianpop, nativeamericanpop, nhpipop, multiracepop, population):
            # Calculate the spatial gini index
            black_perc = (a[1]/h[1])
            white_perc = (b[1]/h[1])
            hispanic_perc = (c[1]/h[1])
            asian_perc = (d[1]/h[1])
            nativeamerican_perc = (e[1]/h[1])
            nhpi_perc = (f[1]/h[1])
            multirace_perc = (g[1]/h[1])
            # Append the SAB's racial composition percentages to proportions
            proportions = [black_perc, white_perc, hispanic_perc, asian_perc, nativeamerican_perc, nhpi_perc, multirace_perc]
            
            # Calculate diversity indices
            shannon_diversity = calculate_shannon_diversity(proportions, num_races=len(proportions))
            simpson_diversity = calculate_simpson_diversity(proportions)
            
            # Append the diversity indices to their respective lists
            list_of_shannons.append(shannon_diversity)
            list_of_simpsons.append(simpson_diversity)
        
        ### now, calculate dissimilarity of the diversity indices into a single score
        dissimilarity = 
    

        
    max_shannons = [0]  # Initialize with 0, the smallest possible shannon index (1 = perfect diversity)
    max_shannon_step = 0  # To store the step with the maximum shannon index
    # Iterating through the master list of the shannon index per burst


    for step in range(len(list_of_shannons)): 
        # Identifies the burst step
        print("step", step) 
        # Print the shannon index for that step
        print("list_of_shannons[step][0]:", list_of_shannons[step][0]) 
        result.append(list_of_shannons[step][0])
        # Print the max shannons index found across the burst
        print("max_shannons[0]:", max_shannons[0])  
        # Find the plan and the position of the maximum of list_of_shannons
        if list_of_shannons[step][0] >= max_shannons[0]: 
            max_shannons_step = step
            max_shannons = list_of_shannons[step]  



    # Prints the burst step that yielded the max shannons index
    print('max_shannons_step:', max_shannons_step) 
    # Set the initial partition of the next burst to the most recent plan 
    #with the higher shannons index in the previous plan
    initial_partition = max_shannons[1] 
    
    
print("result", result)





# for each partition (plan) in each burst, which is equal to the burst length:
# Extract populations by race for every node and calculate distributions
for node in part["population"]:
    proportions = [
        part["black population"][node] / part["population"][node],
        part["white population"][node] / part["population"][node],
        part["hispanic population"][node] / part["population"][node],
        part["asian population"][node] / part["population"][node],
        part["native american population"][node] / part["population"][node],
        part["native hawaiian population"][node] / part["population"][node],
        part["multiracial population"][node] / part["population"][node]
    ]
    
    ### calculate shannon's diversity index (H) for the node
    shannon_sum = -sum(p * math.log(p) for p in proportions if p > 0)
    # normalize the index by ln(number of races)
    num_races = len(proportions)
    shannon_diversity = shannon_sum/(math.log(num_races))
    # append the partition's Shannon's Diversity to a list
    shannons_diversity_indices.append(shannon_diversity)
    
    ### now, calculate Simpson's diversity
    simpson_diversity = 1 - sum(p**2 for p in proportions)
    # append the partition's Simpson's Diversity to a list
    simpsons_diversity_indices.append(simpson_diversity)

# now, print Shannon's and Simpson's diversity indices for each partition
print("Shannon's Diversity:" , shannons_diversity_indices)
print("Simpson's Diversity:", simpsons_diversity_indices)
"""
