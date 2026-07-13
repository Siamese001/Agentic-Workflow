"""Execute all certification groups and emit digest-bound JUnit evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ops_scripts.ci.check_apps_research_rg_e2e_traceability import (
    certification_source_digest,
    validate_traceability,
    write_certification_report,
)

DEPENDENCIES = ROOT / "config/certification/apps_research_rg_e2e_dependencies.v1.json"
_COMMAND_TIMEOUT_SECONDS = 900


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_config() -> dict[str, Any]:
    payload = json.loads(DEPENDENCIES.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("certification dependencies must be a JSON object")
    return payload


def _relative_path(ref: object) -> Path:
    raw = Path(str(ref or ""))
    if not str(raw) or raw.is_absolute() or ".." in raw.parts:
        raise ValueError(f"unsafe certification artifact ref: {ref!r}")
    target = (ROOT / raw).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"unsafe certification artifact ref: {ref!r}") from exc
    return target


def _load_groups(
    config: Mapping[str, Any],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    raw_groups = config.get("test_groups")
    raw_artifacts = config.get("test_group_artifacts")
    if not isinstance(raw_groups, Mapping):
        raise ValueError("certification dependencies must declare test_groups")
    if not isinstance(raw_artifacts, Mapping):
        raise ValueError("certification dependencies must declare test_group_artifacts")
    groups: dict[str, list[str]] = {}
    for group, refs in raw_groups.items():
        if not isinstance(refs, list) or not refs:
            raise ValueError(f"certification test group is empty: {group}")
        normalized = [str(ref) for ref in refs]
        missing = [ref for ref in normalized if not (ROOT / ref).is_file()]
        if missing:
            raise FileNotFoundError(
                f"certification test group {group} has missing refs: {missing}"
            )
        groups[str(group)] = normalized
    artifacts = {str(group): str(ref) for group, ref in raw_artifacts.items()}
    if set(groups) != set(artifacts):
        raise ValueError("test_group_artifacts must exactly cover test_groups")
    for ref in artifacts.values():
        if _relative_path(ref).suffix != ".xml":
            raise ValueError(f"certification evidence is not JUnit XML: {ref}")
    return groups, artifacts


def _write_evidence_manifest(
    *,
    path: Path,
    config: Mapping[str, Any],
    groups: Mapping[str, list[str]],
    artifacts: Mapping[str, str],
    results: Mapping[str, Mapping[str, Any]],
    started_ns: int,
    completed_ns: int,
) -> None:
    group_rows: dict[str, dict[str, Any]] = {}
    for group, refs in groups.items():
        artifact_ref = artifacts[group]
        artifact_path = _relative_path(artifact_ref)
        result = results.get(group, {})
        group_rows[group] = {
            "artifact_ref": artifact_ref,
            "artifact_sha256": _sha256(artifact_path) if artifact_path.is_file() else "",
            "test_refs": list(refs),
            "return_code": result.get("return_code", -1),
            "runner_error": str(result.get("runner_error") or ""),
        }
    payload = {
        "schema_version": "apps_research_rg_e2e_evidence_manifest.v1",
        "source_digest": certification_source_digest(config),
        "run_started_at_ns": started_ns,
        "run_completed_at_ns": completed_ns,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "groups": group_rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    structural_report, structural_errors = validate_traceability(mode="structural")
    if structural_errors:
        write_certification_report(structural_report)
        for error in structural_errors:
            print(error)
        return 1

    config = _load_config()
    groups, artifacts = _load_groups(config)
    manifest_path = _relative_path(config.get("evidence_manifest"))
    report_path = _relative_path(config.get("certification_report"))
    for artifact_ref in artifacts.values():
        artifact_path = _relative_path(artifact_ref)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.unlink(missing_ok=True)
    manifest_path.unlink(missing_ok=True)

    started_ns = time.time_ns()
    results: dict[str, dict[str, Any]] = {}
    for group, refs in groups.items():
        artifact_path = _relative_path(artifacts[group])
        command = [
            sys.executable,
            "-m",
            "pytest",
            *refs,
            "-o",
            "addopts=",
            "-q",
            "--tb=short",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"--junitxml={artifact_path}",
        ]
        print("+", " ".join(command), flush=True)
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                shell=False,
                timeout=_COMMAND_TIMEOUT_SECONDS,
            )
            results[group] = {
                "return_code": completed.returncode,
                "runner_error": "",
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            results[group] = {
                "return_code": -1,
                "runner_error": f"{type(exc).__name__}:{exc}",
            }
            print(f"certification group {group} runner error: {exc}", flush=True)

    completed_ns = time.time_ns()
    _write_evidence_manifest(
        path=manifest_path,
        config=config,
        groups=groups,
        artifacts=artifacts,
        results=results,
        started_ns=started_ns,
        completed_ns=completed_ns,
    )
    report, errors = validate_traceability(
        mode="evidence",
        evidence_manifest_path=manifest_path,
    )
    write_certification_report(report, report_path)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        "Apps Research -> Apps RG full-chain certification: PASS "
        f"({len(report['requirements'])} JUnit-backed requirements)",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
