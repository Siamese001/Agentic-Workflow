#!/usr/bin/env python3
"""
Execution Helpers
Section 4: DAG Orchestration - Helper functions for L2 execution operations
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ExecutionHelper:
    """Helper class for execution operations"""
    
    @staticmethod
    def format_execution_result(result: Dict[str, Any], format_type: str = "json") -> str:
        """Format execution result according to specified type"""
        if format_type == "json":
            import json
            return json.dumps(result, indent=2)
        elif format_type == "summary":
            return f"Execution completed with {len(result)} items"
        else:
            return str(result)
    
    @staticmethod
    def validate_tool_input(input_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate tool input data against required fields"""
        for field in required_fields:
            if field not in input_data:
                logger.error(f"Missing required field: {field}")
                return False
        return True
    
    @staticmethod
    def sanitize_output(output: Any) -> Dict[str, Any]:
        """Sanitize execution output for safe handling"""
        if isinstance(output, dict):
            return output
        else:
            return {"result": str(output)}

def format_execution_result(result: Dict[str, Any], format_type: str = "json") -> str:
    """Format execution result according to specified type"""
    return ExecutionHelper.format_execution_result(result, format_type)

def validate_tool_input(input_data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate tool input data against required fields"""
    return ExecutionHelper.validate_tool_input(input_data, required_fields)

# Re-export components
__all__ = [
    'ExecutionHelper', 'format_execution_result', 'validate_tool_input'
]





