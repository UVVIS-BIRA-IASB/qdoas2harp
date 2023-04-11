.. contents::
   :depth: 2


.. _mappingref:

Mapping of qdoas names
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
  


The aim of the qdoas2harp tool is to facilitate the post processing of a qdoas file. Many functionalities of HARP can be used on such a harp compliant output format. One very useful scenario is when
one want to do some gridding on a qdoas file. Moreover many L2 formats can already be converted to such a Harp format.  Also, the BeAMF tool assumes that an input file is in the Harp format. 
