"""Smoke tests for the canonical author_gate_packet.schema.json.

Plan: author-gate-ssot-consolidation-b7c3e1 W1.2.
Verifies:
  - schema file loads as valid JSON
  - jsonschema lib is available and Draft 2020-12 compatible
  - 3 valid fixtures pass
  - 1 invalid fixture fails (missing routing)
  - emit_packet.build_packet output validates (zero-regression guarantee)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.author_gate.schema_loader import (  # noqa: E402
    SCHEMA_PATH,
    is_valid,
    load_schema,
    validate,
)

FIXTURES = REPO_ROOT / ".cursor" / "schemas" / "fixtures"


def _load(name: str) -> dict:
    with (FIXTURES / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def test_schema_file_exists_and_loads():
    assert SCHEMA_PATH.exists(), f"schema not found at {SCHEMA_PATH}"
    schema = load_schema()
    assert schema["$id"].endswith("author_gate_packet.schema.json")
    assert schema["type"] == "object"
    assert "decision_id" in schema["required"]
    assert "routing" in schema["required"]


def test_jsonschema_lib_available():
    """W1.2 — jsonschema must be importable."""
    import jsonschema  # noqa: F401


@pytest.mark.parametrize(
    "fixture",
    [
        "author_gate_packet.dominance_fires.json",
        "author_gate_packet.surface_top_n.json",
        "author_gate_packet.low_confidence.json",
    ],
)
def test_valid_fixtures_pass(fixture: str):
    packet = _load(fixture)
    findings = validate(packet)
    assert not findings, f"{fixture} should be valid; got: {findings}"
    assert is_valid(packet)


def test_invalid_fixture_fails_missing_routing():
    packet = _load("author_gate_packet.invalid_missing_routing.json")
    findings = validate(packet)
    assert findings, "invalid fixture must report at least one finding"
    paths = {f.get("path") for f in findings}
    # routing is required at top level → finding path is "<root>"
    assert any("routing" in (str(f.get("message", ""))) for f in findings) or "<root>" in paths


def test_emit_packet_output_validates():
    """Zero-regression: a real emit_packet.build_packet() output validates."""
    sys.path.insert(0, str(REPO_ROOT / ".cursor" / "skills" / "author-gate-packet-builder"))
    import emit_packet  # type: ignore

    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "smoke test",
        "files_in_scope": ["x.py"],
        "candidates": [
            {
                "id": "a",
                "thesis": "do thing",
                "confidence_score": 0.91,
                "key_tradeoffs": ["t1", "t2"],
                "what_youd_miss": "miss",
                "what_would_flip": "flip if blast crosses L5",
                "principle_at_stake": "reversibility",
            },
            {
                "id": "b",
                "thesis": "do thing differently",
                "confidence_score": 0.70,
                "key_tradeoffs": ["t1", "t2"],
                "what_youd_miss": "miss",
                "what_would_flip": "flip if hotspot rank improves",
                "principle_at_stake": "SSOT",
            },
        ],
    }
    # Avoid precedent subprocess in test
    emit_packet._fetch_precedent = lambda *a, **kw: {  # type: ignore
        "verdict": "none",
        "matched_ids": [],
        "summary": "skipped",
    }
    packet = emit_packet.build_packet(spec)
    findings = validate(packet)
    # Filter out schema_lib_missing (test should fail loud if lib gone)
    assert all(f["invariant"] != "schema_lib_missing" for f in findings)
    assert not findings, f"emit_packet output failed schema: {findings}"
