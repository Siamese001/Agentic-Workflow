"""
PHASE 3: DEEP INTROSPECTION SCAN
--------------------------------
Objective:
    1. Identify remaining PascalCase files.
    2. Use AST to check if 'class Filename' exists inside.
    3. Generate a definitive "Rename vs Keep" manifest.
"""

import ast
import os
import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
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
    "scripts",
    "tests",
}

# Known valid suffixes we already handled or trust
IGNORED_SUFFIXES = ("Agent.py", "Orchestrator.py", "Validator.py", "Factory.py")


def is_pascal_case(name: str) -> bool:
    # Must start with Upper, contain no underscores, not be all caps
    return name[0].isupper() and "_" not in name and not name.isupper() and name.endswith(".py")


def check_file_content(path: Path) -> str:
    """
    Returns 'KEEP' if class matches filename, 'RENAME' otherwise.
    """
    stem = path.stem
    try:
        # Read and parse
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Look for class definition matching the stem
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == stem:
                    return "KEEP"

        return "RENAME"
    except Exception as e:
        return f"ERROR: {e}"


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def main():
    print("[*] Starting Phase 3 Deep Scan...")

    results = {"KEEP": [], "RENAME": [], "ERROR": []}

    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in QUARANTINED_DIRS]

        for f in files:
            if not is_pascal_case(f):
                continue
            if f.endswith(IGNORED_SUFFIXES):
                continue
            if f == "Config.py":
                continue  # Already handled, but check just in case

            path = Path(root) / f
            decision = check_file_content(path)

            if decision == "KEEP":
                results["KEEP"].append(path)
            elif decision == "RENAME":
                results["RENAME"].append(path)
            else:
                results["ERROR"].append((path, decision))

    # Output Report
    print("\n[SCAN COMPLETE]")
    print(f"  KEEP:   {len(results['KEEP'])} (Valid Class Files)")
    print(f"  RENAME: {len(results['RENAME'])} (Scripts/Utilities)")
    print(f"  ERROR:  {len(results['ERROR'])}")

    # Generate Manifest
    manifest_path = ROOT_DIR / "phase3_manifest.txt"
    with open(manifest_path, "w") as f:
        f.write("# PHASE 3 MANIFEST: Files to Rename\n")
        f.write("# Format: OldPath -> NewName\n")
        for path in results["RENAME"]:
            new_name = to_snake_case(path.name)
            f.write(f"{path.relative_to(ROOT_DIR)} -> {new_name}\n")

    print(f"\n[*] Manifest written to {manifest_path.name}")

    if len(results["RENAME"]) > 0:
        print("    Sample Candidates:")
        for p in results["RENAME"][:5]:
            print(f"    - {p.name}")


if __name__ == "__main__":
    main()
