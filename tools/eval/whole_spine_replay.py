"""Whole-spine offline replay runner.

The runner executes a scenario-owned runtime command and validates the receipt it
emits. It does not grade stored labels or reclassify prior outcomes; the command
is the seam where a pinned U0-to-L6 spine entrypoint is invoked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "whole_spine_replay_receipt.v1"


class ReplayConfigError(ValueError):
    """Scenario configuration is invalid."""


@dataclass(frozen=True, slots=True)
class ScenarioInputIdentity:
    jd_sha256: str
    briefing_sha256: str
    policy_sha256: dict[str, str]
    bundle_sha256: str


@dataclass(frozen=True, slots=True)
class BaselineComparison:
    status: str
    compared_fields: dict[str, dict[str, str | None]] = field(default_factory=dict)
    baseline_path: str | None = None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class WholeSpineReplayReceipt:
    schema_version: str
    scenario_id: str
    provider_mode: str
    expected_receipt_class: str
    input_identity: ScenarioInputIdentity
    command: list[str]
    cwd: str
    exit_code: int
    duration_ms: int
    runtime_receipt_path: str
    runtime_receipt_present: bool
    runtime_receipt_class: str | None
    runtime_receipt_sha256: str | None
    stdout_sha256: str
    stderr_sha256: str
    passed: bool
    reason_codes: list[str]
    baseline: BaselineComparison


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _resolve_path(raw: str, scenario_dir: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = scenario_dir / path
    return path.resolve()


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReplayConfigError(f"{name} must be a non-empty string")
    return value


def _input_identity(scenario: dict[str, Any], scenario_dir: Path) -> ScenarioInputIdentity:
    inputs = scenario.get("inputs")
    if not isinstance(inputs, dict):
        raise ReplayConfigError("inputs must be an object")

    jd_path = _resolve_path(_require_text(inputs.get("jd"), "inputs.jd"), scenario_dir)
    briefing_path = _resolve_path(
        _require_text(inputs.get("briefing"), "inputs.briefing"), scenario_dir
    )
    policies = inputs.get("policies")
    if not isinstance(policies, list) or not policies:
        raise ReplayConfigError("inputs.policies must be a non-empty list")

    for path in [jd_path, briefing_path]:
        if not path.is_file():
            raise ReplayConfigError(f"input file not found: {path}")

    policy_hashes: dict[str, str] = {}
    for raw in policies:
        policy_path = _resolve_path(_require_text(raw, "inputs.policies[]"), scenario_dir)
        if not policy_path.is_file():
            raise ReplayConfigError(f"policy file not found: {policy_path}")
        policy_hashes[str(policy_path)] = _sha256_file(policy_path)

    bundle = {
        "jd": {"path": str(jd_path), "sha256": _sha256_file(jd_path)},
        "briefing": {"path": str(briefing_path), "sha256": _sha256_file(briefing_path)},
        "policies": policy_hashes,
    }
    return ScenarioInputIdentity(
        jd_sha256=bundle["jd"]["sha256"],
        briefing_sha256=bundle["briefing"]["sha256"],
        policy_sha256=policy_hashes,
        bundle_sha256=_canonical_json_sha256(bundle),
    )


def _format_arg(value: str, substitutions: dict[str, str]) -> str:
    try:
        return value.format(**substitutions)
    except KeyError as exc:
        raise ReplayConfigError(f"unknown command placeholder: {exc}") from exc


def _command(scenario: dict[str, Any], scenario_path: Path, output_dir: Path, repo_root: Path) -> list[str]:
    command = scenario.get("command")
    if not isinstance(command, list) or not command:
        raise ReplayConfigError("command must be a non-empty list")
    substitutions = {
        "python": sys.executable,
        "repo_root": str(repo_root),
        "scenario_dir": str(scenario_path.parent),
        "scenario_path": str(scenario_path),
        "output_dir": str(output_dir),
    }
    return [_format_arg(_require_text(part, "command[]"), substitutions) for part in command]


def _runtime_receipt_path(
    scenario: dict[str, Any],
    scenario_path: Path,
    output_dir: Path,
    repo_root: Path,
) -> Path:
    raw = _require_text(scenario.get("runtime_receipt_path"), "runtime_receipt_path")
    substitutions = {
        "repo_root": str(repo_root),
        "scenario_dir": str(scenario_path.parent),
        "scenario_path": str(scenario_path),
        "output_dir": str(output_dir),
    }
    path = Path(_format_arg(raw, substitutions))
    if not path.is_absolute():
        path = scenario_path.parent / path
    return path.resolve()


def _receipt_class(payload: dict[str, Any]) -> str | None:
    for key in ("receipt_class", "receipt_type", "certification_level", "class"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _load_baseline(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.is_file():
        raise ReplayConfigError(f"baseline file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayConfigError("baseline must be a JSON object")
    return payload


def _baseline_for_scenario(baseline: dict[str, Any] | None, scenario_id: str) -> dict[str, Any] | None:
    if baseline is None:
        return None
    scenarios = baseline.get("scenarios", baseline)
    if not isinstance(scenarios, dict):
        raise ReplayConfigError("baseline.scenarios must be an object")
    item = scenarios.get(scenario_id)
    if item is None:
        return None
    if not isinstance(item, dict):
        raise ReplayConfigError(f"baseline for {scenario_id} must be an object")
    return item


def _compare_baseline(
    baseline_path: Path | None,
    baseline_item: dict[str, Any] | None,
    receipt: WholeSpineReplayReceipt,
) -> BaselineComparison:
    if baseline_item is None:
        return BaselineComparison(
            status="NOT_CONFIGURED" if baseline_path is None else "MISSING_SCENARIO",
            baseline_path=str(baseline_path) if baseline_path else None,
            reason="no baseline comparison requested" if baseline_path is None else "scenario absent",
        )

    actual = {
        "input_bundle_sha256": receipt.input_identity.bundle_sha256,
        "runtime_receipt_class": receipt.runtime_receipt_class,
        "runtime_receipt_sha256": receipt.runtime_receipt_sha256,
        "provider_mode": receipt.provider_mode,
        "expected_receipt_class": receipt.expected_receipt_class,
    }
    compared: dict[str, dict[str, str | None]] = {}
    mismatches: list[str] = []
    for field_name, actual_value in actual.items():
        expected_value = baseline_item.get(field_name)
        if expected_value is None:
            continue
        expected_text = str(expected_value)
        actual_text = None if actual_value is None else str(actual_value)
        compared[field_name] = {"baseline": expected_text, "candidate": actual_text}
        if actual_text != expected_text:
            mismatches.append(field_name)

    if mismatches:
        return BaselineComparison(
            status="REGRESSION",
            compared_fields=compared,
            baseline_path=str(baseline_path) if baseline_path else None,
            reason="mismatched fields: " + ", ".join(sorted(mismatches)),
        )
    return BaselineComparison(
        status="MATCH",
        compared_fields=compared,
        baseline_path=str(baseline_path) if baseline_path else None,
        reason="candidate matches baseline",
    )


def run_scenario(
    scenario_path: Path,
    output_dir: Path,
    repo_root: Path,
    baseline_path: Path | None = None,
    timeout_seconds: int = 120,
) -> WholeSpineReplayReceipt:
    scenario_path = scenario_path.resolve()
    output_dir = output_dir.resolve()
    repo_root = repo_root.resolve()
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    if not isinstance(scenario, dict):
        raise ReplayConfigError("scenario must be a JSON object")

    scenario_id = _require_text(scenario.get("scenario_id"), "scenario_id")
    provider_mode = _require_text(scenario.get("provider_mode"), "provider_mode")
    expected_class = _require_text(scenario.get("expected_receipt_class"), "expected_receipt_class")
    identity = _input_identity(scenario, scenario_path.parent)
    command = _command(scenario, scenario_path, output_dir, repo_root)
    runtime_receipt = _runtime_receipt_path(scenario, scenario_path, output_dir, repo_root)
    cwd_raw = scenario.get("cwd")
    cwd_substitutions = {
        "repo_root": str(repo_root),
        "scenario_dir": str(scenario_path.parent),
        "scenario_path": str(scenario_path),
        "output_dir": str(output_dir),
    }
    cwd = Path(_format_arg(str(cwd_raw), cwd_substitutions) if cwd_raw else str(repo_root))
    if not cwd.is_absolute():
        cwd = (scenario_path.parent / cwd).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            shell=False,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        stderr = stderr + f"\nTimed out after {timeout_seconds}s"
    duration_ms = int((time.monotonic() - start) * 1000)

    reason_codes: list[str] = []
    if exit_code != 0:
        reason_codes.append("COMMAND_NONZERO")

    receipt_present = runtime_receipt.is_file()
    receipt_payload: dict[str, Any] = {}
    receipt_hash: str | None = None
    actual_class: str | None = None
    if not receipt_present:
        reason_codes.append("RUNTIME_RECEIPT_MISSING")
    else:
        try:
            receipt_payload = json.loads(runtime_receipt.read_text(encoding="utf-8"))
            if not isinstance(receipt_payload, dict):
                reason_codes.append("RUNTIME_RECEIPT_NOT_OBJECT")
                receipt_payload = {}
        except json.JSONDecodeError:
            reason_codes.append("RUNTIME_RECEIPT_INVALID_JSON")
        receipt_hash = _sha256_file(runtime_receipt)
        actual_class = _receipt_class(receipt_payload)
        if actual_class != expected_class:
            reason_codes.append("RUNTIME_RECEIPT_CLASS_MISMATCH")
        receipt_provider_mode = receipt_payload.get("provider_mode")
        if isinstance(receipt_provider_mode, str) and receipt_provider_mode != provider_mode:
            reason_codes.append("PROVIDER_MODE_MISMATCH")

    placeholder = WholeSpineReplayReceipt(
        schema_version=SCHEMA_VERSION,
        scenario_id=scenario_id,
        provider_mode=provider_mode,
        expected_receipt_class=expected_class,
        input_identity=identity,
        command=command,
        cwd=str(cwd),
        exit_code=exit_code,
        duration_ms=duration_ms,
        runtime_receipt_path=str(runtime_receipt),
        runtime_receipt_present=receipt_present,
        runtime_receipt_class=actual_class,
        runtime_receipt_sha256=receipt_hash,
        stdout_sha256=_sha256_bytes(stdout.encode("utf-8")),
        stderr_sha256=_sha256_bytes(stderr.encode("utf-8")),
        passed=False,
        reason_codes=reason_codes,
        baseline=BaselineComparison(status="PENDING"),
    )
    baseline = _load_baseline(baseline_path)
    baseline_item = _baseline_for_scenario(baseline, scenario_id)
    comparison = _compare_baseline(baseline_path, baseline_item, placeholder)
    if comparison.status == "REGRESSION":
        reason_codes.append("BASELINE_REGRESSION")

    return replace(
        placeholder,
        passed=not reason_codes,
        reason_codes=reason_codes,
        baseline=comparison,
    )


def write_receipt(receipt: WholeSpineReplayReceipt, out_path: Path | None) -> None:
    payload = asdict(receipt)
    if out_path is None:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/eval/whole_spine_replay"))
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args(argv)

    try:
        receipt = run_scenario(
            scenario_path=args.scenario,
            output_dir=args.output_dir,
            repo_root=args.repo_root,
            baseline_path=args.baseline,
            timeout_seconds=args.timeout_seconds,
        )
    except (ReplayConfigError, OSError, json.JSONDecodeError) as exc:
        print(f"[CONFIG_ERROR] {exc}", file=sys.stderr)
        return 2

    write_receipt(receipt, args.out)
    return 0 if receipt.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
