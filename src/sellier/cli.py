"""Typer CLI for sellier."""

from __future__ import annotations

from pathlib import Path

import typer

from sellier import __version__
from sellier.scaffolder import (
    HarnessAlreadyExistsError,
    scaffold_harness,
)

app = typer.Typer(
    add_completion=False,
    help="Scaffold a Claude Code agent project harness into any project.",
    no_args_is_help=True,
)


@app.command()
def init(
    target: Path = typer.Argument(
        Path.cwd(),
        help="Project directory to scaffold the harness into.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing harness files in place (per-file).",
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Remove the existing .claude/ directory before writing so the result matches the templates exactly.",
    ),
) -> None:
    """Scaffold CLAUDE.md and .claude/ into TARGET."""
    try:
        written = scaffold_harness(target, force=force, clean=clean)
    except HarnessAlreadyExistsError as error:
        typer.secho(str(error), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from error

    typer.echo(f"Wrote {len(written)} file(s) to {target}.")
    typer.echo("Next: open the project in Claude Code and run `/saddle-up`.")


@app.command()
def version() -> None:
    """Print the installed sellier version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
