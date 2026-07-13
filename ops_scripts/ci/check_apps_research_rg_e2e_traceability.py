"""Validate full-chain traceability and JUnit-backed certification evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
DEPENDENCIES = ROOT / "config/certification/apps_research_rg_e2e_dependencies.v1.json"
AUTHORITY = ROOT / "config/certification/apps_research_rg_e2e_authority_contract.v1.json"
REPORT = ROOT / "artifacts/apps_research_rg_e2e/certification_report.json"
EVIDENCE_MANIFEST = ROOT / "artifacts/apps_research_rg_e2e/evidence_manifest.json"
_CERTIFICATION_SOURCES = (
    ROOT / "ops_scripts/ci/check_apps_research_rg_e2e_traceability.py",
    ROOT / "ops_scripts/ci/check_apps_research_rg_full_chain_e2e.py",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"expected JSON object: {path}")
    return dict(value)


def _digest(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted({item.resolve() for item in paths}):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_file(ref: object) -> Path | None:
    raw = Path(str(ref or ""))
    if not str(raw) or raw.is_absolute() or ".." in raw.parts:
        return None
    target = (ROOT / raw).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    return target


def _group_maps(
    config: Mapping[str, Any],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    raw_groups = config.get("test_groups")
    raw_artifacts = config.get("test_group_artifacts")
    groups = dict(raw_groups) if isinstance(raw_groups, Mapping) else {}
    artifacts = dict(raw_artifacts) if isinstance(raw_artifacts, Mapping) else {}
    return (
        {
            str(group): [str(ref) for ref in refs]
            for group, refs in groups.items()
            if isinstance(refs, list)
        },
        {str(group): str(ref) for group, ref in artifacts.items()},
    )


def _trigger_source_files(pattern: str) -> tuple[Path, ...]:
    glob_pattern = pattern + "/*" if pattern.endswith("/**") else pattern
    return tuple(
        path.resolve()
        for path in ROOT.glob(glob_pattern)
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".pyo"}
    )


def certification_source_paths(
    config: Mapping[str, Any] | None = None,
    *,
    workflow_path: Path | None = None,
) -> tuple[Path, ...]:
    """Return every byte source that invalidates previously generated evidence."""

    config = dict(config) if config is not None else _load(DEPENDENCIES)
    groups, _ = _group_maps(config)
    workflow_path = workflow_path or _relative_file(config.get("workflow"))
    paths = [DEPENDENCIES, AUTHORITY, *_CERTIFICATION_SOURCES]
    if workflow_path is not None:
        paths.append(workflow_path)
    triggers = config.get("required_path_triggers")
    if isinstance(triggers, list):
        for pattern in triggers:
            paths.extend(_trigger_source_files(str(pattern)))
    for refs in groups.values():
        for ref in refs:
            path = _relative_file(ref)
            if path is not None:
                paths.append(path)
    return tuple(sorted({path.resolve() for path in paths}))


def certification_source_digest(
    config: Mapping[str, Any] | None = None,
    *,
    workflow_path: Path | None = None,
) -> str:
    return _digest(certification_source_paths(config, workflow_path=workflow_path))


def certification_source_mtime_ns(
    config: Mapping[str, Any] | None = None,
    *,
    workflow_path: Path | None = None,
) -> int:
    return max(
        path.stat().st_mtime_ns
        for path in certification_source_paths(config, workflow_path=workflow_path)
    )


def _structural_validation(
    config: Mapping[str, Any],
    authority: Mapping[str, Any],
) -> tuple[dict[str, list[str]], dict[str, str], Path | None, list[str]]:
    errors: list[str] = []
    workflow_path = _relative_file(config.get("workflow"))
    if workflow_path is None or not workflow_path.is_file():
        errors.append("workflow_ref_missing_or_unsafe")
        workflow = ""
    else:
        workflow = workflow_path.read_text(encoding="utf-8")

    triggers = config.get("required_path_triggers")
    triggers = triggers if isinstance(triggers, list) else []
    if not triggers:
        errors.append("required_path_triggers_empty")
    for trigger in triggers:
        if workflow.count(f'"{trigger}"') < 2:
            errors.append(f"workflow_trigger_missing_from_pr_or_push:{trigger}")

    groups, artifacts = _group_maps(config)
    raw_groups = config.get("test_groups")
    if not isinstance(raw_groups, Mapping):
        errors.append("test_groups_missing")
    else:
        for group, refs in raw_groups.items():
            if not isinstance(refs, list) or not refs:
                errors.append(f"test_group_empty_or_invalid:{group}")
    for group, refs in groups.items():
        if not refs:
            errors.append(f"test_group_empty:{group}")
        for ref in refs:
            path = _relative_file(ref)
            if path is None or not path.is_file():
                errors.append(f"test_ref_missing_or_unsafe:{group}:{ref}")
    if set(artifacts) != set(groups):
        errors.append("test_group_artifact_set_mismatch")
    for group, ref in artifacts.items():
        path = _relative_file(ref)
        if path is None or path.suffix != ".xml":
            errors.append(f"test_group_artifact_ref_invalid:{group}:{ref}")

    expected_requirements = {
        *(f"P0-{index:02d}" for index in range(1, 18)),
        *(f"P1-{index:02d}" for index in range(1, 13)),
    }
    raw_requirement_groups = config.get("requirement_groups")
    requirement_groups = (
        dict(raw_requirement_groups)
        if isinstance(raw_requirement_groups, Mapping)
        else {}
    )
    missing_requirements = sorted(expected_requirements - set(requirement_groups))
    extra_requirements = sorted(set(requirement_groups) - expected_requirements)
    if missing_requirements:
        errors.append("requirements_missing:" + ",".join(missing_requirements))
    if extra_requirements:
        errors.append("requirements_unknown:" + ",".join(extra_requirements))
    for requirement, group in requirement_groups.items():
        if group not in groups:
            errors.append(f"requirement_group_unknown:{requirement}:{group}")

    authority_rows = authority.get("stages")
    authority_rows = authority_rows if isinstance(authority_rows, list) else []
    authority_stages = [
        str(stage.get("stage_id") or "")
        for stage in authority_rows
        if isinstance(stage, Mapping)
    ]
    configured_stages = config.get("failure_injection_stages")
    configured_stages = (
        [str(stage) for stage in configured_stages]
        if isinstance(configured_stages, list)
        else []
    )
    if configured_stages != authority_stages:
        missing = [stage for stage in authority_stages if stage not in configured_stages]
        extra = [stage for stage in configured_stages if stage not in authority_stages]
        errors.append(
            "failure_injection_stage_matrix_mismatch:"
            f"missing={','.join(missing)}:extra={','.join(extra)}"
        )

    manifest_ref = _relative_file(config.get("evidence_manifest"))
    report_ref = _relative_file(config.get("certification_report"))
    if manifest_ref is None:
        errors.append("evidence_manifest_ref_missing_or_unsafe")
    if report_ref is None:
        errors.append("certification_report_ref_missing_or_unsafe")
    return groups, artifacts, workflow_path, errors


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _integer_attribute(element: ET.Element, name: str, errors: list[str]) -> int:
    raw = element.get(name)
    try:
        value = int(raw) if raw is not None else -1
    except ValueError:
        value = -1
    if value < 0:
        errors.append(f"junit_invalid_{name}_count")
        return 0
    return value


def read_junit_evidence(
    path: Path,
    *,
    expected_test_refs: Sequence[str] = (),
) -> tuple[dict[str, int | str], list[str]]:
    """Read one JUnit artifact without trusting a manifest-asserted result."""

    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        return (
            {"result": "FAIL", "tests": 0, "failures": 0, "errors": 0, "skipped": 0},
            [f"junit_unreadable:{type(exc).__name__}"],
        )
    suites = [
        element
        for element in root.iter()
        if _local_name(element.tag) == "testsuite"
        and not any(_local_name(child.tag) == "testsuite" for child in element)
    ]
    if not suites:
        errors.append("junit_has_no_test_suites")
    totals = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    for suite in suites:
        for name in totals:
            totals[name] += _integer_attribute(suite, name, errors)
    actual_tests = sum(
        1 for element in root.iter() if _local_name(element.tag) == "testcase"
    )
    actual_failures = sum(
        1 for element in root.iter() if _local_name(element.tag) == "failure"
    )
    actual_errors = sum(
        1 for element in root.iter() if _local_name(element.tag) == "error"
    )
    actual_skipped = sum(
        1 for element in root.iter() if _local_name(element.tag) == "skipped"
    )
    if totals["tests"] != actual_tests:
        errors.append("junit_declared_test_count_mismatch")
    if totals["failures"] != actual_failures:
        errors.append("junit_declared_failure_count_mismatch")
    if totals["errors"] != actual_errors:
        errors.append("junit_declared_error_count_mismatch")
    if totals["skipped"] != actual_skipped:
        errors.append("junit_declared_skipped_count_mismatch")
    if totals["tests"] <= 0:
        errors.append("junit_has_no_tests")
    classnames = {
        str(element.get("classname") or "")
        for element in root.iter()
        if _local_name(element.tag) == "testcase"
    }
    for ref in expected_test_refs:
        module = Path(ref).with_suffix("").as_posix().replace("/", ".")
        if not any(
            classname == module or classname.startswith(module + ".")
            for classname in classnames
        ):
            errors.append(f"junit_test_ref_not_collected:{ref}")
    result = (
        "PASS"
        if not errors and totals["failures"] == 0 and totals["errors"] == 0
        else "FAIL"
    )
    return {"result": result, **totals}, errors


def _read_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        manifest = _load(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {}, [f"evidence_manifest_unreadable:{type(exc).__name__}"]
    return manifest, []


def _evidence_validation(
    *,
    config: Mapping[str, Any],
    groups: Mapping[str, list[str]],
    artifacts: Mapping[str, str],
    source_digest: str,
    source_mtime_ns: int,
    manifest_path: Path,
    evidence_dir: Path | None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    manifest, global_errors = _read_manifest(manifest_path)
    if manifest.get("schema_version") != "apps_research_rg_e2e_evidence_manifest.v1":
        global_errors.append("evidence_manifest_schema_mismatch")
    if manifest.get("source_digest") != source_digest:
        global_errors.append("evidence_manifest_source_digest_mismatch")
    try:
        started_ns = int(manifest.get("run_started_at_ns"))
        completed_ns = int(manifest.get("run_completed_at_ns"))
    except (TypeError, ValueError):
        started_ns = completed_ns = -1
        global_errors.append("evidence_manifest_time_invalid")
    if started_ns < source_mtime_ns:
        global_errors.append("evidence_manifest_predates_certification_sources")
    if completed_ns < started_ns:
        global_errors.append("evidence_manifest_time_order_invalid")

    raw_manifest_groups = manifest.get("groups")
    manifest_groups = (
        dict(raw_manifest_groups) if isinstance(raw_manifest_groups, Mapping) else {}
    )
    if set(manifest_groups) != set(groups):
        global_errors.append("evidence_manifest_group_set_mismatch")

    group_evidence: dict[str, dict[str, Any]] = {}
    all_errors = list(global_errors)
    for group, refs in groups.items():
        errors = list(global_errors)
        row = manifest_groups.get(group)
        row = dict(row) if isinstance(row, Mapping) else {}
        expected_ref = artifacts.get(group, "")
        if row.get("artifact_ref") != expected_ref:
            errors.append(f"evidence_artifact_ref_mismatch:{group}")
        if row.get("test_refs") != refs:
            errors.append(f"evidence_test_refs_mismatch:{group}")
        try:
            return_code = int(row.get("return_code"))
        except (TypeError, ValueError):
            return_code = -1
        if return_code != 0:
            errors.append(f"evidence_test_command_failed:{group}:{return_code}")
        if str(row.get("runner_error") or ""):
            errors.append(f"evidence_test_runner_error:{group}")

        configured_path = _relative_file(expected_ref)
        artifact_path = (
            evidence_dir / Path(expected_ref).name
            if evidence_dir is not None and expected_ref
            else configured_path
        )
        summary: dict[str, Any] = {
            "result": "FAIL",
            "tests": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
        }
        if artifact_path is None or not artifact_path.is_file():
            errors.append(f"evidence_artifact_missing:{group}")
        else:
            modified_ns = artifact_path.stat().st_mtime_ns
            if modified_ns < started_ns or modified_ns < source_mtime_ns:
                errors.append(f"evidence_artifact_stale:{group}")
            if modified_ns > completed_ns:
                errors.append(f"evidence_artifact_postdates_manifest:{group}")
            artifact_digest = _sha256(artifact_path)
            if row.get("artifact_sha256") != artifact_digest:
                errors.append(f"evidence_artifact_digest_mismatch:{group}")
            summary, junit_errors = read_junit_evidence(
                artifact_path,
                expected_test_refs=refs,
            )
            errors.extend(f"{group}:{error}" for error in junit_errors)
        if errors or summary.get("result") != "PASS":
            summary["result"] = "FAIL"
        summary.update(
            {
                "artifact_ref": expected_ref,
                "artifact_sha256": (
                    _sha256(artifact_path)
                    if artifact_path is not None and artifact_path.is_file()
                    else ""
                ),
                "test_refs": refs,
                "evidence_errors": errors,
            }
        )
        group_evidence[group] = summary
        all_errors.extend(errors)
    return group_evidence, list(dict.fromkeys(all_errors))


def validate_traceability(
    *,
    mode: str = "structural",
    evidence_manifest_path: Path | None = None,
    evidence_dir: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Build a structural report or an evidence-backed certification report."""

    if mode not in {"structural", "evidence"}:
        raise ValueError(f"unknown traceability validation mode: {mode}")
    config = _load(DEPENDENCIES)
    authority = _load(AUTHORITY)
    groups, artifacts, workflow_path, structural_errors = _structural_validation(
        config,
        authority,
    )
    source_digest = certification_source_digest(config, workflow_path=workflow_path)
    source_mtime_ns = certification_source_mtime_ns(
        config,
        workflow_path=workflow_path,
    )

    group_evidence: dict[str, dict[str, Any]] = {}
    evidence_errors: list[str] = []
    manifest_path = evidence_manifest_path or EVIDENCE_MANIFEST
    if mode == "evidence":
        group_evidence, evidence_errors = _evidence_validation(
            config=config,
            groups=groups,
            artifacts=artifacts,
            source_digest=source_digest,
            source_mtime_ns=source_mtime_ns,
            manifest_path=manifest_path,
            evidence_dir=evidence_dir,
        )
    errors = list(dict.fromkeys([*structural_errors, *evidence_errors]))

    raw_requirement_groups = config.get("requirement_groups")
    requirement_groups = (
        dict(raw_requirement_groups)
        if isinstance(raw_requirement_groups, Mapping)
        else {}
    )
    requirements = []
    for requirement, group_value in sorted(requirement_groups.items()):
        group = str(group_value)
        evidence = group_evidence.get(group, {})
        requirement_result = (
            "NOT_RUN"
            if mode == "structural"
            else (
                "PASS"
                if not structural_errors and evidence.get("result") == "PASS"
                else "FAIL"
            )
        )
        requirements.append(
            {
                "requirement_id": requirement,
                "test_group": group,
                "test_refs": list(groups.get(group, [])),
                "artifact_ref": artifacts.get(group, ""),
                "result": requirement_result,
                "evidence_errors": list(evidence.get("evidence_errors", [])),
            }
        )

    validation_passed = not errors
    report = {
        "schema_version": "apps_research_rg_e2e_certification_report.v2",
        "authority_contract_id": authority.get("contract_id"),
        "evidence_mode": "JUNIT" if mode == "evidence" else "STRUCTURAL_ONLY",
        "source_digest": source_digest,
        "source_latest_mtime_ns": source_mtime_ns,
        "result": "PASS" if validation_passed else "FAIL",
        "certification_result": (
            "NOT_RUN"
            if mode == "structural"
            else "PASS"
            if validation_passed
            and all(item["result"] == "PASS" for item in requirements)
            else "FAIL"
        ),
        "errors": errors,
        "required_path_trigger_count": len(config.get("required_path_triggers", [])),
        "failure_injection_stages": list(config.get("failure_injection_stages", [])),
        "evidence_manifest": {
            "artifact_ref": str(config.get("evidence_manifest") or ""),
            "sha256": (
                _sha256(manifest_path)
                if mode == "evidence" and manifest_path.is_file()
                else ""
            ),
        },
        "group_evidence": group_evidence,
        "requirements": requirements,
    }
    return report, errors


def write_certification_report(report: Mapping[str, Any], path: Path = REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("structural", "evidence"), default="structural")
    parser.add_argument("--evidence-manifest", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args(argv)
    report, errors = validate_traceability(
        mode=args.mode,
        evidence_manifest_path=args.evidence_manifest,
        evidence_dir=args.evidence_dir,
    )
    write_certification_report(report, args.report)
    if errors:
        for error in errors:
            print(error)
        return 1
    if args.mode == "structural":
        print(
            "Apps Research -> Apps RG E2E traceability: STRUCTURAL PASS "
            f"({len(report['requirements'])} requirements; evidence not run)"
        )
    else:
        print(
            "Apps Research -> Apps RG E2E certification: PASS "
            f"({len(report['requirements'])} JUnit-backed requirements)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
