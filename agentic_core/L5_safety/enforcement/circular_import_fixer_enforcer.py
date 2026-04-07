from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

"\nFix circular imports in agentic_core by converting absolute imports to relative imports.\n\nThis script:\n1. Scans all Python files in agentic_core/\n3. Converts them to relative imports: from .L1_cognition... or from ..L1_cognition...\n4. Preserves imports from outside agentic_core (e.g., from apps_shared, from schemas)\n"
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)


def calculate_relative_import(file_path: Path, import_path: str, project_root: Path) -> str:
    """
    Calculate the correct relative import path.

    Args:
        file_path: Path to the file being modified
        import_path: The import path after 'agentic_core.' (e.g., 'L1_cognition.planning.types')
        project_root: Root of the agentic_core package

    Returns:
        Relative import path (e.g., '.planning.types' or '..L1_cognition.planning.types')
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "calculate_relative_import", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "calculate_relative_import", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "calculate_relative_import")
    file_dir: Any = file_path.parent
    try:
        rel_to_core: Any = file_dir.relative_to(project_root)
    except ValueError:
        rel_to_core: Any = Path(".")
    import_parts: Any = import_path.split(".")
    if str(rel_to_core) == ".":
        file_parts: Any = []
    else:
        file_parts: Any = list(rel_to_core.parts)
    if len(file_parts) == 0:
        return f".{import_path}"
    if len(import_parts) > 0 and len(file_parts) > 0 and (import_parts[0] == file_parts[0]):
        if len(file_parts) == 1:
            if len(import_parts) == 1:
                return "."
            else:
                return f".{'.'.join(import_parts[1:])}"
        else:
            common_depth: Any = 1
            for i in range(1, min(len(file_parts), len(import_parts))):
                if file_parts[i] == import_parts[i]:
                    common_depth: Any = i + 1
                else:
                    break
            levels_up: Any = len(file_parts) - common_depth
            remaining_import: Any = ".".join(import_parts[common_depth:])
            if levels_up == 0:
                return f".{remaining_import}" if remaining_import else "."
            else:
                dots: Any = "." * (levels_up + 1)
                return f"{dots}{remaining_import}" if remaining_import else dots
    else:
        levels_up: Any = len(file_parts)
        dots: Any = "." * (levels_up + 1)
        return f"{dots}{import_path}"
    return f"..{import_path}"


def fix_imports_in_file(
    file_path: Path, agentic_core_root: Path, dry_run: bool = False,
) -> tuple[int, list[str]]:
    """
    Fix imports in a single file.

    Returns:
        Tuple of (number of changes, list of changes made)
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        return (0, [f"ERROR reading {file_path}: {e}"])
    original_content: Any = content
    changes: Any = []
    pattern: Any = "^(\\s*)from agentic_core\\.([a-zA-Z0-9_\\.]+) import (.+)$"
    lines: Any = content.split("\n")
    modified_lines: Any = []
    for line in lines:
        match: Any = re.match(pattern, line)
        if match:
            indent: Any = match.group(1)
            import_path: Any = match.group(2)
            imported_items: Any = match.group(3)
            relative_path: Any = calculate_relative_import(file_path, import_path, agentic_core_root)
            new_line: Any = f"{indent}from {relative_path} import {imported_items}"
            modified_lines.append(new_line)
            changes.append(f"  {line.strip()} -> {new_line.strip()}")
        else:
            modified_lines.append(line)
    new_content: Any = "\n".join(modified_lines)
    if new_content != original_content and (not dry_run):
        try:
            _wg.open_write(file_path, new_content)
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            return (0, [f"ERROR writing {file_path}: {e}"])
    num_changes: Any = len(changes)
    return (num_changes, changes)


def main() -> Any:
    """Main execution function."""
    script_dir: Any = Path(__file__).parent
    agentic_core_root: Any = script_dir / AGENTIC_CORE_DIR
    if not agentic_core_root.exists():
        print(f"ERROR: agentic_core directory not found at {agentic_core_root}")
        return
    print("=" * 80)
    print("FIXING CIRCULAR IMPORTS IN AGENTIC_CORE")
    print("=" * 80)
    print(f"Root: {agentic_core_root}")
    print()
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    py_files: Any = list(get_python_files(agentic_core_root))
    print(f"Found {len(py_files)} Python files")
    print()
    total_changes: Any = 0
    files_modified: Any = 0
    for py_file in py_files:
        num_changes, changes = fix_imports_in_file(py_file, agentic_core_root, dry_run=False)
        if num_changes > 0:
            files_modified += 1
            total_changes += num_changes
            rel_path: Any = py_file.relative_to(agentic_core_root)
            print(f"✓ {rel_path} ({num_changes} changes)")
            for change in changes:
                print(change)
            print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {len(py_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total changes: {total_changes}")
    print()
    print("✓ Circular import fix complete!")


if __name__ == "__main__":
    main()
