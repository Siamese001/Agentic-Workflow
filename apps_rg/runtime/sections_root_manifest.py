"""W4.1 — ``sections_root_manifest.json`` beside ``APPS_RG_MODULAR_R4_SECTIONS_ROOT``.

Prevents ``APPS_RG_MODULAR_R4_SECTIONS_ROOT`` from functioning as an undocumented third
evidence tree: modular section outputs require a typed manifest adjacent to that root.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.run_bundle_index import (
    load_apps_rg_pipeline_namespaces,
    repo_relative_posix,
)

SECTIONS_ROOT_MANIFEST_FILENAME = "sections_root_manifest.json"

_SCHEMA_VERSION = "1"

_LOG = logging.getLogger(__name__)


def log_sections_manifest_write_failed(context: str, exc: OSError) -> None:
    _LOG.warning("sections_root_manifest write failed (%s): %s", context, exc)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_sections_root_manifest_document(
    repo_root: Path,
    *,
    sections_root_abs: Path,
    correlation_id: str | None,
    integrated_run_ref: str | None,
    run_links_ref: str | None,
    source_env_literal: str,
    notes: str | None = None,
) -> dict[str, Any]:
    """Structured manifest describing the modular lane pointer root."""

    root_resolved = sections_root_abs.resolve()
    root_path = repo_relative_posix(repo_root, root_resolved)
    art_ns, _log_ns = load_apps_rg_pipeline_namespaces(repo_root)

    doc: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "root_kind": "modular_r4_sections_root",
        "root_path": root_path,
        "created_at": _utc_now_iso(),
        "source_env_var": source_env_literal,
        "artifact_namespace": art_ns,
        "correlation_id": correlation_id if correlation_id else None,
        "integrated_run_ref": integrated_run_ref,
        "run_links_ref": run_links_ref,
    }
    if notes:
        doc["notes"] = notes
    return doc


def write_sections_root_manifest(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(document), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_sections_root_manifest(
    *,
    repo_root: Path,
    sections_root_abs: Path,
    source_env_literal: str,
    correlation_id: str | None = None,
    integrated_run_ref: str | None = None,
    run_links_ref: str | None = None,
    notes: str | None = None,
) -> Path:
    """Write ``sections_root_manifest.json`` at ``sections_root``. Fail-closed on OSError."""

    target = sections_root_abs.resolve() / SECTIONS_ROOT_MANIFEST_FILENAME
    doc = build_sections_root_manifest_document(
        repo_root,
        sections_root_abs=sections_root_abs,
        correlation_id=correlation_id,
        integrated_run_ref=integrated_run_ref,
        run_links_ref=run_links_ref,
        source_env_literal=source_env_literal,
        notes=notes,
    )
    write_sections_root_manifest(target, doc)
    return target


def require_manifest_for_modular_sections_root(sections_root: Path, *, env_name: str) -> None:
    """Fail-closed gate: env-scoped modular section root requires ``sections_root_manifest.json``."""

    mf = sections_root.resolve() / SECTIONS_ROOT_MANIFEST_FILENAME
    if not mf.is_file():
        raise ValueError(
            f"{env_name} is set but required manifest `{SECTIONS_ROOT_MANIFEST_FILENAME}` "
            f"is missing beside resolved sections root `{sections_root}`."
        )


def assert_sections_root_manifest_document_shape(doc: Mapping[str, Any]) -> None:
    for k in (
        "schema_version",
        "root_kind",
        "root_path",
        "created_at",
        "source_env_var",
        "artifact_namespace",
        "correlation_id",
        "integrated_run_ref",
        "run_links_ref",
    ):
        if k not in doc:
            raise ValueError(f"sections_root_manifest missing key: {k}")
    if doc["root_kind"] != "modular_r4_sections_root":
        raise ValueError("unexpected root_kind")
    rp = str(doc["root_path"])
    if not rp or rp.startswith(("/", "\\")):
        raise ValueError("manifest root_path unsafe")
    if ".." in rp.split("/"):
        raise ValueError("manifest root_path escape")


__all__ = [
    "SECTIONS_ROOT_MANIFEST_FILENAME",
    "assert_sections_root_manifest_document_shape",
    "build_sections_root_manifest_document",
    "emit_sections_root_manifest",
    "log_sections_manifest_write_failed",
    "require_manifest_for_modular_sections_root",
    "write_sections_root_manifest",
]
