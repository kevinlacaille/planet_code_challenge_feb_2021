#! /usr/bin/python3
"""
temporal_ndvi_analysis provides a measure of change in green vegitation over time by analyzing 
the Red and Near Infrared (NIR) bands from Planet Labs' PlanetScope 4-Band imagery. The measure of
green vegitation is provided by the normalized difference vegetation index (NDVI)
Red and NIR bands from PlanetScore 4-band images.

Wikipedia on NDVI: https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
Wikipedia on NDWI: https://en.wikipedia.org/wiki/Normalized_difference_water_index
How to compute NDVI: https://developers.planet.com/planetschool/calculate-an-ndvi-in-python/

Example:
--------
> temporal_ndvi_analysis data_directory output_directory
Vegitation is getting more green over time, at a rate of: (15.1 +/- 0.3) % per day.
"""

import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors

def validate_inputs(args):
    """
    Ensures that the input arguments (data_directory, outout_directory) 
    are valid by checking that the directories exist.

    Parameters:
    -----------
        args : Namespace[str]
               The namespace which contains the input arguments:
               data_directory
               output_directory
    
    Returns:
    --------
        None
    """
    
    # Ensure data directory exists
    if not os.path.isdir(args.data_directory):
        raise Exception("Given data directory not found. Please point to an existing data directory.")

    
    # Ensure output directory exists
    if not os.path.isdir(args.output_directory):
        raise Exception("Given output directory not found. Please point to an existing directory to output to.")


def get_data_filenames(data_directory):
    """
    Returns all file names for the images and their metadata.

    Parameters:
    -----------
        data_directory : str
                         The input path to the PlanetScope 4-Band data.
    
    Returns:
    --------
        image_filenames : List[str]
                         All image file names.
        metadata_filenames : List[str]
                         All metadata file names.
        days_since_observation : List[int]
                         Number of days from observation date
                         until today.
    """
    
    from datetime import datetime

    ## NEXT, PUT TOGETHER AUTOMATED SEARCH FOR DATA
    # data_dir = "/home/klacaill/Documents/Github/planet_hack_2020_arctic_streams/data/BeadedStreams/AOI_1/files/PSScene4Band/"
    subdir = "analytic_udm2/"
    extension_1 = "_3B_AnalyticMS.tif"
    extension_2 = "_3B_AnalyticMS_metadata.xml"

    date_1 = "20190927_211921_1018"
    date_2 = "20190927_211922_1018"
    date_3 = "20190927_211923_1018"
    date_4 = "20190928_211958_103d"
    date_5 = "20190928_211959_103d"

    all_dates = np.array([date_1, date_2, date_3, date_4, date_5])
    
    all_time = [date.split("_")[0] for date in all_dates]

    # Current date
    today = datetime.now()

    # Number of days since observation
    days_since_observation = [(today - datetime.strptime(time, '%Y%m%d')).days for time in all_time]

    # All image file names
    image_filenames = [data_directory + date + "/" + subdir + date + extension_1 for date in all_dates]

    # All metadate file names
    metadata_filenames = [data_directory + date + "/" + subdir + date + extension_2 for date in all_dates]

    # Make sure all image files exist
    does_image_exist = [os.path.isfile(file) for file in image_filenames]
    if not any(does_image_exist):
        images_that_dont_exist = image_filenames[np.where(np.array(does_image_exist) == False)[0][0]]
        raise Exception("Cannot find the following files:", images_that_dont_exist)
    
    # Make sure all metadata files exist
    does_metadata_exist = [os.path.isfile(file) for file in image_filenames]
    if not any(does_metadata_exist):
        metadata_that_dont_exist = metadata_filenames[np.where(np.array(does_metadata_exist) == False)[0][0]]
        raise Exception("Cannot find the following files:", metadata_that_dont_exist)
    

    return image_filenames, metadata_filenames, days_since_observation


def is_image_valid(filename):
    """
    Ensures that the the given PlanetScope image is a valid image

    Parameters:
    -----------
        filename : str
                   The input path to a PlanetScope 4-Band image.
    
    Returns:
    --------
        boolean
    """
    import rasterio

    valid_colours = ['blue', 'green', 'red', 'nir']
    # Make try/catch? satements to see if data & metadata are good?

    with rasterio.open(filename) as src:
        # Check to see if all 4 bands exist
        if not any([colour in src.descriptions for colour in valid_colours]):
            raise Exception("The data does not contain all 4 bands (blue, green, red, nir). Cannot compute NDVI.")
        else:
            src.close()
            return True


def extract_data(filename):
    """
    Extracts un-normalized red and NIR band data from a PlanetScope 4-band image

    Parameters:
    -----------
        filename : str
                   The input path to a PlanetScope 4-Band image.
    
    Returns:
    --------
        band_red : Array[int]
                   Red band image.
        band_nir : Array[int]
                   NIR band image.
    """

    import rasterio

    # Extract green, red, and NIR data from PlanetScope 4-band imagery
    if is_image_valid(filename):

        with rasterio.open(filename) as src:
            band_green = src.read(2)

        with rasterio.open(filename) as src:
            band_red = src.read(3)

        with rasterio.open(filename) as src:
            band_nir = src.read(4)

        return band_green, band_red, band_nir


def normalize_data(metadata_filename, band_green, band_red, band_nir):
    """
    Normalizes the green, red, and NIR band data values by 
    their reflectance coefficient.

    Parameters:
    -----------
        metadata_filename str - The input path to a PlanetScope 4-Band metadata.
        band_green : Array[int]
                   Un-normalized green band image.
        band_red : Array[int]
                   Un-normalized red band image.
        band_nir : Array[int]
                   Un-normalized NIR band image.
    
    Returns:
    --------
        band_green : Array[int]
                   Normalized green band image.
        band_red : Array[int]
                   Normalized red band image.
        band_nir : Array[int]
                   Normalized NIR band image.

    """

    from xml.dom import minidom

    # Parse the XML metadata file
    xmldoc = minidom.parse(metadata_filename)

    nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

    if nodes.length != 4:
        raise Exception("The data does not contain all 4 bands (blue, green, red, nir). Cannot compute NDVI.")

    # XML parser refers to bands by numbers 1-4
    coeffs = {}
    for node in nodes:
        bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
        if bn in ['1', '2', '3', '4']:
            i = int(bn)
            value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
            coeffs[i] = float(value)

    # Multiply the Digital Number (DN) values in each band by the TOA reflectance coefficients
    band_green = band_green * coeffs[2]
    band_red = band_red * coeffs[3]
    band_nir = band_nir * coeffs[4]

    return band_green, band_red, band_nir


def measure_ndwi(band_green, band_nir):
    """
    Measures the normalized difference water index (NDWI), 
    defined as: NDVI = (NIR - red) / (NIR + red).
    See more: https://en.wikipedia.org/wiki/Normalized_difference_water_index

    Parameters:
    -----------
        band_green : Array[int]
               Normalized green band image.
        band_nir : Array[int]
               Normalized NIR band image.
    
    Returns:
    --------
        ndwi : float
               Normalized difference water index
    """

    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDVI. This is the equation at the top of this guide expressed in code
    ndwi = (band_green.astype(float) - band_nir.astype(float)) / (band_green + band_nir)

    return ndwi


def apply_water_mask(band_green, band_red, band_nir):
    """
    Uses the normalzied difference water index (NDWI) to
    mask out regions with water.

    Parameters:
    -----------
        band_green : Array[int]
               Normalized green band image.
        band_red : Array[int]
               Normalized red band image.
        band_nir : Array[int]
               Normalized NIR band image.
    
    Returns:
    --------
        band_red : Array[int]
               Normalized red band image, masked from water.
        band_nir : Array[int]
               Normalized NIR band image, masked from water.
    """

    # Measure NWDI
    nwdi = measure_ndwi(band_green, band_nir)

    # Pixel is water if nwdi >= 0.3 (ref: https://www.mdpi.com/2072-4292/5/7/3544/htm)
    WATER_VALUE = 0.3
    water_mask_rows, water_mask_cols = np.where(nwdi >= WATER_VALUE)

    # Apply mask to red and NIR (used for NDVI calculation)
    band_red[water_mask_rows, water_mask_cols] = np.nan
    band_nir[water_mask_rows, water_mask_cols] = np.nan

    return band_red, band_nir


def measure_ndvi(band_red, band_nir):
    """
    Measures the normalized difference vegetation index (NDVI), 
    defined as: NDVI = (NIR - red) / (NIR + red).
    See more: Wikipedia on NDVI: https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index

    Parameters:
    -----------
        band_red : Array[int]
               Normalized red band image.
        band_nir : Array[int]
               Normalized NIR band image.
    
    Returns:
    --------
        ndvi : float
               Normalized difference vegetation index
    """

    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDVI. This is the equation at the top of this guide expressed in code
    ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

    return ndvi


def compute_rate_of_change(time, ndvi):
    """
    Computes the average rate of change of the NDVI over
    time by measuring the mean change in NDVI per day.

    Parameters:
    -----------
        time : Array[int]
               Number of days from observation
               date until today.
        ndvi : Array[int]
               Normalized difference vegetation
               index per day.
    
    Returns:
    --------
        NONE
    """

    # print(np.diff(ndvi))
    # print(np.diff(time))

    mean_change_in_ndvi = np.mean(np.diff(ndvi))
    mean_change_in_ndvi_uncertainty = np.std(np.diff(ndvi))

    mean_change_in_time = np.mean(np.diff(np.sort(time)))
    mean_rate_of_change = mean_change_in_ndvi / mean_change_in_time
    mean_rate_of_change_uncertainty = abs((mean_change_in_ndvi_uncertainty / mean_change_in_ndvi)) * abs(mean_rate_of_change)

    # Change in NDVI / day
    ndvi_result_message = "(" + str(round(mean_rate_of_change * 100, 1)) + "+/-" + \
                           str(round(mean_rate_of_change_uncertainty * 100, 1)) + ") % per day"

    print("Average change in NDVI / day:", ndvi_result_message)

    # Print findings
    if mean_rate_of_change_uncertainty >= abs(mean_rate_of_change):
        print("Vegitation is not statistically getting greener nor less green over time.")
    else:
        if mean_rate_of_change < 0:
            print("Vegitation is getting less green over time, at a rate of:", ndvi_result_message)
        elif mean_rate_of_change > 0:
            print("Vegitation is getting more green over time, at a rate of:", ndvi_result_message)
        else:
            print("Vegitation is neither getting greener nor getting less green over time!")

    # plt.plot(time[1:], np.diff(ndvi))
    # plt.show()


class MidpointNormalize(colors.Normalize):
    """
    This class is borrowed from: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/ndvi/ndvi_planetscope.ipynb

    Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)
    e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
    Credit: Joe Kington, http://chris35wills.github.io/matplotlib_diverging_colorbar/
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


def visualize_image(image, output_directory):
    """
    This function is modified from: https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/ndvi/ndvi_planetscope.ipynb

    Visualizes a map.

    Parameters:
    -----------
        band_red : Array[int]
               Normalized red band image.
        band_nir : Array[int]
               Normalized NIR band image.
    
    Returns:
    --------
        ndvi : float
               Normalized difference vegetation index
    """
    # Set min/max values from NDVI range for image (excluding NAN)
    # set midpoint according to how NDVI is interpreted: https://earthobservatory.nasa.gov/Features/MeasuringVegetation/
    min_range = np.nanmin(image)
    max_range = np.nanmax(image)
    mid_range = np.mean([min_range, max_range])

    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(111)

    # diverging color scheme chosen from https://matplotlib.org/users/colormaps.html
    cmap = plt.cm.RdYlGn 

    cax = ax.imshow(image, cmap=cmap, clim=(min_range, max_range), \
                    norm=MidpointNormalize(midpoint=mid_range,vmin=min_range, vmax=max_range))

    ax.axis('off')
    # ax.set_title('Normalized Difference Vegetation Index', fontsize=18, fontweight='bold')
    cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)

    # fig.savefig(output_directory + "/ndvi-fig.png", dpi=200, bbox_inches='tight', pad_inches=0.7)
    plt.show()

    # Histogram of values in image
    fig2 = plt.figure(figsize=(10,10))
    ax = fig2.add_subplot(111)

    plt.title("NDVI Histogram", fontsize=18, fontweight='bold')
    plt.xlabel("NDVI values", fontsize=14)
    plt.ylabel("# pixels", fontsize=14)


    x = ndvi[~np.isnan(ndvi)]
    numBins = 20
    ax.hist(x,numBins,color='green',alpha=0.8)

    # fig2.savefig(output_directory + "/ndvi-histogram.png", dpi=200, bbox_inches='tight', pad_inches=0.7)
    plt.show()


if __name__ == "__main__":
    
    # Parse inputs
    parser = argparse.ArgumentParser(description='Measure the change in green vegitation \
                                                  using the Normalized Difference Vegitation Index (NDVI)')
    parser.add_argument('data_directory', type=str, help='Input directory to data. \
                                                          Expected data type: PSScene4Band GeoTIFFs.')
    parser.add_argument('output_directory', type=str, help='Output directory for image. \
                                                            Output images and figures.')
    args = parser.parse_args()

    # Ensure inputs are valid
    validate_inputs(args)

    # Retrieve image and metadata file names, and time since their observation
    image_filenames, metadata_filenames, days_since_observation = get_data_filenames(args.data_directory)

    # Initialize array for incoming measurements
    all_median_ndvi = np.zeros(len(days_since_observation))

    # Cycle through each image
    for i in range(len(image_filenames)):

        # Extract green, red, and NIR data from 4-Band imagery        
        band_green, band_red, band_nir = extract_data(image_filenames[i])

        # Normalize data by their reflectance coefficient
        band_green, band_red, band_nir = normalize_data(metadata_filenames[i], band_green, band_red, band_nir)

        # Mask regions with water
        band_red, band_nir = apply_water_mask(band_green, band_red, band_nir)

        # Measure NDVI in un-masked regions
        ndvi = measure_ndvi(band_red, band_nir)

        # check range NDVI values, excluding NaN
        # print(np.nanmin(ndvi), np.nanmax(ndvi), np.nanmedian(ndvi))
        # visualize_image(image, args.output_directory)

        # Add measurement to array
        all_median_ndvi[i] += np.nanmedian(ndvi)

    # Tell me how green the vegitation has gotten!    
    compute_rate_of_change(days_since_observation, all_median_ndvi)