# The Difference between this code and UAS_NDVI2PAR.py is that this code generates daily PAR whereas
# the other one only generates APAR on the dates of flight with quadratic method!!! better than cubic
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
    # print 'I - start interpolating monthly NDVI to daily'
    # # create a datelist of the files
    # datelist = []
    # #filelist = []
    # for file in os.listdir(UAS_NDVI_dir):
    #     if file.endswith('NDVI.tif'):
    #         temp = datetime.strptime(file[8:16], '%m%d%Y')
    #         datelist.append(date(temp.year, temp.month, temp.day))
    #         #filelist.append(file)
    # datelist = sorted(datelist)
    # #filelist = sorted(filelist)
    # # create daily list for interpolation
    # date_start = datelist[0]
    # date_end = datelist[len(datelist) - 1]
    # datelist_daily = []
    # for result in perdelta(date_start, date_end, timedelta(days=1)):
    #     datelist_daily.append(result)
    # datelist_daily.append(date_end)
    # # generate empty tiffs for non-exist dates
    # i = 0  # for looping through datelist
    # for date in datelist_daily:
    #     if date == datelist[i]:
    #         print "I - sUAS data existed for date " + str(datelist[i])
    #         InFile = glob.glob(UAS_NDVI_dir+'/' +site+'_'+ '%02d' % datelist[i].month + '%02d' % datelist[i].day + str(datelist[i].year) + '*.tif')[0]
    #         day_of_year = date.strftime('%Y%j')
    #         OutFile = os.path.join(UAS_NDVIdaily_dir_temp, site + '_' + day_of_year + "_NDVI.tif")
    #         image = raster2array(InFile, 1)
    #         array2raster(InFile, OutFile, image)
    #         i += 1
    #     elif datelist[i] > date:
    #         print "I - creating a scene for date " + str(date) + " ..."
    #         day_of_year = date.strftime('%Y%j')
    #         OutFile = os.path.join(UAS_NDVIdaily_dir_temp, site + '_' + day_of_year + "_NDVI.tif")
    #         InFile = glob.glob(UAS_NDVI_dir+'/' +site+'_'+ '%02d' % datelist[i].month + '%02d' % datelist[i].day + str(datelist[i].year) + '*.tif')[0]
    #         raster = raster2array(InFile, 1)
    #         raster[-np.isnan(raster)] = np.nan
    #         array2raster(InFile, OutFile, raster)
    # print 'I - Daily temp NDVI is generated!'
    # print 'I - Start reading in tiffs as Multi-raster...'
    # Multi_raster_path = []
    # for raster in os.listdir(UAS_NDVIdaily_dir_temp):
    #     if raster.endswith('NDVI.tif'):
    #         raster_path = os.path.join(UAS_NDVIdaily_dir_temp, raster)
    #         Multi_raster_path.append(raster_path)
    # Multi_raster_path = sorted(Multi_raster_path)
    # Multi_raster = []
    # for raster_path in Multi_raster_path:
    #     Multi_raster.append(raster2array(raster_path, 1))
    # Raster_array = np.array(Multi_raster)
    # Raster_dim = Raster_array.shape
    # print 'I - Finish reading in tiffs as Multi-raster'
    # print 'I - Getting ready to interpolate'
    # Interpolation with cubic
    # fillin_values = pd.Series(Raster_array[:, 0, 0])
    # for row in np.arange(Raster_dim[1]):
    #     for col in np.arange(Raster_dim[2]):
    #         print 'interpolating pixel (' + str(row) + ',' + str(col) + ')...'
    #         print 'number of valid NDVI is ' + str(sum(~np.isnan(Raster_array[:, row, col])))
    #         if sum(~np.isnan(Raster_array[:, row, col]))<6:
    #             Raster_array[:, row, col] = fillin_values
    #         else:
    #             time_series = pd.Series(Raster_array[:, row, col])
    #             # interpolate missing data
    #             time_series_interp = time_series.interpolate(method="cubic")
    #             Raster_array[:, row, col] = time_series_interp
    #         print 'I - Cubic interpolation for pixel (' + str(row) + ',' + str(col) + ') is finished!'
    # print 'I - Interpolation complete!'
    # print 'I - Saving the interpolation results...'
    # for date in np.arange(Raster_dim[0]):
    #     OutFile = os.path.join(UAS_NDVIdaily_dir, site + '_' + str(datelist_daily[date]) + '_NDVI.tif')
    #     #InFile = os.path.join(UAS_NDVIdaily_dir_temp, filelist[i])
    #     raster =  Raster_array[date, :, :]
    #     print 'Saving ' + OutFile + '...'
    #     array2raster(InFile, OutFile, raster)
    # print 'I - daily NDVI interpolation complete!'
    #
    # shutil.rmtree(UAS_NDVIdaily_dir_temp)
    print 'II - start converting NDVI to fPAR'
    # for file in os.listdir(UAS_NDVIdaily_dir):
    #     if file.endswith('NDVI.tif'):
    #         NDVI_path = os.path.join(UAS_NDVIdaily_dir, file)
    #         raster_ndvi = raster2array(NDVI_path, 1)
    #         raster_fPAR = (raster_ndvi - NDVI_min) * (fPAR_max - fPAR_min) / (NDVI_max - NDVI_min) + fPAR_min
    #         raster_fPAR[raster_fPAR < 0] = 0
    #         raster_fPAR[raster_fPAR > fPAR_max] = fPAR_max
    #         export_file = os.path.join(UAS_fPAR_dir, file[:-8] + 'fPAR.tif')
    #         print("I - Calculating fPAR of file " + file + "...")
    #         array2raster(NDVI_path, export_file, raster_fPAR)
    # print 'II finished - fPAR is calculated for all NDVI files'
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

