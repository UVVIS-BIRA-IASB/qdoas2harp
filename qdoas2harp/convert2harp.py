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
from attrs import define, frozen, Attribute, field


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
            qdoas1=makeharp(fileqd,slcol_dict)
            qdoas1.print_product(outdir)
    else:
        assert qdoasfile[-2:]=="nc"
        qdoas1=makeharp(qdoasfile,slcol_dict)
        qdoas1.print_product(outdir)
   

@define(repr=False,slots=False)
class qdoas_fitwin:
    #add dynamical harp product as attribute for fitwin variables
    # win_name: float=field()
    win_down:float=field()
    win_up: float=field()
    product: field()
    


@define(repr=False,slots=False)
class qdoas_harp:
    #add dynamical harp product as attribute  for main variables. 
    qdoasfile:str =field()
    l1file:str=field(default=None)
    product=field(default=None)
    
    def print_product(self,outdir):
        for k in self.__dict__.keys():
            if type(self.__dict__[k]).__name__=='qdoas_fitwin':
                harpout=outdir+re.sub(r'.*/([^.]+)(.*)',r'/\1_{}\2'.format(k),self.qdoasfile)
                output_product=harp.Product()
                for x in  self.product:
                    setattr(output_product,x,self.product[x])
                for x in getattr(self,k).product:
                    setattr(output_product,x,getattr(self,k).product[x])
                harp.export_product(output_product,harpout , file_format='hdf5', hdf5_compression=6)

        
def makeharp(qdfile,slcol_dict):
    groups=[ x for x in  list(set(nctools.listallgroups(qdfile))) ]
    maingroups=[x.split('/')[1] for x in groups]
    maingroup=maingroups[0]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    subgroups=[x.split('/')[2] for x in groups if x.count('/')==2]
    calibgroups=[x.split('/')[3] for x in groups  if x.count('/')==3]
    assert np.all([maingroup==x.split('/')[1] for x in groups])
    assert np.all(['Calib'==x for x in calibgroups]) or len(calibgroups==0)
    
    with Dataset(qdfile,'r') as ncqdoas:
        maingr="/"+maingroup+"/"
        mainvars_in_qdoas=[maingr+x for x in  ncqdoas[maingr].variables.keys()]
        main_vars_mapping=qd2hp_mapping(mainvars_in_qdoas,slcol_dict)
        qdoas1=qdoas_harp(qdfile,ncqdoas[maingr].InputFile.split('/')[-1],create_harp_product(main_vars_mapping,ncqdoas))
        for fitwin in subgroups:
            fitgr=maingr+fitwin+"/"
            fit_vars=[fitgr+x for x in  ncqdoas[fitgr].variables.keys()]
            fit_vars_mapping=qd2hp_mapping(fit_vars,slcol_dict)
            qdoas_fitwin1=qdoas_fitwin(0.0,0.0,create_harp_product(fit_vars_mapping,ncqdoas))
            setattr(qdoas1,fitwin,qdoas_fitwin1) # set attribute field with harp product.
    return qdoas1

    
def get_metadata(ncqdoas,maingr):
    #export some main attributes that cannot be added with a harp export command. 
    with nc.Dataset(harpout,'a') as ncharp:
        L1_InputFile=ncqdoas[maingr].InputFile.split('/')[-1]
    return L1_InputFile

    
        
def create_harp_product(dd,ncqdoas):
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
            
        setattr(product,dd[qdvar].harpname,hpvar) #add harp variables as attribute to harp product.
    return product
        
    
            
     



         

