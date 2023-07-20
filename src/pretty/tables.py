"""
"""
from itertools import zip_longest
from rich.table import Table




COLORS = {'1': "magenta", '2': "cyan"}



def _add_rows(table, df, func, section):
    res = func(df)
    for sec, k in zip_longest([section], res.keys(), fillvalue=''):
        table.add_row(sec, k, *res[k])
    return table


def get_table(df, func, cols, title='', sections=[]):
    table = Table(title=title)
    if sections:
        table.add_column("Section", style="grey74", justify="right")
    table.add_column('', style="grey74", justify="right")
    for col in cols:
        table.add_column(col, style=COLORS.get(col[-1], "gold1"), justify="center")
    try:
        table = _add_rows(table, df[cols], func, '')
    except KeyError:
        pass # Some metrics are only computed for validation for example, so no default
    for sec in sections:
        table.add_section()
        table = _add_rows(table, df[[f"{sec[0]}_{col}" for col in cols]], func, sec)
    return table
