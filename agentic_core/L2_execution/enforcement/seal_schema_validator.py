"""
E5 seal schema validator — W5-P5.3 (gap plan b7c4e2 G14).

Google structured-output + arXiv 2512.09458 pattern: before handing the
sealed artifact to [5] Exit Eval, validate it against a declared schema.
This catches silent type drift at the E5 boundary.

This validator is deliberately lightweight — it checks:

* required top-level keys exist,
* each key's value matches the declared type (``type`` or ``one_of``),
* optional length bounds on strings / collections,
* optional enum constraints on strings.

For richer validation, callers can plug in ``pydantic``/``jsonschema``
elsewhere; this module is stdlib-only so it is import-safe at L2 init.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

__all__ = [
    "FieldSpec",
    "SealSchema",
    "SealValidationError",
    "validate_sealed_artifact",
]


class SealValidationError(Exception):
    """Raised when a sealed artifact does not match its declared schema."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("seal schema validation failed: " + "; ".join(errors))
        self.errors = list(errors)


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Contract for a single field in a sealed artifact."""

    name: str
    type: type | tuple[type, ...]
    required: bool = True
    min_len: int | None = None
    max_len: int | None = None
    enum: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class SealSchema:
    """Collection of field specs for a sealed artifact."""

    name: str
    fields: tuple[FieldSpec, ...] = ()
    allow_extra: bool = True

    def field_names(self) -> list[str]:
        return [f.name for f in self.fields]


def validate_sealed_artifact(
    artifact: Mapping[str, Any],
    schema: SealSchema,
) -> None:
    """Raise ``SealValidationError`` if the artifact violates the schema.

    Accumulates all errors before raising so the caller sees every breach
    at once.
    """
    errors: list[str] = []

    declared = {f.name for f in schema.fields}
    for spec in schema.fields:
        if spec.name not in artifact:
            if spec.required:
                errors.append(f"missing required field {spec.name!r}")
            continue
        value = artifact[spec.name]
        if not isinstance(value, spec.type):
            type_names = _type_names(spec.type)
            errors.append(
                f"field {spec.name!r} expected {type_names}, got {type(value).__name__}"
            )
            continue
        if spec.min_len is not None and hasattr(value, "__len__"):
            if len(value) < spec.min_len:
                errors.append(
                    f"field {spec.name!r} length {len(value)} below min_len {spec.min_len}"
                )
        if spec.max_len is not None and hasattr(value, "__len__"):
            if len(value) > spec.max_len:
                errors.append(
                    f"field {spec.name!r} length {len(value)} above max_len {spec.max_len}"
                )
        if spec.enum is not None and isinstance(value, str):
            if value not in spec.enum:
                errors.append(
                    f"field {spec.name!r} value {value!r} not in enum {spec.enum}"
                )

    if not schema.allow_extra:
        extras = set(artifact.keys()) - declared
        if extras:
            errors.append(f"unexpected fields: {sorted(extras)}")

    if errors:
        raise SealValidationError(errors)


def _type_names(t: type | tuple[type, ...]) -> str:
    if isinstance(t, tuple):
        return "(" + ", ".join(x.__name__ for x in t) + ")"
    return t.__name__
