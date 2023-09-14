import click as cli
import pandas as pd

from pathlib import Path
from rich.table import Table

from metrics import *
from pretty import CONSOLE, loading_bar
from pretty.tables import COLORS, format_line
from utils import load_hdf



def _get_key(l, k):
    return l[0][k], l[1][k], *l[2:]


@cli.command(context_settings={"help_option_names": ["--help", "-h"], "show_default": True})
@cli.argument("hdfdir", type=cli.Path(exists=True, resolve_path=True, path_type=Path, file_okay=False))
@cli.option("--rescaling", "-r", "scale", default=1e3, type=cli.FloatRange(min=0),
            help="Scalor factor to use on computed metrics.")
@cli.option("--unit", "-u", default="mm", type=str,
            help="Distance unit that will be show in table.")
@cli.option("--summary/--no-summary", " /-S", default=True,
            help="Whether to print additional section with mean and STD values.")
def calculate(hdfdir, scale, unit, summary):
    nfiles = len(list(hdfdir.iterdir())) #FIXME
    CONSOLE.print("[sassy]Kids this day can't even do the math themselves...[/]")
    df = pd.DataFrame(columns=["Filename", "Leaflet", f"ASD ({unit})",f"HDF 95% ({unit})", f"SDF ({unit})"])
    #FIXME: Add loading bar
    for fname in hdfdir.iterdir():
        if fname.suffix != ".h5":
            CONSOLE.print(f"[warning]`{fname.name}` is unsuited for this task.[/]")
            continue
        # Load file
        data = list(load_hdf(fname))
        del data[0] # Don't care for input here
        # Append new row of data
        for k in data[0].keys():
            args = _get_key(data, k)
            try:
                df.loc[len(df)] = [fname.stem, k, scale * average_surface_distance(*args),
                                   scale * hausdorff_distance(*args), scale * average_signed_distance(*args)]
            except RuntimeError:
                CONSOLE.print(f"[warning] Something failed, dropping line {fname.name} - {k}[/]")
    table = Table(title="Metrics results")
    for c, j in zip(df.columns, ["left", "center", "right", "right", "right"]):
        table.add_column(c, justify=j)
    table.add_section()
    for i in range(len(df)):
        line = format_line(df.iloc[i].values)
        table.add_row(*line, style=COLORS[line[1]])
    if summary: # Print summary (mean/std)
        table.add_section()
        for k in df["Leaflet"].unique():
            mean = df[df["Leaflet"] == k].mean(numeric_only=True).tolist()
            std = df[df["Leaflet"] == k].std(numeric_only=True).tolist()
            vals = [f"{m:.5f} ± {s:.5f}" for m, s in zip(mean, std)]
            table.add_row('', k, *vals, style=COLORS[k])
    CONSOLE.print(table)
    #TODO?Add option for plot



if __name__ == "__main__":
    calculate()
