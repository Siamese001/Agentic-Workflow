"""
L5 Runner for CodeValidatorAgent.

This module provides subprocess-callable entry points for L0-L4 scripts
to invoke CodeValidatorAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.code_validator_runner --action=validate
    python -m agentic_core.L5_safety.runners.code_validator_runner --action=validate_directory --directory=policy_engine
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent

def validate_repository(project_root: Path) -> dict:
    """Validate entire repository with CodeValidatorAgent."""
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
    agent = CodeValidatorAgent(project_root=project_root)
    result = agent.validate_repository()
    violations = []
    for v in result.get('violations', []):
        violations.append({'file_path': str(v.file_path), 'line_number': v.line_number, 'column': v.column, 'error_message': v.error_message, 'severity': getattr(v, 'severity', 'error')})
    return {'success': True, 'total_violations': result.get('total_violations', 0), 'violations': violations}

def validate_directory(project_root: Path, directory: str) -> dict:
    """Validate specific directory with CodeValidatorAgent."""
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
    agent = CodeValidatorAgent(project_root=project_root)
    target_dir = project_root / directory
    if not target_dir.exists():
        return {'success': False, 'error': f'Directory does not exist: {target_dir}'}
    result = agent.validate_repository()
    violations = []
    for v in result.get('violations', []):
        if target_dir in Path(v.file_path).parents:
            violations.append({'file_path': str(v.file_path), 'line_number': v.line_number, 'column': v.column, 'error_message': v.error_message, 'severity': getattr(v, 'severity', 'error')})
    return {'success': True, 'directory': directory, 'total_violations': len(violations), 'violations': violations}

def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description='CodeValidatorAgent Runner')
    parser.add_argument('--action', choices=['validate', 'validate_directory'], required=True, help='Action to perform')
    parser.add_argument('--directory', type=str, help='Directory to validate (required for validate_directory)')
    parser.add_argument('--project-root', type=str, default=None, help='Project root path (defaults to auto-detect)')
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    try:
        if args.action == 'validate':
            result = validate_repository(project_root)
        elif args.action == 'validate_directory':
            if not args.directory:
                result = {'success': False, 'error': '--directory required for validate_directory'}
            else:
                result = validate_directory(project_root, args.directory)
        else:
            result = {'success': False, 'error': f'Unknown action: {args.action}'}
        print(json.dumps(result, default=str))
        return 0 if result.get('success') else 1
    # guardian: allow-silent-swallow
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        return 1
if __name__ == '__main__':
    sys.exit(main())
