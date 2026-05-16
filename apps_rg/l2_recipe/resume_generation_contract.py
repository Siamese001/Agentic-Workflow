"""Resume artifact contract mode for apps_rg L2 generation (app-local).

``full`` — fail-closed unless model output satisfies STRUCTURED_RESUME_OK.
``stub_receipt`` / ``diagnostic`` — emit a diagnostic snapshot then raise
``STUB_RECEIPT`` so the spine never authorizes full résumé success.
"""

from __future__ import annotations

from typing import Any

MODE_FULL = "full"
MODE_STUB_RECEIPT = "stub_receipt"
MODE_DIAGNOSTIC = "diagnostic"

__all__ = [
    "MODE_DIAGNOSTIC",
    "MODE_FULL",
    "MODE_STUB_RECEIPT",
    "normalize_resume_artifact_contract_mode",
]


def normalize_resume_artifact_contract_mode(raw: Any) -> str:
    """Normalize context / raw_request value to a canonical mode string."""
    s = str(raw or "").strip().lower()
    if not s or s == MODE_FULL:
        return MODE_FULL
    if s in ("stub", "stub_receipt", "receipt", "receipt_only"):
        return MODE_STUB_RECEIPT
    if s in ("diagnostic", "debug"):
        return MODE_DIAGNOSTIC
    return MODE_FULL
