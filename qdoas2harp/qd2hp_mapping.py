#!/usr/bin/env python
import numpy as np
import netCDF4 as nc
import IPython
import os, re
import argparse
import glob
import datetime as dt
import untangle
from cattrs import structure, unstructure
from cattrs.preconf.json import make_converter
from attrs import define, frozen, Attribute, field
from attr import define,  Factory
import json


exclude_qdoasvar=['Calib/','Spec No','Spike removal','Orbit number','Stretch(Spectrum)','Err Stretch(Spectrum)','Day number','Year','Fractional time' ]


def qd2hp_mapping(jsonfile, qd_vars):
    '''qd_vars  contains variables names used in qdoas without the groups prepended.'''

    dd={}
    mapping=readconfig(jsonfile)
    for qdvar_path in qd_vars:
        qdvar=qdvar_path.split('/')[-1]
        if qdvar  in exclude_qdoasvar:
            continue
        if qdvar in mapping.keys():
            dd[qdvar_path]=mapping[qdvar]
        else:
            tempvarharp=re.sub(r"[\(\)](?!$)","_",qdvar)
            tempvarharp=re.sub(r"[\s\-]+(?!$)","_",tempvarharp)
            harpname=re.sub(r"\)$","",tempvarharp)
            dd[qdvar_path]=qd2hp_entry(harpname)
        
    return dd



@define(repr=False)
class qd2hp_entry:
    harpname=field()
    units: str = field(kw_only=True,default=None)
    descrp: str = field(kw_only=True,default=None)
    comment: str = field(kw_only=True,default=None)
    valid_min: float = field(kw_only=True,default=None)
    valid_max: float = field(kw_only=True,default=None)
    
    def __repr__(self):
        return self.harpname



    


def readconfig(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as fc:
        data=json.load(fc)
    for k in data.keys():
        data[k]=structure(data[k],qd2hp_entry)
    return data
      
