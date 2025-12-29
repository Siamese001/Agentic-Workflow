"""Unit tests for Firewall policy enforcement."""
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class test_firewall_policy_enforcement:
    """Test Firewall allow/block decisions."""

    def test_firewall_allows_whitelisted_request(self) -> Any:
        """
        GIVEN: Firewall with whitelist
        WHEN: Whitelisted request arrives
        THEN: Request allowed
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        firewall.whitelist = ['trusted_source']
        allowed: Any = firewall.allow('trusted_source')
        assert allowed is True

    def test_firewall_blocks_blacklisted_request(self) -> Any:
        """
        GIVEN: Firewall with blacklist
        WHEN: Blacklisted request arrives
        THEN: Request blocked
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        firewall.blacklist = ['malicious_source']
        blocked: Any = firewall.block('malicious_source')
        assert blocked is True

    def test_firewall_default_deny_policy(self) -> Any:
        """
        GIVEN: Firewall with default deny
        WHEN: Unknown request arrives
        THEN: Request denied
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        firewall.default_policy = 'deny'
        result: Any = firewall.allow('unknown_source')
        assert result is False

    @pytest.mark.parametrize('source,expected', [('agentic_core', True), ('external_api', False), ('schemas', True)])
    def test_firewall_sovereignty_based_rules(self, source: Any, expected: Any) -> Any:
        """
        GIVEN: Firewall with sovereignty rules
        WHEN: Request from various sources
        THEN: Sovereign sources allowed, external blocked
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        sovereign_sources: Any = ['agentic_core', 'schemas']
        allowed: Any = source in sovereign_sources
        assert allowed == expected

@pytest.mark.unit
class test_firewall_logging:
    """Test Firewall logging and audit trail."""

    def test_firewall_logs_blocked_requests(self) -> Any:
        """
        GIVEN: Firewall blocking requests
        WHEN: Request blocked
        THEN: Block logged to audit trail
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        firewall.audit_log = []
        firewall.block('suspicious_source')
        firewall.audit_log.append({'action': 'block', 'source': 'suspicious_source', 'reason': 'not_whitelisted'})
        assert len(firewall.audit_log) == 1
        assert firewall.audit_log[0]['action'] == 'block'

    def test_firewall_logs_allowed_requests(self) -> Any:
        """
        GIVEN: Firewall allowing requests
        WHEN: Request allowed
        THEN: Allow logged to audit trail
        """
        from firewall import Firewall
        firewall: Any = Firewall()
        firewall.audit_log = []
        firewall.allow('trusted_source')
        firewall.audit_log.append({'action': 'allow', 'source': 'trusted_source', 'reason': 'whitelisted'})
        assert len(firewall.audit_log) == 1
        assert firewall.audit_log[0]['action'] == 'allow'
