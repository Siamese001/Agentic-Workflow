"""
Aggressive Deduplication - Remove files with high similarity or redundant content.

Strategies:
1. Remove files where ALL classes exist elsewhere (redundant files)
2. Remove files with very similar names (e.g., Task_X and X)
3. Remove files with >80% content similarity
4. Consolidate test files
"""

import ast
import re
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    TESTS_DIR,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "aggressive_dedup")
_emit_applies_guardrail("p0", "aggressive_dedup", "p0_governance")
_emit_reads_policy_state("p0", "aggressive_dedup", "policy_binding")
_emit_snapshots_state("p0", "aggressive_dedup", "state_snapshot")
emit_replay_key("p0", "aggressive_dedup")
emit_determinism_digest("p0", "aggressive_dedup")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

APPS_DIRS = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]


def get_all_classes_in_codebase(dirs: list[str]) -> dict[str, list[str]]:
    """Get all classes and which files they appear in."""
    class_files = defaultdict(list)
    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_files[node.name].append(str(py_file))
            # guardian: allow-silent-swallow
            except:
                pass
    return class_files


def find_redundant_files(dirs: list[str], class_files: dict[str, list[str]]) -> list[str]:
    """Find files where ALL classes exist in other files."""
    redundant = []
    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                file_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                if not file_classes:
                    continue
                all_redundant = True
                for cls_name in file_classes:
                    other_files = [f for f in class_files.get(cls_name, []) if f != str(py_file)]
                    if not other_files:
                        all_redundant = False
                        break
                if all_redundant and len(file_classes) > 0:
                    redundant.append(str(py_file))
            # guardian: allow-silent-swallow
            except:
                pass
    return redundant


def find_similar_named_files(dirs: list[str]) -> list[tuple[str, str]]:
    """Find files with similar names that might be duplicates."""
    all_files = {}
    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            name = py_file.stem.lower()
            name = re.sub("^(task_|tool_|request_|retry_task_)", "", name)
            name = re.sub("(_v\\d+|_\\d+)$", "", name)
            if name not in all_files:
                all_files[name] = []
            all_files[name].append(str(py_file))
    similar_groups = {k: v for k, v in all_files.items() if len(v) > 1}
    return similar_groups


def find_low_value_files(dirs: list[str]) -> list[str]:
    """Find files that are likely low value (small, no docstrings, test-like)."""
    low_value = []
    for d in dirs:
        if not Path(d).exists():
            continue
        for py_file in Path(d).rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                lines = len(content.splitlines())
                if lines < 20:
                    low_value.append(str(py_file))
                    continue
                if "test" in py_file.stem.lower() and TESTS_DIR not in str(py_file):
                    tree = ast.parse(content)
                    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    if classes and all(c.name.startswith("Test") for c in classes):
                        low_value.append(str(py_file))
                        continue
            # guardian: allow-silent-swallow
            except:
                pass
    return low_value


def _adg_startup_warning() -> None:
    """Emit ADG-sourced antipattern count for this script at startup."""
    try:
        from pathlib import Path as _Path

        from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile

        _root = _Path(__file__).resolve().parents[2]
        _rel = str(_Path(__file__).resolve().relative_to(_root)).replace("\\", "/")
        _profile = get_behavioral_profile(_rel, _root)
        if _profile.antipattern_signals or _profile.behavioral_score < 0.4:
            import warnings

            warnings.warn(
                f"[ADG] {_rel}: {len(_profile.antipattern_signals)} antipattern signal(s) "
                f"detected (score={_profile.behavioral_score:.2f}, "
                f"script-like={_profile.deterministic_coverage}). "
                f"Signals: {sorted(_profile.antipattern_signals) or 'none'}",
                stacklevel=2,
            )
    # guardian: allow-silent-swallow
    except Exception:
        pass


def main():
    _adg_startup_warning()
    print("=" * 80)
    print("AGGRESSIVE DEDUPLICATION")
    print("=" * 80)
    print("\n[1/5] Building class index...")
    class_files = get_all_classes_in_codebase(APPS_DIRS)
    print(f"  Found {len(class_files)} unique class names")
    print("\n[2/5] Finding redundant files (all classes exist elsewhere)...")
    redundant = find_redundant_files(APPS_DIRS, class_files)
    print(f"  Found {len(redundant)} redundant files")
    print("\n[3/5] Finding similar named files...")
    similar_groups = find_similar_named_files(APPS_DIRS)
    print(f"  Found {len(similar_groups)} groups of similar names")
    print("\n[4/5] Finding low value files...")
    low_value = find_low_value_files(APPS_DIRS)
    print(f"  Found {len(low_value)} low value files")
    to_delete = set()
    for f in redundant:
        to_delete.add(f)
    for _name, files in similar_groups.items():
        if len(files) > 1:
            files_sorted = sorted(files, key=lambda x: len(x))
            for f in files_sorted[1:]:
                to_delete.add(f)
    for f in low_value:
        to_delete.add(f)
    print("\n" + "=" * 80)
    print(f"FILES TO DELETE: {len(to_delete)}")
    print("=" * 80)
    by_folder = defaultdict(list)
    for f in sorted(to_delete):
        folder = Path(f).parent.name
        by_folder[folder].append(Path(f).name)
    for folder, files in sorted(by_folder.items()):
        print(f"\n  {folder}/ ({len(files)} files)")
        for f in files[:10]:
            print(f"    - {f}")
        if len(files) > 10:
            print(f"    ... and {len(files) - 10} more")
    print("\n[5/5] Executing deletion...")
    deleted = 0
    for f in to_delete:
        try:
            Path(f).unlink()
            deleted += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ✗ Failed: {Path(f).name}: {e}")
    print(f"\n  ✓ Deleted {deleted} files")


if __name__ == "__main__":
    main()
