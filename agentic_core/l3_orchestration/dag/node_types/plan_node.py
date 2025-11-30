"""
Plan Node Implementation for DAG Orchestration
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NodeStatus(Enum):
    """Status of a plan node"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NodeResult:
    """Result from node execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PlanNode:
    """A node in the execution plan DAG"""
    
    def __init__(self, node_id: str, node_type: str, description: str = ""):
        self.node_id = node_id
        self.node_type = node_type
        self.description = description
        self.status = NodeStatus.PENDING
        self.dependencies: List[str] = []
        self.result: Optional[NodeResult] = None
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_dependency(self, dependency_node_id: str):
        """Add a dependency to this node"""
        if dependency_node_id not in self.dependencies:
            self.dependencies.append(dependency_node_id)
            self.updated_at = datetime.now()
    
    def remove_dependency(self, dependency_node_id: str):
        """Remove a dependency from this node"""
        if dependency_node_id in self.dependencies:
            self.dependencies.remove(dependency_node_id)
            self.updated_at = datetime.now()
    
    def set_status(self, status: NodeStatus):
        """Set the status of this node"""
        self.status = status
        self.updated_at = datetime.now()
    
    def set_result(self, result: NodeResult):
        """Set the result of this node execution"""
        self.result = result
        if result.success:
            self.status = NodeStatus.COMPLETED
        else:
            self.status = NodeStatus.FAILED
        self.updated_at = datetime.now()
    
    def is_ready(self, completed_nodes: List[str]) -> bool:
        """Check if this node is ready to execute (all dependencies completed)"""
        return (
            self.status == NodeStatus.PENDING and
            all(dep in completed_nodes for dep in self.dependencies)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "result": self.result.__dict__ if self.result else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __str__(self):
        return f"PlanNode(id={self.node_id}, type={self.node_type}, status={self.status.value})"
    
    def __repr__(self):
        return self.__str__()
