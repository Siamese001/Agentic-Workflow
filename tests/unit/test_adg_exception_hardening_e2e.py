"""E2E tests for hardened exception anti-pattern detection.

Validates that the scanner correctly identifies Col4→Col3 leakage:
  - broad_exception_catch: except Exception/BaseException without re-raise
  - log_and_swallow: broad catch with only logging, no re-raise
  - return_none_swallow: broad catch returning None/empty sentinel

Also validates edge cases and ensures no false positives on legitimate patterns.
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import _AntipatternVisitor
from agentic_core.adg.schema_util import (
    BROAD_EXCEPTION_TYPES,
    LOGGING_METHOD_NAMES,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    emit_determinism_digest,
    emit_replay_key,
)

# --- P0-P4 bootstrap (required for ADG coverage) ---
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_1")
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_2")
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_3")
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_4")
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_5")
_emit_emits_metric_event("test_exception_hardening_e2e", "p4obs", "metric_6")
_emit_records_incident_event("test_exception_hardening_e2e", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_exception_hardening_e2e", "p4obs", "anomaly")
_emit_writes_observability_log("test_exception_hardening_e2e", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_exception_hardening_e2e", "p4obs", "mon_state")
_emit_triggers_alert("test_exception_hardening_e2e", "p4obs", "alert")
_emit_links_incident_trace("test_exception_hardening_e2e", "p4obs", "trace_link")
_emit_captures_pattern("test_exception_hardening_e2e", "p3lm", "pattern")
_emit_records_learning_event("test_exception_hardening_e2e", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_exception_hardening_e2e", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_exception_hardening_e2e", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_exception_hardening_e2e", "p3lm", "routing")
_emit_improves_agent_policy("test_exception_hardening_e2e", "p3lm", "policy")
_emit_stores_learning_state("test_exception_hardening_e2e", "p3lm", "state")
_emit_records_execution_trace("test_exception_hardening_e2e", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_exception_hardening_e2e", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_exception_hardening_e2e", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_exception_hardening_e2e", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_exception_hardening_e2e", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_exception_hardening_e2e", "env_read", "p2_env_1")
_emit_reads_environ("test_exception_hardening_e2e", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_exception_hardening_e2e", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_exception_hardening_e2e", "runtime_state", "p2_rt_2")
_emit_records_execution_trace("p0", "evidence", "test_exception_hardening_e2e")
_emit_applies_guardrail("p0", "test_exception_hardening_e2e", "p0_governance")
_emit_reads_policy_state("p0", "test_exception_hardening_e2e", "policy_binding")
_emit_snapshots_state("p0", "test_exception_hardening_e2e", "state_snapshot")
emit_replay_key("p0", "test_exception_hardening_e2e")
emit_determinism_digest("p0", "test_exception_hardening_e2e")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_exception_hardening_e2e", "execution_auth")
_emit_validates_capability("p2", "test_exception_hardening_e2e", "capability_check")
_emit_routes_to_capability("p2", "test_exception_hardening_e2e", "capability_route")
_emit_writes_via_uwg("p2", "test_exception_hardening_e2e", "uwg_write")
_emit_blocks_direct_write("p2", "test_exception_hardening_e2e", "direct_write_block")
_emit_records_tool_invocation("p2", "test_exception_hardening_e2e", "tool_invocation")
_emit_captures_execution_output("p2", "test_exception_hardening_e2e", "exec_output")
_emit_dispatches_agent("p3", "test_exception_hardening_e2e", "agent_dispatch")
_emit_coordinates_agents("p3", "test_exception_hardening_e2e", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_exception_hardening_e2e", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_exception_hardening_e2e", "healing_outcome")
_emit_escalates_failure("p3", "test_exception_hardening_e2e", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_exception_hardening_e2e", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_exception_hardening_e2e", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_exception_hardening_e2e", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_exception_hardening_e2e", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_exception_hardening_e2e", "eval_metric")
_emit_stores_embedding("p4", "test_exception_hardening_e2e", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_exception_hardening_e2e", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_exception_hardening_e2e", "exec_snapshot_link")
_emit_escalates_to_human("p1", "test_exception_hardening_e2e", "human_escalation")
_emit_routes_through("p1", "test_exception_hardening_e2e", "route_through")
_emit_checks_agent_registry("p1", "test_exception_hardening_e2e", "agent_registry")
_emit_validates_agent_capability("p1", "test_exception_hardening_e2e", "capability")
_emit_dispatches_execution_plan("p1", "test_exception_hardening_e2e", "exec_plan")
_emit_agent_executes_agent("p1", "test_exception_hardening_e2e", "sub_agent")
_emit_routes_to_agent("p1", "test_exception_hardening_e2e", "target_agent")
_emit_verifies_policy("p1", "test_exception_hardening_e2e", "policy_check")
_emit_observes_runtime_state("p1", "test_exception_hardening_e2e", "runtime_state")
_emit_verifies_boundary("p1", "test_exception_hardening_e2e", "boundary_check")
_emit_transcripts_response("p1", "test_exception_hardening_e2e", "transcript")
_emit_hard_fails_untranscripted("p1", "test_exception_hardening_e2e")
_emit_gated_by_confidence("p1", "test_exception_hardening_e2e", "confidence_gate")


def _scan(code: str) -> list:
    tree = ast.parse(code)
    visitor = _AntipatternVisitor("ADG::Module::test.py", "test.py")
    visitor.visit(tree)
    return visitor.edges


def _edges_by_kind(edges, kind: str) -> list:
    return [e for e in edges if e.edge_kind == kind]


# ===========================================================================
# Schema integrity tests
# ===========================================================================


class TestSchemaIntegrity:
    def test_broad_exception_types_contains_expected(self):
        assert "Exception" in BROAD_EXCEPTION_TYPES
        assert "BaseException" in BROAD_EXCEPTION_TYPES

    def test_logging_method_names_contains_expected(self):
        for name in ("debug", "info", "warning", "error", "critical", "exception", "print"):
            assert name in LOGGING_METHOD_NAMES

    def test_new_edge_kinds_in_antipattern_category_names(self):
        from agentic_core.adg.schema_util import ANTIPATTERN_CATEGORY_NAMES

        assert "broad_exception_catch" in ANTIPATTERN_CATEGORY_NAMES
        assert "log_and_swallow" in ANTIPATTERN_CATEGORY_NAMES
        assert "return_none_swallow" in ANTIPATTERN_CATEGORY_NAMES


# ===========================================================================
# Pattern 1b: broad_exception_catch
# ===========================================================================


class TestBroadExceptionCatch:
    def test_except_exception_log_no_raise_detected(self):
        code = """
def fetch():
    try:
        return do_request()
    except Exception as e:
        logger.error("Request failed: %s", e)
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        assert "Exception" in broad[0].symbol

    def test_except_base_exception_detected(self):
        code = """
def run():
    try:
        execute()
    except BaseException as e:
        print(f"Error: {e}")
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        assert "BaseException" in broad[0].symbol

    def test_bare_except_no_raise_detected_as_broad(self):
        code = """
def run():
    try:
        execute()
    except:
        print("something failed")
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        assert "bare" in broad[0].symbol

    def test_except_exception_with_raise_not_flagged(self):
        code = """
def fetch():
    try:
        return do_request()
    except Exception as e:
        logger.error("Failed: %s", e)
        raise
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0

    def test_except_exception_with_raise_new_exception_not_flagged(self):
        code = """
def fetch():
    try:
        return do_request()
    except Exception as e:
        raise RuntimeError("Wrapped") from e
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0

    def test_except_exception_with_conditional_raise_not_flagged(self):
        code = """
def fetch():
    try:
        return do_request()
    except Exception as e:
        if is_fatal(e):
            raise
        logger.warning("Non-fatal: %s", e)
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0

    def test_narrow_exception_not_flagged_as_broad(self):
        code = """
def read_config():
    try:
        return load()
    except FileNotFoundError:
        return default_config()
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0

    def test_narrow_valueerror_not_flagged(self):
        code = """
def parse(data):
    try:
        return int(data)
    except ValueError:
        logger.warning("Invalid data: %s", data)
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0

    def test_multiple_broad_catches_in_same_file(self):
        code = """
def a():
    try:
        x()
    except Exception:
        logger.error("a failed")

def b():
    try:
        y()
    except Exception:
        print("b failed")
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 2

    def test_line_number_recorded(self):
        code = """
def a():
    try:
        x()
    except Exception:
        logger.error("failed")
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        assert broad[0].line_no == 5


# ===========================================================================
# Pattern 1c: log_and_swallow
# ===========================================================================


class TestLogAndSwallow:
    def test_single_log_call_detected(self):
        code = """
def run():
    try:
        execute()
    except Exception as e:
        logger.error("Failed: %s", e)
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1

    def test_multiple_log_calls_detected(self):
        code = """
def run():
    try:
        execute()
    except Exception as e:
        logger.warning("Retrying...")
        logger.error("Failed: %s", e)
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1

    def test_print_only_detected(self):
        code = """
def run():
    try:
        execute()
    except Exception:
        print("error happened")
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1

    def test_log_plus_assignment_not_flagged_as_log_only(self):
        code = """
def run():
    try:
        execute()
    except Exception as e:
        logger.error("Failed: %s", e)
        self.last_error = e
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0
        # Still a broad_exception_catch though
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1

    def test_log_plus_raise_not_flagged(self):
        code = """
def run():
    try:
        execute()
    except Exception as e:
        logger.error("Failed: %s", e)
        raise
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0

    def test_narrow_exception_log_only_not_flagged(self):
        code = """
def parse():
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.warning("Bad JSON: %s", e)
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0

    def test_bare_except_log_only_detected(self):
        code = """
def run():
    try:
        do_thing()
    except:
        logger.debug("ignored")
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1

    def test_logger_exception_method_detected(self):
        code = """
def run():
    try:
        execute()
    except Exception:
        logger.exception("Unhandled")
"""
        edges = _scan(code)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1


# ===========================================================================
# Pattern 1d: return_none_swallow
# ===========================================================================


class TestReturnNoneSwallow:
    def test_return_none_detected(self):
        code = """
def get_value():
    try:
        return fetch()
    except Exception:
        return None
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_None" in rns[0].symbol

    def test_return_empty_string_detected(self):
        code = """
def get_name():
    try:
        return lookup()
    except Exception:
        return ""
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_empty_str" in rns[0].symbol

    def test_return_empty_list_detected(self):
        code = """
def get_items():
    try:
        return query()
    except Exception:
        return []
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_empty_list" in rns[0].symbol

    def test_return_empty_dict_detected(self):
        code = """
def get_config():
    try:
        return load_config()
    except Exception:
        return {}
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_empty_dict" in rns[0].symbol

    def test_return_false_detected(self):
        code = """
def is_valid():
    try:
        return validate()
    except Exception:
        return False
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_False" in rns[0].symbol

    def test_return_zero_detected(self):
        code = """
def count():
    try:
        return compute_count()
    except Exception:
        return 0
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        assert "return_zero" in rns[0].symbol

    def test_return_bare_detected(self):
        """bare return (no value) in a broad except handler."""
        code = """
def fetch():
    try:
        do_thing()
    except Exception:
        return
"""
        edges = _scan(code)
        # This is a silent_exception_swallow (bare return), not return_none_swallow
        swallows = _edges_by_kind(edges, "silent_exception_swallow")
        assert len(swallows) == 1

    def test_return_meaningful_value_not_flagged(self):
        code = """
def get_fallback():
    try:
        return primary()
    except Exception:
        return fallback_value()
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 0
        # Still broad_exception_catch though
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1

    def test_narrow_exception_return_none_not_flagged(self):
        code = """
def parse(data):
    try:
        return int(data)
    except ValueError:
        return None
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 0

    def test_log_then_return_none_detected_as_both(self):
        code = """
def get_value():
    try:
        return fetch()
    except Exception as e:
        logger.error("Failed: %s", e)
        return None
"""
        edges = _scan(code)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1
        # NOT log_and_swallow because body has return too
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0
        # Still broad_exception_catch
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1


# ===========================================================================
# Edge case: interaction between patterns
# ===========================================================================


class TestPatternInteraction:
    def test_silent_swallow_does_not_trigger_broad_catch(self):
        """A pass-only except block is silent_exception_swallow, NOT broad_exception_catch."""
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        swallows = _edges_by_kind(edges, "silent_exception_swallow")
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(swallows) == 1
        assert len(broad) == 0

    def test_narrow_silent_swallow_still_detected(self):
        code = """
try:
    risky()
except ValueError:
    pass
"""
        edges = _scan(code)
        swallows = _edges_by_kind(edges, "silent_exception_swallow")
        assert len(swallows) == 1

    def test_broad_catch_with_complex_body_detected(self):
        code = """
def handler():
    try:
        process()
    except Exception as e:
        metrics.increment("error_count")
        self.errors.append(str(e))
        self.state = "degraded"
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        # Not log_and_swallow (body has assignments)
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0
        # Not return_none_swallow (no return)
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 0

    def test_nested_try_except_both_detected(self):
        code = """
def outer():
    try:
        inner()
    except Exception:
        logger.error("outer failed")

def inner():
    try:
        compute()
    except Exception:
        return None
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 2
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1

    def test_except_tuple_not_flagged_as_broad(self):
        """except (KeyError, ValueError) is narrow, not broad."""
        code = """
def parse():
    try:
        return process()
    except (KeyError, ValueError):
        return None
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 0

    def test_clean_code_no_new_antipatterns(self):
        """Code with proper exception handling emits zero antipattern edges."""
        code = """
def safe_fetch(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.warning("Timeout fetching %s", url)
        raise
    except requests.HTTPError as e:
        logger.error("HTTP error %s: %s", url, e)
        raise FetchError(f"HTTP {e.response.status_code}") from e
    except Exception as e:
        logger.critical("Unexpected error: %s", e)
        raise
"""
        edges = _scan(code)
        antipatterns = [e for e in edges if e.relation_type == "antipattern"]
        assert len(antipatterns) == 0

    def test_empty_except_body_is_silent_swallow(self):
        """Edge case: handler with empty body (shouldn't parse, but defensive)."""
        code = """
try:
    risky()
except Exception:
    pass
"""
        edges = _scan(code)
        swallows = _edges_by_kind(edges, "silent_exception_swallow")
        assert len(swallows) == 1


# ===========================================================================
# E2E: Real-world patterns from codebase
# ===========================================================================


class TestRealWorldPatterns:
    def test_cache_fallback_pattern(self):
        """Common cache pattern: broad catch, return empty — should be detected."""
        code = """
class CacheManager:
    def get(self, key):
        try:
            return self._store[key]
        except Exception:
            return None
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1

    def test_agent_dispatch_swallow(self):
        """Agent dispatch pattern that silently swallows errors."""
        code = """
class AgentOrchestrator:
    def dispatch(self, agent_name, payload):
        try:
            agent = self.registry.get(agent_name)
            return agent.execute(payload)
        except Exception as e:
            logger.warning("Agent %s failed: %s", agent_name, e)
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 1

    def test_config_loader_defensive(self):
        """Config loader that catches too broadly."""
        code = """
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1

    def test_proper_config_loader_not_flagged(self):
        """Config loader with proper narrow exceptions."""
        code = """
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON: {e}") from e
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 0

    def test_healing_loop_with_broad_catch(self):
        """Healing loop that catches too broadly, masking real failures."""
        code = """
class HealingOrchestrator:
    def heal(self, target):
        try:
            result = self.healer.run(target)
            return result
        except Exception as e:
            logger.error("Healing failed for %s: %s", target, e)
            return False
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 1
        rns = _edges_by_kind(edges, "return_none_swallow")
        assert len(rns) == 1

    def test_resilient_handler_with_reraise_clean(self):
        """Proper resilient pattern: catch broad, log, re-raise."""
        code = """
class ResilientHandler:
    def process(self, task):
        try:
            return self._execute(task)
        except Exception as e:
            logger.error("Task %s failed: %s", task.id, e)
            self.metrics.increment("failures")
            raise TaskError(f"Processing failed: {e}") from e
"""
        edges = _scan(code)
        broad = _edges_by_kind(edges, "broad_exception_catch")
        assert len(broad) == 0
        las = _edges_by_kind(edges, "log_and_swallow")
        assert len(las) == 0
