"""Emit W10 R1B UWG durable promotion proof fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_uwg_gateway_shim import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_durable_write_guard import record_blocked_direct_r1b_write
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import (
    build_r1b_promotion_candidate,
    promote_and_project_r1b_cache,
    promote_r1b_cache_via_uwg,
)


def _candidate(out: Path) -> object:
    run_dir = out / "_run"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "proof_eligible": True}),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run_w10",
                "proof_eligible": True,
                "prompt_profile_hash": "prompt_profile_w7_v1",
                "gate_profile_hash": "gate_profile_w7_v1",
            }
        ),
        encoding="utf-8",
    )
    w7 = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    base = json.loads((w7 / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    base["record_id"] = "hir_w10_admitted"
    base["source_run_id"] = "run_w10"
    base["request_intent_vector_ref"] = "vectors/hir_w10_admitted.json"
    rec = HistoricalIntentRecord.from_dict(base)
    chunks = [
        HistoricalOutputChunk.from_dict(
            {
                "chunk_id": "hoc_w10_a",
                "parent_intent_record_id": rec.record_id,
                "chunk_type": "final_resume",
                "section_id": "",
                "chunk_text": "{}",
                "chunk_digest": "",
                "chunk_vector_ref": "",
                "artifact_ref": "generated_resume.json",
                "artifact_digest": "",
                "source_fact_ids": [],
                "proof_pool_refs": [],
                "support_status": "",
                "x2_status": "PASS",
                "x1d_status": "",
                "section_prompt_hash": "",
                "section_model_profile_hash": "",
                "generated_at_utc": "2026-05-18T00:00:00+00:00",
            }
        )
    ]
    assessment = {
        "admissible": True,
        "record": rec.to_dict(),
        "chunks": [c.to_dict() for c in chunks],
        "exit_metadata": {"source_run_id": "run_w10", "x3_disposition": "X3_ALLOW"},
    }
    return build_r1b_promotion_candidate(
        record=rec,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=run_dir,
    )


def main() -> int:
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w10_fixtures"
    out.mkdir(parents=True, exist_ok=True)
    gw = AppsRgR1BUwgGateway()
    cand = _candidate(out)
    store = R1BSemanticCacheStore(out / "_fixture_mirror")
    admitted = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        fixture_store=store,
        gateway=gw,
    )
    (out / "uwg_admitted_promotion.json").write_text(
        json.dumps(
            {
                "promotion_outcome": admitted.to_dict(),
                "commit_request_id": admitted.commit_request_id,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    bad_rec = HistoricalIntentRecord.from_dict(
        {**cand.record.to_dict(), "cache_admissible": False, "record_id": "hir_w10_blocked"}
    )
    bad_cand = build_r1b_promotion_candidate(
        record=bad_rec,
        chunks=cand.chunks,
        post_exit_eligibility={**cand.post_exit_eligibility, "admissible": False},
    )
    blocked = promote_r1b_cache_via_uwg(bad_cand, gateway=gw)
    (out / "blocked_promotion.json").write_text(
        json.dumps(blocked.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    (out / "l2_direct_write_blocked.json").write_text(
        json.dumps(
            record_blocked_direct_r1b_write(
                attempting_surface="L2",
                reason="r1b_fixture_l2_blocked",
                run_id="run_w10",
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "l6_direct_write_blocked.json").write_text(
        json.dumps(
            record_blocked_direct_r1b_write(
                attempting_surface="L6",
                reason="r1b_fixture_l6_blocked",
                run_id="run_w10",
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "file_backed_non_durable_manifest.json").write_text(
        json.dumps(store.store_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"W10 fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
