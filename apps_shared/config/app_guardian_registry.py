"""AppGuardianSpec registry — deterministic pass/fail checks for apps_*.

Each spec describes one guardian check: what it detects, which app it covers,
and how severe a failure is. The dispatcher uses this registry to fan-out
checks and collect AppHealResult artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

App = Literal["apps_rg", "apps_lic", "apps_shared", "*"]
Severity = Literal["critical", "high", "medium", "low"]


@dataclass(frozen=True)
class AppGuardianSpec:
    """Immutable descriptor for a single guardian check."""

    check_id: str
    app: App
    description: str
    severity: Severity
    guardian_module: str


APP_GUARDIAN_REGISTRY: tuple[AppGuardianSpec, ...] = (
    AppGuardianSpec(
        check_id="AGS-001",
        app="*",
        description="Dead import edges (F401) in apps_* modules",
        severity="medium",
        guardian_module="ops_scripts.ci._audit_scan",
    ),
    AppGuardianSpec(
        check_id="AGS-002",
        app="*",
        description="Layer gravity violations (L_APP importing L_SL)",
        severity="critical",
        guardian_module="agentic_core.adg.applications.execute_ssot_integration",
    ),
    AppGuardianSpec(
        check_id="AGS-003",
        app="*",
        description="Misplaced test files inside apps_* source trees",
        severity="low",
        guardian_module="ops_scripts.ci._audit_scan",
    ),
    AppGuardianSpec(
        check_id="AGS-004",
        app="*",
        description="Inline pipeline constants not imported from SSOT",
        severity="medium",
        guardian_module="ops_scripts.ci._audit_scan",
    ),
    AppGuardianSpec(
        check_id="AGS-005",
        app="apps_rg",
        description="ContentStrategyAgent backward-compat shim present",
        severity="low",
        guardian_module="ops_scripts.ci._audit_scan",
    ),
    AppGuardianSpec(
        check_id="AGS-006",
        app="apps_lic",
        description="Duplicate class definitions (MCPOperationMixin, HealingPolicyMixin stubs)",
        severity="medium",
        guardian_module="ops_scripts.ci._audit_scan",
    ),
)


def get_specs_for_app(app: str) -> tuple[AppGuardianSpec, ...]:
    """Return all guardian specs applicable to the given app."""
    return tuple(s for s in APP_GUARDIAN_REGISTRY if s.app in (app, "*"))


__all__ = [
    "App",
    "AppGuardianSpec",
    "APP_GUARDIAN_REGISTRY",
    "get_specs_for_app",
    "Severity",
]
