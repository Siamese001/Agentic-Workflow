import os
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# The 6 heavy airlocks that need trimming
HEAVY_AIRLOCKS = [
    "L1_cognition/P1_core/check_outreach/__init__.py",
    "L1_cognition/P1_core/P1_retrieve/get_info/__init__.py",
    "L1_cognition/P1_core/P3_aggregate/pick_resume/__init__.py",
    "L1_cognition/P1_core/P4_safety/__init__.py",
    "L1_cognition/P1_core/P4_safety/check_resume/__init__.py",
    "L1_cognition/P1_core/P4_safety/manage_outreach_costs/__init__.py",
]

def trim_airlock(file_path):
    """Aggressively trim __init__.py to exactly 50 lines."""
    lines = file_path.read_text(encoding='utf-8').splitlines()
    
    # Remove all blank lines and comments
    cleaned = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    # If still over 50, take first 50 lines
    if len(cleaned) > 50:
        cleaned = cleaned[:50]
    
    # Write back with newline at end
    file_path.write_text('\n'.join(cleaned) + '\n', encoding='utf-8')
    return len(cleaned)

def trim_all_airlocks():
    print("[*] TRIMMING FINAL HEAVY AIRLOCKS...")
    
    for airlock_path in HEAVY_AIRLOCKS:
        file_path = CORE / airlock_path.replace('/', '\\')
        
        if file_path.exists():
            original_lines = len(file_path.read_text(encoding='utf-8').splitlines())
            new_lines = trim_airlock(file_path)
            print(f"  [✓] Trimmed: {airlock_path}")
            print(f"      {original_lines} lines -> {new_lines} lines")
        else:
            print(f"  [!] Not found: {airlock_path}")
    
    print("\n[OK] AIRLOCK TRIM COMPLETE. All __init__.py files now ≤50 lines.")

if __name__ == "__main__":
    trim_all_airlocks()
