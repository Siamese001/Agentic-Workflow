"""W5: deterministic contract tests for SRFS receipt aggregator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.audit import srfs_receipt_aggregator as agg
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

REPO = Path(__file__).resolve().parents[2]
AGG_SOURCE = REPO / "apps_rg" / "audit" / "srfs_receipt_aggregator.py"

FORBIDDEN_PHRASES = (
    "release proof",
    "product allow",
    "certified",
    "runtime certified",
    "full resume srfs",
)


def _valid_srfs_receipt(section: str, **overrides: object) -> dict:
    base = {
        "run_id": f"run_{section}",
        "lane_id": section,
        "prompt_id": f"{section}.v1",
        "prompt_hash": "abc123def456",
        "input_payload_hash": "in_hash",
        "output_payload_hash": "out_hash",
        "claim_ledger_hash": "cl_hash",
        "runtime_generation_status": "OFFLINE_STUB",
        "product_quality_status": "PASS",
        "x2_failed_gates": [],
        "x3_code": "X3_ALLOW",
        "proof_eligible": True,
        "judge_proof_eligible": False,
        "proof_pool_type": "selected_role_fact_set",
        "selected_role_fact_set_used": True,
        "srfs_section_id": section,
        "candidate_fact_pool_count": 1,
        "allowed_fact_ids_count": 2,
        "required_fact_ids_count": 1,
        "claim_ledger_union_matches_required_fact_ids": True,
        "out_of_slice_fact_ids": [],
        "fallback_used": False,
        "fallback_reason": "",
        "x2_srfs_gate_status": "PASS",
        "srfs_allowed_fact_ids_count": 2,
        "full_resume_srfs_supported": False,
    }
    base.update(overrides)
    return base


def _write_receipt(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _write_seven_manifest(tmp_path: Path, overrides: dict[str, dict] | None = None) -> tuple[Path, dict[str, Path]]:
    overrides = overrides or {}
    receipt_paths: dict[str, Path] = {}
    receipts_manifest: dict[str, str] = {}
    for section in GENERATED_LANES:
        rdir = tmp_path / section
        rpath = rdir / "section_metric_receipt.json"
        payload = _valid_srfs_receipt(section, **(overrides.get(section) or {}))
        _write_receipt(rpath, payload)
        receipt_paths[section] = rpath
        receipts_manifest[section] = str(rpath)
    manifest_path = tmp_path / "receipt_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {"schema_version": "apps_rg.srfs_receipt_manifest.v1", "receipts": receipts_manifest},
            indent=2,
        ),
        encoding="utf-8",
    )
    return manifest_path, receipt_paths


def _collect_strings(obj: object, *, skip_non_claims: bool = False) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if skip_non_claims and k == "explicit_non_claims":
                continue
            out.extend(_collect_strings(v, skip_non_claims=skip_non_claims))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(_collect_strings(item, skip_non_claims=skip_non_claims))
    elif isinstance(obj, str):
        out.append(obj)
    return out


def _assert_no_forbidden_affirmative(report: dict) -> None:
    for text in _collect_strings(report, skip_non_claims=True):
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            assert phrase not in lower, f"forbidden phrase {phrase!r} in: {text!r}"


def test_pass_seven_valid_receipts_from_manifest(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded, receipt_manifest_ref=str(manifest_path))
    assert report["status"] == "PASS"
    assert report["proof_level"] == "SECTION_SRFS_STRUCTURAL_AUDIT_ONLY"
    assert not report["missing_sections"]
    _assert_no_forbidden_affirmative(report)


def test_pass_or_warn_receipt_root_discovery(tmp_path: Path) -> None:
    _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded, receipt_root=str(tmp_path))
    assert report["status"] in ("PASS", "WARN")
    assert len(report["observed_sections"]) == 7


def test_fail_missing_section(tmp_path: Path) -> None:
    manifest_path, paths = _write_seven_manifest(tmp_path)
    receipts = json.loads(manifest_path.read_text(encoding="utf-8"))["receipts"]
    del receipts["competencies"]
    manifest_path.write_text(
        json.dumps({"schema_version": "apps_rg.srfs_receipt_manifest.v1", "receipts": receipts}, indent=2),
        encoding="utf-8",
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"
    assert "competencies" in report["missing_sections"]


def test_fail_duplicate_section_id(tmp_path: Path) -> None:
    _write_seven_manifest(tmp_path)
    dup_dir = tmp_path / "headline_dup"
    _write_receipt(dup_dir / "section_metric_receipt.json", _valid_srfs_receipt("headline"))
    with pytest.raises(agg.AggregatorOperationalError, match="Duplicate section_id"):
        agg.load_section_receipts(receipt_root=tmp_path)


def test_fail_malformed_receipt_json(tmp_path: Path) -> None:
    manifest_path, paths = _write_seven_manifest(tmp_path)
    paths["headline"].write_text("{ not json", encoding="utf-8")
    with pytest.raises(agg.AggregatorOperationalError):
        agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)


def test_fail_pending_receipt(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"unify_bullets": {"status": "pending", "prompt_hash": "pendingonly"}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"
    assert report["cross_section_findings"]["any_pending_receipt"] is True


def test_fail_unknown_x2_when_srfs_active(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"ibm_bullets": {"x2_srfs_gate_status": "UNKNOWN"}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"


def test_fail_empty_prompt_hash_srfs_active(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"headline": {"prompt_hash": ""}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"


def test_fail_full_resume_srfs_supported_true(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"competencies": {"full_resume_srfs_supported": True}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"


def test_warn_extra_unknown_fields(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"headline": {"extra_audit_field": "benign"}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "WARN"


def test_report_explicit_non_claims_and_advisory_not_run(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert len(report["explicit_non_claims"]) >= 6
    aj = report["advisory_judge_review"]
    assert aj["status"] == "NOT_RUN"
    assert aj["enabled"] is False
    assert aj["can_change_deterministic_status"] is False


def test_fail_missing_srfs_field(tmp_path: Path) -> None:
    manifest_path, paths = _write_seven_manifest(tmp_path)
    bad = _valid_srfs_receipt("headline")
    del bad["x2_srfs_gate_status"]
    _write_receipt(paths["headline"], bad)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "FAIL"


def test_pass_x2_fail_allowed_structural(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(
        tmp_path,
        overrides={"executive_summary": {"x2_srfs_gate_status": "FAIL", "x3_code": "X3_BLOCK"}},
    )
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] == "PASS"
    assert report["cross_section_findings"]["any_section_x2_srfs_fail"] is True


def test_no_latest_successful_inference_in_source() -> None:
    text = AGG_SOURCE.read_text(encoding="utf-8").lower()
    assert "latest_successful" not in text
    assert "resolve_run_dir_from_latest" not in text


def test_latest_successful_pointer_ignored_by_root_discovery(tmp_path: Path) -> None:
    _write_seven_manifest(tmp_path / "runs")
    pointer = {
        "run_id": "phantom",
        "lane_id": "headline",
        "artifact_path": "somewhere",
    }
    (tmp_path / "latest_successful_real_run.json").write_text(json.dumps(pointer), encoding="utf-8")
    loaded = agg.load_section_receipts(receipt_root=tmp_path / "runs")
    assert len(loaded) == 7
    report = agg.build_srfs_audit_report(loaded)
    assert report["status"] in ("PASS", "WARN")


def test_load_rejects_non_receipt_file_in_manifest(tmp_path: Path) -> None:
    bad = tmp_path / "latest_successful_real_run.json"
    bad.write_text("{}", encoding="utf-8")
    manifest = {
        "schema_version": "apps_rg.srfs_receipt_manifest.v1",
        "receipts": {"headline": str(bad)},
    }
    mpath = tmp_path / "m.json"
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(agg.AggregatorOperationalError, match="section_metric_receipt.json"):
        agg.load_section_receipts(receipt_manifest_path=mpath, repo_root=tmp_path)


def test_cli_writes_report_exit_zero_on_fail_status(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(tmp_path / "fixtures")
    out_dir = tmp_path / "out"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg.audit.srfs_receipt_aggregator",
            "--receipt-manifest",
            str(manifest_path),
            "--out",
            str(out_dir),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert (out_dir / "apps_rg_srfs_audit_report.json").is_file()
    assert "deterministic_status=PASS" in proc.stdout
    assert "proof_level=SECTION_SRFS_STRUCTURAL_AUDIT_ONLY" in proc.stdout
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in proc.stdout.lower()


def test_advisory_mock_does_not_change_deterministic_status(tmp_path: Path) -> None:
    from apps_rg.audit.srfs_audit_advisory_judge import attach_advisory_judge_review

    manifest_path, _ = _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    before = report["status"]
    report = attach_advisory_judge_review(report, enable=True, mock=True)
    assert report["status"] == before
    aj = report["advisory_judge_review"]
    assert aj["enabled"] is True
    assert aj["mocked_or_live"] == "mocked"
    assert aj["can_change_deterministic_status"] is False
    assert aj["status"] in ("PASS", "WARN", "FAIL")


def test_advisory_enable_without_mock_stays_not_run(tmp_path: Path) -> None:
    from apps_rg.audit.srfs_audit_advisory_judge import attach_advisory_judge_review

    manifest_path, _ = _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    report = attach_advisory_judge_review(report, enable=True, mock=False)
    assert report["advisory_judge_review"]["status"] == "NOT_RUN"
    assert report["advisory_judge_review"]["mocked_or_live"] == "not_run"


def test_write_srfs_audit_report_paths(tmp_path: Path) -> None:
    manifest_path, _ = _write_seven_manifest(tmp_path)
    loaded = agg.load_section_receipts(receipt_manifest_path=manifest_path, repo_root=tmp_path)
    report = agg.build_srfs_audit_report(loaded)
    out = tmp_path / "report_out"
    jp, mp = agg.write_srfs_audit_report(report, out)
    assert jp.is_file()
    assert mp.is_file()
    md_text = mp.read_text(encoding="utf-8")
    _assert_no_forbidden_affirmative(json.loads(jp.read_text(encoding="utf-8")))
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in md_text.lower()
