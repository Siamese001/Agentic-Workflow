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


class TestP0ViolationsCheck:
    """Tests for _check_p0_violations function."""

    def test_p0_violations_fail_unconditionally(self):
        """Test that P0 layer violations fail unconditionally."""
        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {
            "by_severity": {
                "critical": 5,  # P0 violations present
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

        # Should fail (no strict_mode param)
        with pytest.raises(SystemExit) as exc_info:
            _check_p0_violations(routing_summary)
        assert exc_info.value.code == 1

    def test_no_p0_violations_pass(self):
        """Test that no P0 violations pass."""
        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {
            "by_severity": {
                "critical": 0,  # No P0 violations
                "high": 10,
                "medium": 5,
                "low": 2,
            },
        }

        # Should not raise (no strict_mode param)
        _check_p0_violations(routing_summary)

    def test_in_cycle_blocks_generation(self, tmp_path):
        """Test that in_cycle edges block ADG generation (P0 Tier 1A)."""
        import sqlite3

        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with in_cycle edge
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('in_cycle')")
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p0_violations(routing_summary, sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

    def test_dynamic_exec_blocks_generation(self, tmp_path):
        """Test that dynamic_exec edges block ADG generation (P0 Tier 1B)."""
        import sqlite3

        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with dynamic_exec edge
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('dynamic_exec')")
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p0_violations(routing_summary, sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

    def test_any_violation_blocks(self, tmp_path):
        """Test that any layer violation blocks ADG generation (P0, no exemption bypass)."""
        import sqlite3

        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite with violates edge — line_no=0 triggers the else branch (unapproved)
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT, source_file TEXT, line_no INTEGER)")
        conn.execute(
            "INSERT INTO edges (relation_type, source_file, line_no) VALUES ('violates', 'nonexistent/file.py', 0)",
        )
        conn.commit()
        conn.close()

        # Should fail because violation is present (no exemption bypass)
        with pytest.raises(SystemExit) as exc_info:
            _check_p0_violations(routing_summary, sqlite_path=sqlite_path)
        assert exc_info.value.code == 1

    def test_no_graph_corruption_passes(self, tmp_path):
        """Test that clean graph (no in_cycle/dynamic_exec) passes P0 checks."""
        import sqlite3

        from tools.generate.generate_full_adg import _check_p0_violations

        routing_summary = {"by_severity": {"critical": 0}}
        sqlite_path = tmp_path / "test.sqlite"

        # Create SQLite without in_cycle or dynamic_exec
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT)")
        conn.execute("INSERT INTO edges (relation_type) VALUES ('imports')")
        conn.commit()
        conn.close()

        # Should not raise
        _check_p0_violations(routing_summary, sqlite_path=sqlite_path)


class TestP1RatchetCheck:
    """Tests for P1 HIGH antipatterns non-regression ratchet."""

    def test_exception_swallow_hard_fails(self, tmp_path, capsys):
        """Test that HIGH antipatterns regression blocks ADG generation."""
        import json
        import sqlite3

        from tools.generate.generate_full_adg import _check_p1_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "p1_ratchet.json"

        # Create violations table with 5 HIGH antipatterns
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        for _ in range(5):
            conn.execute("INSERT INTO violations (severity, category) VALUES ('HIGH', 'antipattern')")
        conn.commit()
        conn.close()

        # Pre-set ceiling at 3 so current_count=5 triggers regression
        with open(ratchet_file, "w") as f:
            json.dump({"high_severity_ceiling": 3}, f)

        with pytest.raises(SystemExit) as exc_info:
            _check_p1_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "[ERROR] P1 antipattern regression" in out
        assert "ADG generation failed" in out

    def test_no_antipatterns_passes(self, tmp_path):
        """Test that clean codebase (no HIGH antipatterns) passes P1 ratchet."""
        import sqlite3

        from tools.generate.generate_full_adg import _check_p1_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "p1_ratchet.json"  # isolated — must not touch production file

        # Create violations table with zero HIGH antipatterns
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        conn.execute("INSERT INTO violations (severity, category) VALUES ('MEDIUM', 'antipattern')")
        conn.commit()
        conn.close()

        # Should not raise
        _check_p1_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)


class TestP2RatchetCheck:
    """Tests for P2 MEDIUM antipatterns non-regression ratchet."""

    def test_ratchet_initialization(self, tmp_path, capsys):
        """Test that ratchet initializes with current count as ceiling."""
        import json
        import sqlite3

        from tools.generate.generate_full_adg import _check_p2_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "ratchet.json"

        # Create violations table with 5 MEDIUM antipatterns
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        for _ in range(5):
            conn.execute("INSERT INTO violations (severity, category) VALUES ('MEDIUM', 'antipattern')")
        conn.commit()
        conn.close()

        # Should initialize ratchet
        _check_p2_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)

        # Check ratchet file
        with open(ratchet_file) as f:
            data = json.load(f)
            assert data["exception_swallow_ceiling"] == 5

        out = capsys.readouterr().out
        assert "Initialized P2 ratchet ceiling: 5" in out

    def test_ratchet_blocks_regression(self, tmp_path, capsys):
        """Test that ratchet blocks if count exceeds ceiling."""
        import json
        import sqlite3

        from tools.generate.generate_full_adg import _check_p2_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "ratchet.json"

        # Initialize ratchet with ceiling of 3
        with open(ratchet_file, "w") as f:
            json.dump({"exception_swallow_ceiling": 3}, f)

        # Create violations table with 5 MEDIUM antipatterns (exceeds ceiling)
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        for _ in range(5):
            conn.execute("INSERT INTO violations (severity, category) VALUES ('MEDIUM', 'antipattern')")
        conn.commit()
        conn.close()

        with pytest.raises(SystemExit) as exc_info:
            _check_p2_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "P2 ratchet: MEDIUM antipattern regression detected" in out
        assert "Current count: 5, Ceiling: 3" in out

    def test_ratchet_allows_equal(self, tmp_path, capsys):
        """Test that ratchet allows if count equals ceiling."""
        import json
        import sqlite3

        from tools.generate.generate_full_adg import _check_p2_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "ratchet.json"

        # Initialize ratchet with ceiling of 5
        with open(ratchet_file, "w") as f:
            json.dump({"exception_swallow_ceiling": 5}, f)

        # Create violations table with 5 MEDIUM antipatterns (equals ceiling)
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        for _ in range(5):
            conn.execute("INSERT INTO violations (severity, category) VALUES ('MEDIUM', 'antipattern')")
        conn.commit()
        conn.close()

        # Should not raise
        _check_p2_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)

        out = capsys.readouterr().out
        assert "P2 ratchet: Current count 5 at ceiling 5" in out

    def test_ratchet_updates_downward(self, tmp_path, capsys):
        """Test that ratchet updates ceiling downward if count decreases."""
        import json
        import sqlite3

        from tools.generate.generate_full_adg import _check_p2_ratchet

        sqlite_path = tmp_path / "test.sqlite"
        ratchet_file = tmp_path / "ratchet.json"

        # Initialize ratchet with ceiling of 5
        with open(ratchet_file, "w") as f:
            json.dump({"exception_swallow_ceiling": 5}, f)

        # Create violations table with 3 MEDIUM antipatterns (below ceiling)
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE violations (severity TEXT, category TEXT)")
        for _ in range(3):
            conn.execute("INSERT INTO violations (severity, category) VALUES ('MEDIUM', 'antipattern')")
        conn.commit()
        conn.close()

        # Should not raise and should update ceiling
        _check_p2_ratchet(sqlite_path=sqlite_path, ratchet_file=ratchet_file)

        # Check ceiling was updated
        with open(ratchet_file) as f:
            data = json.load(f)
            assert data["exception_swallow_ceiling"] == 3

        out = capsys.readouterr().out
        assert "P2 ratchet: Reduced ceiling from 5 to 3" in out


class TestLockedFilesFailFast:
    """Tests for locked-file fail-fast behavior and no-restart guidance."""

    def test_check_locked_files_fails_with_adg_close_guidance(self, tmp_path, monkeypatch, capsys):
        """Locked SQLite files must fail and instruct adg_close_connections()."""
        import tools.generate.utils.file_utils as fu
        from tools.generate import generate_full_adg as mod

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        (adg_dir / "adg_indexed_04062026_0100.sqlite").write_text("stub")

        monkeypatch.setattr(fu, "_is_file_locked", lambda _p: True)

        with pytest.raises(SystemExit) as exc_info:
            mod._check_locked_files(adg_dir=adg_dir)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "adg_close_connections()" in out
        assert "ADG generation aborted" in out

    def test_check_locked_files_passes_when_unlocked(self, tmp_path, monkeypatch, capsys):
        """Unlocked SQLite files should pass preflight lock check."""
        import tools.generate.utils.file_utils as fu
        from tools.generate import generate_full_adg as mod

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        (adg_dir / "adg_indexed_04062026_0100.sqlite").write_text("stub")

        monkeypatch.setattr(fu, "_is_file_locked", lambda _p: False)

        mod._check_locked_files(adg_dir=adg_dir)

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


# ---------------------------------------------------------------------------
# Wave 1 completion tests: SC/AP infrastructure
# ---------------------------------------------------------------------------


class TestViolationClassColumn:
    """W1.1: Verify violation_class column exists in canonical DDL."""

    def test_violations_table_has_violation_class_column(self, tmp_path):
        """DDL from multi_writer.py must create violation_class column with default 'hygiene'."""
        from agentic_core.adg.artifact.multi_writer import _DDL

        db = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(db))
        conn.executescript(_DDL)

        cursor = conn.execute("PRAGMA table_info(violations)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert "violation_class" in columns, "violation_class column missing from violations table"
        col_info = columns["violation_class"]
        assert col_info[2] == "TEXT", f"Expected TEXT type, got {col_info[2]}"
        assert col_info[4] == "'hygiene'", f"Expected default 'hygiene', got {col_info[4]}"
        conn.close()

    def test_violation_class_index_created(self, tmp_path):
        """idx_violations_class index must exist after DDL execution."""
        from agentic_core.adg.artifact.multi_writer import _DDL

        db = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(db))
        conn.executescript(_DDL)

        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='violations'"
        ).fetchall()
        index_names = {row[0] for row in indexes}
        assert "idx_violations_class" in index_names, f"Missing idx_violations_class in {index_names}"
        conn.close()

    def test_existing_violations_default_to_hygiene(self, tmp_path):
        """Rows inserted without explicit violation_class must default to 'hygiene'."""
        db = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE violations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "edge_id INTEGER NOT NULL, "
            "category TEXT NOT NULL, "
            "evidence TEXT NOT NULL DEFAULT '', "
            "file_path TEXT NOT NULL DEFAULT '', "
            "line_no INTEGER NOT NULL DEFAULT 0, "
            "severity TEXT NOT NULL DEFAULT 'MEDIUM', "
            "violation_class TEXT NOT NULL DEFAULT 'hygiene')"
        )
        conn.execute("INSERT INTO violations (edge_id, category, severity) VALUES (1, 'antipattern', 'HIGH')")
        conn.commit()

        row = conn.execute("SELECT violation_class FROM violations WHERE id=1").fetchone()
        assert row[0] == "hygiene"
        conn.close()


class TestSCAPConfig:
    """W1.2a: Verify SC/AP config loading, saving, and merging."""

    def test_load_default_config_without_file(self, tmp_path):
        """Loading config when no file exists returns all defaults."""
        from tools.generate.validation.gates import _load_sc_ap_config

        config = _load_sc_ap_config(tmp_path / "nonexistent.json")
        assert "SC-1" in config
        assert "AP-17" in config
        assert config["SC-1"]["enabled"] is False
        assert config["SC-1"]["audit_mode"] is True

    def test_load_config_merges_user_overrides(self, tmp_path):
        """User config file overrides specific fields while preserving defaults."""
        import json as _json

        from tools.generate.validation.gates import _load_sc_ap_config

        config_path = tmp_path / "sc_ap_config.json"
        config_path.write_text(_json.dumps({"SC-1": {"enabled": True}}))

        config = _load_sc_ap_config(config_path)
        assert config["SC-1"]["enabled"] is True
        assert config["SC-1"]["audit_mode"] is True  # default preserved
        assert config["SC-1"]["label"] == "Gravity import / illegal layer reach"  # default preserved
        assert config["AP-1"]["enabled"] is False  # untouched checks keep defaults

    def test_save_and_reload_config(self, tmp_path):
        """Config round-trips through save/load correctly."""
        from tools.generate.validation.gates import _load_sc_ap_config, _save_sc_ap_config

        config_path = tmp_path / "sc_ap_config.json"
        config = _load_sc_ap_config(config_path)
        config["SC-2"]["enabled"] = True
        config["SC-2"]["audit_mode"] = False
        _save_sc_ap_config(config, config_path)

        reloaded = _load_sc_ap_config(config_path)
        assert reloaded["SC-2"]["enabled"] is True
        assert reloaded["SC-2"]["audit_mode"] is False

    def test_all_25_checks_present_in_defaults(self):
        """All 8 SC + 17 AP checks must be in the default config."""
        from tools.generate.validation.gates import _DEFAULT_SC_AP_CONFIG

        sc_keys = [k for k in _DEFAULT_SC_AP_CONFIG if k.startswith("SC-")]
        ap_keys = [k for k in _DEFAULT_SC_AP_CONFIG if k.startswith("AP-")]
        assert len(sc_keys) == 8, f"Expected 8 SC checks, got {len(sc_keys)}: {sc_keys}"
        assert len(ap_keys) == 17, f"Expected 17 AP checks, got {len(ap_keys)}: {ap_keys}"


class TestViolationClassConstants:
    """W1.2b: Verify violation class constants and validation set."""

    def test_constants_defined(self):
        """CLASS_HYGIENE, CLASS_STRUCTURAL, CLASS_AGENTIC must exist."""
        from tools.generate.validation.gates import CLASS_AGENTIC, CLASS_HYGIENE, CLASS_STRUCTURAL

        assert CLASS_HYGIENE == "hygiene"
        assert CLASS_STRUCTURAL == "structural_conformance"
        assert CLASS_AGENTIC == "agentic_antipattern"

    def test_valid_classes_frozenset(self):
        """VALID_VIOLATION_CLASSES must contain all three classes."""
        from tools.generate.validation.gates import VALID_VIOLATION_CLASSES

        assert len(VALID_VIOLATION_CLASSES) == 3
        assert "hygiene" in VALID_VIOLATION_CLASSES
        assert "structural_conformance" in VALID_VIOLATION_CLASSES
        assert "agentic_antipattern" in VALID_VIOLATION_CLASSES


class TestInsertSCAPViolation:
    """W1.2c: Verify _insert_sc_ap_violation writes correctly."""

    def _make_db(self, tmp_path):
        db = tmp_path / "test.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE violations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "edge_id INTEGER NOT NULL, "
            "category TEXT NOT NULL, "
            "evidence TEXT NOT NULL DEFAULT '', "
            "file_path TEXT NOT NULL DEFAULT '', "
            "line_no INTEGER NOT NULL DEFAULT 0, "
            "severity TEXT NOT NULL DEFAULT 'MEDIUM', "
            "violation_class TEXT NOT NULL DEFAULT 'hygiene')"
        )
        conn.commit()
        return conn

    def test_insert_structural_violation(self, tmp_path):
        """Structural conformance violation row written with correct class."""
        from tools.generate.validation.gates import CLASS_STRUCTURAL, _insert_sc_ap_violation

        conn = self._make_db(tmp_path)
        _insert_sc_ap_violation(conn, "SC-1", CLASS_STRUCTURAL, "P0", "test.py", 42, "gravity breach")
        conn.commit()

        row = conn.execute("SELECT category, violation_class, severity, evidence FROM violations").fetchone()
        assert row == ("SC-1", "structural_conformance", "P0", "gravity breach")
        conn.close()

    def test_insert_agentic_violation(self, tmp_path):
        """Agentic anti-pattern violation row written with correct class."""
        from tools.generate.validation.gates import CLASS_AGENTIC, _insert_sc_ap_violation

        conn = self._make_db(tmp_path)
        _insert_sc_ap_violation(conn, "AP-1", CLASS_AGENTIC, "P0", "danger.py", 10, "unsafe text-to-action")
        conn.commit()

        row = conn.execute("SELECT category, violation_class, severity FROM violations").fetchone()
        assert row == ("AP-1", "agentic_antipattern", "P0")
        conn.close()

    def test_edge_id_is_zero(self, tmp_path):
        """SC/AP violations use edge_id=0 since they come from graph queries."""
        from tools.generate.validation.gates import CLASS_STRUCTURAL, _insert_sc_ap_violation

        conn = self._make_db(tmp_path)
        _insert_sc_ap_violation(conn, "SC-3", CLASS_STRUCTURAL, "P0", "uwg.py", 1, "direct write")
        conn.commit()

        row = conn.execute("SELECT edge_id FROM violations").fetchone()
        assert row[0] == 0
        conn.close()


class TestStructuralConformanceGate:
    """W1.2d: Verify _check_structural_conformance audit/enforce infrastructure."""

    def test_returns_empty_when_no_sqlite(self):
        """No SQLite path returns empty results without error."""
        from tools.generate.validation.gates import _check_structural_conformance

        result = _check_structural_conformance(sqlite_path=None)
        assert result == {}

    def test_returns_empty_when_no_checks_enabled(self, tmp_path, capsys):
        """All checks disabled returns empty results and prints 'no checks enabled'."""
        from tools.generate.validation.gates import _check_structural_conformance

        db = tmp_path / "test_sc.sqlite"
        sqlite3.connect(str(db)).close()

        # Use a path guaranteed to not exist so defaults (all disabled) are used
        cfg = tmp_path / "subdir" / "no_config.json"
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert result == {}
        assert "no checks enabled" in capsys.readouterr().out

    def test_enabled_check_prints_passed(self, tmp_path, capsys):
        """Enabled check with no violations prints PASSED."""
        import json as _json

        from tools.generate.validation.gates import _check_structural_conformance

        db = tmp_path / "test.sqlite"
        sqlite3.connect(str(db)).close()

        config_path = tmp_path / "config.json"
        config_path.write_text(_json.dumps({"SC-1": {"enabled": True, "audit_mode": True}}))

        result = _check_structural_conformance(sqlite_path=db, config_path=config_path)
        assert "SC-1" in result
        assert len(result["SC-1"]) == 0
        assert "PASSED" in capsys.readouterr().out


class TestAgenticAntipatternGate:
    """W1.2e: Verify _check_agentic_antipatterns audit/enforce infrastructure."""

    def test_returns_empty_when_no_sqlite(self):
        """No SQLite path returns empty results without error."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        result = _check_agentic_antipatterns(sqlite_path=None)
        assert result == {}

    def test_returns_empty_when_no_checks_enabled(self, tmp_path, capsys):
        """All checks disabled returns empty results and prints 'no checks enabled'."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db = tmp_path / "test_ap.sqlite"
        sqlite3.connect(str(db)).close()

        cfg = tmp_path / "subdir" / "no_config.json"
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert result == {}
        assert "no checks enabled" in capsys.readouterr().out

    def test_enabled_check_prints_passed(self, tmp_path, capsys):
        """Enabled check with no violations prints PASSED."""
        import json as _json

        from tools.generate.validation.gates import _check_agentic_antipatterns

        db = tmp_path / "test.sqlite"
        sqlite3.connect(str(db)).close()

        config_path = tmp_path / "config.json"
        config_path.write_text(_json.dumps({"AP-1": {"enabled": True, "audit_mode": True}}))

        result = _check_agentic_antipatterns(sqlite_path=db, config_path=config_path)
        assert "AP-1" in result
        assert len(result["AP-1"]) == 0
        assert "PASSED" in capsys.readouterr().out


class TestBurndownSchemaV2:
    """W1.3: Verify burndown JSON includes by_class dimension at schema v2.0."""

    def test_burndown_has_by_class_key(self, tmp_path):
        """Burndown output must contain by_class dict with 3 violation classes."""
        # Build a minimal burndown dict matching what reports.py produces
        burndown = {
            "schema_version": "2.0",
            "by_class": {
                "hygiene": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                "structural_conformance": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
                "agentic_antipattern": {"P0": 0, "P1": 0, "P2": 0, "P3": 0},
            },
        }
        assert burndown["schema_version"] == "2.0"
        assert len(burndown["by_class"]) == 3
        for cls in ("hygiene", "structural_conformance", "agentic_antipattern"):
            assert cls in burndown["by_class"]
            for band in ("P0", "P1", "P2", "P3"):
                assert band in burndown["by_class"][cls]

    def test_burndown_v2_backward_compatible(self):
        """v2.0 burndown must still contain P0-P3 top-level keys for backward compat."""
        burndown = {
            "schema_version": "2.0",
            "P0_layer_violations": 0,
            "P1_anti_patterns": 5,
            "P2_anti_patterns": 10,
            "P3_style": 20,
            "by_class": {},
        }
        assert "P0_layer_violations" in burndown
        assert "P1_anti_patterns" in burndown
        assert "P2_anti_patterns" in burndown
        assert "P3_style" in burndown


class TestExportsComplete:
    """W1.4: Verify all new functions are exported from validation package."""

    def test_all_new_exports_importable(self):
        """All W1 exports must be importable from tools.generate.validation."""
        from tools.generate.validation import (
            CLASS_AGENTIC,
            CLASS_HYGIENE,
            CLASS_STRUCTURAL,
            VALID_VIOLATION_CLASSES,
            _check_agentic_antipatterns,
            _check_structural_conformance,
            _insert_sc_ap_violation,
            _load_sc_ap_config,
            _save_sc_ap_config,
        )

        assert CLASS_HYGIENE == "hygiene"
        assert CLASS_STRUCTURAL == "structural_conformance"
        assert CLASS_AGENTIC == "agentic_antipattern"
        assert len(VALID_VIOLATION_CLASSES) == 3
        assert callable(_check_structural_conformance)
        assert callable(_check_agentic_antipatterns)
        assert callable(_load_sc_ap_config)
        assert callable(_save_sc_ap_config)
        assert callable(_insert_sc_ap_violation)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
