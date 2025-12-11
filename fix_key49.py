#!/usr/bin/env python3
"""
Fix Key 49 violations - filename word salad
Strategy: Flatten single-file packages and rename overly verbose files
"""

import re
from pathlib import Path
from collections import defaultdict

# Low signal words from canon_validator.py
LOW_SIGNAL_WORDS = {
    "config", "cache", "utils", "test", "spec", "impl",
    "manager", "service", "handler", "controller", "base", "common",
    "data", "info", "get", "set", "load", "save", "read", "write",
    "process", "execute", "run", "init",
    "create", "delete", "find", "fetch", "store",
    "input", "output", "result", "context", "status",
    "check", "update", "manage", "perform", "task",
}

def count_high_signal_words(filename):
    """Count high-signal words in a filename"""
    words = filename.lower().split("_")
    high_signal = [w for w in words if w and w not in LOW_SIGNAL_WORDS]
    return len(high_signal), high_signal

def analyze_violations():
    """Analyze all Key 49 violations"""
    violations = []
    root = Path(".")
    
    for f in root.rglob("*.py"):
        if f.name == "__init__.py":
            continue
        if any(ex in f.parts for ex in {".git", "__pycache__", "data", "archives", "node_modules"}):
            continue
            
        # Check length violation
        length_violation = len(f.name) > 60
        
        # Check word count violation
        signal_count, high_signal = count_high_signal_words(f.stem)
        word_violation = signal_count > 4
        
        if length_violation or word_violation:
            violations.append({
                "path": f,
                "name": f.name,
                "stem": f.stem,
                "signal_count": signal_count,
                "high_signal": high_signal,
                "length": len(f.name),
                "length_violation": length_violation,
                "word_violation": word_violation
            })
    
    return violations

def generate_rename_mapping(violations):
    """Generate old -> new name mapping"""
    mapping = {}
    
    for v in violations:
        old_path = v["path"]
        old_stem = v["stem"]
        
        # Strategy 1: Remove redundant words
        words = old_stem.lower().split("_")
        
        # Remove redundancies
        cleaned = []
        prev_word = None
        for w in words:
            if w == prev_word:
                continue  # Skip duplicates
            # Remove some verbose combinations
            if w in {"state", "prompt", "governance", "orchestration"} and len(cleaned) > 3:
                continue  # Skip verbose domain words if already long
            cleaned.append(w)
            prev_word = w
        
        # Limit to 4 high-signal words
        high_signal = [w for w in cleaned if w not in LOW_SIGNAL_WORDS]
        low_signal = [w for w in cleaned if w in LOW_SIGNAL_WORDS]
        
        # Keep essential low-signal words (at most 2)
        final = high_signal[:4] + low_signal[:2]
        new_stem = "_".join(final)
        
        # Special case mappings
        special_cases = {
            "rules_manage_costs_state_update_enforce_safety_budget": "enforce_safety_budget",
            "rules_policy_check_safety_apply_prompt_safety_policy": "apply_prompt_safety",
            "content_embedding_compare_meaning_calculate_prompt_similarity": "calculate_similarity",
            "result_refinement_adjust_scores_adjust_prompt_weights": "adjust_prompt_weights",
        }
        
        if old_stem in special_cases:
            new_stem = special_cases[old_stem]
        
        new_name = new_stem + ".py"
        
        if new_name != v["name"]:
            mapping[old_path] = old_path.parent / new_name
    
    return mapping

def find_single_file_packages():
    """Find directories with only __init__.py"""
    single_file_packages = []
    root = Path(".")
    
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        if d.name == "__pycache__":
            continue
            
        children = [c for c in d.iterdir() if c.name != "__pycache__"]
        if len(children) == 1 and children[0].name == "__init__.py":
            single_file_packages.append(d)
    
    return single_file_packages

def generate_flatten_script(packages):
    """Generate script to flatten single-file packages"""
    operations = []
    
    for pkg in packages:
        init_file = pkg / "__init__.py"
        new_file = pkg.parent / f"{pkg.name}.py"
        
        if not new_file.exists():
            operations.append(f'git mv "{init_file}" "{new_file}"')
            operations.append(f'rmdir "{pkg}"')
    
    return operations

def main():
    print("=== Key 49 Violation Analysis ===")
    
    # Analyze violations
    violations = analyze_violations()
    print(f"\nTotal violations: {len(violations)}")
    
    # Categorize by word count
    by_word_count = defaultdict(list)
    for v in violations:
        by_word_count[v["signal_count"]].append(v)
    
    print("\nViolations by high-signal word count:")
    for count in sorted(by_word_count.keys(), reverse=True):
        print(f"  {count} words: {len(by_word_count[count])} files")
    
    # Find single-file packages
    packages = find_single_file_packages()
    print(f"\nSingle-file packages to flatten: {len(packages)}")
    
    # Generate rename mapping
    mapping = generate_rename_mapping(violations)
    print(f"\nFiles to rename: {len(mapping)}")
    
    # Write scripts
    with open("flatten_packages.sh", "w") as f:
        f.write("#!/bin/bash\n# Flatten single-file packages\n")
        f.write("set -e\n\n")
        for op in generate_flatten_script(packages):
            f.write(f"{op}\n")
    
    with open("rename_files.sh", "w") as f:
        f.write("#!/bin/bash\n# Rename verbose files\n")
        f.write("set -e\n\n")
        for old, new in mapping.items():
            f.write(f'git mv "{old}" "{new}"\n')
    
    # Write mapping for review
    with open("rename_mapping.txt", "w") as f:
        f.write("OLD -> NEW\n")
        f.write("=" * 80 + "\n")
        for old, new in mapping.items():
            f.write(f"{old} -> {new}\n")
    
    print("\nGenerated files:")
    print("  - flatten_packages.sh: Flatten single-file packages")
    print("  - rename_files.sh: Rename verbose files")
    print("  - rename_mapping.txt: Review all changes")
    
    # Show worst offenders
    print("\nWorst offenders (7+ words):")
    worst = [v for v in violations if v["signal_count"] >= 7][:10]
    for v in worst:
        print(f"  {v['path']} ({v['signal_count']} words)")

if __name__ == "__main__":
    main()
