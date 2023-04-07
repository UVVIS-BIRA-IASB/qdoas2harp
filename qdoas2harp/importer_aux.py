#!/space/hpc-apps/bira/19i/py36/bin/python3
import IPython
import harp #module load 19g/py37
import harp._harppy as harppy
import numpy as np
import numpy.ma as ma
import netCDF4 as nc
import datetime as dt
import glob
import os,sys
import subprocess
import re
from dateutil.rrule import rrule, DAILY
import collections
import shutil
from datetime import date
import time
import argparse
from . import nctools as nct
import harp 


MOLEC_L2={'hcho':'L2__HCHO__'}


def cml():
    '''entry_point used as a cml argument printing the correspoding cloud file from the L1 file that was used''' 
    helpstr='print which aux. data can be added together with the corresponding file'
    parser = argparse.ArgumentParser(description='give L1 file')
    # parser.add_argument('-file', dest='file', action='store', required=True,help=helpstr, default=None)
    parser.add_argument(dest='l2file',help="adding cloud parameters")
    parser.add_argument('-n','--dry-run',action="store_true",help="see what the importer would be doing")

    parser.add_argument('-molec',dest='molec',help="trace gas molecule")
    parser.add_argument('-auxdir',dest='auxdir',help="dir where aux. file is in",default=None)


    args=parser.parse_args()
    l2file=args.l2file 
    auxdir=args.auxdir
    molec=args.molec
    assert molec in MOLEC_L2.keys()
    if os.path.isdir(l2file):
        if args.dry_run:
            print("Aux. file that will be used for l2file :\n ")
        for l2f in glob.glob(l2file+"/*"):
            if args.dry_run:
                 print("{} ----> {}".format(l2f,give_auxfilename(l2f,molec)))
            else:
                assert len(glob.glob(auxdir+"/"+give_auxfilename(l2f,molec)))==1
                auxfile=glob.glob(auxdir+"/"+give_auxfilename(l2f,molec))[0]
                print("{} ----> {}".format(l2f,auxfile))

                retrieve_auxvars(l2f,auxfile)
    else: #one qdoas l2 file is provided
        if args.dry_run:
            print("Aux. file that will be used for l2file :\n ")
            print("{} ----> {}".format(l2file,give_auxfilename(l2file,molec)))

        else:
            assert len(glob.glob(auxdir+"/"+give_auxfilename(l2file,molec)))==1
            auxfile=glob.glob(auxdir+"/"+give_auxfilename(l2file,molec))[0]
            retrieve_auxvars(l2file,auxfile)
                
            
    
    
def give_auxfilename(l2file,molec):
    
    with nc.Dataset(l2file,'r') as ncfile:
        l1used=ncfile.L1_InputFile
    pp=re.search(r"S5P_(?P<proc>[A-Z]{4})_L1B_RA_BD\d_(?P<start>\d{8}T\d{6})_(?P<end>\d{8}T\d{6})_(?P<orbit>\d{5})_(?P<num>\d{2}).*",l1used)
    proc=pp.group('proc')
    start=pp.group('start')
    end=pp.group('end')
    orbit=pp.group('orbit')
    num=pp.group('num')
    l2filename="S5P_{}_{}_{}_{}_{}_{}_*.nc".format(proc,MOLEC_L2[molec],start,end,orbit,num)
    
    return l2filename
        
        

def retrieve_auxvars(l2file,auxfile):


    with nc.Dataset(l2file,'a') as ncfile:
        #variables to copy from an aux. file to the current existing L2 qdoas file:
        aux_vars=['cloud_fraction','cloud_albedo','cloud_albedo_uncertainty','cloud_fraction_uncertainty','cloud_height','cloud_height_uncertainty','cloud_pressure','cloud_pressure_uncertainty','surface_albedo','surface_altitude','surface_altitude_uncertainty','pressure','surface_pressure','tropopause_pressure','HCHO_volume_mixing_ratio_dry_air_apriori']
        aux_harp=harp.import_product(auxfile)
        assert all([x in aux_harp for x in aux_vars])
        #check if the needed variables are in the imported harp product.  
        #first check if the right dimensions are present:
        if 'vertical' not in ncfile.dimensions.keys():
            ncfile.createDimension("vertical",34)
        for auxvar in aux_vars:
            if auxvar not in ncfile.variables.keys():
                if aux_harp.__getitem__(auxvar).dimension==['time']:
                    varnew=ncfile.createVariable(auxvar,aux_harp.__getitem__(auxvar).data.dtype.char,dimensions=('time'))
                elif aux_harp.__getitem__(auxvar).dimension==['time','vertical']:
                    varnew=ncfile.createVariable(auxvar,aux_harp.__getitem__(auxvar).data.dtype.char,dimensions=('time','vertical'))
                else:
                    assert False, aux_harp.__getitem__(auxvar).dimension
            else:
                varnew=ncfile[auxvar]
            varnew[:]=aux_harp.__getitem__(auxvar).data
    
        
if __name__ == "__main__":
    l2file="/bira-iasb/scratch/jonasv/harpout/S5P_OFFL_L1B_RA_BD3_20180601T034421_20180601T052551_03274_01_010000_20180601T071850_w200_bro_radasref.nc"
    IPython.embed();exit()

         

