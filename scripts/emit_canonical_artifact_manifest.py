#!/usr/bin/env python3
"""
ADG Canonical Artifact Manifest Generator

Emits a deterministic manifest of all ADG artifacts with:
- Exact file inventory with content hashes
- Deterministic ordering for reproducible digests
- Cross-artifact reference validation
- Source snapshot digest generation
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class ArtifactManifestGenerator:
    """Generates canonical ADG artifact manifests."""
    
    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.repo_root = self._find_repo_root()
        
    def _find_repo_root(self) -> Path:
        """Find repository root by searching for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current.resolve()
            current = current.parent
        raise RuntimeError("Could not find repository root")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file contents."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _scan_source_files(self) -> List[Dict[str, Any]]:
        """Scan all source files included in ADG analysis."""
        source_files = []
        
        # Define source file extensions and patterns
        source_extensions = {'.py', '.json', '.yaml', '.yml', '.md', '.txt', '.cfg', '.ini', '.toml'}
        exclude_patterns = {
            '__pycache__',
            '.git',
            '.pytest_cache',
            '.coverage',
            '.mypy_cache',
            'node_modules',
            '.venv',
            'venv',
            'env',
            '.DS_Store',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.tox'
        }
        
        for file_path in self.repo_root.rglob('*'):
            # Skip directories and excluded patterns
            if not file_path.is_file():
                continue
                
            # Skip if matches exclude patterns
            if any(pattern in file_path.parts for pattern in exclude_patterns):
                continue
                
            # Skip if no source extension
            if file_path.suffix.lower() not in source_extensions:
                continue
            
            # Calculate relative path and hash
            rel_path = str(file_path.relative_to(self.repo_root))
            file_hash = self._calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
            file_mtime = file_path.stat().st_mtime
            
            source_files.append({
                "path": rel_path,
                "hash": file_hash,
                "size": file_size,
                "mtime": file_mtime
            })
        
        # Sort for deterministic ordering
        source_files.sort(key=lambda x: x["path"])
        return source_files
    
    def _calculate_source_snapshot_digest(self, source_files: List[Dict[str, Any]]) -> str:
        """Calculate digest of source file inventory."""
        snapshot_data = {
            "files": [
                {
                    "path": f["path"],
                    "hash": f["hash"]
                }
                for f in source_files
            ],
            "count": len(source_files),
            "total_size": sum(f["size"] for f in source_files)
        }
        
        snapshot_json = json.dumps(snapshot_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(snapshot_json.encode()).hexdigest()
    
    def _scan_adg_artifacts(self) -> List[Dict[str, Any]]:
        """Scan all ADG artifacts and calculate their hashes."""
        artifacts = []
        
        if not self.adg_dir.exists():
            return artifacts
        
        for artifact_path in self.adg_dir.rglob('*'):
            if not artifact_path.is_file():
                continue
            
            # Skip temporary files and cache files
            if artifact_path.name.endswith('.tmp') or artifact_path.name.startswith('.'):
                continue
            
            rel_path = str(artifact_path.relative_to(self.adg_dir))
            file_hash = self._calculate_file_hash(artifact_path)
            file_size = artifact_path.stat().st_size
            file_mtime = artifact_path.stat().st_mtime
            
            artifacts.append({
                "path": rel_path,
                "hash": file_hash,
                "size": file_size,
                "mtime": file_mtime,
                "type": self._classify_artifact_type(artifact_path)
            })
        
        # Sort for deterministic ordering
        artifacts.sort(key=lambda x: x["path"])
        return artifacts
    
    def _classify_artifact_type(self, artifact_path: Path) -> str:
        """Classify artifact type based on filename."""
        name = artifact_path.name
        
        if name.startswith("adg_indexed_") and name.endswith(".sqlite"):
            return "sqlite_database"
        elif name.startswith("adg_snapshot_") and name.endswith(".json"):
            return "snapshot"
        elif name.startswith("adg_") and "_graph_" in name and name.endswith(".json"):
            return "graph"
        elif name.startswith("adg_run_") and name.endswith(".zip"):
            return "archive"
        elif name == "scan_result_cache.json":
            return "cache"
        elif name.endswith(".json"):
            return "json_metadata"
        elif name.endswith(".sqlite"):
            return "sqlite_auxiliary"
        else:
            return "other"
    
    def _calculate_artifact_set_digest(self, artifacts: List[Dict[str, Any]]) -> str:
        """Calculate digest of the complete artifact set."""
        # Only include core artifacts in the digest (exclude cache, temporary files)
        core_artifacts = [
            artifact for artifact in artifacts
            if artifact["type"] in ["sqlite_database", "snapshot", "graph", "archive"]
        ]
        
        artifact_data = {
            "artifacts": [
                {
                    "path": a["path"],
                    "hash": a["hash"],
                    "type": a["type"]
                }
                for a in core_artifacts
            ],
            "count": len(core_artifacts)
        }
        
        artifact_json = json.dumps(artifact_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(artifact_json.encode()).hexdigest()
    
    def _validate_cross_references(self, source_files: List[Dict[str, Any]], artifacts: List[Dict[str, Any]]) -> List[str]:
        """Validate cross-references between source and artifacts."""
        validation_issues = []
        
        # Check if SQLite database exists
        sqlite_dbs = [a for a in artifacts if a["type"] == "sqlite_database"]
        if not sqlite_dbs:
            validation_issues.append("No SQLite database found")
        
        # Check if snapshot exists
        snapshots = [a for a in artifacts if a["type"] == "snapshot"]
        if not snapshots:
            validation_issues.append("No snapshot file found")
        
        # Check for expected graph types
        graph_types = {a["path"].split("_")[1] for a in artifacts if a["type"] == "graph"}
        expected_graphs = {"file", "symbol", "governance"}
        missing_graphs = expected_graphs - graph_types
        if missing_graphs:
            validation_issues.append(f"Missing graph types: {sorted(missing_graphs)}")
        
        return validation_issues
    
    def generate_manifest(self) -> Dict[str, Any]:
        """Generate complete canonical manifest."""
        print("🔍 Generating ADG Canonical Artifact Manifest...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"📂 Repository Root: {self.repo_root}")
        
        # Scan source files
        print("📋 Scanning source files...")
        source_files = self._scan_source_files()
        source_snapshot_digest = self._calculate_source_snapshot_digest(source_files)
        
        print(f"   Found {len(source_files)} source files")
        print(f"   Source snapshot digest: {source_snapshot_digest}")
        
        # Scan ADG artifacts
        print("📦 Scanning ADG artifacts...")
        artifacts = self._scan_adg_artifacts()
        artifact_set_digest = self._calculate_artifact_set_digest(artifacts)
        
        print(f"   Found {len(artifacts)} artifacts")
        print(f"   Artifact set digest: {artifact_set_digest}")
        
        # Validate cross-references
        print("🔗 Validating cross-references...")
        validation_issues = self._validate_cross_references(source_files, artifacts)
        
        if validation_issues:
            print("⚠️  Validation issues found:")
            for issue in validation_issues:
                print(f"   • {issue}")
        
        # Build manifest
        manifest = {
            "manifest_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator_version": "1.0.0",
                "repo_root": str(self.repo_root),
                "adg_directory": str(self.adg_dir)
            },
            "source_snapshot": {
                "digest": source_snapshot_digest,
                "file_count": len(source_files),
                "total_size": sum(f["size"] for f in source_files),
                "files": source_files
            },
            "artifact_set": {
                "digest": artifact_set_digest,
                "artifact_count": len(artifacts),
                "total_size": sum(a["size"] for a in artifacts),
                "artifacts": artifacts
            },
            "validation": {
                "issues": validation_issues,
                "status": "PASS" if not validation_issues else "WARNING"
            },
            "canonical_digests": {
                "source_snapshot_digest": source_snapshot_digest,
                "artifact_set_digest": artifact_set_digest,
                "combined_digest": hashlib.sha256(
                    f"{source_snapshot_digest}{artifact_set_digest}".encode()
                ).hexdigest()
            }
        }
        
        return manifest
    
    def save_manifest(self, manifest: Dict[str, Any], output_path: Path) -> None:
        """Save manifest to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        
        print(f"📄 Manifest saved to: {output_path}")
        print(f"🔐 Combined digest: {manifest['canonical_digests']['combined_digest']}")

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ADG canonical artifact manifest")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/adg/canonical_manifest.json"),
        help="Path to save manifest"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't save manifest"
    )
    
    args = parser.parse_args()
    
    try:
        generator = ArtifactManifestGenerator(args.adg_dir)
        manifest = generator.generate_manifest()
        
        if not args.validate_only:
            generator.save_manifest(manifest, args.output)
        
        # Return appropriate exit code
        if manifest["validation"]["status"] == "PASS":
            print("✅ Manifest generation completed successfully")
            return 0
        else:
            print("⚠️  Manifest generation completed with warnings")
            return 0
        
    except Exception as e:
        print(f"💥 Failed to generate manifest: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
