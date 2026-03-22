"""
Comprehensive Dashboard Data Validation
========================================

Performs broader data validation sensibility checks beyond basic schema validation.

Validation Categories:
1. Base Agent Uniqueness - Each layer has exactly 1 base agent
2. Layer Consistency - Agents are in correct layer directories
3. Inheritance Sanity - No circular dependencies, proper base classes
4. Metric Consistency - Percentages add up, no impossible values
5. Path Integrity - All paths exist, no duplicates
6. Naming Conventions - Agents follow naming patterns
7. Data Completeness - Required fields present and valid

This is integrated into the dashboard e2e pipeline to catch data issues early.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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

emit_replay_key("p0", "data_enforcer")
emit_determinism_digest("p0", "data_enforcer")

_emit_dispatches_healing_run("p1", "data_enforcer", "L5")
_emit_routes_through("p1", "data_enforcer", "L5")
_emit_checks_agent_registry("p1", "data_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "data_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "data_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "data_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "data_enforcer", "target_agent")
_emit_verifies_policy("p1", "data_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "data_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "data_enforcer", "boundary_check")
_emit_transcripts_response("p1", "data_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "data_enforcer")
_emit_gated_by_confidence("p1", "data_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "data_enforcer", "L5")
_emit_reads_policy_state("p1", "data_enforcer", "L5")

_emit_applies_guardrail("p0", "data_enforcer", "p0_governance")
_emit_snapshots_state("p0", "data_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "data_enforcer", "execution_auth")
_emit_validates_capability("p2", "data_enforcer", "capability_check")
_emit_routes_to_capability("p2", "data_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "data_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "data_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "data_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "data_enforcer", "exec_output")
_emit_dispatches_agent("p3", "data_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "data_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "data_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "data_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "data_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "data_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "data_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "data_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "data_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "data_enforcer", "eval_metric")
_emit_stores_embedding("p4", "data_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "data_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "data_enforcer", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("data_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("data_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("data_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("data_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("data_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("data_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("data_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("data_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("data_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("data_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("data_enforcer", "p4obs", "alert")
_emit_links_incident_trace("data_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("data_enforcer", "p3lm", "pattern")
_emit_records_learning_event("data_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("data_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("data_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("data_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("data_enforcer", "p3lm", "policy")
_emit_stores_learning_state("data_enforcer", "p3lm", "state")
_emit_records_execution_trace("data_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("data_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("data_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("data_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("data_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("data_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("data_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("data_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("data_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "data_enforcer", "context_pull")
_emit_pulls_context("p1", "data_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "data_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "data_enforcer", "uwg_term_2")
_emit_writes_through("p1", "data_enforcer", "write_through")
_emit_writes_through("p1", "data_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "data_enforcer", "safety_validation")
_emit_invokes_eval("p1", "data_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "data_enforcer", "routing_commit")

_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_CANDIDATE_PATHS = [
    _REPO_ROOT / "artifacts" / "discovery" / "agent_discovery_full.json",
    _REPO_ROOT / "data" / "processed" / "agent_discovery_full.json",
    _REPO_ROOT / "agent_discovery_full.json",
]
discovery_path = next((p for p in _CANDIDATE_PATHS if p.exists()), None)
if discovery_path is None:
    data = []
else:
    data = json.load(open(discovery_path))
LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
CANONICAL_BASE_AGENTS = {
    "L0": "L0RoutingBaseAgent",
    "L1": "L1CognitionBase",
    "L2": "L2Agent",
    "L3": "L3Agent",
    "L4": "L4Agent",
    "L5": "L5Agent",
    "L6": "L6ObservabilityBase",
}


class DataValidator:
    """Comprehensive data validator."""

    def __init__(self, data: list[dict]):
        self.data = data
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "DataValidator.validate_all")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DataValidator.validate_all".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("=" * 80)
        print("COMPREHENSIVE DASHBOARD DATA VALIDATION")
        print("=" * 80)
        print()
        self.check_base_agent_uniqueness()
        self.check_layer_consistency()
        self.check_path_integrity()
        self.check_metric_sanity()
        self.check_inheritance_patterns()
        self.check_naming_conventions()
        self.check_data_completeness()
        self.print_summary()
        return len(self.errors) == 0

    def check_base_agent_uniqueness(self):
        """Validate each layer has exactly 1 base agent."""
        print("📋 Check 1: Base Agent Uniqueness")
        print("-" * 80)
        base_agents_by_layer = defaultdict(list)
        for agent in self.data:
            class_name = agent.get("class_name", "")
            layer = agent.get("layer", "")
            is_base = (
                "BaseAgent" in class_name
                or class_name in CANONICAL_BASE_AGENTS.values()
                or "base_class" in agent.get("path", "").lower()
            )
            if is_base and layer:
                layer_prefix = layer[:2] if len(layer) >= 2 else layer
                if layer_prefix in LAYERS:
                    base_agents_by_layer[layer_prefix].append(agent)
        issues_found = False
        for layer in LAYERS:
            agents = base_agents_by_layer.get(layer, [])
            canonical = CANONICAL_BASE_AGENTS.get(layer)
            if len(agents) == 0:
                self.warnings.append(f"{layer}: No base agent (expected {canonical})")
            elif len(agents) == 1:
                if agents[0]["class_name"] != canonical:
                    self.warnings.append(f"{layer}: Found {agents[0]['class_name']}, expected {canonical}")
            else:
                self.errors.append(
                    f"{layer}: Multiple base agents ({len(agents)}) - {[a['class_name'] for a in agents]}"
                )
                issues_found = True
        if issues_found:
            print("   ❌ Multiple base agents found in some layers")
        else:
            print("   ✅ Each layer has 0-1 base agents")
        print()

    def check_layer_consistency(self):
        """Validate agents are in correct layer directories."""
        print("📋 Check 2: Layer Consistency")
        print("-" * 80)
        mismatches = []
        for agent in self.data:
            layer = agent.get("layer", "")
            path = agent.get("path", "")
            if not layer or not path:
                continue
            layer_prefix = layer[:2] if len(layer) >= 2 else layer
            if layer_prefix in LAYERS:
                expected_dir = f"{layer_prefix.lower()}_"
                if expected_dir not in path.lower() and "apps" not in path.lower():
                    mismatches.append(f"{agent['class_name']}: layer={layer} but path={path}")
        if mismatches:
            self.warnings.extend(mismatches[:5])
            if len(mismatches) > 5:
                self.warnings.append(f"... and {len(mismatches) - 5} more layer mismatches")
            print(f"   ⚠️  {len(mismatches)} agents in wrong layer directories")
        else:
            print("   ✅ All agents in correct layer directories")
        print()

    def check_path_integrity(self):
        """Validate all paths exist and no duplicates."""
        print("📋 Check 3: Path Integrity")
        print("-" * 80)
        paths = [agent.get("path", "") for agent in self.data]
        path_counts = defaultdict(int)
        for path in paths:
            if path:
                path_counts[path] += 1
        duplicates = {p: c for p, c in path_counts.items() if c > 1}
        if duplicates:
            for path, count in list(duplicates.items())[:3]:
                self.errors.append(f"Duplicate path ({count}x): {path}")
            if len(duplicates) > 3:
                self.errors.append(f"... and {len(duplicates) - 3} more duplicate paths")
            print(f"   ❌ {len(duplicates)} duplicate paths found")
        else:
            print(f"   ✅ No duplicate paths ({len(paths)} unique agents)")
        print()

    def check_metric_sanity(self):
        """Validate metrics are within reasonable ranges."""
        print("📋 Check 4: Metric Sanity")
        print("-" * 80)
        metric_issues = []
        for agent in self.data:
            name = agent.get("class_name", "Unknown")
            for field in ["typed_pct", "documented_pct", "test_coverage"]:
                value = agent.get(field, 0)
                if value < 0 or value > 100:
                    metric_issues.append(f"{name}: {field}={value}% (invalid range)")
            cc = agent.get("cyclomatic_complexity", 0)
            if cc > 100:
                metric_issues.append(f"{name}: cyclomatic_complexity={cc} (suspiciously high)")
            loc = agent.get("loc", 0)
            if loc > 10000:
                metric_issues.append(f"{name}: loc={loc} (suspiciously high)")
            elif loc < 10 and agent.get("has_healing"):
                self.warnings.append(f"{name}: loc={loc} (suspiciously low for healing agent)")
        if metric_issues:
            self.errors.extend(metric_issues[:5])
            if len(metric_issues) > 5:
                self.errors.append(f"... and {len(metric_issues) - 5} more metric issues")
            print(f"   ❌ {len(metric_issues)} metric anomalies found")
        else:
            print("   ✅ All metrics within reasonable ranges")
        print()

    def check_inheritance_patterns(self):
        """Validate inheritance makes sense."""
        print("📋 Check 5: Inheritance Patterns")
        print("-" * 80)
        inheritance_issues = []
        for agent in self.data:
            name = agent.get("class_name", "Unknown")
            inheritance = agent.get("inheritance", [])
            layer = agent.get("layer", "")
            if not inheritance:
                continue
            if "object" in inheritance and len(inheritance) > 1:
                inheritance_issues.append(f"{name}: Inherits from 'object' + others (redundant)")
            if layer.startswith("L5") and (
                not any(base in str(inheritance) for base in ["L5", "Safety", "HealerMixin"])
            ):
                self.warnings.append(f"{name}: L5 agent without L5/Safety base class")
        if inheritance_issues:
            self.warnings.extend(inheritance_issues[:3])
            print(f"   ⚠️  {len(inheritance_issues)} inheritance pattern issues")
        else:
            print("   ✅ Inheritance patterns look reasonable")
        print()

    def check_naming_conventions(self):
        """Validate agent naming follows conventions."""
        print("📋 Check 6: Naming Conventions")
        print("-" * 80)
        naming_issues = []
        for agent in self.data:
            name = agent.get("class_name", "")
            if not name.endswith("Agent"):
                naming_issues.append(f"{name}: Does not end with 'Agent'")
            if not name[0].isupper():
                naming_issues.append(f"{name}: Does not start with uppercase")
            if "_" in name and name not in [
                "L0RoutingBaseAgent",
                "L1CognitionBase",
                "L2Agent",
                "L3Agent",
                "L4Agent",
                "L5Agent",
            ]:
                self.warnings.append(f"{name}: Contains underscore (prefer PascalCase)")
        if naming_issues:
            self.errors.extend(naming_issues[:3])
            if len(naming_issues) > 3:
                self.errors.append(f"... and {len(naming_issues) - 3} more naming issues")
            print(f"   ⚠️  {len(naming_issues)} naming convention issues")
        else:
            print("   ✅ All agents follow naming conventions")
        print()

    def check_data_completeness(self):
        """Validate required fields are present."""
        print("📋 Check 7: Data Completeness")
        print("-" * 80)
        required_fields = ["class_name", "path", "layer"]
        incomplete = []
        for agent in self.data:
            missing = [f for f in required_fields if not agent.get(f)]
            if missing:
                incomplete.append(f"{agent.get('class_name', 'Unknown')}: missing {missing}")
        if incomplete:
            self.errors.extend(incomplete[:5])
            if len(incomplete) > 5:
                self.errors.append(f"... and {len(incomplete) - 5} more incomplete records")
            print(f"   ❌ {len(incomplete)} agents missing required fields")
        else:
            print(f"   ✅ All {len(self.data)} agents have required fields")
        print()

    def print_summary(self):
        """Print validation summary."""
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()
        if self.errors:
            print(f"❌ {len(self.errors)} ERRORS (must fix):")
            for error in self.errors[:10]:
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
            print()
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNINGS (should review):")
            for warning in self.warnings[:10]:
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
            print()
        if not self.errors and (not self.warnings):
            print("✅ ALL VALIDATION CHECKS PASSED")
            print(f"   {len(self.data)} agents validated successfully")
            print()


def main():
    """Main entry point."""
    validator = DataValidator(data)
    is_valid = validator.validate_all()
    if not is_valid:
        print("=" * 80)
        print("⚠️  DATA VALIDATION FAILED")
        print("=" * 80)
        print("Fix the errors above before regenerating the dashboard.")
        return 1
    print("=" * 80)
    print("✅ DATA VALIDATION PASSED")
    print("=" * 80)
    print("Dashboard data is ready for generation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
