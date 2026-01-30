"""
Test suite for HARDENED PascalSovereigntyAgent with strict priority ordering.

PRIORITY QUEUE (First Match Wins):
1. STUB     - File contains NOT_AN_AGENT marker (MUST preempt AGENT)
2. TEST     - Path contains tests/ OR name starts with test_
3. PROTOCOL - Class inherits from typing.Protocol
4. GATEWAY  - Class name contains "Gateway"
5. ENGINE   - Path contains engines/ AND has class
6. MIXIN    - Class name ends in "Mixin"
7. AGENT    - Inherits *Agent OR path in agents/validators
8. CLASS    - Any other class
9. UTILITY  - No class definitions

CRITICAL: 100% PASS REQUIREMENT
"""

from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent


class TestPascalSovereigntyHardened:
    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent with security validation bypassed for unit testing."""
        with patch.object(PascalSovereigntyAgent, "_security_hardening_validation"):
            return PascalSovereigntyAgent(project_root=tmp_path, dry_run=True)

    # TEST 1: Stub Priority (The "Trojan Horse" Check)
    # A Stub often inherits from SovereignBaseAgent. It MUST be identified as STUB, not AGENT.
    def test_stub_priority_over_agent(self, agent, tmp_path):
        f = tmp_path / "SubAtomicAgent.py"
        f.write_text("# NOT_AN_AGENT\nclass SubAtomicAgent(SovereignBaseAgent):\n    pass")
        assert agent.classify_file(f) == "STUB"
        # Ensure name cleaning works: SubAtomicAgent -> SubAtomicStub
        assert agent.get_compliant_name(f, "STUB") == "SubAtomicStub.py"

    # TEST 2: Protocol Identity (The "I" Check)
    # A Protocol must not be renamed to *Agent.
    def test_protocol_identity(self, agent, tmp_path):
        f = tmp_path / "IOrchestrator.py"
        f.write_text("from typing import Protocol\nclass IOrchestrator(Protocol):\n    pass")
        assert agent.classify_file(f) == "PROTOCOL"
        assert agent.get_compliant_name(f, "PROTOCOL") == "IOrchestrator.py"

    # TEST 3: Test Rescue (Pascal -> Snake)
    # Files in tests/ named PascalCase must be converted to run in pytest.
    def test_rescue_pascal_test(self, agent, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "TestLogic.py"
        f.write_text("def test_one(): pass")
        assert agent.classify_file(f) == "TEST"
        assert agent.get_compliant_name(f, "TEST") == "test_logic.py"

    # TEST 4: Engine Sovereignty (Path-Based)
    # Files in engines/ are ENGINEs even if they don't inherit from Agent.
    def test_engine_sovereignty(self, agent, tmp_path):
        engines_dir = tmp_path / "apps_rg" / "engines"
        engines_dir.mkdir(parents=True)
        f = engines_dir / "CoreEngine.py"
        f.write_text("class CoreEngine:\n    pass")
        assert agent.classify_file(f) == "ENGINE"
        assert agent.get_compliant_name(f, "ENGINE") == "CoreEngine.py"

    # TEST 5: Gateway Recognition
    # Gateways should be identified by name pattern.
    def test_gateway_recognition(self, agent, tmp_path):
        f = tmp_path / "RedisGateway.py"
        f.write_text("class RedisGateway:\n    pass")
        assert agent.classify_file(f) == "GATEWAY"
        assert agent.get_compliant_name(f, "GATEWAY") == "RedisGateway.py"

    # TEST 6: Mixin Logic (Snake Case Enforcement)
    def test_mixin_naming(self, agent, tmp_path):
        f = tmp_path / "HygieneMixin.py"
        f.write_text("class HygieneMixin:\n    pass")
        assert agent.classify_file(f) == "MIXIN"
        assert agent.get_compliant_name(f, "MIXIN") == "hygiene_mixin.py"

    # TEST 7: Standard Agent Fallback
    # Standard agent in agents/ folder gets AGENT tag.
    def test_standard_agent(self, agent, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir(parents=True)
        f = agents_dir / "Location.py"
        f.write_text("class Location(SovereignBaseAgent):\n    pass")
        assert agent.classify_file(f) == "AGENT"
        assert agent.get_compliant_name(f, "AGENT") == "LocationAgent.py"

    # TEST 8: Test Prefix Enforcement
    # "check_logic.py" in tests/ becomes "test_check_logic.py"
    def test_enforce_test_prefix(self, agent, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "check_logic.py"
        f.write_text("def test_one(): pass")
        assert agent.get_compliant_name(f, "TEST") == "test_check_logic.py"

    # TEST 9: Ignore Logic (conftest.py)
    def test_ignore_config(self, agent, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "conftest.py"
        f.write_text("import pytest")
        assert agent.classify_file(f) == "IGNORE"

    # TEST 10: Stub with existing Correct Name
    # SubAtomicStub.py should stay SubAtomicStub.py
    def test_stub_stability(self, agent, tmp_path):
        f = tmp_path / "SubAtomicStub.py"
        f.write_text("# NOT_AN_AGENT\nclass SubAtomicStub:\n    pass")
        compliant_name = agent.get_compliant_name(f, "STUB")
        assert compliant_name == "SubAtomicStub.py"
