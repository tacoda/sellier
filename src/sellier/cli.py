"""Typer CLI for sellier."""

from __future__ import annotations

from pathlib import Path

import typer

from sellier import __version__
from sellier.scaffolder import (
    HarnessAlreadyExistsError,
    iter_template_files,
    scaffold_harness,
)

app = typer.Typer(
    add_completion=False,
    help="Scaffold a Claude Code agent harness into any project.",
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
    dup: bool = typer.Option(
        False,
        "--dup",
        help="Write the .claude/ config to .claude-candidate/ for local testing; overwrites it if present.",
    ),
) -> None:
    """Scaffold CLAUDE.md and .claude/ into TARGET."""
    try:
        written = scaffold_harness(target, force=force, dup=dup, clean=clean)
    except HarnessAlreadyExistsError as error:
        typer.secho(str(error), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from error

    typer.echo(f"Wrote {len(written)} file(s) to {target}.")
    if dup:
        typer.echo("Candidate config written to .claude-candidate/.")
    else:
        typer.echo("Next: open the project in Claude Code and run `/saddle-up`.")


@app.command(name="list")
def list_templates() -> None:
    """List the templates that `init` will write."""
    for relative, _ in iter_template_files():
        typer.echo(str(relative))


@app.command()
def version() -> None:
    """Print the installed sellier version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
