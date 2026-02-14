"""Validate prompt module assembly integrity.

Checks:
- canonical_artifact_path exists
- All modules listed exist
- No duplicate order values
- Orders form contiguous sequence starting at 0
- Module sha256 matches file contents
- Assembled sha256 matches manifest
- Assembled output matches canonical artifact byte-for-byte
- No files in prompt-modules/ outside manifest except validation/ and schemas/

Hard FAIL on any violation. Exit code 1 on failure, 0 on success.
"""

import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_MODULES_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROMPT_MODULES_DIR.parents[3]  # docs/reports/assessments/prompt-modules -> repo root
MANIFEST_PATH = PROMPT_MODULES_DIR / "modules.json"

# Directories allowed to exist in prompt-modules/ without being in the manifest
ALLOWED_DIRS = {"validation", "schemas"}
# Files allowed at prompt-modules/ root without being in the manifest
ALLOWED_ROOT_FILES = {"modules.json"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print("FAIL: modules.json not found")
        sys.exit(1)
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate() -> int:
    errors = []
    manifest = load_manifest()

    # --- Check canonical_artifact_path ---
    canonical_rel = manifest.get("canonical_artifact_path")
    if not canonical_rel:
        errors.append("canonical_artifact_path missing from manifest")
    else:
        canonical_path = REPO_ROOT / canonical_rel
        if not canonical_path.exists():
            errors.append(f"Canonical artifact not found: {canonical_rel}")

    # --- Check modules list ---
    modules = manifest.get("modules", [])
    if not modules:
        errors.append("No modules listed in manifest")

    # --- Check no duplicate order values ---
    orders = [m["order"] for m in modules]
    if len(orders) != len(set(orders)):
        errors.append(f"Duplicate order values: {orders}")

    # --- Check orders form contiguous sequence starting at 0 ---
    sorted_orders = sorted(orders)
    expected_orders = list(range(len(modules)))
    if sorted_orders != expected_orders:
        errors.append(f"Orders not contiguous from 0: expected {expected_orders}, got {sorted_orders}")

    # --- Check all modules exist and verify sha256 ---
    sorted_modules = sorted(modules, key=lambda m: m["order"])
    for module in sorted_modules:
        module_path = REPO_ROOT / module["path"]
        if not module_path.exists():
            errors.append(f"Module not found: {module['path']}")
            continue
        actual_hash = sha256_file(module_path)
        if actual_hash != module["sha256"]:
            errors.append(
                f"Module hash mismatch: {module['path']}\n"
                f"  manifest: {module['sha256']}\n"
                f"  actual:   {actual_hash}"
            )

    # --- Assemble and verify assembled_sha256 ---
    assembled = b""
    assembly_ok = True
    for module in sorted_modules:
        module_path = REPO_ROOT / module["path"]
        if not module_path.exists():
            assembly_ok = False
            break
        assembled += module_path.read_bytes()

    if assembly_ok:
        assembled_hash = sha256_bytes(assembled)
        manifest_assembled_hash = manifest.get("assembled_sha256", "")

        if assembled_hash != manifest_assembled_hash:
            errors.append(
                f"Assembled hash mismatch:\n"
                f"  manifest: {manifest_assembled_hash}\n"
                f"  actual:   {assembled_hash}"
            )

        # --- Verify assembled output matches canonical artifact byte-for-byte ---
        if canonical_rel:
            canonical_path = REPO_ROOT / canonical_rel
            if canonical_path.exists():
                canonical_bytes = canonical_path.read_bytes()
                if assembled != canonical_bytes:
                    canonical_hash = sha256_bytes(canonical_bytes)
                    errors.append(
                        f"Assembled output differs from canonical artifact\n"
                        f"  canonical: {canonical_hash}\n"
                        f"  assembled: {assembled_hash}"
                    )

    # --- Check no unexpected files in prompt-modules/ ---
    manifest_paths = {m["path"] for m in modules}
    for item in PROMPT_MODULES_DIR.iterdir():
        if item.is_dir():
            if item.name not in ALLOWED_DIRS:
                errors.append(f"Unexpected directory in prompt-modules/: {item.name}")
        elif item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                # Check if this file's repo-relative path is in the manifest
                rel_path = item.relative_to(REPO_ROOT).as_posix()
                if rel_path not in manifest_paths:
                    errors.append(f"Unexpected file in prompt-modules/: {item.name}")

    # --- Report ---
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s)\n")
        for i, e in enumerate(errors, 1):
            print(f"  [{i}] {e}")
        return 1

    print("VALIDATION PASSED")
    print(f"  canonical_artifact: {canonical_rel}")
    print(f"  assembled_sha256:   {manifest.get('assembled_sha256', 'N/A')}")
    print(f"  modules:            {len(modules)}")
    for m in sorted_modules:
        print(f"    [{m['order']}] {m['path']} ({m['classification']})")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
