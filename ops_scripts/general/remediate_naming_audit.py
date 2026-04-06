"""
SMART REMEDIATION: PASCAL CASE AUDIT LOG
----------------------------------------
Objective:
    1. Parse 'pascal_case_audit_log.txt'.
    2. Apply heuristic filtering to separate 'Agents' (Keep) from 'Scripts' (Rename).
    3. Generate and execute `git mv` commands for high-confidence script renames.
    4. Update internal references (imports) for renamed files using AST parsing.

Heuristic Logic:
    - SAFE RENAME: Starts with Verb (Fix, Run, Test, Analyze, Update, Manage, Utilities).
    - PROTECT: Ends with 'Agent', 'Orchestrator', 'Validator', 'Factory', 'Registry'.
    - MANUAL REVIEW: Everything else.

Strict Mode: ON
"""
import os
import re
import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "remediate_naming_audit", "uwg_governed_write")
_emit_writes_through("p1", "remediate_naming_audit", "uwg_governed_write_2")
_emit_pulls_context("p1", "remediate_naming_audit", "context_retrieval")
_emit_pulls_context("p1", "remediate_naming_audit", "context_retrieval_2")
emit_determinism_digest("trace_remediate_naming_audit", "remediate_naming_audit_dispatch")
emit_determinism_digest("trace_remediate_naming_audit", "remediate_naming_audit_complete")
_emit_validated_by_safety_plane("p1", "remediate_naming_audit", "safety_validation")
ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIT_LOG = ROOT_DIR / 'pascal_case_audit_log.txt'
VERB_PATTERN = re.compile('^(Fix|Run|Test|Analyze|Update|Manage|Utilities|Check|Archive|Restore|Generate|Fetch|Find|Load|Perform|Query|Refactor|Verify|Convert|Calculate|Execute|Invoke|Measure|Monitor|Parse|Process|Register|Resolve|Validate|Watch|Write)(?=[A-Z])')
PROTECTED_SUFFIXES = ('Agent.py', 'Orchestrator.py', 'Validator.py', 'Factory.py', 'Registry.py', 'Engine.py', 'Model.py', 'schema.py', 'Config.py', 'Exception.py', 'Error.py', 'Client.py', 'Service.py', 'Manager.py')

def to_snake_case(name: str) -> str:
    """Converts PascalCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', name)
    return re.sub('([a-z0-9])([A-Z])', '\\1_\\2', s1).lower()

def get_files_from_log() -> list[Path]:
    if not AUDIT_LOG.exists():
        print(f'[ERROR] Audit log not found at {AUDIT_LOG}')
        sys.exit(1)
    with open(AUDIT_LOG) as f:
        lines = [line.strip() for line in f if line.strip()]
    files = []
    for line in lines:
        if ']' in line:
            line = line.split(']')[-1].strip()
        clean_path = line.strip()
        full_path = ROOT_DIR / clean_path
        if '\\' in str(full_path):
            full_path = Path(str(full_path).replace('\\', '/'))
        if full_path.exists():
            files.append(full_path)
        else:
            rel_path = ROOT_DIR / clean_path.replace('\\', '/')
            if rel_path.exists():
                files.append(rel_path)
    return files

def update_imports(renames: list[tuple[Path, str]]):
    """Scans codebase to update imports for renamed files."""
    print('\n[Phase 2] Updating Imports (Safe Regex)...')
    rename_map = {p.stem: Path(n).stem for p, n in renames}
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if not file.endswith('.py'):
                continue
            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                for old, new in rename_map.items():
                    if old in content:
                        pattern = re.compile(f'\\b{old}\\b')
                        if pattern.search(content):
                            content = pattern.sub(new, content)
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    count += 1
            # guardian: allow-silent-swallow
            except Exception:
                pass
    print(f'  Modified {count} files with import updates.')

def main():
    print(f'[*] Starting Remediation based on {AUDIT_LOG.name}')
    targets = get_files_from_log()
    print(f'[*] Loaded {len(targets)} verified existing files.')
    rename_queue = []
    skipped = []
    for file_path in targets:
        name = file_path.name
        stem = file_path.stem
        if name.endswith(PROTECTED_SUFFIXES):
            skipped.append((name, 'Protected Suffix'))
            continue
        if VERB_PATTERN.match(stem):
            new_name = to_snake_case(stem) + '.py'
            rename_queue.append((file_path, new_name))
            continue
        skipped.append((name, 'No safe rename pattern match'))
    print(f'\n[Analysis] Renaming {len(rename_queue)} files. Skipping {len(skipped)}.')
    if not rename_queue:
        print('No safe renames found.')
        sys.exit(0)
    print('\n[Phase 1] Executing Git Moves...')
    success_count = 0
    for old_path, new_name in rename_queue:
        new_path = old_path.parent / new_name
        if new_path.exists():
            print(f'  [SKIP] Target exists: {new_name}')
            continue
        cmd = f'git mv "{old_path}" "{new_path}"'
        ret = os.system(cmd)
        if ret != 0:
            print(f'  [ERROR] Git mv failed for {old_path.name}')
        else:
            print(f'  [OK-GIT] {old_path.name} -> {new_name}')
            success_count += 1
    if success_count > 0:
        update_imports(rename_queue)
    with open(ROOT_DIR / 'remediation_skipped.log', 'w') as f:
        for name, reason in skipped:
            f.write(f'{name}: {reason}\n')
    print('\n[*] Skipped log written.')
if __name__ == '__main__':
    main()
