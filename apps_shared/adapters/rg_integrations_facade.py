"""Boundary facade for apps_* code that needs ``apps_rg.integrations`` surfaces.

W11-M3B: centralizes apps_eval → apps_rg integrations coupling (anti-overfitting
gates, length budgets, judge LLM client) so ``apps_eval`` does not import
``apps_rg`` directly.

PEP 562 lazy resolution — module loads without pulling apps_rg until first access.
"""

from __future__ import annotations

from typing import Any

_LAZY_SYMBOLS: dict[str, tuple[str, str]] = {
    "AntiOverfittingConfig": ("apps_rg.integrations.anti_overfitting", "AntiOverfittingConfig"),
    "GateResult": ("apps_rg.integrations.anti_overfitting", "GateResult"),
    "gate_adjacent_repetition": ("apps_rg.integrations.anti_overfitting", "gate_adjacent_repetition"),
    "gate_buzzword_soup": ("apps_rg.integrations.anti_overfitting", "gate_buzzword_soup"),
    "gate_filler_intensifiers": ("apps_rg.integrations.anti_overfitting", "gate_filler_intensifiers"),
    "gate_mirror_density": ("apps_rg.integrations.anti_overfitting", "gate_mirror_density"),
    "gate_pipe_format": ("apps_rg.integrations.anti_overfitting", "gate_pipe_format"),
    "LengthBudget": ("apps_rg.integrations.length_budget", "LengthBudget"),
    "call_judge": ("apps_rg.integrations.hops._llm_client", "call_judge"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_SYMBOLS:
        import importlib  # noqa: PLC0415

        mod_path, sym = _LAZY_SYMBOLS[name]
        module = importlib.import_module(mod_path)
        attr = getattr(module, sym)
        globals()[name] = attr
        return attr
    raise AttributeError(
        f"module 'apps_shared.adapters.rg_integrations_facade' has no attribute {name!r}"
    )


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(_LAZY_SYMBOLS.keys()))


__all__ = list(_LAZY_SYMBOLS.keys())
