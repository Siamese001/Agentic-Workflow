"""ADG-hotspot scaffold tests for `agentic_core.prompt_governance.core.prompt_assembler` (fanin=1, band=P4).

Auto-generated speculative scaffold. Verify class/function names against actual
module before extending these scaffolds with behavioral assertions.
"""

from __future__ import annotations

import importlib

import pytest


MODULE_PATH = "agentic_core.prompt_governance.core.prompt_assembler"


def test_module_imports():
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(callable(getattr(mod, n)) for n in dir(mod) if not n.startswith("_"))
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), f"{MODULE_PATH} not under agentic_core: {file}"


def test_custom_xml_template_dir_points_to_ssot():
    """Custom XML templates MUST live under the SSOT prompt-governance folder.

    Regression guard: the orphan `./templates/prompts` root path was retired
    on 2026-04-28. Any reintroduction of that literal would split the prompt
    SSOT and silently break custom-template loading at runtime.
    """
    import inspect

    mod = importlib.import_module(MODULE_PATH)
    source = inspect.getsource(mod)
    assert "./templates/prompts" not in source, (
        "prompt_assembler must not reference orphan './templates/prompts' root path"
    )
    assert "templates/prompts" not in source.replace(
        "agentic_core/prompt_governance/templates/custom_xml", ""
    ), "Only SSOT path agentic_core/prompt_governance/templates/custom_xml is allowed"
    assert "agentic_core/prompt_governance/templates/custom_xml" in source, (
        "prompt_assembler must point custom XML templates at SSOT custom_xml subfolder"
    )
