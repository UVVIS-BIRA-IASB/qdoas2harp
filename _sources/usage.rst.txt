Overview
========

The aim of the qdoas2harp tool is to facilitate the post processing of a qdoas file. Many functionalities of HARP can be used on such a harp compliant output format. One very useful scenario is when
one want to do some gridding on a qdoas file. Moreover many L2 formats can already be converted to such a Harp format.
The functionality of this qdoas2harp package consist out of :

* Converting a qdoas file into a harp compliant file. This new file will contain the geolocations and the slant columnn of interest. Many variables which are related to the retrieval are not
  included. Some important metadata (sensor, L1 data file, ) is also added in the output. This functionality is described in :ref:`ref1` 
* Starting from this harp qdoas file we can easily add auxiliary info, see :ref:`ref2`. This output file is then in a suitable format for the BeAMF tool (https://uvvis-bira-iasb.github.io/BeAMF/),
  which can calculate an AMF and a corresponding vertical
  column.
* Instructions on the theory behind the conversion to a qdoas harp output file, can be found in :ref:`ref1`
* Currently conversion of the output for   GOME-2A, B and C, OMI and tropomi sensors are implemented, but in the future additional instruments can be easily added.
* The use of the command line tools are described in :ref:`ref_cml`
* A python interface (which has contains the same functionality as the command line tools) can be found in :ref:`ref_py`



Installation
------------

To use qdoas2harp, first install it using pip, for example in a virt. env. called .venv: 

.. code-block:: none

   (.venv) $ git clone https://github.com/UVVIS-BIRA-IASB/qdoas2harp
   (.venv) $ cd qdoas2harp
   (.venv) $ pip install .

Note that a recent version of pip (for example 23.1.2) may be needed. 

A recent qdoas version (>= 3.5.1)  is needed. Currently qdoas 3.5.1 is not yet released, but a qdoas version from commit number d1c582178... on github should work. (https://github.com/UVVIS-BIRA-IASB/qdoas) 
