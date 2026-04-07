"""
Analyze ghost _adg stubs: files on disk that have no imports coverage edges in ADG.
Categorize them into:
  A) Import-nothing stubs (empty/trivial) - safe to delete
  B) Stubs that import from non-agentic_core (e.g. apps_lic, apps_shared) - need re-evaluation
  C) Stubs whose target source file no longer exists - orphan, safe to delete
  D) Stubs that DO import agentic_core but weren't captured in ADG for other reasons
"""

from __future__ import annotations

import ast
import glob
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _parse_imports(path: Path) -> list[str]:
    """Return all imported module names from a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def main() -> None:
    db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    # Get all stubs that DO have coverage edges
    known_in_adg = {
        r["resolved_path"]
        for r in conn.execute(
            "SELECT DISTINCT n1.resolved_path "
            "FROM edges e JOIN nodes n1 ON e.src_id=n1.id "
            "WHERE e.relation_type='imports' "
            "AND n1.resolved_path LIKE 'tests/%' "
            "AND n1.resolved_path LIKE '%_adg.py'",
        )
    }

    # All stubs on disk
    all_stubs_on_disk = {
        p.relative_to(PROJECT_ROOT).as_posix() for p in (PROJECT_ROOT / "tests").rglob("*_adg.py")
    }

    ghosts = sorted(all_stubs_on_disk - known_in_adg)
    print(f"Ghost stubs (on disk, not in ADG coverage): {len(ghosts)}")

    cat_a_empty: list[str] = []
    cat_b_non_ac: list[str] = []
    cat_c_orphan: list[str] = []
    cat_d_ac_import: list[str] = []

    for rel in ghosts:
        path = PROJECT_ROOT / rel
        imports = _parse_imports(path)
        ac_imports = [i for i in imports if i.startswith("agentic_core")]

        if not imports:
            cat_a_empty.append(rel)
            continue

        if ac_imports:
            # Has agentic_core imports but wasn't captured — check if src exists
            cat_d_ac_import.append(rel)
        else:
            # Check if any imported src file exists
            has_existing_src = False
            for imp in imports:
                parts = imp.replace(".", "/")
                for ext in [".py", "/__init__.py"]:
                    if (PROJECT_ROOT / f"{parts}{ext}").exists():
                        has_existing_src = True
                        break
            if has_existing_src:
                cat_b_non_ac.append(rel)
            else:
                cat_c_orphan.append(rel)

    print(f"\n  A) Empty/no-imports:           {len(cat_a_empty)}")
    print(f"  B) Non-agentic_core imports:   {len(cat_b_non_ac)}")
    print(f"  C) Orphan (src gone):          {len(cat_c_orphan)}")
    print(f"  D) Has agentic_core import:    {len(cat_d_ac_import)}")

    print("\n=== Category A (empty) - safe to delete ===")
    for f in cat_a_empty[:20]:
        print(f"  {f}")
    if len(cat_a_empty) > 20:
        print(f"  ... +{len(cat_a_empty) - 20} more")

    print("\n=== Category C (orphan) - safe to delete ===")
    for f in cat_c_orphan[:20]:
        print(f"  {f}")
    if len(cat_c_orphan) > 20:
        print(f"  ... +{len(cat_c_orphan) - 20} more")

    print("\n=== Category B (non-agentic_core) - review ===")
    for f in cat_b_non_ac[:20]:
        path = PROJECT_ROOT / f
        imps = [
            i
            for i in _parse_imports(path)
            if not i.startswith(("pytest", "sys", "pathlib", "typing", "__future__"))
        ]
        print(f"  {f}  -> {imps[:3]}")
    if len(cat_b_non_ac) > 20:
        print(f"  ... +{len(cat_b_non_ac) - 20} more")

    print("\n=== Category D (has agentic_core import but not in ADG) ===")
    for f in cat_d_ac_import[:20]:
        path = PROJECT_ROOT / f
        ac_imps = [i for i in _parse_imports(path) if i.startswith("agentic_core")]
        print(f"  {f}  -> {ac_imps[:2]}")
    if len(cat_d_ac_import) > 20:
        print(f"  ... +{len(cat_d_ac_import) - 20} more")

    conn.close()


if __name__ == "__main__":
    main()
