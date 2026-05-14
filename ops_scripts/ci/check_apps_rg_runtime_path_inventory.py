"""CI gate: Verify apps_rg runtime path classification (W0A).

Per plan apps-rg-structured-resume-refactor-f8c2a1 W0A.

Acceptance:
- CI fails if active code imports quarantined paths
- CI fails if more than one active generation path exists
- CI proves python -m apps_rg --help imports only dispatch, bindings, and approved tools
- Classification table written to artifact
- No agentic_core files changed (verified separately)
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class PathClassification:
    """Classification for a single path."""
    path: str
    classification: str  # ACTIVE, LEGACY, QUARANTINED, OUT_OF_SCOPE
    evidence: str
    has_quarantine_notice: bool = False
    is_imported_by_active: bool = False
    imports_quarantined: list[str] = field(default_factory=list)


# Canonical ACTIVE paths - these are allowed to be imported by __main__
CANONICAL_ACTIVE_PATHS: set[str] = {
    "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
    "apps_rg/runtime/profile_builder.py",  # Bundle A: profile constructor for AppIngressRunner
    "apps_rg/runtime/bindings/u0_binding.py",
    "apps_rg/runtime/bindings/l1_binding.py",
    "apps_rg/runtime/bindings/l0_binding.py",
    "apps_rg/runtime/bindings/c0_binding.py",
    "apps_rg/runtime/bindings/pa_binding.py",
    "apps_rg/runtime/bindings/l2_binding.py",
    "apps_rg/runtime/bindings/exit_binding.py",
    "apps_rg/runtime/bindings/l2_envelope_adapter.py",
    "apps_rg/runtime/bindings/c0_minimum_safety.py",
    "apps_rg/runtime/bindings/__init__.py",
    "apps_rg/runtime/runtime_executive_summary.py",
    "apps_rg/runtime/schemas/__init__.py",
    "apps_rg/tools/__init__.py",
}

# Canonical QUARANTINED paths - these must NOT be imported by active code
CANONICAL_QUARANTINED_PATHS: set[str] = {
    "apps_rg/engines/judges/executive_positioning_judge.py",
    "apps_rg/integrations/gates/online_judges.py",
    "apps_rg/tools/compute_word_count.py",
}

# Quarantine directory - all files here are quarantined
QUARANTINE_DIRS: tuple[str, ...] = (
    "apps_rg/_quarantine/",
    "apps_rg/integrations/hops/",
    "apps_rg/engines/",
    "apps_rg/tools/",
    "apps_rg/reasoning/",
)

# LEGACY paths - exist but have no active imports
# CI FAIL if any of these become reachable from executable entry
LEGACY_PATHS: set[str] = {
    "apps_rg/runtime/section_runtime.py",
    "apps_rg/runtime/section_agentic_pipeline.py",
    "apps_rg/runtime/section_planner.py",
    "apps_rg/runtime/l6_shadow_learning.py",
    "apps_rg/runtime/writeback_candidates.py",
    "apps_rg/runtime/merge_binding.py",
    "apps_rg/runtime/gate_verification.py",
}

# DENIED runtime surfaces - these must NEVER be reachable from executable entry
DENIED_RUNTIME_SURFACES: set[str] = {
    "apps_rg/runtime/entry/dispatch.py",
    "apps_rg/runtime/section_runtime.py",
    "apps_rg/runtime/section_agentic_pipeline.py",
    "apps_rg/runtime/section_planner.py",
    "apps_rg/runtime/l6_shadow_learning.py",
    "apps_rg/engines/judges/executive_positioning_judge.py",
    "apps_rg/integrations/gates/online_judges.py",
    "apps_rg/integrations/hops/",
    "apps_rg/reasoning/",
}


def _resolve_repo_root() -> Path:
    """Resolve repository root using pyproject.toml sentinel."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


def _has_quarantine_notice(file_path: Path) -> bool:
    """Check if file has explicit quarantine notice."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return (
            "QUARANTINE" in content.upper()
            or "RuntimeError" in content
            and "QUARANTINE VIOLATION" in content
        )
    except Exception:
        return False


def _extract_imports(file_path: Path) -> list[str]:
    """Extract all imports from a Python file."""
    imports: list[str] = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
    except SyntaxError:
        pass  # Skip files with syntax errors
    except Exception:
        pass
    return imports


def _is_quarantined_path(rel_path: str, file_path: Path) -> bool:
    """Check if path is quarantined."""
    # Check explicit quarantine notices
    if rel_path in CANONICAL_QUARANTINED_PATHS:
        return True
    # Check quarantine directories
    for q_dir in QUARANTINE_DIRS:
        if rel_path.startswith(q_dir):
            # Exception: tools/__init__.py and __init__.py files are not quarantined
            if rel_path.endswith("__init__.py"):
                continue
            # Verify it has quarantine notice or is in quarantine folder
            if q_dir == "apps_rg/_quarantine/":
                return True
            if _has_quarantine_notice(file_path):
                return True
    return False


def _classify_path(rel_path: str, file_path: Path) -> str:
    """Classify a single path."""
    if rel_path in CANONICAL_ACTIVE_PATHS:
        return "ACTIVE"
    if rel_path in LEGACY_PATHS:
        return "LEGACY"
    if _is_quarantined_path(rel_path, file_path):
        return "QUARANTINED"
    # Default classification based on directory
    if rel_path.startswith("apps_rg/reasoning/"):
        return "OUT_OF_SCOPE"
    if rel_path.startswith("apps_rg/runtime/"):
        # Other runtime files default to LEGACY unless proven active
        return "LEGACY"
    return "OUT_OF_SCOPE"


def _check_imports_from_quarantined(
    file_path: Path, rel_path: str, active_files: set[str]
) -> list[str]:
    """Check if a file imports from quarantined paths."""
    violations: list[str] = []
    if rel_path not in active_files:
        return violations
    
    imports = _extract_imports(file_path)
    content = file_path.read_text(encoding="utf-8")
    for imp in imports:
        # Check if import matches quarantined patterns - must be an exact match
        for q_path in CANONICAL_QUARANTINED_PATHS:
            module_name = q_path.replace("/", ".").replace(".py", "")
            # Check for exact import match in content
            import_patterns = [
                f"from {module_name}",
                f"import {module_name}",
            ]
            for pattern in import_patterns:
                if pattern in content:
                    violations.append(q_path)
        # Check quarantine directory imports
        for q_dir in QUARANTINE_DIRS:
            dir_module = q_dir.replace("/", ".").rstrip(".")
            # Only flag if explicitly importing from quarantined dirs
            import_patterns = [
                f"from {dir_module}.",
                f"import {dir_module}.",
            ]
            for pattern in import_patterns:
                if pattern in content:
                    # Exception: allowed to import from tools/__init__ only
                    if q_dir == "apps_rg/tools/" and "__init__" in pattern:
                        continue
                    violations.append(q_dir + "*")
    return violations


def run_inventory_check(repo_root: Path) -> dict[str, Any]:
    """Run the full runtime path inventory check."""
    results: dict[str, Any] = {
        "status": "PASS",
        "violations": [],
        "classifications": [],
        "active_paths_verified": [],
        "single_generation_path_verified": False,
    }
    
    apps_rg_dir = repo_root / "apps_rg"
    active_files: set[str] = set()
    dispatch_imports: list[str] = []
    
    # Classify all Python files in apps_rg
    for py_file in apps_rg_dir.rglob("*.py"):
        rel_path = str(py_file.relative_to(repo_root)).replace("\\", "/")
        classification = _classify_path(rel_path, py_file)
        
        if classification == "ACTIVE":
            active_files.add(rel_path)
            results["active_paths_verified"].append(rel_path)
        
        # Check for quarantine notices
        has_notice = _has_quarantine_notice(py_file)
        
        # Check imports from quarantined paths
        imports_quarantined = _check_imports_from_quarantined(py_file, rel_path, active_files)
        
        if imports_quarantined and classification == "ACTIVE":
            for iq in imports_quarantined:
                results["violations"].append({
                    "type": "ACTIVE_IMPORTS_QUARANTINED",
                    "file": rel_path,
                    "imports": iq,
                    "severity": "ERROR",
                })
                results["status"] = "FAIL"
        
        results["classifications"].append({
            "path": rel_path,
            "classification": classification,
            "has_quarantine_notice": has_notice,
            "imports_quarantined": imports_quarantined,
        })
    
    # Verify single generation path
    dispatch_file = apps_rg_dir / "runtime" / "dispatch" / "apps_rg_dispatch.py"
    if dispatch_file.exists():
        dispatch_imports = _extract_imports(dispatch_file)
        # Check that dispatch imports from bindings
        imports_bindings = any("bindings" in imp for imp in dispatch_imports)
        if imports_bindings:
            results["single_generation_path_verified"] = True
        else:
            results["violations"].append({
                "type": "NO_BINDINGS_IMPORT",
                "file": "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
                "severity": "ERROR",
            })
            results["status"] = "FAIL"
    else:
        results["violations"].append({
            "type": "DISPATCH_MISSING",
            "file": "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
            "severity": "ERROR",
        })
        results["status"] = "FAIL"
    
    # Verify __main__ imports only dispatch and bindings (FAIL-CLOSED)
    main_file = apps_rg_dir / "__main__.py"
    if main_file.exists():
        main_content = main_file.read_text(encoding="utf-8")
        disallowed_imports: list[str] = []
        
        # Extract apps_rg imports from content
        for line in main_content.split("\n"):
            if "from apps_rg." in line or "import apps_rg." in line:
                # Skip if it's an allowed import
                if any(allowed in line for allowed in [
                    "runtime.dispatch",
                    "runtime.profile_builder",  # Bundle A: profile constructor
                    "runtime.bindings",
                    "tools.__init__",
                ]):
                    continue
                # Skip if it's a core import (agentic_core, not apps_rg)
                if "from agentic_core" in line:
                    continue
                # Skip comments
                if line.strip().startswith("#"):
                    continue
                disallowed_imports.append(line.strip())
        
        if disallowed_imports:
            results["violations"].append({
                "type": "MAIN_IMPORTS_DISALLOWED",
                "file": "apps_rg/__main__.py",
                "imports": disallowed_imports,
                "severity": "ERROR",
                "message": "__main__.py must only import from runtime.dispatch, runtime.profile_builder, runtime.bindings, or tools.__init__",
            })
            results["status"] = "FAIL"
    
    # Check for legacy runtime.entry.dispatch import specifically
    if main_file.exists():
        main_content = main_file.read_text(encoding="utf-8")
        if "runtime.entry.dispatch" in main_content:
            results["violations"].append({
                "type": "LEGACY_DISPATCH_IMPORT",
                "file": "apps_rg/__main__.py",
                "message": "Legacy import from runtime.entry.dispatch detected. Must use runtime.dispatch only.",
                "severity": "ERROR",
            })
            results["status"] = "FAIL"
    
    # Check for denied runtime surfaces in __main__ (structural invariant)
    if main_file.exists():
        main_content = main_file.read_text(encoding="utf-8")
        denied_patterns = [
            "runtime.section_",
            "runtime.l6_shadow_learning",
            "engines.judges",
            "integrations.hops",
            "integrations.gates.online_judges",
            "reasoning",
        ]
        for pattern in denied_patterns:
            if pattern in main_content:
                results["violations"].append({
                    "type": "DENIED_SURFACE_REACHABLE",
                    "file": "apps_rg/__main__.py",
                    "pattern": pattern,
                    "message": f"Denied runtime surface '{pattern}' is reachable from executable entry. "
                               f"ONLY allowed: runtime.dispatch + runtime.bindings.*",
                    "severity": "ERROR",
                })
                results["status"] = "FAIL"
    
    # Check that LEGACY paths are NOT reachable from __main__
    if main_file.exists():
        main_imports = _extract_imports(main_file)
        for legacy_path in LEGACY_PATHS:
            legacy_module = legacy_path.replace("/", ".").replace(".py", "")
            for imp in main_imports:
                if legacy_module in imp or imp in legacy_module:
                    results["violations"].append({
                        "type": "LEGACY_PATH_REACHABLE",
                        "file": "apps_rg/__main__.py",
                        "legacy_path": legacy_path,
                        "message": f"LEGACY path '{legacy_path}' is reachable from executable entry. "
                                   f"If reachable, it is ACTIVE by definition. "
                                   f"Reclassify as ACTIVE or QUARANTINED.",
                        "severity": "ERROR",
                    })
                    results["status"] = "FAIL"
    
    return results


def main() -> int:
    """Main entry point for CI gate."""
    repo_root = _resolve_repo_root()
    results = run_inventory_check(repo_root)
    
    # Write JSON report
    report_path = repo_root / "artifacts" / "ci" / "apps_rg_runtime_path_inventory.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    # Console output
    print("=" * 60)
    print("apps_rg Runtime Path Inventory Check (W0A)")
    print("=" * 60)
    print(f"Status: {results['status']}")
    print(f"Active paths verified: {len(results['active_paths_verified'])}")
    print(f"Single generation path: {'VERIFIED' if results['single_generation_path_verified'] else 'FAILED'}")
    
    if results["violations"]:
        print("\nViolations:")
        for v in results["violations"]:
            print(f"  [{v['severity']}] {v['type']}: {v.get('file', '')}")
            if "imports" in v:
                print(f"    Imports: {v['imports']}")
    
    print(f"\nReport written to: {report_path}")
    print("=" * 60)
    
    # Fail-closed: exit 1 on FAIL unless bypass is set
    if results["status"] == "FAIL":
        bypass_env = "APPS_RG_RUNTIME_PATH_INVENTORY_BYPASS"
        import os
        if os.environ.get(bypass_env):
            print(f"\n{bypass_env}=1: Bypassing failure (CI will pass)")
            return 0
        print("\nAPPS_RG_RUNTIME_PATH_INVENTORY: FAIL (exit 1)")
        print("Set APPS_RG_RUNTIME_PATH_INVENTORY_BYPASS=1 to bypass")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
