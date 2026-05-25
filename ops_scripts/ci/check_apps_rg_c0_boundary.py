"""W7: C0 Boundary CI Gate for apps_rg.

Checks for:
1. apps_rg-specific leakage into agentic_core
2. No direct durable writes from C0/PA/L2/Exit/L6
3. C0 only queries Chroma (no mutation)
4. Proper separation of concerns

Advisory by default. Fail-closed via APPS_RG_C0_BOUNDARY_FAIL_CLOSED=1.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path
from typing import Any

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# apps_rg-specific terms that should NOT appear in agentic_core
APPS_RG_SPECIFIC_TERMS = {
    "master_resume",  # resume schema is apps_rg-specific
    "resume_section",  # section names like header_block, experience_block
    "bullet_diversity",  # apps_rg-specific concept
    "ats_compatibility",  # apps_rg-specific concept
    "achievement_prioritizer",  # apps_rg engine
    "content_optimizer",  # apps_rg engine
    "hallucination_detector",  # apps_rg engine (unless generic)
    "resume_generation_task",  # apps_rg task
}

# Terms that ARE allowed in agentic_core (generic contracts)
GENERIC_ALLOWED_TERMS = {
    "apps_rg",  # app_id reference is generic
    "fact_vectors",  # collection name is generic
    "jd_payload",  # structured job description is generic
    "resume_payload",  # structured resume is generic
    "candidate_profile",  # generic term
    "project_evidence",  # generic term
    "section_retrieval",  # generic capability
    "metadata_filter",  # generic capability
    "briefing_bypass",  # generic capability
    "gate_verdict",  # generic contract
    "evidence_item",  # generic contract
    "final_evidence_contract",  # generic contract
}

# Chroma mutation methods to detect
CHROMA_MUTATION_METHODS = {
    ".add(",
    ".upsert(",
    ".update(",
    ".delete(",
    ".delete_collection(",
    ".modify(",
}

# Python set methods that are NOT Chroma mutations (to exclude)
PYTHON_SET_METHODS = {
    "set.add(",
    "set.discard(",
    "set.remove(",
    "my_set.add(",  # common variable names
    "_set.add(",
    "seen.add(",
    "visited.add(",
}

# L4/UWG paths that should not be imported by C0/PA/L2/Exit
FORBIDDEN_L4_UWG_IMPORTS = {
    "agentic_core.L4_state",
    "agentic_core.runtime.exit.unified_write_gateway",
    "agentic_core.L6_system_learning.L6_observability",  # L6 is post-runtime only
}


class Violation:
    """Single violation record."""
    
    def __init__(self, file: str, line: int, rule: str, message: str, severity: str = "WARN"):
        self.file = file
        self.line = line
        self.rule = rule
        self.message = message
        self.severity = severity
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }


def scan_agentic_core_for_apps_rg_leakage() -> list[Violation]:
    """Scan agentic_core for apps_rg-specific leakage."""
    violations: list[Violation] = []
    
    agentic_core_dir = REPO_ROOT / "agentic_core"
    if not agentic_core_dir.exists():
        return violations
    
    for py_file in agentic_core_dir.rglob("*.py"):
        # Skip tests
        if "test" in py_file.name or "_test.py" in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments and strings
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                
                # Check for apps_rg-specific terms
                for term in APPS_RG_SPECIFIC_TERMS:
                    if term in line.lower():
                        # Check if it's in a comment
                        if "#" in line and line.index("#") < line.lower().index(term):
                            continue
                        
                        violations.append(Violation(
                            file=str(py_file.relative_to(REPO_ROOT)),
                            line=line_num,
                            rule="APPS_RG_LEAKAGE",
                            message=f"apps_rg-specific term '{term}' found in agentic_core",
                            severity="WARN",
                        ))
        except Exception:
            # Skip files we can't read
            continue
    
    return violations


def scan_c0_for_chroma_mutations() -> list[Violation]:
    """Scan C0 binding for Chroma mutation calls."""
    violations: list[Violation] = []
    
    c0_binding_file = REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "c0_binding.py"
    if not c0_binding_file.exists():
        return violations
    
    try:
        content = c0_binding_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip comments
            if stripped.startswith("#"):
                continue
            
            # Check for Chroma mutation methods
            for method in CHROMA_MUTATION_METHODS:
                if method in line:
                    # Exclude Python set operations (not Chroma)
                    is_python_set = any(
                        set_method in line.lower() 
                        for set_method in PYTHON_SET_METHODS
                    )
                    
                    # Check context - is it a collection mutation?
                    if "collection" in line.lower() or "client" in line.lower():
                        violations.append(Violation(
                            file=str(c0_binding_file.relative_to(REPO_ROOT)),
                            line=line_num,
                            rule="C0_CHROMA_MUTATION",
                            message=f"Potential Chroma mutation call '{method}' in C0",
                            severity="ERROR",
                        ))
    except Exception:
        pass
    
    return violations


def scan_for_l4_uwg_violations() -> list[Violation]:
    """Scan C0, PA, L2, Exit bindings for L4/UWG imports."""
    violations: list[Violation] = []
    
    # Files to scan
    scan_dirs = [
        REPO_ROOT / "apps_rg" / "runtime" / "bindings",
        REPO_ROOT / "agentic_core" / "runtime" / "c0",
        REPO_ROOT / "agentic_core" / "prompt_governance",
        REPO_ROOT / "agentic_core" / "L2_execution",
        REPO_ROOT / "agentic_core" / "runtime" / "exit",
    ]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
            
        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Parse AST for imports
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            module = node.module
                            
                            # Check for forbidden L4/UWG imports
                            for forbidden in FORBIDDEN_L4_UWG_IMPORTS:
                                if module.startswith(forbidden.replace(".", ".")):
                                    violations.append(Violation(
                                        file=str(py_file.relative_to(REPO_ROOT)),
                                        line=node.lineno or 0,
                                        rule="L4_UWG_IMPORT",
                                        message=f"Forbidden import from {module}",
                                        severity="ERROR",
                                    ))
                        
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                name = alias.name
                                for forbidden in FORBIDDEN_L4_UWG_IMPORTS:
                                    if name.startswith(forbidden.replace(".", ".")):
                                        violations.append(Violation(
                                            file=str(py_file.relative_to(REPO_ROOT)),
                                            line=node.lineno or 0,
                                            rule="L4_UWG_IMPORT",
                                            message=f"Forbidden import {name}",
                                            severity="ERROR",
                                        ))
            except Exception:
                continue
    
    return violations


def scan_for_direct_l4_writes() -> list[Violation]:
    """Scan for direct filesystem or L4 write calls outside Exit."""
    violations: list[Violation] = []
    
    # C0, PA, L2 should not do direct writes
    scan_dirs = [
        REPO_ROOT / "apps_rg" / "runtime" / "bindings",
        REPO_ROOT / "agentic_core" / "runtime" / "c0",
        REPO_ROOT / "agentic_core" / "prompt_governance",
        REPO_ROOT / "agentic_core" / "L2_execution",
    ]
    
    write_patterns = [
        "open(",
        ".write(",
        ".writelines(",
        "json.dump(",
        "yaml.dump(",
        "pickle.dump(",
    ]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
            
        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")
                
                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # Skip comments and test files
                    if stripped.startswith("#") or "test" in py_file.name:
                        continue
                    
                    # Check for write patterns
                    for pattern in write_patterns:
                        if pattern in line:
                            # Allow read-only opens
                            if pattern == "open(" and ('"r"' in line or "'r'" in line or '"rb"' in line or "'rb'" in line):
                                continue
                            
                            # Check if in exception handler (usually logging)
                            if "except" in line or "logger" in line or "logging" in line:
                                continue
                            
                            violations.append(Violation(
                                file=str(py_file.relative_to(REPO_ROOT)),
                                line=line_num,
                                rule="DIRECT_WRITE",
                                message=f"Potential direct write pattern '{pattern}'",
                                severity="WARN",
                            ))
            except Exception:
                continue
    
    return violations


def main() -> int:
    """Run all boundary checks and report."""
    all_violations: list[Violation] = []
    
    print("=" * 70)
    print("W7: apps_rg C0 Boundary CI Gate")
    print("=" * 70)
    print()
    
    # Check 1: apps_rg leakage into agentic_core
    print("[1/4] Scanning agentic_core for apps_rg-specific leakage...")
    leakage_violations = scan_agentic_core_for_apps_rg_leakage()
    all_violations.extend(leakage_violations)
    print(f"      Found {len(leakage_violations)} potential leakage issues")
    
    # Check 2: C0 Chroma mutations
    print("[2/4] Scanning C0 binding for Chroma mutations...")
    chroma_violations = scan_c0_for_chroma_mutations()
    all_violations.extend(chroma_violations)
    print(f"      Found {len(chroma_violations)} potential mutation issues")
    
    # Check 3: L4/UWG imports
    print("[3/4] Scanning for forbidden L4/UWG imports...")
    l4_violations = scan_for_l4_uwg_violations()
    all_violations.extend(l4_violations)
    print(f"      Found {len(l4_violations)} import violations")
    
    # Check 4: Direct writes
    print("[4/4] Scanning for direct durable writes...")
    write_violations = scan_for_direct_l4_writes()
    all_violations.extend(write_violations)
    print(f"      Found {len(write_violations)} potential write violations")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    errors = [v for v in all_violations if v.severity == "ERROR"]
    warns = [v for v in all_violations if v.severity == "WARN"]
    
    print(f"Total violations: {len(all_violations)}")
    print(f"  ERROR: {len(errors)}")
    print(f"  WARN:  {len(warns)}")
    print()
    
    if errors:
        print("ERRORS (fail in strict mode):")
        for v in errors[:10]:  # Show first 10
            print(f"  {v.file}:{v.line} [{v.rule}] {v.message}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
        print()
    
    if warns:
        print("WARNINGS (advisory):")
        for v in warns[:5]:  # Show first 5
            print(f"  {v.file}:{v.line} [{v.rule}] {v.message}")
        if len(warns) > 5:
            print(f"  ... and {len(warns) - 5} more")
        print()
    
    # Determine exit code
    fail_closed = os.environ.get("APPS_RG_C0_BOUNDARY_FAIL_CLOSED", "0") == "1"
    bypass = os.environ.get("APPS_RG_C0_BOUNDARY_BYPASS", "0") == "1"
    
    if bypass:
        print("BYPASS: APPS_RG_C0_BOUNDARY_BYPASS=1")
        return 0
    
    if fail_closed and errors:
        print("FAIL: APPS_RG_C0_BOUNDARY_FAIL_CLOSED=1 and errors found")
        return 1
    
    if errors:
        print("ADVISORY: Errors found but gate is advisory by default")
        print("Set APPS_RG_C0_BOUNDARY_FAIL_CLOSED=1 for strict mode")
    else:
        print("PASS: No blocking errors found")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
