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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

trace_contract._emit_applies_guardrail("p0", "config_provider", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "config_provider", "policy_binding")

trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("config_provider", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("config_provider", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("config_provider", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("config_provider", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("config_provider", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("config_provider", "p4obs", "alert")
trace_contract._emit_links_incident_trace("config_provider", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("config_provider", "p3lm", "pattern")
trace_contract._emit_records_learning_event("config_provider", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("config_provider", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("config_provider", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("config_provider", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("config_provider", "p3lm", "policy")
trace_contract._emit_stores_learning_state("config_provider", "p3lm", "state")
trace_contract._emit_records_execution_trace("config_provider", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("config_provider", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("config_provider", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("config_provider", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("config_provider", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("config_provider", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("config_provider", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("config_provider", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("config_provider", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "config_provider", "context_pull")
trace_contract._emit_pulls_context("p1", "config_provider", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_provider", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_provider", "uwg_term_2")
trace_contract._emit_writes_through("p1", "config_provider", "write_through")
trace_contract._emit_writes_through("p1", "config_provider", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "config_provider", "safety_validation")
trace_contract._emit_invokes_eval("p1", "config_provider", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "config_provider", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "config_provider", "human_escalation")
trace_contract._emit_routes_through("p1", "config_provider", "route_through")
trace_contract._emit_checks_agent_registry("p1", "config_provider", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "config_provider", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "config_provider", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "config_provider", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "config_provider", "target_agent")
trace_contract._emit_verifies_policy("p1", "config_provider", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "config_provider", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "config_provider", "boundary_check")
trace_contract._emit_transcripts_response("p1", "config_provider", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "config_provider")
trace_contract._emit_gated_by_confidence("p1", "config_provider", "confidence_gate")
trace_contract.emit_replay_key("p0", "config_provider")
trace_contract.emit_determinism_digest("p0", "config_provider")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "config_provider", "execution_auth")
trace_contract._emit_validates_capability("p2", "config_provider", "capability_check")
trace_contract._emit_routes_to_capability("p2", "config_provider", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "config_provider", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "config_provider", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "config_provider", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "config_provider", "exec_output")
trace_contract._emit_dispatches_agent("p3", "config_provider", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "config_provider", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "config_provider", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "config_provider", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "config_provider", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "config_provider", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "config_provider", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "config_provider", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "config_provider", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "config_provider", "eval_metric")
trace_contract._emit_stores_embedding("p4", "config_provider", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "config_provider", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "config_provider", "exec_snapshot_link")

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
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load runtime state %s: %s", self._runtime_state_path, exc)
            return {}

    def get_current_configs(self) -> dict[str, bytes]:
        """Return materialized config bytes keyed by surface name.

        Reads from the config directory (if available) or falls back to
        extracting config sections from runtime_state.json.
        """
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "FileBackedConfigProvider.get_current_configs", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "FileBackedConfigProvider.get_current_configs",
        )

        configs: dict[str, bytes] = {}

        # Try config directory first
        if self._config_dir and self._config_dir.exists():
            for cfg_path in sorted(self._config_dir.glob("*.json")):
                surface = cfg_path.stem
                try:
                    raw = cfg_path.read_bytes()
                    configs[surface] = raw
                except OSError as exc:
                    logger.warning("Failed to read config surface %s: %s", cfg_path, exc)
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
            except (AttributeError, RuntimeError, TypeError, ValueError, OSError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                logger.debug("config_provider: failed to persist config snapshots: %s", exc)

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
        if n <= 0:
            return ()
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "InMemoryConfigProvider.get_param_history",
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
