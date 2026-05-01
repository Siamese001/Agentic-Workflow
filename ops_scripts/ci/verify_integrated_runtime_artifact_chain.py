"""W2 verifier #3 — Integrated-runtime artifact chain integrity.

Walks the W2_CHAIN_LINKAGE in order and asserts:
  1. Each artifact's recomputed SHA256 of canonical-JSON(.payload) matches
     the envelope's artifact_hash field.
  2. Each artifact's upstream_artifact_ref equals its predecessor's
     artifact_hash (root: integrated_runtime_entrypoint_invocation has empty
     upstream).
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (
    EXIT_HARNESS_ERROR,
    W2_CHAIN_LINKAGE,
    fail,
    load_envelope,
    passed,
    resolve_artifact_dir,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import compute_artifact_hash


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_integrated_runtime_artifact_chain] artifact_dir={art_dir}")

    hashes: dict[str, str] = {}
    for filename, _upstream in W2_CHAIN_LINKAGE:
        try:
            env = load_envelope(art_dir, filename)
        except FileNotFoundError as exc:
            return fail("ARTIFACT_MISSING", f"{filename}: {exc}")

        # 1: recomputed sha == declared sha.
        declared = env.get("artifact_hash", "")
        recomputed = compute_artifact_hash(env.get("payload"))
        if declared != recomputed:
            return fail(
                "CHAIN_SHA_DIVERGENCE",
                f"{filename}: declared={declared!r} recomputed={recomputed!r}",
            )
        hashes[filename] = declared

    # 2: upstream linkage check.
    for filename, upstream in W2_CHAIN_LINKAGE:
        env = load_envelope(art_dir, filename)
        actual_upstream = env.get("upstream_artifact_ref", "")
        if upstream is None:
            if actual_upstream not in ("", None):
                return fail(
                    "ROOT_HAS_UPSTREAM",
                    f"{filename}: root artifact must have empty upstream_artifact_ref, got {actual_upstream!r}",
                )
        else:
            expected = hashes.get(upstream, "")
            if actual_upstream != expected:
                return fail(
                    "UPSTREAM_REF_BROKEN",
                    f"{filename}: upstream_artifact_ref={actual_upstream!r} != "
                    f"hash({upstream})={expected!r}",
                )
    return passed(
        f"chain verified: {len(W2_CHAIN_LINKAGE)} artifacts, all SHAs and upstream refs match"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
