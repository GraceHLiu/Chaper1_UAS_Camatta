# Chaper1_UAS_Camatta

## Project Summary
This project is the first research chapter of my dissertation proposal. The goal of this project is to develope light use efficiency based models for forage production mapping using remote sensing observations collected from satellite and small Unmanned Aerial Systems (sUAS).

![sUAS_mapping](https://user-images.githubusercontent.com/17130674/55701045-8b5b0a80-5986-11e9-91bd-6d04e9535657.png)

## Code Descriptions

### 1. Satellite data processing

#### 1.1 I_Clip_DNtoTOANDVI.py

This code 1) clips the raw satellite images to the area of interest, 2) converts the raw digital number (DN) to top of atmosphere (TOA) reflectance, and 3) calculates the normalized difference vegetation index (NDVI). 

- **packages**: os, glob, math, json, ogr, osr, datetime, osgeo,numpy, system, xml

- **input**: PlanetScope satellite images (.tif and the corresponding metadata in .xml) and clipping boundaries (.shp)

- **output**: TOA based NDVI images (.tif)

#### 1.2 II_TOANDVI_Interpolation.py

This code performs temporal interpolation (linear) and smoothing (savgol filter) to the output NDVI images from I_Clip_DNtoTOANDVI and generates daily time series of NDVI images.

- **packages**: gdal, os, osr, datetime,numpy, pandas, scipy.signal, shutil, glob

- **input**: NDVI images (.tif)

- **output**: daily NDVI images (.tif)

### 2. PAR data sharpening 

#### 2.1 I_Daily_AreaSol.py

This code derives clear sky incoming solar radiation from a raster surface.

- **packages**: arcpy (comes with ArcGIS), os, datetime, progressbar, time

- **input**: DEM (.tif)

- **output**: Spatial solar radiation (.tif)

#### 2.2 II_PAR_sharpening.py

This code sharpens the [spatial CIMIS](https://cimis.water.ca.gov/SpatialData.aspx) all sky solar radiation from 2km resolution to 30cm resolution.

- **packages**: os, datetime, glob, osr, gdal, numpy

- **input**: Spatial solar radiation (.tif) at 2km (all sky) and 30cm (clear sky) resolution.

- **output**: Sharpened (all sky) spatial solar radiation (.tif)

### 3. sUAS data processing

#### 3.1 I_Clip_Resample.py

This code clips and resamples the input sUAS images.

- **packages**: os

- **input**: sUAS images (.tif) and boundary (.shp)

- **output**: Clipped and resampled images (.tif)

#### 3.2 II_TopoCorrect_CModel.r

This code performs illumination correction ([C model](https://ieeexplore.ieee.org/abstract/document/5653492)) to sUAS images.

- **libraries**: raster, sp, rgdal, xlsx

- **input**: surface reflectance images (.tif) and illumination condition images (.tif)

- **output**: illumination corrected surface reflectance images (.tif)

#### 3.3 III_SSTARFM_Datafusion.py

This code implements [a simple data fusion method](https://www.mdpi.com/2072-4292/11/5/595/htm) to PlanetScope (3m) and sUAS (30cm) NDVI images and generates daily NDVI images at 30cm resolution.

- **packages**: os, datetime, glob, osr, gdal, numpy, pandas, and scipy

- **input**: NDVI images at supplementary spatial and temporal resolution (.tif)

- **output**: fused NDVI images (.tif)

#### 3.4 IIII_NDVItoAPAR.py

This code calculates APAR from NDVI and incoming shortwave solar radiation.

- **packages**: os, datetime, glob, osr, gdal, numpy, pandas, and shutil

- **input**: NDVI images and spatial incoming shortwave solar radiation (.tif)

- **output**: APAR images (.tif)

#### 3.5 IIIII_ExtractValues.py

This code extracts raster values at the locations of input multipoint shapefiles.

- **packages**: os, gdal, ogr, datetime, glob, pandas

- **input**: raster images (.tif) and multipoint shapefiles (.shp)

- **output**: data table containing the extracted values (.csv)

### 4. Model optimization

The three codes under model optimization uses stochastic gradient descent method to calibrate the coefficients in our models by minimizing the RMSE. The three codes corresponds to the three models in our [paper](https://www.mdpi.com/2072-4292/11/5/595/htm). 

- **libraries**: Deriv, reshape2, Metrics, and (ggplot)



