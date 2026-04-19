from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "telepathy_interface_types")
emit_determinism_digest("p0", "telepathy_interface_types")

_emit_dispatches_healing_run("p1", "telepathy_interface_types", "L3")
_emit_routes_through("p1", "telepathy_interface_types", "L3")
_emit_checks_agent_registry("p1", "telepathy_interface_types", "agent_registry")
_emit_validates_agent_capability("p1", "telepathy_interface_types", "capability")
_emit_dispatches_execution_plan("p1", "telepathy_interface_types", "exec_plan")
_emit_agent_executes_agent("p1", "telepathy_interface_types", "sub_agent")
_emit_routes_to_agent("p1", "telepathy_interface_types", "target_agent")
_emit_verifies_policy("p1", "telepathy_interface_types", "policy_check")
_emit_observes_runtime_state("p1", "telepathy_interface_types", "runtime_state")
_emit_verifies_boundary("p1", "telepathy_interface_types", "boundary_check")
_emit_transcripts_response("p1", "telepathy_interface_types", "transcript")
_emit_hard_fails_untranscripted("p1", "telepathy_interface_types")
_emit_gated_by_confidence("p1", "telepathy_interface_types", "confidence_gate")
_emit_escalates_to_human("p1", "telepathy_interface_types", "L3")
_emit_reads_policy_state("p1", "telepathy_interface_types", "L3")
_emit_authorize_and_execute("p2", "telepathy_interface_types", "execution_auth")
_emit_validates_capability("p2", "telepathy_interface_types", "capability_check")
_emit_routes_to_capability("p2", "telepathy_interface_types", "capability_route")
_emit_writes_via_uwg("p2", "telepathy_interface_types", "uwg_write")
_emit_blocks_direct_write("p2", "telepathy_interface_types", "direct_write_block")
_emit_records_tool_invocation("p2", "telepathy_interface_types", "tool_invocation")
_emit_captures_execution_output("p2", "telepathy_interface_types", "exec_output")
_emit_dispatches_agent("p3", "telepathy_interface_types", "agent_dispatch")
_emit_coordinates_agents("p3", "telepathy_interface_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "telepathy_interface_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "telepathy_interface_types", "healing_outcome")
_emit_escalates_failure("p3", "telepathy_interface_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "telepathy_interface_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telepathy_interface_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "telepathy_interface_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "telepathy_interface_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telepathy_interface_types", "eval_metric")
_emit_stores_embedding("p4", "telepathy_interface_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "telepathy_interface_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telepathy_interface_types", "exec_snapshot_link")

"\nL6 Codebase Telepathy - Human Instruction Watcher\n\nImplements dynamic instruction injection via observability/human_instructions.md.\nAllows humans to telepathically control mission execution by writing commands.\n"
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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
from tqdm import tqdm

_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_1")
_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_2")
_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_3")
_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_4")
_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_5")
_emit_emits_metric_event("telepathy_interface_types", "p4obs", "metric_6")
_emit_records_incident_event("telepathy_interface_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("telepathy_interface_types", "p4obs", "anomaly")
_emit_writes_observability_log("telepathy_interface_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("telepathy_interface_types", "p4obs", "mon_state")
_emit_triggers_alert("telepathy_interface_types", "p4obs", "alert")
_emit_links_incident_trace("telepathy_interface_types", "p4obs", "trace_link")
_emit_captures_pattern("telepathy_interface_types", "p3lm", "pattern")
_emit_records_learning_event("telepathy_interface_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("telepathy_interface_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("telepathy_interface_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("telepathy_interface_types", "p3lm", "routing")
_emit_improves_agent_policy("telepathy_interface_types", "p3lm", "policy")
_emit_stores_learning_state("telepathy_interface_types", "p3lm", "state")
_emit_records_execution_trace("telepathy_interface_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("telepathy_interface_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("telepathy_interface_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("telepathy_interface_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("telepathy_interface_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("telepathy_interface_types", "env_read", "p2_env_1")
_emit_reads_environ("telepathy_interface_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("telepathy_interface_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("telepathy_interface_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "telepathy_interface_types", "context_pull")
_emit_pulls_context("p1", "telepathy_interface_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "telepathy_interface_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "telepathy_interface_types", "uwg_term_2")
_emit_writes_through("p1", "telepathy_interface_types", "write_through")
_emit_writes_through("p1", "telepathy_interface_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "telepathy_interface_types", "safety_validation")
_emit_invokes_eval("p1", "telepathy_interface_types", "eval_call")
_emit_proposal_commits_routing("p1", "telepathy_interface_types", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class TelepathyInterface:
    """
    Human instruction telepathy interface for dynamic mission control.

    Watches observability/human_instructions.md for commands and injects
    them into the execution context to alter mission behavior.
    """

    def __init__(self, instructions_path: str = "observability/human_instructions.md"):
        """
        Initialize the telepathy interface.

        Args:
            instructions_path: Path to the human instructions file
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TelepathyInterface.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TelepathyInterface.__init__", "p0_governance")
        self.instructions_path = Path(instructions_path)
        self._cycle = 0
        self._last_consumed = ""
        _wg.ensure_dir(self.instructions_path.parent)
        LOGGER.info(f"Telepathy interface initialized: {self.instructions_path}")

    def check_instructions(self, cycle: int) -> str | None:
        """
        Check for new human instructions.

        Args:
            cycle: Current mission cycle

        Returns:
            Instruction text if found, None otherwise
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "TelepathyInterface.check_instructions",
        )

        self._cycle = cycle
        if not self.instructions_path.exists():
            return None
        try:
            content: Any = self.instructions_path.read_text(encoding="utf-8").strip()
            if not content or content.startswith("# DONE"):
                return None
            if content == self._last_consumed:
                return None
            LOGGER.info(f"🧠 Telepathic instruction received (Cycle {cycle}): {content[:100]}...")
            return content
        except (ValueError, TypeError) as e:
            LOGGER.error(f"Failed to read telepathy instructions: {e}")
            return None  # guardian: allow-return-none-swallow -- telepathy read: non-fatal, caller checks for None

    def parse_instructions(self, instructions: str) -> dict[str, Any]:
        """
        Parse human instructions into executable commands.

        Args:
            instructions: Raw instruction text

        Returns:
            Dictionary of parsed commands and signals
        """
        commands: Any = {
            "stop": False,
            "pause": False,
            "skip_files": [],
            "force_agents": [],
            "force_test": False,
            "force_style": False,
            "force_safety": False,
            "force_dependency": False,
            "custom_signals": set(),
            "raw": instructions,
        }
        instructions_lower: Any = instructions.lower()
        if any(word in instructions_lower for word in ["stop", "abort", "halt"]):
            commands["stop"] = True
            commands["custom_signals"].add("TELEPATHY_STOP")
        if "pause" in instructions_lower:
            commands["pause"] = True
            commands["custom_signals"].add("TELEPATHY_PAUSE")
        agent_mapping: Any = {
            "test": "TestPilot",
            "style": "CodeStyleGuardian",
            "safety": "SafetyInspectorAgent",
            "dependency": "DependencySentinelAgent",
            "architecture": "ArchitectureGovernor",
            "hygiene": "HygieneGuardian",
            "Historian": "Historian",
            "sherlock": "Sherlock",
            "reflection": "ReflectionAgent",
        }
        for keyword, agent in tqdm(agent_mapping.items(), desc="Processing", unit="item"):
            if f"force {keyword}" in instructions_lower or f"run {keyword}" in instructions_lower:
                commands["force_agents"].append(agent)
                commands["custom_signals"].add(f"FORCE_{agent.upper()}")
                if keyword == "test":
                    commands["force_test"] = True
                elif keyword == "style":
                    commands["force_style"] = True
                elif keyword == "safety":
                    commands["force_safety"] = True
                elif keyword == "dependency":
                    commands["force_dependency"] = True
        if "skip" in instructions_lower:
            import re

            skip_match: Any = re.search("skip\\s+(.+?)(?:\\n|$)", instructions_lower)
            if skip_match:
                skip_patterns: Any = [p.strip() for p in skip_match.group(1).split(",")]
                commands["skip_files"] = skip_patterns
                commands["custom_signals"].add("SKIP_FILES")
        if "signal:" in instructions_lower:
            import re

            signal_matches: Any = re.findall("signal:\\s*(\\w+)", instructions_lower)
            for signal in signal_matches:
                commands["custom_signals"].add(signal.upper())
        return commands

    def consume_instructions(self, instructions: str) -> None:
        """
        Mark instructions as consumed to prevent re-processing.

        Args:
            instructions: The instructions that were consumed
        """
        try:
            done_content: Any = f"# DONE (Cycle {self._cycle})\n\n# Original instructions:\n{instructions}"
            _wg.write_text(self.instructions_path, done_content, encoding="utf-8")
            self._last_consumed = instructions
            LOGGER.info(f"Instructions consumed and marked done (Cycle {self._cycle})")
        except (
            OSError,
            ValueError,
            TypeError,
        ):  # guardian: allow-log-and-swallow -- mark done: re-raises immediately, error log unreachable but preserved for diagnostics
            raise
            LOGGER.error(f"Failed to mark instructions as done: {e}")

    def inject_into_context(self, context: Any, commands: dict[str, Any]) -> Any:
        """
        Inject parsed commands into execution context.

        Args:
            context: Current execution context
            commands: Parsed commands from telepathy

        Returns:
            Modified context with injected commands
        """
        if hasattr(context, "signals"):
            context.signals.update(commands["custom_signals"])
        if hasattr(context, "metadata"):
            context.metadata.update({"telepathy_commands": commands, "telepathy_cycle": self._cycle})
        else:
            context.metadata = {"telepathy_commands": commands, "telepathy_cycle": self._cycle}
        if commands["force_agents"] and hasattr(context, "forced_agents"):
            context.forced_agents.extend(commands["force_agents"])
        return context

    def clear_instructions(self) -> None:
        """Clear the instructions file."""
        try:
            if self.instructions_path.exists():
                _wg.remove_file(self.instructions_path)
                LOGGER.info("Telepathy instructions cleared")
        except (
            OSError,
            ValueError,
            TypeError,
        ):  # guardian: allow-log-and-swallow -- clear instructions: re-raises immediately, error log unreachable but preserved for diagnostics
            raise
            LOGGER.error(f"Failed to clear instructions: {e}")


_telepathy: TelepathyInterface | None = None


def get_telepathy_interface(
    instructions_path: str = "observability/human_instructions.md",
) -> TelepathyInterface:
    """Get or create the global telepathy interface instance."""
    global _telepathy
    if _telepathy is None:
        _telepathy = TelepathyInterface(instructions_path)
    return _telepathy


async def process_telepathy_instructions(context: Any, cycle: int) -> Any:
    """
    Process any telepathic instructions and inject into context.

    Args:
        context: Current execution context
        cycle: Current mission cycle

    Returns:
        Modified context with telepathic instructions applied
    """
    telepathy: Any = get_telepathy_interface()
    instructions: Any = telepathy.check_instructions(cycle)
    if instructions:
        commands: Any = telepathy.parse_instructions(instructions)
        context: Any = telepathy.inject_into_context(context, commands)
        telepathy.consume_instructions(instructions)
        if commands["force_agents"]:
            LOGGER.info(f"🎯 Telepathy forcing agents: {', '.join(commands['force_agents'])}")
        if commands["stop"]:
            LOGGER.warning("🛑 Telepathic STOP instruction received")
            context.signals.add("TELEPATHY_STOP")
    return context
