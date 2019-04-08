library(Deriv)
library(reshape2)
library(ggplot2)
library(Metrics)
####################################
### x1 = AccuAPAR
### x2 = 100/((IC+1)*(DSM-430))
###################################33

F_LUE = function(x1,x2,a,b) x1*(a*x2+b)

#~~Step 1: Read in the data
Input_dir = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v3'
Year = c('2017','2018')
Greenup_2017 = as.Date('2016-11-11','%Y-%m-%d')
Greenup_2018 = as.Date('2018-01-01','%Y-%m-%d')
InputData.y = read.csv(file.path(Input_dir,'InputData_Y_M2_cleaned.csv'),stringsAsFactors = F)
InputData.y$Date = as.Date(InputData.y$Date,'%m/%d/%Y')
InputData.x = read.csv(file.path(Input_dir,'InputData_X_M2.csv'),stringsAsFactors = F)
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
#   APAR_data$Date = as.Date(APAR_data$Date,'%Y-%m-%d')
#   APAR_data$ID = gsub('.{1}$', '', APAR_data$Comment)
#   InputData.x[[Count]] = APAR_data
# 
#   Biomass_data = read.csv(file.path(Input_dir,paste0('Biomass_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   Biomass_data$variable = paste0(Biomass_data$Comment,'_',Biomass_data$Date)
#   DSM_data = read.csv(file.path(Input_dir,paste0('DSM_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(DSM_data) = c('variable','DSM')
#   Aspect_data = read.csv(file.path(Input_dir,paste0('Aspect_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(Aspect_data) = c('variable','Aspect')
#   Slope_data = read.csv(file.path(Input_dir,paste0('Slope_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(Slope_data) = c('variable','Slope')
#   FlowA_data = read.csv(file.path(Input_dir,paste0('FlowA_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(FlowA_data) = c('variable','FlowA')
#   IC_data = read.csv(file.path(Input_dir,paste0('IC_Extracted_',yr,'.csv')),stringsAsFactors = F)[,-1]
#   colnames(IC_data) = c('variable','IC')
#   DSM_data = merge(DSM_data,Aspect_data,by = 'variable')
#   DSM_data = merge(DSM_data,Slope_data,by = 'variable')
#   DSM_data = merge(DSM_data,FlowA_data,by = 'variable')
#   DSM_data = merge(DSM_data,IC_data,by = 'variable')
#   InputData.y[[Count]] = merge(Biomass_data,DSM_data,by = 'variable')[,-1]
# }
# InputData.y = do.call("rbind.data.frame", InputData.y)
# InputData.x  = do.call("rbind.data.frame", InputData.x )
# InputData.y = InputData.y[InputData.y$Date!=as.Date('20170430','%Y%m%d'),]
# write.csv(InputData.x,file.path(Input_dir,'InputData_X_M2.csv'),row.names = F)
# write.csv(InputData.y,file.path(Input_dir,'InputData_Y_M2_cleaned.csv'),row.names = F)
#~~Step 2: Plotting to visialize the relationship between Biomass/AccuAPAR vs. Topo coefficients
PlotData = data.frame(ID = as.character(),Comment = as.character(), Biomass = as.numeric(), Date = as.Date(as.character()), 
                      DSM = as.numeric(), Aspect = as.numeric(), Slope = as.numeric(), 
                      FlowA = as.numeric(), IC = as.numeric(), Curvature = as.numeric(),
                      AccuAPAR = as.numeric(),stringsAsFactors = F)
for(row in (1:nrow(InputData.y))){
  date = InputData.y$Date[row]
  year = substr(date,1,4)
  start_d = get(paste0('Greenup_',year))
  apar_cum = sum(InputData.x$APAR[InputData.x$Date>=start_d&InputData.x$Date<=InputData.x$Date_Harvest&InputData.x$variable==InputData.y$ID[row]])
  PlotData = rbind(PlotData,data.frame(InputData.y[row,],apar_cum,year))
}
PlotData = PlotData[PlotData$Date!=as.Date('20180116','%Y%m%d'),]
PlotData$Aspect = cos(PlotData$Aspect*pi/180)+1
colnames(PlotData)[ncol(PlotData)-1] = 'AccuAPAR'
colnames(PlotData)[ncol(PlotData)] = 'Year'
write.csv(PlotData,file.path(Input_dir,'PlotData_M2,csv'),row.names=F)
### rescale curvature from 0 to 1 from negative as concave and positive as convex
PlotData = read.csv(file.path(Input_dir,'PlotData_M2,csv'),stringsAsFactors = F)
PlotData$Curvature[PlotData$Curvature > 10] = 10
PlotData$Curvature[PlotData$Curvature < -10] = -10
PlotData$Curvature = PlotData$Curvature*-0.05+1.5
# PlotData.2017 = PlotData[PlotData$Year=='2017',]
# PlotData.2018 = PlotData[PlotData$Year=='2018',]
library(ggpmisc)
my.formula <- y ~ x
# x=1/(IC+1)/(DSM-430)
ggplot(PlotData,
       aes(y = Biomass/AccuAPAR, x = 100/((IC+1)*(DSM-430))))+geom_point()+
  geom_smooth(method = "lm", se=FALSE, color="black", formula = my.formula) +
  stat_poly_eq(formula = my.formula, 
               aes(label = paste(..eq.label.., ..rr.label.., sep = "~~~")), 
               parse = TRUE) 


ggplot(PlotData[PlotData$Date==as.Date('20180414','%Y%m%d'),],
       aes(y = Biomass, x = Curvature/(DSM-430)))+geom_point()+
  geom_smooth(method = "lm", se=FALSE, color="black", formula = my.formula) +
  stat_poly_eq(formula = my.formula, 
               aes(label = paste(..eq.label.., ..rr.label.., sep = "~~~")), 
               parse = TRUE) 

ggplot(PlotData, 
       aes(y = Biomass/AccuAPAR, x = 1/(IC+1)/(DSM-430),color = Year))+geom_point()+
  geom_smooth(method = "lm", se=FALSE, color="black", formula = my.formula) +
  stat_poly_eq(formula = my.formula, 
               aes(label = paste(..eq.label.., ..rr.label.., sep = "~~~")), 
               parse = TRUE) 

##########################################################################################
##########################################################################################
###################### Result from variable selection ####################################
######################     100/((IC+1)*(DSM-430))     ####################################
##########################################################################################


#~~Step 3: Stochastic Gradient Descedent
## 3.1 shuffle the data and split into training and testing
### split the InputData.y into InputData.y_train (70%) and InputData.y_test (30%)
bound <- floor((nrow(InputData.y)/4)*3)         #define % of training and test set
set.seed(99)
InputData.y <- InputData.y[sample(nrow(InputData.y)), ]           #sample rows 
InputData.y.train <- InputData.y[1:bound, ]              #get training set
InputData.y.test <- InputData.y[(bound+1):nrow(InputData.y), ]    #get test set
## 3.2 predetermine the stepsize and maximum interation times, and the initial values for the coefficients
Max_iters = 50
Initials = data.frame(a = 4.98 , b = -1.57)
Step_size_initial = 1e-6
Step_size = Step_size_initial
Derive_a = Deriv(F_LUE,'a')
Derive_b = Deriv(F_LUE,'b')
old = Initials
CostPlot = data.frame(Iteration = as.numeric(), 
                      Cost = as.numeric(), 
                      RMSE = as.numeric())
Coefficits = data.frame(Iteration = as.numeric(), a = as.numeric(),
                        b = as.numeric(),
                        RMSE_train = as.numeric(),RMSE_testing = as.numeric())
CostComp.test = data.frame(ID = InputData.y.test$Comment, 
                           Data_Clip = InputData.y.test$Date, 
                           Y_ori = InputData.y.test$Biomass,
                           Y_hat = as.numeric(0))
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
    IC_y = InputData.y.train$IC[row]
    print(paste0('~~~working on ID ', ID_y, ', Date_clip ', Date_y, ' ~~~'))
    print(paste0('~~~old a = ' ,toString(old$a),' ~~~'))
    print(paste0('~~~old b = ' ,toString(old$b),' ~~~'))
    # locate the rows in the InputData.x data frame
    InputData.x.train = InputData.x[InputData.x$Comment==ID_y&InputData.x$Date_Harvest==Date_y&InputData.x$Date<=Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Date_y),1,4))),]
    Derive_a.sum = 0
    Derive_b.sum = 0
    Pred.y = 0
    for (Date_x in (1:nrow(InputData.x.train))){
      Derive_a.sum = Derive_a.sum + Derive_a(InputData.x.train[Date_x,'APAR'],
                                             100/((IC_y+1)*(Elevation_y-430)),
                                             old$a,old$b)
      
      Derive_b.sum = Derive_b.sum + Derive_b(InputData.x.train[Date_x,'APAR'],
                                             100/((IC_y+1)*(Elevation_y-430)),
                                             old$a,old$b)

      Pred.y = Pred.y + F_LUE(InputData.x.train[Date_x,'APAR'],
                              100/((IC_y+1)*(Elevation_y-430)),
                              old$a,old$b)
    }
    for(Cost_row in (1:nrow(CostComp))){
      Cost_ID_y = InputData.y.train$Comment[Cost_row]
      Cost_Date_y = InputData.y.train$Date[Cost_row]
      Cost_Elevation_y = InputData.y.train$DSM[Cost_row]
      Cost_IC_y = InputData.y.train$IC[Cost_row]
      InputData.x.train.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
      Pred.y.cost = 0
      for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
        Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'APAR'],
                                          100/((Cost_IC_y+1)*(Cost_Elevation_y-430)),
                                          old$a,old$b)
                                          
      }
      CostComp$Y_hat[Cost_row] = Pred.y.cost
    }
    CostPlot[nrow(CostPlot)+1,] = c((iter-1)*nrow(InputData.y.train)+row,sqrt((InputData.y.train[row,'Biomass']-Pred.y)^2),rmse(CostComp$Y_ori,CostComp$Y_hat))  
    
    SGD_a = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_a.sum
    SGD_b = -1 * (InputData.y.train[row,'Biomass']- Pred.y)*Derive_b.sum
    SGD_matrix = data.frame(a=SGD_a, b = SGD_b)
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
    if(CostPlot$RMSE[nrow(CostPlot)] <= 800){
      for(Cost_row in (1:nrow(CostComp.test))){
        Cost_ID_y = InputData.y.test$Comment[Cost_row]
        Cost_Date_y = InputData.y.test$Date[Cost_row]
        Cost_Elevation_y = InputData.y.test$DSM[Cost_row]
        Cost_IC_y = InputData.y.test$IC[Cost_row]
        InputData.x.test.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
        Pred.y.cost = 0
        for (Cost_Date_x in (1:nrow(InputData.x.test.cost))){
          Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.test.cost[Cost_Date_x,'APAR'],
                                            100/((Cost_IC_y+1)*(Cost_Elevation_y-430)),
                                            old$a,old$b)
        }
        CostComp.test$Y_hat[Cost_row] = Pred.y.cost
      }
      Coefficits[nrow(Coefficits)+1,] = c(iter*row, old$a, old$b,CostPlot$RMSE[nrow(CostPlot)],rmse(CostComp.test$Y_ori,CostComp.test$Y_hat))
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
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
  }
  #shuffle the data after each iteration
  InputData.y.train <- InputData.y.train[sample(nrow(InputData.y.train)), ]   
}
ggplot(CostPlot,aes(x = Iteration, y = Cost))+geom_line()
ggplot(CostPlot,aes(x = Iteration, y = RMSE))+geom_line()
### Saving the InputData.y#########################
SavingPath = 'D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v3\\Plotting_Dataset'
write.csv(InputData.y.test,file.path(SavingPath,'InputDataYtest_M2.csv'),row.names = FALSE)
write.csv(InputData.y.train,file.path(SavingPath,'InputDataYtrain_M2.csv'),row.names = FALSE)

################################################################################################
### Saving the testing rmse result############################################################
InputData.y.test = read.csv(file.path(SavingPath,'InputDataYtest_M2.csv'),stringsAsFactors = FALSE)
InputData.y.train = read.csv(file.path(SavingPath,'InputDataYtrain_M2.csv'),stringsAsFactors = FALSE)
CostComp.test = read.csv(file.path(SavingPath,'CostCompTest_M2.csv'),stringsAsFactors = FALSE)
old = data.frame(a=3.177506,b=0.5641423)
for(Cost_row in (1:nrow(CostComp.test))){
  Cost_ID_y = InputData.y.test$Comment[Cost_row]
  Cost_Date_y = InputData.y.test$Date[Cost_row]
  Cost_Elevation_y = InputData.y.test$DSM[Cost_row]
  Cost_IC_y = InputData.y.test$IC[Cost_row]
  InputData.x.test.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
  Pred.y.cost = 0
  for (Cost_Date_x in (1:nrow(InputData.x.test.cost))){
    Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.test.cost[Cost_Date_x,'APAR'],
                                      100/((Cost_IC_y+1)*(Cost_Elevation_y-430)),
                                      old$a,old$b)
  }
  CostComp.test$Y_hat[Cost_row] = Pred.y.cost
}
##old = old1
rmse(CostComp.test$Y_ori,CostComp.test$Y_hat)
mae(CostComp.test$Y_ori,CostComp.test$Y_hat)
R2 <- 1 - (sum((CostComp.test$Y_ori-CostComp.test$Y_hat)^2)/sum((CostComp.test$Y_ori-mean(CostComp.test$Y_ori))^2))
write.csv(CostComp.test,file.path(SavingPath,'CostCompTest_M2.csv'),row.names = FALSE)
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
  Cost_IC_y = InputData.y.train$IC[Cost_row]
  InputData.x.train.cost = InputData.x[InputData.x$Comment==Cost_ID_y&InputData.x$Date_Harvest==Cost_Date_y&InputData.x$Date<=Cost_Date_y&InputData.x$Date>=get(paste0('Greenup_',substr(toString(Cost_Date_y),1,4))),]
  Pred.y.cost = 0
  for (Cost_Date_x in (1:nrow(InputData.x.train.cost))){
    Pred.y.cost = Pred.y.cost + F_LUE(InputData.x.train.cost[Cost_Date_x,'APAR'],
                                      100/((Cost_IC_y+1)*(Cost_Elevation_y-430)),
                                      old$a,old$b)
    
  }
  CostComp$Y_hat[Cost_row] = Pred.y.cost
}
rmse(CostComp$Y_ori,CostComp$Y_hat)
write.csv(CostComp,file.path(SavingPath,'CostCompTrain_M2.csv'),row.names = FALSE)
# CostComp = read.csv('D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v3\\Plotting_Dataset\\CostCompTrain_M1.csv')
# CostComp.test = read.csv('D:\\Box Sync\\research\\sUAS\\JastroProposal\\IIIII_Product_Biomass\\30cm_CModel\\code_v3\\Plotting_Dataset\\CostCompTrain_M1.csv')
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
ggsave(file.path(SavingPath,"ModelScatter_testing80_M2.png"), p, width=7, height=5)

