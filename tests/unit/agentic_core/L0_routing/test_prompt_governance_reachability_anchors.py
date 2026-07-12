from __future__ import annotations

import ast
from pathlib import Path


def test_l0_binding_keeps_direct_prompt_governance_module_anchors() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    binding = repo_root / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    tree = ast.parse(binding.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert {
        "agentic_core.prompt_governance.mixins",
        "agentic_core.prompt_governance.validation",
    } <= imported_modules
