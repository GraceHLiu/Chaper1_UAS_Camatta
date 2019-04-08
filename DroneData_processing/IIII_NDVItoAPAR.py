import os
import osr
from osgeo import gdal
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import glob,shutil

Site_Name = ['Camatta']

NDVI_min = 0.22#0.23#0.015 these numbers are histogram from 6 YYYY-MM-19 images (I used 5% and 95% percentile)
NDVI_max = 0.77#0.80#0.950
fPAR_min = 0.001
fPAR_max = 0.950

## Define functions
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def raster2array(rasterfn,i):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(i)
    return band.ReadAsArray()

def array2raster(rasterfn,newRasterfn,array):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())

for site in Site_Name:
    UAS_NDVI_dir = '/z0/lh349796/Rangeland/UAS/' + site + '/II_Clipped_Resampled_NDVI_30cm'
    CIMIS_Rs_dir = '/z0/lh349796/Rangeland/UAS/' + site + '/CIMIS_data'#'/z0/lh349796/Rangeland/CIMIS_Spatial/' + site + '_PAR/sUAS_Res_30cm'
    UAS_NDVIdaily_dir_temp = '/z0/lh349796/Rangeland/UAS/' + site + '/II_Clipped_Resampled_NDVI_daily_30cm_temp'
    UAS_NDVIdaily_dir = '/z0/lh349796/Rangeland/UAS/' + site + '/II_Clipped_Resampled_InteRap_Smooth2_NDVI_daily_30cm'#'/z0/lh349796/Rangeland/UAS/' + site + '/II_Clipped_Resampled_NDVI_daily_30cm'
    UAS_fPAR_dir = '/z0/lh349796/Rangeland/UAS/' + site + '/III_Processed_data_daily_30cm/fPAR_Inte'
    UAS_APAR_dir = '/z0/lh349796/Rangeland/UAS/' + site + '/III_Processed_data_daily_30cm/APAR_Inte_DSMedPAR'
    if not os.path.exists(UAS_fPAR_dir):
        os.makedirs(UAS_fPAR_dir)
    if not os.path.exists(UAS_APAR_dir):
        os.makedirs(UAS_APAR_dir)
    if not os.path.exists(UAS_NDVIdaily_dir_temp):
        os.makedirs(UAS_NDVIdaily_dir_temp)
    if not os.path.exists(UAS_NDVIdaily_dir):
        os.makedirs(UAS_NDVIdaily_dir)
    print 'start processing site ' + site + '...'
    print 'II - start converting NDVI to fPAR'
    for file in os.listdir(UAS_NDVIdaily_dir):
        if file.endswith('NDVI.tif'):
            NDVI_path = os.path.join(UAS_NDVIdaily_dir, file)
            raster_ndvi = raster2array(NDVI_path, 1)
            raster_fPAR = (raster_ndvi - NDVI_min) * (fPAR_max - fPAR_min) / (NDVI_max - NDVI_min) + fPAR_min
            raster_fPAR[raster_fPAR < 0] = 0
            raster_fPAR[raster_fPAR > fPAR_max] = fPAR_max
            export_file = os.path.join(UAS_fPAR_dir, file[:-8] + 'fPAR.tif')
            print("I - Calculating fPAR of file " + file + "...")
            array2raster(NDVI_path, export_file, raster_fPAR)
    print 'II finished - fPAR is calculated for all NDVI files'
    print 'III - start calculating APAR ...'
    for file in os.listdir(UAS_fPAR_dir):
        if file.endswith('fPAR.tif'):
            date_NDVI = datetime.strptime(file[8:18],'%Y-%m-%d')
            date_CIMIS = date_NDVI.strftime('%Y%m%d')
            CIMIS_file_path = os.path.join(CIMIS_Rs_dir,date_CIMIS +'Rs_' + site + '.tif')
            if os.path.isfile(CIMIS_file_path):
                print'II - Calculating APAR for date ' + date_CIMIS
                PAR_data = raster2array(CIMIS_file_path, 1) * 0.5
                fPAR_path = os.path.join(UAS_fPAR_dir,file)
                fPAR_data = raster2array(fPAR_path, 1)
                APAR_data = 1.0 * PAR_data * fPAR_data
                outFile = os.path.join(UAS_APAR_dir, file[:-8] + 'APAR.tif')
                array2raster(fPAR_path, outFile, APAR_data)
            else:
                print 'no CIMIS SR file is found for date ' + date_CIMIS
    print 'III finished - APAR is calculated for all fPAR files'

