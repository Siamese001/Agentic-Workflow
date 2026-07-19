"""Build the deterministic, evidence-bearing C0.3 skill assertion corpus."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any

CORPUS_SCHEMA_VERSION = "apps_rg.c03_skill_assertion_corpus.v1"
ASSERTION_SCHEMA_VERSION = "apps_rg.c03_skill_assertion.v1"


class SkillAssertionCorpusError(ValueError):
    """Raised when assertion authority cannot be derived exactly."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _walk_objects(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_objects(child)


def _evidence_index(
    candidate_fact_payload: Mapping[str, Any],
    base_resume_payload: Mapping[str, Any],
) -> dict[str, tuple[str, dict[str, Any]]]:
    index: dict[str, tuple[str, dict[str, Any]]] = {}
    for raw in candidate_fact_payload.get("candidate_facts") or []:
        if not isinstance(raw, dict):
            continue
        fact_id = str(raw.get("candidate_fact_id") or "").strip()
        if fact_id:
            index[fact_id] = ("candidate_fact", raw)

    id_keys = {
        "bullet_id",
        "candidate_fact_id",
        "certification_id",
        "evidence_id",
        "fact_id",
    }
    for raw in _walk_objects(base_resume_payload):
        for key in id_keys:
            source_id = str(raw.get(key) or "").strip()
            if source_id and source_id not in index:
                index[source_id] = ("base_resume_fact", raw)
    return index


def _evidence_summary(raw: Mapping[str, Any]) -> str:
    for key in ("proof_text", "claim_text", "text", "bullet", "description", "name", "title"):
        value = str(raw.get(key) or "").strip()
        if value:
            return value
    return ""


def _source_locators(raw: Mapping[str, Any], row: Mapping[str, Any]) -> list[str]:
    values: set[str] = set()
    for key in ("source_resume_variants", "source_resume_files", "evidence_sources"):
        values.update(_strings(raw.get(key)))
    values.update(_strings(row.get("source_resume_files")))
    for key in ("source_ledger_ref", "source_authority"):
        value = str(row.get(key) or "").strip()
        if value:
            values.add(value)
    return sorted(values)


def _label(row: Mapping[str, Any], node: Mapping[str, Any]) -> str:
    for value in (
        node.get("label"),
        row.get("capability"),
        row.get("subpillar"),
        row.get("skill_id"),
    ):
        text = str(value or "").strip()
        if text:
            return text
    raise SkillAssertionCorpusError("skill assertion has no semantic label")


def _embedding_text(semantic_card: Mapping[str, Any]) -> str:
    fields = [
        f"Skill: {semantic_card['label']}",
        f"Capability: {semantic_card['capability']}",
        f"Description: {semantic_card['description']}",
        f"Allowed phrases: {'; '.join(semantic_card['allowed_phrases'])}",
        f"Pillar: {semantic_card['pillar']}",
        f"Domain: {semantic_card['domain_id']}",
        f"Career epoch: {semantic_card['career_epoch']}",
        f"Career track: {semantic_card['career_track_id']}",
        f"Evidence: {'; '.join(semantic_card['evidence_summaries'])}",
    ]
    return "\n".join(fields)


def build_skill_assertion_corpus(
    *,
    graph_payload: Mapping[str, Any],
    candidate_fact_payload: Mapping[str, Any],
    base_resume_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one assertion for each explicitly retrieval-eligible skill row."""
    graph_sha256 = canonical_sha256(graph_payload)
    candidate_fact_sha256 = canonical_sha256(candidate_fact_payload)
    base_resume_sha256 = canonical_sha256(base_resume_payload)
    evidence = _evidence_index(candidate_fact_payload, base_resume_payload)
    nodes = {
        str(node.get("node_id") or ""): node
        for node in graph_payload.get("graph_nodes") or []
        if isinstance(node, dict)
    }
    assertions: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []

    rows = sorted(
        (row for row in graph_payload.get("skill_rows") or [] if isinstance(row, dict)),
        key=lambda row: str(row.get("skill_id") or ""),
    )
    for row in rows:
        skill_id = str(row.get("skill_id") or "").strip()
        if not skill_id:
            raise SkillAssertionCorpusError("blank skill_id")
        skill_row_sha256 = canonical_sha256(row)
        if row.get("retrieval_eligible") is not True:
            reason = str(row.get("retrieval_ineligibility_reason") or "").strip()
            if not reason:
                raise SkillAssertionCorpusError(f"{skill_id}: exclusion reason missing")
            exclusions.append(
                {
                    "skill_id": skill_id,
                    "reason": reason,
                    "skill_row_sha256": skill_row_sha256,
                }
            )
            continue

        fact_ids = _strings(row.get("fact_id_links"))
        if not fact_ids:
            raise SkillAssertionCorpusError(f"{skill_id}: eligible assertion has no facts")
        lineage: list[dict[str, Any]] = []
        summaries: list[str] = []
        for fact_id in fact_ids:
            resolved = evidence.get(fact_id)
            if resolved is None:
                raise SkillAssertionCorpusError(f"{skill_id}: unresolved fact {fact_id}")
            source_kind, raw = resolved
            summary = _evidence_summary(raw)
            if summary:
                summaries.append(summary)
            lineage.append(
                {
                    "source_id": fact_id,
                    "source_kind": source_kind,
                    "sha256": canonical_sha256(raw),
                    "locators": _source_locators(raw, row),
                }
            )

        node = nodes.get(skill_id)
        if node is None:
            raise SkillAssertionCorpusError(f"{skill_id}: graph identity missing")
        label = _label(row, node)
        semantic_card = {
            "label": label,
            "capability": str(row.get("capability") or row.get("subpillar") or label),
            "description": str(node.get("description") or "").strip(),
            "allowed_phrases": _strings(row.get("allowed_phrases")),
            "pillar": str(row.get("pillar") or "").strip(),
            "domain_id": str(row.get("domain_id") or "").strip(),
            "career_epoch": str(row.get("career_epoch") or "").strip(),
            "career_track_id": str(row.get("career_track_id") or "").strip(),
            "evidence_summaries": sorted(set(summaries)),
        }
        allowed_sections = _strings(row.get("allowed_sections"))
        authority_envelope = {
            "graph_sha256": graph_sha256,
            "skill_row_sha256": skill_row_sha256,
            "fact_bindings": [
                {"source_id": item["source_id"], "sha256": item["sha256"]}
                for item in lineage
            ],
            "lifecycle": str(row.get("activation_status") or ""),
            "retrieval_eligible": True,
            "allowed_sections": allowed_sections,
        }
        assertion: dict[str, Any] = {
            "schema_version": ASSERTION_SCHEMA_VERSION,
            "assertion_id": skill_id,
            "skill_id": skill_id,
            "semantic_card": semantic_card,
            "embedding_text": _embedding_text(semantic_card),
            "fact_links": fact_ids,
            "source_lineage": lineage,
            "lifecycle": str(row.get("activation_status") or ""),
            "allowed_sections": allowed_sections,
            "authority_envelope_sha256": canonical_sha256(authority_envelope),
            "skill_row_sha256": skill_row_sha256,
        }
        assertion["assertion_document_sha256"] = canonical_sha256(assertion)
        assertions.append(assertion)

    corpus: dict[str, Any] = {
        "schema_version": CORPUS_SCHEMA_VERSION,
        "source_digests": {
            "graph_sha256": graph_sha256,
            "candidate_fact_ledger_sha256": candidate_fact_sha256,
            "base_resume_sha256": base_resume_sha256,
        },
        "counts": {
            "canonical_skill_count": len(rows),
            "eligible_assertion_count": len(assertions),
            "non_retrieval_eligible_count": len(exclusions),
        },
        "assertions": assertions,
        "exclusions": exclusions,
    }
    corpus["corpus_sha256"] = canonical_sha256(corpus)
    return corpus


def validate_skill_assertion_corpus(
    corpus: Mapping[str, Any],
    *,
    graph_payload: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    unsigned = dict(corpus)
    observed_digest = str(unsigned.pop("corpus_sha256", ""))
    if observed_digest != canonical_sha256(unsigned):
        issues.append("CORPUS_DIGEST_MISMATCH")

    graph_sha256 = canonical_sha256(graph_payload)
    if (corpus.get("source_digests") or {}).get("graph_sha256") != graph_sha256:
        issues.append("GRAPH_DIGEST_MISMATCH")
    graph_rows = {
        str(row.get("skill_id") or ""): row
        for row in graph_payload.get("skill_rows") or []
        if isinstance(row, dict)
    }
    assertion_ids: set[str] = set()
    for raw in corpus.get("assertions") or []:
        if not isinstance(raw, dict):
            issues.append("ASSERTION_NOT_OBJECT")
            continue
        assertion_id = str(raw.get("assertion_id") or "")
        if assertion_id in assertion_ids:
            issues.append(f"DUPLICATE_ASSERTION:{assertion_id}")
        assertion_ids.add(assertion_id)
        unsigned_assertion = dict(raw)
        digest = str(unsigned_assertion.pop("assertion_document_sha256", ""))
        if digest != canonical_sha256(unsigned_assertion):
            issues.append(f"ASSERTION_DIGEST_MISMATCH:{assertion_id}")
        graph_row = graph_rows.get(assertion_id)
        if graph_row is None:
            issues.append(f"ORPHAN_ASSERTION:{assertion_id}")
        elif graph_row.get("retrieval_eligible") is not True:
            issues.append(f"UNAUTHORIZED_ASSERTION:{assertion_id}")
        elif raw.get("skill_row_sha256") != canonical_sha256(graph_row):
            issues.append(f"SKILL_ROW_DIGEST_MISMATCH:{assertion_id}")

    exclusion_ids = {
        str(row.get("skill_id") or "")
        for row in corpus.get("exclusions") or []
        if isinstance(row, dict)
    }
    if assertion_ids & exclusion_ids:
        issues.append("ASSERTION_EXCLUSION_OVERLAP")
    if assertion_ids | exclusion_ids != set(graph_rows):
        issues.append("CANONICAL_SKILL_PARITY_MISMATCH")
    return issues


__all__ = [
    "ASSERTION_SCHEMA_VERSION",
    "CORPUS_SCHEMA_VERSION",
    "SkillAssertionCorpusError",
    "build_skill_assertion_corpus",
    "canonical_json_bytes",
    "canonical_sha256",
    "validate_skill_assertion_corpus",
]
