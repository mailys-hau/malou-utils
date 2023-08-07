import click as cli
import wandb

from pretty import CONSOLE, get_table
from dataframes import SUMMARIES
from dataframes.summarize import mean_std




# List of metrics to take into account
DIST = ["hdf95", "masd"]
ACCU = ["acc", "prec", "rec", "dice"]



def _clean_hist(df):
    out = df.loc[:,~df.columns.str.startswith('_')]
    out = out.loc[:,~out.columns.str.endswith("_step")]
    return out

def _filter_keys(keys):
    out = []
    for k in keys:
        if k.startswith('_') or k.endswith("_step") or k == "epoch" or k.startswith("lr-"):
            continue
        out.append(k)
    return out


@cli.command(context_settings={"help_option_names": ["-h", "--help"], "show_default": True})
@cli.argument("run_id", type=str)
@cli.option("--team", "-t", default="tee-4d",
            help="Weight & Bias team associated to the run.")
@cli.option("--project", "-p", default="3DMV-multi-segmentation",
            help="Weight & Bias project associated to the run.")
@cli.option("--summary-type", "-st", "summary", type=cli.Choice(SUMMARIES.keys()),
            default="mean_std", help="Summary function to use.")
@cli.option("--distance-scale", "-s", "scale", default=1.0,
            help="Value to multiply distance metrics with to go to given unit.")
@cli.option("--distance-unit", "-u", "unit", default="mm",
            help="Distances' unit.")
def summarize(run_id, team, project, summary, scale, unit):
    """
    Summarize a given Weights & bias run.

    \b
    RUN_ID    STR    Weight & Bias run id.
    """
    api = wandb.Api()
    run = api.run(f"{team}/{project}/{run_id}")
    CONSOLE.print(f"We'll have a looking at run `{run.name} - {run.id}`.")
    keys = _filter_keys(list(run.summary.keys()))
    x_axis = "epoch" if run.job_type == "train" else "_step"
    #FIXME: If all keys are not defined for the whole row, then it is not returned
    hist = run.history(x_axis=x_axis, keys=keys).astype(float) # Return `pandas.DataFrame`
    if len(hist) == 0:
        CONSOLE.print("[sassy]You're history is as empty as my soul.[/]\n[error]Nothing to summarize, bye.[/]")
        return
    dcols, acols, sections = [], [], []
    for col in sorted(hist.columns): # Order col for diplay purposes
        if not "post-process" in sections and col.startswith("p_"):
            sections.append("post-process")
        elif not "validation" in sections and col.startswith("v_"):
            sections.append("validation")
        if any(d in col for d in DIST):
            c = col.strip("v_").strip("p_")
            if not c in dcols:
                dcols.append(c)
        elif any(a in col for a in ACCU):
            c = col.strip("v_").strip("p_")
            if not c in acols:
                acols.append(c)
    # FIXME: get best or last for validation
    func = SUMMARIES[summary]
    dist = get_table(hist * scale, func, dcols, f"Distance metrics ({unit})", sections)
    accu = get_table(hist * 100, lambda df: func(df, "max"), acols, f"Accuracy metrics (%)", sections)
    CONSOLE.print(dist, accu)



if __name__ == "__main__":
    summarize()
