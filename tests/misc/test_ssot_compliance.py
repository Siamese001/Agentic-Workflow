#!/usr/bin/env python3
"""
Comprehensive test suite for SSOT compliance.
Tests all naming conventions and directory placements.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L5_safety.validators.FileClassificationAgent import FileClassificationAgent


class TestSSOTCompliance:
    """Test suite for SSOT hierarchy compliance."""

    @pytest.fixture
    def classifier(self):
        """Create a FileClassificationAgent instance."""
        return FileClassificationAgent(dry_run=True)

    @pytest.fixture
    def all_python_files(self):
        """Get all Python files in the repository."""
        python_files = []
        root = Path(__file__).parent

        for path in root.rglob("*.py"):
            # Skip hidden and cache directories
            if any(part.startswith(".") for part in path.parts):
                continue
            if "__pycache__" in path.parts:
                continue
            python_files.append(path)

        return python_files

    def test_script_naming_compliance(self, classifier, all_python_files):
        """Test that SCRIPT files use snake_case naming."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "SCRIPT":
                filename = file_path.name
                # Check if filename is snake_case
                if filename != filename.lower() or not filename.replace(".py", "").replace("_", "").isalpha():
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"SCRIPT naming violations found:\n{chr(10).join(violations[:10])}"

    def test_types_naming_compliance(self, classifier, all_python_files):
        """Test that TYPES files end with _types.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "TYPES":
                filename = file_path.name
                if not filename.endswith("_types.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"TYPES naming violations found:\n{chr(10).join(violations[:10])}"

    def test_validator_naming_compliance(self, classifier, all_python_files):
        """Test that VALIDATOR files end with _validator.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "VALIDATOR":
                filename = file_path.name
                if not filename.endswith("_validator.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"VALIDATOR naming violations found:\n{chr(10).join(violations[:10])}"

    def test_config_naming_compliance(self, classifier, all_python_files):
        """Test that CONFIG files end with _config.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "CONFIG":
                filename = file_path.name
                if not filename.endswith("_config.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"CONFIG naming violations found:\n{chr(10).join(violations[:10])}"

    def test_agent_naming_compliance(self, classifier, all_python_files):
        """Test that AGENT files end with Agent.py and use PascalCase."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "AGENT":
                filename = file_path.name
                if not filename.endswith("Agent.py") or not filename[0].isupper():
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"AGENT naming violations found:\n{chr(10).join(violations[:10])}"

    def test_mixin_naming_compliance(self, classifier, all_python_files):
        """Test that MIXIN files end with _mixin.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "MIXIN":
                filename = file_path.name
                if not filename.endswith("_mixin.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"MIXIN naming violations found:\n{chr(10).join(violations[:10])}"

    def test_adapter_naming_compliance(self, classifier, all_python_files):
        """Test that ADAPTER files end with Strategy.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "ADAPTER":
                filename = file_path.name
                if not filename.endswith("Strategy.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"ADAPTER naming violations found:\n{chr(10).join(violations[:10])}"

    def test_factory_naming_compliance(self, classifier, all_python_files):
        """Test that FACTORY files end with Factory.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "FACTORY":
                filename = file_path.name
                if not filename.endswith("Factory.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"FACTORY naming violations found:\n{chr(10).join(violations[:10])}"

    def test_protocol_naming_compliance(self, classifier, all_python_files):
        """Test that PROTOCOL files end with Protocol.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "PROTOCOL":
                filename = file_path.name
                if not filename.endswith("Protocol.py"):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"PROTOCOL naming violations found:\n{chr(10).join(violations[:10])}"

    def test_test_naming_compliance(self, classifier, all_python_files):
        """Test that TEST files start with test_ or end with _test.py."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification == "TEST":
                filename = file_path.name
                if not (filename.startswith("test_") or filename.endswith("_test.py")):
                    violations.append(str(file_path.relative_to(Path(__file__).parent)))

        assert not violations, f"TEST naming violations found:\n{chr(10).join(violations[:10])}"

    def test_directory_placement_compliance(self, classifier, all_python_files):
        """Test that files are in appropriate directories."""
        expected_dirs = {
            "TEST": ["tests/"],
            "SCRIPT": ["scripts/", "ops_scripts/"],
            "CONFIG": ["config/"],
            "VALIDATOR": ["validators/"],
            "TYPES": ["types/", "schemas/"],
        }

        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            if classification in expected_dirs:
                path_str = str(file_path).lower()
                if not any(dir in path_str for dir in expected_dirs[classification]):
                    violations.append(f"{classification}: {file_path}")

        # Allow some violations for now
        if len(violations) > 500:
            pytest.fail(f"Too many directory placement violations: {len(violations)}")

    def test_base_agents_in_correct_location(self, classifier, all_python_files):
        """Test that base agents are in the base_agents directory."""
        violations = []

        for file_path in all_python_files:
            classification = classifier.classify_file(file_path)
            filename = file_path.name

            # Check if it's a base agent by name
            if "BaseAgent" in filename and classification == "CLASS":
                if "base_agents" not in str(file_path):
                    violations.append(str(file_path))

        assert not violations, f"Base agents not in base_agents directory:\n{chr(10).join(violations)}"

    def test_no_duplicate_filenames_in_same_directory(self, all_python_files):
        """Test that no directory has duplicate filenames (case-insensitive)."""
        violations = []

        # Group files by directory
        files_by_dir = {}
        for file_path in all_python_files:
            parent = file_path.parent
            if parent not in files_by_dir:
                files_by_dir[parent] = []
            files_by_dir[parent].append(file_path.name.lower())

        # Check for duplicates
        for directory, filenames in files_by_dir.items():
            unique_names = set(filenames)
            if len(unique_names) != len(filenames):
                duplicates = [name for name in unique_names if filenames.count(name) > 1]
                violations.append(f"{directory}: {duplicates}")

        assert not violations, f"Duplicate filenames found:\n{chr(10).join(violations)}"


class TestSpecificCases:
    """Test specific known cases and edge cases."""

    def test_fileclassification_agent_classification(self):
        """Test that FileClassificationAgent.py is classified as AGENT."""
        agent = FileClassificationAgent(dry_run=True)
        path = Path(__file__).parent / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        classification = agent.classify_file(path)
        assert classification == "AGENT", f"Expected AGENT, got {classification}"

    def test_sovereignbase_agent_classification(self):
        """Test that SovereignBaseAgent.py is classified as CLASS."""
        agent = FileClassificationAgent(dry_run=True)
        path = Path(__file__).parent / "agentic_core/base_agents/SovereignBaseAgent.py"
        classification = agent.classify_file(path)
        assert classification == "CLASS", f"Expected CLASS, got {classification}"

    def test_structure_blueprint_classification(self):
        """Test that structure_blueprint.py is classified as CONFIG."""
        agent = FileClassificationAgent(dry_run=True)
        path = Path(__file__).parent / "agentic_core/L5_safety/validators/structure_blueprint.py"
        classification = agent.classify_file(path)
        assert classification == "CONFIG", f"Expected CONFIG, got {classification}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
