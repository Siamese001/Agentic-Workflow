"""Spine verifier — StaticDagProof is well-formed (MW chain only).

Asserts:
  1. ``static_dag_proof.json`` exists (MW) or does not exist (R1B).
  2. ``schema_version`` matches the contract version.
  3. ``dag_id`` / ``dag_sha256`` non-empty.
  4. ``node_count == len(node_ids)`` and ``edge_count == len(edge_list)``.
  5. ``entry_nodes`` and ``terminal_nodes`` are subsets of ``node_ids``.
  6. ``all_nodes_have_owner``, ``all_nodes_have_step_contract_schema``,
     ``all_nodes_have_allowed_execution_surface`` are all True.
  7. ``l3_no_execute_policy``, ``l3_no_retrieve_policy``,
     ``l3_no_prompt_assembly_policy``, ``l3_no_l4_write_policy`` are all True.
  8. ``has_cycle == False`` OR (``has_cycle == True`` AND
     ``bounded_loop_max > 0``).
  9. Recomputed digest matches the declared ``dag_sha256``.

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
    load_payload,
    passed,
    resolve_artifact_dir,
)

from agentic_core.L3_orchestration.registry.static_dag_proof import (  # noqa: E402
    STATIC_DAG_PROOF_SCHEMA_VERSION,
    compute_static_dag_digest,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_l3_static_dag_proof] artifact_dir={art_dir} "
        f"chain_kind={kind}"
    )

    sdp_path = art_dir / "static_dag_proof.json"

    if kind != "MANAGED_WORKFLOW":
        if sdp_path.exists():
            return fail(
                "STATIC_DAG_PROOF_ON_NON_MW_CHAIN",
                f"static_dag_proof.json present on chain_kind={kind!r}; "
                f"only MANAGED_WORKFLOW runs may carry it",
            )
        return passed(f"non-MW chain (kind={kind}); no static_dag_proof expected")

    if not sdp_path.exists():
        return fail("STATIC_DAG_PROOF_MISSING",
                    "MW chain requires static_dag_proof.json")

    sdp = load_payload(art_dir, "static_dag_proof.json")

    if sdp.get("schema_version") != STATIC_DAG_PROOF_SCHEMA_VERSION:
        return fail(
            "STATIC_DAG_SCHEMA_VERSION_MISMATCH",
            f"schema_version={sdp.get('schema_version')!r} != "
            f"{STATIC_DAG_PROOF_SCHEMA_VERSION!r}",
        )
    if not sdp.get("dag_id"):
        return fail("STATIC_DAG_ID_EMPTY", "dag_id must be non-empty")
    if not sdp.get("dag_sha256"):
        return fail("STATIC_DAG_SHA_EMPTY", "dag_sha256 must be non-empty")

    node_ids = sdp.get("node_ids") or []
    edge_list = sdp.get("edge_list") or []
    if sdp.get("node_count") != len(node_ids):
        return fail(
            "STATIC_DAG_NODE_COUNT_MISMATCH",
            f"node_count={sdp.get('node_count')} != len(node_ids)={len(node_ids)}",
        )
    if sdp.get("edge_count") != len(edge_list):
        return fail(
            "STATIC_DAG_EDGE_COUNT_MISMATCH",
            f"edge_count={sdp.get('edge_count')} != len(edge_list)={len(edge_list)}",
        )

    node_id_set = set(node_ids)
    for n in sdp.get("entry_nodes", []) or []:
        if n not in node_id_set:
            return fail(
                "STATIC_DAG_ENTRY_NODE_UNKNOWN",
                f"entry_node {n!r} not in node_ids",
            )
    for n in sdp.get("terminal_nodes", []) or []:
        if n not in node_id_set:
            return fail(
                "STATIC_DAG_TERMINAL_NODE_UNKNOWN",
                f"terminal_node {n!r} not in node_ids",
            )

    # Per-node invariants.
    for flag in (
        "all_nodes_have_owner",
        "all_nodes_have_step_contract_schema",
        "all_nodes_have_allowed_execution_surface",
    ):
        if sdp.get(flag) is not True:
            return fail(
                "STATIC_DAG_NODE_INVARIANT_FALSE",
                f"{flag}={sdp.get(flag)!r}; must be True",
            )

    # L3 no-execute / no-retrieve / no-PA / no-L4-write policies.
    for policy in (
        "l3_no_execute_policy",
        "l3_no_retrieve_policy",
        "l3_no_prompt_assembly_policy",
        "l3_no_l4_write_policy",
    ):
        if sdp.get(policy) is not True:
            return fail(
                "STATIC_DAG_L3_POLICY_FALSE",
                f"{policy}={sdp.get(policy)!r}; must be True",
            )

    # Cycle rule.
    has_cycle = bool(sdp.get("has_cycle"))
    bounded_loop_max = int(sdp.get("bounded_loop_max", 0))
    if has_cycle and bounded_loop_max <= 0:
        return fail(
            "STATIC_DAG_CYCLE_UNBOUNDED",
            "has_cycle=True requires bounded_loop_max > 0",
        )

    # Recomputed digest MUST match the declared dag_sha256.
    recomputed = compute_static_dag_digest(sdp)
    if recomputed != sdp.get("dag_sha256"):
        return fail(
            "STATIC_DAG_SHA_DIVERGENCE",
            f"recomputed={recomputed!r} != declared={sdp.get('dag_sha256')!r}",
        )

    return passed(
        f"static DAG proof valid: dag_id={sdp.get('dag_id')!r}, "
        f"node_count={sdp.get('node_count')}, "
        f"edge_count={sdp.get('edge_count')}, "
        f"dag_sha256={sdp.get('dag_sha256')[:16]}..."
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
