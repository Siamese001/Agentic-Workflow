"""Tests for post_cascade_author_gate_ui_audit.audit_response and emit_packet
star-gating on the dominance verdict."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".windsurf" / "scripts" / "post_cascade_author_gate_ui_audit.py"
EMIT_PATH = REPO_ROOT / ".windsurf" / "skills" / "author-gate-packet-builder" / "emit_packet.py"


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ui_audit():
    return _load("post_cascade_author_gate_ui_audit", HOOK_PATH)


@pytest.fixture(scope="module")
def emit():
    return _load("emit_packet", EMIT_PATH)


def _make_response(packet: dict, options: list[dict]) -> str:
    """Build a synthetic response string with AUTHOR_GATE_PACKET + ask_user_question."""
    packet_json = json.dumps(packet)
    opts_json = json.dumps(options)
    return (
        f'Some prose...\n\nAUTHOR_GATE_PACKET: {packet_json}\n\n'
        f'... more prose ... ask_user_question("options": {opts_json}) ...'
    )


# ------------------------------ emit_packet: star-gating ------------------------------


def test_emit_packet_star_only_when_dominance_fires(emit):
    """Top ≥ 0.85 AND gap ≥ 0.12 → exactly one starred option."""
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "test",
        "candidates": [
            _cand("a", 0.90, "alpha approach"),
            _cand("b", 0.70, "beta approach"),
        ],
    }
    # Bypass precedent to keep test hermetic
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    assert packet["routing"]["rule_applied"] == "dominance_fires"
    assert packet["recommended_option_id"] == "a"
    stars = [c for c in packet["candidates"] if c.get("is_recommended")]
    assert len(stars) == 1
    assert stars[0]["id"] == "a"
    assert stars[0]["surface_description_prefix"].startswith("[RECOMMENDED ⭐ confidence=0.90]")


def test_emit_packet_no_star_when_top_077_gap_003(emit):
    """The user's reported scenario: top=0.77 < 0.85 → no star anywhere."""
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "test",
        "candidates": [
            _cand("a", 0.77, "alpha"),
            _cand("b", 0.74, "beta"),
        ],
    }
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    assert packet["routing"]["rule_applied"].startswith("surface_top_")
    assert packet["recommended_option_id"] is None
    stars = [c for c in packet["candidates"] if c.get("is_recommended")]
    assert stars == []
    for c in packet["candidates"]:
        if c.get("surfaced"):
            assert c["surface_description_prefix"].startswith("[confidence=")
            assert "⭐" not in c["surface_description_prefix"]


def test_emit_packet_no_star_when_gap_below_012(emit):
    """Top ≥ 0.85 but gap < 0.12 → no dominance, no star."""
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "test",
        "candidates": [
            _cand("a", 0.88, "alpha"),
            _cand("b", 0.80, "beta"),  # gap = 0.08 < 0.12
        ],
    }
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    assert packet["routing"]["rule_applied"] != "dominance_fires"
    stars = [c for c in packet["candidates"] if c.get("is_recommended")]
    assert stars == []


def test_emit_packet_low_confidence_no_star(emit):
    """All < 0.72 → low_confidence_ambiguity, no star, nothing surfaced."""
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "test",
        "candidates": [
            _cand("a", 0.60, "alpha"),
            _cand("b", 0.55, "beta"),
        ],
    }
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    assert packet["routing"]["rule_applied"] == "low_confidence_ambiguity"
    stars = [c for c in packet["candidates"] if c.get("is_recommended")]
    assert stars == []


# ------------------------------ UI audit: three invariants ------------------------------


def test_ui_audit_clean_when_dominance_fires_with_one_star(ui_audit):
    packet = {"routing": {"rule_applied": "dominance_fires"}, "decision_id": "dec_test"}
    options = [
        {"label": "⭐ Recommended — A", "description": "[RECOMMENDED ⭐ confidence=0.90] alpha wins"},
        {"label": "B", "description": "[confidence=0.70] beta"},
    ]
    response = _make_response(packet, options)
    assert ui_audit.audit_response(response) == []


def test_ui_audit_clean_when_surface_top_n_with_zero_stars(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[confidence=0.77] alpha"},
        {"label": "B", "description": "[confidence=0.74] beta"},
    ]
    response = _make_response(packet, options)
    assert ui_audit.audit_response(response) == []


def test_ui_audit_fails_on_missing_confidence_prefix(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "alpha without prefix"},
        {"label": "B", "description": "[confidence=0.74] beta"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "confidence_prefix_missing" for v in violations)


def test_ui_audit_fails_on_star_without_dominance(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[RECOMMENDED ⭐ confidence=0.77] star without dominance"},
        {"label": "B", "description": "[confidence=0.74] beta"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "non_dominance_forbids_star" for v in violations)


def test_ui_audit_fails_on_multiple_stars(ui_audit):
    packet = {"routing": {"rule_applied": "dominance_fires"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[RECOMMENDED ⭐ confidence=0.90] first star"},
        {"label": "B", "description": "[RECOMMENDED ⭐ confidence=0.88] second star"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "multiple_stars" for v in violations)


def test_ui_audit_fails_when_dominance_missing_star(ui_audit):
    packet = {"routing": {"rule_applied": "dominance_fires"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[confidence=0.90] no star despite dominance"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "dominance_requires_exactly_one_star" for v in violations)


def test_ui_audit_noop_when_no_ask_user_question(ui_audit):
    response = "Just some prose with AUTHOR_GATE_PACKET: {\"routing\": {\"rule_applied\": \"dominance_fires\"}}"
    assert ui_audit.audit_response(response) == []


# ------------------------------ helpers ------------------------------


def _cand(cid: str, score: float, thesis: str) -> dict:
    return {
        "id": cid,
        "thesis": thesis,
        "confidence_score": score,
        "principle_at_stake": "layer gravity",
        "what_youd_miss": f"audit-visibility for {cid}",
        "what_would_flip": f"if blast radius exceeds 10 files for {cid}",
        "key_tradeoffs": ["Gains X but increases Y", "Gains P but increases Q"],
    }
