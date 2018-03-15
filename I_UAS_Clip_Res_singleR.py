# This script reads in the NDVI images in I_Raw, and then clip and resample with the same box and resolution.
# box = Camatta boundary
# resolution = 10cm
import os

OriNDVI_dir = 'C:/Users/lh349796\Box Sync/research/sUAS\JastroProposal/I_Raw\SLO_sUAS_b4Geo/Camatta_01162018/reflectance'#'D:/Box Sync/research/sUAS/JastroProposal/I_NDVI_data'#'D:/Box Sync/research/sUAS/JastroProposal/III_Processed_data/APAR'
ClipRe_dir = 'C:/Users/Grace Liu/Box Sync/research/sUAS/JastroProposal/III_Topo_Correct/IC_30cm_daily'#'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/III_Topo_Correct/IC_1m'#'D:/Box Sync/research/sUAS/JastroProposal/II_Clipped_Resampled_NDVI_10cm'#'D:/Box Sync/research/sUAS/JastroProposal/III_Processed_data/APAR_30cm'
box_dir = ''#'C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/SpatialData/Camatta_box.shp'
#box = '744482.136 3931357.923 744966.307 3931701.036'

if not os.path.exists(ClipRe_dir):
   os.makedirs(ClipRe_dir)

for File in os.listdir(OriNDVI_dir):
   if File.endswith(".tif"):
       File_dir = os.path.join(OriNDVI_dir,File)
       Export_file = os.path.join(ClipRe_dir,File)
       #os.system('gdalwarp -overwrite -crop_to_cutline -cutline "' + box_dir + '" -tr 1 1 -r cubic "' + File_dir + '" "' + Export_file + '"')
       os.system('gdalwarp -overwrite -tr .3 .3 -r cubic "' + File_dir + '" "' + Export_file + '"')


