"""
L5 - Pure Safety and Policy Layer

This layer handles all safety checks and policy enforcement.
No business logic, tool execution, or state management is allowed here.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

# Re-export canonical types from l5.types

# Re-export policy engine from l5.policy

# Alias for backward compatibility
SafetySystem = SafetyEngine


# =============================================================================
# Adapter Functions for Legacy/Test Compatibility
# =============================================================================


def safety_gate(result: Any) -> bool:
    """
    Check if a safety result allows the operation to proceed.
    
    This is a simple adapter that checks if there are any blocking findings
    in the safety result. Used by tests and runtime to make go/no-go decisions.
    
    Args:
        result: A SafetyResult-like object with a 'findings' attribute
        
    Returns:
        bool: True if the operation is safe to proceed, False if blocked
    """
    # Handle None or missing result
    if result is None:
        return True
    
    # Check if result has findings attribute
    if not hasattr(result, 'findings'):
        return True
    
    findings = getattr(result, 'findings', [])
    
    # If no findings, allow
    if not findings:
        return True
    
    # Check for blocking findings
    # A finding is blocking if it has high/critical severity
    for finding in findings:
        severity = getattr(finding, 'severity', None)
        if severity:
            # Handle both string and enum severity
            severity_str = severity.value if hasattr(severity, 'value') else str(severity)
            if severity_str in ('high', 'critical'):
                return False
    
    return True


def _extract_severity_string(severity: Any) -> str:
    """Extract severity string from severity object."""
    if not severity:
        return 'unknown'
    return severity.value if hasattr(severity, 'value') else str(severity)

def _process_finding(finding: Any, findings_list: List[Dict], max_severity: Optional[str]) -> Optional[str]:
    """Process a single finding and update max severity."""
    severity = getattr(finding, 'severity', None)
    severity_str = _extract_severity_string(severity)
    
    findings_list.append({
        'check_id': getattr(finding, 'id', 'unknown'),
        'category': getattr(finding, 'type', getattr(finding, 'category', 'unknown')),
        'severity': severity_str,
        'message': getattr(finding, 'message', ''),
    })
    
    if severity_str in ('critical', 'high'):
        return 'high'
    elif severity_str == 'medium' and max_severity != 'high':
        return 'medium'
    return max_severity

def _map_severity_to_decision(max_severity: Optional[str]) -> tuple[str, str]:
    """Map severity level to decision and reason."""
    if max_severity == 'high':
        return "block", "High severity safety violation detected"
    elif max_severity == 'medium':
        return "replan", "Medium severity issue requires replanning"
    return "allow", "No safety concerns detected"

def arbitrate_safety(
    safety_result: Any,
    council_vote: Any,
    policy: Any,
    ctx: Any = None
) -> Dict[str, object]:
    """Arbitrate between safety findings and council votes to produce a decision."""
    decision = "allow"
    reason = "No safety concerns detected"
    findings_list = []
    
    if safety_result and hasattr(safety_result, 'findings'):
        findings = getattr(safety_result, 'findings', [])
        max_severity = None
        
        for finding in findings:
            max_severity = _process_finding(finding, findings_list, max_severity)
            if max_severity == 'high':
                break
        
        decision, reason = _map_severity_to_decision(max_severity)
    
    # Try to call run_l5 if it exists (for test compatibility)
    try:
        event = run_l5(safety_result, council_vote, policy, ctx)
        
        # Extract verdict and reason from event if present
        if event:
            verdict = getattr(event, 'verdict', None)
            event_reason = getattr(event, 'reason', None)
            
            if verdict:
                verdict_str = verdict.value if hasattr(verdict, 'value') else str(verdict)
                if verdict_str == 'block':
                    decision = 'block'
                elif verdict_str == 'review':
                    decision = 'replan'
                elif verdict_str == 'allow':
                    decision = 'allow'
            
            if event_reason:
                reason = str(event_reason)
    except Exception:
        # If run_l5 fails or doesn't exist, use the decision we already computed
        pass
    
    return {
        "decision": decision,
        "reason": reason,
        "findings": findings_list,
    }


def run_l5(
    safety_result: Any,
    council_vote: Any,
    policy: Any,
    ctx: Any = None
) -> Any:
    """
    Run L5 policy evaluation and return a verdict event.
    
    This is a thin adapter that converts safety results into a policy decision
    event with verdict and reason fields.
    
    Args:
        safety_result: SafetyResult with findings
        council_vote: CouncilVote (for future use)
        policy: SafetyPolicy to apply
        ctx: Optional execution context
        
    Returns:
        An event object with 'verdict' and 'reason' attributes
    """
    from dataclasses import dataclass
    
    @dataclass
    class L5Event:
        verdict: Optional[Verdict] = None
        reason: Optional[str] = None
    
    # Determine verdict from safety findings
    verdict = Verdict.ALLOW
    reason = "No safety concerns"
    
    if safety_result and hasattr(safety_result, 'findings'):
        findings = getattr(safety_result, 'findings', [])
        
        for finding in findings:
            severity = getattr(finding, 'severity', None)
            if severity:
                severity_str = severity.value if hasattr(severity, 'value') else str(severity)
                
                if severity_str in ('critical', 'high'):
                    verdict = Verdict.BLOCK
                    reason = f"Blocked: {getattr(finding, 'message', 'safety violation')}"
                    break
                elif severity_str == 'medium' and verdict == Verdict.ALLOW:
                    verdict = Verdict.REVIEW
                    reason = f"Review required: {getattr(finding, 'message', 'potential issue')}"
    
    return L5Event(verdict=verdict, reason=reason)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Core types from l5.types
    'Severity',
    'Verdict',
    'FindingType',
    'SafetyFinding',
    'PolicyDecision',
    'SafetyContext',
    'SafetyError',
    'PolicyEvaluationError',
    'PolicyConfigurationError',
    # Policy engine from l5.policy
    'SafetyPolicy',
    'PolicyResult',
    'SafetyEngine',
    # Adapter functions
    'safety_gate',
    'arbitrate_safety',
    'run_l5',
]


