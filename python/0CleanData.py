# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:05:07 2024

@author: rinan
"""

""" 
This file imports national-level data and shapefiles and parses them down to the s
state level.
"""

state_abbrev = "TX"
statefip = "48"


# Import the relevant libraries to run short bursts: 
import geopandas as gpd
import os
import pandas as pd


# Function to create a directory if such a directory does not exist
def ensure_dir(directory_path):
    os.makedirs(directory_path, exist_ok=True)
    
    
# Import the NCES school districts shapefile
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\School District Boundaries_NCES EDGE")
districts = gpd.read_file('schooldistrict_sy1516_tl16.shp')
# combine LEAID into one (note: each obs has only one ELSDLEA, UNSDLEA, OR SCSDLEA id, so they do not need 
# to be separate columns)
districts['LEAID'] = districts.apply(
    lambda row: row['ELSDLEA'] if pd.notna(row['ELSDLEA']) 
    else (row['UNSDLEA'] if pd.notna(row['UNSDLEA']) 
    else row['SCSDLEA']),
    axis=1
)
# keep only Arizona
districts_state = districts[districts['STATEFP'] == statefip]
# define the directory path
districts_dir = f"C:\\Users\rinan\Box\Senior Thesis Data\School District Boundaries_NCES EDGE{statefip}"
ensure_dir(districts_dir)
# save only Arizona districts
districts_state.to_file(os.path.join(districts_dir, f'schooldistrict_sy1516_tl16_{statefip}.shp'))



# Import the NCES SABS shapefile:
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\SABS_NCES_15-16")
sabs = gpd.read_file('SABS_1516_Primary.shp')

# Save only the Arizona shapefile
sabs_state= sabs[sabs['stAbbrev'] == state_abbrev]
# define the directory path
sabs_dir=f'C:\\Users\rinan\Box\Senior Thesis Data\SABS_NCES_15-16\{statefip}'
ensure_dir(sabs_dir)
# save file
sabs_state.to_file(os.path.join(sabs_dir, f'SABS_1516_Primary_{statefip}.shp'))


### this path doesnt work for some reason
# Import the NCES school site point geometries
os.chdir(r"C:\Users\rinan\Box\Senior Thesis Data\Schools_NCES_15-16\EDGE_GEOCODE_PUBLICSCH_1516")
edge_geocode = gpd.read_file('EDGE_GEOCODE_PUBLICSCH_1516.shp')

# Save only the Arizona shapefile
edge_state = edge_geocode[edge_geocode['STFIP15']==statefip]
# define directory path
edge_dir =f'C:\Users\rinan\Box\Senior Thesis Data\Schools_NCES_15-16\{statefip}'
ensure_dir(edge_dir)
edge_state.to_file(os.path.join(edge_dir, f'EDGE_GEOCODE_1516_PUBLICSCH_{statefip}.shp'))




