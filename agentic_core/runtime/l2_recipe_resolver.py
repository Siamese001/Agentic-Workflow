"""Core-owned L2 recipe resolver.

Resolves registered app-specific L2 step implementations into a composite
zero-argument callable for the R4 deterministic pipeline.

Canonical dependency law:
    agentic_core owns resolution — apps only register step implementations.
    apps/__main__.py MUST NOT call this module.  Only the R4 runner does.

Recipe resolution flow:
    app_name → _RECIPE_REGISTRY lookup → ordered step classes → composite callable
"""

from __future__ import annotations

import logging
from importlib import import_module
from typing import Any, Callable

_log = logging.getLogger("agentic_core.runtime.l2_recipe_resolver")


# ---------------------------------------------------------------------------
# Recipe registry — populated by _register_builtin_recipes() on first access
# ---------------------------------------------------------------------------

_RECIPE_REGISTRY: dict[str, dict[str, Any]] | None = None


def _load_app_module(module_parts: tuple[str, ...]):
    return import_module(".".join(module_parts))


def _register_builtin_recipes() -> dict[str, dict[str, Any]]:
    """Lazy-load the recipe registry with all known app recipes.

    This function imports app-side registry modules.  It is called ONCE
    by ``resolve_l2_recipe`` on first invocation.
    """
    registry: dict[str, dict[str, Any]] = {}

    try:
        # guardian: allow-layer-violation -- L_RUNTIME resolver must lazy-import L_APP recipe registries; this is the canonical core-owned registration seam by design
        app_pkg = "_".join(("apps", "rg"))
        registry_module = _load_app_module((app_pkg, "l2_recipe", "registry"))
        get_apps_rg_recipe_metadata = registry_module.get_apps_rg_recipe_metadata

        meta = get_apps_rg_recipe_metadata()
        registry[meta["app_name"]] = meta
        _log.debug("Registered L2 recipe for app_name=%s", meta["app_name"])
    except ImportError:  # guardian: allow-log-and-swallow -- P1 ADG burndown
        _log.debug("apps_rg.l2_recipe not available — recipe not registered")

    return registry


def _get_registry() -> dict[str, dict[str, Any]]:
    global _RECIPE_REGISTRY
    if _RECIPE_REGISTRY is None:
        _RECIPE_REGISTRY = _register_builtin_recipes()
    return _RECIPE_REGISTRY


def resolve_l2_recipe(
    app_name: str,
    raw_request: dict[str, Any],
    artifact_dir: Any = None,
) -> Callable[[], Any]:
    """Resolve a registered L2 recipe into a composite zero-arg callable.

    Parameters
    ----------
    app_name:
        The app identifier (e.g. ``"apps_rg"``).
    raw_request:
        The raw request dict — used to populate step context.
    artifact_dir:
        Optional per-run artifact directory (set by the R4 entrypoint).
        When provided, it is injected into the L2 context as
        ``context["artifact_dir"]`` so step adapters (e.g. apps_rg's
        ``GenerateResumeStep``) can write narrative outputs into the
        same dir the spine writes its receipts.  This unifies spine
        and narrative artifacts in a single per-run dir — see
        ``docs/archive/windsurf/legacy-tree/plans/apps-rg-spine-narrative-unification-d8e4a1.md``.

    Returns
    -------
    Callable[[], Any]
        A zero-argument callable that chains the registered L2 steps.

    Raises
    ------
    KeyError
        If ``app_name`` has no registered recipe.
    """
    registry = _get_registry()

    if app_name not in registry:
        raise KeyError(
            f"L2_RECIPE_NOT_FOUND: No registered L2 recipe for "
            f"app_name={app_name!r}. Known apps: {sorted(registry.keys())}"
        )
  # guardian: allow-hallucinated-tool-name -- P1 ADG burndown
    meta = registry[app_name]  # guardian: allow-hallucinated-tool-name -- P1 ADG burndown
    recipe_scope = str(raw_request.get("execution_scope") or "").strip()
    scope_steps = meta.get("scope_steps")
    if recipe_scope and isinstance(scope_steps, dict) and recipe_scope in scope_steps:
        step_classes = scope_steps[recipe_scope]
    else:
        step_classes = meta["steps"]

    def _composite_l2_callable() -> dict[str, Any]:
        """Execute the L2 recipe steps in sequence."""
        import json as _json
        from pathlib import Path as _Path

        jd_payload = raw_request.get("jd_payload") or {}
        jd_data = (
            raw_request.get("jd_data")
            or (_json.dumps(jd_payload) if jd_payload else "")
            or raw_request.get("body_text", "")
        )
        master_resume_data = raw_request.get("master_resume_data", "")
        if not master_resume_data:
            _master_path = _Path("apps_shared/data/master_resume.json")
            if _master_path.exists():
                try:
                    master_resume_data = _master_path.read_text(encoding="utf-8")
                except OSError:  # guardian: allow-silent-swallow -- P1 ADG burndown
                    pass
        flow_route = raw_request.get("flow_route", "tailor_existing")

        _contract_mode = raw_request.get("resume_artifact_contract_mode")
        _contract_mode_s = (
            str(_contract_mode).strip() if _contract_mode is not None else ""
        ) or "full"

        context: dict[str, Any] = {
            "app_name": app_name,
            "target_company": raw_request.get("target_company", ""),
            "target_role": raw_request.get("target_role", ""),
            "resume_artifact_contract_mode": _contract_mode_s,
            "manual_brief": raw_request.get("manual_brief", "apps_rg/scripts/_interactive_brief.json"),
            "research_via": raw_request.get("research_via"),
            "auto_research_internal": raw_request.get("auto_research_internal", False),
            "auto_research_tavily": raw_request.get("auto_research_tavily", False),
            "pa_compatible": True,
            "jd_data": jd_data,
            "master_resume_data": master_resume_data,
            "flow_route": flow_route,
            "artifact_dir": artifact_dir,
            "raw_request": dict(raw_request),
        }
        l2_context = raw_request.get("l2_context")
        if isinstance(l2_context, dict):
            context.update(l2_context)
        results: list[dict[str, Any]] = []
        for step_cls in step_classes:
            step = step_cls()
            result = step(context)
            results.append(result)
            if result.get("generated_resume") is not None:
                context["generated_resume"] = result["generated_resume"]
            if result.get("exit_code", 0) != 0 and not result.get("skipped"):
                _log.error(
                    "[L2 recipe] Step %s failed: %s",
                    result.get("step_id", "unknown"),
                    result.get("error", "non-zero exit"),
                )
                break
        witness_builder = meta.get("execution_witness_builder")
        runtime_execution_witness = (
            witness_builder(
                artifact_dir=artifact_dir,
                step_results=results,
                context=context,
            )
            if callable(witness_builder)
            else None
        )
        return {
            "recipe_app_name": app_name,
            "recipe_dag_id": meta["dag_id"],
            "step_results": results,
            "run_dir": context.get("run_dir"),
            "runtime_execution_witness": runtime_execution_witness,
        }

    return _composite_l2_callable


def is_recipe_registered(app_name: str) -> bool:
    """Check whether a recipe is registered for the given app_name."""
    return app_name in _get_registry()


def registered_app_names() -> tuple[str, ...]:
    """Return all registered app names."""
    return tuple(sorted(_get_registry().keys()))


__all__ = [
    "resolve_l2_recipe",
    "is_recipe_registered",
    "registered_app_names",
]
