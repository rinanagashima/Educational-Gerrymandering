** This file cleans the school merged with census geographies data from the Urban Institute endpoint and saves it as a working data set

* This endpoint contains geographic variables corresponding to 2010 Census geographies for each school in the CCD directory. Geographies are merged on by latitude and longitude when available; when unavailable, latitudes and longitudes were obtained from address information using Urban's geocoder. The geocoder uses StreetMap Premium from Esri to perform accurate offline geocoding. Geocode accuracy variables indicate the degree of precision of this geocoding. Additional information on the match accuracy can be found here. Geographies for older years of data or low-accuracy geocode matches should be used with caution. In addition, we link schools' geographic locations to the geographic boundaries of school districts.


* Change to working directory
cd "${dir}"

* Read in data
clear
use "output/dta/schoolcensus2010raw.nvc.dta"

keep if year==2016

* drop irrelevant geographic variables
drop census_region
drop census_division
drop street_location
drop county_code
drop county_fips
drop csa cbsa cbsa_name 
drop place_fips geoid_place place_name
drop class_code 

* drop location vars
drop city_location-zip_location

* drop mailing address
drop street_mailing
drop city_mailing
drop state_mailing
drop zip_mailing


* drop legislative districts
drop state_leg_district_upper-lower_chamber_type
drop congress_district_id

** save as a working data set
save output/dta/schoolcensus2010working.nvc.dta, replace
