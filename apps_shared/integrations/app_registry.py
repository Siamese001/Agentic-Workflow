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
    runner_class:     Class name of the GovernedAppRunner subclass
                      (e.g. "GovernedResearchRun").
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
    """

    app_name: str
    status: GovernanceStatus
    exception_category: str
    exception_reason: str
    owner: str
    target_phase: str


# ---------------------------------------------------------------------------
# Registry — all apps_* packages must appear here
# ---------------------------------------------------------------------------

APP_REGISTRY: dict[str, GovernedAppEntry | ExceptionAppEntry] = {
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
    "apps_rfp": GovernedAppEntry(
        app_name="apps_rfp",
        status=GovernanceStatus.GOVERNED,
        runner_module="apps_rfp.integrations.governed_rfp_run",
        runner_class="GovernedRfpRun",
        capability_token="apps_rfp.governed_e2e.v1",
        routing_target="rfp_proposal_assembly",
        proof_prefix="RFP",
    ),
    # ── Candidates (pending migration — bounded exception until migrated) ─
    "apps_rg": ExceptionAppEntry(
        app_name="apps_rg",
        status=GovernanceStatus.CANDIDATE,
        exception_category="pending_migration",
        exception_reason=(
            "ResumeRequest.trace_id is present; 45+ specialized engines (ATS, achievement "
            "prioritizer, etc.) need query-construction mapping before adoption. Moderate effort."
        ),
        owner="apps_rg maintainer",
        target_phase="Phase 4",
    ),
    "apps_lic": ExceptionAppEntry(
        app_name="apps_lic",
        status=GovernanceStatus.CANDIDATE,
        exception_category="pending_migration",
        exception_reason=(
            "CampaignRequest has campaign_id/trace_id; multi-hop engine (hop_stage_registry, "
            "control_plane) requires careful query-construction mapping. Moderate effort."
        ),
        owner="apps_lic maintainer",
        target_phase="Phase 4",
    ),
    # ── Permanent exceptions (cannot adopt GovernedAppRunner) ────────────
    "apps_eval": ExceptionAppEntry(
        app_name="apps_eval",
        status=GovernanceStatus.EXCEPTION,
        exception_category="circular_dependency",
        exception_reason=(
            "apps_eval IS the evaluation framework; routing it through GovernedAppRunner "
            "(which calls evaluate_and_emit) would create a circular evaluation-of-evaluator "
            "dependency. Permanent exception."
        ),
        owner="eval-platform team",
        target_phase="N/A — permanent exception",
    ),
    "apps_underwriting_ai": ExceptionAppEntry(
        app_name="apps_underwriting_ai",
        status=GovernanceStatus.EXCEPTION,
        exception_category="regulatory_domain",
        exception_reason=(
            "Underwriting decisions are legally-binding credit determinations; injecting "
            "them through a generic evidence-retrieval substrate is inappropriate. The app "
            "defines its own CoreAdapter + CoreHandoffPayload governance protocol. Permanent exception."
        ),
        owner="underwriting-ai team",
        target_phase="N/A — permanent exception",
    ),
}


# ---------------------------------------------------------------------------
# Helpers used by the conformance gate
# ---------------------------------------------------------------------------


def get_governed_apps() -> list[GovernedAppEntry]:
    """Return all fully governed app entries."""
    return [e for e in APP_REGISTRY.values() if isinstance(e, GovernedAppEntry)]


def get_exception_apps() -> list[ExceptionAppEntry]:
    """Return all exception/candidate app entries."""
    return [e for e in APP_REGISTRY.values() if isinstance(e, ExceptionAppEntry)]


def get_apps_by_status(status: GovernanceStatus) -> list[GovernedAppEntry | ExceptionAppEntry]:
    """Return all entries matching a given status."""
    return [e for e in APP_REGISTRY.values() if e.status == status]
