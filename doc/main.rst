Qdoas to Harp Variables
=======================

The aim of the qdoas2harp tool is to facilitate the post processing of a qdoas file. Many functionalities of HARP (https://stcorp.github.io/harp/doc/html/index.html) can be used on such a harp compliant output format. One very useful scenario is when
one want to do some gridding on a qdoas file. Moreover many L2 formats can already be converted to such a Harp format.  Also, the BeAMF tool assumes that an input file is in the Harp format.
Below in picture :numref:`qdoasview`  a typical qdoas layout is shown. 

..  figure:: ../figs/fig1.png
   :name: qdoasview
   :scale: 50 %
   :alt: hdfview of typical qdoas layout
   :align: center

   qdoas view

   ::

Steps to evolve to a harp compliant qdoas output:
-----------------------------------------------------------

* Removing hdf5 groups. Thereby splitting the different groups from different fitting windows into multiple files. 
* Squashing pixels from slant columns (typically scanlines x rows) into the time dimension
* Adding main attribute 'HARP-1.0'
* Transform the qdoas variable where a harp equivalent name exists.  (http://stcorp.github.io/harp/doc/html/conventions/variable_names.html and :ref:`mappingref`) 
   



   
