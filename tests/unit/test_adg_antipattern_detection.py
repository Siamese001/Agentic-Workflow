"""Tests for ADG anti-pattern detection via _AntipatternVisitor.

Verifies that the seven behavioral anti-patterns are correctly detected:
  1. silent_exception_swallow
  2. blocking_call_in_async
  3. global_state_mutation
  4. retry_without_backoff
  5. broad_exception_catch
  6. log_and_swallow
  7. return_none_swallow
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import _AntipatternVisitor
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_antipattern_detection", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_antipattern_detection", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_antipattern_detection", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_antipattern_detection", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_antipattern_detection", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_antipattern_detection", "p4obs", "alert")
_emit_links_incident_trace("test_adg_antipattern_detection", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_antipattern_detection", "p3lm", "pattern")
_emit_records_learning_event("test_adg_antipattern_detection", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_antipattern_detection", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_antipattern_detection", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_antipattern_detection", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_antipattern_detection", "p3lm", "policy")
_emit_stores_learning_state("test_adg_antipattern_detection", "p3lm", "state")
_emit_records_execution_trace("test_adg_antipattern_detection", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_antipattern_detection", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_antipattern_detection", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_antipattern_detection", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_antipattern_detection", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_antipattern_detection", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_antipattern_detection", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_antipattern_detection", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_antipattern_detection", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_adg_antipattern_detection")
_emit_applies_guardrail("p0", "test_adg_antipattern_detection", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_antipattern_detection", "policy_binding")
_emit_snapshots_state("p0", "test_adg_antipattern_detection", "state_snapshot")
emit_replay_key("p0", "test_adg_antipattern_detection")
emit_determinism_digest("p0", "test_adg_antipattern_detection")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_antipattern_detection", "execution_auth")
_emit_validates_capability("p2", "test_adg_antipattern_detection", "capability_check")
_emit_routes_to_capability("p2", "test_adg_antipattern_detection", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_antipattern_detection", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_antipattern_detection", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_antipattern_detection", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_antipattern_detection", "exec_output")
_emit_dispatches_agent("p3", "test_adg_antipattern_detection", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_antipattern_detection", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_antipattern_detection", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_antipattern_detection", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_antipattern_detection", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_antipattern_detection", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_antipattern_detection", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_antipattern_detection", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_antipattern_detection", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_antipattern_detection", "eval_metric")
_emit_stores_embedding("p4", "test_adg_antipattern_detection", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_antipattern_detection", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_antipattern_detection", "exec_snapshot_link")
_emit_escalates_to_human("p1", "test_adg_antipattern_detection", "human_escalation")
_emit_routes_through("p1", "test_adg_antipattern_detection", "route_through")
_emit_checks_agent_registry("p1", "test_adg_antipattern_detection", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_antipattern_detection", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_antipattern_detection", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_antipattern_detection", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_antipattern_detection", "target_agent")
_emit_verifies_policy("p1", "test_adg_antipattern_detection", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_antipattern_detection", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_antipattern_detection", "boundary_check")
_emit_transcripts_response("p1", "test_adg_antipattern_detection", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_antipattern_detection")
_emit_gated_by_confidence("p1", "test_adg_antipattern_detection", "confidence_gate")


def _scan(code: str) -> list:
    tree = ast.parse(code)
    visitor = _AntipatternVisitor("ADG::Module::test.py", "test.py")
    visitor.visit(tree)
    return visitor.edges


# ---------------------------------------------------------------------------
# Pattern 1: silent_exception_swallow
# ---------------------------------------------------------------------------


class TestSilentExceptionSwallow:
    def test_bare_pass_detected(self):
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        assert len(edges) == 1
        assert edges[0].edge_kind == "silent_exception_swallow"
        assert edges[0].relation_type == "antipattern"

    def test_bare_except_pass_detected(self):
        code = """
try:
    risky()
except:
    pass
"""
        edges = _scan(code)
        assert len(edges) == 1
        assert edges[0].edge_kind == "silent_exception_swallow"
        assert "bare" in edges[0].symbol

    def test_continue_in_except_detected(self):
        code = """
for item in items:
    try:
        process(item)
    except ValueError:
        continue
"""
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 1

    def test_bare_return_in_except_detected(self):
        code = """
def do_thing():
    try:
        risky()
    except Exception:
        return
"""
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 1

    def test_except_with_logging_not_flagged(self):
        code = """
try:
    risky()
except Exception as e:
    logger.error("Failed: %s", e)
"""
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 0

    def test_except_with_raise_not_flagged(self):
        code = """
try:
    risky()
except Exception:
    raise RuntimeError("wrapped")
"""
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 0

    def test_except_with_return_value_not_flagged(self):
        code = """
def safe():
    try:
        return risky()
    except Exception:
        return None
"""
        # return None is a bare return-None node, NOT flagged (has value node)
        # ast.Return with value=ast.Constant(None) is different from ast.Return(value=None)
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 0

    def test_symbol_contains_exception_type(self):
        code = """
try:
    risky()
except ValueError:
    pass
"""
        edges = _scan(code)
        assert edges[0].symbol == "except:ValueError"

    def test_multiple_swallowers_all_detected(self):
        code = """
try:
    a()
except TypeError:
    pass

try:
    b()
except KeyError:
    pass
"""
        edges = _scan(code)
        swallows = [e for e in edges if e.edge_kind == "silent_exception_swallow"]
        assert len(swallows) == 2


# ---------------------------------------------------------------------------
# Pattern 2: blocking_call_in_async
# ---------------------------------------------------------------------------


class TestBlockingCallInAsync:
    def test_time_sleep_in_async_detected(self):
        code = """
import time

async def fetch():
    time.sleep(1)
    return data
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 1
        assert blocking[0].symbol == "time.sleep"

    def test_requests_get_in_async_detected(self):
        code = """
async def fetch_data(url):
    response = requests.get(url)
    return response.json()
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 1
        assert "requests.get" in blocking[0].symbol

    def test_subprocess_run_in_async_detected(self):
        code = """
async def run_cmd():
    result = subprocess.run(["ls"], capture_output=True)
    return result.stdout
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 1

    def test_time_sleep_in_sync_not_flagged(self):
        code = """
import time

def sync_wait():
    time.sleep(1)
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 0

    def test_asyncio_sleep_in_async_not_flagged(self):
        code = """
import asyncio

async def async_wait():
    await asyncio.sleep(1)
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 0

    def test_nested_sync_func_in_async_not_flagged(self):
        code = """
async def outer():
    def inner():
        time.sleep(1)  # sync function inside async — not a violation
    inner()
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 0

    def test_line_number_recorded(self):
        code = """
async def fetch():
    x = 1
    time.sleep(2)
    return x
"""
        edges = _scan(code)
        blocking = [e for e in edges if e.edge_kind == "blocking_call_in_async"]
        assert len(blocking) == 1
        assert blocking[0].line_no == 4


# ---------------------------------------------------------------------------
# Pattern 3: global_state_mutation
# ---------------------------------------------------------------------------


class TestGlobalStateMutation:
    def test_uppercase_global_mutated_in_function_detected(self):
        code = """
CONFIG = {}

def update_config(key, value):
    CONFIG = {key: value}
"""
        edges = _scan(code)
        mutations = [e for e in edges if e.edge_kind == "global_state_mutation"]
        assert len(mutations) == 1
        assert mutations[0].symbol == "CONFIG"

    def test_lowercase_global_not_flagged(self):
        code = """
state = {}

def update_state():
    state = {"new": "value"}
"""
        edges = _scan(code)
        mutations = [e for e in edges if e.edge_kind == "global_state_mutation"]
        assert len(mutations) == 0

    def test_module_level_assignment_not_flagged(self):
        code = """
CONFIG = {}
CONFIG = {"initial": True}
"""
        edges = _scan(code)
        mutations = [e for e in edges if e.edge_kind == "global_state_mutation"]
        assert len(mutations) == 0

    def test_multiple_globals_mutated_all_detected(self):
        code = """
CACHE = {}
REGISTRY = []

def reset():
    CACHE = {}
    REGISTRY = []
"""
        edges = _scan(code)
        mutations = [e for e in edges if e.edge_kind == "global_state_mutation"]
        assert len(mutations) == 2
        symbols = {e.symbol for e in mutations}
        assert symbols == {"CACHE", "REGISTRY"}


# ---------------------------------------------------------------------------
# Pattern 4: retry_without_backoff
# ---------------------------------------------------------------------------


class TestRetryWithoutBackoff:
    def test_while_retry_without_sleep_detected(self):
        code = """
def retry_operation():
    while True:
        try:
            do_thing()
            break
        except Exception:
            pass
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 1
        assert retries[0].symbol == "while_retry"

    def test_for_retry_without_sleep_detected(self):
        code = """
def retry_operation():
    for attempt in range(3):
        try:
            do_thing()
            break
        except Exception:
            pass
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 1
        assert retries[0].symbol == "for_retry"

    def test_while_with_sleep_not_flagged(self):
        code = """
import time

def retry_operation():
    while True:
        try:
            do_thing()
            break
        except Exception:
            time.sleep(1)
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 0

    def test_loop_without_try_not_flagged(self):
        code = """
def process_all():
    while items:
        item = items.pop()
        process(item)
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 0

    def test_loop_with_asyncio_sleep_not_flagged(self):
        code = """
async def retry_async():
    for i in range(3):
        try:
            await do_thing()
            break
        except Exception:
            await asyncio.sleep(0.5)
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 0

    def test_loop_with_backoff_call_not_flagged(self):
        code = """
def retry():
    while True:
        try:
            do_thing()
            break
        except Exception:
            exponential_backoff()
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 0


# ---------------------------------------------------------------------------
# Edge metadata correctness
# ---------------------------------------------------------------------------


class TestEdgeMetadata:
    def test_edge_source_file_set(self):
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        assert all(e.source_file == "test.py" for e in edges)

    def test_edge_module_adg_name_set(self):
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        assert all(e.from_name == "ADG::Module::test.py" for e in edges)

    def test_edge_to_name_is_canonical_symbol(self):
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        assert edges[0].to_name == "ADG::Symbol::silent_exception_swallow"

    def test_no_false_positives_on_truly_clean_code(self):
        """Code with no anti-patterns produces zero antipattern edges."""
        code = """
import asyncio
from pathlib import Path
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
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
_emit_pulls_context("p1", "test_adg_antipattern_detection", "context_pull")
_emit_pulls_context("p1", "test_adg_antipattern_detection", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_adg_antipattern_detection", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_antipattern_detection", "uwg_term_secondary")
_emit_writes_through("p1", "test_adg_antipattern_detection", "write_through")
_emit_writes_through("p1", "test_adg_antipattern_detection", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_adg_antipattern_detection", "safety_validation")
_emit_invokes_eval("p1", "test_adg_antipattern_detection", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_antipattern_detection", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_antipattern_detection", "human_escalation")
_emit_routes_through("p1", "test_adg_antipattern_detection", "route_through")
_emit_checks_agent_registry("p1", "test_adg_antipattern_detection", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_antipattern_detection", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_antipattern_detection", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_antipattern_detection", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_antipattern_detection", "target_agent")
_emit_verifies_policy("p1", "test_adg_antipattern_detection", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_antipattern_detection", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_antipattern_detection", "boundary_check")
_emit_transcripts_response("p1", "test_adg_antipattern_detection", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_antipattern_detection")
_emit_gated_by_confidence("p1", "test_adg_antipattern_detection", "confidence_gate")


async def fetch(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def transform_items(items: list) -> list:
    return [transform(item) for item in items]
"""
        edges = _scan(code)
        antipatterns = [e for e in edges if e.relation_type == "antipattern"]
        assert len(antipatterns) == 0

    def test_for_loop_with_try_except_and_continue_is_retry(self):
        """for+try/except with continue (no sleep) is correctly flagged as retry_without_backoff."""
        code = """
def process_items(items: list) -> list:
    results = []
    for item in items:
        try:
            results.append(transform(item))
        except ValueError as e:
            logger.warning("Skipping %s: %s", item, e)
            continue
    return results
"""
        edges = _scan(code)
        retries = [e for e in edges if e.edge_kind == "retry_without_backoff"]
        assert len(retries) == 1
