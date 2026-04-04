#!/usr/bin/env python3
"""
Test suite for capability_extractor.py - Phase 3 Implementation
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import json
import tempfile
from unittest.mock import patch

import pytest

# Import with graceful fallback
try:
    from tools.adg.capability_extractor import CapabilityExtractor
except ImportError as _import_err:
    pytest.skip(f"capability_extractor not available: {_import_err}", allow_module_level=True)


class TestCapabilityExtractor:
    """Test suite for CapabilityExtractor class."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Mock ContextWindowEstimator
        with patch('tools.adg.capability_extractor.ContextWindowEstimator') as mock_estimator:
            self.extractor = CapabilityExtractor(str(self.repo_root))
            self.mock_estimator = mock_estimator

    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test CapabilityExtractor initialization."""
        assert self.extractor.repo_root == self.repo_root
        assert self.extractor.adg_dir == self.repo_root / "tools" / "adg"
        assert self.extractor.shared_modules_dir == self.repo_root / "tools" / "adg" / "shared_modules"
        assert self.extractor.shared_modules_dir.exists()
        assert isinstance(self.extractor.capability_patterns, dict)
        assert "file_operations" in self.extractor.capability_patterns

    def test_load_manifest_file_not_found(self):
        """Test load_manifest with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.load_manifest("nonexistent.json")

    def test_load_manifest_success(self):
        """Test load_manifest with valid file."""
        # Create test manifest
        test_data = {"files": [{"path": "test.py", "classification": "legitimate"}]}
        manifest_path = self.repo_root / "test_manifest.json"

        with open(manifest_path, 'w') as f:
            json.dump(test_data, f)

        result = self.extractor.load_manifest(str(manifest_path))
        assert result == test_data["files"]

    def test_get_legitimate_python_files_empty(self):
        """Test get_legitimate_python_files with empty manifest."""
        result = self.extractor.get_legitimate_python_files([])
        assert result == []

    def test_get_legitimate_python_files_filters(self):
        """Test get_legitimate_python_files filtering."""
        # Create test files
        tools_dir = self.repo_root / "tools" / "adg"
        tools_dir.mkdir(parents=True, exist_ok=True)

        (self.repo_root / "test.py").touch()
        (self.repo_root / "phase_test.py").touch()

        manifest = [
            {"path": "test.py", "classification": "legitimate"},
            {"path": "phase_test.py", "classification": "phase_named"},
            {"path": "missing.py", "classification": "legitimate"},
            {"path": "test.txt", "classification": "legitimate"}
        ]

        result = self.extractor.get_legitimate_python_files(manifest)
        assert len(result) == 1
        assert result[0]["path"] == "test.py"

    def test_analyze_file_capabilities_nonexistent(self):
        """Test analyze_file_capabilities with non-existent file."""
        result = self.extractor.analyze_file_capabilities(Path("nonexistent.py"))
        assert result is None

    def test_analyze_file_capabilities_outside_repo(self):
        """Test analyze_file_capabilities with file outside repo."""
        # Create file outside repo
        outside_file = Path(self.temp_dir) / ".." / "outside.py"
        outside_file.touch()

        result = self.extractor.analyze_file_capabilities(outside_file)
        assert result is None

    def test_analyze_file_capabilities_empty_file(self):
        """Test analyze_file_capabilities with empty file."""
        test_file = self.repo_root / "test.py"
        test_file.write_text("# Empty file")

        result = self.extractor.analyze_file_capabilities(test_file)
        assert result is not None
        assert result["file_path"] == "test.py"
        assert result["functions"] == []
        assert result["classes"] == []
        assert result["reusable_score"] == 0

    def test_analyze_file_capabilities_with_content(self):
        """Test analyze_file_capabilities with actual content."""
        test_file = self.repo_root / "test.py"
        test_file.write_text("""
def validate_input(data):
    '''Validate input data.'''
    return True

def _private_helper():
    pass

class TestClass:
    def method(self):
        pass
""")

        result = self.extractor.analyze_file_capabilities(test_file)
        assert result is not None
        # Note: ast.walk includes class methods as FunctionDef nodes
        assert len(result["functions"]) == 3  # validate_input, _private_helper, method
        assert len(result["classes"]) == 1

        # Check function details
        public_funcs = [f for f in result["functions"] if not f["is_private"]]
        assert len(public_funcs) == 2  # validate_input, method
        assert any(f["name"] == "validate_input" for f in public_funcs)

        # Check class details
        assert result["classes"][0]["name"] == "TestClass"
        assert "method" in result["classes"][0]["methods"]

        # Check capability pattern detection
        assert "validation" in result["capability_patterns"]
        assert "validate_input" in result["capability_patterns"]["validation"]

        # Check reusable score
        assert result["reusable_score"] > 0

    def test_identify_extraction_candidates_empty(self):
        """Test identify_extraction_candidates with empty list."""
        result = self.extractor.identify_extraction_candidates([])
        assert result == []

    def test_identify_extraction_candidates_low_scores(self):
        """Test identify_extraction_candidates with low scores."""
        analyses = [
            {"reusable_score": 1, "file_path": "test1.py"},
            {"reusable_score": 2, "file_path": "test2.py"}
        ]
        result = self.extractor.identify_extraction_candidates(analyses)
        assert result == []

    def test_identify_extraction_candidates_high_scores(self):
        """Test identify_extraction_candidates with high scores."""
        analyses = [
            {"reusable_score": 3, "file_path": "test1.py"},
            {"reusable_score": 5, "file_path": "test2.py"},
            {"reusable_score": 4, "file_path": "test3.py"}
        ]
        result = self.extractor.identify_extraction_candidates(analyses)
        assert len(result) == 3
        # Should be sorted by score descending
        assert result[0]["reusable_score"] == 5
        assert result[1]["reusable_score"] == 4
        assert result[2]["reusable_score"] == 3

    def test_identify_extraction_candidates_limit(self):
        """Test identify_extraction_candidates respects limit of 20."""
        analyses = [{"reusable_score": 10, "file_path": f"test{i}.py"} for i in range(25)]
        result = self.extractor.identify_extraction_candidates(analyses)
        assert len(result) == 20  # Should be limited to 20

    def test_determine_primary_capability_with_patterns(self):
        """Test _determine_primary_capability with capability patterns."""
        candidate = {
            "file_path": "test.py",
            "capability_patterns": {
                "validation": ["validate1", "validate2"],
                "file_operations": ["read_file"]
            }
        }
        result = self.extractor._determine_primary_capability(candidate)
        assert result == "validation"  # Should pick the one with most functions

    def test_determine_primary_capability_no_patterns(self):
        """Test _determine_primary_capability with no capability patterns."""
        candidate = {"file_path": "test_file.py"}
        result = self.extractor._determine_primary_capability(candidate)
        assert result == "extracted_test_file"

    def test_extract_capability_nonexistent_file(self):
        """Test extract_capability with non-existent source file."""
        candidate = {"file_path": "nonexistent.py", "reusable_score": 10}
        result = self.extractor.extract_capability(candidate)
        assert result is False

    def test_extract_capability_no_public_code(self):
        """Test extract_capability with no public code to extract."""
        test_file = self.repo_root / "test.py"
        test_file.write_text("""
def _private_func():
    pass
""")

        candidate = {
            "file_path": "test.py",
            "reusable_score": 0,
            "functions": [{"name": "_private_func", "is_private": True}],
            "classes": []
        }

        result = self.extractor.extract_capability(candidate)
        assert result is False  # Should return False when no code extracted

    def test_extract_capability_success(self):
        """Test extract_capability successful extraction."""
        # Ensure shared_modules directory exists
        shared_dir = self.repo_root / "tools" / "adg" / "shared_modules"
        shared_dir.mkdir(parents=True, exist_ok=True)

        test_file = self.repo_root / "test.py"
        test_file.write_text("""
def validate_input(data):
    return True

class TestValidator:
    def check(self):
        pass
""")

        candidate = {
            "file_path": "test.py",
            "reusable_score": 5,
            "functions": [{"name": "validate_input", "is_private": False}],
            "classes": [{"name": "TestValidator", "is_private": False}]
        }

        result = self.extractor.extract_capability(candidate)
        assert result is True

        # Check that module was created (fallback to extracted_test when no patterns)
        module_path = self.extractor.shared_modules_dir / "extracted_test.py"
        assert module_path.exists()

        # Check module content
        content = module_path.read_text()
        assert "Extracted capability module: extracted_test" in content
        assert "def validate_input(data):" in content
        assert "class TestValidator:" in content

        # Check extraction log
        assert len(self.extractor.extraction_log) == 1
        log_entry = self.extractor.extraction_log[0]
        assert log_entry["source_file"] == "test.py"
        assert log_entry["capability"] == "extracted_test"
        assert log_entry["status"] == "extracted"

    def test_save_extraction_log(self):
        """Test save_extraction_log."""
        # Add test log entry
        self.extractor.extraction_log = [
            {
                "timestamp": "2026-03-27T00:00:00",
                "source_file": "test.py",
                "target_module": "tools/adg/shared_modules/test.py",
                "capability": "test",
                "status": "extracted"
            }
        ]

        log_path = self.extractor.save_extraction_log("test_log.json")

        # Verify log file exists and has correct content
        assert log_path.exists()

        with open(log_path) as f:
            log_data = json.load(f)

        assert log_data["total_extractions"] == 1
        assert len(log_data["extractions"]) == 1
        assert log_data["extractions"][0]["source_file"] == "test.py"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
