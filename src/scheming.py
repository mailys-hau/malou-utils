import click as cli
import h5py
import echoviz as ecv
from multiprocessing import Pool
from pathlib import Path

from pretty import CONSOLE, loading_bar
from utils import load_hdf2vox






def _do_plot(params):
    fname, odir, set_scale = params
    if fname.suffix != ".h5":
        CONSOLE.print(f"[warning]`{fname.name}` don't give a fuck about that one, not loading it.[/]")
        return
    inp, tg, pred = load_hdf2vox(fname)
    oname = odir.joinpath(fname.name).with_suffix(".html")
    # FIXME: Accept whatever echoviz function
    if set_scale is not None:
        inp.set_scale(set_scale)
        for k in tg.keys():
            tg[k].set_scale(set_scale), pred[k].set_scale(set_scale)
    ecv.asd_interactive_3d(tg, pred, vinputs=inp,
                           title="Surface distance between target & prediction (mm)",
                           show=True, filename=oname)


@cli.command(context_settings={"help_option_names": ["--help", "-h"], "show_default": True})
@cli.argument("hdfdir", type=cli.Path(exists=True, resolve_path=True, path_type=Path, file_okay=False))
@cli.option("--output-directory", "-o", "odir", default="output-plots",
            type=cli.Path(resolve_path=True, path_type=Path),
            help="Where to store generated gifs.")
@cli.option("--number-workers", "-n", "nb_workers", type=cli.IntRange(min=1), default=1,
            help="Number of workers used to accelerate file processing.")
@cli.option("--set-unit", "-s", type=cli.Choice(["mm", "m"]), default=None,
            help="Set the unit of the voxel grid scale.")
def main(hdfdir, odir, nb_workers, set_unit):
    """ Do da plot """
    nfiles = len(list(hdfdir.iterdir()))
    odir.mkdir(exist_ok=True, parents=True)
    CONSOLE.print(f"[sassy]{nfiles} fucking files?! Jesus Christ man...[/] :expressionless:")
    params = zip(hdfdir.iterdir(), [odir for i in range(nfiles)], [set_unit for i in range(nfiles)])
    with loading_bar("plotted", CONSOLE) as prb:
        tid = prb.add_task("[green] Plotted...", total=nfiles)
        with Pool(processes=nb_workers) as pool:
            for res in pool.imap(_do_plot, params):
                prb.advance(tid)
    CONSOLE.print("[sassy]Finish your dirty work, hope you're happy now.[/]")


if __name__ == "__main__":
    main()
