#!/usr/bin/env python3
"""
Guardian Regression Tests
Ensures deduplication doesn't break existing functionality.
"""

import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.base import AgentTestMixin, GuardianTestBase


class TestDeduplicationRegression(AgentTestMixin):
    """Regression tests for Guardian deduplication."""

    def test_merged_test_files_exist(self):
        """Ensure merged test files exist."""
        guardian_dir = PROJECT_ROOT / "tests" / "guardian"

        required_files = [
            "test_agent_autonomy.py",
            "test_agent_validation.py",
            "test_architecture_governance.py",
            "test_core_components.py",
            "test_forensic_audit_unified.py",
            "base.py",
            "conftest.py",
        ]

        for filename in required_files:
            file_path = guardian_dir / filename
            assert file_path.exists(), f"Missing required file: {filename}"

    def test_old_files_removed(self):
        """Ensure redundant files were removed."""
        guardian_dir = PROJECT_ROOT / "tests" / "guardian"

        removed_files = [
            "test_agent_autonomy_comprehensive.py",
            "test_agent_validation_comprehensive.py",
            "test_architecture_governance_comprehensive.py",
            "test_core_components_comprehensive.py",
            "test_forensic_audit_phase1.py",
            "test_forensic_audit_phase2.py",
            "test_forensic_audit_phase3.py",
            "test_forensic_audit_phase4.py",
            "test_forensic_audit_phase5.py",
            "test_forensic_audit_phase6.py",
        ]

        for filename in removed_files:
            file_path = guardian_dir / filename
            assert not file_path.exists(), f"Redundant file still exists: {filename}"

    def test_backup_files_exist(self):
        """Ensure backup files were created."""
        backup_dir = PROJECT_ROOT / ".backup" / "guardian_tests"
        assert backup_dir.exists(), "Backup directory should exist"

        backup_files = list(backup_dir.glob("*.py"))
        assert len(backup_files) > 0, "Should have backup files"

    def test_agent_autonomy_functionality_preserved(self):
        """Test agent autonomy validation still works."""
        from tests.guardian.test_agent_autonomy import AgentAutonomyValidator

        compliant_code = """
class TestAgent:
    def heal_repository(self):
        pass
"""
        temp_file = self.create_temp_file(compliant_code)
        try:
            result = AgentAutonomyValidator.validate_agent_file(temp_file)
            assert result["compliant"]
        finally:
            self.cleanup_temp_file(temp_file)

        non_compliant_code = """
class TestAgent:
    def other_method(self):
        pass
"""
        temp_file = self.create_temp_file(non_compliant_code)
        try:
            result = AgentAutonomyValidator.validate_agent_file(temp_file)
            assert not result["compliant"]
        finally:
            self.cleanup_temp_file(temp_file)

    def test_agent_validation_functionality_preserved(self):
        """Test agent validation still works."""
        from tests.guardian.test_agent_validation import AgentStructureValidator

        valid_code = """
class TestAgent:
    def __init__(self):
        pass

    def run(self):
        pass
"""
        temp_file = self.create_temp_file(valid_code, suffix="Agent.py")
        try:
            result = AgentStructureValidator.check_agent_structure(temp_file)
            assert result["has_agent_class"]
        finally:
            self.cleanup_temp_file(temp_file)

    def test_architecture_governance_functionality_preserved(self, tmp_path):
        """Test architecture governance validation still works."""
        from tests.guardian.test_architecture_governance import ArchitectureGovernanceValidator

        valid_code = """
class TestAgent:
    def run(self):
        pass
"""
        layer_dir = tmp_path / "temp_agentic_core" / "L5_safety"
        layer_dir.mkdir(parents=True)
        temp_file = layer_dir / "TestAgent.py"
        temp_file.write_text(valid_code)

        result = ArchitectureGovernanceValidator.validate_file(temp_file)
        assert result["compliant"]

    def test_core_components_functionality_preserved(self):
        """Test core components validation still works."""
        from tests.guardian.test_core_components import CoreComponentsValidator

        # Empty list should be compliant
        validator = CoreComponentsValidator(critical_files=[])
        result = validator.validate()
        assert result["compliant"], f"Empty list should be compliant: {result}"
        assert result["total_files"] == 0

        validator = CoreComponentsValidator(critical_files=["nonexistent.py"])
        result = validator.validate()
        assert not result["compliant"]

    def test_forensic_audit_functionality_preserved(self):
        """Test forensic audit still works."""
        from tests.guardian.test_forensic_audit_unified import ForensicAuditScanner

        scanner = ForensicAuditScanner()
        result = scanner.scan_all_agents()

        assert result.total_agents >= 0
        assert isinstance(result.agents_by_territory, dict)
        assert isinstance(result.clean_agents, list)


class TestPerformanceRegression:
    """Performance regression tests."""

    def test_agent_scanning_performance(self):
        """Ensure agent scanning remains fast."""
        start_time = time.time()
        agents = GuardianTestBase.scan_agents()
        scan_time = time.time() - start_time

        # Allow up to 60 seconds for large repos with many files
        assert scan_time < 60.0, f"Agent scanning too slow: {scan_time:.2f}s"
        print(f"[PERF] Agent scanning: {scan_time:.3f}s for {len(agents)} agents")

    def test_ast_parsing_performance(self):
        """Ensure AST parsing remains fast."""
        agents = GuardianTestBase.scan_agents()[:20]

        start_time = time.time()
        for agent_file in agents:
            GuardianTestBase.parse_ast(agent_file)
        parse_time = time.time() - start_time

        assert parse_time < 2.0, f"AST parsing too slow: {parse_time:.2f}s"
        print(f"[PERF] AST parsing: {parse_time:.3f}s for {len(agents)} files")

    def test_forensic_audit_performance(self):
        """Ensure forensic audit remains fast."""
        from tests.guardian.test_forensic_audit_unified import ForensicAuditScanner

        start_time = time.time()
        scanner = ForensicAuditScanner()
        result = scanner.scan_all_agents()
        audit_time = time.time() - start_time

        assert audit_time < 30.0, f"Forensic audit too slow: {audit_time:.2f}s"
        print(f"[PERF] Forensic audit: {audit_time:.3f}s for {result.total_agents} agents")


class TestCoverageRegression:
    """Coverage regression tests."""

    def test_all_test_categories_covered(self):
        """Ensure all original test categories are still covered."""
        guardian_dir = PROJECT_ROOT / "tests" / "guardian"

        categories = [
            "agent_autonomy",
            "agent_validation",
            "architecture_governance",
            "core_components",
            "forensic_audit",
            "import_safety",
            "mro_integrity",
            "ssot",
        ]

        for category in categories:
            matching_files = list(guardian_dir.glob(f"*{category}*.py"))
            assert len(matching_files) > 0, f"No test file for category: {category}"

    def test_base_class_available(self):
        """Ensure base class is importable."""
        from tests.guardian.base import AgentTestMixin, GuardianTestBase, ValidationResult

        assert GuardianTestBase is not None
        assert AgentTestMixin is not None
        assert ValidationResult is not None

    def test_conftest_fixtures_available(self):
        """Ensure conftest fixtures are defined."""
        conftest_path = PROJECT_ROOT / "tests" / "guardian" / "conftest.py"
        content = conftest_path.read_text(encoding="utf-8", errors="ignore")

        required_fixtures = [
            "agent_registry",
            "layer_hierarchy",
            "guardian_performance_baseline",
            "critical_files",
            "territories",
        ]

        for fixture in required_fixtures:
            assert fixture in content, f"Missing fixture: {fixture}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
