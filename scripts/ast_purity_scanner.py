# ast_purity_scanner.py
# Enforces L1–L5 purity principles via AST.

import os
import ast
import sys

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"

FORBIDDEN_IMPORTS = {
    "agentic_core/l1_planning": ["agentic_core.l2_execution", "agentic_core.l3_orchestration",
                                 "agentic_core.l4_memory", "agentic_core.l5_safety"],
    "agentic_core/l2_execution": ["agentic_core.l1_planning", "agentic_core.l3_orchestration",
                                  "agentic_core.l4_memory", "agentic_core.l5_safety"],
    "agentic_core/l3_orchestration": ["agentic_core.l4_memory", "agentic_core.l5_safety"],
    "agentic_core/l4_memory": ["agentic_core.l1_planning", "agentic_core.l2_execution",
                               "agentic_core.l3_orchestration"],
    "agentic_core/l5_safety": ["agentic_core.l1_planning", "agentic_core.l2_execution",
                               "agentic_core.l3_orchestration", "agentic_core.l4_memory"],
}

NO_INLINE_PROMPTS_IN = {
    "agentic_core/l1_planning": True,
    "agentic_core/l5_safety": True,
}

def is_inline_prompt(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return len(node.value.split()) > 10
    return False

def walk_python_files(root):
    py_files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                py_files.append(os.path.join(dirpath, f))
    return py_files

def check_forbidden_imports(filepath, tree, errors):
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\", "/")
    for prefix, forbidden_list in FORBIDDEN_IMPORTS.items():
        if rel.startswith(prefix):
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(alias.name.startswith(bad) for bad in forbidden_list):
                            errors.append(f"Forbidden import in {rel}: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    fullname = f"{node.module}"
                    if any(fullname.startswith(bad) for bad in forbidden_list):
                        errors.append(f"Forbidden import-from in {rel}: {fullname}")

def check_inline_prompts(filepath, tree, errors):
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\", "/")
    for prefix in NO_INLINE_PROMPTS_IN:
        if rel.startswith(prefix):
            for node in ast.walk(tree):
                if is_inline_prompt(node):
                    errors.append(f"Inline prompt violation in {rel}")

def main():
    errors = []
    files = walk_python_files(REPO_ROOT)

    for f in files:
        with open(f, "r", encoding="utf-8") as src:
            try:
                tree = ast.parse(src.read(), filename=f)
            except SyntaxError as e:
                errors.append(f"Syntax error in {f}: {e}")
                continue

        check_forbidden_imports(f, tree, errors)
        check_inline_prompts(f, tree, errors)

    if errors:
        print("\n=== AST PURITY SCAN FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("AST purity validation PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
