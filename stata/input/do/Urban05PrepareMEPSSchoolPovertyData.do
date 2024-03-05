** This file cleans the meps school poverty data from the Urban Institute endpoint and saves it as a working data set

* Model Estimates of Poverty in Schools is the Urban Institute's school-level measure of the percentage of students living in poverty. It is comparable across states and time. Derived from the CCD and the SAIPE, it provides the estimated percentage of students with family incomes up to 100 percent of the federal poverty level for the years 2013 through 2018.

* (from the Urban Institute) MEPS can under- or overestimate poverty shares for certain districts. In particular, we find that our model underestimates school-level poverty for districts enrolling high shares of Black students. To correct for this, we produce modified MEPS, a second measure that mechanically adjusts our estimate to align with geographic district poverty rates. Because of wider margins of error for districts with small populations in the SAIPE data, we recommend using modified MEPS only for analysis of geographic districts with more than 65,000 residents. https://www.urban.org/research/publication/model-estimates-poverty-schools

* thus, mod = modified

* gleaid is the geographic leaid. UI linked schools' geographic locations with the geographic boundaries of districts. it's more accurate for our use than the leaid because it does not include leaids that are strictly for administrative purposes. keep both just in case

* meps_poverty_pct: estimated percentage of students living in poverty
* meps_poverty_se: standard error for estimated percentage of students living in poverty
* meps_poverty_ptl: estimated national percentile of students living in poverty, weighed by enrollment

* Change to working directory
cd "${dir}"

* Read in data
clear
use "output/dta/schoolmepsraw.nvc.dta"

keep if year==2016

*drop bc it is the numeric version of ncessch, which we already have
drop ncessch_num 

drop meps_poverty_se


** save as a working data set
save output/dta/schoolmepsworking.nvc.dta, replace
