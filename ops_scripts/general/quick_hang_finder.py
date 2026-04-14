#!/usr/bin/env python3
"""
Quick hang finder - isolates imports in subprocesses so hanging modules cannot poison the parent process.
"""

import ast
import os
import subprocess
import sys
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

DEFAULT_TIMEOUT = 3.0


def _resolve_project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _resolve_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))


def find_suspicious_patterns(file_path: Path) -> list[str]:
    """Find top-level execution patterns that could cause hangs."""
    suspicious = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        for node in tqdm(ast.iter_child_nodes(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                call = node.value
                func_name = ""
                if isinstance(call.func, ast.Name):
                    func_name = call.func.id
                elif isinstance(call.func, ast.Attribute):
                    func_name = call.func.attr

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
    ) as e:
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


def _probe_import(module_name: str, timeout: float) -> tuple[str, str | None, float]:
    start = time.time()
    probe = f"import sys;sys.path.insert(0, {str(PROJECT_ROOT)!r});__import__({module_name!r})"
    try:
        subprocess.run(
            [sys.executable, "-c", probe],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return ("ok", None, time.time() - start)
    except subprocess.TimeoutExpired:
        return ("hang", None, time.time() - start)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip().replace("\n", " ")
        return ("error", detail[:200] or "subprocess import failed", time.time() - start)


def main() -> int:
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
    print("Now testing actual imports in isolated subprocesses...")
    print("=" * 70 + "\n")

    hangs = []
    errors = []
    slow = []

    for i, file_path in tqdm(enumerate(files), desc="Processing", unit="item"):
        rel = file_path.relative_to(PROJECT_ROOT)
        module_name = str(rel.with_suffix("")).replace(os.sep, ".")

        if i % 50 == 0:
            print(f"[{i}/{len(files)}] Testing {module_name[:50]}...")

        status, detail, duration = _probe_import(module_name, DEFAULT_TIMEOUT)

        if status == "hang":
            hangs.append((rel, module_name))
            print(f"\n[HANG] {rel} (>{duration:.1f}s)")
        elif status == "error":
            errors.append((rel, detail or "unknown error"))
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
