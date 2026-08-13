"""Explicit offline packagers for the two Apps RG source snapshots."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from agentic_core.L0_routing.config.active_config_snapshot import (
    ActiveConfigSnapshotProviderV1,
    build_active_config_snapshot,
    canonical_json_bytes,
    sha256_bytes,
)
from agentic_core.L2_execution.config.ingestion_snapshot import build_ingestion_snapshot


class SnapshotPublicationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SnapshotPublicationReceipt:
    generation_id: str
    snapshot_path: Path
    pointer_path: Path
    snapshot_digest: str
    input_digest: str = ""
    configuration_digest: str = ""


def _read_exact_bytes(path: Path) -> bytes:
    return Path(path).read_bytes()


def _write_new_file(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _cleanup_staging(staging_dir: Path) -> None:
    snapshot_path = staging_dir / "snapshot.json"
    if snapshot_path.exists():
        snapshot_path.unlink()
    if staging_dir.exists():
        staging_dir.rmdir()


def _publish_snapshot(
    *,
    output_root: Path,
    generation_id: str,
    snapshot_bytes: bytes,
    recheck_sources: Callable[[], None],
) -> SnapshotPublicationReceipt:
    root = Path(output_root)
    generations = root / "generations"
    root.mkdir(parents=True, exist_ok=True)
    generations.mkdir(parents=True, exist_ok=True)
    lock_path = root / ".publish.lock"
    try:
        lock_handle = lock_path.open("x", encoding="ascii")
    except FileExistsError as exc:
        raise SnapshotPublicationError("publication already in progress") from exc

    staging_dir = generations / f".{generation_id}.{uuid.uuid4().hex}.staging"
    pointer_temp = root / f".active.{uuid.uuid4().hex}.tmp"
    final_dir = generations / generation_id
    final_snapshot = final_dir / "snapshot.json"
    try:
        lock_handle.write(generation_id)
        lock_handle.flush()
        os.fsync(lock_handle.fileno())
        staging_dir.mkdir()
        staged_snapshot = staging_dir / "snapshot.json"
        _write_new_file(staged_snapshot, snapshot_bytes)
        if staged_snapshot.read_bytes() != snapshot_bytes:
            raise SnapshotPublicationError("staged snapshot validation failed")

        recheck_sources()

        if final_dir.exists():
            if not final_snapshot.is_file() or final_snapshot.read_bytes() != snapshot_bytes:
                raise SnapshotPublicationError("immutable generation already exists with different bytes")
            _cleanup_staging(staging_dir)
        else:
            os.replace(staging_dir, final_dir)

        pointer_payload = canonical_json_bytes(
            {
                "generation_id": generation_id,
                "schema_version": "snapshot-pointer/v1",
                "snapshot_digest": sha256_bytes(snapshot_bytes),
                "snapshot_path": final_snapshot.relative_to(root).as_posix(),
                "state": "ACTIVE",
            }
        )
        _write_new_file(pointer_temp, pointer_payload)
        os.replace(pointer_temp, root / "active.json")
        return SnapshotPublicationReceipt(
            generation_id=generation_id,
            snapshot_path=final_snapshot,
            pointer_path=root / "active.json",
            snapshot_digest=sha256_bytes(snapshot_bytes),
        )
    finally:
        lock_handle.close()
        if pointer_temp.exists():
            pointer_temp.unlink()
        _cleanup_staging(staging_dir)
        if lock_path.exists():
            lock_path.unlink()


def publish_active_config_snapshot(
    *,
    component_paths: Mapping[str, Path],
    output_root: Path,
    selected_profile_id: str,
    snapshot_boundary_id: str,
) -> SnapshotPublicationReceipt:
    source_bytes = {name: _read_exact_bytes(Path(path)) for name, path in component_paths.items()}
    snapshot, snapshot_bytes = build_active_config_snapshot(
        source_bytes,
        selected_profile_id=selected_profile_id,
        snapshot_boundary_id=snapshot_boundary_id,
    )

    def _recheck() -> None:
        for name, source_path in component_paths.items():
            if _read_exact_bytes(Path(source_path)) != source_bytes[name]:
                raise SnapshotPublicationError(f"active configuration source changed: {name}")

    receipt = _publish_snapshot(
        output_root=output_root,
        generation_id=snapshot.snapshot_id,
        snapshot_bytes=snapshot_bytes,
        recheck_sources=_recheck,
    )
    return SnapshotPublicationReceipt(
        generation_id=receipt.generation_id,
        snapshot_path=receipt.snapshot_path,
        pointer_path=receipt.pointer_path,
        snapshot_digest=receipt.snapshot_digest,
        configuration_digest=snapshot.configuration_digest,
    )


def publish_ingestion_snapshot(
    *,
    payload_path: Path,
    output_root: Path,
    input_schema_version: str,
    active_config_root: Path,
    selected_profile_id: str,
    snapshot_boundary_id: str,
) -> SnapshotPublicationReceipt:
    canonical_payload = _read_exact_bytes(Path(payload_path))
    provider = ActiveConfigSnapshotProviderV1(
        snapshot_root=Path(active_config_root),
        selected_profile_id=selected_profile_id,
        snapshot_boundary_id=snapshot_boundary_id,
    )
    active_config = provider.load()
    snapshot, snapshot_bytes = build_ingestion_snapshot(
        canonical_payload,
        input_schema_version=input_schema_version,
        active_configuration_digest=active_config.configuration_digest,
    )

    def _recheck() -> None:
        if _read_exact_bytes(Path(payload_path)) != canonical_payload:
            raise SnapshotPublicationError("ingestion payload changed before activation")
        current_config = ActiveConfigSnapshotProviderV1(
            snapshot_root=Path(active_config_root),
            selected_profile_id=selected_profile_id,
            snapshot_boundary_id=snapshot_boundary_id,
        ).load()
        if (
            current_config.snapshot_id != active_config.snapshot_id
            or current_config.configuration_digest != active_config.configuration_digest
        ):
            raise SnapshotPublicationError("active configuration changed before activation")

    receipt = _publish_snapshot(
        output_root=output_root,
        generation_id=snapshot.generation_id,
        snapshot_bytes=snapshot_bytes,
        recheck_sources=_recheck,
    )
    return SnapshotPublicationReceipt(
        generation_id=receipt.generation_id,
        snapshot_path=receipt.snapshot_path,
        pointer_path=receipt.pointer_path,
        snapshot_digest=receipt.snapshot_digest,
        input_digest=snapshot.input_digest,
        configuration_digest=snapshot.active_configuration_digest,
    )


def _parse_component(values: Sequence[str]) -> dict[str, Path]:
    components: dict[str, Path] = {}
    for value in values:
        name, separator, raw_path = value.partition("=")
        if not separator or not name or not raw_path or name in components:
            raise SnapshotPublicationError(f"invalid component declaration: {value!r}")
        components[name] = Path(raw_path)
    return components


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    config = subparsers.add_parser("active-config")
    config.add_argument("--component", action="append", required=True)
    config.add_argument("--output-root", type=Path, required=True)
    config.add_argument("--profile-id", required=True)
    config.add_argument("--boundary-id", required=True)

    ingestion = subparsers.add_parser("ingestion")
    ingestion.add_argument("--payload", type=Path, required=True)
    ingestion.add_argument("--output-root", type=Path, required=True)
    ingestion.add_argument("--input-schema-version", required=True)
    ingestion.add_argument("--active-config-root", type=Path, required=True)
    ingestion.add_argument("--profile-id", required=True)
    ingestion.add_argument("--boundary-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "active-config":
        receipt = publish_active_config_snapshot(
            component_paths=_parse_component(args.component),
            output_root=args.output_root,
            selected_profile_id=args.profile_id,
            snapshot_boundary_id=args.boundary_id,
        )
    else:
        receipt = publish_ingestion_snapshot(
            payload_path=args.payload,
            output_root=args.output_root,
            input_schema_version=args.input_schema_version,
            active_config_root=args.active_config_root,
            selected_profile_id=args.profile_id,
            snapshot_boundary_id=args.boundary_id,
        )
    print(json.dumps({key: str(value) for key, value in asdict(receipt).items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SnapshotPublicationError",
    "SnapshotPublicationReceipt",
    "main",
    "publish_active_config_snapshot",
    "publish_ingestion_snapshot",
]
