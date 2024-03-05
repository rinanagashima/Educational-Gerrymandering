*this file will download the education data package
*updated 10/11/23
cd "${dir}"

*make output directories
cap mkdir output
cap mkdir  output/dta

*IPEDS data from Urban Institute
*This do file downloads and assembles school-level data from the Urban Institute API

*Get raw data from UI endpoint
*do urbaninst/input/do/01UISaveRawData.do

* Process ccd directory data (fte teachers, school location)
do input/do/Urban02PrepareCCDDirectoryData.do

* Process Common Core Data enrollment by race and grade data
do input/do/Urban03PrepareCCDEnrollmentData.do

* Process in crdc data on the number of fte teachers and staff at each school
do input/do/Urban04PrepareCRDCTeachersStaffData.do

* Process the meps school poverty measure data
do input/do/Urban05PrepareMEPSSchoolPovertyData.do

* Process in the schools merged with 2010 census geography variables
do input/do/Urban06PrepareSchoolMergedWithCensusGeographies.do

* Merge data from Urban02-Urban06 do files
do input/do/Urban07Merge02-06.do