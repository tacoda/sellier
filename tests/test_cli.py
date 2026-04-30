from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from sellier import __version__
from sellier.cli import app

runner = CliRunner()


def test_init_writes_claude_md_to_target(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "CLAUDE.md").is_file()


def test_init_exits_non_zero_when_target_already_has_harness(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing")

    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code != 0
    assert (tmp_path / "CLAUDE.md").read_text() == "existing"


def test_list_prints_template_paths() -> None:
    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.output
    assert "CLAUDE.md" in result.output
    assert ".claude/commands/saddle-up.md" in result.output


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0, result.output
    assert __version__ in result.output


def test_help_renders() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output
