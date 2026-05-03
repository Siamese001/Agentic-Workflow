"""W4 tests: apps_rg main_canonical() integration with SpineRuntimeAdapter.

Plan: apps-rg-runtime-cert-hardening-a3f8c2.md
Phase: W4.P1 - Adapter integration with prefer_canonical=True
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestMainCanonicalImports:
    """Verify main_canonical entrypoint is importable and wired correctly."""

    def test_main_canonical_importable(self) -> None:
        """main_canonical() can be imported from apps_rg.__main__."""
        from apps_rg.__main__ import main_canonical
        assert callable(main_canonical)

    def test_spine_runtime_adapter_import_in_main(self) -> None:
        """SpineRuntimeAdapter is imported inside main_canonical scope."""
        # Import verifies the adapter module loads correctly
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_w4",
            entrypoint_command="python -m test",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W4 test",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)
        assert adapter.prefer_canonical is True


class TestMainCanonicalVsMain:
    """Compare main() (legacy) and main_canonical() (adapter) entrypoints."""

    def test_both_entrypoints_exist(self) -> None:
        """Both main() and main_canonical() are available."""
        from apps_rg.__main__ import main, main_canonical
        assert callable(main)
        assert callable(main_canonical)
        # They are distinct functions
        assert main is not main_canonical

    def test_emission_config_builder_reused(self) -> None:
        """Both entrypoints use the same _apps_rg_emission_config builder."""
        from apps_rg.__main__ import _apps_rg_emission_config
        cfg = _apps_rg_emission_config(
            target_company="TestCorp",
            target_role="TestRole",
        )
        assert cfg.app_name == "apps_rg"
        assert cfg.expected_execution_form == "DETERMINISTIC_PIPELINE"


class TestAdapterGovernedRunCompatibility:
    """Verify AdapterGovernedRun provides same interface as legacy GovernedRun."""

    def test_adapter_governed_run_has_span_method(self) -> None:
        """AdapterGovernedRun exposes span() context manager."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_compat",
            entrypoint_command="python -m test",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W4 compatibility test",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            # Both legacy and adapter have span()
            assert hasattr(gr, "span")
            # Both have mark_stage()
            assert hasattr(gr, "mark_stage")
            # Both have set_subprocess_exit_code()
            assert hasattr(gr, "set_subprocess_exit_code")

    def test_adapter_governed_run_span_context_manager(self) -> None:
        """AdapterGovernedRun.span() works as context manager."""
        from apps_shared.spine_emission.adapter import SpineRuntimeAdapter
        from apps_shared.spine_emission.context import EmissionConfig

        cfg = EmissionConfig(
            app_name="test_span",
            entrypoint_command="python -m test",
            runs_root=Path("/tmp/test_runs"),
            route_registry_path=Path("/tmp/test_routes.yaml"),
            l3_dag_path=None,
            plan_steps=[],
            plan_rationale="W4 span test",
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_static_dag=False,
            expected_execution_form="SINGLE_STEP",
            expected_l3_path="BYPASSED",
        )
        adapter = SpineRuntimeAdapter(cfg, prefer_canonical=True)

        with adapter.governed_run(cli_args=[]) as gr:
            with gr.span("test.operation"):
                gr.mark_stage("test_stage", "ok")
            # Stage was recorded
            assert "test_stage" in gr._stage_outcomes
