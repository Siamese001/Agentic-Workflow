import os
import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")

def undo_gravity_comments(file_path: Path):
    """Remove gravity fix comments and restore original imports."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove gravity fix comment lines
        content = re.sub(r'# GRAVITY FIX:.*?\n# ', '', content)
        content = re.sub(r'# GRAVITY FIX:.*?\n', '', content)
        
        # Uncomment the imports
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            # If line starts with "# from" or "# import", uncomment it
            if line.strip().startswith('# from ') or line.strip().startswith('# import '):
                new_lines.append(line.replace('# ', '', 1))
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"  [!] Error: {e}")
        return False

def undo_all_comments():
    print("[*] UNDOING GRAVITY FIX COMMENTS...")
    
    files_to_fix = [
        "agentic_core/L1_cognition/agent_logic.py",
        "agentic_core/L3_orchestration/mission_runner.py",
        "agentic_core/L2_execution/P4_agents/analysis.py",
        "apps_shared/verify_hardening.py",
        "scripts/validation/dry_run_signal_failure_test.py",
        "scripts/validation/test_l5_infrastructure.py",
        "scripts/workflow/dry_run_l5_verification.py"
    ]
    
    count = 0
    for file_rel in files_to_fix:
        file_path = ROOT / file_rel
        if file_path.exists():
            if undo_gravity_comments(file_path):
                print(f"  ✓ Restored: {file_rel}")
                count += 1
    
    print(f"\n[OK] Restored {count} files")

if __name__ == "__main__":
    undo_all_comments()
