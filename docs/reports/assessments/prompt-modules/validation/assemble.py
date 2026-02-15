"""Deterministic prompt module assembler.

Reads modules.json, concatenates modules in strict order,
verifies SHA256 against manifest and canonical artifact.

Usage:
    python assemble.py          # Verify mode (CI-safe)
    python assemble.py --lock   # Lock mode (regenerate hashes, overwrite canonical)
"""

import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_MODULES_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROMPT_MODULES_DIR.parents[3]  # docs/reports/assessments/prompt-modules -> repo root
MANIFEST_PATH = PROMPT_MODULES_DIR / "modules.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(f"FAIL: Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def assemble_modules(manifest: dict) -> bytes:
    """Concatenate modules in strict order field ascending. Handle MODULE sentinels in canonical skeleton."""
    modules = sorted(manifest["modules"], key=lambda m: m["order"])

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
                    print(f"FAIL: MODULE sentinel references unknown module: {module_rel_path}")
                    sys.exit(1)
                module_path = REPO_ROOT / module_rel_path
                module_content = module_path.read_text(encoding="utf-8")
                assembled_lines.append(module_content)
                if not module_content.endswith("\n"):
                    assembled_lines.append("\n")
            else:
                assembled_lines.append(line)

        return "".join(assembled_lines).encode("utf-8")
    else:
        # Legacy mode: simple concatenation
        assembled = b""
        for module in modules:
            module_path = REPO_ROOT / module["path"]
            if not module_path.exists():
                print(f"FAIL: Module not found: {module['path']}")
                sys.exit(1)
            assembled += module_path.read_bytes()
        return assembled


def verify_mode(manifest: dict) -> int:
    """Verify assembled output matches manifest and canonical artifact."""
    canonical_path = REPO_ROOT / manifest["canonical_artifact_path"]
    if not canonical_path.exists():
        print(f"FAIL: Canonical artifact not found: {manifest['canonical_artifact_path']}")
        return 1

    errors = []

    # Verify individual module hashes
    modules = sorted(manifest["modules"], key=lambda m: m["order"])
    for module in modules:
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

    # Check if canonical skeleton mode and validate MODULE sentinels
    canonical_skeleton = None
    for module in modules:
        if module.get("classification") == "canonical-skeleton":
            canonical_skeleton = module
            break

    if canonical_skeleton:
        skeleton_path = REPO_ROOT / canonical_skeleton["path"]
        skeleton_content = skeleton_path.read_text(encoding="utf-8")

        # Find all MODULE sentinels
        referenced_modules = set()
        for line in skeleton_content.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("<!-- MODULE: ") and line_stripped.endswith(" -->"):
                module_rel_path = line_stripped[13:-4].strip()
                referenced_modules.add(module_rel_path)

        # Validate all referenced modules exist in manifest
        manifest_paths = {m["path"] for m in modules}
        for ref in referenced_modules:
            if ref not in manifest_paths:
                errors.append(f"MODULE sentinel references unknown module: {ref}")

        # Validate all non-main modules are referenced (except canonical-skeleton itself)
        expected_refs = {
            m["path"] for m in modules if m.get("classification") not in ("main", "canonical-skeleton")
        }
        unreferenced = expected_refs - referenced_modules
        if unreferenced:
            errors.append(f"Modules not referenced by any MODULE sentinel: {unreferenced}")

    # Assemble and verify
    assembled = assemble_modules(manifest)
    assembled_hash = sha256_bytes(assembled)

    if assembled_hash != manifest["assembled_sha256"]:
        errors.append(
            f"Assembled hash mismatch:\n"
            f"  manifest: {manifest['assembled_sha256']}\n"
            f"  actual:   {assembled_hash}"
        )

    # Verify against canonical artifact
    canonical_bytes = canonical_path.read_bytes()
    canonical_hash = sha256_bytes(canonical_bytes)

    if assembled != canonical_bytes:
        errors.append(
            f"Assembled output differs from canonical artifact\n"
            f"  canonical: {canonical_hash}\n"
            f"  assembled: {assembled_hash}"
        )

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print("OK: Assembly verified")
    print(f"  assembled_sha256: {assembled_hash}")
    print(f"  canonical_sha256: {canonical_hash}")
    print(f"  modules: {len(modules)}")
    return 0


def lock_mode(manifest: dict) -> int:
    """Regenerate hashes, overwrite modules.json and canonical artifact."""
    print("LOCK MODE: Regenerating hashes...")

    modules = sorted(manifest["modules"], key=lambda m: m["order"])

    # Recompute module hashes
    for module in modules:
        module_path = REPO_ROOT / module["path"]
        if not module_path.exists():
            print(f"FAIL: Module not found: {module['path']}")
            return 1
        module["sha256"] = sha256_file(module_path)
        print(f"  {module['path']}: {module['sha256']}")

    # Assemble and compute hash
    assembled = assemble_modules(manifest)
    assembled_hash = sha256_bytes(assembled)
    manifest["assembled_sha256"] = assembled_hash
    print(f"  assembled_sha256: {assembled_hash}")

    # Overwrite canonical artifact
    canonical_path = REPO_ROOT / manifest["canonical_artifact_path"]
    canonical_path.write_bytes(assembled)
    print(f"  Canonical artifact overwritten: {manifest['canonical_artifact_path']}")

    # Overwrite modules.json
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print("  modules.json updated")

    print("\nLOCK COMPLETE. Run 'git add' + commit to persist.")
    return 0


def main() -> int:
    manifest = load_manifest()
    if "--lock" in sys.argv:
        return lock_mode(manifest)
    else:
        return verify_mode(manifest)


if __name__ == "__main__":
    sys.exit(main())
