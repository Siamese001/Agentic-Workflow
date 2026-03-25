#!/usr/bin/env python3
"""
Phase 3.3 Tests: Intelligent disposition system with AI-assisted violation triage.

Tests per windsurfrules §1.1-§1.8 requirements:
- §1.1 Deterministic inputs/outputs
- §1.2 No external dependencies
- §1.3 No mutable global state
- §1.4 Idempotent operations
- §1.5 Edge case handling
- §1.6 Error handling and recovery
- §1.7 Deterministic behavior
- §1.8 Fail-closed error handling

Phase 3.3 validates:
1. AI-assisted violation triage and prioritization
2. Learning from manual disposition patterns
3. Context-aware risk assessment
4. Automated disposition recommendations
5. Continuous learning and feedback loops
"""

from __future__ import annotations

import sqlite3

# Import the modules we're testing
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentic_core" / "adg" / "processing"))
from phase3_intelligent_disposition import (
    DispositionClassifier,
    DispositionType,
    FeatureExtractor,
    IntelligentDispositionSystem,
    RiskLevel,
    ViolationFeatures,
    run_phase3_intelligent_disposition,
)


class TestFeatureExtractor:
    """§1.5 Edge case: Feature extraction handles various violation scenarios."""

    @pytest.fixture
    def extractor_adg_db(self) -> Generator[Path, None, None]:
        """Create ADG with test data for feature extraction."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "extractor_adg.sqlite"

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

                # Insert test data
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'test::module', 'module', 'L0', 'test_module.py', 1, 50)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'test::function', 'symbol', 'L0', 'test_module.py', 10, 20)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (3, 'test::test_func', 'symbol', 'tests', 'test_module_test.py', 5, 15)"
                )

                # Insert test coverage edge
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 3, 2, 'tests_execution_of', 'test_linkage', 'test_module_test.py', 8, 'test_function')
                """)

                # Insert violations
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'test_module.py', 15, 'HIGH', 'untriaged')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_extracts_basic_features(self, extractor_adg_db: Path) -> None:
        """§1.1: Extracts basic violation features correctly."""
        with FeatureExtractor(extractor_adg_db) as extractor:
            violation_data = {
                "file_path": "test_module.py",
                "line_no": 15,
                "evidence": "except:Exception",
                "severity": "HIGH",
            }

            features = extractor.extract_features(violation_data)

            assert features.file_path == "test_module.py"
            assert features.line_no == 15
            assert features.exception_type == "Exception"
            assert features.severity == "HIGH"
            assert features.module_name == "test_module"
            assert features.architectural_layer == "L0"

    def test_determines_architectural_layer(self) -> None:
        """§1.1: Determines architectural layer from file path."""
        with FeatureExtractor(Path("dummy.sqlite")) as extractor:
            # Test L0 layer
            features = extractor.extract_features(
                {
                    "file_path": "agentic_core/L0_routing/enforcement/test.py",
                    "line_no": 10,
                    "evidence": "except:ValueError",
                    "severity": "MEDIUM",
                }
            )
            assert features.architectural_layer == "L0"

            # Test L5 layer
            features = extractor.extract_features(
                {
                    "file_path": "agentic_core/L5_safety/types/test.py",
                    "line_no": 10,
                    "evidence": "except:TypeError",
                    "severity": "MEDIUM",
                }
            )
            assert features.architectural_layer == "L5"

    def test_calculates_impact_scores(self) -> None:
        """§1.1: Calculates business, security, and operational impact scores."""
        with FeatureExtractor(Path("dummy.sqlite")) as extractor:
            # High security impact
            features = extractor.extract_features(
                {
                    "file_path": "agentic_core/L5_safety/security/auth.py",
                    "line_no": 10,
                    "evidence": "except:Exception",
                    "severity": "HIGH",
                }
            )

            assert features.security_impact > 0.7
            assert features.business_criticality > 0.7
            assert features.operational_impact > 0.5

    def test_detects_guardian_comments(self) -> None:
        """§1.1: Detects guardian comments correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test_guardian.py"
            test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    except Exception:  # guardian: allow-silent-swallow - Security check
        pass
""")

            with FeatureExtractor(Path("dummy.sqlite")) as extractor:
                features = extractor.extract_features(
                    {
                        "file_path": str(test_file),
                        "line_no": 5,
                        "evidence": "except:Exception",
                        "severity": "MEDIUM",
                    }
                )

                assert features.has_guardian_comment is True

    def test_handles_missing_files_gracefully(self) -> None:
    """Test handles_missing_files_gracefully runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with handles_missing_files_gracefully
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions
            assert features.function_name is None
            assert features.has_guardian_comment is False


class TestDispositionClassifier:
    """§1.5 Edge case: Disposition classifier handles various patterns."""

    def test_initializes_rule_based_system(self) -> None:
        """§1.1: Initializes rule-based classification system."""
        classifier = DispositionClassifier()

        assert "approval_rules" in classifier.pattern_rules
        assert "escalation_rules" in classifier.pattern_rules
        assert "remediation_rules" in classifier.pattern_rules

        # Check that rules have required fields
        for rule in classifier.pattern_rules["approval_rules"]:
            assert "condition" in rule
            assert "disposition" in rule
            assert "confidence" in rule
            assert "reasoning" in rule

    def test_applies_approval_rules(self) -> None:
        """§1.3: Applies approval rules correctly."""
        classifier = DispositionClassifier()

        # Test guardian comment rule
        features_with_guardian = ViolationFeatures(
            file_path="test.py",
            line_no=10,
            exception_type="ValueError",
            severity="MEDIUM",
            architectural_layer="L3",
            module_name="test",
            function_name="test_func",
            has_guardian_comment=True,
            test_coverage=False,
            import_complexity=2,
            function_complexity=1,
            business_criticality=0.5,
            security_impact=0.3,
            operational_impact=0.4,
            historical_frequency=1,
            similar_violations_count=1,
        )

        recommendation = classifier.classify_violation(features_with_guardian)

        assert recommendation.suggested_disposition == DispositionType.APPROVED
        assert recommendation.confidence > 0.8
        assert "guardian comment" in recommendation.reasoning.lower()

    def test_applies_escalation_rules(self) -> None:
        """§1.3: Applies escalation rules correctly."""
        classifier = DispositionClassifier()

        # Test high security impact rule
        features_high_risk = ViolationFeatures(
            file_path="agentic_core/L5_safety/security/auth.py",
            line_no=10,
            exception_type="Exception",
            severity="HIGH",
            architectural_layer="L5",
            module_name="auth",
            function_name="validate_token",
            has_guardian_comment=False,
            test_coverage=False,
            import_complexity=5,
            function_complexity=3,
            business_criticality=0.9,
            security_impact=0.9,
            operational_impact=0.8,
            historical_frequency=5,
            similar_violations_count=2,
        )

        recommendation = classifier.classify_violation(features_high_risk)

        assert recommendation.suggested_disposition == DispositionType.ESCALATED
        assert recommendation.confidence > 0.7
        assert recommendation.risk_level == RiskLevel.CRITICAL

    def test_trains_from_historical_data(self) -> None:
        """§1.4: Trains classifier from historical disposition data."""
        classifier = DispositionClassifier()

        # Mock historical data
        historical_data = [
            {
                "disposition": "approved",
                "source": "guardian: allow-silent-swallow",
                "features": {
                    "has_guardian_comment": True,
                    "business_criticality": 0.5,
                    "security_impact": 0.3,
                },
            },
            {
                "disposition": "tested",
                "source": "test: test_function",
                "features": {"test_coverage": True, "business_criticality": 0.3, "security_impact": 0.2},
            },
            # Add more samples for learning
        ] * 10  # Repeat to meet minimum sample requirement

        classifier.train_from_historical_data(historical_data)

        assert classifier.model_trained is True
        assert len(classifier.feature_weights) > 0

    def test_generates_alternative_suggestions(self) -> None:
        """§1.5: Generates alternative disposition suggestions."""
        classifier = DispositionClassifier()

        features = ViolationFeatures(
            file_path="test.py",
            line_no=10,
            exception_type="ValueError",
            severity="MEDIUM",
            architectural_layer="L3",
            module_name="test",
            function_name="simple_func",
            has_guardian_comment=False,
            test_coverage=True,
            import_complexity=1,
            function_complexity=1,
            business_criticality=0.3,
            security_impact=0.2,
            operational_impact=0.3,
            historical_frequency=1,
            similar_violations_count=1,
        )

        recommendation = classifier.classify_violation(features)

        # Should have alternatives
        assert len(recommendation.alternative_suggestions) > 0

        # Check that untriaged is always an alternative
        alternative_dispositions = [alt[0] for alt in recommendation.alternative_suggestions]
        assert DispositionType.UNTRIAGED in alternative_dispositions


class TestIntelligentDispositionSystem:
    """§1.5 Edge case: Intelligent disposition system handles end-to-end scenarios."""

    @pytest.fixture
    def intelligent_adg_db(self) -> Generator[Path, None, None]:
        """Create ADG with comprehensive test data for intelligent disposition."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "intelligent_adg.sqlite"

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

                # Insert test data
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (1, 'test::module', 'module', 'L0', 'security_module.py', 1, 50)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (2, 'test::function', 'symbol', 'L0', 'security_module.py', 10, 20)"
                )
                conn.execute(
                    "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path, span_line, span_end_line) VALUES (3, 'test::test_func', 'symbol', 'tests', 'test_security.py', 5, 15)"
                )

                # Insert test coverage edge
                conn.execute("""
                    INSERT INTO edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
                    VALUES (1, 3, 2, 'tests_execution_of', 'test_linkage', 'test_security.py', 8, 'test_security_function')
                """)

                # Insert untriaged violations
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'security_module.py', 15, 'HIGH', 'untriaged')
                """)

                # Insert historical dispositions for training
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition, disposition_source, disposition_date)
                    VALUES (1, 'antipattern', 'except:ValueError', 'other_module.py', 20, 'MEDIUM', 'approved', 'guardian: allow-silent-swallow', '2024-01-01')
                """)

                conn.commit()
            finally:
                conn.close()

            yield db_path

    def test_analyzes_and_recommends_dispositions(self, intelligent_adg_db: Path) -> None:
        """§1.3: Analyzes violations and generates recommendations."""
        with IntelligentDispositionSystem(intelligent_adg_db) as system:
            results = system.analyze_and_recommend_dispositions()

            assert "recommendations" in results
            assert "summary" in results
            assert "training_data_size" in results
            assert "model_trained" in results

            # Should have recommendations
            assert len(results["recommendations"]) > 0

            # Check recommendation structure
            recommendation = results["recommendations"][0]
            assert "file_path" in recommendation
            assert "line_no" in recommendation
            assert "evidence" in recommendation
            assert "features" in recommendation
            assert "recommendation" in recommendation

            # Check recommendation content
            rec = recommendation["recommendation"]
            assert "suggested_disposition" in rec
            assert "confidence" in rec
            assert "reasoning" in rec
            assert "risk_level" in rec
            assert "priority_score" in rec
            assert "supporting_evidence" in rec
            assert "alternative_suggestions" in rec

    def test_generates_summary_statistics(self, intelligent_adg_db: Path) -> None:
        """§1.1: Generates comprehensive summary statistics."""
        with IntelligentDispositionSystem(intelligent_adg_db) as system:
            results = system.analyze_and_recommend_dispositions()
            summary = results["summary"]

            assert "total_recommendations" in summary
            assert "high_priority_count" in summary
            assert "high_confidence_count" in summary
            assert "disposition_breakdown" in summary
            assert "risk_level_breakdown" in summary
            assert "average_confidence" in summary
            assert "average_priority_score" in summary

            # Check that counts make sense
            assert summary["total_recommendations"] >= summary["high_priority_count"]
            assert summary["total_recommendations"] >= summary["high_confidence_count"]

    def test_handles_empty_database_gracefully(self) -> None:
        """§1.6: Handles empty or malformed database gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "empty_adg.sqlite"

            # Create empty database
            conn = sqlite3.connect(str(db_path))
            conn.close()

            with IntelligentDispositionSystem(db_path) as system:
                results = system.analyze_and_recommend_dispositions()

                # Should handle gracefully
                assert results["training_data_size"] == 0
                assert results["model_trained"] is False
                assert len(results["recommendations"]) == 0


class TestPhase3Integration:
    """§1.6 & §1.8: Integration tests with error handling."""

    def test_convenience_function(self) -> None:
        """§1.4: Convenience function works correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_adg.sqlite"

            # Create minimal ADG
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
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)
                conn.commit()
            finally:
                conn.close()

            # Should work without crashing
            results = run_phase3_intelligent_disposition(db_path)

            assert "recommendations" in results
            assert "summary" in results

    def test_idempotent_operations(self) -> None:
        """§1.4: Multiple runs produce consistent results."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "idempotent_adg.sqlite"

            # Create test ADG
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
                        disposition TEXT NOT NULL DEFAULT 'untriaged',
                        severity TEXT NOT NULL DEFAULT 'MEDIUM'
                    )
                """)

                # Insert test violation
                conn.execute("""
                    INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity, disposition)
                    VALUES (1, 'antipattern', 'except:Exception', 'test.py', 10, 'HIGH', 'untriaged')
                """)

                conn.commit()
            finally:
                conn.close()

            # Run multiple times
            results1 = run_phase3_intelligent_disposition(db_path)
            results2 = run_phase3_intelligent_disposition(db_path)

            # Should produce consistent results
            assert (
                results1["summary"]["total_recommendations"] == results2["summary"]["total_recommendations"]
            )

    def test_fail_closed_error_handling(self) -> None:
        """§1.8: Handles errors in fail-closed manner (returns empty, does not crash)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create corrupted database
            db_path = Path(tmp_dir) / "corrupted_adg.sqlite"
            db_path.write_text("corrupted data")

            # Fail-closed: should return empty results gracefully, not crash
            results = run_phase3_intelligent_disposition(db_path)
            assert results["training_data_size"] == 0
            assert results["model_trained"] is False
            assert len(results["recommendations"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
