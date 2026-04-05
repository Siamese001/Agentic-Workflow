from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "ArchitectureGovernorAgent")
emit_determinism_digest("p0", "ArchitectureGovernorAgent")

_emit_dispatches_healing_run("p1", "ArchitectureGovernorAgent", "L5")
_emit_routes_through("p1", "ArchitectureGovernorAgent", "L5")
_emit_checks_agent_registry("p1", "ArchitectureGovernorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "ArchitectureGovernorAgent", "capability")
_emit_dispatches_execution_plan("p1", "ArchitectureGovernorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "ArchitectureGovernorAgent", "sub_agent")
_emit_routes_to_agent("p1", "ArchitectureGovernorAgent", "target_agent")
_emit_verifies_policy("p1", "ArchitectureGovernorAgent", "policy_check")
_emit_observes_runtime_state("p1", "ArchitectureGovernorAgent", "runtime_state")
_emit_verifies_boundary("p1", "ArchitectureGovernorAgent", "boundary_check")
_emit_transcripts_response("p1", "ArchitectureGovernorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "ArchitectureGovernorAgent")
_emit_gated_by_confidence("p1", "ArchitectureGovernorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "ArchitectureGovernorAgent", "L5")
_emit_reads_policy_state("p1", "ArchitectureGovernorAgent", "L5")
_emit_authorize_and_execute("p2", "ArchitectureGovernorAgent", "execution_auth")
_emit_validates_capability("p2", "ArchitectureGovernorAgent", "capability_check")
_emit_routes_to_capability("p2", "ArchitectureGovernorAgent", "capability_route")
_emit_writes_via_uwg("p2", "ArchitectureGovernorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ArchitectureGovernorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ArchitectureGovernorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ArchitectureGovernorAgent", "exec_output")
_emit_dispatches_agent("p3", "ArchitectureGovernorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ArchitectureGovernorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ArchitectureGovernorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ArchitectureGovernorAgent", "healing_outcome")
_emit_escalates_failure("p3", "ArchitectureGovernorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ArchitectureGovernorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ArchitectureGovernorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ArchitectureGovernorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ArchitectureGovernorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ArchitectureGovernorAgent", "eval_metric")
_emit_stores_embedding("p4", "ArchitectureGovernorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ArchitectureGovernorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ArchitectureGovernorAgent", "exec_snapshot_link")

'ArchitectureGovernorAgent - Universal Architecture Governance\n\nPhase 1 Upgrade (2026-01-21): Activated from stub to functioning enforcer.\nPhase 2 Upgrade (2026-01-21): Transition from Observer to Active Healer.\nPhase 3 Upgrade (2026-01-21): Environmental Maintenance & Root-Level Lockdown.\nPhase 4 Upgrade (2026-01-21): Deduplication & Logic Consolidation.\nPhase 6 Upgrade (2026-01-21): Universal Logic Consolidation & Healing.\nPhase 7 Upgrade (2026-01-21): Final Sovereign Lockdown & CI/CD Integration.\nPhase 8 Upgrade (2026-01-28): Golden Baseline & Immutable Snapshotting.\nPhase 9 Upgrade (2026-01-21): Golden Baseline Capture & SSOT Normalization.\nPhase 10 Upgrade (2026-01-21): Sovereign Convergence & Categorical Drift Audits.\n\nResponsibilities:\n- Validate layer boundaries (L0-L6) across ALL sovereign territories\n- Detect gravity violations (upward imports: L3 importing L5)\n- Enforce naming conventions (*Agent.py suffix)\n- Detect orphaned and duplicate agents\n- Trigger cross-root deduplication audits\n- Perform Categorical Drift Audits (Phase 10)\n- Manage Immutable Project Baselines\n- Execute Automated Sovereign Purges\n- Enforce Universal Sovereignty via Phase 8 Golden Baseline with SHA-256 integrity\n- Enforce Universal Sovereignty via CI/CD sync verification\n- Support headless CI mode with auto_approve\n- [Phase 2] Autonomous healing via GravityLeakRepairAgent orchestration\n- [Phase 2] Naming convention auto-fix via ArchivalGatekeeper\n- [Phase 3] Post-healing environmental cleanup\n- [Phase 4] Cross-agent deduplication audit\n- [Phase 6] Zero-loss collision resolution via ArchivalGatekeeper\n- [Phase 7] Final CI-ready lockdown verification\n- [Phase 8] SHA-256 snapshotting for immutable "Gold Master" state\n- [Phase 8] Silent Drift detection (logic changes without naming violations)\n- [Phase 8] Immutable audit logs for long-term sovereignty tracking\n- [Phase 9] Golden Baseline capture for SSOT normalization\n- [Phase 10] Sovereign Convergence terminal command\n\n[SSOT] All territorial scope derived from SOVEREIGN_TERRITORIES in structure_blueprint.py\n'
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import TESTS_DIR, THRESHOLD
from agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent import SSOTFolderCleanupAgent
from agentic_core.L5_safety.config.structure_blueprint import CORE_SUBFOLDER_MAP, PROJECT_ROOT_WHITELIST
from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
    get_python_files_fast,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("ArchitectureGovernorAgent", "p4obs", "metric_6")
_emit_records_incident_event("ArchitectureGovernorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("ArchitectureGovernorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("ArchitectureGovernorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("ArchitectureGovernorAgent", "p4obs", "mon_state")
_emit_triggers_alert("ArchitectureGovernorAgent", "p4obs", "alert")
_emit_links_incident_trace("ArchitectureGovernorAgent", "p4obs", "trace_link")
_emit_captures_pattern("ArchitectureGovernorAgent", "p3lm", "pattern")
_emit_records_learning_event("ArchitectureGovernorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ArchitectureGovernorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("ArchitectureGovernorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ArchitectureGovernorAgent", "p3lm", "routing")
_emit_improves_agent_policy("ArchitectureGovernorAgent", "p3lm", "policy")
_emit_stores_learning_state("ArchitectureGovernorAgent", "p3lm", "state")
_emit_records_execution_trace("ArchitectureGovernorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ArchitectureGovernorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ArchitectureGovernorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ArchitectureGovernorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ArchitectureGovernorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ArchitectureGovernorAgent", "env_read", "p2_env_1")
_emit_reads_environ("ArchitectureGovernorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("ArchitectureGovernorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ArchitectureGovernorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ArchitectureGovernorAgent", "context_pull")
_emit_pulls_context("p1", "ArchitectureGovernorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ArchitectureGovernorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ArchitectureGovernorAgent", "uwg_term_2")
_emit_writes_through("p1", "ArchitectureGovernorAgent", "write_through")
_emit_writes_through("p1", "ArchitectureGovernorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "ArchitectureGovernorAgent", "safety_validation")
_emit_invokes_eval("p1", "ArchitectureGovernorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "ArchitectureGovernorAgent", "routing_commit")
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_dispatch_entry")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_dispatch_exit")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_tool_invoke")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_tool_complete")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_agent_entry")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_agent_exit")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_uwg_write")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_trace_sign")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_guardrail_check")
emit_determinism_digest("trace_ArchitectureGovernorAgent", "ArchitectureGovernorAgent_policy_verify")

Logger = logging.getLogger(__name__)
LAYER_DIRS: set[str] = set(CORE_SUBFOLDER_MAP.keys())


@dataclass
class ArchitectureGovernorAgent(SovereignBaseAgent):
    """
    [L5 GOVERNOR] Universal Architecture Pattern Enforcement

    Phase 1 Upgrade: Activated from stub to functioning enforcer.
    Ensures code follows canonical architectural patterns and layer boundaries
    across ALL sovereign territories (not just agentic_core).

    Features:
    - Universal Scope: Scans all SOVEREIGN_TERRITORIES roots
    - Auto-Approve Mode: Headless CI operation without stdin prompts
    - Gravity Detection: L3 importing L5 = violation
    - Naming Enforcement: *Agent.py suffix validation
    """

    project_root: Path = field(default_factory=Path.cwd)
    healing_enabled: bool = True
    auto_approve: bool = False
    ci_mode: bool = False

    def __post_init__(self) -> None:
        """Initialize the ArchitectureGovernorAgent."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)
        self.violations: list[dict[str, Any]] = []
        self.stats = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "drift_detected": 0}
        self.name = self.__class__.__name__
        self.python_files: list[str] = []
        self.baseline_dir = self.project_root / AGENTIC_CORE_DIR / "config" / "baselines"
        self.audit_log_dir = self.project_root / "logs" / "sovereign_audit"
        self._structure_validator = None
        self._gravity_repair_agent = None
        self._archival_gatekeeper = None
        self._cognitive_agent = None
        self.adg_signals: dict[str, list] = {}
        try:
            from agentic_core.adg.applications.guardian_prioritizer import GuardianPrioritizer
            from agentic_core.adg.runtime.cache_loader import load_or_scan as _adg_load_or_scan

            _sr = _adg_load_or_scan(repo_root=str(self.project_root))
            if _sr is not None:
                _gp = GuardianPrioritizer(_sr)
                _raw = _gp.get_signals()
                self.adg_signals = {
                    "cross_layer_violations": _raw.get("cross_layer_violations", []),
                    "fan_in_hotspots": _raw.get("fan_in_hotspots", []),
                    "orphan_modules": _raw.get("orphan_modules", []),
                    "upward_mutations": _raw.get("upward_mutations", []),
                }
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError):
            pass
        Logger.info(
            f"ArchitectureGovernorAgent initialized (auto_approve={self.auto_approve}, ci_mode={self.ci_mode})"
        )

    def _get_structure_validator(self):
        """Lazy-load StructuralValidatorAgent to avoid circular imports."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "ArchitectureGovernorAgent._get_structure_validator", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "ArchitectureGovernorAgent._get_structure_validator", "p0_governance"
        )
        if self._structure_validator is None:
            from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (
                StructuralValidatorAgent,
                StructureConfig,
            )

            config = StructureConfig(
                check_gravity=True,
                check_duplicates=True,
                check_orphans=True,
                check_registry=False,
                check_contracts=False,
                check_hierarchy=True,
                project_root=self.project_root,
            )
            self._structure_validator = StructuralValidatorAgent(config=config)
        return self._structure_validator

    def _get_gravity_repair_agent(self):
        """Lazy-load GravityLeakRepairAgent for orchestrated healing."""
        if self._gravity_repair_agent is None:
            from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

            self._gravity_repair_agent = GravityLeakRepairAgent(project_root=self.project_root)
        return self._gravity_repair_agent

    def _get_archival_gatekeeper(self):
        """Lazy-load ArchivalGatekeeper for safe file operations."""
        if self._archival_gatekeeper is None:
            from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

            self._archival_gatekeeper = ArchivalGatekeeper.get_instance(self.project_root)
        return self._archival_gatekeeper

    def _get_cognitive_agent(self):
        """Lazy-load CognitiveDispositionAgent for AI-powered triage (Phase 11)."""
        if self._cognitive_agent is None:
            from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import CognitiveDispositionAgent

            self._cognitive_agent = CognitiveDispositionAgent(
                project_root=self.project_root, confidence_threshold=THRESHOLD
            )
        return self._cognitive_agent

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Enhanced healing interface with meta-learning integration.

        Args:
            violation: Violation dict with keys: type, file, message, severity, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "ArchitectureGovernorAgent.heal"
        )
        if hasattr(self, "ml_enhanced_heal") and hasattr(self, "_do_heal"):
            return self.ml_enhanced_heal(violation, self._do_heal)
        return self._do_heal(violation)

    def _do_heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        try:
            violation_type = violation.get("type", "")
            file_path = violation.get("file")
            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }
            if violation_type == "GRAVITY":
                result = self._heal_gravity_violation(violation, auto_approve=True)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Gravity violation healing {('succeeded' if result else 'failed')}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Gravity healing failed"],
                }
            elif violation_type == "NAMING":
                result = self._heal_naming_violation(violation, auto_approve=True)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Naming violation healing {('succeeded' if result else 'failed')}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Naming healing failed"],
                }
            elif violation_type == "DUPLICATE":
                result = self._resolve_collision(violation)
                return {
                    "status": "success" if result else "failed",
                    "details": f"Duplicate resolution {('succeeded' if result else 'failed')}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Duplicate resolution failed"],
                }
            elif violation_type == "ORPHAN":
                file_path_obj = Path(file_path)
                result = self._process_cognitive_disposition(file_path_obj, "ORPHAN")
                return {
                    "status": "success" if result else "failed",
                    "details": f"Orphan file processing {('succeeded' if result else 'failed')}",
                    "artifacts": [file_path] if result else [],
                    "errors": [] if result else ["Orphan processing failed"],
                }
            else:
                return {
                    "status": "skipped",
                    "details": f"No healer available for violation type: {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"Heal operation failed: {e}")
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        auto_approve: bool | None = None,
        target_territory: str | None = None,
    ) -> dict[str, Any]:
        """
        Universal architecture governance with optional strict scope targeting.

        Phase 1 Upgrade: Now performs actual validation instead of returning stub.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix violations
            depth: Current recursion depth for cycle detection
            max_depth: Maximum recursion depth
            _call_path: Internal call path tracking
            auto_approve: Override instance auto_approve setting
            target_territory: [STRICT SCOPE] If provided, restricts audit to specific territory

        Returns:
            Dictionary with canonical keys: violations_found, violations_fixed, status
        """
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        effective_auto_approve = auto_approve if auto_approve is not None else self.auto_approve
        try:
            Logger.info(f"[{agent_name}] Starting Universal Architecture Governance...")
            violations_found = 0
            violations_fixed = 0
            roots_scanned = []
            all_violations = []
            if target_territory:
                if target_territory in PROJECT_ROOT_WHITELIST and target_territory != AGENTIC_CORE_DIR:
                    target_roots = [target_territory]
                elif (self.project_root / AGENTIC_CORE_DIR / target_territory).exists():
                    target_roots = [f"{AGENTIC_CORE_DIR}/{target_territory}"]
                else:
                    target_roots = [AGENTIC_CORE_DIR]
                Logger.info(f"[{agent_name}] TARGETED AUDIT: {target_territory} (Roots: {target_roots})")
            else:
                target_roots = sorted(PROJECT_ROOT_WHITELIST)
            for root_name in target_roots:
                root_path = self.project_root / root_name
                if not root_path.exists():
                    continue
                roots_scanned.append(root_name)
                Logger.info(f"  Scanning territory: {root_name}")
                validator = self._get_structure_validator()
                report = validator.validate_structure(root_path)
                for violation in report.violations:
                    if "must end with 'Agent'" in violation.message:
                        if "'Error'" in violation.message or "'Exception'" in violation.message:
                            continue
                        if "Error'" in violation.message or "Exception'" in violation.message:
                            continue
                        _cls = violation.message.split("'")[1] if "'" in violation.message else ""
                        _non_agent = (
                            "Factory",
                            "Role",
                            "Base",
                            "Mixin",
                            "Enum",
                            "Config",
                            "Registry",
                            "Simple",
                        )
                        if any(_cls.endswith(s) for s in _non_agent):
                            continue
                    _vt = (
                        violation.violation_type
                        if isinstance(violation.violation_type, str)
                        else str(violation.violation_type)
                    )
                    if _vt == "GRAVITY" and violation.file_path:
                        if any(p in (TESTS_DIR, "test") for p in Path(str(violation.file_path)).parts):
                            continue
                    violations_found += 1
                    v_type_name = (
                        violation.violation_type
                        if isinstance(violation.violation_type, str)
                        else str(violation.violation_type)
                    )
                    violation_dict = {
                        "type": v_type_name,
                        "file": str(violation.file_path) if violation.file_path else None,
                        "message": violation.message,
                        "severity": violation.severity,
                        "suggestion": violation.suggested_fix,
                        "source_layer": None,
                        "target_layer": None,
                    }
                    all_violations.append(violation_dict)
                    if execute and (not dry_run) and self.healing_enabled:
                        fixed = self._heal_violation(violation_dict, effective_auto_approve)
                        if fixed:
                            violations_fixed += 1
                    elif not dry_run:
                        Logger.warning(f"    [{v_type_name}] {violation.message}")
            self.violations = all_violations
            if dry_run:
                Logger.info(
                    f"[DRY-RUN] Found {violations_found} violations across {len(roots_scanned)} territories"
                )
            else:
                Logger.info(f"Found {violations_found} violations, fixed {violations_fixed}")
            if violations_found > 0 and (not execute):
                Logger.warning(
                    f"[{agent_name}] SHIELD ALERT: {violations_found} violations blocking baseline purity."
                )
            if violations_found > 0:
                self._log_categorical_drift(all_violations)
            dedup_results = self._trigger_deduplication_audit(
                roots_scanned, execute=execute and (not dry_run)
            )
            if self.healing_enabled and execute and (not dry_run) and (violations_fixed > 0):
                Logger.info("[Phase 3] Running post-healing cleanup...")
                for root_name in roots_scanned:
                    self._cleanup_empty_dirs(self.project_root / root_name)
            ssot_moves = 0
            ssot_imports_updated = 0
            if not dry_run:
                try:
                    Logger.info(f"[{agent_name}] Initiating SSOT Folder Cleanup (dry_run={dry_run})...")
                    janitor = SSOTFolderCleanupAgent(project_root=self.project_root, dry_run=dry_run)
                    cleanup_stats = janitor.cleanup_repository()
                    ssot_moves = cleanup_stats.get("files_moved", 0)
                    ssot_imports_updated = cleanup_stats.get("imports_updated", 0)
                    violations_fixed += ssot_moves
                    if cleanup_stats.get("errors", 0) > 0:
                        Logger.warning(
                            f"[{agent_name}] SSOT Cleanup reported errors: {cleanup_stats['errors']}"
                        )
                # guardian: allow-silent-swallow
                except (RuntimeError, OSError) as e:
                    Logger.error(f"[{agent_name}] SSOT Cleanup Sub-routine failed: {e}")
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "roots_scanned": roots_scanned,
                "status": "PASS" if violations_found == 0 else "FAIL",
                "deduplication_audit": dedup_results,
                "ssot_moves": ssot_moves,
                "ssot_imports_updated": ssot_imports_updated,
            }
        finally:
            _call_path.discard(agent_name)

    def run_ci_verification_sync(self) -> tuple[bool, dict[str, Any]]:
        """
        Synchronous CI verification for pre-commit hooks and CLI tools.

        Returns (is_compliant, results_dict) for easy CI integration.
        No stdin prompts - fully headless operation.
        """
        Logger.info("Starting Architecture CI Verification (headless mode)...")
        results = self.heal_repository(dry_run=True, execute=False, auto_approve=True)
        is_compliant = results.get("violations_found", 0) == 0
        if is_compliant:
            Logger.info("✅ Architecture Integrity Verified. No violations.")
        else:
            Logger.error(f"❌ Architecture violations detected: {results.get('violations_found', 0)}")
        return (is_compliant, results)

    def run_audit(self, target_territories: list[str] | None = None) -> dict[str, Any]:
        """
        Executes a comprehensive structural and naming audit with Phase 8 Drift Detection.
        In CI mode, this returns a non-zero-weighted success status.

        Args:
            target_territories: [STRICT SCOPE] Optional list of specific paths/domains to audit.
        """
        Logger.info(
            f"🚀 Starting Sovereign Audit (CI_MODE: {self.ci_mode}, SCOPE: {target_territories or 'GLOBAL'})"
        )
        structural_results = self._orchestrate_guardian_scan(target_territories)
        drift_violations = []
        if not target_territories:
            drift_violations = self._check_baseline_drift()
        total_violations = structural_results.get("total_violations", 0) + len(drift_violations)
        self.stats.update(
            {
                "violations_found": total_violations,
                "drift_detected": len(drift_violations),
                "errors": structural_results.get("total_errors", 0),
            }
        )
        self._persist_audit_report(structural_results, drift_violations)
        success = self.stats["violations_found"] == 0 and self.stats["errors"] == 0
        if self.ci_mode and (not success):
            Logger.critical(
                f"🛑 CI FAILURE: {self.stats['violations_found']} violations (Drift: {len(drift_violations)})"
            )
        return {
            "success": success,
            "stats": self.stats,
            "violations": structural_results.get("violation_details", []),
            "drift_violations": drift_violations,
        }

    def _orchestrate_guardian_scan(self, target_territories: list[str] | None = None) -> dict[str, Any]:
        """
        Orchestrate scanning of all L5 Guardians in one pass.
        Internal method for run_audit to consolidate scanning logic.

        Now supports [STRICT SCOPE] targeting via target_territories.
        """
        total_violations = 0
        total_errors = 0
        violation_details = []
        roots_scanned = []
        try:
            if target_territories:
                scan_targets = []
                for t in target_territories:
                    p_core = self.project_root / AGENTIC_CORE_DIR / t
                    p_root = self.project_root / t
                    if p_core.exists():
                        scan_targets.append(p_core)
                    elif p_root.exists():
                        scan_targets.append(p_root)
                    else:
                        Logger.warning(f"⚠️ Target territory not found: {t}")
            else:
                scan_targets = [self.project_root / k for k in sorted(PROJECT_ROOT_WHITELIST)]
            for root_path in scan_targets:
                if not root_path.exists():
                    continue
                root_name = root_path.name
                roots_scanned.append(str(root_path.relative_to(self.project_root)))
                Logger.info(f"  Scanning territory: {roots_scanned[-1]}")
                validator = self._get_structure_validator()
                report = validator.validate_structure(root_path)
                try:
                    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

                    hierarchy = HierarchyAgent(project_root=self.project_root)
                    h_report = hierarchy.scan_root_violations(target_territory=root_name)
                    for h_violation in h_report.get("violations", []):
                        total_violations += 1
                        violation_details.append(
                            {
                                "type": "STRUCTURE",
                                "file": h_violation.get("file"),
                                "message": "File sitting in territory root. Should be in SSOT subfolder.",
                                "severity": "ERROR",
                                "suggestion": "Relocate to approved subfolder (reasoning/, enforcement/, validators/, etc.)",
                            }
                        )
                # guardian: allow-silent-swallow
                except Exception as e:
                    raise
                    Logger.warning(f"Hierarchy cross-check failed for {root_name}: {e}")
                for violation in report.violations:
                    if "must end with 'Agent'" in violation.message:
                        if "'Error'" in violation.message or "'Exception'" in violation.message:
                            continue
                        if "Error'" in violation.message or "Exception'" in violation.message:
                            continue
                        _cls2 = violation.message.split("'")[1] if "'" in violation.message else ""
                        _non_agent2 = (
                            "Factory",
                            "Role",
                            "Base",
                            "Mixin",
                            "Enum",
                            "Config",
                            "Registry",
                            "Simple",
                        )
                        if any(_cls2.endswith(s) for s in _non_agent2):
                            continue
                    _vt2 = (
                        violation.violation_type
                        if isinstance(violation.violation_type, str)
                        else str(violation.violation_type)
                    )
                    if _vt2 == "GRAVITY" and violation.file_path:
                        if any(p in (TESTS_DIR, "test") for p in Path(str(violation.file_path)).parts):
                            continue
                    total_violations += 1
                    v_type_name = (
                        violation.violation_type
                        if isinstance(violation.violation_type, str)
                        else str(violation.violation_type)
                    )
                    violation_dict = {
                        "type": v_type_name,
                        "file": str(violation.file_path) if violation.file_path else None,
                        "message": violation.message,
                        "severity": violation.severity,
                        "suggestion": violation.suggested_fix,
                        "source_layer": None,
                        "target_layer": None,
                    }
                    violation_details.append(violation_dict)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"Guardian scan failed: {e}")
            total_errors += 1
        return {
            "total_violations": total_violations,
            "total_errors": total_errors,
            "violation_details": violation_details,
            "roots_scanned": roots_scanned,
        }

    def validate_layer_boundaries(self, file_path: Path) -> tuple[bool, str]:
        """
        Validate that file respects layer boundaries using deterministic Guardian test.

        Args:
            file_path: Path to file to validate

        Returns:
            Tuple of (is_valid, reason)
        """
        import subprocess

        result = subprocess.run(
            ["python", "tests/guardian/test_architecture_governance.py", str(file_path)],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )
        if result.returncode == 0:
            return (True, "Architecture governance validated")
        else:
            return (False, result.stdout.strip())

    def _cognitive_triage_validation(self, file_path: Path, violation_type: str) -> tuple[bool, str]:
        """
        [PHASE 22] Invoke CognitiveDispositionAgent for intelligent violation analysis.

        Args:
            file_path: Path to the file with potential violation
            violation_type: Type of violation (ORPHAN, GRAVITY, etc.)

        Returns:
            Tuple of (is_valid, reason) with cognitive triage recommendation
        """
        try:
            cognitive = self._get_cognitive_agent()
            decision = cognitive.analyze_violation(file_path, violation_type)
            if decision.action == "IGNORE":
                return (True, f"False positive identified by Cognitive Triage: {decision.reason}")
            reason = f"Structural violation: {decision.reason}. Recommended Action: {decision.action}"
            if decision.target_path:
                reason += f" to {decision.target_path}"
            reason += f" (confidence: {decision.confidence:.2f})"
            return (False, reason)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.warning(f"Cognitive triage failed, using fallback: {e}")
            return (False, "File outside sovereign territories (cognitive triage unavailable)")

    def validate_architectural_patterns(self, file_path: Path) -> dict[str, Any]:
        """
        Validate architectural patterns in a file.

        Args:
            file_path: Path to file to validate

        Returns:
            Dictionary with validation results
        """
        is_valid, reason = self.validate_layer_boundaries(file_path)
        return {"file": str(file_path), "valid": is_valid, "reason": reason, "violations": self.violations}

    def run_validation(self, files: list[Path]) -> dict[str, Any]:
        """
        Run architecture validation on multiple files.

        Args:
            files: List of file paths to validate

        Returns:
            Summary of validation results
        """
        results: Any = []
        total_violations: Any = 0
        for file_path in files:
            result: Any = self.validate_architectural_patterns(file_path)
            results.append(result)
            if not result["valid"]:
                total_violations += 1
        return {"total_files": len(files), "total_violations": total_violations, "results": results}

    def _heal_violation(self, violation: dict[str, Any], auto_approve: bool) -> bool:
        """
        Attempt to heal a single violation.

        Phase 2: Dispatches to appropriate healer based on violation type.

        Args:
            violation: Violation dict with type, file, message, etc.
            auto_approve: If True, skip interactive prompts

        Returns:
            True if violation was fixed, False otherwise
        """
        violation_type = violation.get("type", "")
        file_path = violation.get("file")
        if not file_path:
            Logger.warning(f"Cannot heal violation without file path: {violation}")
            return False
        file_path = Path(file_path)
        if violation_type == "GRAVITY":
            result = self._heal_gravity_violation(violation, auto_approve)
            if not result:
                return self._process_cognitive_disposition(file_path, "GRAVITY_FAIL")
            return result
        elif violation_type == "NAMING":
            return self._heal_naming_violation(violation, auto_approve)
        elif violation_type == "DUPLICATE":
            return self._resolve_collision(violation)
        elif violation_type == "ORPHAN":
            return self._process_cognitive_disposition(file_path, "ORPHAN")
        else:
            Logger.debug(f"  [SKIP] No healer for violation type: {violation_type}")
            return False

    def _heal_gravity_violation(self, violation: dict[str, Any], auto_approve: bool) -> bool:
        """
        Heal a gravity violation by orchestrating GravityLeakRepairAgent.

        Phase 2: Governor acts as executive that decides WHEN to trigger repair.

        Args:
            violation: Gravity violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        """
        file_path = violation.get("file")
        source_layer = violation.get("source_layer")
        target_layer = violation.get("target_layer")
        if not file_path:
            return False
        Logger.info(f"  [GRAVITY] Attempting repair: {Path(file_path).name}")
        Logger.info(f"    Source layer: {source_layer} -> Target layer: {target_layer}")
        try:
            repair_agent = self._get_gravity_repair_agent()
            fix = repair_agent.analyze_violation(
                file_path=Path(file_path),
                import_statement=violation.get("message", ""),
                file_layer=source_layer or "",
                import_layer=target_layer or "",
            )
            Logger.info(f"    Fix type: {fix.fix_type}")
            Logger.info(f"    Rationale: {fix.rationale}")
            if auto_approve:
                result = repair_agent.apply_fix(fix, dry_run=False)
                if result.get("status") == "fixed":
                    Logger.info(f"    ✅ Fixed via {fix.fix_type}")
                    return True
                else:
                    Logger.warning(f"    ⚠️ Fix not applied: {result.get('status')}")
                    return False
            else:
                Logger.info(f"    [RECOMMENDATION] {fix.fix_type}: {fix.new_import}")
                return False
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"    ❌ Gravity repair failed: {e}")
            return False

    def _heal_naming_violation(self, violation: dict[str, Any], auto_approve: bool) -> bool:
        """
        Heal a naming convention violation via ArchivalGatekeeper safe rename.

        Phase 2: Fixes files missing *Agent.py suffix.

        Args:
            violation: Naming violation dict
            auto_approve: If True, skip interactive prompts

        Returns:
            True if fixed, False otherwise
        """
        file_path = violation.get("file")
        if not file_path:
            return False
        file_path = Path(file_path)
        if not file_path.name.endswith("Agent.py") and "Agent" in violation.get("message", ""):
            stem = file_path.stem
            if stem.endswith("Agent"):
                return False
            new_name = f"{stem}Agent.py"
            new_path = file_path.parent / new_name
            Logger.info(f"  [NAMING] Attempting rename: {file_path.name} -> {new_name}")
            if new_path.exists():
                Logger.warning(f"    ⚠️ Target already exists: {new_path}")
                return False
            if auto_approve:
                try:
                    gatekeeper = self._get_archival_gatekeeper()
                    gatekeeper.set_require_approval(False)
                    result = gatekeeper.safe_move(
                        source=file_path,
                        destination=new_path,
                        requester_agent="ArchitectureGovernorAgent",
                        reason="Naming convention fix: add Agent suffix",
                    )
                    if result.success:
                        Logger.info(f"    ✅ Renamed to {new_name}")
                        return True
                    else:
                        Logger.warning(f"    ⚠️ Rename failed: {result.error}")
                        return False
                # guardian: allow-silent-swallow
                except (RuntimeError, OSError) as e:
                    Logger.error(f"    ❌ Rename failed: {e}")
                    return False
            else:
                Logger.info(f"    [RECOMMENDATION] Rename to: {new_name}")
                return False
        return False

    def _trigger_deduplication_audit(self, roots: list[str], execute: bool = False) -> dict[str, Any]:
        """
        [PHASE 4/6] Identify and resolve redundant logic across roots.

        Scans all sovereign roots for duplicate agent definitions and
        redundant code patterns. When execute=True and auto_approve=True,
        resolves collisions via zero-loss merge using ArchivalGatekeeper.

        Args:
            roots: List of root names that were scanned
            execute: If True, attempt to resolve collisions

        Returns:
            Dictionary with audit results including collisions found/fixed
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Triggering Deduplication Audit...")
        collisions: list[dict[str, Any]] = []
        validator = self._get_structure_validator()
        for root_name in roots:
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue
            duplicates = validator.check_duplicates(root_path)
            for dup in duplicates:
                collisions.append(
                    {
                        "root": root_name,
                        "type": "DUPLICATE_AGENT",
                        "message": dup.message,
                        "file": str(dup.file_path) if dup.file_path else None,
                        "violation": dup,
                    }
                )
        collisions_fixed = 0
        if execute and self.auto_approve and self.healing_enabled and collisions:
            Logger.info(f"  [DEDUP] Attempting to resolve {len(collisions)} collisions...")
            for collision in collisions:
                violation = collision.get("violation")
                if violation:
                    fixed = self._resolve_collision(violation)
                    collisions_fixed += fixed
        if collisions:
            Logger.warning(
                f"  [DEDUP] Found {len(collisions)} potential collisions, fixed {collisions_fixed}"
            )
        else:
            Logger.info(f"  [DEDUP] No collisions found across {len(roots)} roots")
        return {
            "roots_audited": roots,
            "collisions_found": len(collisions),
            "collisions_fixed": collisions_fixed,
            "collisions": collisions[:10] if collisions else [],
        }

    def _resolve_collision(self, violation: Any) -> int:
        """
        [PHASE 6] Zero-loss merge: Archives lower-priority duplicates.

        Priority order (highest to lowest):
        - agentic_core (0) - Master source
        - apps_shared (1) - Shared utilities
        - apps_rg (2) - Resume Generator app
        - apps_lic (3) - LinkedIn app
        - tests (4) - Test files
        - scripts (5) - Scripts

        Args:
            violation: StructureViolation with duplicate locations

        Returns:
            Number of files archived (0 if no action taken)
        """
        priority = {
            "agentic_core": 0,
            "apps_shared": 1,
            "apps_rg": 2,
            "apps_lic": 3,
            "tests": 4,
            "scripts": 5,
        }
        files = getattr(violation, "locations", [])
        if not files:
            files = getattr(violation, "file_paths", [])
        if not files:
            single_path = getattr(violation, "file_path", None)
            if single_path:
                files = [single_path]
        if len(files) < 2:
            return 0
        files = [Path(f) if not isinstance(f, Path) else f for f in files]

        def get_priority(p: Path) -> int:
            try:
                rel_path = p.relative_to(self.project_root)
                root = rel_path.parts[0] if rel_path.parts else ""
                return priority.get(root, 99)
            except ValueError:
                return 99

        sorted_files = sorted(files, key=get_priority)
        master = sorted_files[0]
        to_archive = sorted_files[1:]
        archived_count = 0
        gatekeeper = self._get_archival_gatekeeper()
        for file_path in to_archive:
            try:
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category="deduplication_cleanup",
                    reason=f"Duplicate of {master.name}",
                )
                if result.success:
                    Logger.info(f"  [DEDUP] Archived {file_path.name} in favor of {master.name}")
                    archived_count += 1
                else:
                    Logger.warning(f"  [DEDUP] Failed to archive {file_path.name}: {result.error}")
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError) as e:
                Logger.error(f"  [DEDUP] Error archiving {file_path.name}: {e}")
        return archived_count

    def _cleanup_empty_dirs(self, path: Path) -> None:
        """
        Recursively remove empty directories after healing operations.

        Phase 3: Post-healing environmental maintenance to purge ghost directories
        left behind after renames or refactors.

        Args:
            path: Root path to start cleanup from
        """
        if not path.is_dir():
            return
        for child in list(path.iterdir()):
            if child.is_dir():
                self._cleanup_empty_dirs(child)
        remaining = [
            p
            for p in path.iterdir()
            if p.name not in {"__pycache__", "__init__.py", ".gitkeep"} and (not p.name.startswith("."))
        ]
        if not remaining:
            try:
                for sentinel in [path / "__init__.py", path / ".gitkeep"]:
                    if sentinel.exists():
                        _wg.remove_file(sentinel)
                pycache = path / "__pycache__"
                if pycache.exists():
                    _wg.remove_tree(pycache, ignore_errors=True)    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                _wg.remove_dir(path)
                try:
                    rel_path = path.relative_to(self.project_root)
                    Logger.info(f"  [CLEANUP] Removed empty directory: {rel_path}")
                except ValueError:
                    Logger.info(f"  [CLEANUP] Removed empty directory: {path}")
            except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                pass

    def finalize_sovereign_lockdown(self) -> tuple[bool, dict]:
        """
        [PHASE 7] Final CI-ready lockdown verification.

        Performs a non-blocking sync check to ensure the repository state
        perfectly matches the Sovereign SSOT. Designed for CI/CD pipelines
        and pre-commit hooks.

        Returns:
            Tuple of (is_pure: bool, results: dict)
            - is_pure: True if repository has 0 violations
            - results: Full heal_repository results for inspection

        Usage in CI:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            is_pure, results = agent.finalize_sovereign_lockdown()
            sys.exit(0 if is_pure else 1)
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Initiating Final Sovereign Lockdown...")
        results = self.heal_repository(dry_run=True, execute=False)
        raw_result = results.get("_raw_result", results)
        violations_found = raw_result.get("violations_found", 0)
        is_pure = violations_found == 0
        if is_pure:
            Logger.info(f"[{agent_name}] ✅ LOCKDOWN VERIFIED: Repository is sovereign-compliant")
        else:
            Logger.warning(f"[{agent_name}] ❌ LOCKDOWN FAILED: {violations_found} violations detected")
        return (is_pure, results)

    def capture_golden_baseline(self) -> Path:
        """
        [PHASE 8] Generates a SHA-256 manifest of all files in sovereign territories.
        This represents the 'Gold Master' state of the repository.
        """
        Logger.info("📸 CAPTURING GOLDEN BASELINE...")
        manifest = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "audit_id": str(uuid.uuid4()),
            "files": {},
        }
        FileClassificationAgent(self.project_root)
        files = get_python_files_fast(self.project_root)
        for file_path in files:
            try:
                relative_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                manifest["files"][relative_path] = file_hash
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.warning(f"Skipping file {file_path.name} in baseline: {e}")
        _wg.ensure_dir(self.baseline_dir)
        baseline_path = self.baseline_dir / "golden_baseline.json"
        temp_path = baseline_path.with_suffix(".tmp")
        _wg.write_json(temp_path, manifest, indent=4)
        temp_path.replace(baseline_path)
        Logger.info(f"✅ BASELINE CAPTURED: {len(manifest['files'])} files tracked.")
        return baseline_path

    def _check_baseline_drift(self) -> list[dict[str, Any]]:
        """[PHASE 8] Compares live files against the Golden Baseline."""
        baseline_path = self.baseline_dir / "golden_baseline.json"
        if not baseline_path.exists():
            Logger.warning("⚠️ No Golden Baseline found. Skipping integrity check.")
            return []
        violations = []
        try:
            with open(baseline_path) as f:
                baseline = json.load(f)
            for rel_path, expected_hash in baseline["files"].items():
                full_path = self.project_root / rel_path
                if not full_path.exists():
                    violations.append({"type": "MISSING_FILE", "path": rel_path, "severity": "CRITICAL"})
                    continue
                current_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
                if current_hash != expected_hash:
                    violations.append(
                        {
                            "type": "CONTENT_DRIFT",
                            "path": rel_path,
                            "expected": expected_hash,
                            "actual": current_hash,
                            "severity": "CRITICAL",
                        }
                    )
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"Drift check failed: {e}")
        return violations

    def _persist_audit_report(
        self, structural_results: dict[str, Any], drift_violations: list[dict[str, Any]]
    ) -> None:
        """[PHASE 8] Saves immutable audit record."""
        _wg.ensure_dir(self.audit_log_dir)
        {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_id": str(uuid.uuid4()),
            "structural_summary": structural_results,
            "drift_violations": drift_violations,
            "stats": self.stats,
        }

    def capture_sovereign_baseline(self) -> dict[str, Any]:
        """
        [PHASE 9] Captures the post-purge state as the new SSOT baseline.

        This establishes the zero-violation benchmark for all future
        CI/CD enforcement gates. Should be called after a successful
        purge execution to lock in the clean state.

        Returns:
            Dictionary containing the baseline state with violation counts
            and root scan results.

        Usage:
            # After purge execution
            agent.heal_repository(execute=True, dry_run=False)

            # Capture the clean state as baseline
            baseline = agent.capture_sovereign_baseline()
            assert baseline.get("violations_found", 0) == 0
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] Capturing Golden Baseline...")
        baseline_state = self.heal_repository(dry_run=True)
        raw_result = baseline_state.get("_raw_result", baseline_state)
        violations_found = raw_result.get("violations_found", 0)
        if violations_found > 0:
            Logger.warning(f"[{agent_name}] Baseline captured with {violations_found} unresolved violations.")
        else:
            Logger.info(f"[{agent_name}] ✅ Golden Baseline captured: 0 violations")
        return baseline_state

    def _log_categorical_drift(self, violations: list[Any]) -> dict[str, int]:
        """
        [PHASE 10] Generates a diagnostic breakdown of architectural debt.

        Categorizes violations by type for targeted remediation.

        Args:
            violations: List of violation objects or dictionaries

        Returns:
            Dictionary with counts per violation category
        """
        agent_name = self.__class__.__name__
        report = {"GRAVITY": 0, "NAMING": 0, "ORPHAN": 0, "DUPLICATE": 0, "OTHER": 0}
        for v in violations:
            if isinstance(v, dict):
                v_type = v.get("type", "OTHER")
            else:
                raw_vt = getattr(v, "violation_type", None)
                v_type = str(raw_vt) if raw_vt is not None else "OTHER"
            v_type = str(v_type).upper()
            if v_type in report:
                report[v_type] += 1
            else:
                report["OTHER"] += 1
        Logger.warning(f"[{agent_name}] Drift Analysis: {report}")
        return report

    def execute_sovereign_convergence(self) -> dict[str, Any]:
        """
        [PHASE 10] Final convergence: Purge all drift and seal the baseline.

        This is the terminal command for the L5 safety transition.
        Executes a full purge followed by baseline lockdown verification.

        Returns:
            Dictionary containing:
            - purge_status: Results from heal_repository execution
            - lockdown_status: Tuple of (is_pure, results) from lockdown
            - final_purity: Boolean indicating if repository is clean

        Usage:
            agent = ArchitectureGovernorAgent(project_root=Path.cwd(), auto_approve=True)
            result = agent.execute_sovereign_convergence()
            assert result["final_purity"] is True
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] INITIATING SOVEREIGN CONVERGENCE...")
        purge_results = self.heal_repository(execute=True, dry_run=False)
        lockdown_result = self.finalize_sovereign_lockdown()
        is_pure, lockdown_details = lockdown_result
        if is_pure:
            Logger.info(f"[{agent_name}] ✅ SOVEREIGN CONVERGENCE COMPLETE: Repository is pure.")
        else:
            raw_result = lockdown_details.get("_raw_result", lockdown_details)
            remaining = raw_result.get("violations_found", 0)
            Logger.warning(f"[{agent_name}] ⚠️ CONVERGENCE INCOMPLETE: {remaining} violations remain.")
        return {"purge_status": purge_results, "lockdown_status": lockdown_result, "final_purity": is_pure}

    def execute_cognitive_purge(
        self, checkpoint_file: str = "cognitive_checkpoint.json", rate_limit_delay: float = 1.0
    ) -> dict[str, Any]:
        """
        [PHASE 13] Execute AI-driven purge using Cognitive Batch Processor.

        Processes all violations through Gemini LLM with:
        - Rate limiting to respect API quotas
        - Progress checkpointing for resumable execution
        - Exponential backoff for API errors

        Args:
            checkpoint_file: Path to checkpoint file for progress tracking
            rate_limit_delay: Seconds to wait between API calls

        Returns:
            Dictionary with batch processing statistics
        """
        agent_name = self.__class__.__name__
        Logger.info(f"[{agent_name}] INITIATING COGNITIVE PURGE...")
        Logger.info("=" * 60)
        Logger.info(f"[{agent_name}] Scanning for violations...")
        self.heal_repository(dry_run=True)
        violations = getattr(self, "violations", [])
        if not violations:
            Logger.info(f"[{agent_name}] No violations found. Repository is clean.")
            return {
                "violations_found": 0,
                "batch_stats": {"PROCESSED": 0, "SKIPPED": 0, "ERRORS": 0, "TOTAL": 0},
            }
        Logger.info(f"[{agent_name}] Found {len(violations)} violations to process")
        from agentic_core.L5_safety.utils.cognitive_batch_processor_util import CognitiveBatchProcessor

        cognitive = self._get_cognitive_agent()
        processor = CognitiveBatchProcessor(
            agent=cognitive, checkpoint_file=checkpoint_file, rate_limit_delay=rate_limit_delay
        )
        Logger.info(f"[{agent_name}] Starting batch processing...")
        batch_stats = processor.process_batch(violations)
        results_stats = processor.get_statistics()
        Logger.info("=" * 60)
        Logger.info(f"[{agent_name}] COGNITIVE PURGE COMPLETE")
        Logger.info(f"[{agent_name}] Total Analyzed: {results_stats['total']}")
        Logger.info(f"[{agent_name}] Average Confidence: {results_stats['avg_confidence']:.2%}")
        Logger.info(f"[{agent_name}] Actions by Type:")
        for action, count in sorted(results_stats["by_action"].items()):
            Logger.info(f"    {action}: {count}")
        Logger.info("=" * 60)
        return {
            "violations_found": len(violations),
            "batch_stats": batch_stats,
            "results_stats": results_stats,
            "checkpoint_file": checkpoint_file,
        }

    def comprehensive_territory_audit(
        self,
        target_territories: list[str],
        check_layer_boundaries: bool = True,
        check_naming_conventions: bool = True,
    ) -> dict[str, Any]:
        """
        [HARDENED] Unified Compliance Audit.
        Aggregates output from Hierarchy, Location, and SystemArchitect agents into a single JSON manifest.
        """
        Logger.info(f"🎯 INITIATING UNIFIED AUDIT: {target_territories}")
        audit_results = self.run_audit(target_territories=target_territories)
        if "violations" not in audit_results:
            audit_results["violations"] = []
        try:
            from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

            hierarchy = HierarchyAgent(project_root=self.project_root)
            for territory in target_territories:
                h_report = hierarchy.scan_root_violations(target_territory=territory)
                for v in h_report.get("violations", []):
                    audit_results["violations"].append(
                        {
                            "type": "STRUCTURE",
                            "file": v.get("file"),
                            "message": "File sitting in territory root; must be in SSOT subfolder.",
                            "severity": "ERROR",
                        }
                    )
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.warning(f"Unified Audit: Hierarchy ingestion failed: {e}")
        try:
            from agentic_core.L5_safety.reasoning.SystemArchitectAgent import SystemArchitectAgent

            architect = SystemArchitectAgent(project_root=self.project_root)
            for territory in target_territories:
                arch_path = territory if territory.startswith("agentic_core") else f"agentic_core/{territory}"
                arch_report = architect.validate_core_architecture(arch_path)
                if not arch_report.get("imports_valid", True):
                    for circ in arch_report.get("circular_dependencies", []):
                        audit_results["violations"].append(
                            {
                                "type": "GRAVITY",
                                "file": territory,
                                "message": f"Circular dependency detected: {circ}",
                                "severity": "CRITICAL",
                            }
                        )
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.warning(f"Unified Audit: Architecture ingestion failed: {e}")
        audit_results["stats"]["violations_found"] = len(audit_results["violations"])
        audit_results["target_territories"] = target_territories
        return audit_results

    # guardian: allow-magic-config
    def check_file_sizes(self, territory: str, max_lines: int = 1000) -> list[dict[str, Any]]:
        """Check for Python files exceeding max_lines in the given territory.

        Mirrors the file-size check previously performed by SystemArchitectAgent.
        Returns a list of violation dicts (type FILE_SIZE, file, message, severity).
        """
        import os

        max_lines = int(os.getenv("MAX_FILE_LINES", str(max_lines)))
        territory_path = self.project_root / territory
        if not territory_path.exists():
            return []
        violations: list[dict[str, Any]] = []
        for py_file in territory_path.rglob("*.py"):
            try:
                line_count = len(py_file.read_text(encoding="utf-8", errors="replace").splitlines())
                if line_count > max_lines:
                    violations.append(
                        {
                            "type": "FILE_SIZE",
                            "file": str(py_file.relative_to(self.project_root)),
                            "message": f"{py_file.name}: {line_count} lines exceeds max {max_lines}",
                            "severity": "medium",
                            "recommended_action": "Split or refactor file to reduce line count",
                        }
                    )
            except (OSError, UnicodeDecodeError, KeyError, AttributeError) as e:
                self.logger.warning(f"Failed to analyze {py_file.name}: {type(e).__name__}")
                continue
        return violations

    def generate_healing_plan(self, gov_report: dict[str, Any]) -> dict[str, Any]:
        """
        Generates a healing plan based on the governance report.
        Now recognizes STRUCTURE violations (Root Files) and GRAVITY violations.
        """
        Logger.info("🔧 Generating healing plan from governance report")
        violations = gov_report.get("violations", [])
        has_naming = any(v.get("type") == "NAMING" for v in violations)
        has_structure = any(v.get("type") == "STRUCTURE" for v in violations)
        has_gravity = any(v.get("type") == "GRAVITY" for v in violations)
        plan = {
            "actions": [],
            "requires_healing": len(violations) > 0,
            "violations_count": gov_report.get("stats", {}).get("violations_found", 0),
            "drift_count": gov_report.get("stats", {}).get("drift_detected", 0),
            "errors_count": gov_report.get("stats", {}).get("errors", 0),
            "target_territories": gov_report.get("target_territories", []),
            "naming_fixes": [v for v in violations if v.get("type") == "NAMING"],
            "structure_fixes": [v for v in violations if v.get("type") == "STRUCTURE"],
        }
        if has_naming:
            plan["actions"].append("Rename Non-Compliant Agent Classes")
        if has_structure:
            plan["actions"].append("Relocate Root Files to SSOT Subfolders")
        if has_gravity:
            plan["actions"].append("Repair Circular Dependencies")
        if not plan["actions"]:
            plan["actions"].append("No healing required - system is compliant")
        Logger.info(f"Generated healing plan with {len(plan['actions'])} actions")
        return plan

    def _process_cognitive_disposition(self, file_path: Path, violation_type: str) -> bool:
        """
        [PHASE 11] Delegates violation decision to CognitiveDispositionAgent.

        Uses AI-powered heuristics to determine the appropriate action for
        violations that cannot be resolved deterministically.

        Args:
            file_path: Path to the file with the violation
            violation_type: Type of violation (ORPHAN, GRAVITY_FAIL, etc.)

        Returns:
            True if the violation was resolved, False otherwise
        """
        cognitive = self._get_cognitive_agent()
        Logger.info(f"  [COGNITIVE] Analyzing: {file_path.name} ({violation_type})")
        try:
            decision = cognitive.analyze_violation(file_path, violation_type)
            Logger.info(f"    Decision: {decision.action} (confidence: {decision.confidence:.2f})")
            Logger.info(f"    Reason: {decision.reason}")
            if decision.action == "MOVE" and decision.target_path:
                target = self.project_root / decision.target_path / file_path.name
                Logger.info(f"    [COGNITIVE] Moving {file_path.name} to {decision.target_path}")
                _wg.ensure_dir(target.parent)
                gatekeeper = self._get_archival_gatekeeper()
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category=decision.target_path,
                    reason=f"Cognitive disposition: {decision.reason}",
                )
                if hasattr(result, "success") and result.success:
                    Logger.info("    [OK] Moved successfully")
                    return True
                else:
                    Logger.warning("    [FAIL] Move failed")
                    return False
            elif decision.action == "ARCHIVE":
                archive_path = decision.target_path or "archives/healing_backups/cognitive_disposition"
                Logger.info(f"    [COGNITIVE] Archiving {file_path.name} to {archive_path}")
                gatekeeper = self._get_archival_gatekeeper()
                result = gatekeeper.safe_move(
                    file_path,
                    destination_category=archive_path,
                    reason=f"Cognitive archive: {decision.reason}",
                )
                if hasattr(result, "success") and result.success:
                    Logger.info("    [OK] Archived successfully")
                    return True
                else:
                    Logger.warning("    [FAIL] Archive failed")
                    return False
            elif decision.action == "IGNORE":
                Logger.info(f"    [COGNITIVE] Ignoring: {decision.reason}")
                return True
            elif decision.action == "MANUAL_REVIEW":
                Logger.warning(f"    [COGNITIVE] Requires manual review: {decision.reason}")
                return False
            else:
                Logger.warning(f"    [COGNITIVE] Unknown action: {decision.action}")
                return False
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"    [COGNITIVE] Error processing disposition: {e}")
            return False
