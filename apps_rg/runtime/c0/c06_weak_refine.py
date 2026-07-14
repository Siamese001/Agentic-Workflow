"""C0.6 — one bounded, authority-preserving C0.3 refinement.

The first C0.3 pass is allowed to describe weak/empty direct-path coverage so
that C0.5 can diagnose it.  C0.6 may then make exactly one deterministic
second pass using the *already frozen* section graph plan.  It never changes
the C0.2 atoms, allowed facts, section, role/route scope, or graph snapshot.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    CANONICAL_PLAN_SCHEMA_VERSION,
    build_candidate_receipt,
    stable_digest,
    validate_canonical_section_plan,
)
from apps_rg.runtime.c0.constants import GRAPH_STRENGTH_DIRECT, PROOF_ELIGIBLE

C06_RECEIPT_ARTIFACT = "c06_weak_refine_receipt.json"
C06_SCHEMA_VERSION = "c06_weak_refine_v1"
C06_MAX_ATTEMPTS = 1


def _strings(values: Any) -> list[str]:
    if isinstance(values, (str, bytes)):
        values = [values]
    out: list[str] = []
    for value in values or []:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _atom_fingerprint(atoms: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "fact_id": str(atom.get("fact_id") or ""),
            "source_type": str(atom.get("source_type") or ""),
            "source_span_ref": str(atom.get("source_span_ref") or ""),
            "proof_status": str(atom.get("proof_status") or ""),
            "allowed_sections": sorted(_strings(atom.get("allowed_sections"))),
            "blocked_sections": sorted(_strings(atom.get("blocked_sections"))),
        }
        for atom in atoms
    ]
    rows.sort(key=lambda row: (row["fact_id"], row["source_span_ref"]))
    fact_ids = sorted({row["fact_id"] for row in rows if row["fact_id"]})
    return {
        "fact_ids": fact_ids,
        "fact_ids_digest": stable_digest(fact_ids),
        "atom_scope_digest": stable_digest(rows),
    }


def _coverage_snapshot(
    *, atoms: list[dict[str, Any]], c03: Mapping[str, Any]
) -> dict[str, Any]:
    proof_ids = sorted(
        {
            str(atom.get("fact_id") or "").strip()
            for atom in atoms
            if str(atom.get("fact_id") or "").strip()
            and str(atom.get("proof_status") or "") == PROOF_ELIGIBLE
        }
    )
    direct_ids = sorted(
        {
            str(binding.get("fact_id") or "").strip()
            for binding in c03.get("bindings") or []
            if isinstance(binding, Mapping)
            and str(binding.get("fact_id") or "").strip()
            and binding.get("graph_support_strength") == GRAPH_STRENGTH_DIRECT
            and binding.get("claim_support_allowed") is True
        }
    )
    supported = sorted(set(proof_ids) & set(direct_ids))
    unresolved = sorted(set(proof_ids) - set(supported))
    candidate_receipt = c03.get("graph_candidate_receipt") or {}
    traversal_receipt = c03.get("graph_traversal_receipt") or {}
    authority_receipt = c03.get("pretarget_authority_receipt") or {}
    contract_pass = bool(
        candidate_receipt.get("candidate_conservation_pass") is True
        and traversal_receipt.get("pass") is True
        and authority_receipt.get("authority_before_targeting_pass") is True
    )
    if not contract_pass:
        status = "BLOCKED"
    elif proof_ids and not unresolved:
        status = "PASS"
    elif supported:
        status = "WEAK"
    else:
        status = "EMPTY"
    return {
        "status": status,
        "proof_fact_ids": proof_ids,
        "direct_supported_fact_ids": supported,
        "unresolved_fact_ids": unresolved,
        "proof_fact_count": len(proof_ids),
        "direct_supported_fact_count": len(supported),
        "coverage_ratio": round(len(supported) / len(proof_ids), 6) if proof_ids else 0.0,
        "candidate_conservation_pass": candidate_receipt.get("candidate_conservation_pass")
        is True,
        "traversal_pass": traversal_receipt.get("pass") is True,
        "authority_before_targeting_pass": authority_receipt.get(
            "authority_before_targeting_pass"
        )
        is True,
    }


def _selected_plan_fact_ids(plan: Mapping[str, Any]) -> list[str]:
    return sorted(
        {
            str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
            for row in plan.get("facts") or []
            if isinstance(row, Mapping)
            and str(row.get("fact_id") or row.get("candidate_fact_id") or "").strip()
        }
    )


def _unstamped_plan_decisions(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = deepcopy(list(plan.get("graph_candidate_decision_ledger") or []))
    for row in rows:
        if isinstance(row, dict):
            row.pop("plan_id", None)
            row.pop("plan_digest", None)
    return [row for row in rows if isinstance(row, dict)]


def _canonical_plan_digest_payload(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Reconstruct the payload sealed by finalize_canonical_section_plan.

    The canonical finalizer calculates the top-level digest before copying the
    plan stamp into its decision ledger and compact receipts.  Validation must
    remove those nested stamps as well as the top-level identity fields.
    """
    payload = deepcopy(dict(plan))
    payload.pop("plan_id", None)
    payload.pop("plan_digest", None)
    payload["graph_candidate_decision_ledger"] = _unstamped_plan_decisions(plan)
    for key in ("graph_candidate_receipt", "graph_traversal_receipt"):
        receipt = payload.get(key)
        if isinstance(receipt, dict):
            receipt.pop("plan_id", None)
            receipt.pop("plan_digest", None)
    return payload


def _validate_frozen_selected_plan(
    plan: Mapping[str, Any], *, section_id: str
) -> list[str]:
    """Validate the canonical plan seal and exact fact/skill/path projection."""
    failures: list[str] = []
    if str(plan.get("schema_version") or "") != CANONICAL_PLAN_SCHEMA_VERSION:
        failures.append("selected_graph_plan_schema_invalid")
    for failure in validate_canonical_section_plan(plan):
        failures.append(f"selected_graph_plan_contract_invalid:{failure}")

    plan_digest = str(plan.get("plan_digest") or "").strip()
    expected_digest = stable_digest(_canonical_plan_digest_payload(plan))
    if not plan_digest or plan_digest != expected_digest:
        failures.append("selected_graph_plan_digest_invalid")
    expected_plan_id = f"{section_id}:{expected_digest[:16]}"
    if str(plan.get("plan_id") or "") != expected_plan_id:
        failures.append("selected_graph_plan_id_invalid")

    for index, row in enumerate(plan.get("graph_candidate_decision_ledger") or []):
        if not isinstance(row, Mapping):
            continue
        if (
            str(row.get("plan_id") or "") != expected_plan_id
            or str(row.get("plan_digest") or "") != plan_digest
        ):
            failures.append(
                f"selected_graph_plan_decision_stamp_invalid:{index}"
            )
    for key in ("graph_candidate_receipt", "graph_traversal_receipt"):
        receipt = plan.get(key)
        if isinstance(receipt, Mapping) and (
            str(receipt.get("plan_id") or "") != expected_plan_id
            or str(receipt.get("plan_digest") or "") != plan_digest
        ):
            failures.append(f"selected_graph_plan_receipt_stamp_invalid:{key}")

    decisions = _unstamped_plan_decisions(plan)
    expected_candidate_receipt = build_candidate_receipt(
        section_id=section_id, decisions=decisions
    )
    candidate_receipt = plan.get("graph_candidate_receipt") or {}
    if not isinstance(candidate_receipt, Mapping):
        failures.append("selected_graph_plan_candidate_receipt_invalid")
    else:
        for key, expected in expected_candidate_receipt.items():
            if candidate_receipt.get(key) != expected:
                failures.append(
                    f"selected_graph_plan_candidate_receipt_mismatch:{key}"
                )

    traversal = plan.get("graph_traversal_receipt") or {}
    if not isinstance(traversal, Mapping):
        failures.append("selected_graph_plan_traversal_receipt_invalid")
    else:
        events = traversal.get("events")
        if not isinstance(events, list):
            failures.append("selected_graph_plan_traversal_events_invalid")
        else:
            if traversal.get("events_digest") != stable_digest(events):
                failures.append("selected_graph_plan_traversal_digest_invalid")
            if traversal.get("event_count") != len(events):
                failures.append("selected_graph_plan_traversal_count_invalid")

    selected_leaf_rows: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in decisions:
        if (
            str(row.get("candidate_type") or "") == "leaf_skill"
            and str(row.get("decision") or "") == "selected"
        ):
            key = (
                str(row.get("root_id") or "").strip(),
                str(row.get("candidate_id") or "").strip(),
            )
            if key in selected_leaf_rows:
                failures.append(
                    "selected_graph_plan_duplicate_fact_skill_path:"
                    + ":".join(key)
                )
            selected_leaf_rows[key] = row

    represented_pairs: set[tuple[str, str]] = set()
    for fact in plan.get("facts") or []:
        if not isinstance(fact, Mapping):
            failures.append("selected_graph_plan_fact_shape_invalid")
            continue
        fact_id = str(
            fact.get("fact_id") or fact.get("candidate_fact_id") or ""
        ).strip()
        for skill_id in _strings(
            fact.get("graph_skill_node_ids")
            or fact.get("selected_skill_ids")
            or fact.get("source_skill_ids")
        ):
            pair = (fact_id, skill_id)
            represented_pairs.add(pair)
            decision = selected_leaf_rows.get(pair)
            expected_path = f"root:{fact_id}/skill:{skill_id}"
            if (
                not decision
                or str(decision.get("parent_id") or "") != fact_id
                or str(decision.get("candidate_path_id") or "") != expected_path
                or decision.get("authority_pass") is not True
            ):
                failures.append(
                    "selected_graph_plan_fact_skill_path_mismatch:"
                    f"{fact_id}:{skill_id}"
                )
    orphan_pairs = sorted(set(selected_leaf_rows) - represented_pairs)
    failures.extend(
        "selected_graph_plan_orphan_selected_skill_path:" + ":".join(pair)
        for pair in orphan_pairs
    )
    return list(dict.fromkeys(failures))


def _selected_authority_violation(c03: Mapping[str, Any]) -> list[str]:
    violations: list[str] = []
    for row in c03.get("graph_candidate_decision_ledger") or []:
        if not isinstance(row, Mapping) or row.get("decision") != "selected":
            continue
        authority = row.get("authority") or {}
        if not isinstance(authority, Mapping) or authority.get("authority_pass") is not True:
            violations.append(str(row.get("candidate_path_id") or row.get("candidate_id") or ""))
    return sorted(violations)


def _graph_digest_from_plan(plan: Mapping[str, Any]) -> str:
    authority = plan.get("source_authority_contract") or {}
    if not isinstance(authority, Mapping):
        return ""
    return str(authority.get("graph_digest") or "").strip()


def _graph_digest_from_c03(c03: Mapping[str, Any]) -> str:
    selected = c03.get("selected_graph_plan_receipt") or {}
    if isinstance(selected, Mapping) and selected.get("graph_hash"):
        return str(selected.get("graph_hash") or "").strip()
    sqlite = c03.get("sqlite_selection_receipt") or {}
    if isinstance(sqlite, Mapping) and sqlite.get("graph_hash"):
        return str(sqlite.get("graph_hash") or "").strip()
    source = c03.get("source_authority_contract") or {}
    component_digests = sorted(
        {
            str(component.get("graph_digest") or "").strip()
            for component in (
                source.get("component_contracts") if isinstance(source, Mapping) else []
            )
            or []
            if isinstance(component, Mapping)
            and str(component.get("graph_digest") or "").strip()
        }
    )
    if len(component_digests) == 1:
        return component_digests[0]
    return ""


def _binding_fact_ids(c03: Mapping[str, Any]) -> list[str]:
    return sorted(
        {
            str(binding.get("fact_id") or "").strip()
            for binding in c03.get("bindings") or []
            if isinstance(binding, Mapping)
            and str(binding.get("fact_id") or "").strip()
        }
    )


def c03_handoff_snapshot(c03: Mapping[str, Any]) -> dict[str, Any]:
    """Seal the exact adopted C0.3 payload and its handoff-critical projections."""

    bindings = [
        dict(binding)
        for binding in c03.get("bindings") or []
        if isinstance(binding, Mapping)
    ]
    decisions = [
        dict(row)
        for row in c03.get("graph_candidate_decision_ledger") or []
        if isinstance(row, Mapping)
    ]
    traversal = c03.get("graph_traversal_receipt") or {}
    traversal_events = (
        [dict(row) for row in traversal.get("events") or [] if isinstance(row, Mapping)]
        if isinstance(traversal, Mapping)
        else []
    )
    fact_ids = _binding_fact_ids(c03)
    return {
        "adopted_c03_digest": stable_digest(dict(c03)),
        "adopted_graph_bindings_digest": stable_digest(bindings),
        "binding_fact_ids_after": fact_ids,
        "binding_fact_ids_digest_after": stable_digest(fact_ids),
        "graph_digest_after": _graph_digest_from_c03(c03),
        "candidate_decisions_digest": stable_digest(decisions),
        "traversal_events_digest": stable_digest(traversal_events),
    }


def _seal_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["receipt_digest"] = stable_digest(out)
    return out


def maybe_c06_weak_refine(
    *,
    section_id: str,
    role_family_key: str,
    route_ref: str,
    run_id: str,
    atoms: list[dict[str, Any]],
    initial_c03: dict[str, Any],
    initial_c05_receipt: Mapping[str, Any] | None = None,
    selected_graph_plan: Mapping[str, Any] | None,
    repo_root: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the adopted C0.3 result and a deterministic refinement receipt."""
    frozen_atoms = deepcopy(atoms)
    atom_scope = _atom_fingerprint(frozen_atoms)
    atom_payload_digest = stable_digest(frozen_atoms)
    requested_route_scope = {
        "section_id": str(section_id or ""),
        "role_family_key": str(role_family_key or ""),
        "route_ref": str(route_ref or ""),
    }
    initial_route_scope = {
        "section_id": str(initial_c03.get("section_id") or ""),
        "role_family_key": str(initial_c03.get("role_family_key") or ""),
        "route_ref": str(route_ref or ""),
    }
    requested_route_digest = stable_digest(requested_route_scope)
    initial_route_digest = stable_digest(initial_route_scope)
    initial = _coverage_snapshot(atoms=frozen_atoms, c03=initial_c03)
    plan = (
        deepcopy(dict(selected_graph_plan))
        if isinstance(selected_graph_plan, Mapping)
        else {}
    )
    plan_payload_digest_before = stable_digest(plan)
    plan_digest = str(plan.get("plan_digest") or "").strip()
    plan_graph_digest = _graph_digest_from_plan(plan)
    initial_graph_digest = _graph_digest_from_c03(initial_c03)
    initial_binding_fact_ids = _binding_fact_ids(initial_c03)
    initial_handoff_snapshot = c03_handoff_snapshot(initial_c03)
    initial_c05_support_status = str(
        (initial_c05_receipt or {}).get("support_status") or "UNKNOWN"
    ).upper()
    base: dict[str, Any] = {
        "schema_version": C06_SCHEMA_VERSION,
        "section_id": section_id,
        "run_id": run_id,
        "attempted": False,
        "attempt_count": 0,
        "max_attempts": C06_MAX_ATTEMPTS,
        "strategy": "frozen_section_graph_plan_direct_path_retry",
        "reentry_target": "C0.3",
        "route_scope": initial_route_scope,
        "requested_route_scope": requested_route_scope,
        "requested_route_digest": requested_route_digest,
        "route_digest_before": initial_route_digest,
        "route_digest_after": initial_route_digest,
        "route_changed": False,
        "atom_payload_digest_before": atom_payload_digest,
        "atom_payload_digest_after": atom_payload_digest,
        "atom_scope_digest_before": atom_scope["atom_scope_digest"],
        "atom_scope_digest_after": atom_scope["atom_scope_digest"],
        "fact_ids_digest_before": atom_scope["fact_ids_digest"],
        "fact_ids_digest_after": atom_scope["fact_ids_digest"],
        "binding_fact_ids_before": initial_binding_fact_ids,
        "binding_fact_ids_after": initial_binding_fact_ids,
        "binding_fact_ids_digest_before": stable_digest(initial_binding_fact_ids),
        "binding_fact_ids_digest_after": stable_digest(initial_binding_fact_ids),
        "adopted_c03_digest": initial_handoff_snapshot["adopted_c03_digest"],
        "adopted_graph_bindings_digest": initial_handoff_snapshot[
            "adopted_graph_bindings_digest"
        ],
        "authority_widened": False,
        "acl_scope_widened": False,
        "initial_coverage": initial,
        "final_coverage": initial,
        "initial_c05_support_status": initial_c05_support_status,
        "final_c05_support_status": initial_c05_support_status,
        "selected_graph_plan_digest": plan_digest,
        "selected_graph_plan_payload_digest_before": plan_payload_digest_before,
        "selected_graph_plan_payload_digest_after": plan_payload_digest_before,
        "selected_graph_plan_changed": False,
        "frozen_graph_digest": plan_graph_digest,
        "graph_digest_before": initial_graph_digest,
        "graph_digest_after": initial_graph_digest,
        "candidate_decisions_digest": initial_handoff_snapshot[
            "candidate_decisions_digest"
        ],
        "traversal_events_digest": initial_handoff_snapshot[
            "traversal_events_digest"
        ],
        "broad_fact_link_fallback_used": bool(
            initial_c03.get("broad_fact_link_fallback_used")
        ),
        "label_tag_proof_fallback_used": bool(
            initial_c03.get("label_tag_proof_fallback_used")
        ),
        "new_atoms_created": int(initial_c03.get("new_atoms_created") or 0),
        "failure_reasons": [],
    }
    initial_invariant_failures: list[str] = []
    if initial_route_scope != requested_route_scope:
        initial_invariant_failures.append("initial_c03_route_scope_mismatch")
    if initial_binding_fact_ids != atom_scope["fact_ids"]:
        initial_invariant_failures.append("initial_binding_fact_scope_mismatch")
    if plan_graph_digest:
        if not initial_graph_digest:
            initial_invariant_failures.append("initial_graph_snapshot_digest_missing")
        elif initial_graph_digest != plan_graph_digest:
            initial_invariant_failures.append("initial_graph_snapshot_digest_changed")
    if initial["status"] == "BLOCKED":
        initial_invariant_failures.append("initial_c03_contract_blocked")
        base.update(
            {
                "outcome": "BLOCKED",
                "pass": False,
                "failure_reasons": initial_invariant_failures,
            }
        )
        return initial_c03, _seal_receipt(base)
    needs_refinement = bool(
        initial["status"] in {"WEAK", "EMPTY"}
        or initial_c05_support_status in {"WEAK", "WEAK_WITH_CAVEATS", "EMPTY"}
    )
    if not needs_refinement:
        if initial["direct_supported_fact_ids"] != initial["proof_fact_ids"]:
            initial_invariant_failures.append("initial_direct_coverage_scope_mismatch")
        base.update(
            {
                "outcome": "NOT_REQUIRED" if not initial_invariant_failures else "BLOCKED",
                "pass": not initial_invariant_failures,
                "failure_reasons": initial_invariant_failures,
            }
        )
        return initial_c03, _seal_receipt(base)

    preflight_failures: list[str] = list(initial_invariant_failures)
    if not plan:
        preflight_failures.append("missing_frozen_selected_graph_plan")
    if not plan_digest:
        preflight_failures.append("missing_selected_graph_plan_digest")
    if str(plan.get("section_id") or "") != section_id:
        preflight_failures.append("selected_graph_plan_section_mismatch")
    if not plan_graph_digest:
        preflight_failures.append("missing_selected_graph_plan_graph_digest")
    preflight_failures.extend(
        _validate_frozen_selected_plan(plan, section_id=section_id)
    )
    plan_fact_ids = _selected_plan_fact_ids(plan)
    if plan_fact_ids != atom_scope["fact_ids"]:
        preflight_failures.append("selected_graph_plan_fact_scope_mismatch")
    if preflight_failures:
        base.update(
            {
                "outcome": "BLOCKED",
                "pass": False,
                "failure_reasons": preflight_failures,
            }
        )
        return initial_c03, _seal_receipt(base)

    base["attempted"] = True
    base["attempt_count"] = 1
    retry_atoms = deepcopy(frozen_atoms)
    retry_plan = deepcopy(plan)
    try:
        refined = expand_c03_graph_bindings(
            section_id=section_id,
            atoms=retry_atoms,
            role_family_key=role_family_key,
            repo_root=repo_root,
            run_id=run_id,
            strict_ranked_selection=False,
            selected_graph_plan=retry_plan,
        )
    except Exception as exc:  # guardian: allow-broad-exception -- C0.6 must seal any retry failure before PA
        base.update(
            {
                "outcome": "BLOCKED",
                "pass": False,
                "failure_reasons": [
                    f"refinement_execution_failed:{type(exc).__name__}"
                ],
            }
        )
        return initial_c03, _seal_receipt(base)
    final = _coverage_snapshot(atoms=retry_atoms, c03=refined)
    refined_atom_scope = _atom_fingerprint(retry_atoms)
    refined_atom_payload_digest = stable_digest(retry_atoms)
    caller_atom_payload_digest = stable_digest(atoms)
    plan_payload_digest_after = stable_digest(retry_plan)
    refined_route_scope = {
        "section_id": str(refined.get("section_id") or ""),
        "role_family_key": str(refined.get("role_family_key") or ""),
        "route_ref": str(route_ref or ""),
    }
    graph_after = _graph_digest_from_c03(refined)
    selected_authority_violations = _selected_authority_violation(refined)
    refined_fact_ids = _binding_fact_ids(refined)
    refined_handoff_snapshot = c03_handoff_snapshot(refined)
    invariant_failures: list[str] = []
    if stable_digest(refined_route_scope) != initial_route_digest:
        invariant_failures.append("route_scope_changed")
    if refined_atom_payload_digest != atom_payload_digest:
        invariant_failures.append("atom_payload_changed_during_refinement")
    if caller_atom_payload_digest != atom_payload_digest:
        invariant_failures.append("caller_atom_payload_changed_during_refinement")
    if plan_payload_digest_after != plan_payload_digest_before:
        invariant_failures.append("selected_graph_plan_changed_during_refinement")
    if refined_atom_scope != atom_scope or refined_fact_ids != atom_scope["fact_ids"]:
        invariant_failures.append("atom_or_fact_scope_changed")
    if final["direct_supported_fact_ids"] != final["proof_fact_ids"]:
        invariant_failures.append("direct_coverage_scope_mismatch")
    if graph_after != plan_graph_digest:
        invariant_failures.append("graph_snapshot_digest_changed")
    if selected_authority_violations:
        invariant_failures.append(
            "selected_candidate_failed_authority:" + ",".join(selected_authority_violations)
        )
    if refined.get("new_atoms_created") not in (0, None):
        invariant_failures.append("refinement_created_new_atoms")
    if refined.get("broad_fact_link_fallback_used") is True:
        invariant_failures.append("broad_fact_link_fallback_used")
    if refined.get("label_tag_proof_fallback_used") is True:
        invariant_failures.append("label_tag_proof_fallback_used")
    if final["status"] != "PASS":
        invariant_failures.append("refinement_did_not_restore_full_direct_coverage")

    base.update(
        {
            "route_digest_after": stable_digest(refined_route_scope),
            "route_changed": stable_digest(refined_route_scope) != initial_route_digest,
            "atom_payload_digest_after": refined_atom_payload_digest,
            "atom_scope_digest_after": refined_atom_scope["atom_scope_digest"],
            "fact_ids_digest_after": stable_digest(refined_fact_ids),
            "binding_fact_ids_after": refined_fact_ids,
            "binding_fact_ids_digest_after": stable_digest(refined_fact_ids),
            "adopted_c03_digest": refined_handoff_snapshot["adopted_c03_digest"],
            "adopted_graph_bindings_digest": refined_handoff_snapshot[
                "adopted_graph_bindings_digest"
            ],
            "authority_widened": bool(selected_authority_violations),
            "acl_scope_widened": refined_atom_scope != atom_scope,
            "selected_graph_plan_payload_digest_after": plan_payload_digest_after,
            "selected_graph_plan_changed": (
                plan_payload_digest_after != plan_payload_digest_before
            ),
            "final_coverage": final,
            "graph_digest_after": graph_after,
            "broad_fact_link_fallback_used": bool(
                refined.get("broad_fact_link_fallback_used")
            ),
            "label_tag_proof_fallback_used": bool(
                refined.get("label_tag_proof_fallback_used")
            ),
            "new_atoms_created": int(refined.get("new_atoms_created") or 0),
            "candidate_decisions_digest": refined_handoff_snapshot[
                "candidate_decisions_digest"
            ],
            "traversal_events_digest": refined_handoff_snapshot[
                "traversal_events_digest"
            ],
            "failure_reasons": invariant_failures,
            "outcome": "PASS" if not invariant_failures else "BLOCKED",
            "pass": not invariant_failures,
        }
    )
    return (refined if not invariant_failures else initial_c03), _seal_receipt(base)


def finalize_c06_after_c05(
    receipt: Mapping[str, Any], *, final_c05_receipt: Mapping[str, Any]
) -> dict[str, Any]:
    """Bind the adopted/rebuilt C0.5 diagnosis into the C0.6 receipt."""
    out = dict(receipt)
    out.pop("receipt_digest", None)
    final_status = str(final_c05_receipt.get("support_status") or "UNKNOWN").upper()
    out["final_c05_support_status"] = final_status
    failures = _strings(out.get("failure_reasons"))
    if final_status != "PASS" and "final_c05_support_not_pass" not in failures:
        failures.append("final_c05_support_not_pass")
    if failures:
        out["failure_reasons"] = failures
        out["outcome"] = "BLOCKED"
        out["pass"] = False
    return _seal_receipt(out)


__all__ = [
    "C06_MAX_ATTEMPTS",
    "C06_RECEIPT_ARTIFACT",
    "C06_SCHEMA_VERSION",
    "c03_handoff_snapshot",
    "finalize_c06_after_c05",
    "maybe_c06_weak_refine",
]
