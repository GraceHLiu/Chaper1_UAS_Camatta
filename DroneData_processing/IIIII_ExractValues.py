#This code extracts raster values (APAR, VIs and IC) at the location of input shapefiles
import os
from osgeo import gdal, ogr
from datetime import datetime
import glob
import pandas as pd

##Extract daily APAR for modeling
Mother_Product_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel'
#Mother_Product_dir = '/z0/lh349796/Rangeland/UAS/Camatta/III_Processed_data_daily_30cm'
#Product_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/IIII_Processed_data/30cm_CModel/APAR_30cm_daily'#os.path.join(Mother_Product_dir,'APAR')
Products = ['NDVI','APAR']#['NDVI','RDVI','EVI','EVI2','SR','MSAVI','ISI','NIDI','YVI','APAR','IC']
ShapeFile_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/Spatial_data'#'/z0/lh349796/Rangeland/UAS/Camatta/Spatial_data'
Field_list = ['comment','Northing','Easting','DSM_111120','Slope_1111','Aspect_111','AspectC_11','FlowA_1111']
OutPut_dir = 'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/IIIII_Product_Biomass/30cm_CModel'#'/z0/lh349796/Rangeland/UAS/Camatta/IIII_ExractedValues'
Product_dir = dict(zip(('NDVI','RDVI','EVI','EVI2','SR','MSAVI','ISI','NIDI','YVI','APAR','IC'),
                     (os.path.join(Mother_Product_dir, 'NDVI_RapidEye_Smoothed_II'),
                      os.path.join(Mother_Product_dir, 'RDVI'),
                      os.path.join(Mother_Product_dir, 'EVI'),
                      os.path.join(Mother_Product_dir, 'EVI2'),
                      os.path.join(Mother_Product_dir, 'SR'),
                      os.path.join(Mother_Product_dir, 'MSAVI'),
                      os.path.join(Mother_Product_dir, 'ISI'),
                      os.path.join(Mother_Product_dir, 'NIDI'),
                      os.path.join(Mother_Product_dir, 'YVI'),
                      os.path.join(Mother_Product_dir, 'APAR_inte_DSMed'),
                      'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/III_Topo_Correct/IC_30cm',)))



##Extract values for modeling
Date_list = []
ShapeFile_list = []
for file in os.listdir(ShapeFile_dir):
    if file.startswith('ClippingAll') and file.endswith('.shp'):
        Date_list.append(datetime.strptime(file[12:20], '%m%d%Y'))
        ShapeFile_list.append(file)

print 'I - Start reading in APAR tiffs as Multi-raster...'
Raster_date_list = []
Multi_raster_path = []
for raster in os.listdir(Product_dir['APAR']):
     if raster.endswith('APAR.tif'):
         Raster_date_list.append(raster)
         raster_path = os.path.join(Product_dir['APAR'], raster)
         Multi_raster_path.append(raster_path)
Multi_raster_path = sorted(Multi_raster_path)
Raster_date_list = sorted(Raster_date_list)

for shapefile in ShapeFile_list:
    shapefile_dir = os.path.join(ShapeFile_dir,shapefile)
    date_str = shapefile[12:20]
    date_date = datetime.strptime(date_str, '%m%d%Y')
    print 'opening shapefile ' + shapefile
    ds = ogr.Open(shapefile_dir)
    lyr = ds.GetLayer()
    Fields_alllyr = [Field_list + Products]
    for feat in lyr:
        geom = feat.GetGeometryRef()
        Fields_onelyr = []
        for field in Field_list:
            print 'extracting ' + field + ' for shapefile ' + shapefile
            Fields_onelyr.append(feat.GetField(field))
        for product in Products:
            print 'extracting ' + product + ' for shapefile ' + shapefile
            if product == 'APAR':
                APAR_ts = []
                for raster_num in range(len(Multi_raster_path)):
                    raster_dir = Multi_raster_path[raster_num]
                    raster_date = datetime.strptime(Raster_date_list[raster_num][13:15] + Raster_date_list[raster_num][16:18] + Raster_date_list[raster_num][8:12], '%m%d%Y')
                    print 'opending raster ' + os.path.basename(raster_dir)
                    print raster_date
                    # https://gis.stackexchange.com/questions/46893/getting-pixel-value-of-gdal-raster-under-ogr-point-without-numpy
                    src_ds = gdal.Open(raster_dir)
                    gt = src_ds.GetGeoTransform()
                    rb = src_ds.GetRasterBand(1)
                    mx, my = geom.GetX(), geom.GetY()  # coord in map units
                    # Convert from map to pixel coordinates.
                    # Only works for geotransforms with no rotation.
                    px = int((mx - gt[0]) / gt[1])  # x pixel
                    py = int((my - gt[3]) / gt[5])  # y pixel
                    intval = rb.ReadAsArray(px, py, 1, 1)  # intval is a tuple, length=1 as we only asked for 1 pixel value
                    if raster_date < date_date:
                        APAR_ts.append(intval[0][0])
                        print raster_num
                    elif raster_date == date_date:
                        print date_str
                        print raster_date
                        print raster_num
                        APAR_ts.append(intval[0][0])
                        APAR_cumu = sum(APAR_ts)
                        Fields_onelyr.append(APAR_cumu)
                        break
            else:
                raster_dir = glob.glob(Product_dir[product] + '/*' + date_date.strftime('%Y-%m-%d') + '*_' + product + '.tif')[0]
                print 'opending raster ' + os.path.basename(raster_dir)
                # https://gis.stackexchange.com/questions/46893/getting-pixel-value-of-gdal-raster-under-ogr-point-without-numpy
                src_ds = gdal.Open(raster_dir)
                gt = src_ds.GetGeoTransform()
                rb = src_ds.GetRasterBand(1)
                mx, my = geom.GetX(), geom.GetY()  # coord in map units
                # Convert from map to pixel coordinates.
                # Only works for geotransforms with no rotation.
                px = int((mx - gt[0]) / gt[1])  # x pixel
                py = int((my - gt[3]) / gt[5])  # y pixel
                intval = rb.ReadAsArray(px, py, 1, 1) # intval is a tuple, length=1 as we only asked for 1 pixel value
                Fields_onelyr.append(intval[0][0])
        Fields_alllyr.append(Fields_onelyr)
        Fields_alllyr_df = pd.DataFrame(Fields_alllyr[1:], columns=Fields_alllyr[0])
        Fields_alllyr_df.to_csv(os.path.join(OutPut_dir, 'ClippingAll_' + date_str + 'Inte_DSMED.csv'), index=False, header=True)
    print 'finished extracting of file ' + shapefile






































