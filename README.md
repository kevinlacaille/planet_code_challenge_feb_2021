# Planet Labs Code Challenge (Feb 2021)
A repo for the code test for the Geospatial Software Engineer position at Planet Labs.

### Summary
This code allows a user to pass in a time series of PSScene4Band data of a specified region and it tells you whether or not there has been a statistically significant change in green vegetation over that time series. The measure of greenery is provided by the measurement of the [normalized difference vegetation
index (NDVI)](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) in the scene. See below for more details.

### Input arguments
```data_directory/```
- The relative or absolute path to your PSScene4Band data.
- Assume the following sub-directory structure: date/analytics_udm2/
- Assumes the following data file name: date_3B_AnalyticsMS.tif
- Where "date" is of the following structure: YearMonthDate_XXXXXX_XXXX

```output_directory/```
- The relative or absolute path to the program's output figures

### Run the code!
To run temporal analysis on the change in green vegitation, type the following into you command line:

```bash
> python3 main.py data_directory/ output_directory/
|████████████████████████████████████████| 5/5 [100%] in 2:43.8 (0.03/s)
Vegitation is getting more green over time, at a rate of: (15.1 +/- 0.3) % per day.
```

### High-level flowchart
Here's how the code works:

1) Parse & validate input arguments
2) Ingest and validate image and metadata files
3) Process images

Extract bands from images &rarr; Normalize data &rarr; Mask out regions with water &rarr; Compute NDVI map &rarr; Visualize data

4) Compute rate of change of green vegitation
5) Return how green the vegetation has gotten over time

### To improve

Here are some things that would be useful to do in order to improve the code's scalability and performance:

- Mask out roads, buildings, and other infrastructure with some combination of:
    - A database for known roads (i.e., GRIP global [roads database](https://www.globio.info/download-grip-dataset))
    - A database for known buildings (i.e., [This Canadian Open Database of Buildings](https://www.statcan.gc.ca/eng/lode/databases/odb))
    - Road detection ML models (i.e., [Crowd AI](https://www.crowdai.com/))
    - Simple roads detection models (i.e., [Detect straight roads with Hough lines via OpenCV](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghlines/py_houghlines.html))

- Use the metadata.json file to:
    - Find all anomalous pixels (```anomalous_pixels```) to mask out
    - Compare coordinates (```coordinates```) for all images to ensure we're comparing the same regions accross the time series

### Notes
I participated in [Planet Hack 2020](https://www.planet.com/pulse/planet-hack-2020-our-annual-hackathon-goes-virtual/), where I learned about NDVI and NDWI measurements and how they can be used to find regions of vegetation and water, respectively. We used NDVI and NDWI to classify arctic streams. More on that [here](https://github.com/kevinlacaille/planet_hack_2020_arctic_streams).

Code adopted many useful functions found in a [Planet Labs Jupyter Notebook](https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks/ndvi), which outlines how to import thier data, parse the metadata, and compute NDVI.
