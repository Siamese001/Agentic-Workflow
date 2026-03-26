"""Negative-first tests for Phase 2 prompt governance contracts + enforcement.

All tests are deterministic and minimal.
Tests fail if enforcement is removed.
"""

from __future__ import annotations

import ast
import copy
from pathlib import Path
from unittest.mock import patch

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_capability_contracts")
# REMOVED: _emit_applies_guardrail("p0", "test_capability_contracts", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_capability_contracts", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_capability_contracts", "state_snapshot")
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_capability_contracts", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_capability_contracts", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_capability_contracts", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_capability_contracts", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_capability_contracts", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_capability_contracts", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_capability_contracts", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_capability_contracts", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_capability_contracts", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_capability_contracts", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_capability_contracts", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_capability_contracts", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_capability_contracts", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_capability_contracts", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_capability_contracts", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_capability_contracts", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_capability_contracts", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_capability_contracts", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_capability_contracts", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_capability_contracts", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_capability_contracts", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_capability_contracts", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_capability_contracts", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_capability_contracts", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_capability_contracts", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_capability_contracts", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_capability_contracts", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_capability_contracts", "write_through")
# REMOVED: _emit_writes_through("p1", "test_capability_contracts", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_capability_contracts", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_capability_contracts", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_capability_contracts", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_capability_contracts", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_capability_contracts", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_capability_contracts", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_capability_contracts", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_capability_contracts", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_capability_contracts", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_capability_contracts", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_capability_contracts", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_capability_contracts", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_capability_contracts", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_capability_contracts", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_capability_contracts")
# REMOVED: _emit_gated_by_confidence("p1", "test_capability_contracts", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_capability_contracts")
# REMOVED: emit_determinism_digest("p0", "test_capability_contracts")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_capability_contracts", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_capability_contracts", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_capability_contracts", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_capability_contracts", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_capability_contracts", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_capability_contracts", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_capability_contracts", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_capability_contracts", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_capability_contracts", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_capability_contracts", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_capability_contracts", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_capability_contracts", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_capability_contracts", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_capability_contracts", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_capability_contracts", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_capability_contracts", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_capability_contracts", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_capability_contracts", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_capability_contracts", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_capability_contracts", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """Walk up from this file until pytest.ini is found (repo root sentinel)."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pytest.ini").exists():
            return parent
    raise RuntimeError("Could not locate repo root (pytest.ini not found)")


CONTRACTS_PATH = _repo_root() / AGENTIC_CORE_DIR / "prompt_governance" / "contracts" / "context_contracts.py"

_VALID_RETRIEVAL = {"namespace": "ns1", "max_k": 5, "version": "v1"}
_VALID_CITATION = {
    "source_doc_id": "doc1",
    "offset_start": 0,
    "offset_end": 10,
    "timestamp": "2026-01-01T00:00:00Z",
}


def _vcc(payload):
    """Import fresh each call to avoid _invariant_validated caching issues."""

    return validate_context_contract(payload)


# ---------------------------------------------------------------------------
# validate_context_contract — citations
# ---------------------------------------------------------------------------


def test_citations_missing_required_fields_returns_false_and_empty_normalized():
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR,
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
        from agentic_core.prompt_governance.security.validators.output_schema_validator import (
            validate_context_contract,
        )
        from agentic_core.prompt_governance.security.validators import output_schema_validator as osv
        codes = [
            osv.MISSING_CITATION_FIELDS,
            osv.INCOMPLETE_RETRIEVAL_METADATA,
            osv.MUTATION_VERB_IN_RETRIEVAL,
            osv.INVALID_RETRIEVAL_FIELD_CONSTRAINT,
        ]
        for code in codes:
            assert isinstance(code, str)
            assert code == code.upper()
        from agentic_core.prompt_governance.core.invariant_registry import validate_invariant_registry
        validate_invariant_registry()  # must not raise
        from agentic_core.prompt_governance.core.prompt_assembler import (
            PromptAssembler,
            SecurityIntegrityError,
        )
        from agentic_core.prompt_governance.core import prompt_assembler as pa
        from agentic_core.prompt_governance.core.prompt_assembler import (
            PromptAssembler,
            SecurityIntegrityError,
        )
        from agentic_core.prompt_governance.security.validators import output_schema_validator as osv
        assert osv.INVALID_TELEMETRY_ENVELOPE == osv.INVALID_TELEMETRY_ENVELOPE.upper()
        from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE
        assert isinstance(ITERATIVE_FEEDBACK_DIRECTIVE, str)
        assert len(ITERATIVE_FEEDBACK_DIRECTIVE) > 0
        from agentic_core.prompt_governance.core.invariant_registry import ITERATIVE_FEEDBACK_DIRECTIVE
        lower = ITERATIVE_FEEDBACK_DIRECTIVE.lower()
        assert "no mutation" in lower or "read-only" in lower or "no authority" in lower

    ok, code, normalized = _vcc({"citations": [{"source_doc_id": "x"}]})
    assert ok is False
    assert code == "MISSING_CITATION_FIELDS"
    assert normalized == {}


def test_citations_valid_passes():
    ok, code, normalized = _vcc({"citations": [_VALID_CITATION]})
    assert ok is True
    assert code is None
    assert "citations" in normalized


# ---------------------------------------------------------------------------
# validate_context_contract — retrieval_metadata
# ---------------------------------------------------------------------------


def test_retrieval_missing_version_returns_incomplete():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 3}})
    assert ok is False
    assert code == "INCOMPLETE_RETRIEVAL_METADATA"
    assert normalized == {}


def test_retrieval_missing_namespace_returns_incomplete():
    ok, code, normalized = _vcc({"retrieval_metadata": {"max_k": 3, "version": "v1"}})
    assert ok is False
    assert code == "INCOMPLETE_RETRIEVAL_METADATA"
    assert normalized == {}


def test_retrieval_max_k_zero_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 0, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_max_k_negative_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": -1, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_empty_namespace_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "", "max_k": 5, "version": "v1"}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


def test_retrieval_empty_version_returns_constraint_error():
    ok, code, normalized = _vcc({"retrieval_metadata": {"namespace": "ns", "max_k": 5, "version": ""}})
    assert ok is False
    assert code == "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
    assert normalized == {}


# ---------------------------------------------------------------------------
# validate_context_contract — forbidden verbs (scoped to retrieval_metadata)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("verb", ["write", "modify", "update", "delete"])
def test_retrieval_contains_forbidden_verb_key_fails(verb):
    rm = dict(_VALID_RETRIEVAL)
    rm[verb] = "some_value"
    ok, code, normalized = _vcc({"retrieval_metadata": rm})
    assert ok is False
    assert code == "MUTATION_VERB_IN_RETRIEVAL"
    assert normalized == {}


def test_forbidden_verb_outside_retrieval_metadata_does_not_trigger():
    """Forbidden verbs are scoped: top-level key 'write' must NOT fail when no retrieval_metadata."""
    ok, code, normalized = _vcc({"write": "something"})
    assert ok is True
    assert code is None


# ---------------------------------------------------------------------------
# validate_context_contract — normalization
# ---------------------------------------------------------------------------


def test_drops_unknown_retrieval_keys_in_normalized():
    rm = dict(_VALID_RETRIEVAL)
    rm["extra_key"] = "should_be_dropped"
    ok, code, normalized = _vcc({"retrieval_metadata": rm})
    assert ok is True
    assert code is None
    assert set(normalized["retrieval_metadata"].keys()) == {"namespace", "max_k", "version"}


def test_normalized_is_not_same_object_as_payload():
    payload = {"retrieval_metadata": dict(_VALID_RETRIEVAL)}
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert normalized is not payload


def test_does_not_mutate_input_payload():
    payload = {"retrieval_metadata": dict(_VALID_RETRIEVAL), "other": "data"}
    original = copy.deepcopy(payload)
    _vcc(payload)
    assert payload == original


# ---------------------------------------------------------------------------
# validate_context_contract — error codes are uppercase strings
# ---------------------------------------------------------------------------


def test_error_codes_are_uppercase_strings():
        assert code == code.upper()


# ---------------------------------------------------------------------------
# contracts — no pydantic import
# ---------------------------------------------------------------------------


def test_context_contracts_has_no_pydantic_import():
    source = CONTRACTS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "pydantic" not in alias.name, (
                        f"pydantic import found in context_contracts.py: {alias.name}"
                    )
            else:
                assert node.module is None or "pydantic" not in node.module, (
                    f"pydantic import found in context_contracts.py: {node.module}"
                )


# ---------------------------------------------------------------------------
# invariant registry
# ---------------------------------------------------------------------------


def test_validate_invariant_registry_succeeds():
    validate_invariant_registry()  # must not raise


def test_invariant_registry_called_on_first_use_via_validate_context_contract():
"""Test invariant_registry_called_on_first_use_via_validate_context_contract runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute invariant_registry_called_on_first_use_via_validate_context_contract
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
            return real_vas(obj, schema)

        with patch.object(osv, "validate_against_schema", side_effect=spy_vas):
            # Call validate_context_contract — should trigger validate_invariant_registry
            osv.validate_context_contract({"other": "data"})

        assert len(call_log) >= 1, "validate_against_schema was not called on first use"
    finally:
        osv._invariant_validated = original


# ---------------------------------------------------------------------------
# assembler — single enforcement path
# ---------------------------------------------------------------------------


def test_assembler_rejects_non_dict_context_data_with_invalid_context_type():

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        assembler = PromptAssembler()
    with pytest.raises(SecurityIntegrityError, match="INVALID_CONTEXT_TYPE"):
        assembler.assemble(
            role="Agent",
            objective="Test",
            context_data="not a dict",
            injections=[],
        )


def test_assembler_cannot_bypass_validator_monkeypatch():
    """Meta-test: if validate_context_contract raises, assembler must propagate it."""

    def _always_fail(payload):
        return (False, "MUTATION_VERB_IN_RETRIEVAL", {})

    with patch(
        "agentic_core.prompt_governance.core.prompt_assembler.PromptAssembler._load_templates",
        return_value=None,
    ):
        assembler = PromptAssembler()

    with patch.object(pa, "validate_context_contract", side_effect=_always_fail):
        with pytest.raises(SecurityIntegrityError, match="MUTATION_VERB_IN_RETRIEVAL"):
            assembler.assemble(
                role="Agent",
                objective="Test",
                context_data={"retrieval_metadata": _VALID_RETRIEVAL},
                injections=[],
            )


# ---------------------------------------------------------------------------
# Wave 3 — Capability wiring closure
# ---------------------------------------------------------------------------

_VALID_TELEMETRY = {"hit_rate": 0.9, "recall_estimate": 0.85, "empty_result_signal": False}


# telemetry_envelope validation
def test_telemetry_envelope_valid_passes():
    ok, code, normalized = _vcc({"telemetry_envelope": _VALID_TELEMETRY})
    assert ok is True
    assert code is None
    assert normalized["telemetry_envelope"] == _VALID_TELEMETRY


def test_telemetry_envelope_missing_hit_rate_fails():
    te = {"recall_estimate": 0.5, "empty_result_signal": True}
    ok, code, normalized = _vcc({"telemetry_envelope": te})
    assert ok is False
    assert code == "INVALID_TELEMETRY_ENVELOPE"
    assert normalized == {}


def test_telemetry_envelope_wrong_type_for_empty_result_signal_fails():
    te = {"hit_rate": 0.9, "recall_estimate": 0.5, "empty_result_signal": "yes"}
    ok, code, normalized = _vcc({"telemetry_envelope": te})
    assert ok is False
    assert code == "INVALID_TELEMETRY_ENVELOPE"
    assert normalized == {}


def test_telemetry_envelope_error_code_is_uppercase():
    assert osv.INVALID_TELEMETRY_ENVELOPE == osv.INVALID_TELEMETRY_ENVELOPE.upper()


# iterative feedback directive
def test_iterative_feedback_directive_exists_and_is_non_empty():
    assert len(ITERATIVE_FEEDBACK_DIRECTIVE) > 0


def test_iterative_feedback_directive_contains_no_mutation_authority():
    assert "no mutation" in lower or "read-only" in lower or "no authority" in lower


# structured field pass-through: all three contract sections in one payload
def test_full_structured_payload_passes_validator():
    payload = {
        "retrieval_metadata": _VALID_RETRIEVAL,
        "citations": [_VALID_CITATION],
        "telemetry_envelope": _VALID_TELEMETRY,
        "other": "data",
    }
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert code is None
    assert "retrieval_metadata" in normalized
    assert "citations" in normalized
    assert "telemetry_envelope" in normalized
    assert normalized["other"] == "data"


def test_full_structured_payload_normalized_is_copy():
    payload = {
        "retrieval_metadata": _VALID_RETRIEVAL,
        "citations": [_VALID_CITATION],
        "telemetry_envelope": _VALID_TELEMETRY,
    }
    ok, code, normalized = _vcc(payload)
    assert ok is True
    assert normalized is not payload
    assert normalized["retrieval_metadata"] is not payload["retrieval_metadata"]
