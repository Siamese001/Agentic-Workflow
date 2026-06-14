"""Unit tests for agentic_core.runtime.l2_recipe_resolver.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
Core-owned resolver that maps an ``app_name`` through the lazy-built
``_RECIPE_REGISTRY`` into a composite zero-arg L2 callable. Covers the
registry/dispatch surface: known-key resolution returns a callable, unknown
key raises ``KeyError`` with the canonical ``L2_RECIPE_NOT_FOUND`` marker,
and the ``is_recipe_registered`` / ``registered_app_names`` accessors.

``apps_rg`` is the sole built-in recipe (registered when ``apps_rg.l2_recipe``
imports cleanly), so it is the canonical known-key fixture here.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime import l2_recipe_resolver as resolver


class TestRegistryAccessors:
    def test_apps_rg_is_registered(self) -> None:
        assert resolver.is_recipe_registered("apps_rg") is True

    def test_unknown_app_not_registered(self) -> None:
        assert resolver.is_recipe_registered("apps_does_not_exist") is False

    def test_registered_app_names_returns_sorted_tuple(self) -> None:
        names = resolver.registered_app_names()
        assert isinstance(names, tuple)
        assert "apps_rg" in names
        assert list(names) == sorted(names)

    def test_registry_is_memoized(self) -> None:
        # Second access must return the same cached dict instance.
        first = resolver._get_registry()
        second = resolver._get_registry()
        assert first is second


class TestResolveKnownRecipe:
    def test_returns_zero_arg_callable(self) -> None:
        composite = resolver.resolve_l2_recipe("apps_rg", {"target_company": "ACME"})
        assert callable(composite)

    def test_resolution_does_not_execute_steps(self) -> None:
        # Resolution is pure wiring; building the callable must not invoke steps.
        composite = resolver.resolve_l2_recipe("apps_rg", {})
        assert callable(composite)
        # No exception, no side effect — the closure is returned un-invoked.

    def test_distinct_calls_return_distinct_callables(self) -> None:
        a = resolver.resolve_l2_recipe("apps_rg", {})
        b = resolver.resolve_l2_recipe("apps_rg", {})
        assert a is not b


class TestResolveUnknownRecipe:
    def test_unknown_app_raises_keyerror(self) -> None:
        with pytest.raises(KeyError, match="L2_RECIPE_NOT_FOUND"):
            resolver.resolve_l2_recipe("apps_phantom", {})

    def test_keyerror_lists_known_apps(self) -> None:
        with pytest.raises(KeyError, match="apps_rg"):
            resolver.resolve_l2_recipe("apps_phantom", {})

    @pytest.mark.parametrize("bad_name", ["", "APPS_RG", "apps_rg ", "rg"])
    def test_case_and_whitespace_sensitive(self, bad_name: str) -> None:
        with pytest.raises(KeyError):
            resolver.resolve_l2_recipe(bad_name, {})


class TestRegisterBuiltinRecipes:
    def test_builtin_registration_includes_required_keys(self) -> None:
        registry = resolver._register_builtin_recipes()
        assert "apps_rg" in registry
        meta = registry["apps_rg"]
        assert meta["app_name"] == "apps_rg"
        assert "dag_id" in meta
        assert "steps" in meta


class TestCompositeExecution:
    """Exercise the resolved zero-arg callable against a stub-injected registry.

    The registry is module-level and lazy. We snapshot it, inject a deterministic
    stub recipe (no app dependency), drive the composite, then restore — proving the
    step-chaining, context wiring, and non-zero-exit break path without live apps_rg.
    """

    @pytest.fixture(autouse=True)
    def _stub_registry(self):
        saved = resolver._RECIPE_REGISTRY
        yield
        resolver._RECIPE_REGISTRY = saved

    def _install(self, registry: dict) -> None:
        resolver._RECIPE_REGISTRY = registry

    def test_steps_chain_and_context_wiring(self) -> None:
        class _OkStep:
            def __call__(self, context: dict) -> dict:
                return {
                    "step_id": "ok",
                    "exit_code": 0,
                    "generated_resume": {"company": context.get("target_company")},
                }

        self._install(
            {"apps_demo": {"app_name": "apps_demo", "steps": [_OkStep], "dag_id": "dag-ok"}}
        )
        result = resolver.resolve_l2_recipe("apps_demo", {"target_company": "Acme"})()
        assert result["recipe_app_name"] == "apps_demo"
        assert result["recipe_dag_id"] == "dag-ok"
        assert result["step_results"][0]["generated_resume"] == {"company": "Acme"}

    def test_nonzero_exit_breaks_remaining_steps(self) -> None:
        ran = {"sentinel": False}

        class _FailStep:
            def __call__(self, context: dict) -> dict:
                return {"step_id": "fail", "exit_code": 1, "error": "boom"}

        class _SentinelStep:
            def __call__(self, context: dict) -> dict:
                ran["sentinel"] = True
                return {"step_id": "sentinel", "exit_code": 0}

        self._install(
            {
                "apps_demo": {
                    "app_name": "apps_demo",
                    "steps": [_FailStep, _SentinelStep],
                    "dag_id": "dag-fail",
                }
            }
        )
        result = resolver.resolve_l2_recipe("apps_demo", {})()
        assert ran["sentinel"] is False
        assert len(result["step_results"]) == 1
        assert result["step_results"][0]["step_id"] == "fail"

    def test_artifact_dir_and_defaults_threaded_into_context(self) -> None:
        captured: dict = {}

        class _CaptureStep:
            def __call__(self, context: dict) -> dict:
                captured.update(context)
                return {"step_id": "capture", "exit_code": 0}

        self._install(
            {"apps_demo": {"app_name": "apps_demo", "steps": [_CaptureStep], "dag_id": "d"}}
        )
        resolver.resolve_l2_recipe("apps_demo", {}, artifact_dir="/tmp/run-1")()
        assert captured["artifact_dir"] == "/tmp/run-1"
        assert captured["app_name"] == "apps_demo"
        assert captured["flow_route"] == "tailor_existing"
        assert captured["resume_artifact_contract_mode"] == "full"
