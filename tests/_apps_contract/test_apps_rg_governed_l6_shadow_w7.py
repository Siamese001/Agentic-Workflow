"""W7 — L6 shadow ingest only after sealed exhaust; no promotion without eval."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.exhaust.runtime_exhaust_bundle import build_runtime_exhaust_bundle
from apps_rg.runtime.shadow.l6_handoff_packet import build_l6_shadow_handoff_dict
from apps_rg.runtime.spine.exit_artifacts import EXIT_DISPOSITION_RECEIPT_ARTIFACT
from apps_rg.runtime.spine.governed_l6_shadow_compose import (
    GOVERNED_L6_SHADOW_MODE_INTEGRATED,
    PROMOTION_STATUS_BLOCKED,
    assert_integrated_exhaust_may_feed_l6,
    governed_l6_shadow_enabled,
    ingest_integrated_exhaust_for_l6_shadow,
)
from apps_rg.runtime.section_l2_spine_receipt import SEALED_L2_ARTIFACT
from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
    finalize_section_runtime_exhaust_before_l6,
    gate_section_l6_shadow_after_exhaust,
)
from apps_rg.runtime.section_runtime_exhaust_spine_receipt import (
    L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT,
    RUNTIME_EXHAUST_BUNDLE_ARTIFACT,
    SectionRuntimeExhaustPreconditionError,
)


def test_governed_l6_shadow_enabled_by_default() -> None:
    assert governed_l6_shadow_enabled() is True


def test_integrated_exhaust_requires_post_exit_flags() -> None:
    from types import SimpleNamespace

    bad = SimpleNamespace(
        created_after_exit=False,
        current_run_closed=True,
        exit_disposition_ref="exit-ref",
    )
    with pytest.raises(ValueError, match="created_after_exit"):
        assert_integrated_exhaust_may_feed_l6(bad)


def test_ingest_integrated_exhaust_envelope() -> None:
    exhaust = build_runtime_exhaust_bundle(
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        exit_disposition_ref="exit-ref-abc",
    )
    env = ingest_integrated_exhaust_for_l6_shadow(exhaust, run_id="run1")
    assert env["governed_l6_shadow_mode"] == GOVERNED_L6_SHADOW_MODE_INTEGRATED
    assert env["promotion_status"] == PROMOTION_STATUS_BLOCKED
    assert env["eval_before_learn_satisfied"] is False


def test_l6_handoff_blocked_without_exhaust(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_GOVERNED_L6_SHADOW_SKIP", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.section_runtime_exhaust_spine_receipt.fixture_dev_bypass_active",
        lambda: False,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.section_runtime_exhaust_spine_receipt.runtime_exhaust_kill_switch_enabled",
        lambda: True,
    )
    assert governed_l6_shadow_enabled()
    assert not (tmp_path / RUNTIME_EXHAUST_BUNDLE_ARTIFACT).is_file()
    with pytest.raises(SectionRuntimeExhaustPreconditionError, match="runtime_exhaust_bundle"):
        gate_section_l6_shadow_after_exhaust(tmp_path, {"product_visible": True})


def test_l6_handoff_includes_governed_envelope_after_exhaust(tmp_path: Path) -> None:
    repo = tmp_path
    art = tmp_path / "run_lane"
    art.mkdir()
    (art / EXIT_DISPOSITION_RECEIPT_ARTIFACT).write_text(
        json.dumps(
            {
                "contract_type": "ExitDispositionReceipt",
                "x3_disposition": {"x3_code": "X3_ALLOW", "pass": True},
                "x3_code": "X3_ALLOW",
                "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT,
                "run_id": "run-w7",
            }
        ),
        encoding="utf-8",
    )
    (art / SEALED_L2_ARTIFACT).write_text("{}", encoding="utf-8")
    (art / "l2_output.json").write_text(
        json.dumps({"run_id": "run-w7", "runtime_generation_status": "REAL_LLM"}),
        encoding="utf-8",
    )
    (art / "x1d_llm_judge_outputs.json").write_text("{}", encoding="utf-8")
    (art / "x2_gate_outputs.json").write_text("{}", encoding="utf-8")
    (art / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    finalize_section_runtime_exhaust_before_l6(
        art,
        "headline",
        {"run_id": "run-w7", "product_visible": True},
        repo_root=repo,
    )
    assert (art / L6_SHADOW_HANDOFF_RECEIPT_ARTIFACT).is_file()
    pkt = build_l6_shadow_handoff_dict(
        artifact_dir=art,
        repo_root=repo,
        section_id="headline",
        prompt_id="headline_tailor_v1",
        temperature=0.0,
        max_tokens=256,
    )
    assert pkt["promotion_allowed"] is False
    env = pkt.get("governed_l6_handoff_envelope")
    assert isinstance(env, dict)
    assert env.get("promotion_status") == PROMOTION_STATUS_BLOCKED
    assert env.get("no_l6_current_run_rescue_assertion") is True
