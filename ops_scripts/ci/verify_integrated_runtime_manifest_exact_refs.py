"""Spine verifier — manifest.artifact_filenames matches on-disk artifacts exactly.

Asserts set equality between:

    (a) ``integrated_runtime_artifact_manifest.payload.artifact_filenames``
    (b) ``W2_ARTIFACT_FILENAMES`` (the SSOT chain enumeration)
    (c) The set of ``*.json`` files in the artifact directory that are
        valid W2 envelopes (with a ``producer_component`` starting with
        ``agentic_core.``).

If any of these three sets differ, the run is fail-closed with the
disjoint set spelled out for forensics. This catches:

    - manifest declares an artifact that was never written
    - emitter wrote an artifact the manifest forgot to declare
    - stale or extra files in the run directory (e.g. tampered drops)

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    chain_filenames_for,
    detect_chain_kind,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

# Per-run artifacts that the integrated entry point may legitimately
# write to the run directory but are NOT part of the W2 chain. They are
# excluded from the set-equality check.
_TOLERATED_NON_CHAIN_FILES: frozenset[str] = frozenset({
    "live_provider_attestation.json",
    # R5_FALLBACK extra (bound via manifest.safe_fallback_decision_ref)
    "safe_fallback_decision.json",
    # UWG_BLOCK_PATH extras (bound via manifest.uwg_blocked_commit_receipt_ref
    # and manifest.commit_request_ref).
    "commit_request.json",
    "uwg_blocked_commit_receipt.json",
    # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
    # UWG_COMMIT_PATH extras
    "uwg_commit_receipt.json",
    "uwg_refresh_receipts.json",
    # R3_GROUNDED_READ extras
    "final_evidence_contract.json",
    "retrieval_corpus_manifest.json",
    # R4_SINGLE_ACTION extras
    "sealed_l2_artifact.json",
    "tool_authorization_receipt.json",
    # MANAGED_WORKFLOW_REAL_EXECUTION extras
    "managed_workflow_real_execution_receipt.json",
})


def _is_w2_envelope(path) -> bool:
    """Return True if the JSON at ``path`` looks like a W2 envelope.

    Used to filter the on-disk set: only files that carry the
    integrated_runtime envelope shape and an agentic_core producer count
    as chain artifacts. Other JSON files (e.g. ``live_provider_attestation.json``)
    are tolerated as side-channel.
    """
    try:
        env = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(env, dict):
        return False
    needed = {"producer_component", "artifact_hash", "upstream_artifact_ref", "payload"}
    if not needed.issubset(env.keys()):
        return False
    producer = env.get("producer_component", "")
    return isinstance(producer, str) and producer.startswith("agentic_core.")


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_integrated_runtime_manifest_exact_refs] artifact_dir={art_dir} "
        f"chain_kind={kind}"
    )

    # (b) SSOT chain enumeration for the detected chain kind.
    chain_set = set(chain_filenames_for(kind))

    # (a) manifest declaration.
    try:
        manifest = load_payload(art_dir, "integrated_runtime_artifact_manifest.json")
    except FileNotFoundError as exc:
        return fail("MANIFEST_MISSING", str(exc))
    declared = manifest.get("artifact_filenames")
    if not isinstance(declared, list):
        return fail(
            "MANIFEST_ARTIFACT_FILENAMES_INVALID",
            f"artifact_filenames must be a list; got {type(declared).__name__}",
        )
    declared_set = set(str(x) for x in declared)
    if len(declared_set) != len(declared):
        return fail(
            "MANIFEST_DUPLICATE_FILENAME",
            f"manifest.artifact_filenames has duplicates: {declared}",
        )

    # (c) on-disk envelope set.
    on_disk: set[str] = set()
    for entry in art_dir.iterdir():
        if not entry.is_file() or entry.suffix != ".json":
            continue
        if entry.name in _TOLERATED_NON_CHAIN_FILES:
            continue
        if _is_w2_envelope(entry):
            on_disk.add(entry.name)

    # Compare manifest vs. SSOT chain.
    if declared_set != chain_set:
        only_manifest = sorted(declared_set - chain_set)
        only_chain = sorted(chain_set - declared_set)
        return fail(
            "MANIFEST_VS_CHAIN_DIVERGENCE",
            f"only_in_manifest={only_manifest}; only_in_chain_ssot={only_chain}",
        )

    # Compare on-disk vs. SSOT chain.
    if on_disk != chain_set:
        only_disk = sorted(on_disk - chain_set)
        only_chain = sorted(chain_set - on_disk)
        return fail(
            "ON_DISK_VS_CHAIN_DIVERGENCE",
            f"only_on_disk={only_disk}; only_in_chain_ssot={only_chain}",
        )

    return passed(
        f"manifest declarations == on-disk artifacts == chain_filenames "
        f"({len(chain_set)} entries, chain_kind={kind})"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
