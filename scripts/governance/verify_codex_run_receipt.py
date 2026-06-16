"""Validate Codex primary execution run receipts.

The receipt is the disk artifact that makes a Codex run auditable without
mining chat history. It records run scope, repo state, commands, verification,
fallbacks, and RCA when execution fails or blocks.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "codex-run-receipt/v1"
EXECUTION_STATUSES = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}
CHECK_STATUSES = {"PASS", "FAIL", "SKIPPED", "BLOCKED"}
FAILURE_STATUSES = {"FAIL", "BLOCKED"}
RCA_FIELDS = ("symptom", "root_cause", "evidence", "fix_or_next", "recurrence_guard")


def _non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _require_mapping(parent: Mapping[str, Any], key: str, failures: list[str]) -> Mapping[str, Any]:
    value = parent.get(key)
    if not isinstance(value, Mapping):
        failures.append(f"{key}: expected object")
        return {}
    return value


def _require_list(parent: Mapping[str, Any], key: str, failures: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        failures.append(f"{key}: expected list")
        return []
    return value


def _validate_string_field(parent: Mapping[str, Any], path: str, failures: list[str]) -> None:
    value = parent
    parts = path.split(".")
    for part in parts[:-1]:
        nested = value.get(part)
        if not isinstance(nested, Mapping):
            failures.append(f"{path}: missing parent object {part!r}")
            return
        value = nested
    if not _non_empty_str(value.get(parts[-1])):
        failures.append(f"{path}: expected non-empty string")


def _validate_bool_field(parent: Mapping[str, Any], path: str, failures: list[str]) -> None:
    value = parent
    parts = path.split(".")
    for part in parts[:-1]:
        nested = value.get(part)
        if not isinstance(nested, Mapping):
            failures.append(f"{path}: missing parent object {part!r}")
            return
        value = nested
    if not _is_bool(value.get(parts[-1])):
        failures.append(f"{path}: expected boolean")


def _validate_commands(commands: list[Any], failures: list[str]) -> bool:
    saw_failure = False
    for index, item in enumerate(commands):
        if not isinstance(item, Mapping):
            failures.append(f"execution.commands[{index}]: expected object")
            continue
        for field in ("command", "cwd", "status"):
            if not _non_empty_str(item.get(field)):
                failures.append(f"execution.commands[{index}].{field}: expected non-empty string")
        status = item.get("status")
        if status not in CHECK_STATUSES:
            failures.append(f"execution.commands[{index}].status: expected one of {sorted(CHECK_STATUSES)}")
        if status in FAILURE_STATUSES:
            saw_failure = True
        exit_code = item.get("exit_code")
        if exit_code is not None and not isinstance(exit_code, int):
            failures.append(f"execution.commands[{index}].exit_code: expected integer or null")
    return saw_failure


def _validate_checks(checks: list[Any], failures: list[str]) -> bool:
    saw_failure = False
    if not checks:
        failures.append("verification.checks: expected at least one verification check")
    for index, item in enumerate(checks):
        if not isinstance(item, Mapping):
            failures.append(f"verification.checks[{index}]: expected object")
            continue
        for field in ("name", "status", "evidence"):
            if not _non_empty_str(item.get(field)):
                failures.append(f"verification.checks[{index}].{field}: expected non-empty string")
        status = item.get("status")
        if status not in CHECK_STATUSES:
            failures.append(f"verification.checks[{index}].status: expected one of {sorted(CHECK_STATUSES)}")
        if status in FAILURE_STATUSES:
            saw_failure = True
    return saw_failure


def _validate_fallbacks(fallbacks: list[Any], failures: list[str]) -> None:
    for index, item in enumerate(fallbacks):
        if not isinstance(item, Mapping):
            failures.append(f"execution.fallbacks[{index}]: expected object")
            continue
        for field in ("route", "reason", "substitute"):
            if not _non_empty_str(item.get(field)):
                failures.append(f"execution.fallbacks[{index}].{field}: expected non-empty string")


def _validate_rca(receipt: Mapping[str, Any], failures: list[str]) -> None:
    rca = receipt.get("rca")
    if not isinstance(rca, Mapping):
        failures.append("rca: required when execution fails or blocks")
        return
    for field in RCA_FIELDS:
        if not _non_empty_str(rca.get(field)):
            failures.append(f"rca.{field}: expected non-empty string")


def validate_receipt(receipt: Mapping[str, Any]) -> list[str]:
    """Return validation failures for a Codex run receipt."""
    failures: list[str] = []

    if receipt.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"schema_version: expected {SCHEMA_VERSION!r}")

    for field in ("run_id", "generated_at"):
        if not _non_empty_str(receipt.get(field)):
            failures.append(f"{field}: expected non-empty string")

    repo = _require_mapping(receipt, "repo", failures)
    scope = _require_mapping(receipt, "scope", failures)
    execution = _require_mapping(receipt, "execution", failures)
    verification = _require_mapping(receipt, "verification", failures)

    for path in ("repo.root", "repo.worktree", "repo.branch", "repo.head"):
        _validate_string_field(receipt, path, failures)
    for path in ("repo.dirty_before", "repo.dirty_after"):
        _validate_bool_field(receipt, path, failures)
    for path in ("scope.request", "scope.plan_id"):
        _validate_string_field(receipt, path, failures)

    files_changed = _require_list(scope, "files_changed", failures)
    for index, item in enumerate(files_changed):
        if not _non_empty_str(item):
            failures.append(f"scope.files_changed[{index}]: expected non-empty string")

    status = execution.get("status")
    if status not in EXECUTION_STATUSES:
        failures.append(f"execution.status: expected one of {sorted(EXECUTION_STATUSES)}")

    commands_failed = _validate_commands(_require_list(execution, "commands", failures), failures)
    _validate_fallbacks(execution.get("fallbacks", []), failures) if isinstance(execution.get("fallbacks", []), list) else failures.append("execution.fallbacks: expected list")
    checks_failed = _validate_checks(_require_list(verification, "checks", failures), failures)

    if status in FAILURE_STATUSES or commands_failed or checks_failed:
        _validate_rca(receipt, failures)

    return failures


def load_receipt(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Path to a Codex run receipt JSON file")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures = validate_receipt(load_receipt(args.receipt))
    if failures:
        print("Codex run receipt validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Codex run receipt validation passed")
    print(f"- receipt: {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
