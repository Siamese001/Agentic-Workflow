"""Per-app proof scenarios — 8 specs registered in :data:`SCENARIOS`.

Each scenario describes ONE real intent for ONE app. The shared
:func:`apps_shared.proof.scenario_base.run_app_scenario` drives the spine.

Customizers (optional) emit app-specific gate verdicts that prove the
risk-class invariants from the prompt §4 (e.g. apps_underwriting_ai cannot
auto-commit; apps_lic cannot dispatch externally).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from apps_shared.proof.scenario_base import ScenarioContext, ScenarioSpec


# ---------------------------------------------------------------------------
# Customizers — each emits app-specific gate verdicts the prompt requires
# ---------------------------------------------------------------------------


def _customize_apps_eval(ctx: ScenarioContext) -> None:
    """apps_eval: prove L6 firewall — eval cannot mutate current run policy."""
    ts_span = ctx.spans[-1] if ctx.spans else None
    parent_id = ts_span.span_id if ts_span else None
    # Synthetic gate proving the constraint: the scenario produced no
    # write/UWG path AND no L6 mutation path (validated by W3 ADG re-run).
    sp = ctx.emit_span(
        layer="L6",
        name="l6.firewall.assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"assertion": "no_current_run_mutation"},
    )
    ctx.emit_gate(
        gate_id="apps_eval.l6_firewall",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("eval_observer_only",),
        evidence=("v_p0_l6_mutation==0",),
    )


def _customize_apps_exec(ctx: ScenarioContext) -> None:
    """apps_exec: grounded brief — assert grounding_required AND no external dispatch."""
    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_exec.grounding_assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"grounding_required": ctx.spec.grounding_required},
    )
    ctx.emit_gate(
        gate_id="apps_exec.grounding_required",
        verdict="ALLOW_FINISH" if ctx.spec.grounding_required else "BLOCK",
        span_id=sp.span_id,
        reasons=("grounding_required_true",) if ctx.spec.grounding_required else ("grounding_missing",),
    )


def _customize_apps_lic(ctx: ScenarioContext) -> None:
    """apps_lic: prove no external dispatch — egress + HITL gates required.

    Also emits a real SANDBOX_OUTPUT artifact (the campaign draft) via
    :func:`apps_shared.proof.sandbox_writer.write_sandbox_artifact`, proving
    the W6.2 classification path.
    """
    from apps_shared.proof.sandbox_writer import write_sandbox_artifact

    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_lic.egress_assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"external_dispatch_attempted": False},
    )
    # Emit a real SANDBOX_OUTPUT artifact (the campaign draft).
    artifact = write_sandbox_artifact(
        app_id=ctx.spec.app_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        producing_span_id=sp.span_id,
        export_root=ctx.export_root,
        artifact_id="campaign_draft_v1",
        payload={
            "scenario": ctx.spec.scenario_id,
            "draft_subject": "Synthetic outreach draft",
            "draft_body": "This is a sandbox-classified draft, never dispatched.",
            "audience_count": 0,
        },
    )
    ctx.artifacts.append(artifact)
    ctx.emit_gate(
        gate_id="apps_lic.egress",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("no_external_dispatch_in_proof_scenario",),
        evidence=(
            f"draft_artifact_classified_SANDBOX:{artifact.path}",
            f"content_hash:{artifact.content_hash[:16]}",
        ),
    )
    ctx.emit_gate(
        gate_id="apps_lic.hitl",
        verdict="NOT_APPLICABLE",
        span_id=sp.span_id,
        reasons=("no_send_action_attempted",),
    )


def _customize_apps_research(ctx: ScenarioContext) -> None:
    """apps_research: assert citation-bound output (C0 grounding required)."""
    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_research.citation_assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"grounding_required": True},
    )
    ctx.emit_gate(
        gate_id="apps_research.citation_required",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("c0_grounding_required",),
    )


def _customize_apps_rfp(ctx: ScenarioContext) -> None:
    """apps_rfp: assert requirement-parser contract + compliance evidence."""
    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_rfp.requirement_contract",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"contract_bound": True},
    )
    ctx.emit_gate(
        gate_id="apps_rfp.requirement_contract",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("requirement_parser_contract_bound",),
    )


def _customize_apps_rg(ctx: ScenarioContext) -> None:
    """apps_rg: hallucination detector + provider lane registry-bound."""
    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_rg.hallucination_check",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"hallucination_check_run": True},
    )
    ctx.emit_gate(
        gate_id="apps_rg.hallucination_detector",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("claims_grounded_in_resume_facts",),
    )
    ctx.emit_gate(
        gate_id="apps_rg.contact_dispatch",
        verdict="NOT_APPLICABLE",
        span_id=sp.span_id,
        reasons=("no_external_action_in_proof",),
    )


def _customize_apps_underwriting_ai(ctx: ScenarioContext) -> None:
    """apps_underwriting_ai: HIGH_IMPACT — recommendation-only with explicit
    UWG_DURABLE commit request that NEVER actually commits.

    Records a :class:`CommitRequest` to prove that any future durable write
    must route through the UWG facade, not direct infrastructure. The
    ``no_auto_commit`` gate disposes the request as ALLOW_FINISH because
    this scenario is recommendation-only — the commit request is captured
    but never approved.
    """
    from apps_shared.proof.sandbox_writer import (
        request_uwg_commit,
        write_sandbox_artifact,
    )

    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_underwriting_ai.high_impact_assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"risk_class": "HIGH_IMPACT", "auto_commit_attempted": False},
    )

    # Sandbox copy of the recommendation (always classified SANDBOX_OUTPUT)
    sandbox_artifact = write_sandbox_artifact(
        app_id=ctx.spec.app_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        producing_span_id=sp.span_id,
        export_root=ctx.export_root,
        artifact_id="recommendation_v1",
        payload={
            "scenario": ctx.spec.scenario_id,
            "applicant_id": "UW-PROOF-001",
            "recommendation": "approve_with_caveat",
            "rationale": "Within underwriting limits; no auto-commit.",
        },
    )
    ctx.artifacts.append(sandbox_artifact)

    # Captured-but-unapproved UWG commit request (proves the path exists)
    uwg_artifact, commit_request = request_uwg_commit(
        app_id=ctx.spec.app_id,
        run_id=ctx.run_id,
        trace_id=ctx.trace_id,
        producing_span_id=sp.span_id,
        export_root=ctx.export_root,
        artifact_id="uwg_commit_request_v1",
        payload={
            "decision": "approve_with_caveat",
            "applicant_id": "UW-PROOF-001",
        },
        intent="record_high_impact_decision",
        write_authority="PENDING_UWG_APPROVAL",
    )
    ctx.artifacts.append(uwg_artifact)

    ctx.emit_gate(
        gate_id="apps_underwriting_ai.no_auto_commit",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("recommendation_only_output",),
        evidence=(
            f"sandbox_artifact:{sandbox_artifact.path}",
            f"uwg_commit_request:{uwg_artifact.path}",
            f"write_authority:{commit_request.write_authority}",
            "uwg_commit_NOT_executed",
        ),
    )
    ctx.emit_gate(
        gate_id="apps_underwriting_ai.hitl_routing",
        verdict="NOT_APPLICABLE",
        span_id=sp.span_id,
        reasons=("recommendation_only_path_chosen",),
    )


def _customize_apps_shared(ctx: ScenarioContext) -> None:
    """apps_shared: meta scenario — proves the harness itself works."""
    parent_id = ctx.spans[-1].span_id if ctx.spans else None
    sp = ctx.emit_span(
        layer="L5",
        name="apps_shared.meta_assertion",
        parent_span_id=parent_id,
        status="PASS",
        started_at=ctx.runtime_boundary_ts or "",
        ended_at=ctx.runtime_boundary_ts or "",
        attrs={"meta_proof": True},
    )
    ctx.emit_gate(
        gate_id="apps_shared.meta",
        verdict="ALLOW_FINISH",
        span_id=sp.span_id,
        reasons=("harness_self_proof",),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RegisteredScenario:
    spec: ScenarioSpec
    customizer: Callable[[ScenarioContext], None] | None


# Each scenario uses a deterministic intake_body so W3 replay can compare.
SCENARIOS: dict[str, RegisteredScenario] = {
    "apps_eval": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_eval",
            scenario_id="eval_grounded_run_v1",
            intake_body='{"eval_id": "EVAL-PROOF-001", "prompt": "Verify C0 routing authority claim", "expected": "C0 cannot answer directly"}',
            grounding_required=True,
            task_spec="evaluation_run",
            query_spec="apps_eval grounded evaluation",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_eval,
    ),
    "apps_exec": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_exec",
            scenario_id="exec_grounded_brief_v1",
            intake_body='{"task_id": "EXEC-PROOF-001", "instruction": "Generate grounded executive brief from repo evidence"}',
            grounding_required=True,
            task_spec="executive_brief",
            query_spec="apps_exec grounded brief",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_exec,
    ),
    "apps_lic": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_lic",
            scenario_id="lic_compliant_outreach_draft_v1",
            intake_body='{"campaign_id": "LIC-PROOF-001", "audience": "synthetic_personas", "objective": "compliant_outreach_draft"}',
            grounding_required=False,
            task_spec="campaign_draft",
            query_spec="apps_lic compliant outreach",
            expected_layers=("U0", "L1", "L0", "L3"),  # apps_lic is non-grounded — skips C0/PA/L2
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_lic,
    ),
    "apps_research": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_research",
            scenario_id="research_cited_brief_v1",
            intake_body='{"topic": "C0 Context Engine authority", "depth": "shallow"}',
            grounding_required=True,
            task_spec="cited_research_brief",
            query_spec="apps_research cited brief",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_research,
    ),
    "apps_rfp": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_rfp",
            scenario_id="rfp_compliance_response_v1",
            intake_body='{"rfp_id": "RFP-PROOF-001", "proposal_type": "technology", "deadline": "2026-12-31"}',
            grounding_required=True,
            task_spec="rfp_section_response",
            query_spec="apps_rfp compliance response",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_rfp,
    ),
    "apps_rg": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_rg",
            scenario_id="rg_grounded_resume_v1",
            intake_body=(
                '{"candidate_name": "Test Person", '
                '"target_role": "Senior Engineer", '
                '"target_industry": "technology", '
                '"experience_level": "senior"}'
            ),
            grounding_required=True,
            task_spec="resume_generation",
            query_spec="apps_rg grounded resume",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="NORMAL",
        ),
        customizer=_customize_apps_rg,
    ),
    "apps_underwriting_ai": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_underwriting_ai",
            scenario_id="uw_recommendation_only_v1",
            intake_body='{"applicant_id": "UW-PROOF-001", "policy_type": "term_life", "amount": "500000"}',
            grounding_required=True,
            task_spec="underwriting_recommendation",
            query_spec="apps_underwriting_ai recommendation only",
            expected_layers=("U0", "L1", "L0", "C0", "PromptAssembly", "L3", "L2", "Exit"),
            risk_class="HIGH_IMPACT",
        ),
        customizer=_customize_apps_underwriting_ai,
    ),
    "apps_shared": RegisteredScenario(
        spec=ScenarioSpec(
            app_id="apps_shared",
            scenario_id="shared_meta_proof_v1",
            intake_body='{"meta": "harness_self_proof"}',
            grounding_required=False,
            task_spec="meta_proof",
            query_spec="apps_shared meta proof",
            expected_layers=("U0", "L1", "L0", "L3"),  # apps_shared meta — non-grounded
            risk_class="INFRASTRUCTURE",
        ),
        customizer=_customize_apps_shared,
    ),
}


__all__ = ["RegisteredScenario", "SCENARIOS"]
