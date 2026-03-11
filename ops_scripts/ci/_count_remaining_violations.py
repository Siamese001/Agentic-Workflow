"""Count remaining hardcoded SSOT path literal violations after fixes."""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
    ARCHIVES_DIR,
    REPORTS_DIR,
    DOCS_REPORTS_PLANS,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_RG_DIR,
    APPS_LIC_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    TOOLS_DIR,
    SYSTEM_LEARNING_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
)

CONSTS: list[tuple[str, str]] = sorted([
    ("ARCHIVES_DIR",         ARCHIVES_DIR),
    ("AGENTIC_CORE_DIR",     AGENTIC_CORE_DIR),
    ("APPS_RG_DIR",          APPS_RG_DIR),
    ("APPS_LIC_DIR",         APPS_LIC_DIR),
    ("APPS_SHARED_DIR",      APPS_SHARED_DIR),
    ("OPS_SCRIPTS_DIR",      OPS_SCRIPTS_DIR),
    ("TESTS_DIR",            TESTS_DIR),
    ("TOOLS_DIR",            TOOLS_DIR),
    ("SYSTEM_LEARNING_DIR",  SYSTEM_LEARNING_DIR),
    ("L0_MAINTENANCE_DIR",   L0_MAINTENANCE_DIR),
    ("L1_COGNITION_DIR",     L1_COGNITION_DIR),
    ("L2_EXECUTION_DIR",     L2_EXECUTION_DIR),
    ("L3_ORCHESTRATION_DIR", L3_ORCHESTRATION_DIR),
    ("L4_STATE_DIR",         L4_STATE_DIR),
    ("L5_SAFETY_DIR",        L5_SAFETY_DIR),
    ("L6_OBSERVABILITY_DIR", L6_OBSERVABILITY_DIR),
    ("DOCS_REPORTS_PLANS",   DOCS_REPORTS_PLANS),
    ("REPORTS_DIR",          REPORTS_DIR),
], key=lambda x: -len(x[1]))

SSOT_SKIP = (
    "agentic_core/L5_safety/config/structure_blueprint/",
    "agentic_core/L0_routing/config/path_constants",
)


def main() -> None:
    remaining: dict[str, list[dict]] = {}
    by_const: dict[str, int] = {}

    for territory in sorted(ENFORCED_TERRITORIES):
        scan_root = ROOT / territory
        if not scan_root.exists():
            continue
        for dirpath, dirs, files in os.walk(scan_root):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(dirpath) / fname
                rel = fpath.relative_to(ROOT).as_posix()
                if any(rel.startswith(p) for p in SSOT_SKIP):
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="replace")
                except (OSError, UnicodeDecodeError):
                    continue
                lines = content.splitlines()
                for const, lit in CONSTS:
                    if const in content:
                        continue
                    pat = re.compile(r"""(?P<q>['"])""" + re.escape(lit) + r"""(?P=q)""")
                    for lineno, line in enumerate(lines, 1):
                        s = line.strip()
                        if s.startswith("#") or s.startswith("import ") or s.startswith("from "):
                            continue
                        m = pat.search(line)
                        if m:
                            after = line[m.end()] if m.end() < len(line) else ""
                            if after == "/":
                                continue
                            remaining.setdefault(rel, []).append({
                                "const": const,
                                "lit": lit,
                                "line": lineno,
                                "text": s[:100],
                            })
                            by_const[const] = by_const.get(const, 0) + 1
                            break

    total_files = len(remaining)
    total_hits = sum(len(v) for v in remaining.values())
    print(f"Remaining violations: {total_files} files, {total_hits} hits")
    print()
    print("BY CONSTANT:")
    for c, n in sorted(by_const.items(), key=lambda x: -x[1]):
        print(f"  {c:<30s} {n}")
    print()
    print("FILES:")
    for rel in sorted(remaining):
        print(f"  {rel}")
        for h in remaining[rel]:
            print(f"    L{h['line']:4d} [{h['const']}]  {h['text']}")


if __name__ == "__main__":
    main()
