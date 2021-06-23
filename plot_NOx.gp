# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf



data_file = "tot_frame_header_corrected.csv"

		
set style line 1 pt 0 ps 1 lc rgb "red"
set style line 2 pt 0 ps 1 lc rgb "green"
set style line 3 pt 0 ps 1 lc rgb "purple"

set xdata time
set grid 
set timefmt "%Y-%m-%d %H:%M:%S"


##### NO2 PLOT ######

set output "./results/NO2.pdf"
set ylabel "NO_2"


set multiplot layout 3,1 
# prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# margins 0.05,0.95,.1,.99 spacing 0,0
unset xtics

set ytics -10, 20, 70
plot data_file u 2:"NO2_cal" w p ls 1 t "NO2_{cal}", \
	data_file u 2:"NO2_0" w p ls 2 t "NO2_{corr}"

set ytics 0, 0.2, 1
set yrange [0:1]
plot data_file u 2:( (column("NO2_0") - column("NO2_cal") ) / column("NO2_cal")   ) w p ls 3 t "{/Symbol D}NO_2 / NO_2 [-]"
unset yrange

set xtics
set ytics -1, 1, 3
set yrange [-1:3]
plot data_file u 2:(column("NO2_cal") - column("NO2_0") ) w p ls 3 t "NO2_{cal} - NO2_{corr}"
unset yrange 

unset multiplot


#### NO PLOT ######

set output "./results/NO.pdf"
set ylabel "NO"


set multiplot layout 3,1 

#plot NO_cal and corr on the same plot
set ytics -10, 40,130
plot data_file u 2:"NO_cal" w p ls 1 t "NO_{cal}", \
	data_file u 2:"NO_corr" w p ls 2 t "NO_{corr}"


#plot relative correction
set ytics 0, 0.1, 0.3
plot data_file u 2:( (column("NO_corr") - column("NO_cal") ) / column("NO_cal")   ) w p ls 3 t "{/Symbol D}NO / NO [-]"

set ytics -1, 2, 3
set yrange [-1:3]
plot data_file u 2:(column("NO_corr") - column("NO_cal") ) w p ls 3 t "NO_{corr} - NO_{cal}"
unset yrange

unset multiplot
