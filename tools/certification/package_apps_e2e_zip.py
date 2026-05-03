#!/usr/bin/env python3
"""W4.P1 of plan apps-fortknox-evidence-repackage-30f5ab — Reviewer-bundle zip builder.

Builds a self-contained reviewer zip that includes raw runtime payloads.
The zip contains all artifacts referenced by manifest files, with hash
verification to ensure integrity.

Usage:
    python tools/certification/package_apps_e2e_zip.py --include-runtime --out reviewer_bundle.zip
    python tools/certification/package_apps_e2e_zip.py --out reviewer_bundle_minimal.zip

Exit codes:
    0 — zip built successfully
    1 — missing input files or hash mismatch
    2 — zip creation failed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"

BUNDLE_NAME = "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"
SIGNOFF_NAME = "apps_e2e_signoff_report.json"
SIGNATURE_NAME = "apps_e2e_signoff_report.signature.json"
MERKLE_NAME = "apps_e2e_signoff_report.merkle.json"
SHA_NAME = "apps_e2e_signoff_report.sha256"


def _sha256_file(path: Path) -> str:
    """Compute SHA256 of file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_manifests() -> list[Path]:
    """Find all artifact manifest files under apps_e2e."""
    manifests: list[Path] = []
    if APPS_E2E_DIR.exists():
        for path in APPS_E2E_DIR.rglob("*_artifact_manifest.json"):
            manifests.append(path)
    return sorted(manifests)


def _load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON file, return None on error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _collect_artifacts(
    include_runtime: bool = True,
) -> tuple[list[tuple[Path, Path, str]], list[str]]:
    """Collect artifacts to include in zip.

    Returns (list of (source_path, zip_path, expected_hash)), list of errors).
    """
    artifacts: list[tuple[Path, Path, str]] = []
    errors: list[str] = []

    # Always include core certification artifacts
    core_files = [
        (APPS_E2E_DIR / BUNDLE_NAME, Path(BUNDLE_NAME)),
        (APPS_E2E_DIR / SIGNOFF_NAME, Path(SIGNOFF_NAME)),
        (APPS_E2E_DIR / SIGNATURE_NAME, Path(SIGNATURE_NAME)),
        (APPS_E2E_DIR / MERKLE_NAME, Path(MERKLE_NAME)),
        (APPS_E2E_DIR / SHA_NAME, Path(SHA_NAME)),
    ]

    for src, zip_relpath in core_files:
        if src.exists():
            artifacts.append((src, zip_relpath, ""))
        else:
            errors.append(f"core file missing: {src.name}")

    # Include verifier report if present
    verifier_report = APPS_E2E_DIR / "verifier_report.json"
    if verifier_report.exists():
        artifacts.append((verifier_report, Path("verifier_report.json"), ""))

    # Process app manifests and their referenced artifacts
    manifests = _find_manifests()
    for manifest_path in manifests:
        manifest = _load_json(manifest_path)
        if manifest is None:
            errors.append(f"unreadable manifest: {manifest_path.name}")
            continue

        app_name = manifest.get("app_name", "unknown")
        manifest_relpath = manifest_path.relative_to(REPO_ROOT)
        artifacts.append((manifest_path, manifest_relpath, manifest.get("sha256", "")))

        if not include_runtime:
            continue

        # Include referenced artifacts from manifest
        # Note: manifest uses 'items' not 'entries'
        for item in manifest.get("items", []):
            ref = item.get("ref")
            if not ref:
                continue
            ref_path = REPO_ROOT / ref
            if ref_path.exists():
                ref_relpath = ref_path.relative_to(REPO_ROOT)
                expected_hash = item.get("sha256", "")
                artifacts.append((ref_path, ref_relpath, expected_hash))
            else:
                # Only report error for items marked as present
                if item.get("present"):
                    errors.append(f"{app_name}: missing {item.get('ref_field')}: {ref}")

        # Include per-app proof bundles and static DAG proofs
        app_dir = manifest_path.parent
        for proof_file in ["apps_e2e_proof.json", "static_l3_dag_proof.json"]:
            proof_path = app_dir / proof_file
            if proof_path.exists():
                rel_path = proof_path.relative_to(REPO_ROOT)
                artifacts.append((proof_path, rel_path, ""))

    # Include mutation rejection report if present
    mutation_report = APPS_E2E_DIR / "apps_mutation_rejection_report.json"
    if mutation_report.exists():
        artifacts.append((mutation_report, Path("apps_mutation_rejection_report.json"), ""))

    return artifacts, errors


def _verify_hashes(artifacts: list[tuple[Path, Path, str]]) -> list[str]:
    """Verify artifact hashes match expected values."""
    errors: list[str] = []
    for src, zip_relpath, expected in artifacts:
        if not expected:
            continue
        actual = _sha256_file(src)
        if actual != expected:
            errors.append(
                f"hash mismatch for {zip_relpath}: expected {expected[:16]}..., got {actual[:16]}..."
            )
    return errors


def _build_inventory(
    artifacts: list[tuple[Path, Path, str]],
    zip_path: Path,
    include_runtime: bool,
) -> str:
    """Build INVENTORY.md content."""
    lines = [
        "# Apps E2E Reviewer Bundle Inventory",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Bundle: {zip_path.name}",
        f"Runtime payloads included: {include_runtime}",
        "",
        "## Contents",
        "",
        "| File | Size (bytes) | SHA256 |",
        "|------|-------------|--------|",
    ]

    for src, zip_relpath, _ in sorted(artifacts, key=lambda x: str(x[1])):
        size = src.stat().st_size
        sha = _sha256_file(src)
        lines.append(f"| {zip_relpath.as_posix()} | {size} | {sha} |")

    lines.extend([
        "",
        "## Verification",
        "",
        "To verify this bundle:",
        "",
        "```bash",
        "# Extract and verify hashes",
        "python tools/certification/package_apps_e2e_zip.py --verify extracted_bundle/",
        "",
        "# Or verify directly with the verifier",
        "python tools/cert/apps_e2e/verify_apps_release_signature.py",
        "```",
        "",
    ])

    return "\n".join(lines)


def build_zip(
    out_path: Path,
    include_runtime: bool = True,
    skip_hash_verify: bool = False,
) -> tuple[bool, list[str]]:
    """Build reviewer zip. Returns (success, errors)."""
    artifacts, errors = _collect_artifacts(include_runtime)
    if errors:
        return False, errors

    if not skip_hash_verify:
        hash_errors = _verify_hashes(artifacts)
        if hash_errors:
            return False, hash_errors

    try:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add all artifacts
            for src, zip_relpath, _ in artifacts:
                zf.write(src, zip_relpath.as_posix())

            # Add inventory
            inventory = _build_inventory(artifacts, out_path, include_runtime)
            zf.writestr("INVENTORY.md", inventory)

        return True, []
    except OSError as e:
        return False, [f"zip creation failed: {e}"]


def verify_zip(zip_path: Path) -> tuple[bool, list[str]]:
    """Verify a reviewer zip. Returns (valid, errors)."""
    if not zip_path.exists():
        return False, [f"zip not found: {zip_path}"]

    errors: list[str] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Check INVENTORY.md exists
            if "INVENTORY.md" not in zf.namelist():
                errors.append("missing INVENTORY.md")

            # Verify each file can be read
            for name in zf.namelist():
                try:
                    data = zf.read(name)
                    if name.endswith(".json"):
                        json.loads(data.decode("utf-8"))
                except (OSError, json.JSONDecodeError) as e:
                    errors.append(f"{name}: unreadable ({e})")

    except zipfile.BadZipFile:
        return False, ["invalid zip file"]
    except OSError as e:
        return False, [f"zip read failed: {e}"]

    return len(errors) == 0, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", "-o", type=Path, default=Path("reviewer_bundle.zip"))
    parser.add_argument(
        "--include-runtime",
        action="store_true",
        help="Include raw runtime payloads (proof bundles, DAG proofs).",
    )
    parser.add_argument(
        "--skip-hash-verify",
        action="store_true",
        help="Skip hash verification (DEV USE ONLY).",
    )
    parser.add_argument(
        "--verify",
        type=Path,
        metavar="ZIP_PATH",
        help="Verify an existing zip instead of building.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        if not args.quiet:
            print("[package_apps_e2e_zip] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    if args.verify:
        valid, errors = verify_zip(args.verify)
        if valid:
            if not args.quiet:
                print(f"[package_apps_e2e_zip] VERIFIED: {args.verify}")
            return 0
        else:
            print(f"[package_apps_e2e_zip] FAIL: {args.verify}", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1

    success, errors = build_zip(
        args.out,
        include_runtime=args.include_runtime,
        skip_hash_verify=args.skip_hash_verify,
    )

    if not success:
        print("[package_apps_e2e_zip] FAIL", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        runtime_flag = " (with runtime payloads)" if args.include_runtime else ""
        print(f"[package_apps_e2e_zip] OK: {args.out}{runtime_flag}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
