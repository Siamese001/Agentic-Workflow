#!/usr/bin/env python3
"""Tests for DetectionSignal unified sensor interface."""

from pathlib import Path

from agentic_core.L0_maintenance.sensors.detection_signal import (
    DetectionSignal,
    FailureContext,
    ImpactAssessment,
    ImpactScope,
    Severity,
)


class TestDetectionSignal:
    """Test suite for DetectionSignal."""

    def test_creation_with_defaults(self):
        """Test signal creation with default values."""
        signal = DetectionSignal(signal_id="test-001")

        assert signal.signal_id == "test-001"
        assert signal.is_failure is True
        assert signal.severity == Severity.MEDIUM
        assert signal.confidence == 1.0

    def test_structured_failure_context(self):
        """Test structured failure context creation."""
        context = FailureContext(
            file_path=Path("agentic_core/test.py"),
            line_number=42,
            function_name="test_function",
            error_message="Import violation detected",
        )
        signal = DetectionSignal(
            signal_id="test-002",
            failure_context=context,
        )

        assert signal.failure_context.line_number == 42
        assert "Import violation" in signal.failure_context.error_message

    def test_severity_classification(self):
        """Test severity levels are properly ordered."""
        assert Severity.CRITICAL.value > Severity.HIGH.value
        assert Severity.HIGH.value > Severity.MEDIUM.value
        assert Severity.MEDIUM.value > Severity.LOW.value
        assert Severity.LOW.value > Severity.INFO.value

    def test_impact_assessment(self):
        """Test impact assessment with blast radius."""
        impact = ImpactAssessment(
            scope=ImpactScope.DOMAIN,
            affected_components=["apps_lic", "apps_rg"],
            estimated_blast_radius=50,
            recovery_complexity="medium",
        )
        signal = DetectionSignal(
            signal_id="test-003",
            severity=Severity.HIGH,
            impact=impact,
        )

        assert signal.impact.scope == ImpactScope.DOMAIN
        assert signal.impact.estimated_blast_radius == 50

    def test_risk_level_classification_critical(self):
        """Test critical severity always returns high risk."""
        signal = DetectionSignal(
            signal_id="test-004",
            severity=Severity.CRITICAL,
        )
        assert signal.classify_risk_level() == "high"

    def test_risk_level_classification_system_wide(self):
        """Test system-wide impact returns high risk."""
        signal = DetectionSignal(
            signal_id="test-005",
            severity=Severity.MEDIUM,
            impact=ImpactAssessment(scope=ImpactScope.SYSTEM_WIDE),
        )
        assert signal.classify_risk_level() == "high"

    def test_risk_level_classification_low(self):
        """Test low severity with isolated impact returns low risk."""
        signal = DetectionSignal(
            signal_id="test-006",
            severity=Severity.LOW,
            impact=ImpactAssessment(scope=ImpactScope.ISOLATED),
        )
        assert signal.classify_risk_level() == "low"

    def test_to_dict_serialization(self):
        """Test signal serialization to dictionary."""
        signal = DetectionSignal(
            signal_id="test-007",
            source_sensor="location_agent",
            detection_type="naming_violation",
        )
        data = signal.to_dict()

        assert data["signal_id"] == "test-007"
        assert data["source_sensor"] == "location_agent"
        assert "timestamp" in data
        assert "failure_context" in data

    def test_auto_fixable_flag(self):
        """Test auto-fixable detection signals."""
        signal = DetectionSignal(
            signal_id="test-008",
            is_auto_fixable=True,
            suggested_fix="Rename file to match PascalCase convention",
        )

        assert signal.is_auto_fixable is True
        assert "PascalCase" in signal.suggested_fix

    def test_confidence_scoring(self):
        """Test confidence scoring for validator agent."""
        signal = DetectionSignal(
            signal_id="test-009",
            confidence=0.85,
        )
        assert 0.0 <= signal.confidence <= 1.0


class TestFailureContext:
    """Test suite for FailureContext."""

    def test_to_dict(self):
        """Test failure context serialization."""
        context = FailureContext(
            file_path=Path("test.py"),
            line_number=10,
            error_message="Test error",
        )
        data = context.to_dict()

        assert data["line_number"] == 10
        assert data["error_message"] == "Test error"

    def test_related_files(self):
        """Test related files tracking."""
        context = FailureContext(
            file_path=Path("main.py"),
            related_files=[Path("helper.py"), Path("utils.py")],
        )

        assert len(context.related_files) == 2


class TestImpactAssessment:
    """Test suite for ImpactAssessment."""

    def test_to_dict(self):
        """Test impact assessment serialization."""
        impact = ImpactAssessment(
            scope=ImpactScope.COMPONENT,
            estimated_blast_radius=25,
        )
        data = impact.to_dict()

        assert data["scope"] == "component"
        assert data["estimated_blast_radius"] == 25

    def test_downstream_dependencies(self):
        """Test downstream dependency tracking."""
        impact = ImpactAssessment(
            downstream_dependencies=["service_a", "service_b"],
        )

        assert len(impact.downstream_dependencies) == 2
