"""
Result Normalization Utilities - Standardized Agent Execution Results

This module provides centralized utilities for normalizing agent execution results,
eliminating the need for repeated manual extraction of violations/fixes across 43+ files.

USAGE:
    from agentic_core.utils.result_utils import (
        AgentResult,
        normalize_agent_result,
        aggregate_results,
    )
    
    # Normalize any agent return value
    result = normalize_agent_result("LocationAgent", agent.heal_repository())
    print(f"Status: {result.status}, Violations: {result.violations_found}")
    
    # Aggregate multiple results
    summary = aggregate_results([result1, result2, result3])
    print(f"Total violations: {summary['total_violations']}")

SSOT PRINCIPLE:
    All agent result handling should use this module instead of manual extraction.
    This ensures consistent key mapping and status calculation across all orchestrators.

KEY MAPPINGS:
    violations_found <- violations | violations_found | errors
    violations_fixed <- fixed | violations_fixed | renamed
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

Logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """
    Standardized agent execution result.
    
    This dataclass provides a consistent structure for agent results,
    eliminating the need to handle different key names across agents.
    
    Attributes:
        agent_name: Name of the agent that produced this result
        status: Execution status ('PASS', 'FAIL', 'ERROR', 'SKIPPED')
        violations_found: Number of violations detected
        violations_fixed: Number of violations fixed
        execution_time_ms: Execution duration in milliseconds
        error_message: Error message if status is 'ERROR'
        metadata: Additional agent-specific data
    """
    agent_name: str
    status: str = "UNKNOWN"  # PASS, FAIL, ERROR, SKIPPED
    violations_found: int = 0
    violations_fixed: int = 0
    execution_time_ms: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        """Check if the result indicates success (no violations)."""
        return self.status == "PASS" and self.violations_found == 0
    
    @property
    def is_error(self) -> bool:
        """Check if the result indicates an error."""
        return self.status == "ERROR"
    
    @property
    def is_skipped(self) -> bool:
        """Check if the agent was skipped."""
        return self.status == "SKIPPED"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


def normalize_agent_result(
    agent_name: str,
    result: Any,
    execution_time_ms: int = 0
) -> AgentResult:
    """
    Normalize any agent return value to a standardized AgentResult.
    
    This function handles the various key names used by different agents
    and produces a consistent result structure.
    
    Args:
        agent_name: Name of the agent that produced the result
        result: Raw result from agent (None, dict, or other)
        execution_time_ms: Execution duration in milliseconds
        
    Returns:
        AgentResult with normalized values
        
    Key Mappings:
        violations_found <- violations | violations_found | errors
        violations_fixed <- fixed | violations_fixed | renamed
        
    Status Calculation:
        - None result -> SKIPPED
        - Error in result -> ERROR
        - violations_found > 0 -> FAIL
        - violations_found == 0 -> PASS
    """
    # Handle None result
    if result is None:
        Logger.debug(f"[RESULT] {agent_name}: Returned None (SKIPPED)")
        return AgentResult(
            agent_name=agent_name,
            status="SKIPPED",
            violations_found=0,
            violations_fixed=0,
            execution_time_ms=execution_time_ms,
            error_message="Agent returned None",
        )
    
    # Handle non-dict results
    if not isinstance(result, dict):
        Logger.warning(f"[RESULT] {agent_name}: Unexpected result type {type(result)}")
        return AgentResult(
            agent_name=agent_name,
            status="ERROR",
            violations_found=0,
            violations_fixed=0,
            execution_time_ms=execution_time_ms,
            error_message=f"Unexpected result type: {type(result).__name__}",
            metadata={"raw_result": str(result)[:200]},
        )
    
    # Extract violations_found from various key names
    violations_found = (
        result.get("violations_found")
        or result.get("violations")
        or result.get("errors")
        or 0
    )
    
    # Ensure it's an integer
    if not isinstance(violations_found, int):
        try:
            violations_found = int(violations_found)
        except (ValueError, TypeError):
            violations_found = 0
    
    # Extract violations_fixed from various key names
    violations_fixed = (
        result.get("violations_fixed")
        or result.get("fixed")
        or result.get("renamed")
        or 0
    )
    
    # Ensure it's an integer
    if not isinstance(violations_fixed, int):
        try:
            violations_fixed = int(violations_fixed)
        except (ValueError, TypeError):
            violations_fixed = 0
    
    # Check for error indicators
    error_message = result.get("error_message") or result.get("error")
    has_error = (
        result.get("status") == "ERROR"
        or error_message is not None
        or result.get("is_error", False)
    )
    
    # Determine status
    if has_error:
        status = "ERROR"
    elif result.get("status") == "SKIPPED" or result.get("skipped", False):
        status = "SKIPPED"
    elif violations_found > 0:
        status = "FAIL"
    else:
        status = "PASS"
    
    # Build metadata from remaining keys
    metadata = {}
    standard_keys = {
        "violations", "violations_found", "errors",
        "fixed", "violations_fixed", "renamed",
        "status", "error", "error_message", "is_error", "skipped"
    }
    for key, value in result.items():
        if key not in standard_keys:
            metadata[key] = value
    
    return AgentResult(
        agent_name=agent_name,
        status=status,
        violations_found=violations_found,
        violations_fixed=violations_fixed,
        execution_time_ms=execution_time_ms,
        error_message=str(error_message) if error_message else None,
        metadata=metadata,
    )


def aggregate_results(results: List[AgentResult]) -> Dict[str, Any]:
    """
    Aggregate multiple AgentResults into a summary.
    
    Args:
        results: List of AgentResult objects
        
    Returns:
        Dictionary with aggregated statistics:
        - total_agents: Number of agents
        - total_violations: Sum of violations_found
        - total_fixed: Sum of violations_fixed
        - total_time_ms: Sum of execution times
        - passed: Count of PASS status
        - failed: Count of FAIL status
        - errors: Count of ERROR status
        - skipped: Count of SKIPPED status
        - is_stable: True if no violations remain unfixed
    """
    if not results:
        return {
            "total_agents": 0,
            "total_violations": 0,
            "total_fixed": 0,
            "total_time_ms": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "is_stable": True,
        }
    
    total_violations = sum(r.violations_found for r in results)
    total_fixed = sum(r.violations_fixed for r in results)
    total_time_ms = sum(r.execution_time_ms for r in results)
    
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")
    skipped = sum(1 for r in results if r.status == "SKIPPED")
    
    # Repository is stable if all violations were fixed
    unfixed_violations = total_violations - total_fixed
    is_stable = unfixed_violations <= 0 and errors == 0
    
    return {
        "total_agents": len(results),
        "total_violations": total_violations,
        "total_fixed": total_fixed,
        "total_time_ms": total_time_ms,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "is_stable": is_stable,
        "unfixed_violations": max(0, unfixed_violations),
    }


def extract_violations(result: Any) -> int:
    """
    Extract violations count from any result format.
    
    Convenience function for simple extraction without full normalization.
    
    Args:
        result: Raw agent result
        
    Returns:
        Number of violations found (0 if not determinable)
    """
    if result is None:
        return 0
    if not isinstance(result, dict):
        return 0
    
    violations = (
        result.get("violations_found")
        or result.get("violations")
        or result.get("errors")
        or 0
    )
    
    try:
        return int(violations)
    except (ValueError, TypeError):
        return 0


def extract_fixes(result: Any) -> int:
    """
    Extract fixes count from any result format.
    
    Convenience function for simple extraction without full normalization.
    
    Args:
        result: Raw agent result
        
    Returns:
        Number of fixes applied (0 if not determinable)
    """
    if result is None:
        return 0
    if not isinstance(result, dict):
        return 0
    
    fixes = (
        result.get("violations_fixed")
        or result.get("fixed")
        or result.get("renamed")
        or 0
    )
    
    try:
        return int(fixes)
    except (ValueError, TypeError):
        return 0


__all__ = [
    "AgentResult",
    "normalize_agent_result",
    "aggregate_results",
    "extract_violations",
    "extract_fixes",
]
