# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
# plot over whole period and over single weeks

set terminal postscript eps size 5,7 enhanced color 

data_file = "./tot_frame.csv"

set style line 1 pt 0 ps 1 lw .1 lc rgb "red"
set style line 2 pt 0 ps 1 lw .1 lc rgb "green"
set style line 3 pt 0 ps 1 lw .1 lc rgb "purple"

set xdata time
set grid 
set timefmt '"%Y-%m-%d %H:%M:%S"'

#'"2021-05-15 00:00:00"', '"2021-05-22 00:00:00"', '"2021-05-29 00:00:00"', '"2021-06-05 00:00:00"'
i = 1

array dates = [ "2021-05-01 2021-06-08", "2021-05-01 2021-05-08", "2021-05-08 2021-05-15", "2021-05-15 2021-05-22", "2021-05-22 2021-05-29", "2021-05-29 2021-06-07"]

do for [i=1:6]{

start_date = "\"".substr(dates[i], 0, 10)."\""
end_date = "\"".substr(dates[i], 12, 21)."\""

set xrange [start_date:end_date]

##### NO2 PLOT ######

set output "./results/NO_calibrated_week_".(i-1).".eps"

if (i==1){
set output "./results/NO_calibrated.eps"
}

set title "NO and NO_2 Calibrated Concentrations"

set multiplot layout 2,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# margins 0.05,0.95,.1,.99 spacing 0,0
set xtics nomirror out
set format x ''
set mytics 2

set ylabel "NO^{cal} [ppb]"
#set ytics 0, 15, 90
#set yrange[-10:80]
plot data_file u 1:"NO_cal" w l ls 1 notitle 
unset title 

set format x '%d/%m'
#set ytics -10, 10, 100
#set yrange [-5:60]
set ylabel "NO_2^{cal} [ppb]"
plot data_file u 1:"NO2_cal" w l ls 3 notitle
unset yrange 

unset multiplot

}
