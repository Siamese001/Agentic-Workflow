#!/usr/bin/env python3
"""
Phase 1 SSOT Tests: ADG Violations Table as Single Authority.

Tests per windsurfrules §1.1-§1.8 requirements:
- §1.1 Deterministic inputs/outputs
- §1.2 No external dependencies
- §1.3 No mutable global state
- §1.4 Idempotent operations
- §1.5 Edge case handling
- §1.6 Error handling and recovery
- §1.7 Deterministic behavior
- §1.8 Fail-closed error handling

Phase 1 validates:
1. ADG violations schema extensions (disposition, severity fields)
2. GuardianSweepFixer reads from ADG instead of JSON
3. Disposition updates flow back to ADG
4. No dependency on silent_swallower_report.json
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Generator

import pytest

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
from guardian_sweep import GuardianSweepFixer


class TestADGViolationsSchemaExtensions:
    """§1.5 Edge case: Schema extensions work correctly."""

    @pytest.fixture
    def temp_adg_db(self) -> Generator[Path, None, None]:
        """Create a temporary ADG SQLite with extended violations schema."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_adg.sqlite"

            # Create ADG schema with Phase 1 extensions
            conn = sqlite3.connect(str(db_path))
            try:
                # Basic tables
                conn.execute("""
                    CREATE TABLE nodes (
                        id INTEGER PRIMARY KEY,
                        adg_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        layer TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src_id INTEGER NOT NULL REFERENCES nodes(id),
                        dst_id INTEGER NOT NULL REFERENCES nodes(id),
                        relation_type TEXT NOT NULL,
                        edge_kind TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        line_no INTEGER NOT NULL,
                        symbol TEXT NOT NULL DEFAULT ''
                    )
                """)

                # Phase 1: Extended violations schema
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        edge_id INTEGER NOT NULL REFERENCES edges(id),
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        disposition_source TEXT DEFAULT '',
                        disposition_date TEXT DEFAULT '',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert test data
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (1, 'test::module', 'module', 'L0')")
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (2, 'test::symbol', 'symbol', 'L0')")
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 2, 'antipattern', 'silent_exception_swallow', 'test_file.py', 10, 'except:Exception')
                """)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', 'test_file.py', 10, 'HIGH')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_schema_extensions_exist(self, temp_adg_db: Path) -> None:
        """§1.1: New schema fields are present and correctly typed."""
        conn = sqlite3.connect(str(temp_adg_db))
        try:
            cursor = conn.execute("PRAGMA table_info(violations)")
            columns = {row[1] for row in cursor.fetchall()}

            # Phase 1 extensions must exist
            assert 'disposition' in columns
            assert 'disposition_source' in columns
            assert 'disposition_date' in columns
            assert 'severity' in columns

            # Check default values
            cursor = conn.execute("""
                SELECT disposition, disposition_source, disposition_date, severity
                FROM violations WHERE id = 1
            """)
            row = cursor.fetchone()
            assert row[0] == 'untriaged'  # disposition default
            assert row[1] == ''           # disposition_source default
            assert row[2] == ''           # disposition_date default
            assert row[3] == 'HIGH'       # severity set during insert

        finally:
            conn.close()


class TestGuardianSweepFixerADGIntegration:
    """§1.2: GuardianSweepFixer reads from ADG instead of JSON."""

    @pytest.fixture
    def sample_adg_with_violations(self) -> Generator[Path, None, None]:
        """Create ADG with sample antipattern violations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "sample_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Minimal schema for testing
                conn.execute("""
                    CREATE TABLE nodes (
                        id INTEGER PRIMARY KEY,
                        adg_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        layer TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src_id INTEGER NOT NULL REFERENCES nodes(id),
                        dst_id INTEGER NOT NULL REFERENCES nodes(id),
                        relation_type TEXT NOT NULL,
                        edge_kind TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        line_no INTEGER NOT NULL,
                        symbol TEXT NOT NULL DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        edge_id INTEGER NOT NULL REFERENCES edges(id),
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        disposition_source TEXT DEFAULT '',
                        disposition_date TEXT DEFAULT '',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert test violations
                violations_data = [
                    ('test_high.py', 5, 'except:ImportError', 'HIGH', 'untriaged', ''),
                    ('test_medium.py', 10, 'except:Exception', 'MEDIUM', 'untriaged', ''),
                    ('test_low.py', 15, 'except:SyntaxError', 'LOW', 'untriaged', ''),
                    ('test_approved.py', 20, 'except:ValueError', 'MEDIUM', 'approved', 'guardian: allow-silent-swallow'),
                    ('test_tested.py', 25, 'except:OSError', 'LOW', 'tested', 'test:test_exception_handler'),
                ]

                for i, (file, line, evidence, severity, disposition, source) in enumerate(violations_data, 1):
                    conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (?, ?, ?, ?)",
                               (i, f'test::node::{i}', 'module', 'L0'))
                    conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (?, ?, ?, ?)",
                               (i + 100, f'test::symbol::{i}', 'symbol', 'L0'))
                    conn.execute("""
                        INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (i, i, i + 100, 'antipattern', 'silent_exception_swallow', file, line, evidence))
                    conn.execute("""
                        INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition, disposition_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (i, 'antipattern', evidence, file, line, severity, disposition, source))

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_loads_from_adg_not_json(self, sample_adg_with_violations: Path) -> None:
        """§1.2: GuardianSweepFixer loads from ADG, not JSON file."""
        # Ensure JSON doesn't exist
        json_path = Path(__file__).parent.parent.parent / "tools" / "silent_swallower_report.json"
        json_existed = json_path.exists()
        if json_existed:
            json_path.rename(json_path.with_suffix('.json.bak'))

        try:
            fixer = GuardianSweepFixer(adg_path=sample_adg_with_violations)

            # Should load 3 untriaged violations (skip approved and tested)
            assert len(fixer.violations) == 3

            # Verify loaded data structure
            violation = fixer.violations[0]
            assert 'file_path' in violation
            assert 'line_number' in violation
            assert 'exception_type' in violation
            assert 'severity' in violation
            assert 'disposition' in violation
            assert 'disposition_source' in violation

            # Verify exception type parsing (check HIGH severity violation)
            high_severity_violation = next(v for v in fixer.violations if v['severity'] == 'HIGH')
            assert high_severity_violation['exception_type'] == 'ImportError'  # from "except:ImportError"
            assert high_severity_violation['severity'] == 'HIGH'
            assert high_severity_violation['disposition'] == 'untriaged'

        finally:
            # Restore JSON if it existed
            if json_existed:
                json_path.with_suffix('.json.bak').rename(json_path)

    def test_skip_already_dispositioned(self, sample_adg_with_violations: Path) -> None:
        """§1.4: Already dispositioned violations are skipped."""
        fixer = GuardianSweepFixer(adg_path=sample_adg_with_violations)

        # Should skip approved and tested violations
        assert fixer.skipped_guarded == 2

        # Only untriaged violations should be in the list
        for v in fixer.violations:
            assert v['disposition'] == 'untriaged'

    def test_no_adg_file_error_handling(self) -> None:
        """§1.6: Proper error handling when no ADG file exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create empty SQLite file (exists but no schema)
            empty_db = Path(tmp_dir) / "empty.sqlite"
            empty_db.touch()

            # Should fail with sqlite3 error, not crash
            with pytest.raises(sqlite3.OperationalError, match="no such table"):
                GuardianSweepFixer(adg_path=empty_db)


class TestDispositionUpdates:
    """§1.3: Disposition updates flow back to ADG."""

    @pytest.fixture
    def adg_with_test_file(self) -> Generator[tuple[Path, Path], None, None]:
        """Create ADG and corresponding test file for annotation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_adg.sqlite"
            test_file = Path(tmp_dir) / "test_file.py"

            # Create test file with violation
            test_file.write_text("""
def risky_operation():
    try:
        dangerous_call()
    except Exception:
        pass
""")

            # Create ADG
            conn = sqlite3.connect(str(db_path))
            try:
                conn.execute("""
                    CREATE TABLE nodes (
                        id INTEGER PRIMARY KEY,
                        adg_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        layer TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src_id INTEGER NOT NULL REFERENCES nodes(id),
                        dst_id INTEGER NOT NULL REFERENCES nodes(id),
                        relation_type TEXT NOT NULL,
                        edge_kind TEXT NOT NULL,
                        source_file TEXT NOT NULL,
                        line_no INTEGER NOT NULL,
                        symbol TEXT NOT NULL DEFAULT ''
                    )
                """)

                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        edge_id INTEGER NOT NULL REFERENCES edges(id),
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        disposition_source TEXT DEFAULT '',
                        disposition_date TEXT DEFAULT '',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert test data
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (1, 'test::module', 'module', 'L0')")
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (2, 'test::symbol', 'symbol', 'L0')")
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 2, 'antipattern', 'silent_exception_swallow', ?, 3, 'except:Exception')
                """, (str(test_file),))
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', ?, 3, 'MEDIUM')
                """, (str(test_file),))

                conn.commit()
            finally:
                conn.close()

            yield db_path, test_file

    def test_disposition_update_flow(self, adg_with_test_file: tuple[Path, Path]) -> None:
        """§1.3: Guardian annotation updates disposition in ADG."""
        db_path, test_file = adg_with_test_file

        fixer = GuardianSweepFixer(adg_path=db_path)

        # Verify initial state
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("""
                SELECT disposition, disposition_source, disposition_date
                FROM violations WHERE file_path = ? AND line_no = 3
            """, (str(test_file),))
            initial = cursor.fetchone()
            assert initial[0] == 'untriaged'
            assert initial[1] == ''
            assert initial[2] == ''
        finally:
            conn.close()

        # Apply guardian sweep
        result = fixer.apply_guardian_sweep()

        # Verify file was annotated
        content = test_file.read_text()
        assert "# guardian: allow-silent-swallow" in content

        # Verify ADG was updated
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("""
                SELECT disposition, disposition_source, disposition_date
                FROM violations WHERE file_path = ? AND line_no = 3
            """, (str(test_file),))
            updated = cursor.fetchone()
            assert updated[0] == 'approved'
            assert 'guardian: allow-silent-swallow' in updated[1]
            assert updated[2] != ''  # timestamp should be set
        finally:
            conn.close()

        # Verify result counts
        assert result['annotations_added'] == 1
        assert result['remaining_unannotated'] == 0


class TestDeterministicBehavior:
    """§1.7: Deterministic behavior across multiple runs."""

    @pytest.fixture
    def deterministic_adg(self) -> Generator[Path, None, None]:
        """Create deterministic ADG test data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "deterministic_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Schema
                for table in [
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, edge_id INTEGER NOT NULL REFERENCES edges(id), category TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0, disposition TEXT NOT NULL DEFAULT 'untriaged', disposition_source TEXT DEFAULT '', disposition_date TEXT DEFAULT '', severity TEXT NOT NULL DEFAULT 'MEDIUM')"
                ]:
                    conn.execute(table)

                # Deterministic test data
                test_data = [
                    ('deterministic.py', 5, 'except:ValueError', 'LOW'),
                    ('deterministic.py', 10, 'except:TypeError', 'MEDIUM'),
                    ('deterministic.py', 15, 'except:Exception', 'HIGH'),
                ]

                for i, (file, line, evidence, severity) in enumerate(test_data, 1):
                    conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (?, ?, ?, ?)",
                               (i, f'det::node::{i}', 'module', 'L0'))
                    conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (?, ?, ?, ?)",
                               (i + 100, f'det::symbol::{i}', 'symbol', 'L0'))
                    conn.execute("""
                        INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (i, i, i + 100, 'antipattern', 'silent_exception_swallow', file, line, evidence))
                    conn.execute("""
                        INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (i, 'antipattern', evidence, file, line, severity))

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_identical_input_identical_output(self, deterministic_adg: Path) -> None:
        """§1.7: Same ADG produces same violation list across multiple instances."""
        fixer1 = GuardianSweepFixer(adg_path=deterministic_adg)
        fixer2 = GuardianSweepFixer(adg_path=deterministic_adg)

        # Should load identical data
        assert len(fixer1.violations) == len(fixer2.violations) == 3

        # Each violation should be identical
        for v1, v2 in zip(fixer1.violations, fixer2.violations):
            assert v1['file_path'] == v2['file_path']
            assert v1['line_number'] == v2['line_number']
            assert v1['exception_type'] == v2['exception_type']
            assert v1['severity'] == v2['severity']
            assert v1['disposition'] == v2['disposition']

    def test_guardian_message_consistency(self, deterministic_adg: Path) -> None:
        """§1.7: Guardian messages are deterministic for same input."""
        fixer = GuardianSweepFixer(adg_path=deterministic_adg)

        # Same inputs should produce same messages
        msg1 = fixer._determine_guardian_message('ValueError', 'LOW', '')
        msg2 = fixer._determine_guardian_message('ValueError', 'LOW', '')
        assert msg1 == msg2
        assert 'ValueError is acceptable here' in msg1


class TestErrorHandlingAndRecovery:
    """§1.6 & §1.8: Error handling and fail-closed behavior."""

    def test_missing_adg_directory_fails_closed(self) -> None:
        """§1.8: Missing ADG directory fails with clear error."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Point to non-existent artifacts directory
            non_existent = Path(tmp_dir) / "non_existent" / "artifacts" / "adg"

            with patch('guardian_sweep.PROJECT_ROOT', Path(tmp_dir)):
                with pytest.raises(FileNotFoundError, match="No ADG SQLite found"):
                    GuardianSweepFixer()

    def test_corrupted_adg_handling(self) -> None:
        """§1.6: Handle corrupted ADG gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create invalid SQLite file
            corrupted_db = Path(tmp_dir) / "corrupted.sqlite"
            corrupted_db.write_text("not a sqlite database")

            # Should fail with sqlite3 error, not crash
            with pytest.raises(sqlite3.DatabaseError):
                GuardianSweepFixer(adg_path=corrupted_db)

    def test_file_not_found_handling(self) -> None:
        """§1.6: Handle missing source files gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_adg.sqlite"

            # Create ADG with violation pointing to non-existent file
            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, edge_id INTEGER NOT NULL REFERENCES edges(id), category TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0, disposition TEXT NOT NULL DEFAULT 'untriaged', disposition_source TEXT DEFAULT '', disposition_date TEXT DEFAULT '', severity TEXT NOT NULL DEFAULT 'MEDIUM')"
                ]:
                    conn.execute(table)

                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (1, 'test::module', 'module', 'L0')")
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (2, 'test::symbol', 'symbol', 'L0')")
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 2, 'antipattern', 'silent_exception_swallow', 'nonexistent.py', 5, 'except:Exception')
                """)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', 'nonexistent.py', 5, 'MEDIUM')
                """)

                conn.commit()
            finally:
                conn.close()

            # Should handle missing file gracefully
            fixer = GuardianSweepFixer(adg_path=db_path)
            result = fixer.apply_guardian_sweep()

            # Should not crash, should skip missing file
            assert result['annotations_added'] == 0
            assert result['errors'] == 0  # Missing files are not errors, just skipped


class TestEdgeCases:
    """§1.5: Edge case handling."""

    def test_empty_violations_table(self) -> None:
        """§1.5: Handle empty violations table."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, edge_id INTEGER NOT NULL REFERENCES edges(id), category TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0, disposition TEXT NOT NULL DEFAULT 'untriaged', disposition_source TEXT DEFAULT '', disposition_date TEXT DEFAULT '', severity TEXT NOT NULL DEFAULT 'MEDIUM')"
                ]:
                    conn.execute(table)
                conn.commit()
            finally:
                conn.close()

            fixer = GuardianSweepFixer(adg_path=db_path)
            assert len(fixer.violations) == 0
            assert fixer.skipped_guarded == 0

    def test_malformed_evidence_parsing(self) -> None:
        """§1.5: Handle malformed evidence gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "malformed_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                for table in [
                    "CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT NOT NULL, entity_type TEXT NOT NULL, layer TEXT NOT NULL)",
                    "CREATE TABLE edges (id INTEGER PRIMARY KEY AUTOINCREMENT, src_id INTEGER NOT NULL REFERENCES nodes(id), dst_id INTEGER NOT NULL REFERENCES nodes(id), relation_type TEXT NOT NULL, edge_kind TEXT NOT NULL, source_file TEXT NOT NULL, line_no INTEGER NOT NULL, symbol TEXT NOT NULL DEFAULT '')",
                    "CREATE TABLE violations (id INTEGER PRIMARY KEY AUTOINCREMENT, edge_id INTEGER NOT NULL REFERENCES edges(id), category TEXT NOT NULL, evidence TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '', line_no INTEGER NOT NULL DEFAULT 0, disposition TEXT NOT NULL DEFAULT 'untriaged', disposition_source TEXT DEFAULT '', disposition_date TEXT DEFAULT '', severity TEXT NOT NULL DEFAULT 'MEDIUM')"
                ]:
                    conn.execute(table)

                # Insert malformed evidence
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (1, 'test::module', 'module', 'L0')")
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer) VALUES (2, 'test::symbol', 'symbol', 'L0')")
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 2, 'antipattern', 'silent_exception_swallow', 'test.py', 5, 'malformed_evidence')
                """)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'malformed_evidence', 'test.py', 5, 'MEDIUM')
                """)

                conn.commit()
            finally:
                conn.close()

            fixer = GuardianSweepFixer(adg_path=db_path)

            # Should handle malformed evidence gracefully
            assert len(fixer.violations) == 1
            assert fixer.violations[0]['exception_type'] == 'Unknown'  # Fallback for malformed evidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
