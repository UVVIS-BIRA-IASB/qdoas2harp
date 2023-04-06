.. contents::
   :depth: 2
..

Qdoas to Harp Variables
=======================


We list the cases where a general mapping can be done from qdoas to harp
variables.
per fitting window a separate harp compliant file is created. 

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

      - SlCol(ch2o)
      - tropospheric_HCHO_column_number_density
      - units=molecules cm-2
      - qdoas subgroup
   - 

      - SlCol(no2)
      - tropospheric_NO2_column_number_density
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

      - None
      - relative_azimuth_angle
      - units=degree
      - Harp Variable conversion

