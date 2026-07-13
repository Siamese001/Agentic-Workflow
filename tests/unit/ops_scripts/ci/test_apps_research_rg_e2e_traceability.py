from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from ops_scripts.ci import check_apps_research_rg_e2e_traceability as subject


def _write_junit(
    path: Path,
    *,
    test_refs: tuple[str, ...] = ("certification.py",),
    failures: int = 0,
) -> None:
    testcases = []
    for index, ref in enumerate(test_refs):
        failure = (
            '<failure message="injected">failed</failure>'
            if failures and index == 0
            else ""
        )
        module = Path(ref).with_suffix("").as_posix().replace("/", ".")
        testcases.append(
            f'<testcase classname="{module}" name="test_evidence_{index}">'
            f"{failure}</testcase>"
        )
    path.write_text(
        (
            f'<testsuites><testsuite name="certification" tests="{len(test_refs)}" '
            f'failures="{failures}" errors="0" skipped="0">'
            f"{''.join(testcases)}</testsuite></testsuites>"
        ),
        encoding="utf-8",
    )


def _evidence_fixture(tmp_path: Path) -> tuple[Path, int, dict[str, Path]]:
    config = json.loads(subject.DEPENDENCIES.read_text(encoding="utf-8"))
    started_ns = max(time.time_ns(), subject.certification_source_mtime_ns() + 1)
    artifact_paths: dict[str, Path] = {}
    manifest_groups: dict[str, dict[str, object]] = {}
    for offset, (group, artifact_ref) in enumerate(
        config["test_group_artifacts"].items(),
        start=1,
    ):
        artifact = tmp_path / Path(artifact_ref).name
        test_refs = tuple(config["test_groups"][group])
        _write_junit(artifact, test_refs=test_refs)
        modified_ns = started_ns + offset
        os.utime(artifact, ns=(modified_ns, modified_ns))
        artifact_paths[group] = artifact
        manifest_groups[group] = {
            "artifact_ref": artifact_ref,
            "artifact_sha256": "sha256:"
            + hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "test_refs": list(test_refs),
            "return_code": 0,
            "runner_error": "",
        }
    manifest = tmp_path / "evidence_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "apps_research_rg_e2e_evidence_manifest.v1",
                "source_digest": subject.certification_source_digest(),
                "run_started_at_ns": started_ns,
                "run_completed_at_ns": started_ns + len(artifact_paths) + 1,
                "groups": manifest_groups,
            }
        ),
        encoding="utf-8",
    )
    return manifest, started_ns, artifact_paths


def test_full_chain_dependencies_and_requirements_are_structurally_traceable() -> None:
    report, errors = subject.validate_traceability(mode="structural")
    assert errors == []
    assert report["result"] == "PASS"
    assert report["certification_result"] == "NOT_RUN"
    assert report["evidence_mode"] == "STRUCTURAL_ONLY"
    assert len(report["requirements"]) == 29
    assert {row["result"] for row in report["requirements"]} == {"NOT_RUN"}
    assert len(report["failure_injection_stages"]) == 26
    assert report["source_digest"].startswith("sha256:")


def test_failure_matrix_exactly_matches_every_authority_contract_stage() -> None:
    dependencies = json.loads(subject.DEPENDENCIES.read_text(encoding="utf-8"))
    authority = json.loads(subject.AUTHORITY.read_text(encoding="utf-8"))
    assert dependencies["failure_injection_stages"] == [
        row["stage_id"] for row in authority["stages"]
    ]


def test_evidence_mode_derives_every_requirement_from_fresh_junit(tmp_path: Path) -> None:
    manifest, _, _ = _evidence_fixture(tmp_path)
    report, errors = subject.validate_traceability(
        mode="evidence",
        evidence_manifest_path=manifest,
        evidence_dir=tmp_path,
    )
    assert errors == []
    assert report["result"] == "PASS"
    assert report["certification_result"] == "PASS"
    assert report["evidence_mode"] == "JUNIT"
    assert {row["result"] for row in report["requirements"]} == {"PASS"}
    config = json.loads(subject.DEPENDENCIES.read_text(encoding="utf-8"))
    assert all(
        row["tests"] == len(config["test_groups"][group])
        for group, row in report["group_evidence"].items()
    )


def test_evidence_mode_fails_closed_when_junit_is_missing(tmp_path: Path) -> None:
    manifest, _, artifacts = _evidence_fixture(tmp_path)
    artifacts["eval_purity"].unlink()
    report, errors = subject.validate_traceability(
        mode="evidence",
        evidence_manifest_path=manifest,
        evidence_dir=tmp_path,
    )
    assert "evidence_artifact_missing:eval_purity" in errors
    assert report["certification_result"] == "FAIL"
    assert {
        row["result"]
        for row in report["requirements"]
        if row["test_group"] == "eval_purity"
    } == {"FAIL"}


def test_evidence_mode_fails_closed_when_junit_predates_run(tmp_path: Path) -> None:
    manifest, started_ns, artifacts = _evidence_fixture(tmp_path)
    stale = artifacts["producer_u0"]
    os.utime(stale, ns=(started_ns - 1, started_ns - 1))
    report, errors = subject.validate_traceability(
        mode="evidence",
        evidence_manifest_path=manifest,
        evidence_dir=tmp_path,
    )
    assert "evidence_artifact_stale:producer_u0" in errors
    assert report["certification_result"] == "FAIL"


def test_junit_parser_rejects_declared_counts_without_matching_nodes(
    tmp_path: Path,
) -> None:
    junit = tmp_path / "counts.xml"
    junit.write_text(
        '<testsuite tests="2" failures="0" errors="0" skipped="0">'
        '<testcase name="only_one"/></testsuite>',
        encoding="utf-8",
    )
    summary, errors = subject.read_junit_evidence(junit)
    assert summary["result"] == "FAIL"
    assert "junit_declared_test_count_mismatch" in errors


def test_junit_parser_requires_evidence_from_every_configured_test_ref(
    tmp_path: Path,
) -> None:
    junit = tmp_path / "coverage.xml"
    _write_junit(junit, test_refs=("tests/unit/test_one.py",))
    summary, errors = subject.read_junit_evidence(
        junit,
        expected_test_refs=(
            "tests/unit/test_one.py",
            "tests/unit/test_missing.py",
        ),
    )
    assert summary["result"] == "FAIL"
    assert "junit_test_ref_not_collected:tests/unit/test_missing.py" in errors


def test_checked_in_dependency_ssot_is_valid_json() -> None:
    payload = json.loads(subject.DEPENDENCIES.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "apps_research_rg_e2e_dependencies.v1"
    assert len(payload["required_path_triggers"]) >= 30
