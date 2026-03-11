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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Since this is now in agentic_core, we need to find the prompt-modules directory
# relative to the repo root
REPO_ROOT = Path(__file__).resolve().parents[4]
PROMPT_MODULES_DIR = REPO_ROOT / "docs" / REPORTS_DIR / "assessments" / "prompt-modules"
MANIFEST_PATH = PROMPT_MODULES_DIR / "modules.json"

# Directories allowed to exist in prompt-modules/ without being in the manifest
ALLOWED_DIRS = {"validation", "schemas", "prompt-core", "target-state", "execution"}
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
    # Use the same assembly logic as assemble.py (handle MODULE sentinels)
    modules = sorted(manifest["modules"], key=lambda m: m["order"])
    assembly_ok = True

    # Check if canonical skeleton is present (last module)
    canonical_skeleton = None
    for module in modules:
        if module.get("classification") == "canonical-skeleton":
            canonical_skeleton = module
            break

    if canonical_skeleton:
        # Canonical skeleton mode: process sentinels
        skeleton_path = REPO_ROOT / canonical_skeleton["path"]
        skeleton_content = skeleton_path.read_text(encoding="utf-8")

        # Build module lookup by path
        module_lookup = {m["path"]: m for m in modules}

        # Replace MODULE sentinels
        lines = skeleton_content.splitlines(keepends=True)
        assembled_lines = []
        for line in lines:
            if line.strip().startswith("<!-- MODULE: ") and line.strip().endswith(" -->"):
                # Extract module path from sentinel
                module_rel_path = line.strip()[13:-4].strip()  # Remove <!-- MODULE: and -->
                if module_rel_path not in module_lookup:
                    errors.append(f"MODULE sentinel references unknown module: {module_rel_path}")
                    assembly_ok = False
                    break
                module_path = REPO_ROOT / module_rel_path
                module_content = module_path.read_text(encoding="utf-8")
                assembled_lines.append(module_content)
                if not module_content.endswith("\n"):
                    assembled_lines.append("\n")
            else:
                assembled_lines.append(line)

        assembled = "".join(assembled_lines).encode("utf-8") if assembly_ok else b""
    else:
        # Legacy mode: simple concatenation
        assembled = b""
        for module in modules:
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
