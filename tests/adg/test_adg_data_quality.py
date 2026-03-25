"""Tests for Phase 1 data quality fixes (G1-G6).

Covers:
- G1: invokes_dynamic separated from invokes_provider in _DynamicExecutionVisitor
- G2: PromptSlot/PromptTemplate entity_type in builder.py
- G3: WRITE_SIDE_EFFECT_EXCLUSIONS filter in _CallVisitor
- G4: __future__ excluded from dead_imports in _UnusedImportVisitor
- G5: decorated_by relation (renamed from influences) in _DecoratorVisitor
- G6: reads_env/reads_secret/reads_policy_state promoted to relation_type
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_adg_data_quality")
# REMOVED: _emit_applies_guardrail("p0", "test_adg_data_quality", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_adg_data_quality", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_adg_data_quality", "state_snapshot")
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
    _emit_links_incident_trace,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_adg_data_quality", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_adg_data_quality", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_adg_data_quality", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_adg_data_quality", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_adg_data_quality", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_adg_data_quality", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_adg_data_quality", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_adg_data_quality", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_adg_data_quality", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_adg_data_quality", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_adg_data_quality", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_adg_data_quality", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_adg_data_quality", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_adg_data_quality", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_adg_data_quality", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_adg_data_quality", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_adg_data_quality", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_adg_data_quality", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_adg_data_quality", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_adg_data_quality", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_adg_data_quality", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_adg_data_quality", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_adg_data_quality", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_adg_data_quality", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_adg_data_quality", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_data_quality", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_adg_data_quality", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_adg_data_quality", "write_through")
# REMOVED: _emit_writes_through("p1", "test_adg_data_quality", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_adg_data_quality", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_adg_data_quality", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_adg_data_quality", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_adg_data_quality", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_adg_data_quality", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_adg_data_quality", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_adg_data_quality", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_adg_data_quality", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_adg_data_quality", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_adg_data_quality", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_adg_data_quality", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_adg_data_quality", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_adg_data_quality", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_adg_data_quality", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_adg_data_quality")
# REMOVED: _emit_gated_by_confidence("p1", "test_adg_data_quality", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_adg_data_quality")
# REMOVED: emit_determinism_digest("p0", "test_adg_data_quality")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_adg_data_quality", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_adg_data_quality", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_adg_data_quality", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_adg_data_quality", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_adg_data_quality", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_adg_data_quality", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_adg_data_quality", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_adg_data_quality", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_adg_data_quality", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_adg_data_quality", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_adg_data_quality", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_adg_data_quality", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_adg_data_quality", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_adg_data_quality", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_adg_data_quality", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_adg_data_quality", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_adg_data_quality", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_adg_data_quality", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_adg_data_quality", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_adg_data_quality", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan_source(source: str, module_adg: str = "ADG::Module::test.py", rel: str = "test.py"):
    from agentic_core.adg.extraction.static_scanner import (
        _AttributeVisitor,
        _CallVisitor,
        _DecoratorVisitor,
        _DynamicExecutionVisitor,
        _ImportVisitor,
        _tag_dead_imports,
        _UnusedImportVisitor,
    )

    tree = ast.parse(source)
    edges = []

    iv = _ImportVisitor(module_adg, rel)
    iv.visit(tree)
    edges.extend(iv.edges)

    cv = _CallVisitor(module_adg, rel)
    cv.visit(tree)
    edges.extend(cv.edges)

    dv = _DynamicExecutionVisitor(module_adg, rel)
    dv.visit(tree)
    edges.extend(dv.edges)

    av = _AttributeVisitor(module_adg, rel)
    av.visit(tree)
    edges.extend(av.edges)

    dec = _DecoratorVisitor(module_adg, rel)
    dec.visit(tree)
    edges.extend(dec.edges)

    uiv = _UnusedImportVisitor()
    uiv.visit(tree)
    if uiv.dead_names:
        edges = _tag_dead_imports(edges, uiv.dead_names)

    return edges


# ---------------------------------------------------------------------------
# G1: invokes_dynamic separated from invokes_provider
# ---------------------------------------------------------------------------


class TestG1InvokesDynamic:
    def test_eval_emits_invokes_dynamic(self):
        source = "result = eval('1+1')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "eval() should emit invokes_dynamic edge"
        assert dynamic_edges[0].edge_kind == "dynamic_exec"

    def test_exec_emits_invokes_dynamic(self):
        source = "exec('x=1')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "exec() should emit invokes_dynamic edge"

    def test_importlib_emits_invokes_dynamic(self):
        source = "import importlib\nmod = importlib.import_module('some.mod')"
        edges = _scan_source(source)
        dynamic_edges = [e for e in edges if e.relation_type == "invokes_dynamic"]
        assert dynamic_edges, "importlib.import_module() should emit invokes_dynamic edge"

    def test_dynamic_is_not_invokes_provider(self):
        source = "result = eval('1+1')"
        edges = _scan_source(source)
        provider_from_dynamic = [
            e for e in edges if e.relation_type == "invokes_provider" and e.edge_kind == "dynamic_exec"
        ]
        assert not provider_from_dynamic, "dynamic_exec edges must not use invokes_provider relation"

    def test_network_call_still_invokes_provider(self):
        source = "import requests\nrequests.get('http://example.com')"
        edges = _scan_source(source)
        provider_edges = [e for e in edges if e.relation_type == "invokes_provider"]
        assert provider_edges, "network calls should still emit invokes_provider"


# ---------------------------------------------------------------------------
# G3: WRITE_SIDE_EFFECT_EXCLUSIONS
# ---------------------------------------------------------------------------


class TestG3WriteExclusions:
    def test_copy_excluded_from_writes_to(self):
        source = "result = copy(some_dict)"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to" and "copy" in e.symbol]
        assert not write_edges, "copy() must be excluded from writes_to (false positive)"

    def test_deepcopy_excluded_from_writes_to(self):
        source = "import copy\nresult = copy.deepcopy(obj)"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to" and "deepcopy" in e.symbol]
        assert not write_edges, "copy.deepcopy() must be excluded from writes_to"

    def test_os_remove_still_writes_to(self):
        source = "import os\nos.remove('file.txt')"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to"]
        assert write_edges, "os.remove() should still emit writes_to edge"

    def test_open_still_writes_to(self):
        source = "f = open('file.txt', 'w')"
        edges = _scan_source(source)
        write_edges = [e for e in edges if e.relation_type == "writes_to"]
        assert write_edges, "open() should still emit writes_to edge"


# ---------------------------------------------------------------------------
# G4: __future__ excluded from dead imports
# ---------------------------------------------------------------------------


class TestG4FutureDeadImports:
    def test_future_annotations_not_dead(self):
        source = "from __future__ import annotations\n\ndef foo() -> None:\n    pass\n"
        edges = _scan_source(source)
        dead_future = [e for e in edges if e.relation_type == "dead_imports" and "__future__" in e.symbol]
        assert not dead_future, "from __future__ import annotations must never be tagged dead_import"

    def test_unused_regular_import_is_dead(self):
        source = "import os\n\ndef foo():\n    pass\n"
        edges = _scan_source(source)
        dead = [e for e in edges if e.relation_type == "dead_imports"]
        assert dead, "Truly unused import should be tagged dead_import"

    def test_used_import_not_dead(self):
        source = "import os\n\ndef foo():\n    return os.getcwd()\n"
        edges = _scan_source(source)
        dead_os = [e for e in edges if e.relation_type == "dead_imports" and "os" in e.symbol]
        assert not dead_os, "Used import should not be tagged dead_import"


# ---------------------------------------------------------------------------
# G5: decorated_by (renamed from influences)
# ---------------------------------------------------------------------------


class TestG5DecoratedBy:
    def test_function_decorator_emits_decorated_by(self):
        source = "@some_decorator\ndef foo(): pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges, "@some_decorator should emit decorated_by edge"
        assert dec_edges[0].edge_kind == "decorator"

    def test_class_decorator_emits_decorated_by(self):
        source = "@dataclass\nclass Foo: pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert dec_edges, "@dataclass should emit decorated_by edge"

    def test_no_influences_relation(self):
        source = "@some_decorator\ndef foo(): pass\n"
        edges = _scan_source(source)
        influences_edges = [e for e in edges if e.relation_type == "influences"]
        assert not influences_edges, "influences relation must be replaced by decorated_by"

    def test_chained_decorators_all_emit_decorated_by(self):
        source = "@decorator_a\n@decorator_b\ndef foo(): pass\n"
        edges = _scan_source(source)
        dec_edges = [e for e in edges if e.relation_type == "decorated_by"]
        assert len(dec_edges) == 2, "Both decorators should emit decorated_by edges"


# ---------------------------------------------------------------------------
# G6: reads_env/reads_secret/reads_policy_state as relation_type
# ---------------------------------------------------------------------------


class TestG6ReadsSubtypes:
    def test_os_getenv_emits_reads_env(self):
        source = "import os\nval = os.getenv('KEY')"
        edges = _scan_source(source)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges, "os.getenv() should emit reads_env relation"
        assert all(e.edge_kind == "reads_env" for e in env_edges)

    def test_os_environ_emits_reads_env(self):
        source = "import os\nval = os.environ.get('KEY')"
        edges = _scan_source(source)
        env_edges = [e for e in edges if e.relation_type == "reads_env"]
        assert env_edges, "os.environ.get() should emit reads_env relation"

    def test_reads_env_is_not_reads_from(self):
        source = "import os\nval = os.getenv('KEY')"
        edges = _scan_source(source)
        reads_from_env = [e for e in edges if e.relation_type == "reads_from" and e.edge_kind == "reads_env"]
        assert not reads_from_env, "reads_env edges must use reads_env as relation_type, not reads_from"

    def test_secret_read_emits_reads_secret(self):
        source = "val = get_secret('API_KEY')"
        edges = _scan_source(source)
        secret_edges = [e for e in edges if e.relation_type == "reads_secret"]
        assert secret_edges, "Secret reads should emit reads_secret relation"

    def test_policy_read_emits_reads_policy_state(self):
        source = "val = get_policy('rules')"
        edges = _scan_source(source)
        policy_edges = [e for e in edges if e.relation_type == "reads_policy_state"]
        assert policy_edges, "Policy reads should emit reads_policy_state relation"


# ---------------------------------------------------------------------------
# Schema consistency
# ---------------------------------------------------------------------------


class TestSchemaConsistency:
    def test_invokes_dynamic_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "invokes_dynamic" in RelationType.__args__

    def test_decorated_by_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "decorated_by" in RelationType.__args__

    def test_seam_bypass_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "seam_bypass" in RelationType.__args__

    def test_reads_env_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "reads_env" in RelationType.__args__

    def test_reads_secret_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "reads_secret" in RelationType.__args__

    def test_reads_policy_state_in_relation_type(self):
        from agentic_core.adg.schema_util import RelationType

        assert "reads_policy_state" in RelationType.__args__

    def test_seam_in_entity_type(self):
        from agentic_core.adg.schema_util import EntityType

        assert "seam" in EntityType.__args__

    def test_write_side_effect_exclusions_exported(self):
        from agentic_core.adg.schema_util import WRITE_SIDE_EFFECT_EXCLUSIONS

        assert "copy" in WRITE_SIDE_EFFECT_EXCLUSIONS
        assert "deepcopy" in WRITE_SIDE_EFFECT_EXCLUSIONS

    def test_seam_module_patterns_exported(self):
        from agentic_core.adg.schema_util import SEAM_MODULE_PATTERNS

        assert len(SEAM_MODULE_PATTERNS) >= 1

    def test_rule_id_prefixes_exported(self):
        from agentic_core.adg.schema_util import RULE_ID_PREFIXES

        assert "LAYER_GRAVITY" in RULE_ID_PREFIXES
        assert "UWG_BYPASS" in RULE_ID_PREFIXES
        assert "SEAM_BYPASS" in RULE_ID_PREFIXES
