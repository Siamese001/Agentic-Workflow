"""Implementation for init_v6."""

from typing import Any, Dict, List, Optional

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
    if result is None:
        return True
    if not hasattr(result, 'findings'):
        return True
    findings = getattr(result, 'findings', [])
    if not findings:
        return True
    for finding in findings:
        severity = getattr(finding, 'severity', None)
        if severity:
            severity_str = severity.value if hasattr(severity, 'value') else str(severity)
            if severity_str in ('high', 'critical'):
                return False
    return True

def _extract_severity_string(severity: Any) -> str:
    """Extract severity string from severity object."""
    if not severity:
        return 'unknown'
    return severity.value if hasattr(severity, 'value') else str(severity)

def _process_finding(finding: Any) -> tuple[Optional[str], Dict[str, object]]:
    """Process a single finding and return (severity_str, finding_dict)."""
    severity = getattr(finding, 'severity', None)
    severity_str = _extract_severity_string(severity)
    finding_dict = {'check_id': getattr(finding, 'id', 'unknown'), 'category': getattr(finding, 'type', getattr(finding, 'category', 'unknown')), 'severity': severity_str, 'message': getattr(finding, 'message', '')}
    return (severity_str, finding_dict)

def _determine_max_severity(findings: list) -> tuple[Optional[str], list]:
    """Determine maximum severity from findings and collect finding info."""
    max_severity = None
    findings_list = []
    for finding in findings:
        severity_str, finding_dict = _process_finding(finding)
        findings_list.append(finding_dict)
        if severity_str in ('critical', 'high'):
            max_severity = 'high'
            break
        elif severity_str == 'medium' and max_severity != 'high':
            max_severity = 'medium'
    return (max_severity, findings_list)

def _map_verdict_to_decision(verdict: Any) -> str:
    """Map verdict object to decision string."""
    verdict_str = verdict.value if hasattr(verdict, 'value') else str(verdict)
    verdict_map = {'block': 'block', 'review': 'replan', 'allow': 'allow'}
    return verdict_map.get(verdict_str, 'allow')

def arbitrate_safety(safety_result: Any, council_vote: Any, policy: Any, ctx: Any=None) -> Dict[str, object]:
    """
    Arbitrate between safety findings and council votes to produce a decision.

    This adapter maps safety findings to archived decision format expected by tests.

    Decision mapping:
    - high/critical severity -> "block"
    - medium severity -> "replan"
    - low/no findings -> "allow"

    Args:
        safety_result: SafetyResult with findings
        council_vote: CouncilVote (currently unused in decision logic)
        policy: SafetyPolicy (currently unused in decision logic)
        ctx: Optional execution context

    Returns:
        dict: {"decision": str, "reason": str, "findings": list}
    """
    decision = 'allow'
    reason = 'No safety concerns detected'
    findings_list = []
    if safety_result and hasattr(safety_result, 'findings'):
        findings = getattr(safety_result, 'findings', [])
        max_severity, findings_list = _determine_max_severity(findings)
        if max_severity == 'high':
            decision = 'block'
            reason = 'High severity safety violation detected'
        elif max_severity == 'medium':
            decision = 'replan'
            reason = 'Medium severity issue requires replanning'
    try:
        event = run_l5(safety_result, council_vote, policy, ctx)
        if event:
            verdict = getattr(event, 'verdict', None)
            if verdict:
                decision = _map_verdict_to_decision(verdict)
            event_reason = getattr(event, 'reason', None)
            if event_reason:
                reason = str(event_reason)
    except Exception:
        pass
    return {'decision': decision, 'reason': reason, 'findings': findings_list}

def run_l5(safety_result: Any, council_vote: Any, policy: Any, ctx: Any=None) -> Any:
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
    verdict = Verdict.ALLOW
    reason = 'No safety concerns'
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
