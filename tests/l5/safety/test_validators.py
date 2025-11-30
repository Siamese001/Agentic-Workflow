"""
Contract-level tests for Safety Validators (L5)
Tests validation logic and rule enforcement
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual safety validators when available
try:
    from agentic_core.l5_safety.validators.safety_validator import SafetyValidator
    from agentic_core.l5_safety.validators.schema_validator import SchemaValidator
    from agentic_core.l5_safety.validators.rule_validator import RuleValidator
except ImportError:
    SafetyValidator = SchemaValidator = RuleValidator = Mock


class TestSafetyValidatorsContracts:
    """Test safety validators contracts at L5 boundary"""
    
    def test_safety_validator_initialization_contract(self):
        """Test safety validator initializes with required configuration"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        config = {"strict_mode": True, "validation_level": "high"}
        validator = SafetyValidator(config)
        
        assert hasattr(validator, 'validate')
        assert hasattr(validator, 'check_safety_rules')
        assert hasattr(validator, 'get_validation_result')
        assert hasattr(validator, 'update_rules')
    
    def test_safety_validator_rule_checking_contract(self):
        """Test safety validator checks rules correctly"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({
            "rules": [
                {"type": "no_personal_data", "enabled": True},
                {"type": "no_harmful_content", "enabled": True},
                {"type": "professional_language", "enabled": True}
            ]
        })
        
        # Test content with personal data
        content_with_pii = {
            "text": "My email is john@example.com and my SSN is 123-45-6789",
            "context": {"type": "resume"}
        }
        
        result = validator.validate(content_with_pii)
        
        # Should detect personal data violation
        assert result["valid"] is False
        assert "violations" in result
        assert any(v["rule"] == "no_personal_data" for v in result["violations"])
    
    def test_safety_validator_safe_content_contract(self):
        """Test safety validator allows safe content"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({"validation_level": "medium"})
        
        safe_content = {
            "text": "I am a senior software engineer with expertise in Python and machine learning.",
            "context": {"type": "professional_summary"}
        }
        
        result = validator.validate(safe_content)
        
        # Should allow professional content
        assert result["valid"] is True
        assert "violations" not in result or len(result.get("violations", [])) == 0
        assert result["confidence_score"] > 0.8
    
    def test_safety_validator_context_awareness_contract(self):
        """Test safety validator considers context"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({})
        
        # Same content, different contexts
        content = "I have access to sensitive user data"
        
        # In professional context, might be acceptable
        professional_context = {
            "text": content,
            "context": {"type": "job_description", "role": "data_engineer"}
        }
        
        # In suspicious context, should be flagged
        suspicious_context = {
            "text": content,
            "context": {"type": "personal_message", "sender": "unknown"}
        }
        
        professional_result = validator.validate(professional_context)
        suspicious_result = validator.validate(suspicious_context)
        
        # Context should affect validation
        assert professional_result["valid"] is True
        assert suspicious_result["valid"] is False
    
    def test_schema_validator_initialization_contract(self):
        """Test schema validator initializes with required configuration"""
        if SchemaValidator is Mock:
            pytest.skip("SchemaValidator not implemented")
        
        config = {"strict_validation": True, "allow_extra_fields": False}
        validator = SchemaValidator(config)
        
        assert hasattr(validator, 'validate_schema')
        assert hasattr(validator, 'check_required_fields')
        assert hasattr(validator, 'validate_types')
    
    def test_schema_validator_required_fields_contract(self):
        """Test schema validator validates required fields"""
        if SchemaValidator is Mock:
            pytest.skip("SchemaValidator not implemented")
        
        schema = {
            "type": "object",
            "required": ["name", "email", "experience"],
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "experience": {"type": "integer"}
            }
        }
        
        validator = SchemaValidator({"schema": schema})
        
        # Valid input
        valid_input = {
            "name": "John Doe",
            "email": "john@example.com",
            "experience": 5
        }
        
        result = validator.validate_schema(valid_input)
        assert result["valid"] is True
        
        # Missing required field
        invalid_input = {
            "name": "John Doe",
            "email": "john@example.com"
            # Missing experience
        }
        
        result = validator.validate_schema(invalid_input)
        assert result["valid"] is False
        assert "missing_fields" in result
        assert "experience" in result["missing_fields"]
    
    def test_schema_validator_type_validation_contract(self):
        """Test schema validator validates data types"""
        if SchemaValidator is Mock:
            pytest.skip("SchemaValidator not implemented")
        
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer"},
                "name": {"type": "string"},
                "active": {"type": "boolean"},
                "skills": {"type": "array"}
            }
        }
        
        validator = SchemaValidator({"schema": schema})
        
        # Type violations
        invalid_input = {
            "age": "thirty",  # Should be integer
            "name": 123,      # Should be string
            "active": "true", # Should be boolean
            "skills": "python" # Should be array
        }
        
        result = validator.validate_schema(invalid_input)
        assert result["valid"] is False
        assert "type_errors" in result
        assert len(result["type_errors"]) == 4
    
    def test_rule_validator_initialization_contract(self):
        """Test rule validator initializes with required configuration"""
        if RuleValidator is Mock:
            pytest.skip("RuleValidator not implemented")
        
        config = {"rule_set": "safety_rules", "strict_mode": True}
        validator = RuleValidator(config)
        
        assert hasattr(validator, 'validate_rules')
        assert hasattr(validator, 'add_rule')
        assert hasattr(validator, 'remove_rule')
        assert hasattr(validator, 'get_active_rules')
    
    def test_rule_validator_custom_rules_contract(self):
        """Test rule validator supports custom rules"""
        if RuleValidator is Mock:
            pytest.skip("RuleValidator not implemented")
        
        validator = RuleValidator({})
        
        # Add custom rule
        custom_rule = {
            "name": "no_phone_numbers",
            "pattern": r"\b\d{3}-\d{3}-\d{4}\b",
            "action": "block",
            "message": "Phone numbers not allowed"
        }
        
        validator.add_rule(custom_rule)
        
        # Test with phone number
        content_with_phone = {
            "text": "Call me at 555-123-4567 for more information",
            "context": {}
        }
        
        result = validator.validate_rules(content_with_phone)
        
        # Should trigger custom rule
        assert result["valid"] is False
        assert any(rule["name"] == "no_phone_numbers" for rule in result["violations"])
    
    def test_validator_deterministic_behavior_contract(self):
        """Test validators behave deterministically"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({})
        
        content = {
            "text": "I am a software engineer with Python experience",
            "context": {"type": "professional_summary"}
        }
        
        # Multiple validations should produce identical results
        result1 = validator.validate(content)
        result2 = validator.validate(content)
        
        assert result1 == result2
    
    def test_validator_error_handling_contract(self):
        """Test validators handle errors gracefully"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({})
        
        # Invalid inputs should not crash
        invalid_inputs = [None, {}, {"context": {}}]  # Missing text
        
        for invalid_input in invalid_inputs:
            try:
                result = validator.validate(invalid_input)
                assert isinstance(result, dict)
                assert "valid" in result
            except (ValueError, TypeError):
                # Expected for invalid inputs
                pass
    
    def test_validator_performance_contract(self):
        """Test validators meet performance requirements"""
        if SafetyValidator is Mock:
            pytest.skip("SafetyValidator not implemented")
        
        validator = SafetyValidator({})
        
        content = {
            "text": "This is a test message for performance evaluation of safety validation.",
            "context": {"type": "message"}
        }
        
        import time
        start_time = time.time()
        
        result = validator.validate(content)
        
        elapsed_time = time.time() - start_time
        
        # Should complete quickly
        assert elapsed_time < 0.1  # 100ms for validation
        assert "valid" in result
    
    def test_validator_rule_update_contract(self):
        """Test validators can update rules dynamically"""
        if RuleValidator is Mock:
            pytest.skip("RuleValidator not implemented")
        
        validator = RuleValidator({})
        
        # Initial validation
        content = {"text": "Test content", "context": {}}
        result1 = validator.validate_rules(content)
        
        # Add restrictive rule
        restrictive_rule = {
            "name": "no_test_content",
            "pattern": r"test",
            "action": "block"
        }
        
        validator.add_rule(restrictive_rule)
        
        # Validation should now fail
        result2 = validator.validate_rules(content)
        assert result2["valid"] is False
        
        # Remove rule
        validator.remove_rule("no_test_content")
        
        # Should pass again
        result3 = validator.validate_rules(content)
        assert result3["valid"] is True
    
    def test_validator_integration_contract(self):
        """Test validators work together in pipeline"""
        if all(cls is Mock for cls in [SafetyValidator, SchemaValidator, RuleValidator]):
            pytest.skip("Validators not implemented")
        
        safety_validator = SafetyValidator({})
        schema_validator = SchemaValidator({})
        rule_validator = RuleValidator({})
        
        input_data = {
            "text": "I am a senior software engineer",
            "name": "John Doe",
            "email": "john@example.com",
            "experience": 5,
            "context": {"type": "resume"}
        }
        
        # Pipeline: schema -> safety -> rules
        schema_result = schema_validator.validate_schema(input_data)
        assert schema_result["valid"] is True
        
        safety_result = safety_validator.validate(input_data)
        assert safety_result["valid"] is True
        
        rule_result = rule_validator.validate_rules(input_data)
        assert rule_result["valid"] is True
        
        # Overall should be valid
        assert all([schema_result["valid"], safety_result["valid"], rule_result["valid"]])
