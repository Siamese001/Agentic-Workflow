"""W2 verifier #1 — Integrated runtime entry-point used.

Asserts:
  1. integrated_runtime_artifact_manifest.json exists and is well-formed.
  2. payload.integrated_runtime_entrypoint_used == True.
  3. payload.entry_point identifies the production entry point exactly.
  4. All declared W2 artifacts (W2_ARTIFACT_FILENAMES) are present, each
     as a valid envelope.
  5. Every artifact's producer_component starts with "agentic_core.".

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (
    EXIT_HARNESS_ERROR,
    chain_filenames_for,
    detect_chain_kind,
    fail,
    load_envelope,
    passed,
    resolve_artifact_dir,
)

EXPECTED_ENTRY_POINTS = {
    "R1B": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "MANAGED_WORKFLOW": "agentic_core.runtime.entrypoints.integrated_managed_workflow_run.run_integrated_managed_workflow",
    # R1A / R5 / UWG_BLOCK are thin wrappers around run_integrated_safe_reuse;
    # the underlying runner is the actual code path that emits the chain
    # artifacts, so the stamped entry_point matches.
    "R1A_EXACT_CACHE": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "R5_FALLBACK": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "UWG_BLOCK_PATH": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
    "UWG_COMMIT_PATH": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "R3_GROUNDED_READ": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "R4_SINGLE_ACTION": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
    "MANAGED_WORKFLOW_REAL_EXECUTION": "agentic_core.runtime.entrypoints.integrated_safe_reuse_run.run_integrated_safe_reuse",
}


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    expected_entry_point = EXPECTED_ENTRY_POINTS.get(kind, "")
    print(
        f"[verify_integrated_runtime_entrypoint] artifact_dir={art_dir} "
        f"chain_kind={kind}"
    )
    chain_filenames = chain_filenames_for(kind)

    # 1+2+3: manifest must exist and stamp the entry-point use.
    try:
        manifest = load_envelope(art_dir, "integrated_runtime_artifact_manifest.json")
    except FileNotFoundError as exc:
        return fail("MANIFEST_MISSING", str(exc))
    payload = manifest.get("payload", {})
    if not payload.get("integrated_runtime_entrypoint_used"):
        return fail("ENTRYPOINT_FLAG_FALSE",
                    f"manifest.payload.integrated_runtime_entrypoint_used={payload.get('integrated_runtime_entrypoint_used')!r}")
    if payload.get("entry_point") != expected_entry_point:
        return fail("ENTRYPOINT_MISMATCH",
                    f"manifest.payload.entry_point={payload.get('entry_point')!r} != {expected_entry_point!r}")

    # 4: every declared artifact present, each a valid envelope.
    missing = []
    bad_envelope = []
    bad_producer = []
    for fn in chain_filenames:
        try:
            env = load_envelope(art_dir, fn)
        except FileNotFoundError:
            missing.append(fn)
            continue
        for key in ("producer_component", "producer_module", "producer_function_or_class",
                    "emitted_at", "artifact_hash", "upstream_artifact_ref", "payload"):
            if key not in env:
                bad_envelope.append(f"{fn}:missing_key={key}")
        # 5: producer must be agentic_core.* — never harness, never tools.
        producer = env.get("producer_component", "")
        if not producer.startswith("agentic_core."):
            bad_producer.append(f"{fn}:producer={producer!r}")
    if missing:
        return fail("ARTIFACTS_MISSING", f"{len(missing)}: {missing}")
    if bad_envelope:
        return fail("ENVELOPE_SHAPE_INVALID", f"{len(bad_envelope)}: {bad_envelope[:5]}")
    if bad_producer:
        return fail("PRODUCER_NOT_AGENTIC_CORE", f"{len(bad_producer)}: {bad_producer[:5]}")

    return passed(
        f"entry_point={expected_entry_point}; all {len(chain_filenames)} "
        f"artifacts present and producer-stamped (chain_kind={kind})"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
