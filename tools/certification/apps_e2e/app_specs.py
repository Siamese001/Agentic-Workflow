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


@dataclass(frozen=True)
class AppSpec:
    app_name: str  # canonical apps_<name> module name
    app_package: str  # python package import path; usually == app_name
    runnable: bool  # has __init__.py + __main__.py and `python -m <pkg>` works
    expected_route_form: str  # "MANAGED_WORKFLOW" | "BYPASS" | "UNKNOWN"
    expects_static_dag: bool  # is a static L3 DAG required for this app?
    expects_c0_grounding: bool  # does the app require C0 retrieval?
    expects_prompt_assembly: bool  # does the app require PA before model exec?
    expects_l2_execution: bool  # does the app require L2 sealed artifact?
    expects_durable_mutation: bool  # does the app legitimately write to L4 (UWG)?
    runs_root_glob: str  # glob under artifacts/<app>/runs/ where spine writes
    entrypoint_args: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    @property
    def entrypoint_command(self) -> str:
        base = f"python -m {self.app_package}"
        if self.entrypoint_args:
            return f"{base} {' '.join(self.entrypoint_args)}"
        return base


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
        expected_route_form="UNKNOWN",  # current run: BYPASS; will tighten when DAG ships
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
        expected_route_form="UNKNOWN",
        expects_static_dag=False,  # eval engines are evaluators, not workflows
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_eval/runs/*",
        notes="Eval engines (run_summary_renderer). No static DAG on disk; route form to be verified by first live run.",
    ),
    AppSpec(
        app_name="apps_exec",
        app_package="apps_exec",
        runnable=True,
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_exec/runs/*",
        notes="Brief assembly engine. No static DAG on disk; route form to be verified by first live run.",
    ),
    AppSpec(
        app_name="apps_lic",
        app_package="apps_lic",
        runnable=True,
        expected_route_form="MANAGED_WORKFLOW",
        expects_static_dag=True,  # HOP* engines suggest a managed pipeline
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_lic/runs/*",
        notes="HOP1-HOP6 pipeline (apps_lic/config/hop_pipeline.py). Honest gap: canonical l3_dag.yaml not yet shipped — fail-closed reports this until it does.",
    ),
    AppSpec(
        app_name="apps_qna",
        app_package="apps_qna",
        runnable=True,
        expected_route_form="BYPASS",  # pack-builder/router smell
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_l2_execution=False,
        entrypoint_args=(
            "build",
            "--config",
            "apps_qna/tests/fixtures/synthetic_mini/interview.yaml",
            "--dry-run",
        ),
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_qna/runs/*",
        notes="Pack builder + router. Has route_registry.yaml only (no l3_dag.yaml) — confirmed BYPASS route.",
    ),
    AppSpec(
        app_name="apps_research",
        app_package="apps_research",
        runnable=True,
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_research/runs/*",
        notes="company_brief_engine + governed_research_run. No static DAG on disk; route form TBD by first live run.",
    ),
    AppSpec(
        app_name="apps_rfp",
        app_package="apps_rfp",
        runnable=True,
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=True,
        expects_prompt_assembly=True,
        expects_l2_execution=True,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_rfp/runs/*",
        notes="proposal_assembly_engine + governed_rfp_run. No static DAG on disk; route form TBD by first live run.",
    ),
    AppSpec(
        app_name="apps_underwriting_ai",
        app_package="apps_underwriting_ai",
        runnable=False,  # no __init__.py / __main__.py — skeleton only
        expected_route_form="UNKNOWN",
        expects_static_dag=False,
        expects_c0_grounding=False,
        expects_prompt_assembly=False,
        expects_l2_execution=False,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_underwriting_ai/runs/*",
        notes="Skeleton-only — discovered=true, runnable=false. HOP engines exist but no entrypoint.",
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
