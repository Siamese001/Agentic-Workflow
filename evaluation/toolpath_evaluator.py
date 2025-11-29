#!/usr/bin/env python3
"""
Toolpath Evaluator Implementation
Evaluates tool execution paths and performance metrics
"""

import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class EvaluationStatus(Enum):
    """Evaluation status types"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class ToolExecutionMetrics:
    """Metrics for tool execution"""
    tool_name: str
    execution_time_ms: int
    success: bool
    error_message: Optional[str] = None
    input_size: int = 0
    output_size: int = 0
    memory_usage_mb: float = 0.0

@dataclass
class ToolpathEvaluationResult:
    """Result of toolpath evaluation"""
    toolpath_id: str
    status: EvaluationStatus
    total_tools: int
    successful_tools: int
    failed_tools: int
    total_execution_time_ms: int
    tool_metrics: List[ToolExecutionMetrics]
    score: float  # 0.0 to 1.0
    recommendations: List[str]
    timestamp: str

class ToolpathEvaluator:
    """Evaluates tool execution paths and performance"""
    
    def __init__(self):
        self.evaluation_thresholds = {
            'max_execution_time_ms': 5000,  # 5 seconds per tool
            'max_total_time_ms': 30000,     # 30 seconds total
            'min_success_rate': 0.8,        # 80% of tools must succeed
            'max_memory_usage_mb': 512.0,   # 512MB per tool
            'min_score_threshold': 0.7      # 70% overall score
        }
        
        # Performance baselines for common tools
        self.tool_baselines = {
            'draft_executor': {'max_time_ms': 2000, 'expected_success_rate': 0.95},
            'model_call': {'max_time_ms': 3000, 'expected_success_rate': 0.9},
            'file_operation': {'max_time_ms': 500, 'expected_success_rate': 0.99},
            'data_processing': {'max_time_ms': 1500, 'expected_success_rate': 0.85}
        }
    
    def evaluate_toolpath(self, toolpath: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> ToolpathEvaluationResult:
        """Evaluate a complete toolpath execution"""
        start_time = time.time()
        toolpath_id = self._generate_toolpath_id(toolpath)
        
        tool_metrics = []
        successful_tools = 0
        failed_tools = 0
        
        for tool_config in toolpath:
            metric = self._evaluate_single_tool(tool_config, context)
            tool_metrics.append(metric)
            
            if metric.success:
                successful_tools += 1
            else:
                failed_tools += 1
        
        total_execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Calculate overall score
        score = self._calculate_score(tool_metrics, total_execution_time_ms)
        
        # Determine status
        status = self._determine_status(score, successful_tools, len(toolpath), total_execution_time_ms)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(tool_metrics, score)
        
        result = ToolpathEvaluationResult(
            toolpath_id=toolpath_id,
            status=status,
            total_tools=len(toolpath),
            successful_tools=successful_tools,
            failed_tools=failed_tools,
            total_execution_time_ms=total_execution_time_ms,
            tool_metrics=tool_metrics,
            score=score,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        # Log evaluation result
        logger.info(f"Toolpath evaluation completed: {toolpath_id} - Score: {score:.2f}, Status: {status.value}")
        
        return result
    
    def _evaluate_single_tool(self, tool_config: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolExecutionMetrics:
        """Evaluate a single tool execution"""
        tool_name = tool_config.get('tool_name', 'unknown')
        tool_params = tool_config.get('parameters', {})
        
        start_time = time.time()
        
        try:
            # Simulate tool execution based on tool type
            execution_result = self._simulate_tool_execution(tool_name, tool_params)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Check if execution meets performance thresholds
            baseline = self.tool_baselines.get(tool_name, {'max_time_ms': 5000, 'expected_success_rate': 0.8})
            
            success = (
                execution_result['success'] and
                execution_time_ms <= baseline['max_time_ms'] and
                execution_result['memory_usage_mb'] <= self.evaluation_thresholds['max_memory_usage_mb']
            )
            
            error_message = None if success else execution_result.get('error_message', 'Performance threshold exceeded')
            
            return ToolExecutionMetrics(
                tool_name=tool_name,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                input_size=len(str(tool_params)),
                output_size=len(str(execution_result.get('output', ''))),
                memory_usage_mb=execution_result['memory_usage_mb']
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return ToolExecutionMetrics(
                tool_name=tool_name,
                execution_time_ms=execution_time_ms,
                success=False,
                error_message=str(e),
                input_size=len(str(tool_params)),
                output_size=0,
                memory_usage_mb=0.0
            )
    
    def _simulate_tool_execution(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate tool execution for evaluation purposes"""
        # Simulate different tool execution patterns
        if tool_name == 'draft_executor':
            time.sleep(0.1)  # Simulate drafting time
            return {
                'success': True,
                'output': 'Draft content generated',
                'memory_usage_mb': 45.2,
                'error_message': None
            }
        elif tool_name == 'model_call':
            time.sleep(0.2)  # Simulate model inference time
            return {
                'success': True,
                'output': 'Model response generated',
                'memory_usage_mb': 128.5,
                'error_message': None
            }
        elif tool_name == 'file_operation':
            time.sleep(0.05)  # Simulate file I/O
            return {
                'success': True,
                'output': 'File operation completed',
                'memory_usage_mb': 12.3,
                'error_message': None
            }
        elif tool_name == 'data_processing':
            time.sleep(0.15)  # Simulate data processing
            return {
                'success': True,
                'output': 'Data processed successfully',
                'memory_usage_mb': 89.7,
                'error_message': None
            }
        else:
            # Unknown tool - simulate with default behavior
            time.sleep(0.1)
            return {
                'success': True,
                'output': f'Tool {tool_name} executed',
                'memory_usage_mb': 25.0,
                'error_message': None
            }
    
    def _generate_toolpath_id(self, toolpath: List[Dict[str, Any]]) -> str:
        """Generate unique ID for toolpath"""
        toolpath_str = json.dumps(toolpath, sort_keys=True)
        return hashlib.md5(toolpath_str.encode()).hexdigest()[:12]
    
    def _calculate_score(self, tool_metrics: List[ToolExecutionMetrics], total_time_ms: int) -> float:
        """Calculate overall evaluation score"""
        if not tool_metrics:
            return 0.0
        
        # Success rate component (40% of score)
        successful_tools = sum(1 for m in tool_metrics if m.success)
        success_rate = successful_tools / len(tool_metrics)
        success_score = success_rate * 0.4
        
        # Performance component (30% of score)
        avg_execution_time = sum(m.execution_time_ms for m in tool_metrics) / len(tool_metrics)
        performance_score = max(0, (1.0 - (avg_execution_time / self.evaluation_thresholds['max_execution_time_ms']))) * 0.3
        
        # Memory efficiency component (20% of score)
        avg_memory_usage = sum(m.memory_usage_mb for m in tool_metrics) / len(tool_metrics)
        memory_score = max(0, (1.0 - (avg_memory_usage / self.evaluation_thresholds['max_memory_usage_mb']))) * 0.2
        
        # Total time component (10% of score)
        time_score = max(0, (1.0 - (total_time_ms / self.evaluation_thresholds['max_total_time_ms']))) * 0.1
        
        total_score = success_score + performance_score + memory_score + time_score
        return min(1.0, max(0.0, total_score))
    
    def _determine_status(self, score: float, successful_tools: int, total_tools: int, total_time_ms: int) -> EvaluationStatus:
        """Determine evaluation status"""
        if score >= self.evaluation_thresholds['min_score_threshold'] and total_time_ms <= self.evaluation_thresholds['max_total_time_ms']:
            return EvaluationStatus.PASSED
        elif score >= 0.5:
            return EvaluationStatus.WARNING
        else:
            return EvaluationStatus.FAILED
    
    def _generate_recommendations(self, tool_metrics: List[ToolExecutionMetrics], score: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Analyze failed tools
        failed_tools = [m for m in tool_metrics if not m.success]
        if failed_tools:
            recommendations.append(f"Fix {len(failed_tools)} failing tools: {', '.join(set(t.tool_name for t in failed_tools))}")
        
        # Analyze slow tools
        slow_tools = [m for m in tool_metrics if m.execution_time_ms > 2000]
        if slow_tools:
            recommendations.append(f"Optimize {len(slow_tools)} slow tools: {', '.join(set(t.tool_name for t in slow_tools))}")
        
        # Analyze memory usage
        memory_intensive_tools = [m for m in tool_metrics if m.memory_usage_mb > 100]
        if memory_intensive_tools:
            recommendations.append(f"Reduce memory usage for {len(memory_intensive_tools)} tools: {', '.join(set(t.tool_name for t in memory_intensive_tools))}")
        
        # General recommendations based on score
        if score < 0.5:
            recommendations.append("Overall toolpath performance is poor - consider redesign")
        elif score < 0.7:
            recommendations.append("Toolpath needs optimization before production use")
        elif score < 0.9:
            recommendations.append("Toolpath is acceptable but could be improved")
        
        return recommendations
    
    def get_evaluation_summary(self, results: List[ToolpathEvaluationResult]) -> Dict[str, Any]:
        """Get summary of multiple evaluation results"""
        if not results:
            return {"message": "No evaluation results available"}
        
        total_evaluations = len(results)
        passed_evaluations = sum(1 for r in results if r.status == EvaluationStatus.PASSED)
        failed_evaluations = sum(1 for r in results if r.status == EvaluationStatus.FAILED)
        warning_evaluations = sum(1 for r in results if r.status == EvaluationStatus.WARNING)
        
        avg_score = sum(r.score for r in results) / total_evaluations
        avg_execution_time = sum(r.total_execution_time_ms for r in results) / total_evaluations
        
        return {
            "total_evaluations": total_evaluations,
            "passed_evaluations": passed_evaluations,
            "failed_evaluations": failed_evaluations,
            "warning_evaluations": warning_evaluations,
            "pass_rate": passed_evaluations / total_evaluations,
            "average_score": avg_score,
            "average_execution_time_ms": avg_execution_time,
            "status": "GOOD" if passed_evaluations / total_evaluations >= 0.8 else "NEEDS_IMPROVEMENT"
        }

# Global evaluator instance
_toolpath_evaluator = None

def get_toolpath_evaluator() -> ToolpathEvaluator:
    """Get the global toolpath evaluator instance"""
    global _toolpath_evaluator
    if _toolpath_evaluator is None:
        _toolpath_evaluator = ToolpathEvaluator()
    return _toolpath_evaluator

# Convenience functions
def evaluate_toolpath(toolpath: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> ToolpathEvaluationResult:
    """Evaluate a toolpath"""
    evaluator = get_toolpath_evaluator()
    return evaluator.evaluate_toolpath(toolpath, context)

def run_toolpath_evaluation() -> bool:
    """Run comprehensive toolpath evaluation"""
    evaluator = get_toolpath_evaluator()
    
    # Define test toolpaths
    test_toolpaths = [
        [
            {"tool_name": "draft_executor", "parameters": {"content": "test content"}},
            {"tool_name": "model_call", "parameters": {"prompt": "test prompt"}},
            {"tool_name": "file_operation", "parameters": {"action": "save"}}
        ],
        [
            {"tool_name": "data_processing", "parameters": {"data": "sample data"}},
            {"tool_name": "model_call", "parameters": {"prompt": "analysis prompt"}}
        ],
        [
            {"tool_name": "draft_executor", "parameters": {"content": "complex content"}},
            {"tool_name": "data_processing", "parameters": {"data": "large dataset"}},
            {"tool_name": "model_call", "parameters": {"prompt": "complex prompt"}},
            {"tool_name": "file_operation", "parameters": {"action": "save"}}
        ]
    ]
    
    results = []
    for toolpath in test_toolpaths:
        result = evaluator.evaluate_toolpath(toolpath)
        results.append(result)
    
    # Get summary
    summary = evaluator.get_evaluation_summary(results)
    
    # Save results
    evaluation_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "detailed_results": [asdict(r) for r in results]
    }
    
    # Convert enum values to strings for JSON serialization
    for result in evaluation_report["detailed_results"]:
        result["status"] = result["status"].value if hasattr(result["status"], "value") else str(result["status"])
        for metric in result["tool_metrics"]:
            # ToolExecutionMetrics doesn't have enums, but ensure all values are serializable
            pass
    
    with open("evaluation_results.json", "w") as f:
        json.dump(evaluation_report, f, indent=2)
    
    logger.info(f"Toolpath evaluation completed: {summary['pass_rate']:.1%} pass rate")
    
    # Return True if evaluation passes threshold
    return summary["pass_rate"] >= 0.8 and summary["average_score"] >= 0.7
