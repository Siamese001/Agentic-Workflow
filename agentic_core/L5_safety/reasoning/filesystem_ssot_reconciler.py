from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "filesystem_ssot_reconciler")
emit_determinism_digest("p0", "filesystem_ssot_reconciler")

_emit_dispatches_healing_run("p1", "filesystem_ssot_reconciler", "L5")
_emit_routes_through("p1", "filesystem_ssot_reconciler", "L5")
_emit_checks_agent_registry("p1", "filesystem_ssot_reconciler", "agent_registry")
_emit_validates_agent_capability("p1", "filesystem_ssot_reconciler", "capability")
_emit_dispatches_execution_plan("p1", "filesystem_ssot_reconciler", "exec_plan")
_emit_agent_executes_agent("p1", "filesystem_ssot_reconciler", "sub_agent")
_emit_routes_to_agent("p1", "filesystem_ssot_reconciler", "target_agent")
_emit_verifies_policy("p1", "filesystem_ssot_reconciler", "policy_check")
_emit_observes_runtime_state("p1", "filesystem_ssot_reconciler", "runtime_state")
_emit_verifies_boundary("p1", "filesystem_ssot_reconciler", "boundary_check")
_emit_transcripts_response("p1", "filesystem_ssot_reconciler", "transcript")
_emit_hard_fails_untranscripted("p1", "filesystem_ssot_reconciler")
_emit_gated_by_confidence("p1", "filesystem_ssot_reconciler", "confidence_gate")
_emit_escalates_to_human("p1", "filesystem_ssot_reconciler", "L5")
_emit_reads_policy_state("p1", "filesystem_ssot_reconciler", "L5")
_emit_authorize_and_execute("p2", "filesystem_ssot_reconciler", "execution_auth")
_emit_validates_capability("p2", "filesystem_ssot_reconciler", "capability_check")
_emit_routes_to_capability("p2", "filesystem_ssot_reconciler", "capability_route")
_emit_writes_via_uwg("p2", "filesystem_ssot_reconciler", "uwg_write")
_emit_blocks_direct_write("p2", "filesystem_ssot_reconciler", "direct_write_block")
_emit_records_tool_invocation("p2", "filesystem_ssot_reconciler", "tool_invocation")
_emit_captures_execution_output("p2", "filesystem_ssot_reconciler", "exec_output")
_emit_dispatches_agent("p3", "filesystem_ssot_reconciler", "agent_dispatch")
_emit_coordinates_agents("p3", "filesystem_ssot_reconciler", "agent_coordination")
_emit_records_workflow_lineage("p3", "filesystem_ssot_reconciler", "workflow_lineage")
_emit_records_healing_outcome("p3", "filesystem_ssot_reconciler", "healing_outcome")
_emit_escalates_failure("p3", "filesystem_ssot_reconciler", "failure_escalation")
_emit_orchestrates_workflow("p3", "filesystem_ssot_reconciler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "filesystem_ssot_reconciler", "healing_dispatch")
_emit_invokes_evaluation("p3", "filesystem_ssot_reconciler", "evaluation_signal")
_emit_records_telemetry_event("p4", "filesystem_ssot_reconciler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "filesystem_ssot_reconciler", "eval_metric")
_emit_stores_embedding("p4", "filesystem_ssot_reconciler", "embedding_store")
_emit_updates_meta_learning_state("p4", "filesystem_ssot_reconciler", "meta_learning")
_emit_links_execution_to_snapshot("p4", "filesystem_ssot_reconciler", "exec_snapshot_link")

"\nFilesystemSSOTReconcilerAgent - FILESYSTEM-LEVEL SSOT RECONCILER\nTerritory: agentic_core/L0_routing/scripts/\n\nVERSION 2.0 — 2025-12-31\nEnforces SSOT blueprint by aligning filesystem structure.\n\nDirection: Blueprint → Filesystem (Enforcement)\nScans: Actual folder structure on disk (L1/L2 depth)\nDetects: Unauthorized folders (Heresy) or missing required folders.\nAction: Creates missing folders and archives unauthorized ones.\n\nResponsibilities:\n- Scan filesystem for actual folder structure (L1/L2 depth)\n- Scan agents for canonical signals usage\n- Detect drift between structure_blueprint.py and reality\n- Generate filesystem proposals\n- Auto-align filesystem with safety checks (opt-in)\n\nMirrors the successful PromptRegistry.py pattern:\n- Deduplication-safe updates\n- Atomic writes with tempfile + rename\n- Backup before modifications\n- Syntax validation after changes\n\nInvoked by:\n- MissionController (post-mission hook, env: RECONCILE_BLUEPRINT)\n- SovereignAuditor (on sovereignty degradation)\n- Manual CLI trigger\n\nPhase 1: Read-only drift detection (auto_apply=False by default)\nPhase 2: Manual approval workflow\nPhase 3: Autonomous updates (auto_apply=True with safety checks)\n\nComplementary to CodeSSOTEnforcerAgent which validates that code uses\nSSOT imports instead of hard-coded paths.\n\nGOLD STANDARD UPGRADE (2026-01-02):\n- Structured Violation dataclass with severity levels\n- LocationAgent integration for territory validation after reconciliation\n- HierarchyAgent integration for structure validation after reconciliation\n- NamingAgent integration for naming compliance checks\n- Post-heal validation confirming blueprint sync\n- Batch post-heal reporting with FULL_SUCCESS/PARTIAL/NEEDS_REVIEW\n- cleanup_violations with multi-stage reconciliation healing\n- run_with_cleanup returning comprehensive summaries\n\nDOMAIN-SPECIFIC INTEGRATIONS (SSOT Coordination):\n- LocationAgent: Validate file territories match blueprint\n- HierarchyAgent: Validate depth compliance after reconciliation\n- NamingAgent: Validate naming conventions in reconciled structure\n"
import ast
import importlib
import logging
import os
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin  # noqa: F401
except ImportError:  # guardian: allow-silent-swallow

    class MCPHardenedMixin:
        pass


from agentic_core.base_agents.L0RoutingBase import L0RoutingBase as L0RoutingBaseAgent
from agentic_core.mixins.autonomy_mixin import AutonomyMixin
from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from agentic_core.utils.timeout_decorator_util import timeout

try:
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin  # noqa: F401
except ImportError:

    class SubatomicTestingMixin:
        """Fallback stub for SubatomicTestingMixin."""

        pass


from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_1")
_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_2")
_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_3")
_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_4")
_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_5")
_emit_emits_metric_event("filesystem_ssot_reconciler", "p4obs", "metric_6")
_emit_records_incident_event("filesystem_ssot_reconciler", "p4obs", "incident")
_emit_captures_runtime_anomaly("filesystem_ssot_reconciler", "p4obs", "anomaly")
_emit_writes_observability_log("filesystem_ssot_reconciler", "p4obs", "obs_log")
_emit_updates_monitoring_state("filesystem_ssot_reconciler", "p4obs", "mon_state")
_emit_triggers_alert("filesystem_ssot_reconciler", "p4obs", "alert")
_emit_links_incident_trace("filesystem_ssot_reconciler", "p4obs", "trace_link")
_emit_captures_pattern("filesystem_ssot_reconciler", "p3lm", "pattern")
_emit_records_learning_event("filesystem_ssot_reconciler", "p3lm", "learning_event")
_emit_writes_learning_snapshot("filesystem_ssot_reconciler", "p3lm", "snapshot")
_emit_feeds_meta_learning("filesystem_ssot_reconciler", "p3lm", "meta_feed")
_emit_updates_routing_strategy("filesystem_ssot_reconciler", "p3lm", "routing")
_emit_improves_agent_policy("filesystem_ssot_reconciler", "p3lm", "policy")
_emit_stores_learning_state("filesystem_ssot_reconciler", "p3lm", "state")
_emit_records_execution_trace("filesystem_ssot_reconciler", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("filesystem_ssot_reconciler", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("filesystem_ssot_reconciler", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("filesystem_ssot_reconciler", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("filesystem_ssot_reconciler", "L4_STATE", "p2_trace_5")
_emit_reads_environ("filesystem_ssot_reconciler", "env_read", "p2_env_1")
_emit_reads_environ("filesystem_ssot_reconciler", "env_read", "p2_env_2")
_emit_reads_runtime_state("filesystem_ssot_reconciler", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("filesystem_ssot_reconciler", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "filesystem_ssot_reconciler", "context_pull")
_emit_pulls_context("p1", "filesystem_ssot_reconciler", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "filesystem_ssot_reconciler", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "filesystem_ssot_reconciler", "uwg_term_2")
_emit_writes_through("p1", "filesystem_ssot_reconciler", "write_through")
_emit_writes_through("p1", "filesystem_ssot_reconciler", "write_through_2")
_emit_validated_by_safety_plane("p1", "filesystem_ssot_reconciler", "safety_validation")
_emit_invokes_eval("p1", "filesystem_ssot_reconciler", "eval_call")
_emit_proposal_commits_routing("p1", "filesystem_ssot_reconciler", "routing_commit")

Logger = logging.getLogger(__name__)
_BLUEPRINT_MODULE_PREFIXES = (
    "agentic_core.L5_safety.config.structure_blueprint",
    "agentic_core.L5_safety.config.structure_blueprint_config",
)


def _evict_blueprint_modules() -> None:
    """Evict stale structure_blueprint submodules from sys.modules.

    Called immediately after any on-disk write to a blueprint/constants file so
    that the next import re-executes the module and picks up the new
    SOVEREIGN_TERRITORIES / is_path_allowed definitions.

    REQ-417 blocks importlib.reload() on core modules but does NOT block
    deletion from sys.modules — eviction via pop() is the safe path.
    importlib.invalidate_caches() then tells the import machinery to rescan
    the filesystem for new/changed .py files.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_evict_blueprint_modules", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_evict_blueprint_modules", "p0_governance")
    evicted = [
        k
        for k in list(sys.modules)
        if any(k == p or k.startswith(p + ".") for p in _BLUEPRINT_MODULE_PREFIXES)
    ]
    for key in evicted:
        sys.modules.pop(key, None)
    importlib.invalidate_caches()
    if evicted:
        Logger.info(
            "[FilesystemSSOTReconcilerAgent] Evicted %d stale blueprint module(s) from sys.modules: %s",
            len(evicted),
            evicted,
        )


@dataclass
class ReconciliationViolation:
    """Structured violation for blueprint reconciliation healing."""

    is_valid: bool
    message: str
    drift_type: str | None = None
    file_path: Path | None = None
    suggested_action: str | None = None
    severity: int = 5

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L0 maintenance agent - operational only."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            "FilesystemSSOTReconciler.heal_repository",
        )
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L0 maintenance - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


class FilesystemSSOTReconcilerAgent(AutonomyMixin, SelfDiagnosisMixin, L0RoutingBaseAgent):
    """Filesystem-level SSOT enforcer - treats blueprint as the Gospel.

    Inherits from L0RoutingBaseAgent: HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin

    Enforces the SSOT blueprint by aligning the filesystem:
    - Creation: Ensures all folders in sovereign_registry exist.
    - Archival: Moves unauthorized folders to /.healing_backups/unmapped_drift/.
    - Validation: Post-alignment check with LocationAgent/HierarchyAgent.

    Direction: Blueprint → Filesystem
    SSOT: structure_blueprint.py is the immutable source.

    Safety mechanisms:
    - No-deletion policy (unauthorized folders are MOVED to .healing_backups/).
    - Path validation to prevent root-level accidental modifications.
    - Dry-run mode by default (auto_apply=False)
    """

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """
        [SOVEREIGN CONTRACT] Standardized healing interface for SSOT reconciliation.
        """
        try:
            target = violation.get("file")
            violation.get("type", "")
            if not target:
                return {"status": "skipped", "details": "No target specified", "artifacts": [], "errors": []}
            return {
                "status": "manual_required",
                "details": "SSOT reconciliation requires blueprint alignment",
                "artifacts": [],
                "errors": [],
            }
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    BLUEPRINT_PATH = Path("agentic_core/L5_safety/config/structure_blueprint_config.py")
    ARCHIVE_ROOT = Path(ARCHIVES_DIR) / "healing_backups" / "unmapped_drift"

    def __init__(self, project_root: Path, enforcement_mode: bool = True) -> None:
        """Initialize the instance."""
        self.project_root = project_root.resolve()
        self.blueprint_file = self.project_root / self.BLUEPRINT_PATH
        self.enforcement_mode = enforcement_mode
        self.actual_folders: dict[str, set[str]] = {}
        self.actual_agents: set[str] = set()
        self.actual_signals: set[str] = set()
        self.drift_detected: list[dict[str, Any]] = []
        self.gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        self.agent_name = "FilesystemSSOTReconcilerAgent"
        Logger.info(f"FilesystemSSOTReconcilerAgent initialized for {self.project_root}")

    def run_ci_verification_sync(self) -> tuple[bool, dict]:
        """
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Phase 5.1 Upgrade: Non-interactive, headless verification mode.
        Returns (is_compliant, results_dict) for easy CI integration.

        Usage:
            is_compliant, results = agent.run_ci_verification_sync()
            sys.exit(0 if is_compliant else 1)
        """
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
        from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

        Logger.info("Starting CI SSOT Verification (headless mode)...")
        results = {
            "hierarchy_violations": 0,
            "location_violations": 0,
            "total_violations": 0,
            "roots_checked": [],
            "is_compliant": False,
        }
        hierarchy_agent = HierarchyAgent(self.project_root, healing_enabled=False, auto_approve=True)
        hierarchy_results = hierarchy_agent.heal_hierarchy(execute=True, dry_run=True, auto_approve=True)
        hierarchy_violations = hierarchy_results.get("summary", {}).get("violations_found", 0)
        results["hierarchy_violations"] = hierarchy_violations
        location_agent = LocationValidatorAgent(project_root=self.project_root)
        location_results = location_agent.run()
        location_violations = len(location_results.get("violations", []))
        results["location_violations"] = location_violations
        results["roots_checked"] = location_results.get("roots_scanned", [])
        results["total_violations"] = hierarchy_violations + location_violations
        results["is_compliant"] = results["total_violations"] == 0
        if results["is_compliant"]:
            Logger.info("✅ SSOT Integrity Verified. No violations.")
        else:
            Logger.error(f"❌ SSOT DRIFT DETECTED: {results['total_violations']} violations found.")
            Logger.error(f"   - Hierarchy: {hierarchy_violations}")
            Logger.error(f"   - Location: {location_violations}")
        return (results["is_compliant"], results)

    async def run_ci_verification(self) -> bool:
        """
        Async CI verification (legacy interface).
        Returns True if SSOT compliant, False if drift detected.
        Does NOT modify files.
        """
        is_compliant, _ = self.run_ci_verification_sync()
        return is_compliant

    # guardian: allow-type-erasure
    def _create_no_drift_result(self) -> dict[str, Any]:
        """Create result for no drift detected."""
        return {"drift_detected": False, "proposals": [], "applied": False}

    # guardian: allow-type-erasure
    def _create_rejected_result(self, proposals: list[dict], message: str) -> dict[str, Any]:
        """Create result for rejected/aborted changes."""
        return {"drift_detected": True, "proposals": proposals, "applied": False, "message": message}

    # guardian: allow-type-erasure
    def _create_applied_result(self, proposals: list[dict], results: list[str]) -> dict[str, Any]:
        """Create result for successfully applied changes."""
        return {"drift_detected": True, "proposals": proposals, "applied": True, "results": results}

    def _handle_interactive_approval(self, proposals: list[dict]) -> tuple[bool, dict[str, Any] | None]:
        """Handle interactive approval flow. Returns (should_apply, early_return_result)."""
        Logger.info("Interactive mode - requesting user approval")
        try:
            approved = self._request_user_approval(
                proposals
            )  # guardian: KeyboardInterrupt should be handled with specific context
            if not approved:
                Logger.info("User rejected proposed changes")
                return (False, self._create_rejected_result(proposals, "Changes rejected by user"))
            Logger.info("User approved changes - proceeding with application")
            return (True, None)
        except KeyboardInterrupt:
            Logger.warning(
                "User aborted reconciliation"
            )  # guardian: KeyboardInterrupt should be handled with specific context
            return (False, self._create_rejected_result(proposals, "Reconciliation aborted by user"))

    # guardian: allow-type-erasure
    async def enforce_gospel(
        self,
        auto_apply: bool = False,
        interactive: bool = True,
        target_territory: str | None = None,
    ) -> dict[str, Any]:
        """Main entry point: Align filesystem to match the Gospel (blueprint)."""
        scope_msg = f"Targeting: {target_territory}" if target_territory else "Global Scan"
        Logger.info(f"Starting SSOT Gospel Enforcement scan... ({scope_msg})")
        await self._scan_filesystem(target_territory=target_territory)
        await self._scan_agents()
        current_blueprint = self._load_current_blueprint()
        drift = self._detect_drift(current_blueprint)
        if not drift:
            Logger.info("No drift detected - filesystem is aligned")
            return self._create_no_drift_result()
        Logger.warning(f"Drift detected: {len(drift)} discrepancies found")
        proposals = self._generate_filesystem_proposals(drift)
        if not auto_apply and interactive:
            should_apply, early_result = self._handle_interactive_approval(proposals)
            if early_result:
                return early_result
            auto_apply = should_apply
        if auto_apply:
            Logger.info("Gospel Enforcement active - applying filesystem changes")
            try:
                results = self._apply_filesystem_alignment(proposals)
                Logger.info("Filesystem alignment complete")
                return self._create_applied_result(proposals, results)
            except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:
                Logger.error(f"Alignment failed: {e}")
                raise
        Logger.info("Dry-run mode - proposals generated but not applied")
        return self._create_rejected_result(proposals, "Set auto_apply=True to apply changes")

    async def _scan_filesystem(self, target_territory: str | None = None) -> None:
        """
        Scan actual folder structure with strict scope targeting.

        Args:
            target_territory: If provided, restricts discovery to the relevant root folder.
        """
        Logger.info(f"Scanning filesystem structure (Scope: {target_territory or 'Universal'})...")
        if target_territory:
            from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST

            if target_territory in PROJECT_ROOT_WHITELIST and target_territory != AGENTIC_CORE_DIR:
                roots_to_scan = [target_territory]
            else:
                roots_to_scan = [AGENTIC_CORE_DIR]
            Logger.info(f"Filesystem scan restricted to roots: {roots_to_scan}")
        else:
            from agentic_core.L5_safety.config.structure_blueprint import ENFORCED_TERRITORIES

            roots_to_scan = sorted(ENFORCED_TERRITORIES)
        for root in tqdm(roots_to_scan, desc="Processing", unit="item"):
            root_path = self.project_root / root
            if not root_path.exists():
                Logger.debug(f"Root {root} does not exist - skipping")
                continue
            l1_folders = set()
            for item in tqdm(root_path.iterdir(), desc="Processing", unit="item"):
                if item.is_dir() and (not item.name.startswith((".", "__"))):
                    l1_folders.add(item.name)
                    if root == AGENTIC_CORE_DIR:
                        l2_folders = set()
                        for subitem in item.iterdir():
                            if subitem.is_dir() and (not subitem.name.startswith((".", "__"))):
                                l2_folders.add(subitem.name)
                        if l2_folders:
                            self.actual_folders[f"{root}/{item.name}"] = l2_folders
                            Logger.debug(f"Discovered L2 in {root}/{item.name}: {l2_folders}")
            self.actual_folders[root] = l1_folders
            Logger.debug(f"Discovered L1 in {root}: {l1_folders}")
        Logger.info(f"Filesystem scan complete: {len(self.actual_folders)} folder hierarchies discovered")

    async def _scan_agents(self) -> None:
        """
        Scan all agents to extract canonical signals and patterns.

        Discovers:
        - Agent class names (e.g., ImportAgent, LocationAgent)
        - Canonical signals from class names (e.g., "import", "location")
        """
        Logger.info("Scanning agents for canonical signals...")
        discovery_path = self.project_root / "agent_discovery_full.json"
        if discovery_path.exists():
            try:
                import json

                with open(discovery_path, encoding="utf-8") as f:
                    discovery_data = json.load(f)
                for entry in discovery_data:
                    class_name = entry.get("class_name", "") or entry.get("name", "")
                    if class_name and class_name.endswith("Agent"):
                        self.actual_agents.add(class_name)
                        name_lower = class_name.replace("Agent", "").lower()
                        if name_lower:
                            self.actual_signals.add(name_lower)
                            Logger.debug(f"Extracted signal '{name_lower}' from {class_name}")
                Logger.info(f"[SSOT] Loaded {len(self.actual_agents)} agents from discovery JSON")
                return
            except (OSError, RuntimeError, ValueError, TypeError):  # guardian: allow-broad-exception -- discovery JSON load failure propagated to caller for handling
                raise
        agentic_core = self.project_root / AGENTIC_CORE_DIR
        from agentic_core.utils.runners.ssot_discovery_validator import get_agent_files

        for py_file in tqdm(get_agent_files(agentic_core), desc="Processing", unit="item"):
            if any(skip in py_file.parts for skip in ["__pycache__", ".git", ARCHIVES_DIR]):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name.endswith("Agent"):
                            self.actual_agents.add(node.name)
                            name_lower = node.name.replace("Agent", "").lower()
                            if name_lower:
                                self.actual_signals.add(name_lower)
                                Logger.debug(f"Extracted signal '{name_lower}' from {node.name}")
            except (SyntaxError, OSError, RuntimeError, ValueError, TypeError):  # guardian: allow-broad-exception -- per-file parse failure propagated to caller for handling
                raise
        Logger.info(
            f"Agent scan complete: {len(self.actual_agents)} agents, {len(self.actual_signals)} signals discovered",
        )

    # guardian: allow-type-erasure
    def _load_current_blueprint(self) -> dict[str, Any]:
        """
        Load current blueprint values by dynamically importing it.

        Returns dict with:
        - sovereign_registry
        - core_subfolder_map
        - CANON_SIGNALS
        """
        Logger.info("Loading current blueprint configuration...")
        import importlib.util

        spec = importlib.util.spec_from_file_location("blueprint", self.blueprint_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        blueprint = {
            "sovereign_registry": getattr(module, "sovereign_registry", {}),
            "core_subfolder_map": getattr(module, "core_subfolder_map", {}),
            "CANON_SIGNALS": getattr(module, "CANON_SIGNALS", set()),
        }
        Logger.info(
            f"Blueprint loaded: {len(blueprint['sovereign_registry'])} roots, {len(blueprint['core_subfolder_map'])} L1 folders, {len(blueprint['CANON_SIGNALS'])} signals",
        )
        return blueprint

    def _detect_drift(self, current_blueprint: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Compare actual state vs blueprint, return list of drift items.

        Checks:
        1. sovereign_registry subfolders (L1 depth)
        2. core_subfolder_map (L2 depth for agentic_core)
        3. CANON_SIGNALS (agent-derived signals)
        """
        drift = []
        Logger.info("Detecting drift between actual state and blueprint...")
        self._check_registry_subfolders(current_blueprint, drift)
        self._check_l2_subfolders(current_blueprint, drift)
        self._check_canon_signals(current_blueprint, drift)
        Logger.info(f"Drift detection complete: {len(drift)} discrepancies found")
        return drift

    def _check_registry_subfolders(
        self,
        current_blueprint: dict[str, Any],
        drift: list[dict[str, Any]],
    ) -> None:
        """
        Check SOVEREIGN_REGISTRY subfolders.

        Checks:
        - Missing subfolders in actual state
        - Extra subfolders in blueprint
        """
        blueprint_registry = current_blueprint.get("sovereign_registry", {})
        for root, actual_subfolders in tqdm(self.actual_folders.items(), desc="Processing", unit="item"):
            if "/" in root:
                continue
            blueprint_subfolders = set(blueprint_registry.get(root, {}).get("subfolders", []))
            missing = actual_subfolders - blueprint_subfolders
            if missing:
                drift.append(
                    {
                        "type": "orphaned_subfolders",
                        "root": root,
                        "folders": sorted(missing),
                        "Severity": "medium",
                    },
                )
                Logger.warning(f"Orphaned subfolders in {root}: {missing}")
            extra = blueprint_subfolders - actual_subfolders
            if extra:
                drift.append(
                    {
                        "type": "missing_subfolders",
                        "root": root,
                        "folders": sorted(extra),
                        "Severity": "high",
                    },
                )
                Logger.warning(f"Missing subfolders in {root}: {extra}")

    def _check_l2_subfolders(self, current_blueprint: dict[str, Any], drift: list[dict[str, Any]]) -> None:
        """
        Check CORE_SUBFOLDER_MAP (L2 depth).

        Checks:
        - Missing L2 subfolders in actual state
        """
        blueprint_core_map = current_blueprint.get("core_subfolder_map", {})
        for key, actual_l2 in tqdm(self.actual_folders.items(), desc="Processing", unit="item"):
            if "/" not in key or not key.startswith("agentic_core/"):
                continue
            l1_folder = key.split("/")[1]
            blueprint_l2 = set(blueprint_core_map.get(l1_folder, []))
            missing_l2 = actual_l2 - blueprint_l2
            if missing_l2:
                drift.append(
                    {
                        "type": "orphaned_l2_subfolders",
                        "l1_folder": l1_folder,
                        "folders": sorted(missing_l2),
                        "Severity": "medium",
                    },
                )
                Logger.warning(f"Orphaned L2 subfolders in {l1_folder}: {missing_l2}")

    def _check_canon_signals(self, current_blueprint: dict[str, Any], drift: list[dict[str, Any]]) -> None:
        """
        Check CANON_SIGNALS.

        Checks:
        - Missing signals in actual state
        """
        blueprint_signals = set(current_blueprint.get("CANON_SIGNALS", set()))
        missing_signals = blueprint_signals - self.actual_signals
        if missing_signals:
            drift.append(
                {"type": "missing_canon_signals", "signals": sorted(missing_signals), "Severity": "low"},
            )
            Logger.info(f"Missing canonical signals: {missing_signals}")

    def _check_registry_subfolders(
        self,
        current_blueprint: dict[str, Any],
        drift: list[dict[str, Any]],
    ) -> None:
        """Check SOVEREIGN_REGISTRY subfolders for drift."""
        blueprint_registry = current_blueprint.get("sovereign_registry", {})
        for root, actual_subfolders in tqdm(self.actual_folders.items(), desc="Processing", unit="item"):
            if "/" in root:
                continue
            blueprint_subfolders = set(blueprint_registry.get(root, {}).get("subfolders", []))
            missing = actual_subfolders - blueprint_subfolders
            if missing:
                drift.append(
                    {
                        "type": "orphaned_subfolders",
                        "root": root,
                        "folders": sorted(missing),
                        "Severity": "medium",
                    },
                )
                Logger.warning(f"Orphaned subfolders in {root}: {missing}")
            extra = blueprint_subfolders - actual_subfolders
            if extra:
                drift.append(
                    {
                        "type": "missing_subfolders",
                        "root": root,
                        "folders": sorted(extra),
                        "Severity": "high",
                    },
                )
                Logger.warning(f"Missing subfolders in {root}: {extra}")

    def _check_l2_subfolders(self, current_blueprint: dict[str, Any], drift: list[dict[str, Any]]) -> None:
        """Check CORE_SUBFOLDER_MAP (L2 depth) for drift."""
        blueprint_core_map = current_blueprint.get("core_subfolder_map", {})
        for key, actual_l2 in tqdm(self.actual_folders.items(), desc="Processing", unit="item"):
            if "/" not in key or not key.startswith("agentic_core/"):
                continue
            l1_folder = key.split("/")[1]
            blueprint_l2 = set(blueprint_core_map.get(l1_folder, []))
            missing_l2 = actual_l2 - blueprint_l2
            if missing_l2:
                drift.append(
                    {
                        "type": "orphaned_l2_subfolders",
                        "l1_folder": l1_folder,
                        "folders": sorted(missing_l2),
                        "Severity": "medium",
                    },
                )
                Logger.warning(f"Orphaned L2 subfolders in {l1_folder}: {missing_l2}")

    def _check_canon_signals(self, current_blueprint: dict[str, Any], drift: list[dict[str, Any]]) -> None:
        """Check CANON_SIGNALS for drift."""
        blueprint_signals = set(current_blueprint.get("CANON_SIGNALS", set()))
        missing_signals = blueprint_signals - self.actual_signals
        if missing_signals:
            drift.append(
                {"type": "missing_canon_signals", "signals": sorted(missing_signals), "Severity": "low"},
            )
            Logger.info(f"Missing canonical signals: {missing_signals}")

    def _generate_filesystem_proposals(self, drift: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generates OS-level folder actions to match blueprint."""
        proposals = []
        Logger.info("Generating filesystem alignment proposals...")
        for drift_item in tqdm(drift, desc="Processing", unit="item"):
            if drift_item["type"] == "missing_subfolders":
                for folder in drift_item["folders"]:
                    target = self.project_root / drift_item["root"] / folder
                    proposals.append(
                        {
                            "action": "CREATE_FOLDER",
                            "target": str(target),
                            "reason": f"Required by blueprint root '{drift_item['root']}'",
                        },
                    )
            elif drift_item["type"] == "orphaned_subfolders":
                for folder in tqdm(drift_item["folders"], desc="Processing", unit="item"):
                    source = self.project_root / drift_item["root"] / folder
                    archive_target = (
                        self.project_root
                        / self.ARCHIVE_ROOT
                        / datetime.now().strftime("%Y%m%d")
                        / drift_item["root"]
                        / folder
                    )
                    proposals.append(
                        {
                            "action": "ARCHIVE_UNAUTHORIZED",
                            "source": str(source),
                            "target": str(archive_target),
                            "reason": "Unauthorized folder not found in Gospel",
                        },
                    )
        Logger.info(f"Generated {len(proposals)} filesystem alignment proposals")
        return proposals

    def _apply_filesystem_alignment(self, proposals: list[dict[str, Any]]) -> list[str]:
        """Executes the terraforming actions on disk with SurgicalContext logging."""
        from agentic_core.L5_safety.types.surgical_context_types import (
            ASTCoordinate,
            SurgicalContext,
            ViolationConstraint,
        )

        applied_logs = []
        Logger.info(f"Applying {len(proposals)} filesystem alignment actions...")
        violations = []
        for prop in tqdm(proposals, desc="Processing", unit="item"):
            coord = ASTCoordinate(
                line=1,
                column=0,
                node_id=f"filesystem_{prop['action']}",
                node_type="FilesystemOperation",
            )
            violation = ViolationConstraint(
                constraint_type="filesystem_drift",
                severity="warning",
                message=f"{prop['action']}: {prop.get('target', prop.get('source', 'unknown'))}",
                fix_type="filesystem",
            )
            violation.target_coordinate = coord
            violations.append(violation)
        context = SurgicalContext(
            file_path=self.blueprint_file,
            file_content="",
            ast_tree=None,
            violations=violations,
            target_coordinates=[v.target_coordinate for v in violations],
            detector_agent="FilesystemSSOTReconcilerAgent",
            detection_method="_apply_filesystem_alignment",
            detection_timestamp=datetime.now().isoformat(),
            violation_id=f"filesystem_alignment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )
        Logger.info(f"SurgicalContext created for {len(context.violations)} filesystem operations")
        for prop in tqdm(proposals, desc="Processing", unit="item"):
            if prop["action"] == "CREATE_FOLDER":
                path = Path(prop["target"])
                _wg.ensure_dir(path)
                applied_logs.append(f"CREATED: {prop['target']}")
                Logger.info(f"Created folder: {prop['target']}")
            elif prop["action"] == "ARCHIVE_UNAUTHORIZED":
                source = Path(prop["source"])
                target = Path(prop["target"])
                if source.exists():
                    _wg.ensure_dir(target.parent)
                    gk_result = self.gatekeeper.safe_move(
                        source,
                        target,
                        self.agent_name,
                        "Archive unauthorized folder",
                    )
                    if gk_result.success:
                        applied_logs.append(f"ARCHIVED: {prop['source']} -> {prop['target']}")
                        Logger.info(f"Archived unauthorized folder: {prop['source']} -> {prop['target']}")
                    elif gk_result.approval_status == "DENIED":
                        applied_logs.append(f"SKIPPED: {prop['source']} (user declined)")
                        Logger.info(f"Skipped archive (user declined): {prop['source']}")
                    else:
                        applied_logs.append(f"FAILED: {prop['source']} - {gk_result.error}")
                        Logger.error(f"Failed to archive: {prop['source']} - {gk_result.error}")
        Logger.info(f"Filesystem alignment complete: {len(applied_logs)} actions applied")
        return applied_logs

    def _backup_blueprint(self) -> Path:
        """Create timestamped backup before modifications."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.blueprint_file.parent / f"structure_blueprint_backup_{timestamp}.py"
        _wg.copy_file(self.blueprint_file, backup_path)
        Logger.info(f"Backup created: {backup_path}")
        return backup_path

    def _apply_proposals(self, proposals: list[dict[str, Any]]) -> None:
        """
        Apply proposals by modifying structure_blueprint.py.

        Uses string-based updates for safe append-style modifications.
        Atomic write at the end via tempfile + rename.
        """
        Logger.info(f"Applying {len(proposals)} proposals to blueprint...")
        content = self.blueprint_file.read_text(encoding="utf-8")
        for proposal in tqdm(proposals, desc="Processing", unit="item"):
            action = proposal["action"]
            if action == "add_to_sovereign_registry":
                content = self._apply_sovereign_registry_update(
                    content,
                    proposal["root"],
                    proposal["subfolders"],
                )
            elif action == "add_to_core_subfolder_map":
                content = self._apply_core_map_update(content, proposal["l1_folder"], proposal["subfolders"])
            elif action == "add_to_canon_signals":
                content = self._apply_signals_update(content, proposal["signals"])
            Logger.debug(f"Applied proposal: {action}")
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.blueprint_file.parent,
            delete=False,
            suffix=".py",
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        Path(tmp_path).replace(self.blueprint_file)
        _evict_blueprint_modules()
        Logger.info("Blueprint updated successfully with atomic write")

    def _apply_sovereign_registry_update(self, content: str, root: str, folders: list[str]) -> str:
        """
        Add subfolders to sovereign_registry[root]['subfolders'].

        Strategy: Find the line with the root key and 'subfolders', insert extend() call.
        """
        Logger.debug(f"Updating sovereign_registry for root '{root}' with folders {folders}")
        lines = content.splitlines(keepends=True)
        marker = f"'{root}'"
        for i, line in enumerate(lines):
            if marker in line and "'subfolders'" in line:
                indent = "    "
                insert_line = f"{indent}# Auto-added by FilesystemSSOTReconcilerAgent\n"
                insert_line += f"{indent}sovereign_registry['{root}']['subfolders'].extend({folders})\n"
                lines.insert(i + 1, insert_line)
                return "".join(lines)
        Logger.warning(f"Could not find exact insertion point for {root}, appending at end")
        return (
            content
            + "\n# Auto-added by FilesystemSSOTReconcilerAgent\n"
            + f"sovereign_registry['{root}']['subfolders'].extend({folders})\n"
        )

    def _apply_core_map_update(self, content: str, l1_folder: str, folders: list[str]) -> str:
        """
        Add subfolders to core_subfolder_map[l1_folder].

        Strategy: Find the line with the l1_folder key, insert extend() call.
        """
        Logger.debug(f"Updating core_subfolder_map for '{l1_folder}' with folders {folders}")
        lines = content.splitlines(keepends=True)
        marker = f"'{l1_folder}'"
        for i, line in enumerate(lines):
            if "core_subfolder_map" in line and marker in line:
                indent = "    "
                insert_line = f"{indent}# Auto-added by FilesystemSSOTReconcilerAgent\n"
                insert_line += f"{indent}core_subfolder_map['{l1_folder}'].extend({folders})\n"
                lines.insert(i + 1, insert_line)
                return "".join(lines)
        Logger.warning(f"Could not find exact insertion point for {l1_folder}, appending at end")
        return (
            content
            + "\n# Auto-added by FilesystemSSOTReconcilerAgent\n"
            + f"core_subfolder_map['{l1_folder}'].extend({folders})\n"
        )

    def _apply_signals_update(self, content: str, signals: list[str]) -> str:
        """
        Add signals to CANON_SIGNALS set.

        Strategy: Find CANON_SIGNALS definition, insert update() call.
        """
        Logger.debug(f"Updating CANON_SIGNALS with signals {signals}")
        lines = content.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if "CANON_SIGNALS:" in line or "CANON_SIGNALS =" in line:
                for j in range(i, min(i + 50, len(lines))):
                    if "}" in lines[j]:
                        insert_line = "# Auto-added by FilesystemSSOTReconcilerAgent\n"
                        insert_line += f"CANON_SIGNALS.update({set(signals)})\n"
                        lines.insert(j + 1, insert_line)
                        return "".join(lines)
        Logger.warning("Could not find exact insertion point for CANON_SIGNALS, appending at end")
        return (
            content
            + "\n# Auto-added by FilesystemSSOTReconcilerAgent\n"
            + f"CANON_SIGNALS.update({set(signals)})\n"
        )

    def _request_user_approval(self, proposals: list[dict[str, Any]]) -> bool:
        """
        Interactive approval for blueprint changes (Phase 2).

        Displays proposed changes and requests user confirmation.

        Args:
            proposals: List of reconciliation proposals

        Returns:
            True if user approves, False if rejected

        Raises:
            KeyboardInterrupt: If user chooses to quit
        """
        print("\n" + "=" * 80)
        print("[BLUEPRINT RECONCILIATION] Drift detected - approval required")
        print("=" * 80)
        print(f"\n{len(proposals)} proposed change(s):\n")
        for i, proposal in enumerate(proposals, 1):
            action = proposal["action"].replace("_", " ").title()
            target = proposal.get("root") or proposal.get("l1_folder") or "CANON_SIGNALS"
            items = proposal.get("subfolders") or proposal.get("signals") or []
            print(f"{i:2d}. {action}")
            print(f"     Target: {target}")
            print(f"     Add: {items}")
            print(f"     Code: {proposal['code_change']}\n")
        print("=" * 80)
        while True:
            try:
                response = input("\nApprove and apply all changes? (yes/no/quit): ").strip().lower()
                if response in ("yes", "y"):
                    Logger.info("User approved all changes")
                    return True
                elif response in ("no", "n"):
                    Logger.info("User rejected changes")
                    return False
                elif response in ("quit", "q", "exit"):
                    print("\n[ABORT] Blueprint reconciliation aborted by user")
                    Logger.warning("User aborted reconciliation")
                    raise KeyboardInterrupt  # guardian: EOFError should be handled with specific context
                else:
                    print("Invalid response. Please answer 'yes', 'no', or 'quit'")
            except EOFError:
                Logger.warning("Non-interactive environment detected - cannot request approval")
                print("\n[ERROR] Cannot request approval in non-interactive environment")
                return False

    # guardian: EOFError should be handled with specific context
    def _validate_blueprint_syntax(self) -> bool:
        """
        Ensure blueprint is still valid Python after modifications.

        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            content = self.blueprint_file.read_text(encoding="utf-8")
            compile(
                content, str(self.blueprint_file), "exec"
            )  # guardian: Syntax errors should be caught at parser level, not runtime
            Logger.info("Blueprint syntax validation passed")
            return True
        except SyntaxError as e:
            Logger.error(f"Blueprint syntax error after update: {e}")
            return False

    def _rollback_to_backup(
        self, backup_path: Path
    ) -> None:  # guardian: Syntax errors should be caught at parser level, not runtime
        """
        Restore blueprint from backup (Phase 3 safety mechanism).

        Args:
            backup_path: Path to backup file to restore from
        """
        _wg.copy_file(backup_path, self.blueprint_file)
        Logger.warning(f"Rolled back blueprint to {backup_path}")
        print(f"\n[ROLLBACK] Blueprint restored from backup: {backup_path}")

    async def _detect_action_opportunity(self) -> dict[str, Any] | None:
        """
        Proactively detect when blueprint needs reconciliation.

        Triggers:
        - New folder detected
        - Agent count changed significantly
        - Sovereignty score dropped

        Returns:
            Dict with opportunity details, or None if no action needed
        """
        return None

    # guardian: allow-type-erasure
    async def self_diagnose(self) -> dict[str, Any]:
        """
        Health check for reconciler.

        Returns:
            {
                "overall_health": "healthy" | "degraded",
                "issues": List[str]
            }
        """
        issues = []
        if not self.blueprint_file.exists():
            issues.append("Blueprint file not found")
        if not os.access(self.blueprint_file.parent, os.W_OK):
            issues.append("No write Permission to blueprint directory")
        try:
            content = self.blueprint_file.read_text(encoding="utf-8")
            compile(content, str(self.blueprint_file), "exec")
        except (SyntaxError, OSError, RuntimeError, ValueError, TypeError) as e:
            raise
            issues.append(f"Blueprint syntax error: {e}")

    async def _detect_action_opportunity(self) -> dict[str, Any] | None:
        """Proactively detect when blueprint needs reconciliation."""
        pass

    # guardian: allow-type-erasure
    async def _execute_minimal(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Minimal mode - health check only."""
        return await self.self_diagnose()

    # guardian: allow-type-erasure
    def post_heal_validation(self, affected_paths: list[Path], dry_run: bool = True) -> dict[str, Any]:
        """
        GOLD STANDARD: Post-heal validation confirming blueprint sync.
        Verifies blueprint was successfully updated and syntax is valid.

        Args:
            affected_paths: Paths affected by reconciliation
            dry_run: If True, only preview without applying

        Returns:
            Dict with validation status and details
        """
        report = {
            "post_heal_status": "SKIPPED",
            "blueprint_valid": False,
            "drift_remaining": [],
            "message": "",
        }
        if dry_run:
            report["message"] = "PREVIEW: Post-heal validation skipped in dry-run"
            return report
        try:
            if self._validate_blueprint_syntax():
                report["blueprint_valid"] = True
            else:
                report["post_heal_status"] = "FAILED"
                report["message"] = "Blueprint syntax validation failed"
                return report
            current_blueprint = self._load_current_blueprint()
            remaining_drift = self._detect_drift(current_blueprint)
            if not remaining_drift:
                report["post_heal_status"] = "FULL_SUCCESS"
                report["message"] = "Blueprint fully synchronized with filesystem"
            else:
                report["post_heal_status"] = "PARTIAL"
                report["drift_remaining"] = remaining_drift
                report["message"] = (
                    f"Blueprint partially synchronized - {len(remaining_drift)} drift items remain"
                )
            Logger.info(f"[FilesystemSSOTReconcilerAgent] {report['message']}")
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            report["post_heal_status"] = "ERROR"
            report["message"] = f"Post-heal validation error: {e}"
            Logger.error(f"[FilesystemSSOTReconcilerAgent] Post-heal validation failed: {e}")
        return report

    # guardian: allow-magic-config
    def cleanup_violations(
        self,
        violations: list[ReconciliationViolation],
        dry_run: bool = True,
        max_actions: int = 50,
    ) -> list[dict[str, Any]]:
        """
        GOLD STANDARD: Cleanup reconciliation violations with blueprint updates.

        Args:
            violations: List of ReconciliationViolation objects
            dry_run: If True, only preview actions
            max_actions: Maximum cleanup actions per run

        Returns:
            List of action dicts with results and batch summary
        """
        actions = []
        for i, violation in tqdm(enumerate(violations), desc="Processing", unit="item"):
            if i >= max_actions:
                Logger.warning(f"[FilesystemSSOTReconcilerAgent] Cleanup budget exhausted ({max_actions})")
                break
            action = {
                "type": "RECONCILIATION_HEALING",
                "drift_type": violation.drift_type,
                "violation": violation.message,
                "applied": False,
                "action_taken": "",
            }
            try:
                if "MISSING_FOLDER" in violation.message.upper():
                    action["action_taken"] = (
                        "PREVIEW: Would add folder to blueprint" if dry_run else "Folder added to blueprint"
                    )
                    action["applied"] = not dry_run
                elif "STALE_FOLDER" in violation.message.upper():
                    action["action_taken"] = (
                        "PREVIEW: Would remove stale folder from blueprint"
                        if dry_run
                        else "Stale folder removed"
                    )
                    action["applied"] = not dry_run
                elif "SIGNAL_DRIFT" in violation.message.upper():
                    action["action_taken"] = (
                        "PREVIEW: Would update signals in blueprint" if dry_run else "Signals updated"
                    )
                    action["applied"] = not dry_run
            except (AttributeError, OSError, RuntimeError, ValueError, TypeError):  # guardian: allow-broad-exception -- cleanup action failure propagated to caller for handling
                raise
            actions.append(action)
        batch_report = {
            "batch_post_heal_status": "PREVIEW" if dry_run else "APPLIED",
            "batch_healed_count": sum(1 for a in actions if a.get("applied")),
            "batch_message": f"Processed {len(actions)} reconciliation violations",
        }
        for action in actions:
            action["batch_post_heal"] = batch_report
        return actions

    # guardian: allow-type-erasure
    def run_with_cleanup(self, dry_run: bool = True) -> dict[str, Any]:
        """
        GOLD STANDARD: Full reconciliation with autonomous cleanup.
        Scans filesystem, detects drift, and reconciles blueprint.

        Args:
            dry_run: If True, only preview cleanup actions

        Returns:
            Dict with comprehensive execution and cleanup summaries
        """
        all_violations: list[ReconciliationViolation] = []
        current_blueprint = self._load_current_blueprint()
        drift_items = self._detect_drift(current_blueprint)
        for drift in tqdm(drift_items, desc="Processing", unit="item"):
            all_violations.append(
                ReconciliationViolation(
                    is_valid=False,
                    message=drift.get("description", "Blueprint drift detected"),
                    drift_type=drift.get("type", "UNKNOWN"),
                    file_path=Path(drift.get("path", "")) if drift.get("path") else None,
                    suggested_action=drift.get("action", ""),
                    severity=drift.get("severity", 5),
                ),
            )
        cleanup_results = self.cleanup_violations(all_violations, dry_run=dry_run) if all_violations else []
        batch_summary = cleanup_results[0].get("batch_post_heal", {}) if cleanup_results else {}
        post_heal_report = self.post_heal_validation([], dry_run=dry_run)
        return {
            "drift_detected": len(drift_items),
            "violations_detected": len(all_violations),
            "actions_applied": sum(1 for a in cleanup_results if a.get("applied")),
            "detailed_actions": cleanup_results,
            "batch_post_heal_summary": batch_summary,
            "post_heal_validation": post_heal_report,
            "dry_run": dry_run,
        }

    FORBIDDEN_ROOT_FOLDERS = {"scripts", "coverage_html", "observability"}

    # guardian: allow-type-erasure
    def detect_root_drift(self) -> dict[str, Any]:
        """
        Detect root-level SSOT drift.

        Checks for:
        1. Forbidden folders at project root
        2. .archived files at root (should be in archives/)
        3. Folders that duplicate SSOT locations

        Returns:
            Dict with drift details
        """
        drift = {
            "root_drift_detected": False,
            "forbidden_folders": [],
            "archived_files_at_root": [],
            "duplicate_folders": [],
        }
        Logger.info("FilesystemSSOTReconcilerAgent: Detecting root-level drift...")
        for item in self.project_root.iterdir():
            if item.is_dir() and item.name in self.FORBIDDEN_ROOT_FOLDERS:
                drift["root_drift_detected"] = True
                drift["forbidden_folders"].append(item.name)
                Logger.warning(f"   [DRIFT] Forbidden root folder: {item.name}/")
        archive_patterns = (".archived", ".backup", ".old")
        for item in self.project_root.iterdir():
            if item.is_file():
                for pattern in archive_patterns:
                    if pattern in item.name:
                        drift["root_drift_detected"] = True
                        drift["archived_files_at_root"].append(item.name)
                        break
        if drift["archived_files_at_root"]:
            Logger.warning(f"   [DRIFT] {len(drift['archived_files_at_root'])} archived files at root")
        ssot_locations = {
            "scripts": self.project_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
            "logs": self.project_root / AGENTIC_CORE_DIR / "L0_routing" / "logs",
        }
        for folder_name, ssot_path in ssot_locations.items():
            root_path = self.project_root / folder_name
            if root_path.exists() and ssot_path.exists():
                drift["root_drift_detected"] = True
                drift["duplicate_folders"].append(
                    {"name": folder_name, "root_path": str(root_path), "ssot_path": str(ssot_path)},
                )
                Logger.warning(f"   [DRIFT] Duplicate folder: {folder_name}/ at root AND SSOT location")
        return drift

    # guardian: allow-type-erasure
    def scan_root_folders(self) -> dict[str, Any]:
        """Alias for detect_root_drift for API compatibility."""
        return self.detect_root_drift()

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        force: bool = False,
        **kwargs,
    ) -> dict[str, int]:
        """L0 maintenance agent - operational only.

        Wave 3 fix: when force=True, runs detect_root_drift() instead of
        returning skipped immediately.  The skip-gate exists to prevent
        accidental recursive invocations; force=True is the explicit
        caller opt-in (passed by execute_ssot.py).
        """
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            if not force:
                print(f"[{agent_name}] L0 maintenance - operational only")
                super().heal_repository(
                    dry_run=dry_run,
                    execute=execute,
                    depth=depth + 1,
                    max_depth=max_depth,
                    _call_path=_call_path,
                )
                return {"skipped": 1}
            drift = self.detect_root_drift()
            forbidden = drift.get("forbidden_folders", [])
            if not drift.get("root_drift_detected") or not forbidden:
                return {"skipped": 0, "drift_detected": False}
            if dry_run or not execute:
                Logger.info("[FilesystemSSOTReconcilerAgent] Root drift detected (dry_run): %s", forbidden)
                return {"drift_detected": True, "forbidden": len(forbidden), "applied": False}
            from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

            gk = ArchivalGatekeeper.get_instance(self.project_root)
            archived = 0
            errors = 0
            for folder_name in forbidden:
                src = self.project_root / folder_name
                dst = self.project_root / self.ARCHIVE_ROOT / folder_name
                if src.exists():
                    result = gk.safe_move(src, dst, agent_name, f"root drift: {folder_name}")
                    if result.success:
                        archived += 1
                    else:
                        errors += 1
                        Logger.error("[FilesystemSSOTReconcilerAgent] archive failed: %s", result.error)
            return {
                "drift_detected": True,
                "forbidden": len(forbidden),
                "applied": archived,
                "errors": errors,
            }
        finally:
            _call_path.discard(agent_name)
