qd2hp
======

qdoas to harp tool

.. code-block:: none

  Usage:
      qd2hp  [options] <qdoasfile> 
	      Convert a qdoas file <qdoasfile> into one or several harp compliant format. 
          Options:
			  --outdir directory where to put the output

			  --jsonfile json file that contains the mapping of variables from qdoas to harp variables names.

			  --slcol provide mapping for (multiple) absorbers of interest. e.g: 'ch2o = HCHO ' 'so2 = SO2'
			          on the left side of each expression, the qdoas symbol is written and correspond to a molecule symbol given in
					  http://stcorp.github.io/harp/doc/html/conventions/variable_names.html (see section supported species)
