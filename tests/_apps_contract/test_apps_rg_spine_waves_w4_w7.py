"""W4–W7 deferred harden waves — OTEL metadata, graph lane, L6 eval, live smoke manifest."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF
from apps_rg.runtime.spine.c0_graph_lane_receipt import (
    C0_GRAPH_LANE_RECEIPT_ARTIFACT,
    build_c0_graph_lane_receipt,
    build_c0_graph_lane_receipt_from_bridge,
    emit_c0_graph_lane_receipt,
)
from apps_rg.runtime.spine.governed_l6_shadow_compose import PROMOTION_STATUS_BLOCKED
from apps_rg.runtime.spine.l6_eval_before_learn_receipt import (
    L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT,
    build_l6_eval_before_learn_receipt,
    emit_l6_eval_before_learn_receipt,
)
from apps_rg.runtime.spine.spine_span_emit import (
    SPINE_SPAN_RECEIPT,
    _otel_sdk_enabled,
    emit_spine_span_event,
)

REPO = Path(__file__).resolve().parents[2]
LIVE_SMOKE = REPO / "ops_scripts" / "apps_rg" / "live_section_spine_smoke_all_lanes.py"
SPAN_SITES_GATE = REPO / "ops_scripts" / "ci" / "check_apps_rg_spine_span_emit_sites.py"


def test_w4_span_emit_records_otel_dual_write_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_SPINE_OTEL_SDK", "1")
    monkeypatch.setenv("APPS_RG_SPINE_SPAN_EMIT", "1")
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        with mock.patch(
            "apps_rg.runtime.spine.spine_span_emit._try_otel_span",
            return_value=True,
        ):
            emit_spine_span_event(ad, layer_key="PA", binding_seam="test")
        line = json.loads((ad / SPINE_SPAN_RECEIPT).read_text(encoding="utf-8").strip())
        assert line["otel_dual_write_attempted"] is True
        assert line["otel_dual_write_ok"] is True


def test_w4_span_emit_sites_gate_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(SPAN_SITES_GATE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_w5_c0_graph_lane_receipt_marks_deferred() -> None:
    receipt = build_c0_graph_lane_receipt(
        section_id="headline",
        graph_lane_ref=C0_GRAPH_LANE_NA_REF,
    )
    assert receipt["graph_lane_deferred"] is True
    assert receipt["canonical_c0_3_graph_rag_claimed"] is False
    with tempfile.TemporaryDirectory() as tmp:
        path = emit_c0_graph_lane_receipt(Path(tmp), receipt)
        assert path.name == C0_GRAPH_LANE_RECEIPT_ARTIFACT


def test_w6_l6_eval_before_learn_receipt_blocks_promotion() -> None:
    receipt = build_l6_eval_before_learn_receipt(
        section_id="headline",
        run_id="run-1",
        governed_envelope={
            "promotion_status": PROMOTION_STATUS_BLOCKED,
            "eval_before_learn_satisfied": False,
        },
    )
    assert receipt["promotion_allowed"] is False
    assert receipt["eval_before_learn_satisfied"] is False
    with tempfile.TemporaryDirectory() as tmp:
        emit_l6_eval_before_learn_receipt(Path(tmp), receipt)
        assert (Path(tmp) / L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT).is_file()


def test_w7_live_smoke_blocked_without_chroma() -> None:
    env = dict(os.environ)
    env.pop("CHROMA_PERSIST_DIR", None)
    env.pop("APPS_RG_LIVE_SMOKE_DRY_RUN", None)
    completed = subprocess.run(
        [sys.executable, str(LIVE_SMOKE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=env,
    )
    assert completed.returncode == 2
    doc = json.loads(completed.stdout)
    assert doc["status"] == "BLOCKED"


def test_w5_graph_lane_from_bridge_empty_metadata_defaults_deferred() -> None:
    receipt = build_c0_graph_lane_receipt_from_bridge({"section_id": "headline"})
    assert receipt["graph_lane_deferred"] is True
    assert receipt["skills_graph_bound"] is False


def test_w6_eval_receipt_preserves_envelope_promotion_status() -> None:
    receipt = build_l6_eval_before_learn_receipt(
        section_id="headline",
        run_id="run-x",
        governed_envelope={
            "promotion_status": "CUSTOM_BLOCKED",
            "eval_before_learn_required": True,
        },
    )
    assert receipt["promotion_status"] == "CUSTOM_BLOCKED"
    assert receipt["promotion_allowed"] is False


def test_w4_otel_not_attempted_when_sdk_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_SPINE_OTEL_SDK", raising=False)
    monkeypatch.setenv("APPS_RG_SPINE_SPAN_EMIT", "1")
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        emit_spine_span_event(ad, layer_key="EXIT", binding_seam="test")
        line = json.loads((ad / SPINE_SPAN_RECEIPT).read_text(encoding="utf-8").strip())
        assert line["otel_dual_write_attempted"] is False
        assert line["proof_classification"] == "receipt_fallback_not_otel_sdk"


def test_w7_live_smoke_dry_run_manifest() -> None:
    with tempfile.TemporaryDirectory() as chroma_tmp:
        env = dict(os.environ)
        env["CHROMA_PERSIST_DIR"] = chroma_tmp
        env["APPS_RG_LIVE_SMOKE_DRY_RUN"] = "1"
        completed = subprocess.run(
            [sys.executable, str(LIVE_SMOKE)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env=env,
        )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    doc = json.loads(completed.stdout)
    assert doc["status"] == "PASS"
