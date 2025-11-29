#!/usr/bin/env python3
"""
Usage Policies
Section 14: Security Layer - Usage policies for resume data processing
"""

from typing import Dict, Any, List, Optional
import logging
import time

logger = logging.getLogger(__name__)

class UsagePolicy:
    """Policy manager for resume data usage compliance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.usage_limits = self.config.get("usage_limits", {})
        self.allowed_purposes = self.config.get("allowed_purposes", set())
        self.retention_period = self.config.get("retention_period", 365)  # days
        self.audit_enabled = self.config.get("audit_enabled", True)
    
    def check_resume_usage(self, usage_request: Dict[str, Any]) -> Dict[str, Any]:
        """Check if resume usage request complies with policies"""
        try:
            compliance_result = {
                "is_compliant": True,
                "policy_violations": [],
                "usage_granted": True,
                "conditions": [],
                "audit_log": []
            }
            
            # Check purpose compliance
            purpose_issues = self._validate_purpose(usage_request)
            if purpose_issues:
                compliance_result["policy_violations"].extend(purpose_issues)
                compliance_result["is_compliant"] = False
                compliance_result["usage_granted"] = False
            
            # Check usage limits
            limit_issues = self._check_usage_limits(usage_request)
            if limit_issues:
                compliance_result["policy_violations"].extend(limit_issues)
                if self.is_strict_violation(limit_issues):
                    compliance_result["is_compliant"] = False
                    compliance_result["usage_granted"] = False
            
            # Apply conditions
            compliance_result["conditions"] = self._generate_usage_conditions(usage_request)
            
            # Log audit trail
            if self.audit_enabled:
                compliance_result["audit_log"] = self._create_audit_log(usage_request, compliance_result)
            
            logger.info(f"Usage policy check completed: {'Granted' if compliance_result['usage_granted'] else 'Denied'}")
            return compliance_result
            
        except Exception as e:
            logger.error(f"Usage policy check failed: {e}")
            return {"is_compliant": False, "usage_granted": False, "error": str(e)}
    
    def _validate_purpose(self, usage_request: Dict[str, Any]) -> List[str]:
        """Validate usage purpose against allowed purposes"""
        issues = []
        purpose = usage_request.get("purpose", "").lower()
        
        if not purpose:
            issues.append("Usage purpose not specified")
            return issues
        
        if self.allowed_purposes and purpose not in [p.lower() for p in self.allowed_purposes]:
            issues.append(f"Usage purpose '{purpose}' not in allowed purposes: {list(self.allowed_purposes)}")
        
        # Check for restricted purposes
        restricted_purposes = ["discrimination", "harassment", "illegal", "unauthorized"]
        for restricted in restricted_purposes:
            if restricted in purpose:
                issues.append(f"Usage purpose contains restricted term: {restricted}")
        
        return issues
    
    def _check_usage_limits(self, usage_request: Dict[str, Any]) -> List[str]:
        """Check usage against configured limits"""
        issues = []
        
        # Check data access limits
        if "data_access" in self.usage_limits:
            max_access = self.usage_limits["data_access"]
            requested_access = len(usage_request.get("requested_fields", []))
            if requested_access > max_access:
                issues.append(f"Requested {requested_access} fields, exceeds limit of {max_access}")
        
        # Check processing time limits
        if "processing_time" in self.usage_limits:
            max_time = self.usage_limits["processing_time"]
            requested_time = usage_request.get("estimated_processing_time", 0)
            if requested_time > max_time:
                issues.append(f"Estimated processing time {requested_time}s exceeds limit of {max_time}s")
        
        # Check frequency limits
        if "request_frequency" in self.usage_limits:
            max_requests = self.usage_limits["request_frequency"]
            user_id = usage_request.get("user_id", "")
            current_requests = self._get_user_request_count(user_id)
            if current_requests >= max_requests:
                issues.append(f"User {user_id} has reached request limit of {max_requests}")
        
        return issues
    
    def _generate_usage_conditions(self, usage_request: Dict[str, Any]) -> List[str]:
        """Generate conditions for approved usage"""
        conditions = []
        
        # Standard conditions
        conditions.extend([
            "Data must be used only for specified purpose",
            f"Data must be deleted after {self.retention_period} days",
            "No data sharing with third parties without explicit consent",
            "Compliance with all applicable privacy laws required"
        ])
        
        # Purpose-specific conditions
        purpose = usage_request.get("purpose", "").lower()
        if "analysis" in purpose:
            conditions.append("Analysis results must be anonymized")
        elif "storage" in purpose:
            conditions.append("Data must be encrypted at rest")
        elif "processing" in purpose:
            conditions.append("Processing logs must be maintained")
        
        return conditions
    
    def _create_audit_log(self, usage_request: Dict[str, Any], compliance_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create audit log entry for usage request"""
        return [{
            "timestamp": time.time(),
            "user_id": usage_request.get("user_id", "unknown"),
            "purpose": usage_request.get("purpose", "unknown"),
            "requested_fields": usage_request.get("requested_fields", []),
            "compliance_result": compliance_result["is_compliant"],
            "usage_granted": compliance_result["usage_granted"],
            "violations": compliance_result["policy_violations"],
            "conditions": compliance_result["conditions"]
        }]
    
    def is_strict_violation(self, issues: List[str]) -> bool:
        """Determine if violations are strict (deny usage)"""
        strict_keywords = ["discrimination", "harassment", "illegal", "unauthorized", "restricted"]
        for issue in issues:
            if any(keyword in issue.lower() for keyword in strict_keywords):
                return True
        return False
    
    def _get_user_request_count(self, user_id: str) -> int:
        """Get current request count for user (simplified implementation)"""
        # In production, would query actual usage database
        return 0
    
    def get_usage_summary(self, compliance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate usage compliance summary"""
        return {
            "compliance_status": "Compliant" if compliance_result.get("is_compliant", False) else "Non-compliant",
            "usage_granted": compliance_result.get("usage_granted", False),
            "violations_count": len(compliance_result.get("policy_violations", [])),
            "conditions_applied": len(compliance_result.get("conditions", [])),
            "audit_logged": len(compliance_result.get("audit_log", [])) > 0
        }
    
    def update_usage_policies(self, new_policies: Dict[str, Any]) -> bool:
        """Update usage policy configuration"""
        try:
            self.usage_limits.update(new_policies.get("usage_limits", {}))
            self.allowed_purposes.update(new_policies.get("allowed_purposes", set()))
            self.retention_period = new_policies.get("retention_period", self.retention_period)
            self.audit_enabled = new_policies.get("audit_enabled", self.audit_enabled)
            
            logger.info("Usage policies updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update usage policies: {e}")
            return False

def check_resume_usage(usage_request: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to check resume usage compliance"""
    policy = UsagePolicy(config)
    return policy.check_resume_usage(usage_request)

# Re-export components
__all__ = [
    'UsagePolicy', 'check_resume_usage'
]
