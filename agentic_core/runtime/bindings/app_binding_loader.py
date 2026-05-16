"""Load generic binding packages from a filesystem directory + manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.runtime.bindings.app_binding_package import AppBindingPackage

APP_BINDING_SECTIONS_MANIFEST = "app_binding_sections.binding_v1.yaml"


def load_app_binding_package(package_root: Path) -> AppBindingPackage:
    """Parse ``app_binding_sections.binding_v1.yaml`` under ``package_root``.

    Does not validate existence of section files or nested refs — use
    ``validate_app_binding_package`` for fail-closed checks.
    """
    root = package_root.resolve()
    manifest_path = root / APP_BINDING_SECTIONS_MANIFEST
    if not manifest_path.is_file():
        msg = f"missing binding manifest: {manifest_path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("binding manifest must be a mapping")

    schema_version = str(raw.get("schema_version") or "").strip()
    if not schema_version:
        raise ValueError("binding manifest requires schema_version")

    app_id = str(raw.get("app_id") or "").strip()
    if not app_id:
        raise ValueError("binding manifest requires app_id (data-only string)")

    sections_raw = raw.get("sections")
    if not isinstance(sections_raw, Mapping):
        raise ValueError("binding manifest requires sections mapping")

    section_paths: dict[str, Path] = {}
    for key, rel in sections_raw.items():
        section_key = str(key).strip()
        if not section_key:
            raise ValueError("empty section key in manifest")
        rel_str = str(rel).strip()
        if not rel_str:
            raise ValueError(f"empty path for section {section_key!r}")
        resolved = (root / rel_str).resolve()
        section_paths[section_key] = resolved

    doc_mapping: Mapping[str, Any] = raw  # type: ignore[assignment]

    return AppBindingPackage(
        package_root=root,
        manifest_path=manifest_path.resolve(),
        schema_version=schema_version,
        app_id=app_id,
        section_paths=section_paths,
        manifest_document=doc_mapping,
    )


__all__ = ["APP_BINDING_SECTIONS_MANIFEST", "load_app_binding_package"]
