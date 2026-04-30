"""Apply W2 composition-proof results into the W3-upgraded bundles.

Plan: 10c-proof-depth-remediation-a9f9af.md, end of W2 + start of W3.

Runs both composition harnesses (REQ-077, REQ-128), embeds the result
into their proof_bundles/*.json, recomputes content_hash. The W3 sweep
already wrote the in-memory-exporter result for these REQs; this script
overlays the composition harness's E5_COMPOSITION_PROOF result on top.

Anti-cheat
----------

Composition results only upgrade `actual_proof_depth` to
``E5_COMPOSITION_PROOF`` when the composition harness reports
``status=SATISFIED``. Otherwise the bundle keeps whatever depth the
W3 batch sweep recorded.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUNDLES_DIR = REPO / "artifacts" / "requirements" / "proof_bundles"


def _content_hash(bundle: dict) -> str:
    b = dict(bundle)
    b["content_hash"] = ""
    return hashlib.sha256(
        json.dumps(b, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _embed_composition(req_id: str, bundle_filename: str, run_proof_fn) -> dict:
    bundle_path = BUNDLES_DIR / bundle_filename
    if not bundle_path.exists():
        return {"req_id": req_id, "outcome": "BUNDLE_MISSING"}

    result = run_proof_fn()

    with bundle_path.open(encoding="utf-8") as f:
        bundle = json.load(f)

    composition_block = {
        "harness": "tools.proof.composition_proof_*",
        "req_id": result.req_id,
        "status": result.status,
        "actual_proof_depth": result.actual_proof_depth,
        "reason": result.reason,
        "components_attempted": list(result.components_attempted),
        "components_reached": list(result.components_reached),
    }
    if result.otel_proof is not None:
        composition_block["otel_proof"] = result.otel_proof.to_bundle_payload()
    bundle["composition_proof"] = composition_block

    if result.status == "SATISFIED":
        bundle["actual_proof_depth"] = "E5_COMPOSITION_PROOF"
        bundle["proof_status"] = "EVIDENCE_PRESENT"
    bundle["content_hash"] = _content_hash(bundle)
    bundle_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {
        "req_id": req_id,
        "outcome": "BUNDLE_UPDATED",
        "bundle_path": str(bundle_path.relative_to(REPO)),
        "actual_proof_depth": bundle["actual_proof_depth"],
        "composition_status": result.status,
        "content_hash": bundle["content_hash"],
    }


def main() -> int:
    from tools.proof.composition_proof_semantic_cache import (
        run_composition_proof as run_077,
    )
    from tools.proof.composition_proof_provenance_chain import (
        run_composition_proof as run_128,
    )

    out = []
    print("[apply_composition] running REQ-077...")
    out.append(_embed_composition("10C-REQ-077", "10c-req-077.json", run_077))
    print(f"  -> {out[-1]}")

    print("[apply_composition] running REQ-128...")
    out.append(_embed_composition("10C-REQ-128", "10c-req-128.json", run_128))
    print(f"  -> {out[-1]}")

    print("\n[apply_composition] summary:")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
