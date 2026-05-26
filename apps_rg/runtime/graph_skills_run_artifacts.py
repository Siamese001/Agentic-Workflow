"""Persist graph-skills quality artifacts into per-run proof dirs (W10 D6 hardening)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.graph_selection_rationale import write_graph_selection_rationale
from apps_rg.runtime.section_graph_skills_proof_pool import GRAPH_SKILLS_AUTHORITY_SECTIONS

RATIONALE_FILENAME = "graph_selection_rationale.json"
NATIVE_C03_FILENAME = "native_c03_final_evidence.json"
PROMOTION_CANDIDATES_FILENAME = "c03_promotion_candidates.json"


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _targeting_from_runtime_payload(runtime_payload: dict[str, Any]) -> tuple[str, str, str, str]:
    company = str(runtime_payload.get("target_company") or "").strip()
    role = str(
        runtime_payload.get("target_role")
        or runtime_payload.get("target_title")
        or ""
    ).strip()
    jd_text = str(runtime_payload.get("jd_text") or "").strip()
    briefing = str(runtime_payload.get("briefing") or runtime_payload.get("briefing_text") or "").strip()
    graph_tgt = runtime_payload.get("graph_targeting_for_pa")
    if isinstance(graph_tgt, dict):
        company = company or str(graph_tgt.get("target_company") or "").strip()
        role = role or str(graph_tgt.get("target_role") or graph_tgt.get("target_title") or "").strip()
        jd_text = jd_text or str(graph_tgt.get("jd_text") or "").strip()
        briefing = briefing or str(graph_tgt.get("briefing_text") or graph_tgt.get("briefing") or "").strip()
    return company, role, jd_text, briefing


def persist_graph_skills_lane_artifacts(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    repo_root: Path | None = None,
) -> dict[str, str | None]:
    """Write D6 graph-skills artifacts when targeting + graph authority context is present."""
    paths: dict[str, str | None] = {
        RATIONALE_FILENAME: None,
        NATIVE_C03_FILENAME: None,
        PROMOTION_CANDIDATES_FILENAME: None,
    }
    if section_id not in GRAPH_SKILLS_AUTHORITY_SECTIONS:
        return paths

    company, role, jd_text, briefing = _targeting_from_runtime_payload(runtime_payload)
    if jd_text and company and role:
        rationale_path = artifact_dir / RATIONALE_FILENAME
        graph_digest: str | None = None
        pp_meta = runtime_payload.get("proof_pool_metadata")
        if isinstance(pp_meta, dict):
            auth = pp_meta.get("evidence_authority")
            if isinstance(auth, dict):
                graph_digest = str(auth.get("graph_digest") or "").strip() or None
            if not graph_digest:
                graph_digest = str(
                    pp_meta.get("graph_digest") or pp_meta.get("augmented_skills_graph_digest") or ""
                ).strip() or None
        write_graph_selection_rationale(
            rationale_path,
            section_id=section_id,
            target_company=company,
            target_role=role,
            jd_text=jd_text,
            briefing_text=briefing,
            repo_root=repo_root,
            graph_digest=graph_digest,
        )
        paths[RATIONALE_FILENAME] = rationale_path.as_posix()

    pp_meta = runtime_payload.get("proof_pool_metadata")
    if isinstance(pp_meta, dict):
        native_c03 = pp_meta.get("native_c03_final_evidence")
        if isinstance(native_c03, dict) and native_c03:
            native_path = artifact_dir / NATIVE_C03_FILENAME
            _write_json(native_path, native_c03)
            paths[NATIVE_C03_FILENAME] = native_path.as_posix()

        promo = pp_meta.get("c03_promotion_candidates")
        if not isinstance(promo, dict):
            allow = pp_meta.get("exec_summary_allowlist_receipt")
            if isinstance(allow, dict):
                promo = allow.get("c03_promotion_candidates")
        if isinstance(promo, dict) and promo:
            promo_path = artifact_dir / PROMOTION_CANDIDATES_FILENAME
            _write_json(promo_path, promo)
            paths[PROMOTION_CANDIDATES_FILENAME] = promo_path.as_posix()

    return paths


__all__ = [
    "NATIVE_C03_FILENAME",
    "PROMOTION_CANDIDATES_FILENAME",
    "RATIONALE_FILENAME",
    "persist_graph_skills_lane_artifacts",
]
