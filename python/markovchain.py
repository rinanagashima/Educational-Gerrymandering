# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 22:36:45 2024

@author: rinan
"""


# Short Bursts:
"""
This is the code for setting up and running the short bursts. First, this 
section specifies the parameters of the short bursts and defines the proposal 
function for each new plan. Then, it defines the constraints for proposed plans,
which ensure that they are valid. Lastly, inside a 'for' loop, the short bursts 
are run using the MarkovChain function, and the highest number of 
majority-minority districts observed per burst are recorded. 
"""

## Import additional attributes from Gerrychain required to run the short bursts: 
from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous, contiguous
from gerrychain.proposals import propose_random_flip, recom
from functools import partial
from gerrychain.accept import always_accept

# import biodiversity indices
from biodiversity import calculate_shannon_diversity, calculate_simpson_diversity, calculate_dissimilarity



## Defining the constraints: 
""" 
1) Population constraint: Each school must only have within 10% of their current enrollment
2) Time travel constraint: Later on, use the time travel API
"""

# 1) Population constraint: 
def make_capacities_constraint(initial_partition):        
    def capacities(partition):
        # Print the available keys in the partition's population data for debugging
        #print("Available ncessch keys in partition:", partition.keys())
        #print(partition["cut_edges"])
        
        # Iterate through each part's (sab's) population in the partition
        for district_id in partition.parts.keys():
            school_id = district_id
            #print(school_id)
            ideal_pop = initial_partition['population']
            initial_pop = ideal_pop[school_id]
            #print(initial_pop)
            #print(partition.population)
            current_pop = partition["population"][school_id]
            lower_bound = initial_pop * 0.9
            upper_bound = initial_pop * 1.1
                
            # Check if current population is within the bounds
            if not (lower_bound <= current_pop <= upper_bound):
                #print(school_id, " is not within bounds")
                return False  # If any district is out of bounds, return False
        print("All districts are within bounds")
        return True  # If all districts are within bounds, return True
    return capacities                                                


## Defining the proposal function: 
""" The proposal function used is the Recombination Markov Chain, also known 
as ReCom. For a given plan, ReCom randomly selects two adjacent districts, 
merges them into a single district, and then randomly re-partitions them in a 
manner that maintains the population balance. """

def proposal(initial_partition):
    # define the ideal pop for each school based on initial enrollment
    ideal_pop = initial_partition['population']
    # define the ideal population as the average population per sab
    pop_target = sum(ideal_pop.values()) / len(ideal_pop)
    proposal1 = partial(recom, pop_col = "total", pop_target = pop_target, 
                        epsilon = .5, node_repeats = 1)
    return proposal1



def shortbursts(burst_length, num_bursts, initial_partition, proposal1, capacities):
    total_steps = burst_length*num_bursts  # this is equal to num_bursts * burst_length.
    
    """
    RE=WRITE THIS COMMENT LATER
    This is the code to run the short bursts for range(num_bursts) number of times. 
    For every transition in each burst, the number of majority minority districts 
    are counted and recorded it in list_of_mm. Then, the most recent plan with the 
    highest number of majority minority districts is identified and the next burst 
    restarts from this plan. list_of_mm keeps track of the plans with the maximum 
    number of majority minority districts per burst, which is reflected in max1[1] 
    and max1[0] respectively.
    """
    list_of_max = []
    result = []

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
            accept = always_accept, 
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
            dissimilarity_shannon = calculate_dissimilarity(list_of_shannons)
            dissimilarity_simpson = calculate_dissimilarity(list_of_simpsons)
            
        max_shannons = [-1000]  # Initialize with -1000, a trivially small shannon index (positive numbers -> diverse)
        max_simpsons = [-1000]
        max_shannon_step = 0  # To store the step with the maximum shannon index
        max_simpson_step = 0
        # Iterating through the master list of the shannon and simpson index per burst

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
    return result
                               