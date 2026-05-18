"""Emit W7 R1B semantic-cache proof fixtures under artifacts/apps_rg/r1b_semantic_cache/w7_fixtures/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
from apps_rg.cache.r1b_constants import (
    CHUNK_TYPE_EXEC_SUMMARY,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
)
from apps_rg.cache.r1b_retrieval import lookup_r1b_with_compatibility_report


def _raw(company: str, role: str) -> dict:
    return {
        "target_company": company,
        "target_role": role,
        "generation_mode": "strategic_tailor",
        "resume_hash": "fixture_resume_digest",
        "jd_hash": "fixture_jd_digest",
        "brief_hash": "fixture_brief_digest",
    }


def _exit_ctx(store_root: Path, record_id: str, **extra: object) -> dict:
    exit_dir = store_root / "_exit" / record_id
    exit_dir.mkdir(parents=True, exist_ok=True)
    (exit_dir / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": extra.get("x3_disposition", "X3_ALLOW"),
                "proof_eligible": extra.get("proof_eligible", True),
                "runtime_generation_status": extra.get("runtime_generation_status", "REAL_LLM"),
                "proceed_to_runtime": True,
            }
        ),
        encoding="utf-8",
    )
    (exit_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": extra.get("run_id", record_id),
                "section_id": "executive_summary",
                "proof_eligible": extra.get("proof_eligible", True),
                "runtime_generation_status": extra.get("runtime_generation_status", "REAL_LLM"),
                "prompt_profile_hash": extra.get("prompt_profile_hash", "prompt_profile_w7_v1"),
                "gate_profile_hash": extra.get("gate_profile_hash", "gate_profile_w7_v1"),
            }
        ),
        encoding="utf-8",
    )
    if extra.get("include_output_artifacts", True):
        (exit_dir / "generated_resume.json").write_text('{"sections": []}', encoding="utf-8")
        (exit_dir / "l2_output.json").write_text('{"text": "fixture"}', encoding="utf-8")
        (exit_dir / "x2_gate_outputs.json").write_text('{"x2_failed": 0}', encoding="utf-8")
    return {
        "record_id": record_id,
        "post_exit_ingestion": True,
        "artifact_dir": str(exit_dir),
        "x3_disposition": str(extra.get("x3_disposition", "X3_ALLOW")),
        "proof_eligible": extra.get("proof_eligible", True),
        "runtime_generation_status": str(extra.get("runtime_generation_status", "REAL_LLM")),
        **{k: v for k, v in extra.items()},
    }


def _chunks() -> list[dict]:
    return [
        {"chunk_type": CHUNK_TYPE_FINAL_RESUME, "chunk_text": "{}", "artifact_ref": "generated_resume.json"},
        {
            "chunk_type": CHUNK_TYPE_EXEC_SUMMARY,
            "section_id": "executive_summary",
            "chunk_text": "Fixture executive summary.",
            "x2_status": "PASS",
        },
        {"chunk_type": CHUNK_TYPE_SECTION_PROOF, "section_id": "executive_summary", "chunk_text": "{}"},
    ]


def _build_post_exit_record(
    *,
    raw_request: dict,
    chunks: list[dict],
    run_context: dict,
) -> object:
    """Build HistoricalIntentRecord after post-Exit verdict (for non-mirrored reject fixtures)."""
    from apps_rg.cache.r1b_ingest import build_intent_record_complete, chunks_from_output_list
    from apps_rg.cache.r1b_post_exit_eligibility import (
        apply_post_exit_verdict_to_record,
        assess_post_exit_ingestion_eligibility,
        load_post_exit_metadata,
    )

    record_id = str(run_context["record_id"])
    meta = {
        "prompt_profile_hash": str(
            run_context.get("prompt_profile_hash") or run_context.get("policy_hash") or ""
        ),
        "gate_profile_hash": str(
            run_context.get("gate_profile_hash") or run_context.get("blueprint_hash") or ""
        ),
        "runtime_generation_status": str(run_context.get("runtime_generation_status") or ""),
        "x3_disposition": str(run_context.get("x3_disposition") or ""),
        "proof_eligible": run_context.get("proof_eligible"),
    }
    child_chunks = chunks_from_output_list(
        parent_intent_record_id=record_id,
        output_chunks=chunks,
    )
    record = build_intent_record_complete(
        raw_request=raw_request,
        run_context=run_context,
        metadata=meta,
        chunks=child_chunks,
    )
    exit_dir = Path(str(run_context["artifact_dir"]))
    exit_meta = load_post_exit_metadata(exit_dir)
    verdict = assess_post_exit_ingestion_eligibility(record, child_chunks, exit_meta=exit_meta)
    return apply_post_exit_verdict_to_record(record, verdict)


def _export_intent_fixture(
    *,
    store_root: Path,
    out: Path,
    record_id: str,
    label: str,
    raw_request: dict,
    chunks: list[dict],
    run_context: dict,
) -> None:
    """Copy mirrored intent from store, or build rejected record when store skips mirror."""
    intent_path = store_root / "intents" / f"{record_id}.json"
    if intent_path.is_file():
        payload = intent_path.read_text(encoding="utf-8")
    else:
        record = _build_post_exit_record(
            raw_request=raw_request,
            chunks=chunks,
            run_context=run_context,
        )
        payload = json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n"
        if record.cache_admissible:
            raise RuntimeError(f"expected non-admissible fixture for {label}")
    (out / f"historical_intent_record_{label}.json").write_text(payload, encoding="utf-8")


def main() -> int:
    import os

    # W10: fixture emit uses file mirror only; durable truth is UWG-admitted projection.
    os.environ["APPS_RG_R1B_SKIP_UWG"] = "1"
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    out.mkdir(parents=True, exist_ok=True)
    store_root = out / "_store"
    if store_root.exists():
        import shutil

        shutil.rmtree(store_root)
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(store_root))

    adm_id = "hir_w7_admissible_001"
    adapter.store_intent_and_output(
        intent=_raw("Synthetic Enterprise Corp.", "SVP Engineering"),
        chunks=_chunks(),
        run_context=_exit_ctx(
            store_root,
            adm_id,
            run_id="run_w7_admissible",
            x3_disposition="X3_ALLOW",
            proof_eligible=True,
            runtime_generation_status="REAL_LLM",
            prompt_profile_hash="prompt_profile_w7_v1",
            gate_profile_hash="gate_profile_w7_v1",
        ),
    )
    intent_path = store_root / "intents" / f"{adm_id}.json"
    chunks_dir = store_root / "chunks" / adm_id
    (out / "historical_intent_record_admissible.json").write_text(
        intent_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    chunk_bundle = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(chunks_dir.glob("*.json"))]
    (out / "historical_output_chunks_admissible.json").write_text(
        json.dumps(chunk_bundle, indent=2) + "\n",
        encoding="utf-8",
    )

    mismatch_id = "hir_w7_rejected_digest_mismatch"
    adapter.store_intent_and_output(
        intent=_raw("Synthetic Enterprise Corp.", "SVP Engineering"),
        chunks=_chunks(),
        run_context=_exit_ctx(
            store_root,
            mismatch_id,
            x3_disposition="X3_ALLOW",
            proof_eligible=True,
            runtime_generation_status="REAL_LLM",
            prompt_profile_hash="prompt_profile_stale",
            gate_profile_hash="gate_profile_stale",
        ),
    )
    (out / "historical_intent_record_rejected_digest_mismatch.json").write_text(
        (store_root / "intents" / f"{mismatch_id}.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    for label, ctx in (
        ("rejected_offline_stub", {"runtime_generation_status": "OFFLINE_CONTRACT_STUB"}),
        ("rejected_not_proof_eligible", {"proof_eligible": False}),
    ):
        rid = f"hir_w7_{label}"
        reject_raw = _raw("RejectCo", "Role")
        reject_chunks = _chunks()
        reject_ctx = _exit_ctx(
            store_root,
            rid,
            x3_disposition="X3_ALLOW",
            proof_eligible=ctx.get("proof_eligible", True),
            runtime_generation_status=ctx.get("runtime_generation_status", "REAL_LLM"),
            prompt_profile_hash="p1",
            gate_profile_hash="g1",
        )
        adapter.store_intent_and_output(
            intent=reject_raw,
            chunks=reject_chunks,
            run_context=reject_ctx,
        )
        _export_intent_fixture(
            store_root=store_root,
            out=out,
            record_id=rid,
            label=label,
            raw_request=reject_raw,
            chunks=reject_chunks,
            run_context=reject_ctx,
        )

    from apps_rg.cache.r1b_store import R1BSemanticCacheStore

    st = R1BSemanticCacheStore(store_root)
    hit, report = lookup_r1b_with_compatibility_report(
        _raw("Synthetic Enterprise Corp.", "SVP Engineering"),
        store=st,
        similarity_threshold=0.5,
    )
    # Profile-hash mismatch rows (query expects current profile, stale candidate fails).
    intent_text = __import__(
        "apps_rg.cache.r1b_intent_vector", fromlist=["intent_text_from_request"]
    ).intent_text_from_request(_raw("Synthetic Enterprise Corp.", "SVP Engineering"))
    query_digest = __import__(
        "apps_rg.cache.r1b_intent_vector", fromlist=["normalized_intent_digest"]
    ).normalized_intent_digest(intent_text)
    mismatch_rec = st.load_intent(mismatch_id)
    if mismatch_rec is not None:
        from apps_rg.cache.r1b_compatibility import assess_candidate_for_reuse, compatibility_report_row
        from apps_rg.cache.r1b_intent_vector import cosine_similarity, pseudo_vector_from_digest

        rec_vec = st.load_intent_vector(mismatch_rec)
        qv = pseudo_vector_from_digest(query_digest)
        sim = cosine_similarity(qv, rec_vec)
        chunks = st.load_chunks(mismatch_id)
        verdict = assess_candidate_for_reuse(
            mismatch_rec,
            chunks,
            query_digest=query_digest,
            query_prompt_hash="prompt_profile_w7_v1",
            query_gate_hash="gate_profile_w7_v1",
        )
        report.append(
            compatibility_report_row(
                candidate_record_id=mismatch_id,
                verdict=verdict,
                similarity=sim,
            )
        )
    compat = {
        "accepted_candidate_record_id": hit.record.record_id if hit else None,
        "candidates": report,
        "r1b_vs_c0": "HistoricalIntentRecord vectors only; not Chroma fact_vectors",
    }
    (out / "compatibility_report_w7.json").write_text(json.dumps(compat, indent=2) + "\n", encoding="utf-8")
    print(f"W7 fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
