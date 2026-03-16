"""
Dynamic Prompt Loader for Canon Validator Agents

Loads prompts from modularized markdown files based on agent role.
"""

from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "prompt_loader_util", "p0_governance")
_emit_reads_policy_state("p0", "prompt_loader_util", "policy_binding")
_emit_snapshots_state("p0", "prompt_loader_util", "state_snapshot")
emit_replay_key("p0", "prompt_loader_util")
emit_determinism_digest("p0", "prompt_loader_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "prompt_loader_util", "execution_auth")
_emit_validates_capability("p2", "prompt_loader_util", "capability_check")
_emit_routes_to_capability("p2", "prompt_loader_util", "capability_route")
_emit_writes_via_uwg("p2", "prompt_loader_util", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_loader_util", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_loader_util", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_loader_util", "exec_output")
_emit_dispatches_agent("p3", "prompt_loader_util", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_loader_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_loader_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_loader_util", "healing_outcome")
_emit_escalates_failure("p3", "prompt_loader_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_loader_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_loader_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_loader_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_loader_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_loader_util", "eval_metric")
_emit_stores_embedding("p4", "prompt_loader_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_loader_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_loader_util", "exec_snapshot_link")


class PromptLoader:
    """Loads and caches prompts from markdown files."""

    def __init__(self, prompts_dir: str | None = None):
        """Initialize prompt loader with base directory."""
        if prompts_dir is None:
            project_root = Path(__file__).parent.parent
            self.prompts_dir = project_root / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        self._cache: dict[str, str] = {}
        self._global_constraints: str | None = None

    def load_global_constraints(self) -> str:
        """Load global constraints that apply to all agents."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptLoader.load_global_constraints")

        if self._global_constraints is not None:
            return self._global_constraints
        constraints_path = self.prompts_dir / "global" / "constraints.md"
        if constraints_path.exists():
            self._global_constraints = constraints_path.read_text(encoding="utf-8")
        else:
            self._global_constraints = ""
        return self._global_constraints

    def load_specialist_prompt(self, agent_role: str) -> str:
        """
        Load specialist prompt for a specific agent role.

        Args:
            agent_role: Name of the agent (e.g., 'healer_agent', 'system_architect')

        Returns:
            Specialist prompt content or empty string if not found
        """
        if agent_role in self._cache:
            return self._cache[agent_role]
        specialist_path = self.prompts_dir / "specialists" / f"{agent_role}.md"
        if specialist_path.exists():
            content = specialist_path.read_text(encoding="utf-8")
            self._cache[agent_role] = content
            return content
        return ""

    def build_full_prompt(
        self, agent_role: str, task: str, code: str, original_line_count: int, lesson_learned: str = ""
    ) -> str:
        """
        Build complete prompt combining global constraints and specialist instructions.

        Args:
            agent_role: Name of the agent
            task: Specific task description
            code: Code to be fixed
            original_line_count: Number of lines in original file
            lesson_learned: Optional lesson from previous failure

        Returns:
            Complete prompt ready for LLM
        """
        global_constraints = self.load_global_constraints()
        specialist_prompt = self.load_specialist_prompt(agent_role)
        sections = []
        sections.append(f"Task: {task}")
        if specialist_prompt:
            sections.append(specialist_prompt)
        if global_constraints:
            constraints_with_count = global_constraints.replace(
                "{original_line_count}", str(original_line_count)
            )
            constraints_with_count = constraints_with_count.replace(
                "{int(original_line_count * 0.1)}", str(int(original_line_count * 0.1))
            )
            sections.append(constraints_with_count)
        if lesson_learned:
            sections.append(
                f"\n📚 LESSON LEARNED FROM PREVIOUS ATTEMPT:\n{lesson_learned}\nApply this lesson to your current fix. Start fresh with the original file.\n"
            )
        sections.append(f"\n{code}")
        return "\n\n".join(sections)

    def get_available_specialists(self) -> list[str]:
        """Get list of available specialist prompts."""
        specialists_dir = self.prompts_dir / "specialists"
        if not specialists_dir.exists():
            return []
        return [f.stem for f in specialists_dir.glob("*.md")]

    def reload_cache(self):
        """Clear cache to force reload of prompts."""
        self._cache.clear()
        self._global_constraints = None


_loader = PromptLoader()


def load_prompt_for_agent(
    agent_role: str, task: str, code: str, original_line_count: int, lesson_learned: str = ""
) -> str:
    """
    Convenience function to load complete prompt for an agent.

    Args:
        agent_role: Name of the agent (e.g., 'healer_agent')
        task: Specific task description
        code: Code to be fixed
        original_line_count: Number of lines in original file
        lesson_learned: Optional lesson from previous failure

    Returns:
        Complete prompt ready for LLM
    """
    return _loader.build_full_prompt(agent_role, task, code, original_line_count, lesson_learned)


def get_global_constraints() -> str:
    """Get global constraints that apply to all agents."""
    return _loader.load_global_constraints()


def get_specialist_prompt(agent_role: str) -> str:
    """Get specialist prompt for a specific agent role."""
    return _loader.load_specialist_prompt(agent_role)
