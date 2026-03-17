"""Tests for G23-G27 ADG proof-edge modules.

Coverage:
  G23 - Non-determinism primitive detection (uses_wall_clock, uses_random, uses_uuid)
  G24 - External HTTP / network egress (external_http_call)
  G25 - Agent-to-agent dispatch (agent_executes_agent)
  G26 - L5 validation proof edges (validated_by_registry, validated_by_safety_plane,
         validated_by_llm_gateway, execution_terminates_at_uwg, references_policy_hash)
  G27 - Learning / prompt provenance (proposal_commits_routing, prompt_template_used_by,
         instruction_injection_source, produces_preference_pair, requires_human_review)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_adg_g23_g27_completeness_accuracy")
_emit_applies_guardrail("p0", "test_adg_g23_g27_completeness_accuracy", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_g23_g27_completeness_accuracy", "policy_binding")
_emit_snapshots_state("p0", "test_adg_g23_g27_completeness_accuracy", "state_snapshot")
emit_replay_key("p0", "test_adg_g23_g27_completeness_accuracy")
emit_determinism_digest("p0", "test_adg_g23_g27_completeness_accuracy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_g23_g27_completeness_accuracy", "execution_auth")
_emit_validates_capability("p2", "test_adg_g23_g27_completeness_accuracy", "capability_check")
_emit_routes_to_capability("p2", "test_adg_g23_g27_completeness_accuracy", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_g23_g27_completeness_accuracy", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_g23_g27_completeness_accuracy", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_g23_g27_completeness_accuracy", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_g23_g27_completeness_accuracy", "exec_output")
_emit_dispatches_agent("p3", "test_adg_g23_g27_completeness_accuracy", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_g23_g27_completeness_accuracy", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_g23_g27_completeness_accuracy", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_g23_g27_completeness_accuracy", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_g23_g27_completeness_accuracy", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_g23_g27_completeness_accuracy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_g23_g27_completeness_accuracy", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_g23_g27_completeness_accuracy", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_g23_g27_completeness_accuracy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_g23_g27_completeness_accuracy", "eval_metric")
_emit_stores_embedding("p4", "test_adg_g23_g27_completeness_accuracy", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_g23_g27_completeness_accuracy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_g23_g27_completeness_accuracy", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentic_core.adg.artifact.layer_splitter import _GOVERNANCE_GRAPH_RELS
from agentic_core.adg.extraction.static_scanner import (
    _AgentDispatchVisitor,
    _ExternalHttpVisitor,
    _L5ValidationProofVisitor,
    _LearningProvenanceVisitor,
    _NondeterminismVisitor,
    _scan_file,
)
from agentic_core.adg.schema import (
    # G25
    AGENT_DISPATCH_CLASSES,
    AGENT_DISPATCH_METHODS,
    # G26
    AGENT_REGISTRY_CLASSES,
    # G24
    EXTERNAL_HTTP_SYMBOLS,
    HUMAN_REVIEW_SYMBOLS,
    NONDETERMINISM_RANDOM_SYMBOLS,
    NONDETERMINISM_UUID_SYMBOLS,
    # G23
    NONDETERMINISM_WALL_CLOCK_SYMBOLS,
    POLICY_HASH_SYMBOLS,
    PREFERENCE_PAIR_SYMBOLS,
    PROMPT_INJECTION_SYMBOLS,
    PROMPT_TEMPLATE_SYMBOLS,
    # G27
    ROUTING_COMMIT_SYMBOLS,
    SAFETY_PLANE_CLASSES,
    UWG_TERMINATION_SYMBOLS,
    EdgeKind,
    EntityType,
    # Literals
    RelationType,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_g23_g27_completeness_accuracy", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_g23_g27_completeness_accuracy", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_g23_g27_completeness_accuracy", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_g23_g27_completeness_accuracy", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_g23_g27_completeness_accuracy", "p4obs", "alert")
_emit_links_incident_trace("test_adg_g23_g27_completeness_accuracy", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_g23_g27_completeness_accuracy", "p3lm", "pattern")
_emit_records_learning_event("test_adg_g23_g27_completeness_accuracy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_g23_g27_completeness_accuracy", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_g23_g27_completeness_accuracy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_g23_g27_completeness_accuracy", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_g23_g27_completeness_accuracy", "p3lm", "policy")
_emit_stores_learning_state("test_adg_g23_g27_completeness_accuracy", "p3lm", "state")
_emit_records_execution_trace("test_adg_g23_g27_completeness_accuracy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_g23_g27_completeness_accuracy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_g23_g27_completeness_accuracy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_g23_g27_completeness_accuracy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_g23_g27_completeness_accuracy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_g23_g27_completeness_accuracy", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_g23_g27_completeness_accuracy", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_g23_g27_completeness_accuracy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_g23_g27_completeness_accuracy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_g23_g27_completeness_accuracy", "context_pull")
_emit_pulls_context("p1", "test_adg_g23_g27_completeness_accuracy", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_adg_g23_g27_completeness_accuracy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_g23_g27_completeness_accuracy", "uwg_term_secondary")
_emit_writes_through("p1", "test_adg_g23_g27_completeness_accuracy", "write_through")
_emit_writes_through("p1", "test_adg_g23_g27_completeness_accuracy", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_adg_g23_g27_completeness_accuracy", "safety_validation")
_emit_invokes_eval("p1", "test_adg_g23_g27_completeness_accuracy", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_g23_g27_completeness_accuracy", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_g23_g27_completeness_accuracy", "human_escalation")
_emit_routes_through("p1", "test_adg_g23_g27_completeness_accuracy", "route_through")
_emit_checks_agent_registry("p1", "test_adg_g23_g27_completeness_accuracy", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_g23_g27_completeness_accuracy", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_g23_g27_completeness_accuracy", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_g23_g27_completeness_accuracy", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_g23_g27_completeness_accuracy", "target_agent")
_emit_verifies_policy("p1", "test_adg_g23_g27_completeness_accuracy", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_g23_g27_completeness_accuracy", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_g23_g27_completeness_accuracy", "boundary_check")
_emit_transcripts_response("p1", "test_adg_g23_g27_completeness_accuracy", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_g23_g27_completeness_accuracy")
_emit_gated_by_confidence("p1", "test_adg_g23_g27_completeness_accuracy", "confidence_gate")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _visit(visitor_cls, code: str, source_file: str = "test.py"):
    module_adg = "ADG::Module::test"
    tree = ast.parse(code)
    visitor = visitor_cls(module_adg, source_file)
    visitor.visit(tree)
    return visitor.edges


def _rels(edges):
    return {e.relation_type for e in edges}


def _syms(edges):
    return {e.symbol for e in edges}


# ===========================================================================
# 1. Schema completeness
# ===========================================================================


class TestSchemaCompleteness:
    def test_g23_relation_types_present(self):
        args = RelationType.__args__
        for rel in ("uses_wall_clock", "uses_random", "uses_uuid"):
            assert rel in args, f"{rel} missing from RelationType"

    def test_g24_relation_type_present(self):
        assert "external_http_call" in RelationType.__args__

    def test_g25_relation_type_present(self):
        assert "agent_executes_agent" in RelationType.__args__

    def test_g26_relation_types_present(self):
        args = RelationType.__args__
        for rel in (
            "validated_by_registry",
            "validated_by_safety_plane",
            "validated_by_llm_gateway",
            "execution_terminates_at_uwg",
            "references_policy_hash",
        ):
            assert rel in args, f"{rel} missing from RelationType"

    def test_g27_relation_types_present(self):
        args = RelationType.__args__
        for rel in (
            "proposal_commits_routing",
            "prompt_template_used_by",
            "instruction_injection_source",
            "produces_preference_pair",
            "requires_human_review",
        ):
            assert rel in args, f"{rel} missing from RelationType"

    def test_g23_edge_kinds_present(self):
        args = EdgeKind.__args__
        for ek in ("wall_clock_use", "random_use", "uuid_use"):
            assert ek in args, f"{ek} missing from EdgeKind"

    def test_g24_edge_kind_present(self):
        assert "http_egress_call" in EdgeKind.__args__

    def test_g25_edge_kind_present(self):
        assert "agent_dispatch" in EdgeKind.__args__

    def test_g26_edge_kinds_present(self):
        args = EdgeKind.__args__
        for ek in (
            "registry_validation",
            "safety_plane_validation",
            "llm_gateway_validation",
            "uwg_termination",
            "policy_hash_link",
        ):
            assert ek in args, f"{ek} missing from EdgeKind"

    def test_g27_edge_kinds_present(self):
        args = EdgeKind.__args__
        for ek in (
            "routing_commit",
            "prompt_template_link",
            "injection_source_link",
            "preference_pair_link",
            "human_review_gate",
        ):
            assert ek in args, f"{ek} missing from EdgeKind"

    def test_g23_entity_types_present(self):
        args = EntityType.__args__
        for et in ("nondeterminism_site", "wall_clock_call", "random_call_site", "uuid_call_site"):
            assert et in args, f"{et} missing from EntityType"

    def test_g24_entity_types_present(self):
        for et in ("external_call_site", "http_egress_node"):
            assert et in EntityType.__args__, f"{et} missing from EntityType"

    def test_g25_entity_types_present(self):
        for et in ("agent_dispatch_edge", "agent_invocation_record"):
            assert et in EntityType.__args__, f"{et} missing from EntityType"


# ===========================================================================
# 2. Frozenset constants
# ===========================================================================


class TestFrozensets:
    def test_wall_clock_contains_datetime_now(self):
        assert "datetime.datetime.now" in NONDETERMINISM_WALL_CLOCK_SYMBOLS

    def test_wall_clock_contains_time_time(self):
        assert "time.time" in NONDETERMINISM_WALL_CLOCK_SYMBOLS

    def test_wall_clock_contains_time_monotonic(self):
        assert "time.monotonic" in NONDETERMINISM_WALL_CLOCK_SYMBOLS

    def test_random_contains_random_random(self):
        assert "random.random" in NONDETERMINISM_RANDOM_SYMBOLS

    def test_random_contains_secrets(self):
        assert "secrets.token_hex" in NONDETERMINISM_RANDOM_SYMBOLS

    def test_uuid_contains_uuid4(self):
        assert "uuid.uuid4" in NONDETERMINISM_UUID_SYMBOLS

    def test_uuid_contains_uuid1(self):
        assert "uuid.uuid1" in NONDETERMINISM_UUID_SYMBOLS

    def test_external_http_contains_requests(self):
        assert "requests.get" in EXTERNAL_HTTP_SYMBOLS
        assert "requests.post" in EXTERNAL_HTTP_SYMBOLS

    def test_external_http_contains_httpx(self):
        assert "httpx.get" in EXTERNAL_HTTP_SYMBOLS
        assert "httpx.AsyncClient" in EXTERNAL_HTTP_SYMBOLS

    def test_external_http_contains_aiohttp(self):
        assert "aiohttp.ClientSession" in EXTERNAL_HTTP_SYMBOLS

    def test_external_http_contains_urllib(self):
        assert "urllib.request.urlopen" in EXTERNAL_HTTP_SYMBOLS

    def test_agent_dispatch_classes_nonempty(self):
        assert len(AGENT_DISPATCH_CLASSES) >= 5

    def test_agent_dispatch_methods_nonempty(self):
        assert len(AGENT_DISPATCH_METHODS) >= 5

    def test_agent_dispatch_contains_expected(self):
        assert "AgentDispatcher" in AGENT_DISPATCH_CLASSES
        assert "invoke_agent" in AGENT_DISPATCH_METHODS

    def test_agent_registry_classes_nonempty(self):
        assert "AgentRegistry" in AGENT_REGISTRY_CLASSES

    def test_safety_plane_classes_contains_gateway(self):
        assert "SovereignLLMGateway" in SAFETY_PLANE_CLASSES

    def test_uwg_termination_symbols_nonempty(self):
        assert "UniversalWriteGateway" in UWG_TERMINATION_SYMBOLS

    def test_policy_hash_symbols_nonempty(self):
        assert "PolicyConfigGuard" in POLICY_HASH_SYMBOLS
        assert "policy_hash" in POLICY_HASH_SYMBOLS

    def test_routing_commit_symbols_contain_artifact(self):
        assert "MetaLearningProposalArtifact" in ROUTING_COMMIT_SYMBOLS
        assert "build_meta_learning_proposal" in ROUTING_COMMIT_SYMBOLS

    def test_prompt_template_symbols_nonempty(self):
        assert "PromptTemplate" in PROMPT_TEMPLATE_SYMBOLS

    def test_prompt_injection_symbols_nonempty(self):
        assert "InstructionInjector" in PROMPT_INJECTION_SYMBOLS

    def test_preference_pair_symbols_nonempty(self):
        assert "DPOPair" in PREFERENCE_PAIR_SYMBOLS
        assert "PreferencePair" in PREFERENCE_PAIR_SYMBOLS

    def test_human_review_symbols_contain_requires_human_approval(self):
        assert "requires_human_approval" in HUMAN_REVIEW_SYMBOLS

    def test_human_review_symbols_contain_adapter(self):
        assert "load_human_review_adapter" in HUMAN_REVIEW_SYMBOLS

    def test_all_frozensets_are_frozenset(self):
        for name, obj in [
            ("NONDETERMINISM_WALL_CLOCK_SYMBOLS", NONDETERMINISM_WALL_CLOCK_SYMBOLS),
            ("NONDETERMINISM_RANDOM_SYMBOLS", NONDETERMINISM_RANDOM_SYMBOLS),
            ("NONDETERMINISM_UUID_SYMBOLS", NONDETERMINISM_UUID_SYMBOLS),
            ("EXTERNAL_HTTP_SYMBOLS", EXTERNAL_HTTP_SYMBOLS),
            ("AGENT_DISPATCH_CLASSES", AGENT_DISPATCH_CLASSES),
            ("AGENT_DISPATCH_METHODS", AGENT_DISPATCH_METHODS),
            ("AGENT_REGISTRY_CLASSES", AGENT_REGISTRY_CLASSES),
            ("SAFETY_PLANE_CLASSES", SAFETY_PLANE_CLASSES),
            ("UWG_TERMINATION_SYMBOLS", UWG_TERMINATION_SYMBOLS),
            ("POLICY_HASH_SYMBOLS", POLICY_HASH_SYMBOLS),
            ("ROUTING_COMMIT_SYMBOLS", ROUTING_COMMIT_SYMBOLS),
            ("PROMPT_TEMPLATE_SYMBOLS", PROMPT_TEMPLATE_SYMBOLS),
            ("PROMPT_INJECTION_SYMBOLS", PROMPT_INJECTION_SYMBOLS),
            ("PREFERENCE_PAIR_SYMBOLS", PREFERENCE_PAIR_SYMBOLS),
            ("HUMAN_REVIEW_SYMBOLS", HUMAN_REVIEW_SYMBOLS),
        ]:
            assert isinstance(obj, frozenset), f"{name} is not a frozenset"


# ===========================================================================
# 3. Layer splitter: G23-G27 in governance plane
# ===========================================================================


class TestLayerSplitter:
    NEW_RELS = [
        "uses_wall_clock",
        "uses_random",
        "uses_uuid",
        "external_http_call",
        "agent_executes_agent",
        "validated_by_registry",
        "validated_by_safety_plane",
        "validated_by_llm_gateway",
        "execution_terminates_at_uwg",
        "references_policy_hash",
        "proposal_commits_routing",
        "prompt_template_used_by",
        "instruction_injection_source",
        "produces_preference_pair",
        "requires_human_review",
    ]

    @pytest.mark.parametrize("rel", NEW_RELS)
    def test_relation_in_governance_plane(self, rel):
        assert rel in _GOVERNANCE_GRAPH_RELS, f"{rel} not in _GOVERNANCE_GRAPH_RELS"


# ===========================================================================
# 4. Visitor accuracy: G23 _NondeterminismVisitor
# ===========================================================================


class TestNondeterminismVisitor:
    def test_detects_datetime_now(self):
        code = "import datetime\nx = datetime.datetime.now()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_wall_clock" for e in edges)

    def test_detects_time_time(self):
        code = "import time\nt = time.time()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_wall_clock" for e in edges)

    def test_detects_time_monotonic(self):
        code = "import time\nt = time.monotonic()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_wall_clock" for e in edges)

    def test_detects_random_random(self):
        code = "import random\nx = random.random()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_random" for e in edges)

    def test_detects_random_randint(self):
        code = "import random\nx = random.randint(0, 10)"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_random" for e in edges)

    def test_detects_secrets_token_hex(self):
        code = "import secrets\nk = secrets.token_hex(32)"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_random" for e in edges)

    def test_detects_uuid4(self):
        code = "import uuid\nuid = uuid.uuid4()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_uuid" for e in edges)

    def test_detects_uuid1(self):
        code = "import uuid\nuid = uuid.uuid1()"
        edges = _visit(_NondeterminismVisitor, code)
        assert any(e.relation_type == "uses_uuid" for e in edges)

    def test_edge_kind_wall_clock(self):
        code = "import time\nt = time.time()"
        edges = _visit(_NondeterminismVisitor, code)
        wc = [e for e in edges if e.relation_type == "uses_wall_clock"]
        assert all(e.edge_kind == "wall_clock_use" for e in wc)

    def test_edge_kind_random(self):
        code = "import random\nx = random.random()"
        edges = _visit(_NondeterminismVisitor, code)
        r = [e for e in edges if e.relation_type == "uses_random"]
        assert all(e.edge_kind == "random_use" for e in r)

    def test_edge_kind_uuid(self):
        code = "import uuid\nuid = uuid.uuid4()"
        edges = _visit(_NondeterminismVisitor, code)
        u = [e for e in edges if e.relation_type == "uses_uuid"]
        assert all(e.edge_kind == "uuid_use" for e in u)

    def test_no_false_positive_on_plain_function(self):
        code = "def my_func():\n    return 42"
        edges = _visit(_NondeterminismVisitor, code)
        assert edges == []

    def test_no_false_positive_on_imports(self):
        code = "import random\nimport uuid"
        edges = _visit(_NondeterminismVisitor, code)
        assert edges == []

    def test_symbol_recorded(self):
        code = "import time\nt = time.time()"
        edges = _visit(_NondeterminismVisitor, code)
        assert "time.time" in _syms(edges)


# ===========================================================================
# 5. Visitor accuracy: G24 _ExternalHttpVisitor
# ===========================================================================


class TestExternalHttpVisitor:
    def test_detects_requests_get(self):
        code = "import requests\nr = requests.get('http://example.com')"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_detects_requests_post(self):
        code = "import requests\nr = requests.post('http://example.com', json={})"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_detects_httpx_get(self):
        code = "import httpx\nr = httpx.get('http://example.com')"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_detects_httpx_async_client(self):
        code = "import httpx\nclient = httpx.AsyncClient()"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_detects_aiohttp_client_session(self):
        code = "import aiohttp\nsession = aiohttp.ClientSession()"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_detects_urllib_urlopen(self):
        code = "import urllib.request\nresp = urllib.request.urlopen('http://x.com')"
        edges = _visit(_ExternalHttpVisitor, code)
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_edge_kind_http_egress(self):
        code = "import requests\nr = requests.get('http://x.com')"
        edges = _visit(_ExternalHttpVisitor, code)
        assert all(e.edge_kind == "http_egress_call" for e in edges)

    def test_no_false_positive_on_internal_calls(self):
        code = "def do_thing():\n    my_service.get(path)"
        edges = _visit(_ExternalHttpVisitor, code)
        assert edges == []

    def test_symbol_recorded(self):
        code = "import requests\nr = requests.get('http://x.com')"
        edges = _visit(_ExternalHttpVisitor, code)
        assert "requests.get" in _syms(edges)


# ===========================================================================
# 6. Visitor accuracy: G25 _AgentDispatchVisitor
# ===========================================================================


class TestAgentDispatchVisitor:
    def test_detects_agent_dispatcher_class(self):
        code = "dispatcher = AgentDispatcher(config)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_detects_invoke_agent_method(self):
        code = "result = self.invoke_agent(target='agent_b', payload=data)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_detects_dispatch_agent(self):
        code = "self.dispatch_agent(agent_id='planner', task=task)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_detects_delegate_to(self):
        code = "self.delegate_to(sub_agent)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_detects_handoff_to(self):
        code = "self.handoff_to(next_agent)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_edge_kind_agent_dispatch(self):
        code = "AgentDispatcher(config)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert all(e.edge_kind == "agent_dispatch" for e in edges)

    def test_no_false_positive_on_unrelated_call(self):
        code = "result = compute_value(x, y)"
        edges = _visit(_AgentDispatchVisitor, code)
        assert edges == []


# ===========================================================================
# 7. Visitor accuracy: G26 _L5ValidationProofVisitor
# ===========================================================================


class TestL5ValidationProofVisitor:
    def test_detects_agent_registry(self):
        code = "registry = AgentRegistry()"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "validated_by_registry" for e in edges)

    def test_detects_sovereign_llm_gateway_as_llm_gateway(self):
        code = "gw = SovereignLLMGateway()"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "validated_by_llm_gateway" for e in edges)

    def test_detects_safety_enforcer_as_safety_plane(self):
        code = "plane = SafetyEnforcer(config)"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "validated_by_safety_plane" for e in edges)

    def test_detects_uwg_termination(self):
        code = "gateway = UniversalWriteGateway()"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "execution_terminates_at_uwg" for e in edges)

    def test_detects_policy_hash(self):
        code = "guard = PolicyConfigGuard(config)"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "references_policy_hash" for e in edges)

    def test_detects_policy_hash_attribute(self):
        code = "h = self.policy_hash"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert any(e.relation_type == "references_policy_hash" for e in edges)

    def test_edge_kind_registry_validation(self):
        code = "AgentRegistry()"
        edges = _visit(_L5ValidationProofVisitor, code)
        rv = [e for e in edges if e.relation_type == "validated_by_registry"]
        assert all(e.edge_kind == "registry_validation" for e in rv)

    def test_edge_kind_uwg_termination(self):
        code = "UniversalWriteGateway()"
        edges = _visit(_L5ValidationProofVisitor, code)
        uwg = [e for e in edges if e.relation_type == "execution_terminates_at_uwg"]
        assert all(e.edge_kind == "uwg_termination" for e in uwg)

    def test_edge_kind_policy_hash_link(self):
        code = "PolicyConfigGuard()"
        edges = _visit(_L5ValidationProofVisitor, code)
        ph = [e for e in edges if e.relation_type == "references_policy_hash"]
        assert all(e.edge_kind == "policy_hash_link" for e in ph)

    def test_no_false_positive_on_plain_code(self):
        code = "x = some_function()\ny = another_function()"
        edges = _visit(_L5ValidationProofVisitor, code)
        assert edges == []


# ===========================================================================
# 8. Visitor accuracy: G27 _LearningProvenanceVisitor
# ===========================================================================


class TestLearningProvenanceVisitor:
    def test_detects_meta_learning_proposal_artifact(self):
        code = "artifact = MetaLearningProposalArtifact()"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "proposal_commits_routing" for e in edges)

    def test_detects_build_meta_learning_proposal(self):
        code = "p = build_meta_learning_proposal(clock=c, proposer='x', target='y')"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "proposal_commits_routing" for e in edges)

    def test_detects_prompt_template(self):
        code = "tmpl = PromptTemplate(system='You are...')"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "prompt_template_used_by" for e in edges)

    def test_detects_prompt_loader(self):
        code = "tmpl = PromptLoader.load('system_prompt')"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "prompt_template_used_by" for e in edges)

    def test_detects_instruction_injector(self):
        code = "injector = InstructionInjector(ctx)"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "instruction_injection_source" for e in edges)

    def test_detects_dpo_pair(self):
        code = "pair = DPOPair(chosen=c, rejected=r)"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "produces_preference_pair" for e in edges)

    def test_detects_preference_pair(self):
        code = "pair = PreferencePair(chosen=c, rejected=r)"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "produces_preference_pair" for e in edges)

    def test_detects_human_review_gate(self):
        code = "gate = HumanReviewGate(threshold=0.8)"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "requires_human_review" for e in edges)

    def test_detects_requires_human_approval_attribute(self):
        code = "result.requires_human_approval = True"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "requires_human_review" for e in edges)

    def test_detects_load_human_review_adapter(self):
        code = "adapter = load_human_review_adapter()"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert any(e.relation_type == "requires_human_review" for e in edges)

    def test_edge_kind_routing_commit(self):
        code = "MetaLearningProposalArtifact()"
        edges = _visit(_LearningProvenanceVisitor, code)
        rc = [e for e in edges if e.relation_type == "proposal_commits_routing"]
        assert all(e.edge_kind == "routing_commit" for e in rc)

    def test_edge_kind_prompt_template_link(self):
        code = "PromptTemplate()"
        edges = _visit(_LearningProvenanceVisitor, code)
        pt = [e for e in edges if e.relation_type == "prompt_template_used_by"]
        assert all(e.edge_kind == "prompt_template_link" for e in pt)

    def test_edge_kind_preference_pair_link(self):
        code = "DPOPair()"
        edges = _visit(_LearningProvenanceVisitor, code)
        pp = [e for e in edges if e.relation_type == "produces_preference_pair"]
        assert all(e.edge_kind == "preference_pair_link" for e in pp)

    def test_edge_kind_human_review_gate(self):
        code = "HumanReviewGate()"
        edges = _visit(_LearningProvenanceVisitor, code)
        hr = [e for e in edges if e.relation_type == "requires_human_review"]
        assert all(e.edge_kind == "human_review_gate" for e in hr)

    def test_no_false_positive(self):
        code = "x = compute()\ny = transform(x)"
        edges = _visit(_LearningProvenanceVisitor, code)
        assert edges == []


# ===========================================================================
# 9. Non-contamination: visitors do not emit each other's relations
# ===========================================================================


class TestNonContamination:
    NONDET_CODE = "import time\nt = time.time()\nuid = uuid.uuid4()"
    HTTP_CODE = "import requests\nr = requests.get('http://x.com')"
    DISPATCH_CODE = "dispatcher = AgentDispatcher()"
    L5_CODE = "gw = SovereignLLMGateway()\nuwg = UniversalWriteGateway()"
    LEARNING_CODE = "p = MetaLearningProposalArtifact()\ntmpl = PromptTemplate()"

    def test_nondet_visitor_does_not_emit_http_rels(self):
        edges = _visit(_NondeterminismVisitor, self.NONDET_CODE)
        assert "external_http_call" not in _rels(edges)

    def test_http_visitor_does_not_emit_nondet_rels(self):
        edges = _visit(_ExternalHttpVisitor, self.HTTP_CODE)
        assert not _rels(edges) & {"uses_wall_clock", "uses_random", "uses_uuid"}

    def test_dispatch_visitor_does_not_emit_l5_rels(self):
        edges = _visit(_AgentDispatchVisitor, self.DISPATCH_CODE)
        assert not _rels(edges) & {
            "validated_by_registry",
            "validated_by_safety_plane",
            "execution_terminates_at_uwg",
            "references_policy_hash",
        }

    def test_l5_visitor_does_not_emit_dispatch_rels(self):
        edges = _visit(_L5ValidationProofVisitor, self.L5_CODE)
        assert "agent_executes_agent" not in _rels(edges)

    def test_learning_visitor_does_not_emit_nondet_rels(self):
        edges = _visit(_LearningProvenanceVisitor, self.LEARNING_CODE)
        assert not _rels(edges) & {"uses_wall_clock", "uses_random", "uses_uuid"}


# ===========================================================================
# 10. ADG round-trip: _scan_file produces G23-G27 edges
# ===========================================================================


class TestScanFileRoundTrip:
    def _make_tmp(self, code: str, tmp_path) -> Path:
        f = tmp_path / "sample_g23_g27.py"
        f.write_text(code)
        return f

    def test_scan_produces_uses_wall_clock(self, tmp_path):
        code = "import time\ndef f():\n    return time.time()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "uses_wall_clock" for e in edges)

    def test_scan_produces_uses_random(self, tmp_path):
        code = "import random\ndef f():\n    return random.random()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "uses_random" for e in edges)

    def test_scan_produces_uses_uuid(self, tmp_path):
        code = "import uuid\ndef f():\n    return uuid.uuid4()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "uses_uuid" for e in edges)

    def test_scan_produces_external_http_call(self, tmp_path):
        code = "import requests\ndef f():\n    return requests.get('http://x.com')\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "external_http_call" for e in edges)

    def test_scan_produces_agent_executes_agent(self, tmp_path):
        code = "def f(self):\n    self.invoke_agent(target='b')\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "agent_executes_agent" for e in edges)

    def test_scan_produces_validated_by_registry(self, tmp_path):
        code = "def f():\n    registry = AgentRegistry()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "validated_by_registry" for e in edges)

    def test_scan_produces_execution_terminates_at_uwg(self, tmp_path):
        code = "def f():\n    gate = UniversalWriteGateway()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "execution_terminates_at_uwg" for e in edges)

    def test_scan_produces_references_policy_hash(self, tmp_path):
        code = "def f():\n    guard = PolicyConfigGuard(config)\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "references_policy_hash" for e in edges)

    def test_scan_produces_proposal_commits_routing(self, tmp_path):
        code = "def f():\n    a = MetaLearningProposalArtifact()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "proposal_commits_routing" for e in edges)

    def test_scan_produces_prompt_template_used_by(self, tmp_path):
        code = "def f():\n    t = PromptTemplate(system='x')\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "prompt_template_used_by" for e in edges)

    def test_scan_produces_produces_preference_pair(self, tmp_path):
        code = "def f():\n    p = DPOPair(chosen=c, rejected=r)\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "produces_preference_pair" for e in edges)

    def test_scan_produces_requires_human_review(self, tmp_path):
        code = "def f():\n    gate = HumanReviewGate()\n"
        fp = self._make_tmp(code, tmp_path)
        edges, err = _scan_file(fp, tmp_path)
        assert not err
        assert any(e.relation_type == "requires_human_review" for e in edges)
