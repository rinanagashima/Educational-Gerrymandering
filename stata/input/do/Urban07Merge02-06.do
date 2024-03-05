** This do-file will merge the data sets from Urban02-06 into one file



* Change to working directory
cd "${dir}"

* Read in data from 02.do
clear
use "output/dta/ccddirectoryworking.nvc.dta"
* print var names to compare
ds


clear
use "output/dta/ccdenrollmentworking.nvc.dta"
* print var names to compare
ds


merge 1:1 ncessch using "output/dta/ccddirectoryworking.nvc.dta"
rename _merge _merge0203

* drop obs that are in ccdenrollment and are not in ccddirectory (bc ccddirectory filtered out schools like magnet and charters)
drop if _merge==1
*note that there are 37 schools from ccddirectory that were not in ccdenrollment


** now, merge with teacher fte count
merge 1:1 ncessch using "output/dta/crdcteachersstaffworking.nvc.dta"
* drop the obs that were in the crdc dataset and not the ccddirectory dataset
drop if _merge==2
rename _merge _merge0204

** now, merge with 05 meps school poverty 
merge 1:1 ncessch using "output/dta/schoolmepsworking.nvc.dta"
* drop obs in the meps dataset that is not in the ccd directory dataset
drop if _merge==2
rename _merge _merge0205

** now, merge with 06 school merged w census dataset
merge 1:1 ncessch using "output/dta/schoolcensus2010working.nvc.dta"
* drop obs in the school merged w census data that is not in the ccd directory data
drop if _merge==2
* drop _merge because num_obs(_merge==1) = 0
drop _merge

* save as a working dataset
save output/dta/mergedurbanschooldata.nvc.dta, replace


