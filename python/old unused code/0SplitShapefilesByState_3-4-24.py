# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 16:05:07 2024

@author: rinan
"""

""" 
This file imports national-level data and shapefiles and parses them down to the
state level.
"""

# Import the relevant libraries to run short bursts: 
import geopandas as gpd
import os
import pandas as pd

state_abbrev = "IL"
statefip = "17"

base_dir = r"C:\Users\rinan\Box\Senior Thesis"  # base directory
data_dir = os.path.join(base_dir, 'data') # output directory
raw_dir = os.path.join(base_dir, 'raw') # input directory


# define raw file names
districts_raw = 'schooldistrict_sy1516_tl16'
sabs_raw = 'SABS_1516_Primary'
# sabs_raw = 'SABS_1516
schools_raw = 'EDGE_GEOCODE_PUBLICSCH_1516'


def parse_shapefiles(raw_dir):
    districts_fname = 'schooldistrict_sy1516_tl16.shp'
    sabs_fname = 'SABS_1516_Primary.shp'
    # sabs_fname = 'SABS_1516.shp'
    # Uncomment this line ^ if you want to use composite (all levels) instead of primary
    schools_fname = 'EDGE_GEOCODE_PUBLICSCH_1516.shp'
    
    # Construct full paths for districts, sabs, and schools
    districts_raw_path = os.path.join(raw_dir, "School District Boundaries_NCES EDGE", districts_fname)
    sabs_raw_path = os.path.join(raw_dir, "SABS_NCES_15-16", sabs_fname)
    schools_raw_path = os.path.join(raw_dir, "EDGE_GEOCODE_PUBLICSCH_1516", schools_fname)
    
    # Use the full path to read the shapefile
    districts = gpd.read_file(districts_raw_path)
    sabs = gpd.read_file(sabs_raw_path)
    schools = gpd.read_file(schools_raw_path)

    return districts, sabs, schools

def select_shapefiles(districts, sabs, schools, state_abbrev, statefip):
    districts, sabs, schools = shapefiles
    
    # Consolidate leaid into a single leaid column for the districts geodataframe
    districts['LEAID'] = districts.apply(
        lambda row: row['ELSDLEA'] if pd.notna(row['ELSDLEA']) 
        else (row['UNSDLEA'] if pd.notna(row['UNSDLEA']) 
        else row['SCSDLEA']),
        axis=1
    )
    # Select the specific rows corresponding to the statefip or state_abbrev of the desired state
    my_district = districts[districts['STATEFP'] == statefip]
    my_sabs = sabs[sabs['stAbbrev'] == state_abbrev]
    my_schools = edge_geocode[edge_geocode['STFIP15']==statefip]
    
    return my_district, my_sabs, my_schools
    

def save_shapefiles(data_dir, statefip, shp_type):
    """ 
    Saves a lit of GeoDataFrames to a GeoPackage.
    """
    # Ensure the directory for the output file exists
    # Use a loop to ensure each directory exists
    for shp in shp_type:
        # define output directory path
        {shp}_dir = os.path.join(data_dir, statefip, shp)
        ensure_dir(output_directory)
        
        # define output file
        districts_output_path = os.path.join(output_directory, district_raw + '_' + str(statefip) + '.shp')
        sabs_output_path = os.path.join(output_directory, sabs_raw + '_' + str(statefip) + '.shp')
        schools_output_path = os.path.join(output_directory, schools_raw + '_' + str(statefip) + '.shp')
        return districts
    district_output_dir = os.path.join(data_dir, statefip, 'district')
    os.makedirs(output_directory, exist_ok=True)  # Creates the directory if it does not exist
    
    # save shapefiles
    my_district.to_file(districts_output_path)
    my_sabs.to_file(sabs_output_path)
    my_schools.to_file(schools_output_path)
    
    

# parse the shapefiles
parse_shapefiles(raw_dir)

# now, keep only the obs pertaining to my state
select_shapefiles(districts, sabs, schools, state_abbrev, statefip)


edge_state.to_file(file_path)



        
        
    for shp in shp_type:
        shp_type = gpd.read_file()

    

# save the shapefile pertaining only to my state
sabs_state= sabs[sabs['stAbbrev'] == state_abbrev]
edge_state = edge_geocode[edge_geocode['STFIP15']==statefip]

# save file
sabs_state.to_file(os.path.join(sabs_dir, f'SABS_1516_Primary_'+str(statefip)+'.shp'))


edge_path = os.path.join(edge_dir, f'EDGE_GEOCODE_1516_PUBLICSCH_' + str(statefip)+ '.shp' )
edge_state.to_file(edge_path)

        
        
        gdf = gpd.read_file(raw_path)
        if column:  # For districts and schools
            filtered_gdf = gdf[gdf[column] == statefip]
        else:  # For sabs
            filtered_gdf = gdf[gdf[abbrev_column] == state_abbrev]
        file_name = os.path.basename(raw_path).replace('.shp', f'_{statefip}.shp')
        filtered_gdf.to_file(os.path.join(data_dir, file_name))

    # Save shapefiles
    filter_and_save_shapefile(districts_raw_path, districts_data_dir, statefip, state_abbrev, column='STATEFP')
    filter_and_save_shapefile(sabs_raw_path, sabs_data_dir, statefip, state_abbrev, column=None, abbrev_column='stAbbrev')
    filter_and_save_shapefile(schools_raw_path, schools_data_dir, statefip, state_abbrev, column='STFIP15')
    
    
    
    



# Function to create a directory if such a directory does not exist
def ensure_dir(directory_path):
    os.makedirs(directory_path, exist_ok=True)


    
# Import the NCES school districts shapefile
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\raw\School District Boundaries_NCES EDGE")
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
districts_dir = os.path.join(data_dir, statefip, 'district')
ensure_dir(districts_dir)
# save only Arizona districts
districts_state.to_file(os.path.join(districts_dir, f'schooldistrict_sy1516_tl16_' + str(statefip) + '.shp'))



# Import the NCES SABS shapefile:
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\raw\SABS_NCES_15-16")
sabs = gpd.read_file('SABS_1516_Primary.shp')
# sabs = gpd.read_file('SABS_1516.shp')

# Save only the Arizona shapefile
sabs_state= sabs[sabs['stAbbrev'] == state_abbrev]
# define the directory path
sabs_dir=os.path.join(data_dir, statefip, 'sabs')
ensure_dir(sabs_dir)
# save file
sabs_state.to_file(os.path.join(sabs_dir, f'SABS_1516_Primary_'+str(statefip)+'.shp'))


### this path doesnt work for some reason
# Import the NCES school site point geometries
os.chdir(r"C:\Users\rinan\Box\Senior Thesis\raw\EDGE_GEOCODE_PUBLICSCH_1516")
edge_geocode = gpd.read_file('EDGE_GEOCODE_PUBLICSCH_1516.shp')

# Save only the Arizona shapefile
edge_state = edge_geocode[edge_geocode['STFIP15']==statefip]
# define directory path
edge_dir = os.path.join(data_dir, statefip, "schools") 
ensure_dir(edge_dir)
file_path = os.path.join(edge_dir, f'EDGE_GEOCODE_1516_PUBLICSCH_' + str(statefip)+ '.shp' )
edge_state.to_file(file_path)



