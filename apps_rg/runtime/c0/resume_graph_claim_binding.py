"""Exact final-claim binding to the frozen resume-graph allocation.

This is a post-materialization, pre-X3 authority gate.  It does not select or
repair evidence.  It proves that every claim already emitted by a lane is
visible, source-bound, path-bound, and (when numeric) bound to the exact metric
value/unit reserved by the immutable allocation plan.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    GraphClaimBindingV1,
    stable_digest,
)
from apps_rg.runtime.c0.resume_graph_allocation import extract_exact_metric_value_unit

GRAPH_CLAIM_BINDINGS_ARTIFACT = "graph_claim_bindings.json"
GRAPH_CLAIM_BINDING_CONTRACT_SCHEMA = "resume_graph_claim_binding_contract_v1"
GRAPH_CLAIM_BINDING_GATE_ID = "x2_resume_graph_claim_binding"

_WORD_RE = re.compile(r"[a-z0-9]+")
_CAUSAL_RE = re.compile(
    r"\b(?:drove|driving|yielded|yielding|resulted|resulting|led\s+to|"
    r"increased|increasing|reduced|reducing|generated|delivered)\b",
    re.I,
)
_VISIBLE_METRIC_RE = re.compile(
    r"(?:\$|\busd\s*)\d+(?:\.\d+)?\s*(?:m|million|b|billion)?\b|"
    r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|percentage\b|x\b|times\b)|"
    r"\b\d+(?:\.\d+)?\+?\s*(?:countries|clients|customers|partners|teams|"
    r"workflows|platforms|products|programs|markets|regions|applications|systems)\b",
    re.I,
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _strings(values: Iterable[Any] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or ():
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _text_key(value: str) -> str:
    return " ".join(_WORD_RE.findall(str(value or "").casefold()))


def _claim_text(row: Mapping[str, Any]) -> str:
    return str(row.get("claim_text") or row.get("claim") or "").strip()


def _claim_rows(artifact_dir: Path, l2: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = _load_json(artifact_dir / "claim_ledger.json")
    if not isinstance(raw, list):
        raw = l2.get("claim_ledger")
    rows = [dict(row) for row in raw or [] if isinstance(row, Mapping)]

    canonical = _load_json(artifact_dir / "canonical_claim_ledger_v2.json")
    canonical_rows = canonical.get("claims") if isinstance(canonical, Mapping) else []
    for index, row in enumerate(rows):
        if not str(row.get("claim_id") or "").strip() and index < len(canonical_rows or []):
            canonical_row = canonical_rows[index]
            if isinstance(canonical_row, Mapping):
                row["claim_id"] = str(canonical_row.get("claim_id") or "")

    bullets = [row for row in l2.get("bullets") or [] if isinstance(row, Mapping)]
    by_text = {
        _text_key(str(row.get("bullet_text") or "")): str(row.get("bullet_id") or "")
        for row in bullets
        if str(row.get("bullet_text") or "").strip()
    }
    for row in rows:
        bullet_id = by_text.get(_text_key(_claim_text(row)), "")
        if bullet_id:
            row.setdefault("bullet_id", bullet_id)
    return rows


def _resolve_selected_plan(
    artifact_dir: Path,
    l2: Mapping[str, Any],
) -> dict[str, Any]:
    disk = _load_json(artifact_dir / "selected_fact_plan.json")
    if isinstance(disk, Mapping):
        return dict(disk)
    embedded = l2.get("selected_fact_plan")
    return dict(embedded) if isinstance(embedded, Mapping) else {}


def _allocation_context(
    artifact_dir: Path,
    *,
    section_id: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]] | None:
    l2_raw = _load_json(artifact_dir / "l2_output.json")
    l2 = dict(l2_raw) if isinstance(l2_raw, Mapping) else {}
    plan = _resolve_selected_plan(artifact_dir, l2)
    digest = str(plan.get("allocation_plan_digest") or "").strip()
    assignments = [
        dict(row)
        for row in plan.get("allocation_assignments") or []
        if isinstance(row, Mapping) and str(row.get("section_id") or "") == section_id
    ]
    if not digest and not assignments:
        return None
    if not digest or not assignments:
        return l2, plan, []
    return l2, plan, assignments


def _fact_aliases_by_root(plan: Mapping[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for raw in plan.get("facts") or []:
        if not isinstance(raw, Mapping):
            continue
        root_id = str(
            raw.get("role_episode_bundle_id")
            or raw.get("fact_id")
            or raw.get("candidate_fact_id")
            or ""
        ).strip()
        if not root_id:
            continue
        aliases = out.setdefault(root_id, set())
        aliases.update(
            _strings(
                [
                    root_id,
                    raw.get("fact_id"),
                    raw.get("candidate_fact_id"),
                    *list(raw.get("allowed_graph_evidence_ids") or []),
                    *list(raw.get("linked_identity_fact_ids") or []),
                    *list(raw.get("linked_source_fact_ids") or []),
                    *list(raw.get("graph_skill_node_ids") or []),
                    *list(raw.get("metric_outcome_ids") or []),
                ]
            )
        )
    return out


def _assignment_aliases(
    assignment: Mapping[str, Any],
    *,
    aliases_by_root: Mapping[str, set[str]],
) -> set[str]:
    root_id = str(assignment.get("root_id") or "").strip()
    aliases = set(aliases_by_root.get(root_id) or set())
    aliases.update(
        _strings(
            [
                assignment.get("claim_unit_id"),
                assignment.get("fact_id"),
                root_id,
                assignment.get("skill_id"),
                assignment.get("metric_outcome_id"),
                *list(assignment.get("citation_refs") or []),
            ]
        )
    )
    claim_unit = str(assignment.get("claim_unit_id") or "")
    if ":" in claim_unit:
        aliases.add(claim_unit.rsplit(":", 1)[-1])
    return aliases


def _visible_output_text(artifact_dir: Path, l2: Mapping[str, Any]) -> str:
    command = artifact_dir / "command_output.txt"
    if command.is_file():
        try:
            text = command.read_text(encoding="utf-8").strip()
        except OSError:
            text = ""
        if text:
            return text
    for path in sorted(artifact_dir.glob("*_output.txt")):
        try:
            text = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text
    for key in ("resume_display_text", "headline_line", "narrative_sentence"):
        text = str(l2.get(key) or "").strip()
        if text:
            return text
    bullets = [
        str(row.get("bullet_text") or "").strip()
        for row in l2.get("bullets") or []
        if isinstance(row, Mapping) and str(row.get("bullet_text") or "").strip()
    ]
    return "\n".join(bullets)


def _explicit_claim_unit(
    row: Mapping[str, Any],
    *,
    section_id: str,
) -> str:
    explicit = str(row.get("claim_unit_id") or "").strip()
    if explicit:
        return explicit
    bullet_id = str(row.get("bullet_id") or "").strip()
    if bullet_id:
        return f"{section_id}:{bullet_id}"
    for source_id in _strings(row.get("source_fact_ids")):
        if source_id.startswith("bul_"):
            return f"{section_id}:{source_id}"
    return ""


def _select_assignments_for_claim(
    row: Mapping[str, Any],
    *,
    section_id: str,
    assignments: Sequence[Mapping[str, Any]],
    aliases: Mapping[str, set[str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    failures: list[str] = []
    sources = set(_strings(row.get("source_fact_ids")))
    if not sources:
        return [], ["claim_source_fact_ids_missing"]
    explicit = _explicit_claim_unit(row, section_id=section_id)
    selected: list[dict[str, Any]] = []
    if explicit:
        selected = [
            dict(assignment)
            for assignment in assignments
            if str(assignment.get("claim_unit_id") or "") == explicit
        ]
        if not selected:
            failures.append("claim_unit_not_allocated")
    if not selected:
        selected = [
            dict(assignment)
            for assignment in assignments
            if sources.intersection(aliases[str(assignment.get("claim_unit_id") or "")])
        ]

    text_key = _text_key(_claim_text(row))
    label_matches = [
        assignment
        for assignment in selected
        if _text_key(str(assignment.get("skill_label") or ""))
        and (
            _text_key(str(assignment.get("skill_label") or "")) in text_key
            or text_key in _text_key(str(assignment.get("skill_label") or ""))
        )
    ]
    if label_matches:
        selected = label_matches
    if not selected:
        failures.append("claim_has_no_allocated_graph_path")
        return [], failures

    covered: set[str] = set()
    for assignment in selected:
        covered.update(aliases[str(assignment.get("claim_unit_id") or "")])
    uncovered = sorted(source for source in sources if source not in covered)
    if uncovered:
        failures.append("orphan_source_ids:" + ",".join(uncovered))
    return selected, failures


def _aggregate_score(
    assignments: Sequence[Mapping[str, Any]],
    key: str,
    *,
    mode: str = "min",
) -> float:
    values = [float(row.get(key) or 0.0) for row in assignments]
    if not values:
        return 0.0
    if mode == "mean":
        return sum(values) / len(values)
    return min(values)


def _binding_for_claim(
    row: Mapping[str, Any],
    *,
    ordinal: int,
    section_id: str,
    allocation_digest: str,
    assignments: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any] | None, list[str]]:
    failures: list[str] = []
    text = _claim_text(row)
    if not text:
        return None, ["visible_claim_text_missing"]
    metric_surfaces = _VISIBLE_METRIC_RE.findall(text)
    if len(metric_surfaces) > 1:
        failures.append("multiple_rendered_metrics_in_one_claim")
    metric_value, metric_unit = extract_exact_metric_value_unit(text)
    metric_assignments = [
        assignment
        for assignment in assignments
        if str(assignment.get("metric_outcome_id") or "").strip()
    ]
    bound_metric: Mapping[str, Any] | None = None
    if metric_value or metric_unit:
        exact = [
            assignment
            for assignment in metric_assignments
            if str(assignment.get("metric_value") or "") == metric_value
            and str(assignment.get("metric_unit") or "") == metric_unit
        ]
        if len(exact) != 1:
            failures.append("rendered_metric_exact_value_unit_binding_failed")
        else:
            bound_metric = exact[0]
    elif any(str(row.get("metric_outcome_id") or "").strip() for row in assignments):
        # A reserved metric may support the claim, but it is not counted as rendered.
        bound_metric = None

    roots = {str(row.get("root_id") or "") for row in assignments if row.get("root_id")}
    if len(roots) > 1 and _CAUSAL_RE.search(text):
        failures.append("causal_claim_merges_unrelated_graph_roots")
    if failures:
        return None, failures

    claim_id = str(row.get("claim_id") or "").strip()
    claim_unit_id = claim_id or f"{section_id}:visible-claim:{ordinal:02d}"
    binding = GraphClaimBindingV1(
        section_id=section_id,
        claim_unit_id=claim_unit_id,
        visible_claim_text=text,
        allocation_plan_digest=allocation_digest,
        skill_ids=tuple(_strings(row.get("skill_id") for row in assignments)),
        fact_ids=tuple(_strings(row.get("fact_id") for row in assignments)),
        graph_path_ids=tuple(
            _strings(
                path
                for assignment in assignments
                for path in assignment.get("graph_path_ids") or []
            )
        ),
        edge_ids=tuple(
            _strings(
                edge
                for assignment in assignments
                for edge in assignment.get("edge_ids") or []
            )
        ),
        citation_refs=tuple(
            _strings(
                ref
                for assignment in assignments
                for ref in assignment.get("citation_refs") or []
            )
        ),
        metric_outcome_id=str((bound_metric or {}).get("metric_outcome_id") or ""),
        metric_value=str((bound_metric or {}).get("metric_value") or ""),
        metric_unit=str((bound_metric or {}).get("metric_unit") or ""),
        normalized_metric_signature=str(
            (bound_metric or {}).get("normalized_metric_signature") or ""
        ),
        proof_strength_raw=_aggregate_score(assignments, "proof_strength_raw"),
        target_alignment_score=_aggregate_score(
            assignments, "target_alignment_score", mode="mean"
        ),
        claim_entailment_score=_aggregate_score(assignments, "claim_entailment_score"),
        metric_binding_score=(
            _aggregate_score([bound_metric], "metric_binding_score")
            if bound_metric is not None
            else 0.0
        ),
        path_confidence_raw=_aggregate_score(assignments, "path_confidence_raw"),
        source_independence_score=_aggregate_score(
            assignments, "source_independence_score"
        ),
        selection_margin=_aggregate_score(assignments, "selection_margin"),
    ).to_dict()
    binding["claim_source_fact_ids"] = _strings(row.get("source_fact_ids"))
    binding["allocation_claim_unit_ids"] = _strings(
        row.get("claim_unit_id") for row in assignments
    )
    binding["binding_status"] = "PASS"
    return binding, []


def _stamp_object(path: Path, fields: Mapping[str, Any]) -> None:
    raw = _load_json(path)
    if not isinstance(raw, Mapping):
        return
    doc = dict(raw)
    doc.update(fields)
    _write_json(path, doc)


def _stamp_x2(
    path: Path,
    *,
    contract: Mapping[str, Any],
) -> None:
    raw = _load_json(path)
    doc = dict(raw) if isinstance(raw, Mapping) else {}
    gates = [
        dict(row)
        for row in doc.get("gates") or []
        if isinstance(row, Mapping)
        and str(row.get("gate_id") or "") != GRAPH_CLAIM_BINDING_GATE_ID
    ]
    gate = {
        "gate_id": GRAPH_CLAIM_BINDING_GATE_ID,
        "gate_type": "deterministic_graph_authority",
        "pass": contract.get("pass") is True,
        "observed_value": {
            "allocation_plan_digest": contract.get("allocation_plan_digest"),
            "claim_count": contract.get("claim_count"),
            "bound_claim_count": contract.get("bound_claim_count"),
            "binding_coverage": contract.get("binding_coverage"),
            "metric_exactness_pass": contract.get("metric_exactness_pass"),
            "orphan_allocation_claim_unit_ids": contract.get(
                "orphan_allocation_claim_unit_ids"
            ),
            "failure_reasons": contract.get("failure_reasons"),
        },
        "threshold": {
            "binding_coverage": 1.0,
            "metric_exactness": 1.0,
            "orphan_allocations": 0,
        },
        "failure_reason": "" if contract.get("pass") is True else "resume_graph_claim_binding_failed",
        "evidence_ref": GRAPH_CLAIM_BINDINGS_ARTIFACT,
    }
    gates.append(gate)
    failed = [str(row.get("gate_id") or "") for row in gates if row.get("pass") is not True]
    doc.update(
        {
            "gates": gates,
            "failed_gates": failed,
            "x2_passed": sum(1 for row in gates if row.get("pass") is True),
            "x2_failed": len(failed),
            "total_x2_gates": len(gates),
            "resume_graph_allocation_plan_digest": contract.get(
                "allocation_plan_digest"
            ),
            "graph_claim_binding_contract_digest": contract.get("contract_digest"),
            "graph_claim_bindings_ref": GRAPH_CLAIM_BINDINGS_ARTIFACT,
        }
    )
    _write_json(path, doc)


def _persist_binding_contract(
    artifact_dir: Path,
    *,
    l2: Mapping[str, Any],
    plan: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    _write_json(artifact_dir / GRAPH_CLAIM_BINDINGS_ARTIFACT, contract)
    fields = {
        "resume_graph_allocation_plan_digest": contract.get("allocation_plan_digest"),
        "graph_claim_binding_contract_digest": contract.get("contract_digest"),
        "graph_claim_bindings_ref": GRAPH_CLAIM_BINDINGS_ARTIFACT,
    }
    l2_doc = dict(l2)
    l2_doc.update(fields)
    l2_doc["graph_claim_bindings"] = list(contract.get("bindings") or [])
    _write_json(artifact_dir / "l2_output.json", l2_doc)

    # ``selected_fact_plan.json`` is already sealed with the allocation digest.
    # Do not add downstream fields to it: that would invalidate its canonical
    # section-plan digest after selection.
    for name in (
        "canonical_claim_ledger_v2.json",
        "x1d_llm_judge_outputs.json",
        "prompt_selection_trace.json",
    ):
        _stamp_object(artifact_dir / name, fields)
    _stamp_x2(artifact_dir / "x2_gate_outputs.json", contract=contract)


def bind_final_claims_to_resume_graph_allocation(
    artifact_dir: Path,
    *,
    section_id: str,
) -> dict[str, Any]:
    """Bind every final claim or emit a sealed deterministic failure contract.

    Lanes that have not entered the hardened allocation path are left unchanged;
    the active path is detected only by the immutable allocation digest and its
    section assignment slice on ``selected_fact_plan.json``.
    """
    runtime_payload = _load_json(artifact_dir / "runtime_payload.json")
    if isinstance(runtime_payload, Mapping) and runtime_payload.get(
        "blocked_before_provider"
    ) is True:
        return {
            "schema_version": GRAPH_CLAIM_BINDING_CONTRACT_SCHEMA,
            "section_id": section_id,
            "active": False,
            "status": "NOT_APPLICABLE_PRE_PROVIDER_BLOCK",
            "runtime_generation_status": str(
                runtime_payload.get("runtime_generation_status") or ""
            ),
            "pass": True,
        }
    context = _allocation_context(artifact_dir, section_id=section_id)
    if context is None:
        return {
            "schema_version": GRAPH_CLAIM_BINDING_CONTRACT_SCHEMA,
            "section_id": section_id,
            "active": False,
            "status": "NOT_APPLICABLE_LEGACY_OR_UNALLOCATED_SECTION_RUN",
            "pass": True,
        }
    l2, plan, assignments = context
    allocation_digest = str(plan.get("allocation_plan_digest") or "")
    claims = _claim_rows(artifact_dir, l2)
    output_text = _visible_output_text(artifact_dir, l2)
    aliases_by_root = _fact_aliases_by_root(plan)
    assignment_aliases = {
        str(row.get("claim_unit_id") or ""): _assignment_aliases(
            row, aliases_by_root=aliases_by_root
        )
        for row in assignments
    }

    failures: list[str] = []
    if not allocation_digest:
        failures.append("allocation_plan_digest_missing")
    if not assignments:
        failures.append("section_allocation_assignments_missing")
    if not claims:
        failures.append("visible_claim_ledger_missing")
    if not output_text:
        failures.append("final_materialized_output_missing")
    # C0/FEC and PA are upstream immutable boundaries.  Their allocation digest
    # must already have been present before generation; never repair or stamp it
    # after L2 text exists.
    for artifact_name in (
        "final_evidence_contract.json",
        "compiled_prompt_artifact.json",
    ):
        artifact = _load_json(artifact_dir / artifact_name)
        if not isinstance(artifact, Mapping):
            continue
        observed = str(artifact.get("resume_graph_allocation_plan_digest") or "")
        if observed != allocation_digest:
            failures.append(
                f"{artifact_name}:upstream_allocation_digest_mismatch"
            )

    bindings: list[dict[str, Any]] = []
    used_claim_units: set[str] = set()
    output_key = _text_key(output_text)
    for index, claim in enumerate(claims, start=1):
        text = _claim_text(claim)
        if text and _text_key(text) not in output_key:
            failures.append(f"claim_{index}:claim_not_present_in_final_materialized_output")
        selected, select_failures = _select_assignments_for_claim(
            claim,
            section_id=section_id,
            assignments=assignments,
            aliases=assignment_aliases,
        )
        for reason in select_failures:
            failures.append(f"claim_{index}:{reason}")
        if not selected:
            continue
        binding, binding_failures = _binding_for_claim(
            claim,
            ordinal=index,
            section_id=section_id,
            allocation_digest=allocation_digest,
            assignments=selected,
        )
        for reason in binding_failures:
            failures.append(f"claim_{index}:{reason}")
        if binding is None:
            continue
        bindings.append(binding)
        used_claim_units.update(binding.get("allocation_claim_unit_ids") or [])

    allocated_claim_units = {
        str(row.get("claim_unit_id") or "") for row in assignments if row.get("claim_unit_id")
    }
    orphan_claim_units = sorted(allocated_claim_units - used_claim_units)
    if orphan_claim_units:
        failures.append("orphan_allocation_claim_units:" + ",".join(orphan_claim_units))
    metric_exactness_pass = not any(
        "metric" in reason for reason in failures
    )
    binding_coverage = len(bindings) / len(claims) if claims else 0.0
    pass_ = (
        not failures
        and bool(claims)
        and len(bindings) == len(claims)
        and not orphan_claim_units
    )
    contract: dict[str, Any] = {
        "schema_version": GRAPH_CLAIM_BINDING_CONTRACT_SCHEMA,
        "section_id": section_id,
        "active": True,
        "status": "PASS" if pass_ else "FAIL",
        "allocation_scope": str(plan.get("allocation_scope") or ""),
        "allocation_plan_digest": allocation_digest,
        "claim_count": len(claims),
        "bound_claim_count": len(bindings),
        "binding_coverage": round(binding_coverage, 6),
        "metric_exactness_pass": metric_exactness_pass,
        "allocated_claim_unit_count": len(allocated_claim_units),
        "bound_allocation_claim_unit_count": len(used_claim_units),
        "orphan_allocation_claim_unit_ids": orphan_claim_units,
        "failure_reasons": sorted(set(failures)),
        "bindings": bindings,
        "rendered_claim_reconciliation_pass": not any(
            "final_materialized_output" in reason or "claim_not_present" in reason
            for reason in failures
        ),
        "durable_graph_state_mutated": False,
        "pass": pass_,
    }
    contract["bindings_digest"] = stable_digest(bindings)
    contract["contract_digest"] = stable_digest(contract)
    _persist_binding_contract(
        artifact_dir,
        l2=l2,
        plan=plan,
        contract=contract,
    )
    return contract


__all__ = [
    "GRAPH_CLAIM_BINDINGS_ARTIFACT",
    "GRAPH_CLAIM_BINDING_CONTRACT_SCHEMA",
    "GRAPH_CLAIM_BINDING_GATE_ID",
    "bind_final_claims_to_resume_graph_allocation",
]
