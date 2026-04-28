"""Every contract.span_id must resolve to a span in the OTEL trace.

If a contract claims it was emitted by span X, then X must exist.
Detached contracts (claiming a non-existent span) are forbidden.
"""

from __future__ import annotations

import json
from pathlib import Path


def test_contract_inventory_spans_exist(proof_dir: Path, otel_trace: list[dict]) -> None:
    span_ids = {s.get("span_id") for s in otel_trace if isinstance(s, dict)}
    inventory_path = proof_dir / "contracts" / "contract_inventory.json"
    if not inventory_path.exists():
        # Inventory may not be present in every layout; fall back to scanning
        # the wrapper field on every canonical contract.
        for jp in (proof_dir / "contracts").glob("*.json"):
            body = json.loads(jp.read_text(encoding="utf-8"))
            if isinstance(body, dict):
                sp = body.get("span_id")
                if sp is not None:
                    assert sp in span_ids, (
                        f"{jp.name} span_id={sp!r} not in trace ({len(span_ids)} spans)"
                    )
        return
    body = json.loads(inventory_path.read_text(encoding="utf-8"))
    payload = body.get("payload", body) if isinstance(body, dict) else body
    if isinstance(payload, list):
        for rec in payload:
            if isinstance(rec, dict):
                sp = rec.get("emitted_by_span_id")
                if sp is None:
                    continue
                assert sp in span_ids, (
                    f"contract_inventory record emitted_by_span_id={sp!r} not in trace"
                )


def test_span_tree_has_root_and_no_orphans(otel_trace: list[dict]) -> None:
    span_ids = {s.get("span_id") for s in otel_trace if isinstance(s, dict)}
    roots = 0
    for s in otel_trace:
        if not isinstance(s, dict):
            continue
        parent = s.get("parent_span_id")
        if parent is None:
            roots += 1
            continue
        assert parent in span_ids, f"orphan span: parent_span_id={parent}"
    assert roots >= 1, "no root span"
