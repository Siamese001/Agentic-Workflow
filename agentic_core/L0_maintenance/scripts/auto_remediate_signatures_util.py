"""
Auto-Remediation Script: Signal Propagation Hardening.

TARGET: 102 Leaf Agents missing **kwargs in heal_repository.
METHOD: AST parsing with source reconstruction.
SAFETY: Verifies syntax before writing.
"""

import ast
import os
import re
from pathlib import Path

# SSOT Target Directory
TARGET_DIR = Path("agentic_core")


def has_kwargs_in_signature(func_node: ast.FunctionDef) -> bool:
    """Check if function definition already has **kwargs."""
    return func_node.args.kwarg is not None


def find_heal_repository_methods(tree: ast.AST) -> list[ast.FunctionDef]:
    """Find all heal_repository method definitions in AST."""
    methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "heal_repository":
            methods.append(node)
    return methods


def inject_kwargs_in_signature(content: str, func_node: ast.FunctionDef) -> tuple[str, bool]:
    """
    Inject **kwargs into function signature using line-based approach.
    Returns (modified_content, was_modified).
    """
    lines = content.splitlines(keepends=True)

    # Find the function definition span
    start_line = func_node.lineno - 1  # 0-indexed
    end_line = func_node.lineno - 1

    # Find the closing paren of the signature (may span multiple lines)
    signature_text = ""
    for i in range(start_line, min(start_line + 20, len(lines))):  # Max 20 lines for signature
        signature_text += lines[i]
        if "):" in lines[i] or ") ->" in lines[i]:
            end_line = i
            break

    # Check if already has **kwargs
    if "**kwargs" in signature_text:
        return content, False

    # Inject **kwargs before closing paren
    modified_signature = signature_text
    if "):" in signature_text:
        modified_signature = signature_text.replace("):", ", **kwargs):")
    elif ") ->" in signature_text:
        modified_signature = signature_text.replace(") ->", ", **kwargs) ->")
    else:
        return content, False  # Can't find closing paren

    # Reconstruct content
    new_lines = lines[:start_line] + [modified_signature] + lines[end_line + 1 :]
    return "".join(new_lines), True


def inject_kwargs_in_super_calls(content: str) -> tuple[str, bool]:
    """
    Inject **kwargs into super().heal_repository() calls.
    Returns (modified_content, was_modified).
    """
    # Pattern: super().heal_repository(...) where ... doesn't contain **kwargs
    pattern = r"super\(\)\.heal_repository\(([^)]*)\)"

    def replacer(match):
        args = match.group(1).strip()
        if "**kwargs" in args:
            return match.group(0)  # Already has kwargs
        if args:
            return f"super().heal_repository({args}, **kwargs)"
        else:
            return "super().heal_repository(**kwargs)"

    new_content = re.sub(pattern, replacer, content)
    return new_content, (new_content != content)


def remediate_file(file_path: Path) -> bool:
    """
    Scans a file for heal_repository definition.
    If missing **kwargs, injects it into the signature and super() call.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False

    if "def heal_repository" not in content:
        return False

    # Safety Check: Parse original
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False  # Skip files with existing syntax errors

    # Find heal_repository methods
    heal_methods = find_heal_repository_methods(tree)
    if not heal_methods:
        return False

    modified = False
    new_content = content

    # Process each heal_repository method
    for func_node in heal_methods:
        if not has_kwargs_in_signature(func_node):
            new_content, sig_modified = inject_kwargs_in_signature(new_content, func_node)
            modified = modified or sig_modified

    # Inject kwargs in super() calls
    new_content, super_modified = inject_kwargs_in_super_calls(new_content)
    modified = modified or super_modified

    if not modified:
        return False

    # Final Syntax Verification
    try:
        ast.parse(new_content)
    except SyntaxError:
        return False  # Safety abort - don't write invalid syntax

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    try:
        rel_path = file_path.resolve().relative_to(Path.cwd().resolve())
        print(f"✅ Fixed: {rel_path}")
    except ValueError:
        print(f"✅ Fixed: {file_path}")
    return True


def main():
    print(f"🔍 Scanning {TARGET_DIR} for Signal Blocks...")
    count = 0
    scanned = 0

    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                scanned += 1
                if remediate_file(path):
                    count += 1

    print("-" * 40)
    print(f"Files Scanned: {scanned}")
    print(f"Agents Patched: {count}")
    print("-" * 40)


if __name__ == "__main__":
    main()
