# Details about the code

## How did I determine greenness?

I chose to measure NDVI as the metric for greenness as it is a simple, yet robust, as it measures of how much red-band energy green plants reflect. I selected all pixels which have small positive values, 0 <= NDVI <= 0.3, to represent correspond to regions of baren soil. Additionally, and I selected all pixels which have values between 0.3 < NDVI <= 1.0, to correspond to all of the vegetation in the scene. Source: [USGS](https://www.usgs.gov/core-science-systems/eros/phenology/science/ndvi-foundation-remote-sensing-phenology?qt-science_center_objects=0#qt-science_center_objects).

I measured NDVI as:

```NDVI = (NIR - Red) / (NIR + Red) = (Band 4 - Band 3) / (Band 4 + Band 3)```

### First measure for greenness - Proportions of dirt and vegetation
I measured the proportions of dirt and vegetation as:

``` proportion = number of pixels containing (dirt or veg) / total number of pixels in the image```

This didn't prove to be incredibly useful, as these test scenes contained so much lush vegetation in comparison to barren dirt.

### Second measure for greenness - Mean rate of change in NDVI over entire time series
I measured the mean change in NDVI over the entire time series as:

``` mean rate of change = <Δ NDVI> / number of days in time series```

This was a helpful measure to see if the NDVI changed over the entire time series, however this doesn't paint the whole picture. Since this simply measures 
the average change in NDVI over the entire time, it doesn't capture if the NDVI moves in arount the mean NDVI over the time series (i.e., as a sine wave). In
this case, I found that the NDVI exhibited a sine-like pattern over time, so the mean change in NDVI was approximately zero, however the standard deviation 
in the change was >>0.

## Issues I had
I did not receive the test data until February 18th, 2021, however I was able to put together the majority of the data ingestion and image processing pipeline from data I had previously downloaded for the project I participated in at [Planet Hack 2020](https://www.planet.com/pulse/planet-hack-2020-our-annual-hackathon-goes-virtual/). See planet_hack_2020_manifest.json for details on this data. 

Until I received the data, I was able to completely put together the following functions:
- ```validate_inputs()```
- ```validate_data()```
- ```extract_data()```
- ```normalize_data()```
- ```measure_ndwi()```
- ```apply_water_mask()```
- ```measure_ndvi()```
- ```visualize_image()```

After I received the data, I finalized the following functions:
- ```get_data_filenames()```
- ```measure_dirt_veg_proportions()```
- ```visualize_data()```
- ```compute_rate_of_change```

## What didn't work? 

1) At first, I split the classifications up into 3 categories:
- barren soil (0.0 <= NDVI <= 0.2)
- shrubs and grassland (0.2 < NDVI <= 0.4)
- lush vegetation (0.4 < NDVI <= 1)

However, this dataset seemed to only have very lush vegetation, which then resulted in there being no barren soil, biasing my results to show that there was only green vegetation and no barren soild.

2) During my Planet Hack project, I learned about NDVI and NDWI measurements and how they can be used to find regions of vegetation and water, respectively. We used NDVI and NDWI to classify arctic streams. More on that [here](https://github.com/kevinlacaille/planet_hack_2020_arctic_streams).

In this code test I used NDWI to mask out regions of water in the images. I measured NDWI as:

```NDWI = (Green - NIR) / (Green + NIR) = (Band 2 - Band 4) / (Band 2 + Band 4)```

It turned out that masking water was not needed, as there was no water in the scene. However, this function didn't take much time to write and it makes the code more flexible for future cases where water may be present in the image. Therefore, I kept it in.

## Borrowed code
My code adopted many useful functions found in a [Planet Labs Jupyter Notebook](https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks/ndvi), which outlines how to import their data, parse the metadata, and compute NDVI.

## To improve
Given more time, here are some things that would be useful to do in order to improve the code's scalability and performance:

- Find where all the maps overlay with each other. This would then help me create a mask of the union of all the maps, and then I would only measure NDWIs and NDVIs within this region.

- Parse the metadata.json file to:
    - Find all anomalous pixels (```anomalous_pixels```) to mask out
    - Compare coordinates (```coordinates```) for all images to ensure we're comparing the same regions across the time series

- Mask out roads, buildings, and other infrastructure with some combination of:
    - A database for known roads (i.e., GRIP global [road database](https://www.globio.info/download-grip-dataset))
    - A database for known buildings (i.e., [This Canadian Open Database of Buildings](https://www.statcan.gc.ca/eng/lode/databases/odb))
    - Road detection ML models (i.e., [Crowd AI](https://www.crowdai.com/))
    - Simple road detection models (i.e., [Detect straight roads with Hough lines via OpenCV](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html))

- To improve speed, I would make the output directory optional, along with an optional flag to tell the code whether to output data.

- Instead of measuring the average change of NDVI over the entire time series, it could be useful to fit a function to the data and report back how the NDVI changes over time (perhaps a modified sine wave, or something more physical).
