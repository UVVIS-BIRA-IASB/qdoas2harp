Create Harp compliant qdoas output.
====================================

Layout of qdoas file
-----------------------

A qdoas file consist typically out of a main group with variables such as geolocations, time, ... . The subgroup contains the results of a doas retrieval.  Note that the name of main and subgroup can be freely chosen in qdoas. 

Below in picture :numref:`qdoasview`  a typical qdoas layout is shown. 

..  figure:: figs/fig1.png
   :name: qdoasview
   :scale: 50 %
   :alt: hdfview of typical qdoas layout
   :align: center

   qdoas view



Qdoas to Harp mapping
----------------------

A first application is to use the HARP functionalities on a qdoas output file. Therefore we perform some simplifications:

* We split the subgroup into separate files and copy the output in another directory with a filename that gets the suffix of the original qdoas file.  
* geolocations are kept in every output file. A harp  variable is created according to the conventions specified in http://stcorp.github.io/harp/doc/html/conventions/variable_names.html. 
* One Slant column of interest is chosen. (see :ref:`qdref` for how this is done in practice). Currently only one slant column is kept, because the retrieval focuses in most cases on one single
  absorber. Also,  since the calculation of the AMF depends on the absorber, we choose to process AMF and VCD only for one slant column  present in each output file. Note that easily multiple output
  files can be generated which differ in the absorber that is chosen.  

  
.. include::
   mapping.rst


   
