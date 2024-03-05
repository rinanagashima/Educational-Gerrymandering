# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:12:05 2024

@author: rinan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 08:51:21 2023

@author: rinan
"""


"""

THIS VERSION specifically changed the node keys of the az_bl_dg and sabs_assignment to the block number. 
It was posing issues since it appears that gerrychain only works with its default node keys. 
By changing the node key, the initial partition command could not recognize the geometry of the graph
because it was not stored in the node key, but rather in the node itself as a geometry attribute.


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
leaid = "0408850"
statefip = "04"
statecrs = "EPSG:32612"

# Import the NCES school districts shapefile
#os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\School District Boundaries_NCES EDGE")
#districts = gpd.read_file('schooldistrict_sy1516_tl16.shp')
# combine LEAID into one (note: each obs has only one ELSDLEA, UNSDLEA, OR SCSDLEA id, so they do not need 
# to be separate columns)
#districts['LEAID'] = districts.apply(
#    lambda row: row['ELSDLEA'] if pd.notna(row['ELSDLEA']) 
#    else (row['UNSDLEA'] if pd.notna(row['UNSDLEA']) 
#    else row['SCSDLEA']),
 #   axis=1
#)
# keep only Arizona
#districts_az = districts[districts['STATEFP'] == statefip]
# save only Arizona districts
#districts_az.to_file(r'C:\Users\rinan\Box\Senior Thesis Data\School District Boundaries_NCES EDGE\04\schooldistrict_sy1516_tl16_04.shp')

# Import the Arizona school districts
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\School District Boundaries_NCES EDGE\04")
districts = gpd.read_file('schooldistrict_sy1516_tl16_04.shp')
selected_district = districts[districts['GEOID'] == leaid]


# Import the Arizona census blocks graph: 
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\Census block shapefiles\tl_2010_04_tabblock10")
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


###### DELETE IF IT DOESNT MAKE SENSE ########
# create a ncessch column
# Ensure that the GEOID10 column is a string
arizona_bl_within_district['GEOID10'] = arizona_bl_within_district['GEOID10'].astype(str)

# Extract the last six digits of the GEOID10 column and create the ncessch column
arizona_bl_within_district['ncessch'] = arizona_bl_within_district['GEOID10'].str[3:10]

# Display the first few rows to verify the new column
print(arizona_bl_within_district[['GEOID10', 'ncessch']].head())


#040190041093097
#178011
#193692
################################
################################

# Turn into a dual graph
az_bl_dg = Graph.from_geodataframe(arizona_bl_within_district, ignore_errors=True)

# Step 2: Create a mapping of 'GEOID10' to geometry
geoid_to_geometry = arizona_bl_within_district.set_index('GEOID10')['geometry'].to_dict()

# Step 3: Assign geometries to nodes based on 'GEOID10'
for node, data in az_bl_dg.nodes(data=True):
    geoid = data['GEOID10']
    data['geometry'] = geoid_to_geometry.get(geoid, None)
    
# make the node key block_num
# Create a new graph
az_bl_dg_copy = Graph()

# Iterate over the nodes in the original graph
for node, data in az_bl_dg.nodes(data=True):
    # Extract the block number from the 'GEOID10' attribute
    block_num = data['GEOID10']

    # Add this node to the new graph with block_num as the key
    az_bl_dg_copy.add_node(block_num, **data)

az_bl_dg = az_bl_dg_copy


# Import the NCES SABS shapefile:
#os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\SABS_NCES_15-16")
#sabs = gpd.read_file('SABS_1516_Primary.shp')

# Save only the Arizona shapefile
#sabs_az = sabs[sabs['stAbbrev'] == 'AZ']
#sabs_az.to_file(r'C:\Users\rinan\Box\Senior Thesis Data\SABS_NCES_15-16\04\SABS_1516_Primary_04.shp') #Arizona fips code is 04


# Import the Arizona shapefile
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\SABS_NCES_15-16\04")
sabs_az = gpd.read_file('SABS_1516_Primary_04.shp')
selected_sabs_az = sabs_az[sabs_az['leaid'] == leaid]


# Reproject sabs_az to match the CRS of arizona_bl
selected_sabs_az = selected_sabs_az.to_crs(arizona_bl_within_district.crs)
# Create a dual graph
sabs_az_dg = Graph.from_geodataframe(selected_sabs_az, ignore_errors = True)


# Create a plot of the sabs_az to make sure it loaded properly
selected_sabs_az.plot()
plt.axis('off')
plt.show()


# Import the NCES school site point geometries
#os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\Schools_NCES_15-16\EDGE_GEOCODE_PUBLICSCH_1516")
#edge_geocode = gpd.read_file('EDGE_GEOCODE_PUBLICSCH_1516.shp')

# Save only the Arizona shapefile
#edge_az = edge_geocode[edge_geocode['STFIP15']=="04"]
#edge_az.to_file(r'C:\Users\rinan\Box\Senior Thesis Data\Schools_NCES_15-16\04\EDGE_GEOCODE_1516_PUBLICSCH_04.shp')

# Import the Arizona NCES school site point geometries
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\Schools_NCES_15-16\04")
schsite_az = gpd.read_file('EDGE_GEOCODE_1516_PUBLICSCH_04.shp')
# Reproject edge_az to match the CRS of arizona_bl
schsite_az = schsite_az.to_crs(arizona_bl.crs)
# Convert all column names to lowercase
schsite_az.columns = schsite_az.columns.str.lower()
# Create a plot of the edge_az to make sure it loaded properly
schsite_az.plot()
plt.axis('off')
plt.show()


# Ideal population calculation: 
""" Here, we assume that the ideal population of each school is equivalent to the current enrollment
of the school. In the future, we want to adjust this so that we consider school capacity and/or state-mandated
teacher-student ratios. 
"""

# import urban institute data (REPLACE with fully merged data later)
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\Stata code\urbaninst\output\dta")
ccd = pd.read_stata("mergedurbanschooldata.nvc.dta")
# Filter rows where 'fips' is equal to 'Arizona'
ccd_az = ccd[ccd['fips'] == 4]
# Print the filtered DataFrame
print(ccd_az)

# only keep the observations for the selected school district/leaid. note that ccd does not have leading 0 for the leaid
ccd_az_leaid = ccd_az[ccd_az['leaid'] == leaid[1:]]
print(ccd_az_leaid['school_name'])

# Assume the ideal population of each school is the current enrollment of the school
ideal_pop = ccd_az_leaid['totenrollment']

# Merge the urban institute data with the school site pt geometries
merge_columns_ccd = ['ncessch']
merge_columns_schsite = ['ncessch']
# merge ccd leaid and school site locations, keeping only observations that exist in ccd_az_leaid (i.e., only the selected school district)
merge_ccd_schsite = pd.merge(schsite_az, ccd_az_leaid, left_on=merge_columns_schsite, right_on = merge_columns_ccd, how="inner")

# keep only the sabs that are in ccd dataframe
merge_sabs_ccd = pd.merge(merge_ccd_schsite, selected_sabs_az, left_on=['ncessch'], right_on = ['ncessch'], how="inner")
# Set 'geometry_y' as the active geometry column, which is the attendance boundary polygons
merge_sabs_ccd = merge_sabs_ccd.set_geometry('geometry_y')
sabs_az_dg = Graph.from_geodataframe(merge_sabs_ccd, ignore_errors = True)


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

# Count the number of polygons in the 'geometry' column of sabs_az. This is equivalent to counting
# the number of school attendance zones in the state

num_sabs = len(sabs_az['geometry']) 
# Assuming 'selected_district' is a GeoDataFrame with only one row, extract just the one district to transform from a series to a value
district_geometry = selected_district['geometry'].iloc[0]


# Create a new column to store SAB assignments
for node in az_bl_dg.nodes:
    az_bl_dg.nodes[node]['ncessch_assignment'] = None
    
# Create a dictionary to store the 'ncessch_assignment' values
ncessch_assignment_dict = {}

# Loop through census blocks in the selected district
for block_node in az_bl_dg.nodes:
    block_geometry = az_bl_dg.nodes[block_node]['geometry']
    block_num = az_bl_dg.nodes[block_node]['GEOID10']
    block_area = block_geometry.area

    # Initialize the best match and its overlap percentage
    best_match = None
    best_overlap = 0
    

    # List to store potential matches with less than 95% overlap
    potential_matches = []

    # Loop through SABs to check containment
    for sabs_node in sabs_az_dg.nodes:
        sabs_geometry = sabs_az_dg.nodes[sabs_node]['geometry_y']
        intersection_area = block_geometry.intersection(sabs_geometry).area
        intersection_district = sabs_geometry.intersection(district_geometry).area

        # Calculate overlap percentage over entire school district
        overlap_district = intersection_district / district_geometry.area
        # Calculate overlap percentage
        overlap_percentage = intersection_area / block_area

        # Keep only those with overlap less than 98% if there is more than one sabs
        # Count the number of nodes in the sabs_az_dg graph
        num_sabs_nodes = len(sabs_az_dg.nodes)
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

        # Assign ncessch if best overlap is greater than 50%
        if best_overlap > 0:
            ncessch = sabs_az_dg.nodes[best_match]['ncessch']
            block_num = az_bl_dg.nodes[block_node]['GEOID10']
            ncessch_assignment_dict[block_node] = (ncessch, block_num)
        else:
            print(f"Less than 50% of block {block_node} is within any SAB")
    else:
        print(f"No suitable SAB found for block {block_node}")


# Set the 'ncessch_assignment' attribute for nodes in az_bl_dg
nx.set_node_attributes(az_bl_dg, ncessch_assignment_dict, name='ncessch_assignment')


# Update the ncessch_assignment_dict to use block_num as keys and only ncessch as values
ncessch_assignment_dict = {data['GEOID10']: (ncessch, block_num) for node, data in az_bl_dg.nodes(data=True)}

# Iterate through the ncessch_assignment_dict and keep only the ncessch part
for block_num, (ncessch, _) in ncessch_assignment_dict.items():
    ncessch_assignment_dict[block_num] = ncessch
    
# Check if all blocks were linked to a sabs assignment 
no_sab_count = 0

# Iterate through each node in az_bl_dg
for node in az_bl_dg.nodes:
    # Check if 'ncessch_assignment' attribute is None or empty
    if az_bl_dg.nodes[node]['ncessch_assignment'] is None:
        no_sab_count += 1
        print(f"Block node {block_num} has no SAB assignment")

# Print the total count of blocks with no SAB
print(f"Total blocks with no SAB: {no_sab_count} out of {num_sabs}")

# Set the 'ncessch_assignment' attribute for nodes in az_bl_dg
nx.set_node_attributes(az_bl_dg, ncessch_assignment_dict, name='ncessch_assignment')

# explicitly define the geometry for the initial partition
def extract_geometry(partition):
    return {district: [partition.graph.nodes[node]['geometry'] for node in partition.parts[district]]
            for district in partition.parts}

# Create the initial_partition using the dual graph from sabs_az
initial_partition = Partition(az_bl_dg, assignment=ncessch_assignment_dict, updaters={'geometry': extract_geometry})
# Create a plot of the initial partition to make sure it loaded properly
initial_partition.plot()
plt.axis('off')
plt.legend()
plt.show()


# Print the first few block assignments for verification
for i, node in enumerate(az_bl_dg.nodes):
    if i < 5:  # Print the first 5 block assignments
        print(f"Block {node} assignment: {az_bl_dg.nodes[node]['ncessch_assignment']}")
        
# replace each node key number in dict with block num
# Create a temporary dictionary to store the new nodes
temp_nodes = {}

# Iterate through each node in the graph
for node in list(az_bl_dg.nodes):
    # Retrieve the block number for this node
    block_num = az_bl_dg.nodes[node]['GEOID10']

    # Store the node attributes in the temporary dictionary with block_num as key
    temp_nodes[block_num] = az_bl_dg.nodes[node]

# Clear the original nodes from the graph
az_bl_dg.clear()

# Add the new nodes with updated keys to the graph
for block_num, attrs in temp_nodes.items():
    az_bl_dg.add_node(block_num, **attrs)
    
# Create a dictionary mapping census block identifiers to sabs assignments
ncessch_dict = {node: az_bl_dg.nodes[node]['ncessch_assignment'] for node in az_bl_dg.nodes}

# Create a new dictionary to store only the ncessch values
sabs_assignment = {}

# Iterate through the sabs_assignment dictionary
for block_num, value in ncessch_dict.items():
    # Extract only the ncessch value (which is the first element in the tuple)
    ncessch = value[0] if value is not None else None
    sabs_assignment[block_num] = ncessch

# Optionally, print the first few entries of the new dictionary for verification
for key, value in list(sabs_assignment.items())[:5]:
    print(f"Block {key} assignment: {value}")


# pickle the sabs assignment
with open('sabs_assignment.pkl', 'wb') as f:  # open a text file
    pickle.dump(sabs_assignment, f) # serialize the list






# Initialize an empty list to store the data
data = []

# Iterate through each item in the sabs_assignment dictionary
for block, assignment in sabs_assignment.items():
    # Check if the assignment is a tuple (and hence iterable)
    if isinstance(assignment, tuple):
        # Unpack the tuple
        block_num, ncessch = assignment
        # Append the block number and ncessch to the data list
        data.append((block_num, ncessch))
    else:
        # Handle cases where assignment is None or not a tuple
        block_num = block
        ncessch = -9999
        # Append the block number and ncessch to the data list
        data.append((block_num, ncessch))

# Create a DataFrame from the data list
df_sabs_assignment = pd.DataFrame(data, columns=['block_num', 'ncessch'])

# Display the DataFrame
print(df_sabs_assignment.head())

# Convert 'GEOID10' in arizona_bl_within_district to match the format of 'block_num' in df_sabs_assignment
arizona_bl_within_district['block_num'] = arizona_bl_within_district['GEOID10']

# Merge the two DataFrames on the 'block_num' column
merged_df = arizona_bl_within_district.merge(df_sabs_assignment, on='block_num', how='left')

# Display the merged DataFrame
print(merged_df.head())


# Unique sabs assignments
unique_assignments = merged_df['ncessch_x'].unique()

# Assign colors - using a color map
colors = plt.cm.get_cmap('viridis', len(unique_assignments))

# Create a color dictionary
color_dict = {assignment: colors(i) for i, assignment in enumerate(unique_assignments)}

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

for assignment in unique_assignments:
    # Filter blocks by sabs_assignment
    data = merged_df[merged_df['ncessch_x'] == assignment]
    
    # Plot each group with its color
    data.plot(ax=ax, color=color_dict[assignment], label=str(assignment))

# Customization
ax.set_title('Census Blocks within Selected District by SAB Assignment')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Create a legend
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, title='SAB Assignments')

plt.show()




#########

# Convert 'Polygon' geometries to their WKT representation and use them for assignment
#assignment_dict = {index: geometry.wkt for index, geometry in sabs_az['geometry'].iteritems()}

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
total_steps = 5000  # this is equal to num_bursts * burst_length.
initial_state = initial_partition   # initial_state specifies the seed plan 
                                    #the short bursts start from


## Defining the constraints: 
""" 
1) Compactness constraint: To keep the districts as compact as the original 
    plan, we bound the number of cut edges at 2 times the number of cut edges 
    as the initial plan.
2) Population constraint: To ensure that the chain only generates partitions 
    that are within epsilon of the ideal population. the 
    gerrychain.constraints.within_percent_of_ideal_population function 
    accomplishes exactly this. 
"""
# 1) Compactness constraint:
compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]), 
    2*len(initial_partition["cut_edges"])
)

# 2) Population constraint: 
pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.1)



## Defining the proposal function: 
""" The proposal function used is the Recombination Markov Chain, also known 
as ReCom. For a given plan, ReCom randomly selects two adjacent districts, 
merges them into a single district, and then randomly re-partitions them in a 
manner that maintains the population balance. """
proposal1 = partial(recom, pop_col = "total", pop_target = ideal_pop, 
                    epsilon = 0.1, node_repeats = 1)

# Running the short bursts: 
"""
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

for i in range(num_bursts):
    print("i:", i)
    list_of_mm = [] 
    Chain3 = MarkovChain(
        proposal = proposal1, 
        constraints = [compactness_bound, pop_constraint],
        # A every proposed plan that meets the compactness and population constraints
        accept = always_accept, 
        initial_state = initial_partition, 
        total_steps = burst_length) 
        # For loop for each transition in a single burst. This equals burst length.
    for part in Chain3:  
        # Here we calculate the number of majority minority districts: 
        # First, list the latinopop and total population for every node in the plan
        latinopop4 = list((part["latinopop"].items())) 
        population4 = list((part["population"].items())) 
        # Set the number of majority minority districts to 0 initially
        maj_min_districts1 = 0 
        # For loop for every district in the plan
        for i, j in zip(latinopop4, population4):
            # Add 1 to the number of majority minority districts if we find 
            #a district where latinopop/population > 0.5
            maj_min_perc1 = (i[1]/j[1])  
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
        
    
    print("list_of_mm:", list_of_mm) 
    max1 = [0] 
    max1_a = 0
    # Iterating through the master list of the number of majority minority 
    #districts per burst 

    for a in range(len(list_of_mm)): 
        # Identifies the burst step
        print("a", a) 
        # Print the number of majority_minority districts for that step
        print("list_of_mm[a][0]:", list_of_mm[a][0]) 
        result.append(list_of_mm[a][0])
        # Print the maximum found across the burst
        print("max1[0]:", max1[0])  
        # Find the plan and the position of the maximum of list_of_mm
        if list_of_mm[a][0] >= max1[0]: 
            max1_a = a 
            max1 = list_of_mm[a]  



    # Prints the burst step that yielded the maximum number of 
    #majority_minority districts 
    print('max_a:', max1_a) 
    # Set the initial partition of the next burst to the most recent plan 
    #with the highest number of majority minority districts in the previous plan
    initial_partition = max1[1] 
    
print("result", result)


#Input results of short burst into an excel sheet. Repeat with other burst lengths
from openpyxl import Workbook
wb = Workbook()
ws =  wb.active
ws.append(result)
ws.title = "AZ Short Bursts Results"
wb.save(filename = 'az_shortbursts_results_unadj.xlsx')
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



