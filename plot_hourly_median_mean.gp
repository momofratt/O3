set term pdf

hour_path="./hourly_data/"
night = "_night_corr" # night = "" per fare plot dei files senza night correction
set grid
set ytics
set mytics
set mxtics 5

set ytics 0,3,30

set style line 1 pt 7 ps 0.2 lc rgb "red"
set style line 2 pt 7 ps 0.2 lc rgb "green"
set style line 3 pt 7 ps 0.2 lc rgb "purple"

set style fill solid 0.5 border -1
set style boxplot nooutliers sorted pointtype 7
set style data boxplot
#set style boxplot fraction 0.95
set boxwidth  0.5
set pointsize 0.5
set key off

# ##################################################################################
# ################################ NOx Corrected ###################################
# ##################################################################################
# 
# set output "./results/hourly_box_NOx_corr.pdf"
# 
# set title "Hourly Values for NO_x Corrected"
# 
# set multiplot layout 3,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# # prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# # margins 0.05,0.95,.1,.99 spacing 0,0
# set xtics
# set format x ''
# set xrange [-1:25] 
# 
# set yrange [-2:27]
# set ytics 0,5,30
# set ylabel "NO_2 [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv"  u (i):"NO2_0" ls 1
# unset title
# 
# set yrange [-1.5:10]
# set ytics 0,2,10
# set ylabel "NO [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):"NO_corr" ls 2
# 
# set yrange [-1:32]
# set ytics 0,5,32
# set ylabel "NO_x [ppb]"
# set format x "% g"
# set xlabel "time [h]"
# 
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):(column("NO_corr") + column("NO2_0")) ls 3
# unset multiplot
# unset xlabel
# 
# 
# ##################################################################################
# ################################ NOx Calibrated ###################################
# ##################################################################################
# 
# 
# set output "./results/hourly_box_NOx_cal.pdf"
# 
# set title "Hourly Values for NO_x Calibrated"
# 
# set multiplot layout 3,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# # prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# # margins 0.05,0.95,.1,.99 spacing 0,0
# set xtics
# set format x ''
# set xrange [-1:25] 
# 
# set yrange [-2:27]
# set ytics 0,5,30
# set ylabel "NO_2 [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv"  u (i):"NO2_cal" ls 1
# unset title
# 
# set yrange [-1.5:10]
# set ytics 0,2,10
# set ylabel "NO [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):"NO_cal" ls 2
# 
# set yrange [-1:32]
# set ytics 0,5,32
# set ylabel "NO_x [ppb]"
# set format x "% g"
# set xlabel "time [h]"
# 
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):"NOx_cal" ls 3
# unset multiplot
# unset xlabel
# 
# 
# ##################################################################################
# ############################ NOx Hourly Differences ##############################
# ##################################################################################
# 
# 
# set output "./results/hourly_box_NOx_diff.pdf"
# 
# set title "Hourly Differences: NO_x^{corr} - NO_x^{cal}"
# 
# set multiplot layout 3,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# # prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# # margins 0.05,0.95,.1,.99 spacing 0,0
# set xtics
# set format x ''
# set xrange [-1:25] 
# 
# set yrange [-.3:.2]
# set ytics -.3,.1,.2
# 
# set ylabel "{/Symbol D}NO_2 [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv"  u (i):(column("NO2_0")-column("NO2_cal")) ls 1
# unset title
# 
# set yrange [-.1:.4]
# set ytics -.1,.1,.4
# set ylabel "{/Symbol D}NO [ppb]"
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):(column("NO_corr")-column("NO_cal")) ls 2
# 
# set yrange [-.05:.15]
# set ytics -.1,.05,.2
# set ylabel "{/Symbol D}NO_x [ppb]"
# set format x "% g"
# set xlabel "time [h]"
# plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):((column("NO2_0")+column("NO_corr")) - column("NOx_cal")) ls 3
# 
# unset multiplot
# unset xlabel

##################################################################################
########################### NO Night Corr ON and OFF #############################
##################################################################################


set output "./results/hourly_box_NO_night_corr_comparison.pdf"

set title "Night Correction for NO Concentrations"

set multiplot layout 2,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# margins 0.05,0.95,.1,.99 spacing 0,0
set xtics
set format x ''
set xrange [-1:25] 

set yrange [-1.5:10]
set ytics 0,2,10

set ylabel "NO^{corr}[ppb]"
plot for [i=0:23] hour_path."hour".i.".csv"  u (i):"NO_corr" ls 1
unset title


set ylabel "NO^{night corr} [ppb]"
set format x "% g"
set xlabel "time [h]"
plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):"NO_corr" ls 1

unset multiplot
unset xlabel


##################################################################################
######################### NO Night Corr ON and OFF ZOOM ##########################
##################################################################################


set output "./results/hourly_box_NO_night_corr_comparison_zoom.pdf"

set title "Night Correction for NO Concentrations"

set multiplot layout 2,1  margins 0.15,0.85,.1,.9 spacing 0.05,0.05
# prova per attaccare tutti i plot con stesso asse x. Dice di usare terminal tikz
# margins 0.05,0.95,.1,.99 spacing 0,0
set xtics
set format x ''
set xrange [-1:25] 

set yrange [-.7:.7]
set ytics -.8,.2,.8

set ylabel "NO_{corr} [ppb]"
plot for [i=0:23] hour_path."hour".i.".csv"  u (i):"NO_corr" ls 1
unset title


set ylabel "NO_{night corr} [ppb]"
set format x "% g"
set xlabel "time [h]"
plot for [i=0:23] hour_path."hour".i.night.".csv" u (i):"NO_corr" ls 1

unset multiplot
unset xlabel


