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


def test_full_audit_zero_missed_zero_spurious() -> None:
    """Bulletproof guard: run the audit_coverage.py logic in-process and
    assert that every shape-matched token in every doctrine doc is in
    the registry, and vice versa.

    This is the test the user asked for — proof that "every line was
    covered" reduces to a single empty-set check.
    """
    import re

    snake_re = re.compile(
        r"\b("
        r"[a-z][a-z0-9_]*_"
        r"(?:report|receipt|packet|manifest|log|diff|envelope|result|map|status|ref)"
        r")\b"
    )
    pascal_re = re.compile(
        r"\b("
        r"[A-Z][A-Za-z0-9]*"
        r"(?:Packet|Receipt|Report|Manifest|Result|Diff|Envelope|Map|Log|Context|Token)"
        r")\b"
    )
    if not DOC_ROOT.exists():
        pytest.skip("L5 doctrine docs not present in this checkout")

    found: set[str] = set()
    for doc in sorted(DOC_ROOT.glob("00*.md")):
        text = doc.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for m in snake_re.finditer(line):
                found.add(m.group(1))
            for m in pascal_re.finditer(line):
                found.add(m.group(1))

    missed = sorted(found - ALL_OUTPUT_NAMES)
    spurious = sorted(ALL_OUTPUT_NAMES - found)
    assert missed == [], f"{len(missed)} doctrine tokens have no contract: {missed[:15]}"
    assert spurious == [], f"{len(spurious)} contracts have no doctrine reference: {spurious[:15]}"
    assert len(found) == len(ALL_OUTPUT_NAMES) == 838  # 819 prior + 19 from 00A.8
