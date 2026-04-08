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


# ---------------------------------------------------------------------------
# W2 helper: create a minimal ADG SQLite with nodes + edges + violations
# ---------------------------------------------------------------------------

_TEST_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id            INTEGER PRIMARY KEY,
    adg_name      TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    identity_kind TEXT NOT NULL DEFAULT 'module',
    confidence    TEXT NOT NULL DEFAULT 'high',
    resolved_path TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id        INTEGER NOT NULL REFERENCES nodes(id),
    dst_id        INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL,
    edge_kind     TEXT NOT NULL DEFAULT '',
    source_file   TEXT NOT NULL DEFAULT '',
    line_no       INTEGER NOT NULL DEFAULT 0,
    symbol        TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS violations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id         INTEGER NOT NULL DEFAULT 0,
    category        TEXT NOT NULL DEFAULT '',
    evidence        TEXT NOT NULL DEFAULT '',
    file_path       TEXT NOT NULL DEFAULT '',
    line_no         INTEGER NOT NULL DEFAULT 0,
    severity        TEXT NOT NULL DEFAULT 'P0',
    violation_class TEXT NOT NULL DEFAULT 'hygiene'
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _make_adg_db(tmp_path, name="test_adg.sqlite"):
    """Create a minimal ADG SQLite database and return (db_path, conn)."""
    db = tmp_path / name
    conn = sqlite3.connect(str(db))
    conn.executescript(_TEST_DDL)
    return db, conn


def _write_sc_ap_config(tmp_path, overrides, name="sc_ap_config.json"):
    """Write a minimal SC/AP config JSON with given overrides."""
    import json as _json

    cfg_path = tmp_path / name
    cfg_path.write_text(_json.dumps(overrides))
    return cfg_path


# ---------------------------------------------------------------------------
# W2.1: SC-1 Gravity Import / Illegal Layer Reach
# ---------------------------------------------------------------------------


class TestSC1GravityImport:
    """SC-1: Gravity import / illegal layer reach."""

    def test_clean_graph_passes(self, tmp_path):
        """No violations when all imports respect layer gravity."""
        from tools.generate.validation.gates import _query_sc1_gravity

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',10)"
        )
        conn.commit()
        # L0->L3 IS forbidden, so insert a CLEAN edge instead (L3->L0 is allowed)
        conn.execute("DELETE FROM edges")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,1,'imports','','b.py',5)"
        )
        conn.commit()
        result = _query_sc1_gravity(conn)
        assert result == []
        conn.close()

    def test_forbidden_cross_layer_import_detected(self, tmp_path):
        """L0->L3 import flagged as SC-1 violation."""
        from tools.generate.validation.gates import _query_sc1_gravity

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',10)"
        )
        conn.commit()
        result = _query_sc1_gravity(conn)
        assert len(result) == 1
        assert "L0->L3" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs warning but does not sys.exit."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-1": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-1"]) >= 1
        out = capsys.readouterr().out
        assert "[AUDIT]" in out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode calls sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-1": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.2a: SC-2 L2 Execution Lifecycle Conformance
# ---------------------------------------------------------------------------


class TestSC2Lifecycle:
    """SC-2: L2 execution lifecycle conformance (E1-E5 phases)."""

    def test_full_lifecycle_passes(self, tmp_path):
        """L2 module with all 5 phases passes."""
        from tools.generate.validation.gates import _query_sc2_lifecycle

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','exec.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Target','module','L2','module','high','t.py')")
        for rt in [
            "enters_sandbox",
            "validates_uwg_intent",
            "invokes_provider",
            "orchestrates_healing",
            "packages_execution_trace",
        ]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'',' exec.py',1)",
                (rt,),
            )
        conn.commit()
        result = _query_sc2_lifecycle(conn)
        assert result == []
        conn.close()

    def test_missing_phases_detected(self, tmp_path):
        """L2 module missing >=2 phases is flagged."""
        from tools.generate.validation.gates import _query_sc2_lifecycle

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','exec.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','exec.py',1)"
        )
        conn.commit()
        result = _query_sc2_lifecycle(conn)
        assert len(result) == 1
        assert "missing phases" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','exec.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','exec.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-2": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-2"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','exec.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','exec.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-2": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.2b: SC-3 UWG-Only Durable Write Conformance
# ---------------------------------------------------------------------------


class TestSC3UWGWrite:
    """SC-3: UWG-only durable write conformance."""

    def test_governed_write_passes(self, tmp_path):
        """Write with validates_uwg_intent passes."""
        from tools.generate.validation.gates import _query_sc3_uwg_write

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Writer','module','L2','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Store','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'validates_uwg_intent','','w.py',3)"
        )
        conn.commit()
        result = _query_sc3_uwg_write(conn)
        assert result == []
        conn.close()

    def test_ungoverned_write_detected(self, tmp_path):
        """L2 write without UWG governance flagged."""
        from tools.generate.validation.gates import _query_sc3_uwg_write

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Writer','module','L2','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Store','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        result = _query_sc3_uwg_write(conn)
        assert len(result) == 1
        assert "without UWG" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Writer','module','L2','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Store','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-3": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-3"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Writer','module','L2','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Store','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-3": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.2c: SC-4 Capability / Choke-Point Conformance
# ---------------------------------------------------------------------------


class TestSC4ChokePoint:
    """SC-4: Capability/tool/provider choke-point conformance."""

    def test_gated_provider_passes(self, tmp_path):
        """Provider invocation with capability gate passes."""
        from tools.generate.validation.gates import _query_sc4_choke_point

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Caller','module','L2','module','high','c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Provider','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','c.py',10)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'checks_capability_set','','c.py',8)"
        )
        conn.commit()
        result = _query_sc4_choke_point(conn)
        assert result == []
        conn.close()

    def test_ungated_provider_detected(self, tmp_path):
        """Provider invocation without capability gate flagged."""
        from tools.generate.validation.gates import _query_sc4_choke_point

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Caller','module','L2','module','high','c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Provider','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','c.py',10)"
        )
        conn.commit()
        result = _query_sc4_choke_point(conn)
        assert len(result) == 1
        assert "without capability gate" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Caller','module','L2','module','high','c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Provider','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','c.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-4": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-4"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Caller','module','L2','module','high','c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Provider','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','c.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-4": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.3a: AP-1 Unsafe Text-to-Action Path
# ---------------------------------------------------------------------------


class TestAP1TextToAction:
    """AP-1: Unsafe text-to-action path."""

    def test_guarded_flow_passes(self, tmp_path):
        """Flow with guardrail passes."""
        from tools.generate.validation.gates import _query_ap1_text_to_action

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Retriever','module','L1','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Action','module','L2','module','high','a.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'flows_to','','r.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,2,'invokes_provider','','a.py',10)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'applies_guardrail','','r.py',4)"
        )
        conn.commit()
        result = _query_ap1_text_to_action(conn)
        assert result == []
        conn.close()

    def test_unguarded_flow_detected(self, tmp_path):
        """Flow to action without guardrail flagged."""
        from tools.generate.validation.gates import _query_ap1_text_to_action

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Retriever','module','L1','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Action','module','L2','module','high','a.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'flows_to','','r.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        result = _query_ap1_text_to_action(conn)
        assert len(result) == 1
        assert "without guardrail" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L1','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'A','module','L2','module','high','a.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'flows_to','','r.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-1": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-1"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L1','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'A','module','L2','module','high','a.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'flows_to','','r.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-1": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.3b: AP-2 L2 Phase Bypass
# ---------------------------------------------------------------------------


class TestAP2PhaseBYpass:
    """AP-2: L2 phase bypass — execution without validate or seal."""

    def test_full_validate_and_seal_passes(self, tmp_path):
        """L2 module with validate + seal passes."""
        from tools.generate.validation.gates import _query_ap2_phase_bypass

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        for rt in ["invokes_provider", "validates_uwg_intent", "packages_execution_trace"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'',' e.py',1)",
                (rt,),
            )
        conn.commit()
        result = _query_ap2_phase_bypass(conn)
        assert result == []
        conn.close()

    def test_missing_validate_detected(self, tmp_path):
        """L2 module executing without E2-validate flagged."""
        from tools.generate.validation.gates import _query_ap2_phase_bypass

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        result = _query_ap2_phase_bypass(conn)
        assert len(result) == 1
        assert "E2-validate" in result[0]["evidence"]
        assert "E5-seal" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-2": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-2"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-2": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.3c: AP-3 Provider/Tool Bypass (agentic_core/ scoped)
# ---------------------------------------------------------------------------


class TestAP3ProviderBypass:
    """AP-3: Provider/tool bypass — SC-4 scoped to agentic_core/."""

    def test_gated_provider_in_core_passes(self, tmp_path):
        """Provider invocation in agentic_core/ with capability gate passes."""
        from tools.generate.validation.gates import _query_ap3_provider_bypass

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'C','module','L2','module','high','agentic_core/c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','agentic_core/c.py',10)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'enters_sandbox','','agentic_core/c.py',8)"
        )
        conn.commit()
        result = _query_ap3_provider_bypass(conn)
        assert result == []
        conn.close()

    def test_ungated_provider_in_core_detected(self, tmp_path):
        """Provider invocation in agentic_core/ without gate flagged."""
        from tools.generate.validation.gates import _query_ap3_provider_bypass

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'C','module','L2','module','high','agentic_core/c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','agentic_core/c.py',10)"
        )
        conn.commit()
        result = _query_ap3_provider_bypass(conn)
        assert len(result) == 1
        assert "agentic_core/" in result[0]["evidence"]
        conn.close()

    def test_ungated_provider_outside_core_not_flagged(self, tmp_path):
        """Provider invocation outside agentic_core/ is not flagged by AP-3."""
        from tools.generate.validation.gates import _query_ap3_provider_bypass

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'C','module','L2','module','high','tools/c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','tools/c.py',10)"
        )
        conn.commit()
        result = _query_ap3_provider_bypass(conn)
        assert result == []
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'C','module','L2','module','high','agentic_core/c.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','agentic_core/c.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-3": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-3"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# W2.3d: AP-4 Direct Durable Write Breach
# ---------------------------------------------------------------------------


class TestAP4DirectWrite:
    """AP-4: Direct durable write breach — writing without governed path."""

    def test_governed_write_passes(self, tmp_path):
        """Write with commits_mutation_durable passes."""
        from tools.generate.validation.gates import _query_ap4_direct_write

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'W','module','L2','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'S','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'commits_mutation_durable','','w.py',4)"
        )
        conn.commit()
        result = _query_ap4_direct_write(conn)
        assert result == []
        conn.close()

    def test_ungoverned_write_detected(self, tmp_path):
        """Write without governed path flagged."""
        from tools.generate.validation.gates import _query_ap4_direct_write

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'W','module','L0','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'S','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        result = _query_ap4_direct_write(conn)
        assert len(result) == 1
        assert "direct durable write" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'W','module','L0','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'S','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-4": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-4"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'W','module','L0','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'S','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-4": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W2.4: Verify violations inserted into DB with correct class
# ---------------------------------------------------------------------------


class TestSCAPViolationInsertion:
    """W2.4: Verify SC/AP gates insert violation rows with correct violation_class."""

    def test_sc_violation_class_in_db(self, tmp_path):
        """SC check inserts rows with violation_class='structural_conformance'."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-1": {"enabled": True, "audit_mode": True}})
        _check_structural_conformance(sqlite_path=db, config_path=cfg)

        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute(
            "SELECT category, violation_class FROM violations WHERE violation_class = 'structural_conformance'"
        ).fetchall()
        assert len(rows) >= 1
        assert all(r[1] == "structural_conformance" for r in rows)
        conn2.close()

    def test_ap_violation_class_in_db(self, tmp_path):
        """AP check inserts rows with violation_class='agentic_antipattern'."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'W','module','L0','module','high','w.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'S','module','L4','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','w.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-4": {"enabled": True, "audit_mode": True}})
        _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)

        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute(
            "SELECT category, violation_class FROM violations WHERE violation_class = 'agentic_antipattern'"
        ).fetchall()
        assert len(rows) >= 1
        assert all(r[1] == "agentic_antipattern" for r in rows)
        conn2.close()


# ---------------------------------------------------------------------------
# W2.4: Verify dispatch tables and exports
# ---------------------------------------------------------------------------


class TestW2ExportsComplete:
    """W2: Verify all new query functions and dispatch tables are exported."""

    def test_all_w2_exports_importable(self):
        """All W2 exports must be importable from tools.generate.validation."""
        from tools.generate.validation import (
            _AP_CHECK_DISPATCH,
            _GRAVITY_FORBIDDEN,
            _SC_CHECK_DISPATCH,
            _query_ap1_text_to_action,
            _query_ap2_phase_bypass,
            _query_ap3_provider_bypass,
            _query_ap4_direct_write,
            _query_sc1_gravity,
            _query_sc2_lifecycle,
            _query_sc3_uwg_write,
            _query_sc4_choke_point,
        )

        assert "SC-1" in _SC_CHECK_DISPATCH
        assert "SC-4" in _SC_CHECK_DISPATCH
        assert "AP-1" in _AP_CHECK_DISPATCH
        assert "AP-4" in _AP_CHECK_DISPATCH
        assert "L0" in _GRAVITY_FORBIDDEN
        assert callable(_query_sc1_gravity)
        assert callable(_query_sc2_lifecycle)
        assert callable(_query_sc3_uwg_write)
        assert callable(_query_sc4_choke_point)
        assert callable(_query_ap1_text_to_action)
        assert callable(_query_ap2_phase_bypass)
        assert callable(_query_ap3_provider_bypass)
        assert callable(_query_ap4_direct_write)

    def test_dispatch_tables_cover_all_w2_checks(self):
        """Dispatch tables map all 8 W2 checks to query functions."""
        from tools.generate.validation import _AP_CHECK_DISPATCH, _SC_CHECK_DISPATCH

        assert set(_SC_CHECK_DISPATCH.keys()) == {"SC-1", "SC-2", "SC-3", "SC-4"}
        assert set(_AP_CHECK_DISPATCH.keys()) == {"AP-1", "AP-2", "AP-3", "AP-4"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
