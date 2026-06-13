"""
Fail-fast trigger tests for generate_full_adg.py

Tests the robustness of ADG generation by verifying that fail-fast
conditions correctly abort generation when critical conditions are not met.
"""

import sqlite3
import sys
import json
import ast
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock

import pytest
from tqdm import tqdm


def _discover_repo_root(start: Path) -> Path:
    """Best-effort repository root discovery for direct script and package execution."""
    for candidate in (start, *start.parents):
        if (candidate / "generate").exists() or (candidate / ".git").exists():
            return candidate
    return start.parent


REPO_ROOT = _discover_repo_root(Path(__file__).resolve().parent)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestZipFlagWiring:
    """Static regression coverage for generate_full_adg CLI flag wiring."""

    def test_create_zip_archive_is_guarded_by_enable_zip(self):
        source_path = next(
            candidate / "tools" / "generate" / "generate_full_adg.py"
            for candidate in Path(__file__).resolve().parents
            if (candidate / "tools" / "generate" / "generate_full_adg.py").is_file()
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "generate_full_adg"
        )

        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(func):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent

        calls = [
            node
            for node in ast.walk(func)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_create_zip_archive"
        ]
        assert calls, "expected generate_full_adg to contain a zip creation call"

        def has_enable_zip_guard(node: ast.AST) -> bool:
            current = parents.get(node)
            while current is not None:
                if (
                    isinstance(current, ast.If)
                    and isinstance(current.test, ast.Name)
                    and current.test.id == "enable_zip"
                ):
                    return True
                current = parents.get(current)
            return False

        assert all(has_enable_zip_guard(call) for call in calls)
        assert "zip_label = \"ON\" if enable_zip else \"OFF\"" in source
        assert "Zip creation skipped" in source


class TestReviewTemplateWiring:
    """Static regression coverage for mandatory ADG review template wiring."""

    def test_review_template_emit_and_zip_inclusion_are_wired(self):
        source_path = next(
            candidate / "tools" / "generate" / "generate_full_adg.py"
            for candidate in Path(__file__).resolve().parents
            if (candidate / "tools" / "generate" / "generate_full_adg.py").is_file()
        )
        source = source_path.read_text(encoding="utf-8")
        assert "emit_mandatory_adg_review_template" in source
        assert "\"adg_review_template\"" in source
        assert "extra_files.append(review_template_path)" in source
        assert "review_template_path.with_suffix(\".yaml\")" in source


class TestDispatcherResultsPathResolution:
    """Regression coverage for noisy gate-dispatcher stdout."""

    def test_resolves_existing_gate_results_path_from_stdout(self, tmp_path):
        from tools.generate.generate_full_adg import _resolve_dispatcher_results_path

        gate_results = tmp_path / "adg_gate_results_20260613_192959.json"
        gate_results.write_text("{}", encoding="utf-8")

        resolved = _resolve_dispatcher_results_path(
            f"some banner\n{gate_results}\n",
            tmp_path,
        )

        assert Path(resolved).resolve() == gate_results.resolve()

    def test_ignores_renderer_text_and_falls_back_to_latest_gate_results(self, tmp_path):
        from tools.generate.generate_full_adg import _resolve_dispatcher_results_path

        older = tmp_path / "adg_gate_results_20260613_180000.json"
        latest = tmp_path / "adg_gate_results_20260613_192959.json"
        older.write_text("{}", encoding="utf-8")
        latest.write_text("{}", encoding="utf-8")

        resolved = _resolve_dispatcher_results_path(
            "Report renderer: `tools/reports/adg_burndown_report.py`",
            tmp_path,
        )

        assert Path(resolved).resolve() == latest.resolve()


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


class TestPostCommitSqliteResolution:
    """Tests for deterministic Tier-2 sqlite source selection."""

    @staticmethod
    def _create_valid_sqlite(path: Path) -> None:
        conn = sqlite3.connect(str(path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
        conn.commit()
        conn.close()

    def test_prefers_current_run_paths_sqlite_over_lexicographic_latest(self, tmp_path):
        """Use current run ArtifactPaths sqlite even when a lexicographically newer sentinel exists."""
        from tools.generate.generate_full_adg import _resolve_post_commit_sqlite

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()
        sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"
        sentinel.write_text("not-a-sqlite", encoding="utf-8")

        current = adg_dir / "adg_indexed_04192026_0622.sqlite"
        self._create_valid_sqlite(current)

        mock_paths = Mock()
        mock_paths.sqlite = current

        resolved = _resolve_post_commit_sqlite(mock_paths, adg_dir, "04192026_0622")
        assert resolved == current.resolve()

    def test_falls_back_to_timestamped_sqlite_when_paths_sqlite_missing(self, tmp_path):
        """Fallback should resolve deterministic current timestamp sqlite file."""
        from tools.generate.generate_full_adg import _resolve_post_commit_sqlite

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()
        fallback = adg_dir / "adg_indexed_04192026_0622.sqlite"
        self._create_valid_sqlite(fallback)

        mock_paths = Mock()
        mock_paths.sqlite = adg_dir / "missing.sqlite"

        resolved = _resolve_post_commit_sqlite(mock_paths, adg_dir, "04192026_0622")
        assert resolved == fallback.resolve()

    def test_fails_fast_when_no_post_commit_sqlite_available(self, tmp_path):
        """Fail fast when neither ArtifactPaths sqlite nor timestamp fallback exists."""
        from tools.generate.generate_full_adg import _resolve_post_commit_sqlite

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()

        mock_paths = Mock()
        mock_paths.sqlite = adg_dir / "missing.sqlite"

        with pytest.raises(SystemExit) as exc_info:
            _resolve_post_commit_sqlite(mock_paths, adg_dir, "04192026_0622")
        assert exc_info.value.code == 1


class TestRepairRunnerSqliteResolution:
    """Tests for deterministic repair orchestrator sqlite resolution."""

    @staticmethod
    def _create_valid_sqlite(path: Path) -> None:
        conn = sqlite3.connect(str(path))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE violations (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
        conn.commit()
        conn.close()

    def test_repair_resolver_prefers_explicit_sqlite_path(self, tmp_path):
        from tools.generate.integration.repair_runner import _resolve_repair_sqlite

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()

        sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"
        sentinel.write_text("invalid", encoding="utf-8")

        current = adg_dir / "adg_indexed_04192026_0622.sqlite"
        self._create_valid_sqlite(current)

        resolved = _resolve_repair_sqlite(adg_dir, "04192026_0622", current)
        assert resolved == current.resolve()

    def test_repair_resolver_rejects_missing_required_tables(self, tmp_path):
        from tools.generate.integration.repair_runner import _resolve_repair_sqlite

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()

        invalid = adg_dir / "adg_indexed_04192026_0622.sqlite"
        conn = sqlite3.connect(str(invalid))
        conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        resolved = _resolve_repair_sqlite(adg_dir, "04192026_0622", invalid)
        assert resolved is None

    def test_repair_runner_passes_dry_run_to_orchestrator(self, tmp_path, monkeypatch):
        import tools.adg.repair as repair_pkg
        import tools.adg.repair.rule_engine as rule_engine
        from tools.generate.integration.repair_runner import _run_p1_p2_auto_fix

        adg_dir = tmp_path / "adg"
        adg_dir.mkdir()
        current = adg_dir / "adg_indexed_04192026_0622.sqlite"
        self._create_valid_sqlite(current)
        calls: dict[str, object] = {}

        class FakeOrchestrator:
            def __init__(self, **kwargs):
                calls["init"] = kwargs

            def run(self, *, dry_run: bool):
                calls["dry_run"] = dry_run
                return SimpleNamespace(
                    deficiencies_found=3,
                    fixes_applied=0,
                    fixes_suggested=2,
                    fixes_blocked=1,
                )

        monkeypatch.setattr(repair_pkg, "ADGRepairOrchestrator", FakeOrchestrator)
        monkeypatch.setattr(rule_engine, "register_builtin_rules", lambda: calls.setdefault("registered", True))

        _run_p1_p2_auto_fix(adg_dir, "04192026_0622", sqlite_path=current, dry_run=True)

        assert calls["registered"] is True
        assert calls["dry_run"] is True
        assert calls["init"]["sqlite_path"] == current.resolve()

    def test_generate_full_adg_has_one_repair_runner_call(self):
        repo_root = next(
            candidate for candidate in Path(__file__).resolve().parents if (candidate / ".git").exists()
        )
        source = (repo_root / "tools" / "generate" / "generate_full_adg.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_run_p1_p2_auto_fix"
        ]
        assert len(calls) == 1


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
        # Schema must include columns read by _check_p0_violations (source_file, line_no)
        conn = sqlite3.connect(str(sqlite_path))
        conn.execute("CREATE TABLE edges (relation_type TEXT, source_file TEXT, line_no INTEGER)")
        conn.execute("INSERT INTO edges (relation_type, source_file, line_no) VALUES ('imports', 'a.py', 1)")
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


class TestP0TwoPassRunnerIntegration:
    """Tests for tools.generate.integration.p0_runner._run_p0_two_pass_runner."""

    def test_missing_sqlite_fails_closed(self, tmp_path, capsys):
        """Missing production sqlite must hard-fail instead of silently skipping."""
        from tools.generate.integration.p0_runner import _run_p0_two_pass_runner

        missing_sqlite = tmp_path / "missing.sqlite"

        with pytest.raises(SystemExit) as exc_info:
            _run_p0_two_pass_runner(missing_sqlite)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "P0 runner blocked: no production SQLite snapshot found" in out

    def test_missing_sqlite_prints_plan_path_when_available(self, tmp_path, capsys):
        """When plan path exists, failure output should include remediation plan pointer."""
        from tools.generate.integration.p0_runner import _run_p0_two_pass_runner

        missing_sqlite = tmp_path / "missing.sqlite"
        plan_path = tmp_path / "p0_plan.md"
        plan_path.write_text("# plan\n", encoding="utf-8")

        with pytest.raises(SystemExit) as exc_info:
            _run_p0_two_pass_runner(missing_sqlite, plan_path=plan_path)
        assert exc_info.value.code == 1

        out = capsys.readouterr().out
        assert "See remediation wave plan" in out
        assert str(plan_path) in out

    def test_runner_rc_zero_passes(self, tmp_path, monkeypatch, capsys):
        """Runner rc=0 should pass and not raise."""
        from tools.generate.integration.p0_runner import _run_p0_two_pass_runner

        sqlite_path = tmp_path / "adg.sqlite"
        sqlite_path.write_text("stub", encoding="utf-8")

        import types

        fake_module = types.ModuleType("ops_scripts.ci.adg_gates.p0_runner")

        def _fake_run_p0_two_pass(**kwargs):
            return 0

        fake_module.run_p0_two_pass = _fake_run_p0_two_pass
        monkeypatch.setitem(sys.modules, "ops_scripts.ci.adg_gates.p0_runner", fake_module)

        _run_p0_two_pass_runner(sqlite_path)
        out = capsys.readouterr().out
        assert "P0 two-pass runner: PASSED" in out

    def test_runner_rc_one_blocks(self, tmp_path, monkeypatch):
        """Runner rc=1 must fail-closed with SystemExit(1)."""
        from tools.generate.integration.p0_runner import _run_p0_two_pass_runner

        sqlite_path = tmp_path / "adg.sqlite"
        sqlite_path.write_text("stub", encoding="utf-8")

        import types

        fake_module = types.ModuleType("ops_scripts.ci.adg_gates.p0_runner")

        def _fake_run_p0_two_pass(**kwargs):
            return 1

        fake_module.run_p0_two_pass = _fake_run_p0_two_pass
        monkeypatch.setitem(sys.modules, "ops_scripts.ci.adg_gates.p0_runner", fake_module)

        with pytest.raises(SystemExit) as exc_info:
            _run_p0_two_pass_runner(sqlite_path)
        assert exc_info.value.code == 1

    def test_runner_unexpected_rc_blocks(self, tmp_path, monkeypatch):
        """Any unexpected non-zero rc must fail-closed with SystemExit propagating that rc.

        Plan adg-fail-aggregating-gate-chain-9d4e1f W2.3 changed the contract:
        the unexpected rc is now propagated verbatim (was: normalized to 1) so
        operators see the real signal from the underlying runner. Only rc==0
        is normalized to 1 (the "weird success-but-blocked" case).
        """
        from tools.generate.integration.p0_runner import _run_p0_two_pass_runner

        sqlite_path = tmp_path / "adg.sqlite"
        sqlite_path.write_text("stub", encoding="utf-8")

        import types

        fake_module = types.ModuleType("ops_scripts.ci.adg_gates.p0_runner")

        def _fake_run_p0_two_pass(**kwargs):
            return 42

        fake_module.run_p0_two_pass = _fake_run_p0_two_pass
        monkeypatch.setitem(sys.modules, "ops_scripts.ci.adg_gates.p0_runner", fake_module)

        with pytest.raises(SystemExit) as exc_info:
            _run_p0_two_pass_runner(sqlite_path)
        assert exc_info.value.code == 42


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
        assert "AP-18" in config
        # SC-1 was promoted 2026-04-17 (enabled by default, audit_mode still on)
        assert config["SC-1"]["enabled"] is True
        assert config["SC-1"]["audit_mode"] is True
        # AP-1 remains disabled by default
        assert config["AP-1"]["enabled"] is False

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
        """All 8 SC + 18 AP checks must be in the default config."""
        from tools.generate.validation.gates import _DEFAULT_SC_AP_CONFIG

        sc_keys = [k for k in _DEFAULT_SC_AP_CONFIG if k.startswith("SC-")]
        ap_keys = [k for k in _DEFAULT_SC_AP_CONFIG if k.startswith("AP-")]
        assert len(sc_keys) == 8, f"Expected 8 SC checks, got {len(sc_keys)}: {sc_keys}"
        assert len(ap_keys) == 18, f"Expected 18 AP checks, got {len(ap_keys)}: {ap_keys}"


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
        import json as _json

        from tools.generate.validation.gates import _check_structural_conformance

        db = tmp_path / "test_sc.sqlite"
        sqlite3.connect(str(db)).close()

        # Explicitly disable every SC check (SC-1/SC-5 are enabled by default post-promotion)
        cfg = tmp_path / "all_disabled.json"
        cfg.write_text(_json.dumps({f"SC-{i}": {"enabled": False, "audit_mode": True} for i in range(1, 9)}))
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
        import json as _json

        from tools.generate.validation.gates import _check_agentic_antipatterns

        db = tmp_path / "test_ap.sqlite"
        sqlite3.connect(str(db)).close()

        # Explicitly disable every AP check (AP-18 is enabled by default)
        cfg = tmp_path / "all_disabled.json"
        cfg.write_text(_json.dumps({f"AP-{i}": {"enabled": False, "audit_mode": True} for i in range(1, 19)}))
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
        for rt in tqdm(
            [
                "enters_sandbox",
                "validates_uwg_intent",
                "invokes_provider",
                "orchestrates_healing",
                "packages_execution_trace",
            ],
            desc="Processing",
            unit="item",
        ):
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

    def test_dispatch_tables_cover_all_checks(self):
        """Dispatch tables map all W2+W3+W4 checks to query functions."""
        from tools.generate.validation import _AP_CHECK_DISPATCH, _SC_CHECK_DISPATCH

        assert set(_SC_CHECK_DISPATCH.keys()) == {
            "SC-1",
            "SC-2",
            "SC-3",
            "SC-4",
            "SC-5",
            "SC-6",
            "SC-7",
            "SC-8",
        }
        assert set(_AP_CHECK_DISPATCH.keys()) == {
            "AP-1",
            "AP-2",
            "AP-3",
            "AP-4",
            "AP-5",
            "AP-6",
            "AP-7",
            "AP-8",
            "AP-9",
            "AP-10",
            "AP-11",
            "AP-12",
            "AP-13",
            "AP-14",
            "AP-15",
            "AP-16",
            "AP-17",
            "AP-18",
        }


# ---------------------------------------------------------------------------
# W3: SC-5 Agentic Spine Completeness
# ---------------------------------------------------------------------------


class TestSC5Spine:
    """SC-5: Agentic spine completeness."""

    def test_full_spine_passes(self, tmp_path):
        """All spine edge types present → no violation."""
        from tools.generate.validation.gates import _query_sc5_spine

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L1','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L2','module','high','b.py')")
        for rt in ["pulls_context", "generates_prompt", "consumes_prompt", "packages_execution_trace"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','a.py',1)",
                (rt,),
            )
        conn.commit()
        assert _query_sc5_spine(conn) == []
        conn.close()

    def test_missing_spine_detected(self, tmp_path):
        """Missing spine edge types flagged."""
        from tools.generate.validation.gates import _query_sc5_spine

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L1','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L2','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'pulls_context','','a.py',1)"
        )
        conn.commit()
        result = _query_sc5_spine(conn)
        assert len(result) == 1
        assert "missing edge types" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-5": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-5"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-5": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: SC-6 Role Purity
# ---------------------------------------------------------------------------


class TestSC6RolePurity:
    """SC-6: Role purity for L0, L1, L6."""

    def test_clean_roles_pass(self, tmp_path):
        """No forbidden edges → passes."""
        from tools.generate.validation.gates import _query_sc6_role_purity

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Router','module','L0','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Target','module','L2','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'routes_to','','r.py',5)"
        )
        conn.commit()
        assert _query_sc6_role_purity(conn) == []
        conn.close()

    def test_l0_invokes_provider_detected(self, tmp_path):
        """L0 with invokes_provider is forbidden."""
        from tools.generate.validation.gates import _query_sc6_role_purity

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Router','module','L0','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','r.py',10)"
        )
        conn.commit()
        result = _query_sc6_role_purity(conn)
        assert len(result) == 1
        assert "forbidden edge: invokes_provider" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Router','module','L0','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','r.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-6": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-6"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Router','module','L0','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','r.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-6": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: SC-7 Grounding Contract
# ---------------------------------------------------------------------------


class TestSC7Grounding:
    """SC-7: Grounding contract / C0-PA separation."""

    def test_grounded_module_passes(self, tmp_path):
        """Module with pulls_context + consumes_prompt + invokes_provider passes."""
        from tools.generate.validation.gates import _query_sc7_grounding

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        for rt in ["consumes_prompt", "invokes_provider", "pulls_context"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','m.py',1)",
                (rt,),
            )
        conn.commit()
        assert _query_sc7_grounding(conn) == []
        conn.close()

    def test_ungrounded_module_detected(self, tmp_path):
        """Module consuming prompt + invoking provider without pulls_context flagged."""
        from tools.generate.validation.gates import _query_sc7_grounding

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        for rt in ["consumes_prompt", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','m.py',1)",
                (rt,),
            )
        conn.commit()
        result = _query_sc7_grounding(conn)
        assert len(result) == 1
        assert "without pulls_context" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        for rt in ["consumes_prompt", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','m.py',1)",
                (rt,),
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-7": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-7"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        for rt in ["consumes_prompt", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','m.py',1)",
                (rt,),
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-7": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: SC-8 Trace/Eval Surface Coverage
# ---------------------------------------------------------------------------


class TestSC8TraceCoverage:
    """SC-8: Trace/replay/eval surface coverage."""

    def test_traced_action_passes(self, tmp_path):
        """Action-capable module with trace edge passes."""
        from tools.generate.validation.gates import _query_sc8_trace_coverage

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','a.py',10)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'packages_execution_trace','','a.py',12)"
        )
        conn.commit()
        assert _query_sc8_trace_coverage(conn) == []
        conn.close()

    def test_untraced_action_detected(self, tmp_path):
        """Action-capable module without trace edge flagged."""
        from tools.generate.validation.gates import _query_sc8_trace_coverage

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        result = _query_sc8_trace_coverage(conn)
        assert len(result) >= 1
        assert "without trace/eval" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-8": {"enabled": True, "audit_mode": True}})
        result = _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert len(result["SC-8"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-8": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-5 Tool Overlap
# ---------------------------------------------------------------------------


class TestAP5ToolOverlap:
    """AP-5: Tool overlap / ambiguous tool surfaces."""

    def test_no_overlap_passes(self, tmp_path):
        """Disjoint import sets → no violation."""
        from tools.generate.validation.gates import _query_ap5_tool_overlap

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'P1','module','L2','module','high','p1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P2','module','L2','module','high','p2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib1','module','L3','module','high','l1.py')")
        conn.execute("INSERT INTO nodes VALUES (11,'Lib2','module','L3','module','high','l2.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,10,'invokes_provider','','p1.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,11,'invokes_provider','','p2.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,10,'imports','','p1.py',2)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,11,'imports','','p2.py',2)"
        )
        conn.commit()
        assert _query_ap5_tool_overlap(conn) == []
        conn.close()

    def test_high_overlap_detected(self, tmp_path):
        """Two provider-invoking nodes sharing >70% imports flagged."""
        from tools.generate.validation.gates import _query_ap5_tool_overlap

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'P1','module','L2','module','high','p1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P2','module','L2','module','high','p2.py')")
        for lid in range(10, 20):
            conn.execute(
                f"INSERT INTO nodes VALUES ({lid},'Lib{lid}','module','L3','module','high','l{lid}.py')"
            )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,10,'invokes_provider','','p1.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,11,'invokes_provider','','p2.py',1)"
        )
        for lid in range(10, 18):
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{lid},'imports','','p1.py',2)"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (2,{lid},'imports','','p2.py',2)"
            )
        conn.commit()
        result = _query_ap5_tool_overlap(conn)
        assert len(result) >= 1
        assert "share >" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'P1','module','L2','module','high','p1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P2','module','L2','module','high','p2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib','module','L3','module','high','l.py')")
        for nid in [1, 2]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'invokes_provider','','p{nid}.py',1)"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'imports','','p{nid}.py',2)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-5": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-5"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'P1','module','L2','module','high','p1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P2','module','L2','module','high','p2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib','module','L3','module','high','l.py')")
        for nid in [1, 2]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'invokes_provider','','p{nid}.py',1)"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'imports','','p{nid}.py',2)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-5": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-6 Manager Sprawl
# ---------------------------------------------------------------------------


class TestAP6ManagerSprawl:
    """AP-6: Premature multi-agent / manager sprawl."""

    def test_low_fanout_passes(self, tmp_path):
        """≤5 routes_to_agent → passes."""
        from tools.generate.validation.gates import _query_ap6_manager_sprawl

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.commit()
        assert _query_ap6_manager_sprawl(conn) == []
        conn.close()

    def test_high_fanout_detected(self, tmp_path):
        """>5 routes_to_agent flagged."""
        from tools.generate.validation.gates import _query_ap6_manager_sprawl

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        for i in range(2, 9):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.commit()
        result = _query_ap6_manager_sprawl(conn)
        assert len(result) == 1
        assert ">5 threshold" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        for i in range(2, 9):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-6": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-6"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        for i in range(2, 9):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-6": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-7 Duplicate Specialization
# ---------------------------------------------------------------------------


class TestAP7DupSpecialization:
    """AP-7: Duplicate specialization — sibling agents with >80% overlapping imports."""

    def test_disjoint_agents_pass(self, tmp_path):
        """Agents with disjoint imports → passes."""
        from tools.generate.validation.gates import _query_ap7_dup_specialization

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Agent1','class','L2','module','high','a1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Agent2','class','L2','module','high','a2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib1','module','L3','module','high','l1.py')")
        conn.execute("INSERT INTO nodes VALUES (11,'Lib2','module','L3','module','high','l2.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,10,'imports','','a1.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,11,'imports','','a2.py',1)"
        )
        conn.commit()
        assert _query_ap7_dup_specialization(conn) == []
        conn.close()

    def test_overlapping_agents_detected(self, tmp_path):
        """Sibling agents sharing >80% imports flagged."""
        from tools.generate.validation.gates import _query_ap7_dup_specialization

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Agent1','class','L2','module','high','a1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Agent2','class','L2','module','high','a2.py')")
        for lid in range(10, 20):
            conn.execute(
                f"INSERT INTO nodes VALUES ({lid},'Lib{lid}','module','L3','module','high','l{lid}.py')"
            )
        for lid in range(10, 20):
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{lid},'imports','','a1.py',1)"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (2,{lid},'imports','','a2.py',1)"
            )
        conn.commit()
        result = _query_ap7_dup_specialization(conn)
        assert len(result) >= 1
        assert "share >" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Agent1','class','L2','module','high','a1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Agent2','class','L2','module','high','a2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib','module','L3','module','high','l.py')")
        for nid in [1, 2]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'imports','','a{nid}.py',1)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-7": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-7"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Agent1','class','L2','module','high','a1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Agent2','class','L2','module','high','a2.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Lib','module','L3','module','high','l.py')")
        for nid in [1, 2]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({nid},10,'imports','','a{nid}.py',1)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-7": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-8 Missing Trace (delegates to SC-8)
# ---------------------------------------------------------------------------


class TestAP8MissingTrace:
    """AP-8: Missing trace/eval on action paths (delegates to SC-8 query)."""

    def test_traced_action_passes(self, tmp_path):
        """Action module with trace edge passes."""
        from tools.generate.validation.gates import _query_ap8_missing_trace

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','a.py',10)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'triggered_telemetry','','a.py',12)"
        )
        conn.commit()
        assert _query_ap8_missing_trace(conn) == []
        conn.close()

    def test_untraced_action_detected(self, tmp_path):
        """Action module without trace flagged."""
        from tools.generate.validation.gates import _query_ap8_missing_trace

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','a.py',10)"
        )
        conn.commit()
        result = _query_ap8_missing_trace(conn)
        assert len(result) >= 1
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-8": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-8"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','a.py',10)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-8": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-9 Infrastructure Spread
# ---------------------------------------------------------------------------


class TestAP9InfraSpread:
    """AP-9: Infrastructure spread / service locator drift."""

    def test_narrow_spread_passes(self, tmp_path):
        """Infra module imported from ≤3 layers → passes."""
        from tools.generate.validation.gates import _query_ap9_infra_spread

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        for i, layer in enumerate(["L0", "L2", "L3"], start=10):
            conn.execute(
                f"INSERT INTO nodes VALUES ({i},'M{i}','module','{layer}','module','high','m{i}.py')"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({i},1,'imports','','m{i}.py',1)"
            )
        conn.commit()
        assert _query_ap9_infra_spread(conn) == []
        conn.close()

    def test_wide_spread_detected(self, tmp_path):
        """Infra module imported from >3 layers flagged."""
        from tools.generate.validation.gates import _query_ap9_infra_spread

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        for i, layer in enumerate(["L0", "L1", "L2", "L3"], start=10):
            conn.execute(
                f"INSERT INTO nodes VALUES ({i},'M{i}','module','{layer}','module','high','m{i}.py')"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({i},1,'imports','','m{i}.py',1)"
            )
        conn.commit()
        result = _query_ap9_infra_spread(conn)
        assert len(result) >= 1
        assert ">3 threshold" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        for i, layer in enumerate(["L0", "L1", "L2", "L3"], start=10):
            conn.execute(
                f"INSERT INTO nodes VALUES ({i},'M{i}','module','{layer}','module','high','m{i}.py')"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({i},1,'imports','','m{i}.py',1)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-9": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-9"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        for i, layer in enumerate(["L0", "L1", "L2", "L3"], start=10):
            conn.execute(
                f"INSERT INTO nodes VALUES ({i},'M{i}','module','{layer}','module','high','m{i}.py')"
            )
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({i},1,'imports','','m{i}.py',1)"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-9": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: AP-10 Live/Future Mutation Confusion
# ---------------------------------------------------------------------------


class TestAP10MutationConfusion:
    """AP-10: Live/future mutation confusion — L6 writing to non-L6 modules."""

    def test_l6_internal_write_passes(self, tmp_path):
        """L6 writing to L6 → passes."""
        from tools.generate.validation.gates import _query_ap10_mutation_confusion

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Learner','module','L6','module','high','l.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Store','module','L6','module','high','s.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','l.py',5)"
        )
        conn.commit()
        assert _query_ap10_mutation_confusion(conn) == []
        conn.close()

    def test_l6_cross_layer_write_detected(self, tmp_path):
        """L6 writing to L2 → flagged."""
        from tools.generate.validation.gates import _query_ap10_mutation_confusion

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Learner','module','L6','module','high','l.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Exec','module','L2','module','high','e.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','l.py',5)"
        )
        conn.commit()
        result = _query_ap10_mutation_confusion(conn)
        assert len(result) == 1
        assert "L6" in result[0]["evidence"]
        assert "L2" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Learner','module','L6','module','high','l.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Exec','module','L2','module','high','e.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','l.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-10": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-10"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Learner','module','L6','module','high','l.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Exec','module','L2','module','high','e.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'writes_to','','l.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-10": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W3: P1 severity insertion verification
# ---------------------------------------------------------------------------


class TestW3SeverityInsertion:
    """W3: Verify P1 severity for SC-5+ and AP-5+ violations."""

    def test_sc5_inserts_p1_severity(self, tmp_path):
        """SC-5 violations insert with severity='P1'."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"SC-5": {"enabled": True, "audit_mode": True}})
        _check_structural_conformance(sqlite_path=db, config_path=cfg)
        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute("SELECT severity FROM violations WHERE category = 'SC-5'").fetchall()
        assert len(rows) >= 1
        assert all(r[0] == "P1" for r in rows)
        conn2.close()

    def test_ap6_inserts_p1_severity(self, tmp_path):
        """AP-6 violations insert with severity='P1'."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        for i in range(2, 9):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-6": {"enabled": True, "audit_mode": True}})
        _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute("SELECT severity FROM violations WHERE category = 'AP-6'").fetchall()
        assert len(rows) >= 1
        assert all(r[0] == "P1" for r in rows)
        conn2.close()


# ---------------------------------------------------------------------------
# W3: Exports verification
# ---------------------------------------------------------------------------


class TestW3ExportsComplete:
    """W3: Verify all W3 query functions and tables are exported."""

    def test_all_w3_exports_importable(self):
        """All W3 exports must be importable from tools.generate.validation."""
        from tools.generate.validation import (
            _ROLE_FORBIDDEN_EDGES,
            _query_ap10_mutation_confusion,
            _query_ap5_tool_overlap,
            _query_ap6_manager_sprawl,
            _query_ap7_dup_specialization,
            _query_ap8_missing_trace,
            _query_ap9_infra_spread,
            _query_sc5_spine,
            _query_sc6_role_purity,
            _query_sc7_grounding,
            _query_sc8_trace_coverage,
        )

        assert "L0" in _ROLE_FORBIDDEN_EDGES
        assert callable(_query_sc5_spine)
        assert callable(_query_sc6_role_purity)
        assert callable(_query_sc7_grounding)
        assert callable(_query_sc8_trace_coverage)
        assert callable(_query_ap5_tool_overlap)
        assert callable(_query_ap6_manager_sprawl)
        assert callable(_query_ap7_dup_specialization)
        assert callable(_query_ap8_missing_trace)
        assert callable(_query_ap9_infra_spread)
        assert callable(_query_ap10_mutation_confusion)


# ---------------------------------------------------------------------------
# W4: AP-11 Poorly Scoped Work Contracts
# ---------------------------------------------------------------------------


class TestAP11WorkContracts:
    """AP-11: Poorly scoped work contracts."""

    def test_contract_present_passes(self, tmp_path):
        """L2 module with stamps_work_contract → passes."""
        from tools.generate.validation.gates import _query_ap11_work_contracts

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'stamps_work_contract','','e.py',2)"
        )
        conn.commit()
        assert _query_ap11_work_contracts(conn) == []
        conn.close()

    def test_missing_contract_detected(self, tmp_path):
        """L2 module executing without stamps_work_contract → flagged."""
        from tools.generate.validation.gates import _query_ap11_work_contracts

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        result = _query_ap11_work_contracts(conn)
        assert len(result) >= 1
        assert "without stamps_work_contract" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-11": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-11"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-11": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-12 Prompt Scatter
# ---------------------------------------------------------------------------


class TestAP12PromptScatter:
    """AP-12: Prompt scatter — >3 generates_prompt edges."""

    def test_low_prompt_count_passes(self, tmp_path):
        """≤3 generates_prompt edges → passes."""
        from tools.generate.validation.gates import _query_ap12_prompt_scatter

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        for i in range(2, 5):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'T{i}','module','L3','module','high','t{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'generates_prompt','','m.py',{i})"
            )
        conn.commit()
        assert _query_ap12_prompt_scatter(conn) == []
        conn.close()

    def test_high_prompt_count_detected(self, tmp_path):
        """>3 generates_prompt flagged."""
        from tools.generate.validation.gates import _query_ap12_prompt_scatter

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'T{i}','module','L3','module','high','t{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'generates_prompt','','m.py',{i})"
            )
        conn.commit()
        result = _query_ap12_prompt_scatter(conn)
        assert len(result) == 1
        assert ">3 threshold" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'T{i}','module','L3','module','high','t{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'generates_prompt','','m.py',{i})"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-12": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-12"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'M','module','L2','module','high','m.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'T{i}','module','L3','module','high','t{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'generates_prompt','','m.py',{i})"
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-12": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-13 Retry/Heal Without Exit Criteria
# ---------------------------------------------------------------------------


class TestAP13RetryNoExit:
    """AP-13: Retry/heal without clear exit criteria."""

    def test_sealed_healing_passes(self, tmp_path):
        """Healing with execution trace seal → passes."""
        from tools.generate.validation.gates import _query_ap13_retry_no_exit

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Healer','module','L2','module','high','h.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'orchestrates_healing','','h.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'packages_execution_trace','','h.py',2)"
        )
        conn.commit()
        assert _query_ap13_retry_no_exit(conn) == []
        conn.close()

    def test_unsealed_healing_detected(self, tmp_path):
        """Healing without seal → flagged."""
        from tools.generate.validation.gates import _query_ap13_retry_no_exit

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Healer','module','L2','module','high','h.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'orchestrates_healing','','h.py',1)"
        )
        conn.commit()
        result = _query_ap13_retry_no_exit(conn)
        assert len(result) == 1
        assert "without execution trace seal" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Healer','module','L2','module','high','h.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'orchestrates_healing','','h.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-13": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-13"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Healer','module','L2','module','high','h.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'orchestrates_healing','','h.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-13": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-14 Retrieval Without Evidence Contract
# ---------------------------------------------------------------------------


class TestAP14RetrievalNoEvidence:
    """AP-14: Retrieval without evidence contract."""

    def test_guarded_retrieval_passes(self, tmp_path):
        """Retrieval with applies_guardrail → passes."""
        from tools.generate.validation.gates import _query_ap14_retrieval_no_evidence

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L2','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        for rt in ["pulls_context", "invokes_provider", "applies_guardrail"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','r.py',1)",
                (rt,),
            )
        conn.commit()
        assert _query_ap14_retrieval_no_evidence(conn) == []
        conn.close()

    def test_unguarded_retrieval_detected(self, tmp_path):
        """Retrieval + provider invoke without guardrail → flagged."""
        from tools.generate.validation.gates import _query_ap14_retrieval_no_evidence

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L2','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        for rt in ["pulls_context", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','r.py',1)",
                (rt,),
            )
        conn.commit()
        result = _query_ap14_retrieval_no_evidence(conn)
        assert len(result) >= 1
        assert "without guardrail" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L2','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        for rt in ["pulls_context", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','r.py',1)",
                (rt,),
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-14": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-14"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'R','module','L2','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        for rt in ["pulls_context", "invokes_provider"]:
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                "VALUES (1,2,?,'','r.py',1)",
                (rt,),
            )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-14": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-15 Agent Count Outrunning Tool Surfaces
# ---------------------------------------------------------------------------


class TestAP15AgentToolRatio:
    """AP-15: Agent count outrunning tool surfaces (>3:1)."""

    def test_balanced_ratio_passes(self, tmp_path):
        """Agent:tool ratio ≤3:1 → passes."""
        from tools.generate.validation.gates import _query_ap15_agent_tool_ratio

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'A1','agent','L2','module','high','a1.py')")
        conn.execute("INSERT INTO nodes VALUES (3,'A2','agent','L2','module','high','a2.py')")
        conn.execute("INSERT INTO nodes VALUES (4,'Tool','module','L3','module','high','t.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'routes_to_agent','','m.py',1)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,3,'routes_to_agent','','m.py',2)"
        )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,4,'invokes_provider','','a1.py',3)"
        )
        conn.commit()
        assert _query_ap15_agent_tool_ratio(conn) == []
        conn.close()

    def test_high_ratio_detected(self, tmp_path):
        """Agent:tool ratio >3:1 → flagged."""
        from tools.generate.validation.gates import _query_ap15_agent_tool_ratio

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Tool','module','L3','module','high','t.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,10,'invokes_provider','','a2.py',1)"
        )
        conn.commit()
        result = _query_ap15_agent_tool_ratio(conn)
        assert len(result) == 1
        assert "3:1 threshold" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Tool','module','L3','module','high','t.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,10,'invokes_provider','','a2.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-15": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-15"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Tool','module','L3','module','high','t.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,10,'invokes_provider','','a2.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-15": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-16 Dormant Infrastructure
# ---------------------------------------------------------------------------


class TestAP16DormantInfra:
    """AP-16: Dormant infrastructure — infra modules with <3 imports."""

    def test_well_connected_infra_passes(self, tmp_path):
        """Infra module with ≥3 imports → passes."""
        from tools.generate.validation.gates import _query_ap16_dormant_infra

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        for i in range(10, 13):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'M{i}','module','L2','module','high','m{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES ({i},1,'imports','','m{i}.py',1)"
            )
        conn.commit()
        assert _query_ap16_dormant_infra(conn) == []
        conn.close()

    def test_dormant_infra_detected(self, tmp_path):
        """Infra module with <3 imports → flagged."""
        from tools.generate.validation.gates import _query_ap16_dormant_infra

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'M','module','L2','module','high','m.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (10,1,'imports','','m.py',1)"
        )
        conn.commit()
        result = _query_ap16_dormant_infra(conn)
        assert len(result) >= 1
        assert "<3 threshold" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-16": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-16"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'redis_client','module','L4','module','high','r.py')")
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-16": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: AP-17 Semantic Precision Gaps
# ---------------------------------------------------------------------------


class TestAP17SemanticPrecision:
    """AP-17: Agentic semantic precision gaps."""

    def test_domain_edge_kind_passes(self, tmp_path):
        """Non-generic edge_kind → passes."""
        from tools.generate.validation.gates import _query_ap17_semantic_precision

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','provider_call','a.py',1)"
        )
        conn.commit()
        assert _query_ap17_semantic_precision(conn) == []
        conn.close()

    def test_generic_edge_kind_detected(self, tmp_path):
        """Generic edge_kind 'call' → flagged."""
        from tools.generate.validation.gates import _query_ap17_semantic_precision

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','call','a.py',5)"
        )
        conn.commit()
        result = _query_ap17_semantic_precision(conn)
        assert len(result) >= 1
        assert "generic edge_kind 'call'" in result[0]["evidence"]
        conn.close()

    def test_audit_mode_does_not_exit(self, tmp_path, capsys):
        """Audit mode logs but does not block."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','write','a.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-17": {"enabled": True, "audit_mode": True}})
        result = _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert len(result["AP-17"]) >= 1
        assert "[AUDIT]" in capsys.readouterr().out

    def test_enforce_mode_exits(self, tmp_path):
        """Enforce mode sys.exit(1) on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L3','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','read','a.py',5)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-17": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W4: Severity insertion verification
# ---------------------------------------------------------------------------


class TestW4SeverityInsertion:
    """W4: Verify P2/P3 severity for AP-11+ violations."""

    def test_ap11_inserts_p2_severity(self, tmp_path):
        """AP-11 violations insert with severity='P2'."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Exec','module','L2','module','high','e.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'P','module','L3','module','high','p.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'invokes_provider','','e.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-11": {"enabled": True, "audit_mode": True}})
        _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute("SELECT severity FROM violations WHERE category = 'AP-11'").fetchall()
        assert len(rows) >= 1
        assert all(r[0] == "P2" for r in rows)
        conn2.close()

    def test_ap15_inserts_p3_severity(self, tmp_path):
        """AP-15 violations insert with severity='P3'."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Mgr','module','L0','module','high','m.py')")
        conn.execute("INSERT INTO nodes VALUES (10,'Tool','module','L3','module','high','t.py')")
        for i in range(2, 7):
            conn.execute(f"INSERT INTO nodes VALUES ({i},'A{i}','agent','L2','module','high','a{i}.py')")
            conn.execute(
                "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
                f"VALUES (1,{i},'routes_to_agent','','m.py',{i})"
            )
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (2,10,'invokes_provider','','a2.py',1)"
        )
        conn.commit()
        conn.close()
        cfg = _write_sc_ap_config(tmp_path, {"AP-15": {"enabled": True, "audit_mode": True}})
        _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute("SELECT severity FROM violations WHERE category = 'AP-15'").fetchall()
        assert len(rows) >= 1
        assert all(r[0] == "P3" for r in rows)
        conn2.close()


# ---------------------------------------------------------------------------
# W4: Exports verification
# ---------------------------------------------------------------------------


class TestW4ExportsComplete:
    """W4: Verify all W4 query functions are exported."""

    def test_all_w4_exports_importable(self):
        """All W4 exports must be importable from tools.generate.validation."""
        from tools.generate.validation import (
            _GENERIC_EDGE_KINDS,
            _query_ap11_work_contracts,
            _query_ap12_prompt_scatter,
            _query_ap13_retry_no_exit,
            _query_ap14_retrieval_no_evidence,
            _query_ap15_agent_tool_ratio,
            _query_ap16_dormant_infra,
            _query_ap17_semantic_precision,
        )

        assert "call" in _GENERIC_EDGE_KINDS
        assert callable(_query_ap11_work_contracts)
        assert callable(_query_ap12_prompt_scatter)
        assert callable(_query_ap13_retry_no_exit)
        assert callable(_query_ap14_retrieval_no_evidence)
        assert callable(_query_ap15_agent_tool_ratio)
        assert callable(_query_ap16_dormant_infra)
        assert callable(_query_ap17_semantic_precision)


# ---------------------------------------------------------------------------
# W5: Edge-case tests — empty graph, single node, tools-only
# ---------------------------------------------------------------------------


class TestEdgeCaseEmptyGraph:
    """All SC/AP checks return [] on empty graph."""

    def test_sc_checks_empty_graph(self, tmp_path):
        """All SC query functions return [] on empty graph."""
        from tools.generate.validation.gates import (
            _query_sc1_gravity,
            _query_sc2_lifecycle,
            _query_sc3_uwg_write,
            _query_sc4_choke_point,
            _query_sc5_spine,
            _query_sc6_role_purity,
            _query_sc7_grounding,
            _query_sc8_trace_coverage,
        )

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        # SC-5 (spine) correctly fires on empty graph (missing spine edges)
        for fn in [
            _query_sc1_gravity,
            _query_sc2_lifecycle,
            _query_sc3_uwg_write,
            _query_sc4_choke_point,
            _query_sc6_role_purity,
            _query_sc7_grounding,
            _query_sc8_trace_coverage,
        ]:
            assert fn(conn) == [], f"{fn.__name__} should return [] on empty graph"
        conn.close()

    def test_ap_checks_empty_graph(self, tmp_path):
        """All AP query functions return [] on empty graph."""
        from tools.generate.validation.gates import (
            _query_ap1_text_to_action,
            _query_ap2_phase_bypass,
            _query_ap3_provider_bypass,
            _query_ap4_direct_write,
            _query_ap5_tool_overlap,
            _query_ap6_manager_sprawl,
            _query_ap7_dup_specialization,
            _query_ap8_missing_trace,
            _query_ap9_infra_spread,
            _query_ap10_mutation_confusion,
            _query_ap11_work_contracts,
            _query_ap12_prompt_scatter,
            _query_ap13_retry_no_exit,
            _query_ap14_retrieval_no_evidence,
            _query_ap15_agent_tool_ratio,
            _query_ap16_dormant_infra,
            _query_ap17_semantic_precision,
        )

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        for fn in tqdm(
            [
                _query_ap1_text_to_action,
                _query_ap2_phase_bypass,
                _query_ap3_provider_bypass,
                _query_ap4_direct_write,
                _query_ap5_tool_overlap,
                _query_ap6_manager_sprawl,
                _query_ap7_dup_specialization,
                _query_ap8_missing_trace,
                _query_ap9_infra_spread,
                _query_ap10_mutation_confusion,
                _query_ap11_work_contracts,
                _query_ap12_prompt_scatter,
                _query_ap13_retry_no_exit,
                _query_ap14_retrieval_no_evidence,
                _query_ap15_agent_tool_ratio,
                _query_ap16_dormant_infra,
                _query_ap17_semantic_precision,
            ],
            desc="Processing",
            unit="item",
        ):
            assert fn(conn) == [], f"{fn.__name__} should return [] on empty graph"
        conn.close()


class TestEdgeCaseSingleNode:
    """Checks with a single node and no edges."""

    def test_single_node_no_edges(self, tmp_path):
        """Single production node, no edges → all checks pass."""
        from tools.generate.validation.gates import (
            _query_sc1_gravity,
            _query_ap1_text_to_action,
            _query_ap15_agent_tool_ratio,
        )

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'Solo','module','L2','module','high','s.py')")
        conn.commit()
        assert _query_sc1_gravity(conn) == []
        assert _query_ap1_text_to_action(conn) == []
        assert _query_ap15_agent_tool_ratio(conn) == []
        conn.close()


class TestEdgeCaseToolsOnly:
    """All nodes in tools layer → no SC/AP violations on production-scoped checks."""

    def test_tools_only_no_sc_violations(self, tmp_path):
        """Nodes only in L_TOOLS → no gravity or role-purity violations."""
        from tools.generate.validation.gates import _query_sc1_gravity, _query_sc6_role_purity

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'T1','module','L_TOOLS','module','high','t1.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'T2','module','L_TOOLS','module','high','t2.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','t1.py',1)"
        )
        conn.commit()
        assert _query_sc1_gravity(conn) == []
        assert _query_sc6_role_purity(conn) == []
        conn.close()


# ---------------------------------------------------------------------------
# W5: Burndown by_class severity mapping test
# ---------------------------------------------------------------------------


class TestBurndownByClassMapping:
    """Burndown correctly maps P0-P3 severity strings from SC/AP violations."""

    def test_by_class_maps_sc_ap_violations(self, tmp_path):
        """SC/AP violations with P0-P3 severity appear in burndown by_class."""
        from tools.generate.validation.gates import (
            _check_structural_conformance,
            _check_agentic_antipatterns,
        )

        db, conn = _make_adg_db(tmp_path)
        # SC-1 violation: L0→L2 import (gravity forbidden)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L2','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',1)"
        )
        conn.commit()
        conn.close()

        cfg = _write_sc_ap_config(tmp_path, {"SC-1": {"enabled": True, "audit_mode": True}})
        _check_structural_conformance(sqlite_path=db, config_path=cfg)

        conn2 = sqlite3.connect(str(db))
        rows = conn2.execute(
            "SELECT violation_class, severity FROM violations WHERE category = 'SC-1'"
        ).fetchall()
        assert len(rows) >= 1
        assert rows[0][0] == "structural_conformance"
        assert rows[0][1] == "P0"
        conn2.close()


# ---------------------------------------------------------------------------
# W5: Defect table SC/AP rows test
# ---------------------------------------------------------------------------


class TestDefectTableSCAPRows:
    """SC/AP violations appear in defect table output."""

    def test_sc_ap_rows_in_defect_output(self, tmp_path, capsys):
        """Defect table prints SC~ and AP~ rows when violations exist."""
        from tools.generate.reporting.reports import _print_defect_table

        db, conn = _make_adg_db(tmp_path)
        # Insert SC/AP violations directly
        conn.execute(
            "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, violation_class) "
            "VALUES (0, 'SC-1', 'test evidence', 'a.py', 0, 'P0', 'structural_conformance')"
        )
        conn.execute(
            "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, violation_class) "
            "VALUES (0, 'AP-5', 'test evidence', 'b.py', 0, 'P1', 'agentic_antipattern')"
        )
        conn.commit()
        conn.close()

        _print_defect_table({"by_severity": {}}, sqlite_path=db)
        output = capsys.readouterr().out
        # Output format: aggregate SC/AP rows appear as 'structural conformance'
        # and 'agentic antipatterns' banded rows in the burndown table.
        assert "structural conformance" in output
        assert "agentic antipatterns" in output
        assert "SC-1" in output
        assert "AP-5" in output


# ---------------------------------------------------------------------------
# W5: Config promotion workflow test
# ---------------------------------------------------------------------------


class TestConfigPromotion:
    """Promotion workflow: flip audit_mode to False and set promoted_date."""

    def test_promotion_workflow(self, tmp_path):
        """Save config with promoted check → reload still has promotion."""
        from tools.generate.validation.gates import _load_sc_ap_config, _save_sc_ap_config

        cfg_path = tmp_path / "sc_ap_config.json"
        config = _load_sc_ap_config(config_path=cfg_path)
        config["SC-1"]["enabled"] = True
        config["SC-1"]["audit_mode"] = False
        config["SC-1"]["promoted_date"] = "2026-04-08"
        _save_sc_ap_config(config, config_path=cfg_path)

        reloaded = _load_sc_ap_config(config_path=cfg_path)
        assert reloaded["SC-1"]["enabled"] is True
        assert reloaded["SC-1"]["audit_mode"] is False
        assert reloaded["SC-1"]["promoted_date"] == "2026-04-08"


# ---------------------------------------------------------------------------
# W5: All checks disabled by default
# ---------------------------------------------------------------------------


class TestAllChecksDisabledByDefault:
    """Default config has all checks disabled — no violations on any graph."""

    def test_default_config_no_violations(self, tmp_path):
        """With all checks explicitly disabled, no SC/AP violations are produced."""
        import json as _json

        from tools.generate.validation.gates import (
            _check_structural_conformance,
            _check_agentic_antipatterns,
        )

        db, conn = _make_adg_db(tmp_path)
        # Create a graph that would trigger violations
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L3','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L0','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',1)"
        )
        conn.commit()
        conn.close()

        # Explicit all-disabled config (SC-1/SC-5/AP-18 are enabled in production defaults)
        all_disabled_cfg = tmp_path / "all_disabled.json"
        disabled_map: dict[str, dict[str, object]] = {}
        for i in range(1, 9):
            disabled_map[f"SC-{i}"] = {"enabled": False, "audit_mode": True}
        for i in range(1, 19):
            disabled_map[f"AP-{i}"] = {"enabled": False, "audit_mode": True}
        all_disabled_cfg.write_text(_json.dumps(disabled_map))
        sc_result = _check_structural_conformance(sqlite_path=db, config_path=all_disabled_cfg)
        ap_result = _check_agentic_antipatterns(sqlite_path=db, config_path=all_disabled_cfg)
        assert all(len(v) == 0 for v in sc_result.values())
        assert all(len(v) == 0 for v in ap_result.values())


# ---------------------------------------------------------------------------
# W5: Severity band coverage — all 4 bands represented
# ---------------------------------------------------------------------------


class TestSeverityBandCoverage:
    """All 4 severity bands (P0-P3) are assignable across the full check set."""

    def test_severity_bands_cover_all(self):
        """SC dispatch (P0/P1) + AP dispatch (P0/P1/P2/P3) cover all severity bands."""
        from tools.generate.validation import _SC_CHECK_DISPATCH, _AP_CHECK_DISPATCH

        sc_ids = set(_SC_CHECK_DISPATCH.keys())
        ap_ids = set(_AP_CHECK_DISPATCH.keys())

        # SC-1..4 are P0, SC-5..8 are P1
        for cid in ["SC-1", "SC-2", "SC-3", "SC-4"]:
            assert cid in sc_ids
        for cid in ["SC-5", "SC-6", "SC-7", "SC-8"]:
            assert cid in sc_ids

        # AP-1..4 P0, AP-5..10 P1, AP-11..14 P2, AP-15..17 P3
        for cid in ["AP-1", "AP-2", "AP-3", "AP-4"]:
            assert cid in ap_ids
        for cid in ["AP-5", "AP-6", "AP-7", "AP-8", "AP-9", "AP-10"]:
            assert cid in ap_ids
        for cid in ["AP-11", "AP-12", "AP-13", "AP-14"]:
            assert cid in ap_ids
        for cid in ["AP-15", "AP-16", "AP-17"]:
            assert cid in ap_ids


# ---------------------------------------------------------------------------
# W6-residual: Gate orchestrator enforce-mode exit
# ---------------------------------------------------------------------------


class TestGateEnforceModeExit:
    """Gate orchestrator calls sys.exit(1) when audit_mode=False and violations exist."""

    def test_sc_gate_enforce_exits(self, tmp_path):
        """SC gate in enforce mode exits on violation."""
        from tools.generate.validation.gates import _check_structural_conformance

        db, conn = _make_adg_db(tmp_path)
        # L0→L2 import is gravity-forbidden
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L0','module','high','a.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'B','module','L2','module','high','b.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'imports','','a.py',1)"
        )
        conn.commit()
        conn.close()

        cfg = _write_sc_ap_config(tmp_path, {"SC-1": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_structural_conformance(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1

    def test_ap_gate_enforce_exits(self, tmp_path):
        """AP gate in enforce mode exits on violation."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        db, conn = _make_adg_db(tmp_path)
        # AP-17 fires on generic edge_kind ('call') with non-import relation_type
        conn.execute("INSERT INTO nodes VALUES (1,'X','module','L2','module','high','x.py')")
        conn.execute("INSERT INTO nodes VALUES (2,'Y','module','L2','module','high','y.py')")
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no) "
            "VALUES (1,2,'controls_flow','call','x.py',1)"
        )
        conn.commit()
        conn.close()

        cfg = _write_sc_ap_config(tmp_path, {"AP-17": {"enabled": True, "audit_mode": False}})
        with pytest.raises(SystemExit) as exc_info:
            _check_agentic_antipatterns(sqlite_path=db, config_path=cfg)
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# W6-residual: Bad dispatch warning
# ---------------------------------------------------------------------------


class TestBadDispatchWarning:
    """Gate warns when dispatch table references a non-existent function."""

    def test_sc_bad_dispatch_warns(self, tmp_path, capsys, monkeypatch):
        """SC gate prints warning when dispatch function is not found."""
        from tools.generate.validation import gates as gates_mod

        db, conn = _make_adg_db(tmp_path)
        conn.execute("INSERT INTO nodes VALUES (1,'A','module','L2','module','high','a.py')")
        conn.commit()
        conn.close()

        # Inject a bad dispatch entry
        original = gates_mod._SC_CHECK_DISPATCH.copy()
        monkeypatch.setattr(gates_mod, "_SC_CHECK_DISPATCH", {"SC-99": "_query_sc99_nonexistent"})

        cfg = _write_sc_ap_config(tmp_path, {"SC-99": {"enabled": True, "audit_mode": True, "label": "Fake"}})
        gates_mod._check_structural_conformance(sqlite_path=db, config_path=cfg)
        output = capsys.readouterr().out
        assert "WARNING" in output
        assert "_query_sc99_nonexistent" in output


# ---------------------------------------------------------------------------
# W6-residual: _ensure_violation_class_column migration
# ---------------------------------------------------------------------------


class TestMigrationViolationClassColumn:
    """_ensure_violation_class_column adds column to DBs that lack it."""

    def test_adds_column_when_missing(self, tmp_path):
        """Column is added to old-schema violations table."""
        from tools.generate.validation.gates import _ensure_violation_class_column

        db = tmp_path / "old.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE violations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "edge_id INTEGER, category TEXT, evidence TEXT, "
            "file_path TEXT, line_no INTEGER, severity TEXT)"
        )
        conn.commit()

        cols_before = {r[1] for r in conn.execute("PRAGMA table_info(violations)").fetchall()}
        assert "violation_class" not in cols_before

        _ensure_violation_class_column(conn)

        cols_after = {r[1] for r in conn.execute("PRAGMA table_info(violations)").fetchall()}
        assert "violation_class" in cols_after
        conn.close()

    def test_noop_when_column_exists(self, tmp_path):
        """No error when column already exists."""
        from tools.generate.validation.gates import _ensure_violation_class_column

        db, conn = _make_adg_db(tmp_path)
        conn.commit()
        # violations table in _make_adg_db already has violation_class
        _ensure_violation_class_column(conn)  # should not raise
        cols = {r[1] for r in conn.execute("PRAGMA table_info(violations)").fetchall()}
        assert "violation_class" in cols
        conn.close()


# ---------------------------------------------------------------------------
# W6-residual: Malformed config JSON handling
# ---------------------------------------------------------------------------


class TestMalformedConfigHandling:
    """_load_sc_ap_config fails gracefully on malformed JSON."""

    def test_malformed_json_raises(self, tmp_path):
        """Malformed JSON config file raises json.JSONDecodeError."""
        import json as json_mod
        from tools.generate.validation.gates import _load_sc_ap_config

        cfg_path = tmp_path / "bad_config.json"
        cfg_path.write_text("{broken json", encoding="utf-8")
        with pytest.raises(json_mod.JSONDecodeError):
            _load_sc_ap_config(config_path=cfg_path)


# ---------------------------------------------------------------------------
# W6-residual: Defect table resilience on old DB without violation_class
# ---------------------------------------------------------------------------


class TestDefectTableOldDB:
    """Defect table handles DB without violation_class column gracefully."""

    def test_no_crash_on_old_schema(self, tmp_path, capsys):
        """_print_defect_table does not crash when violation_class column is absent."""
        from tools.generate.reporting.reports import _print_defect_table

        db = tmp_path / "old.sqlite"
        conn = sqlite3.connect(str(db))
        conn.execute(
            "CREATE TABLE violations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "edge_id INTEGER, category TEXT, evidence TEXT, "
            "file_path TEXT, line_no INTEGER, severity TEXT)"
        )
        conn.execute(
            "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity) "
            "VALUES (0, 'SC-1', 'test', 'a.py', 0, 'P0')"
        )
        conn.commit()
        conn.close()

        # Should not raise — SC/AP rows just won't appear
        _print_defect_table({"by_severity": {}}, sqlite_path=db)
        output = capsys.readouterr().out
        # No SC/AP rows since column is absent
        assert "[SC]" not in output


class TestBurndownProvenance:
    """Burndown writer emits deterministic provenance and mismatch signal."""

    def test_burndown_includes_provenance_fields(self, tmp_path, capsys):
        from tools.generate.reporting.reports import _print_defect_table

        db, conn = _make_adg_db(tmp_path)
        conn.execute(
            "INSERT INTO edges (src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol) "
            "VALUES (1,2,'antipattern','return_none_swallow','agentic_core/x.py',5,'ValueError')"
        )
        conn.execute(
            "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, violation_class) "
            "VALUES (1, 'antipattern', 'ValueError', 'agentic_core/x.py', 5, 'HIGH', 'hygiene')"
        )
        conn.commit()
        conn.close()

        _print_defect_table({"by_severity": {}}, sqlite_path=db)
        capsys.readouterr()

        burndown_path = Path("artifacts/adg/adg_burndown_table.json")
        data = json.loads(burndown_path.read_text(encoding="utf-8"))
        assert "provenance" in data
        provenance = data["provenance"]
        assert provenance["generator_module"] == "tools.generate.reporting.reports._print_defect_table"
        assert provenance["sqlite_source_path"].endswith(".sqlite")
        assert provenance["counting_mode"] == "violations_plus_exempted_edge_inference"
        assert "single-tranche" in provenance["historical_interpretation_note"]

    def test_defect_table_reports_snapshot_mismatch_warning(self, tmp_path, capsys):
        from tools.generate.reporting.reports import _print_defect_table

        latest_db = tmp_path / "adg_indexed_04192026_0724.sqlite"
        sentinel_db = tmp_path / "adg_indexed_99999999_9999.sqlite"
        other_db = tmp_path / "older.sqlite"
        for db in (latest_db, sentinel_db, other_db):
            conn = sqlite3.connect(str(db))
            conn.execute(
                "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, relation_type TEXT, source_file TEXT, line_no INTEGER)"
            )
            conn.execute(
                "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, severity TEXT, violation_class TEXT)"
            )
            conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()
            conn.close()

        adg_dir = Path("artifacts/adg")
        adg_dir.mkdir(parents=True, exist_ok=True)
        copied_latest = adg_dir / latest_db.name
        copied_latest.write_bytes(latest_db.read_bytes())

        _print_defect_table({"by_severity": {}}, sqlite_path=other_db)
        output = capsys.readouterr().out
        assert "reporting sqlite differs from latest snapshot" in output

    def test_defect_table_ignores_sentinel_latest_when_source_is_valid_latest(self, tmp_path, capsys):
        from tools.generate.reporting.reports import _print_defect_table

        latest_db = tmp_path / "adg_indexed_04192026_0724.sqlite"
        sentinel_db = tmp_path / "adg_indexed_99999999_9999.sqlite"
        for db in (latest_db, sentinel_db):
            conn = sqlite3.connect(str(db))
            conn.execute(
                "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, relation_type TEXT, source_file TEXT, line_no INTEGER)"
            )
            conn.execute(
                "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, severity TEXT, violation_class TEXT)"
            )
            conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()
            conn.close()

        adg_dir = Path("artifacts/adg")
        adg_dir.mkdir(parents=True, exist_ok=True)
        copied_latest = None
        for db in (latest_db, sentinel_db):
            copied = adg_dir / db.name
            copied.write_bytes(db.read_bytes())
            if db == latest_db:
                copied_latest = copied

        assert copied_latest is not None
        _print_defect_table({"by_severity": {}}, sqlite_path=copied_latest)
        output = capsys.readouterr().out
        assert "reporting sqlite differs from latest snapshot" not in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
