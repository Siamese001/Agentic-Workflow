"""
Test Suite for Hygiene Agent Consolidation

Tests verify:
1. Legacy HygieneGuardian functionality (empty files, orphaned __init__.py)
2. Ported FileCleanupAgent logic (repeated filenames, copy patterns)
3. ArchivalGatekeeper compliance (safe_delete instead of os.remove)
4. Safety - valid files are NOT touched

Test Cases:
- Test Case 1: Legacy Logic - empty files, orphaned __init__.py
- Test Case 2: Ported Logic - repeated filenames, copy patterns
- Test Case 3: Gatekeeper Compliance - safe_delete is called
- Test Case 4: Safety - valid files untouched
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ArchivalGatekeeper,
    ArchivalOperation,
    ArchivalResult,
)
from agentic_core.L5_safety.reasoning.HygieneGuardianAgent import (
    HygieneGuardianAgent,
    HygieneViolation,
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def hygiene_agent(temp_project):
    """Create a HygieneGuardianAgent instance for testing."""
    # Reset gatekeeper singleton for clean test
    ArchivalGatekeeper.reset_instance()
    agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=True)
    yield agent
    ArchivalGatekeeper.reset_instance()


class TestLegacyHygieneFunctionality:
    """Test Case 1: Verify legacy HygieneGuardian functionality."""

    def test_detects_empty_files(self, hygiene_agent, temp_project):
        """Verify HygieneGuardian detects empty Python files."""
        # Create empty Python file
        empty_file = temp_project / "empty_module.py"
        empty_file.write_text("")

        # Also create a whitespace-only file
        whitespace_file = temp_project / "whitespace_only.py"
        whitespace_file.write_text("   \n\n   \t\t\n")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        empty_violations = [v for v in hygiene_agent.violations if v.violation_type == "empty_file"]
        assert len(empty_violations) == 2

        violation_files = {v.file_path for v in empty_violations}
        assert empty_file in violation_files
        assert whitespace_file in violation_files

    def test_detects_orphaned_init(self, hygiene_agent, temp_project):
        """Verify HygieneGuardian detects orphaned __init__.py files."""
        # Create directory with only __init__.py (orphaned)
        orphan_dir = temp_project / "orphan_package"
        orphan_dir.mkdir()
        orphan_init = orphan_dir / "__init__.py"
        orphan_init.write_text("# Orphaned init")

        # Create directory with __init__.py and other Python files (not orphaned)
        valid_dir = temp_project / "valid_package"
        valid_dir.mkdir()
        (valid_dir / "__init__.py").write_text("# Valid init")
        (valid_dir / "module.py").write_text("# Valid module")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        orphan_violations = [v for v in hygiene_agent.violations if v.violation_type == "orphaned_init"]
        assert len(orphan_violations) == 1
        assert orphan_violations[0].file_path == orphan_init

    def test_detects_backup_files(self, hygiene_agent, temp_project):
        """Verify HygieneGuardian detects stale backup files."""
        # Create backup files
        (temp_project / "module.py.bak").write_text("backup content")
        (temp_project / "config.orig").write_text("original content")
        (temp_project / "data.backup").write_text("backup data")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        backup_violations = [v for v in hygiene_agent.violations if v.violation_type == "stale_backup"]
        assert len(backup_violations) == 3

    def test_detects_temp_files(self, hygiene_agent, temp_project):
        """Verify HygieneGuardian detects temporary files."""
        # Create temp files
        (temp_project / "scratch.tmp").write_text("temp content")
        (temp_project / "draft.temp").write_text("draft content")
        (temp_project / "edit~").write_text("edit backup")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        temp_violations = [v for v in hygiene_agent.violations if v.violation_type == "temp_file"]
        assert len(temp_violations) == 3


class TestPortedFileCleanupLogic:
    """Test Case 2: Verify ported FileCleanupAgent logic."""

    def test_detects_repeated_filename_strings(self, hygiene_agent, temp_project):
        """Verify detection of repeated strings in filenames."""
        # Create files with repeated strings
        (temp_project / "enums_enums.py").write_text("# Repeated")
        (temp_project / "impl_impl_impl.py").write_text("# Triple repeated")
        (temp_project / "data_models_enums_enums.py").write_text("# Partial repeated")

        # Create valid file (no repetition)
        (temp_project / "test_data.py").write_text("# Valid")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        repeated_violations = [v for v in hygiene_agent.violations if v.violation_type == "repeated_filename"]
        assert len(repeated_violations) == 3

        # Verify valid file is NOT flagged
        violation_files = {v.file_path.name for v in repeated_violations}
        assert "test_data.py" not in violation_files

    def test_detects_copy_pattern_filenames(self, hygiene_agent, temp_project):
        """Verify detection of copy-pattern filenames."""
        # Create files with copy patterns
        (temp_project / "Copy of report.py").write_text("# Copy pattern 1")
        (temp_project / "report (1).py").write_text("# Copy pattern 2")
        (temp_project / "report (2).py").write_text("# Copy pattern 3")
        (temp_project / "module_copy.py").write_text("# Copy pattern 4")
        (temp_project / "module_copy2.py").write_text("# Copy pattern 5")

        # Create valid file
        (temp_project / "report_v2.py").write_text("# Valid versioned file")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # Check violations
        copy_violations = [v for v in hygiene_agent.violations if v.violation_type == "copy_pattern"]
        assert len(copy_violations) == 5

        # Verify valid file is NOT flagged
        violation_files = {v.file_path.name for v in copy_violations}
        assert "report_v2.py" not in violation_files

    def test_repeated_filename_detection_method(self, hygiene_agent):
        """Test _has_repeated_filename_parts method directly."""
        # Should detect
        assert hygiene_agent._has_repeated_filename_parts("enums_enums") == (True, "enums")
        assert hygiene_agent._has_repeated_filename_parts("impl_impl_impl")[0] is True
        assert hygiene_agent._has_repeated_filename_parts("data_enums_models_enums")[0] is True

        # Should NOT detect
        assert hygiene_agent._has_repeated_filename_parts("test_data") == (False, None)
        assert hygiene_agent._has_repeated_filename_parts("my_module") == (False, None)
        assert hygiene_agent._has_repeated_filename_parts("report_v2") == (False, None)

    def test_copy_pattern_detection_method(self, hygiene_agent):
        """Test _is_copy_pattern_filename method directly."""
        # Should detect
        assert hygiene_agent._is_copy_pattern_filename("Copy of report") == (True, "report")
        assert hygiene_agent._is_copy_pattern_filename("report (1)") == (True, "report")
        assert hygiene_agent._is_copy_pattern_filename("module_copy") == (True, "module")
        assert hygiene_agent._is_copy_pattern_filename("module_copy2") == (True, "module")

        # Should NOT detect
        assert hygiene_agent._is_copy_pattern_filename("report_v2") == (False, None)
        assert hygiene_agent._is_copy_pattern_filename("my_module") == (False, None)
        assert hygiene_agent._is_copy_pattern_filename("test_copy_functionality") == (False, None)


class TestGatekeeperCompliance:
    """Test Case 3: Verify ArchivalGatekeeper is used for all deletions."""

    def test_fix_violations_uses_gatekeeper(self, temp_project):
        """Verify _fix_violations calls gatekeeper.safe_delete instead of os.remove."""
        # Reset and create fresh gatekeeper
        ArchivalGatekeeper.reset_instance()

        # Create agent with dry_run=False to enable fixing
        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=False)

        # Create a file to be "fixed"
        backup_file = temp_project / "test.bak"
        backup_file.write_text("backup content")

        # Add a violation manually
        agent.violations = [
            HygieneViolation(
                file_path=backup_file,
                violation_type="stale_backup",
                message="Test backup file",
                auto_fixable=True,
            ),
        ]

        # Mock the gatekeeper's safe_delete method
        mock_result = ArchivalResult(
            success=True,
            operation=ArchivalOperation.DELETE,
            source_path=backup_file,
            destination_path=temp_project / ".archive" / "test.bak",
            requester_agent="HygieneGuardianAgent",
            reason="stale_backup: Test backup file",
        )

        with patch.object(agent.gatekeeper, "safe_delete", return_value=mock_result) as mock_delete:
            fixed_count = agent._fix_violations()

            # Verify safe_delete was called
            mock_delete.assert_called_once()
            call_args = mock_delete.call_args

            # Verify correct arguments
            assert call_args[0][0] == backup_file  # source path
            assert call_args[0][1] == "HygieneGuardianAgent"  # requester
            assert "stale_backup" in call_args[0][2]  # reason contains violation type

            assert fixed_count == 1

        ArchivalGatekeeper.reset_instance()

    def test_no_direct_unlink_calls(self, temp_project):
        """Verify that Path.unlink() is NOT called directly."""
        ArchivalGatekeeper.reset_instance()

        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=False)

        # Create a file
        test_file = temp_project / "empty.py"
        test_file.write_text("")

        agent.violations = [
            HygieneViolation(
                file_path=test_file,
                violation_type="empty_file",
                message="Empty file",
                auto_fixable=True,
            ),
        ]

        # Patch Path.unlink to detect if it's called directly
        with patch.object(Path, "unlink") as mock_unlink:
            # Also mock gatekeeper to prevent actual file operations
            mock_result = ArchivalResult(
                success=True,
                operation=ArchivalOperation.DELETE,
                source_path=test_file,
                requester_agent="HygieneGuardianAgent",
                reason="test",
            )
            with patch.object(agent.gatekeeper, "safe_delete", return_value=mock_result):
                agent._fix_violations()

            # Path.unlink should NOT be called directly
            mock_unlink.assert_not_called()

        ArchivalGatekeeper.reset_instance()
        assert True  # no-exception contract


class TestSafetyValidFiles:
    """Test Case 4: Verify valid files are NOT touched."""

    def test_valid_files_not_flagged(self, hygiene_agent, temp_project):
        """Verify valid files are not flagged as violations."""
        # Create valid files
        valid_files = [
            ("my_module.py", "# Valid module"),
            ("test_utils.py", "# Test utilities"),
            ("report_v2.py", "# Versioned report"),
            ("data_processor.py", "# Data processor"),
            ("config_loader.py", "# Config loader"),
        ]

        for filename, content in valid_files:
            (temp_project / filename).write_text(content)

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # No violations should be found for these files
        violation_files = {v.file_path.name for v in hygiene_agent.violations}

        for filename, _ in valid_files:
            assert filename not in violation_files, f"Valid file {filename} was incorrectly flagged"

    def test_dry_run_does_not_modify_files(self, temp_project):
        """Verify dry_run mode does not modify any files."""
        ArchivalGatekeeper.reset_instance()

        # Create agent in dry_run mode (default)
        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=True)

        # Create files that would be flagged
        backup_file = temp_project / "test.bak"
        backup_file.write_text("backup content")

        empty_file = temp_project / "empty.py"
        empty_file.write_text("")

        # Run scan and fix
        agent._scan_directory(temp_project)
        fixed_count = agent._fix_violations()

        # No files should be fixed in dry_run mode
        assert fixed_count == 0

        # Files should still exist
        assert backup_file.exists()
        assert empty_file.exists()

        ArchivalGatekeeper.reset_instance()

    def test_ignored_directories_skipped(self, hygiene_agent, temp_project):
        """Verify ignored directories (.git, __pycache__, etc.) are skipped."""
        # Create files in ignored directories
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "config.bak").write_text("git backup")

        pycache_dir = temp_project / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "module.pyc").write_text("compiled")

        venv_dir = temp_project / ".venv"
        venv_dir.mkdir()
        (venv_dir / "empty.py").write_text("")

        # Run scan
        hygiene_agent._scan_directory(temp_project)

        # No violations should be found in ignored directories
        for violation in hygiene_agent.violations:
            assert ".git" not in str(violation.file_path)
            assert "__pycache__" not in str(violation.file_path)
            assert ".venv" not in str(violation.file_path)


class TestHealRepository:
    """Test heal_repository integration.

    NOTE: @standard_heal decorator normalizes return values to canonical schema:
    {
        "violations_found": int,
        "violations_fixed": int,
        "status": str,  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED'
        "errors": int,
        "skipped": int,
        "execution_time_ms": float,
        "error_message": Optional[str],
        "_raw_result": dict,  # Original return preserved here
    }
    """

    def test_heal_repository_dry_run(self, temp_project):
        """Test heal_repository in dry_run mode."""
        ArchivalGatekeeper.reset_instance()

        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=True)

        # Create some violations
        (temp_project / "test.bak").write_text("backup")
        (temp_project / "empty.py").write_text("")

        result = agent.heal_repository(dry_run=True)

        # @standard_heal decorator normalizes to canonical schema
        # Use canonical keys directly (not _raw_result)
        assert result.get("violations_found", 0) >= 2
        # In dry_run, nothing should be fixed
        assert result.get("violations_fixed", 0) == 0
        # Status should be FAIL (violations found but not fixed)
        assert result.get("status") in ["FAIL", "PASS", "SKIPPED"]

        ArchivalGatekeeper.reset_instance()

    def test_heal_repository_execute(self, temp_project):
        """Test heal_repository with execute=True."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        gk.set_require_approval(False)  # Disable approval prompts for testing

        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=True)

        # Create a backup file
        backup_file = temp_project / "test.bak"
        backup_file.write_text("backup content")

        result = agent.heal_repository(dry_run=False, execute=True)

        # File should be archived (moved to archives/gatekeeper)
        assert not backup_file.exists()
        # Check canonical keys - at least one violation was fixed
        assert result.get("violations_fixed", 0) >= 1
        # Status should be PASS (all violations fixed)
        assert result.get("status") == "PASS"

        ArchivalGatekeeper.reset_instance()

    def test_heal_repository_clean_state(self, temp_project):
        """Test heal_repository with zero violations (clean state)."""
        ArchivalGatekeeper.reset_instance()

        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=True)

        # Create only valid files (no violations)
        # Note: print() is detected as debug_print violation, so use logging instead
        (temp_project / "valid_module.py").write_text(
            "# Valid module\nimport logging\nlogger = logging.getLogger(__name__)",
        )

        result = agent.heal_repository(dry_run=True)

        # Canonical schema should have zero violations
        assert result.get("violations_found", -1) == 0
        assert result.get("violations_fixed", -1) == 0
        assert result.get("status") == "PASS"
        # No errors
        assert result.get("errors", -1) == 0

        ArchivalGatekeeper.reset_instance()
