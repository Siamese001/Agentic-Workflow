"""W3 live integrated spine proof — inventory plan agent-inventory-spine-taxonomy-b4e9f2.

Runs ``run_integrated_single_action_spine`` with production recipe resolution
(``_test_mode=False``, no ``l2_callable`` injection). Does NOT backfill mock
``_spine_proof_run/`` artifacts. Does NOT set taxonomy ``ARTIFACT_PROVEN`` for
``*Agent`` classes (A1 remains function/stage truth per ADR-088).

Emits:
  artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "artifacts" / "reports" / "agent_inventory" / "_w3_live_spine_proof_run"
AGENT_RE = re.compile(r"\b[A-Z][a-zA-Z]+Agent(?:Simple)?\b")


def _repo_on_path() -> None:
    root = str(REPO)
    if root not in sys.path:
        sys.path.insert(0, root)


def _vllm_reachable() -> tuple[bool, str]:
    from apps_rg.runtime.providers.competencies_live_provider_gate import (
        qwen_vllm_http_models_preflight,
    )

    url = (
        os.environ.get("VLLM_BASE_URL")
        or os.environ.get("APPS_RG_QWEN_OPENAI_BASE")
        or "http://127.0.0.1:8000/v1"
    )
    ok, detail, _snap = qwen_vllm_http_models_preflight(provider_url=url, timeout_s=10.0)
    return ok, detail or url


def _scan_agent_strings(artifact_dir: Path) -> list[str]:
    hits: list[str] = []
    for p in sorted(artifact_dir.glob("*.json")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in AGENT_RE.findall(text):
            if m.startswith("agentic_core"):
                continue
            hits.append(f"{p.name}:{m}")
    return sorted(set(hits))


def _producer_components(artifact_dir: Path) -> list[str]:
    pcs: list[str] = []
    for p in artifact_dir.glob("*.json"):
        try:
            blob = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(blob, dict):
            pc = blob.get("producer_component")
            if isinstance(pc, str) and pc.strip():
                pcs.append(pc.strip())
        text = json.dumps(blob) if isinstance(blob, (dict, list)) else ""
        pcs.extend(re.findall(r'"producer_component"\s*:\s*"([^"]+)"', text))
    return sorted(set(pcs))


def run_live_spine(*, skip_if_no_vllm: bool) -> dict[str, Any]:
    _repo_on_path()
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report: dict[str, Any] = {
        "generated_utc": generated,
        "plan_slug": "agent-inventory-spine-taxonomy-b4e9f2",
        "wave": "W3",
        "runtime_proof_class": "LIVE_RUNTIME_PROOF",
        "mock_harness_backfill": False,
        "artifact_dir": OUT_DIR.relative_to(REPO).as_posix(),
        "vllm_preflight_ok": False,
        "vllm_detail": "",
        "spine_attempted": False,
        "spine_fault": None,
        "spine_run_id": None,
        "spine_x3": None,
        "artifacts": [],
        "producer_components": [],
        "agent_strings_in_artifacts": [],
        "a1_invoked_agent_classes": 0,
        "taxonomy_artifact_proven_updates": 0,
        "how_trace_stages_sample": [],
        "class_identity_fields_present": False,
        "decision_1_recommendation": "defer — keep function/stage HOW trace; no invoked_class on spine",
    }

    ok, detail = _vllm_reachable()
    report["vllm_preflight_ok"] = ok
    report["vllm_detail"] = detail
    if not ok and skip_if_no_vllm:
        report["blocked_reason"] = "vLLM unreachable — live L2 not attempted"
        return report

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("APPS_RG_L2_PROVIDER_MODE", "live_allowed")
    os.environ.setdefault("APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO", "1")
    os.environ.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)

    from apps_rg.cache.cache_preflight_evidence import (
        build_cache_preflight_evidence,
        write_whole_run_cache_preflight_artifact,
    )
    from apps_rg.cache.whole_run_entrypoint_preflight import (
        ENTRYPOINT_CANONICAL_DISPATCH,
        run_whole_run_cache_preflight,
    )
    from apps_rg.runtime.orchestration.canonical_dispatch import build_raw_request_for_r4
    from agentic_core.runtime.entrypoints.integrated_single_action_spine_run import (
        run_integrated_single_action_spine,
    )

    jd = REPO / "apps_rg" / "config" / "targeting" / "brown_brown_svp_it_strategy_innovation_jd.txt"
    brief = REPO / "apps_rg" / "config" / "targeting" / "brown_brown_svp_it_strategy_innovation_briefing.md"
    if not jd.is_file() or not brief.is_file():
        report["blocked_reason"] = "fixture JD/brief missing for live preflight"
        return report

    raw_request = build_raw_request_for_r4(
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        target_level="",
        jd=str(jd.relative_to(REPO)),
        manual_brief=str(brief.relative_to(REPO)),
        resume_path="",
        generation_mode="strategic_tailor",
    )

    preflight = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=raw_request,
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        artifact_dir=OUT_DIR,
        runs_dir=REPO / "artifacts" / "apps_rg" / "runs",
        policy_hash=os.environ.get("APPS_RG_POLICY_HASH"),
        blueprint_hash=os.environ.get("APPS_RG_BLUEPRINT_HASH"),
    )
    evidence = build_cache_preflight_evidence(preflight, artifact_dir=OUT_DIR)
    write_whole_run_cache_preflight_artifact(OUT_DIR, preflight, evidence)

    if not preflight.generation_required:
        report["blocked_reason"] = "cache preflight hit — generation not required (not a live miss run)"
        report["cache_preflight"] = {
            "generation_required": False,
            "cache_result": getattr(preflight, "cache_result", None),
        }
        return report

    report["spine_attempted"] = True
    outcome = run_integrated_single_action_spine(
        raw_request=raw_request,
        app_name="apps_rg",
        artifact_dir=OUT_DIR,
        route_family="R4_SINGLE_ACTION",
        cache_preflight_evidence=evidence,
        _test_mode=False,
    )
    report["spine_fault"] = (outcome.fault or "").strip() or None
    report["spine_run_id"] = outcome.run_id or None
    report["spine_x3"] = outcome.x3_disposition

    report["artifacts"] = sorted(p.name for p in OUT_DIR.glob("*.json"))
    report["producer_components"] = _producer_components(OUT_DIR)
    report["agent_strings_in_artifacts"] = _scan_agent_strings(OUT_DIR)
    report["a1_invoked_agent_classes"] = len(
        {h.split(":", 1)[-1] for h in report["agent_strings_in_artifacts"]}
    )

    how_path = OUT_DIR / "agentic_core_how_trace.json"
    if how_path.is_file():
        try:
            how_doc = json.loads(how_path.read_text(encoding="utf-8"))
            stages = how_doc.get("stages") or how_doc.get("stage_sequence") or []
            if isinstance(stages, list):
                report["how_trace_stages_sample"] = [
                    s.get("stage_id") or s.get("stage") or str(s)[:80]
                    for s in stages[:16]
                    if isinstance(s, dict)
                ]
            report["class_identity_fields_present"] = any(
                k in json.dumps(how_doc)
                for k in ("invoked_class", "executor_class", "agent_class")
            )
        except json.JSONDecodeError:
            pass

    proof_path = OUT_DIR / "agentic_core_spine_proof.json"
    if proof_path.is_file():
        try:
            proof = json.loads(proof_path.read_text(encoding="utf-8"))
            report["spine_proof_success"] = proof.get("success")
            report["spine_proof_status"] = proof.get("agentic_core_spine_status")
            report["mock_mode_detected"] = proof.get("mock_mode_detected")
        except json.JSONDecodeError:
            pass

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="W3 live spine proof runner")
    parser.add_argument(
        "--skip-if-no-vllm",
        action="store_true",
        help="Exit 0 with blocked report when vLLM preflight fails",
    )
    args = parser.parse_args(argv)
    report = run_live_spine(skip_if_no_vllm=args.skip_if_no_vllm)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "w3_live_spine_proof_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": out_path.relative_to(REPO).as_posix(), **report}, indent=2))
    if report.get("blocked_reason") and not report.get("spine_attempted"):
        return 2
    if report.get("spine_fault"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
