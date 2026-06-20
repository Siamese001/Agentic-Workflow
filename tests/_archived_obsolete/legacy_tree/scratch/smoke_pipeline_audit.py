#!/usr/bin/env python3
"""Temporary smoke test for post_agent_author_gate_pipeline_audit.py.
Delete after W5 verification."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT = REPO / ".codex" / "governance/scripts" / "_legacy_windsurf" / "post_agent_author_gate_pipeline_audit.py"
LOG = REPO / "artifacts" / "governance" / "author_gate_pipeline_violations.jsonl"


def _run(response_text: str) -> int:
    payload = json.dumps({"response": response_text})
    r = subprocess.run(
        [sys.executable, str(AUDIT)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return r.returncode


def _log_lines() -> list[dict]:
    if not LOG.exists():
        return []
    rows = []
    for line in LOG.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> int:
    # Clear log
    if LOG.exists():
        LOG.unlink()

    # --- Test 1: packet-only → violation ---
    packet_only = (
        "Analysis complete.\n"
        'AUTHOR_GATE_PACKET: {"decision_id": "SYNTH-001", '
        '"decision_type": "refactor_scope", "candidates": []}\n'
        "Done."
    )
    rc = _run(packet_only)
    assert rc == 0, f"Expected exit 0 (advisory), got {rc}"
    rows = _log_lines()
    assert len(rows) == 1, f"Expected 1 violation row, got {len(rows)}"
    row = rows[0]
    assert row["invariant"] == "packet_without_ask_user_question"
    assert row["severity"] == "critical"
    assert row["packet_count"] == 1
    assert "SYNTH-001" in row.get("packet_ids", [])
    print(f"✅ Test 1 PASS: violation logged — {json.dumps(row, ensure_ascii=False)}")

    # --- Test 2: packet + ask_user_question → compliant ---
    packet_and_ask = (
        'AUTHOR_GATE_PACKET: {"decision_id": "SYNTH-002", '
        '"decision_type": "refactor_scope", "candidates": []}\n'
        '<invoke name="ask_user_question">'
    )
    rc = _run(packet_and_ask)
    assert rc == 0
    rows2 = _log_lines()
    assert len(rows2) == 1, f"Expected still 1 row (no new), got {len(rows2)}"
    print("✅ Test 2 PASS: compliant response — no new violation row")

    # --- Test 3: empty response → clean ---
    rc = _run("")
    assert rc == 0
    rows3 = _log_lines()
    assert len(rows3) == 1, f"Expected still 1 row, got {len(rows3)}"
    print("✅ Test 3 PASS: empty response — no violation")

    print("\n🎯 All synthetic positive controls passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
