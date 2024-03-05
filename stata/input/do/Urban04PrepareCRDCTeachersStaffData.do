** This file cleans the CRDC Teacher Staff data from the Urban Institute endpoint and saves it as a working data set

* This endpoint contains data on the number of FTE teachers and staff at each school. https://educationdata.urban.org/documentation/schools.html#crdc_teachers-and-staff

* Change to working directory
cd "${dir}"

* Read in data
clear
use "output/dta/crdcteachersstaffraw.nvc.dta"

* only years 2011, 2013, 2015, and 2017 were available.
keep if year==2015 
rename year yearteacher

drop teachers_certified_fte-law_enforcement_ind

drop if ncessch==""

* there are some duplicates of ncessch due to obs with different crdc_id and the same ncessch. the crdc_id is the office of civil rights school ID and is supposed to uniquely identify each school. however, all other data sets use the ncessch so I will combine the crdc teacher counts by ncessch
collapse (sum) teachers_f~c (lastnm) fips yearteacher leaid, by(ncessch)

** save as a working data set
save output/dta/crdcteachersstaffworking.nvc.dta, replace
