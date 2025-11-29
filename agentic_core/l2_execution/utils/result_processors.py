#!/usr/bin/env python3
"""
Result Processors
Section 4: DAG Orchestration - Result processing and transformation utilities
"""

from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ResultProcessor:
    """Base class for processing execution results"""
    
    def __init__(self, processor_name: str, config: Optional[Dict[str, Any]] = None):
        self.processor_name = processor_name
        self.config = config or {}
    
    def process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process execution result"""
        try:
            processed_result = self._process_result(result)
            return {
                "original_result": result,
                "processed_result": processed_result,
                "processor": self.processor_name
            }
        except Exception as e:
            logger.error(f"Result processing failed: {e}")
            return {"error": str(e), "processor": self.processor_name}
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses to implement specific processing logic"""
        return result

class JSONResultProcessor(ResultProcessor):
    """Processor for JSON-formatted results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("json_processor", config)
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON result with formatting"""
        import json
        return {
            "formatted": json.dumps(result, indent=2),
            "keys": list(result.keys()),
            "size": len(str(result))
        }

class ValidationResultProcessor(ResultProcessor):
    """Processor for validation results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("validation_processor", config)
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process validation result with status analysis"""
        is_valid = result.get("success", False)
        return {
            "validation_status": "passed" if is_valid else "failed",
            "error_count": len([k for k, v in result.items() if k.startswith("error")]),
            "warnings": [v for k, v in result.items() if k.startswith("warning")]
        }

class AggregationResultProcessor(ResultProcessor):
    """Processor for aggregating multiple results"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("aggregation_processor", config)
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from multiple executions"""
        results = result.get("results", [])
        if not results:
            return {"aggregated": [], "count": 0}
        
        return {
            "aggregated": results,
            "count": len(results),
            "summary": f"Processed {len(results)} results"
        }

# Re-export components
__all__ = [
    'ResultProcessor', 'JSONResultProcessor', 'ValidationResultProcessor',
    'AggregationResultProcessor'
]





