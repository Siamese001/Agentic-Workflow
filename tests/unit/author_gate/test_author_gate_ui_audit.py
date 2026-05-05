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
        {
            "label": "⭐ Recommended — A",
            "description": (
                "[RECOMMENDED ⭐ confidence=0.90] · trade-off: "
                "Gains reversibility, loses coverage of L4 pattern"
            ),
        },
        {
            "label": "B",
            "description": "[confidence=0.70] · trade-off: Higher coverage but bigger blast radius",
        },
    ]
    response = _make_response(packet, options)
    assert ui_audit.audit_response(response) == []


def test_ui_audit_clean_when_surface_top_n_with_zero_stars(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {
            "label": "A",
            "description": "[confidence=0.77] · trade-off: Localized change, narrow test surface",
        },
        {
            "label": "B",
            "description": "[confidence=0.74] · trade-off: Cross-layer change, wider test surface",
        },
    ]
    response = _make_response(packet, options)
    assert ui_audit.audit_response(response) == []


def test_ui_audit_fails_on_missing_confidence_prefix(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "alpha without prefix · trade-off: still has tradeoff text here"},
        {"label": "B", "description": "[confidence=0.74] · trade-off: beta has the prefix and tradeoff"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "confidence_prefix_missing" for v in violations)


def test_ui_audit_fails_on_star_without_dominance(ui_audit):
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {
            "label": "A",
            "description": (
                "[RECOMMENDED ⭐ confidence=0.77] · trade-off: "
                "star applied without dominance verdict"
            ),
        },
        {
            "label": "B",
            "description": "[confidence=0.74] · trade-off: beta has the standard prefix",
        },
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "non_dominance_forbids_star" for v in violations)


def test_ui_audit_fails_on_multiple_stars(ui_audit):
    packet = {"routing": {"rule_applied": "dominance_fires"}, "decision_id": "dec_test"}
    options = [
        {
            "label": "A",
            "description": "[RECOMMENDED ⭐ confidence=0.90] · trade-off: first star with tradeoff",
        },
        {
            "label": "B",
            "description": "[RECOMMENDED ⭐ confidence=0.88] · trade-off: second star with tradeoff",
        },
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "multiple_stars" for v in violations)


def test_ui_audit_fails_when_dominance_missing_star(ui_audit):
    packet = {"routing": {"rule_applied": "dominance_fires"}, "decision_id": "dec_test"}
    options = [
        {
            "label": "A",
            "description": "[confidence=0.90] · trade-off: no star despite dominance verdict",
        },
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "dominance_requires_exactly_one_star" for v in violations)


def test_ui_audit_noop_when_no_ask_user_question(ui_audit):
    response = "Just some prose with AUTHOR_GATE_PACKET: {\"routing\": {\"rule_applied\": \"dominance_fires\"}}"
    assert ui_audit.audit_response(response) == []


# ------------------------------ UI audit invariant 4: tradeoff segment ------------------------------
# Plan author-gate-four-req-enforcement-c4d2a8 W2.P4 — close pros/cons gap.


def test_ui_audit_invariant4_passes_with_tradeoff_segment(ui_audit):
    """Description carrying ` · trade-off: <≥20 chars>` passes invariant 4."""
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {
            "label": "A",
            "description": "[confidence=0.80] · trade-off: Gains reversibility but loses test coverage",
        },
        {
            "label": "B",
            "description": "[confidence=0.74] · trade-off: Cheaper to ship but harder to roll back",
        },
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert all(v["invariant"] != "description_missing_tradeoff" for v in violations)


def test_ui_audit_invariant4_fails_when_tradeoff_segment_absent(ui_audit):
    """Description without any ` · trade-off:` segment fails invariant 4."""
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[confidence=0.80] just the prefix, no tradeoff segment"},
        {"label": "B", "description": "[confidence=0.74] · trade-off: B has the segment though"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    missing = [v for v in violations if v["invariant"] == "description_missing_tradeoff"]
    assert len(missing) == 1
    assert missing[0]["option_indices"] == [0]
    assert missing[0]["count"] == 1


def test_ui_audit_invariant4_fails_on_short_tradeoff(ui_audit):
    """Tradeoff body shorter than 20 non-whitespace chars fails invariant 4."""
    packet = {"routing": {"rule_applied": "surface_top_1"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[confidence=0.80] · trade-off: tbd"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "description_missing_tradeoff" for v in violations)


def test_ui_audit_invariant4_does_not_double_count_with_invariant1(ui_audit):
    """A description missing both prefix and tradeoff yields BOTH violations independently."""
    packet = {"routing": {"rule_applied": "surface_top_1"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "plain text without prefix or tradeoff"},
    ]
    response = _make_response(packet, options)
    violations = ui_audit.audit_response(response)
    invariants = {v["invariant"] for v in violations}
    assert "confidence_prefix_missing" in invariants
    assert "description_missing_tradeoff" in invariants


# ------------------------------ emit_packet floor + surface_description ------------------------------


def test_emit_packet_mints_surface_description_with_tradeoff_floor(emit):
    """Surfaced candidates carry surface_description containing the tradeoff floor."""
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "floor smoke",
        "candidates": [_cand("a", 0.90, "alpha"), _cand("b", 0.70, "beta")],
    }
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    surfaced = [c for c in packet["candidates"] if c.get("surfaced")]
    assert surfaced, "At least one candidate must be surfaced"
    for c in surfaced:
        floor = c.get("surface_description_floor")
        desc = c.get("surface_description")
        assert isinstance(floor, str) and floor.startswith("[")
        assert " · trade-off: " in floor
        assert isinstance(desc, str) and desc.startswith("[")
        assert " · trade-off: " in desc


def test_emit_packet_surface_description_extension_preserves_floor(emit):
    """When a caller supplies a custom surface_description, emitter prepends the floor."""
    extension = "author appends a longer rationale paragraph here"
    spec = {
        "decision_type": "refactor_scope",
        "normalized_intent": "extension test",
        "candidates": [
            {**_cand("a", 0.90, "alpha"), "surface_description": extension},
            _cand("b", 0.70, "beta"),
        ],
    }
    emit._fetch_precedent = lambda *a, **kw: {"verdict": "none", "matched_ids": [], "summary": ""}
    packet = emit.build_packet(spec)
    a = next(c for c in packet["candidates"] if c["id"] == "a")
    desc = a["surface_description"]
    assert desc.startswith("[")  # prefix preserved
    assert " · trade-off: " in desc
    assert extension in desc  # extension appended


# ------------------------------ UI audit invariant 5: handcrafted detection ------------------------------
# Plan author-gate-pre-response-guard-d3e8a1 W3.P1 — regression test corpus.


def test_invariant5_detects_handcrafted_ag_with_author_gate_word(ui_audit):
    """ask_user_question + 'Author-Gate' + no AUTHOR_GATE_PACKET → violation."""
    response = (
        "This is an Author-Gate decision point.\n"
        "ask_user_question with some options to choose from."
    )
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_detects_handcrafted_ag_with_ag_colon(ui_audit):
    """ask_user_question + 'AG:' + no packet → violation."""
    response = "AG: please pick an option.\nask_user_question is called here."
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_detects_handcrafted_ag_with_decision_point(ui_audit):
    """ask_user_question + 'decision point' + no packet → violation."""
    response = "Reached a decision point that requires user input.\nask_user_question"
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_no_violation_when_packet_present(ui_audit):
    """ask_user_question + Author-Gate words + AUTHOR_GATE_PACKET → no invariant5 violation."""
    packet = {"routing": {"rule_applied": "surface_top_2"}, "decision_id": "dec_test"}
    options = [
        {"label": "A", "description": "[confidence=0.80] · trade-off: tradeoff text here works"},
        {"label": "B", "description": "[confidence=0.74] · trade-off: another tradeoff here fine"},
    ]
    response = (
        f"Author-Gate decision.\n\nAUTHOR_GATE_PACKET: {json.dumps(packet)}\n\n"
        f'ask_user_question("options": {json.dumps(options)})'
    )
    violations = ui_audit.audit_response(response)
    assert all(v["invariant"] != "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_no_violation_when_no_ag_context_words(ui_audit):
    """ask_user_question without AG context words → no invariant5 violation."""
    response = "Please choose your favourite colour.\nask_user_question listed below."
    violations = ui_audit.audit_response(response)
    assert all(v["invariant"] != "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_no_violation_when_no_ask_user_question(ui_audit):
    """Author-Gate words without ask_user_question → no violation."""
    response = "This is an Author-Gate scenario but no tool call was made."
    violations = ui_audit.audit_response(response)
    assert all(v["invariant"] != "handcrafted_author_gate_detected" for v in violations)


def test_invariant5_matched_words_reported(ui_audit):
    """Violation record includes matched_context_words list."""
    response = "Author-Gate decision point.\nask_user_question here."
    violations = ui_audit.audit_response(response)
    inv5 = [v for v in violations if v["invariant"] == "handcrafted_author_gate_detected"]
    assert inv5
    assert "matched_context_words" in inv5[0]
    assert isinstance(inv5[0]["matched_context_words"], list)
    assert len(inv5[0]["matched_context_words"]) >= 1


def test_invariant5_severity_is_warn(ui_audit):
    """Invariant 5 violations carry severity=WARN (advisory only)."""
    response = "Author-Gate\nask_user_question"
    violations = ui_audit.audit_response(response)
    inv5 = [v for v in violations if v["invariant"] == "handcrafted_author_gate_detected"]
    assert inv5
    assert inv5[0]["severity"] == "WARN"


def test_invariant5_hitl_packet_word_triggers(ui_audit):
    """Legacy HITL_PACKET word (without canonical packet) triggers detection."""
    response = "HITL_PACKET scenario — ask_user_question called without proper packet."
    violations = ui_audit.audit_response(response)
    assert any(v["invariant"] == "handcrafted_author_gate_detected" for v in violations)


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
