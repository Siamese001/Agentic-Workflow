"""W4 — 5x4 eval lane matrix + per-recipient batch aggregation.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W4.1 + W4.2). Skipped
when the apps_rg shared graph artifact is unavailable (the bridge is fail-soft).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from apps_lic.integrations.apps_rg_proof_bridge import load_apps_rg_proof_index
from tools.apps_lic.eval_lane_matrix import (
    DISPOSITION_BLOCKED,
    DISPOSITION_READY,
    MESSAGE_TYPES,
    RECIPIENT_TITLES,
    evaluate_lane_matrix,
    render_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BATCH_POLICY = REPO_ROOT / "apps_lic" / "config" / "campaign_batch_policy.yaml"


def _require_shared_ssot():
    index = load_apps_rg_proof_index()
    if not index.available:
        pytest.skip(f"apps_rg shared proof SSOT unavailable: {index.load_error}")


def test_matrix_evaluates_all_twenty_lanes() -> None:
    _require_shared_ssot()
    report = evaluate_lane_matrix()
    assert len(report.cells) == len(MESSAGE_TYPES) * len(RECIPIENT_TITLES) == 20
    # every cell carries a disposition + the markdown renders.
    assert all(c.disposition in {DISPOSITION_READY, DISPOSITION_BLOCKED} for c in report.cells)
    assert "Eval Lane Matrix" in render_markdown(report)


def test_ready_lanes_carry_grounded_apps_rg_provenance() -> None:
    _require_shared_ssot()
    report = evaluate_lane_matrix()
    ready = [c for c in report.cells if c.disposition == DISPOSITION_READY]
    assert ready, "expected at least one READY lane at target quality"
    for cell in ready:
        assert cell.proof_count >= 1
        assert cell.grounded_provenance_count >= 1  # W2 grounding flows through
        assert cell.message_gate_pass and cell.proof_ready


def test_batch_aggregation_is_per_recipient_no_all_or_nothing() -> None:
    """W4.2: a BLOCKED lane never suppresses the others — the full sweep reports."""
    _require_shared_ssot()
    report = evaluate_lane_matrix()
    # The sweep both blocks some lanes AND keeps producing ready lanes.
    assert report.blocked_count >= 1
    assert report.ready_count >= 1
    assert report.ready_count + report.blocked_count == len(report.cells)
    # Blocked lanes carry their own per-cell reason (independent disposition),
    # not a single shared abort.
    for cell in report.cells:
        if cell.disposition == DISPOSITION_BLOCKED:
            assert cell.blocking_reasons


def test_campaign_batch_policy_does_not_abort_on_first_failure() -> None:
    text = BATCH_POLICY.read_text(encoding="utf-8")
    # Policy SSOT documents the no-all-or-nothing contract the matrix demonstrates.
    assert "abort_on_first_failure: false" in text
    config = yaml.safe_load(text)
    assert int(config["max_recipients_per_batch"]) >= 20
