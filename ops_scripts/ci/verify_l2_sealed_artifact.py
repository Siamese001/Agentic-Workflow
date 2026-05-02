"""Spine verifier — L2 sealed artifact shape + identity continuity (MW chain).

Asserts when ``l2_sealed_artifact.json`` exists:
  1. Identity fields (``run_id``, ``request_id``, ``trace_root``) match
     the RuntimeIdentityEnvelope.
  2. ``run_scope == 'CURRENT_RUN'`` (hard architectural invariant — a
     sealed L2 artifact is per-run, never stored in L4 directly).
  3. ``no_l4_write_assertion == True`` (L2 never commits durable state
     itself; any commit must route through UWG).
  4. When ``structural_only == True``, ``no_l2_real_execution_assertion``
     must also be True (structural seals assert no real tool/model
     invocation).
  5. ``l3_step_contracts_ref`` matches the artifact_hash of the
     runtime L3 orchestration receipt on disk (binding L2 seal to L3).
  6. ``has_commit_payload`` correctly reflects ``state_diff`` emptiness.

R1B chain has no ``l2_sealed_artifact.json`` and the verifier passes
trivially.

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    detect_chain_kind,
    fail,
    load_envelope,
    load_payload,
    passed,
    resolve_artifact_dir,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_l2_sealed_artifact] artifact_dir={art_dir} "
        f"chain_kind={kind}"
    )

    p = art_dir / "l2_sealed_artifact.json"
    if not p.exists():
        if kind == "MANAGED_WORKFLOW":
            return fail(
                "L2_SEALED_ARTIFACT_MISSING_ON_MW",
                "MANAGED_WORKFLOW chain requires l2_sealed_artifact.json",
            )
        return passed(f"no l2_sealed_artifact.json present (chain_kind={kind})")

    seal = load_payload(art_dir, "l2_sealed_artifact.json")

    # Identity continuity.
    try:
        identity = load_payload(art_dir, "runtime_identity_envelope.json")
    except FileNotFoundError as exc:
        return fail("RUNTIME_IDENTITY_ENVELOPE_MISSING", str(exc))
    for key in ("run_id", "request_id", "trace_root"):
        if seal.get(key) != identity.get(key):
            return fail(
                "L2_SEAL_IDENTITY_DIVERGENCE",
                f"{key}: seal={seal.get(key)!r} != identity={identity.get(key)!r}",
            )

    if seal.get("run_scope") != "CURRENT_RUN":
        return fail(
            "L2_SEAL_RUN_SCOPE_INVALID",
            f"run_scope={seal.get('run_scope')!r}; must be 'CURRENT_RUN'",
        )

    if seal.get("no_l4_write_assertion") is not True:
        return fail(
            "L2_SEAL_L4_WRITE_ASSERTION_FALSE",
            "no_l4_write_assertion must be True on every sealed L2 artifact",
        )

    if seal.get("structural_only"):
        if seal.get("no_l2_real_execution_assertion") is not True:
            return fail(
                "L2_SEAL_STRUCTURAL_BUT_EXEC_ASSERTION_FALSE",
                "structural_only=True requires no_l2_real_execution_assertion=True",
            )

    # has_commit_payload ↔ state_diff consistency.
    has_commit = bool(seal.get("has_commit_payload"))
    state_diff = seal.get("state_diff") or {}
    if has_commit and not state_diff:
        return fail(
            "L2_SEAL_COMMIT_PAYLOAD_WITHOUT_DIFF",
            "has_commit_payload=True but state_diff is empty",
        )
    if (not has_commit) and state_diff:
        return fail(
            "L2_SEAL_DIFF_WITHOUT_COMMIT_PAYLOAD",
            "state_diff is non-empty but has_commit_payload=False",
        )

    # L3 step-contracts ref: must match the runtime_l3_orchestration_receipt
    # envelope's artifact_hash on disk (when that receipt exists).
    ref = seal.get("l3_step_contracts_ref", "")
    if ref:
        l3_path = art_dir / "runtime_l3_orchestration_receipt.json"
        if not l3_path.exists():
            return fail(
                "L2_SEAL_L3_REF_BUT_NO_RECEIPT",
                f"l3_step_contracts_ref={ref!r} present but "
                f"runtime_l3_orchestration_receipt.json is absent",
            )
        l3_env = load_envelope(art_dir, "runtime_l3_orchestration_receipt.json")
        if l3_env.get("artifact_hash") != ref:
            return fail(
                "L2_SEAL_L3_REF_HASH_MISMATCH",
                f"l3_step_contracts_ref={ref!r} != "
                f"l3_receipt.artifact_hash={l3_env.get('artifact_hash')!r}",
            )

    return passed(
        f"L2 sealed artifact valid: run_scope={seal.get('run_scope')}, "
        f"no_l4_write=True, "
        f"structural_only={bool(seal.get('structural_only'))}, "
        f"has_commit_payload={has_commit}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
