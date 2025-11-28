from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class KNodeState:
    node_name: str
    status: str
    output: Any
    timestamp: datetime
    execution_time_ms: int
    error_message: Optional[str] = None

@dataclass
class ViolationState:
    error_code: str
    severity: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

@dataclass
class LICState:
    message_id: str
    message_type: str
    recipient_type: str
    sender_info: Dict[str, Any]
    message_context: Dict[str, Any]
    
    k_node_states: Dict[str, KNodeState] = field(default_factory=dict)
    violations: List[ViolationState] = field(default_factory=list)
    
    pipeline_start_time: datetime = field(default_factory=datetime.now)
    pipeline_end_time: Optional[datetime] = None
    pipeline_status: str = "INITIALIZED"
    
    final_message: str = ""
    final_validation_status: str = "PENDING"
    
    def add_k_node_state(self, node_name: str, status: str, output: Any, execution_time_ms: int, error_message: Optional[str] = None):
        self.k_node_states[node_name] = KNodeState(
            node_name=node_name,
            status=status,
            output=output,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
    
    def add_violation(self, error_code: str, severity: str, description: str):
        violation = ViolationState(
            error_code=error_code,
            severity=severity,
            description=description,
            timestamp=datetime.now()
        )
        self.violations.append(violation)
    
    def resolve_violation(self, error_code: str):
        for violation in self.violations:
            if violation.error_code == error_code and not violation.resolved:
                violation.resolved = True
                violation.resolution_timestamp = datetime.now()
                break
    
    def get_k_node_output(self, node_name: str) -> Any:
        state = self.k_node_states.get(node_name)
        return state.output if state else None
    
    def get_k_node_status(self, node_name: str) -> str:
        state = self.k_node_states.get(node_name)
        return state.status if state else "NOT_EXECUTED"
    
    def has_blocking_violations(self) -> bool:
        return any(v.severity == "BLOCKING" and not v.resolved for v in self.violations)
    
    def get_active_violations(self) -> List[ViolationState]:
        return [v for v in self.violations if not v.resolved]
    
    def mark_pipeline_complete(self, success: bool, final_message: str = "", validation_status: str = "FAILED"):
        self.pipeline_end_time = datetime.now()
        self.pipeline_status = "SUCCESS" if success else "FAILED"
        self.final_message = final_message
        self.final_validation_status = validation_status
    
    def get_execution_summary(self) -> Dict[str, Any]:
        successful_nodes = sum(1 for state in self.k_node_states.values() if state.status == "SUCCESS")
        failed_nodes = sum(1 for state in self.k_node_states.values() if state.status == "FAILED")
        skipped_nodes = sum(1 for state in self.k_node_states.values() if state.status == "SKIPPED")
        
        total_execution_time = sum(state.execution_time_ms for state in self.k_node_states.values())
        
        pipeline_duration = None
        if self.pipeline_end_time:
            pipeline_duration = int((self.pipeline_end_time - self.pipeline_start_time).total_seconds() * 1000)
        
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "recipient_type": self.recipient_type,
            "pipeline_status": self.pipeline_status,
            "successful_nodes": successful_nodes,
            "failed_nodes": failed_nodes,
            "skipped_nodes": skipped_nodes,
            "total_violations": len(self.violations),
            "active_violations": len(self.get_active_violations()),
            "has_blocking_violations": self.has_blocking_violations(),
            "total_execution_time_ms": total_execution_time,
            "pipeline_duration_ms": pipeline_duration,
            "final_validation_status": self.final_validation_status
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "recipient_type": self.recipient_type,
            "sender_info": self.sender_info,
            "message_context": self.message_context,
            "k_node_states": {
                name: {
                    "node_name": state.node_name,
                    "status": state.status,
                    "timestamp": state.timestamp.isoformat(),
                    "execution_time_ms": state.execution_time_ms,
                    "error_message": state.error_message
                }
                for name, state in self.k_node_states.items()
            },
            "violations": [
                {
                    "error_code": v.error_code,
                    "severity": v.severity,
                    "description": v.description,
                    "timestamp": v.timestamp.isoformat(),
                    "resolved": v.resolved,
                    "resolution_timestamp": v.resolution_timestamp.isoformat() if v.resolution_timestamp else None
                }
                for v in self.violations
            ],
            "pipeline_start_time": self.pipeline_start_time.isoformat(),
            "pipeline_end_time": self.pipeline_end_time.isoformat() if self.pipeline_end_time else None,
            "pipeline_status": self.pipeline_status,
            "final_message": self.final_message,
            "final_validation_status": self.final_validation_status
        }
