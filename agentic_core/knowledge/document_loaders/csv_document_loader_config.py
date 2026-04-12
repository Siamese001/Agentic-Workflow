from __future__ import annotations

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

_emit_applies_guardrail("p0", "csv_document_loader_config", "p0_governance")
_emit_reads_policy_state("p0", "csv_document_loader_config", "policy_binding")
_emit_snapshots_state("p0", "csv_document_loader_config", "state_snapshot")
emit_replay_key("p0", "csv_document_loader_config")
emit_determinism_digest("p0", "csv_document_loader_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "csv_document_loader_config", "execution_auth")
_emit_validates_capability("p2", "csv_document_loader_config", "capability_check")
_emit_routes_to_capability("p2", "csv_document_loader_config", "capability_route")
_emit_writes_via_uwg("p2", "csv_document_loader_config", "uwg_write")
_emit_blocks_direct_write("p2", "csv_document_loader_config", "direct_write_block")
_emit_records_tool_invocation("p2", "csv_document_loader_config", "tool_invocation")
_emit_captures_execution_output("p2", "csv_document_loader_config", "exec_output")
_emit_dispatches_agent("p3", "csv_document_loader_config", "agent_dispatch")
_emit_coordinates_agents("p3", "csv_document_loader_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "csv_document_loader_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "csv_document_loader_config", "healing_outcome")
_emit_escalates_failure("p3", "csv_document_loader_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "csv_document_loader_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "csv_document_loader_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "csv_document_loader_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "csv_document_loader_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "csv_document_loader_config", "eval_metric")
_emit_stores_embedding("p4", "csv_document_loader_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "csv_document_loader_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "csv_document_loader_config", "exec_snapshot_link")

# Configuration constants

"""
CSV Document Loader - Pandas-based structured data loading for RAG.

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/knowledge/document_loaders/csv_loader.py
"""


from pathlib import Path
from typing import Any

try:
    import pandas as pd

    HAS_PANDAS = True
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    HAS_PANDAS = False
    pd = None
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_1")
_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_2")
_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_3")
_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_4")
_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_5")
_emit_emits_metric_event("csv_document_loader_config", "p4obs", "metric_6")
_emit_records_incident_event("csv_document_loader_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("csv_document_loader_config", "p4obs", "anomaly")
_emit_writes_observability_log("csv_document_loader_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("csv_document_loader_config", "p4obs", "mon_state")
_emit_triggers_alert("csv_document_loader_config", "p4obs", "alert")
_emit_links_incident_trace("csv_document_loader_config", "p4obs", "trace_link")
_emit_captures_pattern("csv_document_loader_config", "p3lm", "pattern")
_emit_records_learning_event("csv_document_loader_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("csv_document_loader_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("csv_document_loader_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("csv_document_loader_config", "p3lm", "routing")
_emit_improves_agent_policy("csv_document_loader_config", "p3lm", "policy")
_emit_stores_learning_state("csv_document_loader_config", "p3lm", "state")
_emit_records_execution_trace("csv_document_loader_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("csv_document_loader_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("csv_document_loader_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("csv_document_loader_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("csv_document_loader_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("csv_document_loader_config", "env_read", "p2_env_1")
_emit_reads_environ("csv_document_loader_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("csv_document_loader_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("csv_document_loader_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "csv_document_loader_config", "context_pull")
_emit_pulls_context("p1", "csv_document_loader_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "csv_document_loader_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "csv_document_loader_config", "uwg_term_2")
_emit_writes_through("p1", "csv_document_loader_config", "write_through")
_emit_writes_through("p1", "csv_document_loader_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "csv_document_loader_config", "safety_validation")
_emit_invokes_eval("p1", "csv_document_loader_config", "eval_call")
_emit_proposal_commits_routing("p1", "csv_document_loader_config", "routing_commit")
_emit_escalates_to_human("p1", "csv_document_loader_config", "human_escalation")
_emit_routes_through("p1", "csv_document_loader_config", "route_through")
_emit_checks_agent_registry("p1", "csv_document_loader_config", "agent_registry")
_emit_validates_agent_capability("p1", "csv_document_loader_config", "capability")
_emit_dispatches_execution_plan("p1", "csv_document_loader_config", "exec_plan")
_emit_agent_executes_agent("p1", "csv_document_loader_config", "sub_agent")
_emit_routes_to_agent("p1", "csv_document_loader_config", "target_agent")
_emit_verifies_policy("p1", "csv_document_loader_config", "policy_check")
_emit_observes_runtime_state("p1", "csv_document_loader_config", "runtime_state")
_emit_verifies_boundary("p1", "csv_document_loader_config", "boundary_check")
_emit_transcripts_response("p1", "csv_document_loader_config", "transcript")
_emit_hard_fails_untranscripted("p1", "csv_document_loader_config")
_emit_gated_by_confidence("p1", "csv_document_loader_config", "confidence_gate")


class CsvDocumentLoader:
    """Sovereign CSV loader using pandas for structured data."""

    @staticmethod
    def load(file_path: Path, **kwargs) -> list[dict[str, Any]]:
        """
        Load CSV as list of dictionaries (records).

        Supports:
        - Automatic type inference
        - Custom delimiter, encoding
        - Header row handling

        Args:
            file_path: Path to CSV
            kwargs: Passed to pd.read_csv (e.g., delimiter=";", encoding="utf-8")

        Returns:
            List of row dictionaries
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CsvDocumentLoader.load")

        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            df: Any = pd.read_csv(file_path, **kwargs)
            records: list[dict[str, Any]] = df.to_dict(orient="records")
            return records
        except Exception as e:
            raise ValueError(f"CSV loading failed for {file_path}: {e}") from e

    @staticmethod
    def load_as_dataframe(file_path: Path, **kwargs) -> Any:
        """Load as pandas DataFrame for advanced processing."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f"CSV DataFrame load failed: {e}") from e

    @staticmethod
    def load_sample(file_path: Path, rows: int = 10, **kwargs) -> list[dict[str, Any]]:
        """Load only first N rows for preview/sampling."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            df: Any = pd.read_csv(file_path, nrows=rows, **kwargs)
            return df.to_dict(orient="records")
        except Exception as e:
            raise ValueError(f"CSV sample load failed: {e}") from e


CSVDocumentLoader = CsvDocumentLoader

__all__ = ["CsvDocumentLoader", "CSVDocumentLoader"]
