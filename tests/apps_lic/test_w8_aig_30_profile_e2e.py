import json
import subprocess
import sys
from pathlib import Path

from apps_lic.engines.e2e_acceptance import (
    ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
    ACCEPTANCE_MODE_STRICT_TARGET_FIT,
)
from apps_lic.engines.x1d_preflight import X1D_MODE_FAKE, X1D_MODE_LIVE
from scripts.apps_lic.run_aig_30_profile_e2e import (
    DEFAULT_FIXTURE_PATH,
    FINAL_RETEST_MATRIX_ARTIFACT,
    REQUIRED_ARTIFACTS,
    run_aig_30_profile_e2e,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "apps_lic" / "run_aig_30_profile_e2e.py"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_w4_aig_30_fixture_is_committed_and_complete() -> None:
    fixture = _load_json(DEFAULT_FIXTURE_PATH)

    assert fixture["schema_version"] == "apps_lic.aig_30_profiles_fixture.v1"
    assert fixture["fixture_id"] == "aig_30_linkedin_profiles_20260608"
    assert fixture["profile_count"] == 30
    assert len(fixture["profiles"]) == 30
    assert {row["id"] for row in fixture["profiles"]} >= {
        "daisuke_hayashi",
        "kathleen_gerstner",
        "dennis_najar",
        "anirudh_r",
        "karthikeya_gowd",
        "indu_sri",
    }
    assert sum(1 for row in fixture["profiles"] if row["exit_disposition"] == "clear_draft") == 24


def test_w4_runner_produces_strict_fake_artifact_schema(tmp_path: Path) -> None:
    result = run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )

    assert result["output_dir"] == str(tmp_path)
    assert set(result["artifact_files"]) == set(REQUIRED_ARTIFACTS)
    for artifact_name in REQUIRED_ARTIFACTS:
        assert (tmp_path / artifact_name).is_file()

    summary = _load_json(tmp_path / "summary.json")
    results = _load_json(tmp_path / "results.json")
    judges = _load_json(tmp_path / "judge_receipts.json")
    c0 = _load_json(tmp_path / "c0_readiness.json")
    matrix = _load_json(tmp_path / FINAL_RETEST_MATRIX_ARTIFACT)

    assert summary["schema_version"] == "apps_lic.aig_30_e2e_summary.v1"
    assert summary["mode"] == ACCEPTANCE_MODE_STRICT_TARGET_FIT
    assert summary["x1d_mode"] == X1D_MODE_FAKE
    assert summary["profile_count"] == 30
    assert summary["clear_draft_count"] == 24
    assert summary["blocked_or_review_count"] == 6
    assert summary["acceptance_passed"] is True
    assert summary["final_retest_matrix_passed"] is True
    assert summary["final_retest_matrix_result"] == "strict_target_fit_fake_passed"
    assert summary["live_claude_proof"] is False
    assert results["schema_version"] == "apps_lic.aig_30_e2e_results.v1"
    assert results["acceptance"]["policy_correct_block_count"] == 6
    assert judges["schema_version"] == "apps_lic.aig_30_judge_receipts.v1"
    assert judges["x1d_mode"] == X1D_MODE_FAKE
    assert judges["live_claude_proof"] is False
    assert judges["preflight"]["clearance_allowed"] is False
    assert all(receipt["live_claude_proof"] is False for receipt in judges["receipts"])
    assert c0["schema_version"] == "apps_lic.aig_30_c0_readiness.v1"
    assert c0["profile_count"] == 30
    assert c0["ready_count"] == 30
    assert matrix["schema_version"] == "apps_lic.w8_final_retest_matrix.v1"
    assert matrix["matrix_passed"] is True
    assert matrix["strict_target_fit_fake"]["actual_clear_draft_count"] == 24
    assert matrix["strict_target_fit_fake"]["actual_policy_correct_block_count"] == 6
    assert matrix["strict_target_fit_fake"]["primary_blocker_counts"] == {
        "recipient_class_not_derived": 5,
        "role_ownership_region_mismatch": 1,
    }
    assert matrix["invariants"]["fake_mode_does_not_claim_live_claude_proof"] is True


def test_w4_all_clear_mode_reports_six_remediations_not_pass(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    summary = _load_json(tmp_path / "summary.json")
    matrix = _load_json(tmp_path / FINAL_RETEST_MATRIX_ARTIFACT)
    acceptance = summary["acceptance"]

    assert summary["mode"] == ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE
    assert summary["acceptance_passed"] is False
    assert summary["final_retest_matrix_passed"] is True
    assert summary["final_retest_matrix_result"] == "expected_remediation_required"
    assert acceptance["clear_draft_count"] == 24
    assert acceptance["remediation_required_count"] == 6
    assert acceptance["unexpected_gap_count"] == 0
    assert matrix["matrix_passed"] is True
    assert matrix["all_clear_eligible"]["generation_acceptance_passed"] is False
    assert matrix["all_clear_eligible"]["remediation_required_count"] == 6
    assert matrix["all_clear_eligible"]["expected_clear_only_after_remediation"] is True
    assert sorted(
        row["profile_id"]
        for row in acceptance["rows"]
        if row["status"] == "all_clear_remediation_required"
    ) == [
        "anirudh_r",
        "daisuke_hayashi",
        "dennis_najar",
        "indu_sri",
        "karthikeya_gowd",
        "kathleen_gerstner",
    ]


def test_w8_live_mode_without_anthropic_key_fails_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_ALL_CLEAR_ELIGIBLE,
        x1d_mode=X1D_MODE_LIVE,
        output_dir=tmp_path,
    )

    summary = _load_json(tmp_path / "summary.json")
    judges = _load_json(tmp_path / "judge_receipts.json")
    matrix = _load_json(tmp_path / FINAL_RETEST_MATRIX_ARTIFACT)

    assert summary["x1d_mode"] == X1D_MODE_LIVE
    assert summary["acceptance_passed"] is False
    assert summary["live_claude_proof"] is False
    assert judges["live_claude_proof"] is False
    assert judges["preflight"]["api_key_present"] is False
    assert judges["preflight"]["availability_status"] == "unavailable"
    assert judges["preflight"]["clearance_allowed"] is False
    assert matrix["result"] == "failed_closed_unavailable_judge"
    assert matrix["matrix_passed"] is True
    assert matrix["live_mode"]["unavailable_judge_artifact_emitted"] is True
    assert matrix["live_mode"]["fail_closed_without_live_candidate_receipts"] is True
    assert matrix["live_mode"]["live_candidate_judge_receipts_ready"] is False


def test_w4_markdown_artifacts_split_clear_drafts_from_blocked_profiles(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )

    clear_messages = (tmp_path / "messages_clear_drafts.md").read_text(encoding="utf-8")
    blocked = (tmp_path / "blocked_profiles.md").read_text(encoding="utf-8")

    assert "Nina K" in clear_messages
    assert "Daisuke Hayashi" not in clear_messages
    assert "Blocked drafts are not exposed here" in blocked
    assert "Daisuke Hayashi" in blocked
    assert "Would a quick resume review" not in blocked
    assert "Hi Daisuke" not in blocked


def test_w4_runner_cli_writes_expected_artifacts(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--mode",
            ACCEPTANCE_MODE_STRICT_TARGET_FIT,
            "--x1d-mode",
            X1D_MODE_FAKE,
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["output_dir"] == str(tmp_path)
    assert set(payload["artifact_files"]) == set(REQUIRED_ARTIFACTS)
    assert (tmp_path / "summary.json").is_file()
