import os,sys
import numpy as np
import numpy.ma as ma
import netCDF4 as nc

    
def makemasked(arr):
    if type(arr) == ma.core.MaskedArray:
        return np.where(arr.mask==np.bool_(True),np.nan,arr)
    else: return arr


def listallgroups(file):
    if (not  os.path.exists(file)): # check if the file exists.
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)
    try:
        ncfile= Dataset(file,'r',format="netCDF4")
    except:
        assert 0,"Cannot open file"
    varlist=[]             
    for var in __walktree__(ncfile):
        for var2 in var:
            varlist.append(var2.path)
            for varr in var2.groups:
                varlist.append(var2.path+"/"+varr)
    ncfile.close()
    return  varlist


    

def listallvar(file):
    ''' this function list all variables in a netcdf4 file '''
    if (not  os.path.exists(file)): # check if the file exists. 
        print("no netcdf4 file :" + file + '\n')
        assert 0
    try:
        ncfile= Dataset(file,'r',format="netCDF4")
    except:
        assert 0,"Cannot open file"
    varlist=[]
    for var in __walktree__(datset):
        for var2 in var:
            for varr in var2.variables:
                varlist.append(var2.path+"/"+varr)
    ncfile.close()
    if ncfile.groups==collections.OrderedDict():
        assert len(varlist)==0
        varlist=list(datset.variables.keys())
    return  varlist



                        
  
def __walktree__(top):
    values = top.groups.values()
    yield values
    for value in top.groups.values():
        for children in __walktree__(value):
            yield children
    
    
