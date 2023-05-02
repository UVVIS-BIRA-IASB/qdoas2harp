
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
      - attributes
      - input file + group
   - 

      - LoS ZA
      - sensor_zenith_angle
      - units=degree
      - qdoas main group
   - 

      - SlCol(<absorber>)
      - <absorber>_column_number_density
      - units=molecules cm-2
      - qdoas subgroup
   - 

      - SlErr(<absorber>)
      - <absorber>_column_number_density
      - units=molecules cm-2
      - qdoas subgroup
   - 

      - Latitude
      - latitude
      - units=degree_north
      - qdoas main group
   - 

      - Longitude
      - Longitude
      - units=degree_east
      - qdoas main group
   - 

      - LoS Azimuth
      - sensor_azimuth_angle
      - units=degree
      - qdoas main group
   -

	  - Date & time \(YYYYMMDDhhmmss\)
	  - datetime_start
	  - units=seconds since 2010\-01\-01
	  - qdoas main group


