"""
Test suite for semantic cache safety and policy validation

Tests safety signature extraction, policy compliance checking, and security pattern
detection for both Resume Engine (RG) and Outreach Engine (LIC) engines.
"""

import json
import pytest
import tempfile
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project paths for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "schemas"))
sys.path.append(str(project_root / "runtime"))

from semantic_lineage import (
    EngineType, SafetySignature, SemanticLineageValidator
)
from semantic_scanner import SafetyExtractor


class TestSafetyExtractor:
    """Test safety signature extraction functionality"""
    
    def test_extract_basic_safety_patterns(self):
        """Test extraction of basic safety patterns"""
        safety_code = '''
def validate_input(data):
    """Validate user input"""
    if not data:
        return False
    sanitized_data = sanitize(data)
    return True

def sanitize(data):
    """Sanitize user data"""
    return data.strip()

def authenticate_user(token):
    """Authenticate user with token"""
    if verify_token(token):
        return get_user_permissions(token)
    return None

def encrypt_data(data):
    """Encrypt sensitive data"""
    return hash(data)

def process_pii(user_data):
    """Process personally identifiable information"""
    encrypted = encrypt_data(user_data.ssn)
    return encrypted
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(safety_code)
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Check safety checks
            assert "input_validation" in safety_signature.safety_checks
            assert "sanitization" in safety_signature.safety_checks
            
            # Check security patterns
            assert "cryptography" in safety_signature.security_patterns
            assert "auth" in safety_signature.security_patterns
            
            # Check data handling
            assert "sensitive_data" in safety_signature.data_handling
            
            # Check access controls
            assert "rbac" in safety_signature.access_controls
            
        finally:
            temp_path.unlink()
    
    def test_extract_gdpr_compliance(self):
        """Test extraction of GDPR compliance patterns"""
        gdpr_code = '''
def handle_user_request(user_data):
    """Handle user data request under GDPR"""
    if user_data.consent_given:
        process_lawfully(user_data)
        return user_data
    
def delete_user_data(user_id):
    """Delete user data per GDPR right to be forgotten"""
    user_data = find_user(user_id)
    if user_data:
        delete_from_all_systems(user_data)
        log_deletion_for_compliance(user_id)

def process_lawfully(data):
    """Process data lawfully under GDPR"""
    check_legal_basis(data)
    return data
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(gdpr_code)
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Should detect regulatory compliance
            assert any("gdpr" in pattern.lower() for pattern in safety_signature.policy_compliance)
            
        finally:
            temp_path.unlink()
    
    def test_extract_security_patterns(self):
        """Test extraction of security patterns"""
        security_code = '''
import hashlib
import jwt
from cryptography.fernet import Fernet

def hash_password(password):
    """Hash user password"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id):
    """Generate JWT token"""
    return jwt.encode({'user_id': user_id}, 'secret', algorithm='HS256')

def encrypt_sensitive_data(data):
    """Encrypt sensitive data"""
    key = Fernet.generate_key()
    f = Fernet(key)
    return f.encrypt(data.encode())

def verify_token(token):
    """Verify JWT token"""
    try:
        return jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(security_code)
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Should detect various security patterns
            assert "cryptography" in safety_signature.security_patterns
            assert "auth" in safety_signature.security_patterns
            
        finally:
            temp_path.unlink()
    
    def test_extract_access_controls(self):
        """Test extraction of access control patterns"""
        rbac_code = '''
def check_user_permission(user, resource):
    """Check if user has permission for resource"""
    user_role = get_user_role(user.id)
    required_permission = get_required_permission(resource)
    
    if role_has_permission(user_role, required_permission):
        return True
    return False

def get_user_role(user_id):
    """Get user's role"""
    return UserRole.query.filter_by(user_id=user_id).first()

def role_has_permission(role, permission):
    """Check if role has specific permission"""
    return permission in role.permissions

def authorize_access(user, action, resource):
    """Authorize user access to resource"""
    if check_user_permission(user, resource):
        log_access_attempt(user, action, resource, granted=True)
        return True
    else:
        log_access_attempt(user, action, resource, granted=False)
        return False
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(rbac_code)
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Should detect RBAC patterns
            assert "rbac" in safety_signature.access_controls
            
        finally:
            temp_path.unlink()
    
    def test_extract_empty_file(self):
        """Test safety extraction from empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Should return empty safety signature
            assert len(safety_signature.safety_checks) == 0
            assert len(safety_signature.policy_compliance) == 0
            assert len(safety_signature.security_patterns) == 0
            assert len(safety_signature.data_handling) == 0
            assert len(safety_signature.access_controls) == 0
            
        finally:
            temp_path.unlink()
    
    def test_extract_non_python_file(self):
        """Test safety extraction from non-Python file"""
        json_content = '''
{
    "api_endpoint": "https://api.example.com",
    "authentication": "bearer_token",
    "data_handling": "encrypted"
}
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = Path(f.name)
        
        try:
            safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
            
            # Should handle non-Python files gracefully
            assert isinstance(safety_signature, SafetySignature)
            
        finally:
            temp_path.unlink()
    
    def test_extract_error_handling(self):
        """Test extraction with file read errors"""
        non_existent_path = Path("/non/existent/file.py")
        
        # Should handle non-existent files gracefully
        safety_signature = SafetyExtractor.extract_safety_signature(non_existent_path)
        
        # Should return empty safety signature
        assert len(safety_signature.safety_checks) == 0
        assert len(safety_signature.policy_compliance) == 0


class TestSafetySignature:
    """Test safety signature functionality"""
    
    def test_safety_signature_creation(self):
        """Test creation of safety signatures"""
        signature = SafetySignature(
            safety_checks=["input_validation", "sanitization"],
            policy_compliance=["gdpr", "hipaa"],
            security_patterns=["cryptography", "auth"],
            data_handling=["sensitive_data", "pii"],
            access_controls=["rbac", "permissions"]
        )
        
        assert len(signature.safety_checks) == 2
        assert len(signature.policy_compliance) == 2
        assert len(signature.security_patterns) == 2
        assert len(signature.data_handling) == 2
        assert len(signature.access_controls) == 2
    
    def test_safety_signature_serialization(self):
        """Test safety signature serialization"""
        signature = SafetySignature(
            safety_checks=["validation"],
            policy_compliance=["gdpr"],
            security_patterns=["crypto"],
            data_handling=["pii"],
            access_controls=["rbac"]
        )
        
        signature_dict = signature.to_dict()
        
        assert signature_dict["safety_checks"] == ["validation"]
        assert signature_dict["policy_compliance"] == ["gdpr"]
        assert signature_dict["security_patterns"] == ["crypto"]
        assert signature_dict["data_handling"] == ["pii"]
        assert signature_dict["access_controls"] == ["rbac"]
    
    def test_safety_signature_empty(self):
        """Test empty safety signature"""
        signature = SafetySignature([], [], [], [], [])
        
        assert len(signature.safety_checks) == 0
        assert len(signature.policy_compliance) == 0
        assert len(signature.security_patterns) == 0
        assert len(signature.data_handling) == 0
        assert len(signature.access_controls) == 0


class TestSafetyValidation:
    """Test safety validation functionality"""
    
    def test_validate_safety_signature_comprehensive(self):
        """Test validation of comprehensive safety signature"""
        signature = SafetySignature(
            safety_checks=["input_validation", "output_validation", "error_handling"],
            policy_compliance=["gdpr", "sox"],
            security_patterns=["encryption", "authentication", "authorization"],
            data_handling=["pii_encryption", "data_minimization"],
            access_controls=["rbac", "audit_logging"]
        )
        
        # A comprehensive safety signature should be valid
        assert len(signature.safety_checks) >= 2
        assert len(signature.security_patterns) >= 2
        assert len(signature.access_controls) >= 1
    
    def test_validate_safety_signature_minimal(self):
        """Test validation of minimal safety signature"""
        signature = SafetySignature(
            safety_checks=["input_validation"],
            policy_compliance=[],
            security_patterns=[],
            data_handling=[],
            access_controls=[]
        )
        
        # Even minimal safety signature should be valid
        assert len(signature.safety_checks) >= 1
    
    def test_validate_safety_signature_empty(self):
        """Test validation of empty safety signature"""
        signature = SafetySignature([], [], [], [], [])
        
        # Empty safety signature is technically valid but might indicate missing safety measures
        assert len(signature.safety_checks) == 0
        assert len(signature.policy_compliance) == 0
        assert len(signature.security_patterns) == 0
        assert len(signature.data_handling) == 0
        assert len(signature.access_controls) == 0


class TestPolicyComplianceDetection:
    """Test policy compliance detection"""
    
    def test_detect_gdpr_compliance(self):
        """Test GDPR compliance detection"""
        gdpr_patterns = [
            "def handle_gdpr_request():",
            "def process_lawfully():",
            "def delete_user_data():",
            "def obtain_consent():",
            "# GDPR compliance",
            "if user_consent_given:",
            "data_protection_officer"
        ]
        
        for pattern in gdpr_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect GDPR compliance
                assert any("gdpr" in compliance.lower() for compliance in safety_signature.policy_compliance), \
                    f"Failed to detect GDPR in pattern: {pattern}"
                
            finally:
                temp_path.unlink()
    
    def test_detect_hipaa_compliance(self):
        """Test HIPAA compliance detection"""
        hipaa_patterns = [
            "def handle_phi():",
            "def protect_health_info():",
            "# HIPAA compliance",
            "medical_record",
            "protected_health_info",
            "hipaa_audit_log"
        ]
        
        for pattern in hipaa_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect HIPAA compliance
                assert any("hipaa" in compliance.lower() for compliance in safety_signature.policy_compliance), \
                    f"Failed to detect HIPAA in pattern: {pattern}"
                
            finally:
                temp_path.unlink()
    
    def test_detect_sox_compliance(self):
        """Test SOX compliance detection"""
        sox_patterns = [
            "def financial_audit():",
            "# SOX compliance",
            "sarbanes_oxley",
            "financial_reporting",
            "audit_trail"
        ]
        
        for pattern in sox_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect SOX compliance
                assert any("sox" in compliance.lower() for compliance in safety_signature.policy_compliance), \
                    f"Failed to detect SOX in pattern: {pattern}"
                
            finally:
                temp_path.unlink()


class TestSecurityPatternDetection:
    """Test security pattern detection"""
    
    def test_detect_encryption_patterns(self):
        """Test encryption pattern detection"""
        encryption_patterns = [
            "import hashlib",
            "from cryptography import",
            "def encrypt_data():",
            "def decrypt_data():",
            "hashlib.sha256",
            "Fernet.encrypt"
        ]
        
        for pattern in encryption_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect cryptography
                assert "cryptography" in safety_signature.security_patterns, \
                    f"Failed to detect cryptography in pattern: {pattern}"
                
            finally:
                temp_path.unlink()
    
    def test_detect_authentication_patterns(self):
        """Test authentication pattern detection"""
        auth_patterns = [
            "def authenticate():",
            "def login():",
            "def verify_token():",
            "def check_credentials():",
            "jwt.encode",
            "authenticate_user"
        ]
        
        for pattern in auth_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect authentication
                assert "auth" in safety_signature.security_patterns, \
                    f"Failed to detect auth in pattern: {pattern}"
                
            finally:
                temp_path.unlink()


class TestDataHandlingDetection:
    """Test data handling detection"""
    
    def test_detect_pii_handling(self):
        """Test PII handling detection"""
        pii_patterns = [
            "def process_ssn():",
            "def handle_credit_card():",
            "def process_pii():",
            "personal_data",
            "sensitive_info",
            "user_privacy"
        ]
        
        for pattern in pii_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect sensitive data handling
                assert "sensitive_data" in safety_signature.data_handling, \
                    f"Failed to detect sensitive_data in pattern: {pattern}"
                
            finally:
                temp_path.unlink()


class TestAccessControlDetection:
    """Test access control detection"""
    
    def test_detect_rbac_patterns(self):
        """Test RBAC pattern detection"""
        rbac_patterns = [
            "def check_permission():",
            "def authorize_access():",
            "user_role",
            "role_based_access",
            "permission_check",
            "access_granted"
        ]
        
        for pattern in rbac_patterns:
            code = f'''
{pattern}
def main():
    pass
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = Path(f.name)
            
            try:
                safety_signature = SafetyExtractor.extract_safety_signature(temp_path)
                
                # Should detect RBAC
                assert "rbac" in safety_signature.access_controls, \
                    f"Failed to detect rbac in pattern: {pattern}"
                
            finally:
                temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
