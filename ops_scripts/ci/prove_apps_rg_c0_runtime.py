#!/usr/bin/env python3
"""Runtime proof: apps_rg ``c0_retrieve_apps_rg`` → Chroma ``fact_vectors`` → ``FinalEvidenceContract``.

Invokes (unless ``--skip-subcommands``):
  1. ``check_apps_rg_fact_vectors_readiness.py``
  2. Narrow C0 pytest subset
  3. Live ``c0_retrieve_apps_rg`` against persisted Chroma (no mocks)

Writes ``artifacts/ci/apps_rg_c0_runtime_proof.json`` and exits non-zero on failure.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = REPO_ROOT / "artifacts/ci/apps_rg_c0_runtime_proof.json"

QUERY = (
    "Find apps_rg evidence supporting SVP Agentic AI platform leadership, governed runtime, "
    "C0 evidence, and Unify experience."
)


def _minimal_artifact() -> dict[str, Any]:
    return {
        "status": "FAIL",
        "claim_level": "apps_rg C0 runtime retrieval proof",
        "not_claiming": [
            "full resume generation",
            "full C0 to PA to L2 to Exit runtime",
            "Fort Knox RTC-REQ signoff",
            "L5 governed release signoff",
        ],
        "commands_run": [],
        "persist_path": "",
        "query": QUERY,
        "metadata_filter": {},
        "retrieved_count": 0,
        "evidence_item_count": 0,
        "support_status": "",
        "contract_type": "",
        "cross_app_leakage": False,
        "evidence_refs": [],
        "decisive_reason": "",
        "binding_entrypoint": "apps_rg.runtime.bindings.c0_binding.c0_retrieve_apps_rg",
        "fec_metadata_filter_refs": [],
        "fec_dense_search_refs": [],
        "all_chroma_items_c0_evidence_slot": False,
    }


def _run_cmd(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )


def _is_chroma_fact_item(item: Any) -> bool:
    st = str(getattr(item, "source_type", "") or "")
    src = str(getattr(item, "source", "") or "")
    return st == "fact_vectors" or src.startswith("chromadb:")


def _chunk_id(item: Any) -> str:
    eid = str(getattr(item, "evidence_id", "") or "")
    if eid.startswith("chroma:"):
        return eid.split(":", 1)[1]
    src = str(getattr(item, "source", "") or "")
    if src.startswith("chromadb:"):
        return src.rsplit(":", maxsplit=1)[-1]
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="apps_rg C0 binding runtime proof")
    parser.add_argument(
        "--skip-subcommands",
        action="store_true",
        help="Skip readiness gate + pytest (only run live c0_retrieve_apps_rg proof).",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(REPO_ROOT))
    art: dict[str, Any] = _minimal_artifact()
    cwd = REPO_ROOT

    if not args.skip_subcommands:
        r_gate = _run_cmd(
            [sys.executable, "ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py"],
            cwd=cwd,
        )
        art["commands_run"].append(
            {
                "cmd": "python ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py",
                "exit_code": r_gate.returncode,
                "stdout_tail": (r_gate.stdout or "")[-2000:],
                "stderr_tail": (r_gate.stderr or "")[-1000:],
            }
        )
        if r_gate.returncode != 0:
            art["status"] = "FAIL"
            art["decisive_reason"] = "READINESS_GATE_NONZERO"
            ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
            ARTIFACT_PATH.write_text(json.dumps(art, indent=2), encoding="utf-8")
            print(r_gate.stdout)
            print(r_gate.stderr, file=sys.stderr)
            return 1

        pytest_argv = [
            sys.executable,
            "-m",
            "pytest",
            "tests/_apps_contract/test_w4_c0_chroma_binding.py",
            "tests/_apps_contract/test_w5_c0_metadata_filter_integration.py",
            "tests/_apps_contract/test_w5_metadata_filter_and_claim_checker.py",
            "-q",
            "--tb=short",
            "-p",
            "pytest_timeout",
        ]
        _penv = os.environ.copy()
        # Match repo pytest discipline: explicit -p pytest_timeout requires autoload off.
        _penv.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        r_test = subprocess.run(
            pytest_argv,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            shell=False,
            env=_penv,
        )
        art["commands_run"].append(
            {
                "cmd": " ".join(pytest_argv),
                "env_note": "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 set for subprocess unless already exported.",
                "exit_code": r_test.returncode,
                "stdout_tail": (r_test.stdout or "")[-4000:],
                "stderr_tail": (r_test.stderr or "")[-2000:],
            }
        )
        if r_test.returncode != 0:
            art["status"] = "FAIL"
            art["decisive_reason"] = "PYTEST_C0_SUBSET_NONZERO"
            ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
            ARTIFACT_PATH.write_text(json.dumps(art, indent=2), encoding="utf-8")
            print(r_test.stdout)
            print(r_test.stderr, file=sys.stderr)
            return 1

    # Dense lane requires embedding when Chroma path is set (binding guard).
    if os.environ.get("EMBEDDING_ENABLED", "").strip().lower() not in ("1", "true"):
        os.environ["EMBEDDING_ENABLED"] = "true"
        print(
            "[prove_apps_rg_c0_runtime] EMBEDDING_ENABLED was unset/false — set to true for dense C0 proof.",
            file=sys.stderr,
        )

    persist = (os.environ.get("CHROMA_PERSIST_DIR") or "").strip() or str(
        REPO_ROOT / "data/cache/chromadb"
    )
    art["persist_path"] = persist

    # JD + resume inline: query text flows through section ``query_fields``; company/role
    # optional filters align with seeded smoke chunks (metadata filter lane proof).
    app_payload: dict[str, Any] = {
        "jd_payload": {
            "jd_text": QUERY,
            "target_company": "Contoso Labs",
            "target_role": "Principal Engineer",
        },
        "resume_payload": {
            "resume_text": QUERY,
            "headline": QUERY,
            "executive_summary": QUERY,
            "summary": QUERY,
            "competencies": "Python Kubernetes platform leadership governed runtime Unify",
            "skills": "Agentic AI platform leadership C0 evidence",
            "unify_bullets": "Unify quantified bullets metrics ownership",
            "unify_narrative": "Unify narrative cohesive story verification",
            "experience": QUERY,
        },
    }

    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.final_evidence_contract import (
        ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
        FinalEvidenceContract,
    )
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from apps_rg.runtime.bindings.c0_binding import (
        C0_METADATA_FILTER_REF,
        MetadataFilterProfile,
        c0_retrieve_apps_rg,
    )

    mp = MetadataFilterProfile()
    md_filter = mp.build_chroma_where_clause(
        app_payload,
        source_class_allowlist=["candidate_profile", "project_evidence"],
    )
    if md_filter is None:
        art["status"] = "FAIL"
        art["decisive_reason"] = "METADATA_FILTER_WHERE_NONE (profile disabled or misconfigured)"
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(json.dumps(art, indent=2), encoding="utf-8")
        return 1
    art["metadata_filter"] = md_filter

    route = RouteContract.__new__(RouteContract)
    object.__setattr__(route, "grounding_required", True)

    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "prove-apps-rg-c0-runtime")
    object.__setattr__(vr, "run_id", "prove-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "prove-trace")
    object.__setattr__(vr, "app_payload", app_payload)

    fec = c0_retrieve_apps_rg(route, vr, chromadb_path=persist)

    if not isinstance(fec, FinalEvidenceContract):
        art["decisive_reason"] = "RETURNED_OBJECT_NOT_FINAL_EVIDENCE_CONTRACT"
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_text(json.dumps(art, indent=2), encoding="utf-8")
        return 1

    art["contract_type"] = type(fec).__name__
    art["support_status"] = str(fec.support_status)
    art["fec_metadata_filter_refs"] = list(fec.metadata_filter_refs)
    art["fec_dense_search_refs"] = list(fec.dense_search_refs)

    chroma_items = [it for it in fec.evidence_items if _is_chroma_fact_item(it)]
    jd_resume_items = [
        it
        for it in fec.evidence_items
        if str(getattr(it, "source_type", "")) == "app_payload_inline"
        or str(getattr(it, "source", "")).startswith(("jd_payload", "resume_payload"))
    ]

    uniq_ids = sorted({_chunk_id(it) for it in chroma_items if _chunk_id(it)})

    art["retrieved_count"] = len(uniq_ids)
    # C0 dense proof: count Chroma-backed normative lane items only (not JD/resume carriers).
    art["evidence_item_count"] = len(chroma_items)

    art["evidence_refs"] = [
        {
            "evidence_id": getattr(it, "evidence_id", ""),
            "chunk_id": _chunk_id(it),
            "citation_anchor": getattr(it, "citation_anchor", ""),
            "fact_vec_ref": getattr(it, "fact_vec_ref", ""),
            "source_id": getattr(it, "source_id", ""),
            "allowed_prompt_slot": getattr(it, "allowed_prompt_slot", ""),
        }
        for it in chroma_items
    ]

    cross_leak = False
    if uniq_ids:
        import chromadb

        client = chromadb.PersistentClient(path=persist)
        col = client.get_collection("fact_vectors")
        got = col.get(ids=uniq_ids, include=["metadatas"])
        metas = got.get("metadatas") or []
        for meta in metas:
            if not isinstance(meta, dict):
                cross_leak = True
                continue
            if str(meta.get("app", "")) != "apps_rg":
                cross_leak = True
    art["cross_app_leakage"] = cross_leak

    c0_slot_ok = all(
        getattr(it, "allowed_prompt_slot", "") == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY
        for it in chroma_items
    )
    art["all_chroma_items_c0_evidence_slot"] = c0_slot_ok

    # Heuristic: output is evidence-grade (citation + fact_vec ref), not naked prose.
    refs_ok = all(
        bool(getattr(it, "citation_anchor", "") or "") and bool(getattr(it, "fact_vec_ref", "") or "")
        for it in chroma_items
    )

    mf_applied = bool(fec.metadata_filter_refs) and (C0_METADATA_FILTER_REF in fec.metadata_filter_refs)

    failures: list[str] = []
    if art["retrieved_count"] <= 0:
        failures.append("retrieved_count==0")
    if art["evidence_item_count"] <= 0:
        failures.append("evidence_item_count==0")
    if cross_leak:
        failures.append("cross_app_leakage")
    if not md_filter or "app" not in json.dumps(md_filter):
        failures.append("metadata_filter_missing_app")
    if not mf_applied:
        failures.append("fec_metadata_filter_refs_missing_dense_receipt")
    if not c0_slot_ok:
        failures.append("allowed_prompt_slot_not_c0_evidence_data_only")
    if not refs_ok:
        failures.append("missing_citation_anchor_or_fact_vec_ref")

    if failures:
        art["status"] = "FAIL"
        art["decisive_reason"] = "; ".join(failures)
    else:
        art["status"] = "PASS"
        art["decisive_reason"] = (
            f"{art['binding_entrypoint']} emitted {art['contract_type']} with "
            f"{art['retrieved_count']} unique Chroma chunks; "
            f"metadata_filter applied; cross_app_leakage=false; "
            f"C0 evidence-only prompt slot on all dense items."
        )

    art["fec_summary"] = {
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "app_id": fec.app_id,
        "support_target_met": fec.support_target_met,
        "support_status": fec.support_status,
        "final_evidence_digest": fec.final_evidence_digest,
        "citation_map_sample": list(fec.citation_map[:8]),
        "gate_verdict_refs": list(fec.gate_verdict_refs),
        "dense_search_refs": list(fec.dense_search_refs),
        "metadata_filter_refs": list(fec.metadata_filter_refs),
        "query_vec_ref": fec.query_vec_ref,
        "evidence_collection_timestamp": fec.evidence_collection_timestamp,
        "l5_certification_ref": fec.l5_certification_ref,
    }
    art["inline_payload_evidence_count"] = len(jd_resume_items)
    art["note"] = (
        "evidence_item_count counts Chroma dense-lane items only; "
        "jd_payload/resume_payload inline carriers are excluded from that count "
        "but appear in fec_summary.support_target_met."
    )

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(art, indent=2), encoding="utf-8")

    print(json.dumps({"status": art["status"], "artifact": str(ARTIFACT_PATH)}, indent=2))
    print("retrieved_unique_chunks", art["retrieved_count"])
    print("chroma_evidence_items", art["evidence_item_count"])
    print("support_status", art["support_status"])
    print("contract_type", art["contract_type"])
    print("cross_app_leakage", art["cross_app_leakage"])
    print("metadata_filter_refs", art["fec_metadata_filter_refs"])

    return 0 if art["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
