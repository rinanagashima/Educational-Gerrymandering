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
import fiona

# Import attributes of gerrychain that we need to create the initial partition: 
from gerrychain import Graph, Partition, Election, proposals, updaters, constraints, accept 
from gerrychain.updaters import cut_edges, Tally
from gerrychain.tree import recursive_tree_part


"""This is to make the code more replicable. For example, if we want the 
same result twice, we can run the code with exactly the same random seed. """
random.seed(48)

# set district number, state fip, and state crs
leaid = "0402860"
# leaid = "0409060"
statefip = "04"
statecrs = "EPSG:32612"


'''
Inputs: 
    - State Code
    - State CRS
    - data_dir: directory of data
Outputs: Array of the following GeoDataFrames
    - blocks: Census Blocks
    - district: school district boundaries
    - schools: school point locations
    - sabs: attendance boundaries
Description: Parses blocks, districts, schools, SABS for a given state
Example Usage: shapefiles = parse_shapefiles(state_code)
'''
def parse_shapefiles(state_code, state_crs, data_dir):
    if not isinstance(state_code, str):
        print("Error: State Code is not a string")
        return None
        
    # File names for blocks, districts, schools, SABS
    blocks_fname = 'tl_2010_' + state_code + '_tabblock10' + '.shp'
    district_fname = 'schooldistrict_sy1516_tl16_' + state_code + '.shp'  # Name of the district file
    schools_fname = 'EDGE_GEOCODE_1516_PUBLICSCH_' + state_code + '.shp'
    sabs_fname = 'SABS_1516_Primary_' + state_code + '.shp'
    # sabs_fname = 'SABS_1516_' + state_code + '.shp'
    # Uncomment this line^ if you want to use regular instead of primary
    
    # Construct full paths for blocks, districts, schools, SABS
    state_dir = os.path.join(data_dir, state_code)
    blocks_path = os.path.join(state_dir, 'blocks', blocks_fname)
    district_path = os.path.join(state_dir, 'district', district_fname)
    schools_path = os.path.join(state_dir, 'schools', schools_fname)
    sabs_path = os.path.join(state_dir, 'sabs', sabs_fname)    
    
    # Use the full path to read the shapefile with given CRS
    blocks = gpd.read_file(blocks_path).to_crs(state_crs)
    districts = gpd.read_file(district_path).to_crs(state_crs)
    schools = gpd.read_file(schools_path).to_crs(state_crs)
    sabs = gpd.read_file(sabs_path).to_crs(state_crs)


    return [blocks, districts, schools, sabs]

'''
Inputs:
    - statewide_shapefiles: array of all blocks/districts/schools/sabs for state
    - leaid: ID for desired district
Outputs:
    - my_shapefiles: shapefiles for specified district
Description: Takes shapefiles for the whole state and returns only the district you need
'''
def select_shapefiles(shapefiles, leaid):
    blocks, districts, schools, sabs = shapefiles 
    
    # Select the specific row corresponding to the leaid of desired district   
    my_district = districts[districts['GEOID'] == leaid]
    my_sabs = sabs[sabs['leaid'] == leaid]
    
    # Ensure both geodataframes have the same CRS
    if blocks.crs != my_district.crs:
        print("Error: Different CRS")
        return None
      
    # Reset the index of blocks and keep the old index as a column
    # This is because gpd.overlay may mix around indices, so we keep the OG index as a column in case we need it
    blocks_reset = blocks.reset_index()

    # Perform an intersection to calculate the overlap area
    intersect = gpd.overlay(blocks_reset, my_district, how='intersection')

    # Calculate the area of each block and each intersection
    blocks_reset['area'] = blocks_reset.geometry.area
    intersect['overlap_area'] = intersect.geometry.area

    # Assuming 'index' is the name of the original blocks index in intersect
    blocks_reset = blocks_reset.merge(intersect[['overlap_area', 'index']], on='index', how='left')

    # Calculate the overlap percentage
    blocks_reset['overlap_percentage'] = (blocks_reset['overlap_area'] / blocks_reset['area']) * 100

    # Filter to keep only blocks with 90% or more overlap bc 100% overlap resulted in some perimeter blocks being left out
    my_blocks = blocks_reset[blocks_reset['overlap_percentage'] > 90]

    # Use within to find schools within district
    if len(my_district) > 0:  # Check if district has anything in it
        district_polygon = my_district.geometry.unary_union  # In case my_district has more than one polygon
        my_schools = schools[schools.geometry.within(district_polygon)]
    else:
        print("Error: District length is not greater than 0")
        return None

    return [my_blocks, my_district, my_schools, my_sabs]

def save_shapefiles_gpkg(geo_dataframes, output_file):
    """
    Saves a list of GeoDataFrames to a GeoPackage.
    """
    # Ensure the directory for the output file exists
    output_directory = os.path.dirname(output_file)
    os.makedirs(output_directory, exist_ok=True)  # Creates the directory if it does not exist
    for i, gdf in enumerate(geo_dataframes):
        # Define layer name based on the GeoDataFrame's content
        layer_name = f"layer_{i}"
        # Save the GeoDataFrame to the GeoPackage
        gdf.to_file(output_file, layer=layer_name, driver="GPKG", index=False)

def read_shapefiles_gpkg(input_file):
    """
    Reads layers from a GeoPackage and returns them as a list of GeoDataFrames.
    """
    import geopandas as gpd
    layers = fiona.listlayers(input_file)
    geo_dataframes = [gpd.read_file(input_file, layer=layer) for layer in layers]
    return geo_dataframes


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

# Handle Directories
python_dir = os.getcwd()  # Get current directory
edu_gerry_dir = os.path.dirname(python_dir)
SeniorThesis_dir = os.path.dirname(edu_gerry_dir)
data_dir = os.path.join(SeniorThesis_dir, 'data')


# Parse shapefiles for given state
statewide_shapefiles = parse_shapefiles(statefip, statecrs, data_dir)
print("statewide_shapefiles created")
# print(statewide_shapefiles)
# print("-----------------------------------------------------------------------------------")
# print("-----------------------------------------------------------------------------------")
# print("-----------------------------------------------------------------------------------")

# Save statewide data to GeoPackage
output_file_statewide = os.path.join(data_dir, statefip, 'geopackages', 'statewide_shapefiles.gpkg')
save_shapefiles_gpkg(statewide_shapefiles, output_file_statewide)
print("statewide_shapefiles saved to GeoPackage")

# Read Statewide GeoPackage
statewide_shapefiles_loaded = read_shapefiles_gpkg(output_file_statewide)
print("statewide_shapefiles loaded from GeoPackage")
my_shapefiles = select_shapefiles(statewide_shapefiles_loaded, leaid)
print("my_shapefiles created")
# # print(my_shapefiles)
# print("-----------------------------------------------------------------------------------")
# print("-----------------------------------------------------------------------------------")
# print("-----------------------------------------------------------------------------------")

output_file_my = os.path.join(data_dir, statefip, 'geopackages', leaid, 'my_shapefiles.gpkg')
save_shapefiles_gpkg(my_shapefiles, output_file_my)
print("my_shapefiles saved to GeoPackage")

my_shapefiles_loaded = read_shapefiles_gpkg(output_file_my)
print("my_shapefiles loaded from GeoPackage")


