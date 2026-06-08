import json
from pathlib import Path

from apps_lic.engines.blocked_artifact_ux import (
    DO_NOT_SEND_WATERMARK,
    PRIMARY_RECIPIENT_CLASS_NOT_DERIVED,
    PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH,
)
from apps_lic.engines.e2e_acceptance import ACCEPTANCE_MODE_STRICT_TARGET_FIT
from apps_lic.engines.x1d_preflight import X1D_MODE_FAKE
from scripts.apps_lic.run_aig_30_profile_e2e import REQUIRED_ARTIFACTS, run_aig_30_profile_e2e


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_w7_unknown_profile_exposes_recipient_class_not_derived_primary_blocker(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    results = _load_json(tmp_path / "results.json")
    kathleen = next(row for row in results["rows"] if row["id"] == "kathleen_gerstner")

    assert kathleen["primary_blocker"] == PRIMARY_RECIPIENT_CLASS_NOT_DERIVED
    assert kathleen["blocked_artifact_ux"]["primary_blocker"] == PRIMARY_RECIPIENT_CLASS_NOT_DERIVED
    assert "stronger public profile evidence" in kathleen["user_action_required"]
    assert "Do not send a draft" in kathleen["safe_alternative"]
    assert "message_requirements_not_passed" in kathleen["diagnostics"]["collapsed_downstream_failures"]
    assert "whole_message_shape_gate" in kathleen["diagnostics"]["collapsed_downstream_failures"]
    assert kathleen["product_draft_exposed"] is False


def test_w7_region_mismatch_exposes_role_ownership_primary_blocker(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    results = _load_json(tmp_path / "results.json")
    daisuke = next(row for row in results["rows"] if row["id"] == "daisuke_hayashi")

    assert daisuke["primary_blocker"] == PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH
    assert "target requisition/region" in daisuke["user_action_required"]
    assert "non-JD networking note" in daisuke["safe_alternative"]
    assert "role_ownership_fit_gate" in daisuke["diagnostics"]["collapsed_downstream_failures"]
    assert daisuke["blocked_draft_ref"].startswith("sha256:")


def test_w7_product_facing_blocked_report_has_actions_but_no_blocked_draft(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    blocked = (tmp_path / "blocked_profiles.md").read_text(encoding="utf-8")

    assert "Primary blocker: `recipient_class_not_derived`" in blocked
    assert "Primary blocker: `role_ownership_region_mismatch`" in blocked
    assert "User action required:" in blocked
    assert "Safe alternative:" in blocked
    assert "Diagnostics collapsed:" in blocked
    assert "Hi Daisuke" not in blocked
    assert "Would a quick resume review" not in blocked
    assert DO_NOT_SEND_WATERMARK not in blocked


def test_w7_internal_blocked_appendix_watermarks_any_blocked_draft(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    appendix = (tmp_path / "internal_blocked_draft_appendix.md").read_text(encoding="utf-8")

    assert DO_NOT_SEND_WATERMARK in appendix
    assert "Hi Daisuke" in appendix
    assert "Would a quick resume review" in appendix
    assert "blocked draft failed `role_ownership_region_mismatch`" in appendix
    assert appendix.index(DO_NOT_SEND_WATERMARK) < appendix.index("Hi Daisuke")


def test_w7_summary_reports_blocked_ux_and_required_appendix_artifact(tmp_path: Path) -> None:
    result = run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    summary = _load_json(tmp_path / "summary.json")

    assert "internal_blocked_draft_appendix.md" in REQUIRED_ARTIFACTS
    assert "internal_blocked_draft_appendix.md" in result["artifact_files"]
    assert summary["blocked_ux_passed"] is True
    assert summary["blocked_ux"]["blocked_profile_count"] == 6
    assert summary["blocked_ux"]["product_facing_blocked_draft_exposure_count"] == 0
    assert summary["blocked_ux"]["product_facing_blocked_drafts_suppressed"] is True
    assert summary["blocked_ux"]["blocked_profiles_with_internal_draft_count"] == 1
    assert summary["blocked_ux"]["primary_blocker_counts"] == {
        PRIMARY_RECIPIENT_CLASS_NOT_DERIVED: 5,
        PRIMARY_ROLE_OWNERSHIP_REGION_MISMATCH: 1,
    }
