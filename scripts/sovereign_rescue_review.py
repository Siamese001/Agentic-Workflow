#!/usr/bin/env python3
"""
Sovereign Rescue & Review (SRR) — Eternal Archive Purity Enforcer
Reviews files in archives/depth_violations (and other archives).
Verdict:
  - REDUNDANT → auto-purge (hash match in active canon)
  - UNIQUE → semantic rescue suggestion via Pinecone hybrid search
  - FINAL → archive left empty — sovereignty pure
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from agentic_core.L4_state.vector.pinecone_sovereign_agent import PineconeSovereignAgent

class RescueReviewer:
    """
    Sovereign judge of archived files — eternal purity through hash + semantics.
    """
    def __init__(self, project_root: Path):
        self.root = project_root
        self.archive_path = project_root / "archives/depth_violations"
        self.active_hashes = self._map_active_canon()
        # [SOVEREIGN BRAIN] Link to the vector gateway
        self.pinecone = PineconeSovereignAgent(project_root)

    def _map_active_canon(self) -> Dict[str, str]:
        """Map every active .py file hash to its current path"""
        hash_map = {}
        targets = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "tests"]
        for folder in targets:
            path = self.root / folder
            if not path.exists():
                continue
            for py_file in path.rglob("*.py"):
                try:
                    f_hash = hashlib.sha256(py_file.read_bytes()).hexdigest()
                    rel_path = str(py_file.relative_to(self.root))
                    hash_map[f_hash] = rel_path
                except:
                    pass
        print(f"   [OK] SRR: Mapped {len(hash_map)} active files for deduplication")
        return hash_map

    def review_and_heal(self):
        """Full sovereign review — dedupe + semantic rescue"""
        print(f"\n--- SOVEREIGN ARCHIVE REVIEW ---")
        for arch_file in self.archive_path.rglob("*.py"):
            rel = arch_file.relative_to(self.archive_path)
            content = arch_file.read_text(encoding="utf-8", errors="ignore")
            f_hash = hashlib.sha256(content.encode()).hexdigest()

            if f_hash in self.active_hashes:
                print(f"[PURGE] {rel} -> REDUNDANT (Exists at: {self.active_hashes[f_hash]})")
                arch_file.unlink() # Purge the duplicate
                continue
            
            # [RESCUE MISSION] Unique file found
            print(f"[RESCUE] {rel} -> UNIQUE logic detected.")
            
            # Hybrid search for the "True Home"
            results = self.pinecone.hybrid_search(
                query=content[:5000], # First 5k chars usually have the signal
                top_k=3
            )
            
            if results and results[0]['score'] > 0.82:
                best = results[0]['metadata']
                conf = results[0]['score']
                print(f"         BEST TARGET: {best['territory']} (Confidence: {conf:.2f})")
                print(f"         Path Suggestion: {best['territory']}/{arch_file.name}")
            else:
                print(f"         VERDICT: Unknown logic. Manual review required.")

    def final_lockdown(self):
        """Cleans up empty directories in the archive."""
        for dirpath, dirnames, filenames in os.walk(self.archive_path, topdown=False):
            if not dirnames and not filenames:
                os.rmdir(dirpath)

if __name__ == "__main__":
    reviewer = RescueReviewer(Path("."))
    reviewer.review_and_heal()
