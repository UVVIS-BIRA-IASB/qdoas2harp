'''this module performs the conversion to harp output'''
import datetime as dt
import glob
import os
import re
import argparse
from json import dumps
import harp
import netCDF4 as nc
import numpy as np
from attrs import define, field
from . import nctools
from .qd2hp_mapping import qd2hp_mapping


def cml():
    '''entry_point used as a cml argument for input qdoas filename
    and will generate an output filename '''
    parser = argparse.ArgumentParser(description='give L1 file')
    parser.add_argument(dest='qdoasfile',help="qdoas file to be converted to harp compliant file")
    parser.add_argument('-outdir', dest='outdir',help=
                        "harp compliant qdoas output files per fitting window",required=True)
    parser.add_argument('-slcol', nargs=1,required=True)
    parser.add_argument('-fitwin',nargs=1,type=str,required=True)
    parser.add_argument('-pixcor',type=str)

    args = parser.parse_args()
    qdoasfile = args.qdoasfile
    outdir = args.outdir
    slcol = args.slcol[0]
    fitwindow = args.fitwin[0]
    pixcorfile = args.pixcor
    assert os.path.isdir(outdir)
    if os.path.isdir(qdoasfile):
        # process all files in the given directory
        for fileqd in glob.glob(qdoasfile+"/*"):
            assert fileqd[-2:] == "nc"
            qdoas_obj = qdoas_harp.create_qd2hp(qdoasfile,slcol,fitwindow,pixcorfile=pixcorfile)
            qdoas_obj.print_product(outdir)
    else:
        assert qdoasfile[-2:] == "nc"
        qdoas_obj = qdoas_harp.create_qd2hp(qdoasfile,slcol,fitwindow,pixcorfile=pixcorfile)
        qdoas_obj.print_product(outdir)

@define(repr=False,slots=False)
class qdoas_harp:
    '''class that is used for all type of sensors'''
    filename_qdoas : str = field()
    product: field()
    fitwin_name:str = field()
    fitwin_range: list = field(factory=list)
    l1file: str = field(default=None)
    sensor: str = field(default=None)
    band: str = field(default=None)
    qdoas_version: str = field(default=None)

    @classmethod
    def create_qd2hp(cls, qdoasfile, slcol, fitwin, pixcorfile=None):
        with nc.Dataset(qdoasfile, 'r') as ncqdoas:
            #read groups from qdoas file and retrieve the desired group. 
            groups=list(set(nctools.listallgroups(qdoasfile)))
            maingroup="/"+[x.split('/')[1] for x in groups][0]+"/"  # extract main group. 
            subgroups=[x.split('/')[2] for x in groups if x.count('/') == 2]
            assert fitwin in subgroups,"name of fitting window not present"
            fitgroup=maingroup+fitwin+"/"
            calibgroups=[x.split('/')[3] for x in groups  if x.count('/') == 3]
            assert np.all(['Calib' == x for x in calibgroups]) or len(calibgroups)==0
            main_variables=[maingroup+x for x in ncqdoas[maingroup].variables.keys()]
            fit_variables=[fitgroup+x for x in  ncqdoas[fitgroup].variables.keys()]
            slcol_dict={}
            assert re.search(r"\s*(\S*)\s*=\s*(\S*)\s*", slcol) is not None, \
                "check input of -slcol option"
            slcol_dict[re.search(r"\s*(\S*)\s*=\s*(\S*)\s*",slcol).group(1)]= \
                re.search(r"\s*(\S*)\s*=\s*(\S*)\s*",slcol).group(2)
            #read group and main attributes.
            assert 'fitting window range' in ncqdoas[fitgroup].ncattrs()
            fitwin_range=ncqdoas[fitgroup].getncattr('fitting window range')
            sensor=ncqdoas[maingroup].Sensor
            qdoas_version=re.search(r".* using Qdoas\s*\((.*)\)",ncqdoas[maingroup].Qdoas).group(1)
            l1file=ncqdoas[maingroup].InputFile.split('/')[-1]
            band=ncqdoas[maingroup].getncattr("L1 spectral_band")
            variables_mapping=qd2hp_mapping(main_variables+fit_variables,slcol_dict)
            variables_mapping_pixcor=qd2hp_mapping(["Pixel corner latitudes",
                                                    "Pixel corner longitudes"])
            if sensor == 'OMI':
                product = create_harp_product_omi_tropomi(variables_mapping,ncqdoas)
                assert check_pixcor(l1file,pixcorfile), \
                "{} is not the right corresponding pixcor file is given".format(pixcorfile)
                add_pixcor(product, variables_mapping_pixcor, pixcorfile, band)
            elif sensor == 'TROPOMI':
                product = create_harp_product_omi_tropomi(variables_mapping, ncqdoas)
            elif sensor == 'GOME-2':
                product = create_harp_product_gome2(variables_mapping, ncqdoas)
            else:
                assert False, "sensor not know"
        fitup=float(re.search(r"(\d*\.\d*)\s*\:\s*([\d\.]*)",fitwin_range).group(1))
        fitdown=float(re.search(r"(\d*\.\d*)\s*\:\s*([\d\.]*)",fitwin_range).group(2))
        return qdoas_harp(qdoasfile,product,fitwin ,list([fitup,fitdown]),l1file,sensor,\
                          band,qdoas_version)

    def print_product(self,outdir):
        #create an output filename and export with Harp to a netcdf4 file.
        # outputfile=outdir+"/"+re.sub(r'.*/([^.]+)(.*)',r'/\1_{}\2'.format(self.fitwin_name),self.filename_qdoas)
        if self.sensor == 'TROPOMI':
            outputfile = outdir+"/"+re.sub(r'([^.]+)L1B_RA_BD3(.*)',r'\1QDOAS\2', self.l1file)
        elif self.sensor == 'OMI':
            outputfile = outdir+"/"+re.sub(r'([^.]+)L1-OML1BRUG(.*)',r'\1QDOAS\2', self.l1file)
        elif self.sensor == "GOME-2":
            outputfile = outdir+"/"+re.sub(r'([^.]+)xxx_1B(.*)',r'\1QDOAS\2', self.l1file)
        else:
            assert False, "sensor not known"

        attr_dict={"qdoas file":os.path.basename(self.filename_qdoas),"name of sensor":self.sensor,
                   "fitwindow name":self.fitwin_name,"fitwindow range":self.fitwin_range,
                   "L1 file":self.l1file,"L1 spectral band":self.band,"QDOAS version":
                   self.qdoas_version}
        self.product.history="qdoas2harp conversion. {}".format(dumps(attr_dict))
        #only attribute that is usable to store information,
        #and that is kept when using harp command line tools.
        harp.export_product(self.product,outputfile , file_format='hdf5', hdf5_compression=6)

def check_pixcor(l1file,pfile):
    '''based on the L1 filename, check if the right pixcor file is provided. there can be an issue with pixcor file with diff. mod. times.'''
    check_str=re.search("OMI-Aura_L1-\S{8}_(\d{4}m\d{4}t\d{4}-o\d{5})*",l1file).group(1)
    pfile_found=os.path.dirname(pfile)+"/OMI-Aura_L2-OMPIXCOR_"+check_str+"*"
    if glob.glob(pfile_found)[0]==pfile:
        return True
    else:
        return False


def add_pixcor(product, mapping, pixcorfile, band):
    '''adding lat/long bounds by taking those from the omi pixcor files.'''
    hpobj_lat = mapping["Pixel corner latitudes"]
    with nc.Dataset(pixcorfile, 'r') as ncpixcor:
        data_lat = ncpixcor["/HDFEOS/SWATHS/OMI Ground Pixel Corners {}/"
                            "Data Fields/TiledCornerLatitude".
                            format(band.replace("_", "-"))][:]
        data_long = ncpixcor["/HDFEOS/SWATHS/OMI Ground Pixel Corners {}/"
                             "Data Fields/TiledCornerLongitude".
                             format(band.replace("_", "-"))][:]
    hpvar_lat = harp.Variable(data_lat.reshape(4, -1).swapaxes(0, 1),
                              ['time', None], unit=hpobj_lat.units,
                              valid_min=hpobj_lat.valid_min,
                              valid_max=hpobj_lat.valid_max,
                              description=hpobj_lat.description, enum=None)
    setattr(product, hpobj_lat.harpname, hpvar_lat)
    hpobj_long = mapping["Pixel corner longitudes"]
    hpvar_long = harp.Variable(data_long.reshape(4, -1).swapaxes(0,1),
                               ['time', None], unit=hpobj_long.units,
                               valid_min=hpobj_long.valid_min,
                               valid_max=hpobj_long.valid_max,
                               description=hpobj_long.description,enum=None)
    setattr(product, hpobj_long.harpname, hpvar_long)
    return product


def create_harp_product_gome2(mapping, ncqdoas):
    '''no n_crosstrack dimension for gome2'''
    product = harp.Product()
    for qdvar in mapping.keys():
        hpobj=mapping[qdvar]
        hpvar=harp.Variable(hpobj.harpname)
        assert ncqdoas[qdvar].dtype.char in ['f', 'd', 'h', 's', 'b', 'B', 'c', 'i', 'l', 'H', 'I']
        if ncqdoas[qdvar].dtype.char in ['f', 'd']:#needs conversion of fillvalues to nan
            if ncqdoas[qdvar].dimensions == ('n_alongtrack',):
                dimensions = ["time"]
                nanvar = nctools.makemasked(ncqdoas[qdvar][:]).astype('f',casting='same_kind')
            elif ncqdoas[qdvar].dimensions == ('n_alongtrack','3'):
                dimensions = ["time"]
                nanvar = nctools.makemasked(ncqdoas[qdvar][:,1]).astype('f',casting='same_kind')
            elif ncqdoas[qdvar].dimensions == ('n_alongtrack','4'):
                dimensions = ["time", None]
                assert hpobj.harpname == "latitude_bounds" or hpobj.harpname == "longitude_bounds"
                nanvar = nctools.makemasked(ncqdoas[qdvar][:, [1, 3, 2, 0]]). \
                    astype('f', casting='same_kind')
            else:
                assert 0, f"unknown variable {qdvar} for this  conversion"
            hpvar=harp.Variable(nanvar, dimensions, unit=hpobj.units, valid_min=hpobj.valid_min,
                                valid_max=hpobj.valid_max, description=hpobj.description , enum=None)
        else: #non floating point, integer point:
            if ncqdoas[qdvar].dimensions == ('n_alongtrack',):
                datatype=ncqdoas[qdvar].dtype.char
                if ncqdoas[qdvar].dtype.char == 'H':
                    datatype='h'
                nchpvar=ncqdoas[qdvar][:]
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
                hpvar=harp.Variable(ncqdoas[qdvar][:].flatten(),['time'], unit=hpobj.units,
                                    valid_min=hpobj.valid_min, valid_max=hpobj.valid_max,
                                    description=hpobj.description, enum=None)
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
        #add harp variables as attribute to harp product.
        setattr(product,mapping[qdvar].harpname,hpvar) 
    scansub=harp.Variable(np.arange(product.latitude.data.shape[0],dtype=np.int32)%n_crosstrack_size,['time'],description="pixel index (0-based) within the scanline")
    setattr(product,"scan_subindex",scansub) #add harp variables as attribute to harp product.

    return product

   
def qdoas_time_harp(time,reftime):
    '''this function converts qdoas times to seconds since a reference time'''
    #ref. time 
    arr=np.full((time.shape[0]),np.nan,dtype='d').flatten()

    for j in range(0,time.shape[0]):
        time_harp=[ int(time[j,i]) for i in range(0,7)]
        reftimestr=re.search(r"\d{4}-\d{2}-\d{2}",reftime).group(0)
        assert reftimestr is not None, "check reference time format"
        refdt_time=dt.datetime.strptime(reftimestr,"%Y-%m-%d")
        arr[j]=(dt.datetime(*time_harp)-refdt_time).total_seconds()
        assert arr[j]>0, "reference time too late"
    return arr
