"""Build immutable DOCX render manifest from final_resume assembly evidence (no DOCX emission, no providers)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import (
    CANONICAL_ASSEMBLED_SECTION_ORDER,
    GENERATED_LANE_IDS,
    LOCKED_EMBEDDED_ORDER_IDS,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.section_display_labels import ENGINEERING_PLATFORM_COMPETENCIES_HEADING
from apps_rg.runtime.render.docx_manifest_x2 import (
    failures,
    gate_records_to_blob,
    gates_all_pass,
    run_docx_manifest_x2_gates,
)

MANIFEST_ID = "docx_manifest_v1"
PLANNED_DOCX_POSIX = "artifacts/apps_rg/runtime_proofs/docx/amit_ayer_resume_v1.docx"

BULLET_STYLE_MAPPING_REGISTRY: dict[str, Any] = {
    "resume_standard_bullet": {
        "role": "employment_and_strategy_narrative_bullets",
        "word_builtin_list_library_hint": "List Bullet",
        "word_paragraph_style_hint": "List Paragraph",
        "deterministic_transform_rule": "one_bullet_paragraph_per_json_bullet_fact",
    },
    "competencies_category_bullet": {
        "role": "competencies_lanes_category_blocks",
        "word_builtin_list_library_hint": "List Bullet",
        "word_paragraph_style_hint": "Compact List Paragraph",
        "deterministic_transform_rule": "category_heading_then_bullets_no_paraphrase",
    },
    "skills_inline_plain": {
        "role": "structured_json_arrays_without_native_word_lists",
        "word_builtin_list_library_hint": None,
        "word_paragraph_style_hint": "Body Text",
        "deterministic_transform_rule": "preserve_json_text_order_plain_paragraph_sequence",
    },
}

# Section typography contract (hints only until a template exists).
SECTION_BLUEPRINT_V1: dict[str, dict[str, Any]] = {
    "headline": {
        "paragraph_primary_style": "RG_ResumeHeadlineLine",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": None,
        "notes": "Single-line headline mirrored from headline_line (l2)",
    },
    "executive_summary": {
        "paragraph_primary_style": "RG_BodyExecutiveSummary",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": None,
        "notes": "Two-sentence executive arc only; never expand beyond l2_snapshot",
    },
    "unify_narrative": {
        "paragraph_primary_style": "RG_BodyNarrativeParagraph",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": None,
        "notes": "Narrative paragraph(s) verbatim from unify narrative lane",
    },
    "unify_bullets": {
        "paragraph_primary_style": "RG_ListLeadIn",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "resume_standard_bullet",
        "notes": "Unify bullets as Word list bullets; JSON ordering preserved",
    },
    "ibm_narrative": {
        "paragraph_primary_style": "RG_BodyNarrativeParagraph",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": None,
        "notes": "IBM narrative paragraph(s) verbatim from l2_snapshot",
    },
    "ibm_bullets": {
        "paragraph_primary_style": "RG_ListLeadIn",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "resume_standard_bullet",
        "notes": "IBM bullets as Word bullets; deterministic ordering preserved",
    },
    "insurtech": {
        "paragraph_primary_style": "RG_EmploymentEmployerLeadIn",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "resume_standard_bullet",
        "notes": "Locked-copy JSON verbatim; headings from employer/title/date/location envelope",
    },
    "ey": {
        "paragraph_primary_style": "RG_EmploymentEmployerLeadIn",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "resume_standard_bullet",
        "notes": "Locked-copy JSON verbatim; employment envelope styles",
    },
    "early_career": {
        "paragraph_primary_style": "RG_EmploymentEmployerLeadIn",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "resume_standard_bullet",
        "notes": "Early career locked JSON verbatim",
    },
    "competencies": {
        "paragraph_primary_style": "RG_CompactCategoryHeading",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "competencies_category_bullet",
        "human_section_title_hint": ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
        "notes": "Eight-category lattice; deterministic layout mirrors l2 competency blocks",
    },
    "education": {
        "paragraph_primary_style": "RG_StructuredFactsPlain",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": None,
        "notes": "Locked education JSON array verbatim; plain paragraphs preferred",
    },
    "certifications": {
        "paragraph_primary_style": "RG_StructuredFactsPlain",
        "section_heading_outline_level": 2,
        "bullet_list_style_external_id": "skills_inline_plain",
        "notes": "Certs as structured plain paragraphs (registry id present; not a Word list)",
    },
}


@dataclass(frozen=True)
class DocxManifestPaths:
    repo_root: Path
    final_resume_json: Path
    final_resume_manifest: Path
    final_resume_x2: Path
    output_dir: Path
    planned_docx_posix: str

    def rel(self, p: Path) -> str:
        try:
            return p.relative_to(self.repo_root).as_posix()
        except ValueError:
            return p.resolve().as_posix()


def resolve_docx_manifest_paths(repo: Path | None = None, *, planned_docx_posix: str = PLANNED_DOCX_POSIX) -> DocxManifestPaths:
    root = repo or find_repo_root()
    fr_dir = root / Path("artifacts/apps_rg/runtime_proofs/final_resume_assembly")
    out = root / Path("artifacts/apps_rg/runtime_proofs/docx_manifest")
    return DocxManifestPaths(
        repo_root=root,
        final_resume_json=fr_dir / "final_resume.json",
        final_resume_manifest=fr_dir / "final_resume_manifest.json",
        final_resume_x2=fr_dir / "final_resume_x2_gate_outputs.json",
        output_dir=out,
        planned_docx_posix=planned_docx_posix,
    )


def _generated_render_refs(section: dict[str, Any]) -> dict[str, Any]:
    sid = str(section.get("section_id") or "")
    dispo = section.get("disposition_refs") or {}
    gen = dispo.get("generated_lane") if isinstance(dispo, dict) else {}
    refs = section.get("source_artifact_refs")
    refs = refs if isinstance(refs, dict) else {}
    return {
        "final_resume_section_id": sid,
        "final_resume_source_artifact_refs": refs,
        "final_resume_generated_lane_disposition_refs": gen if isinstance(gen, dict) else {},
        "no_rewrite_projection_rule": (
            "render_only: emit l2_output_snapshot payload without semantic rewrite beyond layout"
        ),
    }


def _locked_render_refs(section: dict[str, Any]) -> dict[str, Any]:
    sid = str(section.get("section_id") or "")
    dispo = section.get("disposition_refs") or {}
    lc = dispo.get("locked_copy") if isinstance(dispo, dict) else {}
    refs = section.get("source_artifact_refs")
    refs = refs if isinstance(refs, dict) else {}
    return {
        "final_resume_section_id": sid,
        "final_resume_source_artifact_refs": refs,
        "final_resume_locked_disposition_refs": lc if isinstance(lc, dict) else {},
        "canonical_text_projection_field": "copied_text_exact",
        "byte_identity_rule": (
            "UTF-8 string identity with assembly manifest copied_text_exact; forbid template paraphrase"
        ),
    }


def _locked_invariant_refs(inv_blob: dict[str, Any]) -> dict[str, Any]:
    iid = str(inv_blob.get("manifest_section_id") or "")
    dispo = inv_blob.get("disposition_refs") or {}
    lc = dispo.get("locked_copy") if isinstance(dispo, dict) else {}
    refs = inv_blob.get("source_artifact_refs")
    refs = refs if isinstance(refs, dict) else {}
    return {
        "locked_invariant_id": iid,
        "final_resume_source_artifact_refs": refs,
        "final_resume_locked_disposition_refs": lc if isinstance(lc, dict) else {},
        "canonical_text_projection_field": "copied_text_exact",
    }


def build_docx_manifest(paths: DocxManifestPaths | None = None) -> dict[str, Any]:
    paths = paths or resolve_docx_manifest_paths()
    repo = paths.repo_root
    planned_abs = repo / paths.planned_docx_posix.replace("\\", "/")

    blob = json.loads(paths.final_resume_json.read_text(encoding="utf-8"))
    by_section_id = {
        str(s.get("section_id")): s
        for s in (blob.get("sections") or [])
        if isinstance(s, dict) and s.get("section_id")
    }

    narrative_order_ids = [
        str(s.get("section_id"))
        for s in (blob.get("sections") or [])
        if isinstance(s, dict) and s.get("section_id")
    ]
    if narrative_order_ids != list(CANONICAL_ASSEMBLED_SECTION_ORDER):
        raise ValueError("final_resume section order differs from canonical contract")

    generated_refs: dict[str, Any] = {}
    locked_refs: dict[str, Any] = {}
    profiles: list[dict[str, Any]] = []

    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:
        sec_block = by_section_id.get(sid)
        if sec_block is None:
            raise ValueError(f"final_resume missing canonical section {sid}")
        blueprint = SECTION_BLUEPRINT_V1[sid]
        style_mapping = {
            "paragraph_primary_style": blueprint["paragraph_primary_style"],
            "section_heading_outline_level": blueprint["section_heading_outline_level"],
            "bullet_list_style_external_id": blueprint["bullet_list_style_external_id"],
        }
        title_hint = blueprint.get("human_section_title_hint") or sid.replace("_", " ").title()
        profiles.append(
            {
                "section_id": sid,
                "assemble_order": int(sec_block.get("assemble_order", -1)),
                "final_resume_section_kind": sec_block.get("section_kind"),
                "human_section_title_hint": title_hint,
                "layout_role": blueprint.get("notes"),
                "style_mapping": style_mapping,
            },
        )
        kind = sec_block.get("section_kind")
        if kind == "generated_lane":
            generated_refs[sid] = _generated_render_refs(sec_block)
        elif kind == "locked_copy_inline":
            locked_refs[sid] = _locked_render_refs(sec_block)
        else:
            raise ValueError(f"Unhandled section_kind for {sid}: {kind}")

    locked_invariants = blob.get("locked_copy_invariants") or {}
    if not isinstance(locked_invariants, dict):
        raise ValueError("locked_copy_invariants must be dict")
    inv_render_refs: dict[str, Any] = {}
    for inv_id in ("company_names", "titles", "locations", "dates"):
        inv_blob = locked_invariants.get(inv_id)
        if not isinstance(inv_blob, dict):
            raise ValueError(f"missing invariant {inv_id}")
        inv_render_refs[inv_id] = _locked_invariant_refs(inv_blob)

    utc_now = datetime.now(timezone.utc).isoformat()

    manifest: dict[str, Any] = {
        "manifest_id": MANIFEST_ID,
        "constructed_at_utc": utc_now,
        "constructor_module": "apps_rg.runtime.render.docx_manifest_builder",
        "sources": {
            "final_resume_json": paths.rel(paths.final_resume_json),
            "final_resume_manifest_json": paths.rel(paths.final_resume_manifest),
            "final_resume_x2_gate_outputs_json": paths.rel(paths.final_resume_x2),
            "final_resume_hash": str(blob.get("final_resume_hash") or ""),
            "assembled_object_id_source": blob.get("assembled_object_id"),
        },
        "section_render_order": narrative_order_ids,
        "locked_copy_invariants_projection_order": ["company_names", "titles", "locations", "dates"],
        "section_profiles": profiles,
        "bullet_style_mapping_registry": BULLET_STYLE_MAPPING_REGISTRY,
        "generated_sections_render_refs": generated_refs,
        "locked_sections_render_refs": {
            sid: locked_refs[sid] for sid in LOCKED_EMBEDDED_ORDER_IDS if sid in locked_refs
        },
        "locked_invariants_render_refs": inv_render_refs,
        "guarantees": {
            "no_rewrite": True,
            "manifest_is_layout_plan_only": True,
            "provider_calls_made": False,
            "qwen_calls_made": False,
            "judge_calls_made": False,
        },
        "planned_output_docx": {
            "output_docx_planned_path": paths.planned_docx_posix,
            "docx_created": False,
            "planned_file_must_not_exist_until_emitter_wave": True,
        },
        "generation_rules": [
            (
                "Sequencing: if generated_lane_rollup is rerun, rerun final_resume_assembler before "
                "regenerating this manifest so rollup_id and final_resume_hash stay aligned."
            ),
            ("Rendering may only apply layout primitives; forbid content paraphrase of final_resume payloads."),
            ("Emitters must refuse when docx_manifest X2 gates are not PASS."),
        ],
        "eligible_generated_lane_section_ids_for_docx_projection": sorted(GENERATED_LANE_IDS),
        "eligible_locked_narrative_section_ids_for_docx_projection": sorted(LOCKED_EMBEDDED_ORDER_IDS),
    }

    gate_results = run_docx_manifest_x2_gates(
        repo_root=repo,
        manifest_blob=manifest,
        final_resume_blob=blob,
        final_resume_json_path=paths.final_resume_json.resolve(),
        planned_docx_abs=planned_abs.resolve(),
    )
    all_pass = gates_all_pass(gate_results)
    gate_failed = failures(gate_results)

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    mj = paths.output_dir / "docx_manifest.json"
    mj.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    xo = paths.output_dir / "docx_manifest_x2_gate_outputs.json"
    xo.write_text(
        json.dumps(
            gate_records_to_blob(
                gate_results,
                evaluated_at_utc=utc_now,
                all_pass_res=all_pass,
                failed_gate_ids_res=gate_failed,
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
        )
        + "\n",
        encoding="utf-8",
    )

    rc = paths.output_dir / "docx_manifest_receipt.json"
    rc.write_text(
        json.dumps(
            {
                "receipt_id": "docx_manifest_receipt_v1",
                "written_at_utc": utc_now,
                "manifest_json_rel": paths.rel(mj),
                "x2_gate_outputs_json_rel": paths.rel(xo),
                "gates_all_pass": all_pass,
                "failed_gate_ids": gate_failed,
                "planned_docx_abs_inspected": paths.planned_docx_posix.replace("\\", "/"),
                "planned_docx_file_exists_observed_at_emit": planned_abs.exists(),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "manifest_path": mj,
        "x2_path": xo,
        "receipt_path": rc,
        "manifest_blob": manifest,
        "gates_all_pass": all_pass,
        "failed_gate_ids": gate_failed,
    }


def main() -> None:
    res = build_docx_manifest()
    h = str(res["manifest_blob"]["sources"]["final_resume_hash"])
    ok = bool(res["gates_all_pass"])
    print(f"DOCX_MANIFEST_DONE gates_all_pass={ok} source_final_resume_hash={h}")
    if not ok:
        print(f"FAILED_GATES:{','.join(res['failed_gate_ids'])}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
