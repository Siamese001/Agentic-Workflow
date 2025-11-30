"""
Controller Implementation for Orchestration
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ControllerStatus(Enum):
    """Status of the controller"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ControllerState:
    """State of the controller"""
    status: ControllerStatus
    current_task: str
    progress: float
    metadata: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Controller:
    """Main orchestration controller for managing complex workflows"""

    def __init__(self, name: str):
        self.name = name
        self.status = ControllerStatus.IDLE
        self.current_task = ""
        self.progress = 0.0
        self.metadata = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.failed_tasks: List[Dict[str, Any]] = []
        self.task_handlers: Dict[str, Callable] = {}
        self.execution_history: List[ControllerState] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_task_handler(self, task_type: str, handler: Callable):
        """Add a handler for a specific task type"""
        self.task_handlers[task_type] = handler

    def enqueue_task(self, task: Dict[str, Any]) -> bool:
        """Add a task to the execution queue"""
        required_fields = ["task_id", "task_type", "priority"]
        if not all(field in task for field in required_fields):
            return False

        # Insert task based on priority (lower number = higher priority)
        insert_index = 0
        for i, queued_task in enumerate(self.task_queue):
            if task["priority"] < queued_task["priority"]:
                insert_index = i
                break
            insert_index = i + 1

        self.task_queue.insert(insert_index, task)
        self.updated_at = datetime.now()
        return True

    def dequeue_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task from the queue"""
        if self.task_queue:
            return self.task_queue.pop(0)
        return None

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task_type = task.get("task_type")
        task_id = task.get("task_id")

        if task_type not in self.task_handlers:
            result = {
                "success": False,
                "error": f"No handler for task type: {task_type}",
                "task_id": task_id
            }
        else:
            try:
                handler = self.task_handlers[task_type]
                task_result = handler(task.get("parameters", {}))
                result = {
                    "success": True,
                    "result": task_result,
                    "task_id": task_id
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e),
                    "task_id": task_id
                }

        return result

    def run_next_task(self) -> Optional[Dict[str, Any]]:
        """Execute the next task in the queue"""
        if not self.task_queue:
            return None

        task = self.dequeue_task()
        self.current_task = task["task_id"]
        self.status = ControllerStatus.RUNNING

        # Record state change
        state = ControllerState(
            status=self.status,
            current_task=self.current_task,
            progress=self.progress,
            metadata=self.metadata.copy()
        )
        self.execution_history.append(state)

        # Execute task
        result = self.execute_task(task)

        # Update task lists
        if result["success"]:
            self.completed_tasks.append(result)
        else:
            self.failed_tasks.append(result)

        # Update progress
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks) + len(self.task_queue)
        if total_tasks > 0:
            self.progress = len(self.completed_tasks) / total_tasks

        # Update state
        if not self.task_queue:
            self.status = ControllerStatus.IDLE
            self.current_task = ""

        self.updated_at = datetime.now()
        return result

    def run_all_tasks(self) -> Dict[str, Any]:
        """Execute all tasks in the queue"""
        if not self.task_queue:
            return {"message": "No tasks to execute"}

        initial_task_count = len(self.task_queue)
        results = []

        while self.task_queue:
            result = self.run_next_task()
            if result:
                results.append(result)

        return {
            "total_tasks": initial_task_count,
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "results": results,
            "success_rate": len(self.completed_tasks) / initial_task_count if initial_task_count > 0 else 0
        }

    def pause(self):
        """Pause the controller"""
        if self.status == ControllerStatus.RUNNING:
            self.status = ControllerStatus.PAUSED
            self.updated_at = datetime.now()

    def resume(self):
        """Resume the controller"""
        if self.status == ControllerStatus.PAUSED:
            self.status = ControllerStatus.RUNNING
            self.updated_at = datetime.now()

    def stop(self):
        """Stop the controller and clear the queue"""
        self.status = ControllerStatus.IDLE
        self.current_task = ""
        self.progress = 0.0
        self.task_queue.clear()
        self.updated_at = datetime.now()

    def reset(self):
        """Reset the controller to initial state"""
        self.stop()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.execution_history.clear()
        self.metadata.clear()
        self.updated_at = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        """Get current controller status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task,
            "progress": self.progress,
            "queue_length": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "available_handlers": list(self.task_handlers.keys()),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def get_task_history(self) -> Dict[str, Any]:
        """Get history of executed tasks"""
        return {
            "completed": self.completed_tasks.copy(),
            "failed": self.failed_tasks.copy(),
            "execution_states": [state.__dict__ for state in self.execution_history]
        }

    def set_metadata(self, key: str, value: Any):
        """Set metadata"""
        self.metadata[key] = value
        self.updated_at = datetime.now()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata"""
        return self.metadata.get(key, default)

    def __str__(self):
        return f"Controller(name='{self.name}', status={self.status.value}, queue={len(self.task_queue)})"

    def __repr__(self):
        return self.__str__()
