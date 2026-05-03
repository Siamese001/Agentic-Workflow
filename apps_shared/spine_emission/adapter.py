"""SpineRuntimeAdapter — bridge from apps_shared.spine_emission to agentic_core runtime.

Plan: apps-rg-runtime-cert-hardening-a3f8c2 W3.P1–P3.

This adapter provides a compatibility layer so apps_* can migrate from
standalone spine_emission to canonical agentic_core runtime entrypoints
without breaking changes to their EmissionConfig/governed_run usage.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

# agentic_core runtime imports (canonical spine entrypoints)
from agentic_core.runtime.entrypoints.integrated_single_action_run import (
    run_integrated_single_action,
    CHAIN_KIND as R4_CHAIN_KIND,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.L0_routing.types.route_contract_v15 import (
    V15RouteContract,
    ExecutionFormV15,
    RouteIdV15,
    ConfidenceClass,
    FreshnessClassV15,
    CachePolicyV15,
    SupportTargetV15,
    CostTierV15,
    FallbackEntryV15,
    RouteSLOV15,
    AuthorityScope,
    TelemetryKeysV15,
    SignaturesV15,
    WriteAuthority,
    CapabilityClass,
    SideEffectClass,
    SandboxClass,
)
# W3: L2 contracts imported but not yet fully wired — W4 will add real E1-E5 binding
from agentic_core.L2_execution.types.l2_v4_contracts import (
    WorkOrderInputs,
    ExecutionForm,
    TaskSpec,
)

# Local imports (same package)
from apps_shared.spine_emission.context import EmissionConfig, GovernedRun
from apps_shared.spine_emission.contracts import (
    RouteContract as LegacyRouteContract,
    L2ExecutionReceipt as LegacyL2Receipt,
    ExitReviewPacket,
)

_logger = logging.getLogger(__name__)


class SpineRuntimeAdapter:
    """Adapter translating spine_emission calls to agentic_core runtime.

    Provides both imperative (run_once) and context-manager (governed_run)
    interfaces for backward compatibility with existing apps_* usage.

    Migration path:
      1. Import SpineRuntimeAdapter alongside existing governed_run usage.
      2. Switch to adapter.governed_run() when ready.
      3. Eventually call agentic_core entrypoints directly.
    """

    def __init__(
        self,
        cfg: EmissionConfig,
        *,
        prefer_canonical: bool = False,
        repo_root: Path | None = None,
    ) -> None:
        """Initialize adapter with spine_emission config.

        Args:
            cfg: The EmissionConfig describing app_name, routes, etc.
            prefer_canonical: If True, use agentic_core directly; if False,
                delegate to legacy spine_emission (current default).
            repo_root: Optional repo root for path resolution.
        """
        self.cfg = cfg
        self.prefer_canonical = prefer_canonical
        self.repo_root = repo_root or Path.cwd()
        self._run_result: IntegratedRunResult | None = None

    def run_once(self, cli_args: list[str] | None = None) -> dict[str, Any]:
        """Execute a single run using canonical runtime if prefer_canonical else legacy.

        Args:
            cli_args: Optional CLI args to pass through.

        Returns:
            Dict with receipt artifacts (RouteContract, L2 receipt, Exit packet).
        """
        if not self.prefer_canonical:
            # W3: Legacy path returns placeholder receipts without full emission
            # (full spine_emission requires real route registry files)
            return {
                "route_contract": {"_placeholder": True, "legacy": True},
                "l2_execution_receipt": {"_placeholder": True, "legacy": True},
                "exit_review_packet": {"_placeholder": True, "legacy": True},
                "canonical": False,
            }

        # Canonical path: construct real agentic_core runtime inputs
        route_contract = self._build_canonical_route_contract()
        l2_receipt = self._build_canonical_l2_receipt(route_contract)
        exit_packet = self._build_canonical_exit_packet(l2_receipt)

        # Serialize V15RouteContract (dataclass) to dict
        from dataclasses import asdict
        return {
            "route_contract": asdict(route_contract),
            "l2_execution_receipt": l2_receipt,
            "exit_review_packet": exit_packet.model_dump(),
            "canonical": True,
        }

    def governed_run(
        self,
        *,
        cli_args: list[str] | None = None,
    ) -> "AdapterGovernedRun":
        """Return a context manager compatible with spine_emission.GovernedRun.

        Usage:
            adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)
            with adapter.governed_run(cli_args=[...]) as run:
                run.mark_stage("generate_resume", "ok")
        """
        return AdapterGovernedRun(self, cli_args=cli_args or [])

    # ------------------------------------------------------------------
    # Canonical builders (private)
    # ------------------------------------------------------------------

    def _build_canonical_route_contract(self) -> V15RouteContract:
        """Construct a canonical v15 RouteContract from EmissionConfig (W3 skeleton)."""
        # Map legacy execution_form to canonical ExecutionFormV15
        form_map = {
            "SINGLE_STEP": ExecutionFormV15.SINGLE_STEP,
            "MANAGED_WORKFLOW": ExecutionFormV15.MANAGED_WORKFLOW,
            "TERMINAL_SHORTCIRCUIT": ExecutionFormV15.TERMINAL_SHORTCIRCUIT,
        }
        legacy_form = self.cfg.expected_execution_form
        canonical_form = form_map.get(legacy_form, ExecutionFormV15.SINGLE_STEP)

        # W3: Minimal valid V15RouteContract (full wiring in W4)
        # Note: All required V15RouteContract fields populated per v15 schema
        return V15RouteContract(
            contract_version="1.0.0",
            route_id=RouteIdV15.R4_SINGLE_ACTION,
            execution_form=canonical_form,
            confidence_score=0.95,
            confidence_class=ConfidenceClass.HIGH,
            reason_codes=("ACTION_LOW_RISK",),
            freshness_class=FreshnessClassV15.STATIC,
            cache_policy=CachePolicyV15.BYPASS_CACHE,
            support_target=SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_S,
            fallback_chain=(FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),),
            slo=RouteSLOV15(
                max_latency_ms=30000,
                max_cost=1.0,
                max_tokens=4000,
                max_retrieval_passes=3,
                max_graph_hops=5,
                max_tool_calls=10,
                max_iterations=5,
                reserve_for_exit_eval=500,
            ),
            authority=AuthorityScope(
                tenant_scope="test_tenant",
                acl_scope=("test",),
                region_scope="us-east-1",
                capability_class=CapabilityClass.READ_ONLY,
                side_effect_class=SideEffectClass.PURE,
                sandbox_class=SandboxClass.NO_SANDBOX,
                write_authority=WriteAuthority.NONE_UNTIL_UWG,
            ),
            telemetry_keys=TelemetryKeysV15(
                trace_root=f"trc-{self.cfg.app_name}-test",
                route_span_id="span-test",
                route_digest="W3_DIGEST",
                policy_hash="W3_POLICY",
                blueprint_hash="W3_BLUEPRINT",
                snapshot_id="W3_SNAPSHOT",
                replay_key="W3_REPLAY",
                route_telemetry_event_id="evt-test",
            ),
            signatures=SignaturesV15(
                manifest_hash="W3_MANIFEST_HASH",
                deterministic_route_digest="W3_PLACEHOLDER_DIGEST",
                hmac_sig="W3_PLACEHOLDER_HMAC",
            ),
        )

    def _build_canonical_l2_receipt(
        self,
        route_contract: V15RouteContract,
    ) -> dict[str, Any]:
        """Construct a canonical v4 L2 ExecutionReceipt (W3 skeleton).

        W4 will upgrade this to return a real L2 dataclass with E1-E5 phases.
        """
        # W3: Return minimal dict shape; W4 will wire real L2 receipt classes
        return {
            "route_contract_id": "W3_PLACEHOLDER_RCID",
            "execution_form": route_contract.execution_form.value,
            "e1_work_order": WorkOrderInputs(
                execution_form=ExecutionForm.SINGLE_STEP,
                task_spec=TaskSpec(intent="W3 skeleton"),
            ),
            "e5_exec_output": {"_placeholder": True},  # W4: real E3 attempt output
            "_placeholder": True,
        }

    def _build_canonical_exit_packet(
        self,
        l2_receipt: dict[str, Any],
    ) -> ExitReviewPacket:
        """Construct ExitReviewPacket from L2 receipt."""
        # Bridge to legacy ExitReviewPacket shape for apps_rg compatibility
        return ExitReviewPacket(
            app_name=self.cfg.app_name,
            run_id="",  # Populated by caller
            request_id="",
            trace_root="",
            exit_review_packet_id="",
            route_contract_id=l2_receipt["route_contract_id"],
            x3_disposition="EXIT_OK",  # Simplified; real X3 from L5 exit_eval
            disposition_reason="Adapter bridge: canonical L2 → legacy Exit",
            subprocess_exit_code=0,
            failed_stages=[],
            sealed=True,
        )

    def _collect_legacy_receipts(self, gr: GovernedRun) -> dict[str, Any]:
        """Collect receipts from legacy GovernedRun execution."""
        return {
            "route_contract": {},  # From gr._staging
            "l2_execution_receipt": {},
            "exit_review_packet": {},
            "canonical": False,
        }


class AdapterGovernedRun:
    """Context manager mimicking spine_emission.GovernedRun for adapter use.

    Implements the same interface (mark_stage, set_subprocess_exit_code, etc.)
    but routes to agentic_core when prefer_canonical=True.
    """

    def __init__(
        self,
        adapter: SpineRuntimeAdapter,
        cli_args: list[str],
    ) -> None:
        self._adapter = adapter
        self._cli_args = cli_args
        self._stage_outcomes: dict[str, str] = {}
        self._failed_stages: list[str] = []
        self._exit_code: int | None = None
        self._run_dir: Path | None = None

    def __enter__(self) -> "AdapterGovernedRun":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        # Emit receipts on exit (success or exception)
        self._emit_receipts()

    def mark_stage(self, stage_name: str, outcome: str) -> None:
        """Record stage outcome; non-ok adds to failed_stages."""
        self._stage_outcomes[stage_name] = outcome
        if outcome != "ok":
            self._failed_stages.append(stage_name)

    def set_subprocess_exit_code(self, code: int) -> None:
        """Set the subprocess exit code for X3 computation."""
        self._exit_code = code

    @property
    def run_dir(self) -> Path | None:
        """Return the run directory for HITL/receipt evaluation."""
        return self._run_dir

    def set_run_dir(self, run_dir: Path) -> None:
        """Late-bound run directory (legacy compat)."""
        self._run_dir = run_dir

    def span(self, name: str):
        """Return a context manager for tracing (legacy compat).

        W4: This is a no-op context manager. Full OTEL span integration
        will land in W5 when agentic_core OTEL wiring is complete.
        """
        from contextlib import nullcontext
        return nullcontext()

    def _emit_receipts(self) -> None:
        """Emit receipts to agentic_core or legacy paths."""
        if self._adapter.prefer_canonical:
            # W4: Route to agentic_core emitter
            _logger.debug("[adapter] Canonical receipt emit (W4 impl)")
        else:
            # Legacy path: receipts already emitted by spine_emission
            _logger.debug("[adapter] Legacy receipt emit (no-op)")


__all__ = [
    "SpineRuntimeAdapter",
    "AdapterGovernedRun",
]
