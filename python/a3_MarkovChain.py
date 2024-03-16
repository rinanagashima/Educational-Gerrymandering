# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 08:51:21 2023

@author: rinan
"""


"""
"This document runs short bursts on Arizona's census block data. The ideal population of
each SAB is based on each school's current enrollment. The existing SABs are used as the seed plan
from which the short burst starts. In the future, we may want to start with a completely random seed plan.
Then, the short bursts are run according to the specific parameters (burst length and number of bursts), 
recording the best spatial dissimilarity index observed in each burst and the ensemble of bursts.

This code is based on AZ_Markov_Chain_bg_unadj.py from my final project in 
Professor Cannon's Math of Political Districting class.

"""

# Import the relevant libraries to run short bursts: 
import matplotlib.pyplot as plt
import random 
import gerrychain
import numpy as np
import networkx as nx
import geopandas as gpd
import pickle
import zipfile
import os
import pandas as pd
import networkx as nx


"""This is to make the code more replicable. For example, if we want the 
same result twice, we can run the code with exactly the same random seed. """
random.seed(48)


# Import attributes of gerrychain that we need to create the initial partition: 
from gerrychain import Graph, Partition, Election, proposals, updaters, constraints, accept 
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part

# set district number
leaid = "0402860"
statefip = "04"
statecrs = "EPSG:32612"

# Import the Arizona school districts
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\data\04\district")
districts = gpd.read_file('schooldistrict_sy1516_tl16_04.shp')
selected_district = districts[districts['GEOID'] == leaid]


# Import the Arizona census blocks graph: 
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\data\04\tl_2010_04_tabblock10")
arizona_bl = gpd.read_file('tl_2010_04_tabblock10.shp')


# Ensure both geodataframes have the same CRS
if arizona_bl.crs != selected_district.crs:
    selected_district = selected_district.to_crs(arizona_bl.crs)
    
# Reset the index of arizona_bl and keep the old index as a column
arizona_bl_reset = arizona_bl.reset_index()

# Perform an intersection to calculate the overlap area
intersections = gpd.overlay(arizona_bl_reset, selected_district, how='intersection')

# Calculate the area of each block and each intersection
arizona_bl_reset['area'] = arizona_bl_reset.geometry.area
intersections['overlap_area'] = intersections.geometry.area

# Assuming 'index' is the name of the original arizona_bl index in intersections
arizona_bl_reset = arizona_bl_reset.merge(intersections[['overlap_area', 'index']], on='index', how='left')

# Calculate the overlap percentage
arizona_bl_reset['overlap_percentage'] = (arizona_bl_reset['overlap_area'] / arizona_bl_reset['area']) * 100

# Filter to keep only blocks with 90% or more overlap bc 100% overlap resulted in some perimeter blocks being left out
arizona_bl_within_district = arizona_bl_reset[arizona_bl_reset['overlap_percentage'] > 50]


# plot to make sure the census blocks are being mapped onto the school district properly
# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the selected district as the base layer
selected_district.plot(ax=ax, color='lightblue', edgecolor='black')

# Overlay the filtered Arizona census blocks within the selected district
arizona_bl_within_district.plot(ax=ax, color='red', alpha=0.5)

# Customization
ax.set_title('Census Blocks within Selected District')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.show()

# reproject arizona_bl_within_district to crs for more accurate area calculations
arizona_bl_within_district = arizona_bl_within_district.to_crs(statecrs)


# Turn into a dual graph
bl_dg = Graph.from_geodataframe(arizona_bl_within_district, ignore_errors=True)

# Step 2: Create a mapping of 'GEOID10' to geometry
geoid_to_geometry = arizona_bl_within_district.set_index('GEOID10')['geometry'].to_dict()


# Import the Arizona shapefile
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\data\04\sabs")
sabs = gpd.read_file('SABS_1516_Primary_04.shp')
selected_sabs = sabs[sabs['leaid'] == leaid]


# Reproject sabs to match the CRS of arizona_bl
selected_sabs = selected_sabs.to_crs(arizona_bl_within_district.crs)
# Create a dual graph
sabs_dg = Graph.from_geodataframe(selected_sabs, ignore_errors = True)


# Create a plot of the sabs to make sure it loaded properly
selected_sabs.plot()
plt.axis('off')
plt.show()


# Import the Arizona NCES school site point geometries
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\data\04\schools")
schools = gpd.read_file('EDGE_GEOCODE_1516_PUBLICSCH_04.shp')
# Reproject edge_az to match the CRS of arizona_bl
schools = schools.to_crs(arizona_bl.crs)
# Convert all column names to lowercase
schools.columns = schools.columns.str.lower()
# Create a plot of the edge_az to make sure it loaded properly
schools.plot()
plt.axis('off')
plt.show()


# Ideal population calculation: 
""" Here, we assume that the ideal population of each school is equivalent to the current enrollment
of the school. In the future, we want to adjust this so that we consider school capacity and/or state-mandated
teacher-student ratios. 
"""

# import urban institute data (REPLACE with fully merged data later)
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\code\Educational-Gerrymandering\stata\output\dta")
ccd = pd.read_stata("mergedurbanschooldata.nvc.dta")
# Filter rows where 'fips' is equal to 'Arizona'
ccd_az = ccd[ccd['fips'] == 4]
# Print the filtered DataFrame
print(ccd_az)

# only keep the observations for the selected school district/leaid. note that ccd does not have leading 0 for the leaid
ccd_az_leaid = ccd_az[ccd_az['leaid'] == leaid[1:]]
print(ccd_az_leaid['school_name'])


# Merge the urban institute data with the school site pt geometries
merge_columns_ccd = ['ncessch']
merge_columns_schsite = ['ncessch']
# merge ccd leaid and school site locations, keeping only observations that exist in ccd_az_leaid (i.e., only the selected school district)
merge_ccd_schsite = pd.merge(schools, ccd_az_leaid, left_on=merge_columns_schsite, right_on = merge_columns_ccd, how="inner")

# keep only the sabs that are in ccd dataframe
merge_sabs_ccd = pd.merge(merge_ccd_schsite, selected_schools, left_on=['ncessch'], right_on = ['ncessch'], how="inner")
# Set 'geometry_y' as the active geometry column, which is the attendance boundary polygons
merge_sabs_ccd = merge_sabs_ccd.set_geometry('geometry_y')
sabs_dg = Graph.from_geodataframe(merge_sabs_ccd, ignore_errors = True)


# Creating the initial partition: 
"""
Here, the initial partition is created for the short bursts. The seed plan is 
grown using Gerrychain's Partition class. Partition takes three arguments: a 
graph, an assignment of nodes to districts, and a dictionary of updaters. The 
relevant graph is the Arizona block groups graph. The recursive_tree_part 
function is used for the assignment argument, which partitions a tree into 
range(num_dist) parts of a population that are within epsilon = 10% of the 
ideal population. Then, we extract information from each district in the 
partition through the updaters. Specifically, we extract the number of 
cut edges, whether or not it is connected, its total population and Latino population.)
"""

# Count the number of polygons in the 'geometry' column of sabs. This is equivalent to counting
# the number of school attendance zones in the state

num_sabs = len(sabs['geometry']) 
# Assuming 'selected_district' is a GeoDataFrame with only one row, extract just the one district to transform from a series to a value
district_geometry = selected_district['geometry'].iloc[0]


# Create a new column to store SAB assignments
for node in bl_dg.nodes:
    bl_dg.nodes[node]['ncessch_assignment'] = None
    
# Create a dictionary to store the 'ncessch_assignment' values
ncessch_assignment_dict = {}
full_sabs_dict = {}

# Loop through census blocks in the selected district
for block_node in bl_dg.nodes:
    block_geometry = bl_dg.nodes[block_node]['geometry']
    block_num = bl_dg.nodes[block_node]['GEOID10']
    block_area = block_geometry.area

    # Initialize the best match and its overlap percentage
    best_match = None
    best_overlap = 0
    

    # List to store potential matches with less than 95% overlap
    potential_matches = []

    # Loop through SABs to check containment
    for sabs_node in sabs_dg.nodes:
        sabs_geometry = sabs_dg.nodes[sabs_node]['geometry_y']
        intersection_area = block_geometry.intersection(sabs_geometry).area
        intersection_district = sabs_geometry.intersection(district_geometry).area

        # Calculate overlap percentage over entire school district
        overlap_district = intersection_district / district_geometry.area
        # Calculate overlap percentage
        overlap_percentage = intersection_area / block_area

        # Keep only those with overlap less than 98% if there is more than one sabs
        # Count the number of nodes in the sabs_dg graph
        num_sabs_nodes = len(sabs_dg.nodes)
        if num_sabs_nodes > 1:
            if overlap_district < .9:
                potential_matches.append((sabs_node, overlap_percentage))
            else:
                print("The sabs intersected with more than 90% of the school district and was removed")
        else:
            potential_matches.append((sabs_node, overlap_percentage))

    # Determine the best match from potential matches
    if potential_matches:
        best_match, best_overlap = max(potential_matches, key=lambda x: x[1])

        # Assign ncessch if best overlap is greater than 0%
        if best_overlap > 0:
            ncessch = sabs_dg.nodes[best_match]['ncessch']
            block_num = bl_dg.nodes[block_node]['GEOID10']
            ncessch_assignment_dict[block_node] = ncessch
            full_sabs_dict[block_num] = ncessch
        else: 
            print(f"Less than or equal to 0% of block {block_node} is within any SAB")
    else:
        print(f"No suitable SAB found for block {block_node}")


# Set the 'ncessch_assignment' attribute for nodes in bl_dg
nx.set_node_attributes(bl_dg, ncessch_assignment_dict, name='ncessch_assignment')

# tally total number of blocks
num_blocks = len(ncessch_assignment_dict)

# Check if all blocks were linked to a sabs assignment 
no_sab_count = 0

# Iterate through each node in bl_dg
for node in bl_dg.nodes:
    # Check if 'ncessch_assignment' attribute is None or empty
    if bl_dg.nodes[node]['ncessch_assignment'] is None:
        no_sab_count += 1
        print(f"Block node {block_num} has no SAB assignment")

# Print the total count of blocks with no SAB
print(f"Total blocks with no SAB: {no_sab_count} out of {num_blocks}")

# now, manually assign a number to the missing nodes so that the nodes in the dict match the one in the dg
missing_nodes = [node for node in bl_dg.nodes if node not in ncessch_assignment_dict]
default_value = '-9999'  # Replace with an appropriate default value
for node in missing_nodes:
    ncessch_assignment_dict[node] = default_value


# Create the initial_partition using the dual graph from sabs
initial_partition = Partition(bl_dg, assignment=ncessch_assignment_dict, updaters={})
# Create a plot of the initial partition to make sure it loaded properly
initial_partition.plot()
plt.axis('off')
plt.legend()
plt.show()


#### now, re-assign blocks with '-9999' based on adjacency
# Identify and store adjacent nodes for each '-9999' node
unassigned_nodes = {node: list(bl_dg.neighbors(node)) for node in bl_dg.nodes() if ncessch_assignment_dict[node] == '-9999'}
# Relabel based on adjacent nodes
relabelled_nodes = set()  # To keep track of relabelled nodes
for node, neighbors in unassigned_nodes.items():
    for neighbor in neighbors:
        if ncessch_assignment_dict[neighbor] != '-9999' and (neighbor not in relabelled_nodes):
            ncessch_assignment_dict[node] = ncessch_assignment_dict[neighbor]
            relabelled_nodes.add(node)
            break  # Stop checking once a relabeling is done

# Update the partition with the new assignments
initial_partition = Partition(bl_dg, assignment=ncessch_assignment_dict, updaters={})

# Graph to check
initial_partition.plot()
plt.axis('off')
plt.legend()
plt.show()


"""
Now that we finished creating the initial partition, the following code will set up the necessary specifications
and constraints for running the short bursts.

"""

#### the population and race constraints should be based on census population data

## first, import the pop data by race
# import census data
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\code\Educational-Gerrymandering\stata\output\dta")
census_az = pd.read_stata("mergedcensusracedata_az.nvc.dta")

# Keep only the rows pertaining to census blocks in the leaid
geoid_list = arizona_bl_within_district['GEOID10'].tolist()
census_az_leaid = census_az[census_az['geoid'].isin(geoid_list)]


## now, reapportion students from schools to census blocks based on race proportions
# create a df of block to ncessch mapping
data = [(block_num, ncessch) for block_num, ncessch in full_sabs_dict.items()]
full_sabs_df = pd.DataFrame(data, columns=['block_num', 'ncessch'])
# list of unique ncessch in the leaid
unique_ncessch = full_sabs_df['ncessch'].unique().tolist()# Initialize an empty DataFrame for combining all apportioned_students data across schools
# initialize dataframe to store results of loop
apportioned_students_df = pd.DataFrame()
# for each ncessch, reapportion students by race from school to blocks
for ncessch in unique_ncessch:
    # Find rows in full_sabs_df where 'ncessch' matches the current ncessch and get the 'block_num' values
    block_list = full_sabs_df[full_sabs_df['ncessch'] == ncessch]['block_num'].tolist()
    # Keep only the census race data that pertains to blocks in the block list.
    census_filtered = census_az_leaid[census_az_leaid['geoid'].isin(block_list)]
    # Keep only the school data pertaining to this school
    ccd_filtered = merge_sabs_ccd[merge_sabs_ccd['ncessch'] == ncessch ]
    
    # # Now, reapportion students from each school to blocks by race
    # Define races to loop over
    races = ['blackpop', 'whitepop', 'hispanicpop', 'asianpop', 'nativeamericanpop', 'nhpipop', 'multiracepop']
    school_enrollments = {
        'blackpop': ccd_filtered['enrollblack'].values[0],
        'whitepop': ccd_filtered['enrollwhite'].values[0],
        'hispanicpop': ccd_filtered['enrollhispanic'].values[0],
        'asianpop': ccd_filtered['enrollasian'].values[0],
        'nativeamericanpop': ccd_filtered['enrollaian'].values[0],
        'nhpipop': ccd_filtered['enrollnhpi'].values[0],
        'multiracepop': ccd_filtered['enrollmultirace'].values[0]
     }   
    # Initialize a DataFrame to store apportioned students
    apportioned_students = pd.DataFrame(index=census_filtered.index, columns=races + ['total'])
    apportioned_students['geoid'] = census_filtered['geoid'].values
    apportioned_students['ncessch'] = ncessch

    # loop through each race
    for race in races:
        # Total number of students from race i at school j
        total_students = school_enrollments[race]
        # Calculate what percentage of students from school j of race i comes from block k
        percentages = census_filtered[race] / census_filtered[race].sum()
        
        # Calculate expected number of students for each block
        expected_students = np.round(percentages * total_students).fillna(0).astype(int)
        
        # Adjust for rounding issues to match total exactly by using numpy to probabilistically adjusts the apportioned students to ensure that the total number of students by race assigned to blocks matches the school's enrollment figures for that race.

        # diff between total number of students at the school and the expected value of students across all races
        difference = total_students - expected_students.sum()
        # if there is a discrepancy between actual total number of students and expected value:
        if difference != 0:
            # randomly selected block indices to adjust based on the size of the discrepancy (abs(difference)) and the distribution of percentages, which indicate how students are spread across blocks
            adjustments = np.random.choice(expected_students.index, abs(difference.astype(int)), replace=True, p=percentages.values)
            # iterates over the randomly chosen block indices
            for index in adjustments:
                # adjusts the num of students in the block by adding or subtracting 1 student, based on the sign of the difference
                expected_students[index] += np.sign(difference.astype(int))
        # save the reapportioned number of students per block as a new column in the df for the given race
        apportioned_students[race] = expected_students
    
    # sum the total across all races
    apportioned_students['total'] = apportioned_students[races].sum(axis=1)
    
    # append all data from each school to a single df
    apportioned_students_df = pd.concat([apportioned_students_df, apportioned_students.reset_index(drop=True)], ignore_index=True)
 
# check that the apportioned students total adds up correctly
total_enrollment = sum(school_enrollments.values())
apportioned_total_enrollment = apportioned_students['total'].sum()
print(f"Actual Total Enrollment: {total_enrollment}")
print(f"Apportioned Total Enrollment: {apportioned_total_enrollment}")
for race in races:
    apportioned_race_total = apportioned_students[race].sum()
    print(f"Total {race}: {apportioned_race_total} (Expected: {school_enrollments[race]})")


# Plot the distribution of races
# Filter out blocks where the total population is 0
apportioned_students_nonzero = apportioned_students[apportioned_students['total'] > 0]

# Now, plot the filtered DataFrame
apportioned_students_nonzero.drop('total', axis=1).plot(kind='bar', stacked=True, figsize=(10, 6), legend=True)
plt.title('Apportioned Students by Race Across Blocks (Non-Zero Populations Only)')
plt.xlabel('Census Block')
plt.ylabel('Number of Students')
# set x-axis tick labels to an empty list to reduce visual clutter
plt.xticks(ticks=[], labels=[])
plt.show()


### now, add apportioned_students df to bl_dg
# Convert GEOID10 to a string if it's not already, to match the geoid format in apportioned_students
apportioned_students_df['geoid'] = apportioned_students_df['geoid'].astype(str)

# Iterate through each node in the bl_dg graph
for node in bl_dg.nodes:
    # Get the GEOID10 of the current node
    geoid10 = bl_dg.nodes[node]['GEOID10']
    
    # Find the matching row in apportioned_students
    matching_row = apportioned_students_df[apportioned_students_df['geoid'] == geoid10]
    
    # If there is a matching row, update the node attributes with the data from apportioned_students
    if not matching_row.empty:
        # Convert matching row to a dictionary and update the node
        # Note: iloc[0] is used because matching_row is a DataFrame and we need the first (and only) row as a Series
        bl_dg.nodes[node].update(matching_row.iloc[0].to_dict())


# Update the initial partition with the population constraint
initial_partition = Partition(bl_dg, assignment=ncessch_assignment_dict, updaters={"population": Tally("total", alias = "population"), 
          "black population": Tally('blackpop', alias = "black population"),
          "hispanic population": Tally('hispanicpop', alias = "hispanic population"),
          "asian population": Tally('asianpop', alias = "asian population"),
          "native american population": Tally('nativeamericanpop', alias = "native american population"),
          "native hawaiian population": Tally('nhpipop', alias = "native hawaiian population"),
          "multiracial population": Tally('multiracepop', alias = "multiracial population"),
          "white population": Tally('whitepop', alias = "white population")
          })




#########

# Convert 'Polygon' geometries to their WKT representation and use them for assignment
#assignment_dict = {index: geometry.wkt for index, geometry in sabs['geometry'].iteritems()}

#initial_partition = Partition(arizona_bl_dg, 
  #                            assignment = assignment_dict, 
   #                           updaters = {"cut edges": cut_edges,
    #                                      "connectedness": lambda part: nx.is_connected(arizona_bl_dg.subgraph(part)),
     #                                     "population": Tally("total", alias="population")
      #                                    }
       #                       )

#initial_partition = Partition(arizona_bl_dg, 
#assignment = recursive_tree_part(arizona_bl_dg, range(num_sabs), ideal_pop, 
#  "total", 0.1, #population tolerance of 0.1 means we can deviate from the ideal population by up to 10%
#  10),  # number of attempts to balance population before moving on
#updaters={
#    "cut edges": cut_edges, 
#    "connectedness": (nx.is_connected(arizona_bl_dg)), 
#    "population": Tally("total", alias = "population")
#})




## Check that each partition has information saved:
#for district, latinopop in initial_partition["latinopop"].items():
#    print("District{}: {}". format(district, latinopop))
#for district, population in initial_partition["population"].items():
#    print("District{}: {}". format(district, population))

 

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

## Specify the parameters of the short bursts: 
burst_length = 100  # length of each burst
num_bursts = 50  # number of bursts in the run
total_steps = burst_length*num_bursts  # this is equal to num_bursts * burst_length.
initial_state = initial_partition   # initial_state specifies the seed plan 
                                    #the short bursts start from


## Defining the constraints: 
""" 
1) Population constraint: Each school must only have within 10% of their current enrollment
2) Time travel constraint: Later on, use the time travel API
"""

# 1) Population constraint: 
def capacities(partition):
    # Print the available keys in the partition's population data for debugging
    #print("Available ncessch keys in partition:", partition.keys())
    #print(partition["cut_edges"])
    
    # Iterate through each part's (sab's) population in the partition
    for district_id in partition.parts.keys():
        school_id = district_id
        #print(school_id)
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


## Defining the proposal function: 
""" The proposal function used is the Recombination Markov Chain, also known 
as ReCom. For a given plan, ReCom randomly selects two adjacent districts, 
merges them into a single district, and then randomly re-partitions them in a 
manner that maintains the population balance. """

# define the ideal pop for each school based on initial enrollment
ideal_pop = initial_partition['population']
# define the ideal population as the average population per sab
pop_target = sum(ideal_pop.values()) / len(ideal_pop)
proposal1 = partial(recom, pop_col = "total", pop_target = pop_target, 
                    epsilon = .5, node_repeats = 1)

"""
def debug_recom(partition):
    # Log before applying recom
    print("Before recom, population tally:", partition['population'])

    # Apply recom proposal
    new_partition = recom(partition, pop_col="total", pop_target=pop_target, epsilon=0.5, node_repeats=1)  # Customize these parameters
    # Since updaters run automatically, you should directly inspect the new partition's population
    print("After recom, population tally:", dict(new_partition['population']))

    # Force updater execution
    new_population = new_partition['population']
    print("After recom, population tally:", new_population)

    return new_partition

# Use this debug_recom function as your proposal function
proposal_function = debug_recom
"""



### creating a function for gini index

def calculate_gini(distributions):
    """
    Calculate a Gini-like index for inequality across racial distributions in districts.

    Args:
    distributions (list of lists): Each sublist represents the racial percentage distribution in a district.

    Returns:
    float: A Gini-like index representing inequality across these distributions.
    """
    
    # pip install inequality
    
    # import gini function
    from inequality.gini import Gini
    
    # Flatten the list of lists to get a single list of all racial percentages
    all_values = np.concatenate(distributions)
    # Sort the list
    all_values.sort()
   
    # Calculate Gini coefficient
    gini = Gini(all_values)
    
    return(gini)




# Running the short bursts: 
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

# for each burst:
for i in range(num_bursts):
    print("Burst:", i)
    list_of_gini = [] 
    chain = MarkovChain(
        proposal = proposal1, 
        # school capacity constraint
        constraints=[capacities],
        accept = accept.always_accept, 
        initial_state = initial_partition, 
        total_steps = burst_length) 
        
    # for each partition (plan) in each burst, which is equal to the burst length:
    for part in chain:  
        print("test")

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
            # Append the SAB's racial composition percentages to the distributions list
            distributions.append([black_perc, white_perc, hispanic_perc, asian_perc, nativeamerican_perc, nhpi_perc, multirace_perc])
     
        # now, calculate the gini index based on the racial distributions
        gini_index = calculate_gini(distributions)
        print(gini_index)
        # create master list of the gini indices per transition per burst. this contains the gini coefficient for each plan.
        list_of_gini += [gini_index]
            
        """    
            if maj_min_perc1 >= 0.5:
                maj_min_districts1 += 1 
                # Record the tally of majority minority districts per transition
                mm = [maj_min_districts1] 
                # Append the plan to this tally
                mm.append(part) 
                
    
        # Create master list of the number of majority minority districts 
        #per transition per burst. Recall that 
        # list_of_mm is already an empty list defined above the for loop. 
        list_of_mm += [mm] 
        """
        
        
    
    print(f"Gini Index for Racial Distribution Across Districts: {gini_index}")
    min_gini = [100]  # Initialize with 100, the largest possible gini index (100 = perfect inequality)
    min_gini_step = 0  # To store the step with the minimum Gini index
    # Iterating through the master list of the gini index per burst


    for step in range(len(list_of_gini)): 
        # Identifies the burst step
        print("step", step) 
        # Print the gini index for that step
        print("list_of_gini[step][0]:", list_of_gini[step][0]) 
        result.append(list_of_gini[step][0])
        # Print the minimum gini coefficient found across the burst
        print("min_gini[0]:", min_gini[0])  
        # Find the plan and the position of the minimum of list_of_gini
        if list_of_gini[step][0] <= min_gini[0]: 
            min_gini_step = step
            min_gini = list_of_gini[step]  



    # Prints the burst step that yielded the minimum gini index
    print('min_gini_step:', min_gini_step) 
    # Set the initial partition of the next burst to the most recent plan 
    #with the lowest gini index in the previous plan
    initial_partition = min_gini[1] 
    
    
print("result", result)


#Input results of short burst into an excel sheet. Repeat with other burst lengths
from openpyxl import Workbook
wb = Workbook()
ws =  wb.active
ws.append(result)
ws.title = "AZ Short Bursts Results"
wb.save(filename = 'az_shortbursts_results.xlsx')
wb.close()
 

#Create a boxplot with the results 
import pandas as pd
  

df = pd.read_csv('az_shortbursts_results_aggregated_unadj.csv')
boxplot = df.boxplot(figsize = (5, 5), vert = False)
boxplot.set_ylabel('Burst length')
boxplot.set_xlabel('Spread of Majority-Latino Districts Found per Burst Length')
boxplot.set_title(
    '''Spread of Majority-Latino Districts Found for Arizona 
    State House and Senate Districts (Unadjusted Population)''')



