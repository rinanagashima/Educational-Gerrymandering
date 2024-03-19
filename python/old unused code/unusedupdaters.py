# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 07:27:05 2024

@author: rinan
"""

# this file records all the updaters that i never used




def capacities(partition):
    # Print the available keys in the partition's population data for debugging
    print("Available ncessch keys in partition:", partition.keys())
    print(dir(partition))  # List all attributes and methods of the partition object
    # Iterate through each part's (sab's) population in the partition
    for district_id, district_data in partition.parts.items():
        print(district_id)
    # This gives you direct access to both the district ID and the associated data, allowing for more complex operations.
    return True



"""    
def within_10_percent_of_initial(initial_partition):
    initial_populations = {district: pop for district, pop in initial_partition["population"].items()}
    
    def population_constraint(proposed_partition):
        print(proposed_partition.updaters.keys())  # See what updaters are available
        print(proposed_partition["population"])
        
        # Initialize a list to store the boolean results for each district
        all_districts_within_bounds = []
        
        for district, proposed_pop in proposed_partition["population"].items():
            initial_pop = initial_populations[district]
            # define upper and lower bounds within 10% of current population
            lower_bound = initial_pop * 0.9
            upper_bound = initial_pop * 1.1
            # Check if the proposed population is within bounds
            within_bounds = lower_bound <= proposed_pop <= upper_bound
            # Append the result to the list
            all_districts_within_bounds.append(within_bounds)
        
        # Use .all() to check if all districts are within bounds
        return all(all_districts_within_bounds)
 
    return population_constraint

    return True
"""



# Use the custom constraint with your initial partition
#pop_constraint = within_10_percent_of_initial(initial_partition)

"""
# check that each district has a school inside it
def contains(initial_partition):
    for part in initial_partition.parts.keys():
        if school_container[part] not in initial_partition.parts[part]:
            return False
    return True
"""

"""
# check that each school has within 10% of actual enrollment
def capacities(partition):
    # iterate through all the parts (sabs) in the partition
    for part_id, part_data in partition.parts.items():
        ncessch = part_data["district_id"]
        initial_pop = ideal_pop[ncessch]
        current_pop = sum(partition["population"].values())
        # define upper and lower bounds within 10% of current population
        lower_bound = initial_pop * 0.9
        upper_bound = initial_pop * 1.1
        if not (lower_bound <= current_pop <= upper_bound):
            return False
    return True

"""
"""
from gerrychain.constraints import WithinPercentRangeOfBounds

def make_population_constraint(district_id, ideal_population, percent=0.1):
    def population_validator(partition):
        # Check if district_id is in the partition's population data to avoid KeyError
        if district_id in partition["population"]:
            print("district id is in partition pop")
            return True
            #return partition["population"][district_id]
        else:
            # Handle the case where district_id is not found
            print("district id is not in the partition population")
            return True  # or some other default behavior

    # Instantiate the WithinPercentRangeOfBounds constraint with the population_validator
    return WithinPercentRangeOfBounds(population_validator, percent)




from gerrychain.constraints import WithinPercentRangeOfBounds

def make_population_constraint(district_id, ideal_population, percent=0.1):
    # Define a function that returns the current population of the specified district
    def population_validator(partition):
        # Assuming 'population' is the key in the partition's updaters dictionary that returns a dict of populations by district
        return partition.updaters["population"][district_id]

    # Instantiate the WithinPercentRangeOfBounds constraint
    # Note: The initial value and percentage bounds are implicitly managed by the constraint itself
    return WithinPercentRangeOfBounds(population_validator, percent)






def population_validator(partition, district_id, pop):
    # Access the population for a specific district
    current_population = partition[district_id]
    return current_population

from gerrychain.constraints import WithinPercentRangeOfBounds

def make_population_constraint(district_id, ideal_pop, percent=0.1):
    # Create a customized population validator for the given district
    def custom_population_validator(partition):
        return population_validator(partition, district_id)
    
    # Instantiate WithinPercentRangeOfBounds with the custom validator
    constraint = WithinPercentRangeOfBounds(custom_population_validator, percent)
    
    # Adjust the initial value used by the constraint to be the initial population of the district
    constraint.initial = ideal_pop
    
    return constraint
"""


