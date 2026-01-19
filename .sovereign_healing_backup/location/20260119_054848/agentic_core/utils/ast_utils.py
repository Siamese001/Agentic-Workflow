"""
AST Utilities - Centralized AST Parsing and Code Analysis

This module provides centralized utilities for parsing Python files
and extracting code structure information.

USAGE:
    from agentic_core.utils.ast_utils import (
        safe_parse_file,
        extract_classes,
        extract_functions,
        extract_imports,
        get_class_methods,
    )
    
    # Safely parse a Python file
    tree = safe_parse_file(Path("agent.py"))
    if tree:
        classes = extract_classes(tree)
        functions = extract_functions(tree)
        imports = extract_imports(tree)

SSOT PRINCIPLE:
    All AST parsing should use this module instead of inline
    ast.parse() calls scattered across 135+ files.
"""
from __future__ import annotations
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from agentic_core.utils.file_utils import safe_read_file

Logger = logging.getLogger(__name__)


def safe_parse_file(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    errors: str = "replace"
) -> Optional[ast.AST]:
    """
    Safely parse a Python file to an AST.
    
    Handles file reading errors and syntax errors gracefully.
    
    Args:
        file_path: Path to the Python file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: replace)
        
    Returns:
        AST tree, or None if parsing failed
        
    Example:
        tree = safe_parse_file(Path("agent.py"))
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    print(node.name)
    """
    path = Path(file_path)
    
    # Read file content
    content = safe_read_file(path, encoding=encoding, errors=errors)
    if content is None:
        return None
    
    # Parse to AST
    try:
        return ast.parse(content, filename=str(path))
    except SyntaxError as e:
        Logger.debug(f"[AST] Syntax error in {path}: {e}")
        return None
    except Exception as e:
        Logger.warning(f"[AST] Failed to parse {path}: {e}")
        return None


def safe_parse_source(
    source: str,
    filename: str = "<string>"
) -> Optional[ast.AST]:
    """
    Safely parse Python source code to an AST.
    
    Args:
        source: Python source code as string
        filename: Optional filename for error messages
        
    Returns:
        AST tree, or None if parsing failed
    """
    try:
        return ast.parse(source, filename=filename)
    except SyntaxError as e:
        Logger.debug(f"[AST] Syntax error in {filename}: {e}")
        return None
    except Exception as e:
        Logger.warning(f"[AST] Failed to parse {filename}: {e}")
        return None


def extract_classes(
    tree: ast.AST,
    include_nested: bool = False
) -> List[Dict[str, Any]]:
    """
    Extract class definitions from an AST.
    
    Args:
        tree: AST tree to analyze
        include_nested: If True, include nested classes
        
    Returns:
        List of dicts with class information:
        - name: Class name
        - bases: List of base class names
        - methods: List of method names
        - decorators: List of decorator names
        - lineno: Line number of class definition
        
    Example:
        tree = safe_parse_file(Path("agent.py"))
        classes = extract_classes(tree)
        for cls in classes:
            print(f"{cls['name']} inherits from {cls['bases']}")
    """
    if tree is None:
        return []
    
    classes = []
    
    # Use walk for nested, or just iterate body for top-level
    if include_nested:
        nodes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    else:
        nodes = [n for n in getattr(tree, 'body', []) if isinstance(n, ast.ClassDef)]
    
    for node in nodes:
        # Extract base class names
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
            elif isinstance(base, ast.Subscript):
                # Handle Generic[T] style bases
                if isinstance(base.value, ast.Name):
                    bases.append(base.value.id)
        
        # Extract method names
        methods = get_class_methods(node)
        
        # Extract decorator names
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)
                elif isinstance(dec.func, ast.Attribute):
                    decorators.append(dec.func.attr)
        
        classes.append({
            "name": node.name,
            "bases": bases,
            "methods": methods,
            "decorators": decorators,
            "lineno": node.lineno,
        })
    
    return classes


def extract_functions(
    tree: ast.AST,
    include_methods: bool = False,
    include_async: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract function definitions from an AST.
    
    Args:
        tree: AST tree to analyze
        include_methods: If True, include class methods
        include_async: If True, include async functions
        
    Returns:
        List of dicts with function information:
        - name: Function name
        - args: List of argument names
        - decorators: List of decorator names
        - is_async: Whether function is async
        - lineno: Line number of function definition
    """
    if tree is None:
        return []
    
    functions = []
    
    for node in ast.walk(tree):
        is_async = isinstance(node, ast.AsyncFunctionDef)
        is_func = isinstance(node, ast.FunctionDef)
        
        if not (is_func or (include_async and is_async)):
            continue
        
        # Skip methods if not requested
        if not include_methods:
            # Check if parent is a class
            # This is a simplified check - may not catch all cases
            pass  # For now, include all
        
        # Extract argument names
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        # Extract decorator names
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)
        
        functions.append({
            "name": node.name,
            "args": args,
            "decorators": decorators,
            "is_async": is_async,
            "lineno": node.lineno,
        })
    
    return functions


def extract_imports(
    tree: ast.AST
) -> Dict[str, List[str]]:
    """
    Extract import statements from an AST.
    
    Args:
        tree: AST tree to analyze
        
    Returns:
        Dict with two keys:
        - imports: List of module names from 'import x' statements
        - from_imports: List of dicts with 'module' and 'names' keys
        
    Example:
        tree = safe_parse_file(Path("agent.py"))
        imports = extract_imports(tree)
        print(imports['imports'])  # ['os', 'sys']
        print(imports['from_imports'])  # [{'module': 'pathlib', 'names': ['Path']}]
    """
    if tree is None:
        return {"imports": [], "from_imports": []}
    
    imports = []
    from_imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names = [alias.name for alias in node.names]
                from_imports.append({
                    "module": node.module,
                    "names": names,
                })
    
    return {
        "imports": imports,
        "from_imports": from_imports,
    }


def get_class_methods(
    class_node: ast.ClassDef
) -> List[str]:
    """
    Get method names from a class definition node.
    
    Args:
        class_node: AST ClassDef node
        
    Returns:
        List of method names
        
    Example:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = get_class_methods(node)
                print(f"{node.name} has methods: {methods}")
    """
    methods = []
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(item.name)
    return methods


def get_class_attributes(
    class_node: ast.ClassDef
) -> List[str]:
    """
    Get class-level attribute names from a class definition.
    
    Args:
        class_node: AST ClassDef node
        
    Returns:
        List of attribute names defined at class level
    """
    attributes = []
    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    attributes.append(target.id)
        elif isinstance(item, ast.AnnAssign):
            if isinstance(item.target, ast.Name):
                attributes.append(item.target.id)
    return attributes


def find_class_by_name(
    tree: ast.AST,
    class_name: str
) -> Optional[ast.ClassDef]:
    """
    Find a class definition by name in an AST.
    
    Args:
        tree: AST tree to search
        class_name: Name of the class to find
        
    Returns:
        ClassDef node, or None if not found
    """
    if tree is None:
        return None
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def has_method(
    class_node: ast.ClassDef,
    method_name: str
) -> bool:
    """
    Check if a class has a specific method.
    
    Args:
        class_node: AST ClassDef node
        method_name: Name of the method to check for
        
    Returns:
        True if method exists, False otherwise
    """
    return method_name in get_class_methods(class_node)


def get_docstring(node: Union[ast.ClassDef, ast.FunctionDef, ast.Module]) -> Optional[str]:
    """
    Extract docstring from a node.
    
    Args:
        node: AST node (ClassDef, FunctionDef, or Module)
        
    Returns:
        Docstring text, or None if no docstring
    """
    return ast.get_docstring(node)


__all__ = [
    "safe_parse_file",
    "safe_parse_source",
    "extract_classes",
    "extract_functions",
    "extract_imports",
    "get_class_methods",
    "get_class_attributes",
    "find_class_by_name",
    "has_method",
    "get_docstring",
]
