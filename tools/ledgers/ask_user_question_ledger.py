"""Ledger writeback for ASK_USER_QUESTION_PACKET decisions.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W3.

Extends refactor_decision_ledger.sqlite to accept non-gated decisions
with ASK_USER_QUESTION_PACKET telemetry.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REFACTOR_DECISION_LEDGER_DB


@dataclass
class AskUserQuestionDecision:
    """Record for an ask_user_question decision."""
    
    # Identity
    decision_id: str = field(default_factory=lambda: f"auq_{uuid.uuid4().hex[:16]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Classification
    decision_type: str = "enriched_choice"  # enriched_choice | data_collection | test_fixture
    context: str = ""  # telemetry context (e.g., "branch-resolution", "file-selection")
    
    # Question details
    question: str = ""
    option_count: int = 0
    recommended_index: int | None = None
    selected_index: int | None = None
    
    # Scoring
    confidence_source: str = "heuristic_default"  # explicit | heuristic_default
    confidence_score: float = 0.72
    
    # Raw packet for audit
    packet_json: str = ""
    
    # Context
    telemetry_context: str = ""
    invariants: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "created_at": self.created_at,
            "decision_type": self.decision_type,
            "context": self.context,
            "question": self.question,
            "option_count": self.option_count,
            "recommended_index": self.recommended_index,
            "selected_index": self.selected_index,
            "confidence_source": self.confidence_source,
            "confidence_score": self.confidence_score,
            "packet_json": self.packet_json,
            "telemetry_context": self.telemetry_context,
            "invariants": self.invariants,
        }


def ensure_schema() -> None:
    """Ensure ask_user_question_decisions table exists.
    
    Creates separate table to avoid schema conflicts with AUTHOR_GATE decisions.
    """
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(LEDGER_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ask_user_question_decisions (
                decision_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                decision_type TEXT NOT NULL DEFAULT 'enriched_choice',
                context TEXT,
                question TEXT,
                option_count INTEGER DEFAULT 0,
                recommended_index INTEGER,
                selected_index INTEGER,
                confidence_source TEXT DEFAULT 'heuristic_default',
                confidence_score REAL DEFAULT 0.72,
                packet_json TEXT,
                telemetry_context TEXT,
                invariants_json TEXT
            )
        """)
        
        # Indexes
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_auq_created 
            ON ask_user_question_decisions(created_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_auq_context 
            ON ask_user_question_decisions(context)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_auq_type 
            ON ask_user_question_decisions(decision_type)
        """)
        
        conn.commit()
    finally:
        conn.close()


def write_decision(
    packet: dict[str, Any],
    selected_index: int | None = None,
) -> str:
    """Write ASK_USER_QUESTION_PACKET to ledger.
    
    Args:
        packet: The ASK_USER_QUESTION_PACKET dict
        selected_index: Which option was selected (if known)
    
    Returns:
        decision_id of the written record
    
    Example:
        >>> packet = {
        ...     "packet_type": "ASK_USER_QUESTION_PACKET",
        ...     "context": "branch-resolution",
        ...     "timestamp": "2026-05-10T10:00:00+00:00",
        ...     "option_count": 2,
        ...     "recommended_index": 0,
        ...     "confidence_source": "heuristic_default",
        ...     "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
        ... }
        >>> decision_id = write_decision(packet, selected_index=0)
    """
    ensure_schema()
    
    decision = AskUserQuestionDecision(
        decision_id=packet.get("decision_id") or f"auq_{uuid.uuid4().hex[:16]}",
        created_at=packet.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        decision_type=packet.get("decision_type", "enriched_choice"),
        context=packet.get("context", ""),
        option_count=packet.get("option_count", 0),
        recommended_index=packet.get("recommended_index"),
        selected_index=selected_index,
        confidence_source=packet.get("confidence_source", "heuristic_default"),
        confidence_score=packet.get("confidence_score", 0.72),
        packet_json=json.dumps(packet),
        telemetry_context=packet.get("context", ""),
        invariants=packet.get("invariants", []),
    )
    
    conn = sqlite3.connect(LEDGER_PATH)
    try:
        conn.execute("""
            INSERT INTO ask_user_question_decisions (
                decision_id, created_at, decision_type, context, question,
                option_count, recommended_index, selected_index,
                confidence_source, confidence_score, packet_json,
                telemetry_context, invariants_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.decision_id,
            decision.created_at,
            decision.decision_type,
            decision.context,
            decision.question,
            decision.option_count,
            decision.recommended_index,
            decision.selected_index,
            decision.confidence_source,
            decision.confidence_score,
            decision.packet_json,
            decision.telemetry_context,
            json.dumps(decision.invariants),
        ))
        conn.commit()
        return decision.decision_id
    finally:
        conn.close()


def get_decision(decision_id: str) -> dict[str, Any] | None:
    """Retrieve a decision by ID."""
    if not LEDGER_PATH.exists():
        return None
    
    conn = sqlite3.connect(LEDGER_PATH)
    try:
        row = conn.execute(
            "SELECT * FROM ask_user_question_decisions WHERE decision_id = ?",
            (decision_id,)
        ).fetchone()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in conn.execute(
            "SELECT * FROM ask_user_question_decisions LIMIT 0"
        ).description]
        
        return dict(zip(columns, row))
    finally:
        conn.close()


def list_recent_decisions(
    context: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List recent decisions, optionally filtered by context."""
    if not LEDGER_PATH.exists():
        return []
    
    conn = sqlite3.connect(LEDGER_PATH)
    try:
        if context:
            rows = conn.execute(
                """SELECT * FROM ask_user_question_decisions 
                   WHERE context = ? 
                   ORDER BY created_at DESC LIMIT ?""",
                (context, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM ask_user_question_decisions 
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            ).fetchall()
        
        if not rows:
            return []
        
        columns = [desc[0] for desc in conn.execute(
            "SELECT * FROM ask_user_question_decisions LIMIT 0"
        ).description]
        
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def main() -> int:
    """CLI for testing ledger operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ASK_USER_QUESTION ledger operations")
    parser.add_argument("--write-test", action="store_true", help="Write a test record")
    parser.add_argument("--list", action="store_true", help="List recent decisions")
    parser.add_argument("--get", type=str, help="Get decision by ID")
    args = parser.parse_args()
    
    if args.write_test:
        test_packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "option_count": 2,
            "recommended_index": 0,
            "confidence_source": "heuristic_default",
            "confidence_score": 0.74,
            "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
        }
        decision_id = write_decision(test_packet, selected_index=0)
        print(f"Wrote test decision: {decision_id}")
        return 0
    
    if args.list:
        decisions = list_recent_decisions(limit=10)
        print(json.dumps(decisions, indent=2, default=str))
        return 0
    
    if args.get:
        decision = get_decision(args.get)
        if decision:
            print(json.dumps(decision, indent=2, default=str))
        else:
            print(f"Decision not found: {args.get}")
            return 1
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
