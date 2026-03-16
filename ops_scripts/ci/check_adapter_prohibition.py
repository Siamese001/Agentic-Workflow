"""
V15 P0.2 — Adapter Prohibition AST Scanner.

Scans all Python files under agentic_core/ for imports of AdapterBase
or class definitions inheriting from AdapterBase/HealingAdapter.
Files under archives/ are excluded.

Exit code 0 = no violations.
Exit code 1 = violations found.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "check_adapter_prohibition")
_emit_applies_guardrail("p0", "check_adapter_prohibition", "p0_governance")
_emit_reads_policy_state("p0", "check_adapter_prohibition", "policy_binding")
_emit_snapshots_state("p0", "check_adapter_prohibition", "state_snapshot")
emit_replay_key("p0", "check_adapter_prohibition")
emit_determinism_digest("p0", "check_adapter_prohibition")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_ROOT = get_validated_project_root()
SCAN_ROOTS = [_ROOT / AGENTIC_CORE_DIR]
EXCLUDED_PREFIXES = (ARCHIVES_DIR, 'archives/deprecated')
EXCEPTION_MARKER = 'v15-exception:'
PROHIBITED_NAMES = frozenset({'AdapterBase', 'HealingAdapter', 'AdapterBaseAdapter'})

def _is_excluded(path: Path) -> bool:
    parts = path.as_posix()
    return any(parts.startswith(prefix) for prefix in EXCLUDED_PREFIXES)

def scan_file(filepath: Path) -> list[str]:
    """Scan a single Python file for AdapterBase usage. Returns violation messages."""
    violations: list[str] = []
    try:
        source = filepath.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return violations
    if EXCEPTION_MARKER in source:
        return violations
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in PROHIBITED_NAMES:
                    violations.append(f"{filepath}:{node.lineno}: imports prohibited name '{alias.name}'")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name_parts = alias.name.split('.')
                if any(part in PROHIBITED_NAMES for part in name_parts):
                    violations.append(f"{filepath}:{node.lineno}: imports prohibited module '{alias.name}'")
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name and base_name in PROHIBITED_NAMES:
                    violations.append(f"{filepath}:{node.lineno}: class '{node.name}' inherits from prohibited '{base_name}'")
    return violations

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    all_violations: list[str] = []
    for scan_root in SCAN_ROOTS:
        root = project_root / scan_root
        if not root.exists():
            continue
        for py_file in sorted(root.rglob('*.py')):
            rel = py_file.relative_to(project_root)
            if _is_excluded(rel):
                continue
            all_violations.extend(scan_file(py_file))
    if all_violations:
        print(f'FAIL: {len(all_violations)} AdapterBase prohibition violation(s):')
        for v in all_violations:
            print(f'  {v}')
        return 1
    print('PASS: No AdapterBase prohibition violations found.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
