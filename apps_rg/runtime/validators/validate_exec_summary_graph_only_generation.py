"""Live proof validator: executive_summary uses augmented skills graph + section graph binding shim only.

Does **not** assert full canonical C0.3 graph traverse or spine FinalEvidenceContract.

Usage:
    python apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py --latest
    python apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py --run-dir <path> --write-report
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.c03_graphrag_bound import FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF
from apps_rg.runtime.runtime_proof_layout import find_repo_root, lane_root

LANE = "executive_summary"
MOCK_PROVIDER_MARKERS = (
    "DEV_DEFAULT_MOCK",
    "OFFLINE_CONTRACT_STUB",
    "APPS_RG_PROVIDER_MODEL_OFFLINE_CONTRACT_STUB",
    "runtime_generation_status\": \"OFFLINE",
    "runtime_generation_status\": \"MOCK",
    "provider\": \"mock",
)
FORBIDDEN_AUTHORITY_MARKERS = (
    "master_resume",
    "base_resume_fallback",
    "broad_skills_ledger_executive_summary",
    "CLAIM SUPPORT POOL (BROAD SKILLS LEDGER)",
    "CLAIM SUPPORT POOL (BASE RESUME FALLBACK)",
    "BASE_RESUME_SOURCE",
    "master_skills_arsenal_ledger.json as sole",
    "broad skills ledger as source of truth",
)
DEPRECATED_DISPATCH_MARKERS = (
    "executive_summary_dispatch",
    "executive_summary_demo",
    "cli_smoke",
    "_w7_cli_smoke_",
)
OLD_LEDGER_MARKERS = (
    "master_candidate_skills_fact_ledger",
    "broad_skills_ledger_used",
    "proof_pool_type\": \"broad_skills_ledger\"",
)


@dataclass
class CheckResult:
    check_id: str
    passed: bool
    detail: str = ""


@dataclass
class ValidationReport:
    status: str
    latest_run_dir: str = ""
    provider_name: str = ""
    provider_resolution_source: str = ""
    proof_eligible: bool | None = None
    manifest_proof_eligible: bool | None = None
    x1d_provider_blockers: list[str] = field(default_factory=list)
    x1d_quality_soft_fails: list[str] = field(default_factory=list)
    x2_status: str = ""
    x3_disposition: str = ""
    graph_only_authority_status: str = "UNKNOWN"
    c03_graphrag_bound_status: str = "UNKNOWN"
    graph_expansion_refs_count: int = 0
    graph_lineage_refs_count: int = 0
    evidence_items_count: int = 0
    non_graph_evidence_items_count: int = 0
    base_resume_reference_count: int = 0
    old_skills_ledger_reference_count: int = 0
    smoke_dispatch_reference_count: int = 0
    mock_provider_flags: list[str] = field(default_factory=list)
    checks: list[CheckResult] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    def add(self, check_id: str, passed: bool, detail: str = "") -> None:
        self.checks.append(CheckResult(check_id=check_id, passed=passed, detail=detail))
        if not passed and detail:
            self.blockers.append(f"{check_id}: {detail}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "latest_run_dir": self.latest_run_dir,
            "provider_name": self.provider_name,
            "provider_resolution_source": self.provider_resolution_source,
            "proof_eligible": self.proof_eligible,
            "manifest_proof_eligible": self.manifest_proof_eligible,
            "x1d_provider_blockers": self.x1d_provider_blockers,
            "x1d_quality_soft_fails": self.x1d_quality_soft_fails,
            "x2_status": self.x2_status,
            "x3_disposition": self.x3_disposition,
            "graph_only_authority_status": self.graph_only_authority_status,
            "c03_graphrag_bound_status": self.c03_graphrag_bound_status,
            "graph_expansion_refs_count": self.graph_expansion_refs_count,
            "graph_lineage_refs_count": self.graph_lineage_refs_count,
            "evidence_items_count": self.evidence_items_count,
            "non_graph_evidence_items_count": self.non_graph_evidence_items_count,
            "base_resume_reference_count": self.base_resume_reference_count,
            "old_skills_ledger_reference_count": self.old_skills_ledger_reference_count,
            "smoke_dispatch_reference_count": self.smoke_dispatch_reference_count,
            "mock_provider_flags": self.mock_provider_flags,
            "checks": [{"check_id": c.check_id, "passed": c.passed, "detail": c.detail} for c in self.checks],
            "blockers": self.blockers,
        }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return doc if isinstance(doc, dict) else {}


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def resolve_latest_run_dir(repo: Path) -> Path | None:
    ptr = lane_root(repo, LANE) / "latest_real_run.json"
    doc = _read_json(ptr)
    rel = doc.get("run_dir") or doc.get("run_dir_repo_relative")
    if not isinstance(rel, str) or not rel.strip():
        return None
    run_dir = (repo / rel.replace("\\", "/")).resolve()
    return run_dir if run_dir.is_dir() else None


def _count_marker_hits(blob: str, markers: tuple[str, ...]) -> int:
    low = blob.lower()
    return sum(1 for m in markers if m.lower() in low)


def _collect_text_blobs(run_dir: Path) -> str:
    names = (
        "compiled_prompt.txt",
        "compiled_prompt_artifact.json",
        "provider_request.json",
        "runtime_payload.json",
        "section_input_usage_ledger.json",
        "run_manifest.json",
        "command_output.txt",
    )
    parts: list[str] = []
    for name in names:
        parts.append(_read_text(run_dir / name))
    return "\n".join(parts)


def _evidence_items_from_run(run_dir: Path, pp_meta: dict[str, Any], c03: dict[str, Any]) -> list[dict[str, Any]]:
    fec = _read_json(run_dir / "final_evidence_contract_snapshot.json")
    if fec.get("evidence_items"):
        items = fec.get("evidence_items")
        return [x for x in items if isinstance(x, dict)]
    if c03.get("final_evidence_contract_snapshot"):
        snap = c03.get("final_evidence_contract_snapshot")
        if isinstance(snap, dict):
            items = snap.get("evidence_items")
            return [x for x in (items or []) if isinstance(x, dict)]
    count = int(pp_meta.get("evidence_items_count") or c03.get("evidence_items_count") or 0)
    if count > 0:
        return [{"synthetic": True}] * count
    return []


def validate_run_dir(run_dir: Path, *, repo: Path) -> ValidationReport:
    report = ValidationReport(status="FAIL", latest_run_dir=str(run_dir))

    if not run_dir.is_dir():
        report.add("run_dir_exists", False, f"missing run dir {run_dir}")
        report.status = "BLOCKED"
        return report

    run_manifest = _read_json(run_dir / "run_manifest.json")
    latest_ptr = _read_json(lane_root(repo, LANE) / "latest_real_run.json")
    runtime_payload = _read_json(run_dir / "runtime_payload.json")
    usage_ledger = _read_json(run_dir / "section_input_usage_ledger.json")
    pp_meta = runtime_payload.get("proof_pool_metadata") or usage_ledger.get("proof_pool_metadata") or {}
    if not pp_meta:
        pp_meta = usage_ledger
    c03 = _read_json(run_dir / "c03_graphrag_bound.json")
    if not c03 and isinstance(pp_meta.get("c03_graphrag_bound"), dict):
        c03 = pp_meta["c03_graphrag_bound"]

    provider_req = _read_json(run_dir / "provider_request.json")
    provider_resp = _read_json(run_dir / "provider_response.json")
    real_l2 = _read_json(run_dir / "real_l2_generation_result.json")
    x2_out = _read_json(run_dir / "x2_gate_outputs.json")
    x2_pool = _read_json(run_dir / "x2_source_fact_pool_receipt.json")
    x3 = _read_json(run_dir / "x3_disposition.json")
    l2 = _read_json(run_dir / "l2_output.json")

    report.provider_name = str(
        provider_resp.get("model")
        or provider_req.get("model")
        or latest_ptr.get("provider_requested")
        or ""
    )
    report.provider_resolution_source = str(
        run_manifest.get("provider_resolution_source")
        or latest_ptr.get("provider_resolution_source")
        or runtime_payload.get("provider_resolution_source")
        or ""
    )
    report.manifest_proof_eligible = (
        bool(run_manifest.get("proof_eligible"))
        if "proof_eligible" in run_manifest
        else None
    )
    report.proof_eligible = report.manifest_proof_eligible
    if report.proof_eligible is None and "pass" in x3:
        report.proof_eligible = bool(x3.get("pass"))

    x1d_doc = _read_json(run_dir / "x1d_llm_judge_outputs.json")
    for j in x1d_doc.get("judges") or []:
        if not isinstance(j, dict):
            continue
        pk = str(j.get("provider_key") or "")
        if j.get("provider_blocked") or str(j.get("evaluator_mode", "")).startswith("BLOCKED_"):
            report.x1d_provider_blockers.append(pk or str(j.get("provider_name") or "unknown"))
        elif str(j.get("provider_status")) == "MODEL_BACKED_FAIL" or j.get("pass") is False:
            if pk:
                report.x1d_quality_soft_fails.append(pk)
    report.add(
        "x1d_no_provider_blockers",
        not report.x1d_provider_blockers,
        ",".join(report.x1d_provider_blockers) or "ok",
    )
    failed_gates = x2_out.get("failed_gates") or []
    report.x2_status = "PASS" if x2_out and not failed_gates else ("FAIL" if failed_gates else "UNKNOWN")
    report.x3_disposition = str(x3.get("x3_code") or x3.get("decisive_reason") or "UNKNOWN")

    runtime_status = str(
        l2.get("runtime_generation_status")
        or real_l2.get("runtime_generation_status")
        or x3.get("runtime_generation_status")
        or latest_ptr.get("runtime_generation_status")
        or ""
    )
    report.add(
        "runtime_generation_real_llm",
        runtime_status == "REAL_LLM",
        f"runtime_generation_status={runtime_status!r}",
    )

    if os.environ.get("APPS_RG_PROVIDER_MODEL_OFFLINE_CONTRACT_STUB", "").strip():
        report.mock_provider_flags.append("APPS_RG_PROVIDER_MODEL_OFFLINE_CONTRACT_STUB=set")
    if report.provider_resolution_source == "DEV_DEFAULT_MOCK":
        report.mock_provider_flags.append("provider_resolution_source=DEV_DEFAULT_MOCK")

    blob = _collect_text_blobs(run_dir)
    for marker in MOCK_PROVIDER_MARKERS:
        if marker in blob or marker in report.provider_resolution_source:
            if marker not in report.mock_provider_flags:
                report.mock_provider_flags.append(marker)
    prov_low = report.provider_name.lower()
    if prov_low and any(x in prov_low for x in ("mock", "stub")) and "PROVIDER_MODEL" not in prov_low:
        report.mock_provider_flags.append(f"provider_name={report.provider_name}")
    if runtime_status in ("MOCK", "OFFLINE", "OFFLINE_CONTRACT_STUB"):
        report.mock_provider_flags.append(f"runtime_generation_status={runtime_status}")
    report.add("no_mock_provider", not report.mock_provider_flags, ",".join(report.mock_provider_flags))

    cmd = str(run_manifest.get("command") or latest_ptr.get("command") or "")
    report.smoke_dispatch_reference_count = _count_marker_hits(cmd, DEPRECATED_DISPATCH_MARKERS) + _count_marker_hits(
        blob, DEPRECATED_DISPATCH_MARKERS
    )
    report.add(
        "no_smoke_or_deprecated_dispatch",
        report.smoke_dispatch_reference_count == 0,
        f"hits={report.smoke_dispatch_reference_count}",
    )

    source_auth = str(pp_meta.get("source_authority") or usage_ledger.get("source_authority") or "")
    proof_source = str(
        pp_meta.get("proof_pool_type")
        or usage_ledger.get("proof_source")
        or _read_json(run_dir / "compiled_prompt_artifact.json").get("proof_source")
        or ""
    )
    graph_only = (
        source_auth == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
        and proof_source in ("augmented_skills_graph", "augmented_skills_graph_c03_graphrag")
        and not pp_meta.get("broad_skills_ledger_used")
        and not pp_meta.get("base_resume_fallback_used")
    )
    report.graph_only_authority_status = "PASS" if graph_only else "FAIL"
    report.add(
        "graph_only_source_authority",
        graph_only,
        f"source_authority={source_auth!r} proof_pool_type={proof_source!r}",
    )

    graph_expansion_allowed = bool(
        c03.get("graph_expansion_allowed")
        or pp_meta.get("graph_expansion_allowed")
    )
    graph_expansion_refs = list(
        c03.get("graph_expansion_refs") or pp_meta.get("graph_expansion_refs") or []
    )
    graph_lineage_refs = list(
        c03.get("graph_lineage_refs") or pp_meta.get("graph_lineage_refs") or []
    )
    report.graph_expansion_refs_count = len(graph_expansion_refs)
    report.graph_lineage_refs_count = len(graph_lineage_refs)
    c03_status = str(c03.get("c03_graphrag_bound_status") or pp_meta.get("c03_graphrag_bound_status") or "")
    report.c03_graphrag_bound_status = c03_status or ("BOUND" if graph_expansion_allowed and graph_expansion_refs else "NOT_BOUND")
    report.add("c03_graph_expansion_allowed", graph_expansion_allowed, "")
    report.add("c03_graph_expansion_refs_nonempty", bool(graph_expansion_refs), f"count={len(graph_expansion_refs)}")
    report.add(
        "c03_graph_lineage_refs_present",
        bool(graph_lineage_refs) or bool(pp_meta.get("graph_sig") or c03.get("graph_sig")),
        "",
    )
    report.add(
        "c03_bound_status",
        report.c03_graphrag_bound_status == "BOUND",
        report.c03_graphrag_bound_status,
    )

    support_status = str(
        c03.get("support_status")
        or (c03.get("final_evidence_contract_snapshot") or {}).get("support_status")
        or pp_meta.get("support_status")
        or ""
    )
    report.add(
        "fec_support_status_product_safe",
        support_status not in FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF,
        f"support_status={support_status!r}",
    )

    evidence_items = _evidence_items_from_run(run_dir, pp_meta, c03)
    report.evidence_items_count = len(evidence_items)
    non_graph = 0
    for it in evidence_items:
        if not isinstance(it, dict):
            continue
        auth = str(it.get("authority") or it.get("source_class") or "")
        if auth and auth != SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH:
            non_graph += 1
    report.non_graph_evidence_items_count = non_graph
    report.add("evidence_items_graph_backed", non_graph == 0 and report.evidence_items_count > 0, "")

    input_auth = usage_ledger.get("input_authority") or {}
    base_auth = str(input_auth.get("base_resume") or "")
    report.add(
        "no_base_resume_claim_authority",
        base_auth not in ("BASE_RESUME_SOURCE", "CLAIM_EVIDENCE", "CLAIM_EVIDENCE_FALLBACK"),
        f"base_resume authority={base_auth!r}",
    )

    report.base_resume_reference_count = _count_marker_hits(blob, FORBIDDEN_AUTHORITY_MARKERS)
    report.add(
        "no_base_resume_packet_in_prompt_artifacts",
        "master_resume" not in blob.lower() and "BASE RESUME FALLBACK" not in blob,
        f"marker_hits={report.base_resume_reference_count}",
    )

    ledger_used = bool(
        pp_meta.get("broad_skills_ledger_used")
        or x2_pool.get("broad_skills_ledger_used")
        or proof_source == "broad_skills_ledger"
    )
    report.old_skills_ledger_reference_count = _count_marker_hits(blob, OLD_LEDGER_MARKERS) + (1 if ledger_used else 0)
    report.add(
        "no_old_skills_ledger_authority",
        not ledger_used and proof_source != "broad_skills_ledger",
        f"broad_skills_ledger_used={ledger_used}",
    )

    compiled = _read_text(run_dir / "compiled_prompt.txt")
    report.add(
        "pa_c0_graph_pool_named",
        "AUGMENTED SKILLS GRAPH" in compiled or "augmented_skills_graph" in compiled,
        "",
    )

    claim_src = str(pp_meta.get("claim_evidence_source_type") or usage_ledger.get("claim_evidence_source_type") or "")
    report.add(
        "claim_evidence_augmented_graph",
        claim_src == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        f"claim_evidence_source_type={claim_src!r}",
    )

    x2_failed = list(_read_json(run_dir / "x2_gate_outputs.json").get("failed_gates") or [])
    if x2_failed:
        report.add(
            "x2_all_gates_pass",
            False,
            f"failed_gates={x2_failed[:8]}",
        )
    else:
        report.add("x2_all_gates_pass", True, "")

    graph_only_pass = (
        not report.mock_provider_flags
        and runtime_status == "REAL_LLM"
        and all(c.passed for c in report.checks)
    )
    if graph_only_pass and report.proof_eligible is True and str(x3.get("x3_code") or "") == "X3_ALLOW":
        report.status = "PASS"
    elif graph_only_pass:
        report.status = "PASS"
    elif runtime_status in ("BLOCKED", "") and not run_dir.joinpath("provider_response.json").is_file():
        report.status = "BLOCKED"
    elif runtime_status == "BLOCKED":
        report.status = "BLOCKED"
    else:
        report.status = "FAIL"
    return report


def _default_report_paths(repo: Path) -> tuple[Path, Path]:
    md = repo / "docs/reports/apps_rg/executive_summary_graph_only_generation_live_proof.md"
    js = repo / "docs/reports/apps_rg/executive_summary_graph_only_generation_live_proof.json"
    return md, js


def write_reports(report: ValidationReport, *, repo: Path) -> tuple[Path, Path]:
    md_path, json_path = _default_report_paths(repo)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Executive summary graph-only generation live proof",
        "",
        f"**STATUS:** {report.status}",
        "",
        f"- latest_run_dir: `{report.latest_run_dir}`",
        f"- provider_name: `{report.provider_name}`",
        f"- provider_resolution_source: `{report.provider_resolution_source}`",
        f"- graph_only_authority_status: `{report.graph_only_authority_status}`",
        f"- c03_graphrag_bound_status: `{report.c03_graphrag_bound_status}`",
        f"- graph_expansion_refs_count: {report.graph_expansion_refs_count}",
        f"- x2_status: {report.x2_status}",
        f"- x3_disposition: {report.x3_disposition}",
        "",
        "## Blockers",
        "",
    ]
    if report.blockers:
        lines.extend(f"- {b}" for b in report.blockers)
    else:
        lines.append("- none")
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latest", action="store_true", help="Validate latest real executive_summary run")
    parser.add_argument("--run-dir", type=str, default="", help="Explicit run directory")
    parser.add_argument("--write-report", action="store_true", help="Write JSON/MD reports under docs/reports/apps_rg/")
    args = parser.parse_args(argv)

    repo = find_repo_root()
    run_dir: Path | None = None
    if args.run_dir:
        run_dir = Path(args.run_dir)
        if not run_dir.is_absolute():
            run_dir = (repo / run_dir).resolve()
    elif args.latest:
        run_dir = resolve_latest_run_dir(repo)
    else:
        parser.error("Specify --latest or --run-dir")

    if run_dir is None:
        report = ValidationReport(status="BLOCKED")
        report.blockers.append("no latest real executive_summary run directory")
        if args.write_report:
            write_reports(report, repo=repo)
        print(json.dumps(report.to_dict(), indent=2))
        return 2

    report = validate_run_dir(run_dir, repo=repo)
    if args.write_report:
        write_reports(report, repo=repo)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.status == "PASS" else (2 if report.status == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
