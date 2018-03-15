# this code fuse the sUAS data with the RapidEye data
import gdal
import os
import osr
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
# import shutil
# import glob

# Define functions
def raster2array(rasterfn, i):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(i)
    return band.ReadAsArray()


def array2raster(rasterfn, newRasterfn, array):
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

## This function will return the datetime in items which is the closest to the date pivot
def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))

## A simple method for reconstructing a high quality NDVI time-series data set based on the Savitzky-Golay filter", Jin Chen et al. 2004
def savitzky_golay_filtering(timeseries, wnds=[11, 7], orders=[2, 4], debug=True):
    interp_ts = pd.Series(timeseries)
    interp_ts = interp_ts.interpolate(method='linear', limit=14)
    smooth_ts = interp_ts
    wnd, order = wnds[0], orders[0]
    F = 1e8
    W = None
    it = 0
    while True:
        smoother_ts = savgol_filter(smooth_ts, window_length=wnd, polyorder=order)
        diff = smoother_ts - interp_ts
        sign = diff > 0
        if W is None:
            W = 1 - np.abs(diff) / np.max(np.abs(diff)) * sign
            wnd, order = wnds[1], orders[1]
        fitting_score = np.sum(np.abs(diff) * W)
        print it, ' : ', fitting_score
        if fitting_score > F:
            break
        else:
            F = fitting_score
            it += 1
        smooth_ts = smoother_ts * sign + interp_ts * (1 - sign)
    if debug:
        return smooth_ts, interp_ts
    return smooth_ts
## a function that extracts a Wsize*Wsize raster centered at [Row,Col] from the original raster
def ExtractMovingWindow(Wsize,Raster,RR,CC):
    if Wsize % 2 == 0:
        return 0
    Length = (Wsize-1)/2
    if RR < Length:
        if CC < Length:
            Out_Raster = Raster[0:(RR + Length + 1), 0:(CC + Length + 1)]
        else:
            Out_Raster = Raster[0:(RR + Length + 1), (CC - Length):(CC + Length + 1)]
    elif CC < Length:
        Out_Raster = Raster[(RR - Length):(RR + Length + 1), 0:(CC + Length + 1)]
    else:
        Out_Raster = Raster[(RR - Length):(RR + Length + 1), (CC - Length):(CC + Length + 1)]
    return Out_Raster
RapidEye_Ori_dir = '/z0/lh349796/Rangeland/Rapid_eye/IIII_Interpolated_data/Camatta/2017growing_30cm/Interpolated_final_cubic'#'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye'
Drone_Ori_dir = '/z0/lh349796/Rangeland/UAS/Camatta/II_Clipped_Resampled_NDVI_30cm'#'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI'
Drone_Inte_dir = '/z0/lh349796/Rangeland/UAS/Camatta/II_Cliipped_Resampled_InteRapMW_NDVI_daily_30cm'#'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye_Intepolated_I'
Drone_Smooth_dir = '/z0/lh349796/Rangeland/UAS/Camatta/II_Clipped_Resampled_InteRapMW_Smooth2_NDVI_daily_30cm'#'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye_Smoothed_II'
if not os.path.exists(Drone_Inte_dir):
    os.makedirs(Drone_Inte_dir)
if not os.path.exists(Drone_Smooth_dir):
    os.makedirs(Drone_Smooth_dir)
## preset data fusion parameters
Moving_Window_Size = 51 # has to be an odd number and bigger than 17 (500/30 = 16.6666)
Num_Class = 15 # number of class being classified in the unsupervised classification before data fusion
## get dates for the whole RapidEye time series
date_str = []
for file in os.listdir(RapidEye_Ori_dir):
    if file.endswith("ndvi_processed.tif"):
        date_str.append(file[0:8])
datelist_str = sorted(list(set(date_str)))
## convert datelist_str to a datetime object
datelist = []
for date_var in datelist_str:
    temp = datetime.strptime(date_var, '%Y%m%d')
    datelist.append(date(temp.year, temp.month, temp.day))
## get dates of available drone images
date_str_drone = []
for file in os.listdir(Drone_Ori_dir):
    if file.endswith("NDVI.tif"):
        date_str_drone.append(file[8:16])
## convert date_str_drone to a datetime object
datelist_drone = []
for date_var in date_str_drone:
    temp = datetime.strptime(date_var, '%m%d%Y')
    datelist_drone.append(date(temp.year, temp.month, temp.day))
datelist_drone = sorted(datelist_drone)
print 'Getting ready to interpolate and smooth...'
# Interpolation and Smoothing
for d in datelist:
    print 'interpolating date '+ d.strftime('%Y%m%d')
    Target_drone_filename = 'Camatta_' + d.strftime('%m%d%Y') + '_NDVI.tif'
    Target_rapideye_filename = d.strftime('%Y%m%d')+'_mosaicked_ndvi_processed.tif'
    Target_rapideye_image = raster2array(os.path.join(RapidEye_Ori_dir,Target_rapideye_filename),1)
    Saving_drone_filename = 'Camatta_' + d.strftime('%Y-%m-%d') + '_NDVI.tif'
    OutFile_dir = os.path.join(Drone_Inte_dir,Saving_drone_filename)
    if os.path.exists(os.path.join(Drone_Ori_dir, Target_drone_filename)):
        Image = raster2array(os.path.join(Drone_Ori_dir, Target_drone_filename),1)
        array2raster(os.path.join(RapidEye_Ori_dir,Target_rapideye_filename),
                     OutFile_dir,
                     Image)
    else:
        # find a earlier drone image closest to the target date
        Base_drone_filename_before = 'Camatta_' + nearest([i for i in datelist_drone if i < d],d).strftime('%m%d%Y') + '_NDVI.tif'
        Base_rapideye_filename_before = nearest([i for i in datelist_drone if i < d],d).strftime('%Y%m%d') +'_mosaicked_ndvi_processed.tif'
        Base_drone_image_before = raster2array(os.path.join(Drone_Ori_dir,Base_drone_filename_before),1)
        Base_rapideye_image_before = raster2array(os.path.join(RapidEye_Ori_dir,Base_rapideye_filename_before),1)
        # find a later drone image closest to the target date
        Base_drone_filename_after = 'Camatta_' + nearest([i for i in datelist_drone if i > d], d).strftime('%m%d%Y') + '_NDVI.tif'
        Base_rapideye_filename_after = nearest([i for i in datelist_drone if i > d], d).strftime('%Y%m%d') +'_mosaicked_ndvi_processed.tif'
        Base_drone_image_after = raster2array(os.path.join(Drone_Ori_dir, Base_drone_filename_after), 1)
        Base_rapideye_image_after = raster2array(os.path.join(RapidEye_Ori_dir,Base_rapideye_filename_after), 1)
        # calculate the coorelation between before-target and after-target
        Target_drone_image = np.copy(Base_drone_image_before) # this is just copying the raster, can not use = because python variables are names bound to objects
        Target_drone_image[Target_drone_image != Base_drone_image_before[0, 0]] = Base_drone_image_before[0, 0]
        for Row in range(0, Base_drone_image_before.shape[0]):# fuse the pixels one by one
            for Col in range(0, Base_drone_image_before.shape[1]):
                print 'Fusing Row '+ str(Row) + ' Col ' + str(Col) + ' ...'
                if Base_drone_image_before[Row, Col] == Base_drone_image_before[0, 0]:# see if the targeted pixel is a background pixel
                    continue
                else:
                    MW = ExtractMovingWindow(Moving_Window_Size, Base_rapideye_image_before, Row, Col)
                    L1 = np.reshape(MW, (np.product(MW.shape), 1))#reshaping the original raster to vector
                    MW = ExtractMovingWindow(Moving_Window_Size, Base_rapideye_image_after, Row, Col)
                    L2 = np.reshape(MW, (np.product(MW.shape), 1))
                    MW = ExtractMovingWindow(Moving_Window_Size, Target_rapideye_image, Row, Col)
                    L3 = np.reshape(MW, (np.product(MW.shape), 1))
                    ## calculate weight based on correlation
                    df13 = pd.DataFrame(np.column_stack((L1, L3)), columns=list('AB'))
                    df13[df13 == 0] = np.nan
                    df23 = pd.DataFrame(np.column_stack((L1, L2)), columns=list('AB'))
                    df23[df23 == 0] = np.nan
                    W13 = df13.corr()['A']['B'] /(df23.corr()['A']['B'] + df13.corr()['A']['B']  )
                    W23 = 1-W13
                    Target_drone_image[Row, Col] = W13*(Target_rapideye_image[Row, Col] + Base_drone_image_before[Row, Col] - Base_rapideye_image_before[Row, Col]) + W23 * (Target_rapideye_image[Row, Col] + Base_drone_image_after[Row, Col] - Base_rapideye_image_after[Row, Col])
        ##Target_drone_image = W13*(Target_rapideye_image + Base_drone_image_before - Base_rapideye_image_before) + W23 * (Target_rapideye_image + Base_drone_image_after - Base_rapideye_image_after)
        array2raster(os.path.join(RapidEye_Ori_dir,Target_rapideye_filename),
                     os.path.join(Drone_Inte_dir,Saving_drone_filename),
                     Target_drone_image)
print 'interpolation and smoothing complete!'

## Smoothing
print 'Smoothing Started...'
print 'converting the TIFFs to numpy array...'
Multi_raster_path = []
for raster in os.listdir(Drone_Inte_dir):
    if raster.endswith('NDVI.tif'):
        raster_path = os.path.join(Drone_Inte_dir, raster)
        Multi_raster_path.append(raster_path)
Multi_raster_path = sorted(Multi_raster_path)
Multi_raster = []
for raster_path in Multi_raster_path:
    print 'reading in file' + raster_path
    Multi_raster.append(raster2array(raster_path, 1))
Raster_array = np.array(Multi_raster)
Raster_dim = Raster_array.shape
print 'Conversion finished!'
for row in np.arange(Raster_dim[1]):
    for col in np.arange(Raster_dim[2]):
# col = 548
# row = 147
        print 'applying the SavGol filter to pixel (' + str(row) + ',' + str(col) + ')...'
        time_series = pd.Series(Raster_array[:, row, col])
        ## apply SavGol filter
        time_series_savgol = savgol_filter(time_series, window_length=31, polyorder=2)
        #time_series_savgol = savitzky_golay_filtering(time_series_savgol_1, wnds=[11, 7], orders=[2, 4], debug=False)
        Raster_array[:, row, col] = time_series_savgol
        print 'interpolation and smoothing for pixel (' + str(row) + ',' + str(col) + ') is finished!'

print 'interpolation and smoothing complete!'
# ts = pd.DataFrame(Raster_array[:, row, col])
# ts.to_csv(os.path.join(Drone_Smooth_dir,'R'+str(row)+'C'+str(col)+'.csv'))

# saving the results
filelist = []
for file in os.listdir(Drone_Inte_dir):
    if file.endswith("NDVI.tif"):
        file_path = os.path.join(Drone_Inte_dir, file)
        filelist.append(file)
filelist = sorted(set(filelist))
for date_var in np.arange(Raster_dim[0]):
    OutFile = os.path.join(Drone_Smooth_dir, filelist[date_var])
    InFile = os.path.join(Drone_Inte_dir, filelist[1])
    raster = Raster_array[date_var, :, :]
    print 'Saving ' + OutFile + '...'
    array2raster(InFile, OutFile, raster)

# Image_H1 = raster2array('C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI/Camatta_02152017_NDVI.tif', 1)
# # Image_H2 = raster2array('C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI/Camatta_03172017_NDVI.tif', 1)
# Image_L1 = raster2array("C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye/20170215_mosaicked_ndvi_processed.tif", 1)
# Image_L2 = raster2array("C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye/20170317_mosaicked_ndvi_processed.tif", 1)
# Image_L3 = raster2array("C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI_RapidEye/20170309_mosaicked_ndvi_processed.tif", 1)
# # date = datelist[110]
# # # Image_L1[Image_L1 == 0] = np.nan # or use np.nan
# # # Image_L3[Image_L3 == 0] = np.nan
# # Image_H3 = Image_L3 + Image_H2 - Image_L2
# # array2raster('C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI/Camatta_02152017_NDVI.tif',
# #              'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/NDVI/Camatta_03092017_Intepolated.tif',
# #              Image_H3)