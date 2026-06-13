"""Agentic Core Leakage Detection Gate — T7-CORE-BOUNDARY

Detects apps_* specific code leakage into agentic_core at every major checkpoint.
Runs as pre-commit gate and CI check.

Hard constraints enforced:
- No apps_* literals in agentic_core files
- No imports from apps_* in agentic_core
- No app-specific conditionals (if app_id == "apps_...")
- No modification of canonical G01-G29 gates
- No modification of canonical X1/X2/X3 schemas

Exit codes:
  0 = No leakage detected
  1 = Leakage detected (fail-closed)
  2 = Tool error

Environment variables:
  CORE_LEAKAGE_GATE_FAIL_CLOSED=1 — fail CI if leakage detected (default: advisory)
  CORE_LEAKAGE_GATE_BYPASS=1 — bypass all checks (logged as WARNING)
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# SSOT paths
REPO_ROOT = Path(__file__).parent.parent.parent
AGENTIC_CORE_DIR = REPO_ROOT / "agentic_core"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci"

# Forbidden patterns indicating leakage
FORBIDDEN_PATTERNS = [
    # App-specific literals
    (r'"apps_rg"', "Literal apps_rg string"),
    (r"'apps_rg'", "Literal apps_rg string (single quote)"),
    (r'"apps_lic"', "Literal apps_lic string"),
    (r'"apps_qna"', "Literal apps_qna string"),
    (r'"apps_research"', "Literal apps_research string"),
    (r'"apps_exec"', "Literal apps_exec string"),
    (r'"apps_underwriting_ai"', "Literal apps_underwriting_ai string"),
    (r'"apps_architect"', "Literal apps_architect string"),
    (r'"apps_eval"', "Literal apps_eval string"),
    
    # App-specific conditionals (anti-pattern)
    (r'if\s+app_id\s*==\s*["\']apps_', "App-specific conditional check"),
    (r'if\s+tenant_id\s*==\s*["\']apps_', "Tenant-specific conditional check"),
    
    # Imports from apps_* (forbidden in core)
    (r'from\s+apps_\w+\s+import', "Import from apps_* package"),
    (r'import\s+apps_\w+', "Import apps_* package"),
    
    # App-specific hardcoding
    (r'["\']apps_\w+_route\s*[=:]', "App-specific route variable"),
    (r'["\']APPS_\w+\s*[=:]', "App-specific constant"),
    (r'["\']apps_\w+_CACHE_BYPASS', "App-specific cache bypass"),
    
    # Direct path references to apps_* (suspicious)
    (r'apps_rg/\w+\.py', "Hardcoded apps_rg file path"),
    (r'apps_lic/\w+\.py', "Hardcoded apps_lic file path"),
]

# Canonical gates that must not be modified
CANONICAL_GATES = [
    "G01", "G02", "G03", "G04", "G05",
    "G06", "G07", "G08", "G09", "G10",
    "G11", "G12", "G13", "G14", "G15",
    "G16", "G17", "G18", "G19", "G20",
    "G21", "G22", "G23", "G24", "G25",
    "G26", "G27", "G28", "G29",
]

# Canonical schema files
CANONICAL_SCHEMA_FILES = [
    "exit_eval/v6/x1_gates.py",
    "exit_eval/v6/x2_aggregator.py", 
    "exit_eval/v6/x3_disposition.py",
    "exit_eval/v6/schemas.py",
]


def scan_file_for_leakage(file_path: Path) -> list[dict[str, Any]]:
    """Scan a single file for leakage patterns."""
    violations = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception as e:
        return [{"error": f"Failed to read {file_path}: {e}"}]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Check for guardian exemptions
                if "# guardian: allow-" in line or "# GUARDIAN: ALLOW-" in line:
                    continue
                
                violations.append({
                    "file": str(file_path.relative_to(REPO_ROOT)),
                    "line": line_num,
                    "pattern": pattern,
                    "description": description,
                    "snippet": line.strip()[:100],
                })
    
    return violations


def check_canonical_gate_modifications() -> list[dict[str, Any]]:
    """Check for modifications to canonical G01-G29 gate definitions."""
    violations = []
    
    # Look for gate definition files in agentic_core
    gate_dirs = [
        AGENTIC_CORE_DIR / "L3_orchestration" / "exit_eval",
        AGENTIC_CORE_DIR / "L4_state" / "gates",
    ]
    
    for gate_dir in gate_dirs:
        if not gate_dir.exists():
            continue
            
        for gate_file in gate_dir.rglob("*.py"):
            try:
                content = gate_file.read_text(encoding="utf-8")
                
                # Check for app-specific gate overrides
                for gate in CANONICAL_GATES:
                    # Look for app-specific overrides of canonical gates
                    pattern = rf'{gate}\s*=.*?apps_\w+'
                    if re.search(pattern, content, re.IGNORECASE):
                        violations.append({
                            "file": str(gate_file.relative_to(REPO_ROOT)),
                            "description": f"App-specific override of {gate}",
                            "snippet": f"{gate} assigned with apps_* reference",
                        })
                        
            except Exception:
                continue
    
    return violations


def check_canonical_schema_modifications() -> list[dict[str, Any]]:
    """Check for modifications to canonical X1/X2/X3 schemas."""
    violations = []
    
    for schema_rel_path in CANONICAL_SCHEMA_FILES:
        schema_path = AGENTIC_CORE_DIR / "L3_orchestration" / schema_rel_path
        if not schema_path.exists():
            continue
            
        try:
            content = schema_path.read_text(encoding="utf-8")
            
            # Check for apps_* references in schema files
            for pattern, description in FORBIDDEN_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append({
                        "file": str(schema_path.relative_to(REPO_ROOT)),
                        "description": f"Canonical schema file has {description}",
                    })
                    break  # One violation per file is enough
                    
        except Exception:
            continue
    
    return violations


def run_leakage_scan() -> dict[str, Any]:
    """Run full leakage scan on agentic_core."""
    all_violations = []
    
    if not AGENTIC_CORE_DIR.exists():
        return {
            "status": "error",
            "error": f"agentic_core directory not found: {AGENTIC_CORE_DIR}",
            "violations": [],
        }
    
    # Scan all Python files in agentic_core
    for py_file in AGENTIC_CORE_DIR.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue
            
        violations = scan_file_for_leakage(py_file)
        all_violations.extend(violations)
    
    # Check canonical gate modifications
    gate_violations = check_canonical_gate_modifications()
    all_violations.extend(gate_violations)
    
    # Check canonical schema modifications
    schema_violations = check_canonical_schema_modifications()
    all_violations.extend(schema_violations)
    
    return {
        "status": "ok",
        "violations": all_violations,
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(list(AGENTIC_CORE_DIR.rglob("*.py"))),
    }


def write_artifact(result: dict[str, Any]) -> None:
    """Write scan result to artifacts directory."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    artifact_path = ARTIFACTS_DIR / "core_leakage_gate.json"
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"[ARTIFACT] Scan result written to: {artifact_path}")


def main() -> int:
    """Main entry point."""
    # Check bypass
    if os.environ.get("CORE_LEAKAGE_GATE_BYPASS") == "1":
        print("[BYPASS] CORE_LEAKAGE_GATE_BYPASS=1 — skipping all checks")
        result = {
            "status": "bypassed",
            "violations": [],
            "bypass_reason": "CORE_LEAKAGE_GATE_BYPASS=1",
        }
        write_artifact(result)
        return 0
    
    print("=" * 70)
    print("AGENTIC CORE LEAKAGE DETECTION GATE — T7-CORE-BOUNDARY")
    print("=" * 70)
    print()
    
    # Run scan
    result = run_leakage_scan()
    
    if result["status"] == "error":
        print(f"[ERROR] {result.get('error', 'Unknown error')}")
        write_artifact(result)
        return 2
    
    violations = result.get("violations", [])
    
    # Report results
    print(f"[INFO] Scanned {result['files_scanned']} files in agentic_core/")
    print(f"[INFO] Found {len(violations)} violation(s)")
    print()
    
    if violations:
        print("-" * 70)
        print("VIOLATIONS DETECTED:")
        print("-" * 70)
        
        for i, v in enumerate(violations, 1):
            print(f"\n{i}. {v.get('description', 'Unknown')}")
            print(f"   File: {v.get('file', 'Unknown')}")
            if 'line' in v:
                print(f"   Line: {v['line']}")
            if 'snippet' in v:
                print(f"   Code: {v['snippet']}")
        
        print()
        print("-" * 70)
        print("INTERPRETATION:")
        print("-" * 70)
        print("""
These violations indicate apps_* specific code has leaked into agentic_core.

agentic_core MUST remain app-agnostic. App-specific logic belongs in apps_*/.

To fix:
1. Move app-specific code to the appropriate apps_*/ module
2. Use generic contracts/profiles for cross-app behavior
3. If this is a false positive, add guardian comment:
   # guardian: allow-<type> -- <specific justification>

Hard rules:
- No if app_id == "apps_..." in agentic_core
- No imports from apps_* in agentic_core  
- No hardcoded app literals in agentic_core
- No modification of canonical G01-G29
- No modification of X1/X2/X3 schemas
""")
    
    # Write artifact
    write_artifact(result)
    
    # Determine exit code
    fail_closed = os.environ.get("CORE_LEAKAGE_GATE_FAIL_CLOSED") == "1"
    
    if violations:
        if fail_closed:
            print("[FAIL] CORE_LEAKAGE_GATE_FAIL_CLOSED=1 — exiting with error")
            return 1
        else:
            print("[WARN] Violations detected but advisory mode (set CORE_LEAKAGE_GATE_FAIL_CLOSED=1 to fail)")
            return 0
    else:
        print("[PASS] No agentic_core leakage detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())
