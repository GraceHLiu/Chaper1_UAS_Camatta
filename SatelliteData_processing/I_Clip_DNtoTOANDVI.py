import os, glob,math,json,ogr, osr
from datetime import datetime
from osgeo import gdal
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import numpy as np
import sys
from xml.dom import minidom

## Define functions
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
# Define Directories
Site_name = ['BlueDoor','BlueFire','HorseFire','HorseLakeFire','NelsonFire','RushFire']#,'HorseFire','Ashley','BlueDoor','BlueFire','HorseFire','HorseFire','HorseLakeFire','NelsonFire','Scorpion']
Box = ['/z0/lh349796/Rangeland/PlanetScope/SpatialData/BlueDoor_Bound.shp',
       '/z0/lh349796/Rangeland/PlanetScope/SpatialData/BlueFire_Bound.shp',
       '/z0/lh349796/Rangeland/PlanetScope/SpatialData/HorseFire_Bound.shp',
       '/z0/lh349796/Rangeland/PlanetScope/SpatialData/HorseLakeFire_Bound.shp',
       '/z0/lh349796/Rangeland/PlanetScope/SpatialData/NelsonFire_Bound.shp',
       '/z0/lh349796/Rangeland/PlanetScope/SpatialData/RushFire_Bound.shp']
Projection = ['EPSG:26910','EPSG:26910','EPSG:26910',
              'EPSG:26910','EPSG:26910','EPSG:26910']#['EPSG:32610']
######################################################################################
#######IMPORTANT!!for site that has multi-scene input the scene ID by importance #####
######################################################################################
ID = [['1158003'],['1058124'],['1057823'],['1057823'],['1058103'],['1057925']]
for i in range(len(Site_name)):	
    if Site_name[i].startswith('Horse'):
	    rapideye_Raw_Path = os.path.join('/z0/lh349796/Rangeland/PlanetScope/Ori_data', 'Horse')
    else:
    	rapideye_Raw_Path = os.path.join('/z0/lh349796/Rangeland/PlanetScope/Ori_data', Site_name[i]) # Where zipped original data are saved
    rapideye_ndvi_Path = os.path.join('/z0/lh349796/Rangeland/PlanetScope/I_NDVI_data', Site_name[i]) # Where reflectance data are saved
    rapideye_clip_Path = os.path.join('/z0/lh349796/Rangeland/PlanetScope/II_Cliped_data',Site_name[i]) # Where mosaikced data are saved
    rapideye_Inputs_Path = os.path.join('/z0/lh349796/Rangeland/PlanetScope/III_Processed_data',Site_name[i]) #Where reprojected and clipped data are saved

    #### Loop through file directory, create a list of date and band
    if not os.path.exists(rapideye_ndvi_Path):
        os.makedirs(rapideye_ndvi_Path)
    if not os.path.exists(rapideye_clip_Path):
        os.makedirs(rapideye_clip_Path)
    if not os.path.exists(rapideye_Inputs_Path):
        os.makedirs(rapideye_Inputs_Path)
    date =[]
    for file in os.listdir(rapideye_Raw_Path):
        if file.endswith('analytic.tif') and file.split('_')[1]==ID[i][0]:
            date.append(file.split('_')[2])
    datelist = list(sorted(set(date)))
    print(datelist)
    #~ step 1: For a certain date, calculate the TOA and NDVI
    for d in datelist:
        print('Step I - Calculating the NDVI/brightness for date '+ d)
        print(rapideye_Raw_Path + '/*' + ID[i][0] + '_' + d + '*analytic.tif')
        file_path = glob.glob(rapideye_Raw_Path + '/*' + ID[i][0] + '_' + d + '*analytic.tif')[0]
        band_blue = raster2array(file_path, 1)
        band_green = raster2array(file_path, 2)
        band_red = raster2array(file_path, 3)
        band_nir = raster2array(file_path, 4)
        meta_path = glob.glob(rapideye_Raw_Path + '/*' +  ID[i][0] +  '_' + d + '*xml.tif')[0]
        xmldoc = minidom.parse(meta_path)
        nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")
        # XML parser refers to bands by numbers 1-4
        coeffs = {}
        for node in nodes:
            bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
            if bn in ['1', '2', '3', '4']:
                ii = int(bn)
                value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
                coeffs[ii] = float(value)
        # Multiply by corresponding coefficients
        band_blue = band_blue * coeffs[1]
        band_green = band_green * coeffs[2]
        band_red = band_red * coeffs[3]
        band_nir = band_nir * coeffs[4]
        band_blue[band_blue == 0] = np.nan
        band_green[band_green == 0] = np.nan
        band_red[band_red == 0] = np.nan
        band_nir[band_nir == 0] = np.nan
        band_ndvi = 1.0*(band_nir-band_red)/(band_nir+band_red)
        band_bright = 1.0*(band_blue+band_green+band_red)
        ndvi_path = os.path.join(rapideye_ndvi_Path,os.path.basename(file_path)[:-17]+'ndvi.tif')
        array2raster(file_path,ndvi_path,band_ndvi)
        bright_path = os.path.join(rapideye_ndvi_Path,os.path.basename(file_path)[:-17]+'bright.tif')
        array2raster(file_path,bright_path,band_bright)
    # #~Step2: Reproject & Clip XXX.tif
    In_Directory = [rapideye_ndvi_Path]
    for directory in In_Directory:
        for file in os.listdir(directory):
            if file.endswith(".tif"):
                current_file = os.path.join(directory, file)
                export_file = os.path.join(rapideye_clip_Path, file)
                print("Step II - Cliping data " + file + "...")
                os.system('gdalwarp -overwrite -crop_to_cutline -cutline "' + Box[i] + '" -tr 3.125 3.125 -r near -t_srs ' + Projection[i] + ' "' + current_file + '" "' + export_file + '"')
                # print("Step II - Cliping and resampling data " + file + "...")
                # current_file = export_file
                # export_file = os.path.join(rapideye_Inputs_Path, file)
                # os.system('gdalwarp -overwrite -crop_to_cutline -cutline "' + Box[i] + '" -tr 0.3 0.3 -r near -t_srs ' + Projection[i] + ' "' + current_file + '" "' + export_file + '"')
                print("done!")

