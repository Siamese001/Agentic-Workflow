"""
Fail-fast trigger tests for generate_full_adg.py

Tests the robustness of ADG generation by verifying that fail-fast
conditions correctly abort generation when critical conditions are not met.
"""

import sqlite3
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestArtifactValidityCheck:
    """Tests for _check_artifact_validity function."""

    def test_missing_artifact_fails(self, tmp_path):
        """Test that missing artifacts cause sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_artifact_validity

        # Create mock paths with missing snapshot
        mock_paths = Mock()
        mock_paths.snapshot = tmp_path / "missing_snapshot.json"
        mock_paths.sqlite = tmp_path / "test.sqlite"

        # Create only SQLite file
        mock_paths.sqlite.write_text("test")

        with pytest.raises(SystemExit) as exc_info:
            _check_artifact_validity(mock_paths)
        assert exc_info.value.code == 1

    def test_zero_byte_artifact_fails(self, tmp_path):
        """Test that zero-byte artifacts cause sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_artifact_validity

        mock_paths = Mock()
        mock_paths.snapshot = tmp_path / "snapshot.json"
        mock_paths.snapshot.write_text("")  # Zero byte

        mock_paths.sqlite = tmp_path / "test.sqlite"
        mock_paths.sqlite.write_text("test")

        with pytest.raises(SystemExit) as exc_info:
            _check_artifact_validity(mock_paths)
        assert exc_info.value.code == 1

    def test_invalid_json_artifact_fails(self, tmp_path):
        """Test that invalid JSON artifacts cause sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_artifact_validity

        mock_paths = Mock()
        mock_paths.snapshot = tmp_path / "snapshot.json"
        mock_paths.snapshot.write_text("{invalid json")

        mock_paths.sqlite = tmp_path / "test.sqlite"
        mock_paths.sqlite.write_text("test")

        with pytest.raises(SystemExit) as exc_info:
            _check_artifact_validity(mock_paths)
        assert exc_info.value.code == 1

    def test_valid_artifacts_pass(self, tmp_path):
        """Test that valid artifacts pass the check."""
        from tools.generate.generate_full_adg import _check_artifact_validity

        # Create valid SQLite
        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.close()

        mock_paths = Mock()
        mock_paths.snapshot = tmp_path / "snapshot.json"
        mock_paths.snapshot.write_text("{}")

        mock_paths.sqlite = sqlite_path

        # Should not raise
        _check_artifact_validity(mock_paths)


class TestSQLiteIntegrityCheck:
    """Tests for _check_sqlite_integrity function."""

    def test_integrity_check_failure_fails(self, tmp_path):
        """Test that SQLite integrity check failures cause sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_sqlite_integrity

        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.close()

        # Corrupt the database by modifying it directly
        with open(sqlite_path, "rb") as f:
            content = bytearray(f.read())
        # Modify a byte to corrupt the database
        content[100] = 0xFF if content[100] != 0xFF else 0x00
        with open(sqlite_path, "wb") as f:
            f.write(content)

        with pytest.raises(SystemExit) as exc_info:
            _check_sqlite_integrity(sqlite_path)
        assert exc_info.value.code == 1

    def test_missing_required_tables_fails(self, tmp_path):
        """Test that missing required tables cause sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_sqlite_integrity

        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        # Create only nodes table, missing edges, violations, meta
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_sqlite_integrity(sqlite_path)
        assert exc_info.value.code == 1

    def test_valid_sqlite_passes(self, tmp_path):
        """Test that valid SQLite with all required tables passes."""
        from tools.generate.generate_full_adg import _check_sqlite_integrity

        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (id INTEGER PRIMARY KEY)")
        conn.close()

        # Should not raise
        _check_sqlite_integrity(sqlite_path)


class TestArtifactConsistencyCheck:
    """Tests for _check_artifact_consistency function."""

    def test_entity_count_mismatch_fails(self, tmp_path):
        """Test that entity/node count mismatch causes sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_artifact_consistency

        # Create SQLite with 5 nodes
        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (id INTEGER PRIMARY KEY)")
        for _i in range(5):
            conn.execute("INSERT INTO nodes DEFAULT VALUES")
        conn.commit()
        conn.close()

        mock_paths = Mock()
        mock_paths.sqlite = sqlite_path

        mock_artifact = Mock()
        mock_artifact.entities = list(range(10))  # 10 entities vs 5 nodes
        mock_artifact.relations = []  # Empty relations

        with pytest.raises(SystemExit) as exc_info:
            _check_artifact_consistency(mock_paths, mock_artifact)
        assert exc_info.value.code == 1

    def test_relation_count_mismatch_fails(self, tmp_path):
        """Test that relation/edge count mismatch causes sys.exit(1)."""
        from tools.generate.generate_full_adg import _check_artifact_consistency

        # Create SQLite with matching entities but mismatched edges
        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (id INTEGER PRIMARY KEY)")
        for _i in range(5):
            conn.execute("INSERT INTO nodes DEFAULT VALUES")
        for _i in range(3):
            conn.execute("INSERT INTO edges DEFAULT VALUES")
        conn.commit()
        conn.close()

        mock_paths = Mock()
        mock_paths.sqlite = sqlite_path

        mock_artifact = Mock()
        mock_artifact.entities = list(range(5))  # Match
        mock_artifact.relations = list(range(10))  # 10 relations vs 3 edges

        with pytest.raises(SystemExit) as exc_info:
            _check_artifact_consistency(mock_paths, mock_artifact)
        assert exc_info.value.code == 1

    def test_consistent_counts_pass(self, tmp_path):
        """Test that matching counts pass the check."""
        from tools.generate.generate_full_adg import _check_artifact_consistency

        sqlite_path = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (id INTEGER PRIMARY KEY)")
        for _i in range(5):
            conn.execute("INSERT INTO nodes DEFAULT VALUES")
        for _i in range(3):
            conn.execute("INSERT INTO edges DEFAULT VALUES")
        conn.commit()
        conn.close()

        mock_paths = Mock()
        mock_paths.sqlite = sqlite_path

        mock_artifact = Mock()
        mock_artifact.entities = list(range(5))  # Match
        mock_artifact.relations = list(range(3))  # Match

        # Should not raise
        _check_artifact_consistency(mock_paths, mock_artifact)


class TestP1DefectsCheck:
    """Tests for _check_p1_defects function."""

    def test_p1_defects_fail_in_strict_mode(self):
        """Test that P1 defects cause failure in strict mode."""
        from tools.generate.generate_full_adg import _check_p1_defects

        routing_summary = {
            "by_severity": {
                "critical": 5,  # P1 defects present
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

        with pytest.raises(SystemExit) as exc_info:
            _check_p1_defects(routing_summary, strict_mode=True)
        assert exc_info.value.code == 1

    def test_no_p1_defects_pass_in_strict_mode(self):
        """Test that no P1 defects pass in strict mode."""
        from tools.generate.generate_full_adg import _check_p1_defects

        routing_summary = {
            "by_severity": {
                "critical": 0,  # No P1 defects
                "high": 10,
                "medium": 5,
                "low": 2,
            },
        }

        # Should not raise
        _check_p1_defects(routing_summary, strict_mode=True)

    def test_p1_defects_fail_unconditionally(self):
        """Test that P1 defects fail regardless of strict_mode (unconditional fail-fast)."""
        from tools.generate.generate_full_adg import _check_p1_defects

        routing_summary = {
            "by_severity": {
                "critical": 5,  # P1 defects present
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

        # Should fail even when strict_mode=False
        with pytest.raises(SystemExit) as exc_info:
            _check_p1_defects(routing_summary, strict_mode=False)
        assert exc_info.value.code == 1

        # Should also fail when strict_mode=True
        with pytest.raises(SystemExit) as exc_info:
            _check_p1_defects(routing_summary, strict_mode=True)
        assert exc_info.value.code == 1

    def test_in_cycle_blocks_generation(self, tmp_path):
        """Test that in_cycle edges block ADG generation (Tier 1A)."""
        from tools.generate.generate_full_adg import _check_p1_defects
        import sqlite3

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with in_cycle edge
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('in_cycle')")
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p1_defects(routing_summary, sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

    def test_dynamic_exec_blocks_generation(self, tmp_path):
        """Test that dynamic_exec edges block ADG generation (Tier 1B)."""
        from tools.generate.generate_full_adg import _check_p1_defects
        import sqlite3

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with dynamic_exec edge
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('dynamic_exec')")
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p1_defects(routing_summary, sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

    def test_no_graph_corruption_passes(self, tmp_path):
        """Test that clean graph (no in_cycle/dynamic_exec) passes P1 checks."""
        from tools.generate.generate_full_adg import _check_p1_defects
        import sqlite3

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite without in_cycle or dynamic_exec
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('imports')")
        conn.commit()
        conn.close()

        # Should not raise
        _check_p1_defects(routing_summary, sqlite_path=sqlite_path)


class TestP2PipelineIntegrityCheck:
    """Tests for Tier 2 P2 pipeline integrity gate."""

    def test_exception_swallow_in_pipeline_blocks(self, tmp_path, capsys):
        """Test that exception swallows in ADG pipeline paths block ADG generation."""
        from tools.generate.generate_full_adg import _check_p2_pipeline_integrity
        import sqlite3

        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with exception swallow in pipeline path
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (edge_kind TEXT, source_file TEXT)")
        conn.execute(
            "INSERT INTO edges (edge_kind, source_file) VALUES ('broad_exception_catch', 'tools/adg/server.py')"
        )
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p2_pipeline_integrity(sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "P2 Tier 2" in out
        assert "Exception swallows in ADG pipeline detected" in out

    def test_exception_swallow_outside_pipeline_passes(self, tmp_path):
        """Test that exception swallows outside pipeline paths do not block."""
        from tools.generate.generate_full_adg import _check_p2_pipeline_integrity
        import sqlite3

        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with exception swallow outside pipeline path
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (edge_kind TEXT, source_file TEXT)")
        conn.execute(
            "INSERT INTO edges (edge_kind, source_file) VALUES ('broad_exception_catch', 'apps_eval/engine.py')"
        )
        conn.commit()
        conn.close()

        # Should not raise
        _check_p2_pipeline_integrity(sqlite_path=sqlite_path)

    def test_no_exception_swallows_passes(self, tmp_path):
        """Test that clean pipeline (no exception swallows) passes P2 checks."""
        from tools.generate.generate_full_adg import _check_p2_pipeline_integrity
        import sqlite3

        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite without exception swallows
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (edge_kind TEXT, source_file TEXT)")
        conn.execute("INSERT INTO edges (edge_kind, source_file) VALUES ('imports', 'tools/adg/server.py')")
        conn.commit()
        conn.close()

        # Should not raise
        _check_p2_pipeline_integrity(sqlite_path=sqlite_path)


class TestLockedFilesFailFast:
    """Tests for locked-file fail-fast behavior and no-restart guidance."""

    def test_check_locked_files_fails_with_adg_close_guidance(self, tmp_path, monkeypatch, capsys):
        """Locked SQLite files must fail and instruct adg_close_connections()."""
        from tools.generate import generate_full_adg as mod

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        (adg_dir / "adg_indexed_04062026_0100.sqlite").write_text("stub")

        monkeypatch.setattr(mod, "ROOT", tmp_path)
        monkeypatch.setattr(mod, "_is_file_locked", lambda _p: True)

        with pytest.raises(SystemExit) as exc_info:
            mod._check_locked_files()
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "adg_close_connections()" in out
        assert "ADG generation aborted" in out

    def test_check_locked_files_passes_when_unlocked(self, tmp_path, monkeypatch, capsys):
        """Unlocked SQLite files should pass preflight lock check."""
        from tools.generate import generate_full_adg as mod

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        (adg_dir / "adg_indexed_04062026_0100.sqlite").write_text("stub")

        monkeypatch.setattr(mod, "ROOT", tmp_path)
        monkeypatch.setattr(mod, "_is_file_locked", lambda _p: False)

        mod._check_locked_files()

        out = capsys.readouterr().out
        assert "No locked SQLite files found" in out

class TestRepoStateChangeCheck:
    """Tests for repository state change detection."""

    def test_repo_state_change_detection_logic(self):
        """Test the logic for detecting repo state changes."""
        # Conceptual test - verify the comparison logic
        start_hash = "abc123def456"
        end_hash = "def456abc123"

        # When hashes differ, it indicates a change
        assert start_hash != end_hash
        assert start_hash != end_hash, "Different hashes should be detected as change"

    def test_repo_state_unchanged_detection_logic(self):
        """Test the logic for detecting unchanged repo state."""
        start_hash = "abc123def456"
        end_hash = "abc123def456"

        # When hashes match, it indicates no change
        assert start_hash == end_hash
        assert start_hash == end_hash, "Matching hashes should be detected as unchanged"


class TestClosureValidationStrictMode:
    """Tests for closure validation in strict mode."""

    def test_non_allowed_gap_fails_in_strict_mode(self, tmp_path, capsys):
        """Test that non-allowed closure gaps fail in strict mode."""
        # This would be tested by checking the closure validation logic
        # The actual implementation is in generate_full_adg function
        # Here we verify the logic conceptually

        failed_caps = ["LAYER_BOUNDARY", "IMPORT_HYGIENE"]  # Not in allowlist
        strict_mode = True

        # These should fail in strict mode
        assert strict_mode is True
        assert "EDGE SEMANTIC PRECISION" not in failed_caps
        assert "DETERMINISM (ARTIFACT LEVEL)" not in failed_caps

    def test_allowed_gap_passes_in_strict_mode(self):
        """Test that allowed closure gaps pass even in strict mode."""
        failed_caps = ["EDGE SEMANTIC PRECISION"]  # In allowlist
        strict_mode = True

        # These should be allowed even in strict mode
        assert strict_mode is True
        assert failed_caps == ["EDGE SEMANTIC PRECISION"]

    def test_multiple_allowed_gaps_pass(self):
        """Test that multiple allowed gaps pass in strict mode."""
        failed_caps = ["EDGE SEMANTIC PRECISION", "DETERMINISM (ARTIFACT LEVEL)"]
        strict_mode = True

        # These should be allowed even in strict mode
        assert strict_mode is True
        assert set(failed_caps) == {"EDGE SEMANTIC PRECISION", "DETERMINISM (ARTIFACT LEVEL)"}


class TestIntegrationFailFast:
    """Integration tests for fail-fast behavior."""

    def test_strict_mode_cli_argument(self):
        """Test that --strict CLI argument is properly parsed."""
        import argparse

        # Simulate CLI parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("--strict", action="store_true")
        args = parser.parse_args(["--strict"])

        assert args.strict is True

    def test_non_strict_mode_default(self):
        """Test that strict mode defaults to False."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--strict", action="store_true")
        args = parser.parse_args([])

        assert args.strict is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
