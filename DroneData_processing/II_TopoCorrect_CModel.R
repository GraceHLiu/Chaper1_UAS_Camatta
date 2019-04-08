library(raster)
library(sp)
library(rgdal)
library(xlsx)

#set working directory
SRdir = 'C:\\Users\\lh349796\\Box Sync\\research\\sUAS\\JastroProposal\\II_Clipiped_Resampled\\SR_30cm'
SRfilenames = c('Camatta_01162017.tif','Camatta_02152017.tif','Camatta_03172017.tif','Camatta_04062017.tif','Camatta_04302017.tif','Camatta_11112016.tif')#c('Camatta_01162018.tif')
ICdir = 'C:\\Users\\lh349796\\Box Sync\\research\\sUAS\\JastroProposal\\III_Topo_Correct\\IC_30cm'
ICfilenames = c('Camatta_01162017_IC.tif','Camatta_02152017_IC.tif','Camatta_03172017_IC.tif','Camatta_04062017_IC.tif','Camatta_04302017_IC.tif','Camatta_11112016_IC.tif')#c('Camatta_01162018_IC.tif')
Bandnames = c('Rededge','red','nir','green','blue')
SunAngles = read.xlsx('C:\\Users\\lh349796\\Box Sync\\research\\sUAS\\JastroProposal\\III_Topo_Correct\\SunAngles.xlsx',sheetIndex = 1)
Outdir = 'C:\\Users\\lh349796\\Box Sync\\research\\sUAS\\JastroProposal\\III_Topo_Correct\\SR_30cm_CModel'
if (!file.exists(Outdir)){
  dir.create(file.path(Outdir))
}

###----Calculate C----###
Output_C = data.frame(File = character(0), Band = character(0), BandNO = numeric(0), C = numeric(0),R2 = numeric(0),stringsAsFactors = F)
#load raster
for(i in (1:length(SRfilenames))){
  for( j in (1:length(Bandnames))){
    print(paste0('working on file ',SRfilenames[i],' band ',Bandnames[j], ' ...'))
    SR <- raster(file.path(SRdir,SRfilenames[i]),band = j)
    IC <- raster(file.path(ICdir,ICfilenames[i]))
    
    #extract values from raster into a vector
    y <-getValues(SR)
    # prere <- resample(pre, ndvi, method="bilinear")
    x <-getValues(IC)
    y[which(is.na(x))]<-NA 
    
    #combine in data frame
    f<-data.frame(IC = x, SR = y)
    #remove zeros
    ##Go through each row and determine if a value is zero
    f = f[!(apply(f, 1, function(y) any(y == 0))),]
    
    model<-lm(SR~IC,data = f)
    summary(model)
    coef = as.numeric(model$coefficients)
    #Date = 
    Output_C[nrow(Output_C)+1,] = c(SRfilenames[i],Bandnames[j],j,coef[1]/coef[2],summary(model)$r.square)
    # print(paste0('C for file ',SRfilenames[i],' band ',Bandnames[j], ' is:'))
    # print((coef[1]/coef[2]))
    # print('R2 for linear regression is')
    # print(summary(model)$r.square)
    #plot(f$SR~f$IC,col = "blue", main = "IC vs SR", xlab = "Surface Reflectance", ylab = "Illumiation Condition")
    #abline(model)
  }
}
Output_C$Date = as.Date('20170101','%Y%m%d')
for (i in (1:nrow(Output_C))){
  Output_C$Date[i] = as.Date(substr(Output_C$File[i],9,16),'%m%d%Y')
}
write.csv(Output_C,file.path(Outdir,'CValues.csv'),row.names = F)

###----Topographic Correction----###
for (i in (1:length(SRfilenames))){
  for( j in (1:length(Bandnames))){
    print(paste0('working on file ',SRfilenames[i],' band ',Bandnames[j], ' ...'))
    SR <- raster(file.path(SRdir,SRfilenames[i]),band = j)
    IC <- raster(file.path(ICdir,ICfilenames[i]))
    CosZ = SunAngles$Cos.Z.[SunAngles$Date==Output_C$Date[length(Bandnames)*(i-1)+j]]
    C = as.numeric(Output_C$C[length(Bandnames)*(i-1)+j])
    CorrectedSR = SR * (C + CosZ) / (IC + C)
    filename = file.path(Outdir,paste0(substr(SRfilenames[i],1,16),'_Topoed_',Bandnames[j],'.tif'))
    writeRaster(CorrectedSR, filename=filename, format="GTiff", overwrite=TRUE)
  }
}


