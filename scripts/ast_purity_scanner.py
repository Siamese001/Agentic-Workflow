#!/usr/bin/env python3
"""
ast_purity_scanner.py
AST-based purity & safety validator.

Covers:
- L1–L5 forbidden imports
- Inline prompts in forbidden layers (long string literals)
- Dangerous builtins: eval, exec
- subprocess.run without timeout
- Debug prints in core code
- Simple secret-pattern detection in string literals
- Tabs and trailing whitespace in core code
- Missing type hints for functions in core modules
"""

import os
import sys
import ast
import re

REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)

FORBIDDEN_IMPORTS = {
    "agentic_core/l1_planning": [
        "agentic_core.l2_execution",
        "agentic_core.l3_orchestration",
        "agentic_core.l4_memory",
        "agentic_core.l5_safety",
    ],
    "agentic_core/l2_execution": [
        "agentic_core.l1_planning",
        "agentic_core.l3_orchestration",
        "agentic_core.l4_memory",
        "agentic_core.l5_safety",
    ],
    "agentic_core/l3_orchestration": [
        "agentic_core.l4_memory",
        "agentic_core.l5_safety",
    ],
    "agentic_core/l4_memory": [
        "agentic_core.l1_planning",
        "agentic_core.l2_execution",
        "agentic_core.l3_orchestration",
    ],
    "agentic_core/l5_safety": [
        "agentic_core.l1_planning",
        "agentic_core.l2_execution",
        "agentic_core.l3_orchestration",
        "agentic_core.l4_memory",
    ],
}

NO_INLINE_PROMPTS_IN = {
    "agentic_core/l1_planning",
    "agentic_core/l5_safety",
}

SECRET_PATTERNS = [
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
]

CORE_CODE_PREFIXES_FOR_DEBUG = (
    "agentic_core/",
    "apps/",
)

CORE_CODE_PREFIXES_FOR_TYPE_HINTS = (
    "agentic_core/",
    "apps/",
)


def walk_py_files(root):
    out = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                out.append(os.path.join(dirpath, f))
    return out


def relpath(path: str) -> str:
    return os.path.relpath(path, REPO_ROOT).replace("\\", "/")


def is_long_string(node):
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and len(node.value.split()) > 10
    )


def check_forbidden_imports(rel, tree, errors):
    for prefix, forbidden_list in FORBIDDEN_IMPORTS.items():
        if rel.startswith(prefix):
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(alias.name.startswith(bad) for bad in forbidden_list):
                            errors.append(f"[IMPORT] Forbidden import in {rel}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(node.module.startswith(bad) for bad in forbidden_list):
                        errors.append(f"[IMPORT] Forbidden import-from in {rel}: {node.module}")


def check_inline_prompts(rel, tree, errors):
    if any(rel.startswith(p) for p in NO_INLINE_PROMPTS_IN):
        for node in ast.walk(tree):
            if is_long_string(node):
                errors.append(f"[PROMPT] Inline prompt not allowed in {rel}")


def check_dangerous_builtins(rel, tree, errors):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                errors.append(f"[DANGER] Use of {node.func.id} in {rel}")


def check_subprocess_without_timeout(rel, tree, errors):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "run":
                if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                    has_timeout = any(
                        isinstance(kw.arg, str) and kw.arg == "timeout"
                        for kw in node.keywords
                    )
                    if not has_timeout:
                        errors.append(f"[RUNTIME] subprocess.run without timeout in {rel}")


def check_debug_prints(rel, tree, errors):
    if not any(rel.startswith(p) for p in CORE_CODE_PREFIXES_FOR_DEBUG):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            errors.append(f"[DEBUG] print() call in core code {rel}")


def check_simple_secrets(rel, tree, errors):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if any(p.search(s) for p in SECRET_PATTERNS):
                errors.append(f"[SECRET] Suspicious secret-like string in {rel}: {s[:80]!r}")


def check_type_hints(rel, tree, errors):
    if not any(rel.startswith(p) for p in CORE_CODE_PREFIXES_FOR_TYPE_HINTS):
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            missing = []
            for arg in node.args.args:
                if arg.arg in ("self", "cls"):
                    continue
                if arg.annotation is None:
                    missing.append(arg.arg)
            if missing:
                errors.append(
                    f"[TYPEHINT] Function {node.name} in {rel} missing arg type hints: {missing}"
                )
            if node.returns is None:
                errors.append(
                    f"[TYPEHINT] Function {node.name} in {rel} missing return type hint"
                )


def check_tabs_and_trailing_ws(rel, source_text, errors):
    if not any(rel.startswith(p) for p in CORE_CODE_PREFIXES_FOR_DEBUG):
        return
    lines = source_text.splitlines()
    for i, line in enumerate(lines, start=1):
        if "\t" in line:
            errors.append(f"[FORMAT] Tab character in {rel}:{i}")
        if line.rstrip() != line:
            errors.append(f"[FORMAT] Trailing whitespace in {rel}:{i}")


def main():
    errors = []
    files = walk_py_files(REPO_ROOT)

    for f in files:
        rel = relpath(f)
        try:
            with open(f, "r", encoding="utf-8") as src:
                source_text = src.read()
        except UnicodeDecodeError as e:
            errors.append(f"[ENCODING] {rel}: {e}")
            continue

        try:
            tree = ast.parse(source_text, filename=rel)
        except SyntaxError as e:
            errors.append(f"[SYNTAX] {rel}: {e}")
            continue

        check_forbidden_imports(rel, tree, errors)
        check_inline_prompts(rel, tree, errors)
        check_dangerous_builtins(rel, tree, errors)
        check_subprocess_without_timeout(rel, tree, errors)
        check_debug_prints(rel, tree, errors)
        check_simple_secrets(rel, tree, errors)
        check_type_hints(rel, tree, errors)
        check_tabs_and_trailing_ws(rel, source_text, errors)

    if errors:
        print("\n=== AST PURITY / SAFETY / HYGIENE SCAN FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("AST purity / safety / hygiene validation PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
