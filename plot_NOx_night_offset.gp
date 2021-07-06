# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf



data_file = "offset_frame.csv"

		
set style line 1 pt 4 ps .01 lc rgb "red"
set style line 2 pt 4 ps .01 lc rgb "green"
set style line 3 pt 0 ps 1 lc rgb "purple"

set xdata time
set grid 
set timefmt "%Y-%m-%d %H:%M:%S"

##### NO2 PLOT ######

set output "./results/night_offset.pdf"

set multiplot layout 2,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05

set xrange ["2021-05-2 12:00:01":"2021-06-08 12:00:00"]
set xtics
set format x ''
set mytics 2

#set ytics 0, 15, 90
#set yrange[-10:80]
set ylabel "NO_{offset}[ppb]"
plot data_file u 1:"NO_offset[ppb]" w p ls 1 notitle    

set format x '%d/%m'
set ylabel "O_3^{interp} [ppb]"
plot data_file u 1:"O3" w p ls 2 notitle  

unset multiplot


