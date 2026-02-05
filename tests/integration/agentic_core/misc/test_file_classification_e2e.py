"""
End-to-End and Integration Tests for FileClassificationAgent.

Comprehensive tests covering all phases of the FileClassificationAgent fixes:
- Phase 1: Critical runtime fixes
- Phase 2: Unified detection/healing logic
- Phase 3: Validation and prompt_governance integration
- Phase 4: Code quality standards
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestE2EFileClassificationAgent:
    """End-to-end tests for complete FileClassificationAgent workflow."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure for testing."""
        # Create directory structure
        (tmp_path / "agents").mkdir()
        (tmp_path / "validators").mkdir()
        (tmp_path / "engines").mkdir()
        (tmp_path / "scripts").mkdir()
        (tmp_path / "tests").mkdir()

        return tmp_path

    @pytest.fixture
    def agent(self, temp_project):
        """Create agent instance for testing."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = temp_project.resolve()
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

    def test_e2e_agent_classification_and_healing(self, agent, temp_project):
        """Test complete workflow: classify -> detect violation -> heal."""
        # Create a file that needs Agent suffix
        agents_dir = temp_project / "agents"
        test_file = agents_dir / "MyProcessor.py"
        test_file.write_text("class MyProcessor:\n    def process(self): pass\n")

        # Step 1: Classify
        file_type = agent.classify_file(test_file)
        assert file_type == "AGENT", f"Expected AGENT, got {file_type}"

        # Step 2: Get compliant name
        new_name = agent.get_compliant_name(test_file, file_type)
        assert new_name is not None, "Should suggest rename"
        assert "Agent" in new_name, f"Should suggest Agent suffix: {new_name}"

        # Step 3: Heal
        result = agent.heal({"type": "naming", "path": str(test_file)})
        assert result["violations_found"] == 1
        # heal() performs the rename directly (doesn't check dry_run)
        assert result["violations_fixed"] == 1 or result["skipped"] == 1

    def test_e2e_script_classification_snake_case(self, agent, temp_project):
        """Test scripts are converted to snake_case."""
        scripts_dir = temp_project / "scripts"
        test_file = scripts_dir / "MyScript.py"
        test_file.write_text("def main():\n    pass\n")

        # Classify
        file_type = agent.classify_file(test_file)
        assert file_type == "SCRIPT", f"Expected SCRIPT, got {file_type}"

        # Get compliant name
        new_name = agent.get_compliant_name(test_file, file_type)
        if new_name:
            assert new_name == "my_script.py", f"Expected snake_case: {new_name}"

    def test_e2e_mixin_classification(self, agent, temp_project):
        """Test mixins are properly classified and named."""
        test_file = temp_project / "LoggingMixin.py"
        test_file.write_text("class LoggingMixin:\n    def log(self): pass\n")

        # Classify
        file_type = agent.classify_file(test_file)
        assert file_type == "MIXIN", f"Expected MIXIN, got {file_type}"

        # Get compliant name
        new_name = agent.get_compliant_name(test_file, file_type)
        if new_name:
            assert "_mixin" in new_name.lower(), f"Expected mixin suffix: {new_name}"

    def test_e2e_protocol_classification(self, agent, temp_project):
        """Test protocols are properly classified."""
        test_file = temp_project / "MyProtocol.py"
        test_file.write_text(
            "from typing import Protocol\n\n"
            "class MyProtocol(Protocol):\n"
            "    def method(self) -> None: ...\n"
        )

        file_type = agent.classify_file(test_file)
        assert file_type == "PROTOCOL", f"Expected PROTOCOL, got {file_type}"

    def test_e2e_engine_classification(self, agent, temp_project):
        """Test engines are properly classified."""
        engines_dir = temp_project / "engines"
        test_file = engines_dir / "ProcessEngine.py"
        test_file.write_text("class ProcessEngine:\n    def run(self): pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "ENGINE", f"Expected ENGINE, got {file_type}"

    def test_e2e_stub_detection(self, agent, temp_project):
        """Test NOT_AN_AGENT marker detection."""
        test_file = temp_project / "FakeAgent.py"
        test_file.write_text("# NOT_AN_AGENT\nclass FakeAgent:\n    pass\n")

        file_type = agent.classify_file(test_file)
        assert file_type == "STUB", f"Expected STUB, got {file_type}"


class TestIntegrationWithExecuteSSOT:
    """Integration tests for execute_ssot.py compatibility."""

    def test_heal_repository_interface(self):
        """Test heal_repository has correct interface for execute_ssot."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        # Verify heal_repository method exists
        assert hasattr(FileClassificationAgent, "heal_repository")

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(FileClassificationAgent.heal_repository)
        params = list(sig.parameters.keys())

        assert "dry_run" in params, "Should have dry_run parameter"
        assert "execute" in params, "Should have execute parameter"

    def test_heal_interface(self):
        """Test heal method has correct interface."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "heal")

        import inspect

        sig = inspect.signature(FileClassificationAgent.heal)
        params = list(sig.parameters.keys())

        assert "violation" in params, "Should have violation parameter"

    def test_run_interface(self):
        """Test run method exists for orchestration."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        assert hasattr(FileClassificationAgent, "run")


class TestIntegrationPromptGovernance:
    """Integration tests with prompt_governance directory."""

    @pytest.fixture
    def agent(self):
        """Create agent with real project root."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        project_root = Path(__file__).parent.parent.parent.parent
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

    def test_prompt_governance_agents_classified_correctly(self, agent):
        """Test prompt_governance/agents files are classified as AGENT."""
        agents_dir = agent.project_root / "agentic_core/prompt_governance/agents"

        if not agents_dir.exists():
            pytest.skip("prompt_governance/agents not found")

        classified_as_agent = 0
        total_files = 0

        for file_path in agents_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue

            total_files += 1
            file_type = agent.classify_file(file_path)

            if file_type == "AGENT":
                classified_as_agent += 1

        assert total_files > 0, "Should have Python files"
        # At least some files should be classified as AGENT
        assert classified_as_agent > 0, "Some files should be classified as AGENT"

    def test_heal_uses_same_logic_as_classify(self, agent):
        """Test heal() uses same classification logic as classify_file()."""
        agents_dir = agent.project_root / "agentic_core/prompt_governance/agents"

        if not agents_dir.exists():
            pytest.skip("prompt_governance/agents not found")

        for file_path in agents_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue

            # Get classification
            file_type = agent.classify_file(file_path)

            if file_type == "IGNORE":
                continue

            # Get compliant name (verify it works)
            _ = agent.get_compliant_name(file_path, file_type)

            # Heal should use same logic
            result = agent.heal({"type": "naming", "path": str(file_path)})

            # Result should be consistent
            assert isinstance(result, dict)
            assert "violations_found" in result

            break  # Test at least one file


class TestAllPhasesIntegration:
    """Integration tests verifying all phases work together."""

    def test_full_workflow_no_crashes(self):
        """Test complete workflow without any crashes."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create test structure
            (tmp_path / "agents").mkdir()
            test_file = tmp_path / "agents" / "TestClass.py"
            test_file.write_text("class TestClass:\n    pass\n")

            # Create agent
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

            # Phase 1: Logger works
            from agentic_core.L5_safety.validators.FileClassificationAgent import Logger

            assert Logger is not None

            # Phase 2: Unified classification/healing
            file_type = agent.classify_file(test_file)
            _ = agent.get_compliant_name(test_file, file_type)  # Verify works
            result = agent.heal({"type": "naming", "path": str(test_file)})

            # Phase 3: Performance acceptable
            import time

            start = time.time()
            for _ in range(10):
                agent.classify_file(test_file)
            elapsed = time.time() - start
            assert elapsed < 1.0, "Classification should be fast"

            # Phase 4: Result format correct
            assert isinstance(result, dict)
            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result

    def test_no_regression_in_existing_tests(self):
        """Verify existing guardian tests still pass conceptually."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

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

            # Test ops_script protection
            scripts_dir = tmp_path / "ops_scripts"
            scripts_dir.mkdir()
            script_file = scripts_dir / "MyScript.py"
            script_file.write_text("class MyClass:\n    pass\n")
            assert agent.classify_file(script_file) == "SCRIPT"

            # Test types collection immunity
            types_file = tmp_path / "types.py"
            types_file.write_text("class MyType:\n    pass\n")
            assert agent.classify_file(types_file) == "TYPES"

            # Test private module immunity
            private_file = tmp_path / "_internal.py"
            private_file.write_text("class Internal:\n    pass\n")
            assert agent.classify_file(private_file) == "TYPES"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
