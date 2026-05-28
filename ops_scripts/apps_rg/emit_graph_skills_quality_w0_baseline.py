#!/usr/bin/env python3
"""Emit W0 baseline + receipt for graph-skills-quality-enhancement-c4e8a1."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.proof.x3_disposition_normalize import normalize_x3_disposition

REPORTS = REPO / "docs" / "reports" / "apps_rg"
BASELINE_JSON = REPORTS / "graph_skills_quality_enhancement_w0_baseline.json"
RECEIPT_JSON = REPORTS / "graph_skills_quality_w0_receipt.json"
PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"

BROWN_FIXTURES = (
    {
        "fixture_id": "brown_jd",
        "path": "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt",
        "sha256": "23b16bd0ae15188a4de4d533209e34ccff8fae6d12c96894a2dd90cc53bb4dfd",
        "briefing_role": "jd",
    },
    {
        "fixture_id": "brown_briefing",
        "path": "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
        "sha256": "9d0b63db755cce713bce35aa7c9089453a0e2ffb5060a3ed7bef8da483843e5d",
        "briefing_role": "all_lanes",
    },
)

LANES = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)

P2_CLOSEOUT = REPORTS / "graph_skills_hardening_p2_accelerated_closeout.json"
PROOFS_ROOT = REPO / "artifacts" / "apps_rg" / "runtime_proofs"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _verify_brown_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in BROWN_FIXTURES:
        p = REPO / spec["path"]
        on_disk = p.is_file()
        digest = _sha256_file(p) if on_disk else None
        plan_sha = spec["sha256"]
        drift = digest != plan_sha if digest else True
        rows.append(
            {
                **spec,
                "exists_on_disk": on_disk,
                "sha256_plan_doc": plan_sha,
                "sha256_pinned_w0": digest,
                "sha256_verified_against_plan_doc": digest == plan_sha if digest else False,
                "fixture_pin_drift": drift,
            }
        )
    return rows


def _latest_real_run(lane: str) -> Path | None:
    real_dir = PROOFS_ROOT / lane / "real"
    if not real_dir.is_dir():
        return None
    runs = [p for p in real_dir.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def _classify_run_dir(run_dir: Path) -> str:
    rel = str(run_dir).replace("\\", "/")
    if "/contract_harness/" in rel or "/fixture/" in rel:
        return "CONTRACT_TEST_PROOF"
    if "/dry_run/" in rel or "/dry-run/" in rel:
        return "DETERMINISTIC_RUNTIME_PROOF"
    if "/real/" in rel:
        prov = run_dir / "provider_response.json"
        if prov.is_file():
            try:
                pr = json.loads(prov.read_text(encoding="utf-8"))
                model = str(pr.get("model") or pr.get("provider") or "").lower()
                if "mock" in model or pr.get("dry_run"):
                    return "DETERMINISTIC_RUNTIME_PROOF"
            except json.JSONDecodeError:
                pass
        return "REAL_LLM_RUNTIME_PROOF"
    return "UNKNOWN"


def _lane_x3_sample(lane: str) -> dict[str, Any]:
    run_dir = _latest_real_run(lane)
    if run_dir is None:
        return {
            "lane": lane,
            "latest_run_dir": None,
            "proof_class": None,
            "x3_code_raw": None,
            "x3_normalized": "UNKNOWN",
            "x3_pass": False,
            "live_x3_allow_claimed": False,
            "note": "no_real_run_dir",
        }
    x3_path = run_dir / "x3_disposition.json"
    proof_class = _classify_run_dir(run_dir)
    rel_run = run_dir.relative_to(REPO).as_posix()
    if not x3_path.is_file():
        return {
            "lane": lane,
            "latest_run_dir": rel_run,
            "proof_class": proof_class,
            "x3_code_raw": None,
            "x3_normalized": "UNKNOWN",
            "x3_pass": False,
            "live_x3_allow_claimed": False,
            "note": "missing_x3_disposition.json",
        }
    payload = json.loads(x3_path.read_text(encoding="utf-8"))
    norm = normalize_x3_disposition(payload)
    return {
        "lane": lane,
        "latest_run_dir": rel_run,
        "proof_class": proof_class,
        **norm,
        "note": None,
    }


def _inventory_evidence() -> dict[str, Any]:
    real_run_count = 0
    contract_run_count = 0
    by_class: dict[str, int] = {
        "CONTRACT_TEST_PROOF": 0,
        "DETERMINISTIC_RUNTIME_PROOF": 0,
        "REAL_LLM_RUNTIME_PROOF": 0,
        "LIVE_X3_ALLOW_PROOF": 0,
        "CI_RATCHET_PROOF": 0,
    }
    for lane in LANES:
        run_dir = _latest_real_run(lane)
        if not run_dir:
            continue
        real_run_count += 1
        cls = _classify_run_dir(run_dir)
        if cls in by_class:
            by_class[cls] += 1
        sample = _lane_x3_sample(lane)
        if sample.get("live_x3_allow_claimed") and cls == "REAL_LLM_RUNTIME_PROOF":
            by_class["LIVE_X3_ALLOW_PROOF"] += 1

    harness = PROOFS_ROOT / "contract_harness"
    if harness.is_dir():
        contract_run_count = sum(1 for p in harness.iterdir() if p.is_dir())
        by_class["CONTRACT_TEST_PROOF"] += contract_run_count

    p2_claims_live = False
    p2_live_sections: list[str] = []
    if P2_CLOSEOUT.is_file():
        p2 = json.loads(P2_CLOSEOUT.read_text(encoding="utf-8"))
        live = p2.get("live_proof_summary") or {}
        for sid, row in (live.get("sections") or {}).items():
            if row.get("live_x3_allow_claimed"):
                p2_live_sections.append(sid)
        p2_claims_live = len(p2_live_sections) > 0

    return {
        "real_lane_runs_with_latest_dir": real_run_count,
        "contract_harness_dirs": contract_run_count,
        "proof_class_lane_latest_counts": by_class,
        "p2_closeout_ref": P2_CLOSEOUT.relative_to(REPO).as_posix(),
        "p2_closeout_status": json.loads(P2_CLOSEOUT.read_text(encoding="utf-8")).get("status")
        if P2_CLOSEOUT.is_file()
        else None,
        "p2_live_x3_sections_claimed": p2_live_sections,
        "p2_live_x3_used_for_d6": False,
        "note": "W0 does not inherit LIVE_X3_ALLOW from P2 closeout; per-lane REAL_LLM artifacts required in W10.",
    }


def emit_baseline() -> dict[str, Any]:
    brown = _verify_brown_fixtures()
    x3_samples = [_lane_x3_sample(lane) for lane in LANES]
    inventory = _inventory_evidence()
    normalization_dry_run = [
        {
            "input": row["x3_code_raw"],
            "x3_normalized": row["x3_normalized"],
            "live_x3_allow_claimed": row["live_x3_allow_claimed"],
            "lane": row["lane"],
        }
        for row in x3_samples
    ]
    lane_registry_discrepancy = {
        "file": "apps_rg/runtime/rigor/lane_registry.py",
        "registry_briefing": "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
        "on_disk_ssot_briefing": "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
        "registry_md_exists": (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").is_file(),
        "remediation_wave": "W9",
    }
    live_count = sum(1 for r in x3_samples if r.get("live_x3_allow_claimed"))
    pin_drift = [r["fixture_id"] for r in brown if r.get("fixture_pin_drift")]
    all_exist = all(r["exists_on_disk"] for r in brown)
    return {
        "schema": "graph_skills_quality_enhancement_w0_baseline_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W0",
        "status": "PASS" if all_exist else "PARTIAL",
        "brown_fixture_pins": brown,
        "brown_all_fixtures_exist": all_exist,
        "brown_fixture_pin_drift_ids": pin_drift,
        "brown_w10_must_use_sha256_pinned_w0": True,
        "x3_code_samples_latest_real_runs": x3_samples,
        "x3_normalization_dry_run": normalization_dry_run,
        "live_x3_allow_lane_count": live_count,
        "live_x3_7_of_7": live_count == 7,
        "claims_live_x3_from_w0": False,
        "evidence_inventory": inventory,
        "lane_registry_briefing_discrepancy": lane_registry_discrepancy,
        "gaps_for_downstream_waves": [
            "graph_skills_quality_w1+ artifacts not emitted",
            "test_graph_skills_authority_separation.py missing (W4)",
            "graph-skills-authority-ratchet.yml missing (W7)",
            "x3_disposition_normalize.py stub present; wire into W10 closeout emitter",
            f"LIVE_X3 lanes at W0: {live_count}/7 (headline only if latest runs unchanged)",
        ],
    }


def emit_receipt(baseline: dict[str, Any], exit_code: int) -> dict[str, Any]:
    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w0_baseline.py"]
    return {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W0",
        "proof_class": "DETERMINISTIC_RUNTIME_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {},
        "exit_code": exit_code,
        "artifact_paths": [
            BASELINE_JSON.relative_to(REPO).as_posix(),
            RECEIPT_JSON.relative_to(REPO).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W0", "status": "PASS" if exit_code == 0 else "FAIL"},
        "notes": "W0 baseline inventory; no LIVE_X3 closeout claim.",
        "baseline_status": baseline.get("status"),
    }


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    baseline = emit_baseline()
    BASELINE_JSON.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    code = 0 if baseline.get("brown_all_fixtures_exist") else 2
    receipt = emit_receipt(baseline, code)
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": code == 0, "baseline": str(BASELINE_JSON), "receipt": str(RECEIPT_JSON)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
