########################################################################################################################
###~~~~~~~~~`~~STEP 3 Interpolation and Smoothing~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
########################################################################################################################
import gdal
import os
import osr
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
import shutil
import glob


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


# for generating a list of date with delta interval
def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta


# Setup Directory Functions#
# Function to create directories - written by Andy J.Y. Wong
def createFolders(Path, Objects):
    for folder in Objects:
        folder_Path = os.path.join(Path, folder)
        if not os.path.exists(folder_Path):
            os.mkdir(folder_Path)
    return


# Function to remove files in a defined directories  -  written by Andy J.Y. Wong
def RemoveFilesInFolder(Path):
    import os
    for file in os.listdir(Path):
        target = os.path.join(Path, file)
        if os.path.isfile(target):
            os.remove(target)
    return


# function to do spatial interpolation - written by Han Liu
def SpatialInterpolation(col, row, Raster_array, Raster_dim):
    if col == 0 and row == 0:
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row + 1, col],
                                                     Raster_array[:, row, col + 1],
                                                     Raster_array[:, row + 1, col + 1]]), axis=0))
    elif col != 0 and row == 0 and col != (Raster_dim[2] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row, col - 1],
                                                     Raster_array[:, row, col + 1],
                                                     Raster_array[:, row + 1, col - 1],
                                                     Raster_array[:, row + 1, col],
                                                     Raster_array[:, row + 1, col + 1]]), axis=0))
    elif row == 0 and col == (Raster_dim[2] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row, col - 1],
                                                     Raster_array[:, row + 1, col],
                                                     Raster_array[:, row + 1, col - 1]]), axis=0))
    elif col == 0 and row != 0 and row != (Raster_dim[1] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col],
                                                     Raster_array[:, row + 1, col],
                                                     Raster_array[:, row - 1, col + 1],
                                                     Raster_array[:, row, col + 1],
                                                     Raster_array[:, row + 1, col + 1]]), axis=0))
    elif col != 0 and row != 0 and row != (Raster_dim[1] - 1) and col != (Raster_dim[2] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col - 1],
                                                     Raster_array[:, row - 1, col],
                                                     Raster_array[:, row - 1, col + 1],
                                                     Raster_array[:, row, col - 1],
                                                     Raster_array[:, row, col + 1],
                                                     Raster_array[:, row + 1, col - 1],
                                                     Raster_array[:, row + 1, col],
                                                     Raster_array[:, row + 1, col + 1]]), axis=0))
    elif col == (Raster_dim[2] - 1) and row != 0 and row != (Raster_dim[1] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col - 1],
                                                     Raster_array[:, row - 1, col],
                                                     Raster_array[:, row, col - 1],
                                                     Raster_array[:, row + 1, col - 1],
                                                     Raster_array[:, row + 1, col]]), axis=0))
    elif row == (Raster_dim[1] - 1) and col == 0:
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col],
                                                     Raster_array[:, row - 1, col + 1],
                                                     Raster_array[:, row, col + 1]]), axis=0))
    elif col != 0 and col != (Raster_dim[2] - 1) and row == (Raster_dim[1] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col - 1],
                                                     Raster_array[:, row - 1, col],
                                                     Raster_array[:, row - 1, col + 1],
                                                     Raster_array[:, row, col - 1],
                                                     Raster_array[:, row, col + 1]]), axis=0))
    elif row == (Raster_dim[1] - 1) and col == (Raster_dim[2] - 1):
        time_series = pd.Series(np.nanmean(np.array([Raster_array[:, row - 1, col - 1],
                                                     Raster_array[:, row - 1, col],
                                                     Raster_array[:, row, col - 1]]), axis=0))
    return time_series


# functions end
Site_name = ['Camatta']
for ii in np.arange(len(Site_name)):
    #Rapideye_Ref_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/III_Processed_data',Site_name[ii],'2017growing/NDVI_30cm') #where the refectance data are saved
    Rapideye_NDVI_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/III_Processed_data',Site_name[ii],'2017growing','NDVI_30cm')
    Rapideye_inter_1_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/IIII_Interpolated_data',Site_name[ii],'2017growing_30cm','Interpolated_Nan_cubic') #save the whole time series with NANs
    Rapideye_inter_2_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/IIII_Interpolated_data',Site_name[ii], '2017growing_30cm','Interpolated_final_cubic') #save the final products
    Rapideye_inter_dir = Rapideye_inter_2_dir  # the processed the Rapideye data
    Rapideye_fPAR_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/IIII_Interpolated_data',Site_name[ii],'2017growing_30cm','fPAR')  # where the calculated fPAR data
    Rapideye_APAR_dir = os.path.join('/z0/lh349796/Rangeland/PlanetScope/IIII_Interpolated_data',Site_name[ii],'2017growing_30cm','APAR')  # where the APAR data will be saved
    if not os.path.exists(Rapideye_fPAR_dir):
        os.makedirs(Rapideye_fPAR_dir)
    if not os.path.exists(Rapideye_APAR_dir):
        os.makedirs(Rapideye_APAR_dir)
    # ~ Step 1 ~  Read in the data and create NAN tiffs for missing dates
    ## Loop through file directory, create a list of date  and file
    print 'reading in the PlanetScope dataset...'
    if not os.path.exists(Rapideye_inter_1_dir):
        os.makedirs(Rapideye_inter_1_dir)
    if not os.path.exists(Rapideye_inter_2_dir):
        os.makedirs(Rapideye_inter_2_dir)
    date_str =[]
    filelist = []
    for file in os.listdir(Rapideye_NDVI_dir):
        if file.endswith("ndvi.tif"):
            file_path = os.path.join(Rapideye_NDVI_dir, file)
            #print file_path
            date_str.append(file.split('_')[2])
            filelist.append(file)
    datelist_str = sorted(list(set(date_str)))
    filelist = sorted(filelist, key=lambda x: x.split('_')[2])
    ## convert datelist to a datetime object
    datelist = []
    for date_var in datelist_str:
        temp = datetime.strptime(date_var, '%Y-%m-%d')
        datelist.append(date(temp.year, temp.month, temp.day))
    # Check the 1 day interval and add empty raster
    date_start = datelist[0]
    date_end = datelist[len(datelist)-1]
    datelist_whole = []
    for result in perdelta(date_start, date_end, timedelta(days=1)):
        datelist_whole.append(result)
    ## check the 16 days interval and add empty raster
    i = 0 #for looping through the Rapideye dates
    for date_whole in datelist_whole:
        if date_whole == datelist[i]:
            day_of_year = date_whole.strftime('%Y-%m-%d')
            print "PlanetScope data existed for date " + str(datelist[i])
            #print os.path.join(Rapideye_NDVI_dir, '*'+ datelist[i] + '*ndvi.tif')
            InFile = glob.glob(os.path.join(Rapideye_NDVI_dir, '*'+ day_of_year + '*ndvi.tif'))[0]
            OutFile = os.path.join(Rapideye_inter_1_dir, 'PS_' + day_of_year + '_ndvi_daily.tif')
            array2raster(InFile, OutFile, raster2array(InFile,1))
            i = i + 1
        elif datelist[i] > date_whole:
            print "creating a scene for date " + str(date_whole) + " ..."
            day_of_year = date_whole.strftime('%Y-%m-%d')
            InFile = os.path.join(Rapideye_NDVI_dir, filelist[i])
            raster = raster2array(InFile,1)
            raster[~np.isnan(raster)] = np.nan
            OutFile = os.path.join(Rapideye_inter_1_dir, 'PS_' + day_of_year + '_simu_ndvi_daily.tif')
            array2raster(InFile, OutFile, raster)
    print 'Rapideye dataset are readed'
    ##~ Step 2 ~  Interpolation & Smoothing (SG filter)
    ##read in rasters as a 3d arrary
    print 'converting the TIFFs to numpy array...'
    Multi_raster_path = []
    for raster in os.listdir(Rapideye_inter_1_dir):
        if raster.endswith('ndvi_daily.tif'):
            raster_path = os.path.join(Rapideye_inter_1_dir, raster)
            Multi_raster_path.append(raster_path)
    Multi_raster_path = sorted(Multi_raster_path)
    #print Multi_raster_path
    Multi_raster = []
    for raster_path in Multi_raster_path:
        Multi_raster.append(raster2array(raster_path, 1))
    Raster_array = np.array(Multi_raster)
    Raster_dim = Raster_array.shape
    print 'Conversion finished!'
    print 'Getting ready to interpolate and smooth...'
    # Interpolation and Smoothing
    for row in np.arange(Raster_dim[1]):
        for col in np.arange(Raster_dim[2]):
            print 'interpolating pixel (' + str(row) + ',' + str(col) + ')...'
            time_series = pd.Series(Raster_array[:, row, col])
            # interpolate missing data
            ## do spatial interpolation if there is less than 3 non nans in a time series
            if np.count_nonzero(~np.isnan(time_series)) <= 3:
                time_series = SpatialInterpolation(col, row, Raster_array, Raster_dim)
            time_series_interp = time_series.interpolate(method="linear")
            print 'applying the SavGol filter to pixel (' + str(row) + ',' + str(col) + ')...'
            # apply SavGol filter
            time_series_savgol = savgol_filter(time_series_interp, window_length=15, polyorder=2)
            time_series_savgol = savgol_filter(time_series_savgol, window_length=5, polyorder=3)
            Raster_array[:, row, col] = time_series_savgol
            print 'interpolation and smoothing for pixel (' + str(row) + ',' + str(col) + ') is finished!'
    print 'interpolation and smoothing complete!'
    # ~ Step 3 ~ Save the processed rasters
    print 'Getting ready to save the results...'
    # datelist_str = []
    # filelist = []
    # for file in os.listdir(Rapideye_inter_1_dir):
    #     if file.endswith("ndvi.tif"):
    #         file_path = os.path.join(Rapideye_inter_1_dir, file)
    #         date_str.append(file.split('_')[1])
    #         filelist.append(file)
    # datelist_str = sorted(set(date_str))
    # filelist = sorted(set(filelist))
    for date_var in np.arange(Raster_dim[0]):
        OutFile = os.path.join(Rapideye_inter_2_dir, os.path.basename(Multi_raster_path[date_var]))
        InFile = Multi_raster_path[0]
        raster = Raster_array[date_var, :, :]
        #print 'Saving ' + OutFile + '...'
        array2raster(InFile, OutFile, raster)
    print np.arange(Raster_dim[0])
    print len(filelist)
    shutil.rmtree(Rapideye_inter_1_dir)

print 'code running complete!'
