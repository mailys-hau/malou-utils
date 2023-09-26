"""
Code originating from echoviz
"""
import h5py

from datetime import timedelta
from pathlib import Path
import subprocess
from time import sleep, time

from echoviz import VoxelGrid




POUTS = {ext: Path(f"test-output.{ext}").resolve() for ext in ["png", "gif", "html"]}



def _get_grid(array, origin, directions, spacing):
    # You want to copy in case you change the scale because it's the same for several grids
    out = VoxelGrid(array, origin.copy(), directions.copy(), spacing.copy())
    #out.set_scale("mm") #FIXME: No hard code
    return out

def load_hdf2vox(fname, has_pred=True):
    hdf = h5py.File(fname, 'r')
    origin = hdf["VolumeGeometry"]["origin"][()]
    directions = hdf["VolumeGeometry"]["directions"][()]
    spacing  = hdf["VolumeGeometry"]["resolution"][()]
    vinp = []
    vtg, vpr = {"all": [], "anterior": [], "posterior": []}, {"all": [], "anterior": [], "posterior": []}
    multi = False
    keys = ["Input", "Target", "Prediction"] if has_pred else ["CartesianVolume", "GroundTruth"]
    for i in range(1, len(hdf[keys[0]]) + 1):
        vinp.append(_get_grid(hdf[keys[0]][f"vol{i:02d}"][()], origin, directions, spacing))
        try:
            vtg["all"].append(_get_grid(hdf[keys[1]][f"vol{i:02d}"][()],origin, directions, spacing))
            if has_pred:
                vpr["all"].append(_get_grid(hdf[keys[2]][f"vol{i:02d}"][()], origin, directions, spacing))
        except KeyError:
            for k in ["anterior", "posterior"]:
                vtg[k].append(_get_grid(hdf[keys[1]][f"{k}-{i:02d}"][()], origin, directions, spacing))
                if has_pred:
                    vpr[k].append(_get_grid(hdf[keys[2]][f"{k}-{i:02d}"][()], origin, directions, spacing))
            multi = True
    hdf.close()
    if multi: # Clean created keys
        vtg.pop("all"), vpr.pop("all")
    else:
        vtg.pop("anterior"), vtg.pop("posterior")
        vpr.pop("anterior"), vpr.pop("posterior")
    if len(vinp) == 1: # Flatten if only one frame
        vinp = vinp[0]
        for k in vtg.keys():
            vtg[k] = vtg[k][0]
            if has_pred:
                vpr[k] = vpr[k][0]
    return vinp, vtg, vpr

def load_hdf(fname, has_pred=True):
    hdf = h5py.File(fname, 'r')
    origin = hdf["VolumeGeometry"]["origin"][()]
    directions = hdf["VolumeGeometry"]["directions"][()]
    spacing  = hdf["VolumeGeometry"]["resolution"][()]
    vinp = []
    vtg, vpr = {"all": [], "anterior": [], "posterior": []}, {"all": [], "anterior": [], "posterior": []}
    multi = False
    keys = ["Input", "Target", "Prediction"] if has_pred else ["CartesianVolume", "GroundTruth"]
    for i in range(1, len(hdf[keys[0]]) + 1):
        vinp.append(hdf[keys[0]][f"vol{i:02d}"][()])
        try:
            vtg["all"].append(hdf[keys[1]][f"vol{i:02d}"][()])
            if has_pred:
                vpr["all"].append(hdf[keys[2]][f"vol{i:02d}"][()])
        except KeyError:
            for k in ["anterior", "posterior"]:
                vtg[k].append(hdf[keys[1]][f"{k}-{i:02d}"][()])
                if has_pred:
                   vpr[k].append(hdf[keys[2]][f"{k}-{i:02d}"][()])
            multi = True
    hdf.close()
    if multi: # Clean created keys
        vtg.pop("all"), vpr.pop("all")
    else:
        vtg.pop("anterior"), vtg.pop("posterior")
        vpr.pop("anterior"), vpr.pop("posterior")
    if len(vinp) == 1: # Flatten if only one frame
        vinp = vinp[0]
        for k in vtg.keys():
            vtg[k] = vtg[k][0]
            vpr[k] = vpr[k][0]
    return vinp, vtg, vpr, origin, directions, spacing

