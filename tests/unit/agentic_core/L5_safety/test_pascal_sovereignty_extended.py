"""
Test suite for PascalSovereigntyAgent extended file type detection.

Tests the 5 new architectural categories:
- PROTOCOL: typing.Protocol inheritance detection
- ENGINE: Path-based engines/ directory detection
- STUB: NOT_AN_AGENT marker detection
- TEST: tests/ directory detection with snake_case enforcement
- GATEWAY: Gateway naming convention detection
"""

from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent


# MANDATORY: 100% PASS
class TestPascalSovereigntyExtended:
    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent with security validation bypassed for unit testing."""
        with patch.object(PascalSovereigntyAgent, "_security_hardening_validation"):
            return PascalSovereigntyAgent(project_root=tmp_path, dry_run=True)

    # 1. PROTOCOL DETECTION
    def test_classify_protocol(self, agent, tmp_path):
        f = tmp_path / "IOrchestrator.py"
        f.write_text("from typing import Protocol\nclass IOrchestrator(Protocol):\n    pass")
        assert agent.classify_file(f) == "PROTOCOL"

    # 2. STUB DETECTION (NOT_AN_AGENT)
    def test_classify_stub(self, agent, tmp_path):
        f = tmp_path / "SubAtomic.py"
        f.write_text("# NOT_AN_AGENT\nclass SubAtomic:\n    pass")
        assert agent.classify_file(f) == "STUB"

    # 3. ENGINE RECOGNITION (Path-Based)
    def test_classify_engine(self, agent, tmp_path):
        # Create engines directory structure
        engines_dir = tmp_path / "apps_rg" / "engines"
        engines_dir.mkdir(parents=True)
        f = engines_dir / "CoreEngine.py"
        f.write_text("class CoreEngine:\n    pass")
        assert agent.classify_file(f) == "ENGINE"

    # 4. GATEWAY DETECTION
    def test_classify_gateway(self, agent, tmp_path):
        f = tmp_path / "RedisGateway.py"
        f.write_text("class RedisGateway:\n    pass")
        assert agent.classify_file(f) == "GATEWAY"

    # 5. TEST RESCUE (PascalCase -> snake_case)
    # Critical: Ensures "TestAgent.py" becomes "test_agent.py"
    def test_rescue_pascal_test(self, agent, tmp_path):
        # Create tests directory structure
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "TestMyFeature.py"
        f.write_text("def test_one(): pass")

        # Classify first to get TEST type
        file_type = agent.classify_file(f)
        assert file_type == "TEST"

        # Now check compliant name
        compliant_name = agent.get_compliant_name(f, "TEST")
        assert compliant_name == "test_my_feature.py"

    # 6. TEST PRESERVATION (snake_case -> snake_case)
    def test_preserve_snake_test(self, agent, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "test_valid.py"
        f.write_text("def test_one(): pass")
        compliant_name = agent.get_compliant_name(f, "TEST")
        assert compliant_name == "test_valid.py"

    # 7. PROTOCOL NAMING (Preserve 'I' Prefix)
    def test_protocol_naming(self, agent, tmp_path):
        f = tmp_path / "IHealable.py"
        f.write_text("from typing import Protocol\nclass IHealable(Protocol):\n    pass")
        compliant_name = agent.get_compliant_name(f, "PROTOCOL")
        assert compliant_name == "IHealable.py"

    # 8. TEST PREFIX ENFORCEMENT
    # "my_feature.py" in tests/ -> "test_my_feature.py"
    def test_enforce_test_prefix(self, agent, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True)
        f = tests_dir / "my_feature.py"
        f.write_text("def test_one(): pass")
        compliant_name = agent.get_compliant_name(f, "TEST")
        assert compliant_name == "test_my_feature.py"

    # 9. ENGINE NAMING (No Forced Agent Suffix)
    def test_engine_naming(self, agent, tmp_path):
        engines_dir = tmp_path / "engines"
        engines_dir.mkdir(parents=True)
        f = engines_dir / "ExecutionEngine.py"
        f.write_text("class ExecutionEngine:\n    pass")
        compliant_name = agent.get_compliant_name(f, "ENGINE")
        assert compliant_name == "ExecutionEngine.py"

    # 10. STUB NAMING (Agent -> Stub transformation)
    # Per hardened logic: SubAtomicAgent.py -> SubAtomicStub.py
    def test_stub_naming(self, agent, tmp_path):
        f = tmp_path / "SubAtomicAgent.py"
        f.write_text("# NOT_AN_AGENT\nclass SubAtomicAgent:\n    pass")
        compliant_name = agent.get_compliant_name(f, "STUB")
        assert compliant_name == "SubAtomicStub.py"
