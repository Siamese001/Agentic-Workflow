"""W2 — Phase-1 resolve attempts every lane even when dispatch reported error / prior abort."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.l2_recipe.modular_resume_generation import (
    ModularResumeInputPackage,
    ModularResumeProfile,
    run_modular_resume_generation,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV


def _write_lane_product_bundle(
    repo: Path,
    sections_root: Path,
    lane: str,
    *,
    run_id: str | None = None,
) -> None:
    rid = run_id or f"pytest_resolve_{lane}"
    run_dir = (sections_root / lane).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    run_rel = run_dir.relative_to(repo).as_posix()
    l2 = {
        "section_id": lane,
        "runtime_generation_status": "REAL_LLM",
        "product_quality_status": "PASS",
    }
    (run_dir / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (run_dir / "provider_request.json").write_text(
        json.dumps({"provider_requested": "qwen_vllm", "provider_attempted": True}),
        encoding="utf-8",
    )
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "pass": True}),
        encoding="utf-8",
    )
    ptr = sections_root / lane / "latest_successful_real_run.json"
    ptr.parent.mkdir(parents=True, exist_ok=True)
    ptr.write_text(json.dumps({"run_dir": run_rel.replace("\\", "/")}), encoding="utf-8")


def test_phase1_resolves_executive_summary_despite_dispatch_exit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """RC-2: on-disk exec_summary pointer must materialize even if dispatch dict says error."""
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_resolve_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)

    def _stub_lane_dispatch(**kwargs: object) -> dict[str, object]:
        lane = str(kwargs.get("section") or "")
        sections_root = Path(os.environ[MODULAR_R4_SECTIONS_ROOT_ENV])
        if lane == "executive_summary":
            _write_lane_product_bundle(repo, sections_root, lane)
        return {
            "exit_status": "error",
            "outcome_authorized": False,
            "x3_disposition": "",
            "fault": "",
        }

    with (
        patch("apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope") as env_call,
        patch(
            "apps_rg.l2_recipe.modular_resume_generation.run_canonical_apps_rg_from_cli_primitives",
            side_effect=_stub_lane_dispatch,
        ),
    ):
        res = run_modular_resume_generation(
            ModularResumeInputPackage(repo_root=repo),
            art,
            "pytest_resolve_abort",
            ModularResumeProfile(
                phase1_invoke_real_lanes=True,
                run_phase0_synthetic_assembly=False,
                validate_rg_output_fixture=False,
            ),
        )
    env_call.assert_not_called()
    calls_path = art / res.section_provider_calls_ref
    raw = json.loads(calls_path.read_text(encoding="utf-8"))
    records = {r["section_lane"]: r for r in raw["records"]}
    assert records["executive_summary"]["generation_status"] != "MISSING_LANE_RUN"
    assert records["executive_summary"].get("provider_call_attempted") is True
    assert records["headline"]["generation_status"] == "MISSING_LANE_RUN"
    assert int(res.extras.get("lanes_executed") or 0) == 1


def test_phase1_materialize_runs_all_lanes_when_first_missing_pointer(monkeypatch: pytest.MonkeyPatch) -> None:
    """First-lane missing pointer must not skip a later lane's (executive_summary) resolve.

    Order-agnostic: asserts the *first* lane in GENERATED_LANES gets PHASE1_NO_RUN_DIR while a
    later lane that wrote its bundle still materializes — the invariant the dependency-ordered
    serial loop must preserve regardless of which lane is first.
    """
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"phase1_resolve_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)

    def _stub_lane_dispatch(**kwargs: object) -> dict[str, object]:
        lane = str(kwargs.get("section") or "")
        sections_root = Path(os.environ[MODULAR_R4_SECTIONS_ROOT_ENV])
        if lane == "executive_summary":
            _write_lane_product_bundle(repo, sections_root, lane)
        return {"exit_status": "success", "fault": ""}

    with patch(
        "apps_rg.l2_recipe.modular_resume_generation.run_canonical_apps_rg_from_cli_primitives",
        side_effect=_stub_lane_dispatch,
    ):
        res = run_modular_resume_generation(
            ModularResumeInputPackage(repo_root=repo),
            art,
            "pytest_order",
            ModularResumeProfile(
                phase1_invoke_real_lanes=True,
                run_phase0_synthetic_assembly=False,
                validate_rg_output_fixture=False,
            ),
        )
    first_lane = GENERATED_LANES[0]
    assert first_lane != "executive_summary"  # exec_summary is the lane that writes its bundle
    raw = json.loads((art / res.section_provider_calls_ref).read_text(encoding="utf-8"))
    records = {r["section_lane"]: r for r in raw["records"]}
    # The lane that wrote its bundle materializes despite the first lane having no run dir.
    assert records["executive_summary"].get("provider_call_attempted") is True
    # The first lane in the order (no bundle written) surfaces PHASE1_NO_RUN_DIR — proving the
    # serial loop does not abort at the first missing lane.
    assert records[first_lane]["decisive_reason_code"] == "PHASE1_NO_RUN_DIR"
