.. _qdref:


qd2hp
======

qdoas to harp tool

.. code-block:: RST

  Usage:
      qd2hp  --outdir --slcol <qdoasfile | qdoasdir> 

	      Convert a qdoas file <qdoasfile> to a Harp compliant qdoasfile by copying it to the directory <outdir>.
		  Convert all qdoas files in a directory <qdoasdir> to a Harp compliant qdoasfile by copying the files to the directory <outdir>.
		  --outdir directory where to put the output.

		  --slcol provide here a  mapping for the  absorber of interest, e.g: 'ch2o = HCHO ' 'so2 = SO2'
			          on the left side of each expression, the qdoas symbol (for which there exists no naming convention in qdoas) is written and correspond to a molecule symbol given in 
					  http://stcorp.github.io/harp/doc/html/conventions/variable_names.html (see section supported species)
		  

  Examples:
          qd2hp  ./input/2022/07/01/S5P_RPRO_L1B_RA_BD3_20220701T010600_20220701T024730_24426_03_020100_20230104T141055.nc -outdir ./output/2022/07/01/ --slcol 'ch2o=HCHO'
	  


				
				



  
