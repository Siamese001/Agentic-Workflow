"""W5.4 SSOT hardcoding probe.

Find hardcoded literals for paths and layer names that have canonical
SSOTs in agentic_core.L0_routing.config.path_constants /
agentic_core.adg.severity_bands, and are used across >=5 files.

Output: ranked list of (literal, canonical_symbol, occurrence_count) so
we can pick the top-N migrations. Does NOT modify source.
"""

from __future__ import annotations
import ast
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# (literal_value, expected_import_from_module, expected_symbol)
CANDIDATES = [
    # path string literals that should be imported from path_constants
    ("artifacts/adg/", "agentic_core.L0_routing.config.path_constants", "ADG_ARTIFACTS_DIR"),
    ("artifacts/cursor/", "agentic_core.L0_routing.config.path_constants", "WINDSURF_ARTIFACTS_DIR"),
    ("docs/archive/windsurf/legacy-tree/plans/", "agentic_core.L0_routing.config.path_constants", "WINDSURF_PLANS_DIR"),
    (".cursor/scripts/_legacy_windsurf/", "agentic_core.L0_routing.config.path_constants", "WINDSURF_SCRIPTS_DIR"),
    ("docs/reports/", "agentic_core.L0_routing.config.path_constants", "DOCS_REPORTS_DIR"),
    ("docs/architecture/adr/", "agentic_core.L0_routing.config.path_constants", "ADR_DIR"),
]

# ADG layer names that should come from severity_bands or similar SSOT
LAYER_LITERALS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

ROOTS = (
    "agentic_core",
    "apps_rg",
    "apps_shared",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_underwriting_ai",
    "tools",
    "ops_scripts",
    "system_learning",
    "infrastructure",
)
EXCLUDE_PATS = (
    r"\\__pycache__\\",
    r"\\archives?\\",
    r"\\_archive\\",
    r"\\tools\\archive\\",
    r"\\tests\\",
    r"\\artifacts\\",
    r"\\tools\\debug\\",
)


def _scan_path_literals() -> dict[str, list[tuple[str, int]]]:
    """For each candidate literal, find every source site using it as a
    string literal (not a variable reference). Returns dict[literal] -> [(file, line)].
    """
    sites: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for root in ROOTS:
        p = Path(root)
        if not p.exists():
            continue
        for py in p.rglob("*.py"):
            sp = str(py)
            if any(re.search(pat, sp) for pat in EXCLUDE_PATS):
                continue
            try:
                text = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue

            # Check if the file already imports from path_constants
            already_imports = any(
                isinstance(node, ast.ImportFrom) and node.module and "path_constants" in node.module
                for node in ast.walk(tree)
            )

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    val = node.value
                    for lit, _mod, _sym in CANDIDATES:
                        # Match literal value or value that starts with literal
                        if val == lit or (len(val) <= 100 and val.startswith(lit) and lit.endswith("/")):
                            key = lit
                            sites[key].append((sp, getattr(node, "lineno", 0)))
                            break
                    # Don't count imports of path_constants themselves
                    if already_imports and any(val == lit for lit, _, _ in CANDIDATES):
                        pass  # still counted; migration may still be wanted
    return sites


def _rank_migrations(sites: dict[str, list[tuple[str, int]]]) -> list[tuple[str, int, int, str, str]]:
    """Return (literal, file_count, site_count, module, symbol) sorted by site_count desc."""
    out = []
    for lit, module, sym in CANDIDATES:
        lst = sites.get(lit, [])
        file_count = len({f for f, _ in lst})
        out.append((lit, file_count, len(lst), module, sym))
    out.sort(key=lambda t: (-t[2], -t[1]))
    return out


def main() -> int:
    print("Scanning candidate path literals...")
    sites = _scan_path_literals()
    ranked = _rank_migrations(sites)

    print("\n" + "=" * 80)
    print(f"{'literal':<30} {'files':>6} {'sites':>6}  canonical import")
    print("=" * 80)
    for lit, fc, sc, mod, sym in ranked:
        print(f"{lit:<30} {fc:>6} {sc:>6}  from {mod} import {sym}")

    # Show sample sites for top 3
    print("\n" + "=" * 80)
    print("Sample sites for top 3 migration candidates:")
    print("=" * 80)
    for lit, fc, sc, _mod, _sym in ranked[:3]:
        print(f"\n--- {lit} ({sc} sites in {fc} files) ---")
        seen_files = set()
        for fp, ln in sorted(sites[lit], key=lambda t: t[0]):
            if fp in seen_files:
                continue
            seen_files.add(fp)
            if len(seen_files) > 10:
                break
            print(f"  {fp}:{ln}")

    # Does path_constants.py even export these symbols?
    print("\n" + "=" * 80)
    print("Check canonical symbols in path_constants.py:")
    print("=" * 80)
    pc_file = Path("agentic_core/L0_routing/config/path_constants.py")
    if pc_file.exists():
        pc_text = pc_file.read_text(encoding="utf-8")
        for _lit, _mod, sym in CANDIDATES:
            present = re.search(rf"^{sym}\s*=", pc_text, re.MULTILINE) is not None
            print(f"  {sym:<30} {'FOUND' if present else 'MISSING'}")
    else:
        print(f"  NOT FOUND: {pc_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
