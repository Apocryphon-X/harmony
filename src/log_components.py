from rich.console import Console
from rich.control import Control
from rich.panel import Panel
from rich.pretty import Pretty

from dataclasses import dataclass

console = Console()

@dataclass
class Prompts:
    client = "[white on #5b5b5b]$CLIENT[/]"
    omegaup = "[white on #5588dd]OMEGAUP[/]"
    discord = "[white on #404eed]DISCORD[/]"


@dataclass
class Bars:
    error = "[red]▌[/]"
    critical_error = "[blink red]▌[/]"
    info = "[cyan]▌[/]"
    success = "[green]▌[/]"
    warning = "[yellow]▌[/]"

