from rich.console import Console
from rich.theme import Theme



_theme = Theme({"error": "red3", "warn": "dark_orange", "good": "green3",
                "sassy": "italic", "sassy-err": "bold red3",
                "happy": "light_coral",
                "dir": "blue bold",
                "repr.number": ""})
CONSOLE = Console(theme=_theme)



from pretty.tables import get_table, format_line
from pretty.progresses import *
