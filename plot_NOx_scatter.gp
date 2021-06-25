# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf



data_file = "tot_frame_header_corrected.csv"

		
set style line 1 pt 0 ps 1 lc rgb "red"
set style line 2 pt 0 ps 1 lc rgb "green"
set style line 3 pt 0 ps 1 lc rgb "purple"

set grid 

##### NO2 SCATTER ######

set output "./results/NO2_scatter.pdf"
set xlabel "{/Symbol D}NO_2 / NO_2 [-]"
set ylabel "NO_2 [ppb]"

set xtics 0,0.1,1
set mxtics 2
set ytics 

set xrange[0:1]
plot data_file u ( (column("NO2_0") - column("NO2_cal") ) / column("NO2_cal")   ):"NO2_cal" w p ls 1 notitle
# data_file u 2:"NO2_0" w p ls 2 t "NO2_{corr}"


#### NO SCATTER ######

set output "./results/NO_scatter.pdf"
set xlabel "{/Symbol D}NO / NO [-]"
set ylabel "NO [ppb]"

set xtics 0,0.1,1
set mxtics 2
set ytics 

set xrange[0:1]
plot data_file u ( (column("NO_corr") - column("NO_cal") ) / column("NO_cal")   ):"NO_cal" w p ls 1 notitle
# data_file u 2:"NO2_0" w p ls 2 t "NO2_{corr}"


