"""Read-only apps_rg section complexity reduction audit.

Emits:
  docs/reports/apps_rg/apps_rg_section_complexity_reduction_audit.{json,md}
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_APPS_RG = _REPO / "apps_rg"
_CONTRACT_DIR = _APPS_RG / "prompt_assembly" / "section_prompt_contracts"
_DECLARATIVE_DIR = _APPS_RG / "prompt_assembly" / "section_contracts"
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
_DEFAULT_PROOF_ROOT = (
    _REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "full_resume_0e41a1c13cfe" / "lanes"
)
_RUNTIME_SCAN_ROOTS = (
    _APPS_RG / "runtime" / "sections",
    _APPS_RG / "runtime" / "validators",
    _APPS_RG / "runtime" / "judges",
    _APPS_RG / "runtime" / "dispatch",
)
_REPAIR_KEYWORDS = (
    "repair",
    "reformat",
    "retry_qwen",
    "coerce_",
    "finalize_",
    "graph_only",
    "srfs",
    "emergency",
    "projection",
    "trim",
)
_RELEASE_REQUIRED = frozenset(
    {
        "l2_output.json",
        "x2_gate_outputs.json",
        "x1d_llm_judge_outputs.json",
        "x3_disposition.json",
    }
)
_ROLLUP_REQUIRED = frozenset(
    {
        "l2_output.json",
        "x2_gate_outputs.json",
        "x1d_llm_judge_outputs.json",
        "x3_disposition.json",
        "l6_shadow_eval_package.json",
    }
)
_NON_RELEASE_ARTIFACT_PATTERNS = (
    ("l6_shadow_eval_package.json", "L6 shadow — offline calibration only; not runtime ALLOW"),
    ("section_l7_binding_manifest.json", "L7 binding correlation — SECTION_L7_CORRELATION classification"),
    ("evidence_package_index.json", "W6/W7 evidence packaging — not section X3 gate"),
    ("one_spine_certification", "Section one-spine cert stamp — not product proof gate"),
    ("c03_graphrag_bound.json", "Graph binding receipt — context only unless X2 fails"),
    ("c0_fec_bridge_receipt.json", "C0 FEC bridge — plumbing receipt"),
    ("RUN_BUNDLE_INDEX.json", "Run index — operator convenience"),
    ("compiled_prompt", "Prompt compile audit — not release disposition"),
    ("prompt_selection_trace.json", "Prompt trace — drift audit only"),
    ("exit_review_packet.json", "Exit review — human packet; X3 is authoritative"),
    ("fact_check_result.json", "Auxiliary fact check — duplicate of X2 claim coverage when wired"),
    ("clean_x3_allow_readiness.json", "Pre-X3 readiness probe — not final disposition"),
    ("graph_only_generation_quality_repair.json", "Repair meta — should collapse into allowed_repair receipt"),
)
_DECLARATIVE_MAP = {
    "executive_summary": _DECLARATIVE_DIR / "executive_summary_contract.yaml",
    "competencies": _DECLARATIVE_DIR / "competencies_contract.yaml",
    "unify_bullets": _DECLARATIVE_DIR / "unify_contract.yaml",
    "unify_narrative": _DECLARATIVE_DIR / "unify_contract.yaml",
}


@dataclass
class SectionComplexityRecord:
    section_id: str
    status: str
    runtime_modules: list[dict[str, Any]] = field(default_factory=list)
    runtime_module_line_total: int = 0
    repair_modules: list[str] = field(default_factory=list)
    repair_stack_documented: list[str] = field(default_factory=list)
    duplicate_dispatch_checks: list[str] = field(default_factory=list)
    invariant_layers: dict[str, Any] = field(default_factory=dict)
    duplicated_invariants: list[str] = field(default_factory=list)
    gates_permanent_noop_or_skipped: list[str] = field(default_factory=list)
    gates_skipped_in_production_proof: list[str] = field(default_factory=list)
    rigor_critical_absent_in_runtime_x2: list[str] = field(default_factory=list)
    rigor_critical_failed: list[str] = field(default_factory=list)
    proof_artifacts_non_release: list[str] = field(default_factory=list)
    proof_artifact_counts: dict[str, int] = field(default_factory=dict)
    collapse_candidates: list[str] = field(default_factory=list)
    complexity_hotspots: list[str] = field(default_factory=list)
    recommended_migration_steps: list[str] = field(default_factory=list)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return dict(data) if isinstance(data, dict) else {}


def _section_py_modules(section_id: str) -> list[dict[str, Any]]:
    needle = section_id.replace("_", "")
    out: list[dict[str, Any]] = []
    for root in _RUNTIME_SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            name = path.stem.lower()
            if section_id in name or needle in name.replace("_", ""):
                try:
                    lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
                except OSError:
                    lines = 0
                out.append(
                    {
                        "path": str(path.relative_to(_REPO)).replace("\\", "/"),
                        "lines": lines,
                    }
                )
    return out


def _repair_modules_for_section(section_id: str, modules: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    for mod in modules:
        path = mod["path"]
        low = path.lower()
        if any(k in low for k in _REPAIR_KEYWORDS):
            hits.append(path)
    extra: dict[str, list[str]] = {
        "executive_summary": [
            "apps_rg/runtime/sections/exec_summary_graph_only_quality.py",
            "apps_rg/runtime/sections/executive_summary_repair_policy.py",
        ],
        "competencies": [
            "apps_rg/runtime/sections/competencies_capability_projection.py",
        ],
        "ibm_narrative": [
            "apps_rg/runtime/sections/ibm_narrative_metric_trim.py",
        ],
    }
    for p in extra.get(section_id, []):
        if p not in hits:
            hits.append(p)
    return sorted(hits)


def _duplicate_dispatch_checks(section_id: str) -> list[str]:
    checks: dict[str, list[str]] = {
        "headline": [
            "infer_product_quality (X2 mirror) + headline_format_repair LLM loops",
            "headline_proof_shape_retry_llm — second quality authority before X2",
            "headline_fact_id_resolution.py — parallel to shared fact_id_typo_repair",
        ],
        "executive_summary": [
            "infer_product_quality (delegates to X2 but lane still 1858 LOC)",
            "apply_executive_summary_targeting_cap + token_budget_policy — pre-X2 shaping",
            "graph_only_generation_quality_repair — deterministic rewrite parallel to X2 style gates",
            "coerce_resume_display_sentence_count_band — display coercion",
            "retry_qwen_for_synthesis — second LLM authority when synthesis_regeneration_enabled",
            "executive_summary_composition.py + evidence_capsule + proof_bundle — split orchestration",
        ],
        "competencies": [
            "competencies_lane_runtime.py (1542) + competencies_lane_execution.py (795) — two-path seam",
            "competencies_rigor.py constants duplicate competencies_x2 + lane_registry",
            "competencies_capability_projection finalize — post-LLM repair stack",
            "bullet_restatement_repair LLM — narrative quality outside X2",
        ],
        "unify_bullets": [
            "repair_protected_unify_bullet_metrics + distribution Qwen repair",
            "foundation vs distribution checks split across lane + x2",
        ],
        "unify_narrative": [
            "companion metric bundle Qwen repair",
            "companion_unify_bullets_context artifacts — dependency + duplicate narrative checks",
        ],
        "ibm_bullets": [
            "foundation proof model constrained rewrite",
            "distribution / proof-shape Qwen repair (mirrors unify_bullets)",
        ],
        "ibm_narrative": [
            "ibm_narrative_lane_runtime + ibm_narrative_lane_execution split (like competencies)",
            "apply_companion_metric_budget_trim — pre-display trim parallel to X2 word budget",
            "companion metric bundle Qwen repair",
        ],
    }
    return checks.get(section_id, [])


def _documented_repair_stack(section_id: str) -> list[str]:
    from ops_scripts.apps_rg.section_authority_convergence_audit import _repair_stack

    return _repair_stack(section_id)


def _invariant_layers(section_id: str) -> dict[str, Any]:
    from apps_rg.runtime.sections.section_product_shape_ssot import (
        product_shape_gate_ids_for_lane,
        section_product_shape,
        shape_to_dict,
    )
    from tests.unit.apps_rg.section_rigor.lane_registry import (  # guardian: allow-layer-violation -- ops audit reads lane rigor registry from tests
        spec_for_lane,
    )

    contract = _load_yaml(_CONTRACT_DIR / f"{section_id}.contract.yaml")
    declarative_path = _DECLARATIVE_MAP.get(section_id)
    declarative = _load_yaml(declarative_path) if declarative_path else None
    shape = shape_to_dict(section_product_shape(section_id))
    rigor = sorted(spec_for_lane(section_id).critical_gates)
    shape_gates = sorted(product_shape_gate_ids_for_lane(section_id))
    rigor_only = sorted(set(rigor) - set(shape_gates))
    shape_only = sorted(set(shape_gates) - set(rigor))
    return {
        "section_prompt_contract": contract,
        "declarative_section_contract_path": str(declarative_path.relative_to(_REPO)).replace("\\", "/")
        if declarative_path and declarative_path.is_file()
        else None,
        "product_shape_ssot_gate_ids": shape_gates,
        "lane_registry_critical_gates": rigor,
        "rigor_minus_shape": rigor_only,
        "shape_minus_rigor": shape_only,
        "competencies_rigor_constants": _competencies_rigor_constants()
        if section_id == "competencies"
        else None,
    }


def _competencies_rigor_constants() -> dict[str, int]:
    from apps_rg.runtime.sections.competencies_rigor import (
        MAX_CATEGORY_COUNT,
        MAX_ITEMS_PER_CATEGORY,
        MIN_CATEGORY_COUNT,
        MIN_ITEMS_PER_CATEGORY,
    )

    return {
        "MIN_CATEGORY_COUNT": MIN_CATEGORY_COUNT,
        "MAX_CATEGORY_COUNT": MAX_CATEGORY_COUNT,
        "MIN_ITEMS_PER_CATEGORY": MIN_ITEMS_PER_CATEGORY,
        "MAX_ITEMS_PER_CATEGORY": MAX_ITEMS_PER_CATEGORY,
    }


def _duplicated_invariants(section_id: str, layers: dict[str, Any]) -> list[str]:
    dupes: list[str] = []
    if layers.get("declarative_section_contract_path"):
        dupes.append(
            f"Second contract file {layers['declarative_section_contract_path']} overlaps section_prompt_contracts/{section_id}.contract.yaml"
        )
    if layers.get("rigor_minus_shape"):
        dupes.append(
            f"lane_registry lists {len(layers['rigor_minus_shape'])} critical gates not in product_shape SSOT (universal/style/C0)"
        )
    if layers.get("shape_minus_rigor"):
        dupes.append(
            f"product_shape SSOT lists {len(layers['shape_minus_rigor'])} gates not marked rigor-critical"
        )
    if section_id == "competencies" and layers.get("competencies_rigor_constants"):
        dupes.append("competencies_rigor.py MIN/MAX category counts triplicate competencies_x2 + product_shape SSOT")
    if section_id == "executive_summary":
        dupes.append(
            "RETIRED_EXEC_SUMMARY_X2_GATE_IDS documented in section_product_shape_ssot — must not reappear in run_x2_gates"
        )
        dupes.append("EXEC_SUMMARY_STYLE_CRITICAL_GATES in lane_registry duplicates product_shape style_gate_ids")
    if section_id in ("unify_bullets", "ibm_bullets"):
        dupes.append("DEFAULT_DISTRIBUTION constants in unify_bullets_x2 / ibm_bullets_x2 + product_shape + templates")
    return dupes


def _retired_gate_catalog(section_id: str) -> list[str]:
    from apps_rg.runtime.sections.section_product_shape_ssot import (
        RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
        RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS,
    )

    out: list[str] = []
    if section_id == "executive_summary":
        out.extend(
            f"{gid} (RETIRED — not emitted by run_x2_gates)"
            for gid in sorted(RETIRED_EXEC_SUMMARY_X2_GATE_IDS)
        )
    slice_id = f"x2_{section_id}_source_fact_ids_within_srfs_slice"
    if slice_id in RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS:
        out.append(f"{slice_id} (RETIRED W3 — use x2_{section_id}_active_proof_pool_source_fact_ids)")
    return out


def _noop_and_skipped_gates(section_id: str) -> tuple[list[str], list[str]]:
    """Static catalog of gates designed to pass/skipped + production proof observation."""
    static_noop: dict[str, list[str]] = {
        "executive_summary": [
            *_retired_gate_catalog("executive_summary"),
            "x2_srfs_* omitted when srfs_integration inactive (W4 — not emitted)",
            "x2_source_sensitive_phrases_supported omitted without selected_facts (W4)",
        ],
        "unify_narrative": [
            "MOCKED_runtime_plumbing skips finalized_bullets dependency in mock path",
        ],
        "ibm_narrative": [
            "MOCKED_runtime_plumbing skips finalized_bullets dependency",
            "companion_aware_disabled skip path",
            "offline_contract_stub skips mock language gate",
        ],
        "competencies": [
            "style markers pass as skipped_not_real_llm when runtime_generation_status != REAL_LLM",
        ],
    }
    proof_skipped: list[str] = []
    proof_retired: list[str] = []
    lane_dir = _DEFAULT_PROOF_ROOT / section_id
    x2_path = lane_dir / "x2_gate_outputs.json"
    if x2_path.is_file():
        gates = json.loads(x2_path.read_text(encoding="utf-8")).get("gates") or []
        from apps_rg.runtime.sections.section_product_shape_ssot import (
            RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
            RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS,
        )

        retired_ids = set(RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS)
        if section_id == "executive_summary":
            retired_ids |= set(RETIRED_EXEC_SUMMARY_X2_GATE_IDS)
        for g in gates:
            if not isinstance(g, dict):
                continue
            gid = str(g.get("gate_id") or "")
            if gid in retired_ids:
                proof_retired.append(f"{gid}: legacy proof bundle artifact (gate retired)")
            detail = str(g.get("detail") or g.get("reason") or g.get("observed_value") or "")
            if "skipped" in detail.lower():
                proof_skipped.append(f"{gid}: {detail[:72]}")
    static = list(static_noop.get(section_id, [])) + proof_retired
    return static, proof_skipped


def _rigor_runtime_gap(section_id: str) -> tuple[list[str], list[str]]:
    from tests.unit.apps_rg.section_rigor.lane_registry import (  # guardian: allow-layer-violation -- ops audit reads lane rigor registry from tests
        spec_for_lane,
    )

    lane_dir = _DEFAULT_PROOF_ROOT / section_id
    critical = spec_for_lane(section_id).critical_gates
    if not (lane_dir / "x2_gate_outputs.json").is_file():
        return sorted(critical), []
    gates = json.loads((lane_dir / "x2_gate_outputs.json").read_text(encoding="utf-8")).get("gates") or []
    by_id = {g["gate_id"]: g for g in gates if isinstance(g, dict) and g.get("gate_id")}
    present = set(by_id)
    absent = sorted(set(critical) - present)
    failed = sorted(gid for gid in critical if gid in by_id and not by_id[gid].get("pass", True))
    return absent, failed


def _proof_artifact_classification(section_id: str) -> tuple[dict[str, int], list[str]]:
    lane_dir = _DEFAULT_PROOF_ROOT / section_id
    if not lane_dir.is_dir():
        return {"total_files": 0}, []
    files = [p.name for p in lane_dir.iterdir() if p.is_file()]
    non_release: list[str] = []
    for fname in sorted(files):
        if fname in _ROLLUP_REQUIRED:
            continue
        if fname in _RELEASE_REQUIRED:
            continue
        labeled = False
        for pattern, reason in _NON_RELEASE_ARTIFACT_PATTERNS:
            if pattern in fname:
                non_release.append(f"{fname}: {reason}")
                labeled = True
                break
        if not labeled and fname.endswith(".json"):
            non_release.append(f"{fname}: auxiliary JSON — not in REQUIRED_RELATIVE / integrated product gate")
        elif not labeled and fname.endswith(".txt"):
            non_release.append(f"{fname}: human/display copy — downstream of l2_output.json")
    return {"total_files": len(files), "release_core": len(_RELEASE_REQUIRED & set(files))}, non_release


def _collapse_candidates(section_id: str, record: SectionComplexityRecord) -> list[str]:
    cands: list[str] = []
    decl = record.invariant_layers.get("declarative_section_contract_path")
    if decl:
        cands.append(f"DELETE declarative duplicate: {decl} → fold into section_spec only")
    if len(record.runtime_modules) > 4:
        cands.append("COLLAPSE split lane_runtime + lane_execution into single generic section runner")
    if record.repair_modules:
        cands.append("DELETE bespoke repair modules; keep shared fact_id_typo_repair + optional one regen flag in section_spec")
    if section_id == "executive_summary":
        cands.extend(
            [
                "DONE(W2): exec_summary_srfs_density_repair + emergency_finalizer removed",
                "COLLAPSE executive_summary_composition/evidence_capsule/proof_bundle into spec-driven hooks",
                "MERGE graph_only_quality into X2 fail-closed only (no parallel rewrite)",
            ]
        )
    if section_id == "competencies":
        cands.append("DELETE competencies_rigor.py — derive checks from section_spec + competencies_x2")
        cands.append("COLLAPSE competencies_capability_projection into validator-only path")
    if section_id == "headline":
        cands.append("COLLAPSE headline_format_repair LLM loops → X2 fail + one regen max")
    if record.rigor_critical_absent_in_runtime_x2:
        cands.append("ALIGN lane_registry with runtime X2 enumeration OR drop rigor-only ghosts")
    return cands


def _hotspots(section_id: str, record: SectionComplexityRecord) -> list[str]:
    hs = [
        f"{len(record.runtime_modules)} section-tagged modules ({record.runtime_module_line_total} LOC)",
        f"{len(record.repair_modules)} repair-tagged modules",
    ]
    if record.duplicate_dispatch_checks:
        hs.append(f"{len(record.duplicate_dispatch_checks)} parallel dispatch-quality paths")
    if record.rigor_critical_absent_in_runtime_x2:
        hs.append(f"{len(record.rigor_critical_absent_in_runtime_x2)} rigor-critical gates absent in production x2 bundle")
    if record.proof_artifact_counts.get("total_files", 0) > 20:
        hs.append(f"{record.proof_artifact_counts.get('total_files')} proof files per lane (~{record.proof_artifact_counts.get('total_files', 0) - 5} non-release)")
    return hs


def audit_section(section_id: str) -> SectionComplexityRecord:
    modules = _section_py_modules(section_id)
    line_total = sum(m["lines"] for m in modules)
    layers = _invariant_layers(section_id)
    absent, failed = _rigor_runtime_gap(section_id)
    noop, proof_skip = _noop_and_skipped_gates(section_id)
    counts, non_release = _proof_artifact_classification(section_id)
    record = SectionComplexityRecord(
        section_id=section_id,
        status="PASS",
        runtime_modules=modules,
        runtime_module_line_total=line_total,
        repair_modules=_repair_modules_for_section(section_id, modules),
        repair_stack_documented=_documented_repair_stack(section_id),
        duplicate_dispatch_checks=_duplicate_dispatch_checks(section_id),
        invariant_layers=layers,
        duplicated_invariants=_duplicated_invariants(section_id, layers),
        gates_permanent_noop_or_skipped=noop,
        gates_skipped_in_production_proof=proof_skip,
        rigor_critical_absent_in_runtime_x2=absent,
        rigor_critical_failed=failed,
        proof_artifacts_non_release=non_release[:24],
        proof_artifact_counts=counts,
    )
    record.collapse_candidates = _collapse_candidates(section_id, record)
    record.complexity_hotspots = _hotspots(section_id, record)
    if failed or any("credential_dump" in x for x in record.duplicated_invariants):
        record.status = "FAIL"
    elif absent or record.repair_modules or len(modules) > 6:
        record.status = "PARTIAL"
    record.recommended_migration_steps = _migration_steps_for_section(section_id, record)
    return record


def _migration_steps_for_section(section_id: str, record: SectionComplexityRecord) -> list[str]:
    steps: list[str] = []
    if record.rigor_critical_absent_in_runtime_x2:
        steps.append("Emit all section_spec.evidence_gates in runtime x2_gate_outputs.json (incl. C0 sidecar split)")
    if record.repair_modules:
        steps.append("Replace repair_modules with section_spec.allowed_repair enum (fact_id_typo | one_regen | none)")
    if len(record.runtime_modules) > 5:
        steps.append("Route lane through canonical_dispatch generic runner; keep only x2 + thin hook module")
    if record.invariant_layers.get("declarative_section_contract_path"):
        steps.append("Remove declarative section_contracts YAML after spec migration")
    return steps


def _proposed_section_spec() -> dict[str, Any]:
    return {
        "description": "Single YAML/JSON per lane — extends section_product_shape_ssot; not a new contract layer.",
        "required_fields": {
            "section_id": "stable lane key",
            "product_shape": "display_field, bounds, distribution, sentence/word bands",
            "source_authority": "jd_as_proof_allowed, companion_context_authority, upstream_lane_deps",
            "section_ownership": "forbidden_cross_section_vocabulary (credential_dump, metric_anchor, etc.)",
            "style_forbids": "first_person, em_dash, meta_disclaimer patterns",
            "evidence_gates": "bounds + proof + style gate_id list (X2 module ref)",
            "allowed_repair": "fact_id_typo_only | one_provider_regen | deterministic_reformat_from_facts | none",
            "required_runtime_artifacts": "subset of REQUIRED_RELATIVE + display txt + claim_ledger",
        },
        "explicitly_not_in_spec": [
            "X1D judge prose",
            "L6 shadow rubric",
            "L7 binding manifests",
            "SRFS emergency finalizers",
        ],
    }


def _derivation_plan() -> list[dict[str, str]]:
    return [
        {
            "target": "prompt rules / PRODUCT_SHAPE compile block",
            "source": "section_spec.product_shape + style_forbids + compile_hints",
            "validator": "section_prompt_drift_audit.py (existing)",
        },
        {
            "target": "X2 critical gates",
            "source": "section_spec.evidence_gates",
            "validator": "runtime x2_gate_outputs.json must emit every gate_id; C0 gates via c0_metrics.json",
        },
        {
            "target": "lane_registry rigor",
            "source": "codegen or test: lane_registry.LANE_CRITICAL_GATES[section] == spec.evidence_gates | UNIVERSAL",
            "validator": "test_section_gate_coverage.py — fail on rigor/runtime drift",
        },
        {
            "target": "runtime receipt expectations",
            "source": "section_spec.required_runtime_artifacts",
            "validator": "generated_lane_rollup REQUIRED_RELATIVE + full_run_section_status display txt",
        },
    ]


def _global_migration_order() -> list[str]:
    return [
        "1. Freeze section_spec schema beside section_product_shape_ssot (rename/extend, no new layer)",
        "2. Reconcile rigor_critical vs runtime X2 enumeration for all lanes (exec_summary credential_dump first)",
        "3. Collapse duplicate section_contracts YAML into spec",
        "4. Delete release-disabled repair (SRFS finalizer, density micro-expansion)",
        "5. Merge competencies + ibm_narrative split runtime/execution modules",
        "6. Replace per-lane infer_product_quality copies with shared helper (already mostly X2-delegating)",
        "7. Trim proof artifact emission to required_runtime_artifacts + operator index",
        "8. Derive lane_registry from spec via test/codegen — rigor becomes validator not parallel truth",
    ]


def build_audit(proof_root: Path | None = None) -> dict[str, Any]:
    _ = proof_root  # inventory uses default bundle; param reserved for CLI
    generated_at = datetime.now(timezone.utc).isoformat()
    sections = [audit_section(s) for s in _SECTIONS]
    delete_or_collapse: list[str] = []
    hotspots: list[str] = []
    for sec in sections:
        hotspots.extend([f"{sec.section_id}: {h}" for h in sec.complexity_hotspots])
        delete_or_collapse.extend([f"{sec.section_id}: {c}" for c in sec.collapse_candidates])
    return {
        "audit_id": "apps_rg_section_complexity_reduction_audit",
        "generated_at_utc": generated_at,
        "proof_inventory_root": str(_DEFAULT_PROOF_ROOT.relative_to(_REPO)).replace("\\", "/"),
        "sections_reviewed": list(_SECTIONS),
        "sections": [asdict(s) for s in sections],
        "complexity_hotspots_global": hotspots,
        "delete_or_collapse_candidates": delete_or_collapse,
        "proposed_section_spec": _proposed_section_spec(),
        "derivation_plan": _derivation_plan(),
        "migration_order": _global_migration_order(),
        "cross_section_patterns": [
            "7 lanes × (contract + product_shape + lane_registry + lane_py + x2_py + x1d_py) ≈ mini-spine each",
            "lane_registry marks gates critical that production x2_gate_outputs.json does not emit",
            "C0 critical gates validated via c0_metrics.json sidecar, not x2_gate_outputs — rigor over-counts",
            "50–78 proof files per lane; only 4–5 gate release artifacts",
            "executive_summary highest split: 10+ section modules, graph_only repair, SRFS vocabulary drift",
            "competencies + ibm_narrative use runtime/execution two-file seam",
        ],
        "explicit_non_claims": [
            "No one-spine convergence achieved by this audit",
            "No agentic_core changes",
            "No X2/X3 weakening",
            "No canonical CLI removal",
            "No code migration executed in this pass",
            "No release eligibility certification",
        ],
    }


def write_reports(audit: dict[str, Any]) -> tuple[Path, Path]:
    _REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _REPORT_DIR / "apps_rg_section_complexity_reduction_audit.json"
    md_path = _REPORT_DIR / "apps_rg_section_complexity_reduction_audit.md"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    lines = [
        "# apps_rg Section Complexity Reduction Audit",
        "",
        f"Generated: `{audit['generated_at_utc']}`",
        f"Proof inventory: `{audit['proof_inventory_root']}`",
        "",
        "## Goal",
        "",
        "Reduce per-section machinery so apps_rg stays a **thin app** over the governed spine: ",
        "one canonical runtime path, one section spec per lane, shared prompt compile + X2 framework, ",
        "no bespoke repair stacks or duplicate quality authority.",
        "",
        "## Cross-section patterns",
        "",
    ]
    for p in audit.get("cross_section_patterns", []):
        lines.append(f"- {p}")
    lines.extend(["", "## Per-section status", "", "| Section | Status | Modules | LOC | Repair modules |", "|---------|--------|---------|-----|----------------|"])
    for sec in audit["sections"]:
        lines.append(
            f"| {sec['section_id']} | {sec['status']} | {len(sec['runtime_modules'])} | {sec['runtime_module_line_total']} | {len(sec['repair_modules'])} |"
        )
    for sec in audit["sections"]:
        sid = sec["section_id"]
        lines.extend(
            [
                "",
                f"## {sid}",
                "",
                f"**Status:** {sec['status']}",
                "",
                "### Runtime modules (section-tagged)",
            ]
        )
        for mod in sec["runtime_modules"][:12]:
            lines.append(f"- `{mod['path']}` ({mod['lines']} lines)")
        if len(sec["runtime_modules"]) > 12:
            lines.append(f"- … +{len(sec['runtime_modules']) - 12} more")
        lines.extend(["", "### Repair stack", ""])
        for r in sec.get("repair_stack_documented") or []:
            lines.append(f"- {r}")
        lines.extend(["", "### Duplicate dispatch / quality authority", ""])
        for d in sec.get("duplicate_dispatch_checks") or []:
            lines.append(f"- {d}")
        lines.extend(["", "### Duplicated invariants", ""])
        for d in sec.get("duplicated_invariants") or []:
            lines.append(f"- {d}")
        if sec.get("rigor_critical_absent_in_runtime_x2"):
            lines.append("")
            lines.append("### Rigor gates absent in production `x2_gate_outputs.json`")
            for g in sec["rigor_critical_absent_in_runtime_x2"]:
                lines.append(f"- `{g}`")
        lines.extend(["", "### Collapse / delete candidates", ""])
        for c in sec.get("collapse_candidates") or []:
            lines.append(f"- {c}")
    lines.extend(["", "## Proposed section spec (minimal shape)", ""])
    spec = audit["proposed_section_spec"]
    lines.append(f"- {spec['description']}")
    for k, v in spec["required_fields"].items():
        lines.append(f"- **{k}**: {v}")
    lines.extend(["", "## Derivation plan", ""])
    for row in audit.get("derivation_plan", []):
        lines.append(f"- **{row['target']}** ← {row['source']} (validate: {row['validator']})")
    lines.extend(["", "## Migration order", ""])
    for step in audit.get("migration_order", []):
        lines.append(f"- {step}")
    lines.extend(["", "## Explicit non-claims", ""])
    for n in audit.get("explicit_non_claims", []):
        lines.append(f"- {n}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def export_complexity_baseline_snapshot() -> dict[str, Any]:
    """W1.2 / W5.0 — machine-readable LOC/module ratchet baseline."""
    import hashlib

    script_path = Path(__file__).resolve()
    digest = hashlib.sha256(script_path.read_bytes()).hexdigest()[:16]
    generated_at = datetime.now(timezone.utc).isoformat()
    sections_out: list[dict[str, Any]] = []
    modules_out: list[dict[str, Any]] = []
    for section_id in _SECTIONS:
        modules = _section_py_modules(section_id)
        tagged_loc = sum(m["lines"] for m in modules)
        sections_out.append(
            {
                "section_id": section_id,
                "tagged_runtime_loc": tagged_loc,
                "module_count": len(modules),
                "loc": tagged_loc,
            }
        )
        for mod in modules:
            modules_out.append(
                {
                    "section_id": section_id,
                    "module_path": mod["path"],
                    "loc": mod["lines"],
                }
            )
    return {
        "baseline_id": "apps_rg_complexity_baseline",
        "linked_plan_id": "apps-rg-complexity-test-radar-605dcc",
        "audit_script_version": "section_complexity_reduction_audit",
        "audit_script_digest": digest,
        "generated_at": generated_at,
        "sections": sections_out,
        "modules": modules_out,
        "thresholds": {
            "loc_increase_max": 0,
            "module_count_increase_max": 0,
        },
    }


def main() -> int:
    audit = build_audit()
    json_path, md_path = write_reports(audit)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
