#!/usr/bin/env python3
"""W6 — Proof Bundle Assembler (RTC-REQ-126).

Assembles zip/tar of all certification evidence.
Per plan: Certification reports + closeout docs.

Exit codes:
  0 — BUNDLE_ASSEMBLED
  1 — EVIDENCE_MISSING (no evidence to bundle)
  2 — MERKLE_MISSING (merkle tree required)

W6 implementation per runtime-cert-hardened-w0-deferred-scope.md
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
MERKLE_TREE_PATH = Path(os.environ.get("MERKLE_TREE_PATH", "artifacts/certification/merkle_tree.json"))
MERKLE_ROOT_PATH = Path(os.environ.get("MERKLE_ROOT_PATH", "artifacts/certification/merkle_root.txt"))
EVIDENCE_DIR = Path(os.environ.get("EVIDENCE_DIR", "artifacts/certification/evidence"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "artifacts/certification/bundles"))


def load_merkle_root() -> str:
    """Load merkle root hash."""
    if not MERKLE_ROOT_PATH.exists():
        return "UNKNOWN"
    
    try:
        with open(MERKLE_ROOT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except IOError:
        return "UNKNOWN"


def gather_evidence_files() -> list[Path]:
    """Gather all evidence files to bundle."""
    files = []
    
    # Merkle tree
    if MERKLE_TREE_PATH.exists():
        files.append(MERKLE_TREE_PATH)
    
    # Merkle root
    if MERKLE_ROOT_PATH.exists():
        files.append(MERKLE_ROOT_PATH)
    
    # Evidence artifacts
    if EVIDENCE_DIR.exists():
        for file_path in EVIDENCE_DIR.glob("*.json"):
            files.append(file_path)
    
    return files


def compute_bundle_hash(file_paths: list[Path]) -> str:
    """Compute aggregate hash of all bundled files."""
    hasher = hashlib.sha256()
    
    for file_path in sorted(file_paths):
        try:
            with open(file_path, "rb") as f:
                hasher.update(f.read())
        except IOError:
            continue
    
    return hasher.hexdigest()


def create_zip_bundle(file_paths: list[Path], output_path: Path, merkle_root: str) -> bool:
    """Create zip bundle of all evidence."""
    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add manifest
            manifest = {
                "bundle_type": "zip",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "merkle_root": merkle_root,
                "file_count": len(file_paths),
                "files": [
                    str(f.relative_to(Path.cwd())) if f.is_relative_to(Path.cwd()) else str(f)
                    for f in file_paths
                ],
            }
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # Add all files
            for file_path in file_paths:
                try:
                    arcname = str(file_path.relative_to(Path.cwd()))
                except ValueError:
                    # File not under cwd, use just the filename
                    arcname = file_path.name
                zf.write(file_path, arcname)
        
        return True
    except (IOError, OSError):
        return False


def create_tar_bundle(file_paths: list[Path], output_path: Path, merkle_root: str) -> bool:
    """Create tar.gz bundle of all evidence."""
    try:
        with tarfile.open(output_path, "w:gz") as tf:
            # Add manifest as string
            manifest = {
                "bundle_type": "tar.gz",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "merkle_root": merkle_root,
                "file_count": len(file_paths),
                "files": [
                    str(f.relative_to(Path.cwd())) if f.is_relative_to(Path.cwd()) else str(f)
                    for f in file_paths
                ],
            }
            manifest_data = json.dumps(manifest, indent=2).encode("utf-8")
            
            import io
            manifest_bytes = io.BytesIO(manifest_data)
            manifest_info = tarfile.TarInfo(name="manifest.json")
            manifest_info.size = len(manifest_data)
            tf.addfile(manifest_info, manifest_bytes)
            
            # Add all files
            for file_path in file_paths:
                tf.add(file_path, arcname=str(file_path.relative_to(Path.cwd())))
        
        return True
    except (IOError, OSError):
        return False


def assemble_bundle() -> tuple[bool, dict[str, Any]]:
    """Assemble proof bundle.
    
    Returns: (success, info)
    """
    # Check merkle exists
    if not MERKLE_TREE_PATH.exists():
        return False, {"error": "MERKLE_MISSING", "path": str(MERKLE_TREE_PATH)}
    
    # Gather evidence
    file_paths = gather_evidence_files()
    
    if len(file_paths) < 2:
        return False, {
            "error": "EVIDENCE_INSUFFICIENT",
            "found": len(file_paths),
            "required": 2,
        }
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get merkle root
    merkle_root = load_merkle_root()
    
    # Generate timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Create zip bundle
    zip_path = OUTPUT_DIR / f"certification_proof_bundle_{timestamp}.zip"
    zip_success = create_zip_bundle(file_paths, zip_path, merkle_root)
    
    # Create tar bundle
    tar_path = OUTPUT_DIR / f"certification_proof_bundle_{timestamp}.tar.gz"
    tar_success = create_tar_bundle(file_paths, tar_path, merkle_root)
    
    # Compute bundle hash
    bundle_hash = compute_bundle_hash(file_paths)
    
    return True, {
        "status": "BUNDLE_ASSEMBLED",
        "zip_path": str(zip_path) if zip_success else None,
        "tar_path": str(tar_path) if tar_success else None,
        "file_count": len(file_paths),
        "bundle_hash": bundle_hash[:16] + "...",
        "merkle_root": merkle_root[:16] + "...",
    }


def emit_attestation(result: dict[str, Any]) -> None:
    """Emit attestation record."""
    attestation_path = OUTPUT_DIR / "bundle_attestation.json"
    
    attestation = {
        "attestation": "proof_bundle",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "result": result,
    }
    
    with open(attestation_path, "w", encoding="utf-8") as f:
        json.dump(attestation, f, indent=2)
    
    print(f"Attestation written to: {attestation_path}")


def main() -> int:
    """Main entry point."""
    success, info = assemble_bundle()
    
    if not success:
        error = info.get("error", "UNKNOWN_ERROR")
        
        if error == "MERKLE_MISSING":
            print(f"ERROR: Merkle tree not found at {info.get('path', MERKLE_TREE_PATH)}")
            return 2
        
        elif error == "EVIDENCE_INSUFFICIENT":
            print(f"ERROR: Insufficient evidence ({info.get('found', 0)} files found, {info.get('required', 2)} required)")
            return 1
        
        else:
            print(f"ERROR: {error}")
            return 3
    
    # Success
    emit_attestation(info)
    
    print("PROOF BUNDLE ASSEMBLED")
    
    zip_path = info.get("zip_path")
    if zip_path:
        print(f"  ZIP: {zip_path}")
    
    tar_path = info.get("tar_path")
    if tar_path:
        print(f"  TAR: {tar_path}")
    
    print(f"  Files: {info.get('file_count', 'N/A')}")
    print(f"  Bundle hash: {info.get('bundle_hash', 'N/A')}")
    print(f"  Merkle root: {info.get('merkle_root', 'N/A')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
