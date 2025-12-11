"""
use_tools_routing_retry_task.py - Shared Execution Module.

This module provides the core implementation for UseToolsRoutingRetryTask, handling
standardized execution flows, error management, and context propagation
within the shared application layer.
"""

import logging
from typing import Dict, Optional, Any, Union, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Standardized operation result container."""
    success: bool
    data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class UseToolsRoutingRetryTask:
    """
    Executor for shared use_tools_routing_retry_task operations.
    
    Ensures consistent handling of configuration context and error boundaries
    across the sovereign domain.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def process(self, payload: Union[str, int, float, bool, List, Dict], context: Optional[Dict] = None) -> ExecutionResult:
        """
        Execute the primary logic for this module.
        
        Args:
            payload: The input data to process
            context: Optional execution context
            
        Returns:
            ExecutionResult indicating success or failure
        """
        try:
            self._logger.info("Starting processing execution")
            result = self._execute_logic(payload, context)
            return ExecutionResult(success=True, data=result)
        except (ValueError, TypeError, KeyError) as e:
            self._logger.error(f"Validation error during processing: {e}")
            return ExecutionResult(success=False, error_message=str(e))
        except Exception as e:
            self._logger.error(f"Unexpected system error: {e}", exc_info=True)
            return ExecutionResult(success=False, error_message="Internal System Error")

    def _execute_logic(self, data: Union[str, int, float, bool, List, Dict], context: Optional[Dict]) -> Union[str, int, float, bool, List, Dict]:
        """Internal logic for routing and retry task execution."""
        # Initialize result
        result = {
            "routing_decision": None,
            "retry_count": 0,
            "max_retries": self.config.get("max_retries", 3),
            "task_status": "pending",
            "execution_history": [],
            "final_result": None,
            "error": None
        }
        
        # Parse task request
        if isinstance(data, dict):
            task_request = data
        else:
            task_request = {"task": str(data), "parameters": {}}
        
        # Extract task information
        task_type = task_request.get("task_type", "unknown")
        parameters = task_request.get("parameters", {})
        priority = task_request.get("priority", "normal")
        
        # Determine routing
        routing_decision = self._determine_routing(task_type, parameters, priority)
        result["routing_decision"] = routing_decision
        
        # Execute with retry logic
        retry_count = 0
        success = False
        last_error = None
        
        while retry_count <= result["max_retries"] and not success:
            try:
                execution_result = self._execute_task(
                    task_type, parameters, routing_decision, context
                )
                
                # Record execution
                execution_record = {
                    "attempt": retry_count + 1,
                    "timestamp": self._get_timestamp(),
                    "route": routing_decision,
                    "success": execution_result.get("success", False),
                    "result": execution_result
                }
                result["execution_history"].append(execution_record)
                
                if execution_result.get("success", False):
                    result["final_result"] = execution_result
                    result["task_status"] = "completed"
                    success = True
                else:
                    last_error = execution_result.get("error", "Unknown error")
                    retry_count += 1
                    
                    # Check if we should retry
                    if retry_count <= result["max_retries"]:
                        if self._should_retry(task_type, last_error, retry_count):
                            result["task_status"] = f"retrying (attempt {retry_count + 1})"
                            # Apply backoff delay
                            delay = self._calculate_backoff_delay(retry_count)
                            self._logger.info(f"Retrying task after {delay}ms delay")
                        else:
                            break
                            
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                result["execution_history"].append({
                    "attempt": retry_count,
                    "timestamp": self._get_timestamp(),
                    "route": routing_decision,
                    "success": False,
                    "error": last_error
                })
        
        # Handle final status
        if not success:
            result["task_status"] = "failed"
            result["error"] = last_error
            result["retry_count"] = retry_count
        
        return result
    
    def _determine_routing(self, task_type: str, parameters: Dict, priority: str) -> Dict:
        """Determine the best routing for the task."""
        routing_rules = self.config.get("routing_rules", {})
        
        # Check for specific routing rules
        if task_type in routing_rules:
            route = routing_rules[task_type]
        elif priority == "high":
            route = {"service": "fast_lane", "endpoint": "/high_priority"}
        elif priority == "low":
            route = {"service": "batch_processor", "endpoint": "/low_priority"}
        else:
            route = {"service": "default", "endpoint": "/standard"}
        
        # Add task-specific parameters to route
        route["task_type"] = task_type
        route["priority"] = priority
        route["estimated_duration"] = self._estimate_task_duration(task_type, parameters)
        
        return route
    
    def _execute_task(self, task_type: str, parameters: Dict, route: Dict, context: Optional[Dict]) -> Dict:
        """Execute the task on the determined route."""
        # Simulate task execution based on type
        if task_type == "search":
            return self._execute_search_task(parameters, context)
        elif task_type == "calculate":
            return self._execute_calculate_task(parameters, context)
        elif task_type == "validate":
            return self._execute_validate_task(parameters, context)
        elif task_type == "transform":
            return self._execute_transform_task(parameters, context)
        else:
            return self._execute_generic_task(task_type, parameters, context)
    
    def _execute_search_task(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute search task."""
        # Simulate potential failure for retry demonstration
        import random
        if random.random() < 0.3:  # 30% chance of failure
            return {"success": False, "error": "Search service temporarily unavailable"}
        
        return {
            "success": True,
            "results": [{"id": 1, "content": "Search result"}],
            "count": 1
        }
    
    def _execute_calculate_task(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute calculation task."""
        try:
            operation = parameters.get("operation", "add")
            operands = parameters.get("operands", [1, 2, 3])
            
            if operation == "add":
                result = sum(operands)
            else:
                result = 0
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_validate_task(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute validation task."""
        data = parameters.get("data", {})
        is_valid = isinstance(data, dict) and "required_field" in data
        
        return {
            "success": True,
            "is_valid": is_valid,
            "errors": [] if is_valid else ["Missing required field"]
        }
    
    def _execute_transform_task(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute transformation task."""
        data = parameters.get("data", "")
        transformed = data.upper() if isinstance(data, str) else data
        
        return {
            "success": True,
            "transformed_data": transformed
        }
    
    def _execute_generic_task(self, task_type: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute generic task."""
        return {
            "success": True,
            "task_type": task_type,
            "parameters": parameters,
            "message": f"Executed {task_type} task"
        }
    
    def _should_retry(self, task_type: str, error: str, retry_count: int) -> bool:
        """Determine if task should be retried."""
        # Don't retry certain errors
        non_retryable_errors = [
            "authentication failed",
            "invalid parameters",
            "access denied"
        ]
        
        if any(err in error.lower() for err in non_retryable_errors):
            return False
        
        # Check retry limit
        max_retries = self.config.get("max_retries", 3)
        if retry_count >= max_retries:
            return False
        
        # Task-specific retry logic
        retry_config = self.config.get("retry_config", {})
        if task_type in retry_config:
            return retry_count < retry_config[task_type].get("max_retries", max_retries)
        
        return True
    
    def _calculate_backoff_delay(self, retry_count: int) -> int:
        """Calculate exponential backoff delay in milliseconds."""
        base_delay = self.config.get("base_delay_ms", 100)
        max_delay = self.config.get("max_delay_ms", 5000)
        
        delay = base_delay * (2 ** retry_count)
        return min(delay, max_delay)
    
    def _estimate_task_duration(self, task_type: str, parameters: Dict) -> float:
        """Estimate task duration in seconds."""
        duration_map = {
            "search": 0.5,
            "calculate": 0.1,
            "validate": 0.2,
            "transform": 0.3
        }
        return duration_map.get(task_type, 1.0)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

def run_process(data: Union[str, int, float, bool, List, Dict]) -> ExecutionResult:
    """Module-level entry point."""
    executor = UseToolsRoutingRetryTask()
    return executor.process(data)
