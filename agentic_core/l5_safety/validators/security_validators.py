#!/usr/bin/env python3
"""
Security Validators
Section 14: Security Layer - Security validation components for safety compliance
"""

from typing import Dict, Any, List, Optional
import logging
import re
import hashlib

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validator for security measures and compliance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.security_rules = self._load_security_rules()
        self.strict_mode = self.config.get("strict_mode", False)
    
    def validate_security_measures(self, security_data: Dict[str, Any], context: str = "general") -> Dict[str, Any]:
        """Validate security measures and compliance"""
        try:
            validation_result = {
                "is_secure": True,
                "security_issues": [],
                "warnings": [],
                "security_score": 1.0,
                "recommendations": []
            }
            
            # Apply context-specific validation
            if context == "authentication":
                validation_result = self._validate_authentication(security_data, validation_result)
            elif context == "encryption":
                validation_result = self._validate_encryption(security_data, validation_result)
            elif context == "access_control":
                validation_result = self._validate_access_control(security_data, validation_result)
            else:
                validation_result = self._validate_general_security(security_data, validation_result)
            
            # Calculate security score
            validation_result["security_score"] = self._calculate_security_score(validation_result)
            
            # Generate recommendations
            validation_result["recommendations"] = self._generate_security_recommendations(validation_result)
            
            logger.info(f"Security validation completed: Score {validation_result['security_score']:.2f}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {"is_secure": False, "error": str(e), "security_score": 0.0}
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security validation rules"""
        return {
            "password_requirements": {
                "min_length": 8,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True
            },
            "encryption_requirements": {
                "min_key_length": 256,
                "allowed_algorithms": ["AES", "RSA", "ChaCha20"],
                "require_salt": True
            },
            "session_requirements": {
                "max_duration_minutes": 30,
                "require_https": True,
                "require_csrf_token": True
            },
            "general_requirements": {
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "require_audit_log": True
            }
        }
    
    def _validate_authentication(self, auth_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate authentication security measures"""
        rules = self.security_rules["password_requirements"]
        
        # Password validation
        if "password" in auth_data:
            password = auth_data["password"]
            password_issues = self._validate_password(password, rules)
            
            if password_issues:
                result["security_issues"].extend(password_issues)
                result["is_secure"] = False
        
        # Multi-factor authentication
        if not auth_data.get("mfa_enabled", False):
            result["warnings"].append("Multi-factor authentication not enabled")
            if self.strict_mode:
                result["security_issues"].append("MFA required in strict mode")
                result["is_secure"] = False
        
        # Account lockout validation
        failed_attempts = auth_data.get("failed_login_attempts", 0)
        max_attempts = self.security_rules["general_requirements"]["max_login_attempts"]
        
        if failed_attempts >= max_attempts:
            result["security_issues"].append(f"Account locked: {failed_attempts} failed attempts")
            result["is_secure"] = False
        
        return result
    
    def _validate_encryption(self, encrypt_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate encryption security measures"""
        rules = self.security_rules["encryption_requirements"]
        
        # Algorithm validation
        algorithm = encrypt_data.get("algorithm", "")
        if algorithm not in rules["allowed_algorithms"]:
            result["security_issues"].append(f"Encryption algorithm not allowed: {algorithm}")
            result["is_secure"] = False
        
        # Key length validation
        key_length = encrypt_data.get("key_length", 0)
        if key_length < rules["min_key_length"]:
            result["security_issues"].append(f"Key length too short: {key_length} < {rules['min_key_length']}")
            result["is_secure"] = False
        
        # Salt validation
        if rules["require_salt"] and not encrypt_data.get("salt_used", False):
            result["security_issues"].append("Salt not used for encryption")
            result["is_secure"] = False
        
        return result
    
    def _validate_access_control(self, access_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate access control security measures"""
        # Role-based access control
        if not access_data.get("rbac_enabled", False):
            result["warnings"].append("Role-based access control not implemented")
        
        # Principle of least privilege
        if not access_data.get("least_privilege", False):
            result["warnings"].append("Principle of least privilege not enforced")
        
        # Access log validation
        if not access_data.get("access_logging", False):
            result["security_issues"].append("Access logging not enabled")
            result["is_secure"] = False
        
        # Permission validation
        permissions = access_data.get("permissions", [])
        if not permissions:
            result["security_issues"].append("No permissions defined")
            result["is_secure"] = False
        
        return result
    
    def _validate_general_security(self, security_data: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate general security measures"""
        # HTTPS requirement
        if not security_data.get("https_enabled", False):
            result["security_issues"].append("HTTPS not enabled")
            result["is_secure"] = False
        
        # Security headers
        required_headers = ["X-Frame-Options", "X-Content-Type-Options", "X-XSS-Protection"]
        headers = security_data.get("security_headers", [])
        
        for header in required_headers:
            if header not in headers:
                result["warnings"].append(f"Security header missing: {header}")
        
        # Input validation
        if not security_data.get("input_validation", False):
            result["security_issues"].append("Input validation not implemented")
            result["is_secure"] = False
        
        # Rate limiting
        if not security_data.get("rate_limiting", False):
            result["warnings"].append("Rate limiting not implemented")
        
        return result
    
    def _validate_password(self, password: str, rules: Dict[str, Any]) -> List[str]:
        """Validate password against security requirements"""
        issues = []
        
        # Length check
        if len(password) < rules["min_length"]:
            issues.append(f"Password too short: {len(password)} < {rules['min_length']}")
        
        # Uppercase check
        if rules["require_uppercase"] and not re.search(r'[A-Z]', password):
            issues.append("Password must contain uppercase letters")
        
        # Lowercase check
        if rules["require_lowercase"] and not re.search(r'[a-z]', password):
            issues.append("Password must contain lowercase letters")
        
        # Numbers check
        if rules["require_numbers"] and not re.search(r'\d', password):
            issues.append("Password must contain numbers")
        
        # Special characters check
        if rules["require_special_chars"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain special characters")
        
        return issues
    
    def _calculate_security_score(self, result: Dict[str, Any]) -> float:
        """Calculate security compliance score"""
        if not result["is_secure"]:
            return 0.0
        
        issue_count = len(result["security_issues"])
        warning_count = len(result["warnings"])
        
        # Simple scoring: 1.0 minus penalties for issues and warnings
        score = 1.0 - (issue_count * 0.3) - (warning_count * 0.1)
        return max(0.0, score)
    
    def _generate_security_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if result["security_issues"]:
            recommendations.append("Address all security issues immediately")
        
        if result["warnings"]:
            recommendations.append("Review and address security warnings")
        
        # General recommendations
        recommendations.extend([
            "Implement regular security audits",
            "Keep security dependencies updated",
            "Monitor security logs regularly",
            "Conduct security training for users"
        ])
        
        return recommendations
    
    def generate_security_hash(self, data: str, algorithm: str = "sha256") -> str:
        """Generate security hash for data"""
        try:
            if algorithm.lower() == "sha256":
                return hashlib.sha256(data.encode()).hexdigest()
            elif algorithm.lower() == "md5":
                return hashlib.md5(data.encode()).hexdigest()
            else:
                return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            return ""
    
    def validate_integrity(self, data: str, expected_hash: str, algorithm: str = "sha256") -> bool:
        """Validate data integrity using hash comparison"""
        try:
            actual_hash = self.generate_security_hash(data, algorithm)
            return actual_hash == expected_hash
        except Exception as e:
            logger.error(f"Integrity validation failed: {e}")
            return False
    
    def get_security_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security compliance summary"""
        return {
            "security_status": "Secure" if validation_result.get("is_secure", False) else "Insecure",
            "security_score": validation_result.get("security_score", 0.0),
            "issues_count": len(validation_result.get("security_issues", [])),
            "warnings_count": len(validation_result.get("warnings", [])),
            "recommendations_count": len(validation_result.get("recommendations", []))
        }
    
    def update_security_rules(self, new_rules: Dict[str, Any]) -> bool:
        """Update security validation rules"""
        try:
            self.security_rules.update(new_rules)
            logger.info("Security rules updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update security rules: {e}")
            return False

def validate_security_measures(security_data: Dict[str, Any], context: str = "general", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to validate security measures"""
    validator = SecurityValidator(config)
    return validator.validate_security_measures(security_data, context)

# Re-export components
__all__ = [
    'SecurityValidator', 'validate_security_measures'
]





