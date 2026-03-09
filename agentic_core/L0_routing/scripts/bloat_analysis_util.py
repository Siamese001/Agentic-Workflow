#!/usr/bin/env python3
"""Bloat analysis script for approved folders."""

import ast
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

ROOT = Path(__file__).parent.parent
APPROVED = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def get_file_stats():
    """Get file statistics by extension and folder."""
    stats = defaultdict(lambda: {"count": 0, "size": 0})
    folder_stats = defaultdict(lambda: {"py": 0, "other": 0, "total_size": 0})

    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*"):
            if f.is_file() and "__pycache__" not in str(f):
                ext = f.suffix.lower()
                size = f.stat().st_size
                stats[ext]["count"] += 1
                stats[ext]["size"] += size
                if ext == ".py":
                    folder_stats[folder]["py"] += 1
                else:
                    folder_stats[folder]["other"] += 1
                folder_stats[folder]["total_size"] += size

    return stats, folder_stats


# guardian: allow-magic-config
def find_large_files(min_size_kb=50):
    """Find files larger than threshold."""
    large = []
    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            size = f.stat().st_size
            if size > min_size_kb * 1024:
                large.append(
                    {
                        "path": str(f.relative_to(ROOT)),
                        "size_kb": round(size / 1024, 1),
                        "lines": len(f.read_text(encoding="utf-8", errors="replace").splitlines()),
                    },
                )
    return sorted(large, key=lambda x: -x["size_kb"])


def find_duplicate_filenames():
    """Find files with duplicate names."""
    names = defaultdict(list)
    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            names[f.name].append(str(f.relative_to(ROOT)))
    return {k: v for k, v in names.items() if len(v) > 1}


def find_empty_or_stub_files():
    """Find empty or stub Python files."""
    stubs = []
    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f) or f.name == "__init__.py":
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                # Remove docstrings
                code_lines = []
                in_docstring = False
                for line in lines:
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                        continue
                    if not in_docstring:
                        code_lines.append(line)
                if len(code_lines) < 5:
                    stubs.append(
                        {
                            "path": str(f.relative_to(ROOT)),
                            "code_lines": len(code_lines),
                            "total_lines": len(content.splitlines()),
                        },
                    )
            # guardian: allow-silent-swallow
            except Exception:
                pass
    return stubs


def find_deprecated_markers():
    """Find files with deprecation markers."""
    deprecated = []
    markers = ["DEPRECATED", "TODO: Remove", "TODO: Delete", "LEGACY", "OBSOLETE", "TO BE REMOVED"]
    for folder in APPROVED:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                for marker in markers:
                    if marker.lower() in content.lower():
                        deprecated.append({"path": str(f.relative_to(ROOT)), "marker": marker})
                        break
            # guardian: allow-silent-swallow
            except Exception:
                pass
    return deprecated


def find_test_files_outside_tests():
    """Find test files outside tests/ folder."""
    misplaced = []
    for folder in APPROVED:
        if folder == "tests":
            continue
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("test_*.py"):
            if "__pycache__" not in str(f):
                misplaced.append(str(f.relative_to(ROOT)))
        for f in folder_path.rglob("*_test.py"):
            if "__pycache__" not in str(f):
                misplaced.append(str(f.relative_to(ROOT)))
    return misplaced


def find_unused_imports():
    """Find files with potentially unused imports (simple heuristic)."""
    candidates = []
    for folder in ["agentic_core", "apps_rg", "apps_lic"]:
        folder_path = ROOT / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.py"):
            if "__pycache__" in str(f) or f.name == "__init__.py":
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname or alias.name.split(".")[0]
                            imports.append(name)
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            imports.append(name)
                # Check if imports are used (simple check)
                unused = []
                for imp in imports:
                    # Count occurrences (excluding import lines)
                    lines = content.splitlines()
                    usage_count = sum(1 for l in lines if imp in l and "import" not in l)
                    if usage_count == 0:
                        unused.append(imp)
                if len(unused) > 3:
                    candidates.append(
                        {
                            "path": str(f.relative_to(ROOT)),
                            "unused_count": len(unused),
                            "examples": unused[:5],
                        },
                    )
            # guardian: allow-silent-swallow
            except Exception:
                pass
    return sorted(candidates, key=lambda x: -x["unused_count"])[:30]


def find_script_candidates():
    """Find scripts that might be one-off or obsolete."""
    candidates = []
    scripts_path = ROOT / "scripts"
    if not scripts_path.exists():
        return candidates

    for f in scripts_path.glob("*.py"):
        if f.name.startswith("__"):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            stat = f.stat()
            # Check for signs of one-off scripts
            signals = []
            if "hardcoded" in content.lower() or "hardcode" in content.lower():
                signals.append("hardcoded values")
            if "temporary" in content.lower() or "temp" in content.lower():
                signals.append("temporary marker")
            if "phase" in f.name.lower() and "batch" in f.name.lower():
                signals.append("batch migration script")
            if "fix_" in f.name.lower() or "patch_" in f.name.lower():
                signals.append("one-time fix script")
            if "archive" in f.name.lower() or "restore" in f.name.lower():
                signals.append("archive utility")
            if "update_" in f.name.lower() and "import" in f.name.lower():
                signals.append("import migration")

            if signals:
                candidates.append(
                    {
                        "path": str(f.relative_to(ROOT)),
                        "size_kb": round(stat.st_size / 1024, 1),
                        "signals": signals,
                    },
                )
        # guardian: allow-silent-swallow
        except Exception:
            pass
    return candidates


def main():
    print("=" * 70)
    print("BLOAT ANALYSIS REPORT")
    print(f"Generated: {datetime.now().isoformat()}")
    print("=" * 70)

    # File stats
    stats, folder_stats = get_file_stats()
    print("\n## FILE STATISTICS BY EXTENSION")
    print("-" * 50)
    for ext, data in sorted(stats.items(), key=lambda x: -x[1]["count"])[:15]:
        ext_name = ext if ext else "(no ext)"
        print(f"  {ext_name:12} {data['count']:5} files  {data['size'] / 1024 / 1024:8.2f} MB")

    print("\n## FILE STATISTICS BY FOLDER")
    print("-" * 50)
    total_py = 0
    total_other = 0
    total_size = 0
    for folder, data in sorted(folder_stats.items()):
        print(
            f"  {folder:20} {data['py']:5} .py  {data['other']:5} other  {data['total_size'] / 1024 / 1024:8.2f} MB",
        )
        total_py += data["py"]
        total_other += data["other"]
        total_size += data["total_size"]
    print(f"  {'TOTAL':20} {total_py:5} .py  {total_other:5} other  {total_size / 1024 / 1024:8.2f} MB")

    # Large files
    large = find_large_files(100)
    print(f"\n## LARGE FILES (>100KB) - {len(large)} files")
    print("-" * 50)
    for f in large[:20]:
        print(f"  {f['size_kb']:7.1f} KB  {f['lines']:5} lines  {f['path']}")

    # Duplicates
    dupes = find_duplicate_filenames()
    print(f"\n## DUPLICATE FILENAMES - {len(dupes)} duplicates")
    print("-" * 50)
    for name, paths in sorted(dupes.items())[:15]:
        print(f"  {name}:")
        for p in paths:
            print(f"    - {p}")

    # Stubs
    stubs = find_empty_or_stub_files()
    print(f"\n## EMPTY/STUB FILES (<5 code lines) - {len(stubs)} files")
    print("-" * 50)
    for s in stubs[:20]:
        print(f"  {s['code_lines']:2} lines  {s['path']}")

    # Deprecated
    deprecated = find_deprecated_markers()
    print(f"\n## FILES WITH DEPRECATION MARKERS - {len(deprecated)} files")
    print("-" * 50)
    for d in deprecated[:20]:
        print(f"  [{d['marker']}] {d['path']}")

    # Misplaced tests
    misplaced = find_test_files_outside_tests()
    print(f"\n## TEST FILES OUTSIDE tests/ - {len(misplaced)} files")
    print("-" * 50)
    for m in misplaced[:20]:
        print(f"  {m}")

    # Script candidates
    scripts = find_script_candidates()
    print(f"\n## SCRIPT ARCHIVE CANDIDATES - {len(scripts)} files")
    print("-" * 50)
    for s in scripts:
        print(f"  {s['path']}")
        print(f"    Signals: {', '.join(s['signals'])}")

    # Unused imports
    unused = find_unused_imports()
    print(f"\n## FILES WITH MANY UNUSED IMPORTS - {len(unused)} files")
    print("-" * 50)
    for u in unused[:15]:
        print(f"  {u['unused_count']:3} unused  {u['path']}")
        print(f"    Examples: {', '.join(u['examples'][:3])}")


if __name__ == "__main__":
    main()
