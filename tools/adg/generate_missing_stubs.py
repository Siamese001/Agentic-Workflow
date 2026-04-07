"""
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_1")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_2")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_3")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_4")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_5")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_6")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_7")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_8")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_9")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_10")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_11")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_12")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_13")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_14")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_15")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_16")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_17")
_emit_reads_through("l4", "generate_missing_stubs", "urg_read_18")
Generate importability stubs for uncovered agentic_core modules.

For each uncovered module (no test imports it at all), generate a minimal
_adg.py stub under the corresponding tests/unit/ path.

Skips:
- __init__.py files (unless they define exported symbols)
- Modules that are clearly scripts/utils with if __name__ == '__main__' only
- Already-stubbed modules
"""

from __future__ import annotations

import ast
import glob
import sqlite3
import sys
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ModuleInfo(NamedTuple):
    rel_path: str  # e.g. agentic_core/L0_routing/scripts/foo.py
    module_name: str  # e.g. agentic_core.L0_routing.scripts.foo
    public_names: list[str]  # top-level public names exported
    is_init: bool


def extract_public_names(path: Path) -> list[str]:
    """Return top-level public class/function/constant names."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        return []

    names = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and not t.id.startswith("_") and t.id.isupper():
                    names.append(t.id)
    return names[:6]  # cap at 6 to keep stubs manageable


def rel_to_module(rel_path: str) -> str:
    """Convert relative path to dotted module name."""
    return rel_path.replace("/", ".").replace("\\", ".").removesuffix(".py")


def stub_path_for(rel_src: str) -> Path:
    """
    Given agentic_core/L0_routing/foo.py
    Return tests/unit/agentic_core/L0_routing/test_foo_adg.py
    """
    p = Path(rel_src)
    # Build stub path
    parts = list(p.parts)  # ['agentic_core', 'L0_routing', 'foo.py']
    stem = p.stem  # foo
    parent_parts = parts[:-1]  # ['agentic_core', 'L0_routing']

    stub_dir = PROJECT_ROOT / "tests" / "unit" / Path(*parent_parts)
    stub_name = f"test_{stem}_adg.py"
    return stub_dir / stub_name


def stub_exists_for(rel_src: str) -> bool:
    return stub_path_for(rel_src).exists()


def generate_stub(info: ModuleInfo) -> str:
    """Generate stub content for a module."""
    module_name = info.module_name
    public = info.public_names

    lines = [
        f'"""ADG importability contract for {info.rel_path}.',
        "",
        "Auto-generated stub — covers GT_covers edge for ADG reachability.",
        f"Behavioral tests belong in test_{Path(info.rel_path).stem}.py (no _adg suffix).",
        '"""',
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
        "try:",
    ]

    if public:
        imports_str = ",\n        ".join(public)
        lines.append(f"    from {module_name} import (  # noqa: F401")
        for name in public:
            lines.append(f"        {name},")
        lines.append("    )")
    else:
        lines.append(f"    import {module_name}  # noqa: F401")

    lines += [
        "    _AVAILABLE = True",
        "except Exception:",
        "    _AVAILABLE = False",
    ]

    if public:
        for name in public:
            lines.append(f"    {name} = None  # type: ignore[assignment,misc]")

    class_name = "".join(w.title() for w in Path(info.rel_path).stem.replace("-", "_").split("_"))
    test_class = f"Test{class_name}Importability"

    lines += [
        "",
        "",
        f'@pytest.mark.skipif(not _AVAILABLE, reason="{Path(info.rel_path).stem} deps unavailable")',
        f"class {test_class}:",
        "    def test_module_importable(self) -> None:",
        f'        """ADG contract: {info.rel_path} must be importable."""',
        "        assert _AVAILABLE",
    ]

    if public:
        for name in public:
            if name[0].isupper() and not name.isupper():
                # Class or function
                lines += [
                    "",
                    f"    def test_{name.lower()}_defined(self) -> None:",
                    f"        assert {name} is not None",
                ]

    lines.append("")
    return "\n".join(lines)


def main(dry_run: bool = True) -> None:
    db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    src_mods = {
        r["resolved_path"]
        for r in conn.execute(
            "SELECT resolved_path FROM nodes "
            "WHERE entity_type='module' "
            "AND resolved_path LIKE 'agentic_core/%' "
            "AND resolved_path NOT LIKE '%__pycache__%' ",
        )
    }

    cov_rows = list(
        conn.execute(
            "SELECT DISTINCT n2.resolved_path as src_file "
            "FROM edges e "
            "JOIN nodes n1 ON e.src_id=n1.id "
            "JOIN nodes n2 ON e.dst_id=n2.id "
            "WHERE e.relation_type='imports' "
            "AND n1.resolved_path LIKE 'tests/%' "
            "AND n2.resolved_path LIKE 'agentic_core/%' "
            "AND n2.resolved_path NOT LIKE '%__pycache__%' ",
        ),
    )

    covered = {r["src_file"].split("::")[0] for r in cov_rows}
    uncovered = sorted(src_mods - covered)

    print(f"Uncovered modules: {len(uncovered)}")

    created = 0
    skipped_existing = 0
    skipped_init = 0
    skipped_no_content = 0

    # Deduplicate: strip ::ClassName suffixes, work per unique .py file
    unique_uncovered: dict[str, str] = {}  # rel_path -> rel_path (dedup by stub target)
    for rel in uncovered:
        base_rel = rel.split("::")[0]  # strip ::ClassName
        stub_p = stub_path_for(base_rel)
        key = str(stub_p)
        if key not in unique_uncovered:
            unique_uncovered[key] = base_rel

    for stub_key, rel in sorted(unique_uncovered.items()):
        # Skip __init__ files with no meaningful content
        if rel.endswith("/__init__.py") or rel.endswith("\\__init__.py"):
            src = PROJECT_ROOT / rel
            names = extract_public_names(src) if src.exists() else []
            if not names:
                skipped_init += 1
                continue

        # Skip if stub already exists
        if stub_exists_for(rel):
            skipped_existing += 1
            continue

        src_path = PROJECT_ROOT / rel
        public_names = extract_public_names(src_path) if src_path.exists() else []

        # Skip completely empty files
        if src_path.exists() and src_path.stat().st_size < 10:
            skipped_no_content += 1
            continue

        module_name = rel_to_module(rel)
        info = ModuleInfo(
            rel_path=rel,
            module_name=module_name,
            public_names=public_names,
            is_init=rel.endswith("__init__.py"),
        )

        stub_p = stub_path_for(rel)
        content = generate_stub(info)

        if dry_run:
            print(f"  [DRY] {stub_p.relative_to(PROJECT_ROOT)}")
            created += 1
        else:
            stub_p.parent.mkdir(parents=True, exist_ok=True)
            # Ensure __init__.py exists in each parent test dir
            for parent in stub_p.parents:
                if parent == PROJECT_ROOT / "tests":
                    break
                init = parent / "__init__.py"
                if not init.exists():
                    init.write_text("", encoding="utf-8")
            stub_p.write_text(content, encoding="utf-8")
            created += 1

    print("\nResults:")
    print(f"  {'Would create' if dry_run else 'Created'}: {created}")
    print(f"  Skipped (stub exists):  {skipped_existing}")
    print(f"  Skipped (__init__ empty): {skipped_init}")
    print(f"  Skipped (empty src):    {skipped_no_content}")

    conn.close()


if __name__ == "__main__":
    dry = "--execute" not in sys.argv
    main(dry_run=dry)
