#! /usr/bin/python3
"""
This provides a measure of change in green vegitation over time by analyzing 
the Red and Near Infrared (NIR) bands from Planet Labs' PlanetScope 4-Band imagery.
The measure of green vegitation is provided by the normalized difference vegetation
index (NDVI) Red and NIR bands from PlanetScore 4-band images.

Author:
-------
Kevin Lacaille

Example:
--------
> python3 main.py task/data/ output/
Vegitation is getting more green over time, at a rate of: (15.1 +/- 0.3) % per day.

See Also:
---------
temporal_ndvi_analysis
"""

from temporal_ndvi_analysis import validate_inputs, get_data_filenames, extract_data, normalize_data, apply_water_mask, measure_ndvi, visualize_image, measure_dirt_veg_proportions, visualize_data, compute_rate_of_change
import numpy as np
import argparse
from alive_progress import alive_bar

if __name__ == "__main__":
    
    # Parse inputs
    parser = argparse.ArgumentParser(description='Measure the change in green vegetation \
                                                  using the Normalized Difference vegetation Index (NDVI)')
    parser.add_argument('data_directory', type=str, help='Input directory to data. \
                                                          Expected data type: PSScene4Band GeoTIFFs.')
    parser.add_argument('output_directory', type=str, help='Output directory for image. \
                                                            Output images and figures.')
    args = parser.parse_args()

    # Ensure inputs are valid
    validate_inputs(args)

    # Retrieve image and metadata file names
    image_filenames, metadata_filenames = get_data_filenames(args.data_directory)

    # Initialize arrays for incoming measurements
    num_images = len(image_filenames)
    all_proportion_dirt = np.zeros(num_images)
    all_proportion_veg = np.zeros(num_images)
    all_median_ndvi = np.zeros(num_images)
    all_days_since_acquisition = np.zeros(num_images)
    
    # Setup a pretty progressbar
    with alive_bar(num_images) as bar:
        
        # Cycle through each image
        for i in range(num_images):

            # Extract green, red, and NIR data from 4-Band imagery        
            band_green, band_red, band_nir, num_days_since_acquisition = extract_data(image_filenames[i], metadata_filenames[i])

            # Normalize data by their reflectance coefficient
            band_green, band_red, band_nir = normalize_data(metadata_filenames[i], band_green, band_red, band_nir)

            # Mask regions with water
            band_red, band_nir = apply_water_mask(band_green, band_red, band_nir)

            # Measure NDVI in un-masked regions
            ndvi = measure_ndvi(band_red, band_nir)

            # Visualize the NDVI maps
            visualize_image(ndvi, "NDVI", image_filenames[i], args.output_directory)

            # Measure the proportions of barren dirt and vegetation in maps
            proportion_dirt, proportion_veg = measure_dirt_veg_proportions(ndvi)

            # Add measurement to array
            all_median_ndvi[i] += np.nanmedian(ndvi)
            all_proportion_dirt[i] += proportion_dirt
            all_proportion_veg[i] += proportion_veg
            all_days_since_acquisition[i] += num_days_since_acquisition

            # Draw progress bar
            bar()
    
    # Sort the data by date
    sorting_index = np.argsort(all_days_since_acquisition)
    all_days_since_acquisition = all_days_since_acquisition[sorting_index]
    all_median_ndvi = all_median_ndvi[sorting_index]
    all_proportion_dirt = all_proportion_dirt[sorting_index]
    all_proportion_veg = all_proportion_veg[sorting_index]

    # Visualize the change in NDVI
    visualize_data(all_days_since_acquisition, all_median_ndvi, all_proportion_dirt, all_proportion_veg, args.output_directory)

    # Tell me how green the vegetation has gotten!    
    compute_rate_of_change(all_days_since_acquisition, all_median_ndvi, all_proportion_dirt, all_proportion_veg, image_filenames)