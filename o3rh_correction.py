# -*- coding: utf-8 -*-
"""
Author: Cosimo Fratticioli
Contact: c.fratticioli@isac.cnr.it
"""
import pandas as pd
from math import log
from numpy import exp
from datetime import date
import matplotlib.pyplot as plt
###------------------------------###
# defining filenames and paths
###------------------------------###

# defining file references
instrument = ["meteo", "O3tei49i", "T200up"]
location = "BOS"
utc = "p00" 

# ####################################################### #
# cycle over dates (in case of analysis of past dataset)  #
# ####################################################### #

# The size of each step in days
#day_delta = datetime.timedelta(days=1)

#start_date = date(2021, 1, 1)
#end_date = date.today()

#for i in range((end_date - start_date).days):
#    d = print(start_date + i*day_delta)

# ####################################################### #
# ####################################################### #

#d = date.today()
d = date(2021, 5, 31)
year = str(d.year)
month = str(d.month)
day = str(d.day)

if int(d.month) < 9:
    month = str(0) + str(d.month)
if int(d.day) < 9:
    day = str(0) +str(d.day)


dd = year + month + day  #convert from datetime to string format

date_loc_ext = "_" + location + "_" + dd + "_" + utc + ".raw"

# define filenames
meteo_filenm = instrument[0] + date_loc_ext 
ozone_filenm = instrument[1] + date_loc_ext
nitrate_filenm = instrument[2] + date_loc_ext

# define filepath
filepath = "./data/"

# read data files
meteo_frame = pd.read_csv(filepath+meteo_filenm, delimiter = " ")
ozone_frame = pd.read_csv(filepath+ozone_filenm, delimiter = " ")
nitrate_frame = pd.read_csv(filepath+nitrate_filenm, delimiter = " ")

meteo_frame.rename(columns={"#date":"Date", "time":"Time", "dey_dec": "DayDec"}, inplace = True)
ozone_frame.rename(columns={"#date":"Date", "time":"Time", "daydec": "DayDec"}, inplace = True)

#meteo_frame["DayDec"] = meteo_frame["DayDec"].astype(str)
#meteo_frame["DayDec"] = pd.to_numeric(meteo_frame["DayDec"],downcast="float")
#meteo_frame.set_index("Time")

########## convert to datetime format (to be improved) ##################
#meteo_frame["Date"] = pd.to_datetime(meteo_frame["Date"])

############# define single frame with aligned times ####################
nit_oz_frame = pd.merge_asof(nitrate_frame, ozone_frame, on='DayDec')
tot_frame = pd.merge_asof(nit_oz_frame, meteo_frame, on='DayDec')

##############################################################################
##                                                                          ##
##                        calibration corrections                           ##
##                                                                          ##
##############################################################################

# slope and offset for calibration of NO and NOx
a = 1.06270603
b = -0.1934
ax = 1.06270603
bx = -0.319
Sc = 0.75  # conversion efficiency
if(Sc>1):
    print("ERROR: efficiency greater then 1")

tot_frame["NO_cal"] = tot_frame["NO[ppb]"] * a + b
tot_frame["NOx_cal1"] = tot_frame["NOx[ppb]"] * ax + bx  
tot_frame["NO2_cal"] = ( tot_frame["NOx_cal1"] - tot_frame["NO_cal"] ) / Sc
tot_frame["NOx_cal"] = tot_frame["NO_cal"] + tot_frame["NO2_cal"]


##############################################################################
##                                                                          ##
##              Application of water vapor correction                       ##
##                 Application of ozone correction                          ##
##                                                                          ##
##############################################################################

####--------------------- ozone correction -------------------------------####
tc2 = 1 #duration of stay in the converter (sec)
tc1 = 1.5 #duration of stay in the by pass line (sec)
tL = 2.5 #duration of stay in the inlet entry to the converter( sec)
tE1 = tc2 + tL #duration of stay in the converter plus in the inlet entry to the converter( sec)

tot_frame["KO3_NO"] = 4.8E-12 *  exp( -1370 / (tot_frame["T_air[C]"] + 273.15) ) 
tot_frame["KO3"] = tot_frame["KO3_NO"] * tot_frame["O3"] * 1E10
Jc = -log(1-Sc)/tc2


# defining NO_E1 and NO_E2 according to "SOPs for NOxy measurement" convenction
tot_frame["NO_E1"] = tot_frame["NO_cal"] # measured NO signal [ppb] without photolytic converter
tot_frame["NO_E2"] = Sc * tot_frame["NO2_cal"] + tot_frame["NO_cal"]  # measured NO signal [ppb] with photolytic converter

tot_frame["NO_0"] = tot_frame["NO_E1"] * exp( tot_frame["KO3"] * tE1 ) 
tot_frame["NO2_0"] = ( Jc + tot_frame["KO3"] ) / Jc * ( tot_frame["NO_E2"] - tot_frame["NO_E1"] * exp( -( tot_frame["KO3"] * (tc2-tc1) + Jc*tc2 ) )) / ( 1 - exp(-(tot_frame["KO3"] + Jc ) * tc2) ) - tot_frame["NO_0"]

####------------------- water vapour correction --------------------------####
alpha = 0.0043 # parameter
Pa = 1013.25 # standard pressure
Ts = 373.15 # steam temperature at 1013.25 hPa

tot_frame["t"] = 1 - Ts / (tot_frame["T_air[C]"] + 273.25) #parameter t
tot_frame["sat_water_press"] = Pa * exp( 13.3185*tot_frame["t"]  - 1.9760 * pow(tot_frame["t"], 2)- 0.6445 * pow(tot_frame["t"], 3) - 0.1299* pow(tot_frame["t"], 4)) # stauration water pressure
tot_frame["water_vapour_conc[ppth]"] = 1E5 * tot_frame["RH[%]"] * tot_frame["sat_water_press"] / (tot_frame["P_air[hPa]"]*1E5)

tot_frame["NO_corr"] = tot_frame["NO_0"] * ( 1 + alpha * tot_frame["water_vapour_conc[ppth]"] )

#plt.plot( (tot_frame["NO_cal"]  ) )


##############################################################################
##                                                                          ##
##                              Plotting                                    ##
##                                                                          ##
##############################################################################

tot_frame["dt"] = pd.to_datetime(tot_frame["Date"] + " " + tot_frame["Time"])

fig, axs = plt.subplots(3, sharex=True, sharey=True)
fig.suptitle('NO and O3 corrections')
axs[0].plot( tot_frame["DayDec"], tot_frame["NO_cal"])
axs[1].plot( tot_frame["DayDec"], tot_frame["NO_cal"] - tot_frame["NO_corr"] )
axs[2].plot( tot_frame["DayDec"], tot_frame["NO_corr"] - tot_frame["NO_0"])
