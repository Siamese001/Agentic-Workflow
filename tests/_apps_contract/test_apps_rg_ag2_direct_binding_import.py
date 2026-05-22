"""Regression: integrated AG-2 entry imports apps_rg bindings directly."""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.runtime.entry import apps_rg_dispatch


def test_run_ag2_retrieval_and_prompt_uses_app_bindings(monkeypatch) -> None:
    calls: list[str] = []

    def _fake_c0(route, validated_request):
        calls.append("c0")
        return {"fec": True}

    def _fake_pa(route, plan, fec, validated_request):
        calls.append("pa")
        return {"prompt": True}

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_binding.c0_retrieve_apps_rg",
        _fake_c0,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.bindings.pa_binding.pa_compose_apps_rg",
        _fake_pa,
    )

    out = apps_rg_dispatch.run_ag2_retrieval_and_prompt("route", "plan", "validated")
    assert out == {"prompt": True}
    assert calls == ["c0", "pa"]


def test_apps_rg_dispatch_module_ast_has_no_core_shim_imports() -> None:
    path = Path(apps_rg_dispatch.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert "apps_rg.runtime.bindings.c0_binding" in imports
    assert "apps_rg.runtime.bindings.pa_binding" in imports
    assert "agentic_core.runtime.c0.apps_rg_c0_binding" not in imports
    assert "agentic_core.prompt_governance.apps_rg_pa_binding" not in imports
