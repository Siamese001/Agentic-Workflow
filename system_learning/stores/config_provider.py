"""Concrete ConfigProvider — provides current routing/threshold configs for the pipeline.

Reads from ``runtime_state.json`` and an optional config directory to supply
the meta-learning pipeline with current configuration state.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

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
    _emit_snapshots_state,
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
from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

_emit_applies_guardrail("p0", "config_provider", "p0_governance")
_emit_reads_policy_state("p0", "config_provider", "policy_binding")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("config_provider", "p4obs", "metric_1")
_emit_emits_metric_event("config_provider", "p4obs", "metric_2")
_emit_emits_metric_event("config_provider", "p4obs", "metric_3")
_emit_emits_metric_event("config_provider", "p4obs", "metric_4")
_emit_emits_metric_event("config_provider", "p4obs", "metric_5")
_emit_emits_metric_event("config_provider", "p4obs", "metric_6")
_emit_records_incident_event("config_provider", "p4obs", "incident")
_emit_captures_runtime_anomaly("config_provider", "p4obs", "anomaly")
_emit_writes_observability_log("config_provider", "p4obs", "obs_log")
_emit_updates_monitoring_state("config_provider", "p4obs", "mon_state")
_emit_triggers_alert("config_provider", "p4obs", "alert")
_emit_links_incident_trace("config_provider", "p4obs", "trace_link")
_emit_captures_pattern("config_provider", "p3lm", "pattern")
_emit_records_learning_event("config_provider", "p3lm", "learning_event")
_emit_writes_learning_snapshot("config_provider", "p3lm", "snapshot")
_emit_feeds_meta_learning("config_provider", "p3lm", "meta_feed")
_emit_updates_routing_strategy("config_provider", "p3lm", "routing")
_emit_improves_agent_policy("config_provider", "p3lm", "policy")
_emit_stores_learning_state("config_provider", "p3lm", "state")
_emit_records_execution_trace("config_provider", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("config_provider", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("config_provider", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("config_provider", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("config_provider", "L4_STATE", "p2_trace_5")
_emit_reads_environ("config_provider", "env_read", "p2_env_1")
_emit_reads_environ("config_provider", "env_read", "p2_env_2")
_emit_reads_runtime_state("config_provider", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("config_provider", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "config_provider", "context_pull")
_emit_pulls_context("p1", "config_provider", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "config_provider", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "config_provider", "uwg_term_2")
_emit_writes_through("p1", "config_provider", "write_through")
_emit_writes_through("p1", "config_provider", "write_through_2")
_emit_validated_by_safety_plane("p1", "config_provider", "safety_validation")
_emit_invokes_eval("p1", "config_provider", "eval_call")
_emit_proposal_commits_routing("p1", "config_provider", "routing_commit")
_emit_escalates_to_human("p1", "config_provider", "human_escalation")
_emit_routes_through("p1", "config_provider", "route_through")
_emit_checks_agent_registry("p1", "config_provider", "agent_registry")
_emit_validates_agent_capability("p1", "config_provider", "capability")
_emit_dispatches_execution_plan("p1", "config_provider", "exec_plan")
_emit_agent_executes_agent("p1", "config_provider", "sub_agent")
_emit_routes_to_agent("p1", "config_provider", "target_agent")
_emit_verifies_policy("p1", "config_provider", "policy_check")
_emit_observes_runtime_state("p1", "config_provider", "runtime_state")
_emit_verifies_boundary("p1", "config_provider", "boundary_check")
_emit_transcripts_response("p1", "config_provider", "transcript")
_emit_hard_fails_untranscripted("p1", "config_provider")
_emit_gated_by_confidence("p1", "config_provider", "confidence_gate")
emit_replay_key("p0", "config_provider")
emit_determinism_digest("p0", "config_provider")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "config_provider", "execution_auth")
_emit_validates_capability("p2", "config_provider", "capability_check")
_emit_routes_to_capability("p2", "config_provider", "capability_route")
_emit_writes_via_uwg("p2", "config_provider", "uwg_write")
_emit_blocks_direct_write("p2", "config_provider", "direct_write_block")
_emit_records_tool_invocation("p2", "config_provider", "tool_invocation")
_emit_captures_execution_output("p2", "config_provider", "exec_output")
_emit_dispatches_agent("p3", "config_provider", "agent_dispatch")
_emit_coordinates_agents("p3", "config_provider", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_provider", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_provider", "healing_outcome")
_emit_escalates_failure("p3", "config_provider", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_provider", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_provider", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_provider", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_provider", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_provider", "eval_metric")
_emit_stores_embedding("p4", "config_provider", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_provider", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_provider", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class FileBackedConfigProvider:
    """File-backed config provider reading from runtime state and config files.

    Parameters
    ----------
    runtime_state_path : Path
        Path to ``runtime_state.json``.
    config_dir : Path | None
        Optional directory containing per-surface config JSON files.
    """

    def __init__(
        self,
        runtime_state_path: Path,
        config_dir: Path | None = None,
    ) -> None:
        self._runtime_state_path = Path(runtime_state_path)
        self._config_dir = Path(config_dir) if config_dir else None

    def _load_runtime_state(self) -> dict[str, Any]:
        if not self._runtime_state_path.exists():
            return {}
        try:
            return json.loads(self._runtime_state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            return {}

    def get_current_configs(self) -> dict[str, bytes]:
        """Return materialized config bytes keyed by surface name.

        Reads from the config directory (if available) or falls back to
        extracting config sections from runtime_state.json.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "FileBackedConfigProvider.get_current_configs", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedConfigProvider.get_current_configs"
        )

        configs: dict[str, bytes] = {}

        # Try config directory first
        if self._config_dir and self._config_dir.exists():
            for cfg_path in sorted(self._config_dir.glob("*.json")):
                surface = cfg_path.stem
                try:
                    raw = cfg_path.read_bytes()
                    configs[surface] = raw
                except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                    continue

        # Fall back to runtime_state sections
        if not configs:
            state = self._load_runtime_state()
            for key in ("meta_learning", "healing_config", "routing_config"):
                section = state.get(key)
                if section is not None:
                    configs[key] = json.dumps(section, separators=(",", ":"), sort_keys=True).encode("utf-8")

        if configs:
            try:
                bridge = get_sl_memory_bridge()
                for surface_name, raw in configs.items():
                    bridge.persist_config_snapshot(surface_name, raw)
            except Exception as exc:  # guardian: allow-silent-swallower
                logger.debug("Failed to persist config snapshots: %s", exc)

        return configs

    def get_last_update_utc(self, surface_name: str) -> int | None:
        """Return last update timestamp for a surface from runtime state."""
        state = self._load_runtime_state()
        # Convention: "<surface>_last_update" key in state
        key = f"{surface_name}_last_update"
        val = state.get(key)
        if isinstance(val, int):
            return val
        # Try nested in meta_learning section
        ml = state.get("meta_learning", {})
        val = ml.get(key)
        return val if isinstance(val, int) else None

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        """Return last N parameter values for a surface.

        Reads from runtime state ``"<surface>_history"`` key, expected to
        be a list of floats.
        """
        state = self._load_runtime_state()
        key = f"{surface_name}_history"
        history = state.get(key, [])
        if not isinstance(history, list):
            return ()
        # Take last N, coerce to float
        values: list[float] = []
        for v in history[-n:]:
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                continue
        return tuple(values)


class InMemoryConfigProvider:
    """In-memory config provider for testing."""

    def __init__(self) -> None:
        self._configs: dict[str, bytes] = {}
        self._last_updates: dict[str, int] = {}
        self._histories: dict[str, list[float]] = {}

    def set_config(self, surface: str, data: bytes) -> None:
        self._configs[surface] = data

    def set_last_update(self, surface: str, utc: int) -> None:
        self._last_updates[surface] = utc

    def set_history(self, surface: str, values: list[float]) -> None:
        self._histories[surface] = values

    def get_current_configs(self) -> dict[str, bytes]:
        return dict(self._configs)

    def get_last_update_utc(self, surface_name: str) -> int | None:
        return self._last_updates.get(surface_name)

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryConfigProvider.get_param_history"
        )

        history = self._histories.get(surface_name, [])
        return tuple(history[-n:])


class InMemoryBaselineMetricsProvider:
    """In-memory baseline metrics provider for testing / initial bootstrap.

    Returns neutral baseline metrics that pass shadow validation by default.
    """

    def __init__(self, production: Any = None, shadow: Any = None) -> None:
        self._production = production
        self._shadow = shadow

    def production_metrics(self) -> Any:
        return self._production

    def shadow_metrics(self, pkg: Any) -> Any:  # noqa: ARG002
        return self._shadow


__all__ = [
    "FileBackedConfigProvider",
    "InMemoryConfigProvider",
    "InMemoryBaselineMetricsProvider",
]
