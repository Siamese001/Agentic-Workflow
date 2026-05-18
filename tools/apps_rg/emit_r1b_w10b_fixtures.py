"""Emit W10b R1B UWG receipt contract parity fixtures."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.cache.r1b_uwg_gateway_shim import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import (
    build_r1b_commit_bundle,
    build_r1b_promotion_candidate,
    promote_and_project_r1b_cache,
    promote_r1b_cache_via_uwg,
)
from apps_rg.cache.r1b_uwg_receipt_contract import (
    build_receipt_field_parity_matrix,
    document_shim_core_gaps,
)
from tools.apps_rg.emit_r1b_w10_fixtures import _candidate as _w10_candidate


def main() -> int:
    out = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w10b_fixtures"
    out.mkdir(parents=True, exist_ok=True)
    cand = _w10_candidate(out)
    store = R1BSemanticCacheStore(out / "_store")
    gw = AppsRgR1BUwgGateway()

    admitted = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        fixture_store=store,
        gateway=gw,
    )
    (out / "admitted_receipt_with_l5.json").write_text(
        json.dumps(
            {
                "promotion_outcome": admitted.to_dict(),
                "governance_receipt": admitted.governance_receipt,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    cr, sds, rb, rf = build_r1b_commit_bundle(cand)

    class _FakeCr:
        def __init__(self, **overrides: object) -> None:
            for k, v in overrides.items():
                setattr(self, k, v)
            for k, v in cr.__dict__.items():
                if not hasattr(self, k):
                    setattr(self, k, v)

    blocked_l5_cr = _FakeCr(l5_certification_ref="")
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(blocked_l5_cr, sds, rb, rf),
    ):
        blocked_l5 = promote_r1b_cache_via_uwg(cand, gateway=gw)
    (out / "blocked_missing_l5.json").write_text(
        json.dumps(blocked_l5.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    blocked_gate_cr = _FakeCr(gate_verdict_refs=())
    with patch(
        "apps_rg.cache.r1b_uwg_promotion.build_r1b_commit_bundle",
        return_value=(blocked_gate_cr, sds, rb, rf),
    ):
        blocked_gate = promote_r1b_cache_via_uwg(cand, gateway=gw)
    (out / "blocked_missing_gate_verdict.json").write_text(
        json.dumps(blocked_gate.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    (out / "receipt_field_parity_matrix.json").write_text(
        json.dumps(build_receipt_field_parity_matrix(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "shim_vs_core_gap.json").write_text(
        json.dumps(document_shim_core_gaps(), indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "file_backed_non_durable_manifest.json").write_text(
        json.dumps(store.store_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"W10b fixtures written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
