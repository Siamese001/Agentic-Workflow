"""E2E causal tests for the Author-Gate meta-learning Arrow-2 closure.

Plan: docs/archive/windsurf/legacy-tree/plans/author-gate-bandit-arrow2-closure-d7c4e9.md

Proves:
    bandit_state.json
      -> emit_packet._load_bandit_prior()
      -> AUTHOR_GATE_PACKET proof fields (bandit_prior, confidence_source,
         causal_use_receipt)
      -> Packet C (bandit-informed) differs from Packet B (precedent-only)

Test inventory (10):
    A/B/C scenario tests (3)
    Causal diff assertion (1)
    Fallback safety tests (6)
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

# ---------------------------------------------------------------------------
# Module loaders
# ---------------------------------------------------------------------------

def _import(rel_path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    assert spec and spec.loader, rel_path
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Shared DDL (mirrors test_lookup_refactor_decisions.py schema)
# ---------------------------------------------------------------------------

_DDL = """\
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS decisions (
    decision_id           TEXT PRIMARY KEY,
    created_at            TEXT NOT NULL,
    branch                TEXT,
    commit_sha            TEXT,
    task_id               TEXT,
    decision_type         TEXT NOT NULL DEFAULT 'unknown',
    reason_code           TEXT,
    request_summary       TEXT,
    normalized_intent     TEXT,
    user_goal             TEXT,
    constraints_json      TEXT,
    risk_profile_json     TEXT,
    blast_radius_estimate TEXT,
    options_json          TEXT,
    recommended_option_id TEXT,
    selected_option_id    TEXT,
    selection_rationale   TEXT,
    status                TEXT NOT NULL DEFAULT 'surfaced'
);

CREATE TABLE IF NOT EXISTS decision_scope (
    scope_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
    file_path   TEXT,
    symbol_name TEXT,
    symbol_kind TEXT,
    layer       TEXT,
    repo_area   TEXT,
    tags        TEXT
);

CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id           TEXT NOT NULL REFERENCES decisions(decision_id),
    execution_completed   INTEGER DEFAULT 0,
    tests_passed          INTEGER DEFAULT 0,
    regression_found      INTEGER DEFAULT 0,
    rollback_required     INTEGER DEFAULT 0,
    followup_decision_id  TEXT,
    promote_to_pattern    INTEGER DEFAULT 0,
    outcome_notes         TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(
    decision_id       UNINDEXED,
    normalized_intent,
    request_summary,
    user_goal,
    selection_rationale,
    content=decisions,
    content_rowid=rowid
);
"""

_NOW = "2026-05-04T00:00:00+00:00"


def _make_seeded_ledger(tmp_path: Path) -> Path:
    """Create ledger.sqlite with 3 refactor_scope rows + outcomes.

    dec_s1: promote=1, rollback=0, regression=0  -> success
    dec_s2: promote=1, rollback=0, regression=0  -> success
    dec_s3: promote=0, rollback=1, regression=0  -> failure

    All with reason_code='override_recommendation'.
    Expected bandit state after --apply:
        key  = 'refactor_scope|override_recommendation'
        alpha = 1 (prior) + 2 (successes) = 3.0
        beta  = 1 (prior) + 1 (failure)  = 2.0
    """
    db = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(_DDL)
    for did, promote, rollback in [
        ("dec_s1", 1, 0),
        ("dec_s2", 1, 0),
        ("dec_s3", 0, 1),
    ]:
        conn.execute(
            "INSERT INTO decisions (decision_id, created_at, decision_type, reason_code, status) "
            "VALUES (?,?,?,?,?)",
            (did, _NOW, "refactor_scope", "override_recommendation", "executed"),
        )
        conn.execute(
            "INSERT INTO decision_outcomes "
            "(decision_id, execution_completed, tests_passed, regression_found, rollback_required, promote_to_pattern) "
            "VALUES (?,1,1,0,?,?)",
            (did, rollback, promote),
        )
        conn.execute(
            "INSERT INTO decisions_fts (decision_id, normalized_intent) VALUES (?,?)",
            (did, "extract bandit test"),
        )
    conn.commit()
    conn.close()
    return db


# Minimal valid spec for build_packet
_SPEC: dict[str, Any] = {
    "decision_type": "refactor_scope",
    "normalized_intent": "extract bandit test",
    "reason_code": "override_recommendation",
    "files_in_scope": [],
    "candidates": [
        {
            "id": "minimal",
            "thesis": "smallest change",
            "confidence_score": 0.80,
            "principle_at_stake": "test",
            "what_youd_miss": "nothing",
            "what_would_flip": "blast_radius > 5",
            "key_tradeoffs": ["risk of rework", "scope creep"],
        }
    ],
}


def _build_packet_with_mocks(
    tmp_path: Path,
    bandit_state_path: Path,
    precedent_verdict: str = "none",
) -> dict[str, Any]:
    """Import emit_packet, patch BANDIT_STATE_PATH and _fetch_precedent, call build_packet."""
    mod_name = f"emit_packet_under_test_{id(tmp_path)}"
    ep = _import(
        ".cursor/skills/author-gate-packet-builder/emit_packet.py",
        mod_name,
    )
    # Patch BANDIT_STATE_PATH to point to tmp_path file
    ep.BANDIT_STATE_PATH = bandit_state_path

    # Stub _fetch_precedent to avoid subprocess
    ep._fetch_precedent = lambda dt, intent, repo_area=None: {  # noqa: E731
        "verdict": precedent_verdict,
        "matched_ids": [],
        "summary": f"stub:{precedent_verdict}",
    }
    # Stub _context_fingerprint to avoid git calls
    ep._context_fingerprint = lambda files: {  # noqa: E731
        "branch": "test-branch",
        "git_sha": "abc123",
        "fp_hash": "deadbeef",
    }
    # Stub _attach_signal_vectors (no-op)
    ep._attach_signal_vectors = lambda annotated, dt, spec: None  # noqa: E731
    # Stub _latest_calibrator_version
    ep._latest_calibrator_version = lambda dt: None  # noqa: E731

    spec = dict(_SPEC)
    return ep.build_packet(spec)


# ---------------------------------------------------------------------------
# A — Cold: empty ledger, no bandit_state.json
# ---------------------------------------------------------------------------

def test_scenario_a_cold_ledger_no_bandit_state(tmp_path: Path) -> None:
    state_path = tmp_path / "bandit_state.json"
    assert not state_path.exists()

    packet = _build_packet_with_mocks(tmp_path, state_path, precedent_verdict="none")

    assert packet["bandit_prior"] is None
    assert packet["confidence_source"] == "cold_prior"
    receipt = packet["causal_use_receipt"]
    assert receipt["bandit_state_read"] is False
    assert receipt["bandit_cell_found"] is False
    assert receipt["reason"] == "bandit_state_missing"


# ---------------------------------------------------------------------------
# B — Precedent only: seeded ledger, no bandit_state.json
# ---------------------------------------------------------------------------

def test_scenario_b_precedent_only_no_bandit_state(tmp_path: Path) -> None:
    _make_seeded_ledger(tmp_path)
    state_path = tmp_path / "bandit_state.json"
    assert not state_path.exists()

    packet = _build_packet_with_mocks(tmp_path, state_path, precedent_verdict="suggestive")

    assert packet["precedent"]["verdict"] == "suggestive"
    assert packet["bandit_prior"] is None
    assert packet["confidence_source"] == "cold_prior"
    receipt = packet["causal_use_receipt"]
    assert receipt["bandit_cell_found"] is False
    assert "alpha" not in (packet["bandit_prior"] or {})
    assert "mean" not in (packet["bandit_prior"] or {})


# ---------------------------------------------------------------------------
# C — Full bandit: seeded ledger + consumer --apply writes bandit_state.json
# ---------------------------------------------------------------------------

def test_scenario_c_full_bandit(tmp_path: Path) -> None:
    db = _make_seeded_ledger(tmp_path)
    state_path = tmp_path / "bandit_state.json"

    consumer = _import(
        "tools/meta_learning/author_gate_consumer.py",
        f"author_gate_consumer_c_{id(tmp_path)}",
    )
    rc = consumer.main(["--db", str(db), "--state", str(state_path), "--apply"])
    assert rc == 0
    assert state_path.exists()

    packet = _build_packet_with_mocks(tmp_path, state_path, precedent_verdict="suggestive")

    assert packet["bandit_prior"] is not None
    bp = packet["bandit_prior"]
    assert bp["alpha"] == 3.0
    assert bp["beta"] == 2.0
    assert abs(bp["mean"] - 3 / 5) < 0.001
    assert bp["ci95_width"] > 0
    assert "n" in bp

    assert packet["confidence_source"] == "bandit_state"
    receipt = packet["causal_use_receipt"]
    assert receipt["bandit_state_read"] is True
    assert receipt["bandit_cell_found"] is True
    assert receipt["reason"] == "bandit_prior_attached"
    assert receipt["bandit_cell_key"] == "refactor_scope|override_recommendation"


# ---------------------------------------------------------------------------
# Causal diff: C must differ from B on bandit fields
# ---------------------------------------------------------------------------

def test_scenario_c_differs_from_b_on_bandit_fields(tmp_path: Path) -> None:
    db = _make_seeded_ledger(tmp_path)
    state_path = tmp_path / "bandit_state.json"

    # Build B (no bandit state)
    packet_b = _build_packet_with_mocks(tmp_path, state_path, precedent_verdict="suggestive")

    # Write bandit state
    consumer = _import(
        "tools/meta_learning/author_gate_consumer.py",
        f"author_gate_consumer_diff_{id(tmp_path)}",
    )
    consumer.main(["--db", str(db), "--state", str(state_path), "--apply"])

    # Build C (bandit state present)
    packet_c = _build_packet_with_mocks(tmp_path, state_path, precedent_verdict="suggestive")

    assert packet_c["bandit_prior"] != packet_b["bandit_prior"], (
        "bandit_state.json is not causally influencing the future packet — Arrow 2 not closed."
    )
    assert packet_c["confidence_source"] != packet_b["confidence_source"], (
        "confidence_source unchanged between B and C — bandit state has no effect."
    )


# ---------------------------------------------------------------------------
# Fallback safety tests — call _load_bandit_prior directly
# ---------------------------------------------------------------------------

@pytest.fixture
def load_prior(tmp_path: Path):
    """Return the _load_bandit_prior function with BANDIT_STATE_PATH patched to tmp_path."""
    mod_name = f"emit_packet_fallback_{id(tmp_path)}"
    ep = _import(
        ".cursor/skills/author-gate-packet-builder/emit_packet.py",
        mod_name,
    )
    ep.BANDIT_STATE_PATH = tmp_path / "bandit_state.json"
    return ep._load_bandit_prior


def test_load_bandit_prior_file_missing(load_prior) -> None:
    cell, reason, state_read = load_prior("refactor_scope", "override_recommendation")
    assert cell is None
    assert reason == "bandit_state_missing"
    assert state_read is False


def test_load_bandit_prior_invalid_json(load_prior, tmp_path: Path) -> None:
    (tmp_path / "bandit_state.json").write_text("not json{{", encoding="utf-8")
    cell, reason, state_read = load_prior("refactor_scope", "override_recommendation")
    assert cell is None
    assert reason == "bandit_state_invalid"
    assert state_read is True


def test_load_bandit_prior_cells_not_dict(load_prior, tmp_path: Path) -> None:
    (tmp_path / "bandit_state.json").write_text(
        json.dumps({"cells": "wrong_type", "updated_at": _NOW}), encoding="utf-8"
    )
    cell, reason, state_read = load_prior("refactor_scope", "override_recommendation")
    assert cell is None
    assert reason == "bandit_cells_invalid"
    assert state_read is True


def test_load_bandit_prior_cell_missing(load_prior, tmp_path: Path) -> None:
    (tmp_path / "bandit_state.json").write_text(
        json.dumps({"cells": {"other_type|unknown": {"alpha": 1.0, "beta": 1.0, "mean": 0.5, "ci95_width": 0.5}}}),
        encoding="utf-8",
    )
    cell, reason, state_read = load_prior("refactor_scope", "override_recommendation")
    assert cell is None
    assert reason == "bandit_cell_missing"
    assert state_read is True


def test_load_bandit_prior_valid_cell_returned(load_prior, tmp_path: Path) -> None:
    # Sub-case 1: n present in JSON
    payload = {
        "cells": {
            "refactor_scope|override_recommendation": {
                "alpha": 3.0,
                "beta": 2.0,
                "mean": 0.6,
                "ci95_width": 0.219,
                "n": 2,
            }
        },
        "updated_at": _NOW,
    }
    (tmp_path / "bandit_state.json").write_text(json.dumps(payload), encoding="utf-8")
    cell, reason, state_read = load_prior("refactor_scope", "override_recommendation")
    assert cell is not None
    assert reason == "bandit_prior_attached"
    assert state_read is True
    for field in ("cell_key", "alpha", "beta", "mean", "ci95_width", "n"):
        assert field in cell, f"missing field: {field}"
    assert cell["n"] == 2  # JSON value wins

    # Sub-case 2: n absent from JSON — must be derived from alpha+beta
    payload["cells"]["refactor_scope|override_recommendation"].pop("n")
    (tmp_path / "bandit_state.json").write_text(json.dumps(payload), encoding="utf-8")
    cell2, _, _ = load_prior("refactor_scope", "override_recommendation")
    assert cell2 is not None
    # n = max(0, int(3.0 + 2.0 - 2)) = 3
    assert cell2["n"] == 3


def test_load_bandit_prior_no_reason_code_falls_back_to_unknown(
    load_prior, tmp_path: Path
) -> None:
    payload = {
        "cells": {
            "refactor_scope|unknown": {
                "alpha": 2.0,
                "beta": 1.0,
                "mean": 0.667,
                "ci95_width": 0.3,
            }
        },
        "updated_at": _NOW,
    }
    (tmp_path / "bandit_state.json").write_text(json.dumps(payload), encoding="utf-8")
    cell, reason, state_read = load_prior("refactor_scope", "")
    assert cell is not None
    assert reason == "bandit_prior_attached"
    assert cell["cell_key"] == "refactor_scope|unknown"
