"""Tests for the judge backend plugin package (plan `-d5e8b3` §Q3)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.eval_spine.judge_backends import (
    AnthropicBackend,
    JudgeBackend,
    NullBackend,
    backend_name,
)
from agentic_core.L5_safety.eval_spine.trace_grader import (
    DimensionResult,
    GraderInput,
    TraceGrader,
)

_DIM_SPEC = {"name": "tool_selection", "pass_threshold": 4.0, "warn_threshold": 3.0}


@pytest.fixture(autouse=True)
def _clear_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


class TestNullBackend:
    def test_returns_unknown(self):
        backend = NullBackend()
        result = backend(GraderInput(), _DIM_SPEC)
        assert isinstance(result, DimensionResult)
        assert result.score == "Unknown"
        assert result.verdict == "unknown"
        assert result.name == "tool_selection"

    def test_note_propagates(self):
        backend = NullBackend(note="because-reasons")
        result = backend(GraderInput(), _DIM_SPEC)
        assert result.notes == "because-reasons"

    def test_dim_name_falls_back(self):
        backend = NullBackend()
        result = backend(GraderInput(), {})
        assert result.name == "unknown_dim"


class TestAnthropicBackend:
    def test_no_api_key_behaves_as_null(self):
        backend = AnthropicBackend()
        assert backend.is_active() is False
        result = backend(GraderInput(), _DIM_SPEC)
        assert result.score == "Unknown"
        assert result.notes == "anthropic:no_api_key"

    def test_with_api_key_raises_not_implemented(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        backend = AnthropicBackend()
        assert backend.is_active() is True
        with pytest.raises(NotImplementedError) as excinfo:
            backend(GraderInput(), _DIM_SPEC)
        assert "deferred" in str(excinfo.value).lower()

    def test_empty_api_key_treated_as_absent(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
        backend = AnthropicBackend()
        assert backend.is_active() is False


class TestJudgeBackendAlias:
    def test_is_alias_of_dim_scorer(self):
        # JudgeBackend is intentionally the same callable shape as DimScorer.
        from agentic_core.L5_safety.eval_spine.trace_grader import DimScorer

        assert JudgeBackend is DimScorer


class TestBackendName:
    def test_class_backend_reports_class_name(self):
        assert backend_name(NullBackend()) == "NullBackend"
        assert backend_name(AnthropicBackend()) == "AnthropicBackend"

    def test_function_backend_reports_module_qualname(self):
        def my_scorer(_i, _s):
            return DimensionResult(name="x", score="Unknown", verdict="unknown")

        name = backend_name(my_scorer)
        assert "my_scorer" in name

    def test_none_is_safe(self):
        assert backend_name(None) == "<none>"  # type: ignore[arg-type]


class TestRegistrationWithTraceGrader:
    def test_null_backend_plugs_into_grader(self):
        grader = TraceGrader()
        grader.register_dim_scorer("tool_selection", NullBackend(dim_name="tool_selection"))
        out = grader.grade(GraderInput())
        sel = out.dim("tool_selection")
        assert sel is not None
        assert sel.score == "Unknown"

    def test_anthropic_without_key_plugs_in_safely(self):
        grader = TraceGrader()
        grader.register_dim_scorer("tool_selection", AnthropicBackend(dim_name="tool_selection"))
        out = grader.grade(GraderInput())
        sel = out.dim("tool_selection")
        assert sel is not None
        assert sel.score == "Unknown"
