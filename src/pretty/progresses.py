import rich.progress as rp



def loading_bar(description, console=None):
    style = [rp.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
             rp.BarColumn(), rp.MofNCompleteColumn(),
             rp.TextColumn(f"[green]{description}[/] [bold]·[/]"),
             rp.TimeRemainingColumn(elapsed_when_finished=True)]
    return rp.Progress(*style, console=console)

def loading_spinner(console=None):
    style = [rp.TextColumn("{task.description}"),
             rp.SpinnerColumn(spinner_name="simpleDotsScrolling",
                              finished_text="done!")]
    return rp.Progress(*style, console=console, transient=True)
