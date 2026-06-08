"""W3 regression: resolve_scratch_max_output_tokens must not be function-local.

E2E-06: a function-local ``from ... import resolve_scratch_max_output_tokens`` made the
name local to ``run_executive_summary_execution`` for the whole scope, so the earlier
use (lane.py:1730) raised ``UnboundLocalError`` before generation. The import is now
hoisted to module scope. This guard is provider-independent and fast.
"""
from __future__ import annotations


def test_resolve_scratch_max_output_tokens_is_module_global():
    from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution

    code = run_executive_summary_execution.__code__
    # Must be a module global (hoisted import), NOT a function-local that shadows the
    # earlier use and raises UnboundLocalError.
    assert "resolve_scratch_max_output_tokens" not in code.co_varnames
    # ... and it must still be referenced (as a global name).
    assert "resolve_scratch_max_output_tokens" in code.co_names


def test_symbol_imported_at_module_scope():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    # The hoisted import binds the name at module scope and it is callable.
    assert callable(lane.resolve_scratch_max_output_tokens)
