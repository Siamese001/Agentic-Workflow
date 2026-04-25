"""W3 — collapse rename shims:
  MCPHardenedMixin   -> MCPOperationMixin   (module: mcp_hardened_mixin -> mcp_operation_mixin)
  HealerMixin        -> HealingPolicyMixin  (module: healer_mixin       -> healing_policy_mixin)

Operates on .py files only. Whole-word boundary on names. Excludes archives,
the canonical mixin files themselves, and the shim files (which are deleted
separately).

DRY-RUN by default. Pass --apply to write changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXCLUDE_DIRS = {
    "archives",
    "tools_graveyard_w5.12",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_smoke_v1_coerce_e9aa09",
    ".backup",
}

# Files that must NOT be rewritten
SKIP_FILES = {
    # Shim files — deleted in a separate step
    "agentic_core/mixins/mcp_hardened_mixin.py",
    "agentic_core/mixins/healer_mixin.py",
    # Canonical files — their internal use of the new name is correct
    "agentic_core/mixins/mcp_operation_mixin.py",
    "agentic_core/mixins/healing_policy_mixin.py",
    # The rewrite script itself contains the names as regex literals
    "tools/analysis/_w3_shim_rewrite.py",
    # Mixin audit script may reference the names in its results — keep stable
    "tools/analysis/_mixin_verify_unused.py",
    # The deleted shim's stub test — handled by separate file deletion
    "tests/unit/agentic_core/mixins/test_healer_mixin.py",
}

# Exact rename rules: list of (regex, replacement) — applied in order.
# Each rule uses \b boundaries so we only hit the canonical names.
RULES = [
    # 1. Module path imports
    (re.compile(r"\bagentic_core\.mixins\.mcp_hardened_mixin\b"), "agentic_core.mixins.mcp_operation_mixin"),
    (re.compile(r"\bagentic_core\.mixins\.healer_mixin\b"), "agentic_core.mixins.healing_policy_mixin"),
    # 2. Lowercase symbol re-export `mcp_hardened_mixin = MCPHardenedMixin`
    #    used only inside mcp_hardened_mixin.py — already in SKIP_FILES.
    # 3. Class name rewrites — whole-word
    (re.compile(r"\bMCPHardenedMixin\b"), "MCPOperationMixin"),
    (re.compile(r"\bHealerMixin\b"), "HealingPolicyMixin"),
]


def iter_py_files() -> list[Path]:
    files: list[Path] = []
    for py in REPO.rglob("*.py"):
        rel_parts = set(py.relative_to(REPO).parts)
        if rel_parts & EXCLUDE_DIRS:
            continue
        rel = str(py.relative_to(REPO)).replace("\\", "/")
        if rel in SKIP_FILES:
            continue
        files.append(py)
    return files


def rewrite_text(txt: str) -> tuple[str, dict[str, int]]:
    counts = {f"rule_{i}": 0 for i in range(len(RULES))}
    for i, (pat, repl) in enumerate(RULES):
        new_txt, n = pat.subn(repl, txt)
        counts[f"rule_{i}"] += n
        txt = new_txt
    return txt, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write changes (default: dry-run)")
    args = parser.parse_args()

    changed_files: list[tuple[str, dict[str, int]]] = []
    total = {f"rule_{i}": 0 for i in range(len(RULES))}

    for py in iter_py_files():
        try:
            orig = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new, counts = rewrite_text(orig)
        if new == orig:
            continue
        rel = str(py.relative_to(REPO)).replace("\\", "/")
        changed_files.append((rel, counts))
        for k, v in counts.items():
            total[k] += v
        if args.apply:
            py.write_text(new, encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"=== W3 shim rewrite ({mode}) ===")
    print(f"Files changed: {len(changed_files)}")
    print(f"Per-rule totals: {total}")
    print(f"Rule legend:")
    for i, (pat, repl) in enumerate(RULES):
        print(f"  rule_{i}: {pat.pattern}  ->  {repl}")
    print()
    for rel, counts in changed_files:
        active = {k: v for k, v in counts.items() if v}
        print(f"  {rel}  {active}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
