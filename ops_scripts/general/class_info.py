#!/usr/bin/env python3
"""
Intelligent Deduplication Analyzer for apps_* folders.

Uses AST analysis to identify:
1. Duplicate classes (same name, similar methods)
2. Duplicate functions (same name, similar signatures)
3. Near-duplicate files (high content similarity)
4. Best version selection (most complete, best documented)
"""

import ast
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ============================================================================
# CONFIGURATION
# ============================================================================

APPS_DIRS = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR]
SKIP_FILES = {"__init__.py", "conftest.py"}

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class ClassInfo:
    """Information about a class."""

    name: str
    file_path: str
    bases: list[str]
    methods: list[str]
    method_count: int
    loc: int
    has_docstring: bool
    docstring_len: int
    is_agent: bool
    content_hash: str  # Hash of class body for exact duplicate detection


@dataclass
class FunctionInfo:
    """Information about a function."""

    name: str
    file_path: str
    params: list[str]
    loc: int
    has_docstring: bool
    content_hash: str


@dataclass
class FileInfo:
    """Information about a file."""

    path: str
    classes: list[ClassInfo]
    functions: list[FunctionInfo]
    loc: int
    content_hash: str
    quality_score: float  # Based on docstrings, type hints, etc.


# ============================================================================
# AST ANALYSIS
# ============================================================================


def get_node_source(node: ast.AST, source_lines: list[str]) -> str:
    """Get source code for an AST node."""
    try:
        start = node.lineno - 1
        end = getattr(node, "end_lineno", start + 1)
        return "\n".join(source_lines[start:end])
    except:
        return ""


def analyze_class(node: ast.ClassDef, file_path: str, source_lines: list[str]) -> ClassInfo:
    """Analyze a class definition."""
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(base.attr)

    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            methods.append(item.name)

    # Get docstring
    docstring = ast.get_docstring(node) or ""

    # Get class body hash
    class_source = get_node_source(node, source_lines)
    content_hash = hashlib.md5(class_source.encode()).hexdigest()[:12]

    return ClassInfo(
        name=node.name,
        file_path=file_path,
        bases=bases,
        methods=methods,
        method_count=len(methods),
        loc=getattr(node, "end_lineno", node.lineno) - node.lineno,
        has_docstring=bool(docstring),
        docstring_len=len(docstring),
        is_agent=node.name.endswith("Agent"),
        content_hash=content_hash,
    )


def analyze_function(
    node: ast.FunctionDef,
    file_path: str,
    source_lines: list[str],
) -> FunctionInfo:
    """Analyze a function definition."""
    params = [arg.arg for arg in node.args.args if arg.arg != "self"]
    docstring = ast.get_docstring(node) or ""

    func_source = get_node_source(node, source_lines)
    content_hash = hashlib.md5(func_source.encode()).hexdigest()[:12]

    return FunctionInfo(
        name=node.name,
        file_path=file_path,
        params=params,
        loc=getattr(node, "end_lineno", node.lineno) - node.lineno,
        has_docstring=bool(docstring),
        content_hash=content_hash,
    )


def analyze_file(file_path: Path) -> FileInfo | None:
    """Analyze a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        source_lines = content.splitlines()
        tree = ast.parse(content)
    except:
        return None

    classes = []
    functions = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(analyze_class(node, str(file_path), source_lines))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if not node.name.startswith("_"):
                functions.append(analyze_function(node, str(file_path), source_lines))

    # Calculate quality score
    has_docstrings = sum(1 for c in classes if c.has_docstring) + sum(1 for f in functions if f.has_docstring)
    total_entities = len(classes) + len(functions)
    docstring_ratio = has_docstrings / max(total_entities, 1)

    has_types = "typing" in content or ": " in content
    quality_score = (docstring_ratio * 50) + (30 if has_types else 0) + min(len(content) / 100, 20)

    return FileInfo(
        path=str(file_path),
        classes=classes,
        functions=functions,
        loc=len(source_lines),
        content_hash=hashlib.md5(content.encode()).hexdigest()[:12],
        quality_score=quality_score,
    )


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================


def find_duplicate_classes(all_files: list[FileInfo]) -> dict[str, list[ClassInfo]]:
    """Find classes with the same name across files."""
    class_map = defaultdict(list)

    for file_info in all_files:
        for cls in file_info.classes:
            class_map[cls.name].append(cls)

    # Filter to only duplicates
    return {name: classes for name, classes in class_map.items() if len(classes) > 1}


def find_duplicate_functions(all_files: list[FileInfo]) -> dict[str, list[FunctionInfo]]:
    """Find functions with the same name across files."""
    func_map = defaultdict(list)

    for file_info in all_files:
        for func in file_info.functions:
            func_map[func.name].append(func)

    # Filter to only duplicates (ignore common names)
    common_names = {"main", "test", "run", "execute", "process", "validate", "init"}
    return {name: funcs for name, funcs in func_map.items() if len(funcs) > 1 and name not in common_names}


def find_exact_duplicate_files(all_files: list[FileInfo]) -> dict[str, list[FileInfo]]:
    """Find files with identical content."""
    hash_map = defaultdict(list)

    for file_info in all_files:
        hash_map[file_info.content_hash].append(file_info)

    return {h: files for h, files in hash_map.items() if len(files) > 1}


def select_best_version(duplicates: list[ClassInfo]) -> tuple[ClassInfo, list[ClassInfo]]:
    """Select the best version of a duplicate class."""
    # Score each version
    scored = []
    for cls in duplicates:
        score = 0
        score += cls.method_count * 5  # More methods = more complete
        score += cls.loc * 0.5  # Longer = more complete
        score += 20 if cls.has_docstring else 0
        score += cls.docstring_len * 0.1
        # Prefer files in base_agents or engines over utils
        if "base_agents" in cls.file_path:
            score += 10
        elif "engines" in cls.file_path and "utils" not in cls.file_path:
            score += 5
        scored.append((score, cls))

    scored.sort(key=lambda x: -x[0])
    best = scored[0][1]
    others = [s[1] for s in scored[1:]]

    return best, others


# ============================================================================
# MAIN
# ============================================================================


def main():
    print("=" * 80)
    print("INTELLIGENT DEDUPLICATION ANALYZER")
    print("=" * 80)

    # Scan all apps_* files
    print("\n[1/4] Scanning apps_* folders...")
    all_files = []

    for apps_dir in APPS_DIRS:
        if not Path(apps_dir).exists():
            continue
        for py_file in Path(apps_dir).rglob("*.py"):
            if py_file.name in SKIP_FILES or "__pycache__" in str(py_file):
                continue
            file_info = analyze_file(py_file)
            if file_info:
                all_files.append(file_info)

    print(f"  Scanned {len(all_files)} files")
    total_classes = sum(len(f.classes) for f in all_files)
    total_functions = sum(len(f.functions) for f in all_files)
    print(f"  Found {total_classes} classes, {total_functions} functions")

    # Find duplicates
    print("\n[2/4] Finding duplicates...")

    dup_classes = find_duplicate_classes(all_files)
    dup_functions = find_duplicate_functions(all_files)
    dup_files = find_exact_duplicate_files(all_files)

    print(f"  Duplicate class names: {len(dup_classes)}")
    print(f"  Duplicate function names: {len(dup_functions)}")
    print(f"  Exact duplicate files: {len(dup_files)}")

    # Analyze duplicates
    print("\n[3/4] Analyzing duplicates...")

    files_to_delete = set()
    classes_to_remove = []  # (file, class_name)

    # Handle duplicate classes
    print("\n" + "=" * 80)
    print("DUPLICATE CLASSES")
    print("=" * 80)

    for class_name, duplicates in sorted(dup_classes.items(), key=lambda x: -len(x[1])):
        # Check if exact duplicates (same content hash)
        hash_groups = defaultdict(list)
        for cls in duplicates:
            hash_groups[cls.content_hash].append(cls)

        print(f"\n  {class_name} ({len(duplicates)} copies)")

        for content_hash, group in hash_groups.items():
            if len(group) > 1:
                # Exact duplicates - keep one, delete others
                best, others = select_best_version(group)
                print(f"    [EXACT] Keep: {Path(best.file_path).name}")
                for other in others:
                    print(f"    [DELETE] {Path(other.file_path).name}")
                    # If file only has this one class, delete the file
                    file_info = next((f for f in all_files if f.path == other.file_path), None)
                    if file_info and len(file_info.classes) == 1 and len(file_info.functions) == 0:
                        files_to_delete.add(other.file_path)
                    else:
                        classes_to_remove.append((other.file_path, class_name))
            else:
                # Different implementations - keep best
                cls = group[0]
                print(f"    [UNIQUE] {Path(cls.file_path).name} (hash: {content_hash})")

    # Handle exact duplicate files
    print("\n" + "=" * 80)
    print("EXACT DUPLICATE FILES")
    print("=" * 80)

    for content_hash, files in dup_files.items():
        print(f"\n  Hash: {content_hash}")
        # Keep the one with best quality score
        files_sorted = sorted(files, key=lambda x: -x.quality_score)
        best = files_sorted[0]
        print(f"    [KEEP] {best.path} (score: {best.quality_score:.1f})")
        for other in files_sorted[1:]:
            print(f"    [DELETE] {other.path} (score: {other.quality_score:.1f})")
            files_to_delete.add(other.path)

    # Summary
    print("\n" + "=" * 80)
    print("DEDUPLICATION SUMMARY")
    print("=" * 80)
    print(f"\n  Files to delete: {len(files_to_delete)}")
    print(f"  Classes to remove from files: {len(classes_to_remove)}")

    # Execute deletion
    print("\n[4/4] Executing deduplication...")

    deleted_count = 0
    for file_path in files_to_delete:
        try:
            Path(file_path).unlink()
            print(f"  ✓ Deleted: {Path(file_path).name}")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ Failed to delete {file_path}: {e}")

    print(f"\n  Total deleted: {deleted_count} files")

    # Note: Not removing individual classes from files as that requires more complex AST manipulation
    if classes_to_remove:
        print(f"\n  NOTE: {len(classes_to_remove)} duplicate classes in multi-class files")
        print("  These require manual review or more complex AST manipulation to remove.")


if __name__ == "__main__":
    main()
