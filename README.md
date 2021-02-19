# Planet Labs Code Challenge (Feb 2021)
A repo for the code test for the Geospatial Software Engineer position at Planet Labs.

### Summary
This code allows a user to pass in a time series of PSScene4Band data of a specified region and it tells you whether or not there has been a statistically significant change in green vegetation over that time series. The measure of greenery is provided by the measurement of the [normalized difference vegetation
index (NDVI)](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) in the scene. See below for more details.

### Input arguments
```data_directory/```
- The relative or absolute path to your PSScene4Band data, for example: ```task/data/```.
- Assumes the following file naming convension for the GeoTIFFs: ```YearMonthDate_XXXXXX_XXXX_3B_AnalyticMS_clip.tif```
- Assumes the following file naming convension for the metadata: ```YearMonthDate_XXXXXX_XXXX_3B_AnalyticMS_metadata_clip.xml```

```output_directory/```
- The relative or absolute path to the program's output figures

### Run the code!
To run temporal analysis on the change in green vegitation, type the following into you command line:

```bash
> python3 main.py task/data/ output/
|████████████████████████████████████████| 7/7 [100%] in 24.9s (0.28/s)
Over the time series, between 0.02% (2020-08-26) and 3.75% (2020-07-01) of the region contained baren dirt.
Over the time series, between 96.25% (2020-07-01) and 99.98% (2020-08-26) of the region contained vegetation.
Average change in NDVI / day: (0.0 +/- 0.12) % per day
Greenness of the vegetation changed over time, however, over the entire time series, the vegetation did not statistically get greener nor less green over time.

```

### High-level flowchart
Here's how the code works:

1) Parse & validate input arguments
2) Ingest and validate image and metadata files
3) Process images

Extract bands from images &rarr; Normalize data &rarr; Mask out regions with water &rarr; Compute NDVI map &rarr; Visualize data

4) Compute rate of change of green vegitation
5) Return how green the vegetation has gotten over time

### Additional details
Please see ```additional_details.txt``` for more information about my exerience with this challenge.
