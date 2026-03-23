"""Test zip creation and archiving functionality with comprehensive error handling.

Tests the fixes for the _0655 archive failure issue:
1. Zip creation with missing runtime files
2. Graceful fallback to individual file archiving
3. Orphaned run detection and cleanup
4. Error handling and logging
"""

import gzip
import pathlib

# Add project root to path
import sys
import zipfile
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))

from tools.generate_full_adg import (
    _RUNTIME_ENFORCEMENT_FILES,
    _archive_individual_files,
    _archive_old_artifacts,
    _archive_zip_files,
    _create_zip_archive,
)


class TestZipCreation:
    """Test zip creation with various failure scenarios."""

    def test_zip_creation_success(self, tmp_path):
        """Test successful zip creation with all files present."""
        # Setup test artifacts
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create mock artifacts
        artifacts = [
            artifact_dir / "adg_snapshot_03232026_1025.json",
            artifact_dir / "adg_indexed_03232026_1025.sqlite",
            artifact_dir / "adg_symbol_graph_03232026_1025.json"
        ]
        for artifact in artifacts:
            artifact.write_text("test content")

        # Create mock runtime files
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        for runtime_path in _RUNTIME_ENFORCEMENT_FILES:
            full_path = repo_root / runtime_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("runtime content")

        # Test zip creation
        with patch('tools.generate_full_adg.ROOT', repo_root):
            zip_path = _create_zip_archive(artifact_dir, "03232026_1025", artifacts)

        # Verify zip exists and contains expected files
        assert zip_path.exists()
        assert zip_path.name == "adg_run_03232026_1025.zip"

        # Close any potential file handles by opening and closing the zip
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            assert len(files) >= len(artifacts) + len(_RUNTIME_ENFORCEMENT_FILES)
            assert any("adg/adg_snapshot_03232026_1025.json" in f for f in files)
            assert any("runtime/" + _RUNTIME_ENFORCEMENT_FILES[0] in f for f in files)

    def test_zip_creation_missing_runtime_file(self, tmp_path):
        """Test zip creation failure when runtime files are missing."""
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create mock artifacts
        artifacts = [
            artifact_dir / "adg_snapshot_03232026_1025.json",
            artifact_dir / "adg_indexed_03232026_1025.sqlite"
        ]
        for artifact in artifacts:
            artifact.write_text("test content")

        # Create repo root with missing runtime files
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        # Don't create runtime files - they're missing

        # Test zip creation should fail with missing runtime files
        with patch('tools.generate_full_adg.ROOT', repo_root):
            with pytest.raises(RuntimeError) as exc_info:
                _create_zip_archive(artifact_dir, "03232026_1025", artifacts)

        # Check that the error mentions missing runtime files
        error_msg = str(exc_info.value)
        assert "Missing critical runtime files" in error_msg or "runtime file" in error_msg.lower()

        # Verify no incomplete zip file left behind
        zip_path = artifact_dir / "adg_run_03232026_1025.zip"
        assert not zip_path.exists()

    def test_zip_creation_missing_artifacts(self, tmp_path):
        """Test zip creation succeeds with missing artifacts but fails with missing runtime."""
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create only some artifacts (missing others)
        artifacts = [
            artifact_dir / "adg_snapshot_03232026_1025.json",  # exists
            artifact_dir / "adg_indexed_03232026_1025.sqlite",   # exists
            artifact_dir / "missing_file.json"                   # missing
        ]
        artifacts[0].write_text("test content")
        artifacts[1].write_text("test content")
        # artifacts[2] is missing

        # Create mock runtime files
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        for runtime_path in _RUNTIME_ENFORCEMENT_FILES:
            full_path = repo_root / runtime_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("runtime content")

        # Test zip creation should succeed (missing artifacts are warnings)
        with patch('tools.generate_full_adg.ROOT', repo_root):
            zip_path = _create_zip_archive(artifact_dir, "03232026_1025", artifacts)

        # Verify zip exists and contains only existing files
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            assert any("adg/adg_snapshot_03232026_1025.json" in f for f in files)
            assert any("adg/adg_indexed_03232026_1025.sqlite" in f for f in files)
            assert not any("missing_file.json" in f for f in files)


class TestArchivingFunctions:
    """Test archiving helper functions."""

    def test_archive_zip_files(self, tmp_path):
        """Test successful zip file archiving."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()

        # Create test zip file
        zip_file = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr("test.txt", "test content")

        # Archive the zip
        archived_count, bytes_original, bytes_archived = _archive_zip_files([zip_file], archive_dir)

        # Verify results
        assert archived_count == 1
        assert bytes_original > 0
        assert bytes_archived > 0
        assert not zip_file.exists()  # Original removed

        # Verify compressed archive exists
        archive_path = archive_dir / "test.zip.gz"
        assert archive_path.exists()

        # Verify compressed content is valid
        with gzip.open(archive_path, 'rb') as gz:
            with zipfile.ZipFile(gz, 'r') as zf:
                assert "test.txt" in zf.namelist()

    def test_archive_individual_files(self, tmp_path):
        """Test individual file archiving for orphaned runs."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()

        # Create test files
        files = [
            tmp_path / "file1.json",
            tmp_path / "file2.sqlite",
            tmp_path / "file3.txt"
        ]
        for i, f in enumerate(files):
            f.write_text(f"content {i}")

        # Archive the files
        archived_count, bytes_original, bytes_archived = _archive_individual_files(files, archive_dir)

        # Verify results
        assert archived_count == len(files)
        assert bytes_original > 0
        assert bytes_archived > 0

        # Verify all original files removed
        for f in files:
            assert not f.exists()

        # Verify all compressed archives exist and have correct content
        for i, f in enumerate(files):
            archive_path = archive_dir / f"{f.name}.gz"
            assert archive_path.exists()

            # Verify compressed content matches original
            with gzip.open(archive_path, 'rt') as gz:
                content = gz.read()
                assert f"content {i}" in content


class TestOrphanedRunHandling:
    """Test detection and handling of orphaned runs."""

    def test_archive_old_artifacts_with_orphaned_run(self, tmp_path):
        """Test archiving logic properly handles orphaned runs."""
        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()

        # Create orphaned run files (no zip file) - use correct timestamp format
        orphaned_files = [
            adg_dir / "adg_snapshot_03232026_0655.json",
            adg_dir / "adg_indexed_03232026_0655.sqlite",
            adg_dir / "adg_symbol_graph_03232026_0655.json"
        ]
        for f in orphaned_files:
            f.write_text("orphaned content")

        # Create current run with zip - use newer timestamp
        current_zip = adg_dir / "adg_run_03232026_1025.zip"
        with zipfile.ZipFile(current_zip, 'w') as zf:
            zf.writestr("current.json", "current content")

        # Force archiving by setting keep_runs=0 (archive everything)
        _archive_old_artifacts(adg_dir, "03232026_1025", keep_runs=0)

        # Verify archive directory was created
        archive_dir = adg_dir / "_archive"
        assert archive_dir.exists()

        # Verify month subdirectory exists
        month_dir = archive_dir / "2026-03"
        assert month_dir.exists()

        # Verify orphaned files were archived
        for f in orphaned_files:
            archive_path = month_dir / f"{f.name}.gz"
            assert archive_path.exists()
            assert not f.exists()  # Original removed

        # Note: With keep_runs=0, even current run gets archived
        assert not current_zip.exists()
        # Verify current run was also archived
        current_archive_path = month_dir / "adg_run_03232026_1025.zip.gz"
        assert current_archive_path.exists()

    def test_archive_old_artifacts_with_zip_and_individual(self, tmp_path):
        """Test archiving when both zip and individual files exist for same run."""
        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()

        # Create old run with both zip and individual files
        old_zip = adg_dir / "adg_run_03232026_0655.zip"
        old_individual = adg_dir / "adg_snapshot_03232026_0655.json"

        with zipfile.ZipFile(old_zip, 'w') as zf:
            zf.writestr("old.json", "old content")
        old_individual.write_text("individual content")  # This should be removed

        # Create current run with newer timestamp
        current_zip = adg_dir / "adg_run_03232026_1025.zip"
        with zipfile.ZipFile(current_zip, 'w') as zf:
            zf.writestr("current.json", "current content")

        # Run archiving with keep_runs=0 to force archiving
        _archive_old_artifacts(adg_dir, "03232026_1025", keep_runs=0)

        # Verify archive directory was created
        archive_dir = adg_dir / "_archive"
        assert archive_dir.exists()

        # Verify month subdirectory exists
        month_dir = archive_dir / "2026-03"
        assert month_dir.exists()

        # Verify old run handled correctly
        assert (month_dir / "adg_run_03232026_0655.zip.gz").exists()
        assert (month_dir / "adg_snapshot_03232026_0655.json.gz").exists()

        # Both original files should be removed
        assert not old_zip.exists()
        assert not old_individual.exists()

        # Note: With keep_runs=0, even current run gets archived
        assert not current_zip.exists()
        # Verify current run was also archived
        current_archive_path = month_dir / "adg_run_03232026_1025.zip.gz"
        assert current_archive_path.exists()


class TestErrorHandling:
    """Test error handling and recovery scenarios."""

    def test_zip_creation_disk_space_error(self, tmp_path):
        """Test handling of disk space errors during zip creation."""
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create mock artifacts
        artifacts = [artifact_dir / "test.json"]
        artifacts[0].write_text("test content")

        # Create mock runtime files
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        for runtime_path in _RUNTIME_ENFORCEMENT_FILES:
            full_path = repo_root / runtime_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("runtime content")

        # Mock disk space error
        with patch('tools.generate_full_adg.ROOT', repo_root):
            with patch('zipfile.ZipFile.__enter__', side_effect=OSError("No space left on device")):
                with pytest.raises(RuntimeError, match="Zip creation failed"):
                    _create_zip_archive(artifact_dir, "03232026_1025", artifacts)

        # Verify no incomplete zip file
        zip_path = artifact_dir / "adg_run_03232026_1025.zip"
        assert not zip_path.exists()

    def test_archive_compression_error(self, tmp_path):
        """Test handling of compression errors during archiving."""
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()

        # Create test file
        zip_file = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr("test.txt", "test content")

        # Mock compression error
        with patch('gzip.open', side_effect=OSError("Compression failed")):
            archived_count, bytes_original, bytes_archived = _archive_zip_files([zip_file], archive_dir)

        # Verify error handling
        assert archived_count == 0
        assert zip_file.exists()  # Original should remain


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_workflow_zip_success(self, tmp_path):
        """Test complete workflow with successful zip creation."""
        # This would test the full generate_full_adg function
        # but requires extensive mocking of the ADG scanner
        pass

    def test_full_workflow_zip_failure_recovery(self, tmp_path):
        """Test complete workflow with zip failure and recovery."""
        # This would test the full workflow when zip fails
        # but requires extensive mocking
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
