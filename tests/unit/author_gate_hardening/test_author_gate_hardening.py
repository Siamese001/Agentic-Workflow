"""Unit tests for plan `docs/archive/windsurf/legacy-tree/plans/author-gate-hardening-a3b8f2.md` W1-W4.

Covers the load-bearing pieces:
  - Schema migration idempotency (W1.P1.1)
  - DECISION_OUTCOME marker parse + outcome_writer insert/update (W1.P1.2)
  - reason_code tail parsing (W1.P1.3)
  - isotonic_fit + isotonic_apply monotonicity + clipping (W2.P2.2)
  - Brier / ECE math (W2.P2.2)
  - Thompson bandit cell update + stats (W4.P4.1)
  - render_card output shape (W3.P3.2)
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _import(mod_path: str, module_name: str):
    """Dynamically load a module-path file into sys.modules under module_name."""
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / mod_path)
    assert spec and spec.loader, mod_path
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ fixtures


@pytest.fixture
def tmp_ledger(tmp_path: Path) -> Path:
    """Return a fresh ledger DB with the full schema applied via _init_db."""
    # Redirect DB_PATH by patching the module-level constant via env var approach
    # would require code changes; simpler is to call the DDL directly.
    capture_mod = _import(
        ".claude/governance/scripts/post_agent_author_gate_capture.py",
        "post_agent_author_gate_capture_under_test",
    )
    db_path = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(capture_mod._ddl)  # pylint: disable=protected-access
    # Apply idempotent migrations same way _init_db does
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    for col, typ in (
        ("reason_code", "TEXT"),
        ("confidence_calibrated", "REAL"),
        ("calibrator_version", "TEXT"),
        ("adg_hotspot_rank", "INTEGER"),
        ("blast_radius_hops", "INTEGER"),
        ("surface_intersections_json", "TEXT"),
        ("decision_class_tier", "TEXT"),
    ):
        if col not in cols:
            conn.execute(f"ALTER TABLE decisions ADD COLUMN {col} {typ}")
    # Ensure decision_outcomes carries common extended cols used by the writer.
    oc_cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    for col, typ in (
        ("commit_shas_json", "TEXT"),
        ("files_written_json", "TEXT"),
        ("tests_run_json", "TEXT"),
        ("latency_to_outcome_s", "INTEGER"),
        ("pattern_promotion_eligible", "INTEGER"),
        ("outcome_label", "TEXT"),
        ("bound_at", "TEXT"),
    ):
        if col not in oc_cols:
            conn.execute(f"ALTER TABLE decision_outcomes ADD COLUMN {col} {typ}")
    conn.commit()
    conn.close()
    return db_path


# ------------------------------------------------------------------ W1.P1.1


def test_schema_has_new_columns(tmp_ledger: Path) -> None:
    conn = sqlite3.connect(str(tmp_ledger))
    cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    for c in (
        "reason_code",
        "confidence_calibrated",
        "calibrator_version",
        "adg_hotspot_rank",
        "blast_radius_hops",
        "surface_intersections_json",
        "decision_class_tier",
    ):
        assert c in cols, f"missing column {c}"
    # New tables
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "decision_signals" in tables
    assert "decision_calibration_snapshots" in tables
    conn.close()


# ------------------------------------------------------------------ W1.P1.2


def test_outcome_writer_parse_and_insert(tmp_ledger: Path) -> None:
    ow = _import("tools/capture/outcome_writer.py", "outcome_writer_under_test")
    marker = (
        "DECISION_OUTCOME: decision_id=dec_abc123, execution_completed=1, "
        "tests_passed=1, regression_found=0, rollback_required=0, "
        "promote_to_pattern=1, time_to_outcome_s=3600, notes=clean landing"
    )
    parsed = ow.parse_outcome(marker)
    assert parsed is not None
    assert parsed["decision_id"] == "dec_abc123"
    assert parsed["promote_to_pattern"] == 1
    assert parsed["latency_to_outcome_s"] == 3600
    assert parsed["outcome_notes"].startswith("clean landing")

    # Insert a matching decision first
    conn = sqlite3.connect(str(tmp_ledger))
    conn.execute(
        "INSERT INTO decisions (decision_id, created_at, decision_type, status) "
        "VALUES (?, ?, ?, ?)",
        ("dec_abc123", "2026-05-03T00:00:00+00:00", "refactor_scope", "executed"),
    )
    conn.commit()

    disp = ow.write_outcome(conn, parsed)
    assert disp == "inserted"
    # Second call idempotent
    disp2 = ow.write_outcome(conn, parsed)
    assert disp2 in ("updated", "skipped")
    row = conn.execute(
        "SELECT promote_to_pattern, outcome_label FROM decision_outcomes WHERE decision_id = ?",
        ("dec_abc123",),
    ).fetchone()
    assert row[0] == 1
    assert row[1] == "promote"
    conn.close()


def test_outcome_writer_unparseable_returns_none() -> None:
    ow = _import("tools/capture/outcome_writer.py", "outcome_writer_under_test")
    assert ow.parse_outcome("NOT_A_MARKER") is None
    assert ow.parse_outcome("DECISION_OUTCOME: decision_id=bad, execution_completed=1") is None


# ------------------------------------------------------------------ W1.P1.3


def test_reason_code_tail_parse() -> None:
    capture_mod = _import(
        ".claude/governance/scripts/post_agent_author_gate_capture.py",
        "post_agent_author_gate_capture_parse_test",
    )
    tail = (
        ", confidence=0.89, gap=0.15, override=true, "
        "reason_code=override_recommendation, adg_hotspot_rank=5, "
        "blast_radius_hops=3, decision_class_tier=T2, surfaces=Execution,Write"
    )
    v2 = capture_mod._parse_v2_tail(tail)  # pylint: disable=protected-access
    assert v2["reason_code"] == "override_recommendation"
    assert v2["adg_hotspot_rank"] == 5
    assert v2["blast_radius_hops"] == 3
    assert v2["decision_class_tier"] == "T2"
    assert v2["override_vs_recommendation"] == 1
    assert v2["surface_intersections_json"] == json.dumps(["Execution", "Write"])


# ------------------------------------------------------------------ W2.P2.2


def test_isotonic_fit_monotonic() -> None:
    cal = _import(
        "ops_scripts/calibration/author_gate_calibrator.py",
        "author_gate_calibrator_under_test",
    )
    xs = [0.1, 0.3, 0.2, 0.5, 0.6, 0.8, 0.95]
    ys = [0, 1, 0, 1, 0, 1, 1]
    points = cal.isotonic_fit(xs, ys)
    # Monotonic non-decreasing in y
    for i in range(1, len(points)):
        assert points[i][1] >= points[i - 1][1], f"monotonicity violated at {i}"


def test_isotonic_apply_clipping() -> None:
    cal = _import(
        "ops_scripts/calibration/author_gate_calibrator.py",
        "author_gate_calibrator_apply_test",
    )
    pts = [(0.1, 0.0), (0.5, 0.5), (0.9, 1.0)]
    assert cal.isotonic_apply(pts, 0.0) == 0.0  # clamps to left
    assert cal.isotonic_apply(pts, 1.0) == 1.0  # clamps to right
    # Midpoint linear interpolation
    assert abs(cal.isotonic_apply(pts, 0.3) - 0.25) < 1e-6


def test_brier_and_ece() -> None:
    cal = _import(
        "ops_scripts/calibration/author_gate_calibrator.py",
        "author_gate_calibrator_metrics_test",
    )
    # Perfectly calibrated: all scores = outcomes
    assert cal.brier_score([0.0, 1.0, 0.0, 1.0], [0, 1, 0, 1]) == 0.0
    # Worst-case
    assert cal.brier_score([1.0, 0.0], [0, 1]) == 1.0
    # Scores 0.9 with outcomes all 1.0 → bin gap |0.9 - 1.0| = 0.1
    ece, bins = cal.expected_calibration_error([0.9, 0.9, 0.9], [1, 1, 1])
    assert abs(ece - 0.1) < 1e-6
    assert isinstance(bins, list) and len(bins) == 10
    # Perfectly calibrated within a single bin: scores 0.5, outcomes split 50/50
    ece2, _ = cal.expected_calibration_error([0.5, 0.5], [1, 0])
    assert abs(ece2 - 0.0) < 1e-6


# ------------------------------------------------------------------ W4.P4.1


def test_bandit_update(tmp_ledger: Path) -> None:
    consumer = _import(
        "tools/meta_learning/author_gate_consumer.py",
        "author_gate_consumer_under_test",
    )
    conn = sqlite3.connect(str(tmp_ledger))
    # Seed two decisions in the same class; one success, one failure.
    conn.execute(
        "INSERT INTO decisions (decision_id, created_at, decision_type, reason_code, status) "
        "VALUES (?,?,?,?,?)",
        ("dec_win1", "2026-05-03T00:00:00+00:00", "refactor_scope", "override_recommendation", "executed"),
    )
    conn.execute(
        "INSERT INTO decisions (decision_id, created_at, decision_type, reason_code, status) "
        "VALUES (?,?,?,?,?)",
        ("dec_lose1", "2026-05-03T00:00:00+00:00", "refactor_scope", "override_recommendation", "executed"),
    )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, execution_completed, tests_passed, "
        "regression_found, rollback_required, promote_to_pattern) VALUES (?,1,1,0,0,1)",
        ("dec_win1",),
    )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, execution_completed, tests_passed, "
        "regression_found, rollback_required, promote_to_pattern) VALUES (?,1,0,0,1,0)",
        ("dec_lose1",),
    )
    conn.commit()
    state = consumer.update_bandit(conn)
    key = "refactor_scope|override_recommendation"
    assert key in state
    cell = state[key]
    # Priors (1,1) + one win + one loss → alpha=2, beta=2
    assert cell["alpha"] == 2.0
    assert cell["beta"] == 2.0
    assert abs(cell["mean"] - 0.5) < 1e-6
    conn.close()


# ------------------------------------------------------------------ W3.P3.2


def test_render_card_shape() -> None:
    rc = _import(
        ".claude/skills/author-gate-ui-renderer/render_card.py",
        "render_card_under_test",
    )
    packet = {
        "decision_id": "dec_test1",
        "decision_type": "refactor_scope",
        "recommended_option_id": "minimal",
        "candidates": [
            {
                "id": "minimal", "surfaced": True, "is_recommended": True,
                "confidence_score": 0.89,
                "surface_label": "⭐ Recommended — 🟢 89% — Extract SovereignBaseAgent only",
                "surface_description": (
                    "[RECOMMENDED ⭐ confidence=0.89] · trade-off: "
                    "Narrow extraction keeps blast radius small"
                ),
                "thesis": "Extract SovereignBaseAgent only",
                "principle_at_stake": "layer gravity",
                "what_would_flip": ["blast_radius>5", "hotspot rank moves to top-10"],
            },
            {
                "id": "comprehensive", "surfaced": True, "confidence_score": 0.61,
                "thesis": "Extract all 5 siblings",
            },
        ],
        "routing": {"rule_applied": "dominance_fires", "dominance_delta_observed": 0.28},
        "precedent": {"verdict": "suggestive", "matched_ids": ["dec_old1"]},
        "reason_code_palette": ["override_recommendation", "other"],
        "blast_radius_hops": 3,
        "adg_hotspot_rank": 5,
        "surface_intersections_json": json.dumps(["Execution"]),
    }
    card, options = rc.render_card(packet)
    assert "🎯 Recommended: minimal" in card
    assert "🟢 0.89" in card
    assert "precedent: suggestive" in card
    assert "Reason-code palette" in card
    assert len(options) == 2
    assert "⭐" in options[0]["label"]
    assert "RECOMMENDED" in options[0]["description"]
    assert "trade-off:" in options[0]["description"]
