# LIC Task Router for L3 orchestration
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Task type enumeration"""
    CONTACT_RESEARCH = "contact_research"
    MESSAGE_GENERATION = "message_generation"
    COMPANY_ANALYSIS = "company_analysis"
    OUTREACH_COORDINATION = "outreach_coordination"

@dataclass
class RoutingDecision:
    """Task routing decision"""
    task_id: str = ""
    task_type: TaskType = TaskType.CONTACT_RESEARCH
    executor_id: str = ""
    priority: int = 5
    estimated_duration: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class LICTaskRouter:
    """Task router for outreach orchestration"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.executor_registry = {}
        self.routing_rules = {}
        self.task_history = {}

    def register_executor(self, executor_id: str, task_types: List[TaskType],
                          capacity: int = 10) -> None:
        """Register executor for specific task types"""
        self.executor_registry[executor_id] = {
            "task_types": task_types,
            "capacity": capacity,
            "current_load": 0
        }

    def route_task(self, task_data: Dict[str, Any], task_type: TaskType = None) -> RoutingDecision:
        """Route task to appropriate executor"""
        task_id = task_data.get("task_id", f"task_{len(self.task_history)}")

        if task_type is None:
            task_type = self._infer_task_type(task_data)

        # Find available executor
        executor_id = self._find_best_executor(task_type)

        decision = RoutingDecision(
            task_id=task_id,
            task_type=task_type,
            executor_id=executor_id,
            priority=task_data.get("priority", 5),
            estimated_duration=self._estimate_duration(task_type, task_data),
            metadata={"routed_at": "now"}
        )

        self.task_history[task_id] = decision
        return decision

    def _infer_task_type(self, task_data: Dict[str, Any]) -> TaskType:
        """Infer task type from data"""
        if "message" in task_data or "content" in task_data:
            return TaskType.MESSAGE_GENERATION
        elif "company" in task_data:
            return TaskType.COMPANY_ANALYSIS
        elif "contact" in task_data:
            return TaskType.CONTACT_RESEARCH
        else:
            return TaskType.OUTREACH_COORDINATION

    def _find_best_executor(self, task_type: TaskType) -> str:
        """Find best executor for task type"""
        available_executors = [
            executor_id for executor_id, info in self.executor_registry.items()
            if task_type in info["task_types"] and info["current_load"] < info["capacity"]
        ]

        return available_executors[0] if available_executors else "default_executor"

    def _estimate_duration(self, task_type: TaskType, task_data: Dict[str, Any]) -> float:
        """Estimate task duration in seconds"""
        duration_map = {
            TaskType.CONTACT_RESEARCH: 2.0,
            TaskType.MESSAGE_GENERATION: 1.5,
            TaskType.COMPANY_ANALYSIS: 3.0,
            TaskType.OUTREACH_COORDINATION: 1.0
        }
        return duration_map.get(task_type, 2.0)

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            "total_tasks_routed": len(self.task_history),
            "registered_executors": len(self.executor_registry),
            "task_type_distribution": {
                task_type.value: len([t for t in self.task_history.values() if t.task_type == task_type])
                for task_type in TaskType
            }
        }
