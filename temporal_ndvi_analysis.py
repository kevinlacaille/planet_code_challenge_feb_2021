import rasterio
import numpy as np
from xml.dom import minidom
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import argparse
import os

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Measure the change in green vegitation using the Normalized Difference Vegitation Index (NDVI)')
    parser.add_argument('data_directory', type=str, help='Input directory to data. Expected data type: PSScene4Band GeoTIFFs.')
    parser.add_argument('output_directory', type=str, help='Output dir for image. Output images and figures.')
    args = parser.parse_args()

    all_median_ndvi = []#np.zeros(len(all_dates))

    image_filenames, metadata_filenames = import_data(args.data_directory)

    for i in range(len(image_filenames)):
        
        band_red, band_nir = extract_data(image_filenames[i])

        # REMOVE / MASK OUT FEATURES WITHOUT VEG
        # E.G., ROADS, WATER, BUILDINGS, ETC.

        band_red, band_nir = normalize_data(metadata_filenames[i], band_red, band_nir)

        ndvi = measure_ndvi(band_red, band_nir)

        # check range NDVI values, excluding NaN
        print(np.nanmin(ndvi), np.nanmax(ndvi), np.nanmedian(ndvi))

        # all_median_ndvi[i] += np.nanmedian(ndvi)
        all_median_ndvi.append(np.nanmedian(ndvi))

    # Get rid of nans
    # ndvi = ndvi[~np.isnan(ndvi)]

    ## Measure change in NDVI (greeness) over time in change in ndvi / day
    all_median_ndvi = np.array(all_median_ndvi)


def import_data(data_directory):

    all_dates = os.listdir(args.data_directory)

    ## NEXT, PUT TOGETHER AUTOMATED SEARCH FOR DATA

    data_dir = "/home/klacaill/Documents/Github/planet_hack_2020_arctic_streams/data/BeadedStreams/AOI_1/files/PSScene4Band/"
    subdir = "analytic_udm2/"
    extension_1 = "_3B_AnalyticMS.tif"
    extension_2 = "_3B_AnalyticMS_metadata.xml"

    date_1 = "20190927_211921_1018"
    date_2 = "20190927_211922_1018"
    date_3 = "20190927_211923_1018"
    date_4 = "20190928_211958_103d"
    date_5 = "20190928_211959_103d"

    # for i in range(len(all_dates)):
        
    # dates_in_days = np.array([0, 1, 2, 3, 4])

    # filename_1 = data_dir + date_1 + "/" + subdir + date_1 + extension
    # filename_2 = data_dir + date_2 + "/" + subdir + date_1 + extension
    # filename_3 = data_dir + date_3 + "/" + subdir + date_1 + extension
    # filename_4 = data_dir + date_4 + "/" + subdir + date_1 + extension
    # filename_5 = data_dir + date_5 + "/" + subdir + date_1 + extension      
    # all_filenames = [filename_1, filename_2, filename_3, filename_4, filename_5]

    all_dates = [date_1, date_2, date_3, date_4, date_5]

    image_filenames = data_dir + all_dates + "/" + subdir + all_dates+ extension_1
    metadata_filenames = data_dir + all_dates + "/" + subdir + all_dates+ extension_2


    return image_filename, metadata_filename

def extract_data(filename):

    ## Extract the data from the red and near-infrared bands
    # Load red and NIR bands - note all PlanetScope 4-band images have band order BGRN
    with rasterio.open(filename) as src:
        band_red = src.read(3)

    with rasterio.open(filename) as src:
        band_nir = src.read(4)

    return band_red, band_nir

def normalize_data(metadata_filename, band_red, band_nir):

    xmldoc = minidom.parse(metadata_filename)

    nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

    # XML parser refers to bands by numbers 1-4
    coeffs = {}
    for node in nodes:
        bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
        if bn in ['1', '2', '3', '4']:
            i = int(bn)
            value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
            coeffs[i] = float(value)

    # Multiply the Digital Number (DN) values in each band by the TOA reflectance coefficients
    band_red = band_red * coeffs[3]
    band_nir = band_nir * coeffs[4]

    return band_red, band_nir

def measure_ndvi(band_red, band_nir):

    ## Perform the NDVI calculation
    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')

    # Calculate NDVI. This is the equation at the top of this guide expressed in code
    ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

    return ndvi

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)





# # Soil should have an NDVI = 0 (ish) ?
# # Compare NDVI to zero to see how NDVI changes over time
# # NDVI = 1 -> very high vegitation -> vegitation
# # NDVI = 0 -> equal absoption and reflection of red light
# # NDVI = 0.1 - 0.2 -> soil! %https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index#:~:text=The%20normalized%20difference%20vegetation%20index,observed%20contains%20live%20green%20vegetation.
# # NDVI = -1 -> very high water -> water
# #
# # Compare same regions with some mask
# #

# # plt.plot(dates_in_days, all_median_ndvi)
# # plt.xlabel("Days")
# # plt.ylabel("NDVI")
# # plt.show()

# # plt.plot(dates_in_days[1:], np.diff(all_median_ndvi))
# # plt.xlabel("Days")
# # plt.ylabel("Change in NDVI")
# # plt.show()

# # """
# # The NDVI values will range from -1 to 1. You want to use a diverging color scheme to visualize the data,
# # and you want to center the colorbar at a defined midpoint. The class below allows you to normalize the colorbar.
# # """

# class MidpointNormalize(colors.Normalize):
#     """
#     Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)
#     e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
#     Credit: Joe Kington, http://chris35wills.github.io/matplotlib_diverging_colorbar/
#     """
#     def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
#         self.midpoint = midpoint
#         colors.Normalize.__init__(self, vmin, vmax, clip)

#     def __call__(self, value, clip=None):
#         # I'm ignoring masked values and all kinds of edge cases to make a
#         # simple example...
#         x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
#         return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


# # Set min/max values from NDVI range for image (excluding NAN)
# # set midpoint according to how NDVI is interpreted: https://earthobservatory.nasa.gov/Features/MeasuringVegetation/
# min=0.2#np.nanmin(ndvi)
# max=np.nanmax(ndvi)
# mid=np.mean([min, max])

# fig = plt.figure(figsize=(20,10))
# ax = fig.add_subplot(111)

# # diverging color scheme chosen from https://matplotlib.org/users/colormaps.html
# cmap = plt.cm.RdYlGn 

# cax = ax.imshow(ndvi, cmap=cmap, clim=(min, max), norm=MidpointNormalize(midpoint=mid,vmin=min, vmax=max))

# ax.axis('off')
# ax.set_title('Normalized Difference Vegetation Index', fontsize=18, fontweight='bold')

# cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)

# # fig.savefig("output/ndvi-fig.png", dpi=200, bbox_inches='tight', pad_inches=0.7)

# plt.show()


# fig2 = plt.figure(figsize=(10,10))
# ax = fig2.add_subplot(111)

# plt.title("NDVI Histogram", fontsize=18, fontweight='bold')
# plt.xlabel("NDVI values", fontsize=14)
# plt.ylabel("# pixels", fontsize=14)


# x = ndvi[~np.isnan(ndvi)]
# numBins = 20
# ax.hist(x,numBins,color='green',alpha=0.8)

# # fig2.savefig("output/ndvi-histogram.png", dpi=200, bbox_inches='tight', pad_inches=0.7)

# plt.show()