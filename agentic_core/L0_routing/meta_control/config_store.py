"""ConfigStore -- Wave 7.0.17.C.

On-disk versioned config store for meta-control mutable components.
Atomic writes, deterministic versioning, fail-closed, no deletes.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.meta_control.config_store_types import (
    ConfigDeltaArtifact,
    ConfigSnapshotArtifact,
    build_config_delta,
    build_config_snapshot,
    canonical_json,
    validate_component_allowed,
)
from agentic_core.L0_routing.types.v15_p2_types import SemanticClockSnapshot
from system_learning.types.meta_learning_types import (
    MetaLearningChangePackageArtifact,
)


def _component_dir(store_root: Path, app_id: str, component: str) -> Path:
    return store_root / "apps" / app_id / component


def _current_path(store_root: Path, app_id: str, component: str) -> Path:
    return _component_dir(store_root, app_id, component) / "current.json"


def _versions_dir(store_root: Path, app_id: str, component: str) -> Path:
    return _component_dir(store_root, app_id, component) / "versions"


def _version_path(store_root: Path, app_id: str, component: str, version: int) -> Path:
    return _versions_dir(store_root, app_id, component) / f"v{version:04d}.json"


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Atomically write *data* as canonical JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = canonical_json(data)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp", prefix=".config_")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _validate_inputs(app_id: str, component: str) -> None:
    if not app_id:
        raise ValueError("APP_ID_EMPTY")
    validate_component_allowed(component)


def load_current(
    store_root: Path,
    app_id: str,
    component: str,
) -> dict[str, Any]:
    """Load the current active config payload. Returns {} if missing."""
    _validate_inputs(app_id, component)
    path = _current_path(store_root, app_id, component)
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"INVALID_JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"PAYLOAD_NOT_DICT: {path}")
    return data


def _scan_latest_version(store_root: Path, app_id: str, component: str) -> int:
    """Scan versions/ directory; return highest version (0 if none)."""
    vdir = _versions_dir(store_root, app_id, component)
    if not vdir.exists():
        return 0
    versions: list[int] = []
    for entry in sorted(vdir.iterdir()):
        name = entry.name
        if name.startswith("v") and name.endswith(".json"):
            try:
                versions.append(int(name[1:-5]))
            except ValueError:
                continue
    return max(versions) if versions else 0


def write_next_version(
    store_root: Path,
    app_id: str,
    component: str,
    payload: dict[str, Any],
    semantic_clock: SemanticClockSnapshot,
) -> ConfigSnapshotArtifact:
    """Write a new versioned snapshot and update current.json."""
    _validate_inputs(app_id, component)
    latest = _scan_latest_version(store_root, app_id, component)
    next_version = latest + 1
    snapshot = build_config_snapshot(
        app_id=app_id,
        target_component=component,
        config_version=next_version,
        payload=payload,
        semantic_clock=semantic_clock,
    )
    _atomic_write_json(
        _version_path(store_root, app_id, component, next_version),
        snapshot.payload,
    )
    _atomic_write_json(
        _current_path(store_root, app_id, component),
        snapshot.payload,
    )
    return snapshot


def apply_change_package_readonly(
    store_root: Path,
    change_package: MetaLearningChangePackageArtifact,
    semantic_clock: SemanticClockSnapshot,
) -> ConfigDeltaArtifact:
    """Compute a config delta WITHOUT writing to disk (read-only)."""
    app_id = change_package.proposal_trace_id[:8]
    component = change_package.target_component
    _validate_inputs(app_id if app_id else "unknown", component)
    latest_version = _scan_latest_version(store_root, app_id, component)
    from_version = max(latest_version, 0)
    return build_config_delta(
        app_id=app_id,
        target_component=component,
        from_version=from_version,
        to_version=from_version + 1,
        change_spec=change_package.change_spec,
        semantic_clock=semantic_clock,
    )
