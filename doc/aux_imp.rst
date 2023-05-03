.. _auxref:


aux_imp
=======

qdoas to harp tool

.. code-block:: RST

  Usage:
      aux_imp    [--auxfile <file> ]  <qdoasfile> 
      
	  
				--auxfile auxiliary file from which variables are taken. When not given the program returns the filename of which aux. file is expected.

  
  Examples:
     put output aux. data in a qdoas file after processing with qd2hp. 


	  aux_imp      ./harp_out/2022/07/01/S5P_RPRO_L1B_RA_BD3_20220701T010600_20220701T024730_24426_03_020100_20230104T141055_w200_bro_radasref.nc 

	  Aux. file that will be used for l2file :
 
	  ./harp_out/2022/07/01/S5P_RPRO_L1B_RA_BD3_20220701T010600_20220701T024730_24426_03_020100_20230104T141055_w200_bro_radasref.nc
	  ----> S5P_RPRO_L2__HCHO___20220701T010600_20220701T024730_24426_03_\*.nc

	  aux_imp     --auxdir ./ESA_HUB/RPRO/HCHO/03_02/2022/07/01/   ./harp_out/2022/07/01/
