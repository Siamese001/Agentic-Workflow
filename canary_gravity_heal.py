#!/usr/bin/env python3
"""
Canary Gravity Healing Test
Tests healing on a single non-critical file with full verification

SAFETY:
- Only heals ONE file at a time
- Creates git checkpoint before healing
- Provides detailed diff output for manual verification
- Records healing in GravityStateAgent
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.GravityValidatorAgent import GravityValidatorAgent
from agentic_core.L2_execution.ToolRegistry.GravityHealerAgent import GravityHealerAgent
from agentic_core.L4_state.GravityStateAgent import GravityStateAgent, HealingRecord
from datetime import datetime


async def canary_test():
    """
    Perform canary healing test on a single file.
    
    Steps:
    1. Identify a low-risk L1 file with violations
    2. Create backup and git checkpoint
    3. Run healing on single file
    4. Display detailed diff
    5. Record in state tracker
    """
    print("=" * 80)
    print("CANARY GRAVITY HEALING TEST")
    print("=" * 80)
    
    # Initialize agents
    validator = GravityValidatorAgent(project_root)
    healer = GravityHealerAgent(project_root)
    state_tracker = GravityStateAgent(project_root)
    
    # Select canary file - a utility agent with minimal dependencies
    canary_candidates = [
        project_root / "agentic_core" / "L1_cognition" / "thought_engine" / "HealerAgent.py",
    ]
    
    canary_file = None
    canary_violations = []
    
    print("\n📋 STEP 1: Identifying canary file...")
    for candidate in canary_candidates:
        if not candidate.exists():
            continue
        
        violations = await validator.detect_violations(candidate)
        if violations:
            canary_file = candidate
            canary_violations = violations
            print(f"   ✅ Selected: {canary_file.relative_to(project_root)}")
            print(f"   📊 Violations found: {len(violations)}")
            for v in violations:
                print(f"      - Line {v.line_number}: {v.violation_type} ({v.severity}/10)")
            break
    
    if not canary_file:
        print("   ⚠️  No suitable canary file found")
        return
    
    # Create checkpoint
    print("\n💾 STEP 2: Creating safety checkpoint...")
    checkpoint = state_tracker.create_checkpoint("canary_test")
    print(f"   ✅ Checkpoint created: {checkpoint}")
    
    # Backup original file
    backup_file = canary_file.with_suffix(".py.backup")
    backup_file.write_text(canary_file.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"   ✅ Backup created: {backup_file.name}")
    
    # Read original content for diff
    original_content = canary_file.read_text(encoding="utf-8")
    
    # Perform healing
    print("\n🔧 STEP 3: Applying healing (REAL MODIFICATION)...")
    print(f"   ⚠️  WARNING: This will modify {canary_file.name}")
    print(f"   ⚠️  Backup available at: {backup_file}")
    
    input("\n   Press ENTER to proceed with healing, or Ctrl+C to abort...")
    
    healing_results = await healer.heal(canary_violations)
    
    print(f"\n   📊 Healing Results:")
    print(f"      Healed: {healing_results['statistics']['healed']}")
    print(f"      Failed: {healing_results['statistics']['failed']}")
    print(f"      Skipped: {healing_results['statistics']['skipped']}")
    
    # Read healed content
    healed_content = canary_file.read_text(encoding="utf-8")
    
    # Display diff
    print("\n📝 STEP 4: Displaying changes...")
    print("=" * 80)
    
    original_lines = original_content.splitlines()
    healed_lines = healed_content.splitlines()
    
    # Simple diff display
    max_lines = max(len(original_lines), len(healed_lines))
    changes_found = False
    
    for i in range(max_lines):
        orig_line = original_lines[i] if i < len(original_lines) else ""
        heal_line = healed_lines[i] if i < len(healed_lines) else ""
        
        if orig_line != heal_line:
            if not changes_found:
                print(f"\n🔍 Changes at line {i+1}:")
                changes_found = True
            
            if orig_line:
                print(f"   - {orig_line}")
            if heal_line:
                print(f"   + {heal_line}")
    
    if not changes_found:
        print("   ⚠️  No changes detected (healing may have failed)")
    
    print("\n" + "=" * 80)
    
    # Record in state tracker
    print("\n💾 STEP 5: Recording healing in state tracker...")
    for result in healing_results['results']:
        if result['result']['success']:
            record = HealingRecord(
                file_path=str(canary_file),
                original_import=result.get('action', 'unknown'),
                healed_import="dynamic_import",
                violation_type=result['violation_type'],
                healing_strategy=result['result']['strategy'],
                timestamp=datetime.now().isoformat(),
            )
            state_tracker.record_healing(record)
    
    print(f"   ✅ Recorded {healing_results['statistics']['healed']} healings")
    
    # Display state summary
    summary = state_tracker.get_healing_summary()
    print(f"\n📊 State Tracker Summary:")
    print(f"   Total files healed: {summary['total_files_healed']}")
    print(f"   Total healings: {summary['total_healings']}")
    
    # Verification instructions
    print("\n" + "=" * 80)
    print("🔍 MANUAL VERIFICATION REQUIRED")
    print("=" * 80)
    print(f"\n1. Review the changes above")
    print(f"2. Run git diff to see full changes:")
    print(f"   git diff {canary_file.relative_to(project_root)}")
    print(f"\n3. Test the file (if applicable):")
    print(f"   python -m pytest {canary_file.relative_to(project_root)}")
    print(f"\n4. If changes look good:")
    print(f"   git add {canary_file.relative_to(project_root)}")
    print(f"   git commit -m 'Canary: Gravity healing test on {canary_file.name}'")
    print(f"\n5. If changes are bad:")
    print(f"   cp {backup_file} {canary_file}")
    print(f"   # Or restore from checkpoint: {checkpoint}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(canary_test())
