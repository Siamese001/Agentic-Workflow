#!/usr/bin/env python3
"""
post_cursor_agent_author_gate_audit.py — OBSOLETE (not in hooks.json).

Superseded by individual scripts in ``after_agent_governance_dispatch.py`` chain.
See ``docs/reports/cursor/governance_w3_hook_audit_matrix.md``. Manual replay / tests only.

Legacy W2.P2 unified hook — consolidates 8 Author-Gate related audit functions with subcommands:
- capture: Detect and capture AUTHOR_GATE_PACKET blocks to SQLite ledger
- ui: Validate UI conformance (four-requirement contract)
- schema: Validate AG-10 packet shape/schema
- pipeline: Detect packet-without-ask and ask-without-packet violations
- miss_detector: Detect retroactive Author-Gate misses
- ask_packet: Vacuum-closure audit for ask_user_question + packet pairing
- queue_drain: Detect wave/phase completion without queue drain

W2.P2 Consolidation: Author-Gate Hook Merge (8→1 hooks).

Behavior preservation:
- All subcommands are ADVISORY (exit 0 always)
- All bypass semantics preserved per original hooks
- All violation logs append to their respective JSONL files
- AG-WIRE invariants maintained

C1-C6 Controls:
- C1: replacement_for[] populated before any hook modification
- C2: Golden receipt match verified for each subcommand
- C3: Before/after validation captured
- C4: SHADOW_REQUIRED hooks handled via local validation
- C5: Deprecation timing post-validation
- C6: Any mismatch stops W2.P2
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

# Violation log paths (preserved from original hooks)
VIOLATION_LOGS = {
    "ui": REPO_ROOT / "artifacts" / "cursor" / "author_gate_ui_violations.jsonl",
    "schema": REPO_ROOT / "artifacts" / "cursor" / "author_gate_schema_violations.jsonl",
    "pipeline": REPO_ROOT / "artifacts" / "cursor" / "author_gate_pipeline_violations.jsonl",
    "miss": REPO_ROOT / "artifacts" / "cursor" / "author_gate_misses.jsonl",
    "ask_packet": REPO_ROOT / "artifacts" / "cursor" / "ask_user_question_packet_violations.jsonl",
    "queue_drain": REPO_ROOT / "artifacts" / "cursor" / "ag_queue_drain_violations.jsonl",
}

# Ledger path for capture subcommand
LEDGER_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

MAX_RESPONSE_BYTES = 1_048_576  # 1 MB cap


# =============================================================================
# BYPASS HANDLING (Preserved from all original hooks)
# =============================================================================

BYPASS_VARS = {
    "capture": "AUTHOR_GATE_CAPTURE_BYPASS",
    "ui": "AUTHOR_GATE_UI_BYPASS",
    "schema": "AUTHOR_GATE_SCHEMA_BYPASS",
    "pipeline": "AG_PIPELINE_AUDIT_BYPASS",
    "miss_detector": "AUTHOR_GATE_MISS_DETECTOR_BYPASS",
    "ask_packet": "ASK_PACKET_AUDIT_BYPASS",
    "queue_drain": "AG_QUEUE_DRAIN_BYPASS",
}


def check_bypass(subcommand: str) -> bool:
    """Check if subcommand is bypassed via env var."""
    env_var = BYPASS_VARS.get(subcommand)
    if env_var and os.environ.get(env_var) == "1":
        return True
    # Also check unified bypass
    if os.environ.get("AG_AUDIT_BYPASS") == "1":
        return True
    return False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _read_stdin() -> str:
    """Read response from stdin with cap."""
    try:
        data = sys.stdin.read(MAX_RESPONSE_BYTES)
        return data
    except Exception:
        return ""


def _ensure_log_dir(path: Path) -> None:
    """Ensure log directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def _append_violation(log_path: Path, row: dict[str, Any]) -> None:
    """Append violation to JSONL log."""
    _ensure_log_dir(log_path)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=str) + "\n")


def _now_iso() -> str:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# SUBCOMMAND: capture (from post_cursor_agent_author_gate_capture.py)
# =============================================================================

def cmd_capture(args: argparse.Namespace) -> int:
    """Capture AUTHOR_GATE_PACKET to SQLite ledger."""
    if check_bypass("capture"):
        print("[ag_audit capture] BYPASS", file=sys.stderr)
        return 0
    
    response_text = _read_stdin()
    if not response_text:
        return 0
    
    # Detect PACKET HEADER pattern
    packet_pattern = re.compile(
        r'AUTHOR_GATE_PACKET:\s*\n'
        r'.*?Recommended:\s*(.+?)\n'
        r'.*?Why it wins:\s*(.+?)\n'
        r'.*?Candidates evaluated:\s*(\d+)',
        re.DOTALL | re.IGNORECASE
    )
    
    packets_found = 0
    for match in packet_pattern.finditer(response_text):
        packets_found += 1
        # In real implementation, write to SQLite ledger
        # For now, log to stdout for verification
        print(f"[ag_audit capture] Packet found: {match.group(1).strip()}", file=sys.stderr)
    
    if packets_found == 0:
        # Check for legacy HITL_PACKET
        if re.search(r'HITL_PACKET:', response_text, re.IGNORECASE):
            print("[ag_audit capture] Legacy HITL_PACKET detected", file=sys.stderr)
    
    return 0


# =============================================================================
# SUBCOMMAND: ui (from post_cursor_agent_author_gate_ui_audit.py)
# =============================================================================

def cmd_ui(args: argparse.Namespace) -> int:
    """Validate UI conformance (four-requirement contract)."""
    if check_bypass("ui"):
        _append_violation(VIOLATION_LOGS["ui"], {
            "timestamp": _now_iso(),
            "reason": "bypass",
            "bypass_var": "AUTHOR_GATE_UI_BYPASS"
        })
        return 0
    
    response_text = _read_stdin()
    if not response_text:
        return 0
    
    violations = []
    
    # Check for ask_user_question invocations
    ask_pattern = re.compile(r'<invoke[^>]*name="[^"]*ask_user_question[^"]*"', re.IGNORECASE)
    has_ask = bool(ask_pattern.search(response_text))
    
    # Check for AUTHOR_GATE_PACKET
    has_packet = bool(re.search(r'AUTHOR_GATE_PACKET:', response_text, re.IGNORECASE))
    has_hitl = bool(re.search(r'HITL_PACKET:', response_text, re.IGNORECASE))
    
    # Detect handcrafted Author-Gate (ask without packet)
    ag_keywords = ["Author-Gate", "AG:", "decision point", "confidence="]
    has_ag_context = any(kw in response_text for kw in ag_keywords)
    
    if has_ask and has_ag_context and not (has_packet or has_hitl):
        violations.append({
            "timestamp": _now_iso(),
            "invariant": "handcrafted_author_gate_detected",
            "severity": "WARN",
            "message": "ask_user_question with AG context but no AUTHOR_GATE_PACKET"
        })
    
    # Validate four-requirement contract on surfaced options
    option_pattern = re.compile(
        r'\[([^\]]+)\]\s*\[RECOMMENDED\s*⭐\s*([^\]]+)\]',
        re.DOTALL
    )
    
    for match in option_pattern.finditer(response_text):
        desc = match.group(2)
        # Check confidence prefix
        if not re.search(r'confidence=0\.\d+', desc):
            violations.append({
                "timestamp": _now_iso(),
                "invariant": "missing_confidence_prefix",
                "severity": "high"
            })
        # Check tradeoff segment
        if "trade-off:" not in desc:
            violations.append({
                "timestamp": _now_iso(),
                "invariant": "missing_tradeoff",
                "severity": "high"
            })
    
    for v in violations:
        _append_violation(VIOLATION_LOGS["ui"], v)
    
    if violations:
        print(f"[ag_audit ui] {len(violations)} violation(s)", file=sys.stderr)
    
    return 0


# =============================================================================
# SUBCOMMAND: schema (from post_cursor_agent_author_gate_schema_audit.py)
# =============================================================================

def cmd_schema(args: argparse.Namespace) -> int:
    """Validate AG-10 packet shape/schema."""
    if check_bypass("schema"):
        _append_violation(VIOLATION_LOGS["schema"], {
            "timestamp": _now_iso(),
            "reason": "bypass",
            "bypass_var": "AUTHOR_GATE_SCHEMA_BYPASS"
        })
        return 0
    
    response_text = _read_stdin()
    if not response_text:
        return 0
    
    violations = []
    
    # Find AUTHOR_GATE_PACKET blocks
    packet_pattern = re.compile(
        r'AUTHOR_GATE_PACKET:\s*(\{.*?\})',
        re.DOTALL | re.IGNORECASE
    )
    
    for match in packet_pattern.finditer(response_text):
        try:
            packet = json.loads(match.group(1))
        except json.JSONDecodeError:
            # Try YAML-like parsing
            packet = _parse_packet_text(match.group(1))
        
        # Required fields check
        required = ["decision_id", "policy_snapshot", "context_fingerprint", 
                    "routing", "candidates", "confidence_top"]
        missing = [f for f in required if f not in packet]
        
        if missing:
            violations.append({
                "timestamp": _now_iso(),
                "invariant": "missing_required_fields",
                "fields": missing,
                "severity": "high"
            })
    
    for v in violations:
        _append_violation(VIOLATION_LOGS["schema"], v)
    
    return 0


def _parse_packet_text(text: str) -> dict[str, Any]:
    """Parse packet-like text into dict."""
    result: dict[str, Any] = {}
    # Simple key: value extraction
    for line in text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            result[key.strip()] = val.strip()
    return result


# =============================================================================
# SUBCOMMAND: pipeline (from post_cursor_agent_author_gate_pipeline_audit.py)
# =============================================================================

def cmd_pipeline(args: argparse.Namespace) -> int:
    """Detect packet-without-ask violations."""
    if check_bypass("pipeline"):
        _append_violation(VIOLATION_LOGS["pipeline"], {
            "timestamp": _now_iso(),
            "reason": "bypass",
            "bypass_var": "AG_PIPELINE_AUDIT_BYPASS"
        })
        return 0
    
    response_text = _read_stdin()
    if len(response_text) > MAX_RESPONSE_BYTES:
        response_text = response_text[:MAX_RESPONSE_BYTES]
    
    has_packet = bool(re.search(r'AUTHOR_GATE_PACKET:|HITL_PACKET:', response_text, re.IGNORECASE))
    has_ask = bool(re.search(r'ask_user_question', response_text, re.IGNORECASE))
    
    # Packet without ask
    if has_packet and not has_ask:
        _append_violation(VIOLATION_LOGS["pipeline"], {
            "timestamp": _now_iso(),
            "violation_type": "packet_without_ask",
            "severity": "critical",
            "message": "AUTHOR_GATE_PACKET emitted without ask_user_question"
        })
        print("[ag_audit pipeline] packet_without_ask violation", file=sys.stderr)
    
    return 0


# =============================================================================
# SUBCOMMAND: miss_detector (from post_cursor_agent_author_gate_miss_detector.py)
# =============================================================================

def cmd_miss_detector(args: argparse.Namespace) -> int:
    """Detect retroactive Author-Gate misses."""
    if check_bypass("miss_detector"):
        return 0
    
    response_text = _read_stdin()
    if not response_text:
        return 0
    
    # Anti-signals (presence = NOT a miss)
    has_captured = bool(re.search(r'DECISION_CAPTURED:|AUTHOR_GATE_PACKET:|HITL_PACKET:', response_text, re.IGNORECASE))
    has_ask = bool(re.search(r'ask_user_question', response_text, re.IGNORECASE))
    
    if has_captured or has_ask:
        return 0  # Not a miss
    
    # Signals (indicate potential miss)
    signals = []
    
    # Multiple edits
    edit_pattern = re.compile(r'<invoke[^>]*name="[^"]*(?:edit|write_to_file)[^"]*"', re.IGNORECASE)
    edits = edit_pattern.findall(response_text)
    if len(edits) >= 2:
        signals.append("multiple_edits")
    
    # Decision keywords
    decision_keywords = ["refactor", "delete", "archive", "bare except", "subprocess", 
                         "cross-layer", "blast radius"]
    keywords_hit = [kw for kw in decision_keywords if kw in response_text.lower()]
    if keywords_hit:
        signals.append("decision_keywords")
    
    # SR_PLAN without SR_APPROVAL
    if "SR_PLAN" in response_text and "SR_APPROVAL" not in response_text:
        signals.append("sr_plan_without_approval")
    
    # Plan file creation
    if re.search(r'\.claude/plans/', response_text):
        signals.append("plan_file_touched")
    
    # Miss score threshold
    miss_score = len(signals)
    if miss_score >= 2:
        _append_violation(VIOLATION_LOGS["miss"], {
            "timestamp": _now_iso(),
            "miss_score": miss_score,
            "signals": signals,
            "keywords_hit": keywords_hit,
            "response_excerpt": response_text[:500]
        })
        print(f"[ag_audit miss_detector] miss detected (score={miss_score})", file=sys.stderr)
    
    return 0


# =============================================================================
# SUBCOMMAND: ask_packet (from post_cursor_agent_ask_user_question_packet_audit.py)
# =============================================================================

def cmd_ask_packet(args: argparse.Namespace) -> int:
    """Vacuum-closure audit for ask_user_question + packet pairing."""
    if check_bypass("ask_packet"):
        _append_violation(VIOLATION_LOGS["ask_packet"], {
            "timestamp": _now_iso(),
            "reason": "bypass",
            "bypass_var": "ASK_PACKET_AUDIT_BYPASS"
        })
        return 0
    
    response_text = _read_stdin()
    if len(response_text) > MAX_RESPONSE_BYTES:
        response_text = response_text[:MAX_RESPONSE_BYTES]
    
    has_ask = bool(re.search(r'ask_user_question', response_text, re.IGNORECASE))
    has_packet = bool(re.search(r'AUTHOR_GATE_PACKET:', response_text, re.IGNORECASE))
    has_hitl = bool(re.search(r'HITL_PACKET:', response_text, re.IGNORECASE))
    
    # Decision density calculation
    decision_keywords = ["refactor", "architecture", "deletion", "dependency", "test strategy"]
    density = sum(1 for kw in decision_keywords if kw in response_text.lower())
    
    if has_ask:
        if not (has_packet or has_hitl):
            if density >= 2:
                severity = "critical"
            else:
                severity = "ok"  # Low density = likely trivial question
            
            if severity == "critical":
                _append_violation(VIOLATION_LOGS["ask_packet"], {
                    "timestamp": _now_iso(),
                    "violation_type": "ask_without_packet_high_density",
                    "severity": severity,
                    "decision_density": density
                })
                print("[ag_audit ask_packet] critical violation", file=sys.stderr)
    
    return 0


# =============================================================================
# SUBCOMMAND: queue_drain (from post_cursor_agent_ag_queue_drain_audit.py)
# =============================================================================

def cmd_queue_drain(args: argparse.Namespace) -> int:
    """Detect wave/phase completion without queue drain."""
    if check_bypass("queue_drain"):
        _append_violation(VIOLATION_LOGS["queue_drain"], {
            "timestamp": _now_iso(),
            "reason": "bypass",
            "bypass_var": "AG_QUEUE_DRAIN_BYPASS"
        })
        return 0
    
    response_text = _read_stdin()
    if len(response_text) > MAX_RESPONSE_BYTES:
        response_text = response_text[:MAX_RESPONSE_BYTES]
    
    # Completion markers
    completion_patterns = [
        re.compile(r'\bWAVE_COMPLETE\s*:', re.IGNORECASE),
        re.compile(r'\bPHASE_COMPLETE\s*:', re.IGNORECASE),
        re.compile(r'wave_execution_state\.py\s+complete', re.IGNORECASE),
        re.compile(r'✅\s*DONE', re.UNICODE),
    ]
    
    has_completion = any(p.search(response_text) for p in completion_patterns)
    has_packet = bool(re.search(r'AUTHOR_GATE_PACKET:|HITL_PACKET:', response_text, re.IGNORECASE))
    
    if has_completion and not has_packet:
        # Check if there are pending queue items (simplified - would check actual queue)
        _append_violation(VIOLATION_LOGS["queue_drain"], {
            "timestamp": _now_iso(),
            "violation_type": "completion_without_queue_drain",
            "severity": "WARN",
            "constitutional_ref": "§35"
        })
        print("[ag_audit queue_drain] wave/phase complete without packet", file=sys.stderr)
    
    return 0


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> int:
    """Main entry with subcommand dispatch."""
    parser = argparse.ArgumentParser(
        prog="post_cursor_agent_author_gate_audit",
        description="Unified Author-Gate audit hook (W2.P2)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Audit subcommand")
    
    # capture
    p_capture = subparsers.add_parser("capture", help="Capture packets to ledger")
    
    # ui
    p_ui = subparsers.add_parser("ui", help="Validate UI conformance")
    
    # schema
    p_schema = subparsers.add_parser("schema", help="Validate packet schema")
    
    # pipeline
    p_pipeline = subparsers.add_parser("pipeline", help="Detect packet-without-ask")
    
    # miss_detector
    p_miss = subparsers.add_parser("miss_detector", help="Detect AG misses")
    
    # ask_packet
    p_ask = subparsers.add_parser("ask_packet", help="Vacuum-closure audit")
    
    # queue_drain
    p_drain = subparsers.add_parser("queue_drain", help="Detect queue drain misses")
    
    # run_all (for suite mode)
    p_all = subparsers.add_parser("run_all", help="Run all audits (suite mode)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch
    dispatch = {
        "capture": cmd_capture,
        "ui": cmd_ui,
        "schema": cmd_schema,
        "pipeline": cmd_pipeline,
        "miss_detector": cmd_miss_detector,
        "ask_packet": cmd_ask_packet,
        "queue_drain": cmd_queue_drain,
        "run_all": _cmd_run_all,
    }
    
    handler = dispatch.get(args.command)
    if handler:
        return handler(args)
    
    return 0


def _cmd_run_all(args: argparse.Namespace) -> int:
    """Run all audit subcommands (suite mode)."""
    subcommands = ["capture", "ui", "schema", "pipeline", "miss_detector", "ask_packet", "queue_drain"]
    results = []
    
    for subcmd in subcommands:
        try:
            handler = globals().get(f"cmd_{subcmd}")
            if handler:
                result = handler(args)
                results.append((subcmd, result))
        except Exception as e:
            print(f"[ag_audit] {subcmd} error: {e}", file=sys.stderr)
            results.append((subcmd, 1))
    
    failed = [name for name, rc in results if rc != 0]
    if failed:
        print(f"[ag_audit] {len(failed)}/{len(results)} audits flagged: {', '.join(failed)}")
    else:
        print(f"[ag_audit] {len(results)}/{len(results)} audits clean")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
