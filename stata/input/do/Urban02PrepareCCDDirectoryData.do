** This file cleans the CCD Directory data from the Urban Institute endpoint and saves it as a working data set

* This endpoint contains school-level information on location, mailing addresses, school types, highest and lowest grades offered, and free and reduced-price lunch. This endpoint also contains the school-level data on the number of full-time eqivalent teachers. https://educationdata.urban.org/documentation/schools.html#ccd_directory 

* Change to working directory
cd "${dir}"

* Read in data
clear
use "output/dta/ccddirectoryraw.nvc.dta"

* see the following for a more detailed description of each variable:
* nces.ed.gov/ccd/commonfiles/glossary.asp

*drop bc it is the numeric version of ncessch, which we already have
drop ncessch_num 

* keep only the 2015-2016 school year data
keep if year == 2016

* drop vars related to legislative districts
drop congress_district_id-state_leg_district_upper

* drop mailing vars
drop street_mailing-zip_mailing

* drop other geographic vars
drop seasch
drop street_location-zip_location
drop county_code
drop cbsa csa

* drop other irrelevant vars
drop phone

* drop lat long here so we only rely on the ones from the 06 census file
drop latitude longitude


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
drop if bureau_indian_education == 1


*drop schools that are closed or inactive
drop if school_status == 2 | school_status == 6
* drop schools that are classified as future aka scheduled to be operational in 2 years
drop if school_status == 7


* drop middle, high, and secondary schools
drop if school_level == 3 | school_level == 2 | school_level == 7

* drop prekindergarten
drop if school_level == 0
drop if highest_grade_offered == -1

*only keep schools with 3rd grade
drop if lowest_grade_offered > 3
drop if highest_grade_offered < 3

* drop charter and magnet schools
drop if charter == 1
drop if magnet == 1
* make the school name lowercase
replace school_name = strlower(school_name)
* drop suspected charter/magnet/special schools based on the school name
drop if strpos(school_name,"magnet")>0
drop if strpos(school_name,"charter")>0
drop if strpos(school_name,"math")>0
drop if strpos(school_name,"science")>0
drop if strpos(school_name,"stem")>0
drop if strpos(school_name,"steam")>0
drop if strpos(school_name,"art")>0
drop if strpos(school_name,"leadership")>0
drop if strpos(school_name,"leaders")>0
drop if strpos(school_name,"academy")>0
drop if strpos(school_name,"traditional")>0
drop if strpos(school_name,"technology")>0
drop if strpos(school_name,"tech")>0
drop if strpos(school_name,"deaf")>0
drop if strpos(school_name,"blind")>0
drop if strpos(school_name,"montessori")>0
drop if strpos(school_name,"spanish")>0
drop if strpos(school_name,"immersion")>0
drop if strpos(school_name,"bilingual")>0
drop if strpos(school_name,"virtual")>0
drop if strpos(school_name,"career")>0
drop if strpos(school_name,"alternative")>0
drop if strpos(school_name,"exploratory")>0

* keep only regular schools (drop special ed, vocational, other/alternative schools)
keep if school_type == 1 

* drop if the school is virtual (so SAB would not matter)
drop if virtual == 1
drop virtual

rename enrollment totenrollment 

** save as a working data set
save output/dta/ccddirectoryworking.nvc.dta, replace