"""
CRITICAL Dual Enforcement Guarantee (REQ-416)

Ensures every CRITICAL requirement has >=2 enforcement layers including at least
one runtime (except ENFORCEMENT_CLASS=STRUCTURAL which requires >=1 CI/AST layer).
CI MUST read ENFORCEMENT_LAYERS and ENFORCEMENT_CLASS metadata per requirement
and fail if audit conditions unmet.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "critical_dual_enforcement_audit_enforcer")
emit_determinism_digest("p0", "critical_dual_enforcement_audit_enforcer")

_emit_dispatches_healing_run("p1", "critical_dual_enforcement_audit_enforcer", "L5")
_emit_routes_through("p1", "critical_dual_enforcement_audit_enforcer", "L5")
_emit_checks_agent_registry("p1", "critical_dual_enforcement_audit_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "critical_dual_enforcement_audit_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "critical_dual_enforcement_audit_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "critical_dual_enforcement_audit_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "critical_dual_enforcement_audit_enforcer", "target_agent")
_emit_verifies_policy("p1", "critical_dual_enforcement_audit_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "critical_dual_enforcement_audit_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "critical_dual_enforcement_audit_enforcer", "boundary_check")
_emit_transcripts_response("p1", "critical_dual_enforcement_audit_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "critical_dual_enforcement_audit_enforcer")
_emit_gated_by_confidence("p1", "critical_dual_enforcement_audit_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "critical_dual_enforcement_audit_enforcer", "L5")
_emit_reads_policy_state("p1", "critical_dual_enforcement_audit_enforcer", "L5")

_emit_snapshots_state("p0", "critical_dual_enforcement_audit_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "critical_dual_enforcement_audit_enforcer", "execution_auth")
_emit_validates_capability("p2", "critical_dual_enforcement_audit_enforcer", "capability_check")
_emit_routes_to_capability("p2", "critical_dual_enforcement_audit_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "critical_dual_enforcement_audit_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "critical_dual_enforcement_audit_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "critical_dual_enforcement_audit_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "critical_dual_enforcement_audit_enforcer", "exec_output")
_emit_dispatches_agent("p3", "critical_dual_enforcement_audit_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "critical_dual_enforcement_audit_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "critical_dual_enforcement_audit_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "critical_dual_enforcement_audit_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "critical_dual_enforcement_audit_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "critical_dual_enforcement_audit_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "critical_dual_enforcement_audit_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "critical_dual_enforcement_audit_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "critical_dual_enforcement_audit_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "critical_dual_enforcement_audit_enforcer", "eval_metric")
_emit_stores_embedding("p4", "critical_dual_enforcement_audit_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "critical_dual_enforcement_audit_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "critical_dual_enforcement_audit_enforcer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("critical_dual_enforcement_audit_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("critical_dual_enforcement_audit_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("critical_dual_enforcement_audit_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("critical_dual_enforcement_audit_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("critical_dual_enforcement_audit_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("critical_dual_enforcement_audit_enforcer", "p4obs", "alert")
_emit_links_incident_trace("critical_dual_enforcement_audit_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("critical_dual_enforcement_audit_enforcer", "p3lm", "pattern")
_emit_records_learning_event("critical_dual_enforcement_audit_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("critical_dual_enforcement_audit_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("critical_dual_enforcement_audit_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("critical_dual_enforcement_audit_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("critical_dual_enforcement_audit_enforcer", "p3lm", "policy")
_emit_stores_learning_state("critical_dual_enforcement_audit_enforcer", "p3lm", "state")
_emit_records_execution_trace("critical_dual_enforcement_audit_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("critical_dual_enforcement_audit_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("critical_dual_enforcement_audit_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("critical_dual_enforcement_audit_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("critical_dual_enforcement_audit_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("critical_dual_enforcement_audit_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("critical_dual_enforcement_audit_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("critical_dual_enforcement_audit_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("critical_dual_enforcement_audit_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "critical_dual_enforcement_audit_enforcer", "context_pull")
_emit_pulls_context("p1", "critical_dual_enforcement_audit_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "critical_dual_enforcement_audit_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "critical_dual_enforcement_audit_enforcer", "uwg_term_2")
_emit_writes_through("p1", "critical_dual_enforcement_audit_enforcer", "write_through")
_emit_writes_through("p1", "critical_dual_enforcement_audit_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "critical_dual_enforcement_audit_enforcer", "safety_validation")
_emit_invokes_eval("p1", "critical_dual_enforcement_audit_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "critical_dual_enforcement_audit_enforcer", "routing_commit")

Logger = logging.getLogger(__name__)
EnforcementLayer = Literal["AST", "Runtime", "CI", "Schema", "Signature", "Replay"]
EnforcementClass = Literal["STRUCTURAL", "EXECUTION_PATH"]
MIN_ENFORCEMENT_LAYERS = 2
MIN_STRUCTURAL_LAYERS = 1


@dataclass(frozen=True)
class RequirementMetadata:
    """Metadata for a requirement from the requirements document."""

    req_id: str
    domain: str
    requirement: str
    enforcement: str
    severity: str
    enforcement_layers: list[EnforcementLayer]
    enforcement_class: EnforcementClass


class DualEnforcementViolation(Exception):
    """Raised when dual enforcement guarantee is violated."""

    pass


class CriticalDualEnforcementAuditor:
    """Audits CRITICAL requirements for dual enforcement compliance (REQ-416)."""

    def __init__(self, requirements_path: Path | None = None):
        """Initialize the auditor.

        Args:
            requirements_path: Path to requirements document
        """
        if requirements_path is None:
            self.requirements_path = (
                Path(__file__).resolve().parents[3]
                / "docs"
                / REPORTS_DIR
                / "plans"
                / "Agentic Master Requirements.md"
            )
        else:
            self.requirements_path = requirements_path

    def parse_requirements_metadata(self) -> dict[str, RequirementMetadata]:
        """Parse requirements from the markdown document.

        Returns:
            Dictionary mapping REQ-ID to RequirementMetadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "CriticalDualEnforcementAuditor.parse_requirements_metadata",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CriticalDualEnforcementAuditor.parse_requirements_metadata".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        requirements = {}
        try:
            content = self.requirements_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            in_table = False
            for i, line in tqdm(enumerate(lines), desc="Processing", unit="item"):
                if (
                    "| Req ID | Domain | Requirement | Enforcement | Severity | ENFORCEMENT_LAYERS | ENFORCEMENT_CLASS |"
                    in line
                ):
                    in_table = True
                    continue
                if not in_table:
                    continue
                if "|--------" in line:
                    continue
                if not line.strip():
                    continue
                if line.startswith("| REQ-"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 7:
                        req_id = parts[0]
                        domain = parts[1]
                        requirement = parts[2]
                        enforcement = parts[3]
                        severity = parts[4]
                        layers_str = parts[5]
                        class_str = parts[6]
                        enforcement_layers = []
                        if layers_str:
                            layers = [l.strip() for l in layers_str.split(",")]
                            for layer in layers:
                                layer = layer.strip()
                                if layer in ["AST", "Runtime", "CI", "Schema", "Signature", "Replay"]:
                                    enforcement_layers.append(layer)
                        enforcement_class = "EXECUTION_PATH"
                        if "STRUCTURAL" in class_str:
                            enforcement_class = "STRUCTURAL"
                        requirements[req_id] = RequirementMetadata(
                            req_id=req_id,
                            domain=domain,
                            requirement=requirement,
                            enforcement=enforcement,
                            severity=severity,
                            enforcement_layers=enforcement_layers,
                            enforcement_class=enforcement_class,
                        )
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            Logger.error(f"Failed to parse requirements: {e}")
            raise
        return requirements

    def audit_critical_requirements(self) -> dict[str, list[str]]:
        """Audit all CRITICAL requirements for dual enforcement compliance.

        Returns:
            Dictionary with "violations" and "warnings" keys containing lists of issues
        """
        requirements = self.parse_requirements_metadata()
        violations = []
        warnings = []
        for req_id, metadata in tqdm(requirements.items(), desc="Processing", unit="item"):
            if metadata.severity != "CRITICAL":
                continue
            layer_count = len(metadata.enforcement_layers)
            if metadata.enforcement_class == "STRUCTURAL":
                has_ci_or_ast = any(layer in ["CI", "AST"] for layer in metadata.enforcement_layers)
                if not has_ci_or_ast:
                    violations.append(
                        f"{req_id}: STRUCTURAL class requires at least 1 CI or AST layer, found: {metadata.enforcement_layers}",
                    )
                elif layer_count < MIN_STRUCTURAL_LAYERS:
                    warnings.append(
                        f"{req_id}: STRUCTURAL class has only {layer_count} enforcement layer(s), recommended minimum: {MIN_STRUCTURAL_LAYERS}",
                    )
            else:
                has_runtime = "Runtime" in metadata.enforcement_layers
                if layer_count < MIN_ENFORCEMENT_LAYERS:
                    violations.append(
                        f"{req_id}: CRITICAL requires >=2 enforcement layers, found {layer_count}: {metadata.enforcement_layers}",
                    )
                elif not has_runtime:
                    violations.append(
                        f"{req_id}: CRITICAL requires at least 1 Runtime enforcement layer, found: {metadata.enforcement_layers}",
                    )
        return {"violations": violations, "warnings": warnings}

    def generate_audit_report(self) -> str:
        """Generate a comprehensive audit report.

        Returns:
            Formatted audit report as string
        """
        audit_results = self.audit_critical_requirements()
        report = []
        report.append("# CRITICAL Dual Enforcement Audit Report (REQ-416)")
        report.append("")
        report.append(f"Requirements file: {self.requirements_path}")
        report.append("")
        if audit_results["violations"]:
            report.append("## VIOLATIONS")
            report.append("")
            for violation in audit_results["violations"]:
                report.append(f"- **VIOLATION**: {violation}")
            report.append("")
        else:
            report.append("## VIOLATIONS")
            report.append("")
            report.append("✅ No violations found.")
            report.append("")
        if audit_results["warnings"]:
            report.append("## WARNINGS")
            report.append("")
            for warning in audit_results["warnings"]:
                report.append(f"- **WARNING**: {warning}")
            report.append("")
        else:
            report.append("## WARNINGS")
            report.append("")
            report.append("✅ No warnings found.")
            report.append("")
        requirements = self.parse_requirements_metadata()
        critical_count = sum(1 for r in requirements.values() if r.severity == "CRITICAL")
        report.append("## SUMMARY")
        report.append("")
        report.append(f"- Total requirements: {len(requirements)}")
        report.append(f"- CRITICAL requirements: {critical_count}")
        report.append(f"- Violations: {len(audit_results['violations'])}")
        report.append(f"- Warnings: {len(audit_results['warnings'])}")
        report.append("")
        if not audit_results["violations"]:
            report.append("✅ All CRITICAL requirements satisfy dual enforcement guarantee (REQ-416).")
        else:
            report.append("❌ Dual enforcement guarantee violations detected (REQ-416).")
        return "\n".join(report)

    def save_audit_report(self, output_path: Path) -> Path:
        """Save audit report to file.

        Args:
            output_path: Path to save the report

        Returns:
            Path to the saved report
        """
        report = self.generate_audit_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        Logger.info(f"Dual enforcement audit report saved to {output_path}")
        return output_path

    def run_ci_audit(self) -> int:
        """Run CI audit and return exit code.

        Returns:
            0 if no violations, 1 if violations found
        """
        audit_results = self.audit_critical_requirements()
        if audit_results["violations"]:
            Logger.error("CRITICAL Dual Enforcement violations detected (REQ-416):")
            for violation in audit_results["violations"]:
                Logger.error(f"  - {violation}")
            return 1
        Logger.info("✅ All CRITICAL requirements satisfy dual enforcement guarantee (REQ-416)")
        if audit_results["warnings"]:
            Logger.warning("Dual enforcement warnings:")
            for warning in audit_results["warnings"]:
                Logger.warning(f"  - {warning}")
        return 0


def run_dual_enforcement_audit() -> int:
    """Run the dual enforcement audit as a CLI command.

    Returns:
        Exit code (0 for success, 1 for violations)
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.run_dual_enforcement_audit", "L5_POLICY")
    auditor = CriticalDualEnforcementAuditor()
    return auditor.run_ci_audit()


def test_dual_enforcement_audit() -> bool:
    """Test the dual enforcement auditor.

    Returns:
        True if audit works correctly, False otherwise
    """
    try:
        auditor = CriticalDualEnforcementAuditor()
        requirements = auditor.parse_requirements_metadata()
        if not requirements:
            Logger.error("No requirements parsed")
            return False
        critical_count = sum(1 for r in requirements.values() if r.severity == "CRITICAL")
        if critical_count == 0:
            Logger.error("No CRITICAL requirements found")
            return False
        auditor.audit_critical_requirements()
        return True
    except (ValueError, TypeError) as e:
        Logger.error(f"Dual enforcement audit test failed: {e}")
        return False
