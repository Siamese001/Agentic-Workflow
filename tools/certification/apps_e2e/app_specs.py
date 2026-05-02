"""Declarative specs for every apps_* package the harness touches.

An AppSpec is the only per-app artifact in this harness. It is purely
declarative — it never executes the app, never reads spine artifacts,
never decides success/failure. The shared core does all of that.

Adding a new app = one ~10-line entry below. Removing an app = one entry
deletion. There is no per-app harness script.

Apps-as-overlay invariant: AppSpecs live HERE, in tools/certification/,
not inside apps_*/. Harness coupling never lands in app code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


# ---------------------------------------------------------------------------
# Two-gate certification additions (plan apps-e2e-two-gate-certification-d8b3a1
# §4, amendments 1-7 dated 2026-05-02). All new fields are additive and
# default to backward-compatible values. Legacy expects_* fields remain the
# source of truth when the parallel *_required field is None.
# ---------------------------------------------------------------------------

# Execution form enum (string values to keep AppSpec frozen-dataclass-friendly).
# NOT to be confused with RouteContract.execution_form (legacy upstream field
# that may still emit "BYPASS" — that string is a path outcome, not a form).
EXECUTION_FORM_TERMINAL_SHORTCIRCUIT = "TERMINAL_SHORTCIRCUIT"
EXECUTION_FORM_SINGLE_STEP = "SINGLE_STEP"
EXECUTION_FORM_MANAGED_WORKFLOW = "MANAGED_WORKFLOW"
EXECUTION_FORM_UNKNOWN = "UNKNOWN"
VALID_EXECUTION_FORMS = frozenset({
    EXECUTION_FORM_TERMINAL_SHORTCIRCUIT,
    EXECUTION_FORM_SINGLE_STEP,
    EXECUTION_FORM_MANAGED_WORKFLOW,
    EXECUTION_FORM_UNKNOWN,
})

# L3 path outcome enum.
L3_PATH_RAN = "RAN"
L3_PATH_BYPASSED = "BYPASSED"
L3_PATH_UNKNOWN = "UNKNOWN"
VALID_L3_PATHS = frozenset({L3_PATH_RAN, L3_PATH_BYPASSED, L3_PATH_UNKNOWN})


@dataclass(frozen=True)
class AppSpec:
    # ----- existing fields (preserved for backward compat) -----
    app_name: str  # canonical apps_<name> module name
    app_package: str  # python package import path; usually == app_name
    runnable: bool  # has __init__.py + __main__.py and `python -m <pkg>` works
    expected_route_form: str  # legacy: "MANAGED_WORKFLOW" | "BYPASS" | "UNKNOWN" (NOT used for cert)
    expects_static_dag: bool  # is a static L3 DAG required for this app?
    expects_c0_grounding: bool  # legacy alias for c0_required (see effective_*)
    expects_prompt_assembly: bool  # legacy alias for prompt_assembly_required
    expects_l2_execution: bool  # legacy alias for l2_required
    expects_durable_mutation: bool  # legacy alias for uwg_required
    runs_root_glob: str  # glob under artifacts/<app>/runs/ where spine writes
    entrypoint_args: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    # ----- two-gate certification fields (plan §4) -----
    # T2/T3 enforcement target. False = bundle emission only, no cert.
    certification_required: bool = True
    # Run-shape: TERMINAL_SHORTCIRCUIT | SINGLE_STEP | MANAGED_WORKFLOW | UNKNOWN
    expected_execution_form: str = EXECUTION_FORM_UNKNOWN
    # L3 receipt outcome: RAN | BYPASSED | UNKNOWN. Independent of execution_form.
    expected_l3_path: str = L3_PATH_UNKNOWN
    # Per-stage required flags. None = fall back to legacy expects_* alias.
    c0_required: bool | None = None
    prompt_assembly_required: bool | None = None
    l2_required: bool | None = None
    l3_required: bool | None = None  # None = derived from expected_l3_path == "RAN"
    uwg_required: bool | None = None
    # L6 exhaust (RuntimeExhaustBundle) — separate from Exit (which is implicit-always).
    l6_exhaust_required: bool = True
    # OTEL or runtime-ADG trace.
    otel_required: bool = True
    # NOTE: exit_required is implicit and ALWAYS True for certification. Not a
    # configurable field. ExitReviewPacket / X3 disposition is NOT an L6
    # artifact; it is the exit-control contract that must precede any L6
    # emission. (See plan amendment 1.)

    # ----- waiver block (all-or-nothing) -----
    waiver_reason: str | None = None
    waiver_owner: str | None = None
    waiver_expiry: str | None = None  # ISO-8601 UTC

    @property
    def entrypoint_command(self) -> str:
        base = f"python -m {self.app_package}"
        if self.entrypoint_args:
            return f"{base} {' '.join(self.entrypoint_args)}"
        return base


# ---------------------------------------------------------------------------
# Effective-flag resolvers — verifier MUST go through these, never read the
# new *_required field directly. Preserves backward compat with rows that
# only set the legacy expects_* alias.
# ---------------------------------------------------------------------------

def effective_c0_required(spec: AppSpec) -> bool:
    if spec.c0_required is not None:
        return spec.c0_required
    return spec.expects_c0_grounding


def effective_prompt_assembly_required(spec: AppSpec) -> bool:
    if spec.prompt_assembly_required is not None:
        return spec.prompt_assembly_required
    return spec.expects_prompt_assembly


def effective_l2_required(spec: AppSpec) -> bool:
    if spec.l2_required is not None:
        return spec.l2_required
    return spec.expects_l2_execution


def effective_l3_required(spec: AppSpec) -> bool:
    if spec.l3_required is not None:
        return spec.l3_required
    # Default: L3 receipt is required iff L3 actually ran. A bypassed L3
    # path requires a bypass receipt, not an L3 runtime receipt; the
    # required_receipts resolver handles that separately.
    return spec.expected_l3_path == L3_PATH_RAN


def effective_uwg_required(spec: AppSpec) -> bool:
    if spec.uwg_required is not None:
        return spec.uwg_required
    return spec.expects_durable_mutation


def effective_l6_exhaust_required(spec: AppSpec) -> bool:
    return spec.l6_exhaust_required


def effective_otel_required(spec: AppSpec) -> bool:
    return spec.otel_required


def has_waiver(spec: AppSpec) -> bool:
    """True iff every waiver triple field is set (non-empty). Validity (e.g.
    expiry-in-future) is checked separately by tools.certification.apps_e2e.waivers.
    """
    return bool(spec.waiver_reason and spec.waiver_owner and spec.waiver_expiry)


# ---------------------------------------------------------------------------
# Canonical app registry — SSOT for which apps the harness covers.
#
# Status of each app's expected_* fields is derived from initial inspection
# of apps_*/config/, apps_*/integrations/, and apps_*/engines/. Where
# uncertain, the field is marked with a TODO note and the harness will
# emit a spec-uncertainty entry into blocking_gaps until the spec is
# tightened by W3 verification runs.
# ---------------------------------------------------------------------------
APP_SPECS: tuple[AppSpec, ...] = (
    AppSpec(
        app_name="apps_rg",
        app_package="apps_rg",
        runnable=True,
        expected_route_form="UNKNOWN",  # legacy field; not used for cert
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,  # W6
        expected_l3_path=L3_PATH_BYPASSED,  # W6: RouteContract emitted, no DAG-driven L3
        expects_static_dag=True,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_rg/runs/*",
        entrypoint_args=(
            "--target-company", "Blend360",
            "--target-role", "SVP, Agentic Transformation",
            "--manual-brief", "apps_rg/scripts/company_research.example.json",
            "--auto-research-tavily",
        ),
        notes="Reference app. Static DAG search at apps_rg/config/{route_registry,l3_dag}.yaml.",
    ),
    AppSpec(
        app_name="apps_eval",
        app_package="apps_eval",
        runnable=True,
        expected_route_form="SINGLE_STEP",
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,  # W6
        expected_l3_path=L3_PATH_BYPASSED,  # W6
        expects_static_dag=False,  # eval engines are evaluators, not workflows
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_eval/runs/*",
        notes="Eval engines (run_summary_renderer). Live-cert path wired via apps_shared.spine_emission (plan apps-e2e-spine-cert-wireup-e1c4d7 W3).",
    ),
    AppSpec(
        app_name="apps_exec",
        app_package="apps_exec",
        runnable=True,
        expected_route_form="SINGLE_STEP",
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,  # W6
        expected_l3_path=L3_PATH_BYPASSED,  # W6
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_exec/runs/*",
        notes="Brief assembly engine. Live-cert path wired via apps_shared.spine_emission (plan apps-e2e-spine-cert-wireup-e1c4d7 W2).",
    ),
    AppSpec(
        app_name="apps_lic",
        app_package="apps_lic",
        runnable=True,
        expected_route_form="MANAGED_WORKFLOW",
        expected_execution_form=EXECUTION_FORM_MANAGED_WORKFLOW,  # W6
        expected_l3_path=L3_PATH_RAN,  # W6: 9-HOP pipeline with canonical l3_dag.yaml
        expects_static_dag=True,  # HOP* engines suggest a managed pipeline
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_lic/runs/*",
        notes="HOP1-HOP9 pipeline (apps_lic/config/hop_pipeline.py). Canonical l3_dag.yaml shipped 2026-05-01. Live-cert path wired via apps_shared.spine_emission MANAGED_WORKFLOW shape (plan apps-e2e-spine-cert-wireup-e1c4d7 W6); emits l3_orchestration_receipt with static_dag_hash bound to l3_dag.yaml sha256.",
    ),
    AppSpec(
        app_name="apps_qna",
        app_package="apps_qna",
        runnable=True,
        # 2026-05-02 post-W10: flipped from WAIVED_NOT_RUNTIME_APP to full
        # runtime cert. User decision: even though apps_qna's product
        # correctness is ledger-backed (constitutional §29: namespace_bandit +
        # Wilson CI + apps_qna_pack_lifecycle ledger), the runtime-contract
        # plumbing (route selection, plan shape, exit discipline, OTEL trace)
        # IS provable and WILL be certified. Wired via apps_qna/__main__.py
        # --apps-e2e-live flag + apps_qna/config/cert_route_registry.yaml
        # (SINGLE_STEP sibling to the product route_registry.yaml) + the
        # shared apps_shared.spine_emission.governed_run context manager.
        # The existing ledger-backed product correctness contract is
        # UNCHANGED and continues to be the authoritative signal for pack
        # quality; the runtime cert proves the envelope, not the contents.
        certification_required=True,
        expected_route_form="SINGLE_STEP",
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,
        expected_l3_path=L3_PATH_BYPASSED,
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_qna/runs/*",
        notes="SINGLE_STEP pack builder. cert_route_registry.yaml (SINGLE_STEP sibling to product route_registry.yaml) + --apps-e2e-live wiring via apps_qna/__main__.py emits the 9 required receipts through apps_shared.spine_emission. Product correctness remains ledger-backed per constitutional §29.",
    ),
    AppSpec(
        app_name="apps_research",
        app_package="apps_research",
        runnable=True,
        expected_route_form="SINGLE_STEP",
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,  # W6
        expected_l3_path=L3_PATH_BYPASSED,  # W6
        expects_static_dag=False,
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_research/runs/*",
        notes="company_brief_engine + governed_research_run. Live-cert path wired via apps_shared.spine_emission (plan apps-e2e-spine-cert-wireup-e1c4d7 W4).",
    ),
    AppSpec(
        app_name="apps_rfp",
        app_package="apps_rfp",
        runnable=True,
        expected_route_form="SINGLE_STEP",
        expected_execution_form=EXECUTION_FORM_SINGLE_STEP,  # W6
        expected_l3_path=L3_PATH_BYPASSED,  # W6
        expects_static_dag=False,
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        entrypoint_args=("--apps-e2e-live",),
        runs_root_glob="artifacts/apps_rfp/runs/*",
        notes="proposal_assembly_engine + governed_rfp_run. Live-cert path wired via apps_shared.spine_emission (plan apps-e2e-spine-cert-wireup-e1c4d7 W5).",
    ),
    AppSpec(
        app_name="apps_underwriting_ai",
        app_package="apps_underwriting_ai",
        runnable=False,  # See waiver_reason — entrypoint exists; verdict logic stubbed.
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_l2_execution=False,
        expects_durable_mutation=False,
        # W6 — skeleton waiver. Plan: apps-e2e-two-gate-certification-d8b3a1 §8.8.
        # 2026-05-02 W8 (plan apps-fort-knox-parity-c5d9a3 §20 OPEN-2):
        # the placeholder-verdict-logic blocker is now CLOSED. The package
        # has a real DeterministicRiskScorer (apps_underwriting_ai/engines/
        # risk_scorer.py) with named thresholds, transparent breakdown, 18
        # tests pinning every band, and explicit non-regulatory disclaimer
        # in its module docstring. The remaining blocker for full cert
        # promotion is SPINE EMISSION wiring — the harness expects 6 runtime
        # artifacts (route_contract, l1_plan, l3_receipt OR bypass, exit_review
        # OR x3_disposition, exhaust_bundle, otel_trace) which require
        # apps_shared.spine_emission MANAGED_WORKFLOW wiring (see
        # apps_research/integrations/governed_research_run.py + plan
        # apps-e2e-spine-cert-wireup-e1c4d7 W6 for the canonical pattern).
        # That wiring is multi-day separate-plan work, not Fort Knox plumbing.
        waiver_reason=(
            "Runtime pipeline wired AND deterministic risk-scoring rubric "
            "shipped 2026-05-02 (apps_underwriting_ai/engines/risk_scorer.py). "
            "Waiver retained because the runtime apps_shared.spine_emission "
            "wiring (route_contract + l1_plan + l3_receipt + exit_review + "
            "exhaust_bundle + otel_trace artifacts) is not yet emitted. "
            "Reference pattern: apps_research/integrations/governed_research_run.py "
            "+ apps_shared.spine_emission MANAGED_WORKFLOW shape per plan "
            "apps-e2e-spine-cert-wireup-e1c4d7 W6. See plan "
            "apps-fort-knox-parity-c5d9a3 §20 OPEN-2 for the path to certification."
        ),
        waiver_owner="apps_underwriting_ai-owner@agentic-workflow.local",
        waiver_expiry="2027-01-01T00:00:00Z",
        runs_root_glob="artifacts/apps_underwriting_ai/runs/*",
        notes="Runtime pipeline + DeterministicRiskScorer wired (verified 2026-05-02: `python -m apps_underwriting_ai --demo` runs end-to-end and emits a decision packet with risk_score=28.33→APPROVE for the synthetic demo input). Waiver now held by spine emission wiring (apps_shared.spine_emission MANAGED_WORKFLOW pattern). Cert-promotion path: plan apps-fort-knox-parity-c5d9a3 §20 OPEN-2.",
    ),
)


def find_spec(app_name: str) -> AppSpec | None:
    for spec in APP_SPECS:
        if spec.app_name == app_name:
            return spec
    return None


def runnable_specs() -> Sequence[AppSpec]:
    return tuple(s for s in APP_SPECS if s.runnable)


__all__ = ["AppSpec", "APP_SPECS", "find_spec", "runnable_specs"]
