"""Read-only Section Authority Convergence Audit for apps_rg generated lanes.

Emits docs/reports/apps_rg/section_authority_convergence_audit.{json,md}
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[2]
import sys

if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
_APPS_RG = _REPO / "apps_rg"
_CONTRACT_DIR = _APPS_RG / "prompt_assembly" / "section_prompt_contracts"
_REPORT_DIR = _REPO / "docs" / "reports" / "apps_rg"
_SECTIONS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

# Default canonical full-resume proof bundle (inventory only; no live generation).
_DEFAULT_PROOF_ROOT = (
    _REPO
    / "artifacts"
    / "apps_rg"
    / "runtime_proofs"
    / "full_resume_0e41a1c13cfe"
    / "lanes"
)


@dataclass
class SectionAuditRecord:
    section_id: str
    status: str
    product_shape_contract: dict[str, Any] = field(default_factory=dict)
    prompt_shape: dict[str, Any] = field(default_factory=dict)
    x2_shape: dict[str, Any] = field(default_factory=dict)
    rigor_critical_gates: list[str] = field(default_factory=list)
    runtime_observed_shape: dict[str, Any] = field(default_factory=dict)
    srfs_behavior: dict[str, Any] = field(default_factory=dict)
    briefing_behavior: dict[str, Any] = field(default_factory=dict)
    ownership_conflicts: list[str] = field(default_factory=list)
    repair_stack: list[str] = field(default_factory=list)
    prompt_trace_status: dict[str, Any] = field(default_factory=dict)
    text_primitive_risks: list[str] = field(default_factory=list)
    critical_mismatches: list[str] = field(default_factory=list)
    recommended_fix_order: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return dict(data) if isinstance(data, dict) else {}


def _load_contract(section_id: str) -> dict[str, Any]:
    return _load_yaml(_CONTRACT_DIR / f"{section_id}.contract.yaml")


def _load_declarative_contract(section_id: str) -> dict[str, Any] | None:
    mapping = {
        "executive_summary": _APPS_RG / "prompt_assembly" / "section_contracts" / "executive_summary_contract.yaml",
        "competencies": _APPS_RG / "prompt_assembly" / "section_contracts" / "competencies_contract.yaml",
        "unify_bullets": _APPS_RG / "prompt_assembly" / "section_contracts" / "unify_contract.yaml",
        "unify_narrative": _APPS_RG / "prompt_assembly" / "section_contracts" / "unify_contract.yaml",
    }
    path = mapping.get(section_id)
    return _load_yaml(path) if path and path.is_file() else None


def _rigor_critical_gates(section_id: str) -> frozenset[str]:
    from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

    return spec_for_lane(section_id).critical_gates


def _product_shape(section_id: str) -> dict[str, Any]:
    from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape, shape_to_dict

    return shape_to_dict(section_product_shape(section_id))


def _drift_violations(section_id: str) -> list[dict[str, str]]:
    from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape
    from apps_rg.runtime.sections.section_prompt_drift_audit import audit_section

    return [
        {"kind": v.kind, "detail": v.detail, "path": v.path}
        for v in audit_section(section_product_shape(section_id))
    ]


def _runtime_lane_dir(proof_root: Path, section_id: str) -> Path | None:
    lane = proof_root / section_id
    return lane if lane.is_dir() else None


def _load_x2_gates(lane_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    x2_path = lane_dir / "x2_gate_outputs.json"
    if not x2_path.is_file():
        return [], None
    data = json.loads(x2_path.read_text(encoding="utf-8"))
    gates = data.get("gates") or []
    return gates, data


def _observed_output_shape(section_id: str, lane_dir: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"proof_dir": str(lane_dir.relative_to(_REPO)).replace("\\", "/")}
    mapping = {
        "headline": ("headline_output.txt", "text"),
        "executive_summary": ("resume_display_text.txt", "text"),
        "unify_bullets": ("unify_bullets_output.txt", "bullets"),
        "unify_narrative": ("unify_narrative_output.txt", "text"),
        "ibm_bullets": ("ibm_bullets_output.txt", "bullets"),
        "ibm_narrative": ("ibm_narrative_output.txt", "text"),
        "competencies": ("competencies_section_output.json", "json"),
    }
    fname, kind = mapping.get(section_id, ("", "text"))
    path = lane_dir / fname
    if not path.is_file():
        out["artifact_missing"] = fname
        return out
    if kind == "json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        cats = payload.get("competencies") or payload.get("categories") or []
        out["category_count"] = len(cats) if isinstance(cats, list) else None
        out["display_preview"] = str(payload)[:200]
        return out
    text = path.read_text(encoding="utf-8").strip()
    out["char_len"] = len(text)
    out["preview"] = text[:240]
    if section_id in ("unify_bullets", "ibm_bullets"):
        lines = [ln for ln in text.splitlines() if ln.strip().startswith("-")]
        out["bullet_count"] = len(lines)
    if section_id in ("executive_summary", "unify_narrative", "ibm_narrative"):
        from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

        sents = split_sentences(text) if section_id == "executive_summary" else [text]
        out["sentence_count"] = len(sents)
        out["word_count"] = len(text.split())
    if section_id == "headline":
        out["pipe_segments"] = len([p for p in text.split("|") if p.strip()])
        out["word_count"] = len(text.replace("|", " ").split())
    return out


def _prompt_trace(lane_dir: Path) -> dict[str, Any]:
    trace_path = lane_dir / "prompt_selection_trace.json"
    compiled_path = lane_dir / "compiled_prompt_artifact.json"
    status: dict[str, Any] = {}
    if trace_path.is_file():
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        status["prompt_selection_trace_present"] = True
        status["apps_rg_prompt_template_ref"] = trace.get("apps_rg_prompt_template_ref")
        status["compiler_template_id"] = trace.get("compiler_template_id") or trace.get("prompt_id")
        status["pa_shell"] = trace.get("strategic_tailor_v1_invoked") or trace.get("section_prompt_adapter")
    else:
        status["prompt_selection_trace_present"] = False
    if compiled_path.is_file():
        compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
        status["compiled_prompt_artifact_present"] = True
        status["compiled_apps_rg_prompt_template_ref"] = compiled.get("apps_rg_prompt_template_ref")
        status["compiled_compiler_template_id"] = compiled.get("compiler_template_id")
        status["slot_count"] = compiled.get("slot_count")
    else:
        status["compiled_prompt_artifact_present"] = False
    return status


def _srfs_and_briefing(section_id: str, lane_dir: Path | None) -> tuple[dict[str, Any], dict[str, Any]]:
    srfs: dict[str, Any] = {"applies": section_id in ("executive_summary", "competencies", "ibm_narrative")}
    briefing: dict[str, Any] = {
        "jd_as_proof_allowed": False,
        "rigor_uses_exec_briefing_variant": section_id == "executive_summary",
    }
    if lane_dir is None:
        return srfs, briefing
    manifest_path = lane_dir / "run_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        briefing["manual_brief_path"] = manifest.get("manual_brief") or manifest.get("briefing_path")
    gates, _ = _load_x2_gates(lane_dir)
    gate_ids = {g.get("gate_id") for g in gates if isinstance(g, dict)}
    if section_id == "executive_summary":
        from apps_rg.runtime.sections.section_product_shape_ssot import (
            RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
        )

        srfs["srfs_gates_observed"] = sorted(g for g in gate_ids if g and "srfs" in g)
        srfs["retired_gate_ids_observed"] = sorted(g for g in gate_ids if g in RETIRED_EXEC_SUMMARY_X2_GATE_IDS)
        srfs["legacy_2_3_gate_observed"] = "x2_exec_summary_sentence_count_2_3" in gate_ids
        srfs["product_4_5_gate_observed"] = "x2_exec_summary_sentence_count_4_5" in gate_ids
        srfs["paragraph_max_gate_observed"] = "x2_exec_summary_paragraph_max_words" in gate_ids
        srfs["paragraph_word_bounds_observed"] = "x2_exec_summary_paragraph_word_bounds" in gate_ids
        for gid in (
            "x2_exec_summary_paragraph_max_words",
            "x2_exec_summary_jd_alignment_proof_flags",
            "x2_exec_summary_prompt_template_authority",
        ):
            srfs[f"{gid}_observed"] = gid in gate_ids
    return srfs, briefing


def _repair_stack(section_id: str) -> list[str]:
    stacks: dict[str, list[str]] = {
        "headline": [
            "normalize_claim_ledger_string_fact_ids",
            "lane_normalize_claim_ledger",
            "headline_proof_shape_retry_llm (same-authority Qwen)",
            "headline_format_repair LLM",
            "fact_id_typo_repair against allowlist",
        ],
        "executive_summary": [
            "RELEASE: SRFS emergency finalizer DISABLED",
            "RELEASE: SRFS judge-safe / density micro-expansion DISABLED",
            "synthesis_regeneration_enabled (one Qwen regen)",
            "graph_only_generation_quality_repair (deterministic reformat)",
            "claim_ledger allowlist repair",
            "coerce_resume_display_sentence_count_band",
            "offline SRFS mock uses 5-sentence arc (stub only)",
        ],
        "competencies": [
            "repair_structured_competencies_source_facts",
            "bullet_restatement_repair LLM",
            "fact_id_typo_repair",
            "deterministic keyword-stuffing repair templates",
        ],
        "unify_bullets": [
            "repair_protected_unify_bullet_metrics",
            "distribution / proof-shape Qwen repair",
            "fact_id_typo_repair",
        ],
        "unify_narrative": [
            "companion metric bundle Qwen repair",
            "fact_id_typo_repair",
        ],
        "ibm_bullets": [
            "foundation proof model constrained rewrite",
            "distribution / proof-shape Qwen repair",
            "fact_id_typo_repair",
        ],
        "ibm_narrative": [
            "companion metric bundle Qwen repair",
            "fact_id_typo_repair",
        ],
    }
    return stacks.get(section_id, [])


def _text_primitive_risks(section_id: str) -> list[str]:
    risks: list[str] = []
    if section_id == "executive_summary":
        risks.append("split_sentences abbreviation guards (U.S., Basel III, decimals) — comma chains still fragile")
        risks.append("SRFS _srfs_join_fragments_as_one_sentence can mask boundary miscounts")
    if section_id in ("unify_narrative", "ibm_narrative"):
        risks.append("single-sentence display; word/char caps — template still mentions legacy 250-char band")
    if section_id in ("unify_bullets", "ibm_bullets"):
        risks.append("bullet lines parsed by prefix; metric anchor ownership is regex/heuristic")
    if section_id == "headline":
        risks.append("pipe-segment split; word count includes segment text flattened")
    if section_id == "competencies":
        risks.append("term_phrase normalization; two-word low-rigor detector; category label exact match")
    return risks


def _ownership_conflicts(section_id: str) -> list[str]:
    conflicts: dict[str, list[str]] = {
        "executive_summary": [
            "Credentials block competes with competencies + certifications lanes (credential_dump gate)",
            "Mechanism stack overlaps unify_bullets vocabulary",
            "Commercial metrics overlap unify/ibm bullet metric anchors",
        ],
        "headline": [
            "Creative X/Y/Z segments must not absorb bullet metrics (headline_no_metrics)",
            "JD mirroring vs fact-grounded segments",
        ],
        "competencies": [
            "Must not relist credentials (forbidden cert category)",
            "Must not restate bullet outcomes (bullet_restatement gate)",
            "Metrics-as-skills without capability context",
        ],
        "unify_bullets": [
            "Owns unify metric anchors; narrative must not duplicate",
            "Mechanism-dense bullet cap (max 1)",
        ],
        "unify_narrative": [
            "Depends on unify_bullets ACCEPTED_FINALIZED companion",
            "Metric repetition gate defers to bullets",
        ],
        "ibm_bullets": [
            "Zero HEAVY distribution; IBM foundation vocabulary vs unify agentic vocabulary",
        ],
        "ibm_narrative": [
            "Meta-disclaimer anti-pattern vs model compliance phrasing",
            "Career-bridge phrasing vs executive_summary arc",
        ],
    }
    return conflicts.get(section_id, [])


def audit_section(section_id: str, proof_root: Path) -> SectionAuditRecord:
    contract = _load_contract(section_id)
    declarative = _load_declarative_contract(section_id)
    shape = _product_shape(section_id)
    drift = _drift_violations(section_id)
    critical = sorted(_rigor_critical_gates(section_id))
    lane_dir = _runtime_lane_dir(proof_root, section_id)
    gates: list[dict[str, Any]] = []
    x2_bundle: dict[str, Any] | None = None
    if lane_dir:
        gates, x2_bundle = _load_x2_gates(lane_dir)
    present = {g["gate_id"] for g in gates if isinstance(g, dict) and g.get("gate_id")}
    by_id = {g["gate_id"]: g for g in gates if isinstance(g, dict) and g.get("gate_id")}
    c0_gate_ids = frozenset({"x2_c0_metrics_artifact_present", "x2_c0_support_status_gate"})
    missing_critical = sorted(set(critical) - present)
    missing_section = [g for g in missing_critical if g not in c0_gate_ids]
    missing_c0 = [g for g in missing_critical if g in c0_gate_ids]
    failed_critical = sorted(
        gid for gid in critical if gid in by_id and not by_id[gid].get("pass", by_id[gid].get("pass_"))
    )
    mismatches: list[str] = []
    for v in drift:
        mismatches.append(f"prompt_drift:{v['kind']}: {v['detail']} ({v['path']})")
    if missing_section:
        mismatches.append(
            f"rigor_critical_gate_absent_in_runtime_x2: {missing_section}"
        )
    if missing_c0:
        mismatches.append(
            f"rigor_c0_gate_not_in_x2_bundle (expected c0_metrics.json sidecar): {missing_c0}"
        )
    if failed_critical:
        mismatches.append(f"rigor_critical_gate_failed: {failed_critical}")
    if section_id == "executive_summary" and lane_dir:
        text_path = lane_dir / "resume_display_text.txt"
        if text_path.is_file():
            text = text_path.read_text(encoding="utf-8")
            if re.search(r"AWS Certified|Fellow of the Society", text, re.I):
                if "x2_exec_summary_no_credential_dump" in critical and (
                    "x2_exec_summary_no_credential_dump" not in present
                    or by_id.get("x2_exec_summary_no_credential_dump", {}).get("pass") is not False
                ):
                    mismatches.append(
                        "display_contains_credential_dump_risk: certifications named in resume_display_text "
                        "while x2_exec_summary_no_credential_dump missing or not failed"
                    )
    if section_id == "ibm_narrative" and lane_dir:
        text = (lane_dir / "ibm_narrative_output.txt").read_text(encoding="utf-8")
        if re.search(r"without claiming", text, re.I):
            if "x2_ibm_narrative_no_meta_disclaimer_in_display" in missing_critical:
                mismatches.append(
                    "display_meta_disclaimer_present_but_gate_absent: "
                    "'without claiming' in narrative while x2_ibm_narrative_no_meta_disclaimer_in_display "
                    "not emitted in x2_gate_outputs.json"
                )
            elif by_id.get("x2_ibm_narrative_no_meta_disclaimer_in_display", {}).get("pass"):
                mismatches.append(
                    "display_meta_disclaimer_present_but_gate_passed: judge-flagged meta disclaimer"
                )
    srfs, briefing = _srfs_and_briefing(section_id, lane_dir)
    exit_x2_path = lane_dir / "section_exit_x2_result.json" if lane_dir else None
    aggregation_status = None
    if exit_x2_path and exit_x2_path.is_file():
        aggregation_status = json.loads(exit_x2_path.read_text(encoding="utf-8")).get(
            "aggregation_status"
        )
    authority_fail = bool(failed_critical) or any(
        k in " ".join(mismatches)
        for k in (
            "credential_dump",
            "meta_disclaimer",
            "prompt_drift",
        )
    )
    status = "PASS"
    if authority_fail:
        status = "FAIL"
    elif mismatches:
        status = "PARTIAL"
    rec: list[str] = []
    if section_id == "executive_summary":
        rec.extend(
            [
                "Align SRFS vs default X2 gate IDs with lane_registry critical set",
                "Emit x2_exec_summary_no_credential_dump in all runtime bundles",
                "Enforce paragraph_max_words + jd_alignment_proof_flags in SRFS runs",
            ]
        )
    if section_id == "ibm_narrative":
        rec.append("Emit and fail-closed x2_ibm_narrative_no_meta_disclaimer_in_display in production X2")
    if section_id == "competencies" and failed_critical:
        rec.append("Repair low-rigor two-word terms and metric-without-context terms before X3")
    if missing_critical:
        rec.append(f"Reconcile lane_registry vs runtime gate enumeration for {section_id}")
    return SectionAuditRecord(
        section_id=section_id,
        status=status,
        product_shape_contract={
            "section_prompt_contract": contract,
            "declarative_section_contract": declarative,
            "product_shape_ssot": shape,
        },
        prompt_shape={
            "template_ref": contract.get("apps_rg_prompt_template_ref"),
            "pa_template_ref": contract.get("pa_template_ref"),
            "mode": contract.get("mode"),
            "jd_as_proof_allowed": contract.get("jd_as_proof_allowed"),
            "companion_context_authority": contract.get("companion_context_authority"),
            "drift_violations": drift,
        },
        x2_shape={
            "x2_gate_profile_ref": contract.get("x2_gate_profile_ref"),
            "runtime_gate_count": len(gates),
            "aggregation_status": aggregation_status,
            "failed_gate_ids": (x2_bundle or {}).get("failed_gate_ids"),
            "missing_section_critical_in_x2": missing_section,
            "missing_c0_critical_in_x2": missing_c0,
        },
        rigor_critical_gates=critical,
        runtime_observed_shape=_observed_output_shape(section_id, lane_dir)
        if lane_dir
        else {"proof_missing": True},
        srfs_behavior=srfs,
        briefing_behavior=briefing,
        ownership_conflicts=_ownership_conflicts(section_id),
        repair_stack=_repair_stack(section_id),
        prompt_trace_status=_prompt_trace(lane_dir) if lane_dir else {"proof_missing": True},
        text_primitive_risks=_text_primitive_risks(section_id),
        critical_mismatches=mismatches,
        recommended_fix_order=rec,
    )


def build_audit(proof_root: Path | None = None) -> dict[str, Any]:
    root = proof_root or _DEFAULT_PROOF_ROOT
    generated_at = datetime.now(timezone.utc).isoformat()
    sections = [audit_section(s, root) for s in _SECTIONS]
    high_severity = []
    patterns = []
    for sec in sections:
        high_severity.extend(
            [f"{sec.section_id}: {m}" for m in sec.critical_mismatches if "absent" in m or "failed" in m or "dump" in m or "disclaimer" in m]
        )
    if any(
        "rigor_critical_gate_absent_in_runtime_x2" in m
        for s in sections
        for m in s.critical_mismatches
    ):
        patterns.append(
            "lane_registry critical gates are not all enumerated in production x2_gate_outputs.json"
        )
    if any("rigor_c0_gate_not_in_x2_bundle" in m for s in sections for m in s.critical_mismatches):
        patterns.append("C0 critical gates are rigor-critical but absent from lane x2_gate_outputs sidecar")
    if any(
        s.section_id == "executive_summary"
        and (s.srfs_behavior or {}).get("retired_gate_ids_observed")
        for s in sections
    ):
        patterns.append(
            "executive_summary proof bundle contains RETIRED_EXEC_SUMMARY_X2_GATE_IDS — refresh runtime proof"
        )
    fix_order = []
    for s in sections:
        fix_order.extend(s.recommended_fix_order)
    # de-dupe preserving order
    seen: set[str] = set()
    fix_order_unique = []
    for item in fix_order:
        if item not in seen:
            seen.add(item)
            fix_order_unique.append(item)
    return {
        "audit_id": "section_authority_convergence_audit",
        "generated_at_utc": generated_at,
        "proof_inventory_root": str(root.relative_to(_REPO)).replace("\\", "/"),
        "sections": [asdict(s) for s in sections],
        "high_severity_gaps": high_severity,
        "cross_section_patterns": patterns,
        "recommended_fix_order_global": fix_order_unique,
        "explicit_non_claims": [
            "No release eligibility",
            "No one-spine convergence",
            "No agentic_core edits",
            "No live regeneration in this audit run",
            "Mock/stub paths not used as product proof unless labeled",
        ],
    }


def write_reports(audit: dict[str, Any]) -> tuple[Path, Path]:
    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _REPORT_DIR / "section_authority_convergence_audit.json"
    md_path = _REPORT_DIR / "section_authority_convergence_audit.md"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    lines = [
        "# Section Authority Convergence Audit",
        "",
        f"Generated: `{audit['generated_at_utc']}`",
        f"Proof inventory: `{audit['proof_inventory_root']}`",
        "",
        "## Executive summary",
        "",
        "This audit compares section prompt contracts, product-shape SSOT, X2 validators, ",
        "`lane_registry` critical gates, and canonical runtime proof artifacts. ",
        "Goal: prevent **executive_summary-style authority drift** (prompt shape ≠ X2 shape ≠ rigor anchors).",
        "",
        "## Cross-section patterns",
        "",
    ]
    for p in audit.get("cross_section_patterns", []):
        lines.append(f"- {p}")
    lines.extend(["", "## High-severity gaps", ""])
    for g in audit.get("high_severity_gaps", []):
        lines.append(f"- {g}")
    lines.extend(["", "## Per-section status", "", "| Section | Status |", "|---------|--------|"])
    for sec in audit["sections"]:
        lines.append(f"| {sec['section_id']} | {sec['status']} |")
    for sec in audit["sections"]:
        sid = sec["section_id"]
        lines.extend(
            [
                "",
                f"## {sid}",
                "",
                f"**Status:** {sec['status']}",
                "",
                "### Product shape",
                f"- SSOT: `{sec['product_shape_contract']['product_shape_ssot'].get('shape_summary', '')}`",
                f"- Contract mode: `{sec['prompt_shape'].get('mode')}`",
                "",
                "### Source authority",
                f"- jd_as_proof_allowed: `{sec['prompt_shape'].get('jd_as_proof_allowed')}`",
                f"- companion: `{sec['prompt_shape'].get('companion_context_authority')}`",
                "",
                "### Rigor vs runtime X2",
                f"- Critical gates (rigor): {len(sec['rigor_critical_gates'])}",
                f"- Runtime gate rows: {sec['x2_shape'].get('runtime_gate_count')}",
                f"- Aggregation: `{sec['x2_shape'].get('aggregation_status')}`",
                "",
                "### Critical mismatches",
            ]
        )
        if sec["critical_mismatches"]:
            for m in sec["critical_mismatches"]:
                lines.append(f"- {m}")
        else:
            lines.append("- None recorded")
        lines.extend(["", "### Recommended fix order"])
        for r in sec.get("recommended_fix_order") or []:
            lines.append(f"- {r}")
    lines.extend(["", "## Explicit non-claims", ""])
    for n in audit.get("explicit_non_claims", []):
        lines.append(f"- {n}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    audit = build_audit()
    json_path, md_path = write_reports(audit)
    print(json_path)
    print(md_path)
    statuses = [s["status"] for s in audit["sections"]]
    print("STATUSES", statuses)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
