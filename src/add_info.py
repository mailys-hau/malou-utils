import click as cli
import h5py

from pathlib import Path

from pretty import CONSOLE



def add_dataset(dname, key, value, group=None, tab=' '):
    CONSOLE.print(f"{tab}Going through {dname.name}...")
    for fname in dname.iterdir():
        if fname.suffix != ".h5":
            if fname.is_dir():
                add_dataset(fname, key, value, group, tab + ' ')
            else:
                CONSOLE.print(f"{tab} {fname.name} not an HDF, skipping it. [sassy]At least give me proper files.[/]")
            continue
        hdf = h5py.File(fname, 'a')
        if group is not None:
            foo = hdf
            hdf = hdf[group]
        #TODO? Handle if dataset already exist
        hdf.create_dataset(key, data=value)
        hdf.file.close() # If you went down to a group, `.file` is needed



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
    CONSOLE.print(f"Going through {dname.name}.")
    for fname in dname.iterdir():
        if fname.suffix != ".h5":
            if fname.is_dir() and recursive:
                add_dataset(fname, key, value, group=group)
            else:
                CONSOLE.print(f" {fname.name} not an HDF, skipping it. [sassy]At least give me proper files.[/]")
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
