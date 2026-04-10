#!/usr/bin/env python3
"""
Scout script to identify hanging imports in the codebase.
Uses multiprocessing with a 2-second timeout per module.
"""

import ast
import multiprocessing
import os
import sys
import time
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def try_import_module(module_path: str) -> tuple[str, str, float]:
    """
    Attempt to import a module and return status.
    Returns: (module_path, status, duration)
    """
    start = time.time()
    try:
        # Convert file path to module path
        rel_path = Path(module_path).relative_to(PROJECT_ROOT)
        module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")

        # Skip test files and __pycache__
        if "__pycache__" in module_name or module_name.startswith("tests."):
            return (module_path, "SKIPPED", 0.0)

        __import__(module_name)
        duration = time.time() - start
        return (module_path, "OK", duration)
    except (ImportError, AttributeError, SyntaxError, ValueError, TypeError) as e:
        duration = time.time() - start
        return (module_path, f"ERROR: {type(e).__name__}: {str(e)[:100]}", duration)


# guardian: allow-magic-config
def import_with_timeout(module_path: str, timeout: float = 2.0) -> tuple[str, str, float]:
    """
    Import a module with a timeout using multiprocessing.
    """
    # Use a simple approach - spawn a process and wait
    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()

    def worker(path, q):
        result = try_import_module(path)
        q.put(result)

    proc = ctx.Process(target=worker, args=(module_path, queue))
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=DEFAULT_TIMEOUT)
        if proc.is_alive():
            proc.kill()
        return (module_path, "HANG (timeout)", timeout)

    try:
        return queue.get_nowait()
    except (queue.Empty, OSError):    # guardian: Add error context logging
        return (module_path, "UNKNOWN", 0.0)


def has_top_level_execution(file_path: Path) -> list[str]:
    """
    Parse a Python file and detect potential top-level execution patterns.
    Returns list of suspicious patterns found.
    """
    suspicious = []
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            # Check for top-level function calls (not in functions/classes)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if hasattr(node.value.func, "id"):
                    func_name = node.value.func.id
                    if func_name not in ("print", "type", "isinstance"):
                        suspicious.append(f"Top-level call: {func_name}()")
                elif hasattr(node.value.func, "attr"):
                    attr = node.value.func.attr
                    if attr in ("setup", "configure", "connect", "init", "initialize"):
                        suspicious.append(f"Top-level call: .{attr}()")

            # Check for top-level assignments that might trigger side effects
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # Check if RHS is a call
                        if isinstance(node.value, ast.Call):
                            if hasattr(node.value.func, "id"):
                                func = node.value.func.id
                                if func in ("Pinecone", "OpenAI", "Client", "connect", "setup"):
                                    suspicious.append(f"Top-level: {name} = {func}()")
                            elif hasattr(node.value.func, "attr"):
                                attr = node.value.func.attr
                                if attr in ("connect", "setup", "configure", "getLogger"):
                                    suspicious.append(f"Top-level: {name} = ...{attr}()")
    except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies
        suspicious.append(f"Parse error: {e}")

    return suspicious


def find_all_python_files(root: Path) -> list[Path]:
    """Find all Python files in the project, excluding tests and cache."""
    files = []
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    for path in root.rglob("*.py"):
        # Skip excluded directories
        if any(excl in path.parts for excl in exclude_dirs):
            continue
        # Skip test files for now
        if TESTS_DIR in path.parts:
            continue
        files.append(path)

    return sorted(files)


def main():
    print("=" * 80)
    print("IMPORT HANG SCOUT - Detecting import-time side effects")
    print("=" * 80)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # Phase 1: Static analysis for suspicious patterns
    print("PHASE 1: Static Analysis (AST scan for top-level execution)")
    print("-" * 60)

    all_files = find_all_python_files(PROJECT_ROOT)
    print(f"Found {len(all_files)} Python files to analyze")
    print()

    suspicious_files = []
    for file_path in all_files:
        patterns = has_top_level_execution(file_path)
        if patterns:
            suspicious_files.append((file_path, patterns))

    if suspicious_files:
        print(f"Found {len(suspicious_files)} files with suspicious top-level patterns:")
        print()
        for file_path, patterns in suspicious_files[:20]:  # Limit output
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"  {rel_path}:")
            for p in patterns[:3]:
                print(f"    - {p}")
        if len(suspicious_files) > 20:
            print(f"  ... and {len(suspicious_files) - 20} more files")
        print()

    # Phase 2: Dynamic import testing with timeout
    print("PHASE 2: Dynamic Import Testing (2s timeout per module)")
    print("-" * 60)

    # Focus on agentic_core and apps_* directories
    priority_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
    priority_files = [f for f in all_files if any(d in f.parts for d in priority_dirs)]

    print(f"Testing {len(priority_files)} priority files...")
    print()

    hangs = []
    slow = []
    errors = []

    for i, file_path in enumerate(priority_files):
        rel_path = file_path.relative_to(PROJECT_ROOT)
        print(
            f"\r[{i + 1}/{len(priority_files)}] Testing: {str(rel_path)[:60]:<60}",
            end="",
            flush=True,
        )
# guardian: allow-magic-config

        result = import_with_timeout(str(file_path), timeout=DEFAULT_TIMEOUT)
        path, status, duration = result

        if "HANG" in status:
            hangs.append((rel_path, status, duration))
            print(f"\n  ⚠️  HANG DETECTED: {rel_path}")
        elif "ERROR" in status:
            errors.append((rel_path, status, duration))
        elif duration > 0.5:
            slow.append((rel_path, status, duration))

    print("\n")

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if hangs:
        print(f"\n🚨 HANGING MODULES ({len(hangs)}):")
        for path, status, duration in hangs:
            print(f"  - {path}")

    if slow:
        print(f"\n⏱️  SLOW MODULES (>0.5s) ({len(slow)}):")
        for path, status, duration in sorted(slow, key=lambda x: -x[2])[:10]:
            print(f"  - {path} ({duration:.2f}s)")

    if errors:
        print(f"\n❌ IMPORT ERRORS ({len(errors)}):")
        for path, status, duration in errors[:20]:
            print(f"  - {path}: {status}")

    print()
    print("=" * 80)
    print("RECOMMENDED ACTIONS:")
    print("=" * 80)
    print("1. Move top-level client instantiations behind `if __name__ == '__main__':`")
    print("2. Convert global connections to lazy properties or factory methods")
    print("3. Defer logging setup to explicit initialization calls")
    print()


if __name__ == "__main__":
    main()
