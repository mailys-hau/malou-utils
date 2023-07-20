from rich.console import Console
from rich.theme import Theme



_theme = Theme({"error": "red3", "warn": "dark_orange", "good": "green3",
                "sassy": "italic",
                "repr.number": ""})
CONSOLE = Console(theme=_theme)



from pretty.tables import get_table
