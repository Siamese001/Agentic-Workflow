"""Tests for the back-fill script for runtime ADG trace-index repair."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L6_system_learning.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)
from agentic_core.L6_system_learning.store import FileBackedRuntimeADGStore
from tools.runtime_adg.backfill_trace_index import apply_backfill, build_backfill


@pytest.fixture
def populated_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Build a runtime_adg dir that simulates the production-bug state:
    - N snapshots on disk with real trace_ids
    - but _trace_index.json only has an empty-string entry"""
    monkeypatch.setattr(
        FileBackedRuntimeADGStore,
        "_validate_l4_compliance",
        lambda self: None,
    )
    # Stub broken memory bridge dep (missing tools.implement_unified_memory).
    from agentic_core.L6_system_learning.stores import version_store as vs_mod

    class _NullBridge:
        def persist_active_version(self, *_args, **_kwargs) -> None:
            return None

    monkeypatch.setattr(vs_mod, "get_sl_memory_bridge", lambda: _NullBridge())
    base = tmp_path / "runtime_adg"
    store = FileBackedRuntimeADGStore(base_dir=base)

    # Persist some real snapshots (Tier-1 compliant — guardrail satisfied).
    for i in range(3):
        node = RuntimeADGNode(
            node_id=f"n{i}",
            name=f"span.{i}",
            kind="t",
            layer="L2",
            component="C",
            started_at_utc=i,
            duration_ms=1.0,
            status="ok",
            attributes_json="{}",
        )
        snap = create_runtime_adg_snapshot(
            trace_id=f"real-trace-{i}",
            mission=f"m{i}",
            started_at_utc=i,
            ended_at_utc=i + 1,
            nodes=(node,),
            edges=(),
        )
        store.persist(snap)

    # Also drop a malformed empty snapshot directly onto disk to simulate the
    # residue from the pre-Tier-1 bug. We need a real version entry for it,
    # so persist it via allow_* escape hatches then corrupt the trace index.
    empty_snap = create_runtime_adg_snapshot(
        trace_id="",  # the pathological case
        mission="legacy-empty",
        started_at_utc=0,
        ended_at_utc=0,
        nodes=(),
        edges=(),
    )
    store.persist(empty_snap, allow_unbound=True, allow_empty_payload=True)

    # Simulate the "stale empty-key" pathology by writing directly to index.
    tidx_path = base / "_trace_index.json"
    current = json.loads(tidx_path.read_text(encoding="utf-8"))
    # Inject the lockout key that caused the bug.
    current[""] = "v_bogus"
    tidx_path.write_text(json.dumps(current), encoding="utf-8")

    return base


class TestBuildBackfill:
    def test_report_counts_are_sane(self, populated_store: Path) -> None:
        report = build_backfill(populated_store)
        assert report.scanned == 4  # 3 real + 1 empty
        assert report.empty_payload == 1

    def test_new_bindings_dict_contains_real_traces(self, populated_store: Path) -> None:
        # Wipe the trace_index before build to force fresh discovery.
        (populated_store / "_trace_index.json").write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        for i in range(3):
            assert f"real-trace-{i}" in report.new_bindings


class TestApplyBackfill:
    def test_apply_writes_real_trace_bindings(self, populated_store: Path) -> None:
        # Wipe trace_index to simulate total loss.
        (populated_store / "_trace_index.json").write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        result = apply_backfill(populated_store, report, archive_empty=True)
        assert result["new_bindings_written"] >= 3

        # After apply, trace_index must contain all 3 real trace IDs.
        recovered = json.loads((populated_store / "_trace_index.json").read_text(encoding="utf-8"))
        for i in range(3):
            assert f"real-trace-{i}" in recovered

    def test_apply_archives_empty_payloads(self, populated_store: Path) -> None:
        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=True)
        archive_dir = populated_store / "_archive_empty_payloads"
        assert archive_dir.exists()
        # At least 1 file archived (the one we seeded).
        archived = list(archive_dir.glob("*.json"))
        assert len(archived) >= 1

    def test_apply_strips_empty_string_keys(self, populated_store: Path) -> None:
        """After apply, no empty-string key should remain in trace_index."""
        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=True)
        recovered = json.loads((populated_store / "_trace_index.json").read_text(encoding="utf-8"))
        assert "" not in recovered

    def test_no_archive_preserves_empty_files(self, populated_store: Path) -> None:
        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=False)
        archive_dir = populated_store / "_archive_empty_payloads"
        assert not archive_dir.exists()
