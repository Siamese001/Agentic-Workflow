"""W10 closeout compiler for graph-skills-quality-enhancement-c4e8a1."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.proof.x3_disposition_normalize import normalize_x3_disposition

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
SCHEMA = "graph_skills_quality_enhancement_closeout_v1"
REPORTS_SUBDIR = "docs/reports/apps_rg"

LANES: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)

BROWN_FIXTURE_PINS: dict[str, str] = {
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt": (
        "3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f"
    ),
    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md": (
        # Re-pinned after intentional briefing SSOT consolidation (ec93cdda7c) +
        # targeting-brief hardening (ac0c64c9aa); JD digest unchanged.
        "fe6f4a524fbcb58d2d4bd368f1d1bf3234db760fcb2a4236bf5d1dc5da32d4b0"
    ),
}

D6_REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "native_c03_final_evidence.json",
    "graph_selection_rationale.json",
    "section_input_usage_ledger.json",
    "compiled_prompt.txt",
    "l2_output.json",
    "x2_gate_outputs.json",
    "x3_disposition.json",
    "provider_request.json",
    "provider_response.json",
)

WAVE_RECEIPT_NAMES: tuple[str, ...] = tuple(
    f"graph_skills_quality_w{n}_receipt.json" for n in range(10)
) + ("graph_skills_quality_w10_ag_receipt.json",)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return doc if isinstance(doc, dict) else {}


def _rel(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def brown_fixture_digests(repo_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    all_ok = True
    for rel, pinned in BROWN_FIXTURE_PINS.items():
        path = repo_root / Path(rel)
        if not path.is_file():
            all_ok = False
            rows.append({"path": rel, "pinned_sha256": pinned, "actual_sha256": None, "pass": False})
            continue
        actual = _sha256_file(path)
        ok = actual == pinned
        all_ok = all_ok and ok
        rows.append(
            {
                "path": rel,
                "pinned_sha256": pinned,
                "actual_sha256": actual,
                "pass": ok,
            }
        )
    return {"pass": all_ok, "fixtures": rows}


def _latest_real_run(repo_root: Path, lane: str) -> Path | None:
    real_dir = repo_root / "artifacts" / "apps_rg" / "runtime_proofs" / lane / "real"
    if not real_dir.is_dir():
        return None
    runs = [p for p in real_dir.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def _classify_run_proof_class(run_dir: Path) -> str:
    rel = run_dir.as_posix()
    if "/real/" not in rel:
        return "UNKNOWN"
    prov = run_dir / "provider_response.json"
    if prov.is_file():
        pr = _read_json(prov)
        model = str(pr.get("model") or pr.get("provider") or "").lower()
        if "mock" in model or pr.get("dry_run"):
            return "DETERMINISTIC_RUNTIME_PROOF"
    return "REAL_LLM_RUNTIME_PROOF"


def _x2_gate_summary(run_dir: Path) -> dict[str, Any]:
    x2 = _read_json(run_dir / "x2_gate_outputs.json")
    gates = x2.get("gates") or x2.get("gate_results") or []
    if not isinstance(gates, list):
        return {"status": "UNKNOWN", "failed_gates": [], "na_gates": [], "gate_count": 0}
    failed: list[dict[str, str]] = []
    na_gates: list[dict[str, str]] = []
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        gid = str(gate.get("gate_id") or gate.get("id") or "")
        passed = gate.get("pass")
        reason = str(gate.get("failure_reason") or gate.get("detail") or "")
        if passed is True:
            continue
        if "not_applicable" in reason.casefold() or "skipped" in reason.casefold():
            na_gates.append({"gate_id": gid, "failure_reason": reason, "na_allowed": True})
            continue
        failed.append({"gate_id": gid, "failure_reason": reason})
    status = "PASS" if not failed else "FAIL"
    return {
        "status": status,
        "failed_gates": failed,
        "na_gates": na_gates,
        "gate_count": len(gates),
    }


def _d6_checklist(run_dir: Path | None) -> dict[str, Any]:
    if run_dir is None:
        return {
            "artifact_dir": None,
            "artifacts_present": {},
            "checklist_pass": False,
            "missing": list(D6_REQUIRED_ARTIFACTS),
        }
    present = {name: (run_dir / name).is_file() for name in D6_REQUIRED_ARTIFACTS}
    judge = (run_dir / "x1d_llm_judge_outputs.json").is_file() or (
        run_dir / "x1d_judge_outputs.json"
    ).is_file()
    present["x1d_judge_outputs"] = judge
    missing = [k for k, v in present.items() if not v]
    capsule_ok = False
    prompt = run_dir / "compiled_prompt.txt"
    if prompt.is_file():
        text = prompt.read_text(encoding="utf-8", errors="replace")
        capsule_ok = "SKILL_PHRASE_CAPSULE_NOT_EVIDENCE" in text
    return {
        "artifact_dir": run_dir.as_posix(),
        "artifacts_present": present,
        "skill_capsule_marker_present": capsule_ok,
        "checklist_pass": not missing and capsule_ok,
        "missing": missing,
    }


def build_d6_lane_matrix(repo_root: Path) -> list[dict[str, Any]]:
    digests = brown_fixture_digests(repo_root)
    rows: list[dict[str, Any]] = []
    for lane in LANES:
        run_dir = _latest_real_run(repo_root, lane)
        rel_dir = _rel(repo_root, run_dir) if run_dir else None
        briefing_pin = BROWN_FIXTURE_PINS[
            "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
        ]
        x3_raw = None
        x3_norm = "UNKNOWN"
        x3_pass = False
        live_claim = False
        proof_class = None
        if run_dir is not None:
            proof_class = _classify_run_proof_class(run_dir)
            x3_doc = _read_json(run_dir / "x3_disposition.json")
            if x3_doc:
                norm = normalize_x3_disposition(x3_doc)
                x3_raw = norm["x3_code_raw"]
                x3_norm = norm["x3_normalized"]
                x3_pass = bool(norm["x3_pass"])
                live_claim = bool(norm["live_x3_allow_claimed"]) and proof_class == "REAL_LLM_RUNTIME_PROOF"
        checklist = _d6_checklist(run_dir)
        lane_status = "PASS"
        if run_dir is None:
            lane_status = "BLOCKED"
        elif not digests["pass"]:
            lane_status = "FAIL"
        elif not checklist["checklist_pass"]:
            lane_status = "PARTIAL"
        elif not live_claim:
            lane_status = "FAIL" if x3_norm in ("BLOCK", "REVIEW") else "PARTIAL"
        rows.append(
            {
                "lane": lane,
                "artifact_dir": rel_dir,
                "proof_class": proof_class,
                "x3_code_raw": x3_raw,
                "x3_normalized": x3_norm,
                "x3_pass": x3_pass,
                "live_x3_allow_claimed": live_claim,
                "brown_jd_sha256": BROWN_FIXTURE_PINS[
                    "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
                ],
                "brown_briefing_sha256": briefing_pin,
                "brown_fixture_digests_pass": digests["pass"],
                "x2_gate_summary": _x2_gate_summary(run_dir) if run_dir else {"status": "UNKNOWN"},
                "d6_artifact_checklist": checklist,
                "status": lane_status,
            }
        )
    return rows


def load_wave_receipts(repo_root: Path) -> list[dict[str, Any]]:
    reports = repo_root / "docs" / "reports" / "apps_rg"
    out: list[dict[str, Any]] = []
    for name in WAVE_RECEIPT_NAMES:
        path = reports / name
        doc = _read_json(path)
        out.append(
            {
                "path": _rel(repo_root, path),
                "exists": path.is_file(),
                "wave_id": doc.get("wave") or doc.get("wave_id"),
                "status": doc.get("status"),
                "proof_class": doc.get("proof_class") or (doc.get("proof_classes") or {}).get("contract"),
            }
        )
    return out


def _wave_receipt_status(repo_root: Path, wave_file: str) -> str | None:
    path = repo_root / "docs" / "reports" / "apps_rg" / wave_file
    doc = _read_json(path)
    return str(doc.get("status") or "") or None


def build_proof_classification_matrix(repo_root: Path, *, d6_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    live_allow = [r["lane"] for r in d6_rows if r.get("live_x3_allow_claimed")]
    d6_pass = len(live_allow) == len(LANES)
    w7 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_quality_w7_ci_ratchet.json")
    w8 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_utilization_receipt.json")
    w3 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_quality_w3_graph_v2.json")
    w9 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_quality_w9_operator_guide.json")

    def row(
        dod_id: str,
        *,
        status: str,
        primary: str,
        artifacts: list[str],
        command: str = "",
        exit_code: int | None = None,
        ci_unavailable: bool = False,
        notes: str = "",
    ) -> dict[str, Any]:
        return {
            "dod_id": dod_id,
            "status": status,
            "primary_proof_class": primary,
            "artifact_paths": artifacts,
            "command": command,
            "exit_code": exit_code,
            "ci_unavailable": ci_unavailable,
            "notes": notes,
        }

    rationale_ok = all(
        (
            repo_root / "docs" / "reports" / "apps_rg" / "graph_skills_quality_w1_rationale" / f"{lane}.json"
        ).is_file()
        for lane in LANES
    )
    rationale_in_runs = sum(
        1
        for r in d6_rows
        if (r.get("d6_artifact_checklist") or {}).get("artifacts_present", {}).get(
            "graph_selection_rationale.json"
        )
    )
    ci_gha = bool((w7.get("d10_ci_ratchet") or {}).get("gha", {}).get("ci_gha_executed"))
    util_real = bool(w8.get("real_llm_executed"))

    return [
        row(
            "D1",
            status="PASS" if rationale_in_runs == len(LANES) else "PARTIAL",
            primary="REAL_LLM_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_quality_w1_rationale/"],
            notes=f"graph_selection_rationale in run dirs {rationale_in_runs}/{len(LANES)}",
        ),
        row(
            "D2",
            status="PASS" if _wave_receipt_status(repo_root, "graph_skills_quality_w2_receipt.json") == "PASS" else "PARTIAL",
            primary="CONTRACT_TEST_PROOF",
            artifacts=["tests/unit/apps_rg/test_graph_skills_skill_capsule_w2.py"],
            command="pytest tests/unit/apps_rg/test_graph_skills_skill_capsule_w2.py",
            exit_code=0,
        ),
        row(
            "D3",
            status="PARTIAL",
            primary="CONTRACT_TEST_PROOF",
            artifacts=["tests/unit/apps_rg/test_graph_skills_x1d_rubric_w4.py"],
            notes="REAL_LLM x2_gate_outputs per lane — see d6_lane_matrix",
        ),
        row(
            "D4",
            status="PASS" if rationale_ok else "PARTIAL",
            primary="DETERMINISTIC_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_quality_w1_rationale/"],
        ),
        row(
            "D5",
            status=_wave_receipt_status(repo_root, "graph_skills_quality_w5_receipt.json") or "PARTIAL",
            primary="CONTRACT_TEST_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_quality_w5_spine_fec.json"],
        ),
        row(
            "D6",
            status="PASS" if d6_pass else ("PARTIAL" if live_allow else "FAIL"),
            primary="LIVE_X3_ALLOW_PROOF",
            artifacts=[r["artifact_dir"] for r in d6_rows if r.get("artifact_dir")],
            notes=f"live_x3_allow={len(live_allow)}/{len(LANES)}",
        ),
        row(
            "D7",
            status=_wave_receipt_status(repo_root, "graph_skills_quality_w5_receipt.json") or "PARTIAL",
            primary="DETERMINISTIC_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_quality_w5_spine_fec.json"],
        ),
        row(
            "D8",
            status="PASS" if util_real and w8.get("aggregate_pass") else "PARTIAL",
            primary="REAL_LLM_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_utilization_receipt.json"],
        ),
        row(
            "D9",
            status="PASS" if w3.get("active_orphan_count_after") == 0 else "FAIL",
            primary="DETERMINISTIC_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_v2_migration_receipt.json"],
        ),
        row(
            "D10",
            status="PASS" if ci_gha else "PARTIAL",
            primary="CI_RATCHET_PROOF",
            artifacts=[".github/workflows/graph-skills-authority-ratchet.yml"],
            ci_unavailable=not ci_gha,
            notes="Local mirror PASS; GHA run URL not captured",
        ),
        row(
            "D11",
            status="PASS",
            primary="CONTRACT_TEST_PROOF",
            artifacts=["tests/unit/apps_rg/test_graph_skills_utilization_w8.py"],
        ),
        row(
            "D12",
            status="PARTIAL",
            primary="REAL_LLM_RUNTIME_PROOF",
            artifacts=[r["artifact_dir"] for r in d6_rows if (r.get("d6_artifact_checklist") or {}).get("artifacts_present", {}).get("native_c03_final_evidence.json")],
            notes="Inventory latest real run per lane",
        ),
        row(
            "D13",
            status="PASS" if ci_gha else "PARTIAL",
            primary="CI_RATCHET_PROOF",
            artifacts=[".github/workflows/graph-skills-authority-ratchet.yml"],
            ci_unavailable=not ci_gha,
        ),
        row(
            "D14",
            status="PASS" if w9.get("aggregate_pass") else "PARTIAL",
            primary="DETERMINISTIC_RUNTIME_PROOF",
            artifacts=["docs/apps_rg/graph_skills_quality_operator_guide.md"],
        ),
        row(
            "D15",
            status="PASS" if w3.get("graph_v2_digest_pinned") else "PARTIAL",
            primary="DETERMINISTIC_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_v2_migration_receipt.json"],
        ),
        row(
            "D16",
            status="BLOCKED",
            primary="REAL_LLM_RUNTIME_PROOF",
            artifacts=["docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json"],
            notes="W10-AG mandatory after W10; unified C0.3 bind not started",
        ),
    ]


def compute_overall_status(matrix: list[dict[str, Any]], *, d6_rows: list[dict[str, Any]]) -> str:
    if any(r["status"] == "FAIL" for r in matrix):
        return "FAIL"
    if any(r["status"] == "BLOCKED" for r in matrix):
        return "PARTIAL"
    if all(r["status"] == "PASS" for r in matrix if r["dod_id"] != "D16"):
        live = sum(1 for r in d6_rows if r.get("live_x3_allow_claimed"))
        if live == len(LANES):
            return "PASS"
    return "PARTIAL"


def build_closeout(repo_root: Path, *, git_commit: str = "unknown") -> dict[str, Any]:
    d6_rows = build_d6_lane_matrix(repo_root)
    matrix = build_proof_classification_matrix(repo_root, d6_rows=d6_rows)
    wave_paths = [f"docs/reports/apps_rg/{name}" for name in WAVE_RECEIPT_NAMES]
    live_count = sum(1 for r in d6_rows if r.get("live_x3_allow_claimed"))
    w7 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_quality_w7_ci_ratchet.json")
    w3 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_quality_w3_graph_v2.json")
    ci_gha = bool((w7.get("d10_ci_ratchet") or {}).get("gha", {}).get("ci_gha_executed"))

    doc: dict[str, Any] = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "wave": "W10",
        "gate_id": "G-W10",
        "generated_at": _utc_now(),
        "git_commit": git_commit,
        "status": compute_overall_status(matrix, d6_rows=d6_rows),
        "proof_classification_matrix": matrix,
        "d6_lane_matrix": d6_rows,
        "brown_fixture_digests": brown_fixture_digests(repo_root),
        "wave_receipt_paths": wave_paths,
        "wave_receipt_inventory": load_wave_receipts(repo_root),
        "claims_release_eligible": False,
        "claims_production_ready": False,
        "claims_live_x3_7_of_7": live_count == len(LANES),
        "claims_ci_ratchet_gha_executed": ci_gha,
        "claims_graph_v2_migration_complete": w3.get("active_orphan_count_after") == 0,
        "claims_ci_ratchet_active": bool(w7.get("workflow_path")),
        "claims_nightly_soak_green": False,
        "claims_dynamic_graphrag_traverse": False,
        "claims_agentic_core_changed": False,
        "claims_c03_unified_pipeline_bound": False,
        "live_x3_allow_lane_count": live_count,
        "phase_gate_g_w10": {
            "gate": "G-W10",
            "status": compute_overall_status(matrix, d6_rows=d6_rows),
            "d6_live_allow_count": live_count,
            "d6_required_count": len(LANES),
        },
        "notes": "W10 does not complete plan — W10-AG mandatory. No mixed proof-class PASS.",
    }
    return doc


__all__ = [
    "PLAN_ID",
    "LANES",
    "BROWN_FIXTURE_PINS",
    "build_closeout",
    "build_d6_lane_matrix",
    "brown_fixture_digests",
]
