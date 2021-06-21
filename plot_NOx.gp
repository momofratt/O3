# plot Measured gas concentrations using datetime format ( yyyy-mm-dd HH:MM:SS )
set term pdf


set output "./results/NO2.pdf"
data_file = "tot_frame.csv"
plotted_col = "NO2_cal"

set style line 1 pt 0 ps 1

set xdata time
set grid 
set ylabel "$NO_2cal$"
set timefmt "%Y-%m-%d %H:%M:%S"
plot data_file u 2:plotted_col w p ls 1
