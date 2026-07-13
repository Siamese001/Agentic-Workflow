from __future__ import annotations

import ast
from pathlib import Path


def test_l0_binding_uses_prompt_governance_public_contract() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    binding = repo_root / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    tree = ast.parse(binding.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    public_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "agentic_core.prompt_governance"
        for alias in node.names
    }

    assert {"assemble_prompt", "get_bundled_mixin", "validate_apply_patch"} <= public_names
    assert "agentic_core.prompt_governance.mixins" not in imported_modules
    assert "agentic_core.prompt_governance.validation" not in imported_modules


def test_prompt_governance_facade_wiring_is_graph_resolvable() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    facade_modules = {
        node.module
        for path in (
            repo_root / "agentic_core" / "prompt_governance" / "__init__.py",
            repo_root / "agentic_core" / "prompt_governance" / "validation" / "__init__.py",
        )
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom) and node.level == 0
    }

    assert {
        "agentic_core.prompt_governance.mixins",
        "agentic_core.prompt_governance.validation",
        "agentic_core.prompt_governance.validation.apply_patch_validator",
    } <= facade_modules
