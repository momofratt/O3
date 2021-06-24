# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf



data_file = "tot_frame_header_corrected.csv"

		
set style line 1 pt 0 ps 1 lc rgb "red"
set style line 2 pt 0 ps 1 lc rgb "green"
set style line 3 pt 0 ps 1 lc rgb "purple"

set grid 

##### NO2 SCATTER ######

set output "./results/NO2_scatter_O3.pdf"
set xlabel "{/Symbol D}NO_2 / NO_2 [-]"
set ylabel "O3 [ppb]"

set xtics
set ytics 
set xrange[0:1]

plot data_file u (abs( (column("NO2_0") - column("NO2_cal") ) / column("NO2_cal") )  ):"O3" w p ls 1 notitle

set output "./results/NO2_scatter_RH.pdf"
set ylabel "RH[%]"
plot data_file u (abs( (column("NO2_0") - column("NO2_cal") ) / column("NO2_cal")  ) ):"RH[%]" w p ls 1 notitle


#### NO SCATTER ######

set output "./results/NO_scatter_O3.pdf"
set xlabel "{/Symbol D}NO / NO [-]"
set ylabel "O3 [ppb]"
set xrange [0:1]

set xtics 
set ytics 

plot data_file u ( (column("NO_corr") - column("NO_cal") ) / column("NO_cal")   ):"O3" w p ls 1 notitle

set output "./results/NO_scatter_RH.pdf"
set ylabel "RH[%]"
plot data_file u ( (column("NO_corr") - column("NO_cal") ) / column("NO_cal")   ):"RH[%]" w p ls 1 notitle


