"""apps_rg generation entrypoints — prevents confusing R4 CLI with modular lane orchestration.

ENTRYPOINT_MATRIX (code-derived; keep in sync with ``apps_rg.l2_recipe.r4_generation_route``):

1) **Integrated R4 product (golden governed spine)**
   - Command/import: ``python -m apps_rg`` → ``apps_rg.__main__.main`` →
     ``agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run`` →
     ``apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives`` →
     ``agentic_core...run_integrated_single_action_spine``
   - Runner: R4 pipeline + apps_rg L2 recipe
   - Declared **canonical proven** execution style: **modular_section_lanes**
     (see ``R4_RECIPE_GENERATION_EXECUTION_STYLE``) — seven section lanes + merge when
     ``APPS_RG_R4_GENERATION_MODE=modular_section_lanes``.
   - **Default** runtime mode when env unset: **modular_section_lanes**
     → ``GenerateResumeStep`` uses ``run_modular_resume_generation`` (no envelope)
   - **Retired:** ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume`` raises (modular only)
   - Provider call expectation (modular mode): **per-lane** structured generation (no
     full-résumé provider lane)
   - RetiredProvider full résumé in one call: **only in legacy envelope mode** (single CPA)
   - RetiredProvider sections-only: **yes** in modular mode
   - Deterministic merge: **yes** for modular path (``modular_rg_output_builder``)
   - Product outputs: JSON + manifest (``ResumeArtifactGateStep``); DOCX retired
   - Status: **supported** canonical product entry

2) **Offline modular lane library (tests only)**
   - Import: ``tests.helpers.offline_lane_orchestration.run_orchestration``
   - No ``python -m apps_rg.runtime.internal.lane_batch`` command surface
   - Status: **library-only** batch helper; product proof uses ``python -m apps_rg`` only

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
from apps_rg.runtime.internal import lane_batch as lb


def test_canonical_product_entry_is_dispatch_apps_rg_run() -> None:
    mod = importlib.import_module("agentic_core.runtime.entry.apps_rg_dispatch")
    assert hasattr(mod, "dispatch_apps_rg_run")
    src = inspect.getsource(mod.dispatch_apps_rg_run)
    assert "run_canonical_apps_rg_from_cli_primitives" in src


def test_r4_ssot_modular_requires_no_full_envelope_cpa() -> None:
    assert rr.R4_RECIPE_GENERATION_EXECUTION_STYLE == "modular_section_lanes"
    assert rr.R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA is False


def test_generate_resume_step_modular_only() -> None:
    cls_src = inspect.getsource(GenerateResumeStep)
    assert "run_modular_resume_generation" in cls_src
    assert "from apps_rg.runtime.bindings.l2_envelope_adapter import run_apps_rg_l2_envelope" not in cls_src
    assert "resolve_apps_rg_r4_generation_mode" in cls_src


def test_modular_orchestrator_is_not_core_r4_dispatch() -> None:
    """Lane orchestrator must remain a distinct module from integrated R4."""
    assert rr.MODULAR_SECTION_ORCHESTRATOR_MODULE == "tests.helpers.offline_lane_orchestration"
    canon_src = inspect.getsource(
        importlib.import_module("apps_rg.runtime.orchestration.canonical_dispatch").run_canonical_apps_rg_from_cli_primitives
    )
    assert "orchestrate_full_resume" not in canon_src


def test_lane_batch_exports_seven_lane_modules() -> None:
    assert len(lb.LANE_MODULES) == 7
    assert "headline_lane" in lb.LANE_MODULES[0]


def test_golden_r4_ssot_declares_modular_canonical() -> None:
    assert rr.R4_RECIPE_GENERATION_EXECUTION_STYLE == "modular_section_lanes"
    assert rr.CANONICAL_PROVEN_GENERATION_ROUTE == "modular_section_lanes"
    assert rr.DEFAULT_RUNTIME_GENERATION_MODE == "modular_section_lanes"
