#!/usr/bin/env python3
"""APPS-TEST-MODEL - changed-file gate for apps_* test classification.

The gate enforces that changed app-owned test files carry an
``apps-test-model: <bucket>`` marker. It is changed-file scoped by default so
historical tests can be annotated incrementally.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DOC = REPO_ROOT / ".codex" / "skills" / "testing-framework" / "apps_testing_model.md"

CANONICAL_BUCKETS = {
    "LAW",
    "APP CONTRACT",
    "SPINE BINDING",
    "EVAL CONTRACT",
    "HARNESS",
    "MIGRATION",
    "ARCHAEOLOGY",
    "FUTURE",
}
BUCKET_ALIASES = {
    "CONTRACT": "APP CONTRACT",
    "APP": "APP CONTRACT",
    "SPINE": "SPINE BINDING",
    "EVAL": "EVAL CONTRACT",
}
_MARKER_RE = re.compile(r"apps-test-model\s*:\s*([A-Za-z][A-Za-z0-9 _/-]*)", re.IGNORECASE)


@dataclass(frozen=True)
class Violation:
    path: str
    code: str
    message: str


@dataclass(frozen=True)
class CheckResult:
    scanned: int
    violations: list[Violation]

    @property
    def ok(self) -> bool:
        return not self.violations


def _repo_relative(path: str | Path, repo_root: Path = REPO_ROOT) -> str:
    candidate = Path(path)
    try:
        if candidate.is_absolute():
            candidate = candidate.resolve().relative_to(repo_root.resolve())
    except ValueError:
        pass
    return candidate.as_posix()


def _parts(path: str | Path) -> list[str]:
    return [part for part in _repo_relative(path).replace("\\", "/").split("/") if part]


def is_app_test_path(path: str | Path) -> bool:
    """Return True for app-owned Python test surfaces."""

    rel = _repo_relative(path)
    if not rel.endswith(".py"):
        return False

    parts = _parts(path)
    if "tests" not in parts:
        return False
    test_index = parts.index("tests")
    after_tests = parts[test_index + 1 :]
    if not after_tests:
        return False

    if after_tests[0] == "_apps_contract":
        return True
    if after_tests[0] == "unit" and len(after_tests) > 1 and _is_app_package(after_tests[1]):
        return True
    return _is_app_package(after_tests[0])


def _is_app_package(segment: str) -> bool:
    return segment.startswith("apps_") and segment != "apps_shared"


def normalize_bucket(raw: str) -> str | None:
    value = raw.upper().replace("_", " ").replace("-", " ").replace("/", " ")
    value = re.sub(r"[^A-Z0-9 ]+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value in BUCKET_ALIASES:
        value = BUCKET_ALIASES[value]
    if value in CANONICAL_BUCKETS:
        return value
    return None


def marker_bucket(text: str) -> tuple[str | None, str | None]:
    match = _MARKER_RE.search(text)
    if not match:
        return None, None
    raw = match.group(1).strip()
    return raw, normalize_bucket(raw)


def check_paths(path_text: Mapping[str, str]) -> CheckResult:
    violations: list[Violation] = []
    scanned = 0
    for path, text in sorted(path_text.items()):
        if not is_app_test_path(path):
            continue
        scanned += 1
        raw, bucket = marker_bucket(text)
        if raw is None:
            violations.append(
                Violation(
                    path=_repo_relative(path),
                    code="missing_marker",
                    message="changed app test file is missing apps-test-model: <bucket>",
                )
            )
            continue
        if bucket is None:
            valid = ", ".join(sorted(CANONICAL_BUCKETS))
            violations.append(
                Violation(
                    path=_repo_relative(path),
                    code="invalid_bucket",
                    message=f"invalid apps-test-model bucket {raw!r}; expected one of: {valid}",
                )
            )
    return CheckResult(scanned=scanned, violations=violations)


def changed_files(repo_root: Path, *, base_ref: str | None = None) -> list[str]:
    has_head = True
    if not base_ref:
        head_check = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        has_head = head_check.returncode == 0

    if base_ref:
        args = ["git", "diff", "--name-only", f"{base_ref}...HEAD"]
    elif has_head:
        args = ["git", "diff", "--name-only", "HEAD"]
    else:
        args = []
    changed: list[str] = []
    if args:
        proc = subprocess.run(
            args,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git diff failed")
        changed = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if base_ref:
        return changed

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if untracked.returncode != 0:
        raise RuntimeError(untracked.stderr.strip() or untracked.stdout.strip() or "git ls-files failed")
    changed.extend(line.strip() for line in untracked.stdout.splitlines() if line.strip())
    return sorted(set(changed))


def all_tracked_files(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git ls-files failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def read_existing_paths(paths: Sequence[str], repo_root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in paths:
        candidate = Path(path)
        full_path = candidate if candidate.is_absolute() else repo_root / candidate
        if not full_path.exists() or not full_path.is_file():
            continue
        try:
            text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = full_path.read_text(encoding="utf-8", errors="ignore")
        out[_repo_relative(full_path, repo_root)] = text
    return out


def check_skill_doc(repo_root: Path = REPO_ROOT) -> list[Violation]:
    doc = repo_root / ".codex" / "skills" / "testing-framework" / "apps_testing_model.md"
    if not doc.is_file():
        return [
            Violation(
                path=_repo_relative(doc, repo_root),
                code="missing_skill_doc",
                message="apps testing model skill doc is missing",
            )
        ]
    text = doc.read_text(encoding="utf-8")
    required = [
        "apps_* tests do not protect old app implementation",
        "apps_* tests protect governed product behavior",
        "## APPS_TEST_TRIAGE",
        "ops_scripts/ci/check_apps_test_model.py",
    ]
    violations = []
    for anchor in required:
        if anchor not in text:
            violations.append(
                Violation(
                    path=_repo_relative(doc, repo_root),
                    code="missing_skill_anchor",
                    message=f"skill doc missing anchor: {anchor}",
                )
            )
    return violations


def write_report(path: Path, result: CheckResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "gate": "APPS-TEST-MODEL",
        "scanned": result.scanned,
        "violations": [violation.__dict__ for violation in result.violations],
        "ok": result.ok,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", default=None, help="Explicit files to check")
    parser.add_argument("--all", action="store_true", help="Check all tracked files")
    parser.add_argument("--base-ref", default=None, help="Check git diff from base...HEAD")
    parser.add_argument("--report-json", type=Path, default=None)
    parser.add_argument("--skip-doc-check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()

    try:
        if args.paths is not None:
            paths = args.paths
        elif args.all:
            paths = all_tracked_files(repo_root)
        else:
            paths = changed_files(repo_root, base_ref=args.base_ref)
        path_text = read_existing_paths(paths, repo_root)
        result = check_paths(path_text)
        if not args.skip_doc_check:
            result = CheckResult(
                scanned=result.scanned,
                violations=[*check_skill_doc(repo_root), *result.violations],
            )
    except Exception as exc:  # guardian: allow-broad-exception -- CLI gate reports fail-closed
        print(f"APPS-TEST-MODEL: ERROR - {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if args.report_json is not None:
        write_report(args.report_json, result)

    if result.ok:
        print(f"APPS-TEST-MODEL: OK - scanned {result.scanned} changed app test file(s)")
        return 0

    print(f"APPS-TEST-MODEL: FAIL - {len(result.violations)} violation(s)", file=sys.stderr)
    for violation in result.violations:
        print(
            f"{violation.path}: {violation.code}: {violation.message}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
