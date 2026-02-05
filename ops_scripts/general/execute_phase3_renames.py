"""
PHASE 3: EXECUTION & LINKAGE REPAIR
-----------------------------------
Objective:
    1. Parse 'phase3_manifest.txt'.
    2. Execute `git mv` for 116 files.
    3. Aggressively update module references using robust regex.
"""

import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = ROOT_DIR / "phase3_manifest.txt"

QUARANTINED_DIRS = {
    "archives",
    ".sovereign_healing_backup",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}


def load_manifest():
    if not MANIFEST_FILE.exists():
        print(f"[ERROR] Manifest not found: {MANIFEST_FILE}")
        return []

    renames = []
    with open(MANIFEST_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse "OldPath -> NewName"
            if "->" in line:
                parts = line.split("->")
                old_rel = parts[0].strip()
                new_name = parts[1].strip()

                old_path = ROOT_DIR / old_rel
                new_path = old_path.parent / new_name

                renames.append((old_path, new_path))
    return renames


def update_imports_global(renames):
    print("\n[Phase 3] Updating Imports (Global Robust)...")

    # Build Map: OldStem -> NewStem
    # Example: LicArchetypes -> lic_archetypes
    rename_map = {}
    for old_path, new_path in renames:
        rename_map[old_path.stem] = new_path.stem

    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]

        for f in files:
            if not f.endswith(".py"):
                continue
            path = Path(root) / f

            # Skip the script itself
            if path.name == "execute_phase3_renames.py":
                continue

            try:
                content = path.read_text(encoding="utf-8")
                original_content = content

                for old, new in rename_map.items():
                    if old not in content:
                        continue

                    # LOGIC: Replace whole word 'Old' with 'New'
                    # EXCEPT: If preceded by 'class ' (defensive coding, even if AST said no class)

                    def replacement_logic(match):
                        prefix = match.group(1)
                        if "class" in prefix:
                            return match.group(0)  # Protect definitions
                        return f"{prefix}{new}"

                    # Regex: (Non-Word-Char) + OldName + (Word-Boundary)
                    pattern = re.compile(r"([^a-zA-Z0-9_])" + re.escape(old) + r"\b")
                    content = pattern.sub(replacement_logic, content)

                if content != original_content:
                    path.write_text(content, encoding="utf-8")
                    count += 1
            except Exception:
                pass

    print(f"  Modified {count} files with reference updates.")


def main():
    print("[*] Starting Phase 3 Execution...")
    renames = load_manifest()
    print(f"[*] Loaded {len(renames)} renames from manifest.")

    # 1. Execute Git Moves
    print("\n[Phase 3] Executing Git Moves...")
    success_count = 0

    for old_path, new_path in renames:
        if new_path.exists():
            print(f"  [SKIP] Target exists: {new_path.name}")
            continue

        if not old_path.exists():
            print(f"  [WARN] Source missing: {old_path.name}")
            continue

        # Try git mv
        cmd = f'git mv "{old_path}" "{new_path}"'
        if os.system(cmd) == 0:
            success_count += 1
        else:
            # Fallback to os.rename if git fails (e.g. untracked file)
            try:
                os.rename(old_path, new_path)
                success_count += 1
                print(f"  [OK-OS] {old_path.name} -> {new_path.name}")
            except OSError as e:
                print(f"  [ERROR] Failed to move {old_path.name}: {e}")

    print(f"  Moved {success_count} files.")

    # 2. Update Imports
    if success_count > 0:
        update_imports_global(renames)

    print("\n[SUCCESS] Phase 3 Complete.")


if __name__ == "__main__":
    main()
