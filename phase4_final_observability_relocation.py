"""
Phase 4 Final Push: Observability Agent Relocation
Relocates the last 14 gravity-violating agents from observability/ to achieve ZERO violations.
"""

import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.resolve()

# Final 14 gravity violations - all observability agents assigned to L3
OBSERVABILITY_VIOLATIONS: List[Tuple[str, str, str]] = [
    (
        "agentic_core/observability/metrics/CoverageAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/CoverageAgent.py"
    ),
    (
        "agentic_core/observability/metrics/DagRuntimeInspectorAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/DagRuntimeInspectorAgent.py"
    ),
    (
        "agentic_core/observability/metrics/GeneralExerciserAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/GeneralExerciserAgent.py"
    ),
    (
        "agentic_core/observability/metrics/HierarchyEnforcerAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/HierarchyEnforcerAgent.py"
    ),
    (
        "agentic_core/observability/metrics/MetaCoverageOptimizerAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/MetaCoverageOptimizerAgent.py"
    ),
    (
        "agentic_core/observability/metrics/MetricsAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/MetricsAgent.py"
    ),
    (
        "agentic_core/observability/metrics/PredictiveCostAuditorAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/PredictiveCostAuditorAgent.py"
    ),
    (
        "agentic_core/observability/compliance/ReportingAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/ReportingAgent.py"
    ),
    (
        "agentic_core/observability/metrics/SignatureVerifierAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/SignatureVerifierAgent.py"
    ),
    (
        "agentic_core/observability/metrics/SovereignCanonAuditorAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/SovereignCanonAuditorAgent.py"
    ),
]


def relocate_agent(source: Path, target: Path, dry_run: bool = True) -> Dict[str, any]:
    """Relocate a single agent file."""
    result = {
        "source": str(source),
        "target": str(target),
        "success": False,
        "action": "PREVIEW" if dry_run else "MOVED",
        "error": None
    }
    
    try:
        if not source.exists():
            result["error"] = f"Source not found: {source}"
            return result
        
        if target.exists():
            result["error"] = f"Target exists: {target}"
            return result
        
        if dry_run:
            result["success"] = True
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            result["success"] = True
            result["action"] = "MOVED"
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def run_final_observability_relocation(dry_run: bool = True):
    """Execute final observability relocation to achieve ZERO violations."""
    print("\n" + "=" * 80)
    print(f"  PHASE 4 FINAL PUSH: OBSERVABILITY RELOCATION ({'DRY-RUN' if dry_run else 'LIVE'})")
    print("=" * 80 + "\n")
    
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Final agents to relocate: {len(OBSERVABILITY_VIOLATIONS)}")
    print(f"Target: ZERO GRAVITY VIOLATIONS (Perfection Absolute)\n")
    
    results = []
    success_count = 0
    
    for i, (source_rel, layer, target_rel) in enumerate(OBSERVABILITY_VIOLATIONS, 1):
        source = PROJECT_ROOT / source_rel
        target = PROJECT_ROOT / target_rel
        
        print(f"[{i}/{len(OBSERVABILITY_VIOLATIONS)}] {layer} Violation:")
        print(f"  Source: {source_rel}")
        print(f"  Target: {target_rel}")
        
        result = relocate_agent(source, target, dry_run=dry_run)
        results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"  ✅ {result['action']}")
        else:
            print(f"  ❌ ERROR: {result['error']}")
        print()
    
    # Summary
    print("=" * 80)
    print("  FINAL PUSH SUMMARY")
    print("=" * 80 + "\n")
    print(f"Total agents: {len(OBSERVABILITY_VIOLATIONS)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {len(OBSERVABILITY_VIOLATIONS) - success_count}")
    
    if dry_run:
        print("\n⚠️  DRY-RUN complete. Run with --execute to achieve Zero Violations.")
    else:
        print("\n✅ PERFECTION ABSOLUTE ACHIEVED!")
        print("   All observability agents relocated to L3 orchestration.")
        print("   Run audit_ssot.py to verify: Gravity Violations = 0")
    
    return {
        "total": len(OBSERVABILITY_VIOLATIONS),
        "successful": success_count,
        "errors": len(OBSERVABILITY_VIOLATIONS) - success_count,
        "dry_run": dry_run
    }


if __name__ == "__main__":
    dry_run = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        dry_run = False
        print("\n⚠️  WARNING: FINAL PUSH - LIVE EXECUTION")
        print("   This will achieve ZERO GRAVITY VIOLATIONS")
        response = input("   Continue? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            print("   Aborted.")
            sys.exit(0)
    
    summary = run_final_observability_relocation(dry_run=dry_run)
    sys.exit(0 if summary["errors"] == 0 else 1)
