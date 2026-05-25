"""Manifest hash helper for runtime certification (Phase B.3).

Design references
-----------------
- ``docs/reference/runtime_certification/contract_span_binding_matrix.md`` v2 §8, §12 Q6
- ``docs/reports/runtime_certification/phase_a_trace_inventory.md``
- Sibling: ``system_learning/runtime_adg/app_route_contracts.py`` (Phase B.2)

What this module does
---------------------
Computes a deterministic ``manifest_hash`` for each app's
``spine_manifest.yaml``. The hash is one of the **10 required cert-span
attributes** defined in design matrix v2 §8 and is required non-empty
at ``TRACE_OBSERVED`` certification level and higher.

Convention chosen (resolves design Q6): ``sha256-raw-bytes``
---------------------------------------------------------
Lowercase hex SHA-256 of the raw file bytes, with **no** YAML parse,
**no** line-ending normalization, **no** comment stripping, and **no**
canonicalization.

Rationale: the purpose of ``manifest_hash`` is to pin the exact
manifest state that was in effect when a trace was emitted. Any change
to the manifest bytes \u2014 even a comment or a whitespace tweak \u2014 should
invalidate existing certification evidence, because comments and
formatting can carry meaning (e.g., CC-SHARED-05's prose text defines
compensating-control scope). Canonical-YAML hashing would let prose
edits slip past re-certification; raw-bytes hashing forces re-cert on
any change and is trivially deterministic.

What this module is NOT
-----------------------
- Not a trace collector (Phase C).
- Not a certification evaluator (Phase D).
- Not an emitter.
- Does NOT verify that a manifest is well-formed YAML \u2014 that is an
  orthogonal concern handled by the scanner and the existing manifest
  schema checks.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

#: Algorithm identifier embedded in cert-report provenance so that a
#: future change to the hashing convention (e.g., a Phase C.2 switch to
#: canonical YAML) is detectable at the evidence-store level.
MANIFEST_HASH_ALGORITHM: str = "sha256-raw-bytes"

#: Canonical manifest filename. Every apps_* declares
#: ``<app>/spine_manifest.yaml``; no other filename is accepted here.
MANIFEST_FILENAME: str = "spine_manifest.yaml"


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def compute_manifest_hash(path: str | Path) -> str:
    """Return the lowercase hex SHA-256 of the raw bytes at ``path``.

    Contract:
      - Reads the file in binary mode \u2014 no decoding, no line-ending
        normalization, no comment stripping, no YAML parse.
      - Returns a 64-character lowercase hex digest.
      - Raises ``FileNotFoundError`` if the path does not exist.
      - Raises ``IsADirectoryError`` if the path is a directory.
      - Raises ``ValueError`` on empty / whitespace-only input paths.

    This is the SSOT for ``manifest_hash`` attribute generation.
    """
    if path is None:
        raise ValueError("compute_manifest_hash: path must not be None")
    # Guard against empty / whitespace-only inputs BEFORE Path conversion,
    # because Path("") becomes Path(".") which would falsely look like a
    # directory rather than an invalid-input error.
    if isinstance(path, str) and not path.strip():
        raise ValueError("compute_manifest_hash: path must not be empty")
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"compute_manifest_hash: manifest not found at {p!s}"
        )
    if p.is_dir():
        raise IsADirectoryError(
            f"compute_manifest_hash: path is a directory, not a file: {p!s}"
        )
    if not p.is_file():
        # Symlink-to-nothing, device node, etc.
        raise FileNotFoundError(
            f"compute_manifest_hash: path is not a regular file: {p!s}"
        )
    hasher = hashlib.sha256()
    # Read in binary, single-shot (manifests are small \u2014 a few KB). If
    # future manifests grow, switch to chunked reads; keeping it simple
    # for now matches the repo's existing hashing patterns.
    hasher.update(p.read_bytes())
    return hasher.hexdigest()


def _infer_repo_root() -> Path:
    """Infer the repo root from this module's path.

    ``manifest_hash.py`` lives at
    ``<repo_root>/system_learning/runtime_adg/manifest_hash.py`` so
    ``parents[2]`` is the repo root. This is robust to the workspace
    being cloned to any absolute path.
    """
    return Path(__file__).resolve().parents[2]


def compute_manifest_hash_for_app(
    app_name: str,
    repo_root: str | Path | None = None,
) -> str:
    """Compute the manifest_hash for a given ``apps_*`` app.

    Contract:
      - ``app_name`` MUST start with ``apps_`` (the cohort taxonomy).
      - Looks up ``<repo_root>/<app_name>/spine_manifest.yaml``.
      - If ``repo_root`` is ``None``, infers the repo root from this
        module's path (``parents[2]``).
      - Delegates to :func:`compute_manifest_hash` for the actual digest.

    Raises ``ValueError`` on invalid app_name. Propagates
    ``FileNotFoundError`` / ``IsADirectoryError`` from
    :func:`compute_manifest_hash`.
    """
    if not isinstance(app_name, str) or not app_name.strip():
        raise ValueError(
            "compute_manifest_hash_for_app: app_name must be a non-empty string"
        )
    if not app_name.startswith("apps_"):
        raise ValueError(
            f"compute_manifest_hash_for_app: app_name must start with 'apps_'; "
            f"got {app_name!r}"
        )
    root = Path(repo_root) if repo_root is not None else _infer_repo_root()
    manifest_path = root / app_name / MANIFEST_FILENAME
    return compute_manifest_hash(manifest_path)


__all__ = [
    "MANIFEST_FILENAME",
    "MANIFEST_HASH_ALGORITHM",
    "compute_manifest_hash",
    "compute_manifest_hash_for_app",
]
