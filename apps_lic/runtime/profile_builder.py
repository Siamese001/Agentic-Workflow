"""Thin import surface — canonical profile wiring lives in ``profile_builder_adapter``."""

from __future__ import annotations

from apps_lic.runtime.profile_builder_adapter import (
    APPS_LIC_REQUIRED_FIELDS,
    build_app_runtime_contract,
    parse_payload,
)

__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_LIC_REQUIRED_FIELDS",
]
