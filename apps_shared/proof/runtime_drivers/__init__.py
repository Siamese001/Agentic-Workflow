"""Per-app runtime drivers — the bridge from spine proof to app proof.

Each driver invokes the app's REAL engine code (not a stub) using the
``extra_payload`` fixture from the scenario spec. The driver runs INSIDE
``scenario_base.run_l2`` AFTER the spine's bounded executor has produced a
SealedArtifact, and writes app-specific artifacts (e.g. ``decision_packet.json``,
``evidence_register.json``) under the scenario's contract directory.

Drivers are opt-in. If no driver is registered for ``app_id``, the spine
runs as before with the deterministic_model stub — preserving backward
compatibility with the existing harness.

Registry shape:

    DRIVERS: dict[str, AppRuntimeDriver] = {
        "apps_underwriting_ai": AppsUnderwritingAIDriver(),
        ...
    }

Each driver exposes ``invoke(ctx) -> dict[str, str]`` returning a map of
``artifact_kind -> relative_path`` for every file it wrote under
``ctx.scenario_dir``. The spine adds those to the contract inventory.
"""

from __future__ import annotations

from typing import Protocol


class AppRuntimeDriver(Protocol):
    """Interface every app-specific driver must implement."""

    app_id: str

    def invoke(self, ctx) -> dict[str, str]:  # ScenarioContext (avoid circular import)
        """Run the app's real engine and write artifacts under ``ctx.scenario_dir``.

        Returns a map of ``{artifact_kind: relative_path}`` for files written.
        ``artifact_kind`` follows the same convention as scenario_base.emit_contract
        (e.g. ``"DecisionPacket"`` → matches CONTRACT_FILE_BY_KIND if registered).
        Relative paths are relative to ``ctx.scenario_dir``.

        On any failure, the driver MUST raise — the spine's run_l2 wraps the
        call in a try/except that records the failure as a span attribute.
        """
        ...


# Lazy import of registered drivers to keep the package import light.
def get_driver(app_id: str):
    """Return the registered driver for ``app_id`` or None."""
    if app_id == "apps_underwriting_ai":
        from apps_shared.proof.runtime_drivers.apps_underwriting_ai_driver import (
            AppsUnderwritingAIDriver,
        )
        return AppsUnderwritingAIDriver()
    if app_id == "apps_research":
        from apps_shared.proof.runtime_drivers.apps_research_driver import AppsResearchDriver
        return AppsResearchDriver()
    if app_id == "apps_exec":
        from apps_shared.proof.runtime_drivers.apps_exec_driver import AppsExecDriver
        return AppsExecDriver()
    if app_id == "apps_lic":
        from apps_shared.proof.runtime_drivers.apps_lic_driver import AppsLicDriver
        return AppsLicDriver()
    if app_id == "apps_rg":
        from apps_shared.proof.runtime_drivers.apps_rg_driver import AppsRgDriver
        return AppsRgDriver()
    if app_id == "apps_eval":
        from apps_shared.proof.runtime_drivers.apps_eval_driver import AppsEvalDriver
        return AppsEvalDriver()
    if app_id == "apps_shared":
        from apps_shared.proof.runtime_drivers.apps_shared_driver import AppsSharedDriver
        return AppsSharedDriver()
    return None


__all__ = ["AppRuntimeDriver", "get_driver"]
