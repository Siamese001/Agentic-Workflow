#!/usr/bin/env python3
"""
STUB/PLACEHOLDER AUDIT
======================
Identifies all stub, placeholder, and empty files in the repository.
Categorizes them for cleanup or implementation.
"""

import scripts.check_canonical_structure
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
import json

REPO_ROOT = Path(__file__).parent.parent.resolve()

STUB_PATTERNS = [
    r'^\s*$',                          # Empty
    r'^\s*pass\s*$',                   # Just pass
    r'^\s*#.*\n\s*pass\s*$',           # Comment + pass
    r'raise\s+NotImplementedError',    # NotImplementedError
    r'PENDING',                           # Implementation pending
    r'PLACEHOLDER',                    # Placeholder markers
    r'STUB',                               r'ATTENTION',                          # Implementation pending
    r'XXX',                                r'\.\.\.(?:\s*#.*)?$',             # Ellipsis (...)
]

# Folders to skip
SKIP_FOLDERS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '06_data'}

def is_stub_file(file_path: Path) -> Tuple[bool, str]:
    """Check if a file is a stub/placeholder. Returns (is_stub, reason)."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore').strip()

        # Empty file
        if not content:
            return True, "empty"

        # Very short file (likely just pass or similar)
        if len(content) < 20:
            if content in ['pass', '...']:
                return True, "minimal_stub"
    
        for pattern in STUB_PATTERNS:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                if 'NotImplementedError' in content:
                    return True, "not_implemented"
                if 'PENDING' in content.upper():
                    return True, "todo_marker"
                if 'PLACEHOLDER' in content.upper():
                    return True, "placeholder_marker"
                if 'STUB' in content.upper():
                    return True, "stub_marker"
                if content.strip() == 'pass' or re.match(r'^\s*#.*\n\s*pass\s*$', content):
                    return True, "pass_only"
                if content.strip() == '...':
                    return True, "ellipsis_only"

        # Check for minimal docstring + pass pattern
        if re.match(r'^"""[^"]*"""\s*\n\s*pass\s*$', content, re.DOTALL):
            return True, "docstring_pass"

        # Check for function/class with only pass
        if re.search(r'def\s+\w+\([^)]*\):\s*\n\s*pass\s*$', content, re.MULTILINE):
            return True, "empty_function"
        if re.search(r'class\s+\w+[^:]*:\s*\n\s*pass\s*$', content, re.MULTILINE):
            return True, "empty_class"

        return False, "has_content"

    except (ValueError, TypeError, KeyError) as e:
        return False, f"error: {e}"

def audit_stubs() -> Dict:
    """Audit all Python files for stubs/placeholders."""
    report = {
        "summary": {
            "total_py_files": 0,
            "stub_files": 0,
            "real_files": 0,
        },
        "by_reason": defaultdict(list),
        "by_folder": defaultdict(lambda: {"stubs": 0, "real": 0, "files": []}),
        "stubs": [],
        "recommendations": [],
    }

    for py_file in REPO_ROOT.rglob("*.py"):
        # Skip certain folders
        if any(skip in py_file.parts for skip in SKIP_FOLDERS):
            continue

        # Skip __init__.py files
        if py_file.name == "__init__.py":
            continue

        report["summary"]["total_py_files"] += 1
        rel_path = str(py_file.relative_to(REPO_ROOT))

        # Get top-level folder
        parts = py_file.relative_to(REPO_ROOT).parts
        top_folder = parts[0] if parts else "root"

        is_stub, reason = is_stub_file(py_file)

        if is_stub:
            report["summary"]["stub_files"] += 1
            report["by_reason"][reason].append(rel_path)
            report["by_folder"][top_folder]["stubs"] += 1
            report["by_folder"][top_folder]["files"].append(rel_path)
            report["stubs"].append({
                "path": rel_path,
                "reason": reason,
                "folder": top_folder,
            })
        else:
            report["summary"]["real_files"] += 1
            report["by_folder"][top_folder]["real"] += 1

    # Generate recommendations
    stub_pct = (report["summary"]["stub_files"] / report["summary"]["total_py_files"] * 100) if report["summary"]["total_py_files"] > 0 else 0

    report["recommendations"].append(
        f"CRITICAL: {report['summary']['stub_files']} stub files ({stub_pct:.1f}%) need implementation or removal"
    )

    for folder, stats in report["by_folder"].items():
        total = stats["stubs"] + stats["real"]
        if total > 0 and stats["stubs"] / total > 0.5:
            report["recommendations"].append(
                f"Folder '{folder}' has {stats['stubs']}/{total} stub files ({stats['stubs']/total*100:.0f}%)"
            )

    return report

def print_report(report: Dict) -> None:
    """Print formatted audit report."""

    stub_pct = (report['summary']['stub_files'] / report['summary']['total_py_files'] * 100) if report['summary']['total_py_files'] > 0 else 0

    for reason, files in sorted(report["by_reason"].items(), key=lambda x: -len(x[1])):
        print(f"\n    {reason}: {len(files)} files")

    for folder, stats in sorted(report["by_folder"].items(), key=lambda x: -x[1]["stubs"]):
        total = stats["stubs"] + stats["real"]
        if stats["stubs"] > 0:
            pct = stats["stubs"] / total * 100 if total > 0 else 0
            print(f"\n    {folder}: {stats['stubs']}/{total} stubs ({pct:.1f}%)")

    print("\n    Stubs found:")
    for stub in report["stubs"][:20]:
        print(f"      - {stub}")
    
    if len(report["stubs"]) > 20:
        print(f"      ... and {len(report['stubs']) - 20} more")
    
    if report["recommendations"]:
        print("\n    Recommendations:")
        for i, rec in enumerate(report["recommendations"][:10], 1):
            print(f"      {i}. {rec}")

def main() -> None:
    """Main entry point for stub audit."""
    report = audit_stubs()
    print_report(report)

    # Convert defaultdicts for JSON
    report["by_reason"] = dict(report["by_reason"])
    report["by_folder"] = dict(report["by_folder"])

    # Save report
    report_path = REPO_ROOT / "stub_audit_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    return report

if __name__ == "__main__":
    main()
