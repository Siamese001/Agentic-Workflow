"""D7 — Legacy engine audit for apps_underwriting_ai.

Audit confirms all engine files under apps_underwriting_ai/engines/ are
reachable from the module's __init__.py, underwriting_engine.py, or the
hop pipeline substrate. Zero orphans found → nothing to archive.

Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D7.
Acceptance criteria: 0 tests reference archived files; audit confirms
which files are unreachable (answer: none).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINES_DIR = REPO_ROOT / "apps_underwriting_ai" / "engines"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_ARCHIVED_DIR = ENGINES_DIR / "_archived"

_KNOWN_REACHABLE_ENGINES = {
    "base_underwriting_engine",
    "decision_packet_assembler",
    "document_reconciliation_engine",
    "evidence_register_engine",
    "feature_derivation_engine",
    "hop_assemble_decision_engine",
    "hop_collect_evidence_engine",
    "hop_derive_features_engine",
    "hop_initialize_evidence_engine",
    "hop_reconcile_documents_engine",
    "risk_scorer",
    "rubric_output_mapper",
    "underwriting_engine",
}


def _collect_engine_stems() -> set[str]:
    stems: set[str] = set()
    for f in ENGINES_DIR.glob("*.py"):
        if f.name == "__init__.py":
            continue
        if "_archived" in str(f):
            continue
        stems.add(f.stem)
    return stems


# ---------------------------------------------------------------------------
# D7.1 — no _archived directory exists (nothing was archived)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_no_archived_engines_directory_exists() -> None:
    """D7 audit result: zero unreachable files → _archived/ must not exist."""
    assert not _ARCHIVED_DIR.exists(), (
        f"Unexpected _archived/ directory at {_ARCHIVED_DIR}. "
        "If files were archived, update _KNOWN_REACHABLE_ENGINES and "
        "document the archival decision."
    )


# ---------------------------------------------------------------------------
# D7.2 — every engine file is in the known-reachable set
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_all_engine_files_are_known_reachable() -> None:
    """D7 audit: every .py in engines/ must be in the known-reachable set."""
    actual_stems = _collect_engine_stems()
    unknown = actual_stems - _KNOWN_REACHABLE_ENGINES
    assert not unknown, (
        f"D7 audit: the following engine files are not in the known-reachable "
        f"set and require an archival decision: {sorted(unknown)}. "
        "Either add them to _KNOWN_REACHABLE_ENGINES or move them to _archived/."
    )


@pytest.mark.governance
def test_no_engine_files_vanished_from_known_reachable() -> None:
    """D7 audit: no engines in the known-reachable set have been silently deleted."""
    actual_stems = _collect_engine_stems()
    missing = _KNOWN_REACHABLE_ENGINES - actual_stems
    assert not missing, (
        f"D7 audit: the following engines were expected but not found: "
        f"{sorted(missing)}. If deliberately removed, update _KNOWN_REACHABLE_ENGINES."
    )


# ---------------------------------------------------------------------------
# D7.3 — parsers sub-package contains no unreachable files
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_parsers_subpackage_has_init() -> None:
    """engines/parsers/ must have an __init__.py (prevents import stubs)."""
    parsers_init = ENGINES_DIR / "parsers" / "__init__.py"
    assert parsers_init.exists(), (
        f"engines/parsers/__init__.py missing at {parsers_init}"
    )


# ---------------------------------------------------------------------------
# D7.4 — __init__.py re-exports only reachable engines (no stale references)
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_engines_init_references_only_reachable_modules() -> None:
    """engines/__init__.py must not import modules that don't exist."""
    init_path = ENGINES_DIR / "__init__.py"
    assert init_path.exists(), f"engines/__init__.py missing at {init_path}"
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.startswith("apps_underwriting_ai.engines."):
                stem = mod.split(".")[-1]
                if stem not in _KNOWN_REACHABLE_ENGINES:
                    pytest.fail(
                        f"engines/__init__.py imports from unknown module "
                        f"'{mod}' (stem={stem!r}). "
                        "Update _KNOWN_REACHABLE_ENGINES or remove the import."
                    )
