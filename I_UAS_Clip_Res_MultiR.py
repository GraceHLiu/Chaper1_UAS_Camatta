# This script reads in the multiband reflectance in I_Raw, and 1) clip and resample with the same box and resolution;
#                                                              2) do topo-correction using the cosine model (used the C model R not the cosine model here)
#                                                              3) calculate vegetation indices
# box = Camatta boundary
# resolution = 30cm
# Input - multispectral tif rasters of sr from rededge
# Output - 1) Cliped and resampled reflectance (single band)
#          2) Topo-corrected reflectance (single band)
#          3) VIs

import os
import osr
from osgeo import gdal
import sys
import glob
import numpy as np
from datetime import datetime

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

# ##########################################################################################################################
# ######################################## step 1: Clipping and Resampling #################################################
# ##########################################################################################################################
# print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# print '<<<<<<<<<<<<<<<<<<<<<<<<< STEP 1 Clipping and Resampling <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# Raw_data_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/I_Raw/SLO_sUAS_b4Geo/Camatta_01162018/dsm'# where the multirasters of reflectance are
Clip_Res_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/I_cliped_resampled/Res_30cm'#'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/II_Clipiped_Resampled/SR_30cm'# where the cliped and resampled data are saved
# Box_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/SpatialData/Camatta_box.shp' # where the boundary shapefile is saved
#
# if not os.path.exists(Clip_Res_dir):
#    os.makedirs(Clip_Res_dir)
#
# for file in os.listdir(Raw_data_dir):
#     if file.endswith('2018_dsm.tif'): #or file.endswith('2017.tif'):
#         Input_dir = os.path.join(Raw_data_dir,file)
#         Output_dir = os.path.join(Clip_Res_dir,file)
#         os.system('gdalwarp -overwrite -crop_to_cutline -cutline "' + Box_dir + '" -tr 0.3 0.3 -r cubic "' + Input_dir + '" "' + Output_dir + '"')

# ##########################################################################################################################
# ######################################## step 2: Illumination Correction #################################################
# ##########################################################################################################################
# # print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# # print '<<<<<<<<<<<<<<<<<<<<<<<<< STEP 2 Illumination Correction<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# # print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
# C MODEL IS IN R
TopoCorrect_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/III_Topo_Correct/SR_30cm_CModel'# 7/7/2017 update using c model# where the topographic corrected images are saved
# IC_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/III_Topo_Correct/IC_30cm'# where the illumination condition data are saved
# # Cos_zenith = dict(zip(('11112016','01162017','02152017','03172017','04062017','04302017'),(0.5986, 0.5433,0.6551,0.7281,0.8194,0.871)))
# # Bands = dict(zip(('b1','b2','b3','b4','b5'),('rededge','red','nir','green','blue')))
Site = 'Camatta'
# #
# # if not os.path.exists(TopoCorrect_dir):
# #    os.makedirs(TopoCorrect_dir)
# #
# for file in os.listdir(Clip_Res_dir):
#     if file.endswith('2016.tif') or file.endswith('2017.tif'):
#         Date_str = file[8:16]
#         Raster_IC_dir = glob.glob(os.path.join(IC_dir,Site + '_'+ Date_str + '_IC.tif'))[0]
#         Array_IC = raster2array(Raster_IC_dir, 1)
#         Input_dir = os.path.join(Clip_Res_dir, file)
#         Raster_ref = gdal.Open(Input_dir)
#         if Raster_ref is None:
#             print 'Unable to open INPUT.tif'
#             sys.exit(1)
#         print "[ RASTER BAND COUNT ]: ", Raster_ref.RasterCount
#         for band in range(Raster_ref.RasterCount):
#             band += 1
#             Array_ref_before = raster2array(Input_dir, band)
#             Array_ref_after = Array_ref_before * Cos_zenith[Date_str]/Array_IC
#             print("Topographically correcting the Reflectance of band" + str(band) + " of image " + file + " on " + Date_str + "...")
#             Output_dir = os.path.join(TopoCorrect_dir, Site + '_' + Date_str + '_Topoed_' + Bands['b'+str(band)] + '.tif')
#             array2raster(Input_dir, Output_dir, Array_ref_after)
#             print("done!")

# ##########################################################################################################################
# ######################################## step 3: Calculating VIs #########################################################
# ##########################################################################################################################
print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
print '<<<<<<<<<<<<<<<<<<<<<<<<< STEP 3 CALCULATING VIs<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
Mother_Index_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_Cmodel'
Index_dir = dict(zip(('NDVI','RDVI','EVI','EVI2','SR','MSAVI','ISI','NIDI','YVI'),
                     (os.path.join(Mother_Index_dir, 'NDVI'),
                      os.path.join(Mother_Index_dir, 'RDVI'),
                      os.path.join(Mother_Index_dir, 'EVI'),
                      os.path.join(Mother_Index_dir, 'EVI2'),
                      os.path.join(Mother_Index_dir, 'SR'),
                      os.path.join(Mother_Index_dir, 'MSAVI'),
                      os.path.join(Mother_Index_dir, 'ISI'),
                      os.path.join(Mother_Index_dir, 'NIDI'),
                      os.path.join(Mother_Index_dir, 'YVI'))))
Indices = ['NDVI','RDVI','EVI','EVI2','SR','MSAVI','ISI','NIDI','YVI'] # http://bleutner.github.io/RStoolbox/rstbx-docu/spectralIndices.html and https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3859895/

if not os.path.exists(Mother_Index_dir):
    os.makedirs(Mother_Index_dir)

Date_list = []
for file in os.listdir(TopoCorrect_dir):
    if file.endswith('2018_Topoed_red.tif'):
        Date_list.append(datetime.strptime(file[8:16], '%m%d%Y'))
Date_list = sorted(set(Date_list))

for index in Indices:
    if not os.path.exists(Index_dir[index]):
        os.makedirs(Index_dir[index])
    for date in Date_list:
        print 'Calulating index '+ index + ' for images on date '+ str(date)
        date_str = '%02d' % date.month + '%02d' % date.day + str(date.year)
        B_green_path = glob.glob(os.path.join(TopoCorrect_dir, Site + '_' + date_str + '_Topoed_green.tif'))[0]
        B_red_path = glob.glob(os.path.join(TopoCorrect_dir,Site + '_' + date_str + '_Topoed_red.tif'))[0]
        B_nir_path = glob.glob(os.path.join(TopoCorrect_dir, Site + '_' + date_str + '_Topoed_nir.tif'))[0]
        B_blue_path = glob.glob(os.path.join(TopoCorrect_dir, Site + '_' + date_str + '_Topoed_blue.tif'))[0]
        B_rededge_path = glob.glob(os.path.join(TopoCorrect_dir, Site + '_' + date_str + '_Topoed_rededge.tif'))[0]
        B_green = raster2array(B_green_path, 1)
        B_red = raster2array(B_red_path,1)
        B_nir = raster2array(B_nir_path,1)
        B_blue = raster2array(B_blue_path,1)
        B_rededge = raster2array(B_rededge_path,1)
        if index == 'NDVI':
            NDVI = (B_nir - B_red)/(B_nir + B_red)
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, NDVI)
        elif index == 'RDVI':
            NDRI = (B_nir - B_red) / np.sqrt(B_nir + B_red)
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, NDRI)
        elif index == 'EVI':
            EVI = 2.5 * ((B_nir-B_red)/(B_nir + 6 * B_red - 7.5 * B_blue + 1))
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, EVI)
        elif index == 'EVI2':
            EVI2 = 2.5 * ((B_nir - B_red) / (B_nir + 2.4 * B_red + 1))
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, EVI2)
        elif index == 'MSAVI':
            MSAVI = B_nir + 0.5 - 0.5 * np.sqrt((2 * B_nir + 1) * (2 * B_nir + 1) - 8 * (B_nir-2 * B_red))
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, MSAVI)
        elif index == 'ISI':
            ISI = B_nir - B_rededge
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, ISI)
        elif index == 'NIDI':
            NIDI = (B_nir - B_rededge) / (B_nir + B_rededge)
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, NIDI)
        elif index == 'SR':
            NIDI = B_nir / B_red
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, NIDI)
        elif index == 'YVI':
            YVI = (B_red - B_green)/(B_green + B_red)
            Output_dir = os.path.join(Index_dir[index], Site + '_' + date_str + '_' + index + '.tif')
            array2raster(B_red_path, Output_dir, YVI)
