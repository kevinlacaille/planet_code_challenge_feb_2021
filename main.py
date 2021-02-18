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
> python3 main.py PSScene4Band output
Vegitation is getting more green over time, at a rate of: (15.1 +/- 0.3) % per day.

See Also:
---------
temporal_ndvi_analysis
"""

from temporal_ndvi_analysis import validate_inputs, get_data_filenames, extract_data, normalize_data, apply_water_mask, measure_ndvi, visualize_image, compute_rate_of_change
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

    # Retrieve image and metadata file names, and time since their observation
    image_filenames, metadata_filenames = get_data_filenames(args.data_directory)

    # Initialize arrays for incoming measurements
    num_images = len(image_filenames)
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

            # check range NDVI values, excluding NaN
            # print(np.nanmin(ndvi), np.nanmax(ndvi), np.nanmedian(ndvi))
            visualize_image(ndvi, "NDVI", args.output_directory)

            # Add measurement to array
            all_median_ndvi[i] += np.nanmedian(ndvi)
            all_days_since_acquisition[i] += num_days_since_acquisition

            # Draw progress bar
            bar()

    # Tell me how green the vegetation has gotten!    
    compute_rate_of_change(all_days_since_acquisition, all_median_ndvi)