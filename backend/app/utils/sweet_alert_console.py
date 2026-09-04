from __future__ import annotations
import sys
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.box import ROUNDED, DOUBLE_EDGE, HEAVY
from rich.box import ROUNDED

console = Console()


class SweetAlert:
    """
    Renders aesthetic SweetAlert2-style modal dialogs in the terminal console.
    """

    @staticmethod
    def success(
        title: str,
        text: str,
        details: Optional[Dict[str, Any]] = None,
        action_button: str = "OK"
    ) -> None:
        content = Text()
        # Top Icon Badge
        content.append("\n  ( ✓ )  ", style="bold white on green")
        content.append("  SUCCESS\n\n", style="bold green")

        # Title
        content.append(f"{title}\n", style="bold bright_white")
        content.append("─" * max(40, len(title)) + "\n", style="dim green")

        # Body text
        content.append(f"{text}\n\n", style="white")

        # Details list if provided
        if details:
            for k, v in details.items():
                content.append(f"  • {k}: ", style="bold green")
                content.append(f"{v}\n", style="bright_white")
            content.append("\n")

        # Action button
        content.append(f"   [ {action_button} ]   ", style="bold white on dark_green")
        content.append("\n")

        panel = Panel(
            Align.center(content),
            title="[bold green]● Gastroteacher SweetAlert[/bold green]",
            title_align="left",
            border_style="green",
            box=ROUNDED,
            padding=(1, 3),
            expand=False
        )
        console.print("\n")
        console.print(Align.center(panel))
        console.print("\n")

    @staticmethod
    def info(
        title: str,
        text: str,
        details: Optional[Dict[str, Any]] = None,
        action_button: str = "Entendido"
    ) -> None:
        content = Text()
        # Top Icon Badge
        content.append("\n  ( i )  ", style="bold white on cyan")
        content.append("  INFO\n\n", style="bold cyan")

        # Title
        content.append(f"{title}\n", style="bold bright_white")
        content.append("─" * max(40, len(title)) + "\n", style="dim cyan")

        # Body text
        content.append(f"{text}\n\n", style="white")

        if details:
            for k, v in details.items():
                content.append(f"  • {k}: ", style="bold cyan")
                content.append(f"{v}\n", style="bright_white")
            content.append("\n")

        # Action button
        content.append(f"   [ {action_button} ]   ", style="bold white on dark_cyan")
        content.append("\n")

        panel = Panel(
            Align.center(content),
            title="[bold cyan]● Gastroteacher InfoAlert[/bold cyan]",
            title_align="left",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 3),
            expand=False
        )
        console.print("\n")
        console.print(Align.center(panel))
        console.print("\n")

    @staticmethod
    def warning(
        title: str,
        text: str,
        details: Optional[Dict[str, Any]] = None,
        action_button: str = "Aceptar"
    ) -> None:
        content = Text()
        # Top Icon Badge
        content.append("\n  ( ! )  ", style="bold black on yellow")
        content.append("  WARNING\n\n", style="bold yellow")

        # Title
        content.append(f"{title}\n", style="bold bright_white")
        content.append("─" * max(40, len(title)) + "\n", style="dim yellow")

        # Body text
        content.append(f"{text}\n\n", style="bright_white")

        if details:
            for k, v in details.items():
                content.append(f"  • {k}: ", style="bold yellow")
                content.append(f"{v}\n", style="white")
            content.append("\n")

        # Action button
        content.append(f"   [ {action_button} ]   ", style="bold black on yellow")
        content.append("\n")

        panel = Panel(
            Align.center(content),
            title="[bold yellow]● Gastroteacher WarningAlert[/bold yellow]",
            title_align="left",
            border_style="yellow",
            box=ROUNDED,
            padding=(1, 3),
            expand=False
        )
        console.print("\n")
        console.print(Align.center(panel))
        console.print("\n")

    @staticmethod
    def error(
        title: str,
        text: str,
        details: Optional[Dict[str, Any]] = None,
        action_button: str = "Cerrar"
    ) -> None:
        content = Text()
        # Top Icon Badge
        content.append("\n  ( ✕ )  ", style="bold white on red")
        content.append("  ERROR\n\n", style="bold red")

        # Title
        content.append(f"{title}\n", style="bold bright_white")
        content.append("─" * max(40, len(title)) + "\n", style="dim red")

        # Body text
        content.append(f"{text}\n\n", style="white")

        if details:
            for k, v in details.items():
                content.append(f"  • {k}: ", style="bold red")
                content.append(f"{v}\n", style="bright_white")
            content.append("\n")

        # Action button
        content.append(f"   [ {action_button} ]   ", style="bold white on dark_red")
        content.append("\n")

        panel = Panel(
            Align.center(content),
            title="[bold red]● Gastroteacher ErrorAlert[/bold red]",
            title_align="left",
            border_style="red",
            box=ROUNDED,
            padding=(1, 3),
            expand=False
        )
        console.print("\n")
        console.print(Align.center(panel))
        console.print("\n")

    @staticmethod
    def render_summary_table(
        title: str,
        headers: List[str],
        rows: List[List[str]],
        subtitle: Optional[str] = None
    ) -> None:
        table = Table(
            title=f"[bold green]{title}[/bold green]",
            caption=f"[dim]{subtitle}[/dim]" if subtitle else None,
            box=ROUNDED,
            header_style="bold bright_white on dark_green",
            border_style="green",
            show_lines=True
        )

        for h in headers:
            table.add_column(h, justify="left", style="white")

        for r in rows:
            table.add_row(*r)

        console.print("\n")
        console.print(Align.center(table))
        console.print("\n")
