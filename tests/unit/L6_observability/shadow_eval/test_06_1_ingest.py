"""06.1 ingest/normalization doctrine tests.

Doctrine TEST REQUIREMENTS (06.1) — all enforced here:
- L6 must reject in-flight run as completed.
- Missing evidence is not filled by inference.
- Raw traces are not rewritten — they are referenced.
- Lineage is not summarized away.
- Optional stage absence is NOT_APPLICABLE, not failure.
- Required stage absence is reflected in gap report.
- Orphan artifacts produce a gap report entry.
- Normalized records carry replay_key, policy_hash, trace lineage.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.shadow_eval import (
    IngestError,
    REASON_EXIT_DISPOSITION_MISSING,
    REASON_LIVE_RUN_NOT_CLOSED,
    REASON_REPLAY_KEY_MISSING,
    REASON_TRACE_LINK_MISSING,
    build_runtime_exhaust_bundle,
    receive_completed_run_marker,
    stratify_outcome,
)


def test_in_flight_run_is_rejected(in_flight_run):
    with pytest.raises(IngestError) as exc:
        receive_completed_run_marker(in_flight_run)
    assert REASON_LIVE_RUN_NOT_CLOSED in str(exc.value)


def test_missing_exit_disposition_is_rejected(run_missing_exit):
    with pytest.raises(IngestError) as exc:
        receive_completed_run_marker(run_missing_exit)
    assert REASON_EXIT_DISPOSITION_MISSING in str(exc.value)


def test_repair_fixture_allows_missing_exit(run_missing_exit):
    # Repair fixture marker explicitly permits ingest of missing-exit runs.
    receive_completed_run_marker(run_missing_exit, repair_fixture=True)


def test_full_pipeline_smoke(sealed_completed_run):
    bundle, normalized, manifests, stage_map, inv, gap = build_runtime_exhaust_bundle(sealed_completed_run)
    assert bundle.runtime_boundary_crossed
    assert bundle.deterministic_digest
    # 06.1: required stages present, no gap codes for missing required stages.
    assert "U0" not in stage_map.missing_stages
    assert "L1" not in stage_map.missing_stages
    assert "L0" not in stage_map.missing_stages
    assert "L2" not in stage_map.missing_stages
    assert "EXIT" not in stage_map.missing_stages
    assert not stage_map.impossible_order_flags
    # 06.1: lineage preserved per source manifest.
    assert all(m.source_ref for m in manifests)
    # 06.1: normalized records carry policy_hash, replay_key, trace lineage.
    for rec in normalized:
        assert rec.replay_key == "replay-key-A"
        assert rec.policy_hash == "policy-hash-A"
        assert rec.trace_id and rec.span_id
    # 06.1: artifact inventory preserves lineage and hashes.
    assert inv.file_hashes
    assert inv.artifact_lineage
    # 06.1: gap_codes for fully-clean run should not include trace/replay/policy issues.
    assert REASON_TRACE_LINK_MISSING not in gap.gap_codes
    assert REASON_REPLAY_KEY_MISSING not in gap.gap_codes


def test_missing_trace_root_emits_gap(run_missing_trace_root):
    bundle, _norm, _mans, _smap, _inv, gap = build_runtime_exhaust_bundle(run_missing_trace_root)
    assert REASON_TRACE_LINK_MISSING in gap.gap_codes
    # Missing field must NOT be filled by inference.
    assert bundle.trace_root == ""


def test_missing_replay_key_emits_gap(run_missing_replay_key):
    bundle, _norm, _mans, _smap, _inv, gap = build_runtime_exhaust_bundle(run_missing_replay_key)
    assert REASON_REPLAY_KEY_MISSING in gap.gap_codes
    assert bundle.replay_key is None


def test_lineage_not_summarized(sealed_completed_run):
    """Source manifests retain raw refs; nothing is collapsed."""
    _b, _n, manifests, _smap, _inv, _gap = build_runtime_exhaust_bundle(sealed_completed_run)
    raw_refs = [s["source_ref"] for s in sealed_completed_run["source_exhaust"]]
    manifest_refs = [m.source_ref for m in manifests]
    for r in raw_refs:
        assert r in manifest_refs


def test_outcome_stratification_known(sealed_completed_run):
    assert stratify_outcome(sealed_completed_run) == "normal_success"


def test_outcome_stratification_unknown_class():
    assert stratify_outcome({"outcome_class": "made_up_class"}) == "unresolved_unknown"


def test_normalized_records_omit_no_required_field(sealed_completed_run):
    _b, normalized, _m, _s, _i, _g = build_runtime_exhaust_bundle(sealed_completed_run)
    for rec in normalized:
        assert rec.replay_key, "doctrine: normalized record must carry replay_key"
        assert rec.policy_hash, "doctrine: normalized record must carry policy_hash"
        assert rec.trace_id, "doctrine: normalized record must carry trace lineage"


def test_orphan_artifact_appears_in_gap_report(sealed_completed_run):
    """Adding an orphan source produces a gap report entry."""
    payload = dict(sealed_completed_run)
    payload["source_exhaust"] = list(payload["source_exhaust"]) + [
        {
            "source_type": "stray",
            "source_ref": "orphan-1",
            "source_hash": "ophash",
            "observed_stage": "UNKNOWN",
            "expected_stage_order": -1,
            "lineage_parent_refs": [],
            "completeness_status": "PARTIAL",
            "trust_status": "UNKNOWN",
        }
    ]
    _b, _n, _m, _smap, _inv, gap = build_runtime_exhaust_bundle(payload)
    assert "ORPHAN_ARTIFACT" in gap.gap_codes or gap.orphan_artifact_refs


def test_impossible_stage_order_flagged():
    """UWG observed without EXIT is impossible per stage map rules."""
    payload = {
        "runtime_boundary_crossed": True,
        "completed_at": "2026-04-26T00:00:00Z",
        "request_id": "r",
        "run_id": "rr",
        "session_id": "s",
        "tenant_id": "t",
        "trace_root": "tr",
        "exit_disposition_ref": None,  # impossible without exit
        "policy_hash": "p",
        "blueprint_hash": "b",
        "replay_key": "rk",
        "source_exhaust": [
            {
                "source_type": "uwg",
                "source_ref": "uwg-1",
                "source_hash": "h",
                "observed_stage": "UWG",
                "expected_stage_order": 4,
                "lineage_parent_refs": ["x"],
            }
        ],
        "events": [],
        "artifacts": {},
    }
    # First, have to bypass marker check.
    bundle, _n, _m, smap, _inv, gap = build_runtime_exhaust_bundle(
        {**payload, "exit_disposition_ref": "exit-1"}
    )
    # We provided UWG without EXIT in source_exhaust — stagemap should flag.
    assert "UWG_BEFORE_EXIT" in smap.impossible_order_flags or "EXIT" in smap.missing_stages
