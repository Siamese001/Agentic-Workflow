#!/usr/bin/env python3
"""
Quick hang finder - uses threading with timeout to find hanging imports.
Simpler approach that works better on Windows.
"""

import ast
import os
import sys
import threading
import time
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def find_suspicious_patterns(file_path: Path) -> list[str]:
    """Find top-level execution patterns that could cause hangs."""
    suspicious = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        for node in tqdm(ast.iter_child_nodes(tree), desc="Processing", unit="item"):
            # Top-level assignments with calls
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    call = node.value
                    func_name = ""
                    if isinstance(call.func, ast.Name):
                        func_name = call.func.id
                    elif isinstance(call.func, ast.Attribute):
                        func_name = call.func.attr

                    # Suspicious patterns
                    if func_name in (
                        "Pinecone",
                        "OpenAI",
                        "Client",
                        "connect",
                        "create_client",
                        "setup",
                        "configure",
                        "init",
                    ):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                suspicious.append(
                                    f"Line {node.lineno}: {target.id} = {func_name}(...)",
                                )

            # Top-level function calls (not in if __name__ == "__main__")
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                func_name = ""
                if isinstance(call.func, ast.Name):
                    func_name = call.func.id
                elif isinstance(call.func, ast.Attribute):
                    func_name = call.func.attr

                if func_name in ("setup", "configure", "init", "initialize", "connect"):
                    suspicious.append(f"Line {node.lineno}: {func_name}() called at module level")

    except (
        OSError,
        UnicodeDecodeError,
        SyntaxError,
    ) as e:  # guardian: Parsing and encoding errors need separate handling strategies
        suspicious.append(f"Parse error: {e}")

    return suspicious


def get_python_files() -> list[Path]:
    """Get all Python files in priority directories."""
    files = []
    priority_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
    exclude = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    for dir_name in priority_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            for path in dir_path.rglob("*.py"):
                if not any(ex in path.parts for ex in exclude):
                    files.append(path)

    return sorted(files)


def main():
    print("=" * 70)
    print("QUICK HANG FINDER - Static Analysis")
    print("=" * 70)
    print(f"Project: {PROJECT_ROOT}\n")

    files = get_python_files()
    print(f"Scanning {len(files)} Python files for suspicious patterns...\n")

    findings = []
    for f in files:
        patterns = find_suspicious_patterns(f)
        if patterns:
            findings.append((f, patterns))

    if findings:
        print(f"Found {len(findings)} files with suspicious top-level execution:\n")
        for file_path, patterns in findings:
            rel = file_path.relative_to(PROJECT_ROOT)
            print(f"[FILE] {rel}")
            for p in patterns:
                print(f"   [!] {p}")
            print()
    else:
        print("No suspicious patterns found via static analysis.")

    print("\n" + "=" * 70)
    print("Now testing actual imports (will print dots for progress)...")
    print("=" * 70 + "\n")

    # Test imports one by one with simple timeout
    hangs = []
    errors = []
    slow = []

    for i, file_path in tqdm(enumerate(files), desc="Processing", unit="item"):
        rel = file_path.relative_to(PROJECT_ROOT)
        module_name = str(rel.with_suffix("")).replace(os.sep, ".")

        # Print progress
        if i % 50 == 0:
            print(f"[{i}/{len(files)}] Testing {module_name[:50]}...")

        start = time.time()
        result = {"status": "unknown", "error": None}

        def do_import():
            try:
                __import__(module_name)
                result["status"] = "ok"
            except (ImportError, AttributeError, SyntaxError, ValueError, TypeError) as e:
                result["status"] = "error"
                result["error"] = f"{type(e).__name__}: {str(e)[:100]}"

        thread = threading.Thread(target=do_import)
        thread.daemon = True
        thread.start()
        thread.join(timeout=DEFAULT_TIMEOUT)  # 3 second timeout

        duration = time.time() - start

        if thread.is_alive():
            hangs.append((rel, module_name))
            print(f"\n[HANG] {rel} (>{duration:.1f}s)")
        elif result["status"] == "error":
            errors.append((rel, result["error"]))
        elif duration > 1.0:
            slow.append((rel, duration))
            print(f"\n[SLOW] {rel} ({duration:.1f}s)")

    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if hangs:
        print(f"\n[!] HANGING MODULES ({len(hangs)}):")
        for rel, _mod in hangs:
            print(f"   - {rel}")

    if slow:
        print(f"\n[*] SLOW MODULES ({len(slow)}):")
        for rel, dur in sorted(slow, key=lambda x: -x[1])[:10]:
            print(f"   - {rel} ({dur:.2f}s)")

    if errors:
        print(f"\n[X] IMPORT ERRORS ({len(errors)}):")
        for rel, err in errors[:20]:
            print(f"   - {rel}: {err}")

    print(
        f"\n[OK] Completed: {len(files) - len(hangs)} OK, {len(hangs)} hangs, {len(errors)} errors",
    )


if __name__ == "__main__":
    main()
