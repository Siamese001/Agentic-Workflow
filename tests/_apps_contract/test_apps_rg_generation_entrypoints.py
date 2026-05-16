"""apps_rg generation entrypoints — prevents confusing R4 CLI with modular lane orchestration.

ENTRYPOINT_MATRIX (code-derived; keep in sync with ``apps_rg.l2_recipe.r4_generation_route``):

1) **Integrated R4 product (golden governed spine)**
   - Command/import: ``python -m apps_rg`` → ``apps_rg.__main__.main`` →
     ``agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run`` →
     ``apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives`` →
     ``agentic_core...run_integrated_r4_deterministic_pipeline``
   - Runner: R4 pipeline + apps_rg L2 recipe
   - Declared **canonical proven** execution style: **modular_section_lanes**
     (see ``R4_RECIPE_GENERATION_EXECUTION_STYLE``) — seven section lanes + merge when
     ``APPS_RG_R4_GENERATION_MODE=modular_section_lanes``.
   - **Default** runtime mode when env unset: **modular_section_lanes**
     → ``GenerateResumeStep`` uses ``run_modular_resume_generation`` (no envelope)
   - **Explicit rollback:** ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume`` →
     ``run_apps_rg_l2_envelope`` + tailor-existing CPA
   - Provider call expectation (modular mode): **per-lane** structured generation (no
     full-résumé provider lane)
   - Qwen full résumé in one call: **only in legacy envelope mode** (single CPA)
   - Qwen sections-only: **yes** in modular mode
   - Deterministic merge: **yes** for modular path (``modular_rg_output_builder``)
   - DOCX export: yes (``DocxExportStep`` + gate) when generation succeeds
   - Status: **supported** canonical product entry

2) **Offline modular lane orchestrator (not R4 dispatch surface)**
   - Command: ``python -m apps_rg.runtime.orchestrate_full_resume``
   - Runner: ``apps_rg.runtime.orchestrate_full_resume.run_orchestration``
   - Execution style: **modular_section_l2** naming in subprocess lane modules (seven ``*_dispatch``)
   - Provider call expectation: **per-lane** (subprocess-dispatched lanes)
   - Qwen full résumé in one call: **no** (lane-scoped generation)
   - Qwen sections-only: **yes**
   - Deterministic merge / locked copy: **yes** (orchestrator pipeline)
   - DOCX: **yes** (runtime_proofs path)
   - Status: **supported** for offline proofs; **not** the same module path as ``dispatch_apps_rg_run``

3) **Direct envelope adapter (tests / advanced callers)**
   - Import: ``apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope``
   - Execution style: **monolithic_full_resume** (single CPA → provider)
   - Status: **test_fixture_only** / integration helper — not the CLI entry

4) **L2 binding ``l2_execute_apps_rg``**
   - May delegate to envelope per feature flag; still **monolithic** when using v4 envelope path.
"""

from __future__ import annotations

import importlib
import inspect

from apps_rg.l2_recipe import r4_generation_route as rr
from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.runtime import orchestrate_full_resume as ofr


def test_canonical_product_entry_is_dispatch_apps_rg_run() -> None:
    mod = importlib.import_module("agentic_core.runtime.entry.apps_rg_dispatch")
    assert hasattr(mod, "dispatch_apps_rg_run")
    src = inspect.getsource(mod.dispatch_apps_rg_run)
    assert "run_canonical_apps_rg_from_cli_primitives" in src


def test_r4_ssot_modular_requires_no_full_envelope_cpa() -> None:
    assert rr.R4_RECIPE_GENERATION_EXECUTION_STYLE == "modular_section_lanes"
    assert rr.R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA is False


def test_generate_resume_step_supports_legacy_envelope_and_modular() -> None:
    cls_src = inspect.getsource(GenerateResumeStep)
    assert "run_apps_rg_l2_envelope" in cls_src
    assert "run_modular_resume_generation" in cls_src
    assert "resolve_apps_rg_r4_generation_mode" in cls_src


def test_modular_orchestrator_is_not_core_r4_dispatch() -> None:
    """Lane orchestrator must remain a distinct module from integrated R4."""
    assert rr.MODULAR_SECTION_ORCHESTRATOR_MODULE == "apps_rg.runtime.orchestrate_full_resume"
    canon_src = inspect.getsource(
        importlib.import_module("apps_rg.runtime.orchestration.canonical_dispatch").run_canonical_apps_rg_from_cli_primitives
    )
    assert "orchestrate_full_resume" not in canon_src


def test_modular_orchestrator_exports_seven_lane_modules() -> None:
    assert len(ofr.LANE_MODULES) == 7
    assert "headline_dispatch" in ofr.LANE_MODULES[0]


def test_golden_r4_ssot_declares_modular_canonical() -> None:
    assert rr.R4_RECIPE_GENERATION_EXECUTION_STYLE == "modular_section_lanes"
    assert rr.CANONICAL_PROVEN_GENERATION_ROUTE == "modular_section_lanes"
    assert rr.DEFAULT_RUNTIME_GENERATION_MODE == "modular_section_lanes"
