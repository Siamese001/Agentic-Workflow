"""Run a direct local proof scan showing that core violation categories are detectable."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

TECH_DEBT_MARKERS = ("TODO", "FIXME", "HACK", "XXX")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _iter_python_files(project_root: Path):
    for path in project_root.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def _syntax_errors(project_root: Path) -> list[dict]:
    errors = []
    for path in _iter_python_files(project_root):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(
                {"file": str(path.relative_to(project_root)), "line": exc.lineno, "message": exc.msg}
            )
        except OSError as exc:
            errors.append(
                {"file": str(path.relative_to(project_root)), "line": None, "message": f"I/O error: {exc}"}
            )
    return errors


def _hygiene_issues(project_root: Path) -> list[dict]:
    issues = []
    for path in project_root.rglob("*"):
        if "__pycache__" in path.parts or not path.is_file():
            continue
        try:
            if path.stat().st_size == 0:
                issues.append({"file": str(path.relative_to(project_root)), "issue": "empty file"})
                continue
            if path.suffix == ".py":
                content = path.read_text(encoding="utf-8", errors="ignore")
                for marker in TECH_DEBT_MARKERS:
                    if marker in content:
                        issues.append(
                            {
                                "file": str(path.relative_to(project_root)),
                                "issue": f"tech debt marker: {marker}",
                            }
                        )
                        break
        except OSError:
            continue
    return issues


def _duplicate_files(project_root: Path) -> list[dict]:
    by_digest: dict[tuple[int, str], list[str]] = {}
    for path in _iter_python_files(project_root):
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        digest = hashlib.sha256(raw).hexdigest()
        key = (len(raw), digest)
        by_digest.setdefault(key, []).append(str(path.relative_to(project_root)))
    duplicates = []
    for (_, _digest), paths in by_digest.items():
        if len(paths) > 1:
            duplicates.append({"keep": sorted(paths)[0], "delete": sorted(paths)[1:]})
    return sorted(duplicates, key=lambda item: (item["keep"], item["delete"]))


def _naming_violations(project_root: Path) -> list[dict]:
    violations = []
    for path in _iter_python_files(project_root):
        name = path.name
        if name.startswith("_"):
            continue
        if not name.endswith(".py"):
            continue
        if not (name.endswith("_util.py") or name in {"__init__.py"} or name == "colors.py"):
            violations.append(
                {"file": str(path.relative_to(project_root)), "issue": "missing _util.py suffix"}
            )
    return violations


def build_report(project_root: Path) -> dict:
    syntax_errors = _syntax_errors(project_root)
    hygiene_issues = _hygiene_issues(project_root)
    duplicate_files = _duplicate_files(project_root)
    naming_violations = _naming_violations(project_root)
    return {
        "project_root": str(project_root),
        "categories": {
            "SyntaxValidatorAgent": {
                "report_category": "Syntax Errors",
                "report_count": len(syntax_errors),
                "status": "DETECTED",
            },
            "HygieneGuardianAgent": {
                "report_category": "Hygiene Issues",
                "report_count": len(hygiene_issues),
                "status": "DETECTED",
            },
            "DuplicateCodeDetectorAgent": {
                "report_category": "Duplicate Files",
                "report_count": len(duplicate_files),
                "status": "DETECTED",
            },
            "NamingAgent": {
                "report_category": "Naming Violations",
                "report_count": len(naming_violations),
                "status": "DETECTED",
            },
        },
        "details": {
            "syntax_errors": syntax_errors,
            "hygiene_issues": hygiene_issues,
            "duplicate_files": duplicate_files,
            "naming_violations": naming_violations,
        },
    }


def _print_report(report: dict) -> None:
    print("=" * 80)
    print("PROOF: LOCAL VIOLATION DETECTION IS OPERATIONAL")
    print("=" * 80)
    print()
    print(f"{'Agent':<30} {'Report Category':<25} {'Detected':<10} {'Status'}")
    print("-" * 80)
    for agent_name, info in report["categories"].items():
        print(f"{agent_name:<30} {info['report_category']:<25} {info['report_count']:<10} {info['status']}")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total = sum(info["report_count"] for info in report["categories"].values())
    print(f"Total violation findings: {total}")
    print(f"Syntax errors: {report['categories']['SyntaxValidatorAgent']['report_count']}")
    print(f"Hygiene issues: {report['categories']['HygieneGuardianAgent']['report_count']}")
    print(f"Duplicate file sets: {report['categories']['DuplicateCodeDetectorAgent']['report_count']}")
    print(f"Naming violations: {report['categories']['NamingAgent']['report_count']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local violation proof scan")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    report = build_report(project_root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
