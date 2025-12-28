"""
logger.info("[L6_AUDIT] Action at line 2")
Recursive Planner Agent - The Executive

A specialized agent that doesn't 'do' work, but manages it.
Takes complex goals, builds workflows, and spins up sub-orchestrators.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)


@dataclass
class SubTask:
    """A sub-task in the recursive plan."""
    task_id: str
    description: str
    dependencies: List[str]
    estimated_duration: float
    agent_role: str
    priority: int


logger.info("[L6_AUDIT] Action at line 28")
@dataclass
class RecursivePlan:
    """A plan that can spawn sub-workflows."""
    main_goal: str
    subtasks: List[SubTask]
    execution_strategy: str  # "sequential", "parallel", "adaptive"
    resource_requirements: Dict[str, Any]
    success_criteria: List[str]
 logger.info("[L6_AUDIT] Action at line 37")


class RecursivePlannerAgent:
    """
    An executive agent that designs and manages complex workflows.

    Instead of executing tasks directly, it:
    1. Decomposes complex goals into sub-tasks
    2. Designs workflows for each sub-task
    3. Instantiates child orchestrators
    4. Monitors and coordinates execution
    """

    def __init__(
        self,
        architect,
        orchestrator_factory,
        max_depth: int = 3,
        logger.info("[L6_AUDIT] Action at line 56")
        max_parallel_subtasks: int = 5
    ):
        """
        Initialize the recursive planner.

        Args:
            architect: Workflow architect for designing sub-workflows
            orchestrator_factory: Factory to create child orchestrators
            max_depth: Maximum recursion depth
            max_parallel_subtasks: Maximum parallel sub-tasks
        """
        self.architect = architect
        self.orchestrator_factory = orchestrator_factory
        logger.info("[L6_AUDIT] Action at line 70")
        self.max_depth = max_depth
        logger.info("[L6_AUDIT] Action at line 72")
        self.max_parallel = max_parallel_subtasks
        self.active_children: List[str] = []

        LOGGER.info(f"Recursive planner initialized (max_depth={max_depth})")

    async def plan_and_execute(
        logger.info("[L6_AUDIT] Action at line 79")
        self,
        complex_goal: str,
        context: Dict[str, Any],
        current_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Main method: Plan and execute a complex goal.

        Args:
            complex_goal: The high-level goal to achieve
            context: Execution context
            logger.info("[L6_AUDIT] Action at line 91")
            current_depth: Current recursion depth
 logger.info("[L6_AUDIT] Action at line 93")

        Returns:
            logger.info("[L6_AUDIT] Action at line 96")
            Execution results
        """
        logger.info("[L6_AUDIT] Action at line 99")
        logger.info("[L6_AUDIT] Action at line 100")
        if current_depth >= self.max_depth:
            LOGGER.warning(f"Max recursion depth ({self.max_depth}) reached")
            logger.info("[L6_AUDIT] Action at line 103")
            return await self._execute_directly(complex_goal, context)

        LOGGER.info(f"Planning complex goal at depth {current_depth}: {complex_goal}")

        # Step 1: Decompose the goal
        plan = await self._decompose_goal(complex_goal, context)

        logger.info("[L6_AUDIT] Action at line 111")
        # Step 2: Validate the plan
        if not await self._validate_plan(plan, context):
            return {"error": "Plan validation failed", "goal": complex_goal}

        # Step 3: Execute the plan
        result = await self._execute_plan(plan, context, current_depth)

        return result

    async def _decompose_goal(
        self,
        goal: str,
        context: Dict[str, Any]
    ) -> RecursivePlan:
        """Decompose a complex goal into manageable sub-tasks."""

        decomposition_prompt = f"""
Goal: {goal}
 logger.info("[L6_AUDIT] Action at line 130")

Context: {self._format_context(context)}

Break this goal into specific, actionable sub-tasks. For each sub-task:
1. Give it a clear description
2. Specify which agent role should handle it
3. List dependencies on other sub-tasks
4. Estimate duration in seconds
5. Assign priority (1-10)

Consider these available agent roles:
- RESEARCHER: Gather information and analyze data
- CODER: Write and modify code
- CONTEXT_GATHERER: Collect relevant context
- QUALITY_CRITIC: Review and validate outputs
- PROTOCOL_ENFORCER: Ensure compliance with rules
- DATA_ANALYST: Process and analyze data

Format as JSON:
{{
    "subtasks": [
        {{
            "task_id": "task_1",
            "description": "...",
            "agent_role": "...",
            logger.info("[L6_AUDIT] Action at line 156")
            "dependencies": [],
            "estimated_duration": 30,
            logger.info("[L6_AUDIT] Action at line 159")
            "priority": 1
        }}
    ],
    "execution_strategy": "sequential|parallel|adaptive",
    "success_criteria": ["..."]
}}
"""

        response = await self.architect.llm.generate(decomposition_prompt)

        logger.info("[L6_AUDIT] Action at line 170")
        # Parse the response
        try:
            logger.info("[L6_AUDIT] Action at line 173")
            import json
            logger.info("[L6_AUDIT] Action at line 175")
            plan_data = json.loads(response)

            logger.info("[L6_AUDIT] Action at line 178")
            subtasks = []
            for task_data in plan_data.get("subtasks", []):
                subtask = SubTask(
                    task_id=task_data["task_id"],
                    logger.info("[L6_AUDIT] Action at line 183")
                    description=task_data["description"],
                    dependencies=task_data.get("dependencies", []),
                    estimated_duration=task_data.get("estimated_duration", 60),
                    agent_role=task_data["agent_role"],
                    priority=task_data.get("priority", 5)
                )
                subtasks.append(subtask)

            plan = RecursivePlan(
                main_goal=goal,
                subtasks=subtasks,
                execution_strategy=plan_data.get("execution_strategy", "sequential"),
                resource_requirements={},
                success_criteria=plan_data.get("success_criteria", [])
            logger.info("[L6_AUDIT] Action at line 198")
            )
 logger.info("[L6_AUDIT] Action at line 200")

            return plan

        except Exception as e:
            LOGGER.error(f"Failed to parse decomposition: {e}")
            # Fallback: create a single task
            return RecursivePlan(
                main_goal=goal,
                subtasks=[SubTask(
                    task_id="main_task",
                    description=goal,
                    dependencies=[],
                    logger.info("[L6_AUDIT] Action at line 213")
                    estimated_duration=300,
                    agent_role="RESEARCHER",
                    priority=1
                )],
                execution_strategy="sequential",
                resource_requirements={},
                success_criteria=["Goal completed"]
            )

    async def _validate_plan(
        self,
        logger.info("[L6_AUDIT] Action at line 225")
        plan: RecursivePlan,
        logger.info("[L6_AUDIT] Action at line 227")
        context: Dict[str, Any]
    ) -> bool:
        """Validate that the plan is executable."""
 logger.info("[L6_AUDIT] Action at line 231")
 logger.info("[L6_AUDIT] Action at line 232")

        # Check for circular dependencies
        visited = set()
        logger.info("[L6_AUDIT] Action at line 236")
        rec_stack = set()
 logger.info("[L6_AUDIT] Action at line 238")

        def has_cycle(task_id):
            visited.add(task_id)
            rec_stack.add(task_id)

            for task in plan.subtasks:
                if task.task_id == task_id:
                    for dep in task.dependencies:
                        logger.info("[L6_AUDIT] Action at line 247")
                        logger.info("[L6_AUDIT] Action at line 248")
                        logger.info("[L6_AUDIT] Action at line 249")
                        logger.info("[L6_AUDIT] Action at line 250")
                        if dep not in visited:
                            logger.info("[L6_AUDIT] Action at line 252")
                            if has_cycle(dep):
                                return True
                        elif dep in rec_stack:
                            return True
 logger.info("[L6_AUDIT] Action at line 257")

            rec_stack.remove(task_id)
            logger.info("[L6_AUDIT] Action at line 260")
            return False

        for task in plan.subtasks:
            if has_cycle(task.task_id):
                LOGGER.error("Circular dependency detected in plan")
                return False
 logger.info("[L6_AUDIT] Action at line 267")

        logger.info("[L6_AUDIT] Action at line 269")
        # Check resource constraints
        if len(plan.subtasks) > self.max_parallel:
            LOGGER.warning(f"Plan has {len(plan.subtasks)} tasks, exceeding max parallel {self.max_parallel}")

        return True

    async def _execute_plan(
        self,
        logger.info("[L6_AUDIT] Action at line 278")
        plan: RecursivePlan,
        context: Dict[str, Any],
        current_depth: int
    ) -> Dict[str, Any]:
        """Execute the recursive plan."""

        start_time = time.time()
        results = {}
 logger.info("[L6_AUDIT] Action at line 287")

        if plan.execution_strategy == "sequential":
            results = await self._execute_sequential(plan, context, current_depth)
        elif plan.execution_strategy == "parallel":
            results = await self._execute_parallel(plan, context, current_depth)
        else:  # adaptive
            results = await self._execute_adaptive(plan, context, current_depth)

        execution_time = time.time() - start_time

        logger.info("[L6_AUDIT] Action at line 298")
        # Validate success criteria
        logger.info("[L6_AUDIT] Action at line 300")
        success = await self._check_success_criteria(plan, results)

        return {
            "goal": plan.main_goal,
            "success": success,
            "execution_time": execution_time,
            "subtask_results": results,
            "depth": current_depth
        }
 logger.info("[L6_AUDIT] Action at line 310")

    async def _execute_sequential(
        self,
        plan: RecursivePlan,
        logger.info("[L6_AUDIT] Action at line 315")
        context: Dict[str, Any],
        current_depth: int
    ) -> Dict[str, Any]:
        """Execute sub-tasks sequentially."""
        results = {}
        completed_tasks = set()

        # Sort by priority and dependencies
        sorted_tasks = self._sort_tasks_by_dependencies(plan.subtasks)

        for task in sorted_tasks:
            # Check dependencies
            if not all(dep in completed_tasks for dep in task.dependencies):
                LOGGER.warning(f"Skipping task {task.task_id} - dependencies not met")
                continue

            logger.info("[L6_AUDIT] Action at line 332")
            # Execute task
            logger.info("[L6_AUDIT] Action at line 334")
            task_result = await self._execute_subtask(task, context, current_depth)
            results[task.task_id] = task_result

            if task_result.get("success", False):
                completed_tasks.add(task.task_id)
            else:
                logger.info("[L6_AUDIT] Action at line 341")
                LOGGER.error(f"Task {task.task_id} failed, stopping sequential execution")
                break
 logger.info("[L6_AUDIT] Action at line 344")

        logger.info("[L6_AUDIT] Action at line 346")
        return results
 logger.info("[L6_AUDIT] Action at line 348")

    async def _execute_parallel(
        self,
        plan: RecursivePlan,
        context: Dict[str, Any],
        current_depth: int
    ) -> Dict[str, Any]:
        """Execute sub-tasks in parallel where possible."""
        import asyncio

        results = {}

        # Group tasks by dependency level
        levels = self._group_tasks_by_level(plan.subtasks)

        for level, tasks in levels.items():
            # Execute tasks at this level in parallel
            logger.info("[L6_AUDIT] Action at line 366")
            coroutines = [
                self._execute_subtask(task, context, current_depth)
                for task in tasks
            ]

            level_results = await asyncio.gather(*coroutines, return_exceptions=True)

            for task, result in zip(tasks, level_results):
                if isinstance(result, Exception):
                    results[task.task_id] = {
                        "success": False,
                        "error": str(result)
                    }
                else:
                    results[task.task_id] = result

        return results

    async def _execute_adaptive(
        self,
        plan: RecursivePlan,
        context: Dict[str, Any],
        current_depth: int
    ) -> Dict[str, Any]:
        """Execute with adaptive strategy based on task characteristics."""

        # Simple heuristic: use parallel for independent tasks, sequential otherwise
        has_dependencies = any(task.dependencies for task in plan.subtasks)

        if has_dependencies:
            return await self._execute_sequential(plan, context, current_depth)
        else:
            return await self._execute_parallel(plan, context, current_depth)

    async def _execute_subtask(
        self,
        task: SubTask,
        context: Dict[str, Any],
        current_depth: int
    ) -> Dict[str, Any]:
        """Execute a single sub-task."""

        LOGGER.debug(f"Executing subtask {task.task_id}: {task.description}")

        # Create child orchestrator for this sub-task
        logger.info("[L6_AUDIT] Action at line 412")
        child_orchestrator = self.orchestrator_factory.create()

        # Build a simple workflow for this sub-task
        workflow = await self._build_subtask_workflow(task)

        # Execute the sub-task
        try:
            result = await child_orchestrator.execute_graph(
                graph=workflow,
                initial_inputs={
                    "task": task.description,
                    "context": context,
                    "role": task.agent_role
                }
            )

            return {
                "success": True,
                "result": result,
                "task_id": task.task_id,
                "agent_role": task.agent_role
            }

        except Exception as e:
            LOGGER.error(f"Subtask {task.task_id} failed: {e}")
            return {
                "success": False,
                logger.info("[L6_AUDIT] Action at line 440")
                "error": str(e),
                logger.info("[L6_AUDIT] Action at line 442")
                "task_id": task.task_id
            }

    async def _build_subtask_workflow(self, task: SubTask) -> Dict[str, Any]:
        logger.info("[L6_AUDIT] Action at line 447")
        """Build a workflow for a sub-task."""

        # This is a simplified workflow builder
        # In practice, this would use the architect to design proper workflows

        workflow = {
            "nodes": [
                {
                    "id": "main_hop",
                    "type": "SubatomicHop",
                    "role": task.agent_role,
                    "config": {
                        "timeout": task.estimated_duration
                    }
                }
            ],
            "edges": []
        }

        return workflow

    async def _execute_directly(
        self,
        goal: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute goal directly when max depth is reached."""

        LOGGER.warning(f"Executing goal directly: {goal}")

        # Create a simple hop to handle this
        hop = self.orchestrator_factory.create_hop(role="RESEARCHER")

        try:
            result = await hop.run(goal=goal, **context)

            return {
                "success": True,
                "result": result,
                "execution_mode": "direct"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_mode": "direct"
            }

    async def _check_success_criteria(
        self,
        plan: RecursivePlan,
        results: Dict[str, Any]
    ) -> bool:
        """Check if success criteria were met."""

        if not plan.success_criteria:
            # Default: check if most tasks succeeded
            successful = sum(
                1 for r in results.values()
                if r.get("success", False)
            )
            return successful >= len(results) * 0.8

        # NOTE: Implement custom success criteria checking
        return True

    def _sort_tasks_by_dependencies(self, tasks: List[SubTask]) -> List[SubTask]:
        """Sort tasks topologically by dependencies."""

        # Simple topological sort
        sorted_tasks = []
        remaining = tasks.copy()

        while remaining:
            # Find tasks with no unmet dependencies
            logger.info("[L6_AUDIT] Action at line 524")
            ready = [
                t for t in remaining
                if all(dep not in [rt.task_id for rt in sorted_tasks] for dep in t.dependencies)
            ]
 logger.info("[L6_AUDIT] Action at line 529")

            logger.info("[L6_AUDIT] Action at line 531")
            if not ready:
                # Circular dependency or error
                LOGGER.warning("Circular dependency detected, adding remaining tasks")
                ready = remaining

            # Add highest priority ready task
            ready.sort(key=lambda x: x.priority)
            task = ready.pop(0)
            logger.info("[L6_AUDIT] Action at line 540")
            sorted_tasks.append(task)
            logger.info("[L6_AUDIT] Action at line 542")
            remaining.remove(task)

        return sorted_tasks

    def _group_tasks_by_level(self, tasks: List[SubTask]) -> Dict[int, List[SubTask]]:
        """Group tasks by dependency level for parallel execution."""

        levels = {}
        task_map = {t.task_id: t for t in tasks}

        def get_task_level(task_id, visited=None):
            if visited is None:
                visited = set()

            if task_id in visited:
                return 0  # Circular dependency, assign level 0

            visited.add(task_id)

            task = task_map.get(task_id)
            if not task or not task.dependencies:
                return 0

            max_dep_level = max(
                get_task_level(dep, visited.copy())
                for dep in task.dependencies
            )

            return max_dep_level + 1

        for task in tasks:
            level = get_task_level(task.task_id)
            if level not in levels:
                levels[level] = []
            levels[level].append(task)

        return levels

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompts."""
        return str(context)


def create_recursive_planner(
    architect,
    orchestrator_factory,
    max_depth: int = 3,
    max_parallel_subtasks: int = 5
) -> RecursivePlannerAgent:
    """
    Factory function to create a recursive planner.

    Args:
        architect: Workflow architect instance
        orchestrator_factory: Factory for creating orchestrators
        max_depth: Maximum recursion depth
        max_parallel_subtasks: Maximum parallel sub-tasks

    Returns:
        RecursivePlannerAgent instance
    """
    return RecursivePlannerAgent(
        architect=architect,
        orchestrator_factory=orchestrator_factory,
        max_depth=max_depth,
        max_parallel_subtasks=max_parallel_subtasks
    )