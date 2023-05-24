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
    parser.add_argument( dest='qdoasfile',help="qdoas file to be converted to harp compliant file")
    parser.add_argument('-outdir',dest='outdir',help="harp compliant qdoas output files per fitting window",required=True)
    parser.add_argument('-slcol', nargs=1,required=True)
    parser.add_argument('-fitwin',nargs=1,type=str,required=True)

    args=parser.parse_args()
    qdoasfile=args.qdoasfile
    outdir=args.outdir
    slcol=args.slcol[0]
    fitwindow=args.fitwin[0]
   
    assert os.path.isdir(outdir)
    if os.path.isdir(qdoasfile):
        #process all files in the given directory
        for fileqd in glob.glob(qdoasfile+"/*"):
            assert fileqd[-2:]=="nc"
            qdoas_obj=qdoas_harp.create_qd2hp(qdoasfile,slcol,fitwindow)
            qdoas_obj.print_product(outdir)
    else:
        assert qdoasfile[-2:]=="nc"
        qdoas_obj=qdoas_harp.create_qd2hp(qdoasfile,slcol,fitwindow)
        qdoas_obj.print_product(outdir)

   

@define(repr=False,slots=False)
class qdoas_harp:
    '''class that is used for all type of sensors'''
    filename_qdoas:str=field() 
    product: field()
    fitwin_name:str=field()
    fitwin_range: list=field(factory=list)
    l1file:str=field(default=None)
    sensor:str=field(default=None)
        
    @classmethod
    def create_qd2hp(cls,qdoasfile,slcol,fitwin):
        
        with Dataset(qdoasfile,'r') as ncqdoas:
            #read groups from qdoas file and retrieve the desired group. 
            groups=[ x for x in  list(set(nctools.listallgroups(qdoasfile))) ]
            maingroup="/"+[x.split('/')[1] for x in groups][0]+"/" #extract main group. 
            subgroups=[x.split('/')[2] for x in groups if x.count('/')==2]
            assert fitwin in subgroups,"name of fitting window not present"
            fitgroup=maingroup+fitwin+"/"
            calibgroups=[x.split('/')[3] for x in groups  if x.count('/')==3]
            assert np.all(['Calib'==x for x in calibgroups]) or len(calibgroups==0)
            main_variables=[maingroup+x for x in  ncqdoas[maingroup].variables.keys()]
            fit_variables=[fitgroup+x for x in  ncqdoas[fitgroup].variables.keys()]
            slcol_dict={}
            assert re.search("\s*(\S*)\s*=\s*(\S*)\s*",slcol)!=None, "check input of -slcol option"
            slcol_dict[re.search("\s*(\S*)\s*=\s*(\S*)\s*",slcol).group(1)]=re.search("\s*(\S*)\s*=\s*(\S*)\s*",slcol).group(2)
            #read group and main attributes. 
            assert 'fitting window range' in ncqdoas[fitgroup].ncattrs()
            fitwin_range=ncqdoas[fitgroup].getncattr('fitting window range')
            sensor=ncqdoas[maingroup].Sensor
            l1file=ncqdoas[maingroup].InputFile.split('/')[-1]
            variables_mapping=qd2hp_mapping(main_variables+fit_variables,slcol_dict)
            if(sensor=='OMI' or sensor=='TROPOMI'):
                product=create_harp_product_omi_tropomi(variables_mapping,ncqdoas)
            elif(sensor=='GOME-2'):
                product=create_harp_product_gome2(variables_mapping,ncqdoas)
            else:
                assert False, "sensor not know"
                    
        fitup=float(re.search("(\d*\.\d*)\s*\:\s*([\d\.]*)",fitwin_range).group(1))
        fitdown=float(re.search("(\d*\.\d*)\s*\:\s*([\d\.]*)",fitwin_range).group(2))
        
        return qdoas_harp(qdoasfile,product,fitwin ,list([fitup,fitdown]),l1file,sensor)

    def print_product(self,outdir):
        #create an output filename and export with Harp to a netcdf4 file.
        outputfile=outdir+"/"+re.sub(r'.*/([^.]+)(.*)',r'/\1_{}\2'.format(self.fitwin_name),self.filename_qdoas)
        harp.export_product(self.product,outputfile , file_format='hdf5', hdf5_compression=6)
        #Harp doesn't allow to add  attributes, so we add them seperately 
        with Dataset(outputfile,'a') as ncharp:
            ncharp.fitting_window_range=self.fitwin_range
            ncharp.L1_file=self.l1file
            ncharp.sensor=self.sensor
            

def create_harp_product_gome2(mapping,ncqdoas):
    #no n_crosstrack dimension for gome2
    product = harp.Product()
    maingroup=list(ncqdoas.groups.keys())[0]
    for qdvar in mapping.keys():
        hpobj=mapping[qdvar]
        hpvar=harp.Variable(hpobj.harpname)
        assert ncqdoas[qdvar].dtype.char in ['f','d','h','s','b','B','c','i','l','H','I']
        if ncqdoas[qdvar].dtype.char in ['f','d']:#needs conversion of fillvalues to nan
            if ncqdoas[qdvar].dimensions==('n_alongtrack',):
                dimensions=["time"]
                nanvar=nctools.makemasked(ncqdoas[qdvar][:]).astype('f',casting='same_kind')
            elif ncqdoas[qdvar].dimensions==('n_alongtrack','3'):
                dimensions=["time"]
                nanvar=nctools.makemasked(ncqdoas[qdvar][:,1]).astype('f',casting='same_kind')
            elif ncqdoas[qdvar].dimensions==('n_alongtrack','4'):
                dimensions=["time",None]
                assert hpobj.harpname=="latitude_bounds" or hpobj.harpname=="longitude_bounds"
                nanvar=nctools.makemasked(ncqdoas[qdvar][:,[1,3,2,0]]).astype('f',casting='same_kind')
            else:
                assert 0, f"unknown variable {qdvar} for this  conversion"
            hpvar=harp.Variable(nanvar,dimensions, unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description , enum=None)
        else: #non floating point, integer point:
            if ncqdoas[qdvar].dimensions==('n_alongtrack',):
                datatype=ncqdoas[qdvar].dtype.char
                if ncqdoas[qdvar].dtype.char=='H':
                    datatype='h'
                nchpvar[:]=ncqdoas[qdvar][:]
                hpvar=harp.Variable(nchpvar,['time'], unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description, enum=None)
            elif hpobj.harpname=="datetime_start": #exception for times.
                time_hpvar=qdoas_time_harp(ncqdoas[qdvar],hpobj.units)
                hpvar=harp.Variable(time_hpvar,['time'], unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description, enum=None)
            else:
                assert 0, "unknown variable for this  conversion"
            
        setattr(product,mapping[qdvar].harpname,hpvar) #add harp variables as attribute to harp product.
    return product

           
def create_harp_product_omi_tropomi(mapping,ncqdoas):
    product = harp.Product()
    maingroup=list(ncqdoas.groups.keys())[0]
    n_crosstrack_size=ncqdoas[maingroup].dimensions['n_crosstrack'].size
    for qdvar in mapping.keys():
        hpobj=mapping[qdvar]
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
                time_tmp=nctools.makemasked(ncqdoas[qdvar][:])
                #bug in qdoas that some times are fillvalues for some rows>0, temporary solution is to take the times from rows=0, since times for all rows is the same. #also appearing when rows are skipped. 
                #since only a subset of rows is sometimes selected or masked, find the first valid row (this is correct since all rows have the same time) find a row for which all scanlines are valid.
                validrow=[row  for row in range(0,n_crosstrack_size) if np.all(~np.isnan(time_tmp[:,row,:]))][0]
                time= time_tmp[:,validrow,:] #
                #end of bug fix from
                time_harp=qdoas_time_harp(time,hpobj.units)
                tmp=tuple(time_harp for i in range(0,n_crosstrack_size))
                time_harp_var=np.vstack(tmp).flatten(order='F')
                hpvar=harp.Variable(time_harp_var,['time'], unit=hpobj.units, valid_min=hpobj.valid_min, valid_max=hpobj.valid_max, description=hpobj.description, enum=None)
            else:
                assert 0, "unknown variable for this  conversion"
            
        setattr(product,mapping[qdvar].harpname,hpvar) #add harp variables as attribute to harp product.
    return product



    
def qdoas_time_harp(time,reftime):
    '''this function converts qdoas times to seconds since a reference time'''
    arr=np.full((time.shape[0]),np.nan,dtype='d').flatten()

    for j in range(0,time.shape[0]):
        time_harp=[ int(time[j,i]) for i in range(0,7)]
        reftimestr=re.search("\d{4}-\d{2}-\d{2}",reftime).group(0)
        assert reftimestr!=None, "check reference time format"
        refdt_time=dt.datetime.strptime(reftimestr,"%Y-%m-%d")
        arr[j]=(dt.datetime(*time_harp)-refdt_time).total_seconds()
        assert arr[j]>0, "reference time too late"
    return arr
    
    


         

