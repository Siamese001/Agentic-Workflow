"""LJH5.2 capability suite — seed test.

Exercises :class:`agentic_core.evaluation.metrics.stability.StabilityReport`
on a deterministic fake "agent" so the suite collects and runs in CI
without an LLM provider. Real capability items replace this stub as
hill-climbing targets are added.
"""

from __future__ import annotations

import importlib

import pytest

_stability = importlib.import_module("agentic_core.evaluation.metrics.stability")
StabilityReport = _stability.StabilityReport


@pytest.mark.eval_capability
def test_capability_seed_stub_produces_stability_report() -> None:
    """Deterministic fake: 4/6 success → pass@1≈0.667, pass@3 larger, pass^3 smaller."""
    results = [True, False, True, True, False, True]
    report = StabilityReport.from_results(results, k_values=(1, 3))
    assert report.n == 6
    assert report.c == 4
    pak_1 = dict(report.pass_at_k_values)[1]
    pak_3 = dict(report.pass_at_k_values)[3]
    phk_1 = dict(report.pass_hat_k_values)[1]
    phk_3 = dict(report.pass_hat_k_values)[3]
    # Capability invariants: pass@k non-decreasing, pass^k non-increasing.
    assert pak_3 >= pak_1
    assert phk_3 <= phk_1
