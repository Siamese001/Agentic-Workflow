"""
Phase 2: Gravity Relocation Script
Relocates 34 misplaced agents to their SSOT-assigned L1/L2 territories.

Safety Features:
- Dry-run mode by default
- shutil.move preserves file metadata
- Ignores __pycache__ and .pyc files
- Creates target directories if needed
- Logs all operations

Usage:
    python phase2_gravity_relocation.py --dry-run  # Preview moves
    python phase2_gravity_relocation.py --execute  # Execute moves
"""

import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.resolve()

# Gravity violations from Phase 1 audit (34 agents)
# Format: (current_path, assigned_layer, target_path)
GRAVITY_VIOLATIONS: List[Tuple[str, str, str]] = [
    # L1 Violations (1 agent)
    (
        "agentic_core/schemas/models/CognitiveContractValidatorAgent.py",
        "L1",
        "agentic_core/L1_cognition/thought_engine/CognitiveContractValidatorAgent.py"
    ),
    
    # L2 Violations (33 agents)
    (
        "agentic_core/runtime/shared_runtime/CanonAstValidatorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/CanonAstValidatorAgent.py"
    ),
    (
        "agentic_core/patterns/agent_roles/ContextAwareValidatorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/ContextAwareValidatorAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/DeadCodeDetectorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/DeadCodeDetectorAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/DriftDetectorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/DriftDetectorAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/GlobalComplianceAggregatorAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/GlobalComplianceAggregatorAgent.py"
    ),
    (
        "agentic_core/runtime/shared_runtime/ImportHealerAgent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/ImportHealerAgent.py"
    ),
    (
        "agentic_core/utils/core_extensions/L0Agent.py",
        "L2",
        "agentic_core/L0_maintenance/scripts/L0Agent.py"
    ),
    (
        "agentic_core/utils/core_extensions/L1Agent.py",
        "L2",
        "agentic_core/L1_cognition/thought_engine/L1Agent.py"
    ),
    (
        "agentic_core/utils/core_extensions/L2Agent.py",
        "L2",
        "agentic_core/L2_execution/ToolRegistry/L2Agent.py"
    ),
]


def print_header(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def relocate_agent(source: Path, target: Path, dry_run: bool = True) -> Dict[str, any]:
    """
    Relocate a single agent file with safety checks.
    
    Args:
        source: Current file path
        target: Target file path
        dry_run: If True, only preview the move
        
    Returns:
        Dict with operation status and details
    """
    result = {
        "source": str(source),
        "target": str(target),
        "success": False,
        "action": "PREVIEW" if dry_run else "MOVED",
        "error": None
    }
    
    try:
        # Check source exists
        if not source.exists():
            result["error"] = f"Source file not found: {source}"
            return result
        
        # Check target doesn't exist
        if target.exists():
            result["error"] = f"Target already exists: {target}"
            return result
        
        if dry_run:
            result["success"] = True
            result["action"] = "PREVIEW"
        else:
            # Create target directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file (preserves metadata)
            shutil.move(str(source), str(target))
            
            result["success"] = True
            result["action"] = "MOVED"
            
            # Clean up empty source directories
            try:
                if source.parent.exists() and not any(source.parent.iterdir()):
                    source.parent.rmdir()
            except OSError:
                pass  # Directory not empty, that's fine
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


def run_gravity_relocation(dry_run: bool = True) -> Dict[str, any]:
    """
    Execute gravity relocation for all 34 misplaced agents.
    
    Args:
        dry_run: If True, only preview moves without executing
        
    Returns:
        Summary dict with results
    """
    print_header(f"PHASE 2: GRAVITY RELOCATION ({'DRY-RUN' if dry_run else 'LIVE EXECUTION'})")
    
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Agents to relocate: {len(GRAVITY_VIOLATIONS)}")
    print(f"Mode: {'PREVIEW ONLY' if dry_run else 'EXECUTING MOVES'}\n")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, (source_rel, layer, target_rel) in enumerate(GRAVITY_VIOLATIONS, 1):
        source = PROJECT_ROOT / source_rel
        target = PROJECT_ROOT / target_rel
        
        print(f"[{i}/{len(GRAVITY_VIOLATIONS)}] {layer} Violation:")
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
    print_header("RELOCATION SUMMARY")
    print(f"Total agents: {len(GRAVITY_VIOLATIONS)}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Mode: {'DRY-RUN (no changes made)' if dry_run else 'LIVE EXECUTION (files moved)'}")
    
    if dry_run:
        print("\n⚠️  This was a DRY-RUN. No files were moved.")
        print("   Run with --execute to apply changes.")
    else:
        print("\n✅ Gravity relocation complete!")
        print("   Run audit_ssot.py to verify violations dropped to 0.")
    
    return {
        "total": len(GRAVITY_VIOLATIONS),
        "successful": success_count,
        "errors": error_count,
        "dry_run": dry_run,
        "results": results
    }


if __name__ == "__main__":
    # Parse command line arguments
    dry_run = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--execute":
            dry_run = False
            print("\n⚠️  WARNING: LIVE EXECUTION MODE")
            print("   Files will be physically moved on disk.")
            response = input("   Continue? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                print("   Aborted by user.")
                sys.exit(0)
        elif sys.argv[1] == "--dry-run":
            dry_run = True
        else:
            print("Usage: python phase2_gravity_relocation.py [--dry-run|--execute]")
            sys.exit(1)
    
    # Run relocation
    summary = run_gravity_relocation(dry_run=dry_run)
    
    # Exit with error code if any failures
    sys.exit(0 if summary["errors"] == 0 else 1)
