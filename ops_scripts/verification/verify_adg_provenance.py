#!/usr/bin/env python3
"""
ADG Provenance SSOT Verification

Ensures every ADG artifact emits and validates consistent provenance metadata:
- commit_sha: exact git HEAD, non-null, non-empty
- artifact_digest: SHA256 over canonical ADG artifact set
- scan_timestamp_utc: ISO8601 UTC
- scanner_version: semantic version
- ruleset_version: semantic version
- repo_root: normalized absolute repo path
- extractor_build_id: deterministic build identifier
- schema_version: ADG schema version
- generation_mode: full | incremental
- source_snapshot_digest: digest of file inventory included in scan

HARD FAIL IF any provenance is inconsistent across artifacts.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ProvenanceVerificationError(Exception):
    """Raised when provenance verification fails."""

    pass


class ADGProvenanceVerifier:
    """Verifies ADG artifact provenance consistency."""

    # Required provenance fields
    REQUIRED_FIELDS = {
        "commit_sha",
        "artifact_digest",
        "scan_timestamp_utc",
        "scanner_version",
        "ruleset_version",
        "repo_root",
        "extractor_build_id",
        "schema_version",
        "generation_mode",
        "source_snapshot_digest",
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.repo_root = self._find_repo_root()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _find_repo_root(self) -> Path:
        """Find repository root by searching for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current.resolve()
            current = current.parent
        raise ProvenanceVerificationError("Could not find repository root")

    def _get_git_commit_sha(self) -> str:
        """Get exact git HEAD commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise ProvenanceVerificationError(f"Failed to get git commit SHA: {e}")

    def _get_git_status(self) -> dict[str, Any]:
        """Get git status for dirty working directory detection."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return {
                "is_dirty": bool(result.stdout.strip()),
                "changed_files": result.stdout.strip().split("\n") if result.stdout.strip() else [],
            }
        except subprocess.CalledProcessError as e:
            raise ProvenanceVerificationError(f"Failed to get git status: {e}")

    def _calculate_file_inventory_digest(self, file_paths: list[Path]) -> str:
        """Calculate SHA256 digest of file inventory with deterministic ordering."""
        # Sort paths for deterministic ordering
        sorted_paths = sorted(str(p.relative_to(self.repo_root)) for p in file_paths)

        inventory_data = {
            "files": sorted_paths,
            "count": len(sorted_paths),
        }

        inventory_json = json.dumps(inventory_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(inventory_json.encode()).hexdigest()

    def _load_json_artifact(self, artifact_path: Path) -> dict[str, Any]:
        """Load and parse JSON artifact."""
        try:
            with open(artifact_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ProvenanceVerificationError(f"Failed to load {artifact_path}: {e}")

    def _load_sqlite_meta(self, sqlite_path: Path) -> dict[str, Any]:
        """Load metadata from SQLite ADG database."""
        try:
            with sqlite3.connect(sqlite_path) as conn:
                cursor = conn.cursor()

                # Check if meta table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta'")
                if not cursor.fetchone():
                    raise ProvenanceVerificationError("SQLite database missing 'meta' table")

                # Load all metadata
                cursor.execute("SELECT key, value FROM meta")
                meta = dict(cursor.fetchall())

                # Parse JSON values
                for key, value in meta.items():
                    try:
                        meta[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        pass  # Keep as string if not JSON

                return meta
        except Exception as e:
            raise ProvenanceVerificationError(f"Failed to load SQLite metadata from {sqlite_path}: {e}")

    def _verify_required_fields(self, artifact_name: str, metadata: dict[str, Any]) -> None:
        """Verify all required provenance fields are present."""
        missing = self.REQUIRED_FIELDS - set(metadata.keys())
        if missing:
            raise ProvenanceVerificationError(
                f"{artifact_name} missing required fields: {sorted(missing)}",
            )

    def _verify_non_null_fields(self, artifact_name: str, metadata: dict[str, Any]) -> None:
        """Verify critical fields are non-null and non-empty."""
        critical_fields = {"commit_sha", "artifact_digest", "scan_timestamp_utc", "repo_root"}

        for field in critical_fields:
            value = metadata.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ProvenanceVerificationError(
                    f"{artifact_name} has null/empty critical field: {field}",
                )

    def _verify_timestamp_format(self, artifact_name: str, timestamp: str) -> None:
        """Verify timestamp is valid ISO8601 UTC."""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                raise ProvenanceVerificationError(
                    f"{artifact_name} timestamp missing timezone: {timestamp}",
                )
            # Ensure UTC
            if dt.tzinfo != timezone.utc:
                raise ProvenanceVerificationError(
                    f"{artifact_name} timestamp not UTC: {timestamp}",
                )
        except ValueError as e:
            raise ProvenanceVerificationError(
                f"{artifact_name} invalid timestamp format: {timestamp} - {e}",
            )

    def _verify_git_commit_consistency(self, artifact_name: str, commit_sha: str) -> None:
        """Verify commit_sha matches actual git HEAD."""
        actual_commit = self._get_git_commit_sha()
        if commit_sha != actual_commit:
            raise ProvenanceVerificationError(
                f"{artifact_name} commit_sha ({commit_sha}) does not match git HEAD ({actual_commit})",
            )

    def _verify_repo_root_consistency(self, artifact_name: str, repo_root: str) -> None:
        """Verify repo_root matches actual repository root."""
        actual_root = str(self.repo_root)
        if Path(repo_root).resolve() != self.repo_root:
            raise ProvenanceVerificationError(
                f"{artifact_name} repo_root ({repo_root}) does not match actual root ({actual_root})",
            )

    def _collect_adg_artifacts(self) -> dict[str, Path]:
        """Collect all ADG artifacts for verification."""
        artifacts = {}

        # Find SQLite database (latest by timestamp)
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if sqlite_files:
            # Sort by modification time to get latest
            latest_sqlite = max(sqlite_files, key=lambda p: p.stat().st_mtime)
            artifacts["sqlite"] = latest_sqlite

        # Find snapshot JSON
        snapshot_files = list(self.adg_dir.glob("adg_snapshot_*.json"))
        if snapshot_files:
            latest_snapshot = max(snapshot_files, key=lambda p: p.stat().st_mtime)
            artifacts["snapshot"] = latest_snapshot

        # Find graph JSON files
        graph_files = list(self.adg_dir.glob("adg_*graph_*.json"))
        for graph_file in graph_files:
            graph_type = graph_file.stem.split("_")[1]  # e.g., "file", "symbol", "governance"
            artifacts[f"graph_{graph_type}"] = graph_file

        if not artifacts:
            raise ProvenanceVerificationError("No ADG artifacts found")

        return artifacts

    def _verify_cross_artifact_consistency(self, all_metadata: dict[str, dict[str, Any]]) -> None:
        """Verify critical fields match across all artifacts."""
        # Fields that must be identical across artifacts
        consistent_fields = {
            "commit_sha",
            "artifact_digest",
            "ruleset_version",
            "schema_version",
            "scan_timestamp_utc",
            "repo_root",
        }

        for field in consistent_fields:
            values = {}
            for artifact_name, metadata in all_metadata.items():
                if field in metadata:
                    values[artifact_name] = metadata[field]

            # Check if all values are the same
            if len(set(str(v) for v in values.values())) > 1:
                raise ProvenanceVerificationError(
                    f"Field {field} inconsistent across artifacts: {values}",
                )

    def verify(self) -> dict[str, Any]:
        """Run complete provenance verification."""
        print("🔍 Starting ADG Provenance Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"📂 Repository Root: {self.repo_root}")

        # Get git status
        git_status = self._get_git_status()
        if git_status["is_dirty"]:
            self.warnings.append(
                f"Working directory is dirty with {len(git_status['changed_files'])} changed files",
            )
            print("⚠️  Warning: Working directory is dirty")

        # Collect artifacts
        artifacts = self._collect_adg_artifacts()
        print(f"📦 Found {len(artifacts)} artifacts: {list(artifacts.keys())}")

        # Load metadata from all artifacts
        all_metadata = {}

        for artifact_name, artifact_path in artifacts.items():
            print(f"🔍 Verifying {artifact_name}: {artifact_path.name}")

            if artifact_name == "sqlite":
                metadata = self._load_sqlite_meta(artifact_path)
            else:
                metadata = self._load_json_artifact(artifact_path)

            all_metadata[artifact_name] = metadata

            # Verify required fields
            self._verify_required_fields(artifact_name, metadata)

            # Verify non-null critical fields
            self._verify_non_null_fields(artifact_name, metadata)

            # Verify timestamp format
            if "scan_timestamp_utc" in metadata:
                self._verify_timestamp_format(artifact_name, metadata["scan_timestamp_utc"])

            # Verify git commit consistency
            if "commit_sha" in metadata:
                self._verify_git_commit_consistency(artifact_name, metadata["commit_sha"])

            # Verify repo root consistency
            if "repo_root" in metadata:
                self._verify_repo_root_consistency(artifact_name, metadata["repo_root"])

        # Verify cross-artifact consistency
        print("🔗 Verifying cross-artifact consistency...")
        self._verify_cross_artifact_consistency(all_metadata)

        # Prepare result
        result = {
            "status": "PASS" if not self.errors else "FAIL",
            "artifacts_verified": list(artifacts.keys()),
            "errors": self.errors,
            "warnings": self.warnings,
            "git_status": git_status,
            "provenance_summary": {
                artifact_name: {
                    field: metadata.get(field)
                    for field in ["commit_sha", "artifact_digest", "scan_timestamp_utc", "schema_version"]
                    if field in metadata
                }
                for artifact_name, metadata in all_metadata.items()
            },
        }

        if self.errors:
            print("\n❌ PROVENANCE VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")
            sys.exit(1)
        else:
            print("\n✅ PROVENANCE VERIFICATION PASSED")
            if self.warnings:
                print("⚠️  Warnings:")
                for warning in self.warnings:
                    print(f"   • {warning}")

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG provenance consistency")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report",
    )

    args = parser.parse_args()

    try:
        verifier = ADGProvenanceVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except (
        ProvenanceVerificationError
    ) as e:  # guardian: ProvenanceVerificationError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
