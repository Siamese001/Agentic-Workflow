"""Spine verifier — L3 ran OR L3 was lawfully bypassed (R1B doctrine).

Asserts exactly one of these holds for the run:

    A) ``route_contract.execution_form == MANAGED_WORKFLOW`` AND
       ``runtime_l3_orchestration_receipt.json`` exists with a matching
       ``dag_sha256``.

    B) ``route_contract.execution_form != MANAGED_WORKFLOW`` AND
       ``l3_bypass_receipt.json`` exists with a permitted bypass reason
       and ``l3_required == False``.

This pass implements only Branch B (R1B closure). When a future pass
adds ``MANAGED_WORKFLOW`` support, this verifier will also enforce
Branch A; today it FAIL_CLOSED if execution_form == MANAGED_WORKFLOW
because the receipt does not yet exist in agentic_core.

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
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

from agentic_core.runtime.contracts.l3_bypass_receipt import (  # noqa: E402
    ALLOWED_L3_BYPASS_REASONS,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_l3_runtime_or_bypass] artifact_dir={art_dir}")

    try:
        rc = load_payload(art_dir, "route_contract.json")
    except FileNotFoundError as exc:
        return fail("ROUTE_CONTRACT_MISSING", str(exc))

    # The R1B emitter writes a "route_id_hint" + a TerminalRetPacket
    # later in the chain whose ``execution_form`` is the authoritative
    # field. We read both for robustness.
    rc_form = str(rc.get("execution_form", "") or "")
    if not rc_form:
        try:
            tp = load_payload(art_dir, "terminal_ret_packet.json")
            rc_form = str(tp.get("execution_form", "") or "")
        except FileNotFoundError:
            rc_form = ""

    if rc_form == "MANAGED_WORKFLOW":
        # Branch A (MW substrate added 2026-05-01).
        rec_path = art_dir / "runtime_l3_orchestration_receipt.json"
        sdp_path = art_dir / "static_dag_proof.json"
        if not rec_path.exists():
            return fail(
                "L3_RUNTIME_RECEIPT_MISSING",
                "execution_form=MANAGED_WORKFLOW but "
                "runtime_l3_orchestration_receipt.json not present",
            )
        if not sdp_path.exists():
            return fail(
                "STATIC_DAG_PROOF_MISSING",
                "execution_form=MANAGED_WORKFLOW but "
                "static_dag_proof.json not present",
            )
        try:
            receipt = load_payload(art_dir, "runtime_l3_orchestration_receipt.json")
            sdp = load_payload(art_dir, "static_dag_proof.json")
            identity = load_payload(art_dir, "runtime_identity_envelope.json")
        except FileNotFoundError as exc:
            return fail("MW_ARTIFACT_MISSING", str(exc))

        # Hash binding: receipt.dag_sha256 MUST equal static_dag.dag_sha256.
        if receipt.get("dag_sha256") != sdp.get("dag_sha256"):
            return fail(
                "L3_RUNTIME_STATIC_DAG_SHA_DIVERGENCE",
                f"runtime_l3.dag_sha256={receipt.get('dag_sha256')!r} != "
                f"static_dag.dag_sha256={sdp.get('dag_sha256')!r}",
            )
        if receipt.get("dag_id") != sdp.get("dag_id"):
            return fail(
                "L3_RUNTIME_STATIC_DAG_ID_DIVERGENCE",
                f"runtime_l3.dag_id={receipt.get('dag_id')!r} != "
                f"static_dag.dag_id={sdp.get('dag_id')!r}",
            )

        # l3_required=True on receipt side.
        if receipt.get("l3_required") is not True:
            return fail(
                "L3_REQUIRED_FALSE_ON_RECEIPT",
                "runtime_l3_orchestration_receipt.l3_required must be True",
            )

        # No-execute / no-retrieve / no-PA / no-L4-write assertions.
        for flag in (
            "l3_no_execute_assertion",
            "l3_no_retrieve_assertion",
            "l3_no_prompt_assembly_assertion",
            "l3_no_l4_write_assertion",
        ):
            if receipt.get(flag) is not True:
                return fail(
                    "L3_RUNTIME_ASSERTION_FALSE",
                    f"runtime_l3_orchestration_receipt.{flag}={receipt.get(flag)!r}; must be True",
                )

        # selected_node_ids ⊆ static_dag.node_ids.
        selected = set(receipt.get("selected_node_ids") or [])
        declared = set(sdp.get("node_ids") or [])
        if not selected:
            return fail(
                "L3_RUNTIME_NO_NODES_SELECTED",
                "selected_node_ids empty on MANAGED_WORKFLOW receipt",
            )
        off_dag = selected - declared
        if off_dag:
            return fail(
                "L3_RUNTIME_SELECTED_NODE_OFF_DAG",
                f"selected_node_ids {sorted(off_dag)!r} not in static_dag.node_ids",
            )

        # Step contracts must all bind run_id to identity and map to a
        # node in selected_node_ids.
        expected_run_id = identity.get("run_id")
        for sc in receipt.get("step_contracts") or []:
            if not isinstance(sc, dict):
                return fail("L3_STEP_CONTRACT_INVALID_SHAPE", f"step: {sc!r}")
            if sc.get("run_id") != expected_run_id:
                return fail(
                    "L3_STEP_RUN_ID_DIVERGENCE",
                    f"step_id={sc.get('step_id')!r} run_id={sc.get('run_id')!r} "
                    f"!= identity.run_id={expected_run_id!r}",
                )
            if sc.get("node_id") not in selected:
                return fail(
                    "L3_STEP_NODE_NOT_SELECTED",
                    f"step_id={sc.get('step_id')!r} node_id={sc.get('node_id')!r} "
                    f"not in selected_node_ids",
                )

        return passed(
            f"L3 orchestrated: dag_id={receipt.get('dag_id')!r}, "
            f"dag_sha256={receipt.get('dag_sha256', '')[:16]}..., "
            f"selected_nodes={sorted(selected)}, "
            f"steps={len(receipt.get('step_contracts') or [])}"
        )

    # Branch B — bypass required.
    try:
        bypass = load_payload(art_dir, "l3_bypass_receipt.json")
    except FileNotFoundError as exc:
        return fail(
            "L3_BYPASS_RECEIPT_MISSING",
            f"execution_form={rc_form!r} != MANAGED_WORKFLOW but "
            f"l3_bypass_receipt.json is absent: {exc}",
        )

    if bypass.get("l3_required") is not False:
        return fail(
            "L3_REQUIRED_TRUE_ON_BYPASS",
            f"l3_bypass_receipt.l3_required={bypass.get('l3_required')!r}; must be False",
        )
    reason = bypass.get("l3_bypass_reason", "")
    if reason not in ALLOWED_L3_BYPASS_REASONS:
        return fail(
            "L3_BYPASS_REASON_INVALID",
            f"l3_bypass_reason={reason!r} not in {sorted(ALLOWED_L3_BYPASS_REASONS)}",
        )
    if not bypass.get("why_static_dag_not_used"):
        return fail(
            "L3_BYPASS_MISSING_REASON_TEXT",
            "l3_bypass_receipt.why_static_dag_not_used must be non-empty",
        )

    return passed(
        f"L3 lawfully bypassed: execution_form={rc_form!r}, "
        f"reason={reason!r}, static_dag_available={bypass.get('static_dag_available')}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
