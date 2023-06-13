.. _ref2:
Adding auxiliary information.
=============================


Further processing tools, like the BeAMF require some additional auxiliary data, which can be derived from external databases. For example the interpolation of the surface albedo climatology, 
meteorological input data, cloud height, ....  to the appriopriate pixel coordinates.  Since  cloud, albedo and other information is often already available in currrent operational L2 datafiles, this 'importer' tool
retrieves this data from existing L2 files.     



Current limitations
--------------------
This software tool can be applied only for S5P qdoas output format. Currently only HCHO is supported. 

Variables that are imported for a S5P HCHO product.
----------------------------------------------------

The operational S5P HCHO L2 file is imported with Harp and then the following Harp variable are added to the qdoas HCHO product. (see http://stcorp.github.io/harp/doc/html/ingestions/S5P_L2_HCHO.html )

* cloud_fraction
* cloud_albedo
* cloud_albedo_uncertainty
* cloud_fraction_uncertainty
* cloud_height
* cloud_height_uncertainty
* cloud_pressure
* cloud_pressure_uncertainty
* surface_albedo
* surface_altitude
* surface_altitude_uncertainty
* pressure
* surface_pressure
* tropopause_pressure
* HCHO_volume_mixing_ratio_dry_air_apriori


