from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def test_l_contracts_execution_trace_is_runtime_authority_shim() -> None:
    module_path = _repo_root() / "agentic_core" / "L_CONTRACTS" / "execution_trace.py"
    source = module_path.read_text(encoding="utf-8")

    assert "from agentic_core.runtime.types.execution_trace import" in source
    assert "class ExecutionTrace" not in source


def test_no_runtime_code_imports_l_contracts_execution_trace() -> None:
    root = _repo_root()
    search_roots = [root / "agentic_core", root / "apps_shared", root / "system_learning"]
    prohibited = "from agentic_core.L_CONTRACTS.execution_trace import"

    offenders: list[str] = []
    for base in search_roots:
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if prohibited in text:
                offenders.append(str(path.relative_to(root)))

    assert offenders == []
