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


def test_dup_writes_to_claude_candidate_and_skips_claude_md(tmp_path: Path) -> None:
    scaffold_harness(tmp_path, dup=True)

    candidate = tmp_path / ".claude-candidate"
    assert (candidate / "settings.json").is_file()
    assert (candidate / "commands").is_dir()
    assert not (tmp_path / ".claude").exists()
    assert not (tmp_path / "CLAUDE.md").exists()


def test_dup_overwrites_existing_candidate_folder(tmp_path: Path) -> None:
    candidate = tmp_path / ".claude-candidate"
    candidate.mkdir()
    stale = candidate / "stale.txt"
    stale.write_text("stale")

    scaffold_harness(tmp_path, dup=True)

    assert not stale.exists()
    assert (candidate / "settings.json").is_file()


def test_clean_removes_extra_files_in_claude_dir(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    stale = claude_dir / "stale-rule.md"
    stale.write_text("stale")

    scaffold_harness(tmp_path, clean=True)

    assert not stale.exists()
    assert (claude_dir / "settings.json").is_file()
    assert (tmp_path / "CLAUDE.md").is_file()


def test_clean_bypasses_existence_check(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing")

    scaffold_harness(tmp_path, clean=True)

    assert (tmp_path / "CLAUDE.md").read_text() != "existing"


def test_dup_ignores_existing_harness_without_force(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("existing")

    scaffold_harness(tmp_path, dup=True)

    assert (tmp_path / "CLAUDE.md").read_text() == "existing"
    assert (tmp_path / ".claude-candidate" / "settings.json").is_file()
