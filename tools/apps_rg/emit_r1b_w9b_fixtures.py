"""Emit W9b whole-run entrypoint parity proof fixtures."""

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
from apps_rg.cache.whole_run_entrypoint_preflight import (
    ENTRYPOINT_CANONICAL_DISPATCH,
    build_cache_hit_dispatch_result,
    build_entrypoint_audit_matrix,
    run_whole_run_cache_preflight,
)


def _seed_w7(store: R1BSemanticCacheStore) -> None:
    w7 = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    intent = json.loads((w7 / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    chunks = json.loads((w7 / "historical_output_chunks_admissible.json").read_text(encoding="utf-8"))
    store.write_intent(HistoricalIntentRecord.from_dict(intent))
    for row in chunks:
        store.write_chunk(HistoricalOutputChunk.from_dict(row))


def _request() -> dict:
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
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w9b_fixtures"
    store_root = out / "_store"
    if store_root.exists():
        shutil.rmtree(store_root)
    store = R1BSemanticCacheStore(store_root)
    _seed_w7(store)
    out.mkdir(parents=True, exist_ok=True)
    os.environ["SEMANTIC_CACHE_D2_ENABLED"] = "1"
    os.environ["APPS_RG_R1B_CACHE_ROOT"] = str(store_root.resolve())

    hit_pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=_request(),
        target_company="Synthetic Enterprise Corp.",
        target_role="SVP Engineering",
        artifact_dir=out / "production_hit",
        runs_dir=out,
        policy_hash="prompt_profile_w7_v1",
        blueprint_hash="gate_profile_w7_v1",
    )
    hit_payload = {
        "preflight": hit_pf.to_dict(),
        "dispatch_result": build_cache_hit_dispatch_result(hit_pf),
    }
    (out / "production_entrypoint_accepted_hit.json").write_text(
        json.dumps(hit_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    miss_pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request={
            "target_company": "UnknownCo",
            "target_role": "Unknown",
            "resume_hash": "x",
            "jd_hash": "y",
        },
        target_company="UnknownCo",
        target_role="Unknown",
        artifact_dir=out / "production_miss",
        runs_dir=out,
    )
    (out / "production_entrypoint_miss_fallthrough.json").write_text(
        json.dumps(miss_pf.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    reject_pf = run_whole_run_cache_preflight(
        entrypoint=ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request=_request(),
        target_company="Synthetic Enterprise Corp.",
        target_role="SVP Engineering",
        artifact_dir=out / "production_reject",
        runs_dir=out,
        policy_hash="WRONG_PROFILE",
        blueprint_hash="WRONG_GATE",
    )
    (out / "production_entrypoint_rejected_candidate.json").write_text(
        json.dumps(reject_pf.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    (out / "entrypoint_audit_matrix.json").write_text(
        json.dumps(build_entrypoint_audit_matrix(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"W9b fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
