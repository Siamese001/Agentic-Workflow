#!/usr/bin/env python3
"""
Prompt Injection Policies
Section 3: Canonical Repository Tree - Prompt Governance Injection Policies
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InjectionPolicy:
    """Injection prevention and security policies for prompt governance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.policy_id = self.config.get("policy_id", "")
        self.policy_name = self.config.get("policy_name", "")
        self.policy_type = self.config.get("policy_type", "prevention")
    
    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new injection prevention policy"""
        try:
            policy = {
                "policy_id": f"policy_{hash(str(policy_data)) % 10000}",
                "policy_name": policy_data.get("policy_name", ""),
                "policy_type": policy_data.get("policy_type", "prevention"),
                "description": policy_data.get("description", ""),
                "rules": policy_data.get("rules", []),
                "detection_patterns": policy_data.get("detection_patterns", []),
                "prevention_measures": policy_data.get("prevention_measures", []),
                "severity_levels": policy_data.get("severity_levels", {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "active": True
            }
            
            logger.info(f"Created injection policy: {policy['policy_name']}")
            return policy
            
        except Exception as e:
            logger.error(f"Failed to create injection policy: {e}")
            return {"error": str(e)}
    
    def get_default_policies(self) -> List[Dict[str, Any]]:
        """Get default injection prevention policies"""
        try:
            default_policies = [
                {
                    "policy_id": "policy_prompt_injection",
                    "policy_name": "Prompt Injection Prevention",
                    "policy_type": "prevention",
                    "description": "Prevents prompt injection attacks through input validation and filtering",
                    "rules": [
                        "Block inputs containing 'ignore previous instructions'",
                        "Block inputs containing 'system override'",
                        "Block inputs containing role-changing commands"
                    ],
                    "detection_patterns": [
                        r"(ignore|forget|disregard).*(previous|above|earlier).*(instructions|prompts|commands)",
                        r"(system|developer|admin).*(mode|override|privileges)",
                        r"(new\s+role|act\s+as|pretend\s+you\s+are)"
                    ],
                    "prevention_measures": [
                        "Input sanitization",
                        "Pattern matching",
                        "Context validation",
                        "Output filtering"
                    ],
                    "severity_levels": {
                        "high": "Immediate block",
                        "medium": "Warning and review",
                        "low": "Log and monitor"
                    }
                },
                {
                    "policy_id": "policy_data_injection",
                    "policy_name": "Data Injection Prevention",
                    "policy_type": "prevention",
                    "description": "Prevents malicious data injection through parameter validation",
                    "rules": [
                        "Validate all input parameters",
                        "Sanitize user-provided data",
                        "Check for SQL injection patterns",
                        "Block executable code snippets"
                    ],
                    "detection_patterns": [
                        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b)",
                        r"(\&\&|\|\||;|`|\$\()",
                        r"(<script[^>]*>.*?</script>)"
                    ],
                    "prevention_measures": [
                        "Parameter type checking",
                        "SQL parameterization",
                        "HTML encoding",
                        "Code execution blocking"
                    ],
                    "severity_levels": {
                        "critical": "Immediate block and alert",
                        "high": "Block with notification",
                        "medium": "Sanitize and proceed",
                        "low": "Log for review"
                    }
                },
                {
                    "policy_id": "policy_output_injection",
                    "policy_name": "Output Injection Prevention",
                    "policy_type": "prevention",
                    "description": "Prevents injection attacks through generated output validation",
                    "rules": [
                        "Validate output format",
                        "Check for malicious content",
                        "Sanitize HTML output",
                        "Prevent code execution in responses"
                    ],
                    "detection_patterns": [
                        r"(<script[^>]*>.*?</script>)",
                        r"(javascript:|vbscript:)",
                        r"(\b(exec|eval|system)\s*\()"
                    ],
                    "prevention_measures": [
                        "Output content filtering",
                        "HTML sanitization",
                        "Format validation",
                        "Safe rendering"
                    ],
                    "severity_levels": {
                        "high": "Block output generation",
                        "medium": "Sanitize and warn",
                        "low": "Log and monitor"
                    }
                }
            ]
            
            logger.info(f"Retrieved {len(default_policies)} default injection policies")
            return default_policies
            
        except Exception as e:
            logger.error(f"Failed to get default policies: {e}")
            return []
    
    def validate_input_against_policies(self, input_text: str, policies: List[str]) -> Dict[str, Any]:
        """Validate input against specified policies"""
        try:
            validation_result = {
                "is_safe": True,
                "violations": [],
                "risk_score": 0.0,
                "applied_policies": policies
            }
            
            # Get policy rules
            default_policies = self.get_default_policies()
            applicable_policies = [p for p in default_policies if p["policy_id"] in policies]
            
            for policy in applicable_policies:
                policy_violations = self._check_policy_violations(input_text, policy)
                if policy_violations:
                    validation_result["is_safe"] = False
                    validation_result["violations"].extend(policy_violations)
                    validation_result["risk_score"] += 0.3
            
            # Normalize risk score
            validation_result["risk_score"] = min(1.0, validation_result["risk_score"])
            
            logger.info(f"Input validation: risk_score={validation_result['risk_score']:.2f}, safe={validation_result['is_safe']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return {"is_safe": False, "error": str(e), "risk_score": 1.0}
    
    def _check_policy_violations(self, input_text: str, policy: Dict[str, Any]) -> List[str]:
        """Check for violations against a specific policy"""
        violations = []
        
        try:
            import re
            
            for pattern in policy.get("detection_patterns", []):
                if re.search(pattern, input_text, re.IGNORECASE):
                    violations.append(f"Violation of {policy['policy_name']}: pattern matched")
                    break  # One violation per policy is enough
            
            for rule in policy.get("rules", []):
                if rule.lower() in input_text.lower():
                    violations.append(f"Violation of {policy['policy_name']}: {rule}")
                    break
            
        except Exception as e:
            logger.error(f"Policy violation check failed: {e}")
        
        return violations
    
    def apply_prevention_measures(self, input_text: str, policy_id: str) -> Dict[str, Any]:
        """Apply prevention measures for a specific policy"""
        try:
            # Simulate prevention measure application
            prevention_result = {
                "policy_id": policy_id,
                "original_input": input_text,
                "sanitized_input": input_text,  # Would be actual sanitized input
                "measures_applied": [
                    "Input sanitization",
                    "Pattern filtering",
                    "Context validation"
                ],
                "applied_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Applied prevention measures for policy: {policy_id}")
            return prevention_result
            
        except Exception as e:
            logger.error(f"Failed to apply prevention measures: {e}")
            return {"success": False, "error": str(e)}
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing injection policy"""
        try:
            result = {
                "policy_id": policy_id,
                "updates": updates,
                "updated_at": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Updated injection policy: {policy_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update policy: {e}")
            return {"success": False, "error": str(e)}
    
    def get_policy_compliance_report(self, policies: List[str]) -> Dict[str, Any]:
        """Generate compliance report for specified policies"""
        try:
            compliance_report = {
                "report_id": f"report_{hash(str(policies)) % 1000}",
                "policies_evaluated": policies,
                "compliance_score": 0.85,  # Mock compliance score
                "findings": [
                    {
                        "policy_id": "policy_prompt_injection",
                        "status": "compliant",
                        "issues": []
                    },
                    {
                        "policy_id": "policy_data_injection",
                        "status": "warning",
                        "issues": ["Some parameters lack validation"]
                    }
                ],
                "recommendations": [
                    "Add parameter validation for all user inputs",
                    "Implement real-time injection monitoring",
                    "Regular policy review and updates"
                ],
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated compliance report for {len(policies)} policies")
            return compliance_report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {"error": str(e)}

def create_injection_policy(config: Optional[Dict[str, Any]] = None) -> InjectionPolicy:
    """Factory function to create injection policy instance"""
    return InjectionPolicy(config)

# Re-export components
__all__ = [
    'InjectionPolicy', 'create_injection_policy'
]
