# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:08:44 2024

@author: rinan

made some edits to check version control
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
leaid = "0404630"
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


# Turn into a dual graph
az_bl_dg = Graph.from_geodataframe(arizona_bl_within_district, ignore_errors=False)

# Step 2: Create a mapping of 'GEOID10' to geometry
geoid_to_geometry = arizona_bl_within_district.set_index('GEOID10')['geometry'].to_dict()



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
full_sabs_dict = {}

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

        # Assign ncessch if best overlap is greater than 0%
        if best_overlap > 0:
            ncessch = sabs_az_dg.nodes[best_match]['ncessch']
            block_num = az_bl_dg.nodes[block_node]['GEOID10']
            ncessch_assignment_dict[block_node] = ncessch
            full_sabs_dict[block_num] = ncessch
        else: 
            print(f"Less than or equal to 0% of block {block_node} is within any SAB")
    else:
        print(f"No suitable SAB found for block {block_node}")


# Set the 'ncessch_assignment' attribute for nodes in az_bl_dg
nx.set_node_attributes(az_bl_dg, ncessch_assignment_dict, name='ncessch_assignment')

# tally total number of blocks
num_blocks = len(ncessch_assignment_dict)

# Check if all blocks were linked to a sabs assignment 
no_sab_count = 0

# Iterate through each node in az_bl_dg
for node in az_bl_dg.nodes:
    # Check if 'ncessch_assignment' attribute is None or empty
    if az_bl_dg.nodes[node]['ncessch_assignment'] is None:
        no_sab_count += 1
        print(f"Block node {block_num} has no SAB assignment")

# Print the total count of blocks with no SAB
print(f"Total blocks with no SAB: {no_sab_count} out of {num_blocks}")

# now, manually assign a number to the missing nodes so that the nodes in the dict match the one in the dg
missing_nodes = [node for node in az_bl_dg.nodes if node not in ncessch_assignment_dict]
default_value = '-9999'  # Replace with an appropriate default value
for node in missing_nodes:
    ncessch_assignment_dict[node] = default_value


# Create the initial_partition using the dual graph from sabs_az
initial_partition = Partition(az_bl_dg, assignment=ncessch_assignment_dict, updaters={})
# Create a plot of the initial partition to make sure it loaded properly
initial_partition.plot()
plt.axis('off')
plt.legend()
plt.show()


#### now, re-assign blocks with '-9999' based on adjacency
# Identify and store adjacent nodes for each '-9999' node
unassigned_nodes = {node: list(az_bl_dg.neighbors(node)) for node in az_bl_dg.nodes() if ncessch_assignment_dict[node] == '-9999'}
# Relabel based on adjacent nodes
relabelled_nodes = set()  # To keep track of relabelled nodes
for node, neighbors in unassigned_nodes.items():
    for neighbor in neighbors:
        if ncessch_assignment_dict[neighbor] != '-9999' and (neighbor not in relabelled_nodes):
            ncessch_assignment_dict[node] = ncessch_assignment_dict[neighbor]
            relabelled_nodes.add(node)
            break  # Stop checking once a relabeling is done

# Update the partition with the new assignments
initial_partition = Partition(az_bl_dg, assignment=ncessch_assignment_dict, updaters={})

# Graph to check
initial_partition.plot()
plt.axis('off')
plt.legend()
plt.show()
