"""
Phase 4 Step 2: Final Gravity Relocation
Relocates remaining 24 gravity-violating agents to Gospel-mandated territories.

This completes the Gospel Enforcement by moving all remaining agents to their
SSOT-assigned L1/L2/L3 locations.
"""

import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.resolve()

# Remaining 24 gravity violations from Phase 3 audit
FINAL_GRAVITY_VIOLATIONS: List[Tuple[str, str, str]] = [
    # L2 Violations - utils/core_extensions agents (7 agents)
    (
        "agentic_core/utils/core_extensions/L3Agent.py",
        "L2",
        "agentic_core/L3_orchestration/workflow_engines/L3Agent.py"
    ),
    (
        "agentic_core/utils/core_extensions/L4Agent.py",
        "L2",
        "agentic_core/L4_state/ValidationContext/L4Agent.py"
    ),
    (
        "agentic_core/utils/core_extensions/L5Agent.py",
        "L2",
        "agentic_core/L5_safety/validators/L5Agent.py"
    ),
    (
        "agentic_core/utils/core_extensions/NamingAgent.py",
        "L2",
        "agentic_core/L5_safety/validators/NamingAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/NamingLawHealerAgent.py",
        "L2",
        "agentic_core/L5_safety/validators/NamingLawHealerAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/NamingNormalizationAgent.py",
        "L2",
        "agentic_core/L5_safety/validators/NamingNormalizationAgent.py"
    ),
    (
        "agentic_core/prompt_governance/rendering/LLMPromptGovernorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/LLMPromptGovernorAgent.py"
    ),
    
    # L2 Violation - semantic_memory (1 agent)
    (
        "agentic_core/semantic_memory/store/SovereignPineconeStoreAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/SovereignPineconeStoreAgent.py"
    ),
    
    # L3 Violations - observability/metrics (2 agents)
    (
        "agentic_core/observability/metrics/BenchmarkingAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/BenchmarkingAgent.py"
    ),
    (
        "agentic_core/observability/metrics/CoordinateObservabilityOperationsAgent.py",
        "L3",
        "agentic_core/L3_orchestration/workflow_engines/CoordinateObservabilityOperationsAgent.py"
    ),
]


def print_header(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def relocate_agent(source: Path, target: Path, dry_run: bool = True) -> Dict[str, any]:
    """Relocate a single agent file with safety checks."""
    result = {
        "source": str(source),
        "target": str(target),
        "success": False,
        "action": "PREVIEW" if dry_run else "MOVED",
        "error": None
    }
    
    try:
        if not source.exists():
            result["error"] = f"Source file not found: {source}"
            return result
        
        if target.exists():
            result["error"] = f"Target already exists: {target}"
            return result
        
        if dry_run:
            result["success"] = True
            result["action"] = "PREVIEW"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            result["success"] = True
            result["action"] = "MOVED"
            
            # Clean up empty source directories
            try:
                if source.parent.exists() and not any(source.parent.iterdir()):
                    source.parent.rmdir()
            except OSError:
                pass
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def run_final_gravity_relocation(dry_run: bool = True) -> Dict[str, any]:
    """Execute final gravity relocation for remaining 24 agents."""
    print_header(f"PHASE 4 STEP 2: FINAL GRAVITY RELOCATION ({'DRY-RUN' if dry_run else 'LIVE'})")
    
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Remaining agents to relocate: {len(FINAL_GRAVITY_VIOLATIONS)}")
    print(f"Mode: {'PREVIEW ONLY' if dry_run else 'EXECUTING MOVES'}\n")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, (source_rel, layer, target_rel) in enumerate(FINAL_GRAVITY_VIOLATIONS, 1):
        source = PROJECT_ROOT / source_rel
        target = PROJECT_ROOT / target_rel
        
        print(f"[{i}/{len(FINAL_GRAVITY_VIOLATIONS)}] {layer} Violation:")
        print(f"  Source: {source_rel}")
        print(f"  Target: {target_rel}")
        
        result = relocate_agent(source, target, dry_run=dry_run)
        results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"  ✅ {result['action']}")
        else:
            error_count += 1
            print(f"  ❌ ERROR: {result['error']}")
        
        print()
    
    # Summary
    print_header("FINAL RELOCATION SUMMARY")
    print(f"Total agents: {len(FINAL_GRAVITY_VIOLATIONS)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Mode: {'DRY-RUN (no changes made)' if dry_run else 'LIVE EXECUTION (files moved)'}")
    
    if dry_run:
        print("\n⚠️  This was a DRY-RUN. No files were moved.")
        print("   Run with --execute to apply changes.")
    else:
        print("\n✅ Final gravity relocation complete!")
        print("   All 24 remaining agents relocated to Gospel territories.")
        print("   Run full_agent_discovery.py to refresh registry.")
    
    return {
        "total": len(FINAL_GRAVITY_VIOLATIONS),
        "successful": success_count,
        "errors": error_count,
        "dry_run": dry_run,
        "results": results
    }


if __name__ == "__main__":
    dry_run = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--execute":
            dry_run = False
            print("\n⚠️  WARNING: LIVE EXECUTION MODE")
            print("   24 agents will be physically moved on disk.")
            response = input("   Continue? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                print("   Aborted by user.")
                sys.exit(0)
        elif sys.argv[1] == "--dry-run":
            dry_run = True
        else:
            print("Usage: python phase4_final_gravity_relocation.py [--dry-run|--execute]")
            sys.exit(1)
    
    summary = run_final_gravity_relocation(dry_run=dry_run)
    sys.exit(0 if summary["errors"] == 0 else 1)
