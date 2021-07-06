# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf



data_file = "night_frame.csv"

		
set style line 1 pt 0 ps 1 lc rgb "red"
set style line 2 pt 0 ps 1 lc rgb "green"
set style line 3 pt 0 ps 1 lc rgb "purple"

set xdata time
set grid 
set timefmt '"%Y-%m-%d %H:%M:%S"'
#set xrange ["2021-05-03 12:00:00" : "2021-06-08 12:00:00"]

#### NO PLOT ######

set output "./results/NO_night.pdf"
set ylabel "NO"
set format x ''

set multiplot layout 2,1 margins 0.15,0.85,.1,.9 spacing 0.05,0.05

#plot relative correction
#set ytics 0, 0.1, 0.3
set yrange [-1:5]
set ytics 0.5

set ylabel "NO^{corr}[ppb]"
plot data_file u 1:"NO_corr" w p ls 2 notitle

set format x '%d/%m'
#set yrange [-1:3]
set ylabel "NO[ppb]"
plot data_file u 1:(column("NO_corr") + column("NO_offset[ppb]") ) w p ls 3 notitle
unset yrange

unset multiplot
