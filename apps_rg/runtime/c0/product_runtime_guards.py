"""Canonical product section runtime env guards — fail-closed, test-harness-only opt-out."""

from __future__ import annotations

import os

from apps_rg.runtime.c0.constants import C0_SECTIONS_ENABLED

ENV_APPS_RG_C0_EVIDENCE_ROOM = "APPS_RG_C0_EVIDENCE_ROOM"
ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH = "APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH"


class ProductRuntimeEnvForbiddenError(RuntimeError):
    """Raised when a forbidden env disables product authority surfaces."""


def _env_disabled(name: str, *, default: str = "1") -> bool:
    return os.environ.get(name, default).strip().lower() in ("0", "false", "no")


def assert_canonical_product_section_env(section_id: str) -> None:
    """Fail closed on ``python -m apps_rg --section`` product lanes when env disables C0/FEC."""
    from apps_rg.runtime.product_output_policy import (
        is_apps_rg_test_harness,
        product_fail_closed_runtime,
    )

    if not product_fail_closed_runtime() or is_apps_rg_test_harness():
        return
    if section_id not in C0_SECTIONS_ENABLED:
        return
    if _env_disabled(ENV_APPS_RG_C0_EVIDENCE_ROOM):
        raise ProductRuntimeEnvForbiddenError(
            f"{ENV_APPS_RG_C0_EVIDENCE_ROOM}=0 is forbidden on canonical product section runs "
            f"for {section_id!r}; unset or use APPS_RG_TEST_HARNESS=1 for dev-only bypass"
        )
    if _env_disabled(ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH):
        raise ProductRuntimeEnvForbiddenError(
            f"{ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH}=0 is forbidden on canonical product "
            f"section runs; FEC bridge is mandatory. Use APPS_RG_TEST_HARNESS=1 for dev-only bypass"
        )


def product_fec_bridge_mandatory() -> bool:
    """Product-visible runs must use FEC bridge (no env kill switch)."""
    from apps_rg.runtime.product_output_policy import (
        is_apps_rg_test_harness,
        product_fail_closed_runtime,
    )

    if is_apps_rg_test_harness():
        return False
    return product_fail_closed_runtime()


def fec_bridge_kill_switch_enabled() -> bool:
    """Legacy name: True when FEC bridge is required for the current runtime mode."""
    return product_fec_bridge_mandatory() or not _env_disabled(
        ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH
    )


__all__ = [
    "ENV_APPS_RG_C0_EVIDENCE_ROOM",
    "ENV_APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH",
    "ProductRuntimeEnvForbiddenError",
    "assert_canonical_product_section_env",
    "fec_bridge_kill_switch_enabled",
    "product_fec_bridge_mandatory",
]
