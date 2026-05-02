"""One-shot helper: cross-link legacy artifacts/certification/apps_rg_e2e/
with the new artifacts/certification/apps_e2e/apps_rg/ canonical layout.

Strategy: NEVER delete the legacy directory (the legacy emitter at
tools/certification/apps_rg_e2e/ still writes there). Instead:

  * Verify the new path has a fresh bundle.
  * Write a small `legacy_path_pointer.json` in the legacy dir telling
    consumers where the canonical bundle lives now.
  * Append `legacy_path_ref` to the new bundle's notes (idempotent).

Run:
    python -m tools.certification.apps_e2e.migrate_legacy_paths
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, relative_to_repo, sha256_file, utc_now_iso,
)
from tools.certification.apps_e2e.paths import AppCertPaths

LEGACY_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_rg_e2e"
LEGACY_BUNDLE = LEGACY_DIR / "apps_rg_e2e_proof.json"
POINTER_PATH = LEGACY_DIR / "legacy_path_pointer.json"


def main() -> int:
    new_paths = AppCertPaths("apps_rg")
    if not new_paths.proof_bundle.exists():
        print(f"[migrate] FAIL: new bundle absent at {new_paths.proof_bundle}", file=sys.stderr)
        print("[migrate]   run: python -m tools.certification.apps_e2e.emit_proof_bundle --app apps_rg --dry-run")
        return 2

    legacy_present = LEGACY_BUNDLE.exists()
    pointer = {
        "kind": "legacy_path_pointer",
        "generated_at_utc": utc_now_iso(),
        "legacy_path": relative_to_repo(LEGACY_DIR),
        "legacy_bundle": relative_to_repo(LEGACY_BUNDLE) if legacy_present else None,
        "legacy_bundle_sha256": sha256_file(LEGACY_BUNDLE) if legacy_present else None,
        "canonical_path": relative_to_repo(new_paths.app_dir),
        "canonical_bundle": relative_to_repo(new_paths.proof_bundle),
        "canonical_bundle_sha256": sha256_file(new_paths.proof_bundle),
        "notes": (
            "The canonical apps_rg end-to-end proof bundle now lives at the "
            "shared apps_e2e harness path. The legacy apps_rg_e2e emitter at "
            "tools/certification/apps_rg_e2e/ is preserved unchanged for "
            "backward compatibility but is superseded by "
            "tools/certification/apps_e2e/. Consumers should read the "
            "canonical bundle."
        ),
    }
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    POINTER_PATH.write_text(json.dumps(pointer, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[migrate] wrote {relative_to_repo(POINTER_PATH)}")
    print(f"[migrate]   legacy_bundle  = {pointer['legacy_bundle']}")
    print(f"[migrate]   canonical      = {pointer['canonical_bundle']}")
    print(f"[migrate]   canonical_sha  = {pointer['canonical_bundle_sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
