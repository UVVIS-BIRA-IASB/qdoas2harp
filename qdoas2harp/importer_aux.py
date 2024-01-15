'''module that put aux. data from a L2 s5p file into the harp compliant qdoas output'''
import glob
import os
import re
import argparse
import json
import harp
import netCDF4 as nc
# mapping use to identify L2 auxiliary file. 
MOLEC_L2 = {'HCHO': 'L2__HCHO__', 'SO2': 'L2__SO2___'} 


def cml():
    '''entry_point used as a cml argument printing the correspoding cloud file
    from the L1 file that was used''' 
    parser = argparse.ArgumentParser(description='provide harp compliant qdoas output file')
    parser.add_argument(dest='l2file',  help="qdoas harp compliant file")
    parser.add_argument('--auxdir', dest='auxdir', help="dir where aux.\
    file is in", default=None)
    args = parser.parse_args()
    l2file = args.l2file
    auxdir = args.auxdir
    if os.path.isdir(l2file):
        for l2f in glob.glob(l2file+"/*"):
            if auxdir is None:
                print("{} ----> {}".format(l2f,give_auxfilename(l2f)))
            else:
                assert len(glob.glob(auxdir+"/"+give_auxfilename(l2f))) == 1
                auxfile = glob.glob(auxdir+"/"+give_auxfilename(l2f))[0]
                print("{} ----> {}".format(l2f, auxfile))
                retrieve_auxvars(l2f, auxfile)
    else:  # one qdoas l2 file is provided
        if auxdir is None:
            print("Aux. file that will be used for l2file :\n ")
            print("{} ----> {}".format(l2file, give_auxfilename(l2file)))
        else:
            assert len(glob.glob(auxdir+"/"+give_auxfilename(l2file))) == 1
            auxfile=glob.glob(auxdir+"/"+give_auxfilename(l2file))[0]
            retrieve_auxvars(l2file, auxfile)


def give_auxfilename(l2file):
    '''molecule is derived from the slant column present in qdoas. '''
    with nc.Dataset(l2file, 'r') as ncfile:
        l1used = json.loads(re.search(r"qdoas2harp conversion.\s*(.*)", ncfile.history).group(1))['L1 file']
        slcol = [x for x in ncfile.variables.keys() if
                 re.search(r"\w*slant\w*density$", x)]
    patt = re.search(r"S5P_(?P<proc>[A-Z]{4})_L1B_RA_BD\d_(?P<start>\d{8}T\d{6})"
                     "_(?P<end>\d{8}T\d{6})_(?P<orbit>\d{5})_(?P<num>\d{2}).*",
                     l1used)
    molec = []
    for mol in MOLEC_L2.keys():
        if all([mol in y for y in slcol]):
            molec.append(mol)
        else:
            assert len([mol in y for y in slcol]) == 1, "not a single slant column in product"
    assert len(molec) == 1, "absorber molecule not found"
    molecule = molec[0]
    proc = patt.group('proc')
    start = patt.group('start')
    end = patt.group('end')
    orbit = patt.group('orbit')
    num = patt.group('num')
    l2filename = "S5P_{}_{}_{}_{}_{}_{}_*.nc".format(proc, MOLEC_L2[molecule],
                                                     start, end, orbit, num)
    return l2filename


def retrieve_auxvars(l2file, auxfile):
    '''variables to copy from an aux. file to the current existing L2 qdoas file:'''
    aux_vars = ['cloud_fraction', 'cloud_albedo', 'cloud_albedo_uncertainty',
                'cloud_fraction_uncertainty', 'cloud_height',
                'cloud_height_uncertainty', 'cloud_pressure',
                'cloud_pressure_uncertainty', 'surface_albedo', 'surface_altitude',
                'surface_altitude_uncertainty', 'pressure', 'surface_pressure',
                'tropopause_pressure', 'HCHO_volume_mixing_ratio_dry_air_apriori']
    #during harp.import_product global attr. dissappear, so read them and write them again in the output after harp.export_product.
    product_aux = harp.import_product(auxfile)
    product_qdoas = harp.import_product(l2file)
    assert all([x in product_aux.__dict__.keys() for x in aux_vars])
    for auxvar in aux_vars:
        setattr(product_qdoas, auxvar,getattr(product_aux, auxvar))
    harp.export_product(product_qdoas, l2file, file_format='hdf5',
                        hdf5_compression=6)
