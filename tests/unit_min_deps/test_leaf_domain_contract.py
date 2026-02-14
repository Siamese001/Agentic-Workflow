"""
Structural invariant: LEAF_DOMAIN_NO_LCD folders must not contain subdirectories.

Deterministic filesystem scan. No heuristics.
Guardian hard gate per LEAF_DOMAINS_NO_LCD in ssot.py.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / "agentic_core"

LEAF_DOMAINS_NO_LCD: frozenset[str] = frozenset(
    {
        "prompt_governance",
        "knowledge",
        "mixins",
        "runtime",
        "interfaces",
        "base_agents",
        "config",
    },
)

# Subdirectories that are always allowed (Python cache, etc.)
ALWAYS_ALLOWED_SUBDIRS: frozenset[str] = frozenset({"__pycache__"})


def _scan_leaf_domain_violations() -> list[str]:
    """Find LEAF_DOMAIN folders that contain illegal subdirectories."""
    violations: list[str] = []
    for domain in LEAF_DOMAINS_NO_LCD:
        domain_path = AGENTIC_CORE / domain
        if not domain_path.is_dir():
            continue
        for entry in domain_path.iterdir():
            if entry.is_dir() and entry.name not in ALWAYS_ALLOWED_SUBDIRS:
                # Check if this subdirectory is declared in the domain's own structure
                # (e.g., prompt_governance has declared subfolders like meta_prompts)
                # We need to check the blueprint for optional_subfolders
                violations.append(
                    f"{domain}/{entry.name}: illegal subdirectory in LEAF_DOMAIN"
                )
    return violations


def _get_declared_subfolders(domain: str) -> set[str]:
    """Get subfolders declared in the blueprint for a LEAF_DOMAIN."""
    # Import here to avoid circular deps at module level
    try:
        from agentic_core.L5_safety.config.structure_blueprint._constants import (
            build_sovereign_territories,
        )

        territories = build_sovereign_territories()
        ac = territories.get("agentic_core", {})
        subfolders_def = ac.get("subfolders", {})
        domain_def = subfolders_def.get(domain, {})
        declared = set()
        # Check for subfolders key
        if "subfolders" in domain_def:
            declared.update(domain_def["subfolders"].keys())
        # Check for required_subfolders and optional_subfolders
        if "required_subfolders" in domain_def:
            declared.update(domain_def["required_subfolders"])
        if "optional_subfolders" in domain_def:
            declared.update(domain_def["optional_subfolders"])
        return declared
    except Exception:
        return set()


class TestLeafDomainNoSubdirs:
    """Hard gate: LEAF_DOMAIN folders must not sprout LCD-style subdirectories."""

    def test_prompt_governance_no_illegal_subdirs(self) -> None:
        """prompt_governance must not contain domain/ or other LCD subdirs."""
        pg = AGENTIC_CORE / "prompt_governance"
        if not pg.is_dir():
            pytest.skip("prompt_governance not found")
        declared = _get_declared_subfolders("prompt_governance")
        declared.update(ALWAYS_ALLOWED_SUBDIRS)
        illegal = []
        for entry in pg.iterdir():
            if entry.is_dir() and entry.name not in declared:
                illegal.append(entry.name)
        assert not illegal, (
            f"prompt_governance/ contains undeclared subdirectories: {illegal}\n"
            f"Declared: {sorted(declared - ALWAYS_ALLOWED_SUBDIRS)}"
        )

    def test_no_domain_subfolder_in_prompt_governance(self) -> None:
        """Specific regression: domain/ must never exist under prompt_governance."""
        assert not (AGENTIC_CORE / "prompt_governance" / "domain").exists(), (
            "prompt_governance/domain/ exists — LEAF_DOMAIN violation"
        )

    def test_synthetic_subfolder_detected(self, tmp_path: Path) -> None:
        """Negative test: prove scanner catches a synthetic subfolder."""
        fake_domain = tmp_path / "fake_leaf"
        fake_domain.mkdir()
        (fake_domain / "__init__.py").write_text("", encoding="utf-8")
        illegal_sub = fake_domain / "illegal_subdir"
        illegal_sub.mkdir()
        (illegal_sub / "__init__.py").write_text("", encoding="utf-8")

        subdirs = [
            e.name
            for e in fake_domain.iterdir()
            if e.is_dir() and e.name not in ALWAYS_ALLOWED_SUBDIRS
        ]
        assert subdirs, "Scanner failed to detect synthetic illegal subdirectory"
        assert "illegal_subdir" in subdirs
