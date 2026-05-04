"""DS-4 Governance sentinels for integrated_single_action_run identity.

DS-4 was originally scoped as: "rename / demote integrated_single_action_run.py
to cert-fixture-only; ADR notes misleading name resolved; zero non-cert imports".

The DS-4 assumption ("no live callers outside cert fixtures") is INCORRECT.
Investigation found 3 active callers:
  1. apps_shared/spine_emission/adapter.py  — live production spine adapter
     (imports run_integrated_single_action + CHAIN_KIND as R4_CHAIN_KIND)
  2. agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py
     — imports TOOL_REGISTRY_RECORDS, _authorize_tool, _invoke_tool
  3. tools/certification/regen_r4_latest.py — cert tooling

The file is the canonical R4_SINGLE_ACTION runtime entrypoint, not a cert
fixture. DS-4 is therefore closed as: governance tests that lock this
correct identity and prevent accidental future demotion or rename that
would break the spine adapter.

Tests:
1. Module imports cleanly.
2. CHAIN_KIND == "R4_SINGLE_ACTION" (canonical identifier, must not drift).
3. ROUTE_FAMILY == "R4_SINGLE_ACTION".
4. __all__ contains the stable public surface (no silent removal).
5. run_integrated_single_action is callable.
6. TOOL_REGISTRY_RECORDS is a non-empty dict.
7. SpineRuntimeAdapter (apps_shared) imports from this module — live caller confirmed.
8. integrated_managed_workflow_real_run imports from this module — live caller confirmed.
9. File lives in agentic_core/runtime/entrypoints/ (canonical location, not cert/).

Plan: apps-rg-deferred-scope-followon-d4e1b9 DS-4.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "agentic_core" / "runtime" / "entrypoints"
    / "integrated_single_action_run.py"
)
ADAPTER_PATH = REPO_ROOT / "apps_shared" / "spine_emission" / "adapter.py"
MW_RUN_PATH = (
    REPO_ROOT
    / "agentic_core" / "runtime" / "entrypoints"
    / "integrated_managed_workflow_real_run.py"
)


@pytest.mark.governance
def test_integrated_single_action_run_file_in_runtime_entrypoints() -> None:
    """File must live in agentic_core/runtime/entrypoints/ — not in a cert/ subdirectory."""
    assert MODULE_PATH.exists(), f"Module file missing: {MODULE_PATH}"
    assert "cert" not in str(MODULE_PATH).replace("\\", "/").lower().split("/"), (
        f"integrated_single_action_run.py must not be inside a cert/ directory. "
        f"It is the canonical R4_SINGLE_ACTION runtime entrypoint. Path: {MODULE_PATH}"
    )


@pytest.mark.governance
def test_integrated_single_action_run_chain_kind() -> None:
    """CHAIN_KIND must equal R4_SINGLE_ACTION — canonical identifier must not drift."""
    from agentic_core.runtime.entrypoints.integrated_single_action_run import (
        CHAIN_KIND,
    )
    assert CHAIN_KIND == "R4_SINGLE_ACTION", (
        f"CHAIN_KIND drifted to {CHAIN_KIND!r}. "
        "SpineRuntimeAdapter imports this as R4_CHAIN_KIND — any change breaks the spine."
    )


@pytest.mark.governance
def test_integrated_single_action_run_route_family() -> None:
    """ROUTE_FAMILY must equal R4_SINGLE_ACTION."""
    from agentic_core.runtime.entrypoints.integrated_single_action_run import (
        ROUTE_FAMILY,
    )
    assert ROUTE_FAMILY == "R4_SINGLE_ACTION"


@pytest.mark.governance
def test_integrated_single_action_run_public_surface_stable() -> None:
    """__all__ must contain the stable public symbols that callers depend on."""
    from agentic_core.runtime.entrypoints import integrated_single_action_run as m

    required = {
        "run_integrated_single_action",
        "CHAIN_KIND",
        "ROUTE_FAMILY",
        "SEALED_L2_ARTIFACT_FILENAME",
        "TOOL_AUTHORIZATION_RECEIPT_FILENAME",
        "TOOL_REGISTRY_RECORDS",
    }
    missing = required - set(m.__all__)
    assert not missing, (
        f"integrated_single_action_run.__all__ is missing symbols: {missing}. "
        "Removing these breaks spine adapter and MW real-run imports."
    )


@pytest.mark.governance
def test_integrated_single_action_run_callable() -> None:
    """run_integrated_single_action must be a callable."""
    from agentic_core.runtime.entrypoints.integrated_single_action_run import (
        run_integrated_single_action,
    )
    assert callable(run_integrated_single_action)


@pytest.mark.governance
def test_integrated_single_action_run_tool_registry_non_empty() -> None:
    """TOOL_REGISTRY_RECORDS must be a non-empty dict (development surrogate)."""
    from agentic_core.runtime.entrypoints.integrated_single_action_run import (
        TOOL_REGISTRY_RECORDS,
    )
    assert isinstance(TOOL_REGISTRY_RECORDS, dict)
    assert TOOL_REGISTRY_RECORDS, "TOOL_REGISTRY_RECORDS must not be empty."
    for record in TOOL_REGISTRY_RECORDS.values():
        assert "tool_id" in record
        assert "required_capability" in record


@pytest.mark.governance
def test_spine_adapter_imports_from_integrated_single_action_run() -> None:
    """SpineRuntimeAdapter must import from integrated_single_action_run (live caller)."""
    assert ADAPTER_PATH.exists(), f"spine_emission/adapter.py missing: {ADAPTER_PATH}"
    src = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "integrated_single_action_run" in src, (
        "apps_shared/spine_emission/adapter.py no longer imports from "
        "integrated_single_action_run. This is a live production caller — "
        "any rename must update this import first."
    )
    assert "run_integrated_single_action" in src, (
        "spine adapter must import run_integrated_single_action"
    )


@pytest.mark.governance
def test_managed_workflow_real_run_imports_from_integrated_single_action_run() -> None:
    """integrated_managed_workflow_real_run must import from integrated_single_action_run."""
    assert MW_RUN_PATH.exists(), f"integrated_managed_workflow_real_run.py missing: {MW_RUN_PATH}"
    src = MW_RUN_PATH.read_text(encoding="utf-8")
    assert "integrated_single_action_run" in src, (
        "integrated_managed_workflow_real_run.py no longer imports from "
        "integrated_single_action_run. Any rename must update this import first."
    )
