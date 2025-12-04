from __future__ import annotations

from typing import Any, Iterable, Type

from pydantic import BaseModel


def _get_schema_version(obj: Any) -> str | None:
    """Best-effort helper to read a schema_version attribute from a model.

    The validator is intentionally defensive and never raises on simple
    attribute access issues; it only raises when the value is present but
    incompatible with expectations.
    """

    try:
        return getattr(obj, "schema_version", None)
    except Exception:  # pragma: no cover - extreme defensive
        return None


def validate_schema_version(
    obj: Any,
    expected_versions: Iterable[str] = ("v1",),
    model_type: Type[BaseModel] | None = None,
) -> None:
    """Validate that a Pydantic model has an expected schema_version.

    This is a light-weight guard used on critical cross-layer contracts
    (e.g., WorkflowPlanBundle, L2ResultBundle) so that incompatible data
    shapes surface early during development and testing.

    The function is intentionally conservative:
        • If obj is not a BaseModel (and model_type is not given), it is a no-op.
        • If schema_version is missing or None, it is a no-op for now.
        • If schema_version is present but not in expected_versions, it raises
          a ValueError to signal an incompatible contract.
    """

    if model_type is not None and not isinstance(obj, model_type):
        # Caller requested a specific model type; anything else is ignored.
        return

    if model_type is None and not isinstance(obj, BaseModel):
        # Non-Pydantic payloads are ignored by this helper.
        return

    version = _get_schema_version(obj)
    if version is None:
        # Older objects or non-versioned models are tolerated for now.
        return

    if str(version) not in set(expected_versions):
        raise ValueError(
            f"Unexpected schema_version={version!r}; expected one of {tuple(expected_versions)!r}"
        )



