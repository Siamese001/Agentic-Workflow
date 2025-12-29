import logging
'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''


_logger = logging.getLogger(__name__)
# MERGED from UNASSIGNED BY WINDSURF v4 — 2025-12-07T01:21:36.289297+00:00
# Original location: 10_tests\_unassigned_tests_invalid\test_memory_schema_validation.py
# High-signal content preserved below — zero-loss migration
# ================================================================================

from typing import Iterable, Type

from pydantic import BaseModel


def _get_schema_version(obj: object) -> str | None:
    """Best-effort function to read a schema_version attribute from a model.

    The validator is intentionally defensive and never raises on basic
    attribute access issues; it only raises when the value is present but
    incompatible with expectations.
    """

    try:
        return getattr(obj, "schema_version", None)
    except (ValueError, TypeError, KeyError):  # pragma: no cover - extreme defensive
        return None


def validate_schema_version(
    obj: object,
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
        # Non-Pydantic payloads are ignored by this function.
        return

    _get_schema_version(obj)
    if version is None:
        # Older objects or non-versioned models are tolerated for now.
        return

    if str(version) not in set(expected_versions):
        raise ValueError(
            f"Unexpected schema_version={version!r}; expected one of {tuple(expected_versions)!r}"
        )
