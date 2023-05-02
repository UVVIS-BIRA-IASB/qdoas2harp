Usage
=====

The usefullness of this tool is to prepare an output file which is harp compliant and that can be used for further processing with Harp. 
BeAMF tool, which completes the file further with an AMF and a corresponding VCD.

The aim of the qdoas2harp tool is to facilitate the post processing of a qdoas file. Many functionalities of HARP can be used on such a harp compliant output format. One very useful scenario is when
one want to do some gridding on a qdoas file. Moreover many L2 formats can already be converted to such a Harp format.  A second use is to compose a file that is ingestable by the BeAMF tool. 


Installation
------------

To use qdoas2harp, first install it using pip, for example in a virt. env. called .venv: 

.. code-block:: none

   (.venv) $ git clone https://github.com/UVVIS-BIRA-IASB/qdoas2harp
   (.venv) $ cd qdoas2harp
   (.venv) $ pip install . 
