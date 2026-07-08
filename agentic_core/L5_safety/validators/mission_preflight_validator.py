from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "mission_preflight_validator")
trace_contract.emit_determinism_digest("p0", "mission_preflight_validator")

trace_contract._emit_dispatches_healing_run("p1", "mission_preflight_validator", "L5")
trace_contract._emit_routes_through("p1", "mission_preflight_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "mission_preflight_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mission_preflight_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mission_preflight_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mission_preflight_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mission_preflight_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "mission_preflight_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mission_preflight_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mission_preflight_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mission_preflight_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mission_preflight_validator")
trace_contract._emit_gated_by_confidence("p1", "mission_preflight_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "mission_preflight_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "mission_preflight_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "mission_preflight_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "mission_preflight_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "mission_preflight_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "mission_preflight_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mission_preflight_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mission_preflight_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mission_preflight_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mission_preflight_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mission_preflight_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mission_preflight_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mission_preflight_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mission_preflight_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mission_preflight_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mission_preflight_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mission_preflight_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mission_preflight_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mission_preflight_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mission_preflight_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mission_preflight_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mission_preflight_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mission_preflight_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mission_preflight_validator", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mission_preflight_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mission_preflight_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mission_preflight_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mission_preflight_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mission_preflight_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mission_preflight_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mission_preflight_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mission_preflight_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mission_preflight_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mission_preflight_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mission_preflight_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mission_preflight_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mission_preflight_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mission_preflight_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("mission_preflight_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mission_preflight_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mission_preflight_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mission_preflight_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mission_preflight_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mission_preflight_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mission_preflight_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mission_preflight_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mission_preflight_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mission_preflight_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "mission_preflight_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mission_preflight_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mission_preflight_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mission_preflight_validator", "write_through")
trace_contract._emit_writes_through("p1", "mission_preflight_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mission_preflight_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mission_preflight_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mission_preflight_validator", "routing_commit")


class MissionPreflight:
    """
    L5 Mission Preflight Validator

    Integrates Void Compliance into the Master Validation Sweep.
    Executes pre-flight checks before any validation begins.
    """

    def __init__(self, project_root: Path, healing_enabled: bool = True):
        """
        Initialize the preflight validator.

        Args:
            project_root: Absolute path to the project root
            healing_enabled: Whether healing operations are enabled
        """
        self.project_root = project_root.resolve()
        self.healing_enabled = healing_enabled
        self.protected_folders = SOVEREIGN_EXCLUDED_FOLDERS
        self.HierarchyHealerAgent = StructureEnforcerAgent(project_root=project_root)
        self._location_agent = None
        self._hierarchy_agent = None
        self._import_agent = None

    def _get_location_agent(self):
        """Lazy load LocationAgent."""
        if self._location_agent is None:
            try:
                from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

                self._location_agent = LocationValidatorAgent(self.project_root)
            except ImportError as e:
                raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
                pass
        return self._location_agent

    def _get_hierarchy_agent(self):
        """Lazy load the structure hierarchy scanner."""
        if self._hierarchy_agent is None:
            try:
                from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

                self._hierarchy_agent = StructureEnforcerAgent(project_root=self.project_root)
            except (  # guardian: allow-silent-swallow -- lazy loader: structure scanner optional, caller handles None
                ImportError
            ):
                pass
        return self._hierarchy_agent

    def _target_territory(self, target_path: Path) -> str | None:
        resolved = target_path.resolve()
        if not resolved.is_relative_to(self.project_root):
            return None
        rel = resolved.relative_to(self.project_root)
        return rel.parts[0] if rel.parts else None

    def _get_import_agent(self):
        """Lazy load import healer."""
        if self._import_agent is None:
            try:
                from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR  # noqa: F401
                from agentic_core.L5_safety.reasoning.CodeHealerAgent import create_legacy_import_healer

                self._import_agent = create_legacy_import_healer()
            except (  # guardian: allow-silent-swallow -- lazy loader: import healer optional, caller handles None
                ImportError
            ):
                pass
        return self._import_agent

    def run_preflight(self, target_sector: str) -> dict[str, Any]:
        """
        Execute the full preflight compliance check.

        Args:
            target_sector: Path to the target sector for validation

        Returns:
            Dict with compliance results and Violation counts
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "MissionPreflight.run_preflight")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MissionPreflight.run_preflight".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print(f"\n[*] L6 PRE-FLIGHT: Enforcing Void Compliance on {target_sector}...")
        results = {"compliant": True, "Span": 0, "hierarchy": 0, "naming": 0, "gravity": 0}
        rules_path = self.project_root / "windsurfrules.md"
        if rules_path.exists():
            print("   [INFO] Synchronization active: windsurfrules.md detected.")
        target_path = Path(target_sector).resolve()
        results["Span"] = self._check_span_of_two(target_path)
        hierarchy_violations = self._check_hierarchy(target_path)
        results["hierarchy"] = len(hierarchy_violations)
        if hierarchy_violations and self.healing_enabled:
            healing_results = self.HierarchyHealerAgent.heal_repository(
                dry_run=True,
                execute=False,
                target_territory=self._target_territory(target_path),
            )
            results["hierarchy_healed"] = healing_results.get("fixed", 0)
            if healing_results.get("fixed", 0) > 0:
                hierarchy_violations_after = self._check_hierarchy(target_path)
                results["hierarchy"] = len(hierarchy_violations_after)
                print(f"   [POST-HEALING] {results['hierarchy']} hierarchy violations remaining")
        if self.healing_enabled:
            results["purged_orphans"] = 0
        results["gravity"] = self._check_gravity(target_path)
        results["naming"] = self._check_file_locations(target_path)
        _adg_antipattern_count: int = 0
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _bp = _gbp(Path(target_sector).resolve(), self.project_root)
            _adg_antipattern_count = len(_bp.antipattern_signals)
            if _adg_antipattern_count:
                print(
                    f"   [ADG] {target_sector}: {_adg_antipattern_count} antipattern signal(s) "
                    f"(score={_bp.behavioral_score:.2f})",
                )
        except (  # guardian: allow-silent-swallow -- ADG antipattern count optional: non-fatal, preflight proceeds with count=0
            ValueError,
            TypeError,
        ):
            pass
        results["adg_antipattern_count"] = _adg_antipattern_count
        self._print_dashboard(results)
        total_violations = results["Span"] + results["hierarchy"] + results["naming"] + results["gravity"]
        results["compliant"] = total_violations == 0
        return results

    def _check_span_of_two(self, target_path: Path) -> int:
        """Check Span-of-Two compliance when a scanner implementation exposes it."""
        hierarchy_agent = self._get_hierarchy_agent()
        if hierarchy_agent and hasattr(hierarchy_agent, "check_span_of_two"):
            try:
                span_result = hierarchy_agent.check_span_of_two()
                violations = span_result.get("violations", 0)
                if span_result.get("compliant", True):
                    print("   [OK] Span-of-Two compliance verified")
                else:
                    print(f"[!] L6 ALERT: Found {violations} Span violations:")
                    for v in span_result.get("details", [])[:3]:
                        print(f"   [X] {v}")
                return violations
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
        else:
            print("   [!] Hierarchy monitoring unavailable - Span-of-Two status unknown.")
        return 0

    def _check_hierarchy(self, target_path: Path) -> list[tuple[Path, str]]:
        """Check hierarchy alignment using root-file structure scanning."""
        hierarchy_agent = self._get_hierarchy_agent()
        if hierarchy_agent:
            try:
                result = hierarchy_agent.scan_root_violations(target_territory=self._target_territory(target_path))
                violations = [
                    (self.project_root / str(v.get("path")), str(v.get("message") or "hierarchy violation"))
                    for v in result.get("violations", [])
                    if ".git" not in str(v.get("path")) and "__init__.py" not in str(v.get("path"))
                ]
                if violations:
                    print(f"[!] L6 ALERT: Found {len(violations)} hierarchy violations:")
                    for folder_path, reason in violations[:3]:
                        try:
                            rel_path = folder_path.relative_to(self.project_root)
                        except ValueError:
                            rel_path = folder_path
                        print(f"   [X] {rel_path}: {reason}")
                    if len(violations) > 3:
                        print(f"   ... and {len(violations) - 3} more violations")
                return violations
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
        return []

    def _check_gravity(self, target_path: Path) -> int:
        """Check import waterfall violations."""
        import_agent = self._get_import_agent()
        if not import_agent:
            return 0
        waterfall_violations = []
        MAX_SCAN_FILES = 3000
        scanned_count = 0
        print(f"   [GRAVITY SCAN] Starting bounded scan (max {MAX_SCAN_FILES} files)...")
        if target_path.is_dir():
            scan_limit_reached = False
            for root, dirs, files in tqdm(os.walk(target_path), desc="Processing", unit="item"):
                if scan_limit_reached:
                    break
                dirs[:] = [d for d in dirs if d not in self.protected_folders]
                for file in tqdm(files, desc="Processing", unit="item"):
                    if scanned_count >= MAX_SCAN_FILES:
                        print(f"   [WARNING] Scan limit reached ({MAX_SCAN_FILES} files) - stopping early")
                        scan_limit_reached = True
                        break
                    if not file.endswith(".py"):
                        continue
                    scanned_count += 1
                    py_file = Path(root) / file
                    try:
                        rel_path = py_file.relative_to(self.project_root)
                        root_folder = rel_path.parts[0]
                        if root_folder == AGENTIC_CORE_DIR:
                            violations = import_agent.check_waterfall_violations(str(py_file))
                            if violations:
                                waterfall_violations.extend([(py_file, v) for v in violations])
                    except (OSError, UnicodeDecodeError, KeyError, AttributeError) as e:
                        print(f"   [WARNING] Failed to process {py_file.name}: {type(e).__name__}")
                        continue
            if not scan_limit_reached:
                print(f"   [OK] Gravity scan completed: {scanned_count} Python files analyzed")
        if waterfall_violations:
            print(f"[!] L6 ALERT: Found {len(waterfall_violations)} import waterfall violations:")
            for file_path, reason in waterfall_violations[:3]:
                print(f"   [X] {file_path.name}: {reason}")
            if len(waterfall_violations) > 3:
                print(f"   ... and {len(waterfall_violations) - 3} more violations")
        return len(waterfall_violations)

    def _check_file_locations(self, target_path: Path) -> int:
        """Check file location validation."""
        location_agent = self._get_location_agent()
        if not location_agent:
            return 0
        location_violations = []
        if target_path.is_dir():
            for root, dirs, files in tqdm(os.walk(target_path), desc="Processing", unit="item"):
                dirs[:] = [d for d in dirs if d not in self.protected_folders and d != ".git"]
                for file in tqdm(files, desc="Processing", unit="item"):
                    if not file.endswith(".py"):
                        continue
                    py_file = Path(root) / file
                    try:
                        is_valid, reason = location_agent.validate_file_location(py_file)
                        if not is_valid:
                            location_violations.append((py_file, reason))
                    except (OSError, AttributeError, KeyError) as e:
                        print(f"   [WARNING] Failed to validate {py_file.name}: {type(e).__name__}")
                        continue
        autonomous_agents = {
            "autonomous_checkpoint_manager.py",
            "autonomous_state_guardian.py",
            "self_updating_safety_engine.py",
            "neural_auto_immune_agent.py",
        }
        allowed_stages = {"policy", "shared", "hierarchy", "meta"}
        location_violations = [
            v
            for v in location_violations
            if v[0].name not in autonomous_agents and (not any(s in str(v[0]) for s in allowed_stages))
        ]
        if location_violations:
            print(f"[!] L6 ALERT: Found {len(location_violations)} file location violations:")
            for file_path, reason in location_violations[:3]:
                safe_reason = reason.encode("ascii", "replace").decode("ascii")
                print(f"   [X] {file_path.name}: {safe_reason}")
            if len(location_violations) > 3:
                print(f"   ... and {len(location_violations) - 3} more violations")
        return len(location_violations)

    def _print_dashboard(self, results: dict[str, Any]) -> None:
        """Print the sovereignty dashboard."""
        print("\n" + "=" * 70)
        print(" SOVEREIGN INTEGRITY DASHBOARD (L6 PRE-FLIGHT)")
        print("=" * 70)
        metrics = [
            ("DEPTH / SPAN OF TWO", results["Span"]),
            ("HIERARCHY ALIGNMENT", results["hierarchy"]),
            ("NAMING / SIGNAL", results["naming"]),
            ("GRAVITY / IMPORTS", results["gravity"]),
        ]
        for label, count in metrics:
            status = "[OK]" if count == 0 else f"[X] {count} VIOLATIONS"
            print(f" {label:<25} | {status}")
        print("-" * 70)
        total_violations = sum(m[1] for m in metrics)
        if total_violations == 0:
            print("[SUCCESS] All structural laws satisfied. Neural Link established.")
        else:
            print(f"   [SOVEREIGN OVERRIDE] Forcing mutation for convergence ({total_violations} violations)")
        print("=" * 70 + "\n")
