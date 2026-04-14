"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py."""

from __future__ import annotations

import json


def test_module_importable():
    """Module archival_gatekeeper_gate must be importable."""
    from agentic_core.L5_safety.enforcement import archival_gatekeeper_gate

    assert archival_gatekeeper_gate is not None


def test_get_audit_log_returns_empty_when_file_absent(tmp_path):
    """get_audit_log must return [] when audit_log_path does not exist."""
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

    gk = ArchivalGatekeeper.__new__(ArchivalGatekeeper)
    gk.audit_log_path = tmp_path / "archival_audit.jsonl"
    result = gk.get_audit_log()
    assert result == []


def test_get_audit_log_limit_enforced_by_deque(tmp_path):
    """deque(maxlen=limit) must return at most `limit` entries, most-recent first."""
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

    gk = ArchivalGatekeeper.__new__(ArchivalGatekeeper)
    gk.audit_log_path = tmp_path / "archival_audit.jsonl"
    lines = "\n".join(json.dumps({"id": i}) for i in range(5)) + "\n"
    gk.audit_log_path.write_text(lines, encoding="utf-8")
    result = gk.get_audit_log(limit=3)
    assert len(result) == 3
    assert result[0]["id"] == 4


def test_get_audit_log_oversized_line_skipped(tmp_path):
    """Lines wider than 1 MiB must be silently skipped."""
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

    gk = ArchivalGatekeeper.__new__(ArchivalGatekeeper)
    gk.audit_log_path = tmp_path / "archival_audit.jsonl"
    valid_line = json.dumps({"id": 0}) + "\n"
    oversized_line = ("x" * (1024 * 1024 + 2)) + "\n"
    gk.audit_log_path.write_text(valid_line + oversized_line, encoding="utf-8")
    result = gk.get_audit_log()
    assert len(result) == 1
    assert result[0]["id"] == 0
