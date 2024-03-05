*** This do file reads in the school-level institutional and demographic data using the UI API and saves the data sets locally

*Change to working directory
cd "${dir}"
cap mkdir output
cap mkdir output/dta

*install the package
ssc install libjson
*update the package
net install educationdata, replace from("https://urbaninstitute.github.io/education-data-package-stata/")

*read in the directory endpoint

clear
 
*Read in Common Core Data directory (fte teachers, school location)
educationdata using "school ccd directory", csv
save output/dta/ccddirectoryraw.nvc.dta, replace


clear

*Read in Common Core Data enrollment by race and grade data
educationdata using "school ccd enrollment race", csv
save output/dta/ccdenrollmentraceraw.nvc.dta, replace


clear

*Read in crdc data on the number of fte teachers and staff at each school
educationdata using "school crdc teachers-staff", csv
save output/dta/crdcteachersstaffraw.nvc.dta, replace

clear

*Read in the meps school poverty measure data
educationdata using "school meps", csv
save output/dta/schoolmepsraw.nvc.dta, replace

clear

*Read in the schools merged with 2010 census geography variables
educationdata using "school nhgis census-2010", csv
save output/dta/schoolcensus2010raw.nvc.dta, replace

