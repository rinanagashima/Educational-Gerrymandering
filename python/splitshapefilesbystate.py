# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 15:59:06 2024

@author: rinan
"""

import os
import geopandas as gpd
import pandas as pd

# Change as needed
data_dir = r'C:\Users\rinan\Box\Senior Thesis\data'
state_abbrev = "IL"
statefip = "17"


def ensure_dir(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def filter_and_save_shapefile(raw_path, output_dir, state_abbrev, statefip, file_suffix, column='STATEFP'):
    """
    Filters a shapefile based on state FIPS code or abbreviation and saves the filtered shapefile to a specified directory.

    Parameters:
    - raw_path: Path to the raw shapefile.
    - output_dir: Directory to save the filtered shapefile.
    - state_abbrev: State abbreviation to filter by (if applicable).
    - statefip: State FIPS code to filter by.
    - file_suffix: Suffix to add to the filename when saving.
    - column: Column name to filter by. Default is 'STATEFP'.
    """
    # Read the raw shapefile
    gdf = gpd.read_file(raw_path)
    
    # If working with school districts, combine LEAID columns before filtering
    if 'schooldistrict' in raw_path:
        gdf['LEAID'] = gdf.apply(
            lambda row: row['ELSDLEA'] if pd.notna(row['ELSDLEA']) 
            else (row['UNSDLEA'] if pd.notna(row['UNSDLEA']) 
            else row['SCSDLEA']),
            axis=1
        )
    
    # Filter the GeoDataFrame based on state FIPS code or abbreviation
    if column == 'STATEFP':
        filtered_gdf = gdf[gdf[column] == statefip]
    else:
        filtered_gdf = gdf[gdf[column] == state_abbrev]
    
    # Define the output path
    output_path = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(raw_path))[0]}_{statefip}.shp')
    
    # Save the filtered GeoDataFrame
    ensure_dir(output_dir)
    filtered_gdf.to_file(output_path)


# Directories for raw shapefiles
raw_dir = r'C:\Users\rinan\Box\Senior Thesis\raw'
districts_raw_path = os.path.join(raw_dir, 'School District Boundaries_NCES EDGE', 'schooldistrict_sy1516_tl16.shp')
sabs_raw_path = os.path.join(raw_dir, 'SABS_NCES_15-16', 'SABS_1516_Primary.shp')
schools_raw_path = os.path.join(raw_dir, 'EDGE_GEOCODE_PUBLICSCH_1516', 'EDGE_GEOCODE_PUBLICSCH_1516.shp')

# Call the function for each shapefile
filter_and_save_shapefile(districts_raw_path, os.path.join(data_dir, statefip, 'district'), state_abbrev, statefip, 'district')
filter_and_save_shapefile(sabs_raw_path, os.path.join(data_dir, statefip, 'sabs'), state_abbrev, statefip, 'sabs', column='stAbbrev')
filter_and_save_shapefile(schools_raw_path, os.path.join(data_dir, statefip, 'schools'), state_abbrev, statefip, 'schools', column='STFIP15')




# check if file saved properly

# Define the path to the district shapefile you saved
output_dir = r'C:\Users\rinan\Box\Senior Thesis\data'
filename = f'schooldistrict_sy1516_tl16_{statefip}.shp'
file_path = os.path.join(output_dir, statefip, 'district', filename)

# Try to load the shapefile
district = gpd.read_file(file_path)
print(district.head())  # Display the first few rows of the dataframe
print(district.columns)
print(district['STATEFP'])
