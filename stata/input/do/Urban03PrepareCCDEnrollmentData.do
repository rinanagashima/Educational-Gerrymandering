** This file cleans the CCD Enrollment data from the Urban Institute endpoint and saves it as a working data set

* This endpoint contains student membership data for each school by grade. Only operational schools serving one or more grades are required to report membership and only these are included in this endpoint. https://educationdata.urban.org/documentation/schools.html#ccd-enrollment-by-grade

* Change to working directory
cd "${dir}"

* Read in data
clear
use "output/dta/ccdenrollmentraceraw.nvc.dta"

*drop bc it is the numeric version of ncessch, which we already have
drop ncessch_num 

*** drop all US territories ***
*pr
drop if fips == 72 | fips == 43
*guam
drop if fips == 66
*northern mariana islands
drop if fips == 69
*virgin islands
drop if fips == 78
*american samoa
drop if fips == 60

* drop dept of defense dependent schools overseas and domestic, and dod educ activity schools
drop if fips == 58
drop if fips == 61
drop if fips == 63

* drop bureau of indian education schools
drop if fips == 59

* transpoise race var 
gen enrollwhite = enrollment if race == 1
gen enrollblack = enrollment if race == 2
gen enrollhispanic = enrollment if race == 3
gen enrollasian = enrollment if race == 4
gen enrollaian = enrollment if race == 5
gen enrollnhpi = enrollment if race == 6
gen enrollmultirace = enrollment if race == 7
gen enrollunknownrace = enrollment if race == 9
gen totenrollment = enrollment if race == 99
drop enrollment
drop race

drop sex

* get rid of repeat observations by collapsing all race enrollment counts by school
collapse (lastnm) year leaid-totenrollment, by(ncessch)



** save as a working data set
save output/dta/ccdenrollmentworking.nvc.dta, replace