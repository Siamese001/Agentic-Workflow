#!/usr/bin/env python3
"""
Data Validators
Section 14: Security Layer - Data validation components for safety compliance
"""

from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class DataValidator:
    """Validator for data safety and compliance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validation_rules = self._load_validation_rules()
        self.strict_mode = self.config.get("strict_mode", False)
    
    def validate_data_safety(self, data: Dict[str, Any], data_type: str = "general") -> Dict[str, Any]:
        """Validate data for safety compliance"""
        try:
            validation_result = {
                "is_valid": True,
                "validation_errors": [],
                "warnings": [],
                "sanitized_data": data.copy(),
                "compliance_score": 1.0
            }
            
            # Apply data type specific validation
            if data_type == "resume":
                validation_result = self._validate_resume_data(data, validation_result)
            elif data_type == "contact":
                validation_result = self._validate_contact_data(data, validation_result)
            else:
                validation_result = self._validate_general_data(data, validation_result)
            
            # Apply common validation rules
            validation_result = self._apply_common_rules(data, validation_result)
            
            # Calculate compliance score
            validation_result["compliance_score"] = self._calculate_compliance_score(validation_result)
            
            logger.info(f"Data validation completed: {'Valid' if validation_result['is_valid'] else 'Invalid'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return {"is_valid": False, "error": str(e), "compliance_score": 0.0}
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load data validation rules"""
        return {
            "max_field_length": 10000,
            "allowed_file_types": [".txt", ".pdf", ".doc", ".docx"],
            "required_fields": {
                "resume": ["name", "contact"],
                "contact": ["email"]
            },
            "blocked_patterns": [
                r"password",
                r"secret",
                r"token",
                r"api_key"
            ]
        }
    
    def _validate_resume_data(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate resume-specific data"""
        required_fields = self.validation_rules["required_fields"].get("resume", [])
        
        for field in required_fields:
            if field not in data or not data[field]:
                result["validation_errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False
        
        # Validate personal information
        personal_fields = ["email", "phone", "address"]
        for field in personal_fields:
            if field in data:
                validation = self._validate_personal_field(field, data[field])
                if not validation["is_valid"]:
                    result["validation_errors"].extend(validation["errors"])
                    result["is_valid"] = False
        
        return result
    
    def _validate_contact_data(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contact-specific data"""
        required_fields = self.validation_rules["required_fields"].get("contact", [])
        
        for field in required_fields:
            if field not in data or not data[field]:
                result["validation_errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False
        
        # Email validation
        if "email" in data:
            if not self._is_valid_email(data["email"]):
                result["validation_errors"].append("Invalid email format")
                result["is_valid"] = False
        
        return result
    
    def _validate_general_data(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate general data"""
        # Check field lengths
        for key, value in data.items():
            if isinstance(value, str):
                if len(value) > self.validation_rules["max_field_length"]:
                    result["validation_errors"].append(f"Field {key} exceeds maximum length")
                    if self.strict_mode:
                        result["is_valid"] = False
                    else:
                        result["warnings"].append(f"Field {key} is very long")
        
        return result
    
    def _apply_common_rules(self, data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply common validation rules"""
        def scan_for_blocked_patterns(obj: Any, path: str = ""):
            if isinstance(obj, str):
                for pattern in self.validation_rules["blocked_patterns"]:
                    if re.search(pattern, obj, re.IGNORECASE):
                        result["validation_errors"].append(f"Blocked pattern found in {path}: {pattern}")
                        result["is_valid"] = False
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    scan_for_blocked_patterns(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    scan_for_blocked_patterns(item, new_path)
        
        scan_for_blocked_patterns(data)
        return result
    
    def _validate_personal_field(self, field: str, value: str) -> Dict[str, Any]:
        """Validate personal information fields"""
        result = {"is_valid": True, "errors": []}
        
        if field == "email":
            if not self._is_valid_email(value):
                result["is_valid"] = False
                result["errors"].append("Invalid email format")
        elif field == "phone":
            if not self._is_valid_phone(value):
                result["is_valid"] = False
                result["errors"].append("Invalid phone format")
        
        return result
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format"""
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10 and len(digits) <= 15
    
    def _calculate_compliance_score(self, result: Dict[str, Any]) -> float:
        """Calculate data compliance score"""
        if not result["is_valid"]:
            return 0.0
        
        error_count = len(result["validation_errors"])
        warning_count = len(result["warnings"])
        
        # Simple scoring: 1.0 minus penalties for errors and warnings
        score = 1.0 - (error_count * 0.2) - (warning_count * 0.05)
        return max(0.0, score)
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data by removing sensitive information"""
        sanitized = data.copy()
        
        def remove_sensitive(obj: Any):
            if isinstance(obj, dict):
                keys_to_remove = []
                for key, value in obj.items():
                    if self._is_sensitive_field(key):
                        keys_to_remove.append(key)
                    else:
                        obj[key] = remove_sensitive(value)
                
                for key in keys_to_remove:
                    del obj[key]
            elif isinstance(obj, list):
                return [remove_sensitive(item) for item in obj]
            
            return obj
        
        return remove_sensitive(sanitized)
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive information"""
        sensitive_keywords = ["password", "secret", "token", "key", "credential"]
        return any(keyword in field_name.lower() for keyword in sensitive_keywords)

def validate_data_safety(data: Dict[str, Any], data_type: str = "general", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to validate data safety"""
    validator = DataValidator(config)
    return validator.validate_data_safety(data, data_type)

# Re-export components
__all__ = [
    'DataValidator', 'validate_data_safety'
]
