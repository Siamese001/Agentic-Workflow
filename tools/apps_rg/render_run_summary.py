"""Render a markdown summary of an apps_rg run for inline Codex chat display.

Reads the JSON evidence emitted by ``apps_rg`` into ``artifacts/apps_rg/runs/<run_id>/``
and prints a structured markdown summary covering:

  * Run identity (run_id, route, commit, replay_key, started_at)
  * L2 sub-stages (E1..E5) with PASS/FAIL/BYPASSED status and timing
  * HOP checkpoints (HOP-0.5 .. HOP-5) reached during the run
  * Per-section narrative verdicts (headline, exec_summary, ENGINEERING & PLATFORM COMPETENCIES, role bullets)
    with composite score, accepted status, and first failed gate
  * Gate failures with reason text
  * L7 route family certification matrix (1/9 certified for R4 path is the norm)
  * ATS / overfit / provenance reports
  * Final artifact paths (DOCX, JSON, run manifest)

Invocation:
    python tools/apps_rg/render_run_summary.py [<run_dir>]

If ``<run_dir>`` is omitted, the most recently modified directory under
``artifacts/apps_rg/runs/`` is selected.

Codex integration: per ``.codex/rules/apps-rg-post-run-summary.md``,
Codex MUST invoke this script after every apps_rg run and surface the
markdown output inline in chat.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "artifacts" / "apps_rg" / "runs"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.run_output_contract import (
    APPS_RG_MANDATORY_RUN_OUTPUT_JSON,
    APPS_RG_MANDATORY_RUN_OUTPUT_MD,
    BCG_EXECUTIVE_OUTPUT_MD,
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
    FULL_RUN_SECTION_STATUS_JSON,
    REVIEW_BUNDLE_FILENAME,
)
from apps_rg.runtime.section_display_labels import summary_section_label

# ----------------------------------------------------------------- read helpers


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _latest_run_dir() -> Optional[Path]:
    if not RUNS_ROOT.is_dir():
        return None
    candidates = [
        p for p in RUNS_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _fmt_dur_ms(ms: float) -> str:
    if ms is None:
        return "—"
    if ms < 1.0:
        return f"{ms:.3f}ms"
    if ms < 1000:
        return f"{ms:.1f}ms"
    return f"{ms / 1000:.2f}s"


def _truncate_sha(s: str, head: int = 12) -> str:
    if not s:
        return "—"
    if s.startswith("sha256:"):
        return s[: 7 + head] + "…"
    return s[:head] + ("…" if len(s) > head else "")


def _yes_no(v: Any) -> str:
    if v is True:
        return "✅"
    if v is False:
        return "❌"
    return "—"


def _sample_values(values: Any, *, limit: int = 8) -> str:
    vals = [str(v).strip() for v in (values or []) if str(v).strip()]
    if not vals:
        return "none"
    suffix = f" (+{len(vals) - limit} more)" if len(vals) > limit else ""
    return ", ".join(vals[:limit]) + suffix


def _gate_status(gates: Any, gate_id: str) -> str:
    for gate in gates or []:
        if not isinstance(gate, dict):
            continue
        if str(gate.get("gate_id") or gate.get("id") or gate.get("name") or "") != gate_id:
            continue
        passed = gate.get("pass")
        if passed is None:
            passed = gate.get("passed")
        return "PASS" if bool(passed) else "FAIL"
    return "missing"


def _repo_rel(path: Path) -> str:
    try:
        rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
    except ValueError:
        rel = path
    return str(rel)


def _safe_manifest_rel(value: Any, default: str) -> Path:
    raw = str(value or "").strip().replace("\\", "/") or default
    if raw.startswith(("/", "\\")) or (len(raw) > 1 and raw[1] == ":"):
        raw = default
    if ".." in raw.split("/"):
        raw = default
    return Path(raw)


def _first_existing_path(run_dir: Path, candidates: List[Path]) -> Path:
    for candidate in candidates:
        path = run_dir / candidate
        if path.is_file():
            return path
    return run_dir / candidates[0]


def _artifact_status(path: Path, *, required: bool, optional_reason: str = "") -> str:
    if path.is_file():
        return f"✅ {path.stat().st_size:,} bytes"
    if required:
        return "❌ missing"
    reason = optional_reason.strip() or "not required by this run contract"
    return f"➖ optional ({reason})"


def _bundle_role_required(run_dir: Path, role: str, default: bool = False) -> bool:
    bundle = _load_json(run_dir / "RUN_BUNDLE_INDEX.json") or {}
    for entry in bundle.get("entries") or []:
        if isinstance(entry, dict) and entry.get("role") == role:
            return bool(entry.get("required"))
    return default


# ------------------------------------------------------------------- renderers


def _render_identity(run_dir: Path, identity: Optional[Dict[str, Any]],
                     manifest: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Run Identity", ""]
    payload = (identity or {}).get("payload", {}) if identity else {}
    rows: List[Tuple[str, str]] = [
        ("Run dir", str(run_dir.relative_to(REPO_ROOT)) if run_dir.is_relative_to(REPO_ROOT) else str(run_dir)),
        ("Run ID", payload.get("run_id") or (manifest or {}).get("run_id") or "—"),
        ("Request ID", payload.get("request_id") or (manifest or {}).get("request_id") or "—"),
        ("Route", payload.get("route_id") or (manifest or {}).get("route_id") or "—"),
        ("Chain kind", (manifest or {}).get("chain_kind") or "—"),
        ("Started at (UTC)", payload.get("started_at_utc") or "—"),
        ("Git commit", _truncate_sha(payload.get("git_commit") or "")),
        ("Git dirty", _yes_no(payload.get("git_dirty"))),
        ("Deterministic digest", _truncate_sha(payload.get("deterministic_digest") or "")),
        ("Replay key", payload.get("replay_key") or "—"),
        ("X3 disposition", (manifest or {}).get("x3_disposition") or "—"),
    ]
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for k, v in rows:
        lines.append(f"| **{k}** | `{v}` |")
    lines.append("")
    return lines


def _render_fact_vector_readiness_gates(run_dir: Path) -> List[str]:
    receipts = [
        ("Gate A pre-U0", _load_json(run_dir / "pre_u0_fact_vector_readiness.json") or {}),
        ("Gate B post-U0", _load_json(run_dir / "post_u0_section_sufficiency_preview.json") or {}),
    ]
    receipts = [(label, doc) for label, doc in receipts if doc]
    if not receipts:
        return []

    lines: List[str] = ["## Fact-Vector Readiness Gates", ""]
    lines.append("| Gate | Status | Collection | Manifest | Failed sections | Reasons |")
    lines.append("|---|---|---|---|---:|---|")
    for label, doc in receipts:
        collection = doc.get("collection") if isinstance(doc.get("collection"), dict) else {}
        summary = doc.get("summary") if isinstance(doc.get("summary"), dict) else {}
        manifest = doc.get("bootstrap_manifest") if isinstance(doc.get("bootstrap_manifest"), dict) else {}
        failed = doc.get("failed_sections") if isinstance(doc.get("failed_sections"), list) else []
        reasons = doc.get("reasons") if isinstance(doc.get("reasons"), list) else []
        lines.append(
            f"| {label} | `{doc.get('status') or 'missing'}` "
            f"`{doc.get('block_code') or '—'}` | "
            f"`{collection.get('collection_doc_count', summary.get('collection_doc_count', 0))}` docs, "
            f"dim `{collection.get('collection_dimension', summary.get('collection_dimension', '—'))}` | "
            f"present `{manifest.get('present', '—')}`, "
            f"required lanes `{len(manifest.get('required_lanes') or [])}` | "
            f"{len(failed)} | `{_sample_values(reasons, limit=5)}` |"
        )
    lines.append("")
    lines.append(
        "Policy: live `fact_vectors` must be hydrated before U0/C0; section generation "
        "may compare against them. Grounded write-back rows stage during C0 and may only "
        "promote to live Chroma after X3 through UWG/L4."
    )
    lines.append("")
    return lines


def _render_whole_run_cache_preflight(run_dir: Path) -> List[str]:
    receipt = _load_json(run_dir / "whole_run_cache_preflight.json")
    if not receipt:
        return []
    eligibility = receipt.get("r1b_eligibility") if isinstance(receipt.get("r1b_eligibility"), dict) else {}
    preflight = receipt.get("preflight") if isinstance(receipt.get("preflight"), dict) else {}
    if not eligibility and isinstance(preflight.get("r1b_eligibility"), dict):
        eligibility = preflight.get("r1b_eligibility") or {}
    reuse_policy = receipt.get("reuse_authority_policy") if isinstance(receipt.get("reuse_authority_policy"), dict) else {}
    rows = [
        ("R1A", str(receipt.get("r1a_preflight_status") or "—"), ""),
        (
            "R1B",
            str(receipt.get("r1b_preflight_status") or "—"),
            str(receipt.get("r1b_preflight_reason") or eligibility.get("reason") or "—"),
        ),
        (
            "R1B reuse authority",
            _yes_no(eligibility.get("reuse_authority_enabled")),
            str(eligibility.get("reuse_authority_env") or "APPS_RG_ENABLE_R1B_SEMANTIC_CACHE"),
        ),
        (
            "R1B probeable",
            _yes_no(eligibility.get("probeable")),
            str(eligibility.get("decisive_reason") or "—"),
        ),
        (
            "C0 fact_vectors consulted",
            _yes_no(reuse_policy.get("c0_fact_vectors_consulted")),
            "R1B is separate from C0 fact_vectors",
        ),
    ]
    lines = ["## Whole-Run Cache Preflight", ""]
    lines.append("| Lane | Status | Reason |")
    lines.append("|---|---|---|")
    for lane, status, reason in rows:
        lines.append(f"| **{lane}** | `{status}` | `{reason}` |")
    lines.append("")
    return lines


def _render_mandatory_run_outputs(run_dir: Path) -> List[str]:
    ledger_path = run_dir / APPS_RG_MANDATORY_RUN_OUTPUT_JSON
    ledger_md = run_dir / APPS_RG_MANDATORY_RUN_OUTPUT_MD
    bcg_md = run_dir / BCG_EXECUTIVE_OUTPUT_MD
    ledger = _load_json(ledger_path) or {}
    lines: List[str] = ["## Mandatory BCG / Run-Ledger Outputs", ""]
    lines.append("| Artifact | Path | Status |")
    lines.append("|---|---|---|")
    for label, path in (
        ("BCG executive output", bcg_md),
        ("Mandatory run output", ledger_md),
        ("Mandatory run output JSON", ledger_path),
    ):
        lines.append(
            f"| **{label}** | `{_repo_rel(path)}` | {_artifact_status(path, required=True)} |"
        )
    if not ledger:
        lines.append("")
        lines.append(
            "**RCA gap:** mandatory run output JSON is missing. This run is not "
            "operator-ready until BCG and run-ledger artifacts are emitted."
        )
        lines.append("")
        return lines

    counts = ledger.get("section_counts") if isinstance(ledger.get("section_counts"), dict) else {}
    result = ledger.get("result_summary") if isinstance(ledger.get("result_summary"), dict) else {}
    rca = ledger.get("rca_findings") if isinstance(ledger.get("rca_findings"), list) else []
    final_out = ledger.get("final_resume_output") if isinstance(ledger.get("final_resume_output"), dict) else {}
    lines.append("")
    lines.append("| Signal | Value |")
    lines.append("|---|---|")
    lines.append(f"| Outcome authorized | `{result.get('outcome_authorized')}` |")
    lines.append(f"| Exit status | `{result.get('exit_status') or '—'}` |")
    lines.append(f"| X3 disposition | `{result.get('x3_disposition') or '—'}` |")
    lines.append(f"| Final resume output gate | `{final_out.get('status') or 'UNKNOWN'}` |")
    lines.append(
        "| Section counts | "
        f"total `{counts.get('total', 0)}`, real LLM `{counts.get('ran_real_llm', 0)}`, "
        f"allow `{counts.get('allowed', 0)}`, block `{counts.get('blocked', 0)}`, "
        f"pre-run `{counts.get('pre_run_blocked', 0)}`, not-run `{counts.get('not_run', 0)}` |"
    )
    lines.append(f"| RCA findings | `{len(rca)}` |")
    if final_out:
        lines.append("")
        lines.append("Final resume mandatory outputs:")
        lines.append("")
        lines.append("| Artifact | Path | Status | Bytes |")
        lines.append("|---|---|---|---:|")
        for label, key in (
            ("Canonical final resume JSON", "final_resume_json"),
            ("Rendered final resume text", "rendered_resume_text"),
            ("Final resume DOCX", "resume_docx"),
        ):
            art = final_out.get(key) if isinstance(final_out.get(key), dict) else {}
            exists = "PASS" if art.get("exists") else "MISSING"
            lines.append(
                f"| **{label}** | `{art.get('relpath') or '—'}` | `{exists}` | {int(art.get('bytes') or 0)} |"
            )
        failed_final = final_out.get("failed_gate_ids") if isinstance(final_out.get("failed_gate_ids"), list) else []
        lines.append("")
        lines.append(
            "Final resume failed gates: "
            + ("`" + "`, `".join(str(g) for g in failed_final) + "`" if failed_final else "`none`")
        )
    if rca:
        lines.append("")
        lines.append("Top RCA findings:")
        for finding in rca[:5]:
            if not isinstance(finding, dict):
                continue
            lines.append(
                f"- `{finding.get('section')}`: {finding.get('classification')} "
                f"({finding.get('evidence') or 'no gate evidence'})."
            )
            lines.append(f"  - Root cause: {finding.get('root_cause') or 'missing'}")
            allocation = _rca_causal_allocation(finding)
            if allocation:
                lines.append("  - Causal allocation:")
                lines.append(f"    - Dominant cause: {allocation['dominant_cause']}")
                lines.append(
                    f"    - Retry recoverability: `{allocation['retry_recoverability']}` - "
                    f"{allocation['retry_recoverability_reason']}"
                )
                lines.append("    - Allocation rows:")
                for row in allocation["allocation"]:
                    evidence = ", ".join(str(ref) for ref in row.get("evidence_refs") or [])
                    lines.append(
                        f"      - `{row['domain']}` / `{row['causal_role']}` / "
                        f"`{row['work_share']}`: {row['root_cause_link']} "
                        f"Evidence: `{evidence}`. Required work: {row['required_work']}"
                    )
            else:
                lines.append(
                    "  - **RCA format gap:** missing causal allocation with concrete root-cause-linked rows."
                )
            plan = _rca_implementation_plan(finding)
            if plan:
                lines.append("  - Required implementation plan:")
                for item in plan:
                    lines.append(f"    - {item}")
            else:
                lines.append(
                    "  - **RCA format gap:** missing 3-5 root-cause implementation bullets."
                )
    lines.append("")
    return lines


def _rca_implementation_plan(finding: Dict[str, Any]) -> List[str]:
    plan = finding.get("implementation_plan")
    if not isinstance(plan, list):
        return []
    items = [str(item).strip() for item in plan if str(item).strip()]
    if 3 <= len(items) <= 5:
        return items
    return []


def _rca_causal_allocation(finding: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    allocation = finding.get("causal_allocation")
    if not isinstance(allocation, dict):
        return None
    rows = allocation.get("allocation")
    if not isinstance(rows, list) or not rows:
        return None
    required = {"domain", "causal_role", "root_cause_link", "work_share", "evidence_refs", "required_work"}
    valid_rows: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not required.issubset(row):
            return None
        domain = str(row.get("domain") or "").strip()
        root_cause_link = str(row.get("root_cause_link") or "").strip()
        if not domain or not root_cause_link or domain == root_cause_link or len(root_cause_link) < 20:
            return None
        evidence_refs = row.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            return None
        valid_rows.append(row)
    dominant = str(allocation.get("dominant_cause") or "").strip()
    retry = str(allocation.get("retry_recoverability") or "").strip()
    retry_reason = str(allocation.get("retry_recoverability_reason") or "").strip()
    if not dominant or not retry or not retry_reason:
        return None
    return {
        "dominant_cause": dominant,
        "retry_recoverability": retry,
        "retry_recoverability_reason": retry_reason,
        "allocation": valid_rows,
    }


def _render_bcg_competencies_report(run_dir: Path) -> List[str]:
    if not (run_dir / "competencies_display.txt").is_file():
        return []
    runtime = _load_json(run_dir / "runtime_graph_sourcing_assessment.json") or {}
    x3 = _load_json(run_dir / "x3_disposition.json") or {}
    x2 = _load_json(run_dir / "x2_gate_outputs.json") or {}
    x1d = _load_json(run_dir / "x1d_llm_judge_outputs.json") or {}
    visible = _load_json(run_dir / "competencies_visible_graph_surface_enrichment_receipt.json") or {}
    c0_room = _load_json(run_dir / "c0_evidence_room_receipt.json") or {}
    c02_vector = _load_json(run_dir / "c02_vector_query.json") or {}
    preflight_artifact = _load_json(run_dir / "c02_fact_vector_index_preflight.json") or {}
    semantic_payload = _load_json(run_dir / "c02_semantic_cache_payload.json") or {}
    display = _load_text(run_dir / "competencies_display.txt")

    traversal = runtime.get("traversal")
    traversal = traversal if isinstance(traversal, dict) else runtime
    confidence = runtime.get("confidence_decomposition")
    confidence = confidence if isinstance(confidence, dict) else {}
    frontier = traversal.get("frontier_size_by_hop_depth")
    frontier = frontier if isinstance(frontier, dict) else {}
    comparison = traversal.get("selected_vs_rejected_candidate_comparison")
    comparison = comparison if isinstance(comparison, dict) else {}
    axes = traversal.get("role_specific_axis_coverage")
    axes = axes if isinstance(axes, dict) else {}
    depth = traversal.get("graph_evidence_depth_comparison")
    depth = depth if isinstance(depth, dict) else {}
    gates = x2.get("gates") or x2.get("gate_outputs") or []
    judges = [row for row in (x1d.get("judges") or []) if isinstance(row, dict)]
    visible_rows = [
        row for row in (visible.get("rows") or [])
        if isinstance(row, dict) and row.get("surface") == "competencies"
    ]
    bridge_room = ((c0_room.get("bridge_doc") or {}).get("c0_evidence_room") or {})
    c02_room = c0_room.get("c02") if isinstance(c0_room.get("c02"), dict) else {}
    if not c02_room:
        c02_room = bridge_room.get("c02") if isinstance(bridge_room.get("c02"), dict) else {}
    c05_room = c0_room.get("c05") if isinstance(c0_room.get("c05"), dict) else {}
    if not c05_room:
        c05_room = bridge_room.get("c05") if isinstance(bridge_room.get("c05"), dict) else {}
    preflight = c05_room.get("fact_vector_index_preflight")
    if not isinstance(preflight, dict):
        preflight = c02_room.get("fact_vector_index_preflight")
    preflight = preflight if isinstance(preflight, dict) else {}
    if not preflight:
        preflight = preflight_artifact
    preflight_collection = preflight.get("collection") if isinstance(preflight.get("collection"), dict) else {}
    write_receipt = c02_room.get("c02_chroma_write")
    write_receipt = write_receipt if isinstance(write_receipt, dict) else {}
    ingest_receipt = c02_room.get("fact_vectors_ingest")
    ingest_receipt = ingest_receipt if isinstance(ingest_receipt, dict) else {}
    vector_query = c02_vector if c02_vector else c05_room.get("c02_vector_query")
    vector_query = vector_query if isinstance(vector_query, dict) else {}
    intent_vector = semantic_payload.get("intent_vector")
    intent_vector = intent_vector if isinstance(intent_vector, dict) else {}
    lanes = vector_query.get("lanes") if isinstance(vector_query.get("lanes"), dict) else {}
    lane_summary = ", ".join(f"{k}:{v}" for k, v in lanes.items()) or "missing"
    display_order: dict[str, int] = {}
    for idx, line in enumerate(display.splitlines(), 1):
        label = line.split(":", 1)[0].strip()
        if label and label not in display_order:
            display_order[label] = idx

    def _visible_row_sort_key(row: Dict[str, Any]) -> tuple[int, int]:
        label = str(row.get("resume_display_label") or "").strip()
        fallback = int(row.get("order_index") or 999)
        return (display_order.get(label, 999), fallback)

    judge_summary = ", ".join(
        f"{j.get('provider_name') or j.get('provider_key')}: {j.get('provider_status') or 'unknown'}"
        for j in judges
    )
    rubric_versions = sorted({str(j.get("rubric_version")) for j in judges if j.get("rubric_version")})
    svp_judge_status = ", ".join(
        f"{j.get('provider_name') or j.get('provider_key')}: "
        f"{((j.get('dimension_verdicts') or {}).get('svp_agentic_specificity') or {}).get('pass', 'missing')}"
        for j in judges
    )

    lines: List[str] = ["## BCG Competencies Improvement Report", ""]
    lines.append(
        "**Executive readout:** standalone competencies are graph-sourced, partnership-ordered, "
        "and visibly enriched when the visible graph surface receipt is present."
    )
    lines.append("")
    lines.append("| Signal | Value |")
    lines.append("|---|---|")
    lines.append(f"| X3 / runtime | `{x3.get('x3_code') or '—'}` / `{x3.get('runtime_generation_status') or '—'}` |")
    lines.append(f"| Proof eligible | `{x3.get('proof_eligible')}` |")
    lines.append(f"| Role profile | `{traversal.get('target_role_profile') or 'unknown'}` |")
    lines.append(f"| Selection method | `{traversal.get('selection_method') or 'unknown'}` |")
    lines.append(
        "| C0 fact-vector index | "
        f"status `{preflight.get('status') or 'missing'}`, "
        f"collection `{preflight_collection.get('collection_name') or 'fact_vectors'}`, "
        f"count `{preflight_collection.get('collection_count') or 0}`, "
        f"section hits `{preflight_collection.get('section_target_count') or 0}`, "
        f"model `{preflight.get('expected_embedding_model') or '—'}`, "
        f"dim `{preflight.get('expected_embedding_dim') or '—'}` |"
    )
    lines.append(
        "| C0.2 retrieval compare | "
        f"required `{vector_query.get('product_hybrid_required', '—')}`, "
        f"attempted `{vector_query.get('product_hybrid_attempted', '—')}`, "
        f"lanes `{lane_summary}`, "
        f"mode `{vector_query.get('c0_retrieval_mode') or '—'}`, "
        f"enrichment `{vector_query.get('hybrid_enrichment_item_count') or 0}` |"
    )
    lines.append(
        "| C0.2 same-run write | "
        f"attempted `{write_receipt.get('attempted', ingest_receipt.get('attempted', '—'))}`, "
        f"status `{write_receipt.get('status') or ingest_receipt.get('status') or 'missing'}`, "
        f"upserted `{write_receipt.get('upserted_count', ingest_receipt.get('upserted_count', 0))}`, "
        f"reason `{write_receipt.get('reason') or ingest_receipt.get('reason') or '—'}`, "
        f"policy `{preflight.get('same_run_write_policy') or '—'}` |"
    )
    lines.append(
        "| Intent vector | "
        f"model `{intent_vector.get('embedding_model') or '—'}`, "
        f"dim `{intent_vector.get('dimensions') or '—'}`, "
        f"digest `{_truncate_sha(str(semantic_payload.get('intent_digest') or ''))}`, "
        f"query output `{semantic_payload.get('query_output_count', '—')}` |"
    )
    lines.append(
        "| Fact vector store | "
        f"path `{preflight.get('chroma_path') or '—'}`, "
        f"manifest upserts `{preflight.get('manifest_upserted_count', '—')}`, "
        f"manifest count `{preflight.get('manifest_collection_count_after', '—')}`, "
        f"sparse sidecar `{preflight.get('manifest_sparse_sidecar_built', '—')}` |"
    )
    lines.append(f"| Depth status | `{traversal.get('graph_evidence_depth_status') or 'unknown'}` |")
    lines.append(
        "| Frontier | "
        f"roots `{frontier.get('0_role_episode_roots') or 0}`, "
        f"skills `{frontier.get('1_leaf_skill_candidates') or 0}`, "
        f"metrics `{frontier.get('2_metric_outcome_candidates') or 0}` |"
    )
    lines.append(
        "| Selected graph evidence | "
        f"roots `{traversal.get('selected_role_episode_root_count') or 0}`, "
        f"skills `{traversal.get('selected_unique_leaf_skill_count') or 0}`, "
        f"metrics `{traversal.get('selected_unique_metric_count') or 0}` |"
    )
    lines.append(
        "| Rejected alternatives | "
        f"sibling skills `{traversal.get('rejected_sibling_skill_count') or 0}`, "
        f"sibling metrics `{traversal.get('rejected_sibling_metric_count') or 0}`, "
        f"selector rejected `{comparison.get('selector_rejected_neighbor_count') or 0}` |"
    )
    lines.append(f"| Confidence values | `{_sample_values(confidence.get('category_confidence_values'), limit=12)}` |")
    lines.append(f"| Covered role axes | `{_sample_values(axes.get('covered_axes'), limit=12)}` |")
    lines.append(f"| Missing role axes | `{_sample_values(axes.get('missing_axes'), limit=12)}` |")
    lines.append(f"| Visible graph surface | `{visible.get('schema_version') or 'missing'}` |")
    if judges:
        lines.append(f"| X1D judges | `{judge_summary}` |")
        lines.append(f"| X1D rubric versions | `{_sample_values(rubric_versions, limit=8)}` |")
        lines.append(f"| SVP agentic specificity judge | `{svp_judge_status}` |")
    lines.append("")

    lines.append("**Preserved Quality Controls**" if visible_rows else "**Open Improvement Opportunities**")
    lines.append("")
    if visible_rows:
        lines.append("1. **Graph-bound visible surface:** each visible category has `resume_display_label`, `competency_bundle_id`, graph skills, and graph-derived terms.")
    else:
        lines.append("1. **Block generic visible output:** visible graph surface receipt is missing, so the section may still be using old taxonomy labels only.")
    lines.append("2. **Partnership-first ordering:** prioritize ecosystem/co-sell fit before generic strategy and leadership wrappers for Anthropic partnership roles.")
    lines.append("3. **Rejected-path evidence:** report rejected sibling skills/metrics so operators can see what graph paths were explored but not selected.")
    lines.append("4. **Confidence diversity:** nonconstant per-category confidence remains visible to prevent all categories collapsing onto one default fact.")
    lines.append("")

    lines.append("**Graph / Richness Gates**")
    lines.append("")
    lines.append("| Gate | Status |")
    lines.append("|---|---|")
    for gate_id in [
        "x2_competencies_graph_traversal_sufficiency",
        "x2_competencies_graph_granularity_gates",
        "x2_competencies_source_fact_concentration_limit",
        "x2_competencies_per_category_confidence_nonconstant",
        "x2_competencies_no_metrics_as_skills_without_capability_context",
        "x2_competencies_no_metric_ids_in_source_fact_ids",
        "x2_competencies_visible_terms_svp_agentic_richness",
        "x2_competencies_keyword_repetition_limit",
    ]:
        lines.append(f"| `{gate_id}` | `{_gate_status(gates, gate_id)}` |")
    lines.append("")

    if visible_rows:
        lines.append("**Visible Competency Order**")
        lines.append("")
        lines.append("| Order | Display label | Bundle | Visible terms |")
        lines.append("|---:|---|---|---|")
        for idx, row in enumerate(sorted(visible_rows, key=_visible_row_sort_key), 1):
            lines.append(
                f"| {idx} | {row.get('resume_display_label') or '—'} | "
                f"`{row.get('competency_bundle_id') or '—'}` | "
                f"{_sample_values(row.get('visible_terms'), limit=4)} |"
            )
        lines.append("")

    if depth.get("summary"):
        lines.append(f"Depth delta: `{depth.get('summary')}`")
        lines.append("")
    if display:
        lines.append("**Competencies Display**")
        lines.append("")
        lines.append("```text")
        lines.append(display)
        lines.append("```")
        lines.append("")
    return lines


def _render_bcg_unify_bullets_report(run_dir: Path) -> List[str]:
    output_text = _load_text(run_dir / "unify_bullets_output.txt")
    c0_room = _load_json(run_dir / "c0_evidence_room_receipt.json") or {}
    c02_vector = _load_json(run_dir / "c02_vector_query.json") or {}
    preflight_artifact = _load_json(run_dir / "c02_fact_vector_index_preflight.json") or {}
    semantic_payload = _load_json(run_dir / "c02_semantic_cache_payload.json") or {}
    c07 = _load_json(run_dir / "c07_handoff_audit.json") or {}
    x2 = _load_json(run_dir / "x2_gate_outputs.json") or {}
    x3 = _load_json(run_dir / "x3_disposition.json") or {}

    bridge_room = ((c0_room.get("bridge_doc") or {}).get("c0_evidence_room") or {})
    c02_room = c0_room.get("c02") if isinstance(c0_room.get("c02"), dict) else {}
    if not c02_room:
        c02_room = bridge_room.get("c02") if isinstance(bridge_room.get("c02"), dict) else {}
    c05_room = c0_room.get("c05") if isinstance(c0_room.get("c05"), dict) else {}
    if not c05_room:
        c05_room = bridge_room.get("c05") if isinstance(bridge_room.get("c05"), dict) else {}
    if not c07:
        c07 = c0_room.get("c07") if isinstance(c0_room.get("c07"), dict) else {}
    preflight = c05_room.get("fact_vector_index_preflight")
    if not isinstance(preflight, dict):
        preflight = c02_room.get("fact_vector_index_preflight")
    preflight = preflight if isinstance(preflight, dict) else preflight_artifact
    preflight = preflight if isinstance(preflight, dict) else {}
    if (
        not output_text
        and str(c02_vector.get("section_id") or preflight.get("section_id") or "") != "unify_bullets"
    ):
        return []

    collection = preflight.get("collection") if isinstance(preflight.get("collection"), dict) else {}
    unify = preflight.get("unify_bullets_sufficiency")
    unify = unify if isinstance(unify, dict) else {}
    traversal = unify.get("graph_traversal_receipt")
    traversal = traversal if isinstance(traversal, dict) else {}
    write_receipt = c02_room.get("c02_chroma_write")
    write_receipt = write_receipt if isinstance(write_receipt, dict) else {}
    ingest_receipt = c02_room.get("fact_vectors_ingest")
    ingest_receipt = ingest_receipt if isinstance(ingest_receipt, dict) else {}
    vector_query = c02_vector if c02_vector else c05_room.get("c02_vector_query")
    vector_query = vector_query if isinstance(vector_query, dict) else {}
    lanes = vector_query.get("lanes") if isinstance(vector_query.get("lanes"), dict) else {}
    lane_summary = ", ".join(f"{k}:{v}" for k, v in lanes.items()) or "missing"
    intent_vector = semantic_payload.get("intent_vector")
    intent_vector = intent_vector if isinstance(intent_vector, dict) else {}
    checks = c07.get("checks") if isinstance(c07.get("checks"), dict) else {}
    gates = [g for g in (x2.get("gates") or []) if isinstance(g, dict)]

    def _gate_status(gate_id: str) -> str:
        for gate in gates:
            if gate.get("gate_id") == gate_id:
                return "PASS" if gate.get("pass") or gate.get("passed") else "FAIL"
        return "missing"

    expected_slots = list(unify.get("expected_slot_ids") or [])
    missing_slots = list(unify.get("missing_source_fact_slots") or [])
    missing_metric_slots = list(unify.get("missing_metric_outcome_slots") or [])
    lines: List[str] = ["## BCG Unify Bullets C0-C7 Report", ""]
    lines.append(
        "**Executive readout:** Unify bullets require pre-existing six-slot fact vectors plus "
        "approved metric-outcome lineage before generation; C0.2 remains read/compare only."
    )
    lines.append("")
    lines.append("| Signal | Value |")
    lines.append("|---|---|")
    lines.append(f"| X3 / runtime | `{x3.get('x3_code') or '—'}` / `{x3.get('runtime_generation_status') or '—'}` |")
    lines.append(
        "| C0 fact-vector index | "
        f"status `{preflight.get('status') or 'missing'}`, "
        f"collection `{collection.get('collection_name') or 'fact_vectors'}`, "
        f"count `{collection.get('collection_count') or 0}`, "
        f"section hits `{collection.get('section_target_count') or 0}`, "
        f"model `{preflight.get('expected_embedding_model') or '—'}`, "
        f"dim `{preflight.get('expected_embedding_dim') or '—'}` |"
    )
    lines.append(
        "| Unify six-slot sufficiency | "
        f"status `{unify.get('status') or 'missing'}`, "
        f"slots `{len(expected_slots) - len(missing_slots)}/{len(expected_slots)}`, "
        f"missing source slots `{missing_slots or 'none'}`, "
        f"missing metric slots `{missing_metric_slots or 'none'}` |"
    )
    lines.append(
        "| Unify metric/graph depth | "
        f"unique metrics `{len(unify.get('unique_metric_outcome_ids') or [])}`, "
        f"metric distribution `{unify.get('metric_distribution_pass')}`, "
        f"roots `{traversal.get('selected_role_episode_root_count') or 0}`, "
        f"skills `{traversal.get('selected_unique_leaf_skill_count') or 0}`, "
        f"metrics `{traversal.get('selected_unique_metric_count') or 0}`, "
        f"graph traversal `{unify.get('graph_traversal_pass')}`, "
        f"granularity `{unify.get('graph_granularity_pass')}` |"
    )
    lines.append(
        "| C0.2 retrieval compare | "
        f"required `{vector_query.get('product_hybrid_required', '—')}`, "
        f"attempted `{vector_query.get('product_hybrid_attempted', '—')}`, "
        f"lanes `{lane_summary}`, "
        f"mode `{vector_query.get('c0_retrieval_mode') or '—'}`, "
        f"enrichment `{vector_query.get('hybrid_enrichment_item_count') or 0}` |"
    )
    lines.append(
        "| C0.2 same-run write | "
        f"attempted `{write_receipt.get('attempted', ingest_receipt.get('attempted', '—'))}`, "
        f"status `{write_receipt.get('status') or ingest_receipt.get('status') or 'missing'}`, "
        f"upserted `{write_receipt.get('upserted_count', ingest_receipt.get('upserted_count', 0))}`, "
        f"reason `{write_receipt.get('reason') or ingest_receipt.get('reason') or '—'}`, "
        f"policy `{preflight.get('same_run_write_policy') or '—'}` |"
    )
    policy = preflight.get("delayed_loop_policy")
    policy = policy if isinstance(policy, dict) else {}
    lines.append(
        "| Delayed loop policy | "
        f"pre-run index `{policy.get('pre_run_fact_vector_index_required', '—')}`, "
        f"live C0 write `{policy.get('live_write_during_c0', '—')}`, "
        f"generated route `{policy.get('generated_output_route') or '—'}`, "
        f"promotion `{policy.get('promotion_gate') or '—'}` |"
    )
    lines.append(
        "| Intent vector | "
        f"model `{intent_vector.get('embedding_model') or '—'}`, "
        f"dim `{intent_vector.get('dimensions') or '—'}`, "
        f"digest `{_truncate_sha(str(semantic_payload.get('intent_digest') or ''))}`, "
        f"query output `{semantic_payload.get('query_output_count', '—')}` |"
    )
    lines.append(
        "| C0.7 handoff | "
        f"safe `{c07.get('handoff_safe', '—')}`, "
        f"unify sufficiency `{checks.get('unify_bullets_fact_vector_sufficiency_status', '—')}`, "
        f"metric distribution `{checks.get('unify_bullets_metric_distribution_pass', '—')}` |"
    )
    lines.append(
        "| X2 metric lineage gates | "
        f"lineage `{_gate_status('x2_unify_each_bullet_approved_metric_outcome_lineage')}`, "
        f"visible surface `{_gate_status('x2_unify_each_bullet_metric_outcome_surface_visible')}`, "
        f"distribution `{_gate_status('x2_unify_metric_outcomes_distributed_by_slot')}` |"
    )
    lines.append("")
    if output_text:
        lines.append("**Unify Bullets Display**")
        lines.append("")
        lines.append("```text")
        lines.append(output_text)
        lines.append("```")
        lines.append("")
    return lines


def _render_l2_substages(terminal_packet: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## L2 Sub-Stages (Steps)", ""]
    if not terminal_packet:
        lines.append("_terminal_ret_packet.json not found — substages unavailable._")
        lines.append("")
        return lines
    stages = (terminal_packet.get("payload", {}) or {}).get("l2_sub_stages", []) or []
    if not stages:
        lines.append("_No L2 sub-stages recorded._")
        lines.append("")
        return lines
    lines.append("| Step | Stage | Status | Duration |")
    lines.append("|---|---|---|---|")
    for st in stages:
        sid = st.get("sub_stage_id", "?")
        sname = st.get("sub_stage_name", "?")
        status = st.get("status", "—")
        dur = st.get("duration_ms", 0.0)
        icon = {"PASS": "✅", "FAIL": "❌", "BYPASSED": "⏭️"}.get(status, "•")
        lines.append(f"| **{sid}** | {sname} | {icon} {status} | {_fmt_dur_ms(dur)} |")
    lines.append("")
    return lines


def _render_hop_checkpoints(run_report: Optional[Dict[str, Any]], run_dir: Path | None = None) -> List[str]:
    lines: List[str] = ["## Narrative HOP Checkpoints (Sub-steps)", ""]
    if not run_report:
        if run_dir is not None and (run_dir / FULL_RUN_SECTION_STATUS_JSON).is_file():
            lines.append(
                "_Legacy run_report.json not emitted; modular R4 section status is rendered below._"
            )
        else:
            lines.append("_run_report.json not found — narrative HOPs unavailable._")
        lines.append("")
        return lines
    checkpoints = run_report.get("checkpoints", []) or []
    if not checkpoints:
        lines.append("_No HOP checkpoints recorded._")
        lines.append("")
        return lines
    # All checkpoints listed reached PASS by virtue of being recorded.
    lines.append("Reached: " + ", ".join(f"`{c}`" for c in checkpoints))
    lines.append("")
    completed = run_report.get("narrative_completed_at")
    if completed:
        lines.append(f"Narrative pass completed at: `{completed}`")
        lines.append("")
    return lines


def _render_section_verdicts(run_report: Optional[Dict[str, Any]], run_dir: Path | None = None) -> List[str]:
    lines: List[str] = ["## Per-Section Narrative Verdicts", ""]
    if not run_report:
        if run_dir is not None and (run_dir / FULL_RUN_SECTION_STATUS_JSON).is_file():
            lines.append(
                "_Legacy run_report.json not emitted; modular R4 section verdicts are rendered below._"
            )
        else:
            lines.append("_run_report.json not found — verdicts unavailable._")
        lines.append("")
        return lines
    narrative = run_report.get("narrative", {}) or {}
    verdicts = narrative.get("per_section_verdicts", []) or []
    if not verdicts:
        lines.append("_No per-section verdicts recorded._")
        lines.append("")
        return lines
    lines.append("| Section | Tier | Source | Composite | Accepted | First failed gate |")
    lines.append("|---|---|---|---|---|---|")
    for v in verdicts:
        section = summary_section_label(str(v.get("section_id", "?")))
        tier = v.get("tier", "?")
        source = v.get("chosen_source", "?")
        comp = v.get("composite", 0.0)
        accepted = v.get("accepted")
        gate = v.get("failed_gate") or "—"
        icon = "✅" if accepted else "❌"
        lines.append(
            f"| `{section}` | {tier} | {source} | {comp:.4f} | {icon} | `{gate}` |"
        )
    lines.append("")
    return lines


def _render_modular_section_status(run_dir: Path) -> List[str]:
    status_doc = _load_json(run_dir / FULL_RUN_SECTION_STATUS_JSON) or {}
    lanes = [row for row in (status_doc.get("lanes") or []) if isinstance(row, dict)]
    if not lanes:
        return []
    lines: List[str] = ["## Modular Section Status", ""]
    lines.append(
        f"Source: `{FULL_RUN_SECTION_STATUS_JSON}` — modular R4 section evidence "
        "when legacy `run_report.json` is not emitted."
    )
    lines.append("")
    lines.append("| Section | X3 | X2 | Product quality | Runtime | Judges / score | Display |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in lanes:
        display = str(row.get("display_txt_relpath") or "").strip()
        display_status = f"`{display}`" if display else "—"
        judges = str(row.get("judge_summary") or "").strip()
        if not judges and row.get("judges"):
            judge_cells = []
            for judge in row.get("judges") or []:
                if not isinstance(judge, dict):
                    continue
                provider = judge.get("provider_name") or judge.get("provider_key") or "judge"
                model = judge.get("model_name") or ""
                score = judge.get("score", "—")
                threshold = judge.get("threshold", "—")
                verdict = "PASS" if judge.get("pass") is True else "FAIL" if judge.get("pass") is False else "UNKNOWN"
                model_text = f" `{model}`" if model else ""
                judge_cells.append(f"{provider}{model_text}: {score}/5 vs {threshold} {verdict}")
            judges = "; ".join(judge_cells)
        judges_status = judges or "—"
        lines.append(
            f"| `{row.get('lane') or '—'}` | `{row.get('x3_code') or '—'}` | "
            f"`{row.get('x2_pass') or '—'}` | `{row.get('product_quality_status') or '—'}` | "
            f"`{row.get('runtime_generation_status') or '—'}` | {judges_status} | {display_status} |"
        )
    lines.append("")
    return lines


def _render_gate_failures(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Gate Failures", ""]
    if not run_report:
        return []
    failures = (run_report.get("narrative", {}) or {}).get("gate_failures", []) or []
    if not failures:
        lines.append("_None — all gates passed._")
        lines.append("")
        return lines
    for i, f in enumerate(failures, 1):
        section_raw = str(f.get("section_id", "—"))
        section = summary_section_label(section_raw)
        gate = f.get("failed_gate") or f.get("reason") or "—"
        detail = f.get("detail") or ""
        if section != section_raw:
            lines.append(f"**{i}.** section=`{section}` (id=`{section_raw}`) gate=`{gate}`")
        else:
            lines.append(f"**{i}.** section=`{section}` gate=`{gate}`")
        if detail:
            lines.append(f"   - detail: {detail}")
    lines.append("")
    return lines


def _render_quality_reports(run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Quality Reports", ""]
    if not run_report:
        return []
    rows: List[Tuple[str, str]] = []
    rows.append(("Final quality score", f"{run_report.get('final_quality_score', '—')}"))
    rows.append(("Status", str(run_report.get("status", "—"))))
    rows.append(("ATS valid", _yes_no(run_report.get("ats_valid"))))
    rows.append(("Retry iterations", str(run_report.get("retry_iterations", "—"))))

    overfit = run_report.get("overfit_report") or {}
    rows.append((
        "Overfit detector",
        f"score={overfit.get('score', '—')} escalate={_yes_no(overfit.get('escalate'))} flags={len(overfit.get('flags', []))}",
    ))
    prov = run_report.get("provenance_report") or {}
    rows.append((
        "Provenance",
        f"valid={_yes_no(prov.get('valid'))} reason=`{prov.get('reason', '—')}`",
    ))
    coverage = (run_report.get("narrative", {}) or {}).get("jd_keyword_coverage") or {}
    if coverage:
        cr = coverage.get("coverage_result") or {}
        rows.append((
            "JD keyword coverage",
            f"coverage={cr.get('coverage', '—')} missing={cr.get('missing', [])}",
        ))
    else:
        rows.append(("JD keyword coverage", "_not run / null_"))

    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k, v in rows:
        lines.append(f"| **{k}** | {v} |")
    lines.append("")
    return lines


def _render_l7_certification(l7: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## L7 Route Family Certification", ""]
    if not l7:
        lines.append("_agentic_core_l7_route_family_coverage.json not found._")
        lines.append("")
        return lines
    payload = l7.get("payload") if isinstance(l7.get("payload"), dict) else l7
    summary = payload.get("summary") or {}
    lines.append(
        f"Certified: **{summary.get('certified', 0)} / {summary.get('total_families', 0)}** · "
        f"fixture-only: {summary.get('fixture_only', 0)} · "
        f"not certified: {summary.get('not_certified', 0)}"
    )
    lines.append("")
    families = payload.get("route_families") or []
    if families:
        lines.append("| Family | Status | Proof class | Exercised |")
        lines.append("|---|---|---|---|")
        for f in families:
            fam = f.get("route_family", "?")
            stat = f.get("certification_status", "—")
            proof = f.get("proof_class", "—")
            exer = _yes_no(f.get("exercised_in_current_run"))
            icon = {"CERTIFIED": "✅", "NOT_CERTIFIED": "❌"}.get(stat, "•")
            lines.append(f"| `{fam}` | {icon} {stat} | `{proof}` | {exer} |")
        lines.append("")
    return lines


def _render_post_x3_completion(run_dir: Path) -> List[str]:
    receipt = _load_json(run_dir / "apps_rg_post_x3_completion_receipt.json")
    if not receipt:
        return [
            "## Post-X3 Completion",
            "",
            "_apps_rg_post_x3_completion_receipt.json not found._",
            "",
        ]
    apps_eval = receipt.get("apps_eval") if isinstance(receipt.get("apps_eval"), dict) else {}
    uwg = receipt.get("uwg") if isinstance(receipt.get("uwg"), dict) else {}
    l6 = receipt.get("l6_shadow") if isinstance(receipt.get("l6_shadow"), dict) else {}
    coverage = apps_eval.get("coverage_summary") if isinstance(apps_eval.get("coverage_summary"), dict) else {}
    rows: List[Tuple[str, str]] = [
        ("Status", str(receipt.get("status") or "—")),
        ("Completed", _yes_no(receipt.get("completed"))),
        ("UWG validation", str(uwg.get("uwg_validation_status") or "—")),
        ("UWG commit", str(uwg.get("commit_status") or "—")),
        ("UWG receipt", str(uwg.get("uwg_commit_receipt_id") or "—")),
        ("apps_eval verdict", str(apps_eval.get("verdict") or "—")),
        (
            "apps_eval coverage",
            (
                f"{coverage.get('passed_required', 0)} / "
                f"{coverage.get('required_microsteps', 0)} passed; "
                f"missing={coverage.get('missing_required_artifacts', 0)}, "
                f"unknown={coverage.get('unknown_required', 0)}, "
                f"blocked={_yes_no(coverage.get('release_blocked'))}"
            ),
        ),
        ("L6 bridge", str(l6.get("l6_shadow_bridge_ref") or "—")),
    ]
    fact_vectors = receipt.get("fact_vector_writeback")
    if isinstance(fact_vectors, dict):
        rows.append(
            (
                "Fact-vector write-back",
                (
                    f"{fact_vectors.get('status') or '—'}; "
                    f"{fact_vectors.get('reason') or '—'}; "
                    f"promotions={len(fact_vectors.get('promotions') or [])}"
                ),
            )
        )
    lines: List[str] = ["## Post-X3 Completion", ""]
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for key, value in rows:
        lines.append(f"| **{key}** | `{value}` |")
    lines.append("")
    return lines


def _render_artifacts(run_dir: Path, run_report: Optional[Dict[str, Any]]) -> List[str]:
    lines: List[str] = ["## Output Artifacts", ""]
    output_manifest = _load_json(run_dir / "apps_rg_output_manifest.json") or {}
    json_rel = _safe_manifest_rel(
        output_manifest.get("generated_resume_json_relpath"),
        "outputs/generated_resume.json",
    )
    json_resume = _first_existing_path(
        run_dir,
        [
            json_rel,
            Path(FINAL_RESUME_ASSEMBLY_JSON_RELPATH),
            Path("outputs/generated_resume.json"),
            Path("generated_resume.json"),
            Path("modular_r4/outputs/final_resume.json"),
        ],
    )
    json_required = True

    docx = _first_existing_path(
        run_dir,
        [
            Path(FINAL_RESUME_DOCX_RELPATH),
            Path("Amit_Ayer_Resume.docx"),
        ],
    )
    if "docx_output_required" in output_manifest:
        docx_required = bool(output_manifest.get("docx_output_required"))
    else:
        docx_required = _bundle_role_required(run_dir, "product_resume_docx_outputs") or _bundle_role_required(
            run_dir,
            "product_resume_docx_branded",
        )
    if (run_dir / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).is_file():
        docx_required = True
    run_report_path = run_dir / "run_report.json"
    run_report_required = _bundle_role_required(run_dir, "narrative_run_report", default=False)
    section_status = run_dir / FULL_RUN_SECTION_STATUS_JSON
    final_assembly = run_dir / "modular_r4" / "final_resume_assembly" / "final_resume_manifest.json"
    final_assembly_required = (run_dir / "modular_r4").is_dir() or bool(output_manifest)
    review_bundle = run_dir / REVIEW_BUNDLE_FILENAME
    rows: List[Tuple[str, str, str]] = []
    artifact_rows: List[Tuple[str, Path, bool, str]] = [
        ("Resume JSON", json_resume, json_required, ""),
        ("Final resume text", run_dir / FINAL_RESUME_OUTPUT_TXT, (run_dir / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).is_file(), ""),
        ("Final resume output contract", run_dir / FINAL_RESUME_OUTPUT_JSON, (run_dir / FINAL_RESUME_ASSEMBLY_JSON_RELPATH).is_file(), ""),
        ("Resume DOCX", docx, docx_required, "final resume not assembled for this run"),
        ("Run manifest", run_dir / "r4_run_manifest.json", True, ""),
        (
            "Run report",
            run_report_path,
            run_report_required,
            f"modular R4 uses {FULL_RUN_SECTION_STATUS_JSON}",
        ),
        ("Section status", section_status, False, "legacy narrative report replacement"),
        ("Final assembly manifest", final_assembly, final_assembly_required, ""),
        ("Review bundle", review_bundle, False, "operator review package"),
        ("How-trace", run_dir / "agentic_core_how_trace.json", True, ""),
        ("L7 coverage", run_dir / "agentic_core_l7_route_family_coverage.json", True, ""),
        ("Spine proof", run_dir / "agentic_core_spine_proof.json", False, "supplemental spine proof"),
    ]
    for label, path, required, optional_reason in artifact_rows:
        rows.append(
            (
                label,
                _repo_rel(path),
                _artifact_status(path, required=required, optional_reason=optional_reason),
            )
        )
    lines.append("| Artifact | Path | Status |")
    lines.append("|---|---|---|")
    for label, path, stat in rows:
        lines.append(f"| **{label}** | `{path}` | {stat} |")
    lines.append("")

    # Surface key narrative anchors when available.
    if run_report:
        company = (run_report.get("narrative", {}) or {}).get("company_brief_provenance", {}).get("company")
        if company:
            lines.append(f"Company: **{company}**")
            lines.append("")
    return lines


# ------------------------------------------------------------------- main


def render(run_dir: Path) -> str:
    """Render the full markdown summary for ``run_dir``."""
    run_report = _load_json(run_dir / "run_report.json")
    manifest = _load_json(run_dir / "r4_run_manifest.json")
    identity = _load_json(run_dir / "runtime_identity_envelope.json")
    terminal = _load_json(run_dir / "terminal_ret_packet.json")
    l7 = _load_json(run_dir / "agentic_core_l7_route_family_coverage.json")

    title = f"# apps_rg Run Summary — `{run_dir.name}`"
    rendered_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts: List[str] = [title, "", f"_Rendered at {rendered_at}_", ""]
    parts += _render_identity(run_dir, identity, manifest)
    parts += _render_fact_vector_readiness_gates(run_dir)
    parts += _render_whole_run_cache_preflight(run_dir)
    parts += _render_mandatory_run_outputs(run_dir)
    parts += _render_bcg_competencies_report(run_dir)
    parts += _render_bcg_unify_bullets_report(run_dir)
    parts += _render_l2_substages(terminal)
    parts += _render_hop_checkpoints(run_report, run_dir)
    parts += _render_section_verdicts(run_report, run_dir)
    parts += _render_modular_section_status(run_dir)
    parts += _render_gate_failures(run_report)
    parts += _render_quality_reports(run_report)
    parts += _render_post_x3_completion(run_dir)
    parts += _render_l7_certification(l7)
    parts += _render_artifacts(run_dir, run_report)
    return "\n".join(parts).rstrip() + "\n"


def main(argv: List[str]) -> int:
    if len(argv) > 1 and argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0
    if len(argv) > 1:
        run_dir = Path(argv[1]).resolve()
    else:
        latest = _latest_run_dir()
        if latest is None:
            print(
                f"No run directories found under {RUNS_ROOT}. "
                "Run `python -m apps_rg ...` first.",
                file=sys.stderr,
            )
            return 2
        run_dir = latest
    if not run_dir.is_dir():
        print(f"Run dir not found: {run_dir}", file=sys.stderr)
        return 2
    sys.stdout.write(render(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
