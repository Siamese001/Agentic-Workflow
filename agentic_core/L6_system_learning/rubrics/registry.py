"""Rubric registry implementation.

Read-only view over ``config/judges/*.yaml`` that gives engine code a typed,
content-addressed handle on a rubric. See :mod:`system_learning.rubrics`
package docstring and plan ``system-learning-waves-7b3c91.md`` phase A2 for
the normative contract.

The registry deliberately does NOT write YAML, does NOT reach into running
judges, and does NOT expose any mutation API — it is a pure reader. Consumers
that want to enforce freshness call :meth:`RubricRegistry.rubric_hash`
before and after a critical section.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError as exc:  # pragma: no cover - yaml is a hard dep of the repo
    raise ImportError(
        "system_learning.rubrics.registry requires PyYAML. Install via `pip install pyyaml`."
    ) from exc

from .types import (
    RubricDimension,
    RubricFile,
    RubricRecord,
)

# Canonical rubric files shipped by the repo. New rubric files SHOULD be added
# here; out-of-tree callers can pass explicit paths to ``load_rubric_file``.
_DEFAULT_RUBRIC_SOURCES: Mapping[str, str] = {
    "rubrics": "config/judges/rubrics.yaml",
    "trace_rubric": "config/judges/trace_rubric.yaml",
}


def _canonicalize_yaml_bytes(text: str) -> bytes:
    """Return canonical bytes for hashing.

    Normalizes line endings, strips trailing whitespace per line, drops a
    single trailing newline if present, then encodes utf-8. This keeps the
    hash stable across cosmetic edits while still catching semantic changes.
    """

    normalized_lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    # Drop all trailing empty lines — any number of trailing newlines is cosmetic.
    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()
    return "\n".join(normalized_lines).encode("utf-8")


def _hash_canonical(text: str) -> str:
    return hashlib.sha256(_canonicalize_yaml_bytes(text)).hexdigest()


def _coerce_dimension(name: str, raw: Mapping[str, Any]) -> RubricDimension:
    """Build a :class:`RubricDimension` from a YAML mapping fragment.

    Missing optional fields fall back to sensible defaults (``weight=1.0``,
    empty ``anchors``). Unknown keys go into ``extras`` so the registry does
    not hide forward-compatible YAML evolution.
    """

    known = {
        "display_name",
        "description",
        "scale_min",
        "scale_max",
        "pass_threshold",
        "warn_threshold",
        "unknown_budget",
        "weight",
        "anchors",
    }
    extras = {key: value for key, value in raw.items() if key not in known}

    anchors_raw = raw.get("anchors") or {}
    # YAML may surface integer keys as int or str; normalize to int.
    anchors: dict[int, str] = {}
    for key, value in anchors_raw.items():
        try:
            anchors[int(key)] = str(value)
        except (TypeError, ValueError):
            # Non-integer anchor keys are preserved in extras for audit.
            extras.setdefault("_non_integer_anchors", {})[str(key)] = str(value)

    return RubricDimension(
        name=name,
        display_name=str(raw.get("display_name", name)),
        description=str(raw.get("description", "")).strip(),
        scale_min=int(raw.get("scale_min", 1)),
        scale_max=int(raw.get("scale_max", 5)),
        pass_threshold=float(raw.get("pass_threshold", 4.0)),
        warn_threshold=float(raw.get("warn_threshold", 3.0)),
        unknown_budget=float(raw.get("unknown_budget", 0.20)),
        weight=float(raw.get("weight", 1.0)),
        anchors=anchors,
        extras=extras,
    )


def load_rubric_file(rubric_id: str, path: str | os.PathLike[str]) -> RubricFile:
    """Load a single rubric file from ``path`` and return a :class:`RubricFile`.

    Raises :class:`FileNotFoundError` if ``path`` does not exist and
    :class:`ValueError` if the YAML is not a mapping at the top level.
    """

    source_path = str(Path(path))
    with open(source_path, encoding="utf-8") as handle:
        text = handle.read()

    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(
            f"Rubric file {source_path!r} must be a top-level mapping; got {type(data).__name__}"
        )

    rubric_hash = _hash_canonical(text)
    version = int(data.get("version", 0))
    schema = str(data.get("schema", ""))

    dims_raw = data.get("dimensions") or {}
    if not isinstance(dims_raw, dict):
        raise ValueError(
            f"Rubric file {source_path!r}: 'dimensions' must be a mapping; got {type(dims_raw).__name__}"
        )

    dimensions = {
        name: _coerce_dimension(name, dim_raw)
        for name, dim_raw in dims_raw.items()
        if isinstance(dim_raw, dict)
    }

    return RubricFile(
        rubric_id=rubric_id,
        source_path=source_path,
        version=version,
        schema=schema,
        rubric_hash=rubric_hash,
        dimensions=dimensions,
        raw=data,
    )


class RubricRegistry:
    """Content-addressed, read-only registry of rubric files.

    Thread-safe: all state access is guarded by a single lock. The hot path
    (``get``) is O(1) and does no I/O after initial load — callers wanting
    freshness checks use :meth:`rubric_hash` or :meth:`reload`.
    """

    def __init__(
        self,
        repo_root: str | os.PathLike[str],
        sources: Mapping[str, str] | None = None,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._sources = dict(sources if sources is not None else _DEFAULT_RUBRIC_SOURCES)
        self._records: dict[str, RubricRecord] = {}
        self._lock = threading.Lock()

    def known_rubric_ids(self) -> tuple[str, ...]:
        """Return rubric ids this registry was configured to serve."""

        return tuple(self._sources.keys())

    def _load_locked(self, rubric_id: str) -> RubricRecord:
        if rubric_id not in self._sources:
            raise KeyError(f"Unknown rubric_id: {rubric_id!r}")
        rel_path = self._sources[rubric_id]
        abs_path = self._repo_root / rel_path
        rubric_file = load_rubric_file(rubric_id, abs_path)
        mtime = abs_path.stat().st_mtime
        record = RubricRecord(
            rubric_id=rubric_id,
            rubric_file=rubric_file,
            loaded_at=time.time(),
            mtime=mtime,
        )
        self._records[rubric_id] = record
        return record

    def get(self, rubric_id: str) -> RubricRecord:
        """Return the cached record for ``rubric_id``, loading on first access.

        Subsequent calls are cache hits; to force a fresh read, call
        :meth:`reload` first.
        """

        with self._lock:
            record = self._records.get(rubric_id)
            if record is not None:
                return record
            return self._load_locked(rubric_id)

    def reload(self, rubric_id: str) -> RubricRecord:
        """Force a re-read of ``rubric_id`` from disk and return the new record."""

        with self._lock:
            self._records.pop(rubric_id, None)
            return self._load_locked(rubric_id)

    def rubric_hash(self, rubric_id: str) -> str:
        """Return the content-addressed hash for ``rubric_id``.

        Useful as a cheap freshness check — callers can stash the hash
        around a critical section and compare on exit.
        """

        return self.get(rubric_id).rubric_file.rubric_hash

    def version(self, rubric_id: str) -> int:
        """Return the ``version`` integer declared in the rubric YAML."""

        return self.get(rubric_id).rubric_file.version


_DEFAULT_REGISTRY: RubricRegistry | None = None
_DEFAULT_REGISTRY_LOCK = threading.Lock()


def default_registry(
    repo_root: str | os.PathLike[str] | None = None,
) -> RubricRegistry:
    """Return a process-wide default registry rooted at ``repo_root``.

    If ``repo_root`` is omitted, the caller's current working directory is
    used. The registry is memoized; call :meth:`RubricRegistry.reload` on it
    to pick up on-disk changes.
    """

    global _DEFAULT_REGISTRY
    with _DEFAULT_REGISTRY_LOCK:
        if _DEFAULT_REGISTRY is None:
            root = Path(repo_root) if repo_root is not None else Path.cwd()
            _DEFAULT_REGISTRY = RubricRegistry(root)
        return _DEFAULT_REGISTRY
