# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf

data_file = "./hourly_data/hourly_averaged_mean.csv"

set style line 1 pt 0 ps 1 lw .1 lc rgb "red"
set style line 2 pt 0 ps 1 lw .1 lc rgb "green"
set style line 3 pt 0 ps 1 lw .1 lc rgb "purple"

set xdata time
set grid 
set timefmt "%Y-%m-%d %H:%M:%S"
start_date = "2021-05-01 00:00:00"
end_date = "2021-06-10 23:59:00"
set xrange [start_date:end_date]

##### NO2 PLOT ######

set output "./results/NOx_hourly.pdf"

set title "Hourly Averaged NO_x Concentrations"

set multiplot layout 3,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# margins 0.05,0.95,.1,.99 spacing 0,0
set xtics nomirror out
set format x ''
set mytics 2

set ylabel "NO2_{corr} [ppb]"
#set ytics 0, 15, 90
#set yrange[-10:80]
plot data_file u 1:"NO2_0" w l ls 1 notitle 
unset title 

set ytics -10, 10, 100
#set yrange [-5:60]
set ylabel "NO_{corr} [ppb]"
plot data_file u 1:"NO_corr" w l ls 3 notitle
unset yrange 

set format x '%d/%m'
set ylabel "NO_x [ppb]"
set ytics -15, 15, 100
set mytics 2
#set yrange [-1:1]
plot data_file u 1:(column("NO_corr") + column("NO2_0")) w l ls 2 notitle 
unset yrange

unset multiplot
