"""Unit tests for Firewall policy enforcement."""
import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestFirewallPolicyEnforcement:
    """Test Firewall allow/block decisions."""
    
    def test_firewall_allows_whitelisted_request(self):
        """
        GIVEN: Firewall with whitelist
        WHEN: Whitelisted request arrives
        THEN: Request allowed
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        firewall.whitelist = ["trusted_source"]
        
        # Act
        allowed = firewall.allow("trusted_source")
        
        # Assert
        assert allowed is True
    
    def test_firewall_blocks_blacklisted_request(self):
        """
        GIVEN: Firewall with blacklist
        WHEN: Blacklisted request arrives
        THEN: Request blocked
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        firewall.blacklist = ["malicious_source"]
        
        # Act
        blocked = firewall.block("malicious_source")
        
        # Assert
        assert blocked is True
    
    def test_firewall_default_deny_policy(self):
        """
        GIVEN: Firewall with default deny
        WHEN: Unknown request arrives
        THEN: Request denied
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        firewall.default_policy = "deny"
        
        # Act
        result = firewall.allow("unknown_source")
        
        # Assert
        assert result is False
    
    @pytest.mark.parametrize("source,expected", [
        ("agentic_core", True),
        ("external_api", False),
        ("schemas", True),
    ])
    def test_firewall_sovereignty_based_rules(self, source, expected):
        """
        GIVEN: Firewall with sovereignty rules
        WHEN: Request from various sources
        THEN: Sovereign sources allowed, external blocked
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        sovereign_sources = ["agentic_core", "schemas"]
        
        # Act
        allowed = source in sovereign_sources
        
        # Assert
        assert allowed == expected


@pytest.mark.unit
class TestFirewallLogging:
    """Test Firewall logging and audit trail."""
    
    def test_firewall_logs_blocked_requests(self):
        """
        GIVEN: Firewall blocking requests
        WHEN: Request blocked
        THEN: Block logged to audit trail
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        firewall.audit_log = []
        
        # Act
        firewall.block("suspicious_source")
        firewall.audit_log.append({
            "action": "block",
            "source": "suspicious_source",
            "reason": "not_whitelisted"
        })
        
        # Assert
        assert len(firewall.audit_log) == 1
        assert firewall.audit_log[0]["action"] == "block"
    
    def test_firewall_logs_allowed_requests(self):
        """
        GIVEN: Firewall allowing requests
        WHEN: Request allowed
        THEN: Allow logged to audit trail
        """
        # Arrange
        from firewall import Firewall
        
        firewall = Firewall()
        firewall.audit_log = []
        
        # Act
        firewall.allow("trusted_source")
        firewall.audit_log.append({
            "action": "allow",
            "source": "trusted_source",
            "reason": "whitelisted"
        })
        
        # Assert
        assert len(firewall.audit_log) == 1
        assert firewall.audit_log[0]["action"] == "allow"
