"""Copy harness templates into a target project directory."""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

_PACKAGE = "sellier"
_TEMPLATES_DIR = "templates"
_HARNESS_MARKERS = ("CLAUDE.md", ".claude")
_CLAUDE_DIR = ".claude"
_CLAUDE_CANDIDATE_DIR = ".claude-candidate"


class HarnessAlreadyExistsError(FileExistsError):
    """Raised when the target already contains harness files and force is not set."""


def template_root() -> Traversable:
    return resources.files(_PACKAGE) / _TEMPLATES_DIR


def iter_template_files() -> Iterator[tuple[Path, Traversable]]:
    """Yield ``(relative_path, source)`` for each file shipped in the templates."""
    yield from _walk(template_root(), Path())


def _walk(node: Traversable, prefix: Path) -> Iterator[tuple[Path, Traversable]]:
    for child in node.iterdir():
        relative = prefix / child.name
        if child.is_dir():
            yield from _walk(child, relative)
        else:
            yield relative, child


def scaffold_harness(
    target: Path,
    *,
    force: bool = False,
    dup: bool = False,
    clean: bool = False,
) -> list[Path]:
    """Copy the harness into ``target``.

    Returns the list of files written, relative to ``target``.
    Raises ``HarnessAlreadyExistsError`` if the target already has harness files
    and none of ``force``, ``dup``, or ``clean`` is set.

    When ``dup`` is set, the ``.claude/`` config is written to
    ``.claude-candidate/`` instead, overwriting any existing candidate folder.

    When ``clean`` is set, the existing ``.claude/`` directory at the target is
    removed before writing, so the result matches the templates exactly.
    """
    target = Path(target)
    if not force and not dup and not clean and _harness_exists(target):
        raise HarnessAlreadyExistsError(
            f"{target} already contains a harness; pass force=True to overwrite"
        )

    target.mkdir(parents=True, exist_ok=True)

    if dup:
        candidate_root = target / _CLAUDE_CANDIDATE_DIR
        if candidate_root.exists():
            shutil.rmtree(candidate_root)
    elif clean:
        claude_root = target / _CLAUDE_DIR
        if claude_root.exists():
            shutil.rmtree(claude_root)

    written: list[Path] = []
    for relative, source in iter_template_files():
        if dup and relative.parts and relative.parts[0] == _CLAUDE_DIR:
            relative = Path(_CLAUDE_CANDIDATE_DIR, *relative.parts[1:])
        elif dup:
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with resources.as_file(source) as concrete_source:
            shutil.copyfile(concrete_source, destination)
        written.append(relative)
    return written


def _harness_exists(target: Path) -> bool:
    return any((target / marker).exists() for marker in _HARNESS_MARKERS)
