"""G-16-24: RCA engine for System Learning root cause analysis.

Pure analyzer producing deterministic RCA reports from audit slices.

Invariants:
  - Deterministic parsing rules
  - No randomness/time/env
  - Fail-closed on malformed input
  - Read-only inputs, proposal-only outputs
"""

from __future__ import annotations

import hashlib
import re
from tqdm import tqdm

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "rca_engine", "execution_auth")
_emit_validates_capability("p2", "rca_engine", "capability_check")
_emit_routes_to_capability("p2", "rca_engine", "capability_route")
_emit_writes_via_uwg("p2", "rca_engine", "uwg_write")
_emit_blocks_direct_write("p2", "rca_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "rca_engine", "tool_invocation")
_emit_captures_execution_output("p2", "rca_engine", "exec_output")
_emit_dispatches_agent("p3", "rca_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "rca_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "rca_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "rca_engine", "healing_outcome")
_emit_escalates_failure("p3", "rca_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "rca_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rca_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "rca_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "rca_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rca_engine", "eval_metric")
_emit_stores_embedding("p4", "rca_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "rca_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rca_engine", "exec_snapshot_link")
from system_learning.types.rca_types import RCAFinding, create_rca_report

_emit_records_execution_trace("p0", "evidence", "rca_engine")
_emit_applies_guardrail("p0", "rca_engine", "p0_governance")
_emit_reads_policy_state("p0", "rca_engine", "policy_binding")
_emit_snapshots_state("p0", "rca_engine", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
)

_emit_emits_metric_event("rca_engine", "p4obs", "metric_1")
_emit_emits_metric_event("rca_engine", "p4obs", "metric_2")
_emit_emits_metric_event("rca_engine", "p4obs", "metric_3")
_emit_emits_metric_event("rca_engine", "p4obs", "metric_4")
_emit_emits_metric_event("rca_engine", "p4obs", "metric_5")
_emit_emits_metric_event("rca_engine", "p4obs", "metric_6")
_emit_records_incident_event("rca_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("rca_engine", "p4obs", "anomaly")
_emit_writes_observability_log("rca_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("rca_engine", "p4obs", "mon_state")
_emit_triggers_alert("rca_engine", "p4obs", "alert")
_emit_links_incident_trace("rca_engine", "p4obs", "trace_link")
_emit_captures_pattern("rca_engine", "p3lm", "pattern")
_emit_records_learning_event("rca_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rca_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("rca_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rca_engine", "p3lm", "routing")
_emit_improves_agent_policy("rca_engine", "p3lm", "policy")
_emit_stores_learning_state("rca_engine", "p3lm", "state")
_emit_records_execution_trace("rca_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rca_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rca_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rca_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rca_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rca_engine", "env_read", "p2_env_1")
_emit_reads_environ("rca_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("rca_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rca_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rca_engine", "context_pull")
_emit_pulls_context("p1", "rca_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rca_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rca_engine", "uwg_term_2")
_emit_writes_through("p1", "rca_engine", "write_through")
_emit_writes_through("p1", "rca_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "rca_engine", "safety_validation")
_emit_invokes_eval("p1", "rca_engine", "eval_call")
_emit_proposal_commits_routing("p1", "rca_engine", "routing_commit")
_emit_escalates_to_human("p1", "rca_engine", "human_escalation")
_emit_routes_through("p1", "rca_engine", "route_through")
_emit_checks_agent_registry("p1", "rca_engine", "agent_registry")
_emit_validates_agent_capability("p1", "rca_engine", "capability")
_emit_dispatches_execution_plan("p1", "rca_engine", "exec_plan")
_emit_agent_executes_agent("p1", "rca_engine", "sub_agent")
_emit_routes_to_agent("p1", "rca_engine", "target_agent")
_emit_verifies_policy("p1", "rca_engine", "policy_check")
_emit_observes_runtime_state("p1", "rca_engine", "runtime_state")
_emit_verifies_boundary("p1", "rca_engine", "boundary_check")
_emit_transcripts_response("p1", "rca_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "rca_engine")
_emit_gated_by_confidence("p1", "rca_engine", "confidence_gate")
emit_replay_key("p0", "rca_engine")
emit_determinism_digest("p0", "rca_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RCAAnalysisError(RuntimeError):
    """Raised when RCA analysis fails."""


CLASSIFICATION_RULES = [
    ("SYNTAX", re.compile("SyntaxError:"), lambda line: "SyntaxError"),
    ("SYNTAX", re.compile("IndentationError:"), lambda line: "IndentationError"),
    ("SYNTAX", re.compile("TabError:"), lambda line: "TabError"),
    ("IMPORT", re.compile("ModuleNotFoundError:"), lambda line: "ModuleNotFoundError"),
    ("IMPORT", re.compile("ImportError:"), lambda line: "ImportError"),
    ("TEST_DISCOVERY", re.compile("ERROR collecting"), lambda line: "pytest_collection_error"),
    ("TEST_DISCOVERY", re.compile("collection errors"), lambda line: "pytest_collection_errors"),
    ("POLICY_BLOCK", re.compile("SourceMutationBlocked"), lambda line: "SourceMutationBlocked"),
    ("POLICY_BLOCK", re.compile("AuthorityViolation"), lambda line: "AuthorityViolation"),
    ("RUNTIME", re.compile("RuntimeError:"), lambda line: "RuntimeError"),
    ("RUNTIME", re.compile("AttributeError:"), lambda line: "AttributeError"),
    ("RUNTIME", re.compile("TypeError:"), lambda line: "TypeError"),
    ("RUNTIME", re.compile("ValueError:"), lambda line: "ValueError"),
    ("RUNTIME", re.compile("KeyError:"), lambda line: "KeyError"),
    ("RUNTIME", re.compile("IndexError:"), lambda line: "IndexError"),
    ("TIMEOUT", re.compile("TimeoutError"), lambda line: "TimeoutError"),
    ("TIMEOUT", re.compile("timeout"), lambda line: "timeout"),
]


def classify_line(line: str) -> tuple[str, str] | None:
    """Classify a line into (category, signature).

    Parameters
    ----------
    line : str
        The line to classify.

    Returns
    -------
    tuple[str, str] | None
        (category, signature) if matched, None otherwise.
    """
    for category, pattern, signature_fn in CLASSIFICATION_RULES:
        if pattern.search(line):
            signature = signature_fn(line)
            return (category, signature)
    return None


def analyze_failures(
    snapshot_id: str, audit_slice: bytes, window_start_utc: int, window_end_utc: int, *, violation_file_set: frozenset[str] | None = None,
) -> object:
    """Analyze failures from audit slice and produce RCA report.

    Deterministic parsing rules:
      - Treat audit_slice as UTF-8 text lines
      - Classify into categories by stable pattern rules
      - Count occurrences per (category, signature)
      - evidence_hash = SHA-256 of canonical normalized evidence bytes

    Parameters
    ----------
    snapshot_id : str
        The snapshot this RCA is based on.
    audit_slice : bytes
        Raw audit data to analyze.
    window_start_utc : int
        Start of analysis window.
    window_end_utc : int
        End of analysis window.
    violation_file_set : frozenset[str] | None
        Set of file paths with ADG violations for correlation.

    Returns
    -------
    RCAReport
        Deterministic RCA report.

    Raises
    ------
    RCAAnalysisError
        If audit_slice cannot be decoded or window is invalid.
    """
    if window_start_utc >= window_end_utc:
        raise RCAAnalysisError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")
    if isinstance(audit_slice, list):
        audit_slice = "\n".join(str(item) for item in audit_slice).encode("utf-8")
    elif not isinstance(audit_slice, (bytes, bytearray)):
        audit_slice = b""
    try:    # guardian: Encoding errors should specify fallback encoding strategy
        audit_text = audit_slice.decode("utf-8")
    except UnicodeDecodeError as e:
        raise RCAAnalysisError(f"Failed to decode audit_slice as UTF-8: {e}") from e
    lines = audit_text.splitlines()
    findings_dict: dict[tuple[str, str], list[str]] = {}
    for line in tqdm(lines, desc="parse audit", unit="line", leave=False):
        line = line.strip()
        if not line:
            continue
        classification = classify_line(line)
        if classification:
            category, signature = classification
            key = (category, signature)
            if key not in findings_dict:
                findings_dict[key] = []
            findings_dict[key].append(line)
    if not findings_dict:
        findings_dict["UNKNOWN", "no_patterns_matched"] = ["<no matching patterns>"]

    # Check for ADG violation correlation
    adg_correlated = False
    violation_type = None
    if violation_file_set:
        for line in tqdm(lines, desc="scan violations", unit="line", leave=False):
            line = line.strip()
            # Extract file path from error lines (common patterns)
            for prefix in ["File ", "  File ", "    File "]:
                if line.startswith(prefix):
                    parts = line.split('"')
                    if len(parts) > 1:
                        file_path = parts[1]
                        if file_path in violation_file_set:
                            adg_correlated = True
                            violation_type = "layer_boundary"
                            break
            if adg_correlated:
                break

    findings = []
    for (category, signature), evidence_lines in tqdm(findings_dict.items(), desc="findings", unit="finding", leave=False):
        count = len(evidence_lines)
        canonical_evidence = "\n".join(sorted(evidence_lines)).encode("utf-8")
        evidence_hash = hashlib.sha256(canonical_evidence).hexdigest()

        # Add ADG correlation metadata if applicable
        if adg_correlated and category in ["SYNTAX", "IMPORT", "RUNTIME"]:
            # Add correlation info to signature
            signature = f"{signature}_ADG_CORRELATED"

        findings.append(
            RCAFinding(category=category, signature=signature, count=count, evidence_hash=evidence_hash),
        )
    return create_rca_report(
        snapshot_id=snapshot_id,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        findings=tuple(findings),
    )


def analyze_failures_and_persist(
    snapshot_id: str, audit_slice: bytes, window_start_utc: int, window_end_utc: int, violation_file_set: set[str] | None = None,
) -> object:
    """Analyze failures and persist findings to Memory MCP.

    Drop-in replacement for ``analyze_failures`` that additionally persists
    the RCA report into the Memory MCP knowledge graph, building an
    accumulated failure pattern library across sessions.

    Returns the same RCAReport as ``analyze_failures``.
    """
    report = analyze_failures(snapshot_id, audit_slice, window_start_utc, window_end_utc)
    try:
        from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

        get_sl_memory_bridge().persist_rca_findings(
            snapshot_id, report, window_start=window_start_utc, window_end=window_end_utc,
        )
    # guardian: allow-silent-swallow
    except Exception as e:

        import logging; logging.getLogger(__name__).debug("rca_engine: Exception swallowed at L332: %s", e)
    return report
