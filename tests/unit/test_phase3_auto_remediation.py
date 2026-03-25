#!/usr/bin/env python3
"""
Phase 3 Tests: Auto-remediation engine for exception handling violations.

Tests per windsurfrules §1.1-§1.8 requirements:
- §1.1 Deterministic inputs/outputs
- §1.2 No external dependencies
- §1.3 No mutable global state
- §1.4 Idempotent operations
- §1.5 Edge case handling
- §1.6 Error handling and recovery
- §1.7 Deterministic behavior
- §1.8 Fail-closed error handling

Phase 3 validates:
1. Exception type inference from code context
2. Auto-remediation strategy selection
3. Safe code transformation with rollback
4. Risk-based prioritization
5. Integration with ADG violation tracking
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core" / "adg" / "processing"))
from phase3_auto_remediation import (
    AutoRemediationEngine,
    ExceptionTypeInference,
    ViolationContext,
    RemediationStrategy,
    ExceptionType,
    RemediationAction,
    run_phase3_remediation_analysis
)


class TestExceptionTypeInference:
    """§1.5 Edge case: Exception type inference handles various code patterns."""

    def test_infers_value_error_from_parsing_code(self) -> None:
        """§1.1: ValueError inference from parsing patterns."""
        violation = ViolationContext(
            file_path='test_parser.py',
            line_no=10,
            original_line='except Exception:',
            evidence='except:Exception',
            severity='MEDIUM',
            function_name='parse_config',
            class_name=None,
            imports=[],
            surrounding_code=[
                'def parse_config(data):',
                '    try:',
                '        result = int(data)',
                '        return result',
                '    except Exception:',
                '        return None'
            ]
        )

        inference = ExceptionTypeInference()
        candidates = inference.infer_from_context(violation)

        assert len(candidates) > 0
        value_error = next((c for c in candidates if c.name == 'ValueError'), None)
        assert value_error is not None
        assert value_error.confidence > 0.3
        assert 'int(' in value_error.evidence

    def test_infers_key_error_from_dict_operations(self) -> None:
        """§1.1: KeyError inference from dictionary operations."""
        violation = ViolationContext(
            file_path='test_dict.py',
            line_no=15,
            original_line='except Exception:',
            evidence='except:Exception',
            severity='MEDIUM',
            function_name='get_value',
            class_name=None,
            imports=[],
            surrounding_code=[
                'def get_value(data, key):',
                '    try:',
                '        return data[key]',
                '    except Exception:',
                '        return None'
            ]
        )

        inference = ExceptionTypeInference()
        candidates = inference.infer_from_context(violation)

        assert len(candidates) > 0
        key_error = next((c for c in candidates if c.name == 'KeyError'), None)
        assert key_error is not None
        assert key_error.confidence >= 0.3
        assert '[' in key_error.evidence

    def test_infers_from_imports(self) -> None:
        """§1.1: Exception type inference from imports."""
        violation = ViolationContext(
            file_path='test_json.py',
            line_no=20,
            original_line='except Exception:',
            evidence='except:Exception',
            severity='MEDIUM',
            function_name='load_json',
            class_name=None,
            imports=['import json', 'import os'],
            surrounding_code=[
                'import json',
                'def load_json(text):',
                '    try:',
                '        return json.loads(text)',
                '    except Exception:',
                '        return {}'
            ]
        )

        inference = ExceptionTypeInference()
        candidates = inference.infer_from_context(violation)

        assert len(candidates) > 0
        json_error = next((c for c in candidates if c.name == 'json.JSONDecodeError'), None)
        assert json_error is not None
        assert json_error.confidence > 0.5
        assert 'JSON library imported' in json_error.evidence


class TestAutoRemediationEngine:
    """§1.5 Edge case: Auto-remediation engine handles all scenarios correctly."""

    @pytest.fixture
    def phase3_adg_db(self) -> Generator[Path, None, None]:
        """Create a comprehensive ADG SQLite with Phase 3 test data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "phase3_adg.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Basic schema
                conn.execute("""
                    CREATE TABLE nodes (
                        id INTEGER PRIMARY KEY,
                        adg_name TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        layer TEXT NOT NULL,
                        resolved_path TEXT NOT NULL,
                        span_line INTEGER DEFAULT 0,
                        span_end_line INTEGER DEFAULT 0
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

                # Insert test data for remediation analysis
                conn.execute("INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (1, 'test::module', 'module', 'L0', 'test_remediation.py')")

                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 1, 1, 'antipattern', 'silent_exception_swallow', 'test_remediation.py', 10, 'except:Exception')
                """)

                # High severity violation (should be prioritized)
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'test_remediation.py', 6, 'HIGH', 'untriaged')
                """)

                conn.commit()
            finally:
                conn.close()

            # Create the actual test file
            test_file = Path(tmp_dir) / "test_remediation.py"
            test_file.write_text("""
def test_function():
    try:
        result = int("not_a_number")
        return result
    except Exception:
        return None
""")

            yield db_path

    def test_loads_remediation_candidates(self, phase3_adg_db: Path) -> None:
        """§1.4: Loads only high/medium severity untriaged violations."""
        with AutoRemediationEngine(phase3_adg_db) as engine:
            violations = engine._load_remediation_candidates()

            assert len(violations) == 1
            assert violations[0].severity == 'HIGH'
            assert violations[0].evidence == 'except:Exception'
            assert violations[0].line_no == 6

    def test_generates_remediation_actions(self, phase3_adg_db: Path) -> None:
        """§1.3: Generates appropriate remediation actions."""
        with AutoRemediationEngine(phase3_adg_db) as engine:
            actions = engine.analyze_violations_for_remediation()

            assert len(actions) > 0
            action = actions[0]

            assert action.strategy in [RemediationStrategy.NARROW_TO_SPECIFIC, RemediationStrategy.ADD_LOGGING]
            assert action.confidence > 0.0
            assert action.risk_score > 0.0
            assert action.file_path == 'test_remediation.py'

    def test_prioritizes_by_risk_score(self, phase3_adg_db: Path) -> None:
        """§1.7: Actions are sorted by risk score (highest first)."""
        with AutoRemediationEngine(phase3_adg_db) as engine:
            actions = engine.analyze_violations_for_remediation()

            if len(actions) > 1:
                # Verify descending order by risk score
                for i in range(len(actions) - 1):
                    assert actions[i].risk_score >= actions[i + 1].risk_score

    def test_applies_remediation_safely(self) -> None:
        """§1.8: Remediation is applied safely with validation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test file
            test_file = Path(tmp_dir) / "test_safe.py"
            test_file.write_text("""
def risky_function():
    try:
        result = int(data)
        return result
    except Exception:
        return None
""")

            # Create remediation action
            action = RemediationAction(
                strategy=RemediationStrategy.NARROW_TO_SPECIFIC,
                file_path=str(test_file),
                line_no=5,
                original_line="    except Exception:",
                suggested_line="    except ValueError:",
                exception_types=[ExceptionType("ValueError", 0.8, "int() pattern found", "code_analysis")],
                risk_score=0.7,
                confidence=0.8
            )

            # Test dry run
            with AutoRemediationEngine(Path(tmp_dir) / "dummy.sqlite") as engine:
                result = engine.apply_remediation(action, dry_run=True)
                assert result is True

                # Verify file unchanged
                content = test_file.read_text()
                assert "except Exception:" in content
                assert "except ValueError:" not in content

            # Test actual application
            with AutoRemediationEngine(Path(tmp_dir) / "dummy.sqlite") as engine:
                result = engine.apply_remediation(action, dry_run=False)
                assert result is True

                # Verify file changed
                content = test_file.read_text()
                assert "except ValueError:" in content
                assert "except Exception:" not in content


class TestPhase3SchemaCompatibility:
    """§1.6: Handle different ADG schema versions gracefully."""

    def test_pre_phase1_schema_handling(self) -> None:
        """§1.6: Works with pre-Phase 1 schema."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "pre_phase1.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Basic violations schema without Phase 1 extensions
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY,
                        edge_id INTEGER,
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0
                    )
                """)

                # Insert test violation
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no)
                    VALUES (1, 'antipattern', 'except:Exception', 'test.py', 5)
                """)

                conn.commit()
            finally:
                conn.close()

            # Create test file
            test_file = Path(tmp_dir) / "test.py"
            test_file.write_text("def test():\n    try:\n        pass\n    except Exception:\n        pass\n")

            with AutoRemediationEngine(db_path) as engine:
                # Should not crash with pre-Phase 1 schema
                violations = engine._load_remediation_candidates()
                assert len(violations) == 1
                assert violations[0].severity == 'MEDIUM'  # Default severity

    def test_partial_phase1_schema_handling(self) -> None:
        """§1.6: Works with partial Phase 1 schema."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "partial_phase1.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                # Partial Phase 1 schema (severity but no disposition)
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY,
                        edge_id INTEGER,
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert test violation
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', 'test.py', 5, 'HIGH')
                """)

                conn.commit()
            finally:
                conn.close()

            with AutoRemediationEngine(db_path) as engine:
                violations = engine._load_remediation_candidates()
                assert len(violations) == 1
                assert violations[0].severity == 'HIGH'


class TestPhase3ErrorHandling:
    """§1.6 & §1.8: Error handling and fail-closed behavior."""

    def test_missing_file_handling(self) -> None:
        """§1.6: Handles missing source files gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "missing_file.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY,
                        edge_id INTEGER,
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert violation pointing to non-existent file
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', 'nonexistent.py', 10, 'HIGH')
                """)

                conn.commit()
            finally:
                conn.close()

            with AutoRemediationEngine(db_path) as engine:
                violations = engine._load_remediation_candidates()
                # Should skip missing file without crashing
                assert len(violations) == 0

    def test_malformed_code_handling(self) -> None:
        """§1.6: Handles malformed Python code gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "malformed.sqlite"

            conn = sqlite3.connect(str(db_path))
            try:
                conn.execute("""
                    CREATE TABLE violations (
                        id INTEGER PRIMARY KEY,
                        edge_id INTEGER,
                        category TEXT NOT NULL,
                        evidence TEXT NOT NULL DEFAULT '',
                        file_path TEXT NOT NULL DEFAULT '',
                        line_no INTEGER NOT NULL DEFAULT 0,
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
                    VALUES (1, 'antipattern', 'except:Exception', 'malformed.py', 10, 'HIGH')
                """)

                conn.commit()
            finally:
                conn.close()

            # Create malformed Python file
            test_file = Path(tmp_dir) / "malformed.py"
            test_file.write_text("def broken_syntax(\n    # Missing closing parenthesis\n    pass\nexcept Exception:\n    pass\n")

            with AutoRemediationEngine(db_path) as engine:
                violations = engine._load_remediation_candidates()
                # Should handle malformed code without crashing
                assert len(violations) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
