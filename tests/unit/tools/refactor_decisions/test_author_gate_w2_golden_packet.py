"""Golden alignment: emit_packet signal vectors vs W2 capture writer + SQLite."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import importlib.util

_ep_spec = importlib.util.spec_from_file_location(
    "emit_packet_ag_w2_golden",
    REPO / ".claude" / "skills" / "author-gate-packet-builder" / "emit_packet.py",
)
assert _ep_spec and _ep_spec.loader
ep = importlib.util.module_from_spec(_ep_spec)
sys.modules["emit_packet_ag_w2_golden"] = ep
_ep_spec.loader.exec_module(ep)

from tools.refactor_decisions.author_gate_w2_signals import (  # noqa: E402
    PRECEDENT_AGREEMENT_BY_VERDICT,
    replace_decision_signals_for_capture,
    stable_option_key,
)
from tools.refactor_decisions.ledger_w2_schema import ensure_w2_decision_signal_columns  # noqa: E402


@pytest.mark.parametrize("verdict", ["strong", "suggestive", "none"])
def test_golden_packet_signals_match_db_rows(verdict: str):
    labels = ["Alpha scope", "Beta scope"]
    annotated = [
        {
            "id": stable_option_key(labels[i], i),
            "surfaced": True,
            # Align verbalized with capture_hook heuristic (recommended 0.85, else 0.5).
            "confidence_score": 0.85 if i == 0 else 0.5,
        }
        for i in range(2)
    ]
    spec = {
        "precedent_agreement_by_option": {
            stable_option_key(labels[0], 0): PRECEDENT_AGREEMENT_BY_VERDICT[verdict],
            stable_option_key(labels[1], 1): 0.5,
        },
        "blast_radius_hops": 2,
        "adg_hotspot_rank": 10,
        "adg_hotspot_top_n": 100,
        "rule_flagged_options": [],
    }
    ep._attach_signal_vectors(annotated, "refactor_scope", spec)

    conn = sqlite3.connect(":memory:")
    conn.execute(
        """CREATE TABLE decision_signals (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id TEXT NOT NULL,
            option_id TEXT NOT NULL,
            signal_name TEXT NOT NULL,
            signal_value REAL NOT NULL,
            signal_weight REAL NOT NULL,
            signal_source TEXT
        )"""
    )
    ensure_w2_decision_signal_columns(conn)
    decision_id = "dec_golden_test"
    meta = {
        "precedent_lookup_ok": True,
        "precedent_verdict_from_lookup": verdict,
        "precedent_lookup_query_digest": "golden_digest_01",
        "precedent_top_match_ids_json": json.dumps(["dec_legacy_1"]),
        "precedent_lookup_reason": "GOLDEN_FIXTURE_BELOW_THRESHOLD",
    }
    replace_decision_signals_for_capture(
        conn,
        decision_id,
        labels,
        recommended_label=labels[0],
        merged_verdict=verdict,
        meta=meta,
        v2={"blast_radius_hops": 2, "adg_hotspot_rank": 10},
    )

    for opt in annotated:
        oid = opt["id"]
        expected = opt["signals"]
        is_primary = oid == annotated[0]["id"]
        for sname, ev in expected.items():
            row = conn.execute(
                "SELECT signal_value, signal_source, source_ref FROM decision_signals "
                "WHERE decision_id = ? AND option_id = ? AND signal_name = ?",
                (decision_id, oid, sname),
            ).fetchone()
            assert row is not None, f"missing {oid} {sname}"
            assert abs(float(row[0]) - float(ev)) < 1e-5, f"{oid} {sname}: db={row[0]} emit={ev}"
            if sname == "precedent_agreement":
                assert row[1] == "capture_hook"
                ref = json.loads(row[2])
                if is_primary:
                    assert ref.get("lookup_reason") == "GOLDEN_FIXTURE_BELOW_THRESHOLD"

    conn.close()
