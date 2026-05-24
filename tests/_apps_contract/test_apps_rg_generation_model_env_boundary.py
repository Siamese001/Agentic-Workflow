"""W2 — apps_rg section body generation must not use spine shared-agent model env vars."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_SPINE_MODEL_SYMBOLS: frozenset[str] = frozenset(
    {
        "OPENAI_MODEL",
        "GOOGLE_AI_MODEL",
        "GOOGLE_AI_PRO_MODEL",
        "OPENAI_MODEL_ID",
        "GEMINI_FLASH_MODEL_ID",
        "GEMINI_PRO_MODEL_ID",
    }
)

FORBIDDEN_SPINE_MODEL_ENV_GET: frozenset[str] = frozenset(
    {
        "OPENAI_MODEL",
        "GOOGLE_AI_MODEL",
        "GOOGLE_AI_PRO_MODEL",
        "HEALING_GOOGLE_AI_PRO_MODEL",
    }
)

# Canonical modular generation surface (HIGH static).
PRODUCT_GENERATION_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "apps_rg" / "runtime" / "sections",
    REPO_ROOT / "apps_rg" / "runtime" / "providers" / "qwen_vllm_provider.py",
    REPO_ROOT / "apps_rg" / "runtime" / "providers" / "section_qwen_slice.py",
)

# Explicitly classified non-generation (must not fail W2 if they reference spine vars).
CLASSIFIED_NON_GENERATION_PREFIXES: tuple[str, ...] = (
    "apps_rg/runtime/judges/",
    "apps_rg/runtime/dispatch/",
    "tests/fixtures/apps_rg/",
)


def _rel(p: Path) -> str:
    return p.relative_to(REPO_ROOT).as_posix()


def _py_files_under(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(
        p
        for p in path.rglob("*.py")
        if "__pycache__" not in p.parts and p.name != "__init__.py"
    )


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "agentic_core.L0_routing.config.model_registry":
                for alias in node.names:
                    names.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "agentic_core.L0_routing.config.model_registry":
                    names.add("model_registry")
    return names


def _getenv_keys(tree: ast.AST) -> list[str]:
    keys: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "getenv":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
                node.args[0].value, str
            ):
                keys.append(node.args[0].value)
    return keys


@pytest.mark.parametrize("root", PRODUCT_GENERATION_ROOTS, ids=lambda p: _rel(p))
def test_product_generation_modules_do_not_import_spine_model_registry_ids(root: Path) -> None:
    violations: list[str] = []
    for py in _py_files_under(root):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        imported = _imported_names(tree)
        bad = imported & FORBIDDEN_SPINE_MODEL_SYMBOLS
        if bad:
            violations.append(f"{_rel(py)}: imports {sorted(bad)} from model_registry")
        if "model_registry" in imported and imported - FORBIDDEN_SPINE_MODEL_SYMBOLS:
            # Any model_registry import in generation path is suspicious.
            violations.append(f"{_rel(py)}: imports model_registry symbols {sorted(imported)}")
    assert not violations, "W2 generation boundary violations:\n" + "\n".join(violations)


@pytest.mark.parametrize("root", PRODUCT_GENERATION_ROOTS, ids=lambda p: _rel(p))
def test_product_generation_modules_do_not_read_spine_model_env_vars(root: Path) -> None:
    violations: list[str] = []
    for py in _py_files_under(root):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for key in _getenv_keys(tree):
            if key in FORBIDDEN_SPINE_MODEL_ENV_GET:
                violations.append(f"{_rel(py)}: os.getenv({key!r})")
    assert not violations, "W2 spine env getenv in generation path:\n" + "\n".join(violations)


def test_qwen_vllm_provider_uses_qwen_vllm_env_defaults() -> None:
    mod = REPO_ROOT / "apps_rg" / "runtime" / "providers" / "qwen_vllm_provider.py"
    text = mod.read_text(encoding="utf-8")
    assert 'os.environ.get("VLLM_BASE_URL"' in text or 'getenv("VLLM_BASE_URL"' in text
    assert "QWEN_VLLM_MODEL" in text
    assert "DEFAULT_QWEN_MODEL" in text


def test_classified_non_generation_paths_are_documented() -> None:
    for prefix in CLASSIFIED_NON_GENERATION_PREFIXES:
        assert (REPO_ROOT / prefix).exists(), f"missing classified path {prefix}"
