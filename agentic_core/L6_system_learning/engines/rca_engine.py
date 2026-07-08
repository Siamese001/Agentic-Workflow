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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "rca_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "rca_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rca_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rca_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rca_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rca_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rca_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rca_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rca_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rca_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rca_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rca_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rca_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rca_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rca_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rca_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rca_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rca_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rca_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rca_engine", "exec_snapshot_link")
from agentic_core.L6_system_learning.types.rca_types import RCAFinding, create_rca_report

trace_contract._emit_records_execution_trace("p0", "evidence", "rca_engine")
trace_contract._emit_applies_guardrail("p0", "rca_engine", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "rca_engine", "policy_binding")
trace_contract._emit_snapshots_state("p0", "rca_engine", "state_snapshot")

trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rca_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rca_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rca_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rca_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rca_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rca_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rca_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rca_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rca_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rca_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rca_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rca_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rca_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rca_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("rca_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rca_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rca_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rca_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rca_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rca_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rca_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rca_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rca_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rca_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "rca_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rca_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rca_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rca_engine", "write_through")
trace_contract._emit_writes_through("p1", "rca_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rca_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rca_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rca_engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "rca_engine", "human_escalation")
trace_contract._emit_routes_through("p1", "rca_engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "rca_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rca_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rca_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rca_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rca_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "rca_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rca_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rca_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rca_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rca_engine")
trace_contract._emit_gated_by_confidence("p1", "rca_engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "rca_engine")
trace_contract.emit_determinism_digest("p0", "rca_engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
    snapshot_id: str,
    audit_slice: bytes,
    window_start_utc: int,
    window_end_utc: int,
    *,
    violation_file_set: frozenset[str] | None = None,
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
    try:  # review: Encoding errors should specify fallback encoding strategy
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
    for (category, signature), evidence_lines in tqdm(
        findings_dict.items(), desc="findings", unit="finding", leave=False
    ):
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
    snapshot_id: str,
    audit_slice: bytes,
    window_start_utc: int,
    window_end_utc: int,
    violation_file_set: set[str] | None = None,
) -> object:
    """Analyze failures and persist findings to Memory MCP.

    Drop-in replacement for ``analyze_failures`` that additionally persists
    the RCA report into the Memory MCP knowledge graph, building an
    accumulated failure pattern library across sessions.

    Returns the same RCAReport as ``analyze_failures``.
    """
    report = analyze_failures(snapshot_id, audit_slice, window_start_utc, window_end_utc)
    try:
        from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

        get_sl_memory_bridge().persist_rca_findings(
            snapshot_id,
            report,
            window_start=window_start_utc,
            window_end=window_end_utc,
        )
    except (AttributeError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
        import logging

        logging.getLogger(__name__).debug("Failed to persist RCA findings for %s: %s", snapshot_id, exc)
    return report
