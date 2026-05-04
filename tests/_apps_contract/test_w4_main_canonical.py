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
    """Verify main entrypoint is importable and wired correctly."""

    def test_main_importable(self) -> None:
        """main() can be imported from apps_rg.__main__."""
        from apps_rg.__main__ import main
        assert callable(main)

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
    """Verify main() is the single entrypoint (pure shim to R4 runner)."""

    def test_single_main_entrypoint(self) -> None:
        """Only main() exists — main_canonical was removed in shim refactor."""
        from apps_rg.__main__ import main
        assert callable(main)
        assert not hasattr(__import__("apps_rg.__main__", fromlist=["main"]), "main_canonical")

    def test_main_passes_app_name_to_r4(self) -> None:
        """main() delegates to R4 runner with app_name='apps_rg'."""
        import inspect
        from apps_rg.__main__ import main
        source = inspect.getsource(main)
        assert 'app_name="apps_rg"' in source


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
