import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.box import SQUARE
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
import time
import os
import sys
import random
from importlib.resources import files
from contextlib import contextmanager


app = typer.Typer()
console = Console()


def generate_paragraph(word_count: int = 300, top_n: int = 1000) -> str:
    word_file = files("typeman.assets").joinpath("common_words.txt")
    words = word_file.read_text().splitlines()
    words = [w.strip() for w in words if w.strip()]

    # Limit to top N most frequent words
    words = words[:top_n]

    return " ".join(random.choices(words, k=word_count))


paragraph = generate_paragraph(word_count=400)


def render_colored_text(paragraph: str, typed: str) -> Text:
    styled = Text()
    cursor_position = len(typed)

    for i, char in enumerate(paragraph):
        if i < cursor_position:
            # Alredy typed characters
            if typed[i] == char:
                styled.append(char, style="bold green")
            else:
                styled.append(char, style="bold red")
        elif i == cursor_position:
            # current cursor position
            styled.append(
                char, style="bold black on bright_white underline"
            )  # cursor position
        else:
            styled.append(char, style="dim")

    return styled


# Cross-platform non-blocking input check
def is_key_pressed():
    if os.name == "nt":
        import msvcrt

        return msvcrt.kbhit()
    else:
        import select

        return select.select([sys.stdin], [], [], 0)[0]


def read_key():
    if os.name == "nt":
        import msvcrt

        return msvcrt.getwch()
    else:
        return sys.stdin.read(1)


# Context manager to enable raw mode on Unix
@contextmanager
def raw_mode(file):
    if os.name == "nt":
        yield
    else:
        import termios
        import tty

        old_attrs = termios.tcgetattr(file.fileno())
        try:
            tty.setcbreak(file.fileno())
            yield
        finally:
            termios.tcflush(file.fileno(), termios.TCIFLUSH)  # Flush pending input
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)


@app.command()
def main(seconds: int):
    if not 0 <= seconds <= 60:
        console.print("[red]Please provide a duration between 0 & 60 seconds.[/red]")
        raise typer.Exit()

    console.print("[cyan]Your test starts in [cyan]")

    for i in range(3, 0, -1):
        console.print(f"[bold]{i}..[/bold]")
        time.sleep(1)
    console.print("[bold green]Go![/bold green]")

    # Setup progress bar (manually updated)
    progress = Progress(
        TextColumn("[bold blue]Time Left[/bold blue]"),
        BarColumn(),
        TimeRemainingColumn(compact=True),
        transient=False,
    )
    task_id = progress.add_task("timer", total=seconds)

    # Create a new progress bar just for final display
    final_progress = Progress(
        TextColumn("[bold red]Time's Up[/bold red]"),
        BarColumn(finished_style="bold yellow"),
        TimeRemainingColumn(compact=True),
        transient=False,
    )

    # Add a completed task to it
    final_progress.add_task("timer", total=seconds, completed=seconds)

    typed = ""
    start_time = time.time()
    end_time = time.time() + seconds
    display = Text()

    with raw_mode(sys.stdin):
        with Live(refresh_per_second=60, screen=True) as live:
            while time.time() < end_time and len(typed) < len(paragraph):
                # Update progress bar manually
                elapsed = time.time() - start_time
                progress.update(task_id, completed=elapsed)

                display = render_colored_text(paragraph, typed)
                # paragraph_display = Panel(display, title="Typing Test")
                paragraph_display = Align.center(
                    Panel.fit(
                        display,
                        title="[bold magenta]Typing Test[/bold magenta]",
                        border_style="blue",
                        box=SQUARE,
                        padding=(1, 2),
                    )
                )

                # Build UI group with progress and paragraph panel
                layout = Group(progress.get_renderable(), paragraph_display)
                live.update(layout)

                # char = readchar.readkey()

                if is_key_pressed():
                    char = read_key()

                    # Only accept valid characters (basic)
                    if char in ("\x03", "\x04"):  # Ctrl+C or Ctrl+D
                        console.print("[red]Exiting the test.[/red]")
                        raise typer.Exit()
                    elif char == "\x7f":  # Backspace
                        typed = typed[:-1]
                    elif char == "\r" or char == "\n":
                        continue
                    elif len(typed) < len(paragraph):
                        if char == " ":
                            if paragraph[len(typed)] == " ":
                                typed += char
                            else:
                                continue
                        else:
                            typed += char

                time.sleep(0.01)  # Slight delay for smoother UI

            # Calculate WPM and accuracy
            duration = max(time.time() - start_time, 1)
            correct_chars = sum(
                1 for i in range(len(typed)) if typed[i] == paragraph[i]
            )
            wpm = (correct_chars / 5) / (duration / 60)
            accuracy = (correct_chars / len(typed)) * 100 if len(typed) > 0 else 0.0

            countdown = 10

            while countdown > 0:
                final_layout = Group(
                    final_progress.get_renderable(),
                    Panel(
                        render_colored_text(paragraph, typed),
                        title="[bold magenta]Typing Test[/bold magenta]",
                        border_style="blue",
                        box=SQUARE,
                        padding=(1, 2),
                    ),
                    Panel(
                        Text.from_markup(
                            f"[bold yellow]Results:[/bold yellow]\n"
                            f"• WPM: [green]{wpm:.2f}[/green]\n"
                            f"• Accuracy: [cyan]{accuracy:.2f}%[/cyan]"
                        ),
                        title="🎉 Test Summary",
                        border_style="bright_magenta",
                    ),
                    Align.center(
                        Text.from_markup(
                            f"[bold]Returning to prompt in [cyan]{countdown}[/cyan] seconds...[/bold]\n"
                            f"[dim]Press Ctrl+C to exit early[/dim]",
                            justify="center",
                        )
                    ),
                )
                live.update(final_layout)
                time.sleep(1)
                countdown -= 1

        console.print("[bold magenta]Test Completed![/bold magenta]")


if __name__ == "__main__":
    app()
