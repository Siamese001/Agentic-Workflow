"""Package carrier for generic apps binding manifests (data-only)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AppBindingPackage:
    package_root: Path
    manifest_path: Path
    schema_version: str
    app_id: str
    section_paths: dict[str, Path]
    manifest_document: Mapping[str, Any]


__all__ = ["AppBindingPackage"]
