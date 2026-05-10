#!/usr/bin/env python3
"""_notion_drift_detector.py — Bidirectional drift detection for Notion sync.

Pure logic. No I/O at import. Safe to import from any hook or audit.

Detects three types of drift:
  1. Status drift: Notion Status ≠ expected from last marker
  2. Property drift: AI Summary, Summary, Waiting For changed externally
  3. Existence drift: Plan file on disk but Notion row missing (or vice versa)

Constitutional: §25 (MCP serialization), §36 (plan registration)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class DriftType(Enum):
    """Types of drift that can be detected."""
    STATUS = auto()          # Status mismatch
    PROPERTY = auto()        # Property value mismatch
    EXISTENCE = auto()       # Row exists in one place but not other
    MISSING_FILE = auto()    # Notion row exists but no file on disk
    EXTRA_FILE = auto()      # File on disk but no Notion row


class DriftSeverity(Enum):
    """Severity levels for drift."""
    TRIVIAL = "trivial"      # Auto-reconcilable
    MINOR = "minor"          # Low impact, can defer
    MAJOR = "major"          # Needs attention
    CRITICAL = "critical"    # Source of truth conflict


@dataclass(frozen=True)
class DriftEvent:
    """A single detected drift event."""
    drift_type: DriftType
    severity: DriftSeverity
    page_id: str | None
    slug: str
    property_name: str | None = None
    expected_value: str | None = None
    actual_value: str | None = None
    message: str = ""
    auto_reconcilable: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "drift_type": self.drift_type.name,
            "severity": self.severity.value,
            "page_id": self.page_id,
            "slug": self.slug,
            "property_name": self.property_name,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "message": self.message,
            "auto_reconcilable": self.auto_reconcilable,
        }


@dataclass
class DriftReport:
    """Complete drift report for a plan or batch."""
    slug: str
    drifts: list[DriftEvent] = field(default_factory=list)
    checked_at: float = 0.0
    
    @property
    def has_drift(self) -> bool:
        return len(self.drifts) > 0
    
    @property
    def has_critical_drift(self) -> bool:
        return any(d.severity == DriftSeverity.CRITICAL for d in self.drifts)
    
    @property
    def auto_reconcilable_count(self) -> int:
        return sum(1 for d in self.drifts if d.auto_reconcilable)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "has_drift": self.has_drift,
            "has_critical_drift": self.has_critical_drift,
            "auto_reconcilable_count": self.auto_reconcilable_count,
            "drifts": [d.to_dict() for d in self.drifts],
            "drift_count": len(self.drifts),
            "checked_at": self.checked_at,
        }


# Properties that can be auto-reconciled (trivial drift)
AUTO_RECONCILE_PROPERTIES = {"Status"}

# Properties that indicate manual external edits (need review)
MANUAL_EDIT_PROPERTIES = {"Summary", "AI Summary "}  # Note trailing space

# Critical properties (source of truth conflicts)
CRITICAL_PROPERTIES: set[str] = set()  # None currently defined


def detect_status_drift(
    slug: str,
    expected_status: str,
    notion_status: str | None,
    page_id: str | None = None,
) -> DriftEvent | None:
    """Detect if Notion status differs from expected.
    
    Args:
        slug: Plan slug
        expected_status: Expected status from disk/markers
        notion_status: Actual status in Notion (None if row missing)
        page_id: Notion page ID
    
    Returns:
        DriftEvent if drift detected, None otherwise
    """
    if notion_status is None:
        # Notion row doesn't exist - handled by existence check
        return None
    
    if expected_status == notion_status:
        return None
    
    # Status drift is auto-reconcilable
    return DriftEvent(
        drift_type=DriftType.STATUS,
        severity=DriftSeverity.TRIVIAL,
        page_id=page_id,
        slug=slug,
        property_name="Status",
        expected_value=expected_status,
        actual_value=notion_status,
        message=f"Status drift: expected '{expected_status}', found '{notion_status}'",
        auto_reconcilable=True,
    )


def detect_property_drift(
    slug: str,
    property_name: str,
    expected_value: str | None,
    notion_value: str | None,
    page_id: str | None = None,
) -> DriftEvent | None:
    """Detect if a property value differs from expected.
    
    Args:
        slug: Plan slug
        property_name: Property name
        expected_value: Expected value from disk (None if not tracked)
        notion_value: Actual value in Notion (None if empty)
        page_id: Notion page ID
    
    Returns:
        DriftEvent if drift detected, None otherwise
    """
    # Normalize None vs empty string
    expected = (expected_value or "").strip()
    actual = (notion_value or "").strip()
    
    if expected == actual:
        return None
    
    # Determine severity and reconcilability
    if property_name in AUTO_RECONCILE_PROPERTIES:
        severity = DriftSeverity.TRIVIAL
        auto_reconcile = True
    elif property_name in MANUAL_EDIT_PROPERTIES:
        severity = DriftSeverity.MAJOR
        auto_reconcile = False
    elif property_name in CRITICAL_PROPERTIES:
        severity = DriftSeverity.CRITICAL
        auto_reconcile = False
    else:
        severity = DriftSeverity.MINOR
        auto_reconcile = False
    
    return DriftEvent(
        drift_type=DriftType.PROPERTY,
        severity=severity,
        page_id=page_id,
        slug=slug,
        property_name=property_name,
        expected_value=expected,
        actual_value=actual,
        message=f"{property_name} drift: expected '{expected[:50]}...', found '{actual[:50]}...'",
        auto_reconcilable=auto_reconcile,
    )


def detect_existence_drift(
    slug: str,
    file_exists: bool,
    notion_exists: bool,
    page_id: str | None = None,
) -> DriftEvent | None:
    """Detect if plan file and Notion row are out of sync.
    
    Args:
        slug: Plan slug
        file_exists: Whether plan file exists on disk
        notion_exists: Whether Notion row exists
        page_id: Notion page ID
    
    Returns:
        DriftEvent if drift detected, None otherwise
    """
    if file_exists and notion_exists:
        return None
    
    if not file_exists and not notion_exists:
        # Both missing - not necessarily drift (could be archived/retired)
        return None
    
    if file_exists and not notion_exists:
        return DriftEvent(
            drift_type=DriftType.EXTRA_FILE,
            severity=DriftSeverity.MAJOR,
            page_id=page_id,
            slug=slug,
            message=f"Plan file exists on disk but no Notion row (slug: {slug})",
            auto_reconcilable=False,  # Requires registration
        )
    
    if notion_exists and not file_exists:
        return DriftEvent(
            drift_type=DriftType.MISSING_FILE,
            severity=DriftSeverity.CRITICAL,
            page_id=page_id,
            slug=slug,
            message=f"Notion row exists but no plan file on disk (slug: {slug})",
            auto_reconcilable=False,
        )
    
    return None


def check_plan_for_drift(
    slug: str,
    disk_state: dict[str, Any],
    notion_state: dict[str, Any] | None,
    page_id: str | None = None,
) -> DriftReport:
    """Check a plan for all types of drift.
    
    Args:
        slug: Plan slug
        disk_state: Dictionary of property values from disk
            - status: str
            - summary: str
            - ai_summary: str
            - file_exists: bool
        notion_state: Dictionary of property values from Notion (None if row missing)
            - status: str
            - summary: str
            - ai_summary: str
        page_id: Notion page ID
    
    Returns:
        DriftReport with all detected drifts
    """
    import time
    
    report = DriftReport(slug=slug, checked_at=time.time())
    
    file_exists = disk_state.get("file_exists", False)
    notion_exists = notion_state is not None
    
    # Check existence drift first
    existence_drift = detect_existence_drift(slug, file_exists, notion_exists, page_id)
    if existence_drift:
        report.drifts.append(existence_drift)
        # If row is missing, can't check other properties
        if not notion_exists:
            return report
    
    # Check status drift
    expected_status = disk_state.get("status", "Not Started")
    notion_status = notion_state.get("status") if notion_state else None
    status_drift = detect_status_drift(slug, expected_status, notion_status, page_id)
    if status_drift:
        report.drifts.append(status_drift)
    
    # Check property drifts for tracked properties
    tracked_properties = {
        "Summary": (disk_state.get("summary"), notion_state.get("summary") if notion_state else None),
        "AI Summary ": (disk_state.get("ai_summary"), notion_state.get("ai_summary") if notion_state else None),
    }
    
    for prop_name, (expected, actual) in tracked_properties.items():
        if expected is not None:  # Only check if we have expected value
            prop_drift = detect_property_drift(slug, prop_name, expected, actual, page_id)
            if prop_drift:
                report.drifts.append(prop_drift)
    
    return report


# ---------------------------------------------------------------------------
# Batch drift checking
# ---------------------------------------------------------------------------

@dataclass
class BatchDriftReport:
    """Drift report for multiple plans."""
    reports: dict[str, DriftReport] = field(default_factory=dict)
    total_checked: int = 0
    total_with_drift: int = 0
    total_auto_reconcilable: int = 0
    
    @property
    def all_drifts(self) -> list[DriftEvent]:
        """Flatten all drift events from all reports."""
        drifts = []
        for report in self.reports.values():
            drifts.extend(report.drifts)
        return drifts
    
    @property
    def critical_drifts(self) -> list[DriftEvent]:
        """All critical severity drift events."""
        return [d for d in self.all_drifts if d.severity == DriftSeverity.CRITICAL]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_checked": self.total_checked,
            "total_with_drift": self.total_with_drift,
            "total_auto_reconcilable": self.total_auto_reconcilable,
            "reports": {
                slug: report.to_dict()
                for slug, report in self.reports.items()
            },
        }


def check_plans_for_drift(
    plan_states: dict[str, tuple[dict[str, Any], dict[str, Any] | None, str | None]],
) -> BatchDriftReport:
    """Check multiple plans for drift.
    
    Args:
        plan_states: Dict mapping slug to (disk_state, notion_state, page_id)
    
    Returns:
        BatchDriftReport with all results
    """
    batch = BatchDriftReport()
    batch.total_checked = len(plan_states)
    
    for slug, (disk_state, notion_state, page_id) in plan_states.items():
        report = check_plan_for_drift(slug, disk_state, notion_state, page_id)
        batch.reports[slug] = report
        
        if report.has_drift:
            batch.total_with_drift += 1
            batch.total_auto_reconcilable += report.auto_reconcilable_count
    
    return batch
