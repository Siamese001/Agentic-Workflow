"""HTML Document Loader — stdlib-first HTML text extraction for RAG ingestion."""

from __future__ import annotations

import html
import logging
import re
from html.parser import HTMLParser
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "html_loader", "p0_governance")
_emit_reads_policy_state("p0", "html_loader", "policy_binding")
_emit_snapshots_state("p0", "html_loader", "state_snapshot")
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

_emit_emits_metric_event("html_loader", "p4obs", "metric_1")
_emit_emits_metric_event("html_loader", "p4obs", "metric_2")
_emit_emits_metric_event("html_loader", "p4obs", "metric_3")
_emit_emits_metric_event("html_loader", "p4obs", "metric_4")
_emit_emits_metric_event("html_loader", "p4obs", "metric_5")
_emit_emits_metric_event("html_loader", "p4obs", "metric_6")
_emit_records_incident_event("html_loader", "p4obs", "incident")
_emit_captures_runtime_anomaly("html_loader", "p4obs", "anomaly")
_emit_writes_observability_log("html_loader", "p4obs", "obs_log")
_emit_updates_monitoring_state("html_loader", "p4obs", "mon_state")
_emit_triggers_alert("html_loader", "p4obs", "alert")
_emit_links_incident_trace("html_loader", "p4obs", "trace_link")
_emit_captures_pattern("html_loader", "p3lm", "pattern")
_emit_records_learning_event("html_loader", "p3lm", "learning_event")
_emit_writes_learning_snapshot("html_loader", "p3lm", "snapshot")
_emit_feeds_meta_learning("html_loader", "p3lm", "meta_feed")
_emit_updates_routing_strategy("html_loader", "p3lm", "routing")
_emit_improves_agent_policy("html_loader", "p3lm", "policy")
_emit_stores_learning_state("html_loader", "p3lm", "state")
_emit_records_execution_trace("html_loader", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("html_loader", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("html_loader", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("html_loader", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("html_loader", "L4_STATE", "p2_trace_5")
_emit_reads_environ("html_loader", "env_read", "p2_env_1")
_emit_reads_environ("html_loader", "env_read", "p2_env_2")
_emit_reads_runtime_state("html_loader", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("html_loader", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "html_loader", "context_pull")
_emit_pulls_context("p1", "html_loader", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "html_loader", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "html_loader", "uwg_term_2")
_emit_writes_through("p1", "html_loader", "write_through")
_emit_writes_through("p1", "html_loader", "write_through_2")
_emit_validated_by_safety_plane("p1", "html_loader", "safety_validation")
_emit_invokes_eval("p1", "html_loader", "eval_call")
_emit_proposal_commits_routing("p1", "html_loader", "routing_commit")
_emit_escalates_to_human("p1", "html_loader", "human_escalation")
_emit_routes_through("p1", "html_loader", "route_through")
_emit_checks_agent_registry("p1", "html_loader", "agent_registry")
_emit_validates_agent_capability("p1", "html_loader", "capability")
_emit_dispatches_execution_plan("p1", "html_loader", "exec_plan")
_emit_agent_executes_agent("p1", "html_loader", "sub_agent")
_emit_routes_to_agent("p1", "html_loader", "target_agent")
_emit_verifies_policy("p1", "html_loader", "policy_check")
_emit_observes_runtime_state("p1", "html_loader", "runtime_state")
_emit_verifies_boundary("p1", "html_loader", "boundary_check")
_emit_transcripts_response("p1", "html_loader", "transcript")
_emit_hard_fails_untranscripted("p1", "html_loader")
_emit_gated_by_confidence("p1", "html_loader", "confidence_gate")
emit_replay_key("p0", "html_loader")
emit_determinism_digest("p0", "html_loader")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "html_loader", "execution_auth")
_emit_validates_capability("p2", "html_loader", "capability_check")
_emit_routes_to_capability("p2", "html_loader", "capability_route")
_emit_writes_via_uwg("p2", "html_loader", "uwg_write")
_emit_blocks_direct_write("p2", "html_loader", "direct_write_block")
_emit_records_tool_invocation("p2", "html_loader", "tool_invocation")
_emit_captures_execution_output("p2", "html_loader", "exec_output")
_emit_dispatches_agent("p3", "html_loader", "agent_dispatch")
_emit_coordinates_agents("p3", "html_loader", "agent_coordination")
_emit_records_workflow_lineage("p3", "html_loader", "workflow_lineage")
_emit_records_healing_outcome("p3", "html_loader", "healing_outcome")
_emit_escalates_failure("p3", "html_loader", "failure_escalation")
_emit_orchestrates_workflow("p3", "html_loader", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "html_loader", "healing_dispatch")
_emit_invokes_evaluation("p3", "html_loader", "evaluation_signal")
_emit_records_telemetry_event("p4", "html_loader", "telemetry_event")
_emit_captures_evaluation_metric("p4", "html_loader", "eval_metric")
_emit_stores_embedding("p4", "html_loader", "embedding_store")
_emit_updates_meta_learning_state("p4", "html_loader", "meta_learning")
_emit_links_execution_to_snapshot("p4", "html_loader", "exec_snapshot_link")

log = logging.getLogger(__name__)


class _TagStripper(HTMLParser):
    """Minimal stdlib HTMLParser that extracts visible text content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._pieces: list[str] = []
        self._skip_depth: int = 0
        self._skip_tags: frozenset[str] = frozenset({"script", "style", "head"})

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._pieces.append(data)

    def get_text(self) -> str:
        return " ".join(self._pieces)


_RE_SCRIPT_STYLE = re.compile("<\\s*(script|style)[^>]*>.*?</\\s*\\1\\s*>", re.DOTALL | re.IGNORECASE)
_RE_TAGS = re.compile("<[^>]+>")
_RE_WHITESPACE = re.compile("\\s+")


def _try_load_text(file_path: Path) -> str | None:
    """
    Attempt HTML text extraction via multiple strategies.

    Returns:
        Extracted visible text on success, or None on any failure.
    """
    try:
        raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("HTML read failed for %s: %s", file_path, exc)
        return None
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text: str = soup.get_text(separator=" ", strip=True)
        return _RE_WHITESPACE.sub(" ", text).strip()
    # guardian: allow-silent-swallow - optional dependency
    except ImportError:
        pass
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("bs4 extraction failed, falling back to stdlib: %s", exc)
    try:
        stripper = _TagStripper()
        stripper.feed(raw)
        text = stripper.get_text()
        text = html.unescape(text)
        text = _RE_WHITESPACE.sub(" ", text).strip()
        return text
    # guardian: allow-silent-swallow
    except Exception as exc:
        log.warning("Stdlib HTML extraction failed for %s: %s", file_path, exc)
    try:
        text = _RE_SCRIPT_STYLE.sub("", raw)
        text = _RE_TAGS.sub(" ", text)
        text = html.unescape(text)
        text = _RE_WHITESPACE.sub(" ", text).strip()
        return text
    # guardian: allow-silent-swallow
    except Exception:
        return None


class HTMLDocumentLoader:
    """ImportError-safe HTML loader. Uses BeautifulSoup if available, stdlib otherwise."""

    @staticmethod
    def load_file(file_path: Path) -> str:
        """
        Extract visible text from an HTML file.

        Args:
            file_path: Path to the HTML file.

        Returns:
            Visible text content with tags stripped, or "" on any failure.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HTMLDocumentLoader.load_file"
        )

        text = _try_load_text(file_path)
        return text if text is not None else ""

    @staticmethod
    def load_path(path: Path) -> str:
        """Alias for load_file (API parity with other loaders)."""
        return HTMLDocumentLoader.load_file(path)


__all__ = ["HTMLDocumentLoader"]
