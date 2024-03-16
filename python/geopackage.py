import fiona
import geopandas as gpd
import os

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
    layers = fiona.listlayers(input_file)
    geo_dataframes = [gpd.read_file(input_file, layer=layer) for layer in layers]
    return geo_dataframes