"""Doctrine alignment test.

Re-extracts every named output from the 8 docs under
``docs/reference/00_L5_Policy_Plane`` and asserts that every name is
present in ``CONTRACT_REGISTRY`` (and vice versa).

This is the canonical guard that the contracts package stays in sync
with the doctrine documents.
"""

from __future__ import annotations

import pathlib

import pytest

from agentic_core.L5_safety.contracts import ALL_OUTPUT_NAMES
from tools.l5_contracts.extract_outputs import extract

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
DOC_ROOT = REPO_ROOT / "docs" / "reference" / "00_L5_Policy_Plane"


@pytest.fixture(scope="module")
def doctrine_names() -> set[str]:
    if not DOC_ROOT.exists():
        pytest.skip("L5 doctrine docs not present in this checkout")
    mapping = extract()
    return {n for v in mapping.values() for n in v}


def test_every_doctrine_name_has_a_contract(doctrine_names: set[str]) -> None:
    missing = sorted(doctrine_names - ALL_OUTPUT_NAMES)
    assert missing == [], (
        f"{len(missing)} doctrine outputs lack contracts. Run "
        f"`python tools/l5_contracts/generate_contracts.py` to regenerate. "
        f"First missing: {missing[:10]}"
    )


def test_no_orphan_contracts(doctrine_names: set[str]) -> None:
    orphans = sorted(ALL_OUTPUT_NAMES - doctrine_names)
    assert orphans == [], f"{len(orphans)} contracts are not referenced in any doctrine doc: {orphans[:10]}"
