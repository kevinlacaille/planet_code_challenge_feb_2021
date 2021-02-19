### To improve
Given more time, here are some things that would be useful to do in order to improve the code's scalability and performance:

- Find where all the maps overlay with each other. I would create a mask of the union of all of the maps and only measure NDWI and NDVI within this region.

- Use the metadata.json file to:
    - Find all anomalous pixels (```anomalous_pixels```) to mask out
    - Compare coordinates (```coordinates```) for all images to ensure we're comparing the same regions accross the time series

- Mask out roads, buildings, and other infrastructure with some combination of:
    - A database for known roads (i.e., GRIP global [roads database](https://www.globio.info/download-grip-dataset))
    - A database for known buildings (i.e., [This Canadian Open Database of Buildings](https://www.statcan.gc.ca/eng/lode/databases/odb))
    - Road detection ML models (i.e., [Crowd AI](https://www.crowdai.com/))
    - Simple roads detection models (i.e., [Detect straight roads with Hough lines via OpenCV](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html))

- To improve speed, I could make the output directory optional, along with an optional flag to tell the code whether or not to output data.

- Intead of measuring the average change of NDVI over the entire time series, it could be useful to fit a function to the data and report back how the NDVI changes over time (perhaps a modified sine wave, or something more physical).

### Notes
#### How did I determine greenness?

I chose to measure NDVI as the metric for "greenness" as it is a simple, yet robust, measure of how much red-band energy green plants reflect. Small positive values, 0 < NDVI < 0.1, likely represent regions of baren land and soil. Slightly higher positive values, 0.2 < NDVI < 0.5, likely represent shrubs and grassland. High NDVI values, NDVI > 0.6, likely corresponds to dense vegetation. Source: https://www.usgs.gov/core-science-systems/eros/phenology/science/ndvi-foundation-remote-sensing-phenology?qt-science_center_objects=0#qt-science_center_objects

Measured the mean change in NDVI over the entire time series. If the the standard deviation of the NDVI of the time series was greater than the mean change, I say that the mean ...



#### What didn't work? 

Initially, I measured the median NDVI as a function of time, however, this did not accuratly represent how the vegetation change with respect to baren soil. So, I changed my strategy and measured the number of pixels that had vegetation (0.2 < NDVI < 1.0) and compared that to the number of pixels that were baren soil (0.0 < NDVI < 0.2).

#### Issues I had
I did not recieve the test data until February 18th, 2021, however I was able to put together the majority of the data ingestion and image processing pipeline from data I had previously downloaded for the project I participated in at [Planet Hack 2020](https://www.planet.com/pulse/planet-hack-2020-our-annual-hackathon-goes-virtual/). See planet_hack_2020_manifest.json for details on this data. 

Until I recieved the data, I was able to completely put together the following function:
```validate_inputs()```
```validate_data()```
```extract_data()```
```normalize_data()```
```measure_ndwi()```
```apply_water_mask()```
```measure_ndvi()```
```compute_rate_of_change()```
```visualize_image()```

After I recieved the data, I finalized the following functions:
```get_data_filenames()```
```visualize_data()```

During this project, I learned about NDVI and NDWI measurements and how they can be used to find regions of vegetation and water, respectively. We used NDVI and NDWI to classify arctic streams. More on that [here](https://github.com/kevinlacaille/planet_hack_2020_arctic_streams).

It turned out that masking water was not needed, as there was no water in the scene. However, this fucntion didn't take much time to write and it makes the code more flexible for future cases where water may be present in the image.

#### Borrowed code
My code adopted many useful functions found in a [Planet Labs Jupyter Notebook](https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks/ndvi), which outlines how to import thier data, parse the metadata, and compute NDVI.



