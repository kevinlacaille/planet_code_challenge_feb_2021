# planet_code_challenge_feb_2021
A repo for the code test for the Geospatial Software Engineer position at Planet Labs.

To run temporal analysis on the change in green vegitation, type the following into you command line:

> python3 main.py data_directory/ output_directory/

data_directory/
- The relative or absolute path to your PSScene4Band data.
- Assume the following sub-directory structure: date/analytics_udm2/
- Assumes the following data file name: date_3B_AnalyticsMS.tif
- Where "date" is of the following structure: YearMonthDate_XXXXXX_XXXX

output_directory/
- The relative or absolute path to the program's output data (TBD)


I participated in Planet Hack 2020, where I learned about NDVI and NDWI measurements and how they can be used to find regions of vegetation and water, respectively.

Where I learned about NDVI and found code on how to measure it: https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks/ndvi

What I would do next:
- Mask out roads, buildings, and other infrastructure via road with either knowlege of a road database or from detection models (Crowd AI: https://www.crowdai.com/)
- In metadata.json:
    - Look into "anomalous_pixels"
    - Compare coordinates to ensure looking at same region

