"""W3.P3 — SpineRuntimeAdapter import and skeleton verification.

Plan: apps-rg-runtime-cert-hardening-a3f8c2 W3.P3.

Tests that adapter.py imports resolve and the class skeleton is functional.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# Ensure repo root on path for adapter imports
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if TYPE_CHECKING:
    from apps_shared.spine_emission.adapter import SpineRuntimeAdapter


class TestSpineRuntimeAdapterImports:
    """Verify adapter module imports and basic structure."""

    def test_adapter_module_imports(self) -> None:
        """adapter.py imports without raising."""
        from apps_shared.spine_emission import adapter
        assert hasattr(adapter, "SpineRuntimeAdapter")
        assert hasattr(adapter, "AdapterGovernedRun")

    def test_spine_runtime_adapter_class_exists(self) -> None:
        """SpineRuntimeAdapter class is importable and constructible."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_app",
            entrypoint_command="python -m test_app",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W3 test skeleton",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=False)
        assert adapter.cfg.app_name == "test_app"
        assert adapter.prefer_canonical is False

    def test_adapter_governed_run_context_manager(self) -> None:
        """AdapterGovernedRun works as context manager."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter, AdapterGovernedRun
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_app",
            entrypoint_command="python -m test_app",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W3 test skeleton",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=False)

        with adapter.governed_run(cli_args=["--test"]) as run:
            run.mark_stage("test_stage", "ok")
            run.set_subprocess_exit_code(0)
            # In legacy mode, this is a no-op context manager

    def test_agentic_core_imports_resolve(self) -> None:
        """agentic_core imports inside adapter resolve correctly."""
        from apps_shared.spine_emission.adapter import (
            run_integrated_single_action,
            run_integrated_safe_reuse,
            compute_artifact_hash,
        )
        # Functions are imported; we don't call them (would need full runtime setup)
        assert callable(run_integrated_single_action)
        assert callable(run_integrated_safe_reuse)
        assert callable(compute_artifact_hash)

    def test_canonical_route_contract_v15_import(self) -> None:
        """V15RouteContract and enums import from agentic_core."""
        from apps_shared.spine_emission.adapter import (
            V15RouteContract,
            ExecutionFormV15,
            RouteIdV15,
        )
        assert ExecutionFormV15.SINGLE_STEP.value == "SINGLE_STEP"
        assert RouteIdV15.R4_SINGLE_ACTION.value == "R4_SINGLE_ACTION"

    def test_canonical_l2_contracts_import(self) -> None:
        """L2 v4 contracts import from agentic_core (WorkOrderInputs placeholder for W4)."""
        from apps_shared.spine_emission.adapter import (
            WorkOrderInputs,
            ExecutionForm,
            TaskSpec,
        )
        # Can instantiate minimal contracts (W4 will wire real E1-E5 phases)
        wo = WorkOrderInputs(
            execution_form=ExecutionForm.SINGLE_STEP,
            task_spec=TaskSpec(intent="test"),
        )
        assert wo is not None
        assert wo.execution_form == ExecutionForm.SINGLE_STEP

    def test_legacy_contracts_still_importable(self) -> None:
        """Legacy contracts remain importable for backward compatibility."""
        from apps_shared.spine_emission.contracts import (
            RouteContract as LegacyRouteContract,
            L2ExecutionReceipt as LegacyL2Receipt,
            ExitReviewPacket,
        )
        # These are pydantic models with the legacy shape
        # Check model_fields for Pydantic v2 models
        assert "route_contract_id" in LegacyRouteContract.model_fields
        assert "l2_receipt_id" in LegacyL2Receipt.model_fields


class TestAdapterPreferCanonicalFalse:
    """Test adapter behavior when prefer_canonical=False (legacy delegation)."""

    def test_run_once_returns_legacy_shape(self) -> None:
        """run_once with prefer_canonical=False returns legacy-style receipts."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_app",
            entrypoint_command="python -m test_app",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W3 test skeleton",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=False)
        result = adapter.run_once(cli_args=[])

        assert "canonical" in result
        assert result["canonical"] is False
        # Legacy path returns placeholder dicts (real receipts emitted by spine_emission)
        assert "route_contract" in result
        assert "l2_execution_receipt" in result
        assert "exit_review_packet" in result


class TestAdapterPreferCanonicalTrue:
    """Test adapter behavior when prefer_canonical=True (canonical wiring)."""

    def test_run_once_returns_canonical_shape(self) -> None:
        """run_once with prefer_canonical=True returns canonical receipt shapes."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_app",
            entrypoint_command="python -m test_app",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W3 test skeleton",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)
        result = adapter.run_once(cli_args=[])

        assert result["canonical"] is True
        assert "route_contract" in result
        assert "l2_execution_receipt" in result
        assert "exit_review_packet" in result
