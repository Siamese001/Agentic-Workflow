"""
file: ops_scripts/migration/flatten_shadow_units.py
description: |
    Remediation Script.
    Fixes the 'Path Stuttering' bug where tests were moved to:
    tests/unit/agentic_core/unit/...
    
    Action:
    Moves content of tests/unit/agentic_core/unit/* -> tests/unit/agentic_core/*
    Removes the empty 'unit' shadow folder.
    
    Also handles nested shadow units within layer directories:
    tests/unit/agentic_core/L0_maintenance/unit/* -> tests/unit/agentic_core/L0_maintenance/*
"""
import shutil
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_UNIT_DIR = PROJECT_ROOT / "tests/unit"

# Shadow patterns to detect and flatten
SHADOW_PATTERNS = [
    # Top-level shadow
    ("tests/unit/agentic_core/unit", "tests/unit/agentic_core"),
    # Layer-level shadows
    ("tests/unit/agentic_core/L0_maintenance/unit", "tests/unit/agentic_core/L0_maintenance"),
    ("tests/unit/agentic_core/L0_maintenance/L0_maintenance", "tests/unit/agentic_core/L0_maintenance"),
    ("tests/unit/agentic_core/L1_cognition/unit", "tests/unit/agentic_core/L1_cognition"),
    ("tests/unit/agentic_core/L2_execution/unit", "tests/unit/agentic_core/L2_execution"),
    ("tests/unit/agentic_core/L3_orchestration/unit", "tests/unit/agentic_core/L3_orchestration"),
    ("tests/unit/agentic_core/L4_state/unit", "tests/unit/agentic_core/L4_state"),
    ("tests/unit/agentic_core/L5_safety/unit", "tests/unit/agentic_core/L5_safety"),
    ("tests/unit/agentic_core/L6_observability/unit", "tests/unit/agentic_core/L6_observability"),
]


def flatten_shadow_directory(shadow_rel: str, target_rel: str) -> int:
    """
    Flatten a shadow directory by hoisting its contents to the target.
    Returns count of items moved.
    """
    shadow_dir = PROJECT_ROOT / shadow_rel
    target_dir = PROJECT_ROOT / target_rel
    
    if not shadow_dir.exists():
        return 0
    
    print(f"\n⚠️  Shadow Directory detected: {shadow_dir}")
    print("   Initiating Hoist Operation...")
    
    moved_count = 0
    
    # Walk the shadow directory
    for item in shadow_dir.iterdir():
        if item.name == "__pycache__":
            # Skip pycache, will be regenerated
            shutil.rmtree(item, ignore_errors=True)
            continue
            
        src = item
        dst = target_dir / item.name
        
        try:
            if dst.exists():
                if dst.is_dir() and src.is_dir():
                    # Merge directories recursively
                    print(f"   🔀 Merging directory: {item.name}")
                    for sub_item in src.rglob("*"):
                        if sub_item.is_file():
                            rel_path = sub_item.relative_to(src)
                            dest_file = dst / rel_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            if not dest_file.exists():
                                shutil.copy2(sub_item, dest_file)
                                moved_count += 1
                    shutil.rmtree(src, ignore_errors=True)
                else:
                    # Collision handling: If file, warn
                    print(f"   ❌ COLLISION: {dst} already exists. Skipping {item.name}")
                continue
                
            shutil.move(str(src), str(dst))
            print(f"   ✅ Hoisted: {item.name}")
            moved_count += 1
        except Exception as e:
            print(f"   ❌ Failed to move {item.name}: {e}")

    # Cleanup empty shadow
    try:
        if shadow_dir.exists():
            shutil.rmtree(shadow_dir, ignore_errors=True)
            print(f"   🗑️  Shadow Directory removed: {shadow_rel}")
    except OSError as e:
        print(f"   ⚠️  Could not remove shadow directory: {e}")

    return moved_count


def execute_flattening():
    """Main execution function."""
    print("=" * 60)
    print("SHADOW UNIT REMEDIATION - Path Stuttering Fix")
    print("=" * 60)
    
    total_moved = 0
    shadows_found = 0
    
    for shadow_rel, target_rel in SHADOW_PATTERNS:
        shadow_path = PROJECT_ROOT / shadow_rel
        if shadow_path.exists():
            shadows_found += 1
            moved = flatten_shadow_directory(shadow_rel, target_rel)
            total_moved += moved
    
    # Also scan for any other nested 'unit' directories dynamically
    print("\n📡 Scanning for additional shadow patterns...")
    for layer_dir in (PROJECT_ROOT / "tests/unit/agentic_core").iterdir():
        if layer_dir.is_dir() and layer_dir.name.startswith("L"):
            unit_shadow = layer_dir / "unit"
            if unit_shadow.exists():
                shadows_found += 1
                rel_shadow = unit_shadow.relative_to(PROJECT_ROOT)
                rel_target = layer_dir.relative_to(PROJECT_ROOT)
                moved = flatten_shadow_directory(str(rel_shadow), str(rel_target))
                total_moved += moved
    
    print("\n" + "=" * 60)
    if shadows_found == 0:
        print("✅ No Shadow Directories found. System is clean.")
    else:
        print(f"✅ Remediation Complete.")
        print(f"   Shadows processed: {shadows_found}")
        print(f"   Items hoisted: {total_moved}")
    print("=" * 60)


if __name__ == "__main__":
    execute_flattening()
