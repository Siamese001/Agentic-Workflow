"""Think-Act-Observe Cycle Implementation.

Phase 2 - Pillar 4: Workflow (DAGs)
Implements the 5-step Mission-Scene-Think-Act-Observe loop with ReAct integration.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

@dataclass
class CycleConfig:
    """Configuration for Think-Act-Observe cycle."""
    max_iterations: int = 10
    enable_react: bool = True
    enable_dag: bool = True
    enable_state_persistence: bool = True
    react_max_steps: int = 5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
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
    scene: Dict[str, Any]
    iteration: int = 0
    current_phase: str = "mission"
    observations: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_traces: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
    - DAG engine for task dependencies (Pillar 4)
    - State persistence for pause/resume

    5-Step Cycle:
    1. MISSION - Define the goal
    2. SCENE - Gather context
    3. THINK - Plan next actions (uses ReAct)
    4. ACT - Execute actions (uses DAG)
    5. OBSERVE - Interpret results and update state
    """

    def __init__(
        self,
        config: Optional[CycleConfig] = None,
        enable_logging: bool = True,
    ):
        """Initialize Think-Act-Observe engine.

        Args:
            config: Cycle configuration
            enable_logging: Enable logging
        """
        self.config = config or CycleConfig()
        self.enable_logging = enable_logging

        # Initialize sub-engines
        if self.config.enable_react:
            # Assuming ReActEngine exists and is imported
            # from .react_engine import ReActEngine # Example import
            self.react_engine = ReActEngine(
                max_steps=self.config.react_max_steps,
            )
        else:
            self.react_engine = None

        if self.config.enable_dag:
            # Assuming DAGEngine exists and is imported
            # from .dag_engine import DAGEngine # Example import
            self.dag_engine = DAGEngine(enable_logging=enable_logging)
        else:
            self.dag_engine = None

        self.state: Optional[CycleState] = None

        if self.enable_logging:
            LOGGER.info(
                "think_act_observe_engine_initialized",
                extra={"config": self.config.to_dict()}
            )

    async def execute_cycle(
        self,
        mission: str,
        scene: Dict[str, Any],
        think_fn: Any,
        act_fn: Any,
    ) -> Dict[str, Any]:
        """Execute the full Think-Act-Observe cycle.

        Args:
            mission: The mission/goal to accomplish
            scene: Initial scene/context
            think_fn: Function for thinking/planning
            act_fn: Function for executing actions

        Returns:
            Final result with observations and state
        """
        # Initialize state
        self.state = CycleState(
            mission=mission,
            scene=scene,
        )

        if self.enable_logging:
            LOGGER.info(
                "cycle_started",
                extra={
                    "mission": mission,
                    "scene_keys": list(scene.keys()),
                }
            )

        # Step 1: MISSION (already defined)
        self.state.current_phase = "mission"

        # Step 2: SCENE (already provided)
        self.state.current_phase = "scene"

        # Main loop: THINK -> ACT -> OBSERVE
        while self.state.iteration < self.config.max_iterations:
            self.state.iteration += 1

            if self.enable_logging:
                LOGGER.info(
                    "iteration_started",
                    extra={"iteration": self.state.iteration}
                )

            # Step 3: THINK
            think_result = await self._think_phase(think_fn)

            if not think_result.get("success"):
                break

            # Step 4: ACT
            act_result = await self._act_phase(
                think_result.get("actions", []),
                act_fn,
            )

            # Step 5: OBSERVE
            observe_result = await self._observe_phase(
                think_result,
                act_result,
            )

            # Check if mission is complete
            if observe_result.get("mission_complete"):
                if self.enable_logging:
                    LOGGER.info(
                        "mission_complete",
                        extra={"iteration": self.state.iteration}
                    )
                break

        final_result = {
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
                }
            )

        return final_result

    async def _think_phase(self, think_fn: Any) -> Dict[str, Any]:
        """Execute THINK phase using ReAct engine.

        Args:
            think_fn: Function for LLM thinking

        Returns:
            Thinking result with planned actions
        """
        self.state.current_phase = "think"

        if self.enable_logging:
            LOGGER.debug("think_phase_started")

        # Use ReAct engine if enabled
        if self.react_engine:
            try:
                # Create context for ReAct
                context = {
                    "mission": self.state.mission,
                    "scene": self.state.scene,
                    "iteration": self.state.iteration,
                    "previous_observations": self.state.observations[-3:] if self.state.observations
    else [],
                }

                # Run ReAct reasoning
                # Assuming ReActEngine.run returns a trace object
                trace = await self.react_engine.run(
                    task=self.state.mission,
                    think_fn=think_fn,
                    act_fn=lambda action: {"type": "plan", "action": action},
                )

                # Convert trace to reasoning trace
                reasoning_trace = trace.to_reasoning_trace()
                self.state.reasoning_traces.append(reasoning_trace.to_dict())

                # Extract actions from trace
                actions = []
                for step in trace.steps:
                    if step.action and step.action != "FINISH":
                        actions.append({
                            "type": "action",
                            "action": step.action,
                            "thought": step.thought,
                        })

                return {
                    "success": True,
                    "actions": actions,
                    "reasoning_trace": reasoning_trace.to_dict(),
                }

            except Exception as e:
                if self.enable_logging:
                    LOGGER.error(
                        "think_phase_failed",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
                return {
                    "success": False,
                    "error": str(e),
                    "actions": [],
                }

        else:
            # Fallback: direct thinking without ReAct
            try:
                result = await think_fn(self.state.mission, self.state.scene)
                return {
                    "success": True,
                    "actions": result.get("actions", []),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "actions": [],
                }

    async def _act_phase(
        self,
        actions: List[Dict[str, Any]],
        act_fn: Any,
    ) -> Dict[str, Any]:
        """Execute ACT phase using DAG engine.

        Args:
            actions: Actions to execute
            act_fn: Function for executing actions

        Returns:
            Action results
        """
        self.state.current_phase = "act"

        if self.enable_logging:
            LOGGER.debug(
                "act_phase_started",
                extra={"action_count": len(actions)}
            )

        if not actions:
            return {
                "success": True,
                "results": [],
            }

        # Use DAG engine if enabled
        if self.dag_engine:
            try:
                # Reset DAG
                self.dag_engine.reset()

                # Add tasks to DAG
                # Assuming Task and TaskType exist and are imported
                # from .dag_engine import Task, TaskType # Example import
                for i, action in enumerate(actions):
                    task = Task(
                        id=f"action_{i}",
                        name=action.get("action", f"Action {i}"),
                        task_type=TaskType.ACTION,
                        parameters=action,
                    )
                    self.dag_engine.add_task(task)

                # Execute DAG
                dag_result = await self.dag_engine.execute(
                    executor=lambda task: act_fn(task.parameters),
                )

                # Record actions
                for action in actions:
                    self.state.actions_taken.append(action)

                return {
                    "success": dag_result.success,
                    "results": list(dag_result.task_results.values()),
                    "dag_result": dag_result.to_dict(),
                }

            except Exception as e:
                if self.enable_logging:
                    LOGGER.error(
                        "act_phase_failed",
                        extra={"error": str(e)},
                        exc_info=True,
                    )
                return {
                    "success": False,
                    "error": str(e),
                    "results": [],
                }

        else:
            # Fallback: sequential execution
            results = []
            for action in actions:
                try:
                    result = await act_fn(action)
                    results.append(result)
                    self.state.actions_taken.append(action)
                except Exception as e:
                    if self.enable_logging:
                        LOGGER.error(
                            "action_failed",
                            extra={"action": action, "error": str(e)}
                        )
                    results.append({"success": False, "error": str(e)})

            return {
                "success": True,
                "results": results,
            }

    async def _observe_phase(
        self,
        think_result: Dict[str, Any],
        act_result: Dict[str, Any],
    ) -> Dict[str, Any]:
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

        # Create observation
        observation = {
            "iteration": self.state.iteration,
            "think_success": think_result.get("success"),
            "act_success": act_result.get("success"),
            "results": act_result.get("results", []),
            "timestamp": self.state.metadata.get("timestamp"),
        }

        self.state.observations.append(observation)

        # Determine if mission is complete
        # Simple heuristic: check if last action indicated completion
        mission_complete = False
        results = act_result.get("results", [])
        if results:
            last_result = results[-1]
            if isinstance(last_result, dict):
                mission_complete = last_result.get("mission_complete", False)

        return {
            "observation": observation,
            "mission_complete": mission_complete,
        }

    def get_state(self) -> Optional[Dict[str, Any]]:
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

        import json

        with open(path, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2, default=str)

        if self.enable_logging:
            LOGGER.info("state_saved", extra={"path": path})

    async def load_state(self, path: str) -> None:
        """Load cycle state from disk.

        Args:
            path: Path to load state from
        """

        with open(path, 'r') as f:
            state_dict = json.load(f)

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
            LOGGER.info(
                "state_loaded",
                extra={
                    "path": path,
                    "iteration": self.state.iteration,
                }
            )