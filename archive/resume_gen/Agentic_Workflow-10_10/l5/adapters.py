"""L5 Adapter - Wraps SafetyValidator to implement L5 interfaces

This adapter provides backward compatibility while enforcing strict interface contracts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from l5.interfaces import (
    L5PolicyEnforcerInterface,
    L5SafetyCheckerInterface,
    L5RiskAssessmentInterface,
    L5ComplianceCheckerInterface,
    L5HitLInterface,
    L5ResourceGuardInterface,
    L5AuditLoggerInterface,
    L5PolicyRequest,
    L5PolicyResult,
    PolicyType,
    Action,
)
from l5.safety_validator import SafetyValidator, SafetyViolation
from core.models.models import (
    ExecutionContext,
    SafetyResult,
    SafetyFinding,
    RiskLevel,
    PolicyViolation,
    HitLRequest,
)


class SafetyValidatorAdapter(L5SafetyCheckerInterface):
    """Adapter that wraps SafetyValidator to implement L5 safety interface."""
    
    def __init__(self, wrapped_validator: SafetyValidator):
        self.wrapped_validator = wrapped_validator
    
    async def check_content_safety(self, content: str, context: ExecutionContext) -> SafetyResult:
        """Check content for safety violations using wrapped implementation."""
        try:
            violations = self.wrapped_validator.validate_content(content)
            
            findings = []
            risk_level = RiskLevel.LOW
            
            for violation in violations:
                finding = SafetyFinding(
                    type="safety_violation",
                    severity=violation.severity,
                    description=violation.description,
                    recommendation=f"Address policy violation: {violation.policy_rule}",
                )
                findings.append(finding)
                
                # Determine overall risk level
                if violation.severity == "high":
                    risk_level = RiskLevel.HIGH
                elif violation.severity == "medium" and risk_level == RiskLevel.LOW:
                    risk_level = RiskLevel.MEDIUM
            
            is_safe = len(violations) == 0
            
            return SafetyResult(
                is_safe=is_safe,
                risk_level=risk_level.value,
                findings=findings,
                recommendations=[f.recommendation for f in findings],
                metadata={"violations_count": len(violations)},
            )
            
        except Exception as e:
            return SafetyResult(
                is_safe=False,
                risk_level=RiskLevel.HIGH.value,
                findings=[],
                recommendations=[f"Safety check failed: {str(e)}"],
                metadata={"error": str(e)},
            )
    
    async def check_data_privacy(self, data: Any, context: ExecutionContext) -> SafetyResult:
        """Check data for privacy violations."""
        # Convert data to string for validation
        content = str(data) if data else ""
        return await self.check_content_safety(content, context)
    
    async def assess_risk(self, operation: str, data: Any, context: ExecutionContext) -> RiskLevel:
        """Assess risk level for an operation."""
        safety_result = await self.check_content_safety(str(data), context)
        return RiskLevel(safety_result.risk_level)
    
    async def detect_injection(self, input_data: str, context: ExecutionContext) -> SafetyResult:
        """Detect potential injection attacks."""
        # Enhanced injection detection beyond basic safety validation
        injection_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'\$\{.*\}',
            r'__import__\(',
            r'eval\s*\(',
            r'exec\s*\(',
        ]
        
        import re
        violations = []
        
        for pattern in injection_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                violations.append(SafetyFinding(
                    type="injection_attempt",
                    severity="high",
                    description=f"Potential injection pattern detected: {pattern}",
                    recommendation="Remove or sanitize input containing code patterns",
                ))
        
        # Also run standard safety check
        base_safety = await self.check_content_safety(input_data, context)
        violations.extend(base_safety.findings)
        
        is_safe = len(violations) == 0
        risk_level = RiskLevel.HIGH if violations else RiskLevel.LOW
        
        return SafetyResult(
            is_safe=is_safe,
            risk_level=risk_level.value,
            findings=violations,
            recommendations=[v.recommendation for v in violations],
            metadata={"injection_check": True},
        )


class PolicyEnforcerAdapter(L5PolicyEnforcerInterface):
    """Adapter for policy enforcement operations."""
    
    def __init__(self, safety_adapter: SafetyValidatorAdapter):
        self.safety_adapter = safety_adapter
        self.policies = {
            PolicyType.CONTENT_SAFETY: True,
            PolicyType.DATA_PRIVACY: True,
            PolicyType.RESOURCE_LIMITS: True,
            PolicyType.ACCESS_CONTROL: False,  # Not implemented yet
            PolicyType.COMPLIANCE: False,      # Not implemented yet
            PolicyType.ETHICAL_GUIDELINES: True,
        }
    
    async def evaluate_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Evaluate policy compliance for an operation."""
        violations = []
        findings = []
        action = Action.ALLOW
        risk_level = RiskLevel.LOW
        
        # Evaluate each policy type
        for policy_type in request.policy_types:
            if not self.policies.get(policy_type, False):
                continue
            
            if policy_type == PolicyType.CONTENT_SAFETY:
                safety_result = await self.safety_adapter.check_content_safety(
                    str(request.data), request.context
                )
                findings.extend(safety_result.findings)
                
                if not safety_result.is_safe:
                    action = Action.BLOCK
                    risk_level = RiskLevel(safety_result.risk_level)
                    
                    for finding in safety_result.findings:
                        violation = PolicyViolation(
                            policy_type=policy_type.value,
                            severity=finding.severity,
                            description=finding.description,
                            recommendation=finding.recommendation,
                        )
                        violations.append(violation)
            
            elif policy_type == PolicyType.DATA_PRIVACY:
                privacy_result = await self.safety_adapter.check_data_privacy(
                    request.data, request.context
                )
                findings.extend(privacy_result.findings)
                
                if not privacy_result.is_safe:
                    action = Action.BLOCK
                    risk_level = RiskLevel(privacy_result.risk_level)
        
        return L5PolicyResult(
            action=action,
            risk_level=risk_level,
            findings=findings,
            violations=violations,
            metadata={"evaluated_policies": [p.value for p in request.policy_types]},
        )
    
    async def enforce_policy(self, request: L5PolicyRequest) -> L5PolicyResult:
        """Enforce policy compliance and take appropriate action."""
        result = await self.evaluate_policy(request)
        
        # Take enforcement action based on evaluation
        if result.action == Action.BLOCK:
            # Log the blocking event
            await self._log_policy_event("policy_block", {
                "operation": request.operation,
                "violations": [v.description for v in result.violations],
                "context": request.context.execution_id,
            })
        
        return result
    
    async def validate_policy_config(self, policy_config: Dict[str, Any]) -> bool:
        """Validate policy configuration."""
        required_keys = ["enabled_policies", "thresholds"]
        return all(key in policy_config for key in required_keys)
    
    async def _log_policy_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log policy-related events."""
        # Simple logging - would integrate with proper audit system
        print(f"POLICY_EVENT: {event_type} - {data}")


class RiskAssessmentAdapter(L5RiskAssessmentInterface):
    """Adapter for risk assessment operations."""
    
    def __init__(self):
        self.risk_factors = {
            "high": ["personal_info", "injection_attempt", "prohibited_content"],
            "medium": ["long_content", "external_links", "file_operations"],
            "low": ["text_generation", "analysis", "summarization"],
        }
    
    async def calculate_risk_score(self, operation: str, data: Any, context: ExecutionContext) -> float:
        """Calculate numerical risk score (0.0-1.0)."""
        risk_level = await self._assess_operation_risk(operation, data, context)
        
        # Convert risk level to numerical score
        scores = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0,
        }
        
        return scores.get(risk_level, 0.5)
    
    async def identify_risk_factors(self, operation: str, data: Any, context: ExecutionContext) -> List[str]:
        """Identify specific risk factors."""
        factors = []
        content = str(data).lower()
        
        # Check for high-risk factors
        for factor in self.risk_factors["high"]:
            if factor.replace("_", "") in content:
                factors.append(factor)
        
        # Check for medium-risk factors
        for factor in self.risk_factors["medium"]:
            if factor.replace("_", "") in content:
                factors.append(factor)
        
        # Operation-specific risks
        if "file" in operation.lower():
            factors.append("file_operations")
        if "network" in operation.lower() or "http" in content:
            factors.append("network_access")
        
        return factors
    
    async def recommend_mitigation(self, risk_factors: List[str], context: ExecutionContext) -> List[str]:
        """Recommend risk mitigation strategies."""
        recommendations = []
        
        for factor in risk_factors:
            if factor == "personal_info":
                recommendations.append("Sanitize personally identifiable information")
            elif factor == "injection_attempt":
                recommendations.append("Use input validation and sanitization")
            elif factor == "prohibited_content":
                recommendations.append("Filter prohibited content patterns")
            elif factor == "file_operations":
                recommendations.append("Use sandboxed file operations")
            elif factor == "network_access":
                recommendations.append("Restrict network access to approved endpoints")
            elif factor == "long_content":
                recommendations.append("Implement content length limits")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _assess_operation_risk(self, operation: str, data: Any, context: ExecutionContext) -> RiskLevel:
        """Assess risk level for an operation."""
        risk_factors = await self.identify_risk_factors(operation, data, context)
        
        # Determine risk level based on factors
        high_risk_factors = [f for f in risk_factors if f in self.risk_factors["high"]]
        medium_risk_factors = [f for f in risk_factors if f in self.risk_factors["medium"]]
        
        if high_risk_factors:
            return RiskLevel.HIGH
        elif medium_risk_factors:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class ComplianceCheckerAdapter(L5ComplianceCheckerInterface):
    """Adapter for compliance checking operations."""
    
    def __init__(self):
        self.regulations = {
            "GDPR": ["personal_data", "consent", "data_minimization"],
            "HIPAA": ["health_info", "phi", "access_controls"],
            "SOX": ["financial_data", "audit_trail", "retention"],
        }
    
    async def check_regulatory_compliance(self, data: Any, regulations: List[str], context: ExecutionContext) -> bool:
        """Check compliance with specific regulations."""
        content = str(data).lower()
        
        for regulation in regulations:
            if regulation in self.regulations:
                required_elements = self.regulations[regulation]
                # Simple check - in reality would be much more sophisticated
                for element in required_elements:
                    if element in content:
                        # Found potentially regulated content
                        # Would need proper compliance checking here
                        pass
        
        return True  # Placeholder
    
    async def validate_ethical_guidelines(self, content: str, guidelines: List[str], context: ExecutionContext) -> SafetyResult:
        """Validate content against ethical guidelines."""
        findings = []
        
        # Simple ethical guideline checks
        ethical_concerns = [
            "harmful", "discriminatory", "biased", "unethical",
            "manipulative", "deceptive", "exploitative"
        ]
        
        content_lower = content.lower()
        for concern in ethical_concerns:
            if concern in content_lower:
                findings.append(SafetyFinding(
                    type="ethical_concern",
                    severity="medium",
                    description=f"Potential ethical issue: {concern}",
                    recommendation=f"Review content for {concern} language",
                ))
        
        is_safe = len(findings) == 0
        risk_level = RiskLevel.MEDIUM if findings else RiskLevel.LOW
        
        return SafetyResult(
            is_safe=is_safe,
            risk_level=risk_level.value,
            findings=findings,
            recommendations=[f.recommendation for f in findings],
            metadata={"ethical_guidelines": guidelines},
        )
    
    async def audit_operation(self, operation: str, data: Any, context: ExecutionContext) -> Dict[str, Any]:
        """Create audit trail for operation."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "execution_id": context.execution_id,
            "user_id": getattr(context, "user_id", "unknown"),
            "data_hash": hash(str(data)) if data else None,
            "metadata": context.metadata,
        }
        
        # Store audit entry (simplified - would use proper audit storage)
        return audit_entry


class HitLAdapter(L5HitLInterface):
    """Adapter for Human-in-the-Loop operations."""
    
    def __init__(self):
        self.pending_requests: Dict[str, HitLRequest] = {}
    
    async def should_require_hitl(self, operation: str, data: Any, context: ExecutionContext) -> bool:
        """Determine if human approval is required."""
        # High-risk operations require HITL
        high_risk_operations = [
            "file_delete", "system_modify", "external_api_call",
            "data_export", "user_impersonation", "payment_process"
        ]
        
        return any(risk_op in operation.lower() for risk_op in high_risk_operations)
    
    async def create_hitl_request(self, operation: str, data: Any, context: ExecutionContext) -> HitLRequest:
        """Create human approval request."""
        request = HitLRequest(
            id=f"hitl_{context.execution_id}_{datetime.now().timestamp()}",
            operation=operation,
            data_summary=str(data)[:200] + "..." if len(str(data)) > 200 else str(data),
            context=context,
            created_at=datetime.now(),
            status="pending",
        )
        
        self.pending_requests[request.id] = request
        return request
    
    async def process_hitl_response(self, request_id: str, response: Dict[str, Any]) -> bool:
        """Process human response to approval request."""
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        request.status = "approved" if response.get("approved") else "rejected"
        request.response = response
        request.processed_at = datetime.now()
        
        return True
    
    async def escalate_for_review(self, issue: str, context: ExecutionContext) -> bool:
        """Escalate issue for human review."""
        escalation_request = HitLRequest(
            id=f"escalate_{context.execution_id}_{datetime.now().timestamp()}",
            operation="escalation",
            data_summary=issue,
            context=context,
            created_at=datetime.now(),
            status="escalated",
        )
        
        self.pending_requests[escalation_request.id] = escalation_request
        return True


class ResourceGuardAdapter(L5ResourceGuardInterface):
    """Adapter for resource guarding operations."""
    
    def __init__(self):
        self.limits = {
            "max_tokens_per_request": 10000,
            "max_requests_per_minute": 60,
            "max_cost_per_hour": 10.0,
            "max_file_size_mb": 100,
        }
        self.usage = {}
    
    async def check_resource_limits(self, resource_usage: Dict[str, Any], limits: Dict[str, Any]) -> bool:
        """Check if resource usage exceeds limits."""
        for resource, usage_value in resource_usage.items():
            limit_value = limits.get(resource)
            if limit_value and usage_value > limit_value:
                return False
        return True
    
    async def enforce_rate_limits(self, operation: str, user_id: str, context: ExecutionContext) -> bool:
        """Enforce rate limiting for operations."""
        now = datetime.now()
        minute_key = f"{user_id}:{now.strftime('%Y%m%d%H%M')}"
        
        current_count = self.usage.get(minute_key, 0)
        if current_count >= self.limits["max_requests_per_minute"]:
            return False
        
        self.usage[minute_key] = current_count + 1
        return True
    
    async def monitor_cost_limits(self, cost_estimate: float, budget_remaining: float) -> bool:
        """Monitor and enforce cost limits."""
        return cost_estimate <= budget_remaining


class AuditLoggerAdapter(L5AuditLoggerInterface):
    """Adapter for audit logging operations."""
    
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
    
    async def log_policy_event(self, event_type: str, data: Dict[str, Any], context: ExecutionContext) -> bool:
        """Log policy-related events."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data,
                "execution_id": context.execution_id,
            }
            self.audit_log.append(log_entry)
            return True
        except Exception:
            return False
    
    async def log_safety_violation(self, violation: PolicyViolation, context: ExecutionContext) -> bool:
        """Log safety violations."""
        return await self.log_policy_event("safety_violation", {
            "policy_type": violation.policy_type,
            "severity": violation.severity,
            "description": violation.description,
        }, context)
    
    async def create_compliance_report(self, time_range: Dict[str, datetime], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance reports."""
        filtered_logs = [
            log for log in self.audit_log
            if self._in_time_range(log["timestamp"], time_range)
            and self._matches_filters(log, filters)
        ]
        
        return {
            "time_range": time_range,
            "total_events": len(filtered_logs),
            "events_by_type": self._group_by_type(filtered_logs),
            "violations": [log for log in filtered_logs if "violation" in log["event_type"]],
        }
    
    async def export_audit_trail(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Export audit trail data."""
        return [log for log in self.audit_log if self._matches_filters(log, filters)]
    
    def _in_time_range(self, timestamp: str, time_range: Dict[str, datetime]) -> bool:
        """Check if timestamp is within time range."""
        ts = datetime.fromisoformat(timestamp)
        return time_range["start"] <= ts <= time_range["end"]
    
    def _matches_filters(self, log: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if log entry matches filters."""
        for key, value in filters.items():
            if key in log and log[key] != value:
                return False
        return True
    
    def _group_by_type(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group logs by event type."""
        groups = {}
        for log in logs:
            event_type = log["event_type"]
            groups[event_type] = groups.get(event_type, 0) + 1
        return groups
