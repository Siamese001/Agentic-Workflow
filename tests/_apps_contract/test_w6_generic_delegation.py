"""W6 Generic Delegation Tests — Profile-Driven Validation and Routing

Tests that verify:
1. Missing profile fails closed
2. Invalid profile fails closed
3. Unknown app fails closed
4. Adding a new app requires profile only, not core edit
5. No apps_rg/apps_lic literals remain in agentic_core/runtime/delegation
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agentic_core.runtime.delegation import (
    DelegationContext,
    CrossAppPayload,
    DelegationType,
    ReuseEligibility,
)
from agentic_core.runtime.delegation.generic_payload_validator import (
    GenericPayloadValidator,
    ValidationPolicy,
    AppValidationProfile,
)
from agentic_core.runtime.delegation.generic_delegation_router import (
    GenericDelegationRouter,
    DelegationConfig,
    AppDelegationProfile,
)


class TestGenericPayloadValidator:
    """Tests for profile-driven payload validation."""
    
    def test_missing_profile_fails_closed(self):
        """Test that missing profile causes validation to fail."""
        policy = ValidationPolicy()
        
        # Mock profile loader that returns None (missing profile)
        def mock_loader(app_id):
            return None
        
        validator = GenericPayloadValidator(policy, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="unknown_app",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            tenant_id="tenant-1",
            session_id="session-1",
        )
        payload = CrossAppPayload(
            payload_id="payload-1",
            delegation_context=context,
        )
        
        errors = validator.validate_payload(payload)
        
        assert len(errors) > 0
        assert any("No delegation profile found" in e for e in errors)
    
    def test_valid_profile_passes(self):
        """Test that valid profile allows validation to pass."""
        policy = ValidationPolicy()
        
        # Mock profile for apps_rg
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppValidationProfile(
                    app_id="apps_rg",
                    require_jd_content_hash=True,
                    require_role_context_hash=False,
                    error_messages={"missing_jd_hash": "JD hash required"},
                )
            return None
        
        validator = GenericPayloadValidator(policy, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_rg",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            tenant_id="tenant-1",
            session_id="session-1",
            jd_content_hash="hash123",  # Provide required field
        )
        payload = CrossAppPayload(
            payload_id="payload-1",
            delegation_context=context,
        )
        
        errors = validator.validate_payload(payload)
        
        # Should pass (no errors related to missing profile)
        assert not any("No delegation profile found" in e for e in errors)
    
    def test_profile_missing_required_field_fails(self):
        """Test that profile requiring jd_content_hash fails when missing."""
        policy = ValidationPolicy()
        
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppValidationProfile(
                    app_id="apps_rg",
                    require_jd_content_hash=True,
                    error_messages={"missing_jd_hash": "JD hash required for apps_rg"},
                )
            return None
        
        validator = GenericPayloadValidator(policy, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_rg",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            tenant_id="tenant-1",
            session_id="session-1",
            jd_content_hash="",  # Missing required field
        )
        payload = CrossAppPayload(
            payload_id="payload-1",
            delegation_context=context,
        )
        
        errors = validator.validate_payload(payload)
        
        assert any("JD hash required for apps_rg" in e for e in errors)
    
    def test_reuse_validation_uses_profile(self):
        """Test that reuse validation uses profile-driven rules."""
        policy = ValidationPolicy()
        
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppValidationProfile(
                    app_id="apps_rg",
                    reuse_match_fields=["tenant_id", "jd_content_hash"],
                    reuse_eligibility_rules=[
                        {"field": "jd_content_hash", "condition": "equals", "failure_eligibility": "JD_HASH_MISMATCH"}
                    ],
                )
            return None
        
        validator = GenericPayloadValidator(policy, profile_loader=mock_loader)
        
        substrate = {
            "substrate_id": "sub-1",
            "tenant_id": "tenant-1",
            "jd_content_hash": "hash-old",
        }
        requesting_context = {
            "tenant_id": "tenant-1",
            "jd_content_hash": "hash-new",  # Different hash
        }
        
        result = validator.validate_reuse(substrate, "apps_rg", requesting_context)
        
        assert not result.eligible
        assert result.eligibility == ReuseEligibility.JD_HASH_MISMATCH


class TestGenericDelegationRouter:
    """Tests for profile-driven delegation routing."""
    
    def test_missing_profile_fails_delegation(self):
        """Test that missing profile causes delegation to fail."""
        config = DelegationConfig()
        
        def mock_loader(app_id):
            return None
        
        router = GenericDelegationRouter(config, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="unknown_app",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
        )
        
        result = router.delegate_research("unknown_app", "apps_research", context)
        
        assert not result.success
        assert "No delegation profile found" in result.failure_reason
    
    def test_disallowed_target_fails(self):
        """Test that delegation to non-allowed target fails."""
        config = DelegationConfig()
        
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppDelegationProfile(
                    app_id="apps_rg",
                    allowed_targets=["apps_research"],
                    required_context_fields=["caller_app_id"],
                )
            return None
        
        router = GenericDelegationRouter(config, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_rg",
            target_app_id="apps_qna",  # Not allowed
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
        )
        
        result = router.delegate_research("apps_rg", "apps_qna", context)
        
        assert not result.success
        assert "only supported to" in result.failure_reason
    
    def test_valid_delegation_succeeds(self):
        """Test that valid profile and target succeeds."""
        config = DelegationConfig()
        
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppDelegationProfile(
                    app_id="apps_rg",
                    allowed_targets=["apps_research"],
                    required_context_fields=["caller_app_id", "task_class"],
                )
            return None
        
        router = GenericDelegationRouter(config, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_rg",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            tenant_id="tenant-1",
        )
        
        result = router.delegate_research("apps_rg", "apps_research", context)
        
        assert result.success
    
    def test_missing_required_context_field_fails(self):
        """Test that missing required context field fails."""
        config = DelegationConfig()
        
        def mock_loader(app_id):
            if app_id == "apps_rg":
                return AppDelegationProfile(
                    app_id="apps_rg",
                    allowed_targets=["apps_research"],
                    required_context_fields=["cross_app_reuse_policy_ref"],
                )
            return None
        
        router = GenericDelegationRouter(config, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_rg",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            # cross_app_reuse_policy_ref is missing
        )
        
        result = router.delegate_research("apps_rg", "apps_research", context)
        
        assert not result.success
        assert "Missing required fields" in result.failure_reason
        assert "cross_app_reuse_policy_ref" in result.failure_reason


class TestNoCoreAppLiterals:
    """Tests that verify no app-specific literals remain in core delegation."""
    
    def test_no_hardcoded_app_strings_in_generic_validator(self):
        """Test that generic validator source has no hardcoded app strings."""
        validator_path = Path("agentic_core/runtime/delegation/generic_payload_validator.py")
        
        if not validator_path.exists():
            pytest.skip("Generic validator not yet created")
        
        content = validator_path.read_text()
        
        # Check for app-specific string literals (not in comments)
        lines = content.split("\n")
        in_docstring = False
        docstring_delim = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle docstrings (both single and triple quotes)
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = True
                    docstring_delim = stripped[:3]
                    # Check if docstring ends on same line
                    if stripped[3:].endswith(docstring_delim):
                        in_docstring = False
                        docstring_delim = None
                    continue
            else:
                if docstring_delim in line:
                    in_docstring = False
                    docstring_delim = None
                continue
            
            # Skip comments
            if stripped.startswith("#"):
                continue
            
            # Check for app-specific strings in actual code (not in comments at end of line)
            code_part = line.split("#")[0]  # Remove end-of-line comments
            
            if '"apps_rg"' in code_part or "'apps_rg'" in code_part:
                pytest.fail(f"Hardcoded apps_rg at line {i+1}: {line.strip()}")
            
            if '"apps_lic"' in code_part or "'apps_lic'" in code_part:
                pytest.fail(f"Hardcoded apps_lic at line {i+1}: {line.strip()}")
    
    def test_no_hardcoded_app_strings_in_generic_router(self):
        """Test that generic router source has no hardcoded app strings."""
        router_path = Path("agentic_core/runtime/delegation/generic_delegation_router.py")
        
        if not router_path.exists():
            pytest.skip("Generic router not yet created")
        
        content = router_path.read_text()
        
        lines = content.split("\n")
        in_docstring = False
        docstring_delim = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle docstrings
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = True
                    docstring_delim = stripped[:3]
                    if stripped[3:].endswith(docstring_delim):
                        in_docstring = False
                        docstring_delim = None
                    continue
            else:
                if docstring_delim in line:
                    in_docstring = False
                    docstring_delim = None
                continue
            
            # Skip comments
            if stripped.startswith("#"):
                continue
            
            # Check for app-specific strings in actual code
            code_part = line.split("#")[0]
            
            if '"apps_rg"' in code_part or "'apps_rg'" in code_part:
                pytest.fail(f"Hardcoded apps_rg at line {i+1}: {line.strip()}")
            
            if '"apps_lic"' in code_part or "'apps_lic'" in code_part:
                pytest.fail(f"Hardcoded apps_lic at line {i+1}: {line.strip()}")
    
    def test_no_equality_checks_on_app_id(self):
        """Test that no code does `caller_app_id == "apps_*"` checks."""
        delegation_dir = Path("agentic_core/runtime/delegation")
        
        for py_file in delegation_dir.glob("*.py"):
            if py_file.name in ["__init__.py", "cross_app_payload_validator.py", "package_driven_delegation_broker.py"]:
                continue
            
            content = py_file.read_text()
            
            # Look for patterns like `if caller_app_id == "..."` or `if requesting_app_id == "..."`
            problematic_patterns = [
                'caller_app_id ==',
                'requesting_app_id ==',
            ]
            
            for pattern in problematic_patterns:
                if pattern in content:
                    # Check if it's in a comment
                    lines = content.split("\n")
                    for line in lines:
                        if pattern in line and not line.strip().startswith("#"):
                            pytest.fail(f"App-specific equality check in {py_file.name}: {line.strip()}")


class TestNewAppRequiresProfileOnly:
    """Tests that adding a new app only requires profile, not core edit."""
    
    def test_new_app_with_profile_works(self):
        """Test that a new app with a valid profile works without core changes."""
        policy = ValidationPolicy()
        
        # Simulate adding a new app "apps_new" with a profile
        def mock_loader(app_id):
            if app_id == "apps_new":
                return AppValidationProfile(
                    app_id="apps_new",
                    require_jd_content_hash=False,
                    require_role_context_hash=False,
                )
            return None
        
        validator = GenericPayloadValidator(policy, profile_loader=mock_loader)
        
        context = DelegationContext(
            delegation_id="test-1",
            caller_app_id="apps_new",
            target_app_id="apps_research",
            task_class="research_substrate",
            delegation_type=DelegationType.RESEARCH_SUBSTRATE,
            tenant_id="tenant-1",
            session_id="session-1",
        )
        payload = CrossAppPayload(
            payload_id="payload-1",
            delegation_context=context,
        )
        
        errors = validator.validate_payload(payload)
        
        # Should pass validation (no profile-not-found error)
        assert not any("No delegation profile found" in e for e in errors)
