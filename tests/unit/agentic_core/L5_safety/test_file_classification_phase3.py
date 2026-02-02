"""
Unit tests for FileClassificationAgent Phase 3 - Validation and Integration.

Tests:
1. Integration with prompt_governance files
2. Correct classification of agents/ directory files
3. Performance validation
"""

import sys
import time
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestPhase3PromptGovernanceIntegration:
    """Test integration with prompt_governance files."""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        project_root = Path(__file__).parent.parent.parent.parent.parent
        agent = object.__new__(FileClassificationAgent)
        agent.project_root = project_root.resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []
        return agent

    def test_prompt_governance_agents_directory_exists(self):
        """Verify prompt_governance/agents directory exists."""
        project_root = Path(__file__).parent.parent.parent.parent.parent
        agents_dir = project_root / "agentic_core/prompt_governance/agents"
        assert agents_dir.exists(), "prompt_governance/agents should exist"

    def test_classify_prompt_governance_agent_files(self, agent):
        """Test classification of files in prompt_governance/agents."""
        agents_dir = agent.project_root / "agentic_core/prompt_governance/agents"

        if not agents_dir.exists():
            pytest.skip("prompt_governance/agents not found")

        py_files = list(agents_dir.glob("*.py"))
        assert len(py_files) > 0, "Should have Python files in agents/"

        for file_path in py_files:
            if file_path.name.startswith("__"):
                continue

            file_type = agent.classify_file(file_path)
            # Files in agents/ directory should be classified as AGENT
            assert file_type in ["AGENT", "IGNORE", "TEST"], (
                f"{file_path.name} should be AGENT or IGNORE, got {file_type}"
            )

    def test_structural_agent_classification(self, agent):
        """Test that files in agents/ are classified as AGENT structurally."""
        agents_dir = agent.project_root / "agentic_core/prompt_governance/agents"

        if not agents_dir.exists():
            pytest.skip("prompt_governance/agents not found")

        # Test a specific file that should be AGENT type
        for file_path in agents_dir.glob("*.py"):
            if file_path.name.startswith("__") or file_path.name.startswith("test_"):
                continue

            file_type = agent.classify_file(file_path)
            if file_type == "IGNORE":
                continue

            # Should be AGENT due to structural context (in agents/ directory)
            assert file_type == "AGENT", (
                f"{file_path.name} in agents/ should be AGENT, got {file_type}"
            )
            break  # Test at least one


class TestPhase3ClassificationAccuracy:
    """Test classification accuracy across different file types."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent instance for testing."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = tmp_path.resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []
        return agent

    def test_protocol_classification(self, agent, tmp_path):
        """Test Protocol class is classified correctly."""
        test_file = tmp_path / "my_protocol.py"
        test_file.write_text(
            "from typing import Protocol\n\n"
            "class MyProtocol(Protocol):\n"
            "    def method(self) -> None: ...\n"
        )

        file_type = agent.classify_file(test_file)
        assert file_type == "PROTOCOL", f"Expected PROTOCOL, got {file_type}"

    def test_mixin_classification(self, agent, tmp_path):
        """Test Mixin class is classified correctly."""
        test_file = tmp_path / "LoggingMixin.py"
        test_file.write_text("class LoggingMixin:\n    def log(self): pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "MIXIN", f"Expected MIXIN, got {file_type}"

    def test_gateway_classification(self, agent, tmp_path):
        """Test Gateway class is classified correctly."""
        test_file = tmp_path / "ApiGateway.py"
        test_file.write_text("class ApiGateway:\n    def route(self): pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "GATEWAY", f"Expected GATEWAY, got {file_type}"

    def test_engine_classification(self, agent, tmp_path):
        """Test Engine file is classified correctly."""
        engines_dir = tmp_path / "engines"
        engines_dir.mkdir()
        test_file = engines_dir / "ProcessEngine.py"
        test_file.write_text("class ProcessEngine:\n    def run(self): pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "ENGINE", f"Expected ENGINE, got {file_type}"

    def test_stub_classification(self, agent, tmp_path):
        """Test STUB marker is detected correctly."""
        test_file = tmp_path / "MyAgent.py"
        test_file.write_text("# NOT_AN_AGENT\nclass MyAgent:\n    pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "STUB", f"Expected STUB, got {file_type}"


class TestPhase3PerformanceValidation:
    """Test performance characteristics."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent instance for testing."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = tmp_path.resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []
        return agent

    def test_classification_performance(self, agent, tmp_path):
        """Test that classification is fast enough."""
        # Create 50 test files
        for i in range(50):
            test_file = tmp_path / f"file_{i}.py"
            test_file.write_text(f"class Class{i}:\n    pass\n")

        # Time classification of all files
        start = time.time()
        for file_path in tmp_path.glob("*.py"):
            agent.classify_file(file_path)
        elapsed = time.time() - start

        # Should complete in under 5 seconds for 50 files
        assert elapsed < 5.0, f"Classification took too long: {elapsed:.2f}s"

    def test_heal_performance(self, agent, tmp_path):
        """Test that heal method is fast enough."""
        test_file = tmp_path / "TestFile.py"
        test_file.write_text("class TestFile:\n    pass\n")

        # Time healing
        start = time.time()
        agent.heal({"type": "naming", "path": str(test_file)})
        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0, f"Heal took too long: {elapsed:.2f}s"


class TestPhase3RegressionPrevention:
    """Tests to prevent regression of fixed issues."""

    def test_no_bare_except_in_file(self):
        """Verify no bare except statements exist."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "except:":
                pytest.fail(f"Found bare 'except:' at line {i + 1}")

    def test_logger_defined_before_use(self):
        """Verify Logger is defined before any use."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        # Find Logger definition
        logger_def_pos = content.find("Logger = logging.getLogger")
        assert logger_def_pos > 0, "Logger should be defined"

        # Find first Logger use
        logger_use_pos = content.find("Logger.info")
        if logger_use_pos > 0:
            assert logger_def_pos < logger_use_pos, "Logger should be defined before first use"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
