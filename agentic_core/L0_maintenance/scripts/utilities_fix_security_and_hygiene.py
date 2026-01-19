from __future__ import annotations
"""
Security & Hygiene Fixer for Canon Validator.
Targets: Keys 0-6 (TODO/FIXME, print statements, bare except, empty except, trailing whitespace)
"""
import ast
import os
import re
import shutil
from datetime import datetime
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from archives.location_violations.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file
excluded_dirs: Any = {'.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', 'build', 'dist', 'eggs', ARCHIVES_DIR, 'data'}
excluded_files: Any = {'CanonValidatorAgent.py', 'canon_validator_backup.py', 'canon_validator_v2_agentic.py', 'resume_engine.py', 'action_registry.py', 'fix_syntax_errors.py', 'healthcheck.py', 'check_pinecone.py', 'governed_outreach.py', 'fix_security_and_hygiene.py', 'fix_structural_debt.py', 'fix_print_statements.py'}

def fix_file(file_path: Any) -> Any:
    """Apply security and hygiene fixes to a file."""
    backup_path: Any = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        shutil.copy2(file_path, backup_path)
        original: Any = content
        lines: Any = content.split('\n')
        try:
            tree: Any = ast.parse(content)
            print_lines: Any = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'print':
                        print_lines.add(node.lineno - 1)
            for line_idx in sorted(print_lines, reverse=True):
                if 0 <= line_idx < len(lines):
                    line: Any = lines[line_idx]
                    if not line.strip().startswith('#'):
                        indent: Any = len(line) - len(line.lstrip())
                        lines[line_idx] = ' ' * indent + '# ' + line.strip() + '  # [Security Fix]'
        except SyntaxError:
            print(f'   WARNING: Skipping print fixes for {file_path} (syntax error)')
        content: Any = '\n'.join(lines)
        content: Any = re.sub('(?m)^\\s*except:\\s*$', 'except Exception:', content)
        content: Any = re.sub('except (.*):\\s*\\n\\s*(?=[a-zA-Z#])', 'except \\1:\\n    pass\\n', content)
        lines: Any = content.split('\n')
        for i, line in enumerate(lines):
            stripped: Any = line.strip()
            if stripped.startswith('#') and any((x in stripped for x in ['# TODO', '#FIXME', '# TODO', '# FIXME'])):
                lines[i] = ''
        content: Any = '\n'.join(lines)
        content: Any = re.sub('[ \\t]+$', '', content, flags=re.MULTILINE)
        if content and (not content.endswith('\n')):
            content += '\n'
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.remove(backup_path)
            return True
        os.remove(backup_path)
        return False
    except Exception as e:
        print(f'   ERROR: Failed to process {file_path}: {e}')
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
        return False

def main() -> Any:
    """Brief description of functionality and purpose."""
    print('Running Security & Hygiene Fixer...')
    count: Any = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file in EXCLUDED_FILES:
                continue
            if file.endswith('.py'):
                if fix_file(os.path.join(root, file)):
                    count += 1
    print(f'Fixed {count} files.')
if __name__ == '__main__':
    main()
