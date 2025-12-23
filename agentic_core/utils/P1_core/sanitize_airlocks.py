import os
import ast
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

def sanitize_file(file_path):
    """Checks for common syntax errors and forces closure of brackets."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    
    for line in lines:
        # Fix 1: Character after line continuation '\'
        if "\\" in line and not line.strip().endswith("\\"):
            # If there's content after the \, it's a syntax error
            parts = line.split("\\")
            line = parts[0] + "\\" + "\n"
            modified = True
            
        new_lines.append(line)

    # Fix 2: Balancing Brackets in __init__ files (very common in __all__ lists)
    content = "".join(new_lines)
    for opening, closing in [("{", "}"), ("[", "]"), ("(", ")")]:
        if content.count(opening) > content.count(closing):
            print(f"  [!] Closing unsealed {opening} in {file_path.name}")
            content += f"\n{closing}\n"
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def run_sanitizer():
    print("[*] SOVEREIGN SANITIZER: Flushing the Synaptic Loops...")
    count = 0
    
    # Target all __init__ files and the files mentioned in your logs
    targets = list(CORE.rglob("__init__.py")) + list(CORE.rglob("*_impl.py"))
    
    for target in targets:
        try:
            if sanitize_file(target):
                print(f"  [✓] Sanitized: {target.relative_to(CORE)}")
                count += 1
        except Exception as e:
            print(f"  [X] Failed to sanitize {target.name}: {e}")

    print(f"\n[OK] SANITIZATION COMPLETE. {count} files flushed.")
    print("[!] ACTION: You can now restart the validator without the 'Resilient Mutation' loop.")

if __name__ == "__main__":
    run_sanitizer()
