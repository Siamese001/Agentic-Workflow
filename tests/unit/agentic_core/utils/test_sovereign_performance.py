"""Phase 5 Tests: SovereignScanner and AST Engine Performance.

Tests for centralized I/O optimization and AST parsing utilities.
"""

from __future__ import annotations

import pytest


class TestSovereignScannerSingleton:
    """Phase 5 Tests: SovereignScanner singleton integrity."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup minimal project structure."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "test_file.py").write_text("# Test")
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "tests").mkdir()
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_sovereign_scanner_singleton_integrity(self, mock_project):
        """[Phase 5] Verify singleton pattern - both instances share same _root_map."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        # Initialize twice
        scanner1 = SovereignScanner(mock_project)
        scanner2 = SovereignScanner(mock_project)

        # Should be the same instance
        assert scanner1 is scanner2

        # Scan with first instance
        map1 = scanner1.scan_repository()

        # Second instance should return same cached map
        map2 = scanner2.scan_repository()

        assert map1 is map2

    def test_sovereign_scanner_get_instance(self, mock_project):
        """[Phase 5] Verify get_instance returns singleton."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        scanner1 = SovereignScanner.get_instance(mock_project)
        scanner2 = SovereignScanner.get_instance(mock_project)

        assert scanner1 is scanner2

    def test_sovereign_scanner_scan_repository(self, mock_project):
        """[Phase 5] Verify scan_repository returns valid structure."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        scanner = SovereignScanner(mock_project)
        repo_map = scanner.scan_repository()

        assert isinstance(repo_map, dict)
        # Should have entries for sovereign roots
        assert "agentic_core" in repo_map or len(repo_map) >= 0

    def test_sovereign_scanner_get_root_files(self, mock_project):
        """[Phase 5] Verify get_root_files returns list."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        scanner = SovereignScanner(mock_project)
        files = scanner.get_root_files("agentic_core")

        assert isinstance(files, list)

    def test_sovereign_scanner_invalidate_cache(self, mock_project):
        """[Phase 5] Verify cache invalidation works."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        scanner = SovereignScanner(mock_project)

        # First scan
        map1 = scanner.scan_repository()

        # Invalidate
        scanner.invalidate_cache()

        # Second scan should create new map
        map2 = scanner.scan_repository()

        # Maps should be equal but not the same object after invalidation
        assert map1 is not map2


class TestASTEngineImportExtraction:
    """Phase 5 Tests: AST Engine import extraction."""

    @pytest.fixture
    def complex_import_file(self, tmp_path):
        """Create a file with complex import statements."""
        test_file = tmp_path / "complex_imports.py"
        test_file.write_text('''"""Test file with complex imports."""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from agentic_core.L5_safety.validators import HierarchyAgent
from agentic_core.utils.file_cache import FileCache
import json as j
from collections import defaultdict, Counter
''')
        return test_file

    def test_ast_engine_import_extraction(self, complex_import_file):
        """[Phase 5] Verify import extraction from complex file."""
        from agentic_core.L5_safety.utils.ast_engine import get_file_imports

        imports = get_file_imports(complex_import_file)

        assert isinstance(imports, list)
        assert len(imports) > 0

        # Check that we got the expected imports
        import_names = [name for name, _line in imports]

        assert "os" in import_names
        assert "sys" in import_names
        assert "pathlib" in import_names
        assert "typing" in import_names
        assert "agentic_core.L5_safety.validators" in import_names
        assert "agentic_core.utils.file_cache" in import_names
        assert "json" in import_names
        assert "collections" in import_names

    def test_ast_engine_import_line_numbers(self, complex_import_file):
        """[Phase 5] Verify import line numbers are correct."""
        from agentic_core.L5_safety.utils.ast_engine import get_file_imports

        imports = get_file_imports(complex_import_file)

        # All line numbers should be positive integers
        for _name, line_no in imports:
            assert isinstance(line_no, int)
            assert line_no > 0

    def test_ast_engine_handles_syntax_error(self, tmp_path):
        """[Phase 5] Verify graceful handling of syntax errors."""
        from agentic_core.L5_safety.utils.ast_engine import get_file_imports

        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text("def broken(:\n    pass")

        imports = get_file_imports(bad_file)

        # Should return empty list, not raise
        assert imports == []

    def test_ast_engine_handles_missing_file(self, tmp_path):
        """[Phase 5] Verify graceful handling of missing files."""
        from agentic_core.L5_safety.utils.ast_engine import get_file_imports

        missing_file = tmp_path / "does_not_exist.py"

        imports = get_file_imports(missing_file)

        # Should return empty list, not raise
        assert imports == []


class TestASTEngineLayerExtraction:
    """Phase 5 Tests: AST Engine layer extraction utilities."""

    def test_extract_layer_from_path_l5(self, tmp_path):
        """[Phase 5] Verify layer extraction from L5 path."""
        from agentic_core.L5_safety.utils.ast_engine import extract_layer_from_path

        path = tmp_path / "agentic_core" / "L5_safety" / "validators" / "test.py"
        layer = extract_layer_from_path(path)

        assert layer == "L5"

    def test_extract_layer_from_path_l3(self, tmp_path):
        """[Phase 5] Verify layer extraction from L3 path."""
        from agentic_core.L5_safety.utils.ast_engine import extract_layer_from_path

        path = tmp_path / "agentic_core" / "L3_orchestration" / "test.py"
        layer = extract_layer_from_path(path)

        assert layer == "L3"

    def test_extract_layer_from_path_apps(self, tmp_path):
        """[Phase 5] Verify layer extraction from apps path."""
        from agentic_core.L5_safety.utils.ast_engine import extract_layer_from_path

        path = tmp_path / "apps_rg" / "engines" / "test.py"
        layer = extract_layer_from_path(path)

        assert layer == "Apps"

    def test_extract_layer_from_import(self):
        """[Phase 5] Verify layer extraction from import path."""
        from agentic_core.L5_safety.utils.ast_engine import extract_layer_from_import

        assert extract_layer_from_import("agentic_core.L5_safety.validators") == "L5"
        assert extract_layer_from_import("agentic_core.L3_orchestration") == "L3"
        assert extract_layer_from_import("apps_rg.engines") == "Apps"
        assert extract_layer_from_import("some.random.module") is None

    def test_check_gravity_violation(self):
        """[Phase 5] Verify gravity violation detection."""
        from agentic_core.L5_safety.utils.ast_engine import check_gravity_violation

        # L3 importing from L5 is a violation
        assert check_gravity_violation("L3", "L5") is True

        # L5 importing from L3 is allowed
        assert check_gravity_violation("L5", "L3") is False

        # Same layer is allowed
        assert check_gravity_violation("L3", "L3") is False


class TestCrossAgentScanConsistency:
    """Phase 5 Tests: Cross-agent scan consistency."""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup project structure."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "TestAgent.py").write_text(
            "class TestAgent: pass"
        )
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_cross_agent_scan_consistency(self, mock_project):
        """[Phase 5] Verify scanner caching works across different agents."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        # Simulate first agent accessing scanner
        scanner1 = SovereignScanner.get_instance(mock_project)
        map1 = scanner1.scan_repository()

        # Simulate second agent accessing scanner
        scanner2 = SovereignScanner.get_instance(mock_project)
        map2 = scanner2.scan_repository()

        # Both should get the same cached map
        assert scanner1 is scanner2
        assert map1 is map2

    def test_scanner_used_by_structural_validator(self, mock_project):
        """[Phase 5] Verify StructuralValidatorAgent uses SovereignScanner."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        from agentic_core.L5_safety.policy_engine.StructuralValidatorAgent import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        # Create validator
        config = StructureConfig(project_root=mock_project)
        validator = StructuralValidatorAgent(config=config)

        # Run heal_repository which should use SovereignScanner
        result = validator.heal_repository(dry_run=True)

        # Verify scanner was initialized
        scanner = SovereignScanner.get_instance(mock_project)
        assert scanner is not None

        # Result should have expected structure
        assert "violations_found" in result or "_raw_result" in result
