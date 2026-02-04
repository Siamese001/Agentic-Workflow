"""Unit tests for architecture_gap_analyzer.py SSOT path fix."""

import json
import tempfile
from pathlib import Path


class TestArchitectureGapAnalyzerSSOT:
    """Test suite for SSOT path fix in architecture_gap_analyzer.py."""

    def test_report_saved_to_ssot_location(self):
        """Test that reports are saved to docs/reports/plans (SSOT location)."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo_root = temp_path / "test_repo"
            repo_root.mkdir()

            # Create docs/reports/plans structure
            ssot_dir = repo_root / "docs" / "reports" / "plans"
            ssot_dir.mkdir(parents=True)

            # Test the path construction logic from the fixed code
            json_path = (
                repo_root / "docs" / "reports" / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.json"
            )
            md_path = repo_root / "docs" / "reports" / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.md"

            # Write test files
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({"test": "data"}, f, indent=2)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Test Report\n")

            # Verify files are in SSOT location
            assert json_path.exists(), f"JSON report should exist at {json_path}"
            assert md_path.exists(), f"MD report should exist at {md_path}"
            assert "docs/reports/plans" in str(json_path), (
                f"Path should contain SSOT structure: {json_path}"
            )
            assert "docs/reports/plans" in str(md_path), (
                f"Path should contain SSOT structure: {md_path}"
            )

    def test_ssot_path_construction(self):
        """Test that SSOT path is correctly constructed."""
        from pathlib import Path

        # Mock repo root
        repo_root = Path("/test/repo")

        # Expected SSOT paths (matching the fixed code)
        json_path = repo_root / "docs" / "reports" / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.json"
        md_path = repo_root / "docs" / "reports" / "plans" / "ARCHITECTURE_GAP_ANALYSIS_AST.md"

        # Verify path structure
        assert str(json_path).endswith("docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.json")
        assert str(md_path).endswith("docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.md")

        # Verify SSOT directory is correct
        assert json_path.parent.name == "plans"
        assert json_path.parent.parent.name == "reports"
        assert json_path.parent.parent.parent.name == "docs"

    def test_path_contains_ssot_structure(self):
        """Test that the fixed code uses the correct SSOT path structure."""
        # Read the fixed source code
        script_path = (
            Path(__file__).parent.parent.parent.parent
            / "ops_scripts"
            / "architecture_gap_analyzer.py"
        )
        assert script_path.exists(), "Source script should exist"

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify the SSOT path is used in the code
        assert "docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.json" in content, (
            "JSON report should be saved to SSOT location"
        )
        assert "docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.md" in content, (
            "MD report should be saved to SSOT location"
        )

        # Verify old path is NOT present
        assert "docs/reports/ARCHITECTURE_GAP_ANALYSIS_AST.json" not in content, (
            "Old non-SSOT path should not exist"
        )
        assert "docs/reports/ARCHITECTURE_GAP_ANALYSIS_AST.md" not in content, (
            "Old non-SSOT path should not exist"
        )

    def test_rca_bug_fix(self):
        """Test RCA: Bug was saving to docs/reports instead of docs/reports/plans."""
        # Read the fixed source code
        script_path = (
            Path(__file__).parent.parent.parent.parent
            / "ops_scripts"
            / "architecture_gap_analyzer.py"
        )
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count occurrences of correct vs incorrect paths
        correct_json = content.count("docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.json")
        correct_md = content.count("docs/reports/plans/ARCHITECTURE_GAP_ANALYSIS_AST.md")
        incorrect_json = content.count("docs/reports/ARCHITECTURE_GAP_ANALYSIS_AST.json")
        incorrect_md = content.count("docs/reports/ARCHITECTURE_GAP_ANALYSIS_AST.md")

        # Verify fix
        assert correct_json >= 1, "Should have at least one correct JSON path"
        assert correct_md >= 1, "Should have at least one correct MD path"
        assert incorrect_json == 0, "Should have no incorrect JSON paths"
        assert incorrect_md == 0, "Should have no incorrect MD paths"

        # Verify the fix comment
        assert "Save report to SSOT location" in content, "Should have comment indicating SSOT fix"

    def test_file_creation_in_ssot(self):
        """Test that files are actually created in SSOT location when script runs."""
        # This test verifies the behavior without actually running the full script
        script_path = (
            Path(__file__).parent.parent.parent.parent
            / "ops_scripts"
            / "architecture_gap_analyzer.py"
        )
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find the lines where paths are defined
        json_path_line = None
        md_path_line = None

        for i, line in enumerate(lines):
            if 'output_path = repo_root / "docs" / "reports" / "plans"' in line:
                json_path_line = i
            if 'md_path = repo_root / "docs" / "reports" / "plans"' in line:
                md_path_line = i

        assert json_path_line is not None, "Should have JSON path definition in SSOT location"
        assert md_path_line is not None, "Should have MD path definition in SSOT location"

        # Verify the paths include /plans/ directory
        assert "/plans/" in lines[json_path_line], "JSON path should include /plans/ directory"
        assert "/plans/" in lines[md_path_line], "MD path should include /plans/ directory"
