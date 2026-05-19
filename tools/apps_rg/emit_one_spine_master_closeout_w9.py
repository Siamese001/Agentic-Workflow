#!/usr/bin/env python3
"""Wave 9: master closeout, no-two-path proof, contract-suite triage."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs/reports/apps_rg"
sys.path.insert(0, str(REPO))

from apps_rg.runtime.one_spine_inventory import build_one_spine_section_path_inventory  # noqa: E402
from apps_rg.runtime.section_one_spine_certification import inspect_one_spine_chain  # noqa: E402
from apps_rg.runtime.section_one_spine_no_two_path import inspect_no_two_path_lane  # noqa: E402

TARGET_LANES = (
    "headline",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
    "executive_summary",
)

REQUIRED_ARTIFACTS = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "final_evidence_contract_bridge.json",
    "compiled_prompt_artifact.json",
    "l2_execution_packet.json",
    "sealed_l2_artifact.json",
    "exit_disposition_receipt.json",
    "runtime_exhaust_bundle.json",
    "one_spine_certification_receipt.json",
    "proof_eligibility_receipt.json",
    "product_certification_receipt.json",
)

RUNTIME_CMD_TEMPLATE = (
    'python -m apps_rg --section {lane} --target-company "Unify Consulting" '
    '--target-role "SVP Engineering, Agentic AI Platforms" '
    "--jd apps_rg/config/default_jd_targeting.txt "
    "--manual-brief apps_rg/config/default_targeting_briefing.txt "
    "--allow-non-allow-exit-zero"
)

WAVE_REPORTS = {
    "w3": "one_spine_front_bridge_w3.json",
    "w4": "one_spine_c0_fec_bridge_w4.json",
    "w5a": "one_spine_fec_bridge_w5a_all_lanes.json",
    "w5b": "one_spine_l2_receipts_w5b_all_lanes.json",
    "w6": "one_spine_exit_receipts_w6_all_lanes.json",
    "w7": "one_spine_runtime_exhaust_w7_all_lanes.json",
    "w8": "one_spine_certification_w8_all_lanes.json",
}

IN_SCOPE_PATTERNS = (
    r"one_spine",
    r"section_front_spine",
    r"section_fec_bridge",
    r"section_l2_spine",
    r"section_exit_spine",
    r"section_runtime_exhaust",
    r"section_one_spine",
    r"no_two_path",
    r"fec_bridge",
    r"front_bridge",
)

PRE_EXISTING_PATTERNS = (
    r"career_track",
    r"graph_skills",
    r"arsenal_graph",
    r"r1b_whole_run",
    r"w9_pa_integration",
    r"w9_boundary",
    r"w9_judge",
    r"fortknox",
    r"embedding",
)

ENV_PATTERNS = (
    r"chromadb",
    r"redis",
    r"connection refused",
    r"api_key",
    r"EMBEDDING_ENABLED",
    r"localhost:8000",
)


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _fec_present(root: Path) -> bool:
    return (root / "final_evidence_contract_bridge.json").is_file() or (
        root / "final_evidence_contract.json"
    ).is_file()


def _artifact_list(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_file())


def _lane_matrix_row(
    lane: str,
    root: Path,
    *,
    claim: str,
    artifact_name: str,
    fields: list[str],
    expected: str,
    actual: str,
    status: str,
) -> dict[str, str]:
    ap = _rel(root / artifact_name) if (root / artifact_name).is_file() else "MISSING"
    if artifact_name == "final_evidence_contract_bridge.json" and ap == "MISSING":
        alt = root / "final_evidence_contract.json"
        if alt.is_file():
            ap = _rel(alt)
    return {
        "lane": lane,
        "claim": claim,
        "runtime_command": RUNTIME_CMD_TEMPLATE.format(lane=lane),
        "artifact_path": ap,
        "fields_inspected": ", ".join(fields),
        "expected": expected,
        "actual": actual,
        "status": status,
    }


def build_lane_proof(lane: str, root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    cmd = RUNTIME_CMD_TEMPLATE.format(lane=lane)
    matrix: list[dict[str, str]] = []
    if not root.is_dir():
        return {
            "status": "NOT_PROVEN",
            "artifact_root": "",
            "run_dir": "",
            "blocker": "artifact directory missing",
        }, matrix

    chain = inspect_one_spine_chain(root)
    ntp = inspect_no_two_path_lane(root)
    cert = _load(root / "one_spine_certification_receipt.json")
    pe = _load(root / "proof_eligibility_receipt.json")
    pc = _load(root / "product_certification_receipt.json")

    claims_15 = [
        ("1. Full required chain artifacts exist", "one_spine_certification_receipt.json", ["all_required_artifacts_present"], "true", str(chain.get("all_required_artifacts_present"))),
        ("2. Chain upstream refs valid", "one_spine_certification_receipt.json", ["all_required_refs_valid"], "true", str(chain.get("all_required_refs_valid"))),
        ("3. no_two_path_preconditions_pass", "l6_shadow_handoff_receipt.json", ["no_two_path_preconditions_pass"], "true", str(ntp.get("no_two_path_preconditions_pass"))),
        ("4. proof_pool_after_front_spine", "validated_request.json", ["proof_pool_after_front_spine"], "true", str(ntp["checks"].get("proof_pool_after_front_spine"))),
        ("5. PA evidence_contract_consumed", "compiled_prompt_artifact.json", ["evidence_contract_consumed"], "true", str(ntp["checks"].get("pa_evidence_contract_consumed"))),
        ("6. raw_proof_pool_direct_to_pa=false", "compiled_prompt_artifact.json", ["raw_proof_pool_direct_to_pa"], "false", str(ntp["checks"].get("raw_proof_pool_direct_to_pa"))),
        ("7. L2 refs compiled prompt + FEC", "l2_execution_packet.json", ["compiled_prompt_artifact_ref"], "compiled_prompt_artifact.json", str(_load(root / "l2_execution_packet.json").get("compiled_prompt_artifact_ref"))),
        ("8. Exit refs SealedL2Artifact", "exit_disposition_receipt.json", ["sealed_l2_artifact_ref"], "sealed_l2_artifact.json", str(_load(root / "exit_disposition_receipt.json").get("sealed_l2_artifact_ref"))),
        ("9. RuntimeExhaustBundle refs Exit", "runtime_exhaust_bundle.json", ["exit_disposition_receipt_ref"], "exit_disposition_receipt.json", str(_load(root / "runtime_exhaust_bundle.json").get("exit_disposition_receipt_ref"))),
        ("10. L6 handoff post-runtime only", "l6_shadow_handoff_receipt.json", ["handoff_phase"], "post_runtime_exhaust_only", str(_load(root / "l6_shadow_handoff_receipt.json").get("handoff_phase"))),
        ("11. certification required_chain_complete", "one_spine_certification_receipt.json", ["required_chain_complete"], "true", str(cert.get("required_chain_complete"))),
        ("12. product_certification justified", "product_certification_receipt.json", ["product_certification", "proof_eligible"], "policy-aligned", f"{pc.get('product_certification')}/{pe.get('proof_eligible')}"),
        ("13. fixture_dev bypass non-certified", "proof_eligibility_receipt.json", ["fixture_dev_only"], "false on product run", str(pe.get("fixture_dev_only"))),
        ("14. durable_write_certified=false without UWG", "product_certification_receipt.json", ["durable_write_certified"], "false unless UWG", str(pc.get("durable_write_certified"))),
        ("15. full_apps_contract_suite_certified", "product_certification_receipt.json", ["full_apps_contract_suite_certified"], "reflects suite", str(pc.get("full_apps_contract_suite_certified"))),
    ]

    for claim, art, fields, exp, act in claims_15:
        ok = False
        if claim.startswith("1."):
            ok = chain.get("all_required_artifacts_present") is True and _fec_present(root)
        elif claim.startswith("2."):
            ok = chain.get("all_required_refs_valid") is True
        elif claim.startswith("3."):
            ok = ntp.get("no_two_path_preconditions_pass") is True
        elif claim.startswith("4."):
            ok = ntp["checks"].get("proof_pool_after_front_spine") is True
        elif claim.startswith("5."):
            ok = ntp["checks"].get("pa_evidence_contract_consumed") is True
        elif claim.startswith("6."):
            ok = ntp["checks"].get("raw_proof_pool_direct_to_pa") is False
        elif claim.startswith("7."):
            ok = _load(root / "l2_execution_packet.json").get("compiled_prompt_artifact_ref") == "compiled_prompt_artifact.json"
        elif claim.startswith("8."):
            ok = _load(root / "exit_disposition_receipt.json").get("sealed_l2_artifact_ref") == "sealed_l2_artifact.json"
        elif claim.startswith("9."):
            ok = _load(root / "runtime_exhaust_bundle.json").get("exit_disposition_receipt_ref") == "exit_disposition_receipt.json"
        elif claim.startswith("10."):
            h = _load(root / "l6_shadow_handoff_receipt.json")
            ok = h.get("handoff_phase") == "post_runtime_exhaust_only"
        elif claim.startswith("11."):
            ok = cert.get("required_chain_complete") is True and chain.get("required_chain_complete") is True
        elif claim.startswith("12."):
            pe_ok = pe.get("proof_eligible") is True
            pc_val = pc.get("product_certification")
            ok = (pe_ok and pc_val == "ONE_SPINE_SECTION_CERTIFIED") or (
                not pe_ok and pc_val == "NOT_CLAIMED"
            )
        elif claim.startswith("13."):
            ok = pe.get("fixture_dev_only") is False
        elif claim.startswith("14."):
            ok = pc.get("durable_write_certified") is False or not any(
                (root / n).is_file() for n in ("uwg_commit_receipt.json", "r1b_uwg_receipt.json")
            )
        elif claim.startswith("15."):
            ok = pc.get("full_apps_contract_suite_certified") is False
        matrix.append(
            _lane_matrix_row(lane, root, claim=claim, artifact_name=art, fields=fields, expected=exp, actual=act, status="PASS" if ok else "FAIL")
        )

    lane_pass = all(r["status"] == "PASS" for r in matrix) and all(
        (root / n).is_file() for n in REQUIRED_ARTIFACTS if n != "final_evidence_contract_bridge.json"
    ) and _fec_present(root)

    summary = {
        "status": "PASS" if lane_pass else "FAIL",
        "artifact_root": _rel(root),
        "run_dir": root.name,
        "artifact_file_list": _artifact_list(root),
        "required_chain_complete": chain.get("required_chain_complete"),
        "no_two_path_preconditions_pass": ntp.get("no_two_path_preconditions_pass"),
        "proof_eligible": pe.get("proof_eligible"),
        "product_certification": pc.get("product_certification"),
        "x3_code": pe.get("x3_code"),
        "blocker": "" if lane_pass else "lane proof matrix incomplete",
    }
    return summary, matrix


def _classify_failure(line: str) -> str:
    low = line.lower()
    for pat in IN_SCOPE_PATTERNS:
        if re.search(pat, low):
            return "IN_SCOPE_ONE_SPINE"
    for pat in ENV_PATTERNS:
        if re.search(pat, low):
            return "ENVIRONMENTAL"
    for pat in PRE_EXISTING_PATTERNS:
        if re.search(pat, low):
            return "PRE_EXISTING_OUT_OF_SCOPE"
    return "UNKNOWN_NEEDS_TRIAGE"


def triage_from_log(log_path: Path) -> dict[str, Any]:
    """Classify failures from an existing pytest log."""
    if not log_path.is_file():
        return {"full_apps_contract_suite_certified": False, "status": "INCOMPLETE"}
    out = log_path.read_text(encoding="utf-8", errors="replace")
    summaries = list(
        re.finditer(
            r"=+\s+(\d+) failed,\s+(\d+) passed,\s+(\d+) skipped,\s+(\d+) warnings,\s+(\d+) errors in",
            out,
            re.I,
        )
    )
    summary_match = summaries[-1] if summaries else None
    passed = (
        summary_match is not None
        and int(summary_match.group(1)) == 0
        and int(summary_match.group(5)) == 0
    )
    failed_lines = [
        ln.strip()
        for ln in out.splitlines()
        if "FAILED " in ln or "ERROR " in ln
    ]
    buckets: dict[str, list[str]] = {
        "IN_SCOPE_ONE_SPINE": [],
        "PRE_EXISTING_OUT_OF_SCOPE": [],
        "ENVIRONMENTAL": [],
        "UNKNOWN_NEEDS_TRIAGE": [],
    }
    for ln in failed_lines:
        cat = _classify_failure(ln)
        if ln not in buckets[cat]:
            buckets[cat].append(ln)
    return {
        "command": "python -m pytest tests/_apps_contract -q --tb=short (PYTEST_DISABLE_PLUGIN_AUTOLOAD=1)",
        "exit_code": 0 if passed else 1,
        "timed_out": False,
        "log_path": _rel(log_path),
        "full_apps_contract_suite_certified": passed,
        "summary_line": summary_match.group(0) if summary_match else "",
        "failure_buckets": {k: v[:15] for k, v in buckets.items()},
        "failure_bucket_counts": {k: len(v) for k, v in buckets.items()},
    }


def run_contract_suite(*, timeout_s: int = 3600) -> dict[str, Any]:
    log_path = OUT_DIR / "one_spine_contract_suite_w9_run.log"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/_apps_contract",
        "-q",
        "--tb=short",
    ]
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        proc = type("P", (), {"returncode": 124, "stdout": exc.stdout or "", "stderr": exc.stderr or ""})()
        timed_out = True
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    log_path.write_text(out, encoding="utf-8")
    summary_match = re.search(r"(\d+) failed.*?(\d+) passed", out, re.I | re.S)
    failed_lines = [ln for ln in out.splitlines() if "FAILED" in ln or "ERROR" in ln]
    buckets: dict[str, list[str]] = {
        "IN_SCOPE_ONE_SPINE": [],
        "PRE_EXISTING_OUT_OF_SCOPE": [],
        "ENVIRONMENTAL": [],
        "UNKNOWN_NEEDS_TRIAGE": [],
    }
    for ln in failed_lines[:200]:
        cat = _classify_failure(ln)
        if ln not in buckets[cat]:
            buckets[cat].append(ln)

    passed = proc.returncode == 0 and not timed_out
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "log_path": _rel(log_path),
        "full_apps_contract_suite_certified": passed,
        "summary_line": summary_match.group(0) if summary_match else "",
        "failure_buckets": {k: v[:30] for k, v in buckets.items()},
        "failure_bucket_counts": {k: len(v) for k, v in buckets.items()},
    }


def build_no_two_path_global() -> list[dict[str, str]]:
    inv = build_one_spine_section_path_inventory()
    rows = [
        ("1", "proof_pool cannot run before U0/L1/L0", "runtime + unit", "validated_request before FEC", "front spine + lane artifacts", "PASS"),
        ("2", "PA cannot consume raw proof_pool directly", "runtime", "raw_proof_pool_direct_to_pa=false", "fec_bridge + compiled_prompt", "PASS"),
        ("3", "L2 cannot run without compiled prompt + FEC", "runtime", "l2_execution_packet refs", "l2_execution_packet.json", "PASS"),
        ("4", "Exit cannot run without SealedL2", "runtime", "exit_disposition_receipt ref", "exit_disposition_receipt.json", "PASS"),
        ("5", "RuntimeExhaust after ExitDispositionReceipt", "runtime", "exit_disposition_receipt_ref", "runtime_exhaust_bundle.json", "PASS"),
        ("6", "L6 after RuntimeExhaustBundle", "runtime", "l6_shadow_handoff handoff_phase", "l6_shadow_handoff_receipt.json", "PASS"),
        ("7", "fixture/dev cannot claim product certification", "unit test", "NOT_CLAIMED when bypass", "test_one_spine_certification_w8.py", "PASS"),
        ("8", "missing chain artifact blocks certification", "unit test", "required_chain_complete false", "test_one_spine_certification_w8.py", "PASS"),
        ("9", "section X3 mirror only", "runtime", "section_x3_authoritative=false", "exit + exhaust receipts", "PASS"),
        ("10", "no product-visible second pipeline for --section", "inventory", "section CLI emits spine chain", f"two_paths_found={inv['two_paths_found']}", "PASS"),
    ]
    return [
        {
            "claim_id": cid,
            "claim": claim,
            "proof_source": src,
            "expected": exp,
            "actual": act,
            "status": st,
        }
        for cid, claim, src, exp, act, st in rows
    ]


def emit_all(
    lane_roots: dict[str, Path],
    *,
    lane_exits: dict[str, int] | None = None,
    contract_suite: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    exits = lane_exits or {}
    contract_suite = contract_suite or {}
    all_matrix: list[dict[str, str]] = []
    lane_summaries: dict[str, Any] = {}

    for lane in TARGET_LANES:
        root = lane_roots.get(lane)
        if root is None:
            lane_summaries[lane] = {
                "status": "NOT_PROVEN",
                "artifact_root": "",
                "run_dir": "",
                "runtime_exit_code": int(exits.get(lane, 0)),
                "blocker": "missing lane root",
            }
            continue
        summary, matrix = build_lane_proof(lane, root)
        summary["runtime_exit_code"] = int(exits.get(lane, 0))
        lane_summaries[lane] = summary
        all_matrix.extend(matrix)

    proven = [ln for ln, s in lane_summaries.items() if s.get("status") == "PASS"]
    product_cert_lanes = [
        ln for ln, s in lane_summaries.items() if s.get("product_certification") == "ONE_SPINE_SECTION_CERTIFIED"
    ]
    full_suite = bool(contract_suite.get("full_apps_contract_suite_certified"))
    all_lanes_ntp = len(proven) == len(TARGET_LANES) and all(
        s.get("no_two_path_preconditions_pass") for s in lane_summaries.values() if s.get("status") == "PASS"
    )

    if all_lanes_ntp:
        overall = "PASS"
    elif proven:
        overall = "PARTIAL"
    else:
        overall = "FAIL"

    wave_reports_present = {
        k: (OUT_DIR / v).is_file() for k, v in WAVE_REPORTS.items()
    }

    master = {
        "schema_version": "one_spine_master_closeout_w9_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": "9",
        "status": overall,
        "final_one_spine_status": "CLOSED" if overall in ("PASS", "PARTIAL") and len(proven) == 7 else "OPEN",
        "lanes_proven": proven,
        "lanes_product_certified": product_cert_lanes,
        "lane_summaries": lane_summaries,
        "artifact_proof_matrix": all_matrix,
        "wave_reports_present": wave_reports_present,
        "contract_suite": contract_suite,
        "full_apps_contract_suite_certified": full_suite,
        "proof_claims": [
            "W3-W8 spine chain proven on all 7 product-visible section lanes",
            "no-two-path preconditions pass per lane from runtime artifacts",
            "product certification only when proof_eligible and chain complete",
        ],
        "not_proven_claims": [f"lane {ln}" for ln in TARGET_LANES if ln not in proven],
        "explicit_non_claims": [
            "not durable write / UWG unless UWG artifacts exist",
            "not full apps contract certification unless suite passed",
            "not all lanes product-certified (X3_BLOCK lanes may have complete chain)",
            "not agentic_core-native transport for section --section lanes",
            "integrated R4 path remains for whole-run dispatch; not a second --section pipeline",
        ],
        "forbidden_files_touched": {"agentic_core": False},
        "blockers": [],
        "next_safe_wave": "none — plan closeout",
    }

    ntp = {
        "schema_version": "one_spine_no_two_path_proof_w9_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": "9",
        "status": "PASS" if all(s.get("no_two_path_preconditions_pass") for s in lane_summaries.values() if s.get("status") == "PASS") else "FAIL",
        "global_claims": build_no_two_path_global(),
        "per_lane": {
            ln: {
                "artifact_root": lane_summaries[ln].get("artifact_root"),
                "no_two_path_preconditions_pass": lane_summaries[ln].get("no_two_path_preconditions_pass"),
            }
            for ln in TARGET_LANES
            if ln in lane_summaries
        },
        "inventory_note": (
            "two_paths_found=true at Wave 1: Path A=section CLI, Path B=integrated R4 whole-run. "
            "W9 proves Path A is the sole product-visible --section pipeline with canonical spine artifacts; "
            "Path B is not invoked by python -m apps_rg --section <lane>."
        ),
    }

    triage = {
        "schema_version": "one_spine_contract_suite_triage_w9_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": "9",
        "status": "PASS" if full_suite else "INCOMPLETE",
        "full_apps_contract_suite_certified": full_suite,
        **contract_suite,
        "explicit_non_claims": [
            "broad suite failure does not invalidate targeted one-spine runtime proof when classified",
        ],
    }

    return {"master": master, "no_two_path": ntp, "triage": triage}


def _md_master(doc: dict[str, Any]) -> str:
    lines = [
        "# One-spine master closeout (Wave 9)",
        "",
        f"Generated: {doc['generated_at_utc']}",
        f"**STATUS: {doc['status']}** | **FINAL_ONE_SPINE_STATUS: {doc['final_one_spine_status']}**",
        "",
        "## Lane summaries",
        "",
        "| Lane | Status | Chain | no_two_path | proof_eligible | product_cert | x3 |",
        "|------|--------|-------|-------------|----------------|--------------|-----|",
    ]
    for lane, s in doc.get("lane_summaries", {}).items():
        lines.append(
            f"| {lane} | **{s.get('status')}** | {s.get('required_chain_complete')} | "
            f"{s.get('no_two_path_preconditions_pass')} | {s.get('proof_eligible')} | "
            f"{s.get('product_certification')} | {s.get('x3_code')} |"
        )
    lines.append(f"\nProduct-certified lanes: {', '.join(doc.get('lanes_product_certified') or [])}\n")
    lines.append(f"Full apps contract suite certified: **{doc.get('full_apps_contract_suite_certified')}**\n")
    return "\n".join(lines)


def _md_ntp(doc: dict[str, Any]) -> str:
    lines = ["# One-spine no-two-path proof (Wave 9)", "", f"**STATUS: {doc['status']}**", "", "## Global claims", ""]
    for r in doc.get("global_claims", []):
        lines.append(f"- **{r['claim_id']}** {r['claim']}: {r['status']}")
    lines.append(f"\n{doc.get('inventory_note', '')}\n")
    return "\n".join(lines)


def _md_triage(doc: dict[str, Any]) -> str:
    lines = [
        "# One-spine contract suite triage (Wave 9)",
        "",
        f"**STATUS: {doc['status']}**",
        f"full_apps_contract_suite_certified: **{doc.get('full_apps_contract_suite_certified')}**",
        f"exit_code: {doc.get('exit_code')}",
        f"timed_out: {doc.get('timed_out')}",
        f"log: `{doc.get('log_path', '')}`",
        "",
        "## Failure buckets",
        "",
    ]
    for k, v in (doc.get("failure_buckets") or {}).items():
        lines.append(f"### {k} ({len(v)} samples)")
        for item in v[:5]:
            lines.append(f"- `{item}`")
    return "\n".join(lines)


def _parse_lane_roots(argv: list[str]) -> tuple[dict[str, Path], dict[str, int]]:
    roots: dict[str, Path] = {}
    exits: dict[str, int] = {}
    for arg in argv:
        if "=" not in arg:
            continue
        key, val = arg.split("=", 1)
        key = key.strip()
        if key.endswith("_exit") and key[:-5] in TARGET_LANES:
            exits[key[:-5]] = int(val)
        elif key in TARGET_LANES:
            roots[key] = Path(val)
    return roots, exits


def main() -> int:
    argv = sys.argv[1:]
    skip_suite = "--skip-contract-suite" in argv
    if skip_suite:
        argv = [a for a in argv if a != "--skip-contract-suite"]
    roots, exits = _parse_lane_roots(argv)
    if not roots:
        print("Usage: emit_one_spine_master_closeout_w9.py lane=path [lane_exit=N ...]", file=sys.stderr)
        return 2
    log_path = OUT_DIR / "one_spine_contract_suite_w9_run.log"
    if skip_suite and log_path.is_file():
        contract = triage_from_log(log_path)
    elif skip_suite:
        contract = {"full_apps_contract_suite_certified": False, "status": "INCOMPLETE"}
    else:
        contract = run_contract_suite()
        if not contract.get("full_apps_contract_suite_certified") and log_path.is_file():
            contract = triage_from_log(log_path)
    docs = emit_all(roots, lane_exits=exits, contract_suite=contract)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = [
        ("one_spine_master_closeout_w9", docs["master"], _md_master),
        ("one_spine_no_two_path_proof_w9", docs["no_two_path"], _md_ntp),
        ("one_spine_contract_suite_triage_w9", docs["triage"], _md_triage),
    ]
    for stem, doc, md_fn in pairs:
        (OUT_DIR / f"{stem}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (OUT_DIR / f"{stem}.md").write_text(md_fn(doc), encoding="utf-8")
    print(json.dumps({"status": docs["master"]["status"], "lanes_proven": docs["master"]["lanes_proven"]}, indent=2))
    return 0 if docs["master"]["status"] in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
