#! /usr/bin/python3
"""
A group of functions which aid in the measurements of the change in 
normalized difference vegetation index (NDVI) over time, using 
Planet Labs' PlanetScope 4-Band imagery.

Author
------
Kevin Lacaille

See Also
--------
midpoint
main

References
----------
Planet's notebook on importing & parsing data and measuring NDVI: https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks/ndvi
"""

import numpy as np
import os

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
    """
    
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
    
    return image_filenames, metadata_filenames


def validate_image(image_filename):
    """
    Ensures that the the given PlanetScope image is a valid image

    Parameters:
    -----------
        image_filename : str
                         The input path to a PlanetScope 4-Band image.
    
    Returns:
    --------
        is_image_valid : bool
                         A flag which returns True if the image is valid.
    """
    import rasterio

    valid_colours = ['blue', 'green', 'red', 'nir']
    # Make try/catch? satements to see if data & metadata are good?

    with rasterio.open(image_filename) as src:
        # Check to see if all 4 bands exist
        if not any([colour in src.descriptions for colour in valid_colours]):
            raise Exception("The data does not contain all 4 bands (blue, green, red, nir). Cannot compute NDVI.")
        else:
            src.close()
            is_image_valid = True
            return is_image_valid


def extract_data(image_filename, metadata_filename):
    """
    Extracts un-normalized red and NIR band data from a PlanetScope 4-band image

    Parameters:
    -----------
        image_filename : str
                   The input path to a PlanetScope 4-Band image.
        metadata_filename : str
                   The input path to a PlanetScope 4-Band image metadata.
    
    Returns:
    --------
        band_red : Array[int]
                   Red band image.
        band_nir : Array[int]
                   NIR band image.
        num_days_since_acquisition : int
                   Number of days since acquisition
                   from today.
    """

    from xml.dom import minidom
    from datetime import datetime
    import rasterio

    # Extract acquisition date from metadata
    xmldoc = minidom.parse(metadata_filename)
    acquisition_date = xmldoc.getElementsByTagName("ps:acquisitionDateTime")[0].firstChild.data

    # Current date
    today = datetime.now()
    # Number of days since acquisition    
    num_days_since_acquisition = (today - datetime.strptime(acquisition_date.split("T")[0], '%Y-%m-%d')).days

    if num_days_since_acquisition < 0:
        raise Exception("Number of days since acquisition for", image_filename, "is < 0. Metadata may be corrupt.")

    # Extract green, red, and NIR data from PlanetScope 4-band imagery
    if validate_image(image_filename):

        with rasterio.open(image_filename) as src:
            band_green = src.read(2)

        with rasterio.open(image_filename) as src:
            band_red = src.read(3)

        with rasterio.open(image_filename) as src:
            band_nir = src.read(4)

        return band_green, band_red, band_nir, num_days_since_acquisition


def normalize_data(metadata_filename, band_green, band_red, band_nir):
    """
    Normalizes the green, red, and NIR band data values by 
    their reflectance coefficient.

    Parameters:
    -----------
        metadata_filename : str
                   The input path to a PlanetScope 4-Band 
                   image metadata.
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

    See Also:
    ---------
    https://en.wikipedia.org/wiki/Normalized_difference_water_index
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

    See Also:
    ---------
    https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index
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

    # Mean change in NDVI and its standard deviation
    mean_change_in_ndvi = np.mean(np.diff(ndvi))
    mean_change_in_ndvi_uncertainty = np.std(np.diff(ndvi))

    # Number of days in time series
    num_days = np.max(time) - np.min(time)

    # Mean rate of change in NDVI and its uncertainty
    mean_rate_of_change = mean_change_in_ndvi / num_days
    mean_rate_of_change_uncertainty = abs((mean_change_in_ndvi_uncertainty / mean_change_in_ndvi)) * abs(mean_rate_of_change)

    # Print rate of change in NDVI per day with uncertainty
    ndvi_result_message = "(" + str(round(mean_rate_of_change * 100, 1)) + " +/- " + \
                           str(round(mean_rate_of_change_uncertainty * 100, 1)) + ") % per day"

    print("Average change in NDVI / day:", ndvi_result_message)

    # Print findings
    if mean_rate_of_change_uncertainty >= abs(mean_rate_of_change):
        print("Vegetation is not statistically getting greener nor less green over time.")
    else:
        if mean_rate_of_change < 0:
            print("Vegetation is getting less green over time, at a rate of:", ndvi_result_message)
        elif mean_rate_of_change > 0:
            print("Vegetation is getting more green over time, at a rate of:", ndvi_result_message)
        else:
            print("Vegetation is neither getting greener nor getting less green over time!")

    # plt.plot(time[1:], np.diff(ndvi))
    # plt.show()


def visualize_image(image, image_type, output_directory):
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

    import matplotlib.pyplot as plt
    from midpoint import MidpointNormalize

    # Set min/max values from NDVI range for image (excluding NAN)
    # set midpoint according to how NDVI is interpreted: https://earthobservatory.nasa.gov/Features/MeasuringVegetation/
    min_range = np.nanmin(image)
    max_range = np.nanmax(image)
    mid_range = np.mean([min_range, max_range])

    # Map
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot(111)

    # diverging color scheme chosen from https://matplotlib.org/users/colormaps.html
    cmap = plt.cm.RdYlGn 

    cax = ax.imshow(image, cmap=cmap, clim=(min_range, max_range), \
                    norm=MidpointNormalize(midpoint=mid_range,vmin=min_range, vmax=max_range))

    ax.axis('off')
    ax.set_title(image_type, fontsize=18, fontweight='bold')
    fig.colorbar(cax, orientation='horizontal', shrink=0.65)

    fig.savefig(output_directory + "/" + image_type + "-fig.png", dpi=200, bbox_inches='tight', pad_inches=0.7)
    plt.show()

    # Histogram of values in image
    fig2 = plt.figure(figsize=(10,10))
    ax = fig2.add_subplot(111)

    plt.title("NDVI Histogram", fontsize=18, fontweight='bold')
    plt.xlabel("NDVI values", fontsize=14)
    plt.ylabel("# pixels", fontsize=14)


    x = image[~np.isnan(image)]
    numBins = 20
    ax.hist(x,numBins,color='green',alpha=0.8)

    fig2.savefig(output_directory + "/" + image_type + "-histogram.png", dpi=200, bbox_inches='tight', pad_inches=0.7)
    plt.show()