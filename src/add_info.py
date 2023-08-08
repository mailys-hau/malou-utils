import click as cli
import h5py

from pathlib import Path

from pretty import CONSOLE, loading_spinner



def add_dataset(dname, key, value, progress, group=None, tab="├── "):
    CONSOLE.print(f"{tab}Going through [dir]{dname.name}[/]")
    tab = "│   " + tab
    tid = progress.add_task('', total=None)
    for fname in progress.track(dname.iterdir(), task_id=tid, description=''):
        if fname.suffix != ".h5":
            if fname.is_dir():
                add_dataset(fname, key, value, progress, group, tab)
            else:
                CONSOLE.print(f"{tab}{fname.stem}[sassy-err]{fname.suffix}[/]? [sassy]Give me a proper file.[/]")
            continue
        hdf = h5py.File(fname, 'a')
        if group is not None:
            hdf = hdf[group]
        #TODO? Handle if dataset already exist
        hdf.create_dataset(key, data=value)
        hdf.file.close() # If you went down to a group, `.file` is needed
    progress.remove_task(tid)



@cli.command(context_settings={"help_option_names": ["-h", "--help"], "show_default": True})
@cli.argument("dname", type=cli.Path(exists=True, resolve_path=True, path_type=Path, file_okay=False))
@cli.option("--dataset-name", "-n", "key", default="unit", type=str,
            help="Key name given to created dataset.")
@cli.option("--value", "-v", default='m', help="Value to put in created dataset.")
@cli.option("--group", "-g", default=None, type=str,
            help="Group where to put the dataset in.")
@cli.option("--recursive", "-r", default=False, is_flag=True,
            help="Whether to recursively iterate through given directory.")
def add_info(dname, key, value, group, recursive):
    """
    Add a dataset and a value to all HDF files in given directory.
    /!\ HDFs are modified in place and not copied /!\ 

    \b
    DNAME    DIR    Directory containing HDFs.
    """
    CONSOLE.print(f". Going through [dir]{dname.name}[/]")
    with loading_spinner(CONSOLE) as progress:
        for fname in progress.track(dname.iterdir(), description=''):
            if fname.suffix != ".h5":
                if fname.is_dir() and recursive:
                    add_dataset(fname, key, value, progress, group=group)
                else:
                    CONSOLE.print(f"├── {fname.stem}[sassy-err]{fname.suffix}[/]? [sassy]Give me a proper file.[/]")
                continue
            hdf = h5py.File(fname, 'w')
            if group is not None:
                hdf = hdf[group]
            #TODO? Handle if dataset already exist
            hdf.create_dataset(key, data=value)
            hdf.close()
    CONSOLE.print("[happy]I'm done! :blush:[/]")



if __name__ == "__main__":
    add_info()
