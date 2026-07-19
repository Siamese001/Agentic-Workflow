from __future__ import annotations

import hashlib
import json
import socket
import subprocess
from pathlib import Path

import pytest

from agentic_core.L2_execution.config.ingestion_snapshot import (
    INGESTION_BUILDER_VERSION,
    INGESTION_SNAPSHOT_SCHEMA_VERSION,
    IngestionLoadRequestV1,
    IngestionSnapshotError,
    IngestionSnapshotFailureReason,
    IngestionSnapshotLoaderV1,
)
from ops_scripts.apps_rg.package_source_snapshots import (
    SnapshotPublicationError,
    publish_active_config_snapshot,
    publish_ingestion_snapshot,
)

CANONICAL_PAYLOAD = b'{"chunks":[{"metadata":{"source":"fixture"},"text":"Exact payload text"}]}'


def _active_config(tmp_path: Path) -> Path:
    components: dict[str, Path] = {}
    for name in ("budget", "model", "policy", "routing"):
        path = tmp_path / f"{name}.cfg"
        path.write_bytes(f"{name}-bytes\n".encode("ascii"))
        components[name] = path
    root = tmp_path / "active-config"
    publish_active_config_snapshot(
        component_paths=components,
        output_root=root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return root


def _publish(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload_path = tmp_path / "payload.json"
    payload_path.write_bytes(CANONICAL_PAYLOAD)
    root = tmp_path / "ingestion"
    receipt = publish_ingestion_snapshot(
        payload_path=payload_path,
        output_root=root,
        input_schema_version="chunks/v1",
        active_config_root=_active_config(tmp_path),
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return root, receipt


def _request(root: Path, receipt, **overrides) -> IngestionLoadRequestV1:
    values = {
        "snapshot_root": root,
        "expected_input_digest": hashlib.sha256(CANONICAL_PAYLOAD).hexdigest(),
        "expected_configuration_digest": receipt.configuration_digest,
        "expected_input_schema_version": "chunks/v1",
        "expected_snapshot_schema_version": INGESTION_SNAPSHOT_SCHEMA_VERSION,
        "expected_builder_version": INGESTION_BUILDER_VERSION,
        "expected_generation_id": receipt.generation_id,
    }
    values.update(overrides)
    return IngestionLoadRequestV1(**values)


def test_runtime_loader_preserves_exact_payload_and_makes_no_writes(tmp_path: Path) -> None:
    root, receipt = _publish(tmp_path)
    before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    snapshot = IngestionSnapshotLoaderV1().load(_request(root, receipt))
    after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}

    assert snapshot.canonical_payload_bytes == CANONICAL_PAYLOAD
    assert snapshot.payload["chunks"][0]["text"] == "Exact payload text"
    assert after == before


def test_runtime_loader_has_no_network_provider_or_subprocess_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, receipt = _publish(tmp_path)

    def _forbidden(*_args, **_kwargs):
        raise AssertionError("side effect attempted")

    monkeypatch.setattr(Path, "write_bytes", _forbidden)
    monkeypatch.setattr(Path, "write_text", _forbidden)
    monkeypatch.setattr(socket, "create_connection", _forbidden)
    monkeypatch.setattr(subprocess, "Popen", _forbidden)
    assert IngestionSnapshotLoaderV1().load(_request(root, receipt)).payload_digest


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"expected_input_digest": "0" * 64}, IngestionSnapshotFailureReason.INPUT_DIGEST_MISMATCH),
        ({"expected_configuration_digest": "0" * 64}, IngestionSnapshotFailureReason.CONFIG_DIGEST_MISMATCH),
        ({"expected_input_schema_version": "chunks/v2"}, IngestionSnapshotFailureReason.SCHEMA_VERSION_MISMATCH),
        (
            {"expected_snapshot_schema_version": "ingestion-snapshot/v2"},
            IngestionSnapshotFailureReason.SCHEMA_VERSION_MISMATCH,
        ),
        ({"expected_builder_version": "builder/v2"}, IngestionSnapshotFailureReason.BUILDER_VERSION_MISMATCH),
        ({"expected_generation_id": "stale"}, IngestionSnapshotFailureReason.SNAPSHOT_STALE),
    ],
)
def test_runtime_loader_rejects_mismatched_expectations(
    tmp_path: Path,
    overrides: dict[str, str],
    reason: IngestionSnapshotFailureReason,
) -> None:
    root, receipt = _publish(tmp_path)
    with pytest.raises(IngestionSnapshotError) as caught:
        IngestionSnapshotLoaderV1().load(_request(root, receipt, **overrides))
    assert caught.value.reason is reason


def test_runtime_loader_rejects_missing_and_partial_publication(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(IngestionSnapshotError) as caught:
        IngestionSnapshotLoaderV1().load(
            IngestionLoadRequestV1(
                snapshot_root=missing,
                expected_input_digest="0" * 64,
                expected_configuration_digest="0" * 64,
                expected_input_schema_version="chunks/v1",
            )
        )
    assert caught.value.reason is IngestionSnapshotFailureReason.SNAPSHOT_MISSING

    root, receipt = _publish(tmp_path)
    receipt.snapshot_path.unlink()
    with pytest.raises(IngestionSnapshotError) as caught:
        IngestionSnapshotLoaderV1().load(_request(root, receipt))
    assert caught.value.reason is IngestionSnapshotFailureReason.SNAPSHOT_PUBLICATION_INCOMPLETE


def test_runtime_loader_rejects_malformed_snapshot_and_stale_pointer(tmp_path: Path) -> None:
    root, receipt = _publish(tmp_path)
    malformed = b"not-json"
    receipt.snapshot_path.write_bytes(malformed)
    pointer_path = root / "active.json"
    pointer = json.loads(pointer_path.read_bytes())
    pointer["snapshot_digest"] = hashlib.sha256(malformed).hexdigest()
    pointer_path.write_bytes(
        json.dumps(pointer, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )
    with pytest.raises(IngestionSnapshotError) as caught:
        IngestionSnapshotLoaderV1().load(_request(root, receipt))
    assert caught.value.reason is IngestionSnapshotFailureReason.SNAPSHOT_MALFORMED

    root, receipt = _publish(tmp_path / "stale-case")
    pointer_path = root / "active.json"
    pointer = json.loads(pointer_path.read_bytes())
    pointer["state"] = "STALE"
    pointer_path.write_bytes(
        json.dumps(pointer, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )
    with pytest.raises(IngestionSnapshotError) as caught:
        IngestionSnapshotLoaderV1().load(_request(root, receipt))
    assert caught.value.reason is IngestionSnapshotFailureReason.SNAPSHOT_STALE


def test_offline_publish_is_deterministic_pointer_last_and_lock_guarded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ops_scripts.apps_rg.package_source_snapshots as packager

    destinations: list[Path] = []
    original_replace = packager.os.replace

    def _record_replace(source, destination):
        destinations.append(Path(destination))
        return original_replace(source, destination)

    monkeypatch.setattr(packager.os, "replace", _record_replace)
    root, first = _publish(tmp_path)
    assert destinations[-1] == root / "active.json"

    payload_path = tmp_path / "payload.json"
    second = publish_ingestion_snapshot(
        payload_path=payload_path,
        output_root=root,
        input_schema_version="chunks/v1",
        active_config_root=tmp_path / "active-config",
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    assert second.generation_id == first.generation_id
    assert second.snapshot_path.read_bytes() == first.snapshot_path.read_bytes()

    (root / ".publish.lock").write_text("held", encoding="ascii")
    with pytest.raises(SnapshotPublicationError):
        publish_ingestion_snapshot(
            payload_path=payload_path,
            output_root=root,
            input_schema_version="chunks/v1",
            active_config_root=tmp_path / "active-config",
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="run-001",
        )


def test_offline_publish_rechecks_payload_before_activation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ops_scripts.apps_rg.package_source_snapshots as packager

    tmp_path.mkdir(parents=True, exist_ok=True)
    payload_path = tmp_path / "payload.json"
    payload_path.write_bytes(CANONICAL_PAYLOAD)
    config_root = _active_config(tmp_path)
    original_read = packager._read_exact_bytes
    payload_reads = 0

    def _read_with_drift(path: Path) -> bytes:
        nonlocal payload_reads
        payload = original_read(path)
        if Path(path) == payload_path:
            payload_reads += 1
            if payload_reads == 2:
                return payload + b" "
        return payload

    monkeypatch.setattr(packager, "_read_exact_bytes", _read_with_drift)
    output_root = tmp_path / "ingestion"
    with pytest.raises(SnapshotPublicationError, match="payload changed"):
        publish_ingestion_snapshot(
            payload_path=payload_path,
            output_root=output_root,
            input_schema_version="chunks/v1",
            active_config_root=config_root,
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="run-001",
        )
    assert not (output_root / "active.json").exists()


def test_failed_pointer_publication_preserves_previous_active_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ops_scripts.apps_rg.package_source_snapshots as packager

    root, _ = _publish(tmp_path)
    pointer_path = root / "active.json"
    previous_pointer = pointer_path.read_bytes()
    payload_path = tmp_path / "payload.json"
    payload_path.write_bytes(b'{"chunks":[{"metadata":{},"text":"second generation"}]}')
    original_replace = packager.os.replace

    def _fail_pointer_replace(source, destination):
        if Path(destination) == pointer_path:
            raise OSError("simulated pointer failure")
        return original_replace(source, destination)

    monkeypatch.setattr(packager.os, "replace", _fail_pointer_replace)
    with pytest.raises(OSError, match="simulated pointer failure"):
        publish_ingestion_snapshot(
            payload_path=payload_path,
            output_root=root,
            input_schema_version="chunks/v1",
            active_config_root=tmp_path / "active-config",
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="run-001",
        )
    assert pointer_path.read_bytes() == previous_pointer
    assert not (root / ".publish.lock").exists()
