import ast
import shutil
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
QUARANTINE = ROOT / "quarantine_syntax_errors"

def quarantine_all_broken():
    print("[*] QUARANTINE: Scanning for all syntax-broken files...")
    QUARANTINE.mkdir(exist_ok=True)
    quarantined = 0
    
    for py_file in CORE.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            ast.parse(content)
        except SyntaxError:
            # This file has syntax errors - quarantine it
            try:
                dest = QUARANTINE / py_file.name
                # Avoid collisions in quarantine
                counter = 1
                while dest.exists():
                    dest = QUARANTINE / f"{py_file.stem}_{counter}{py_file.suffix}"
                    counter += 1
                
                shutil.move(str(py_file), str(dest))
                print(f"  [✓] Quarantined: {py_file.relative_to(CORE)}")
                quarantined += 1
            except Exception as e:
                print(f"  [X] Failed to quarantine {py_file.name}: {e}")
        except Exception as e:
            # Other errors (encoding, etc.) - skip
            print(f"  [!] Skipped {py_file.name}: {e}")
    
    print(f"\n[OK] QUARANTINE COMPLETE. {quarantined} broken files isolated.")
    print(f"    Files moved to: {QUARANTINE}")

if __name__ == "__main__":
    quarantine_all_broken()
