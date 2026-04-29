from __future__ import annotations

import re
from pathlib import Path

import pytest

from sellier.scaffolder import (
    HarnessAlreadyExistsError,
    iter_template_files,
    scaffold_harness,
)


def test_scaffolds_claude_md_at_target_path(tmp_path: Path) -> None:
    scaffold_harness(tmp_path)

    assert (tmp_path / "CLAUDE.md").is_file()


def test_scaffolds_claude_subdirectories(tmp_path: Path) -> None:
    scaffold_harness(tmp_path)

    claude_dir = tmp_path / ".claude"
    assert (claude_dir / "rules").is_dir()
    assert (claude_dir / "agents").is_dir()
    assert (claude_dir / "commands").is_dir()
    assert (claude_dir / "skills").is_dir()


def test_refuses_to_overwrite_existing_claude_md_without_force(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing content")

    with pytest.raises(HarnessAlreadyExistsError):
        scaffold_harness(tmp_path)

    assert (tmp_path / "CLAUDE.md").read_text() == "existing content"


def test_force_overwrites_existing_files(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing content")

    scaffold_harness(tmp_path, force=True)

    assert (tmp_path / "CLAUDE.md").read_text() != "existing content"


def test_creates_target_path_if_missing(tmp_path: Path) -> None:
    target = tmp_path / "new_project"

    scaffold_harness(target)

    assert (target / "CLAUDE.md").is_file()


def test_templates_contain_placeholder_tokens() -> None:
    pattern = re.compile(r"\[[A-Z][A-Z0-9_]+\]")
    files_with_placeholders = [
        relative
        for relative, source in iter_template_files()
        if pattern.search(source.read_text(encoding="utf-8"))
    ]

    assert files_with_placeholders, (
        "expected at least one template with a [PLACEHOLDER] token"
    )


def test_scaffolded_files_match_template_bytes(tmp_path: Path) -> None:
    scaffold_harness(tmp_path)

    for relative, source in iter_template_files():
        scaffolded = tmp_path / relative
        assert scaffolded.read_bytes() == source.read_bytes(), relative
