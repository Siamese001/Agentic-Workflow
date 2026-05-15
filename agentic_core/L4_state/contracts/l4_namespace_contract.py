"""Generic L4 namespace contract parser and validator.

Provides declarative governance validation for L4 read surface namespace
manifests. This module is parser-only: it validates structure and policy
constraints but NEVER creates, implies, or grants write authority.

All write operations in a manifest are treated as declarative governance
metadata only. The parser will fail validation unless a UWG-mediated
writer_policy accompanies any write-capable operation declaration.

Hard rules:
- No app_* imports or app-specific literals.
- No write authority creation of any kind.
- No inference of authority from manifest content.
- YAML parsing uses safe_load only.
- Fail closed on malformed input.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

try:
    import yaml as _yaml  # optional; fail-closed if absent
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _yaml = None  # type: ignore[assignment]
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Vocabulary constants (generic only — no app literals)
# ---------------------------------------------------------------------------

ALLOWED_SURFACE_TYPES: FrozenSet[str] = frozenset({
    "cache",
    "vector_index",
    "graph_projection",
    "policy_registry",
    "prompt_registry",
    "rubric_registry",
    "audit_ledger",
    "replay_store",
    "memory_store",
    "document_store",
})

ALLOWED_READ_OPERATIONS: FrozenSet[str] = frozenset({
    "query",
    "get",
    "search",
    "scan",
    "list",
    "hydrate",
})

# Operations that require UWG-mediated writer_policy to appear in a manifest.
# Parser treats these as declarative metadata; it does NOT grant write authority.
WRITE_CAPABLE_OPERATIONS: FrozenSet[str] = frozenset({
    "write",
    "mutate",
    "update",
    "delete",
    "append",
    "upsert",
    "index_refresh",
    "cache_write",
    "memory_write",
    "policy_promotion",
    "registry_promotion",
    "prompt_promotion",
    "rubric_promotion",
})

UWG_MEDIATED_WRITER_POLICY: str = "UWG-mediated"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class L4ReadSurface:
    """Immutable descriptor for a single L4 read surface.

    All fields are required in a valid manifest; defaults of '' signal
    'absent' and will trigger a ValidationError.
    """
    surface_id: str
    surface_type: str
    schema_version: str
    schema_ref: str
    acl_profile: str
    authority_class: str
    replay_key_pattern: str
    audit_manifest_ref: str
    retention_policy: str
    allowed_operations: Tuple[str, ...] = ()
    writer_policy: str = ""
    read_policy: str = ""
    owner_app_id: str = ""
    pii_or_sensitive_data_class: str = ""
    lineage_required: bool = False


@dataclass(frozen=True)
class L4NamespaceManifest:
    """Immutable top-level L4 namespace manifest.

    Produced by L4NamespaceParser after successful validation.
    This object is read-only governance metadata; it carries no write
    authority and cannot be used to drive L4 state changes directly.
    """
    app_id: str
    version: str
    surfaces: Tuple[L4ReadSurface, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of L4NamespaceParser.validate()."""
    valid: bool
    errors: Tuple[str, ...] = ()

    @property
    def error_summary(self) -> str:
        return "; ".join(self.errors) if self.errors else ""


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class L4NamespaceContractError(ValueError):
    """Raised when a manifest fails schema or policy validation."""


class L4NamespaceParseError(ValueError):
    """Raised when raw input cannot be parsed (malformed JSON/YAML)."""


# ---------------------------------------------------------------------------
# Validator (internal)
# ---------------------------------------------------------------------------

def _validate_manifest_dict(data: Dict[str, Any]) -> ValidationResult:
    """Validate a parsed manifest dict against all governance constraints.

    Returns a ValidationResult. Does NOT raise; callers decide whether to
    raise on invalid results.
    """
    errors: List[str] = []

    # --- Top-level fields ---
    app_id: str = data.get("app_id", "") or ""
    version: str = data.get("version", "") or ""
    surfaces_raw: Any = data.get("surfaces", None)

    if not app_id:
        errors.append("EMPTY_APP_ID: app_id must be non-empty")

    if not version:
        errors.append("EMPTY_VERSION: version must be non-empty")

    if not surfaces_raw:
        errors.append("EMPTY_SURFACES: surfaces list must be non-empty")
        return ValidationResult(valid=False, errors=tuple(errors))

    if not isinstance(surfaces_raw, list):
        errors.append("INVALID_SURFACES: surfaces must be a list")
        return ValidationResult(valid=False, errors=tuple(errors))

    # --- Surface-level validation ---
    seen_surface_ids: Dict[str, int] = {}
    for idx, surf in enumerate(surfaces_raw):
        if not isinstance(surf, dict):
            errors.append(f"SURFACE[{idx}] INVALID_SURFACE: must be a mapping")
            continue

        sid: str = surf.get("surface_id", "") or ""
        stype: str = surf.get("surface_type", "") or ""
        schema_version: str = surf.get("schema_version", "") or ""
        schema_ref: str = surf.get("schema_ref", "") or ""
        acl_profile: str = surf.get("acl_profile", "") or ""
        authority_class: str = surf.get("authority_class", "") or ""
        replay_key_pattern: str = surf.get("replay_key_pattern", "") or ""
        audit_manifest_ref: str = surf.get("audit_manifest_ref", "") or ""
        retention_policy: str = surf.get("retention_policy", "") or ""
        allowed_operations: Any = surf.get("allowed_operations", []) or []
        writer_policy: str = surf.get("writer_policy", "") or ""
        owner_app_id: str = surf.get("owner_app_id", "") or ""

        # Duplicate surface_id
        if sid:
            if sid in seen_surface_ids:
                errors.append(
                    f"SURFACE[{idx}] DUPLICATE_SURFACE_ID: '{sid}' already seen at index {seen_surface_ids[sid]}"
                )
            else:
                seen_surface_ids[sid] = idx

        # owner_app_id mismatch
        if owner_app_id and app_id and owner_app_id != app_id:
            errors.append(
                f"SURFACE[{idx}] OWNER_APP_ID_MISMATCH: owner_app_id '{owner_app_id}' "
                f"does not match manifest app_id '{app_id}'"
            )

        # Unknown surface_type
        if stype and stype not in ALLOWED_SURFACE_TYPES:
            errors.append(
                f"SURFACE[{idx}] UNKNOWN_SURFACE_TYPE: '{stype}' not in allowed types"
            )
        elif not stype:
            errors.append(f"SURFACE[{idx}] MISSING_SURFACE_TYPE")

        # Required string fields
        if not schema_version:
            errors.append(f"SURFACE[{idx}] MISSING_SCHEMA_VERSION")
        if not schema_ref:
            errors.append(f"SURFACE[{idx}] MISSING_SCHEMA_REF")
        if not acl_profile:
            errors.append(f"SURFACE[{idx}] MISSING_ACL_PROFILE")
        if not authority_class:
            errors.append(f"SURFACE[{idx}] MISSING_AUTHORITY_CLASS")
        if not replay_key_pattern:
            errors.append(f"SURFACE[{idx}] MISSING_REPLAY_KEY_PATTERN")
        if not audit_manifest_ref:
            errors.append(f"SURFACE[{idx}] MISSING_AUDIT_MANIFEST_REF")
        if not retention_policy:
            errors.append(f"SURFACE[{idx}] MISSING_RETENTION_POLICY")

        # allowed_operations validation
        if not isinstance(allowed_operations, list):
            errors.append(f"SURFACE[{idx}] INVALID_ALLOWED_OPERATIONS: must be a list")
        else:
            all_valid_ops = ALLOWED_READ_OPERATIONS | WRITE_CAPABLE_OPERATIONS
            for op in allowed_operations:
                if op not in all_valid_ops:
                    errors.append(
                        f"SURFACE[{idx}] INVALID_OPERATION: '{op}' is not a recognised operation"
                    )
            # Write-capable ops require UWG-mediated writer_policy
            write_ops_present = [op for op in allowed_operations if op in WRITE_CAPABLE_OPERATIONS]
            if write_ops_present and writer_policy != UWG_MEDIATED_WRITER_POLICY:
                errors.append(
                    f"SURFACE[{idx}] WRITE_OPS_REQUIRE_UWG_WRITER_POLICY: "
                    f"operations {write_ops_present} require writer_policy == "
                    f"'{UWG_MEDIATED_WRITER_POLICY}', got '{writer_policy}'"
                )

    return ValidationResult(valid=len(errors) == 0, errors=tuple(errors))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class L4NamespaceParser:
    """Declarative governance parser for L4 namespace manifests.

    Supports JSON and safe-YAML only. Accepts path input. Fail-closed on
    malformed input. Never creates write authority — parsing a manifest
    with write-capable operations declared does not grant those operations;
    it only validates that the writer_policy governance metadata is present.
    """

    @staticmethod
    def _build_manifest(data: Dict[str, Any]) -> L4NamespaceManifest:
        """Build an L4NamespaceManifest from a validated dict. Internal use only."""
        surfaces = []
        for surf in data.get("surfaces", []):
            allowed_ops_raw = surf.get("allowed_operations", []) or []
            surfaces.append(L4ReadSurface(
                surface_id=surf.get("surface_id", ""),
                surface_type=surf.get("surface_type", ""),
                schema_version=surf.get("schema_version", ""),
                schema_ref=surf.get("schema_ref", ""),
                acl_profile=surf.get("acl_profile", ""),
                authority_class=surf.get("authority_class", ""),
                replay_key_pattern=surf.get("replay_key_pattern", ""),
                audit_manifest_ref=surf.get("audit_manifest_ref", ""),
                retention_policy=surf.get("retention_policy", ""),
                allowed_operations=tuple(allowed_ops_raw),
                writer_policy=surf.get("writer_policy", ""),
                read_policy=surf.get("read_policy", ""),
                owner_app_id=surf.get("owner_app_id", ""),
                pii_or_sensitive_data_class=surf.get("pii_or_sensitive_data_class", ""),
                lineage_required=bool(surf.get("lineage_required", False)),
            ))
        return L4NamespaceManifest(
            app_id=data.get("app_id", ""),
            version=data.get("version", ""),
            surfaces=tuple(surfaces),
        )

    @classmethod
    def parse_json(cls, path: Path) -> L4NamespaceManifest:
        """Parse and validate a JSON manifest file. Raises on error."""
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise L4NamespaceParseError(f"JSON parse error in {path}: {exc}") from exc
        result = _validate_manifest_dict(data)
        if not result.valid:
            raise L4NamespaceContractError(
                f"Manifest validation failed for {path}: {result.error_summary}"
            )
        return cls._build_manifest(data)

    @classmethod
    def parse_yaml(cls, path: Path) -> L4NamespaceManifest:
        """Parse and validate a YAML manifest file using safe_load only. Raises on error."""
        if not _YAML_AVAILABLE:  # pragma: no cover
            raise L4NamespaceParseError(
                "PyYAML is not installed. Install pyyaml to parse YAML manifests."
            )
        try:
            raw = path.read_text(encoding="utf-8")
            data = _yaml.safe_load(raw)
        except (OSError, _yaml.YAMLError) as exc:
            raise L4NamespaceParseError(f"YAML parse error in {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise L4NamespaceParseError(f"YAML manifest must be a mapping, got {type(data)}")
        result = _validate_manifest_dict(data)
        if not result.valid:
            raise L4NamespaceContractError(
                f"Manifest validation failed for {path}: {result.error_summary}"
            )
        return cls._build_manifest(data)

    @classmethod
    def validate_dict(cls, data: Dict[str, Any]) -> ValidationResult:
        """Validate a pre-parsed dict without raising. Returns ValidationResult."""
        return _validate_manifest_dict(data)
