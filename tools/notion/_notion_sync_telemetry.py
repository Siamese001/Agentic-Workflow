#!/usr/bin/env python3
"""_notion_sync_telemetry.py — Sync telemetry emitter for Notion operations.

Records structured telemetry for every sync attempt, success, or failure.
Emits to artifacts/governance/sync_telemetry.jsonl per §24 deferred-scope capture.

Constitutional: §25 (MCP serialization), §36 (plan registration), §30 (capture health)
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from tools.notion._notion_circuit_breaker import CircuitBreaker, get_circuit_breaker
from tools.notion._notion_retry import RetryContext, RetryResult

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_LOG_PATH = REPO_ROOT / "artifacts" / "governance" / "sync_telemetry.jsonl"
LEDGER_DB_PATH = REPO_ROOT / "artifacts" / "governance" / "sync_health_ledger.sqlite"

# ---------------------------------------------------------------------------
# Telemetry event types
# ---------------------------------------------------------------------------

@dataclass
class SyncAttemptEvent:
    """Telemetry event for a sync attempt."""
    event_type: str = "sync_attempt"
    timestamp: float = field(default_factory=lambda: time.time())
    
    # Target
    slug: str = ""
    page_id: str | None = None
    database_id: str | None = None
    
    # Operation
    operation: str = ""  # wave_start, wave_complete, plan_complete, etc.
    trigger_source: str = ""
    
    # Result
    success: bool = False
    status_code: int | None = None
    latency_ms: float = 0.0
    retry_count: int = 0
    
    # Failure details
    failure_type: str | None = None
    error_message: str | None = None
    
    # Circuit breaker state
    circuit_state: str | None = None
    
    # Retry context (if applicable)
    retry_context: dict[str, Any] | None = None


@dataclass
class DriftDetectedEvent:
    """Telemetry event for drift detection."""
    event_type: str = "drift_detected"
    timestamp: float = field(default_factory=lambda: time.time())
    
    slug: str = ""
    page_id: str | None = None
    drift_type: str = ""  # STATUS, PROPERTY, EXISTENCE, etc.
    severity: str = ""  # trivial, minor, major, critical
    property_name: str | None = None
    expected_value: str | None = None
    actual_value: str | None = None
    auto_reconcilable: bool = False


@dataclass
class ReconciliationEvent:
    """Telemetry event for drift reconciliation."""
    event_type: str = "reconciliation"
    timestamp: float = field(default_factory=lambda: time.time())
    
    slug: str = ""
    drift_type: str = ""
    action: str = ""  # auto_reconciled, manual_reconciled, ignored, escalated
    success: bool = False
    error_message: str | None = None


@dataclass
class CircuitTransitionEvent:
    """Telemetry event for circuit breaker state transition."""
    event_type: str = "circuit_transition"
    timestamp: float = field(default_factory=lambda: time.time())
    
    circuit_name: str = ""
    old_state: str = ""
    new_state: str = ""
    trigger: str = ""  # failure_threshold, success_threshold, timeout, manual_reset


# Union type for all events
TelemetryEvent = SyncAttemptEvent | DriftDetectedEvent | ReconciliationEvent | CircuitTransitionEvent


# ---------------------------------------------------------------------------
# JSONL emitter
# ---------------------------------------------------------------------------

def _ensure_log_directory() -> None:
    """Ensure the telemetry log directory exists."""
    TELEMETRY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def emit_telemetry(event: TelemetryEvent) -> None:
    """Emit a telemetry event to the JSONL log.
    
    Fail-soft: logs errors but never raises.
    """
    try:
        _ensure_log_directory()
        
        event_dict = asdict(event)
        # Remove None values for compactness
        event_dict = {k: v for k, v in event_dict.items() if v is not None}
        
        with open(TELEMETRY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict, ensure_ascii=False) + "\n")
    except Exception:
        # Fail-soft: telemetry failure should not break sync
        pass


# ---------------------------------------------------------------------------
# SQLite ledger writer
# ---------------------------------------------------------------------------

def _ensure_ledger_schema() -> None:
    """Ensure the ledger database schema is initialized."""
    LEDGER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if not LEDGER_DB_PATH.exists():
        # Initialize schema from SQL file
        schema_path = REPO_ROOT / ".claude" / "schemas" / "sync_health_ledger.schema.sql"
        if schema_path.exists():
            conn = sqlite3.connect(str(LEDGER_DB_PATH))
            try:
                with open(schema_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            finally:
                conn.close()


def write_sync_attempt_to_ledger(event: SyncAttemptEvent) -> None:
    """Write a sync attempt to the SQLite ledger.
    
    Fail-soft: logs errors but never raises.
    """
    try:
        _ensure_ledger_schema()
        
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        try:
            conn.execute(
                """
                INSERT INTO sync_attempts (
                    timestamp, slug, page_id, database_id, operation,
                    status_code, latency_ms, retry_count, success,
                    failure_type, error_message, trigger_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.timestamp,
                    event.slug,
                    event.page_id,
                    event.database_id,
                    event.operation,
                    event.status_code,
                    event.latency_ms,
                    event.retry_count,
                    event.success,
                    event.failure_type,
                    event.error_message,
                    event.trigger_source,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        # Fail-soft: ledger failure should not break sync
        pass


def write_drift_to_ledger(event: DriftDetectedEvent) -> None:
    """Write a drift event to the SQLite ledger."""
    try:
        _ensure_ledger_schema()
        
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        try:
            conn.execute(
                """
                INSERT INTO drift_events (
                    detected_at, slug, page_id, drift_type, severity,
                    property_name, expected_value, actual_value, auto_reconcilable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug, drift_type, property_name) 
                WHERE reconciliation_action = 'pending'
                DO UPDATE SET
                    last_seen = excluded.detected_at,
                    occurrence_count = occurrence_count + 1
                """,
                (
                    event.timestamp,
                    event.slug,
                    event.page_id,
                    event.drift_type,
                    event.severity,
                    event.property_name,
                    event.expected_value,
                    event.actual_value,
                    event.auto_reconcilable,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


def write_circuit_transition_to_ledger(event: CircuitTransitionEvent) -> None:
    """Write a circuit breaker transition to the ledger."""
    try:
        _ensure_ledger_schema()
        
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        try:
            # Get circuit stats
            cb = get_circuit_breaker(event.circuit_name)
            context_json = json.dumps(cb.stats.to_dict())
            
            conn.execute(
                """
                INSERT INTO circuit_state_log (
                    timestamp, circuit_name, old_state, new_state, trigger, context_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.timestamp,
                    event.circuit_name,
                    event.old_state,
                    event.new_state,
                    event.trigger,
                    context_json,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Convenience functions for common patterns
# ---------------------------------------------------------------------------

def emit_sync_attempt(
    slug: str,
    operation: str,
    success: bool,
    page_id: str | None = None,
    status_code: int | None = None,
    latency_ms: float = 0.0,
    retry_result: RetryResult | None = None,
    failure_type: str | None = None,
    error_message: str | None = None,
    trigger_source: str = "wave_lifecycle_writer",
) -> None:
    """Convenience function to emit a sync attempt event.
    
    Records to both JSONL and SQLite ledger.
    """
    # Determine circuit state
    try:
        cb = get_circuit_breaker("notion_api")
        circuit_state = cb.state.name
    except Exception:
        circuit_state = None
    
    # Build retry context
    retry_context = None
    if retry_result:
        retry_context = retry_result.context.to_dict()
        if status_code is None and retry_result.context.last_status_code:
            status_code = retry_result.context.last_status_code
    
    event = SyncAttemptEvent(
        slug=slug,
        page_id=page_id,
        operation=operation,
        success=success,
        status_code=status_code,
        latency_ms=latency_ms,
        retry_count=retry_result.context.attempt if retry_result else 0,
        failure_type=failure_type,
        error_message=error_message,
        trigger_source=trigger_source,
        circuit_state=circuit_state,
        retry_context=retry_context,
    )
    
    emit_telemetry(event)
    write_sync_attempt_to_ledger(event)


def emit_drift_detected(
    slug: str,
    drift_type: str,
    severity: str,
    page_id: str | None = None,
    property_name: str | None = None,
    expected_value: str | None = None,
    actual_value: str | None = None,
    auto_reconcilable: bool = False,
) -> None:
    """Convenience function to emit a drift detected event."""
    event = DriftDetectedEvent(
        slug=slug,
        page_id=page_id,
        drift_type=drift_type,
        severity=severity,
        property_name=property_name,
        expected_value=expected_value,
        actual_value=actual_value,
        auto_reconcilable=auto_reconcilable,
    )
    
    emit_telemetry(event)
    write_drift_to_ledger(event)


def emit_circuit_transition(
    circuit_name: str,
    old_state: str,
    new_state: str,
    trigger: str,
) -> None:
    """Convenience function to emit a circuit breaker transition."""
    event = CircuitTransitionEvent(
        circuit_name=circuit_name,
        old_state=old_state,
        new_state=new_state,
        trigger=trigger,
    )
    
    emit_telemetry(event)
    write_circuit_transition_to_ledger(event)


def emit_reconciliation(
    slug: str,
    drift_type: str,
    action: str,
    success: bool,
    error_message: str | None = None,
) -> None:
    """Convenience function to emit a reconciliation event."""
    event = ReconciliationEvent(
        slug=slug,
        drift_type=drift_type,
        action=action,
        success=success,
        error_message=error_message,
    )
    
    emit_telemetry(event)


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_recent_sync_summary(hours: int = 24) -> dict[str, Any]:
    """Get a summary of recent sync activity from the ledger."""
    try:
        _ensure_ledger_schema()
        
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        try:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failures,
                    AVG(latency_ms) as avg_latency
                FROM sync_attempts
                WHERE timestamp >= julianday('now', ?)
                """,
                (f"-{hours} hours",),
            )
            
            row = cursor.fetchone()
            return {
                "period_hours": hours,
                "total_attempts": row[0] or 0,
                "successes": row[1] or 0,
                "failures": row[2] or 0,
                "avg_latency_ms": round(row[3], 2) if row[3] else 0,
                "success_rate": (
                    round(row[1] / row[0] * 100, 1) if row[0] else 0
                ),
            }
        finally:
            conn.close()
    except Exception as e:
        return {"error": str(e)}


def get_pending_drift_count() -> int:
    """Get count of pending drift events."""
    try:
        _ensure_ledger_schema()
        
        conn = sqlite3.connect(str(LEDGER_DB_PATH))
        try:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM drift_events
                WHERE reconciliation_action = 'pending'
                """
            )
            return cursor.fetchone()[0] or 0
        finally:
            conn.close()
    except Exception:
        return 0
