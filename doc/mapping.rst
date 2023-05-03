
.. _mappingref:

Mapping of qdoas names
------------------------

We list the cases where a general mapping can be done from qdoas to harp
variables. 



.. list-table::
   :header-rows: 1

   - 

      - original name
      - harp name
      - unit attribute
      - qdoas group
  
   - 

      - SlCol(<absorber>)
      - <absorber>_column_number_density
      - molecules cm-2
      - qdoas subgroup
   - 

      - SlErr(<absorber>)
      - <absorber>_column_number_density_uncertainty
      - molecules cm-2
      - qdoas subgroup
   - 

      - Latitude
      - latitude
      - degree_north
      - qdoas main group
   - 

      - Longitude
      - Longitude
      - degree_east
      - qdoas main group
   -
   
	  - Pixel corner latitudes
	  - latitude_bounds
	  - degree_north
	  - qdoas main group
   -
   
	  - Pixel corner longitudes
	  - longitude_bounds
	  - degree_east
	  - qdoas main group
   -
   

      - LoS Azimuth
      - sensor_azimuth_angle
      - units=degree
      - qdoas main group
   - 

      - LoS ZA
      - sensor_zenith_angle
      - degree
      - qdoas main group
   - 

      - SZA
      - solar_zenith_angle
      - degree
      - qdoas main group
   -

	  - Solar Azimuth Angle
	  -	solar_azimuth_angle
	  - degree
	  - qdoas main group
   -

	  - Date & time \(YYYYMMDDhhmmss\)
	  - datetime_start
	  - seconds since 2010\-01\-01
	  - qdoas main group


SlCol(<absorber>), SlErr(<absorber>) is the main retrieved slant column of interest. Other slant columns from (pseudo-) absorbers are use in the fitting procedure, but are excluded in the conversion to a qdoas harp
format. 
