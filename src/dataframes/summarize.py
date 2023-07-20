"""
Compute things on pandas.DataFrame and return results as pretty string.
"""
import inspect as ispc
import sys

from pretty import CONSOLE



def _dropna(df):
    n = len(df)
    df = df.dropna(axis=0)
    if len(df) != n:
        CONSOLE.print(f"[warn]Found {n - len(df)} NaN in {', '.join(df.columns)}."
                       " Following computation will not include concerned rows.[/]")
    return df

def mean_std(df, order="", dropna=True):
    df = _dropna(df) if dropna else df
    return {"mean ± std": [ f"{mean:.2f} ± {std:.2f}" for mean, std in zip(df.mean(), df.std()) ]}


def best(df, order="min", dropna=True):
    df = _dropna(df) if dropna else df
    res = df.min() if order == "min" else df.max()
    return {"best": [ f"{best:.2f}" for best in res ]}

def last(df, dropna=False):
    df = _dropna(df) if dropna else df
    return {"last": [ f"{last:.2f}" for last in df.iloc[-1] ]}

def best_last(df, order="min", dropna=False):
    return best(df, order) | last(df)


def alls(df, order="min", dropna=False):
    out = {}
    for func in SUMMARIES.values():
        if func.__name__ == "alls":
            continue # Or else welcome infinite recursion
        out.update(func(df, order))
    return out



SUMMARIES = dict(ispc.getmembers(sys.modules[__name__],
                                 lambda obj: ispc.isfunction(obj) and not obj.__name__.startswith('_')))
