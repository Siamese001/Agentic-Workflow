"""
use_tools_use_a_tool.py - Shared Execution Module.

This module provides the core implementation for UseToolsUseATool, handling
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

class UseToolsUseATool:
    """
    Executor for shared use_tools_use_a_tool operations.
    
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
        """Internal logic for tool usage execution."""
        # Initialize result
        result = {
            "tool_result": None,
            "tool_used": None,
            "execution_status": "pending",
            "parameters": {},
            "output": None,
            "error": None
        }
        
        # Parse tool request
        if isinstance(data, dict):
            tool_request = data
        else:
            # Convert to tool request format
            tool_request = {"tool_name": str(data), "parameters": {}}
        
        # Extract tool information
        tool_name = tool_request.get("tool_name", "unknown")
        parameters = tool_request.get("parameters", {})
        
        result["tool_used"] = tool_name
        result["parameters"] = parameters
        
        # Execute tool based on name
        try:
            if tool_name == "search":
                output = self._execute_search(parameters, context)
            elif tool_name == "calculate":
                output = self._execute_calculate(parameters, context)
            elif tool_name == "validate":
                output = self._execute_validate(parameters, context)
            elif tool_name == "transform":
                output = self._execute_transform(parameters, context)
            else:
                output = self._execute_generic_tool(tool_name, parameters, context)
            
            result["output"] = output
            result["execution_status"] = "completed"
            result["tool_result"] = output
            
        except Exception as e:
            result["error"] = str(e)
            result["execution_status"] = "failed"
            self._logger.error(f"Tool execution failed: {e}")
        
        return result
    
    def _execute_search(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute search tool."""
        query = parameters.get("query", "")
        limit = parameters.get("limit", 10)
        
        # Simulate search results
        results = [
            {"id": i, "content": f"Result {i} for query: {query}", "score": 0.9 - i * 0.1}
            for i in range(min(limit, 5))
        ]
        
        return {
            "tool": "search",
            "query": query,
            "results": results,
            "total_found": len(results)
        }
    
    def _execute_calculate(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute calculation tool."""
        operation = parameters.get("operation", "add")
        operands = parameters.get("operands", [])
        
        if operation == "add":
            result = sum(operands)
        elif operation == "multiply":
            result = 1
            for num in operands:
                result *= num
        elif operation == "average":
            result = sum(operands) / len(operands) if operands else 0
        else:
            result = None
        
        return {
            "tool": "calculate",
            "operation": operation,
            "operands": operands,
            "result": result
        }
    
    def _execute_validate(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute validation tool."""
        data_to_validate = parameters.get("data", {})
        rules = parameters.get("rules", {})
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Simple validation logic
        for field, rule in rules.items():
            if field in data_to_validate:
                value = data_to_validate[field]
                if rule.get("required") and not value:
                    validation_result["errors"].append(f"Field {field} is required")
                    validation_result["is_valid"] = False
                
                if rule.get("type") and not isinstance(value, rule["type"]):
                    validation_result["errors"].append(
                        f"Field {field} must be of type {rule['type'].__name__}"
                    )
                    validation_result["is_valid"] = False
        
        return {
            "tool": "validate",
            "data": data_to_validate,
            "validation": validation_result
        }
    
    def _execute_transform(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute transformation tool."""
        data = parameters.get("data", {})
        transformation = parameters.get("transformation", "identity")
        
        if transformation == "uppercase" and isinstance(data, str):
            result = data.upper()
        elif transformation == "lowercase" and isinstance(data, str):
            result = data.lower()
        elif transformation == "keys" and isinstance(data, dict):
            result = list(data.keys())
        elif transformation == "values" and isinstance(data, dict):
            result = list(data.values())
        else:
            result = data
        
        return {
            "tool": "transform",
            "transformation": transformation,
            "input": data,
            "output": result
        }
    
    def _execute_generic_tool(self, tool_name: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Execute generic tool fallback."""
        return {
            "tool": tool_name,
            "parameters": parameters,
            "message": f"Executed generic tool: {tool_name}",
            "status": "completed"
        }

def run_process(data: Union[str, int, float, bool, List, Dict]) -> ExecutionResult:
    """Module-level entry point."""
    executor = UseToolsUseATool()
    return executor.process(data)
