"""
Fix gravity breaches caused by force_app_depth.py moving app-specific code to core.
Move app-specific orchestrators and engines back to their respective apps.
"""
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Files that were incorrectly moved to core and need to go back to apps
MOVES_BACK = [
    # L3 orchestrators that belong in apps_rg
    (CORE / "L3_orchestration/P1_core/l5_autonomous_orchestrator.py", ROOT / "apps_rg/L3_orchestration"),
    (CORE / "L3_orchestration/P1_core/l5_orchestrator", ROOT / "apps_rg/L3_orchestration"),
    
    # Outreach engine tests that import apps_lic
    (CORE / "L2_execution/P3_engines/outreach_engine", ROOT / "apps_lic/engines"),
    
    # Resume engine tests that import apps_rg  
    (CORE / "L2_execution/P3_engines/resume_engine", ROOT / "apps_rg/engines"),
]

def fix_gravity():
    print("[*] FIXING GRAVITY BREACHES...")
    fixed = 0
    
    for src, dest_dir in MOVES_BACK:
        if not src.exists():
            print(f"  [SKIP] {src.name} - doesn't exist")
            continue
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        
        # If destination exists, remove it first
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(str(dest))
            else:
                dest.unlink()
        
        shutil.move(str(src), str(dest))
        print(f"  [✓] Moved: {src.relative_to(CORE)} -> {dest.relative_to(ROOT)}")
        fixed += 1
    
    print(f"\n[OK] Fixed {fixed} gravity breaches")

if __name__ == "__main__":
    fix_gravity()
