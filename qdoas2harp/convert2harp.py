import harp
import numpy as np
import netCDF4 as nc
import datetime as dt
import glob
import os,sys
import re
from datetime import date
import time
import argparse
from . import nctools 
from .qd2hp_mapping import qd2hp_mapping



class Dataset(nc.Dataset): #https://github.com/Unidata/netcdf4-python/issues/785
        def __init__(self, *args, **kwargs):
            super(Dataset, self).__init__(*args, **kwargs)
            self.set_auto_mask(True)
 

def cml():
    '''entry_point used as a cml argument for input qdoas filename and will generate an output filename '''
    helpstr='qdoas output file' 
    parser = argparse.ArgumentParser(description='give L1 file')
    # parser.add_argument('-file', dest='file', action='store', required=True,help=helpstr, default=None)
    parser.add_argument( dest='qdoasfile',help="qdoas file to be converted to harp compliant file")
    parser.add_argument('-outdir',dest='outdir',help="harp compliant qdoas output files per fitting window",required=True)
    parser.add_argument('-slcol', nargs=1,required=True)
    args=parser.parse_args()
    qdoasfile=args.qdoasfile
    outdir=args.outdir
    slcol=args.slcol
    slcol_dict={}
    for x in slcol:
        assert re.search("\s*(\S*)\s*=\s*(\S*)\s*",slcol[0])!=None, "check input of -slcol option"
        slcol_dict[re.search("\s*(\S*)\s*=\s*(\S*)\s*",x).group(1)]=re.search("\s*(\S*)\s*=\s*(\S*)\s*",x).group(2)
    assert os.path.isdir(outdir)
    if os.path.isdir(qdoasfile):
        #process all files in the given directory
        for fileqd in glob.glob(qdoasfile+"/*"):
            assert fileqd[-2:]=="nc"
            makeharp(fileqd,outdir,slcol_dict)
    else:
        assert qdoasfile[-2:]=="nc"
        makeharp(qdoasfile,outdir,slcol_dict)

    

def makeharp(qdfile,outdir,slcol_dict):
    groups=[ x for x in  list(set(nctools.listallgroups(qdfile))) ]
    maingroups=[x.split('/')[1] for x in groups]
    maingroup=maingroups[0]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    subgroups=[x.split('/')[2] for x in groups if x.count('/')==2]
    calibgroups=[x.split('/')[3] for x in groups  if x.count('/')==3]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    assert np.all(['Calib'==x for x in calibgroups]) or len(calibgroups==0)
    for fitwin in subgroups:
        harpout=outdir+re.sub(r'.*/([^.]+)(.*)',r'/\1_{}\2'.format(fitwin),qdfile)
        with Dataset(qdfile,'r') as ncqdoas:
            fitgr="/"+maingroup+"/"+fitwin+"/"
            maingr="/"+maingroup+"/"
            mainvars=[maingr+x for x in  ncqdoas[maingr].variables.keys()]
            fitvars=[fitgr+x for x in  ncqdoas[fitgr].variables.keys()]
            dd=qd2hp_mapping(mainvars+fitvars,slcol_dict)
            create_ncharpvar(dd,ncqdoas,harpout)
            export_metadata(ncqdoas,maingr, harpout)


        
def export_metadata(ncqdoas,maingr,harpout):
    #export some main attributes that cannot be added with a harp export command. 
    with nc.Dataset(harpout,'a') as ncharp:
        ncharp.L1_InputFile=ncqdoas[maingr].InputFile.split('/')[-1]


    
        
def create_ncharpvar(dd,ncqdoas,output_filename):
    product = harp.Product()
    for qdvar in dd.keys():
        hpobj=dd[qdvar]
        hpvar=harp.Variable(hpobj.harpname)
        assert ncqdoas[qdvar].dtype.char in ['f','d','h','s','b','B','c','i','l','H','I']
        if ncqdoas[qdvar].dtype.char in ['f','d']:#needs conversion of fillvalues to nan
            if ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack'):
                dimensions=["time"]
                nanvar=nctools.makemasked(ncqdoas[qdvar][:].flatten()).astype('f',casting='same_kind')
            elif ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack','4'):
                dimensions=["time",None]
                nanvar=nctools.makemasked(ncqdoas[qdvar][:].reshape(-1,4)).astype('f',casting='same_kind')
            hpvar=harp.Variable(nanvar,dimensions, unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description , enum=None)
        else: #non floating point, integer point:
            if ncqdoas[qdvar].dimensions==('n_alongtrack','n_crosstrack'):
                datatype=ncqdoas[qdvar].dtype.char
                if ncqdoas[qdvar].dtype.char=='H':
                    datatype='h'
                nchpvar[:]=ncqdoas[qdvar][:].flatten()
                hpvar=harp.Variable(nchpvar,['time'], unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description, enum=None)

            elif hpobj.harpname=="datetime_start": #exception for times. 
                assert ncqdoas[qdvar].dimensions==('n_alongtrack', 'n_crosstrack','datetime')
                tt=nctools.makemasked(ncqdoas[qdvar][:])
                #bug in qdoas that some times are fillvalues for some rows>0, temporary solution is to take the times from rows=0, since times for all rows is the same. 
                idxnan=np.nonzero(np.isnan(tt))
                if idxnan:
                    idxnan2=(idxnan[0],np.zeros((len(idxnan[1]),),dtype=np.int32),idxnan[2])
                    tt[idxnan]=tt[idxnan2]
                tt=tt.reshape(-1,ncqdoas[qdvar].shape[-1])
                #end of bug fix from qdoas
                arr=np.full((tt.shape[0],),np.nan,dtype='d')
                for j in range(0,tt.shape[0]):
                    bb=[ int(tt[j,i]) for i in range(0,7)]
                    #WARNING ref. time should be taken from the units attr.
                    reftimestr=re.search("\d{4}-\d{2}-\d{2}",hpobj.units).group(0)
                    assert reftimestr!=None, "check reference time format"
                    reftime=dt.datetime.strptime(reftimestr,"%Y-%m-%d")
                    arr[j]=(dt.datetime(*bb)-reftime).total_seconds()
                    assert arr[j]>0, "reference time too late"
                arr=arr.astype('d',casting='same_kind')
                hpvar=harp.Variable(arr,['time'], unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description, enum=None)
            else:
                assert 0, "unknown variable for this  conversion"
            
        obj=setattr(product,dd[qdvar].harpname,hpvar) #add harp variables as attribute to harp product.
    harp.export_product(product,output_filename , file_format='hdf5', hdf5_compression=6)
        
    
            
     



         

