"""
Phase 4 PERFECTION ABSOLUTE: Final 4 Agents
Relocates the last 4 gravity-violating agents to achieve ZERO violations.
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

# Final 4 gravity violations - all observability agents assigned to L3
FINAL_FOUR: list = [
    (
        "agentic_core/observability/telemetry/TelemetryAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/TelemetryAgent.py"
    ),
    (
        "agentic_core/observability/metrics/TokenBudgetInspectorAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/TokenBudgetInspectorAgent.py"
    ),
    (
        "agentic_core/observability/tracing/TracingAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/TracingAgent.py"
    ),
    (
        "agentic_core/observability/metrics/TrackObservabilityCostAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/TrackObservabilityCostAgent.py"
    ),
]


def relocate_agent(source: Path, target: Path):
    """Relocate a single agent file."""
    if not source.exists():
        return False, f"Source not found: {source}"
    
    if target.exists():
        return False, f"Target exists: {target}"
    
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return True, "MOVED"
    except Exception as e:
        return False, str(e)


def achieve_perfection_absolute():
    """Execute final 4 relocations to achieve ZERO violations."""
    print("\n" + "=" * 80)
    print("  PHASE 4: PERFECTION ABSOLUTE - FINAL 4 AGENTS")
    print("=" * 80 + "\n")
    
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Final agents: {len(FINAL_FOUR)}")
    print(f"Target: ZERO GRAVITY VIOLATIONS\n")
    
    success_count = 0
    
    for i, (source_rel, layer, target_rel) in enumerate(FINAL_FOUR, 1):
        source = PROJECT_ROOT / source_rel
        target = PROJECT_ROOT / target_rel
        
        print(f"[{i}/{len(FINAL_FOUR)}] {layer} Violation:")
        print(f"  Source: {source_rel}")
        print(f"  Target: {target_rel}")
        
        success, msg = relocate_agent(source, target)
        
        if success:
            success_count += 1
            print(f"  ✅ {msg}\n")
        else:
            print(f"  ❌ ERROR: {msg}\n")
    
    # Summary
    print("=" * 80)
    print("  PERFECTION ABSOLUTE")
    print("=" * 80 + "\n")
    print(f"Total: {len(FINAL_FOUR)}")
    print(f"Success: {success_count}")
    print(f"Errors: {len(FINAL_FOUR) - success_count}\n")
    
    if success_count == len(FINAL_FOUR):
        print("🎯 PERFECTION ABSOLUTE ACHIEVED!")
        print("   ALL agents in Gospel-mandated territories.")
        print("   Gravity Violations = 0")
        print("\n   Run: python scripts/audit_ssot.py")
        print("   Expected: Gravity Violations: 0\n")
    
    return success_count == len(FINAL_FOUR)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("\n⚠️  FINAL EXECUTION: Achieving Perfection Absolute")
        response = input("   Continue? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            print("   Aborted.")
            sys.exit(0)
        
        success = achieve_perfection_absolute()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python phase4_perfection_absolute.py --execute")
        sys.exit(1)
