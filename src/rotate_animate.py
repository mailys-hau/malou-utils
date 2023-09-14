""" https://community.plotly.com/t/how-to-animate-a-rotation-of-a-3d-plot/20974 """

import click as cli
import echoviz as ecv
import numpy as np
import plotly.graph_objects as go

from echoviz.utils.misc import clean_fname
from numpy import pi, cos, sin, sqrt
from pathlib import Path

from utils import load_hdf, load_hdf2vox




LAYOUT = {"plot_bgcolor": "rgb(64, 64, 64)",
          #"scene_aspectmode": "data",
          #"scene_xaxis_visible": False,
          #"scene_yaxis_visible": False,
          #"scene_zaxis_visible": False,
          "title_y": 0.98,
          "autosize": True, "width": 600, "height": 500,
          "margin": {'l': 10, 't': 30, 'b': 10},
          "updatemenus": [{
              "type": "buttons",
              "showactive": False,
              'y': 1,
              'x': 1.02,
              "xanchor": "left",
              "yanchor": "bottom",
              "pad": {'t': 45, 'r': 10},
              "buttons": [{
                  "label": "Play",
                  "method": "animate",
                  "args": [
                      None,
                      {
                          "frame": {"duration": 1, "redraw": True},
                          "transition_duration": 0,
                          "fromcurrent": True,
                          "mode": "immediate"
                          }]
                      }]}]}



def rotx(a):
    return np.array([[1, 0, 0], [0, cos(a), -sin(a)], [0, sin(a), cos(a)]])

def roty(a):
    return np.array([[cos(a), 0, sin(a)], [0, 1, 0], [-sin(a), 0, cos(a)]])

def rotz(a):
    return np.array([[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]])

def rotez(x, y, z, theta):
    w = x + 1j * y
    return {'x': np.real(np.exp(1j * theta) * w),
            'y': np.imag(np.exp(1j * theta) * w),
            'z': z}


def rotate_eye(fig):
    fig.update_layout(LAYOUT)
    xe, ye, ze = -0.5, -1.15, 0.7 #FIXME: No hard code
    # Now to created an animation around it
    frames = []
    for t in np.arange(0, 6.26, 0.05):
        frames.append(go.Frame(layout={"scene_camera_eye": rotez(xe, ye, ze, -t)}))
    fig.frames = frames
    return fig

def rotate_points(fig):
    fig.update_layout(LAYOUT)
    alphas = np.linspace(0, 2*pi, 48)
    frames = []
    for a in alphas:
        data = []
        for mesh in fig.data:
            points = np.stack([mesh.x, mesh.y, mesh.z]) #(3, n)
            rpts = rotz(a).dot(points)
            data.append(go.Mesh3d(x=rpts[0,:], y=rpts[1,:], z=rpts[2,:]))
        frames.append(go.Frame(data=data, traces=[0]))
    fig.frames = frames
    return fig



@cli.command(context_settings={"help_option_names": ["--help", "-h"], "show_default": True})
@cli.argument("fname", type=cli.Path(exists=True, resolve_path=True, path_type=Path))
@cli.option("--output-filename", "-o", "oname", default=None,
            type=cli.Path(resolve_path=True, path_type=Path),
            help="Where to store generated animation.")
@cli.option("--prediction/--not-prediction", "-p/-P", "has_pred", default=True,
            help="If the given file has prediction stored in it or not.")
@cli.option("--set-unit", "-s", type=cli.Choice(["mm", "m"]), default=None,
            help="Set the unit of the voxel grid scale.")
@cli.option("--show", "-S", is_flag=True, help="Whether to interactive show generated plot.")
def rotate(fname, oname, has_pred, set_unit, show):
    """
    Create a 3D plot that rotates automatically in an inneficient way, but I
    didn't had to dig too much in the code, so here we are.
    """
    inps, tgs, preds  = load_hdf2vox(fname, has_pred)
    if isinstance(inps, list):
        f = int(len(inps) / 2) # Middle frame
        inp, tg = inps[f], { k: v[f] for k, v in tgs.items()}
        if has_pred:
            pred = { k: v[f] for k, v in preds.items()}
    else:
        inp, tg = inps, tgs
        if has_pred:
            pred = preds
    #FIXME: Set scale, get data and layout
    fig = ecv.asd_interactive_3d(tg, pred, vinputs=inp, title="Surface Distance (mm)", show=False)
    #fig = ecv.interactive_3d(inp, vlabels=tg, title="Input & label example", show=False)
    fig = rotate_eye(fig)
    if show:
        fig.show()
    if oname:
        oname = clean_fname(oname)
        fig.write_html(oname)



if __name__ == "__main__":
    rotate()
