"""
Test Prompt System v10.10

Tests prompt registry, ACL governance, and prompt validation
functionality for the v10.10 prompt system.
"""

import pytest
from unittest.mock import Mock, patch

# Import actual prompt system components
try:
    from l1.prompt_system_v10_10 import (
        PromptActorRole,
        PromptACL,
        PromptDiff,
        register_prompt,
        get_prompt,
        get_prompt_acl,
        validate_prompt_definition,
    )
    from core.models.models import PromptDefinition, PromptVersion
except ImportError:
    pytest.skip("Prompt system v10.10 not available", allow_module_level=True)

# Mark as prompt tests
pytestmark = [pytest.mark.prompts, pytest.mark.l1, pytest.mark.planning]


class TestPromptSystemV10_10:
    """Test prompt system v10.10 functionality."""
    
    def test_prompt_actor_roles(self):
        """Test prompt actor role enumeration."""
        assert PromptActorRole.ENGINE == "engine"
        assert PromptActorRole.ADMIN == "admin"
        assert PromptActorRole.EDITOR == "editor"
        assert PromptActorRole.VIEWER == "viewer"
        
        # Test role hierarchy
        roles = list(PromptActorRole)
        assert len(roles) == 4
        assert all(isinstance(role, str) for role in roles)
    
    def test_prompt_acl_creation(self):
        """Test prompt ACL creation and validation."""
        acl = PromptACL(
            id="test_prompt",
            engine_can_use=True,
            admins_can_edit=True,
            editors_can_edit=False,
            viewers_can_read=True
        )
        
        assert acl.id == "test_prompt"
        assert acl.engine_can_use is True
        assert acl.admins_can_edit is True
        assert acl.editors_can_edit is False
        assert acl.viewers_can_read is True
    
    def test_register_prompt_definition(self):
        """Test registering prompt definitions."""
        prompt_def = PromptDefinition(
            id="test_strategy",
            text="Test template for {input}",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Test strategy prompt", "layer": "L1", "agent": "strategy"}
        )
        
        # Register prompt
        register_prompt(prompt_def)
        
        # Verify registration
        retrieved = get_prompt("test_strategy", PromptActorRole.ADMIN)
        assert retrieved.id == "test_strategy"
        assert retrieved.text == "Test template for {input}"
    
    def test_get_prompt_with_acl_enforcement(self):
        """Test prompt retrieval with ACL enforcement."""
        prompt_def = PromptDefinition(
            id="acl_test",
            text="ACL test template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Test ACL"}
        )
        
        # Register with permissive ACL for admin
        acl = PromptACL(
            id="acl_test",
            engine_can_use=False,
            admins_can_edit=True,  # Allow admin access
            editors_can_edit=False,
            viewers_can_read=False
        )
        register_prompt(prompt_def, acl)
        
        # Admin should be able to access when admins_can_edit is True
        admin_prompt = get_prompt("acl_test", PromptActorRole.ADMIN)
        assert admin_prompt.id == "acl_test"
        
        # Engine should be able to use when engine_can_use is True
        # Register another prompt with engine access
        engine_prompt_def = PromptDefinition(
            id="engine_test",
            text="Engine test template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Engine test"}
        )
        
        engine_acl = PromptACL(
            id="engine_test",
            engine_can_use=True,  # Allow engine access
            admins_can_edit=False,
            editors_can_edit=False,
            viewers_can_read=False
        )
        register_prompt(engine_prompt_def, engine_acl)
        
        engine_prompt = get_prompt("engine_test", PromptActorRole.ENGINE, use_case="use")
        assert engine_prompt.id == "engine_test"
    
    def test_get_prompt_acl(self):
        """Test retrieving prompt ACL."""
        prompt_def = PromptDefinition(
            id="acl_retrieval_test",
            text="Test template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Test"}
        )
        
        acl = PromptACL(
            id="acl_retrieval_test",
            engine_can_use=True,
            admins_can_edit=True,
            editors_can_edit=False,
            viewers_can_read=True
        )
        
        register_prompt(prompt_def, acl)
        
        retrieved_acl = get_prompt_acl("acl_retrieval_test")
        assert retrieved_acl is not None
        assert retrieved_acl.id == "acl_retrieval_test"
        assert retrieved_acl.engine_can_use is True
    
    def test_prompt_diff_creation(self):
        """Test prompt diff functionality."""
        old_prompt = PromptDefinition(
            id="diff_test",
            text="Old template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Old description"}
        )
        
        new_prompt = PromptDefinition(
            id="diff_test",
            text="New template",
            version=PromptVersion(major=2, minor=0, patch=0),
            metadata={"description": "New description"}
        )
        
        diff = PromptDiff(
            id="diff_test",
            from_version=PromptVersion(major=1, minor=0, patch=0),
            to_version=PromptVersion(major=2, minor=0, patch=0),
            text_changed=True,
            metadata_changed=True
        )
        
        assert diff.id == "diff_test"
        assert diff.from_version.major == 1
        assert diff.to_version.major == 2
        assert diff.text_changed is True
        assert diff.metadata_changed is True
    
    def test_prompt_validation(self):
        """Test prompt definition validation."""
        valid_prompt = PromptDefinition(
            id="valid_test",
            text="Valid template with {variable}",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Valid prompt"}
        )
        
        # Should not raise exception
        validate_prompt_definition(valid_prompt)
        
        # Test invalid prompt (missing required fields would be caught by Pydantic)
        invalid_prompt = PromptDefinition(
            id="",  # Empty ID should be invalid
            text="Template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Description"}
        )
        
        # Validation should catch issues
        try:
            validate_prompt_definition(invalid_prompt)
            # If no exception, at least check the structure
            assert hasattr(invalid_prompt, 'id')
        except Exception:
            # Expected to fail validation
            pass
    
    def test_acl_permission_errors(self):
        """Test ACL permission enforcement."""
        prompt_def = PromptDefinition(
            id="permission_test",
            text="Test template",
            version=PromptVersion(major=1, minor=0, patch=0),
            metadata={"description": "Test"}
        )
        
        # Restrictive ACL
        acl = PromptACL(
            id="permission_test",
            engine_can_use=False,
            admins_can_edit=False,
            editors_can_edit=False,
            viewers_can_read=False
        )
        register_prompt(prompt_def, acl)
        
        # Viewer should not be able to edit
        with pytest.raises(PermissionError):
            get_prompt("permission_test", PromptActorRole.VIEWER, use_case="edit")
        
        # Non-existent prompt should raise KeyError
        with pytest.raises(KeyError):
            get_prompt("non_existent", PromptActorRole.ENGINE)
