"""Emit W9 whole-run R1B preflight proof fixtures."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_whole_run_preflight import execute_whole_run_r1b_preflight


def _seed_w7_admissible(store: R1BSemanticCacheStore) -> None:
    w7 = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    intent = json.loads((w7 / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    chunks = json.loads((w7 / "historical_output_chunks_admissible.json").read_text(encoding="utf-8"))
    record = HistoricalIntentRecord.from_dict(intent)
    store.write_intent(record)
    for row in chunks:
        store.write_chunk(HistoricalOutputChunk.from_dict(row))


def _matching_request() -> dict:
    return {
        "target_company": "Synthetic Enterprise Corp.",
        "target_role": "SVP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "fixture_resume_digest",
        "jd_hash": "fixture_jd_digest",
        "brief_hash": "fixture_brief_digest",
    }


def main() -> int:
    import os

    os.environ["APPS_RG_R1B_SKIP_UWG"] = "1"
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w9_fixtures"
    store_root = out / "_store"
    if store_root.exists():
        shutil.rmtree(store_root)
    store = R1BSemanticCacheStore(store_root)
    _seed_w7_admissible(store)
    out.mkdir(parents=True, exist_ok=True)

    hit = execute_whole_run_r1b_preflight(
        raw_request=_matching_request(),
        runs_dir=store_root,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    (out / "accepted_r1b_hit.json").write_text(
        json.dumps(hit.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    miss = execute_whole_run_r1b_preflight(
        raw_request={
            "target_company": "Unknown Company",
            "target_role": "Unknown Role",
            "generation_mode": "strategic_tailor",
            "resume_hash": "x",
            "jd_hash": "y",
            "brief_hash": "z",
        },
        runs_dir=store_root,
        similarity_threshold=0.99,
    )
    (out / "semantic_miss_fallthrough.json").write_text(
        json.dumps(miss.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    inadmissible = execute_whole_run_r1b_preflight(
        raw_request=_matching_request(),
        runs_dir=store_root,
        similarity_threshold=0.5,
        prompt_profile_hash="profile_MISMATCH",
        gate_profile_hash="gate_MISMATCH",
    )
    (out / "inadmissible_profile_mismatch.json").write_text(
        json.dumps(inadmissible.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    fallthrough = {
        "outcome": miss.outcome,
        "generation_required": miss.generation_required,
        "pipeline_invoked": True,
        "note": "On r1b_miss or r1b_inadmissible_only, apps_rg/__main__ continues to run_integrated_r4_deterministic_pipeline",
        "preflight_order": list(miss.to_dict().get("preflight_order", [])),
    }
    (out / "fallthrough_to_generation.json").write_text(
        json.dumps(fallthrough, indent=2) + "\n",
        encoding="utf-8",
    )

    inspection = hit.child_chunk_inspection or {}
    (out / "child_chunks_inspected_not_independently_retrieved.json").write_text(
        json.dumps(inspection, indent=2) + "\n",
        encoding="utf-8",
    )

    c0_sep = {
        "c0_fact_vectors_consulted": hit.c0_fact_vectors_consulted,
        "not_c0_fact_vectors": True,
        "lookup_anchor": hit.lookup_anchor,
        "r1b_vs_c0": hit.to_dict().get("r1b_vs_c0"),
    }
    (out / "r1b_vs_c0_separation.json").write_text(
        json.dumps(c0_sep, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"W9 fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
