'''qdoas to harp mappings'''
import os
import re
import json
import numpy as np
from attrs import define, field
from cattrs import structure

#contains a mapping of default qdoas names, like geolocation, time. 
mapping_file = os.path.join(os.path.dirname(__file__), "qd2hp_mapping.json") 
molecule_fullname = {'HCHO': 'formaldehyde',
                     'SO2': 'sulfur dioxide',
                     'BrO': 'Bromine oxide',
                     'NO2': 'nitrogen dioxide',
                     'C2H2O2': 'glyoxal'} 


def qd2hp_mapping(qd_vars,slcol_dict=None):
    '''qd_vars  contains variables names used in qdoas without the groups prepended.'''
    qd2hp_dict = {}
    assert slcol_dict is None or np.all([slcol_dict[x] in molecule_fullname.keys()
                                        for x in slcol_dict.keys()]),\
                                        "wrong molecule name"
    mapping=readconfig(mapping_file)
    for qdvar_path in qd_vars:
        qdvar = qdvar_path.split('/')[-1]
        # search if qdoas variable is a  variable name for which a standard
        # mapping exist. 
        if qdvar in mapping:
            qd2hp_dict[qdvar_path] = mapping[qdvar]
        # search in the slant columns is from a molecule of interest
        elif re.search(r"SlCol\((.*)\)", qdvar) is not None:
            qdoas_name = re.search(r"SlCol\((.*)\)", qdvar).group(1)
            if qdoas_name in slcol_dict.keys():
                qd2hp_dict[qdvar_path] = qd2hp_entry.create_from_slcol(
                    slcol_dict[qdoas_name])
        # search in the slant columns error is from a molecule  of interest
        elif re.search(r"SlErr\((.*)\)", qdvar) is not None:
            if qdoas_name in slcol_dict.keys():
                qd2hp_dict[qdvar_path] = qd2hp_entry.create_from_slerr(
                    slcol_dict[qdoas_name])
    return qd2hp_dict


@define(repr=False)
class qd2hp_entry:
    harpname = field()
    units: str = field(kw_only=True)  # required attribute.
    description: str = field(kw_only=True, default=None)
    comment: str = field(kw_only=True, default=None)
    valid_min: float = field(kw_only=True, default=None)
    valid_max: float = field(kw_only=True, default=None)

    def __repr__(self):
        return self.harpname

    @classmethod
    def create_from_slcol(cls, molecule):
        harpname = "{}_slant_column_number_density".format(molecule)
        units = "molecules/cm2"
        description = "slant column {}".format(molecule_fullname[molecule])
        return cls(harpname=harpname, units=units, description=description)

    @classmethod
    def create_from_slerr(cls, molecule):
        harpname = "{}_slant_column_number_density_uncertainty".format(molecule)
        units = "molecules/cm2"
        description = "uncertainty slant column {}".format(molecule_fullname[molecule])
        return cls(harpname=harpname, units=units, description=description)


def readconfig(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as jfile:
        data = json.load(jfile)
    for k in data.keys():
        data[k] = structure(data[k], qd2hp_entry)
    return data
