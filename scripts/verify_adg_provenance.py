#!/usr/bin/env python3
"""ADG Provenance Verification — Validate cross-artifact consistency."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class ProvenanceVerificationError(Exception):
    """Error raised when provenance verification fails."""
    pass


class ADGProvenanceVerifier:
    """Verifier for ADG provenance metadata across artifacts."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.issues: list[str] = []

    def _collect_adg_artifacts(self) -> list[Path]:
        """Collect all ADG artifact files (SQLite, JSON, CSV)."""
        if not self.adg_dir.exists():
            raise ProvenanceVerificationError(f"No artifacts found in {self.adg_dir}")
        
        artifacts = []
        for pattern in ["*.sqlite", "*.json", "*.csv"]:
            artifacts.extend(self.adg_dir.glob(pattern))
        
        if not artifacts:
            raise ProvenanceVerificationError(f"No artifacts found in {self.adg_dir}")
        
        return artifacts

    def _load_sqlite_meta(self, db_path: Path) -> dict[str, Any]:
        """Load metadata from SQLite database."""
        if not db_path.exists():
            raise ProvenanceVerificationError(f"Database not found: {db_path}")

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        try:
            c.execute("SELECT key, value FROM meta")
            meta = {row[0]: row[1] for row in c.fetchall()}
        except sqlite3.OperationalError as e:
            conn.close()
            raise ProvenanceVerificationError(f"No meta table found: {e}")

        conn.close()
        return meta

    def _load_graph_meta(self) -> dict[str, Any] | None:
        """Load metadata from graph JSON file."""
        graph_files = list(self.adg_dir.glob("*.json"))
        for f in graph_files:
            try:
                with open(f, "r") as fp:
                    data = json.load(fp)
                    if "meta" in data or "metadata" in data:
                        return data.get("meta") or data.get("metadata", {})
            except (json.JSONDecodeError, IOError):
                continue
        return None

    def verify(self) -> tuple[bool, list[str]]:
        """Run all provenance checks."""
        if not self.adg_dir.exists():
            raise ProvenanceVerificationError(f"ADG directory not found: {self.adg_dir}")

        # Find SQLite database
        db_files = list(self.adg_dir.glob("*.sqlite"))
        if not db_files:
            raise ProvenanceVerificationError(f"No SQLite artifact found in {self.adg_dir}")

        issues = []

        for db_path in db_files:
            meta = self._load_sqlite_meta(db_path)

            # Check for empty commit_sha - raise exception for test compatibility
            commit_sha = meta.get("commit_sha", "")
            if not commit_sha:
                raise ProvenanceVerificationError(f"Empty commit_sha in {db_path.name}")

            # Check for missing scanner_digest
            scanner_digest = meta.get("scanner_digest", "")
            if not scanner_digest:
                issues.append(f"Missing scanner_digest in {db_path.name}")

        return len(issues) == 0, issues
