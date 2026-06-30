"""W7 contract tests for ``check_app_registry_conformance.py``.

Locks in the W7 invariants:
1. The conformance gate exists, exits 0 on the current tree, and is
   importable for unit testing.
2. ``_discover_apps_packages`` excludes ``apps_shared`` (infrastructure).
3. The gate's ``_check_conformance`` returns ``(True, [])`` on the current
   tree (every governed/exception app properly classified).
4. Adding a hypothetical missing package to discovery raises a violation.
5. Adding a hypothetical orphan registry entry raises a violation.
6. ADR-076 is on disk and referenced by the gate.

Plan ``apps-runtime-first-principles-e6ba58`` W7.1.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_app_registry_conformance.py"
ADR_FILE = REPO_ROOT / "docs" / "architecture" / "adr" / "ADR-076-governed-or-exception-binary.md"


# ---------------------------------------------------------------------------
# Gate script + ADR exist
# ---------------------------------------------------------------------------


def test_conformance_gate_script_exists() -> None:
    """W7: the CI gate script is on disk at the canonical location."""
    assert GATE_SCRIPT.is_file(), f"Conformance gate not found: {GATE_SCRIPT}"


def test_adr_076_exists() -> None:
    """W7: ADR-076 is on disk."""
    assert ADR_FILE.is_file(), f"ADR-076 not found: {ADR_FILE}"


def test_adr_076_documents_governed_or_exception_binary() -> None:
    """W7: ADR-076 contains the binary statement and references the gate."""
    text = ADR_FILE.read_text(encoding="utf-8")
    assert "GOVERNED-or-EXCEPTION" in text
    assert "GovernedAppEntry" in text
    assert "FormalExceptionEntry" in text
    assert "check_app_registry_conformance" in text


# ---------------------------------------------------------------------------
# Gate exits 0 on current tree
# ---------------------------------------------------------------------------


def test_gate_passes_on_current_tree() -> None:
    """W7: the gate must exit 0 on the current repo state.

    All apps_* packages (excluding the infrastructure apps_shared) are
    properly classified in APP_REGISTRY.
    """
    proc = subprocess.run(
        [sys.executable, str(GATE_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    assert proc.returncode == 0, (
        f"Conformance gate failed unexpectedly:\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )
    assert "OK" in proc.stdout
    assert "GOVERNED-or-EXCEPTION binary holds" in proc.stdout


# ---------------------------------------------------------------------------
# Internal API contract
# ---------------------------------------------------------------------------


def test_discover_apps_packages_excludes_apps_shared() -> None:
    """W7: ``apps_shared`` is the substrate library and MUST be excluded
    from the governance discovery set."""
    from ops_scripts.ci.check_app_registry_conformance import (
        INFRASTRUCTURE_PACKAGES,
        _discover_apps_packages,
    )

    discovered = _discover_apps_packages()
    assert "apps_shared" not in discovered
    assert "apps_shared" in INFRASTRUCTURE_PACKAGES


def test_discover_apps_packages_includes_all_known_apps() -> None:
    """W7: the non-infrastructure apps must all be discovered."""
    from ops_scripts.ci.check_app_registry_conformance import _discover_apps_packages

    discovered = set(_discover_apps_packages())
    expected = {
        "apps_architect",
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_qna",
        "apps_research",
        "apps_rg",
        "apps_underwriting_ai",
    }
    missing = expected - discovered
    assert not missing, f"Discovery missed apps: {missing}"


def test_check_conformance_passes_on_current_tree() -> None:
    """W7: ``_check_conformance()`` returns (True, []) on the current tree."""
    from ops_scripts.ci.check_app_registry_conformance import _check_conformance

    ok, errors = _check_conformance()
    assert ok, f"Conformance check failed:\n  " + "\n  ".join(errors)
    assert errors == []


# ---------------------------------------------------------------------------
# Negative cases \u2014 simulated failure modes
# ---------------------------------------------------------------------------


def test_check_conformance_flags_missing_package() -> None:
    """W7: a hypothetical apps_<new> package without a registry row triggers a violation."""
    from ops_scripts.ci import check_app_registry_conformance as gate

    real_discover = gate._discover_apps_packages

    def _fake_discover() -> list[str]:
        return real_discover() + ["apps_hypothetical_new"]

    with patch.object(gate, "_discover_apps_packages", _fake_discover):
        ok, errors = gate._check_conformance()

    assert not ok
    assert any("apps_hypothetical_new" in line for line in errors)
    assert any("APP_REGISTRY" in line for line in errors)


def test_check_conformance_flags_orphan_registry_entry() -> None:
    """W7: a registry row for a nonexistent package triggers an orphan violation."""
    from apps_shared.integrations import app_registry as reg_mod
    from apps_shared.integrations.app_registry import (
        APP_REGISTRY,
        FormalExceptionEntry,
    )
    from ops_scripts.ci import check_app_registry_conformance as gate

    # Build an injected registry containing one orphan key.
    sample_orphan_key = "apps_orphaned_test_only"
    sample_orphan_entry = FormalExceptionEntry(
        app_name=sample_orphan_key,
        status=APP_REGISTRY["apps_eval"].status,  # reuse a valid status enum value
        exception_reason_code=APP_REGISTRY["apps_eval"].exception_reason_code,
        exception_reason="orphan probe \u2014 used only by this contract test",
        blocked_layers=("L0",),
        safe_layers=("conformance_metadata",),
        compensating_controls=("orphan probe",),
        review_cadence="annual",
        owner="test",
        target_phase="N/A",
        partial_adoption_module="test",
        partial_adoption_class="Test",
        proof_prefix="ORPH",
    )

    injected = dict(APP_REGISTRY)
    injected[sample_orphan_key] = sample_orphan_entry

    with patch.object(reg_mod, "APP_REGISTRY", injected):
        ok, errors = gate._check_conformance()

    assert not ok
    assert any(sample_orphan_key in line for line in errors)
