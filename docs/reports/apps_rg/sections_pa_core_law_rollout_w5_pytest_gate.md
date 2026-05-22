# Sections PA Core-Law — W5 Pytest Gate

**Generated:** 20260522_102621 (UTC)

**Exit code:** 0

## Command

```bash
C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py tests/unit/apps_rg/test_headline_prompt_drift_ratchet.py tests/unit/apps_rg/test_competencies_prompt_drift_ratchet.py tests/unit/apps_rg/test_unify_ibm_prompt_drift_ratchet.py tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w1.py tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py tests/unit/apps_rg/test_headline_tailor_v15_prompt_quality.py tests/_apps_contract/test_headline_pa_compiled_prompt.py tests/_apps_contract/test_competencies_pa_compiled_prompt.py tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py -o addopts= -q --tb=short
```

## Stdout

```
...............................................................          [100%]
============================== warnings summary ===============================
agentic_core\L2_execution\reasoning\EmbeddingSovereignAgent.py:20
  C:\Git\Agentic-Workflow-FRESH\agentic_core\L2_execution\reasoning\EmbeddingSovereignAgent.py:20: DeprecationWarning: agentic_core.L2_execution.providers is deprecated. Import from agentic_core.utils.providers instead.
    from agentic_core.L2_execution.utils.providers import get_clock

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: builtin type SwigPyObject has no __module__ attribute

tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py: 1 warning
tests/unit/apps_rg/test_headline_prompt_drift_ratchet.py: 1 warning
tests/unit/apps_rg/test_competencies_prompt_drift_ratchet.py: 1 warning
tests/unit/apps_rg/test_unify_ibm_prompt_drift_ratchet.py: 2 warnings
tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py: 6 warnings
tests/_apps_contract/test_headline_pa_compiled_prompt.py: 5 warnings
tests/_apps_contract/test_competencies_pa_compiled_prompt.py: 4 warnings
tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py: 7 warnings
  <string>:15: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).

tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py::test_canonical_dispatch_routes_ibm_narrative_lane
  C:\Git\Agentic-Workflow-FRESH\agentic_core\L2_execution\healers\confidence_scorer.py:15: DeprecationWarning: agentic_core.L2_execution.healers.heal_classifier_model routes its outputs through the unified heal_router.v1 OTEL schema (agentic_core.L6_observability.heal_router_otel). Direct telemetry hooks on classifier results are deprecated (ADR-025 Wave F2 M4).
    from .heal_classifier_model import ClassifierFeatures, HealClassifierModel

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
63 passed, 31 warnings in 1.68s

```

## Stderr

```
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute

```

**Status:** PASS
