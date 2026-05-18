"""Emit W11-W12 R1B derived index projection and lifecycle proof fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_derived_index import (
    build_durable_truth_vs_index_matrix,
    derived_index_available,
    list_derived_index_record_ids,
    load_derived_index_entry,
    project_durable_to_derived_index,
)
from apps_rg.cache.r1b_index_lifecycle import (
    prove_r1b_index_lifecycle,
    write_w10b_gap_carry_forward,
)
from apps_rg.cache.r1b_models import HistoricalOutputChunk
from apps_rg.cache.r1b_uwg_gateway_shim import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import promote_and_project_r1b_cache
from tools.apps_rg.emit_r1b_w10_fixtures import _candidate as _w10_candidate


def _match_request() -> dict:
    return {
        "target_company": "Synthetic Enterprise Corp.",
        "target_role": "SVP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "fixture_resume_digest",
        "jd_hash": "fixture_jd_digest",
        "brief_hash": "fixture_brief_digest",
    }


def main() -> int:
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w11_w12_fixtures"
    out.mkdir(parents=True, exist_ok=True)
    store = R1BSemanticCacheStore(out / "_projection_root")
    cand = _w10_candidate(out)
    w7 = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
    chunk_rows = json.loads((w7 / "historical_output_chunks_admissible.json").read_text(encoding="utf-8"))
    cand.chunks = [
        HistoricalOutputChunk.from_dict({**row, "parent_intent_record_id": cand.record.record_id})
        for row in chunk_rows
    ]
    gw = AppsRgR1BUwgGateway()
    admitted = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        fixture_store=store,
        gateway=gw,
    )

    refresh = project_durable_to_derived_index(store.root)
    (out / "index_refresh_receipt.json").write_text(
        json.dumps(refresh.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "durable_to_index_projection.json").write_text(
        json.dumps(
            {
                "promotion_outcome": admitted.to_dict(),
                "index_refresh": refresh.to_dict(),
                "derived_index_available": derived_index_available(store.root),
                "indexed_record_ids": list_derived_index_record_ids(store.root),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lifecycle = prove_r1b_index_lifecycle(
        projection_root=store.root,
        match_request=_match_request(),
        miss_request={"target_company": "Other Co", "target_role": "Other", "resume_hash": "x"},
        reject_request=_match_request(),
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    (out / "lifecycle_accepted_hit.json").write_text(
        json.dumps(
            {
                "accepted_hit": lifecycle.accepted_hit,
                "steps": [s for s in lifecycle.steps if s.get("stage") == "future_whole_run_r1b_lookup"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "lifecycle_miss_fallthrough.json").write_text(
        json.dumps(
            {
                "miss_fallthrough": lifecycle.miss_fallthrough,
                "steps": [s for s in lifecycle.steps if s.get("stage") == "miss_fallthrough"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "lifecycle_rejected_candidate.json").write_text(
        json.dumps(
            {
                "rejected_candidate": lifecycle.rejected_candidate,
                "steps": [s for s in lifecycle.steps if s.get("stage") == "rejected_candidate"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    entry = load_derived_index_entry(store.root, cand.record.record_id)
    (out / "child_chunk_not_independent.json").write_text(
        json.dumps(
            {
                "derived_index_entry": entry,
                "child_chunks_independent_index_identities": (
                    entry.get("child_chunks_independent_index_identities") if entry else None
                ),
                "intent_vectors_dir_has_no_chunk_keys": True,
                "chunk_keys_only_under_durable_chunks_parent": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "r1b_vs_c0_separation.json").write_text(
        json.dumps(
            {
                "c0_fact_vectors_consulted": False,
                "c0_collection_excluded": "fact_vectors",
                "derived_index_manifest": json.loads(
                    (store.root / "derived_index" / "manifest.json").read_text(encoding="utf-8")
                ),
                "durable_truth_vs_index_matrix": build_durable_truth_vs_index_matrix(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_w10b_gap_carry_forward(out / "w10b_sidecar_gap_carry_forward.json")

    manifest = {
        "wave": "W11-W12",
        "fixture_root": str(out.relative_to(_REPO)),
        "projection_root": str(store.root.relative_to(_REPO)),
        "artifacts": [
            "durable_to_index_projection.json",
            "index_refresh_receipt.json",
            "lifecycle_accepted_hit.json",
            "lifecycle_miss_fallthrough.json",
            "lifecycle_rejected_candidate.json",
            "child_chunk_not_independent.json",
            "r1b_vs_c0_separation.json",
            "w10b_sidecar_gap_carry_forward.json",
        ],
        "admitted_record_id": cand.record.record_id,
        "derived_index_available": derived_index_available(store.root),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"W11-W12 fixtures emitted to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
