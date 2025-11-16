"""Ensure the flattened test view stays synchronized with the source files."""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "tests_flat" / "manifest.json"


def _load_manifest() -> List[Tuple[Path, Path]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [
        (Path(entry["flat"]), Path(entry["source"]))
        for entry in manifest
    ]


def _extract_embedded_sources(flat_path: Path) -> Dict[str, str]:
    module_ast = ast.parse(flat_path.read_text(encoding="utf-8"))
    for node in module_ast.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "EMBEDDED_SOURCES":
                embedded = ast.literal_eval(node.value)
                if not isinstance(embedded, dict):
                    raise AssertionError("EMBEDDED_SOURCES must be a literal dictionary")
                return embedded
    raise AssertionError("Could not find EMBEDDED_SOURCES definition in flattened file")


def _source_pairs() -> Iterable[Tuple[Path, Path]]:
    return _load_manifest()


@pytest.mark.parametrize(
    ("flat_rel_path", "source_rel_path"),
    [
        pytest.param(flat, source, id=f"{flat}::{source}")
        for flat, source in _source_pairs()
    ],
)
def test_flat_view_matches_source_files(flat_rel_path: Path, source_rel_path: Path) -> None:
    """Every flattened block must mirror the exact source test file content."""
    flat_path = REPO_ROOT / flat_rel_path
    source_path = REPO_ROOT / source_rel_path

    embedded = _extract_embedded_sources(flat_path)
    key = source_rel_path.as_posix()
    assert key in embedded, f"{flat_rel_path} is missing embedded content for {source_rel_path}"

    flat_source = embedded[key]
    source_text = source_path.read_text(encoding="utf-8")
    assert flat_source == source_text, (
        f"Flattened block for {source_rel_path} diverges from source file."
    )


def test_manifest_matches_repository_tree() -> None:
    """If a new test is added to tests/, it must appear in the manifest."""
    manifest_sources = {entry[1].as_posix() for entry in _load_manifest()}
    repo_sources = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "tests").rglob("*.py")
        if "__pycache__" not in path.parts
    }
    assert manifest_sources == repo_sources, "Manifest is out of sync with tests/ tree"
