"""Lightweight verification runner for repository runtime and layout checks."""

from __future__ import annotations

import argparse
import json
import py_compile
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
    get_validated_project_root,
)


PROJECT_ROOT = get_validated_project_root()


@dataclass(slots=True)
class VerificationResult:
    name: str
    passed: bool
    details: str


def verify_required_directories() -> VerificationResult:
    required = [PROJECT_ROOT / AGENTIC_CORE_DIR, PROJECT_ROOT / TESTS_DIR]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required if not path.exists()]
    return VerificationResult(
        name="required_directories",
        passed=not missing,
        details="OK" if not missing else f"Missing: {missing}",
    )


def verify_tempfile_writes() -> VerificationResult:
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = Path(tmp_dir) / "verification_probe.txt"
        target.write_text("ok", encoding="utf-8")
        passed = target.read_text(encoding="utf-8") == "ok"
    return VerificationResult(name="tempfile_writes", passed=passed, details="Temporary write round-trip")


def verify_compile_subset(limit: int = 25) -> VerificationResult:
    checked = 0
    for path in sorted(PROJECT_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        py_compile.compile(str(path), doraise=True)
        checked += 1
        if checked >= limit:
            break
    return VerificationResult(name="compile_subset", passed=True, details=f"Compiled {checked} Python files")


def run_checks() -> list[VerificationResult]:
    return [
        verify_required_directories(),
        verify_tempfile_writes(),
        verify_compile_subset(),
    ]


def main(json_output: bool = False) -> int:
    results = run_checks()
    failed = [result for result in results if not result.passed]
    if json_output:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.name}: {result.details}")
    return 0 if not failed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run lightweight repository verification checks.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    raise SystemExit(main(json_output=parser.parse_args().json))
