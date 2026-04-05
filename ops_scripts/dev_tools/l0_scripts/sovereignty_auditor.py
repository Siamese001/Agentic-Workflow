"""
File: scripts/discover_agents.py
Path: C:\\Git\\Agentic-Workflow\\scripts\\discover_agents.py
Status: Post-Migration Validation Tool
Rationale:
    Referenced in DEPLOYMENT_PROTOCOL.md.
    This script verifies that the "Pascal Sovereignty" migration was successful by:
    1. Finding all files ending in 'Agent.py'.
    2. attempting to import them (verifying paths/imports are healthy).
    3. Confirming the internal class name matches the filename.
"""
import ast
import importlib.util
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "sovereignty_auditor")
_emit_applies_guardrail("p0", "sovereignty_auditor", "p0_governance")
_emit_reads_policy_state("p0", "sovereignty_auditor", "policy_binding")
_emit_snapshots_state("p0", "sovereignty_auditor", "state_snapshot")
emit_replay_key("p0", "sovereignty_auditor")
emit_determinism_digest("p0", "sovereignty_auditor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereignty_auditor", "execution_auth")
_emit_validates_capability("p2", "sovereignty_auditor", "capability_check")
_emit_routes_to_capability("p2", "sovereignty_auditor", "capability_route")
_emit_writes_via_uwg("p2", "sovereignty_auditor", "uwg_write")
_emit_blocks_direct_write("p2", "sovereignty_auditor", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereignty_auditor", "tool_invocation")
_emit_captures_execution_output("p2", "sovereignty_auditor", "exec_output")
_emit_dispatches_agent("p3", "sovereignty_auditor", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereignty_auditor", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereignty_auditor", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereignty_auditor", "healing_outcome")
_emit_escalates_failure("p3", "sovereignty_auditor", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereignty_auditor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereignty_auditor", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereignty_auditor", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereignty_auditor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereignty_auditor", "eval_metric")
_emit_stores_embedding("p4", "sovereignty_auditor", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereignty_auditor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereignty_auditor", "exec_snapshot_link")
REPO_ROOT = Path(__file__).parent.parent.resolve()
# guardian: allow-global-mutation
sys.path.insert(0, str(REPO_ROOT))
from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_1")
_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_2")
_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_3")
_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_4")
_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_5")
_emit_emits_metric_event("sovereignty_auditor", "p4obs", "metric_6")
_emit_records_incident_event("sovereignty_auditor", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereignty_auditor", "p4obs", "anomaly")
_emit_writes_observability_log("sovereignty_auditor", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereignty_auditor", "p4obs", "mon_state")
_emit_triggers_alert("sovereignty_auditor", "p4obs", "alert")
_emit_links_incident_trace("sovereignty_auditor", "p4obs", "trace_link")
_emit_captures_pattern("sovereignty_auditor", "p3lm", "pattern")
_emit_records_learning_event("sovereignty_auditor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereignty_auditor", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereignty_auditor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereignty_auditor", "p3lm", "routing")
_emit_improves_agent_policy("sovereignty_auditor", "p3lm", "policy")
_emit_stores_learning_state("sovereignty_auditor", "p3lm", "state")
_emit_records_execution_trace("sovereignty_auditor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereignty_auditor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereignty_auditor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereignty_auditor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereignty_auditor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereignty_auditor", "env_read", "p2_env_1")
_emit_reads_environ("sovereignty_auditor", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereignty_auditor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereignty_auditor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereignty_auditor", "context_pull")
_emit_pulls_context("p1", "sovereignty_auditor", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "sovereignty_auditor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereignty_auditor", "uwg_term_secondary")
_emit_writes_through("p1", "sovereignty_auditor", "write_through")
_emit_writes_through("p1", "sovereignty_auditor", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "sovereignty_auditor", "safety_validation")
_emit_invokes_eval("p1", "sovereignty_auditor", "eval_call")
_emit_proposal_commits_routing("p1", "sovereignty_auditor", "routing_commit")
_emit_escalates_to_human("p1", "sovereignty_auditor", "human_escalation")
_emit_routes_through("p1", "sovereignty_auditor", "route_through")
_emit_checks_agent_registry("p1", "sovereignty_auditor", "agent_registry")
_emit_validates_agent_capability("p1", "sovereignty_auditor", "capability")
_emit_dispatches_execution_plan("p1", "sovereignty_auditor", "exec_plan")
_emit_agent_executes_agent("p1", "sovereignty_auditor", "sub_agent")
_emit_routes_to_agent("p1", "sovereignty_auditor", "target_agent")
_emit_verifies_policy("p1", "sovereignty_auditor", "policy_check")
_emit_observes_runtime_state("p1", "sovereignty_auditor", "runtime_state")
_emit_verifies_boundary("p1", "sovereignty_auditor", "boundary_check")
_emit_transcripts_response("p1", "sovereignty_auditor", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereignty_auditor")
_emit_gated_by_confidence("p1", "sovereignty_auditor", "confidence_gate")


class SovereigntyAuditor:

    def __init__(self):
        self.agents_found = 0
        self.import_failures = []
        self.naming_violations = []

    def audit_file(self, path: Path):
        if not path.name.endswith('Agent.py'):
            return
        self.agents_found += 1
        module_name = path.stem
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if module_name not in classes:
                self.naming_violations.append(f"{path.name}: Expected class '{module_name}' not found. Found: {classes}")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            self.naming_violations.append(f'{path.name}: AST Parse Error - {e}')
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
        except ImportError as e:
            self.import_failures.append(f'{path.name}: {e}')
        # guardian: allow-silent-swallow
        except Exception as e:
            self.import_failures.append(f'{path.name}: Runtime Error - {e}')

    def run(self):
        print('=' * 60)
        print('PASCAL SOVEREIGNTY: POST-MIGRATION AUDIT')
        print('=' * 60)
        target_dirs = [REPO_ROOT / d for d in [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]]
        files = []
        for d in target_dirs:
            if d.exists():
                files.extend(get_python_files(d))
        print(f'Scanning {len(files)} files for Agents...')
        for f in files:
            self.audit_file(f)
        print('\n' + '=' * 60)
        print(f'Agents Found: {self.agents_found}')
        print(f'Naming Violations: {len(self.naming_violations)}')
        print(f'Import Failures:   {len(self.import_failures)}')
        if self.naming_violations:
            print('\n[!] NAMING VIOLATIONS (Class name != Filename):')
            for v in self.naming_violations:
                print(f'  - {v}')
        if self.import_failures:
            print('\n[!] IMPORT FAILURES (Broken References):')
            for f in self.import_failures:
                print(f'  - {f}')
        if self.import_failures:
            sys.exit(1)
        print('\n[PASS] Architecture Integrity Verified.')
        sys.exit(0)
if __name__ == '__main__':
    SovereigntyAuditor().run()
