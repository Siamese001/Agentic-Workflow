#!/usr/bin/env python3
"""
Fix all canon violations to achieve 50/50 pass rate.
This script renames directories and files to comply with the canon.
"""

import os
import scripts.validation.check_canonical_structure
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SOVEREIGN_DIRS = {
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "schemas",
    "prompt_governance",
    "observability",
    "config",
}

def sovereign_roots():
    return [ROOT / d for d in SOVEREIGN_DIRS if (ROOT / d).is_dir()]

def fix_smashed_directories():
    """
    Rename directories with >=3 underscores to use nested subfolders.
    Example: check_rules_policy_check_safety -> check_rules/policy_check_safety
    """

    smashed = []
    for root in sovereign_roots():
        for d in root.rglob("*"):
            if not d.is_dir():
                continue
            if d.name in {"__pycache__", ".git", "node_modules"}:
                continue
            if d.name.count("_") >= 3:
                smashed.append(d)

    # Sort by depth (deepest first to avoid parent conflicts)
    smashed.sort(key=lambda p: len(p.parts), reverse=True)

    for d in smashed:
        name = d.name
        parts = name.split("_")

        # Split into 2 parts: first 2 words + rest
        if len(parts) >= 4:
            new_parent_name = "_".join(parts[:2])
            new_child_name = "_".join(parts[2:])
        else:
            # 3 underscores = 4 parts, split 2+2
            new_parent_name = "_".join(parts[:2])
            new_child_name = "_".join(parts[2:])

        new_parent = d.parent / new_parent_name
        new_path = new_parent / new_child_name

        # Skip if already exists or would create conflict
        if new_path.exists():

            continue

        try:
            # Create parent if needed
            new_parent.mkdir(parents=True, exist_ok=True)

            # Move the directory
            shutil.move(str(d), str(new_path))

        except Exception as e:

def fix_repeated_concept_filenames():
    """
    Rename files with repeated concepts like state_update_update_safety_usage.py
    """

    pattern = re.compile(
        r"(update.*update|check.*check|state.*state|cost.*cost|policy.*policy|rule.*rule|safety.*safety)",
            
        re.IGNORECASE,
    )

    for f in ROOT.rglob("*.py"):
        if f.name == "__init__.py":
            continue
        if ".git" in f.parts or "__pycache__" in f.parts:
            continue

        stem = f.stem
        match = pattern.search(stem)
        if match:
            # Remove the duplicate word
            matched = match.group(1)
            words = matched.split("_")

            # Find and remove duplicate
            new_stem = stem
            for word in ["update", "check", "state", "cost", "policy", "rule", "safety"]:
                # Replace word_word with just word
                new_stem = re.sub(rf"({word})_\1", r"\1", new_stem, flags=re.IGNORECASE)
                # Replace word_X_word with word_X
                new_stem = re.sub(rf"({word})_(\w+)_\1", r"\1_\2", new_stem, flags=re.IGNORECASE)

            if new_stem != stem:
                new_path = f.parent / f"{new_stem}.py"
                if not new_path.exists():
                    try:
                        f.rename(new_path)

                    except Exception as e:

                else:

def create_init_files():
    """Ensure all directories with .py files have __init__.py"""

    for root in sovereign_roots():
        for d in root.rglob("*"):
            if not d.is_dir():
                continue
            if d.name == "__pycache__":
                continue

            has_py = any(child.suffix == ".py" for child in d.iterdir() if child.is_file())
            init_file = d / "__init__.py"

            if has_py and not init_file.exists():
                init_file.write_text('"""Package initialization."""\n')

if __name__ == "__main__":

    fix_smashed_directories()
    fix_repeated_concept_filenames()
    create_init_files()
