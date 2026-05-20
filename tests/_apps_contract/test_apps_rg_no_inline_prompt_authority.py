"""W10 — generated lanes compile provider messages via PA only (no hand-built runtime prompts)."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_DISPATCH_MODULES = [
    "apps_rg.runtime.sections.headline_lane",
    "apps_rg.runtime.sections.executive_summary_lane",
    "apps_rg.runtime.sections.competencies_lane_runtime",
    "apps_rg.runtime.sections.unify_narrative_lane",
    "apps_rg.runtime.sections.unify_bullets_lane",
    "apps_rg.runtime.sections.ibm_narrative_lane_runtime",
    "apps_rg.runtime.sections.ibm_bullets_lane",
]


def _fn_source(modname: str, fn: str) -> str:
    mod = __import__(modname, fromlist=["_"])
    m = sys.modules[modname]
    return inspect.getsource(getattr(m, fn))


@pytest.mark.parametrize("modname", _DISPATCH_MODULES)
def test_build_prompt_messages_compiles_and_returns_artifact_messages(modname: str) -> None:
    src = _fn_source(modname, "build_prompt_messages")
    assert "compile_" in src, modname
    assert ".artifact.messages" in src.replace(" ", ""), modname


@pytest.mark.parametrize(
    "modname",
    [
        "apps_rg.runtime.dispatch.headline_pa",
        "apps_rg.runtime.dispatch.executive_summary_pa",
        "apps_rg.runtime.dispatch.competencies_pa",
        "apps_rg.runtime.dispatch.unify_narrative_pa",
        "apps_rg.runtime.dispatch.unify_bullets_pa",
        "apps_rg.runtime.dispatch.ibm_narrative_pa",
        "apps_rg.runtime.dispatch.ibm_bullets_pa",
    ],
)
def test_pa_modules_call_section_prompt_adapter_compile(modname: str) -> None:
    m = __import__(modname, fromlist=["_"])
    mod = sys.modules[modname]
    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "compile_section_prompt" in src, modname
    assert "section_prompt_adapter" in src or "section_prompt_adapter" in src.replace("\n", " "), modname


def test_adapter_has_no_silent_fallback() -> None:
    path = _REPO / "apps_rg" / "runtime" / "bindings" / "section_prompt_adapter.py"
    text = path.read_text(encoding="utf-8").lower()
    assert "fallback" not in text or "no fallback" in text
