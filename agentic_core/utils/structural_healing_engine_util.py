"""
structural_healing_engine.py - Stateless Structural Healing Operations

[MIXIN REFACTOR] Extracted pure logic from structural_healing_mixin.py.
All functions are stateless (no Agent `self` dependency).
Naming convention: *_engine.py = pure logic/transformations.

Provides:
- File relocation with integrity verification
- AST-based structure analysis
- Complexity scoring
- File split suggestions
"""
from __future__ import annotations
import ast
import hashlib
import shutil
from pathlib import Path
from typing import Any
from agentic_core.runtime.exceptions.SovereignError import StructuralError
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def relocate_file(source_path: Path, target_path: Path, project_root: Path, *, dry_run: bool=True) -> dict[str, Any]:
    """Relocate a file with integrity verification and rollback.

    Args:
        source_path: Source file to move.
        target_path: Destination path.
        project_root: Project root for safety boundary checks.
        dry_run: If True, only validate without moving.

    Returns:
        Dict with 'status' key ('success', 'blocked', 'dry_run').
    """
    if not source_path.exists():
        raise StructuralError(f'Source file not found: {source_path}')
    if not _is_safe_relocation(source_path, target_path, project_root):
        raise StructuralError(f'Unsafe relocation: {source_path} -> {target_path}')
    source_hash = calculate_file_hash(source_path)
    if target_path.exists():
        return {'status': 'blocked', 'reason': 'target_exists'}
    if dry_run:
        return {'status': 'dry_run', 'source': str(source_path), 'target': str(target_path)}
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(target_path))
    if calculate_file_hash(target_path) != source_hash:
        shutil.move(str(target_path), str(source_path))
        raise StructuralError('File integrity check failed after relocation')
    return {'status': 'success'}

def analyze_file_structure(file_path: Path, *, max_lines: int=800) -> dict[str, Any]:
    """Analyze a Python file's structure for potential issues.

    Args:
        file_path: Path to the Python file.
        max_lines: Threshold for "file too large" warning.

    Returns:
        Dict with line_count, size_bytes, has_syntax_errors, complexity_score, issues.
    """
    if not file_path.exists():
        raise StructuralError(f'File not found: {file_path}')
    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    structure_info: dict[str, Any] = {'line_count': len(lines), 'size_bytes': file_path.stat().st_size, 'has_syntax_errors': False, 'complexity_score': 0, 'issues': []}
    if structure_info['line_count'] > max_lines:
        structure_info['issues'].append(f"File too large: {structure_info['line_count']} lines (limit: {max_lines})")
    try:
        ast.parse(content)
    except SyntaxError as e:
        structure_info['has_syntax_errors'] = True
        structure_info['issues'].append(f'Syntax error: {e}')
    structure_info['complexity_score'] = calculate_complexity(content)
    return structure_info

def calculate_complexity(content: str) -> int:
    """Calculate simplified cyclomatic complexity score from source text.

    Args:
        content: Python source code string.

    Returns:
        Integer complexity score (1 = base).
    """
    complexity = 1
    control_keywords = ['if', 'elif', 'for', 'while', 'try', 'except', 'with']
    for keyword in control_keywords:
        complexity += content.count(f' {keyword} ')
    complexity += content.count('def ')
    complexity += content.count('class ')
    return complexity

def suggest_file_split(file_path: Path, *, max_lines: int=800) -> list[dict[str, Any]]:
    """Suggest splitting strategies for large files.

    Args:
        file_path: Path to the Python file.
        max_lines: Threshold below which no split is suggested.

    Returns:
        List of suggestion dicts with 'strategy', 'description', 'priority'.
    """
    structure = analyze_file_structure(file_path, max_lines=max_lines)
    if structure['line_count'] <= max_lines:
        return []
    suggestions = []
    content = file_path.read_text(encoding='utf-8')
    if 'class ' in content:
        suggestions.append({'strategy': 'split_by_classes', 'description': 'Split file into separate class files', 'priority': 'high'})
    if 'def ' in content:
        suggestions.append({'strategy': 'split_by_functions', 'description': 'Group related functions into modules', 'priority': 'medium'})
    return suggestions

def calculate_file_hash(file_path: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

def _is_safe_relocation(source: Path, target: Path, project_root: Path) -> bool:
    """Check both paths are within the project root."""
    try:
        source.resolve().relative_to(project_root.resolve())
        target.resolve().relative_to(project_root.resolve())
        return True
    except ValueError:
        return False
