#!/usr/bin/env python3
"""
Data Privacy Policies
Section 14: Security Layer - Privacy protection policies for resume data
"""

from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

class DataPrivacyPolicy:
    """Policy manager for resume data privacy protection"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.allowed_fields = self.config.get("allowed_fields", set())
        self.redaction_enabled = self.config.get("redaction_enabled", True)
    
    def validate_resume_privacy(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume data for privacy compliance"""
        try:
            validation_result = {
                "is_compliant": True,
                "privacy_issues": [],
                "sensitive_data_found": [],
                "recommendations": []
            }
            
            # Check for sensitive information
            sensitive_items = self._scan_for_sensitive_data(resume_data)
            if sensitive_items:
                validation_result["sensitive_data_found"] = sensitive_items
                validation_result["is_compliant"] = False
                validation_result["privacy_issues"].append("Sensitive personal data detected")
            
            # Validate field access
            field_issues = self._validate_field_access(resume_data)
            if field_issues:
                validation_result["privacy_issues"].extend(field_issues)
                validation_result["is_compliant"] = False
            
            # Generate recommendations
            validation_result["recommendations"] = self._generate_privacy_recommendations(validation_result)
            
            logger.info(f"Privacy validation completed: {'Compliant' if validation_result['is_compliant'] else 'Non-compliant'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Privacy validation failed: {e}")
            return {"is_compliant": False, "error": str(e)}
    
    def _load_sensitive_patterns(self) -> List[Dict[str, Any]]:
        """Load patterns for detecting sensitive information"""
        return [
            {
                "type": "ssn",
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "description": "Social Security Number",
                "severity": "high"
            },
            {
                "type": "phone",
                "pattern": r'\b\d{3}-\d{3}-\d{4}\b',
                "description": "Phone Number",
                "severity": "medium"
            },
            {
                "type": "email",
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "description": "Email Address",
                "severity": "medium"
            },
            {
                "type": "address",
                "pattern": r'\b\d+\s+([A-Z][a-z]*\s*)+\b',
                "description": "Street Address",
                "severity": "medium"
            },
            {
                "type": "credit_card",
                "pattern": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "description": "Credit Card Number",
                "severity": "high"
            },
            {
                "type": "bank_account",
                "pattern": r'\b\d{9,18}\b',
                "description": "Bank Account Number",
                "severity": "high"
            }
        ]
    
    def _scan_for_sensitive_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan data for sensitive information patterns"""
        sensitive_items = []
        
        def scan_text(text: str, field_path: str):
            for pattern_info in self.sensitive_patterns:
                matches = re.findall(pattern_info["pattern"], text)
                if matches:
                    sensitive_items.append({
                        "type": pattern_info["type"],
                        "description": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "field": field_path,
                        "matches": matches[:3]  # Limit to first 3 matches
                    })
        
        def recursive_scan(obj: Any, path: str = ""):
            if isinstance(obj, str):
                scan_text(obj, path)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    recursive_scan(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    recursive_scan(item, new_path)
        
        recursive_scan(data)
        return sensitive_items
    
    def _validate_field_access(self, data: Dict[str, Any]) -> List[str]:
        """Validate that only allowed fields are accessed"""
        issues = []
        
        if self.allowed_fields:
            def check_fields(obj: Any, path: str = ""):
                if isinstance(obj, dict):
                    for key in obj.keys():
                        field_path = f"{path}.{key}" if path else key
                        if key not in self.allowed_fields and not key.startswith("_"):
                            issues.append(f"Unauthorized field access: {field_path}")
                        check_fields(obj[key], field_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_fields(item, f"{path}[{i}]" if path else f"[{i}]")
            
            check_fields(data)
        
        return issues
    
    def _generate_privacy_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate privacy improvement recommendations"""
        recommendations = []
        
        if validation_result["sensitive_data_found"]:
            recommendations.append("Remove or redact sensitive personal information")
            recommendations.append("Implement data masking for PII fields")
        
        if any("field access" in issue for issue in validation_result["privacy_issues"]):
            recommendations.append("Review and restrict field access permissions")
        
        if not self.redaction_enabled:
            recommendations.append("Enable automatic data redaction")
        
        # General recommendations
        recommendations.extend([
            "Implement data retention policies",
            "Use encryption for stored resume data",
            "Establish audit logging for data access"
        ])
        
        return recommendations
    
    def redact_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from data"""
        if not self.redaction_enabled:
            return data
        
        def redact_text(text: str) -> str:
            redacted = text
            for pattern_info in self.sensitive_patterns:
                if pattern_info["severity"] in ["high", "medium"]:
                    redacted = re.sub(pattern_info["pattern"], "[REDACTED]", redacted)
            return redacted
        
        def recursive_redact(obj: Any):
            if isinstance(obj, str):
                return redact_text(obj)
            elif isinstance(obj, dict):
                return {key: recursive_redact(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [recursive_redact(item) for item in obj]
            else:
                return obj
        
        return recursive_redact(data)
    
    def get_privacy_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate privacy compliance summary"""
        return {
            "compliance_status": "Compliant" if validation_result.get("is_compliant", False) else "Non-compliant",
            "issues_found": len(validation_result.get("privacy_issues", [])),
            "sensitive_items": len(validation_result.get("sensitive_data_found", [])),
            "high_severity_count": len([item for item in validation_result.get("sensitive_data_found", []) if item.get("severity") == "high"]),
            "recommendations_count": len(validation_result.get("recommendations", []))
        }

def validate_resume_privacy(resume_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to validate resume privacy"""
    policy = DataPrivacyPolicy(config)
    return policy.validate_resume_privacy(resume_data)

# Re-export components
__all__ = [
    'DataPrivacyPolicy', 'validate_resume_privacy'
]
