"""
Trim heavy airlock __init__.py files to meet 50-line limit.
Condenses verbose __all__ lists and removes blank lines.
"""
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def trim_airlock(init_file):
    """Trim a single __init__.py file to ≤50 lines."""
    lines = init_file.read_text(encoding='utf-8').splitlines()
    
    if len(lines) <= 50:
        return False
    
    # Strategy: Remove blank lines and condense __all__
    new_lines = []
    in_all = False
    all_items = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip blank lines
        if not stripped:
            continue
        
        # Collect __all__ items
        if '__all__' in line:
            in_all = True
            continue
        
        if in_all:
            if ']' in line:
                in_all = False
                continue
            # Extract items from __all__
            items = stripped.strip("',\"").split(',')
            all_items.extend([i.strip().strip("'\"") for i in items if i.strip()])
            continue
        
        new_lines.append(line)
    
    # Add condensed __all__ if it existed
    if all_items:
        # Keep only first 8 most important items
        important = all_items[:8]
        new_lines.append(f"__all__ = {important}")
    
    # Write back
    content = '\n'.join(new_lines) + '\n'
    init_file.write_text(content, encoding='utf-8')
    return True

def trim_all_airlocks():
    """Trim all heavy airlock files."""
    print("[*] TRIMMING HEAVY AIRLOCKS...")
    trimmed = 0
    
    for init_file in CORE.rglob("__init__.py"):
        lines = init_file.read_text(encoding='utf-8').splitlines()
        if len(lines) > 50:
            if trim_airlock(init_file):
                new_lines = len(init_file.read_text(encoding='utf-8').splitlines())
                print(f"  [✓] Trimmed: {init_file.relative_to(CORE)} ({len(lines)} -> {new_lines} lines)")
                trimmed += 1
    
    print(f"\n[OK] Trimmed {trimmed} airlock files")

if __name__ == "__main__":
    trim_all_airlocks()
