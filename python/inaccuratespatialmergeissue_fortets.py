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
import random 
import networkx as nx
import geopandas as gpd
import os
import pandas as pd
from openpyxl import Workbook

# Import attributes of gerrychain that we need to create the initial partition: 
from gerrychain import Graph, Partition, updaters
from gerrychain.updaters import Tally


# Import functions from other files
#from parser import parse_shapefiles, select_shapefiles
from geopackage import read_shapefiles_gpkg
from visualizations import plot_all, plot_initialpartition, plot_stackedbar, plot_histogram
from reapportionment import reapportion_students, apportioned_to_dg
from markovchain import shortbursts, proposal, make_capacities_constraint, calculate_partition_diversity

"""This is to make the code more replicable. For example, if we want the 
same result twice, we can run the code with exactly the same random seed. """
random.seed(48)


'''
Framework for automating repeating this entire file for different states

def read_csv(excel sheet)
    make function that reads csv file into an array where index 1 (row) is state and index 2 (col) is either fip or crs

def get_fip_crs(state):
    state_data = read_csv(excel sheet)
    fip = state_data[state]['fip']
    crs = state_data[state]['crs']
    return fip, crs

# for AZ and TX
states = ['AZ', 'TX']  # put the rest of your states here
for state in states:
    fip, crs = get_fip_crs(state)
    # literally the rest of the file
'''

# set district number, state fip, and state crs
leaid = "0402860"
# leaid = "0409060"
statefip = "04"
fipnum = 4
statecrs = "EPSG:32612"
state_abbrev = "az"

# Get Senior Thesis Directory
python_dir = os.getcwd()
#python_dir = r"C:\Users\rinan\Box\Senior Thesis\code\Educational-Gerrymandering\python"
edu_gerry_dir = os.path.dirname(python_dir)
code_dir = os.path.dirname(edu_gerry_dir)
SeniorThesis_dir = os.path.dirname(code_dir)

# Name other useful directories
data_dir = os.path.join(SeniorThesis_dir, 'data')
output_dir = os.path.join(SeniorThesis_dir, 'output')
state_output_dir = os.path.join(output_dir, statefip, leaid)
stata_dir = os.path.join(edu_gerry_dir, 'stata')


# Shapefiles for specific district
output_file_my = os.path.join(data_dir, statefip, 'geopackages', leaid, 'my_shapefiles.gpkg')

# Load Shapefiles from GeoPackage
my_shapefiles_loaded = read_shapefiles_gpkg(output_file_my)
#print(f"my_shapefiles loaded from GeoPackage for LEAID={leaid}")

# list layers in geopackage
#layers = fiona.listlayers(output_file_my)
#print(layers)

# read in the layers as GeoDataframes
blocks = gpd.read_file(output_file_my, layer = 'layer_0')
district = gpd.read_file(output_file_my, layer = 'layer_1')
schools = gpd.read_file(output_file_my, layer = 'layer_2')
sabs = gpd.read_file(output_file_my, layer = 'layer_3')

plot_all(blocks, district, schools, sabs, leaid, state_output_dir)


# Turn into a dual graph
bl_dg = Graph.from_geodataframe(blocks, ignore_errors=False)

# TODO: figure out if this is needed
# # Step 2: Create a mapping of 'GEOID10' to geometry
# geoid_to_geometry = blocks.set_index('GEOID10')['geometry'].to_dict()


# Create a dual graph of sabs
sabs_dg = Graph.from_geodataframe(sabs, ignore_errors = True)

# Ideal population calculation: 
""" Here, we assume that the ideal population of each school is equivalent to the current enrollment
of the school. In the future, we want to adjust this so that we consider school capacity and/or state-mandated
teacher-student ratios. 
"""

# import urban institute data (REPLACE with fully merged data later)
stata_output_dir = os.path.join(stata_dir, 'output')
dta_dir = os.path.join(stata_output_dir, 'dta')
sdd_path = os.path.join(dta_dir, "mergedurbanschooldata.nvc.dta")  # School Demographic Data file path

sdd = pd.read_stata(sdd_path) 
# only keep the observations for the selected state and school district/leaid.
my_sdd = sdd[(sdd['fips'] == fipnum) & (sdd['leaid'] == leaid)]
#print(my_sdd['school_name'])

# merge sdd leaid and school site locations, keeping only observations that exist in my_sdd (i.e., only the selected school district)
merge_sdd_schools = pd.merge(schools, my_sdd, on = ['ncessch'], how="inner")
# keep only the sabs that are in sdd dataframe
merge_sabs_sdd = pd.merge(merge_sdd_schools, sabs, left_on=['ncessch'], right_on = ['ncessch'], how="inner")
# Set 'geometry_y' as the active geometry column, which is the attendance boundary polygons
merge_sabs_sdd = merge_sabs_sdd.set_geometry('geometry_y')
sabs_dg = Graph.from_geodataframe(merge_sabs_sdd, ignore_errors = True)


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
# Assuming 'district' is a GeoDataFrame with only one row, extract just the one district to transform from a series to a value
district_geometry = district['geometry'].iloc[0]


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
            #else:
                #print("The sabs intersected with more than 90% of the school district and was removed")
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
        #else: 
            #print(f"Less than or equal to 0% of block {block_node} is within any SAB")
    #else:
        #print(f"No suitable SAB found for block {block_node}")


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
        #print(f"Block node {block_num} has no SAB assignment")

# Print the total count of blocks with no SAB
print(f"Total blocks with no SAB: {no_sab_count} out of {num_blocks}")

# now, manually assign a number to the missing nodes so that the nodes in the dict match the one in the dg
missing_nodes = [node for node in bl_dg.nodes if node not in ncessch_assignment_dict]
default_value = '-9999'  # Replace with an appropriate default value
for node in missing_nodes:
    ncessch_assignment_dict[node] = default_value


# Create the initial_partition using the dual graph from sabs
initial_partition = Partition(bl_dg, assignment=ncessch_assignment_dict, updaters={})
# plot and save figure in output folder
plot_initialpartition(initial_partition, state_output_dir, f'{leaid}_initialpartition_orig.png')

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
# plot and save figure in output folder
plot_initialpartition(initial_partition, state_output_dir, f'{leaid}_initialpartition_corrected.png')



"""
Now that we finished creating the initial partition, the following code will set up the necessary specifications
and constraints for running the short bursts.

"""

#### the population and race constraints should be based on census population data

## first, import the pop data by race
# import census data
census_path = os.path.join(dta_dir, "mergedcensusracedata_az.nvc.dta")  # Census data file path
census = pd.read_stata(census_path)

# Keep only the rows pertaining to census blocks in the leaid
geoid_list = blocks['GEOID10'].tolist()
my_census = census[census['geoid'].isin(geoid_list)]


## now, reapportion students from schools to census blocks based on race proportions
apportioned_students_df, apportioned_students_nonzero = reapportion_students(full_sabs_dict, my_census, merge_sabs_sdd)
# Now, plot the filtered DataFrame
plot_stackedbar(apportioned_students_nonzero)
### now, add apportioned_students df to bl_dg
bl_dg = apportioned_to_dg(apportioned_students_df, bl_dg)


# Update the initial partition with the population constraint
updaters = {"population": Tally("total", alias = "population"), 
          "black population": Tally('blackpop', alias = "black population"),
          "hispanic population": Tally('hispanicpop', alias = "hispanic population"),
          "asian population": Tally('asianpop', alias = "asian population"),
          "native american population": Tally('nativeamericanpop', alias = "native american population"),
          "native hawaiian population": Tally('nhpipop', alias = "native hawaiian population"),
          "multiracial population": Tally('multiracepop', alias = "multiracial population"),
          "white population": Tally('whitepop', alias = "white population")
          }
initial_partition = Partition(bl_dg, assignment=ncessch_assignment_dict, updaters=updaters)
# calculate dissimilarity index for initial partition
initial_dissim_shannon, initial_dissim_simpson = calculate_partition_diversity(initial_partition)


## Specify the parameters of the short bursts: 
burst_length = 100  # length of each burst
num_bursts = 50  # number of bursts in the run
proposal1 = proposal(initial_partition)
capacities = make_capacities_constraint(initial_partition)
# run the short bursts markov chain
results_shannon, results_simpson = shortbursts(burst_length, num_bursts, initial_partition, proposal1, capacities)


# Input results of short burst into an excel sheet.
wb = Workbook()
ws =  wb.active
ws.title = f"{statefip} {leaid} Short Bursts Results"
# create a column header
ws.append(['Gini from Simpsons'])
# transpose the list (row of data) into a column of data
for item in results_simpson:
    ws.append([item]) # this makes each item its own row
filename = os.path.join(state_output_dir, f'{state_abbrev}_{leaid}_simpsons_shortbursts_results.xlsx')
wb.save(filename = filename)
wb.close()
 

# now, create and save a histogram of results
# add initial dissimilarity score to all scores
all_scores = []
all_scores = results_simpson + [initial_dissim_simpson]
plot_histogram(all_scores, initial_dissim_shannon, state_abbrev, state_output_dir, leaid)

