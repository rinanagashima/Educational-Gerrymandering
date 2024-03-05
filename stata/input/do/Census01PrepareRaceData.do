** This file cleans the US Census 2010 race and ethnicity data at the block level

* change working directory
cd "${dir}/input/raw data/04 - Arizona"


* import data file
clear
import delimited "04_census10_nonhispwhite.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under non hispanic white var
rename v4 whitepop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile white
save `white'


* import data file
clear
import delimited "04_census10_black.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under black var
rename v4 blackpop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile black
save `black'



* import data file
clear
import delimited "04_census10_asian.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under asian var
rename v4 asianpop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile asian
save `asian'




* import data file
clear
import delimited "04_census10_hispanic.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under hispanic var
rename v4 hispanicpop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile hispanic
save `hispanic'



* import data file
clear
import delimited "04_census10_multirace.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under multirace var
rename v4 multiracepop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile multirace
save `multirace'




* import data file
clear
import delimited "04_census10_nativeamerican.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under nativeamerican var
rename v4 nativeamericanpop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile nativeamerican
save `nativeamerican'



* import data file
clear
import delimited "04_census10_nhpi.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under nhpi var
rename v4 nhpipop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile nhpi
save `nhpi'



* import data file
clear
import delimited "04_census10_otherrace.csv", rowrange(2:)

rename v1 geoid

* drop the geographic area name
drop v2

* drop total pop and tot pop 18 years and over
drop v3 v5

* 18 and under otherrace var
rename v4 otherracepop

* drop v6 which was an extra column created by import error (alll missing obs)
drop v6

* drop first row, which accidentally took header text from the csv file and turned it into an obs
drop if geoid == "Geography"

* keep only the part of the geoid var that correspond to a geoid
replace geoid = substr(geoid,10,.)

tempfile otherrace
save `otherrace'



* merge them together
merge 1:1 geoid using `nhpi'
drop _merge
merge 1:1 geoid using `nativeamerican'
drop _merge
merge 1:1 geoid using `multirace'
drop _merge
merge 1:1 geoid using `hispanic'
drop _merge
merge 1:1 geoid using `asian'
drop _merge
merge 1:1 geoid using `black'
drop _merge
merge 1:1 geoid using `white'
drop _merge

* convert vars from string to integers
destring otherracepop-whitepop, replace

* now, turn race integers into percentages
gen totalpop = otherracepop + nhpipop + nativeamericanpop + multiracepop + hispanicpop + asianpop + blackpop + whitepop

/*foreach race in otherrace nhpi nativeamerican multirace hispanic asian black white {
	gen `race'perc = `race'pop/totalpop
	replace `race'perc = 0 if `race'perc == .
} 

* drop race count vars since we now have race perc vars
drop otherracepop-whitepop */

save "${dir}\urbaninst\output\dta\mergedcensusracedata_az.nvc.dta", replace

