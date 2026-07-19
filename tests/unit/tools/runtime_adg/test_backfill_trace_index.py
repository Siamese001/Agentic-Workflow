"""Tests for the back-fill script for runtime ADG trace-index repair."""

from __future__ import annotations

import hashlib
import json
import multiprocessing
from pathlib import Path

import pytest

from agentic_core.L6_system_learning.snapshot import (
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)
from agentic_core.L6_system_learning.store import FileBackedRuntimeADGStore, _deserialise_snapshot
from agentic_core.L6_system_learning.stores.version_store import FileBackedVersionStore
from tools.runtime_adg.backfill_trace_index import (
    apply_backfill,
    build_backfill,
    recover_version_index_only,
)


class _ProcessPayload:
    def __init__(self, raw: bytes) -> None:
        self._raw = raw

    def canonical_bytes(self) -> bytes:
        return self._raw


def _commit_while_recovery_holds_lock(
    base_dir: str,
    payload: bytes,
    ready,
    start,
    blocked,
) -> None:  # noqa: ANN001
    from agentic_core.L6_system_learning.stores import index_file_lock, version_store

    class _NullBridge:
        def persist_active_version(self, *_args, **_kwargs) -> None:
            return None

    version_store.get_sl_memory_bridge = lambda: _NullBridge()
    original_try_lock = index_file_lock._try_lock

    def _signaled_try_lock(descriptor: int) -> bool:
        acquired = original_try_lock(descriptor)
        if not acquired:
            blocked.set()
        return acquired

    index_file_lock._try_lock = _signaled_try_lock
    writer = version_store.FileBackedVersionStore(Path(base_dir))
    ready.set()
    if not start.wait(10.0):
        raise TimeoutError("parent did not start recovery/writer race")
    writer.commit_change_package(_ProcessPayload(payload))


def _persist_runtime_snapshot_while_recovery_holds_lock(
    base_dir: str,
    ready,
    start,
    blocked,
) -> None:  # noqa: ANN001
    from agentic_core.L6_system_learning.stores import index_file_lock, version_store

    class _NullBridge:
        def persist_active_version(self, *_args, **_kwargs) -> None:
            return None

    version_store.get_sl_memory_bridge = lambda: _NullBridge()
    original_try_lock = index_file_lock._try_lock

    def _signaled_try_lock(descriptor: int) -> bool:
        acquired = original_try_lock(descriptor)
        if not acquired:
            blocked.set()
        return acquired

    index_file_lock._try_lock = _signaled_try_lock
    FileBackedRuntimeADGStore._validate_l4_compliance = lambda self: None
    writer = FileBackedRuntimeADGStore(base_dir=Path(base_dir))
    snapshot = create_runtime_adg_snapshot(
        trace_id="overlapping-runtime-writer",
        mission="overlapping-runtime-writer",
        started_at_utc=70,
        ended_at_utc=71,
        nodes=(
            RuntimeADGNode(
                node_id="overlapping-runtime-writer",
                name="overlapping.runtime.writer",
                kind="t",
                layer="L2",
                component="C",
                started_at_utc=70,
                duration_ms=1.0,
                status="ok",
                attributes_json="{}",
            ),
        ),
        edges=(),
    )
    ready.set()
    if not start.wait(10.0):
        raise TimeoutError("parent did not start trace recovery/writer race")
    writer.persist(snapshot)


def _snapshot_from_shard(path: Path):  # noqa: ANN202
    metadata = json.loads(path.read_text(encoding="utf-8"))
    return _deserialise_snapshot(bytes.fromhex(metadata["payload_hex"]))


def _unbound_empty_shard(base_dir: Path) -> Path:
    return next(
        shard
        for shard in base_dir.glob("[0-9a-f][0-9a-f]/*.json")
        if not _snapshot_from_shard(shard).trace_id
        and not _snapshot_from_shard(shard).nodes
        and not _snapshot_from_shard(shard).edges
    )


def _persist_duplicate_trace(
    base_dir: Path,
    *,
    trace_id: str,
) -> tuple[tuple[str, str], tuple[str, str]]:
    """Persist two distinct snapshots sharing one trace ID."""
    store = FileBackedRuntimeADGStore(base_dir=base_dir)
    persisted: list[tuple[str, str]] = []
    for ordinal in range(2):
        node = RuntimeADGNode(
            node_id=f"duplicate-{ordinal}",
            name=f"duplicate.span.{ordinal}",
            kind="t",
            layer="L2",
            component="C",
            started_at_utc=ordinal + 10,
            duration_ms=1.0,
            status="ok",
            attributes_json="{}",
        )
        snapshot = create_runtime_adg_snapshot(
            trace_id=trace_id,
            mission=f"duplicate-mission-{ordinal}",
            started_at_utc=ordinal + 10,
            ended_at_utc=ordinal + 11,
            nodes=(node,),
            edges=(),
        )
        persisted.append((snapshot.snapshot_id, store.persist(snapshot)))
    return persisted[0], persisted[1]


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

    def test_missing_version_index_is_recovered_from_verified_shards(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        index_path.unlink()
        (populated_store / "_trace_index.json").write_text("{}", encoding="utf-8")

        first = build_backfill(populated_store)
        second = build_backfill(populated_store)

        assert first.recovered_version_index == second.recovered_version_index
        assert len(first.recovered_version_index) == 4
        assert all(
            version_id == f"v_{content_hash[:16]}"
            for version_id, content_hash in first.recovered_version_index.items()
        )
        for i in range(3):
            assert f"real-trace-{i}" in first.new_bindings
        assert not index_path.exists(), "dry-run planning must not materialize the recovered index"

    def test_missing_version_index_rejects_hash_divergent_shard_without_writes(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_before = trace_index_path.read_bytes()
        shard = next(populated_store.glob("[0-9a-f][0-9a-f]/*.json"))
        metadata = json.loads(shard.read_text(encoding="utf-8"))
        metadata["content_hash"] = "0" * 64
        shard.write_text(json.dumps(metadata), encoding="utf-8")

        with pytest.raises(ValueError, match="content_hash"):
            build_backfill(populated_store)

        assert not index_path.exists()
        assert trace_index_path.read_bytes() == trace_before

    def test_corrupt_present_version_index_fails_closed_without_writes(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.write_text("{not-json", encoding="utf-8")
        index_before = index_path.read_bytes()
        trace_before = trace_index_path.read_bytes()

        with pytest.raises(ValueError, match="malformed runtime ADG version index"):
            build_backfill(populated_store)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before

    @pytest.mark.parametrize(
        "corrupt_payload",
        ["{not-json", "[]", '{"trace-id": 7}'],
    )
    def test_corrupt_present_trace_index_fails_closed_without_writes(
        self,
        populated_store: Path,
        corrupt_payload: str,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text(corrupt_payload, encoding="utf-8")
        index_before = index_path.read_bytes()
        trace_before = trace_index_path.read_bytes()

        with pytest.raises(ValueError, match="malformed runtime ADG trace index"):
            build_backfill(populated_store)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before

    def test_semantically_noncanonical_shard_fails_closed_without_writes(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_before = trace_index_path.read_bytes()
        shard = next(populated_store.glob("[0-9a-f][0-9a-f]/*.json"))
        metadata = json.loads(shard.read_text(encoding="utf-8"))
        payload = bytes.fromhex(metadata["payload_hex"]) + b"\x1fignored-noncanonical-record"
        content_hash = hashlib.sha256(payload).hexdigest()
        metadata.update(
            {
                "version_id": f"v_{content_hash[:16]}",
                "content_hash": content_hash,
                "payload_hex": payload.hex(),
            }
        )
        replacement = populated_store / content_hash[:2] / f"{content_hash}.json"
        replacement.parent.mkdir(parents=True, exist_ok=True)
        replacement.write_text(json.dumps(metadata), encoding="utf-8")
        shard.unlink()

        with pytest.raises(ValueError, match="semantic verification failed"):
            build_backfill(populated_store)

        assert not index_path.exists()
        assert trace_index_path.read_bytes() == trace_before

    def test_valid_existing_mapping_is_authoritative_among_duplicate_traces(
        self,
        populated_store: Path,
    ) -> None:
        trace_id = "duplicate-authoritative-trace"
        (_first_snapshot_id, first_version), (_second_snapshot_id, _second_version) = (
            _persist_duplicate_trace(populated_store, trace_id=trace_id)
        )
        trace_index_path = populated_store / "_trace_index.json"
        trace_index = json.loads(trace_index_path.read_text(encoding="utf-8"))
        trace_index[trace_id] = first_version
        trace_index_path.write_text(json.dumps(trace_index, sort_keys=True), encoding="utf-8")

        report = build_backfill(populated_store)

        assert report.authoritative_trace_bindings[trace_id] == first_version
        assert trace_id not in report.new_bindings
        assert report.trace_conflict_count == 0

        apply_backfill(populated_store, report, archive_empty=False)
        applied = json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert applied[trace_id] == first_version

    def test_ambiguous_duplicate_trace_is_reported_and_left_unbound(
        self,
        populated_store: Path,
    ) -> None:
        trace_id = "duplicate-ambiguous-trace"
        (first_snapshot_id, first_version), (second_snapshot_id, second_version) = _persist_duplicate_trace(
            populated_store, trace_id=trace_id
        )
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")

        report = build_backfill(populated_store)

        assert report.trace_conflict_count == 1
        assert report.trace_conflicts == {trace_id: tuple(sorted((first_version, second_version)))}
        assert trace_id not in report.new_bindings
        assert report.new_bindings[first_snapshot_id] == first_version
        assert report.new_bindings[second_snapshot_id] == second_version

        index_before = (populated_store / "_index.json").read_bytes()
        trace_before = trace_index_path.read_bytes()
        with pytest.raises(ValueError, match="unresolved trace conflicts"):
            apply_backfill(populated_store, report, archive_empty=False)

        assert (populated_store / "_index.json").read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before

    def test_trace_less_snapshot_identity_is_recovered(
        self,
        populated_store: Path,
    ) -> None:
        store = FileBackedRuntimeADGStore(base_dir=populated_store)
        snapshot = create_runtime_adg_snapshot(
            trace_id="",
            mission="unbound-but-nonempty",
            started_at_utc=20,
            ended_at_utc=21,
            nodes=(
                RuntimeADGNode(
                    node_id="unbound-but-nonempty",
                    name="unbound.but.nonempty",
                    kind="t",
                    layer="L2",
                    component="C",
                    started_at_utc=20,
                    duration_ms=1.0,
                    status="ok",
                    attributes_json="{}",
                ),
            ),
            edges=(),
        )
        version_id = store.persist(snapshot, allow_unbound=True)
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")

        report = build_backfill(populated_store)

        assert report.new_bindings[snapshot.snapshot_id] == version_id

    def test_indexed_corrupt_shard_fails_closed_without_writes(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        shard = next(populated_store.glob("[0-9a-f][0-9a-f]/*.json"))
        metadata = json.loads(shard.read_text(encoding="utf-8"))
        metadata["payload_hex"] = "00"
        shard.write_text(json.dumps(metadata), encoding="utf-8")
        index_before = index_path.read_bytes()
        trace_before = trace_index_path.read_bytes()

        with pytest.raises(ValueError, match="content_hash payload mismatch"):
            build_backfill(populated_store)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before

    def test_valid_shard_missing_from_present_index_fails_closed(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index = json.loads(index_path.read_text(encoding="utf-8"))
        index.pop(next(iter(index)))
        index_path.write_text(json.dumps(index, sort_keys=True), encoding="utf-8")
        index_before = index_path.read_bytes()
        trace_before = trace_index_path.read_bytes()

        with pytest.raises(ValueError, match="not represented by _index.json"):
            build_backfill(populated_store)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before


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
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        source = _unbound_empty_shard(populated_store)
        source_before = source.read_bytes()
        index_before = index_path.read_bytes()
        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=True)
        archive_dir = populated_store / "_archive_empty_payloads"
        assert archive_dir.exists()
        archived = archive_dir / source.name
        assert archived.read_bytes() == source_before
        assert hashlib.sha256(archived.read_bytes()).digest() == hashlib.sha256(source_before).digest()
        assert source.read_bytes() == source_before, "trace repair must not destructively clean shards"
        assert index_path.read_bytes() == index_before
        recovered_trace = json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert "" not in recovered_trace

    def test_archive_preserves_traced_empty_snapshot_and_indexes(
        self,
        populated_store: Path,
    ) -> None:
        store = FileBackedRuntimeADGStore(base_dir=populated_store)
        traced_empty = create_runtime_adg_snapshot(
            trace_id="traced-empty",
            mission="valid-traced-empty",
            started_at_utc=1,
            ended_at_utc=1,
            nodes=(),
            edges=(),
        )
        version_id = store.persist(traced_empty, allow_empty_payload=True)
        source = populated_store / traced_empty.snapshot_hash[:2] / f"{traced_empty.snapshot_hash}.json"
        source_before = source.read_bytes()

        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=True)

        assert source.read_bytes() == source_before
        assert not (populated_store / "_archive_empty_payloads" / source.name).exists()
        assert (
            json.loads((populated_store / "_index.json").read_text(encoding="utf-8"))[version_id]
            == traced_empty.snapshot_hash
        )
        assert (
            json.loads((populated_store / "_trace_index.json").read_text(encoding="utf-8"))["traced-empty"]
            == version_id
        )

    def test_existing_archive_destination_is_replay_safe(
        self,
        populated_store: Path,
    ) -> None:
        report = build_backfill(populated_store)
        empty_source = _unbound_empty_shard(populated_store)
        archive_dir = populated_store / "_archive_empty_payloads"
        archive_dir.mkdir()
        destination = archive_dir / empty_source.name
        destination.write_bytes(empty_source.read_bytes())
        source_before = empty_source.read_bytes()

        result = apply_backfill(populated_store, report, archive_empty=True)

        assert result["empty_payloads_archived"] == 1
        assert empty_source.read_bytes() == source_before
        assert destination.read_bytes() == source_before

    def test_existing_archive_destination_mismatch_fails_without_removal(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        index_path.unlink()
        report = build_backfill(populated_store)
        empty_source = _unbound_empty_shard(populated_store)
        archive_dir = populated_store / "_archive_empty_payloads"
        archive_dir.mkdir()
        destination = archive_dir / empty_source.name
        source_before = empty_source.read_bytes()
        mismatched = bytearray(source_before)
        mismatched[-1] ^= 1
        destination.write_bytes(mismatched)
        trace_before = (populated_store / "_trace_index.json").read_bytes()

        with pytest.raises(ValueError, match="archive destination differs"):
            apply_backfill(populated_store, report, archive_empty=True)

        assert empty_source.read_bytes() == source_before
        assert destination.read_bytes() == bytes(mismatched)
        assert not index_path.exists()
        assert (populated_store / "_trace_index.json").read_bytes() == trace_before

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

    def test_apply_atomically_materializes_recovered_version_index(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)

        result = apply_backfill(populated_store, report, archive_empty=False)

        recovered_index = json.loads(index_path.read_text(encoding="utf-8"))
        recovered_trace_index = json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert recovered_index == report.recovered_version_index
        assert result["version_index_entries_recovered"] == 4
        for i in range(3):
            assert f"real-trace-{i}" in recovered_trace_index
        assert not list(populated_store.glob("_index.json.*.tmp"))
        assert not list(populated_store.glob("_trace_index.json.*.tmp"))

    def test_version_index_only_recovery_preserves_ambiguous_trace_unbound(
        self,
        populated_store: Path,
    ) -> None:
        trace_id = "ambiguous-version-recovery"
        _persist_duplicate_trace(populated_store, trace_id=trace_id)
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        assert report.trace_conflicts == {
            trace_id: report.trace_conflicts[trace_id],
        }
        trace_before = trace_index_path.read_bytes()

        result = recover_version_index_only(populated_store, report)

        assert result["version_index_entries_recovered"] == len(report.recovered_version_index or {})
        assert json.loads(index_path.read_text(encoding="utf-8")) == report.recovered_version_index
        assert trace_index_path.read_bytes() == trace_before
        assert trace_id not in json.loads(trace_index_path.read_text(encoding="utf-8"))

    def test_version_index_only_receipts_preserved_invalid_trace_binding(
        self,
        populated_store: Path,
    ) -> None:
        trace_id = "ambiguous-stale-binding"
        _persist_duplicate_trace(populated_store, trace_id=trace_id)
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        stale_version = "v_" + "f" * 16
        trace_index_path.write_text(
            json.dumps({trace_id: stale_version}, sort_keys=True),
            encoding="utf-8",
        )
        report = build_backfill(populated_store)
        assert report.trace_bindings_to_remove == (trace_id,)

        result = recover_version_index_only(populated_store, report)

        assert result["trace_conflicts_left_unbound"] == 0
        assert result["trace_conflicts_with_existing_binding"] == 1
        assert json.loads(trace_index_path.read_text(encoding="utf-8")) == {trace_id: stale_version}

    def test_preinitialized_version_writer_merges_after_index_recovery(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        index_path.unlink()
        stale_writer = FileBackedVersionStore(populated_store)
        report = build_backfill(populated_store)
        expected = dict(report.recovered_version_index or {})
        recover_version_index_only(populated_store, report)

        snapshot = create_runtime_adg_snapshot(
            trace_id="writer-after-recovery",
            mission="writer-after-recovery",
            started_at_utc=50,
            ended_at_utc=51,
            nodes=(
                RuntimeADGNode(
                    node_id="writer-after-recovery",
                    name="writer.after.recovery",
                    kind="t",
                    layer="L2",
                    component="C",
                    started_at_utc=50,
                    duration_ms=1.0,
                    status="ok",
                    attributes_json="{}",
                ),
            ),
            edges=(),
        )
        version_id = stale_writer.commit_change_package(snapshot)

        observed = json.loads(index_path.read_text(encoding="utf-8"))
        assert observed.items() >= expected.items()
        assert observed[version_id] == snapshot.snapshot_hash

    def test_live_writer_waits_for_recovery_then_merges_complete_index(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        index_path = populated_store / "_index.json"
        index_path.unlink()
        report = build_backfill(populated_store)
        expected = dict(report.recovered_version_index or {})
        context = multiprocessing.get_context("spawn")
        ready = context.Event()
        start = context.Event()
        blocked = context.Event()
        payload = b"live-writer-during-version-recovery"
        process = context.Process(
            target=_commit_while_recovery_holds_lock,
            args=(str(populated_store), payload, ready, start, blocked),
        )
        process.start()
        assert ready.wait(10.0)
        original_publish = backfill._atomic_publish_json_if_absent

        def _publish_after_writer_attempt(path: Path, mapping: dict[str, str]) -> None:
            start.set()
            assert blocked.wait(10.0), "writer never observed recovery's shared lock"
            original_publish(path, mapping)

        monkeypatch.setattr(backfill, "_atomic_publish_json_if_absent", _publish_after_writer_attempt)
        try:
            recover_version_index_only(populated_store, report)
            process.join(15.0)
        finally:
            start.set()
            if process.is_alive():
                process.terminate()
                process.join(5.0)
        assert process.exitcode == 0

        observed = json.loads(index_path.read_text(encoding="utf-8"))
        content_hash = hashlib.sha256(payload).hexdigest()
        assert observed.items() >= expected.items()
        assert observed[f"v_{content_hash[:16]}"] == content_hash

    def test_preinitialized_runtime_writer_merges_after_trace_recovery(
        self,
        populated_store: Path,
    ) -> None:
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")
        stale_writer = FileBackedRuntimeADGStore(base_dir=populated_store)
        report = build_backfill(populated_store)
        apply_backfill(populated_store, report, archive_empty=False)
        expected = json.loads(trace_index_path.read_text(encoding="utf-8"))

        node = RuntimeADGNode(
            node_id="writer-after-trace-recovery",
            name="writer.after.trace.recovery",
            kind="t",
            layer="L2",
            component="C",
            started_at_utc=60,
            duration_ms=1.0,
            status="ok",
            attributes_json="{}",
        )
        snapshot = create_runtime_adg_snapshot(
            trace_id="writer-after-trace-recovery",
            mission="writer-after-trace-recovery",
            started_at_utc=60,
            ended_at_utc=61,
            nodes=(node,),
            edges=(),
        )
        version_id = stale_writer.persist(snapshot)

        observed = json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert observed.items() >= expected.items()
        assert observed[snapshot.trace_id] == version_id
        assert observed[snapshot.snapshot_id] == version_id

    def test_live_runtime_writer_waits_for_trace_recovery_then_merges(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        context = multiprocessing.get_context("spawn")
        ready = context.Event()
        start = context.Event()
        blocked = context.Event()
        process = context.Process(
            target=_persist_runtime_snapshot_while_recovery_holds_lock,
            args=(str(populated_store), ready, start, blocked),
        )
        process.start()
        assert ready.wait(10.0)
        original_write = backfill.atomic_write_json_mapping

        def _write_after_writer_attempt(path: Path, mapping: dict[str, str]) -> None:
            if path == trace_index_path:
                start.set()
                assert blocked.wait(10.0), "writer never observed recovery's shared lock"
            original_write(path, mapping)

        monkeypatch.setattr(backfill, "atomic_write_json_mapping", _write_after_writer_attempt)
        try:
            apply_backfill(populated_store, report, archive_empty=False)
            recovered = json.loads(trace_index_path.read_text(encoding="utf-8"))
            process.join(15.0)
        finally:
            start.set()
            if process.is_alive():
                process.terminate()
                process.join(5.0)
        assert process.exitcode == 0

        observed = json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert observed.items() >= recovered.items()
        assert "overlapping-runtime-writer" in observed

    def test_apply_revalidates_shards_and_writes_nothing_after_plan_drift(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_before = trace_index_path.read_bytes()
        report = build_backfill(populated_store)
        shard = next(populated_store.glob("[0-9a-f][0-9a-f]/*.json"))
        metadata = json.loads(shard.read_text(encoding="utf-8"))
        metadata["version_id"] = "v_divergent"
        shard.write_text(json.dumps(metadata), encoding="utf-8")

        with pytest.raises(ValueError, match="version_id"):
            apply_backfill(populated_store, report, archive_empty=False)

        assert not index_path.exists()
        assert trace_index_path.read_bytes() == trace_before

    def test_recovered_index_publication_never_replaces_live_writer_index(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        index_path.unlink()
        trace_before = trace_index_path.read_bytes()
        report = build_backfill(populated_store)
        competing_bytes = json.dumps(
            report.recovered_version_index,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        original_link = backfill.os.link

        def _racing_link(source: str | bytes, destination: str | bytes, *args, **kwargs) -> None:
            index_path.write_bytes(competing_bytes)
            original_link(source, destination, *args, **kwargs)

        monkeypatch.setattr(backfill.os, "link", _racing_link)

        with pytest.raises(FileExistsError):
            apply_backfill(populated_store, report, archive_empty=False)

        assert index_path.read_bytes() == competing_bytes
        assert trace_index_path.read_bytes() == trace_before

    def test_apply_rejects_post_plan_trace_index_drift_without_writes(
        self,
        populated_store: Path,
    ) -> None:
        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        planned_version = report.new_bindings["real-trace-0"]
        trace_index_path.write_text(
            json.dumps({"real-trace-0": planned_version}, sort_keys=True),
            encoding="utf-8",
        )
        index_before = index_path.read_bytes()
        trace_before = trace_index_path.read_bytes()

        with pytest.raises(ValueError, match="trace index changed after backfill planning"):
            apply_backfill(populated_store, report, archive_empty=False)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == trace_before

    def test_apply_rejects_trace_drift_during_revalidation_without_own_writes(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        index_path = populated_store / "_index.json"
        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        index_before = index_path.read_bytes()
        planned_version = report.new_bindings["real-trace-0"]
        drifted_trace = json.dumps(
            {"external-trace": planned_version},
            sort_keys=True,
        ).encode("utf-8")
        original_read = backfill._read_trace_index
        read_count = 0

        def _drifting_read(base_dir: Path) -> dict[str, str]:
            nonlocal read_count
            read_count += 1
            if read_count == 2:
                trace_index_path.write_bytes(drifted_trace)
            return original_read(base_dir)

        monkeypatch.setattr(backfill, "_read_trace_index", _drifting_read)

        with pytest.raises(ValueError, match="trace index changed during backfill revalidation"):
            apply_backfill(populated_store, report, archive_empty=False)

        assert index_path.read_bytes() == index_before
        assert trace_index_path.read_bytes() == drifted_trace

    def test_trace_publication_never_replaces_live_writer_update(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        trace_index_path = populated_store / "_trace_index.json"
        trace_index_path.write_text("{}", encoding="utf-8")
        report = build_backfill(populated_store)
        original_write = backfill.atomic_write_json_mapping
        observed_present = False

        def _observing_write(path: Path, payload: dict[str, str]) -> None:
            nonlocal observed_present
            if path == trace_index_path:
                observed_present = path.exists()
            original_write(path, payload)

        monkeypatch.setattr(backfill, "atomic_write_json_mapping", _observing_write)

        apply_backfill(populated_store, report, archive_empty=False)

        assert observed_present, "repair must not rename the canonical trace index away"
        assert "real-trace-0" in json.loads(trace_index_path.read_text(encoding="utf-8"))
        assert not list(populated_store.glob("_trace_index.json.*.tmp"))

    def test_apply_rejects_lock_contention(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from contextlib import contextmanager

        from agentic_core.L6_system_learning.stores.index_file_lock import runtime_adg_index_lock
        from tools.runtime_adg import backfill_trace_index as backfill

        report = build_backfill(populated_store)

        @contextmanager
        def _short_timeout_lock(base_dir: Path):  # noqa: ANN202
            with runtime_adg_index_lock(base_dir, timeout_seconds=0.01):
                yield

        monkeypatch.setattr(backfill, "runtime_adg_index_lock", _short_timeout_lock)
        with runtime_adg_index_lock(populated_store):
            with pytest.raises(ValueError, match="timed out acquiring runtime ADG index lock"):
                apply_backfill(populated_store, report, archive_empty=False)

    def test_apply_releases_lock_after_publication_error(
        self,
        populated_store: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tools.runtime_adg import backfill_trace_index as backfill

        report = build_backfill(populated_store)

        def _fail_publication(*_args, **_kwargs) -> None:
            raise OSError("injected publication failure")

        monkeypatch.setattr(backfill, "_atomic_replace_trace_index_if_unchanged", _fail_publication)

        with pytest.raises(OSError, match="injected publication failure"):
            apply_backfill(populated_store, report, archive_empty=False)

        from agentic_core.L6_system_learning.stores.index_file_lock import runtime_adg_index_lock

        with runtime_adg_index_lock(populated_store, timeout_seconds=0.1):
            pass
        assert (populated_store / "_runtime_adg_indexes.lock").exists()
