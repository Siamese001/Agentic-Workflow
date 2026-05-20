"""Process-local store for U0-resolved runtime package metadata on the L0 ValidatedRequest path.

apps_qna U0 composes agentic_core ``u0_resolve_runtime_package`` (package + digest)
with ``intake_interview_request`` (L0 routing ValidatedRequest). The L0 type has no
``app_payload`` field; this module holds the resolved package keyed by request_id
for downstream bindings and tests to inspect.
"""
from __future__ import annotations

from typing import Any

_STORE: dict[str, dict[str, Any]] = {}


def stash_u0_package_artifacts(
    request_id: str,
    *,
    runtime_customization_package: dict[str, Any],
    package_validation_receipt: dict[str, Any],
    auto_injection_context: dict[str, Any],
) -> None:
    _STORE[request_id] = {
        "runtime_customization_package": runtime_customization_package,
        "package_validation_receipt": package_validation_receipt,
        "auto_injection_context": auto_injection_context,
    }


def get_u0_package_artifacts(request_id: str) -> dict[str, Any] | None:
    return _STORE.get(request_id)


def clear_u0_package_store() -> None:
    _STORE.clear()


__all__ = [
    "stash_u0_package_artifacts",
    "get_u0_package_artifacts",
    "clear_u0_package_store",
]
