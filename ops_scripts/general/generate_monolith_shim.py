"""
Generate the monolith shim that re-exports everything from the modular package.

Scans all 197 importers to find exactly which names they import from
structure_blueprint_config, then generates a shim that re-exports them.
"""
from __future__ import annotations

import ast
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

_emit_records_execution_trace("p0", "evidence", "generate_monolith_shim")
_emit_applies_guardrail("p0", "generate_monolith_shim", "p0_governance")
_emit_reads_policy_state("p0", "generate_monolith_shim", "policy_binding")
_emit_snapshots_state("p0", "generate_monolith_shim", "state_snapshot")
emit_replay_key("p0", "generate_monolith_shim")
emit_determinism_digest("p0", "generate_monolith_shim")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
ROOT = get_validated_project_root()
MONOLITH = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint_config.py'
MOD_DIR = ROOT / AGENTIC_CORE_DIR / 'L5_safety' / 'config' / 'structure_blueprint'

def find_all_imported_names() -> set[str]:
    """Scan every .py file for names imported from structure_blueprint_config."""
    imported_names: set[str] = set()
    for py_file in ROOT.rglob('*.py'):
        rel = py_file.relative_to(ROOT)
        rel_str = str(rel).replace('\\', '/')
        if 'structure_blueprint_config.py' in rel_str and 'test' not in rel_str:
            continue
        if 'structure_blueprint/' in rel_str:
            continue
        if '_migrate_' in rel_str or 'generate_' in rel_str:
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, UnicodeDecodeError):
            continue
        if 'structure_blueprint_config' not in source:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'structure_blueprint_config' in node.module:
                    if node.names:
                        for alias in node.names:
                            imported_names.add(alias.name)
    return imported_names

def find_modular_locations(names: set[str]) -> dict[str, str]:
    """Find which modular module each name lives in."""
    name_to_module: dict[str, str] = {}
    for f in sorted(MOD_DIR.glob('*.py')):
        if f.name == '__init__.py':
            continue
        src = f.read_text(encoding='utf-8')
        tree = ast.parse(src)
        for node in ast.iter_child_nodes(tree):
            node_name = None
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        node_name = t.id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                node_name = node.target.id
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                node_name = node.name
            elif isinstance(node, ast.ClassDef):
                node_name = node.name
            if node_name and node_name in names:
                name_to_module[node_name] = f.stem
    return name_to_module

def generate_shim(imported_names: set[str], name_to_module: dict[str, str]) -> str:
    """Generate the shim content."""
    parts: list[str] = []
    parts.append('"""')
    parts.append('Structure Blueprint Config - Backward Compatible Shim.')
    parts.append('')
    parts.append('SSOT is now: agentic_core.L5_safety.config.structure_blueprint/')
    parts.append('This file re-exports all public names for backward compatibility.')
    parts.append('All 197+ existing importers will continue to work unchanged.')
    parts.append('')
    parts.append('DO NOT add new definitions here. Add them to the modular package instead.')
    parts.append('"""')
    parts.append('')
    parts.append('from __future__ import annotations')
    parts.append('')
    by_module: dict[str, list[str]] = {}
    missing: list[str] = []
    for name in sorted(imported_names):
        if name in name_to_module:
            mod = name_to_module[name]
            if mod not in by_module:
                by_module[mod] = []
            by_module[mod].append(name)
        else:
            missing.append(name)
    module_order = ['ssot', 'territories', 'classification', 'semantics', 'artifacts', 'derived', 'governance']
    for mod in module_order:
        names = by_module.get(mod, [])
        if not names:
            continue
        parts.append(f'from agentic_core.L5_safety.config.structure_blueprint.{mod} import (')
        for n in sorted(names):
            parts.append(f'    {n},')
        parts.append(')')
        parts.append('')
    if missing:
        parts.append('')
        parts.append(f'# WARNING: {len(missing)} names not found in modular package:')
        for n in sorted(missing):
            parts.append(f'#   {n}')
    parts.append('')
    parts.append('# Re-export all names for backward compatibility')
    all_names = sorted(imported_names & set(name_to_module.keys()))
    parts.append('__all__ = [')
    for n in all_names:
        parts.append(f'    "{n}",')
    parts.append(']')
    parts.append('')
    return '\n'.join(parts)

def main() -> None:
    print('Scanning importers...')
    imported_names = find_all_imported_names()
    print(f'Found {len(imported_names)} unique names imported from monolith')
    print('Locating names in modular package...')
    name_to_module = find_modular_locations(imported_names)
    found = imported_names & set(name_to_module.keys())
    missing = imported_names - set(name_to_module.keys())
    print(f'Found: {len(found)}, Missing: {len(missing)}')
    if missing:
        print(f'MISSING names: {sorted(missing)}')
    shim = generate_shim(imported_names, name_to_module)
    output = ROOT / 'data' / 'freeze_reports' / '_monolith_shim.py'
    output.write_text(shim, encoding='utf-8')
    print(f'\nWrote shim to {output} ({len(shim.splitlines())} lines)')
    ast.parse(shim)
    print('Syntax OK')
if __name__ == '__main__':
    main()
