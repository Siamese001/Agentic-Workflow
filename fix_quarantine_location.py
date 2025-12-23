import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
ARCHIVES = ROOT / "archives"
WRONG_LOCATION = ROOT / "agentic_core/L0_maintenance/automation/quarantine_syntax_errors"
CORRECT_LOCATION = ARCHIVES / "quarantine_syntax_errors"

def fix_quarantine():
    print("[*] MOVING quarantine_syntax_errors to archives...")
    
    if not WRONG_LOCATION.exists():
        print("[!] Quarantine folder not found at wrong location")
        return
    
    ARCHIVES.mkdir(exist_ok=True)
    
    try:
        shutil.move(str(WRONG_LOCATION), str(CORRECT_LOCATION))
        print(f"[✓] Moved quarantine to: {CORRECT_LOCATION.relative_to(ROOT)}")
    except Exception as e:
        print(f"[X] Failed to move quarantine: {e}")

if __name__ == "__main__":
    fix_quarantine()
