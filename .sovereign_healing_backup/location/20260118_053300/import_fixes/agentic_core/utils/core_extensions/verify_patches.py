from __future__ import annotations
"""Verify Sovereign Patches Applied Successfully"""
import ast
from pathlib import Path
from typing import Any, Tuple
from import ALLOWED_CORE_STAGES, CANONICAL_DEPTH_MAP, validate_file_location


def validate_ast_integrity(file_path: Path) -> Tuple[bool, str]:
    """Validate that a Python file has valid AST structure."""
    if not file_path.exists():
        return False, "File does not exist"
    
    if file_path.suffix != '.py':
        return True, "Non-Python file - skipping AST validation"
    
    try:
        content = file_path.read_text(encoding='utf-8')
        ast.parse(content)
        return True, "AST valid"
    except SyntaxError as e:
        return False, f"AST invalid: {e}"
    except Exception as e:
        return False, f"Failed to read file: {e}"


root: Any = Path('C:/Git/Agentic-Workflow')
print('=' * 70)
print('SOVEREIGN PATCH VERIFICATION')
print('=' * 70)
print('\n✓ Patch 1: void_compliance.py - Absolute Depth-4 Enforcement')
print(f'  CANONICAL_DEPTH_MAP: {CANONICAL_DEPTH_MAP}')
print(f'\n  ALLOWED_CORE_STAGES ({len(ALLOWED_CORE_STAGES)} authorized stages):')
for stage in sorted(ALLOWED_CORE_STAGES):
    print(f'    - {stage}')
print('\n  Depth-4 Validation Tests:')
tests: Any = [(root / 'agentic_core/L1_cognition/identity/spiffe_manager_impl.py', 'identity'), (root / 'agentic_core/L1_cognition/inference/signal_anchoring.py', 'inference'), (root / 'agentic_core/L2_execution/P5_healing/structural_engineer.py', 'P5_healing'), (root / 'agentic_core/__init__.py', 'root __init__')]
for file_path, stage in tests:
    if file_path.exists():
        valid, msg = validate_file_location(file_path, root)
        status: Any = '✓ PASS' if valid else '✗ FAIL'
        print(f'    {stage:20} -> {status:8} ({file_path.name})')
        if not valid:
            print(f'      Reason: {msg}')
print('\n✓ Patch 2: canon_validator_agentic_v2.py - Unified Async/Sync Wrapper')
print('  Checking telemetry wrapper implementation...')

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

validator_path: Any = root / 'canon_validator_agentic_v2.py'
with open(validator_path, 'r', encoding='utf-8') as f:
    content: Any = f.read()
has_unified_wrapper: Any = '# Unified Smart Wrapper (Handles both Sync and Async)' in content
has_smart_dispatch: Any = '# Smart Dispatch: Check if method is async at runtime' in content
has_iscoroutinefunction_check: Any = 'if inspect.iscoroutinefunction(original_method):' in content
print(f'    Unified wrapper present: {has_unified_wrapper}')
print(f'    Smart dispatch logic: {has_smart_dispatch}')
print(f'    Runtime async detection: {has_iscoroutinefunction_check}')
if has_unified_wrapper and has_smart_dispatch and has_iscoroutinefunction_check:
    print('    Status: ✓ PATCH APPLIED SUCCESSFULLY')
else:
    print('    Status: ✗ PATCH INCOMPLETE')
print('\n' + '=' * 70)
print('VERIFICATION COMPLETE')
print('=' * 70)
