#!/usr/bin/env python3
"""test_drift_detector.py — Unit tests for _notion_drift_detector module."""
import pytest

from tools.notion._notion_drift_detector import (
    DriftEvent,
    DriftReport,
    DriftSeverity,
    DriftType,
    BatchDriftReport,
    check_plan_for_drift,
    check_plans_for_drift,
    detect_existence_drift,
    detect_property_drift,
    detect_status_drift,
)


class TestStatusDriftDetection:
    """Tests for status drift detection."""
    
    def test_no_drift_when_status_matches(self):
        result = detect_status_drift("test-plan", "In Progress", "In Progress", "page-123")
        assert result is None
    
    def test_detects_status_drift(self):
        result = detect_status_drift("test-plan", "In Progress", "Completed", "page-123")
        assert result is not None
        assert result.drift_type == DriftType.STATUS
        assert result.severity == DriftSeverity.TRIVIAL
        assert result.expected_value == "In Progress"
        assert result.actual_value == "Completed"
        assert result.auto_reconcilable is True
    
    def test_none_when_notion_missing(self):
        # Missing Notion row is handled by existence check
        result = detect_status_drift("test-plan", "In Progress", None, "page-123")
        assert result is None


class TestPropertyDriftDetection:
    """Tests for property drift detection."""
    
    def test_no_drift_when_property_matches(self):
        result = detect_property_drift(
            "test-plan", "Summary", "Expected summary", "Expected summary", "page-123"
        )
        assert result is None
    
    def test_detects_summary_drift(self):
        result = detect_property_drift(
            "test-plan", "Summary", "Expected", "Different", "page-123"
        )
        assert result is not None
        assert result.drift_type == DriftType.PROPERTY
        assert result.severity == DriftSeverity.MAJOR  # Summary is major
        assert result.auto_reconcilable is False
    
    def test_normalizes_whitespace(self):
        # Should treat None, empty, and whitespace-only as equivalent
        result = detect_property_drift(
            "test-plan", "Summary", None, "   ", "page-123"
        )
        assert result is None
    
    def test_ai_summary_trailing_space_property_name(self):
        # The actual property name has trailing space
        result = detect_property_drift(
            "test-plan", "AI Summary ", "Expected", "Different", "page-123"
        )
        assert result is not None
        assert result.property_name == "AI Summary "


class TestExistenceDriftDetection:
    """Tests for existence drift detection."""
    
    def test_no_drift_when_both_exist(self):
        result = detect_existence_drift("test-plan", True, True, "page-123")
        assert result is None
    
    def test_no_drift_when_both_missing(self):
        # Both missing is not necessarily drift
        result = detect_existence_drift("test-plan", False, False, "page-123")
        assert result is None
    
    def test_detects_extra_file(self):
        # File exists but no Notion row
        result = detect_existence_drift("test-plan", True, False, None)
        assert result is not None
        assert result.drift_type == DriftType.EXTRA_FILE
        assert result.severity == DriftSeverity.MAJOR
    
    def test_detects_missing_file(self):
        # Notion row exists but no file
        result = detect_existence_drift("test-plan", False, True, "page-123")
        assert result is not None
        assert result.drift_type == DriftType.MISSING_FILE
        assert result.severity == DriftSeverity.CRITICAL


class TestDriftEvent:
    """Tests for DriftEvent data class."""
    
    def test_to_dict_serialization(self):
        event = DriftEvent(
            drift_type=DriftType.STATUS,
            severity=DriftSeverity.TRIVIAL,
            page_id="page-123",
            slug="test-plan",
            property_name="Status",
            expected_value="In Progress",
            actual_value="Completed",
            message="Status drift detected",
            auto_reconcilable=True,
        )
        
        d = event.to_dict()
        assert d["drift_type"] == "STATUS"
        assert d["severity"] == "trivial"
        assert d["slug"] == "test-plan"
        assert d["auto_reconcilable"] is True


class TestDriftReport:
    """Tests for DriftReport."""
    
    def test_empty_report_has_no_drift(self):
        report = DriftReport(slug="test-plan")
        assert report.has_drift is False
        assert report.has_critical_drift is False
    
    def test_report_with_drift(self):
        report = DriftReport(slug="test-plan")
        report.drifts.append(DriftEvent(
            drift_type=DriftType.STATUS,
            severity=DriftSeverity.TRIVIAL,
            page_id="page-123",
            slug="test-plan",
        ))
        
        assert report.has_drift is True
        assert report.has_critical_drift is False
    
    def test_critical_drift_detection(self):
        report = DriftReport(slug="test-plan")
        report.drifts.append(DriftEvent(
            drift_type=DriftType.MISSING_FILE,
            severity=DriftSeverity.CRITICAL,
            page_id="page-123",
            slug="test-plan",
        ))
        
        assert report.has_critical_drift is True
    
    def test_auto_reconcilable_count(self):
        report = DriftReport(slug="test-plan")
        report.drifts.append(DriftEvent(
            drift_type=DriftType.STATUS,
            severity=DriftSeverity.TRIVIAL,
            page_id="page-123",
            slug="test-plan",
            auto_reconcilable=True,
        ))
        report.drifts.append(DriftEvent(
            drift_type=DriftType.PROPERTY,
            severity=DriftSeverity.MAJOR,
            page_id="page-123",
            slug="test-plan",
            auto_reconcilable=False,
        ))
        
        assert report.auto_reconcilable_count == 1


class TestCheckPlanForDrift:
    """Tests for check_plan_for_drift function."""
    
    def test_no_drift_when_all_match(self):
        disk_state = {
            "status": "In Progress",
            "file_exists": True,
        }
        notion_state = {
            "status": "In Progress",
        }
        
        report = check_plan_for_drift("test-plan", disk_state, notion_state, "page-123")
        
        assert report.has_drift is False
    
    def test_detects_status_and_property_drift(self):
        disk_state = {
            "status": "In Progress",
            "summary": "Expected summary",
            "file_exists": True,
        }
        notion_state = {
            "status": "Completed",
            "summary": "Different summary",
        }
        
        report = check_plan_for_drift("test-plan", disk_state, notion_state, "page-123")
        
        assert report.has_drift is True
        assert len(report.drifts) == 2  # Status + Summary
    
    def test_detects_missing_notion_row(self):
        disk_state = {
            "status": "In Progress",
            "file_exists": True,
        }
        notion_state = None
        
        report = check_plan_for_drift("test-plan", disk_state, notion_state, None)
        
        assert report.has_drift is True
        drift_types = [d.drift_type for d in report.drifts]
        assert DriftType.EXTRA_FILE in drift_types


class TestBatchDriftCheck:
    """Tests for check_plans_for_drift batch function."""
    
    def test_checks_multiple_plans(self):
        plan_states = {
            "plan-1": (
                {"status": "In Progress", "file_exists": True},
                {"status": "In Progress"},
                "page-1",
            ),
            "plan-2": (
                {"status": "Completed", "file_exists": True},
                {"status": "In Progress"},  # Drift!
                "page-2",
            ),
            "plan-3": (
                {"status": "Not Started", "file_exists": True},
                {"status": "Not Started"},
                "page-3",
            ),
        }
        
        batch = check_plans_for_drift(plan_states)
        
        assert batch.total_checked == 3
        assert batch.total_with_drift == 1
        assert "plan-2" in batch.reports
        assert batch.reports["plan-2"].has_drift is True
    
    def test_critical_drifts_property(self):
        plan_states = {
            "plan-1": (
                {"status": "In Progress", "file_exists": False},
                {"status": "In Progress"},
                "page-1",
            ),
        }
        
        batch = check_plans_for_drift(plan_states)
        
        assert len(batch.critical_drifts) == 1
        assert batch.critical_drifts[0].drift_type == DriftType.MISSING_FILE
