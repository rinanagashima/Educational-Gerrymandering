# Import the relevant libraries to run short bursts: 
import geopandas as gpd
import os
from geopackage import save_shapefiles_gpkg, read_shapefiles_gpkg

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
    statewide_shapefiles = [blocks, districts, schools, sabs]
    
    # Save statewide data to GeoPackage
    output_file_statewide = os.path.join(data_dir, state_code, 'geopackages', 'statewide_shapefiles.gpkg')
    save_shapefiles_gpkg(statewide_shapefiles, output_file_statewide)
    print(f"statewide_shapefiles saved to GeoPackage for statefip={state_code}")

    return statewide_shapefiles

'''
Inputs:
    - statewide_shapefiles: array of all blocks/districts/schools/sabs for state
    - leaid: ID for desired district
Outputs:
    - my_shapefiles: shapefiles for specified district
Description: Takes shapefiles for the whole state and returns only the district you need
'''
def select_shapefiles(state_code, shapefiles, leaid, data_dir):
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

    my_shapefiles = [my_blocks, my_district, my_schools, my_sabs]
    
    # Save Shapefiles to GeoPackage
    output_file_my = os.path.join(data_dir, state_code, 'geopackages', leaid, 'my_shapefiles.gpkg')
    save_shapefiles_gpkg(my_shapefiles, output_file_my)
    print("my_shapefiles saved to GeoPackage")
    
    return my_shapefiles


'''
Inputs:
    - data_dir: Directory called "data" where your state shapefile data is located
    - leaid: LEAID
    - statefip: State Code Number (as a string)
    - statecrs: State Coordinate System
Outputs:
Description:
    - Call parser() using this current file (a2_parser.py) to save shapefiles to a GeoPackage
    - If you want the shapefiles in a variable, call read_shapefiles
'''
def parser():
    
    leaid = "0402860"
    statefip = "04"
    statecrs = "EPSG:32612"

    # Handle Directories
    python_dir = os.getcwd()  # Get current directory
    edu_gerry_dir = os.path.dirname(python_dir)
    code_dir = os.path.dirname(edu_gerry_dir)
    SeniorThesis_dir = os.path.dirname(code_dir)
    data_dir = os.path.join(SeniorThesis_dir, 'data')
    
    # Parse shapefiles for given state
    statewide_shapefiles = parse_shapefiles(statefip, statecrs, data_dir)
    print(f"statewide_shapefiles created for statefip={statefip}")
    
    # Select specific shapefiles for district LEAID
    my_shapefiles = select_shapefiles(statewide_shapefiles, leaid, data_dir)
    print(f"my_shapefiles created for LEAID={leaid}")


# Uncomment this if you want to run JUST this a2_parser.py file.
# If calling parser() from a different file, comment this out.
#parser()
