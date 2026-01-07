#!/usr/bin/env python3
"""
Audit Remaining Architectural Violations
Identifies all intra_core violations requiring manual file relocation
"""
import asyncio
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L5_safety.validators.GravityValidatorAgent import GravityValidatorAgent

async def main():
    project_root = Path(__file__).parent
    validator = GravityValidatorAgent(project_root)
    
    print("=" * 80)
    print("ARCHITECTURAL VIOLATIONS AUDIT")
    print("=" * 80)
    print("\nScanning for intra_core violations (L1→L2/L3/L4/L5)...")
    print("These require manual file relocation to resolve.\n")
    
    # Scan L1_cognition directory
    target_dir = project_root / "agentic_core" / "L1_cognition"
    
    architectural_violations = []
    files_scanned = 0
    
    for py_file in target_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        
        files_scanned += 1
        violations = await validator.detect_violations(py_file)
        
        # Filter for intra_core violations only
        intra_core = [v for v in violations if v.violation_type == "intra_core"]
        
        if intra_core:
            architectural_violations.extend(intra_core)
    
    print(f"Files scanned: {files_scanned}")
    print(f"Architectural violations found: {len(architectural_violations)}\n")
    
    if not architectural_violations:
        print("✅ No architectural violations found!")
        return
    
    # Group by file
    by_file = defaultdict(list)
    for v in architectural_violations:
        by_file[v.file_path].append(v)
    
    print("=" * 80)
    print("VIOLATIONS BY FILE")
    print("=" * 80)
    
    for file_path, violations in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True):
        rel_path = file_path.relative_to(project_root)
        print(f"\n📄 {rel_path}")
        print(f"   Violations: {len(violations)}")
        
        for v in violations:
            print(f"\n   Line {v.line_number}: {v.source_layer} → {v.target_layer}")
            print(f"   Import: {v.import_line}")
            print(f"   Severity: {v.severity}/10")
    
    # Group by target layer
    print("\n" + "=" * 80)
    print("VIOLATIONS BY TARGET LAYER")
    print("=" * 80)
    
    by_target = defaultdict(list)
    for v in architectural_violations:
        by_target[v.target_layer].append(v)
    
    for target_layer, violations in sorted(by_target.items()):
        print(f"\n{target_layer}: {len(violations)} violation(s)")
        files = set(v.file_path.name for v in violations)
        for file_name in sorted(files):
            print(f"  - {file_name}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    print("\nFor each file with violations, you have two options:")
    print("\n1. RELOCATE FILE: Move the file to the target layer")
    print("   Example: Move L1 file to L2_execution if it imports from L2")
    print("\n2. REFACTOR IMPORTS: Remove the dependency on lower-authority layers")
    print("   Example: Extract shared code to L0_maintenance or L1_cognition")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
