#!/usr/bin/env python3
"""
L6 Runtime: Void Compliance Helper Functions
Exception checking and AST-based import extraction utilities.
"""
import ast
import fnmatch
import re
from pathlib import Path
from typing import Set

from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_EXCEPTIONS


def is_excepted_from_key(key_id: int, file_path: Path, line_content: str = "") -> bool:
    """
    [L6 HARDENING] Central SSOT check for known false-positive exceptions.
    Supports exact paths, glob patterns, and regex-based line suppression.
    
    Args:
        key_id: Canon key number to check exceptions for
        file_path: Path to the file being validated
        line_content: Optional line content for pattern matching
        
    Returns:
        True if this file/line is excepted from the key validation
    """
    exceptions = CANON_KEY_EXCEPTIONS.get(key_id, {})
    if not exceptions:
        return False
        
    # 1. Resolve relative path for SSOT comparison
    try:
        project_root = Path(__file__).resolve().parents[3]  # Adjust based on void_compliance location
        rel_path = str(file_path.relative_to(project_root)).replace("\\", "/")
    except (ValueError, IndexError):
        rel_path = file_path.name

    # 2. Check file-level exceptions (Exact or Glob)
    file_exceptions = exceptions.get("files", set())
    if rel_path in file_exceptions or any(fnmatch.fnmatch(rel_path, pattern) for pattern in file_exceptions):
        return True

    # 3. Check line-level pattern exceptions
    if line_content:
        for pattern in exceptions.get("patterns", []):
            if re.search(pattern, line_content):
                return True
                
    return False


def get_ast_safe_imports(content: str) -> Set[str]:
    """
    [L5 SAFETY] Uses AST to extract functional imports only, ignoring comments/docstrings.
    
    Args:
        content: Python source code as string
        
    Returns:
        Set of imported module names
    """
    imports = set()
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except SyntaxError:
        # Fallback to regex if file is currently broken during healing
        regex_imports = re.findall(r"^(?:import|from)\s+([a-zA-Z0-9_.]+)", content, re.MULTILINE)
        imports.update(regex_imports)
    return imports
