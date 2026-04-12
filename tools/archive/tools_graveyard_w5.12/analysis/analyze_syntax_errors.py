#!/usr/bin/env python3
"""Analyze syntax errors in the codebase to categorize them for fixing."""

import ast
import json
import os
from pathlib import Path


def analyze_syntax_errors():
    repo_root = Path(__file__).parent
    syntax_errors = []

    # Collect detailed syntax error information
    scan_roots = [
        "agentic_core",
        "apps_eval",
        "apps_exec",
        "apps_lic",
        "apps_research",
        "apps_rfp",
        "apps_rg",
        "apps_shared",
        "system_learning",
        "tools",
        "tests",
        "ops_scripts",
    ]

    for root in scan_roots:
        root_path = repo_root / root
        if not root_path.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [
                d
                for d in dirnames
                if d
                not in [
                    "__pycache__",
                    ".git",
                    "node_modules",
                    "venv",
                    ".venv",
                    "env",
                    "archives",
                    ".mypy_cache",
                    ".pytest_cache",
                    ".tox",
                    "htmlcov",
                ]
            ]
            for fname in filenames:
                if fname.endswith(".py") and not fname.endswith(".pyc"):
                    fp = Path(dirpath) / fname
                    rel_path = str(fp.relative_to(repo_root))
                    try:
                        with open(fp, encoding="utf-8") as f:
                            content = f.read()
                        ast.parse(content, filename=str(fp))
                    except SyntaxError as e:
                        syntax_errors.append(
                            {
                                "file": rel_path,
                                "line": e.lineno,
                                "message": str(e),
                                "text": e.text,
                                "category": rel_path.split("/")[0] if "/" in rel_path else "root",
                                "size": fp.stat().st_size,
                            }
                        )
                    except Exception as e:
                        syntax_errors.append(
                            {
                                "file": rel_path,
                                "line": 0,
                                "message": f"Non-syntax error: {str(e)}",
                                "text": "",
                                "category": rel_path.split("/")[0] if "/" in rel_path else "root",
                                "size": fp.stat().st_size,
                            }
                        )

    # Categorize by directory
    categories = {}
    for err in syntax_errors:
        cat = err["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(err)

    print("=== SYNTAX ERROR CATEGORIZATION ===")
    print(f"Total syntax errors: {len(syntax_errors)}")
    print()
    for cat, errs in sorted(categories.items()):
        print(f"{cat}: {len(errs)} files")
        # Show first error as example
        if errs:
            example = errs[0]
            msg = example["message"][:80] + "..." if len(example["message"]) > 80 else example["message"]
            print(f"  Example: {example['file']}:{example['line']} - {msg}")
        print()

    # Save detailed report
    with open("syntax_error_report.json", "w") as f:
        json.dump(
            {
                "total": len(syntax_errors),
                "categories": {k: len(v) for k, v in categories.items()},
                "details": syntax_errors,
            },
            f,
            indent=2,
        )

    print("Detailed report saved to: syntax_error_report.json")
    return syntax_errors, categories


if __name__ == "__main__":
    analyze_syntax_errors()
