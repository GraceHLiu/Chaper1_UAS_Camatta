import os
from datetime import date, timedelta
import glob
import osr
import gdal
import numpy

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
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

Asol_dir= 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/Daily_Solar/'
Asol_Ave_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/Daily_Solar_Ave/'
CIMIS_Rs_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/PAR/'
Output_Rs_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/Daily_Input_Rs/'

if not os.path.exists(Output_Rs_dir):
    os.makedirs(Output_Rs_dir)

Dates = perdelta(date(2016, 10, 1), date(2017, 5,1), timedelta(days=1))
for Date in Dates:
    Asol_path = glob.glob(os.path.join(Asol_dir, 'AreaSol_' + Date.strftime('%Y%j') + '.tif'))
    Asol_Ave_path = glob.glob(os.path.join(Asol_Ave_dir, 'AreaSol_' + Date.strftime('%Y%j') + '.tif'))
    CIMIS_Rs_path = glob.glob(os.path.join(CIMIS_Rs_dir, Date.strftime('%Y%m%d') + 'Rs_Camatta.tif'))
    print len(Asol_path) * len(Asol_Ave_path) * len(CIMIS_Rs_path)
    if len(Asol_path)*len(Asol_Ave_path)*len(CIMIS_Rs_path)!=0:
        print 'processing date ' + Date.strftime('%Y%m%d') + '...'
        Asol = raster2array(Asol_path[0],1)
        Asol_Ave = raster2array(Asol_Ave_path[0],1)
        CIMIS_Rs = raster2array(CIMIS_Rs_path[0],1)

        Output_Rs = Asol/Asol_Ave*CIMIS_Rs

        Output_path = os.path.join(Output_Rs_dir,os.path.basename(CIMIS_Rs_path[0]))
        array2raster(CIMIS_Rs_path[0], Output_path, Output_Rs)
