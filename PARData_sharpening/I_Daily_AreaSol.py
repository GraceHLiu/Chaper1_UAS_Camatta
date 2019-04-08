# Name: Calculate_Daily_PARratio.py
# Description: Derives incoming solar radiation from a raster surface.
#              Outputs a global radiation raster for a specified time period. (11/11/2016 to 4/30/2017).
#              use the average DSM do the same thing and calculate a ratio
# Requirements: Spatial Analyst Extension

# Import system modules
import arcpy
from arcpy.sa import *
from arcpy import env
import os
from datetime import date, datetime, timedelta
import progressbar as pb
from progressbar import Bar,Percentage,ETA
import time
# Define functions
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
# Set environment settings
env.workspace = "C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/Daily_Solar"
env.scratchWorkspace ="C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/Daily_Solar"
env.overwriteOutput = True
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# Set local variables
inRaster = "C:/Users/lh349796/Box Sync/research/sUAS/JastroProposal/DSM/I_cliped_resampled/Res_30cm/camatta_11112016_dsm.tif"
latitude = 35.4971949269299
skySize = 200
timeConfig = TimeMultipleDays(2016,316,317)#TimeMultipleDays(2016,316,120)
dayInterval = 1
hourInterval = 0.5
zFactor = 1
calcDirections = 32
zenithDivisions = 16
azimuthDivisions = 16
diffuseProp = 0.3
transmittivity = 0.5
outDirectRad = ""
outDiffuseRad = ""
outDirectDur = ""
# Set the progressor
progress = pb.ProgressBar(widgets = [Percentage(), Bar(), ETA()],maxval=172).start()
progvar = 0
for dat in perdelta(date(2016,11,11), date(2017,5,2), timedelta(days=1)):
    print '\nCalculating solar radiation for date '+ dat.strftime('%m-%d-%Y') + '...'
    OutRasterName = 'AreaSol_'+dat.strftime("%Y%j")+'.tif'
    next_dat = dat + timedelta(days=1)
    timeConfig = TimeMultipleDays(dat.timetuple().tm_year, dat.timetuple().tm_yday, next_dat.timetuple().tm_yday)
    # Execute AreaSolarRadiation
    outGlobalRad = AreaSolarRadiation(inRaster, latitude, skySize, timeConfig,
                                      dayInterval, hourInterval, "INTERVAL", zFactor, "FROM_DEM",
                                      calcDirections, zenithDivisions, azimuthDivisions, "UNIFORM_SKY",
                                      diffuseProp, transmittivity, outDirectRad, outDiffuseRad, outDirectDur)

    print 'Saving '+ OutRasterName + '...'
    # Save the output
    outGlobalRad.save(OutRasterName)
    progress.update(progvar + 1)
    progvar += 1

progress.finish()
