"""Shared fixtures for U0→Exit spine contract tests."""
from __future__ import annotations

from typing import Any

L5_CERT = "test:valid:w6"


def thin_apps_rg_ingress_kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "source_resume_text": "Resume body for spine contract tests.",
        "l5_certification_ref": L5_CERT,
    }
    base.update(overrides)
    return base
