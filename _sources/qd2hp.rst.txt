.. _qdref:


qd2hp
======

qdoas to harp tool

.. code-block:: RST

  Usage:
      qd2hp  --outdir --slcol "<qdoas_symbol> = <harp_molecule_name>"   <qdoasfile> [--pixcor <ompixcor>]  

	      Convert a qdoas file <qdoasfile> to a Harp compliant qdoasfile by copying it to the directory <outdir>.
		  Convert all qdoas files in a directory <qdoasdir> to a Harp compliant qdoasfile by copying the files to the directory <outdir>.
		  --outdir directory where to put the output.

		  --slcol provide here a  mapping for the  absorber of interest, e.g: 'ch2o = HCHO ' 'so2 = SO2'
			          on the left side of each expression, the qdoas symbol (for which there exists no naming convention in qdoas) is written and correspond to a molecule symbol given in 
					  http://stcorp.github.io/harp/doc/html/conventions/variable_names.html (see section supported species)
		  

  Examples:

   1) This example convert a S5P qdoas output file:
  
  (venv) : ~>   qd2hp   -outdir ./harp_out/2020/08/10 -fitwin w320_h2co_radasref -slcol "ch2o = HCHO " .//2020/08/10/S5P_RPRO_L1B_RA_BD3_20200810T014139_20200810T032308_14637_03_020100_20220707T114433.nc 

  Note that year/month/day directories for the output have to be created before using qd2hp, otherwise it will fail. 
  
   2) example for an OMI qdoas output file:
	  (venv) : ~>   qd2hp   -outdir ./harp_out/2022/01/02 -slcol "ch2o = HCHO " ./2022/01/02/OMI-Aura_L1-OML1BRUG_2022m0102t0142-o92906_v003-2022m0102t071548.nc  -fitwin 'w200' -pixcor
	  ./2022/002/OMI-Aura_L2-OMPIXCOR_2022m0102t0142-o92906_v003-2022m0102t072111.he5

	  Note tha the program will fail is not the right (same orbit) file has been provided. The band which is used is read from the qdoas main attributes.  
