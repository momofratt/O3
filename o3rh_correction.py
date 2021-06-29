# -*- coding: utf-8 -*-
"""
Author: Cosimo Fratticioli
Contact: c.fratticioli@isac.cnr.it
"""
import pandas as pd
from math import log
from numpy import exp
import matplotlib.dates as mdates
from datetime import date, timedelta
import datetime
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


tot_frame = pd.DataFrame()
hourly_averaged_mean = pd.DataFrame()
hourly_averaged_median = pd.DataFrame()

day_delta = timedelta(days=1) # The size of each step in days
start_date = date(2021, 5, 1)
#end_date = date.today()
end_date = date(2021, 6, 8)

############ loop over dates ####################
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
    meteo_frame.rename(columns={"dey_dec": "daydec"}, inplace = True)
    nitrate_frame.rename(columns={"DayDec": "daydec"}, inplace = True)
    
    #meteo_frame.sort_values(by='daydec', inplace=True)
    #ozone_frame.sort_values(by='daydec', inplace=True)
    #nitrate_frame.sort_values(by='daydec', inplace=True)
    
    ############# define single frame with aligned times ####################
    # daily_frame contains all the data from meteo, nitrate and ozone frames
    ######## TO BE IMPROVED???? (merge_asof does not align): 
    # data are aligned on 'day_dec'. If times do not match, the line is not included in daily_frame
    try:
        nit_oz_frame = pd.merge(nitrate_frame, ozone_frame, on='daydec')
        daily_frame = pd.merge(nit_oz_frame, meteo_frame, on='daydec')
        #nit_oz_frame = pd.merge_asof(nitrate_frame, ozone_frame, on='daydec')
        #daily_frame = pd.merge_asof(nit_oz_frame, meteo_frame, on='daydec')
    except:
        print("merging problem on date " +str(d))
        continue # skip to next day
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
#### ------ calculate NO2 using NO_corr (RH corrected) values ----------- ####
##############################################################################


    # same as before replacing NO_cal with NO_corr
    #daily_frame["NO_F1"] = daily_frame["NO_corr"] 
    #daily_frame["NO_F2"] = Sc * daily_frame["NO2_cal"] + daily_frame["NO_corr"]  
    
    #daily_frame["NO_00"] = daily_frame["NO_F1"] * exp( daily_frame["KO3"] * tE1 ) 
    #daily_frame["NO2_RHcorr"] = ( Jc + daily_frame["KO3"] ) / Jc * ( daily_frame["NO_F2"] - daily_frame["NO_F1"] * exp( -( daily_frame["KO3"] * (tc2-tc1) + Jc*tc2 ) )) / ( 1 - exp(-(daily_frame["KO3"] + Jc ) * tc2) ) - daily_frame["NO_00"]
    
    # plotting differences
    
    #fig1, axs1 = plt.subplots(2, sharex=True)
    #axs1[0].plot( daily_frame["day_dec"], daily_frame["NO2_0"] )
    #axs1[0].plot( daily_frame["day_dec"], daily_frame["NO2_RHcorr"]  )
    #axs1[0].set_ylabel('$NO_2$')
    
    #axs1[1].plot( daily_frame["day_dec"], daily_frame["NO2_RHcorr"] - daily_frame["NO2_0"] )
    #axs1[1].set_ylabel('$\Delta NO_2$')

##############################################################################
#### --------------- Append daily_frame to tot_frame -------------------- ####
##############################################################################

    tot_frame = tot_frame.append(daily_frame, ignore_index=True)

##############################################################################
#### -------------- Evaluate hourly averaged data ----------------------- ####
##############################################################################
    daily_frame.insert(0, "datetime", pd.to_datetime( tot_frame["#date_x"] + " " +tot_frame["time_x"] ))
    daily_frame = daily_frame.set_index("datetime")
    for j in range (0, 24):
        mean_daily = daily_frame.between_time(str(datetime.time(j,0,0)), str(datetime.time(j,59,0))).mean().to_frame().transpose() #evaluate hourly mean of daily_frame
        mean_daily.insert(0, "ddate", d)
        mean_daily.insert(1, "ttime", str(datetime.time(j,0,0)))
        hourly_averaged_mean = hourly_averaged_mean.append( mean_daily , ignore_index=True ) #append to the frame that contains hourly averaged data
        
        #the same replacing mean with median:
        median_daily = daily_frame.between_time(str(datetime.time(j,0,0)), str(datetime.time(j,59,0))).median().to_frame().transpose()
        median_daily.insert(0, "ddate", d)
        median_daily.insert(1, "ttime", str(datetime.time(j,0,0)))
        hourly_averaged_median = hourly_averaged_median.append( median_daily , ignore_index=True )

##############################################################################
#### ------------- Evaluate hourly mean and median ---------------------- ####
##############################################################################

tot_frame.insert(0, "datetime", pd.to_datetime( tot_frame["#date_x"] + " " +tot_frame["time_x"] ))
tot_frame = tot_frame.set_index("datetime")

for k in range(0, 24):  #crea output file per ogni ora. Calcolando .mean() e .median() puoi ottenere valori medi)
     hourly = pd.DataFrame()
     hourly = hourly.append( tot_frame.between_time(str(datetime.time(k,0,0)), str(datetime.time(k,59,0))), ignore_index=True )
     hourly.rename(columns={"#date_x": "date"}, inplace = True)
     hourly.to_csv("./hourly_data/hour"+str(k)+".csv", sep=' ', index=False)
     del(hourly)

##############################################################################
#### ----------------------- Save to File ------------------------------- ####
##############################################################################

# remove redundant date and time cols
del tot_frame["time"], tot_frame["#date_y"], tot_frame["time_y"], tot_frame["#date"]
del hourly_averaged_mean["#date_x"], hourly_averaged_mean["#date_y"], hourly_averaged_mean["#date"], 
del hourly_averaged_mean["time_x"], hourly_averaged_mean["time_y"], hourly_averaged_mean["time"]
del hourly_averaged_mean["status_x"], hourly_averaged_mean["status_y"], hourly_averaged_mean["flags"]
del hourly_averaged_median["#date_x"], hourly_averaged_median["#date_y"], hourly_averaged_median["#date"]
del hourly_averaged_median["time_x"], hourly_averaged_median["time_y"], hourly_averaged_median["time"]
del hourly_averaged_median["status_x"], hourly_averaged_median["status_y"], hourly_averaged_median["flags"]

tot_frame.to_csv("tot_frame.csv", sep = ' ')
hourly_averaged_median.to_csv("./hourly_data/hourly_averaged_median.csv", sep = ' ', index=False)
hourly_averaged_mean.to_csv("./hourly_data/hourly_averaged_mean.csv", sep = ' ', index=False)

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


