#!/space/hpc-apps/bira/19i/py36/bin/python3
import IPython
import harp #module load 19g/py37
import harp._harppy as harppy
import numpy as np
import numpy.ma as ma
import netCDF4
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
from .qd2hp_mapping import qd2hp_mapping

#calib group is excluded. 

# qd_dim={'scanlines':'n_alongtrack','rows':'n_crosstrack'}




class Dataset(netCDF4.Dataset): #https://github.com/Unidata/netcdf4-python/issues/785
        def __init__(self, *args, **kwargs):
            super(Dataset, self).__init__(*args, **kwargs)
            self.set_auto_mask(True)
 

def cml():
    '''entry_point used as a cml argument for input qdoas filename and will generate an output filename '''
    helpstr='qdoas output file'
    parser = argparse.ArgumentParser(description='give L1 file')
    # parser.add_argument('-file', dest='file', action='store', required=True,help=helpstr, default=None)
    parser.add_argument('-qdoasfile',dest='qdoasfile',help="qdoas file to be converted to harp compliant file")
    parser.add_argument('-jsonfile')

    args=parser.parse_args()
    qdoasfile=args.qdoasfile
    jsonfile=args.jsonfile

    makeharp(qdoasfile,jsonfile)

    

def makeharp(qdfile,jsonfile):
    groups=[ x for x in  list(set(nct.listallgroups(qdfile))) ]
    # group name Calib is fixed in qdoas, see engine/output_netcdf.cpp:31:const static string calib_subgroup_name = "Calib";
    maingroups=[x.split('/')[1] for x in groups]
    maingroup=maingroups[0]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    subgroups=[x.split('/')[2] for x in groups if x.count('/')==2]
    calibgroups=[x.split('/')[3] for x in groups  if x.count('/')==3]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    assert np.all(['Calib'==x for x in calibgroups]) or len(calibgroups==0)
    for fitwin in subgroups:
        qdoas_meta=get_qdoasmeta(qdfile,maingroup)
        harpout=re.sub(r'.*/([^.]+)(.*)',r'\1_{}\2'.format(fitwin),qdfile)
        # IPython.embed();exit()
        with Dataset(qdfile,'r') as ncqdoas, Dataset(harpout,'w') as ncharp:
            fitgr="/"+maingroup+"/"+fitwin+"/"
            maingr="/"+maingroup+"/"
            mainvars=[maingr+x for x in  ncqdoas[maingr].variables.keys()]
            fitvars=[fitgr+x for x in  ncqdoas[fitgr].variables.keys()]
            time_scans=qdoas_meta['scanlines']*qdoas_meta['rows']
            time=ncharp.createDimension("time",time_scans)
            if '4' in ncqdoas[maingr].dimensions.keys(): #this corresponds to the independent_4 dim in harp for the ground pixel corners:
                corners=ncharp.createDimension("independent_4",4)

            dd=qd2hp_mapping(jsonfile,mainvars+fitvars)
            # IPython.embed();exit()

            create_ncharpvar(dd,ncqdoas,ncharp)
            create_ncharpattr(ncqdoas,ncharp)


def create_ncharpattr(ncqdoas,ncharp):
    ncharp.Conventions='HARP-1.0'
        
def create_ncharpvar(dd,ncqdoas,ncharp):
    for qdvar in dd.keys():
        hpobj=dd[qdvar]
        assert ncqdoas[qdvar].dtype.char in ['f','d','h','s','b','B','c','i','l','H','I']
        if ncqdoas[qdvar].dtype.char in ['f','d']:#needs conversion of fillvalues to nan
            
            if ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack'):
                nchpvar=ncharp.createVariable(hpobj.harpname,'f8', ("time"),fill_value=False)
                nanvar=nct.makemasked(ncqdoas[qdvar][:].flatten())
            elif ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack','4'):
                # IPython.embed();exit()
                nchpvar=ncharp.createVariable(hpobj.harpname,'f8', ("time","independent_4"),fill_value=False)
                nanvar=nct.makemasked(ncqdoas[qdvar][:].reshape(-1,4))
            
                
            
            if hpobj.comment!=None: nchpvar.comment=hpobj.comment
            if hpobj.descrp!=None: nchpvar.descrpition=hpobj.descrp 
            if hpobj.units!=None: nchpvar.units=hpobj.units 
            nchpvar[:]=nanvar
        else: #non floating point, integer point:
            if ncqdoas[qdvar].dimensions==('n_alongtrack','n_crosstrack'):
                # continue
                datatype=ncqdoas[qdvar].dtype.char
                if ncqdoas[qdvar].dtype.char=='H':
                    datatype='h'
                    # continue
                nchpvar=ncharp.createVariable(hpobj.harpname,datatype, ("time"),fill_value=False)
                nchpvar[:]=ncqdoas[qdvar][:].flatten()
            elif hpobj.harpname=="datetime_start": #exception for times. 
                assert ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack','datetime')
                nchpvar=ncharp.createVariable(hpobj.harpname,'f8', ("time"),fill_value=False)
                tt=nct.makemasked(ncqdoas[qdvar][:]).reshape(-1,ncqdoas[qdvar].shape[-1])
                arr=np.full((tt.shape[0],),None)
                for j in range(0,tt.shape[0]):
                    bb=[ int(tt[j,i]) for i in range(0,7)]
                    #WARNING ref. time should be taken from the units attr. 
                    arr[j]=(dt.datetime(*bb)-dt.datetime(1995,1,1,0,0,0)).total_seconds()+CountLeapSec(*bb[:3],1995)
                    if hpobj.comment!=None: nchpvar.comment=hpobj.comment
                    if hpobj.descrp!=None: nchpvar.descrpition=hpobj.descrp 
                    if hpobj.units!=None: nchpvar.units=hpobj.units 
                nchpvar[:]=arr
            else:
                    assert 0, "unknown variable for this conversion"
            

    
            
            
def get_qdoasmeta(qdoas_l2,maingroup):
    qdoas_meta={}
    maingroup="/"+maingroup+"/"
    with Dataset(qdoas_l2,'r') as ncqdoas:
        
        inputfile=ncqdoas[maingroup].InputFile.split('/')[-1]
        # IPython.embed();exit()
        
        qdoas_meta['scanlines']=ncqdoas[maingroup+'Latitude'][:].shape[0]
        qdoas_meta['rows']=ncqdoas[maingroup+'Latitude'][:].shape[1]

        # qdoas_meta['starttime_granule']=dt.datetime.strptime(datstr,"%Y/%j")
        
        assert np.all(nct.makemasked(ncqdoas[maingroup+'/Orbit number'][:])==nct.makemasked(ncqdoas[maingroup+'/Orbit number'][0,0]))
        qdoas_meta['orbit']=int(nct.makemasked(ncqdoas[maingroup+'/Orbit number'][0,0]))
        

    return qdoas_meta



def CountLeapSec(year,month,day,RefYear):
    '''
     Determine the number of leap seconds since 01 Jan. RefYear and
     the current date.
    '''
    
    t1 = date(RefYear, 1, 1)   # start date
    t2 = date(year,month,day)  # current date
    
    lsdates = [date(1972, 6,30),date(1972,12,31),date(1973,12,31),
               date(1974,12,31),date(1975,12,31),date(1976,12,31),
               date(1977,12,31),date(1978,12,31),date(1979,12,31),
               date(1981, 6,30),date(1982, 6,30),date(1983, 6,30),
               date(1985, 6,30),date(1987,12,31),date(1989,12,31),
               date(1990,12,31),date(1992, 6,30),date(1993, 6,30),
               date(1994, 6,30),date(1995,12,31),date(1997, 6,30),
               date(1998,12,31),date(2005,12,31),date(2008,12,31),
               date(2012, 6,30),date(2015, 6,30),date(2016,12,31)]
    
    nls = 0
    for dls in lsdates:
        if ( dls > t1 ) & ( dls < t2 ):
            nls = nls+1
            
    return nls




         

