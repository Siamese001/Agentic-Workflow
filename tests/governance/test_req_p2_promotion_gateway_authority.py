"""Tests for Wave 17 P2: Promotion gateway authority."""

import pytest
import hashlib
from unittest.mock import Mock, patch

pytestmark = pytest.mark.governance

# Import the modules we're testing
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L4_state" / "enforcement"))
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution" / "capability"))
sys.path.append(str(Path(__file__).parent.parent.parent / "agentic_core" / "L2_execution"))

from promotion_authority import PromotionAuthority, PromotionPointerUpdate, get_promotion_authority
from promotion_token import PromotionToken, issue_promotion_token
from UniversalWriteGateway import UniversalWriteGateway

class TestPromotionGatewayAuthority:
    """Test promotion pointer updates through gateway with capability tokens."""
    
    def setup_method(self):
        """Set up test environment."""
        self.authority = get_promotion_authority()
        self.gateway = UniversalWriteGateway(replay_mode=False)
        self.authority.set_write_gateway(self.gateway)
    
    def test_pointer_update_via_gateway_success(self):
        """Test successful pointer update via gateway with valid token."""
        # Given - Create valid promotion token
        token = issue_promotion_token(
            target_namespace="test_namespace",
            semantic_clock_tick=100,
            window_size=10
        )
        
        # When - Update pointer via gateway
        update = self.authority.update_pointer_via_gateway("new_pointer_value", token)
        
        # Then - Update should succeed
        assert isinstance(update, PromotionPointerUpdate), "Should return PromotionPointerUpdate"
        assert update.new_pointer == "new_pointer_value", "New pointer should be set"
        assert update.capability_token_hash == hashlib.sha256(str(token).encode()).hexdigest(), \
            "Should store token hash"
        assert update.semantic_clock_tick == 100, "Should record semantic clock"
    
    def test_pointer_update_without_gateway_fails(self):
        """Test that pointer update fails without configured gateway."""
        # Given - Authority without gateway
        authority = PromotionAuthority()  # No gateway set
        
        # Create token
        token = issue_promotion_token(
            target_namespace="test_namespace",
            semantic_clock_tick=100
        )
        
        # When/Then - Should raise error
        with pytest.raises(RuntimeError, match="Write gateway not configured"):
            authority.update_pointer_via_gateway("new_pointer", token)
    
    def test_pointer_update_invalid_token_fails(self):
        """Test that pointer update fails with invalid token."""
        # Given - Invalid token (missing validation method)
        invalid_token = Mock()
        del invalid_token.validate_scope_and_use
        
        # When/Then - Should raise error
        with pytest.raises(ValueError, match="Invalid capability token"):
            self.authority.update_pointer_via_gateway("new_pointer", invalid_token)
    
    def test_pointer_update_token_validation_failure(self):
        """Test that pointer update fails when token validation fails."""
        # Given - Token that fails validation
        token = Mock()
        token.validate_scope_and_use.return_value = False
        token.target_namespace = "test_namespace"
        token.semantic_clock_tick = 100
        
        # When/Then - Should raise error
        with pytest.raises(RuntimeError, match="Capability token validation failed"):
            self.authority.update_pointer_via_gateway("new_pointer", token)
    
    def test_pointer_update_records_mutation(self):
        """Test that pointer update records mutation in gateway."""
        # Given - Valid token
        token = issue_promotion_token(
            target_namespace="record_test",
            semantic_clock_tick=100
        )
        
        # When - Update pointer
        self.authority.update_pointer_via_gateway("recorded_pointer", token)
        
        # Then - Mutation should be recorded
        ledger = self.gateway.get_mutation_ledger()
        promotion_mutations = [m for m in ledger if "promotion" in m.path]
        assert len(promotion_mutations) > 0, "Should record promotion mutation"
        
        mutation = promotion_mutations[-1]
        assert mutation.operation == "promotion_pointer_update", \
            "Should record correct operation"
        assert "record_test" in mutation.path, "Should include namespace"
    
    def test_pointer_update_integrity_validation(self):
        """Test pointer update integrity validation."""
        # Given - Perform update
        token = issue_promotion_token(
            target_namespace="integrity_test",
            semantic_clock_tick=100
        )
        
        update = self.authority.update_pointer_via_gateway("integrity_pointer", token)
        
        # Compute expected hash
        expected_hash = hashlib.sha256(
            f"{update.old_pointer}{update.new_pointer}{update.timestamp}".encode()
        ).hexdigest()
        
        # When/Then - Validation should pass
        assert self.authority.validate_pointer_update_integrity("integrity_test", expected_hash), \
            "Integrity validation should pass"
        
        # Wrong hash should fail
        wrong_hash = hashlib.sha256("wrong".encode()).hexdigest()
        assert not self.authority.validate_pointer_update_integrity("integrity_test", wrong_hash), \
            "Wrong hash should fail validation"
    
    def test_pointer_update_history_tracking(self):
        """Test that pointer update history is tracked."""
        # Given - Perform updates
        token1 = issue_promotion_token(
            target_namespace="history_test",
            semantic_clock_tick=100
        )
        
        token2 = issue_promotion_token(
            target_namespace="history_test",
            semantic_clock_tick=101
        )
        
        # When - Perform updates
        update1 = self.authority.update_pointer_via_gateway("pointer_v1", token1)
        update2 = self.authority.update_pointer_via_gateway("pointer_v2", token2)
        
        # Then - History should track latest update
        history = self.authority.get_update_history("history_test")
        assert history is not None, "Should have update history"
        assert history.new_pointer == "pointer_v2", "Should track latest update"
        assert history.old_pointer == "pointer_v1", "Should track previous pointer"
    
    def test_gateway_replay_mode_simulation(self):
        """Test pointer update in gateway replay mode."""
        # Given - Gateway in replay mode
        replay_gateway = UniversalWriteGateway(replay_mode=True)
        self.authority.set_write_gateway(replay_gateway)
        
        token = issue_promotion_token(
            target_namespace="replay_test",
            semantic_clock_tick=100
        )
        
        # When - Update in replay mode
        update = self.authority.update_pointer_via_gateway("replay_pointer", token)
        
        # Then - Should succeed without actual mutation
        assert isinstance(update, PromotionPointerUpdate), "Should return update"
        
        # Check that replay mutations are marked
        ledger = replay_gateway.get_mutation_ledger()
        replay_mutations = [m for m in ledger if m.replay_mode]
        assert len(replay_mutations) > 0, "Should record replay mutations"
    
    def test_multiple_namespace_isolation(self):
        """Test that updates to different namespaces are isolated."""
        # Given - Tokens for different namespaces
        token_a = issue_promotion_token(
            target_namespace="namespace_a",
            semantic_clock_tick=100
        )
        
        token_b = issue_promotion_token(
            target_namespace="namespace_b",
            semantic_clock_tick=100
        )
        
        # When - Update different namespaces
        update_a = self.authority.update_pointer_via_gateway("pointer_a", token_a)
        update_b = self.authority.update_pointer_via_gateway("pointer_b", token_b)
        
        # Then - Updates should be isolated
        assert update_a.capability_token_hash != update_b.capability_token_hash, \
            "Different namespaces should have different token hashes"
        
        history_a = self.authority.get_update_history("namespace_a")
        history_b = self.authority.get_update_history("namespace_b")
        
        assert history_a.new_pointer == "pointer_a", "Namespace A should have its pointer"
        assert history_b.new_pointer == "pointer_b", "Namespace B should have its pointer"

def test_req_p2_promotion_gateway_authority():
    """Test P2 promotion gateway authority requirements."""
    test = TestPromotionGatewayAuthority()
    test.setup_method()
    
    # Core functionality tests
    test.test_pointer_update_via_gateway_success()
    test.test_pointer_update_without_gateway_fails()
    test.test_pointer_update_invalid_token_fails()
    test.test_pointer_update_token_validation_failure()
    
    # Integrity and tracking tests
    test.test_pointer_update_records_mutation()
    test.test_pointer_update_integrity_validation()
    test.test_pointer_update_history_tracking()
    
    # Edge cases
    test.test_gateway_replay_mode_simulation()
    test.test_multiple_namespace_isolation()
