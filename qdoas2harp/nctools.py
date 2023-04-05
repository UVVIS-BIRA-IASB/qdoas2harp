#!/usr/bin/env python3.5
import os,sys,shutil
import datetime as dt  # Python standard library datetime  module
import numpy as np
#numpy.dtype
import numpy.ma as ma
# from h5py import *
import netCDF4
from netCDF4 import *  # http://code.google.com/p/netcdf4-python/
from numpy import arange, dtype # array module from http://numpy.scipy.org
#import cdltocode
import types
import errno
import glob
import collections
import IPython
import pdb

    
def makemasked(arr):
    if type(arr) == ma.core.MaskedArray:
        # IPython.embed();exit()
        return np.where(arr.mask==np.bool_(True),np.nan,arr)
    
    else: return arr


def listallgroups(file):
 
    if( isinstance(file,str)):
        if (not  os.path.exists(file)): # check if the file exists.
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
        try:
            datset= Dataset(file,'r',format="netCDF4")
        except:
            print("cannot open file")
            datset.close()
            assert 0
    else:
        datset=file

    varlist=[]             
    for var in __walktree__(datset):
        for var2 in var:
            varlist.append(var2.path)
            for varr in var2.groups:
                varlist.append(var2.path+"/"+varr)
    datset.close()

    return  varlist


    

def listallvar(file):
    ''' this function list all variables in a netcdf4 file '''

    if (not  os.path.exists(file)): # check if the file exists. 
        print("no netcdf4 file :" + file + '\n')
        assert 0
    
    try:
        datset= Dataset(file,'r',format="netCDF4")
    except:
        print("cannot open file")
        assert 0
    varlist=[]
    for var in __walktree__(datset):
        # pdb.set_trace()
        # print(var)
        for var2 in var:
            for varr in var2.variables:
                varlist.append(var2.path+"/"+varr)
    datset.close()
    if datset.groups==collections.OrderedDict():
        assert len(varlist)==0
        varlist=list(datset.variables.keys())
    return  varlist



                        
  
def __walktree__(top):
    values = top.groups.values()
    yield values
    for value in top.groups.values():
        for children in __walktree__(value):
            yield children
    
    
