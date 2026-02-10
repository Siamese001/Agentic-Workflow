"""
VERIFICATION SCRIPT: REFACTOR INTEGRITY CHECK
---------------------------------------------
Objective:
    1. Verify that renamed files exist at their new locations.
    2. Aggressively scan the codebase for lingering references to old filenames.
    3. Catalog remaining PascalCase violations for future debt payoff.

Strict Mode: ON
"""

import re
import sys
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent

# Map of Old Name (stem) -> New Name (file)
# We are looking for imports that reference the OLD module name
RENAMES = {
    "Config": "app_config",
    "Exceptions": "canon_exceptions",
    "Factory": "router_factory",
    "Prompts": "resume_prompts",
}

SEARCH_PATHS = ["agentic_core", "apps_shared", "apps_lic", "scripts"]


def main():
    print(f"[*] Starting Integrity Scan from root: {ROOT_DIR}")

    errors = []

    # 1. Verify New Files Exist
    print("\n[Phase 1] Verifying File Existence...")
    base_utils = ROOT_DIR / "apps_shared" / "common_utils"
    for old_stem, new_name in RENAMES.items():
        target = base_utils / f"{new_name}.py"
        if not target.exists():
            errors.append(f"[MISSING] Target file not found: {target}")
        else:
            print(f"  [OK] {new_name}.py exists.")

    # 2. Scan for Broken Imports
    print("\n[Phase 2] Scanning for Legacy Import References...")
    # Patterns to look for:
    # from apps_shared.common_utils import AppConfig
    # import apps_shared.common_utils.app_config
    # from . import AppConfig

    import_patterns = {stem: re.compile(rf"(from|import).*\b{stem}\b") for stem in RENAMES.keys()}

    scanned_count = 0
    for folder in SEARCH_PATHS:
        search_root = ROOT_DIR / folder
        if not search_root.exists():
            continue

        for path in search_root.rglob("*.py"):
            # Skip the newly renamed files themselves (they might contain class names matching the old file)
            if path.name in [f"{n}.py" for n in RENAMES.values()]:
                continue

            # Skip test/audit scripts that contain these patterns as detection strings
            if path.name in ["test_naming_convention_audit.py", "verify_refactor_integrity_util.py"]:
                continue

            try:
                content = path.read_text(encoding="utf-8")
                scanned_count += 1

                lines = content.split("\n")
                for i, line in enumerate(lines):
                    # Skip comments
                    if line.strip().startswith("#"):
                        continue

                    for old_stem, pattern in import_patterns.items():
                        # We only care if it looks like an import from common_utils
                        # This is a heuristic; we accept some false positives to be safe
                        if pattern.search(line) and "common_utils" in line:
                            # Check if it's already updated? No, we are looking for the OLD name
                            errors.append(
                                f"[BROKEN IMPORT] {path.relative_to(ROOT_DIR)}:{i + 1} "
                                f"references '{old_stem}' -> '{line.strip()}'",
                            )

            except Exception as e:
                print(f"  [WARN] Could not read {path}: {e}")

    print(f"  Scanned {scanned_count} files.")

    # 3. Audit Remaining PascalCase Violations (Future Debt)
    print("\n[Phase 3] Cataloging PascalCase Violations (Information Only)...")
    pascal_violations = []
    for folder in SEARCH_PATHS:
        root_path = ROOT_DIR / folder
        for path in root_path.rglob("*.py"):
            stem = path.stem
            # Simple PascalCase check: Starts with Upper, not all upper, no underscores
            if (
                stem[0].isupper()
                and "_" not in stem
                and not stem.isupper()
                and path.name not in ["__init__.py"]
            ):
                # Rough check for Class definition matching filename
                try:
                    content = path.read_text(encoding="utf-8")
                    if f"class {stem}" not in content:
                        pascal_violations.append(str(path.relative_to(ROOT_DIR)))
                except:
                    pass

    print(
        f"  Found {len(pascal_violations)} potential PascalCase violations (Files without matching Classes).",
    )
    if len(pascal_violations) > 0:
        with open(ROOT_DIR / "pascal_case_audit_log.txt", "w") as f:
            f.write("\n".join(pascal_violations))
        print("  -> Logged to pascal_case_audit_log.txt")

    # Final Verdict
    print("-" * 50)
    if errors:
        print(f"FAILED: Found {len(errors)} critical issues.")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("SUCCESS: No broken imports detected. Refactor integrity verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
