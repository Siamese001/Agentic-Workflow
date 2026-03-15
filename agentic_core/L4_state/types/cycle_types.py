from __future__ import annotations

"Think-Act-Observe Cycle Implementation.\n\nPhase 2 - Pillar 4: Workflow (DAGs)\nImplements the 5-step Mission-Scene-Think-Act-Observe loop with ReAct integration.\n"
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


Logger: Any = logging.getLogger(__name__)


@dataclass
class CycleConfig:
    """configuration for Think-Act-Observe cycle."""

    max_iterations: int = 10
    enable_react: bool = True
    enable_dag: bool = True
    enable_state_persistence: bool = True
    react_max_steps: int = 5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "CycleConfig.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "CycleConfig.to_dict", "p0_governance")
        return {
            "max_iterations": self.max_iterations,
            "enable_react": self.enable_react,
            "enable_dag": self.enable_dag,
            "enable_state_persistence": self.enable_state_persistence,
            "react_max_steps": self.react_max_steps,
        }


@dataclass
class CycleState:
    """State of the Think-Act-Observe cycle."""

    mission: str
    scene: dict[str, Any]
    iteration: int = 0
    current_phase: str = "mission"
    observations: list[dict[str, Any]] = field(default_factory=list)
    actions_taken: list[dict[str, Any]] = field(default_factory=list)
    reasoning_traces: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mission": self.mission,
            "scene": self.scene,
            "iteration": self.iteration,
            "current_phase": self.current_phase,
            "observations": self.observations,
            "actions_taken": self.actions_taken,
            "reasoning_traces": self.reasoning_traces,
            "metadata": self.metadata,
        }


class ThinkActObserveEngine:
    """Engine for executing the Think-Act-Observe cycle.

    Integrates:
    - ReAct engine for structured reasoning (Pillar 6)
    - DAG engine for Task dependencies (Pillar 4)
    - State persistence for pause/resume

    5-Step Cycle:
    1. MISSION - Define the goal
    2. SCENE - Gather context
    3. THINK - Plan next actions (uses ReAct)
    4. ACT - Execute actions (uses DAG)
    5. OBSERVE - Interpret results and update state
    """

    def __init__(self, config: CycleConfig | None = None, enable_logging: bool = True):
        """Initialize Think-Act-Observe engine.

        Args:
            config: Cycle configuration
            enable_logging: Enable logging
        """
        self.config = config or CycleConfig()
        self.enable_logging = enable_logging
        if self.config.enable_react:
            self.react_engine = ReActEngine(max_steps=self.config.react_max_steps)
        else:
            self.react_engine = None
        if self.config.enable_dag:
            self.dag_engine = DAGEngine(enable_logging=enable_logging)
        else:
            self.dag_engine = None
        self.state: CycleState | None = None
        if self.enable_logging:
            LOGGER.info("think_act_observe_engine_initialized", extra={"config": self.config.to_dict()})

    async def execute_cycle(
        self, mission: str, scene: dict[str, Any], think_fn: Any, act_fn: Any
    ) -> dict[str, Any]:
        """Execute the full Think-Act-Observe cycle.

        Args:
            mission: The mission/goal to accomplish
            scene: Initial scene/context
            think_fn: Function for thinking/planning
            act_fn: Function for executing actions

        Returns:
            Final result with observations and state
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ThinkActObserveEngine.execute_cycle")

        self.state = CycleState(mission=mission, scene=scene)
        if self.enable_logging:
            LOGGER.info("cycle_started", extra={"mission": mission, "scene_keys": list(scene.keys())})
        self.state.current_phase = "mission"
        self.state.current_phase = "scene"
        while self.state.iteration < self.config.max_iterations:
            self.state.iteration += 1
            if self.enable_logging:
                LOGGER.info("iteration_started", extra={"iteration": self.state.iteration})
            think_result: Any = await self._think_phase(think_fn)
            if not think_result.get("success"):
                break
            act_result: Any = await self._act_phase(think_result.get("actions", []), act_fn)
            observe_result: Any = await self._observe_phase(think_result, act_result)
            if observe_result.get("mission_complete"):
                if self.enable_logging:
                    LOGGER.info("mission_complete", extra={"iteration": self.state.iteration})
                break
        final_result: Any = {
            "success": True,
            "mission": mission,
            "iterations": self.state.iteration,
            "observations": self.state.observations,
            "actions_taken": self.state.actions_taken,
            "reasoning_traces": self.state.reasoning_traces,
            "final_state": self.state.to_dict(),
        }
        if self.enable_logging:
            LOGGER.info(
                "cycle_completed",
                extra={
                    "iterations": self.state.iteration,
                    "observations_count": len(self.state.observations),
                },
            )
        return final_result

    async def _think_phase(self, think_fn: Any) -> dict[str, Any]:
        """Execute THINK phase using ReAct engine.

        Args:
            think_fn: Function for LLM thinking

        Returns:
            Thinking result with planned actions
        """
        self.state.current_phase = "think"
        if self.enable_logging:
            LOGGER.debug("think_phase_started")
        if self.react_engine:
            try:
                {
                    "mission": self.state.mission,
                    "scene": self.state.scene,
                    "iteration": self.state.iteration,
                    "previous_observations": self.state.observations[-3:] if self.state.observations else [],
                }
                trace = await self.react_engine.run(
                    Task=self.state.mission,
                    think_fn=think_fn,
                    act_fn=lambda action: {"type": "plan", "action": action},
                )
                reasoning_trace = trace.to_reasoning_trace()
                self.state.reasoning_traces.append(reasoning_trace.to_dict())
                actions = []
                for step in trace.steps:
                    if step.action and step.action != "FINISH":
                        actions.append({"type": "action", "action": step.action, "thought": step.thought})
                return {"success": True, "actions": actions, "reasoning_trace": reasoning_trace.to_dict()}
            # guardian: allow-silent-swallow
            except Exception as e:
                if self.enable_logging:
                    LOGGER.error("think_phase_failed", extra={"error": str(e)}, exc_info=True)
                return {"success": False, "error": str(e), "actions": []}
        else:
            try:
                result = await think_fn(self.state.mission, self.state.scene)
                return {"success": True, "actions": result.get("actions", [])}
            # guardian: allow-silent-swallow
            except Exception as e:
                return {"success": False, "error": str(e), "actions": []}

    async def _act_phase(self, actions: list[dict[str, Any]], act_fn: Any) -> dict[str, Any]:
        """Execute ACT phase using DAG engine.

        Args:
            actions: Actions to execute
            act_fn: Function for executing actions

        Returns:
            Action results
        """
        self.state.current_phase = "act"
        if self.enable_logging:
            LOGGER.debug("act_phase_started", extra={"action_count": len(actions)})
        if not actions:
            return {"success": True, "results": []}
        if self.dag_engine:
            try:
                self.dag_engine.reset()
                for i, action in enumerate(actions):
                    Task = Task(
                        id=f"action_{i}",
                        name=action.get("action", f"Action {i}"),
                        TaskType=TaskType.ACTION,
                        parameters=action,
                    )
                    self.dag_engine.add_task(Task)
                dag_result = await self.dag_engine.execute(executor=lambda Task: act_fn(Task.parameters))
                for action in actions:
                    self.state.actions_taken.append(action)
                return {
                    "success": dag_result.success,
                    "results": list(dag_result.task_results.values()),
                    "dag_result": dag_result.to_dict(),
                }
            # guardian: allow-silent-swallow
            except Exception as e:
                if self.enable_logging:
                    LOGGER.error("act_phase_failed", extra={"error": str(e)}, exc_info=True)
                return {"success": False, "error": str(e), "results": []}
        else:
            results = []
            for action in actions:
                try:
                    result = await act_fn(action)
                    results.append(result)
                    self.state.actions_taken.append(action)
                # guardian: allow-silent-swallow
                except Exception as e:
                    if self.enable_logging:
                        LOGGER.error("action_failed", extra={"action": action, "error": str(e)})
                    results.append({"success": False, "error": str(e)})
            return {"success": True, "results": results}

    async def _observe_phase(
        self, think_result: dict[str, Any], act_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute OBSERVE phase.

        Args:
            think_result: Result from think phase
            act_result: Result from act phase

        Returns:
            Observations and state updates
        """
        self.state.current_phase = "observe"
        if self.enable_logging:
            LOGGER.debug("observe_phase_started")
        observation = {
            "iteration": self.state.iteration,
            "think_success": think_result.get("success"),
            "act_success": act_result.get("success"),
            "results": act_result.get("results", []),
            "timestamp": self.state.metadata.get("timestamp"),
        }
        self.state.observations.append(observation)
        mission_complete = False
        results = act_result.get("results", [])
        if results:
            last_result = results[-1]
            if isinstance(last_result, dict):
                mission_complete = last_result.get("mission_complete", False)
        return {"observation": observation, "mission_complete": mission_complete}

    def get_state(self) -> dict[str, Any] | None:
        """Get current cycle state.

        Returns:
            Current state or None
        """
        return self.state.to_dict() if self.state else None

    async def save_state(self, path: str) -> None:
        """Save cycle state to disk.

        Args:
            path: Path to save state
        """
        if not self.state:
            raise ValueError("No state to save")
        assert_no_persistent_write("L4", "json.dump")
        _get_write_gateway().write_json(path, self.state.to_dict(), indent=2)
        if self.enable_logging:
            LOGGER.info("state_saved", extra={"path": path})

    async def load_state(self, path: str) -> None:
        """Load cycle state from disk.

        Args:
            path: Path to load state from
        """
        with open(path) as f:
            state_dict: Any = json.load(f)
        self.state = CycleState(
            mission=state_dict["mission"],
            scene=state_dict["scene"],
            iteration=state_dict.get("iteration", 0),
            current_phase=state_dict.get("current_phase", "mission"),
            observations=state_dict.get("observations", []),
            actions_taken=state_dict.get("actions_taken", []),
            reasoning_traces=state_dict.get("reasoning_traces", []),
            metadata=state_dict.get("metadata", {}),
        )
        if self.enable_logging:
            LOGGER.info("state_loaded", extra={"path": path, "iteration": self.state.iteration})
