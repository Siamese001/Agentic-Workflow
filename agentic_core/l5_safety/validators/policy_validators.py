#!/usr/bin/env python3
"""
Policy Validators
Section 14: Security Layer - Policy validation components for safety compliance
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PolicyValidator:
    """Validator for policy compliance and enforcement"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.policy_rules = self._load_policy_rules()
        self.enforcement_mode = self.config.get("enforcement_mode", "warn")
    
    def validate_policy_compliance(self, action_data: Dict[str, Any], policy_type: str = "general") -> Dict[str, Any]:
        """Validate action against policy compliance"""
        try:
            validation_result = {
                "is_compliant": True,
                "policy_violations": [],
                "warnings": [],
                "required_actions": [],
                "compliance_level": "full"
            }
            
            # Apply policy type specific validation
            if policy_type == "data_access":
                validation_result = self._validate_data_access_policy(action_data, validation_result)
            elif policy_type == "usage":
                validation_result = self._validate_usage_policy(action_data, validation_result)
            elif policy_type == "security":
                validation_result = self._validate_security_policy(action_data, validation_result)
            else:
                validation_result = self._validate_general_policy(action_data, validation_result)
            
            # Determine compliance level
            validation_result["compliance_level"] = self._determine_compliance_level(validation_result)
            
            logger.info(f"Policy validation completed: {validation_result['compliance_level']} compliance")
            return validation_result
            
        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            return {"is_compliant": False, "error": str(e), "compliance_level": "failed"}
    
    def _load_policy_rules(self) -> Dict[str, Any]:
        """Load policy validation rules"""
        return {
            "data_access": {
                "required_permissions": ["read", "write"],
                "restricted_fields": ["ssn", "password", "api_key"],
                "audit_required": True
            },
            "usage": {
                "allowed_purposes": ["business", "research", "analysis"],
                "max_requests_per_hour": 100,
                "retention_period_days": 365
            },
            "security": {
                "min_encryption_level": "AES-256",
                "required_authentication": True,
                "session_timeout_minutes": 30
            },
            "general": {
                "max_data_size_mb": 100,
                "allowed_file_types": [".txt", ".pdf", ".doc", ".docx"],
                "require_consent": True
            }
        }
    
    def _validate_data_access_policy(self, action_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data access policy compliance"""
        rules = self.policy_rules["data_access"]
        
        # Check required permissions
        permissions = action_data.get("permissions", [])
        required_perms = rules["required_permissions"]
        
        for perm in required_perms:
            if perm not in permissions:
                result["policy_violations"].append(f"Missing required permission: {perm}")
                result["is_compliant"] = False
        
        # Check restricted field access
        requested_fields = action_data.get("requested_fields", [])
        restricted_fields = rules["restricted_fields"]
        
        for field in requested_fields:
            if field in restricted_fields:
                result["policy_violations"].append(f"Access to restricted field: {field}")
                result["is_compliant"] = False
                result["required_actions"].append(f"Request explicit approval for {field} access")
        
        # Check audit requirements
        if rules["audit_required"] and not action_data.get("audit_enabled", False):
            result["warnings"].append("Audit logging should be enabled for data access")
            if self.enforcement_mode == "strict":
                result["required_actions"].append("Enable audit logging")
        
        return result
    
    def _validate_usage_policy(self, action_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate usage policy compliance"""
        rules = self.policy_rules["usage"]
        
        # Check purpose compliance
        purpose = action_data.get("purpose", "").lower()
        allowed_purposes = [p.lower() for p in rules["allowed_purposes"]]
        
        if purpose not in allowed_purposes:
            result["policy_violations"].append(f"Usage purpose not allowed: {purpose}")
            result["is_compliant"] = False
        
        # Check request frequency
        user_id = action_data.get("user_id", "")
        if user_id:
            current_requests = self._get_user_request_count(user_id)
            max_requests = rules["max_requests_per_hour"]
            
            if current_requests >= max_requests:
                result["policy_violations"].append(f"Request limit exceeded: {current_requests}/{max_requests}")
                result["is_compliant"] = False
                result["required_actions"].append("Wait before making additional requests")
        
        # Check retention policy
        data_age_days = action_data.get("data_age_days", 0)
        max_retention = rules["retention_period_days"]
        
        if data_age_days > max_retention:
            result["warnings"].append(f"Data exceeds retention period: {data_age_days} days")
            result["required_actions"].append("Consider data deletion or archival")
        
        return result
    
    def _validate_security_policy(self, action_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security policy compliance"""
        rules = self.policy_rules["security"]
        
        # Check encryption requirements
        encryption_level = action_data.get("encryption_level", "")
        min_encryption = rules["min_encryption_level"]
        
        if encryption_level and encryption_level < min_encryption:
            result["policy_violations"].append(f"Encryption level too low: {encryption_level} < {min_encryption}")
            result["is_compliant"] = False
            result["required_actions"].append(f"Upgrade encryption to {min_encryption}")
        
        # Check authentication
        if rules["required_authentication"] and not action_data.get("authenticated", False):
            result["policy_violations"].append("Authentication required but not provided")
            result["is_compliant"] = False
            result["required_actions"].append("Authenticate before proceeding")
        
        # Check session timeout
        session_age = action_data.get("session_age_minutes", 0)
        max_session_age = rules["session_timeout_minutes"]
        
        if session_age > max_session_age:
            result["policy_violations"].append(f"Session expired: {session_age} > {max_session_age} minutes")
            result["is_compliant"] = False
            result["required_actions"].append("Re-authenticate to continue")
        
        return result
    
    def _validate_general_policy(self, action_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate general policy compliance"""
        rules = self.policy_rules["general"]
        
        # Check data size limits
        data_size_mb = action_data.get("data_size_mb", 0)
        max_size = rules["max_data_size_mb"]
        
        if data_size_mb > max_size:
            result["policy_violations"].append(f"Data size exceeds limit: {data_size_mb}MB > {max_size}MB")
            result["is_compliant"] = False
            result["required_actions"].append("Reduce data size or request exception")
        
        # Check file type restrictions
        file_types = action_data.get("file_types", [])
        allowed_types = rules["allowed_file_types"]
        
        for file_type in file_types:
            if file_type not in allowed_types:
                result["warnings"].append(f"File type may be restricted: {file_type}")
        
        # Check consent requirements
        if rules["require_consent"] and not action_data.get("consent_obtained", False):
            result["policy_violations"].append("Consent required but not obtained")
            result["is_compliant"] = False
            result["required_actions"].append("Obtain proper consent before proceeding")
        
        return result
    
    def _determine_compliance_level(self, result: Dict[str, Any]) -> str:
        """Determine overall compliance level"""
        if not result["is_compliant"]:
            return "failed"
        elif result["policy_violations"]:
            return "partial"
        elif result["warnings"]:
            return "partial_with_warnings"
        else:
            return "full"
    
    def _get_user_request_count(self, user_id: str) -> int:
        """Get current request count for user (simplified implementation)"""
        # In production, would query actual usage database
        return 0
    
    def get_policy_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate policy compliance summary"""
        return {
            "compliance_level": validation_result.get("compliance_level", "unknown"),
            "violations_count": len(validation_result.get("policy_violations", [])),
            "warnings_count": len(validation_result.get("warnings", [])),
            "required_actions_count": len(validation_result.get("required_actions", [])),
            "is_compliant": validation_result.get("is_compliant", False)
        }
    
    def update_policy_rules(self, new_rules: Dict[str, Any]) -> bool:
        """Update policy validation rules"""
        try:
            self.policy_rules.update(new_rules)
            logger.info("Policy rules updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update policy rules: {e}")
            return False

def validate_policy_compliance(action_data: Dict[str, Any], policy_type: str = "general", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to validate policy compliance"""
    validator = PolicyValidator(config)
    return validator.validate_policy_compliance(action_data, policy_type)

# Re-export components
__all__ = [
    'PolicyValidator', 'validate_policy_compliance'
]





