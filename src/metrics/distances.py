import numpy as np
from pysdf import SDF

from skimage.measure import marching_cubes



def _vox2coord(voxgrid, origin, directions, spacing, stride=1):
    verts, faces, _, _ = marching_cubes(voxgrid, None, spacing=tuple(spacing),
                                        step_size=stride, allow_degenerate=False,
                                        mask=None)
    # Map to coordinates given by voxel grid. Need right multiplication
    verts = verts @ directions + origin
    return verts, faces


def _signed_distance(gt, pred, origin, directions, spacing):
    verts, faces = _vox2coord(gt, origin, directions, spacing)
    gt_sdf = SDF(verts, faces)
    verts, faces = _vox2coord(pred, origin, directions, spacing)
    return gt_sdf(verts)


def hausdorff_distance(gt, pred, origin, directions, spacing, gtpercentile=95):
    sdf = abs(_signed_distance(gt, pred, origin, directions, spacing))
    psdf1 = np.percentile(sdf, 95)
    sdf = abs(_signed_distance(pred, gt, origin, directions, spacing))
    psdf2 = np.percentile(sdf, 95)
    return max(psdf1, psdf2)

def average_signed_distance(gt, pred, origin, directions, spacing):
    return _signed_distance(gt, pred, origin, directions, spacing).mean()

def average_surface_distance(gt, pred, origin, directions, spacing):
    return abs(_signed_distance(gt, pred, origin, directions, spacing)).mean()
