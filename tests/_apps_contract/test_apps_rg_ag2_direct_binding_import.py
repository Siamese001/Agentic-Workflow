"""Regression: integrated AG-2 entry uses verified apps_rg C0 planning boundary.

apps-test-model: APP CONTRACT
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.runtime.entry import apps_rg_dispatch


def test_run_ag2_retrieval_and_prompt_uses_verified_app_bindings(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    def _fake_c0(route, validated_request, *, l1_plan):
        calls.append(("c0", l1_plan))
        return {"fec": True}

    def _fake_pa(route, plan, fec, validated_request):
        calls.append(("pa", plan))
        return {"prompt": True}

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_planned_binding.c0_retrieve_apps_rg_planned",
        _fake_c0,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.bindings.pa_planned_binding.pa_compose_apps_rg_planned",
        _fake_pa,
    )

    plan = object()
    out = apps_rg_dispatch.run_ag2_retrieval_and_prompt("route", plan, "validated")
    assert out == {"prompt": True}
    assert calls == [("c0", plan), ("pa", plan)]


def test_apps_rg_dispatch_module_ast_has_no_static_core_to_app_imports() -> None:
    path = Path(apps_rg_dispatch.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert "apps_rg.runtime.bindings.c0_binding" not in imports
    assert "apps_rg.runtime.bindings.c0_planned_binding" not in imports
    assert "apps_rg.runtime.bindings.pa_binding" not in imports
    assert "apps_rg.runtime.bindings.pa_planned_binding" not in imports
    assert "apps_rg.runtime.dispatch.apps_rg_dispatch" not in imports
    assert "apps_rg.runtime.orchestration.canonical_dispatch" not in imports
    assert "agentic_core.runtime.c0.apps_rg_c0_binding" not in imports
    assert "agentic_core.prompt_governance.apps_rg_pa_binding" not in imports
