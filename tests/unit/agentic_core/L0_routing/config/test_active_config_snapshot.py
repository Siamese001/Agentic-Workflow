from __future__ import annotations

import hashlib
import json
import socket
import subprocess
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.active_config_snapshot import (
    ACTIVE_CONFIG_SCHEMA_VERSION,
    ActiveConfigFailureReason,
    ActiveConfigSnapshotError,
    ActiveConfigSnapshotProviderV1,
    build_active_config_snapshot,
)
from ops_scripts.apps_rg.package_source_snapshots import publish_active_config_snapshot

COMPONENT_BYTES = {
    "budget": b"budget-bytes\n",
    "model": b"model-bytes\x00\n",
    "policy": b"policy-bytes\r\n",
    "routing": b"routing-bytes\n",
}


def _component_paths(tmp_path: Path) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name, payload in COMPONENT_BYTES.items():
        path = tmp_path / f"{name}.cfg"
        path.write_bytes(payload)
        paths[name] = path
    return paths


def _publish(tmp_path: Path):
    root = tmp_path / "active-config"
    receipt = publish_active_config_snapshot(
        component_paths=_component_paths(tmp_path),
        output_root=root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return root, receipt


def _rewrite_snapshot(root: Path, receipt, payload: bytes) -> None:
    receipt.snapshot_path.write_bytes(payload)
    pointer_path = root / "active.json"
    pointer = json.loads(pointer_path.read_bytes())
    pointer["snapshot_digest"] = hashlib.sha256(payload).hexdigest()
    pointer_path.write_bytes(
        json.dumps(pointer, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )


def test_build_is_deterministic_and_binds_exact_component_bytes() -> None:
    first, first_bytes = build_active_config_snapshot(
        dict(reversed(tuple(COMPONENT_BYTES.items()))),
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    second, second_bytes = build_active_config_snapshot(
        COMPONENT_BYTES,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )

    assert first_bytes == second_bytes
    assert first.configuration_digest == second.configuration_digest
    assert first.hashes() == {
        f"{name}_hash": hashlib.sha256(payload).hexdigest()
        for name, payload in COMPONENT_BYTES.items()
    }
    assert {component.name: component.exact_bytes() for component in first.components} == COMPONENT_BYTES


def test_provider_loads_once_and_hashes_perform_no_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _ = _publish(tmp_path)
    provider = ActiveConfigSnapshotProviderV1(
        snapshot_root=root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    snapshot = provider.load()
    expected = dict(snapshot.hashes())

    monkeypatch.setattr(Path, "read_bytes", lambda _self: (_ for _ in ()).throw(AssertionError("read")))
    assert provider.load() is snapshot
    assert dict(snapshot.hashes()) == expected


def test_provider_runtime_has_no_write_network_or_subprocess_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, _ = _publish(tmp_path)

    def _forbidden(*_args, **_kwargs):
        raise AssertionError("side effect attempted")

    monkeypatch.setattr(Path, "write_bytes", _forbidden)
    monkeypatch.setattr(Path, "write_text", _forbidden)
    monkeypatch.setattr(socket, "create_connection", _forbidden)
    monkeypatch.setattr(subprocess, "Popen", _forbidden)

    snapshot = ActiveConfigSnapshotProviderV1(
        snapshot_root=root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    ).load()
    assert snapshot.schema_version == ACTIVE_CONFIG_SCHEMA_VERSION


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("missing", ActiveConfigFailureReason.ACTIVE_CONFIG_MISSING),
        ("profile", ActiveConfigFailureReason.ACTIVE_CONFIG_PROFILE_MISMATCH),
        ("schema", ActiveConfigFailureReason.ACTIVE_CONFIG_VERSION_UNSUPPORTED),
        ("digest", ActiveConfigFailureReason.ACTIVE_CONFIG_DIGEST_MISMATCH),
        ("incomplete", ActiveConfigFailureReason.ACTIVE_CONFIG_INCOMPLETE),
    ],
)
def test_provider_fails_closed(
    tmp_path: Path,
    mutation: str,
    reason: ActiveConfigFailureReason,
) -> None:
    root, receipt = _publish(tmp_path)
    profile = "apps-rg-test"
    if mutation == "missing":
        (root / "active.json").unlink()
    elif mutation == "profile":
        profile = "another-profile"
    else:
        payload = json.loads(receipt.snapshot_path.read_bytes())
        if mutation == "schema":
            payload["schema_version"] = "active-config-snapshot/v999"
        elif mutation == "digest":
            payload["configuration_digest"] = "0" * 64
        elif mutation == "incomplete":
            payload["components"] = payload["components"][:-1]
        _rewrite_snapshot(
            root,
            receipt,
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"),
        )

    with pytest.raises(ActiveConfigSnapshotError) as caught:
        ActiveConfigSnapshotProviderV1(
            snapshot_root=root,
            selected_profile_id=profile,
            snapshot_boundary_id="run-001",
        ).load()
    assert caught.value.reason is reason


def test_provider_rejects_noncanonical_snapshot(tmp_path: Path) -> None:
    root, receipt = _publish(tmp_path)
    payload = json.loads(receipt.snapshot_path.read_bytes())
    _rewrite_snapshot(root, receipt, json.dumps(payload, indent=2).encode("utf-8"))

    with pytest.raises(ActiveConfigSnapshotError) as caught:
        ActiveConfigSnapshotProviderV1(
            snapshot_root=root,
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="run-001",
        ).load()
    assert caught.value.reason is ActiveConfigFailureReason.ACTIVE_CONFIG_NONCANONICAL


def test_post_load_environment_change_cannot_override_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, _ = _publish(tmp_path)
    snapshot = ActiveConfigSnapshotProviderV1(
        snapshot_root=root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    ).load()
    before = dict(snapshot.hashes())
    monkeypatch.setenv("APPS_RG_PROFILE", "mutated")
    monkeypatch.setenv("APPS_RG_POLICY_HASH", "0" * 64)
    assert dict(snapshot.hashes()) == before


def test_provider_rejects_boundary_mismatch(tmp_path: Path) -> None:
    root, _ = _publish(tmp_path)
    with pytest.raises(ActiveConfigSnapshotError) as caught:
        ActiveConfigSnapshotProviderV1(
            snapshot_root=root,
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="another-run",
        ).load()
    assert caught.value.reason is ActiveConfigFailureReason.ACTIVE_CONFIG_SOURCE_CHANGED


def test_provider_rejects_pointer_drift_during_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, _ = _publish(tmp_path)
    pointer_path = root / "active.json"
    original_read = Path.read_bytes
    pointer_reads = 0

    def _read_with_drift(path: Path) -> bytes:
        nonlocal pointer_reads
        payload = original_read(path)
        if path == pointer_path:
            pointer_reads += 1
            if pointer_reads == 2:
                return payload + b" "
        return payload

    monkeypatch.setattr(Path, "read_bytes", _read_with_drift)
    with pytest.raises(ActiveConfigSnapshotError) as caught:
        ActiveConfigSnapshotProviderV1(
            snapshot_root=root,
            selected_profile_id="apps-rg-test",
            snapshot_boundary_id="run-001",
        ).load()
    assert caught.value.reason is ActiveConfigFailureReason.ACTIVE_CONFIG_DRIFT_DURING_OPERATION
