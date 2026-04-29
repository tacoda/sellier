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


def scaffold_harness(target: Path, *, force: bool = False) -> list[Path]:
    """Copy the harness into ``target``.

    Returns the list of files written, relative to ``target``.
    Raises ``HarnessAlreadyExistsError`` if the target already has harness files
    and ``force`` is not set.
    """
    target = Path(target)
    if not force and _harness_exists(target):
        raise HarnessAlreadyExistsError(
            f"{target} already contains a harness; pass force=True to overwrite"
        )

    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for relative, source in iter_template_files():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with resources.as_file(source) as concrete_source:
            shutil.copyfile(concrete_source, destination)
        written.append(relative)
    return written


def _harness_exists(target: Path) -> bool:
    return any((target / marker).exists() for marker in _HARNESS_MARKERS)
