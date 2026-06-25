"""
Repo-wide governed-app registry.
Single source of truth for governed-app adoption status across all apps_* packages.

Every apps_* package must appear in APP_REGISTRY as one of:
  - GOVERNED:   uses GovernedAppRunner; has a governed_*_run.py subclass.
  - CANDIDATE:  targeted for migration; not yet adopted; treated as explicit exception.
  - EXCEPTION:  cannot adopt the runner; must supply a bounded ExceptionRecord with justification.

Adding a new apps_* package without a registry entry is a conformance violation (exit 1).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------


class GovernanceStatus(str, Enum):
    GOVERNED = "governed"
    CANDIDATE = "candidate"
    EXCEPTION = "exception"


class ExceptionReasonCode(str, Enum):
    """Canonical reason codes for permanent governed exceptions."""

    CIRCULAR_DEPENDENCY = "circular_dependency"
    REGULATORY_DOMAIN = "regulatory_domain"
    PENDING_MIGRATION = "pending_migration"


# ---------------------------------------------------------------------------
# Registry entry types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedAppEntry:
    """A fully governed app that uses the shared GovernedAppRunner pipeline.

    Required fields
    ---------------
    app_name:         Importable package name (e.g. "apps_research").
    runner_module:    Dotted module path of the governed runner
                      (e.g. "apps_research.integrations.governed_research_run").
    runner_class:     Class name of the GovernedAppRunner subclass or canonical callable
                      (e.g. "GovernedResearchRun" or "dispatch_apps_rg_run").
    capability_token: Stable token unique to this app's governed capability
                      (e.g. "apps_research.governed_e2e.v1").
    routing_target:   L0 routing target registered by this app
                      (e.g. "research_assembly").
    proof_prefix:     Short prefix for proof-harness check IDs (e.g. "APP", "EXE").
    """

    app_name: str
    status: GovernanceStatus
    runner_module: str
    runner_class: str
    capability_token: str
    routing_target: str
    proof_prefix: str


@dataclass(frozen=True)
class ExceptionAppEntry:
    """An app that cannot yet (or must never) adopt GovernedAppRunner.

    Required fields
    ---------------
    app_name:          Importable package name.
    status:            CANDIDATE or EXCEPTION.
    exception_category: One of "circular_dependency" | "regulatory_domain" |
                        "pending_migration".
    exception_reason:  One-sentence human-readable justification.
    owner:             Team or person responsible for this entry.
    target_phase:      When migration is expected ("Phase N" or "N/A — permanent exception").

    Note: Use FormalExceptionEntry for all permanent (status=EXCEPTION) apps.
    ExceptionAppEntry is retained for transient CANDIDATE entries only.
    """

    app_name: str
    status: GovernanceStatus
    exception_category: str
    exception_reason: str
    owner: str
    target_phase: str


@dataclass(frozen=True)
class FormalExceptionEntry:
    """Formal governed-exception entry for permanent exceptions.

    All EXCEPTION-status apps MUST use FormalExceptionEntry.
    ExceptionAppEntry is for transient CANDIDATE apps only.

    Required fields
    ---------------
    exception_reason_code : ExceptionReasonCode enum value.
    blocked_layers        : Tuple of governed substrate layers that cannot be adopted.
    safe_layers           : Tuple of substrate surfaces safely adopted.
    compensating_controls : Tuple of CC-XXX-NN control descriptions (≥2 required).
    review_cadence        : "annual" | "semi-annual" | "quarterly".
    partial_adoption_module : Dotted module path of the safe-adoption handler.
    partial_adoption_class  : Class name of the handler.
    proof_prefix          : Short prefix for proof-harness check IDs.
    """

    app_name: str
    status: GovernanceStatus
    exception_reason_code: ExceptionReasonCode
    exception_reason: str
    blocked_layers: tuple[str, ...]
    safe_layers: tuple[str, ...]
    compensating_controls: tuple[str, ...]
    review_cadence: str
    owner: str
    target_phase: str
    partial_adoption_module: str
    partial_adoption_class: str
    proof_prefix: str


# ---------------------------------------------------------------------------
# Registry — all apps_* packages must appear here
# ---------------------------------------------------------------------------

APP_REGISTRY: dict[str, GovernedAppEntry | ExceptionAppEntry | FormalExceptionEntry] = {
    # ── Governed (fully adopted) ──────────────────────────────────────────
    "apps_research": GovernedAppEntry(
        app_name="apps_research",
        status=GovernanceStatus.GOVERNED,
        runner_module="apps_research.integrations.governed_research_run",
        runner_class="GovernedResearchRun",
        capability_token="apps_research.governed_e2e.v1",
        routing_target="research_assembly",
        proof_prefix="APP",
    ),
    "apps_exec": GovernedAppEntry(
        app_name="apps_exec",
        status=GovernanceStatus.GOVERNED,
        runner_module="apps_exec.integrations.governed_exec_run",
        runner_class="GovernedExecRun",
        capability_token="apps_exec.governed_e2e.v1",
        routing_target="exec_brief_assembly",
        proof_prefix="EXE",
    ),
    "apps_rg": GovernedAppEntry(
        app_name="apps_rg",
        status=GovernanceStatus.GOVERNED,
        runner_module="agentic_core.runtime.entry.apps_rg_dispatch",
        runner_class="dispatch_apps_rg_run",
        capability_token="apps_rg.canonical_dispatch.e2e.v1",
        routing_target="resume_generation_assembly",
        proof_prefix="RG",
    ),
    "apps_lic": FormalExceptionEntry(
        app_name="apps_lic",
        status=GovernanceStatus.EXCEPTION,
        exception_reason_code=ExceptionReasonCode.PENDING_MIGRATION,
        exception_reason=(
            "apps_lic product runtime uses AG-8 canonical_dispatch spine "
            "(run_canonical_apps_lic_spine), not GovernedAppRunner. "
            "GovernedLicRun and shadow pipelines hard-deleted."
        ),
        blocked_layers=("GovernedAppRunner", "GovernedLicRun"),
        safe_layers=(
            "canonical_dispatch",
            "agentic_core spine bindings (L0/L1/L2/L3/C0/PA/Exit)",
        ),
        compensating_controls=(
            "CC-LIC-01: python -m apps_lic invokes run_canonical_apps_lic_spine only",
            "CC-LIC-02: pytest negative proofs block shadow module imports",
        ),
        review_cadence="annual",
        owner="apps_lic team",
        target_phase="N/A — canonical_dispatch is product SSOT",
        partial_adoption_module="apps_lic.runtime.dispatch.canonical_dispatch",
        partial_adoption_class="CanonicalDispatchResult",
        proof_prefix="LIC",
    ),
    # ── Formal governed exceptions (permanent; FormalExceptionEntry required) ──
    "apps_eval": FormalExceptionEntry(
        app_name="apps_eval",
        status=GovernanceStatus.EXCEPTION,
        exception_reason_code=ExceptionReasonCode.CIRCULAR_DEPENDENCY,
        exception_reason=(
            "apps_eval IS the evaluation framework; routing it through GovernedAppRunner "
            "(which calls evaluate_and_emit) would create a circular evaluation-of-evaluator "
            "dependency. Permanent exception. Compensating: BUS-T telemetry without circularity."
        ),
        blocked_layers=("L0", "L1", "C0", "L2", "L5", "L6"),
        safe_layers=("BUS_T_telemetry", "conformance_metadata"),
        compensating_controls=(
            "CC-EVAL-01: eval runs emit standard telemetry without calling evaluate_and_emit",
            "CC-EVAL-02: get_exception_record() exposes machine-readable ExceptionRecord",
            "CC-EVAL-03: module import guard — no L6 circularity triggered on import",
            "CC-EVAL-04: exception reviewed and re-certified annually by eval-platform team",
        ),
        review_cadence="annual",
        owner="eval-platform team",
        target_phase="N/A — permanent exception",
        partial_adoption_module="apps_eval.integrations.governed_eval_exception",
        partial_adoption_class="GovernedEvalException",
        proof_prefix="EVAL",
    ),
    "apps_underwriting_ai": FormalExceptionEntry(
        app_name="apps_underwriting_ai",
        status=GovernanceStatus.EXCEPTION,
        exception_reason_code=ExceptionReasonCode.REGULATORY_DOMAIN,
        exception_reason=(
            "Underwriting decisions are legally-binding credit determinations; injecting "
            "them through a generic evidence-retrieval substrate is inappropriate and a "
            "regulatory compliance risk. The app defines its own CoreAdapter + "
            "CoreHandoffPayload governance protocol. Permanent exception."
        ),
        blocked_layers=("L0", "L1", "C0", "L2", "L5"),
        safe_layers=("BUS_T_telemetry", "conformance_metadata"),
        compensating_controls=(
            "CC-UW-01: all decisions emit L6-compatible telemetry via ObservabilityAdapter",
            "CC-UW-02: CoreAdapter.prepare_handoff() provides equivalent L2 governance guarantees",
            "CC-UW-03: get_exception_record() exposes machine-readable ExceptionRecord",
            "CC-UW-04: governance protocol reviewed annually with regulatory compliance sign-off",
        ),
        review_cadence="annual",
        owner="underwriting-ai team",
        target_phase="N/A — permanent exception",
        partial_adoption_module="apps_underwriting_ai.integrations.governed_uw_exception",
        partial_adoption_class="GovernedUwException",
        proof_prefix="UW",
    ),
}


# ---------------------------------------------------------------------------
# Helpers used by the conformance gate
# ---------------------------------------------------------------------------


def get_governed_apps() -> list[GovernedAppEntry]:
    """Return all fully governed app entries."""
    return [e for e in APP_REGISTRY.values() if isinstance(e, GovernedAppEntry)]


def get_exception_apps() -> list[ExceptionAppEntry | FormalExceptionEntry]:
    """Return all exception/candidate app entries (both legacy and formal)."""
    return [e for e in APP_REGISTRY.values() if isinstance(e, (ExceptionAppEntry, FormalExceptionEntry))]


def get_formal_exception_apps() -> list[FormalExceptionEntry]:
    """Return only formal governed-exception entries."""
    return [e for e in APP_REGISTRY.values() if isinstance(e, FormalExceptionEntry)]


def get_apps_by_status(
    status: GovernanceStatus,
) -> list[GovernedAppEntry | ExceptionAppEntry | FormalExceptionEntry]:
    """Return all entries matching a given status."""
    return [e for e in APP_REGISTRY.values() if e.status == status]
