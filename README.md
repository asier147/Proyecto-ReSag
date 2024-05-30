# Project-ReSag-MasterThesis

This project code was developed for the Master's Thesis within the framework of the project "Development of new remote sensing methodologies for more sustainable agriculture (ReSAg)," funded by the Ministry of Science and Innovation of Spain through the State Plan for R&D&I (PID2019-107386RB-I00).

The title of the Master's Thesis is "Development of remote sensing methodologies for the identification of sustainable agricultural practices."

The code is structured in a way that each agricultural region has its own folder containing:

1- Google Earth Engine code for calculating statistics for each plot for Sentinel-2 bands and selected indices using the cloud filter based on the SCL band.

2- Python code for loading data and visualizing time series prior to outlier removal, interpolation, and smoothing.

3- Python code for loading data and calculating zonal statistics for Sentinel-1 data. 

4- Visualization of time series from S-1 prior to  interpolation.

5- Python code for outlier removal, interpolation, and smoothing of time series of S-2 bands and indices.

6- Python code for  interpolation of time series of S-1 bands.

7- Python code for visualizing time series of Sentinel-2 indices and bands after outlier removal, interpolation, and smoothing.

8- Python code for visualizing time series of Sentinel-1 bands after interpolation.

9- Python code for statistical analysis.

10- Python code to calculate the correlation matrix between bands and indices from Sentinel-2.

11- Python code to prepare datasets for the Random Forest supervised classifier.

12- Python code for estimating optimal hyperparameters for the Random Forest supervised classifier.

13- Python code for implementing the Random Forest supervised classifier.
