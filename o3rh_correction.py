# -*- coding: utf-8 -*-
"""
Author: Cosimo Fratticioli
Contact: c.fratticioli@isac.cnr.it
"""
import pandas as pd
from math import log
from numpy import exp
from datetime import date, timedelta
import datetime
from math import nan
import matplotlib.pyplot as plt
##############################################################################
### ----------------- defining filenames and paths ----------------------- ###
##############################################################################

# defining file references
instrument = ["meteo", "O3tei49i", "T200up"]
location = "BOS"
utc = "p00" 
filepath = "./BOS/"
resFolder = "./results"
night_correction = 'ON' # set 'ON' to enable night time correction
# ####################################################### #
# ------------- calibration coefficients ---------------  #
# ####################################################### #
slopeNO = 1.06270603
offsetNO = -0.1934
slopeNOx = 1.06270603
offsetNOx = -0.319
Sc = 0.95  # conversion efficiency
if(Sc>1):
    print("ERROR: efficiency greater then 1")


night_corr_frame = pd.DataFrame()
tot_frame = pd.DataFrame()
nit_oz_frame = pd.DataFrame()
hourly_averaged_mean = pd.DataFrame()
hourly_averaged_median = pd.DataFrame()

day_delta = timedelta(days=1) # The size of each step in days
start_date = date(2021, 5, 1)
#end_date = date.today()
end_date = date(2021, 6, 7)

##############################################################################
### ---- 1st loop over dates to build single frame from data files --------###
##############################################################################

#### create dataframe with NO and O3 measurements for all times ####

for i in range((end_date - start_date).days):
    d = start_date + i*day_delta
    year = str(d.year)
    month = str(d.month)
    day = str(d.day)
    # convert date into str using the same format of the filenames e.g. 20210101 
    # need to add "0" to months and days <9
    if int(d.month) < 9:
        month = str(0) + str(d.month)
    if int(d.day) < 9:
        day = str(0) +str(d.day)

    # define filenames
    dd = year + month + day  #convert from datetime to string format
    date_loc_ext = "_" + location + "_" + dd + "_" + utc + ".raw"

    ozone_filenm = instrument[1] + date_loc_ext
    nitrate_filenm = instrument[2] + date_loc_ext
    # read data files
    ozone_cols = ['daydec', 'O3']
    nitrate_cols =  ['#date', 'time', 'DayDec', 'NO[ppb]']
    try:
        ozone_frame = pd.read_csv(filepath+ozone_filenm, delimiter = " ", usecols = ozone_cols)
        nitrate_frame = pd.read_csv(filepath+nitrate_filenm, delimiter = " ", usecols = nitrate_cols)
    except Exception:
        print("could not open file on date " + str(d))
        continue  # skip to next day

    ########## rename daydec columns (to be changed in original headers-> Busetto) ##################
    nitrate_frame.rename(columns={"DayDec": "daydec"}, inplace = True)
    
    try:
        daily_night_corr_frame = pd.merge(nitrate_frame, ozone_frame, on='daydec')  
    except:
        print("merging problem on date " +str(d))
        continue # skip to next day
    
    night_corr_frame = night_corr_frame.append(daily_night_corr_frame, ignore_index=True)

##############################################################################
### -------- 2nd loop over dates to evaluate nightime offset ------------- ###
##############################################################################
    
#### evaluate NO mean values for O3>20 ppb at night time (e.g. 22:00-01:00) ####
    
hourly_mean = pd.DataFrame()
night_corr_frame.insert(0, "datetime", pd.to_datetime(night_corr_frame["#date"] + " " + night_corr_frame["time"]) )
daily_offset=pd.DataFrame()

for i in range((end_date - start_date).days-2):
    ### three daye are required in order to perform the night correction average. If you need to average data between e.g. 22:00 and 2:00 you need no acces to day-1 (d_1)
    ### furthermore, if you need a 1.5 days running average you need to acces also to d+1 (d1) data
    d_1 = start_date + (i-1)*day_delta
    d = start_date + i*day_delta
    d1 = start_date + (i+1)*day_delta
    if d==start_date:#skip first day
        continue
    
    night_day_frame = night_corr_frame[night_corr_frame["#date"] == str(d_1) ]    # select day
    night_day_frame = night_day_frame.append(night_corr_frame[night_corr_frame["#date"] == str(d)], ignore_index=True)
    night_day_frame = night_day_frame.append(night_corr_frame[night_corr_frame["#date"] == str(d1)], ignore_index=True)
    night_day_frame = night_day_frame.set_index("datetime")                                                                    
    
    night_00_03_frame = night_day_frame[ str(d_1) + " " + str(datetime.time(21,0,0)) : str(d) + " " + str(datetime.time(0,0,0)) ]
    night_00_03_frame = night_00_03_frame.append(night_day_frame[ str(d) + " " + str(datetime.time(21,0,0)) : str(d1) + " " + str(datetime.time(0,0,0)) ], ignore_index=True)                               
        
    nightly_mean = night_00_03_frame[ night_00_03_frame["O3"] > 20 ].median().to_frame().transpose()
    nightly_mean.insert(0, "datetime", pd.to_datetime(str(d) + " " + str(datetime.time(12,0,0)) ) )
    nightly_mean.rename(columns={"NO[ppb]":"NO_offset[ppb]"}, inplace=True)
    if nightly_mean["NO_offset[ppb]"].to_numpy() > 0.1:
        nightly_mean["NO_offset[ppb]"] = nan
    daily_offset = daily_offset.append( nightly_mean, ignore_index=True)

### create offset_frame using daily_offset. daily_offset data are reported once a day at 12:00:00.
### the temporary frame offset_dates_frame is created in order to obtain a frame with all the times
### the daily_offset frame is then merged to offset_dates_frame in order to obtain a frame with nan values everywhere except at 12:00:00  
### the obtained frame is then interpolated in order to obtain corrections at all times
offset_dates_frame = night_corr_frame["datetime"].to_frame()
offset_frame = offset_dates_frame.merge(daily_offset, how='left', left_on='datetime', right_on='datetime')
del offset_frame["daydec"]
offset_frame.interpolate(inplace=True)

#################### export offset_frame to csv ####################
if night_correction=='ON' :  
    ### BUG:: se la data parte dopo il 1/5 questo rigo da noia perché c'è gia la colonna "#@date" o "time"
    #del offset_frame["#date"] offset_frame["time"]
    offset_frame.insert(0, "date", offset_frame["datetime"].dt.date)
    offset_frame.insert(1, "time", offset_frame["datetime"].dt.time)
    offset_frame.fillna(-999,inplace=True)
    offset_frame.to_csv("offset_frame.csv", sep = ' ', index=False)

####################################################################

del offset_frame["O3"]
del night_corr_frame, offset_dates_frame

###############################################################################
### -- 3rd loop over dates for calibration, RH, O3 and night corrections -- ###
###############################################################################

    
for i in range((end_date - start_date).days):
    d = start_date + i*day_delta
    year = str(d.year)
    month = str(d.month)
    day = str(d.day)
    # convert date into str using the same format of the filenames e.g. 20210101 
    # need to add "0" to months and days <9
    if int(d.month) < 9:
        month = str(0) + str(d.month)
    if int(d.day) < 9:
        day = str(0) +str(d.day)

    # define filenames
    dd = year + month + day  #convert from datetime to string format
    date_loc_ext = "_" + location + "_" + dd + "_" + utc + ".raw"
    
    meteo_filenm = instrument[0] + date_loc_ext
    ozone_filenm = instrument[1] + date_loc_ext
    nitrate_filenm = instrument[2] + date_loc_ext
    # read data files
    try:
        meteo_frame = pd.read_csv(filepath+meteo_filenm, delimiter = " ")
        ozone_frame = pd.read_csv(filepath+ozone_filenm, delimiter = " ")
        nitrate_frame = pd.read_csv(filepath+nitrate_filenm, delimiter = " ")
    except Exception:
        print("could not open file on date " + str(d))
        continue  # skip to next day

    ########## rename daydec columns (to be changed in original headers-> Busetto) ##################
    nitrate_frame.rename(columns={"DayDec": "daydec"}, inplace = True)
    meteo_frame.rename(columns={"dey_dec": "daydec"}, inplace = True)
    
    try:
        nit_oz_frame = pd.merge(nitrate_frame, ozone_frame, on='daydec')  
        daily_frame = pd.merge( nit_oz_frame, meteo_frame, on = 'daydec')
    except:
        print("merging problem on date " +str(d))
        continue # skip to next day    
    ##############################################################################
    ##                                                                          ##
    ##                        Nighttime corrections                             ##
    ##                                                                          ##
    ##############################################################################
    if night_correction == 'ON':
        daily_offset_frame = offset_frame[offset_frame["datetime"].dt.date == d]
        daily_frame.insert(0, "datetime", pd.to_datetime( daily_frame["#date_x"] + " " + daily_frame["time_x"] ))
        ###########################################################
        ####### questo merge cambia la lunghezza di daily_frame quando si va a calcolare il between_time nell'hourly average
        ###########################################################
        daily_frame = daily_frame.merge(daily_offset_frame, how='left', left_on='datetime', right_on='datetime')  
        daily_frame = daily_frame.set_index("datetime")
        
        NO_numpy = daily_frame["NO[ppb]"].to_numpy()
        off_numpy = daily_frame["NO_offset[ppb]"].to_numpy()
        daily_frame["NO[ppb]"] = (NO_numpy - off_numpy)
    else:
        daily_frame.insert(0, "datetime", pd.to_datetime( daily_frame["#date_x"] + " " + daily_frame["time_x"] ))
        daily_frame = daily_frame.set_index("datetime")
    
    daily_frame.fillna(-999,inplace=True)
    ##############################################################################
    ##                                                                          ##
    ##                        Calibration corrections                           ##
    ##                                                                          ##
    ##############################################################################
    
    daily_frame["NO_cal"] = daily_frame["NO[ppb]"] * slopeNO + offsetNO
    daily_frame["NOx_cal1"] = daily_frame["NOx[ppb]"] * slopeNOx + offsetNOx  
    daily_frame["NO2_cal"] = ( daily_frame["NOx_cal1"] - daily_frame["NO_cal"] ) / Sc
    daily_frame["NOx_cal"] = daily_frame["NO_cal"] + daily_frame["NO2_cal"]

    ##############################################################################
    ##                                                                          ##
    ##              Application of water vapor corrections                      ##
    ##                 Application of ozone corrections                         ##
    ##                                                                          ##
    ##############################################################################

    ####--------------------- ozone correction -------------------------------####
    tc2 = 1 #duration of stay in the converter (sec)
    tc1 = 1.5 #duration of stay in the by pass line (sec)
    tL = 2.5 #duration of stay in the inlet entry to the converter( sec)
    tE1 = tc2 + tL #duration of stay in the converter plus in the inlet entry to the converter( sec)
    
    daily_frame["KO3_NO"] = 4.8E-12 *  exp( -1370 / (daily_frame["T_air[C]"] + 273.15) ) 
    daily_frame["KO3"] = daily_frame["KO3_NO"] * daily_frame["O3"] * 1E10
    Jc = -log(1-Sc)/tc2
    
    # defining NO_E1 and NO_E2 according to "SOPs for NOxy measurement" convenction
    daily_frame["NO_E1"] = daily_frame["NO_cal"] # measured NO signal [ppb] without photolytic converter
    daily_frame["NO_E2"] = Sc * daily_frame["NO2_cal"] + daily_frame["NO_cal"]  # measured NO signal [ppb] with photolytic converter
    
    daily_frame["NO_0"] = daily_frame["NO_E1"] * exp( daily_frame["KO3"] * tE1 ) 
    daily_frame["NO2_0"] = ( Jc + daily_frame["KO3"] ) / Jc * ( daily_frame["NO_E2"] - daily_frame["NO_E1"] * exp( -( daily_frame["KO3"] * (tc2-tc1) + Jc*tc2 ) )) / ( 1 - exp(-(daily_frame["KO3"] + Jc ) * tc2) ) - daily_frame["NO_0"]

    ####------------------- water vapour correction ------------------------- ####
    alpha = 0.0043 # parameter
    Pa = 1013.25 # standard pressure
    Ts = 373.15 # steam temperature at 1013.25 hPa
    
    daily_frame["t"] = 1 - Ts / (daily_frame["T_air[C]"] + 273.25) #parameter t
    daily_frame["sat_water_press"] = Pa * exp( 13.3185*daily_frame["t"]  - 1.9760 * pow(daily_frame["t"], 2)- 0.6445 * pow(daily_frame["t"], 3) - 0.1299* pow(daily_frame["t"], 4)) # stauration water pressure
    daily_frame["water_vapour_conc[ppth]"] = 1E5 * daily_frame["RH[%]"] * daily_frame["sat_water_press"] / (daily_frame["P_air[hPa]"]*1E5)
    
    daily_frame["NO_corr"] = daily_frame["NO_0"] * ( 1 + alpha * daily_frame["water_vapour_conc[ppth]"] )

    ##############################################################################
    #### --------------- Append daily_frame to tot_frame -------------------- ####
    ##############################################################################
    tot_frame = tot_frame.append(daily_frame)
    tot_frame.fillna(-999,inplace=True)
    ##############################################################################
    #### -------------- Evaluate hourly averaged data ----------------------- ####
    ##############################################################################
    ### c'è un problema: in data 4/5/2021 la lunghezza di hourly_mean è diversa da hourly_averaged_mean e non riesce a fare il .append(hourly_mean)
    ### cosa strana: se fai il ciclo tipo fino al 10 maggio funziona, se lo fai fino al 15 si blocca        

    # for j in range (0, 24): 
    #     hourly_mean = daily_frame.between_time(str(datetime.time(j,0,0)), str(datetime.time(j,59,0))).mean().to_frame().transpose() #evaluate hourly mean of daily_frame
    #     #print(hourly_mean)
    #     hourly_mean.insert(0, "ddate", d)
    #     hourly_mean.insert(1, "ttime", str(datetime.time(j,0,0)))
    #     hourly_averaged_mean = hourly_averaged_mean.append( hourly_mean , ignore_index=True ) #append to the frame that contains hourly averaged data
        
    #     #the same replacing mean with median:
    #     hourly_median = daily_frame.between_time(str(datetime.time(j,0,0)), str(datetime.time(j,59,0))).median().to_frame().transpose()
    #     hourly_median.insert(0, "ddate", d)
    #     hourly_median.insert(1, "ttime", str(datetime.time(j,0,0)))
    #     hourly_averaged_median = hourly_averaged_median.append( hourly_median , ignore_index=True )
    
##############################################################################
#### ------------- Evaluate hourly mean and median ---------------------- ####
##############################################################################

#tot_frame.insert(0, "date_time", pd.to_datetime( tot_frame["#date_x"] + " " +tot_frame["time_x"] ))
#tot_frame = tot_frame.set_index("date_time")

for k in range(0, 24):  #crea output file per ogni ora. Calcolando .mean() e .median() puoi ottenere valori medi)
     hourly = pd.DataFrame()
     hourly = hourly.append( tot_frame.between_time(str(datetime.time(k,0,0)), str(datetime.time(k,59,0))), ignore_index=True )
     hourly.rename(columns={"#date_x": "date"}, inplace = True)
     if night_correction=='ON':
         hourly.to_csv("./hourly_data/hour"+str(k)+"_night_corr.csv", sep=' ', index=False)
     else:
         hourly.to_csv("./hourly_data/hour"+str(k)+".csv", sep=' ', index=False)
         
##############################################################################
#### ----------------------- Save to File ------------------------------- ####
##############################################################################

#### remove redundant date and time cols
del tot_frame["time_x"], tot_frame["#date_y"], tot_frame["time_y"], tot_frame["#date_x"]

if night_correction=='ON' :     
    tot_frame.to_csv("tot_frame_night_corr.csv", sep = ' ')
else:
    tot_frame.to_csv("tot_frame.csv", sep = ' ')


###############################################################################
### ----- 4th loop over dates to obtain night data in minutes gnuplot ----- ###
###############################################################################

night_frame = pd.DataFrame()
 
for i in range((end_date - start_date).days):
    d_1 = start_date + (i-1)*day_delta
    d = start_date + i*day_delta
    
    if d==start_date:#skip first day
        continue
    
    night_frame = night_frame.append( tot_frame[ str(d_1) + " " + str(datetime.time(22,0,0)) : str(d) + " " + str(datetime.time(1,0,0)) ])                               

# night_frame.insert(1, "ddate", night_frame["datetime"].dt.date )
# night_frame.insert(2, "ttime", night_frame["datetime"].dt.time )

night_frame.to_csv("night_frame.csv", sep=' ')
# del hourly_averaged_mean["#date_x"], hourly_averaged_mean["#date_y"], hourly_averaged_mean["#date"], 
# del hourly_averaged_mean["time_x"], hourly_averaged_mean["time_y"], hourly_averaged_mean["time"]
# del hourly_averaged_mean["status_x"], hourly_averaged_mean["status_y"], hourly_averaged_mean["flags"]
# del hourly_averaged_median["#date_x"], hourly_averaged_median["#date_y"], hourly_averaged_median["#date"]
# del hourly_averaged_median["time_x"], hourly_averaged_median["time_y"], hourly_averaged_median["time"]
# del hourly_averaged_median["status_x"], hourly_averaged_median["status_y"], hourly_averaged_median["flags"]
#hourly_averaged_median.to_csv("./hourly_data/hourly_averaged_median.csv", sep = ' ', index=False)
# hourly_averaged_mean.to_csv("./hourly_data/hourly_averaged_mean.csv", sep = ' ', index=False)


##############################################################################
##                                                                          ##
##                              Plotting                                    ##
##                                                                          ##
##############################################################################

# daily_frame["dt"] = pd.to_datetime(daily_frame["Date"] + " " + daily_frame["Time"])

#plot_date = pd.to_datetime(tot_frame["#date_x"] + " " + tot_frame["time_x"])
#
#                                     
#                                     
## Major ticks every month.
#fmt_month = mdates.MonthLocator()
#
## Minor ticks every.
#fmt_day = mdates.DayLocator()
#
#nplots=3                                    
#fig, axs = plt.subplots(nplots, sharex=True)
#for i in range(0, nplots):
#    axs[i].xaxis.set_major_locator(fmt_month)
#    axs[i].xaxis.set_minor_locator(fmt_day)
#    
#fig.suptitle('NO and O3 corrections')
#axs[0].scatter( tot_frame["#date_x"], tot_frame["NO_cal"])
#axs[0].set_ylabel('$NO_{cal}$')
#axs[1].scatter( tot_frame["#date_x"], tot_frame["NO_corr"] - tot_frame["NO_cal"] )
#axs[1].set_ylabel('$NO_{corr} - NO_{cal}$')
#axs[2].scatter( tot_frame["#date_x"], tot_frame["NO2_0"] - tot_frame["NO2_cal"] )
#axs[2].set_ylabel('$NO_{2corr} - NO_{2cal}$')
#
#
#fig.savefig(resFolder + "NOx_corr.pdf")
#axs[2].plot( tot_frame["#date"], tot_frame["NO_corr"] - tot_frame["NO_0"])
#axs[2].set_ylabel('$NO_{corr} - NO_{0}$')

#fig3, axs3 = plt.scatter(tot_frame["NO_corr"] - tot_frame['NO_cal'], tot_frame["NO_corr"])
#plt.show()


