library(Deriv)
library(reshape2)
library(ggplot2)
library(Metrics)
####################################
### x1= soil moisture
### x2 = soil temperature
### x3 = elevation
### x4 = APAR
###################################33
WP = 0.144
F_soilm = function(x1,a) 1/(1+exp(a*(x1-0.144)))
F_soilt = function(x2, Topt, d, e) (((exp(-0.1*d)+1)*(exp(-.1*e)+1))/((1+exp(d*(Topt-0.1-x2)))*(1+exp(e*(-Topt-0.1+x2)))))
#F_soilt = function(x2, Topt,d,e) ((exp(-10*d)+1)*(exp(-10*e)+1))/((1+exp(d*(Topt-10-x2)))*(1+exp(e*(-Topt-10+x2))))
F_elevation = function(x3,b,c) b*x3+c
# asymmterical soil temperature function
#F_LUE = function(x1,x2,x3,Topt,a,b,c,d,e) (1/(1+exp(a*(x1-0.05152))))*(b*x3+c)*(((exp(-0.1*d)+1)*(exp(-.1*e)+1))/((1+exp(d*(Topt-0.1-x2)))*(1+exp(e*(-Topt-0.1+x2)))))
# symmterical soil temperature function
F_LUE = function(x1,x2,x3,Topt,a,b,c,d) (1/(1+exp(a*(x1-WP))))*(b*x3+c)*(4/((1+exp(d*(Topt-x2)))*(1+exp(d*(-Topt+x2)))))

#~~Step 1: Read in the data
Input_dir = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v5'
SoilT_dir = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\Ground_mea\\Datalogger'
SoilM_dir = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\Ground_mea\\Datalogger'
Year = c('2017','2018')
Greenup_2017 = as.Date('2016-11-11','%Y-%m-%d')
Greenup_2018 = as.Date('2018-01-01','%Y-%m-%d')
### do not run the commented reading in part because I have run it before and made some 
### outlier cleaning mannually, just read in the csv saved
InputData.y = read.csv(file.path(Input_dir,'InputData_Y_cleaned.csv'),stringsAsFactors = F)
InputData.y$Date = as.Date(InputData.y$Date,'%m/%d/%Y')
InputData.x = read.csv(file.path(Input_dir,'InputData_X.csv'),stringsAsFactors = F)
InputData.x$Date_Harvest = as.Date(InputData.x$Date_Harvest,'%Y-%m-%d')
InputData.x$Date = as.Date(InputData.x$Date,'%Y-%m-%d')

# InputData.x = list()
# InputData.y = list()
# for(yr in Year){
#   Count = as.numeric(yr)-as.numeric(Year[1])+1
#   APAR_data = read.csv(file.path(Input_dir,paste0('APAR_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(APAR_data)[3] = 'APAR'
#   APAR_data$Comment = unlist(strsplit(APAR_data$variable,'_'))[ c(TRUE,FALSE) ]
#   APAR_data$Date_Harvest = unlist(strsplit(APAR_data$variable,'_'))[ c(FALSE,TRUE) ]
#   APAR_data$Date_Harvest = as.Date(APAR_data$Date_Harvest,'%Y-%m-%d')
#   APAR_data = APAR_data[grep("[[:digit:]][[:alpha:]]",APAR_data$Comment),]
#   APAR_data$Date = as.Date(APAR_data$Date,'%Y-%m-%d')
#   APAR_data$ID = gsub('.{1}$', '', APAR_data$Comment)
# 
#   SoilM_data = read.csv(file.path(SoilM_dir,yr,'dailySMmean.csv'),stringsAsFactors = F)
#   SoilT_data = read.csv(file.path(SoilT_dir,yr,'dailySTmean.csv'),stringsAsFactors = F)
#   SoilM_data$Date = as.Date(SoilM_data$Date, '%Y-%m-%d')
#   SoilT_data$Date = as.Date(SoilT_data$Date, '%Y-%m-%d')
#   Soil_data = merge(SoilM_data,SoilT_data,by=c('Date','ID'))
#   APAR_Soil_data = merge(APAR_data,Soil_data,by = c('Date','ID'))
# 
#   InputData.x[[Count]] = APAR_Soil_data

# Biomass_data = read.csv(file.path(Input_dir,paste0('Biomass_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
# Biomass_data = Biomass_data[grep("[[:digit:]][[:alpha:]]",Biomass_data$Comment),]
# Biomass_data$Date = as.Date(Biomass_data$Date,'%Y-%m-%d')
# Biomass_data$variable = paste0(Biomass_data$Comment,'_',Biomass_data$Date)
# DSM_data = read.csv(file.path(Input_dir,paste0('DSM_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
# colnames(DSM_data) = c('variable','DSM')
# InputData.y[[Count]] = merge(Biomass_data,DSM_data,by = 'variable')[,-1]

# }
# InputData.y = do.call("rbind.data.frame", InputData.y)
# InputData.x  = do.call("rbind.data.frame", InputData.x )
# ###### get ride of the outliers ######
# InputData.y = InputData.y[InputData.y$Date!=as.Date('20170430','%Y%m%d'),]

# write.csv(InputData.x,file.path(Input_dir,'InputData_X.csv'),row.names = F)
# ggplot(InputData.y[InputData.y$Date>=as.Date('20180101','%Y%m%d'),],aes(x = Date, y = Biomass, color = Comment))+ 
#   geom_line()+geom_point()
# write.csv(InputData.y,file.path(Input_dir,'InputData_Y.csv'),row.names = F)
# InputData.y = read.csv(file.path(Input_dir,'InputData_Y.csv'),stringsAsFactors = F)
# InputData.y$Date = as.Date(InputData.y$Date,'%m/%d/%Y')
# ggplot(InputData.y[InputData.y$Date>=as.Date('20180101','%Y%m%d')&InputData.y$Aspect=='T',],aes(x = Date, y = Biomass, color = Comment))+ 
#   geom_line() + geom_point()
# InputData.y = InputData.y[!(InputData.y$Comment=='13B'&InputData.y$Date==as.Date('20170406','%Y%m%d')),]#decreasing measurements
# InputData.y = InputData.y[!(InputData.y$Comment=='13A'&InputData.y$Date==as.Date('20170406','%Y%m%d')),]#too high measurement
# InputData.y = InputData.y[(InputData.y$comment=='8B'&InputData.y$Date_Clip==as.Date('20170406','%Y%m%d')),]
#~~Step 2: Stochastic Gradient Descedent
## 2.1 shuffle the data and split into training and testing
### split the InputData.y into InputData.y_train (70%) and InputData.y_test (30%)
bound <- floor((nrow(InputData.y)/4)*3)         #define % of training and test set
set.seed(77)
InputData.y <- InputData.y[sample(nrow(InputData.y)), ]           #sample rows 
InputData.y.train <- InputData.y[1:bound, ]              #get training set
InputData.y.test <- InputData.y[(bound+1):nrow(InputData.y), ]    #get test set
## 2.2 predetermine the stepsize and maximum interation times, and the initial values for the coefficients
#Initials = data.frame(a = -44.58, b = -36.63, c = 22,d = 20, e = 30)
Max_iters = 50
#Initials = data.frame(a = -15, b = -39.86, c = 23.8,d = 20.41, e = 28.8)
Initials = data.frame(a = -15, b = -39.86, c = 23.8,d = 76)
Topt = 14.209/100
InputData.x$ST_low = InputData.x$ST_low/100
InputData.y.test$DSM = InputData.y.test$DSM/1000
InputData.y.train$DSM = InputData.y.train$DSM/1000

Step_size_initial = c(1e-4,1e-5,1e-6,1e-4)
Step_size = Step_size_initial
Derive_a = Deriv(F_LUE,'a')
Derive_b = Deriv(F_LUE,'b')
Derive_c = Deriv(F_LUE,'c')
Derive_d = Deriv(F_LUE,'d')
#Derive_e = Deriv(F_LUE,'e')
old = Initials
CostPlot = data.frame(Iteration = as.numeric(), 
                      ID = as.character(),
                      Cost = as.numeric(), 
                      RMSE = as.numeric(),
                      stringsAsFactors = F)
Coefficits = data.frame(Iteration = as.numeric(), a = as.numeric(),
                        b = as.numeric(),c = as.numeric(),
                        d = as.numeric(),#e = as.numeric(),
                        RMSE_train = as.numeric(),RMSE_testing = as.numeric(),
                        stringsAsFactors = F)
CostComp.test = data.frame(ID = InputData.y.test$Comment, 
                           Data_Harvest = InputData.y.test$Date, 
                           Y_ori = InputData.y.test$Biomass,
                           Y_hat = as.numeric(0),
                           stringsAsFactors = F)
Removed.y.train = InputData.y.train[0,]
## 3.3 calibrate the coefficients
for(iter in (1:Max_iters)){
  print(paste0('~~~starting the ', toString(iter), ' iteration~~~'))
  CostComp = data.frame(ID = InputData.y.train$Comment, 
                        Data_Clip = InputData.y.train$Date, 
                        Y_ori = InputData.y.train$Biomass,
                        Y_hat = as.numeric(0))
  for(row in (1:nrow(InputData.y.train))){
    ID_y = InputData.y.train$Comment[row]
    Date_y = InputData.y.train$Date[row]
    Elevation_y = InputData.y.train$DSM[row]
    print(paste0('~~~working on ID ', ID_y, ', Date_clip ', Date_y, ' ~~~'))
    print(paste0('~~~old a = ' ,toString(old$a),' ~~~'))
    print(paste0('~~~old b = ' ,toString(old$b),' ~~~'))
    print(paste0('~~~old c = ' ,toString(old$c),' ~~~'))
    print(paste0('~~~old d = ' ,toString(old$d),' ~~~'))
    # print(paste0('~~~old e = ' ,toString(old$e),' ~~~'))
    # locate the rows in the InputData.x data frame
    InputData.x.train = InputData.x[InputData.x$Comment==ID_y&InputData.x$Date_Harvest==Date_y&InputData.x$Date<=Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Date_y),1,4))),]
    Derive_a.sum = 0
    Derive_b.sum = 0
    Derive_c.sum = 0
    Derive_d.sum = 0
    #Derive_e.sum = 0
    Pred.y = 0
    for (Date_x in (1:nrow(InputData.x.train))){
      Derive_a.sum = Derive_a.sum + Derive_a(InputData.x.train[Date_x,'SM_low'],
                                             InputData.x.train[Date_x,'ST_low'],
                                             Elevation_y,Topt,
                                             old$a,old$b,old$c,old$d)*InputData.x.train[Date_x,'APAR']
      
      Derive_b.sum = Derive_b.sum + Derive_b(InputData.x.train[Date_x,'SM_low'],
                                             InputData.x.train[Date_x,'ST_low'],
                                             Elevation_y,Topt,
                                             old$a,old$b,old$c,old$d)*InputData.x.train[Date_x,'APAR']
      
      Derive_c.sum = Derive_c.sum + Derive_c(InputData.x.train[Date_x,'SM_low'],
                                             InputData.x.train[Date_x,'ST_low'],
                                             Elevation_y,Topt,
                                             old$a,old$b,old$c,old$d)*InputData.x.train[Date_x,'APAR']
      Derive_d.sum = Derive_d.sum + Derive_d(InputData.x.train[Date_x,'SM_low'],
                                             InputData.x.train[Date_x,'ST_low'],
                                             Elevation_y,Topt,
                                             old$a,old$b,old$c,old$d)*InputData.x.train[Date_x,'APAR']
      
      Pred.y = Pred.y + F_LUE(InputData.x.train[Date_x,'SM_low'],
                              InputData.x.train[Date_x,'ST_low'],
                              Elevation_y,Topt,
                              old$a,old$b,old$c,old$d)*InputData.x.train[Date_x,'APAR']
    }
    for(Cost_row in (1:nrow(CostComp))){
      Cost_ID_y = InputData.y.train$Comment[Cost_row]
      Cost_Date_y = InputData.y.train$Date[Cost_row]
      Cost_Elevation_y = InputData.y.train$DSM[Cost_row]
      InputData.x.train.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
      Pred.y.cost = 0
      for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
        Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'SM_low'],
                                          InputData.x.train.cost[Cost_Date_x,'ST_low'],
                                          Cost_Elevation_y, Topt,
                                          old$a,old$b,old$c,old$d)*InputData.x.train.cost[Cost_Date_x,'APAR']
      }
      CostComp$Y_hat[Cost_row] = Pred.y.cost
    }
    CostPlot[nrow(CostPlot)+1,] = data.frame((iter-1)*nrow(InputData.y.train)+row,ID_y,
                                             sqrt((InputData.y.train[row,'Biomass']-Pred.y)^2),rmse(CostComp$Y_ori,CostComp$Y_hat))  
    
    SGD_a = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_a.sum
    SGD_b = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_b.sum
    SGD_c = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_c.sum
    SGD_d = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_d.sum
    SGD_matrix = data.frame(a=SGD_a, b = SGD_b, c = SGD_c,d = SGD_d)
    print(SGD_matrix) 
    print(paste0('~~~cost old = ',CostPlot$Cost[nrow(CostPlot)-1]))
    print(paste0('~~~cost new = ',CostPlot$Cost[nrow(CostPlot)]))
    # if the new RMSE is wiredly bigger than the previous one then 
    # the data point could be outlier (could not be explained by the current coeffs) 
    # and needed to be removed from optimization
    if(iter*row>1){
      if((CostPlot$RMSE[nrow(CostPlot)]/CostPlot$RMSE[nrow(CostPlot)-1])>1000){
        Removed.y.train[nrow(Removed.y.train)+1,] = InputData.y.train[row,]
        InputData.y.train = InputData.y.train[-row,]
        print('this data point has been removed from this optimization')
        print('~~~new = old ~~~')
        next
      }
    }
    if(CostPlot$RMSE[nrow(CostPlot)] <= 600){
      for(Cost_row in (1:nrow(CostComp.test))){
        Cost_ID_y = InputData.y.test$Comment[Cost_row]
        Cost_Date_y = InputData.y.test$Date[Cost_row]
        Cost_Elevation_y = InputData.y.test$DSM[Cost_row]
        InputData.x.test.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
        Pred.y.cost = 0
        for (Cost_Date_x in (1:nrow(InputData.x.test.cost))){
          Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.test.cost[Cost_Date_x,'SM_low'],
                                            InputData.x.test.cost[Cost_Date_x,'ST_low'],
                                            Cost_Elevation_y, Topt,
                                            old$a,old$b,old$c,old$d)*InputData.x.test.cost[Cost_Date_x,'APAR']
        }
        CostComp.test$Y_hat[Cost_row] = Pred.y.cost
      }
      Coefficits[nrow(Coefficits)+1,] = c(iter*row, old$a, old$b, old$c,
                                          old$d,CostPlot$RMSE[nrow(CostPlot)],rmse(CostComp.test$Y_ori,CostComp.test$Y_hat))
    }
    # Step_size = Step_size_initial
    # if(nrow(CostPlot)>1){
    #   while((CostPlot$Cost[nrow(CostPlot)]-CostPlot$Cost[nrow(CostPlot)-1])>1){
    #     print(paste0('~~~ within while cost old = ',CostPlot$Cost[nrow(CostPlot)-1]))
    #     print(paste0('~~~ within while cost new = ',CostPlot$Cost[nrow(CostPlot)]))
    #     print(paste0('~~~ within while step size = ',Step_size))
    #     Step_size = Step_size/2
    #     new = old - Step_size * SGD_matrix
    #     #print(SGD_matrix)
    #     Pred.y = 0
    #     for (Date_x in (1:nrow(InputData.x.train))){
    #       Pred.y = Pred.y + F_LUE(InputData.x.train[Date_x,'SM_low'],
    #                               InputData.x.train[Date_x,'ST_low'],
    #                               Elevation_y,Topt,
    #                               old$a,old$b,old$c,old$d,old$e)*InputData.x.train[Date_x,'APAR']
    #     }
    #     # for(Cost_row in (1:nrow(CostComp))){
    #     #   Cost_ID_y = InputData.y.train$comment[Cost_row]
    #     #   Cost_Date_y = InputData.y.train$Date_Clip[Cost_row]
    #     #   Cost_Elevation_y = InputData.y.train$Elevation[Cost_row]
    #     #   InputData.x.train.cost = InputData.x[InputData.x$ID==Cost_ID_y&InputData.x$Date_Clip==Cost_Date_y&InputData.x$Date<=Cost_Date_y,]
    #     #   Pred.y.cost = 0
    #     #   for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
    #     #     Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'SM_low'],
    #     #                                       Cost_Elevation_y,
    #     #                                       new$a,new$b,new$c)*F_soilt(InputData.x.train.cost[Cost_Date_x,'ST_low'],Topt)*InputData.x.train.cost[Cost_Date_x,'APAR']
    #     #   }
    #     #   CostComp$Y_hat[Cost_row] = Pred.y.cost
    #     # }
    #     CostPlot[nrow(CostPlot),] = c(iter*row,sqrt((InputData.y.train[row,'Biomass']-Pred.y)^2))#,rmse(CostComp$Y_ori,CostComp$Y_hat))
    #   }
    # }
    
    new = old - Step_size * SGD_matrix
    old = new
    print(paste0('~~~new a = ' ,toString(old$a),'~~~'))
    print(paste0('~~~new b = ' ,toString(old$b),'~~~'))
    print(paste0('~~~new c = ' ,toString(old$c),'~~~'))
    print(paste0('~~~new d = ' ,toString(old$d),'~~~'))
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
  }
  #shuffle the data after each iteration
  InputData.y.train <- InputData.y.train[sample(nrow(InputData.y.train)), ]   
}



# ggplot(CostPlot,aes(x = Iteration, y = Cost))+geom_line()
# ggplot(CostPlot,aes(x = Iteration, y = RMSE))+geom_line()
# ######################################################
# ### for testing code only##################
# # old$a = -4.49262422625622#-4.46776305700909#-4.46780655588052
# # old$b = -366.248833320965#-366.30663673253#-366.306026720435
# # old$c = 22.5855401775978#21.3968481951085#21.4097088035158
# # old$d = 1.08123706136536#1.02030270396617#1.02029798639395
# # old$e = -0.102521140304283#-5.06184938225673#-5.07830247252686
# # for(Cost_row in (1:nrow(CostComp))){
# #   Cost_ID_y = InputData.y.train$comment[Cost_row]
# #   Cost_Date_y = InputData.y.train$Date_Clip[Cost_row]
# #   Cost_Elevation_y = InputData.y.train$Elevation[Cost_row]
# #   InputData.x.train.cost = InputData.x[InputData.x$ID==Cost_ID_y&InputData.x$Date_Clip==Cost_Date_y&InputData.x$Date<=Cost_Date_y,]
# #   Pred.y.cost = 0
# #   for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
# #     Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'SM_low'],
# #                                       InputData.x.train.cost[Cost_Date_x,'ST_low'],
# #                                       Cost_Elevation_y, Topt,
# #                                       old$a,old$b,old$c,old$d,old$e)*InputData.x.train.cost[Cost_Date_x,'APAR']
# #   }
# #   CostComp$Y_hat[Cost_row] = Pred.y.cost
# # }
# # rmse(CostComp$Y_ori,CostComp$Y_hat)
# ###################################################
# CostComp$Diff = abs(CostComp$Y_hat-CostComp$Y_ori)
# ###################################################
# ### Saving the InputData.y#########################
SavingPath = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v5\\Plotting_Dataset'
ifelse(!dir.exists(SavingPath), dir.create(SavingPath), FALSE)
write.csv(InputData.y.test,file.path(SavingPath,'InputDataYtest_M1_symm.csv'),row.names = FALSE)
write.csv(InputData.y.train,file.path(SavingPath,'InputDataYtrain_M1_symm.csv'),row.names = FALSE)
write.csv(CostComp.test,file.path(SavingPath,'CostCompTest_M1_symm.csv'),row.names = FALSE)
# ################################################################################################
# ### Saving the testing rmse result############################################################
InputData.y.test = read.csv(file.path(SavingPath,'InputDataYtest_M1_symm.csv'),stringsAsFactors = FALSE)
InputData.y.train = read.csv(file.path(SavingPath,'InputDataYtrain_M1_symm.csv'),stringsAsFactors = FALSE)
InputData.x = read.csv(file.path('D:/Box Sync/research/sUAS/JastroProposal/IIIII_Product_Biomass/30cm_CModel/code_v4','InputData_X.csv'),stringsAsFactors = FALSE)
InputData.x$ST_low = InputData.x$ST_low/100
CostComp.test = read.csv(file.path(SavingPath,'CostCompTest_M1_symm.csv'),stringsAsFactors = FALSE)
old = data.frame(a=-58.86211,b=-25.49102,c=27.79847,d=84.2545)
#old = data.frame(a=-51.249742,b=-27.45852,c=28.50916,d=76.75904)
for(Cost_row in (1:nrow(CostComp.test))){
  Cost_ID_y = InputData.y.test$Comment[Cost_row]
  Cost_Date_y = InputData.y.test$Date[Cost_row]
  Cost_Elevation_y = InputData.y.test$DSM[Cost_row]
  InputData.x.test.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
  Pred.y.cost = 0
  for (Cost_Date_x in (1:nrow(InputData.x.test.cost))){
    Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.test.cost[Cost_Date_x,'SM_low'],
                                      InputData.x.test.cost[Cost_Date_x,'ST_low'],
                                      Cost_Elevation_y, Topt,
                                      old$a,old$b,old$c,old$d)*InputData.x.test.cost[Cost_Date_x,'APAR']
  }
  CostComp.test$Y_hat[Cost_row] = Pred.y.cost
}
#old = data.frame(a=-21.22152,b=-36.95654,c=24.46457,d=76)
##old = old1
rmse(CostComp.test$Y_ori,CostComp.test$Y_hat)
mae(CostComp.test$Y_ori,CostComp.test$Y_hat)
1 - (sum((CostComp.test$Y_ori-CostComp.test$Y_hat)^2)/sum((CostComp.test$Y_ori-mean(CostComp.test$Y_ori))^2))
write.csv(CostComp.test,file.path(SavingPath,'CostCompTest_M1_symm.csv'),row.names = FALSE)
#########################################################################################
### Saving the training rmse result ############################
CostComp = data.frame(ID = InputData.y.train$Comment,
                      Data_Clip = InputData.y.train$Date,
                      Y_ori = InputData.y.train$Biomass,
                      Y_hat = as.numeric(0))
for(Cost_row in (1:nrow(CostComp))){
  Cost_ID_y = InputData.y.train$Comment[Cost_row]
  Cost_Date_y = InputData.y.train$Date[Cost_row]
  Cost_Elevation_y = InputData.y.train$DSM[Cost_row]
  InputData.x.train.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
  Pred.y.cost = 0
  for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
    Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'SM_low'],
                                      InputData.x.train.cost[Cost_Date_x,'ST_low'],
                                      Cost_Elevation_y, Topt,
                                      old$a,old$b,old$c,old$d)*InputData.x.train.cost[Cost_Date_x,'APAR']
  }
  CostComp$Y_hat[Cost_row] = Pred.y.cost
}
rmse(CostComp$Y_ori,CostComp$Y_hat)
write.csv(CostComp,file.path(SavingPath,'CostCompTrain_M1_symm.csv'),row.names = FALSE)
##################################################################################3
###Plotting Fig.14 the Result ScatterPlots (test) ################################
colnames(CostComp.test)[2] = 'Data_Clip'
CostComp.plot = CostComp.test#rbind(CostComp.test,CostComp)
CostComp.plot$Year = strftime(CostComp.plot$Data_Clip,'%Y')
CostComp.plot$Month = strftime(CostComp.plot$Data_Clip,'%b')
CostComp.plot$Month  <- factor(CostComp.plot$Month, levels=c("Jan", "Feb", "Mar","Apr"), labels=c("Jan", "Feb", "Mar","Apr"))
p=ggplot(CostComp.plot,aes(y=Y_hat,x=Y_ori,color = Month, shape = Year,order = Data_Clip))+geom_point()+
  scale_shape_manual(values=c(1, 16))+
  scale_colour_brewer(palette = 'Set1')+
  #scale_color_manual(values=c('#993300',"#3333FF", "#009900")) +
  geom_abline(intercept = 0, slope = 1,color = 'grey10',size = 0.8, linetype = 'longdash')+
  ylab('predicted biomass (kg/ha)')+xlab('measured biomass (kg/ha)')+
  labs(color = 'Date') +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 4300), breaks = seq(0,4000, by = 1000)) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 4300),  breaks = seq(0,4000, by = 1000)) +
  theme(
    #panel.background = element_rect(fill = "grey80"),
    panel.background = element_blank(),
    # panel.grid.minor = element_blank(),
    panel.grid.major.y = element_line(colour = "grey60", size = 0.5),
    panel.grid.major.x = element_line(colour = "grey60", size = 0.5),
    plot.title = element_text(colour = 'black', size = 16,family = "serif"),
    axis.text.y = element_text(colour = 'black', size = 14,family = "serif",color ='black', face = 'bold'),
    axis.text.x = element_text(colour = 'black', size = 14,family = "serif", face = 'bold'),
    axis.title = element_text(colour = 'black', size = 14,family = "serif",face = 'bold'),
    axis.ticks = element_line(colour = 'grey60'),
    legend.text=element_text(colour = 'black', size = 14,family = "serif"),
    legend.title=element_text(colour = 'black', size = 14,family = "serif"),
    axis.ticks.length = unit(.25, "cm"),
    axis.ticks.x = element_line(colour = "black"))
ggsave(file.path(SavingPath,"ModelScatter_Test_ModelI_symm.png"), p, width=7, height=5)
nrow(CostComp.test)
nrow(CostComp)
