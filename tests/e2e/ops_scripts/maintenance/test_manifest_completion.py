"""
scripts/maintenance/test_manifest_completion.py
-----------------------------------------------
PHASE 5: FINAL AUDIT
Target: 100% Code Completion.
Context: Verifies that all High Priority files are RESOLVED.
"""

import json
from pathlib import Path

import pytest

MANIFEST_PATH = Path("docs/reports/reconciliation_manifest.json")


class TestManifestCompletion:
    def test_all_high_priority_resolved(self):
        """
        FAIL if any High Priority file is still PENDING.
        """
        if not MANIFEST_PATH.exists():
            pytest.fail("Manifest not found")

        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)

        high_priority = manifest.get("high_priority_files", [])
        pending = [f for f in high_priority if f.get("status") == "PENDING"]

        if pending:
            print("\n[FAIL] The following files are still PENDING:")
            for p in pending:
                print(f"  - {p['file']}")

        assert len(pending) == 0, f"Incomplete Migration! {len(pending)} files pending."


if __name__ == "__main__":
    pytest.main([__file__])
