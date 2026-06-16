from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]


def _iter_product_python_files() -> list[Path]:
    roots = [
        REPO_ROOT / "apps_rg" / "runtime",
        REPO_ROOT / "apps_rg" / "fact_inventory",
    ]
    files: list[Path] = []
    for root in roots:
        files.extend(p for p in root.rglob("*.py") if p.is_file())
    return sorted(files)


def test_retired_selected_role_fact_set_import_paths_are_not_used_by_product_code() -> None:
    forbidden = (
        "from apps_rg.runtime.sections.selected_role_fact_set",
        "from apps_rg.runtime.sections import selected_role_fact_set",
        "apps_rg.runtime.sections.selected_role_fact_set",
        "from apps_rg.fact_inventory.selected_role_fact_set",
        "apps_rg.fact_inventory.selected_role_fact_set",
    )
    tombstones = {
        REPO_ROOT / "apps_rg" / "runtime" / "sections" / "selected_role_fact_set.py",
        REPO_ROOT / "apps_rg" / "fact_inventory" / "selected_role_fact_set.py",
    }
    offenders: list[str] = []
    for path in _iter_product_python_files():
        if path in tombstones:
            continue
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)} contains {needle!r}")
    assert offenders == []


def test_selected_role_fact_set_cli_flag_is_removed() -> None:
    text = (REPO_ROOT / "apps_rg" / "__main__.py").read_text(encoding="utf-8")
    assert "--selected-role-fact-set" not in text


def test_resolver_does_not_accept_selected_role_fact_set_argument() -> None:
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    sig = inspect.signature(resolve_section_proof_pool)
    assert "selected_role_fact_set_path" not in sig.parameters


def test_retired_executive_summary_prompt_symbols_are_not_exported() -> None:
    import apps_rg.runtime.dispatch.executive_summary_pa as dispatch_pa
    import apps_rg.runtime.sections.executive_summary_pa as section_pa

    retired_symbols = (
        "SRFS_STYLE_ONESHOT_MARKER",
        "SRFS_COMPOSITION_ONESHOT_MARKER",
        "SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER",
        "SRFS_FORBIDDEN_PHRASES_ALWAYS",
        "format_srfs_style_only_quality_oneshot_block",
        "format_srfs_forbidden_phrase_guardrails_block",
        "format_srfs_role_adaptive_appendix",
    )
    for module in (dispatch_pa, section_pa):
        for symbol in retired_symbols:
            assert not hasattr(module, symbol), f"{module.__name__}.{symbol} should stay retired"


@pytest.mark.parametrize(
    "module_name",
    [
        "apps_rg.runtime.sections.selected_role_fact_set",
        "apps_rg.fact_inventory.selected_role_fact_set",
    ],
)
def test_retired_selected_role_fact_set_modules_fail_closed(module_name: str) -> None:
    with pytest.raises(RuntimeError, match="SelectedRoleFactSet/SRFS"):
        importlib.import_module(module_name)


def test_retired_fact_inventory_selected_role_fact_set_static_import_fails_closed() -> None:
    with pytest.raises(RuntimeError, match="SelectedRoleFactSet/SRFS"):
        from apps_rg.fact_inventory import selected_role_fact_set  # noqa: F401
