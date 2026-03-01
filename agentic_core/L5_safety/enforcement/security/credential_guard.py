from agentic_core.L2_execution.tools import write_gateway as _wg

#!/usr/bin/env python3
"""
Deterministic Credential Scanner

Repository Security Gate Maintainer (L5 Safety Surface)

Scans repository for exposed credentials using deterministic regex patterns.
Read-only scanning only - no file modification or auto-remediation.
"""

import re
from pathlib import Path
from typing import Any

# Deterministic credential patterns covering all providers used in this repo
PATTERNS = [
    {"name": "OPENAI_KEY_PROJ", "regex": re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}")},
    {"name": "OPENAI_KEY_ADMIN", "regex": re.compile(r"sk-admin-[A-Za-z0-9_-]{20,}")},
    {"name": "OPENAI_KEY_GENERIC", "regex": re.compile(r"sk-[A-Za-z0-9]{48}")},
    {"name": "ANTHROPIC_API_KEY", "regex": re.compile(r"sk-ant-api[0-9]+-[A-Za-z0-9_-]{20,}")},
    {"name": "GOOGLE_GEMINI_KEY", "regex": re.compile(r"AIzaSy[A-Za-z0-9_-]{33}")},
    {"name": "PINECONE_API_KEY", "regex": re.compile(r"pcsk_[A-Za-z0-9_]{30,}")},
    {"name": "GITHUB_PAT", "regex": re.compile(r"github_pat_[A-Za-z0-9_]{20,}")},
    {"name": "GITHUB_TOKEN_GHP", "regex": re.compile(r"ghp_[A-Za-z0-9]{36}")},
    {"name": "FIGMA_TOKEN", "regex": re.compile(r"figd_[A-Za-z0-9_-]{20,}")},
    {"name": "BRAVE_API_KEY", "regex": re.compile(r"BSA[A-Za-z0-9]{20,}")},
    {"name": "SLACK_TOKEN", "regex": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")},
]

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".mypy_cache",
    ".nox",
    ".venv",
    "venv",
    "node_modules",
}

# File size limit (2MB)
MAX_FILE_SIZE = 2 * 1024 * 1024


def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file based on extension and content."""
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".txt",
        ".md",
        ".env",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".bash",
        ".zsh",
        ".ps1",
        ".html",
        ".css",
        ".xml",
        ".sql",
        ".log",
        ".out",
        ".err",
    }

    if file_path.suffix.lower() in text_extensions:
        return True

    # Check for files without extension but likely text
    if not file_path.suffix and file_path.stat().st_size < MAX_FILE_SIZE:
        try:
            with open(file_path, encoding="utf-8") as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, PermissionError):
            return False

    return False


def scan_file(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single file for credential patterns."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return violations

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        for pattern in PATTERNS:
            if pattern["regex"].search(line):
                violations.append(
                    {"file": str(file_path), "line_number": line_num, "pattern": pattern["name"]}
                )

    return violations


def scan_repository(root_path: Path) -> dict[str, Any]:
    """Scan entire repository for credentials."""
    all_violations = []
    files_scanned = 0

    # Use deterministic file ordering
    all_files = sorted(root_path.rglob("*"))

    for file_path in all_files:
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip excluded directories
        if any(exclude_dir in file_path.parts for exclude_dir in EXCLUDE_DIRS):
            continue

        # Skip files that are too large
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue

        # Only scan text files
        if not is_text_file(file_path):
            continue

        # Scan the file
        violations = scan_file(file_path)
        all_violations.extend(violations)
        files_scanned += 1

    # Sort violations deterministically by (file, line_number, pattern)
    all_violations.sort(key=lambda v: (v["file"], v["line_number"], v["pattern"]))

    return {"files_scanned": files_scanned, "violations": all_violations}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent

    print(f"Scanning repository for credentials: {root_path}")

    scan_result = scan_repository(root_path)

    # Create artifacts directory if it doesn't exist
    artifacts_dir = root_path / "artifacts" / "security"
    _wg.ensure_dir(artifacts_dir)

    # Write report
    report_path = artifacts_dir / "credential_scan_report.json"
    _wg.write_json(report_path, scan_result, indent=2)

    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {scan_result['files_scanned']}")
    print(f"Violations found: {len(scan_result['violations'])}")

    if scan_result["violations"]:
        print("CREDENTIAL VIOLATIONS DETECTED:")
        for violation in scan_result["violations"]:
            print(f"  {violation['file']}:{violation['line_number']} - {violation['pattern']}")
        exit(1)
    else:
        print("No credential violations found.")
        exit(0)


if __name__ == "__main__":
    main()
