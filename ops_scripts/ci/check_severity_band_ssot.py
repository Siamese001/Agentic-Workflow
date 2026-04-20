"""CI gate: forbid new hardcoded severity/band literals outside SSOT modules.

The canonical SSOT modules for severity<->band mapping are:
  - agentic_core/adg/severity_bands.py         (authoritative P0-P3 <-> CRITICAL..LOW)
  - agentic_core/L5_safety/config/severity.py  (high-level SeverityLevel enum)

This gate does NOT attempt to detect every possible usage. It scans production
Python source files under agentic_core/, tools/, and ops_scripts/ for inline
severity<->band mapping dicts that would diverge from the SSOT. Specifically,
it flags files that define a local dict mapping CRITICAL/HIGH/MEDIUM/LOW to
P0/P1/P2/P3 (or inverse) without importing from one of the SSOT modules.

Exit codes:
  0 = clean (no violations)
  1 = one or more files contain a local severity<->band mapping and do not
      import from a SSOT module.

Usage:
  python ops_scripts/ci/check_severity_band_ssot.py
  python ops_scripts/ci/check_severity_band_ssot.py --verbose
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# SSOT module import lines. If any of these substrings appears in the file,
# the file is allowed to reference severity/band literals freely.
SSOT_IMPORT_MARKERS: tuple[str, ...] = (
    "from agentic_core.adg.severity_bands",
    "import agentic_core.adg.severity_bands",
    "from agentic_core.L5_safety.config.severity",
    "import agentic_core.L5_safety.config.severity",
)

# Files allowed to hold the SSOT itself or thin shims around it.
SSOT_OWNER_FILES: tuple[Path, ...] = (
    REPO_ROOT / "agentic_core" / "adg" / "severity_bands.py",
    REPO_ROOT / "agentic_core" / "L5_safety" / "config" / "severity.py",
)

# Directories excluded from the scan. We only care about live production code.
EXCLUDE_DIR_SEGMENTS: tuple[str, ...] = (
    "archives",
    "archive",
    "_archive",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "tools_graveyard_w5.12",
    "adg_root_oneshots_w5.10",
    "adg_subdir_stubs_w5.11",
)

SCAN_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "tools",
    REPO_ROOT / "ops_scripts",
    REPO_ROOT / "system_learning",
)

# Pattern: a dict literal mapping at least three of CRITICAL/HIGH/MEDIUM/LOW
# to P0/P1/P2/P3 (or inverse). Conservative: both sides must be quoted strings.
_BANDS = r"(?:P0|P1|P2|P3)"
_SEVS = r"(?:CRITICAL|HIGH|MEDIUM|LOW)"
_Q = r"['\"]"

# Forward: {"CRITICAL": "P0", ...}
_FORWARD_PAIR = rf"{_Q}{_SEVS}{_Q}\s*:\s*{_Q}{_BANDS}{_Q}"
# Inverse: {"P0": "CRITICAL", ...}
_INVERSE_PAIR = rf"{_Q}{_BANDS}{_Q}\s*:\s*{_Q}{_SEVS}{_Q}"

PAIR_RE = re.compile(rf"(?:{_FORWARD_PAIR})|(?:{_INVERSE_PAIR})")


def _iter_python_files() -> list[Path]:
    """Return all Python files in scan roots, excluding archive/cache dirs."""
    results: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(seg in path.parts for seg in EXCLUDE_DIR_SEGMENTS):
                continue
            results.append(path)
    return results


def _file_has_ssot_import(text: str) -> bool:
    return any(marker in text for marker in SSOT_IMPORT_MARKERS)


def _count_mapping_pairs(text: str) -> int:
    return len(PAIR_RE.findall(text))


def scan() -> list[tuple[Path, int]]:
    """Return list of (path, pair_count) for files that violate the SSOT rule."""
    violations: list[tuple[Path, int]] = []
    for path in _iter_python_files():
        if path.resolve() in {p.resolve() for p in SSOT_OWNER_FILES}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        pair_count = _count_mapping_pairs(text)
        # Threshold: 3+ pairs indicates a local severity<->band mapping dict.
        # A single isolated literal elsewhere (e.g. a test fixture string) does
        # not trigger the gate.
        if pair_count >= 3 and not _file_has_ssot_import(text):
            violations.append((path, pair_count))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="Show scanned file count")
    args = parser.parse_args()

    files = _iter_python_files()
    if args.verbose:
        print(f"[check_severity_band_ssot] scanned {len(files)} Python files")

    violations = scan()
    if not violations:
        print("[check_severity_band_ssot] PASS \u2014 no local severity\u2194band mappings outside SSOT")
        return 0

    print("[check_severity_band_ssot] FAIL \u2014 local severity\u2194band mappings found:")
    for path, count in violations:
        rel = path.relative_to(REPO_ROOT)
        print(f"  {rel}  ({count} mapping pair(s))")
    print()
    print("Fix: import from one of the SSOT modules instead of hardcoding the mapping:")
    print("  from agentic_core.adg.severity_bands import severity_to_band, Severity, Band")
    print("  from agentic_core.L5_safety.config.severity import SeverityLevel")
    return 1


if __name__ == "__main__":
    sys.exit(main())
