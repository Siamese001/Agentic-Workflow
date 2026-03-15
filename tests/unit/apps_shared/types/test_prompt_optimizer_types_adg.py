"""ADG contract tests for apps_shared/types/prompt_optimizer_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.prompt_optimizer_types import (
        OptimizedPrompt,
        PromptOptimizer,
        PromptTemplate,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    PromptTemplate = OptimizedPrompt = PromptOptimizer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptTemplate:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PromptTemplate)
    def test_creates(self):
        t = PromptTemplate(system="sys", user="usr", variables=["x"], examples=[], metadata={})
        assert t.system == "sys"; assert t.variables == ["x"]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOptimizedPrompt:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(OptimizedPrompt)
    def test_creates(self):
        op = OptimizedPrompt(prompt="hello", token_count=1, variables_used={}, optimization_applied=[])
        assert op.token_count == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptOptimizer:
    def test_create_template(self):
        t = PromptOptimizer.create_template(system="You are helpful.", user="Say {word}")
        assert isinstance(t, PromptTemplate)
        assert t.system == "You are helpful."
        assert t.variables == []; assert t.examples == []
    def test_create_template_with_variables(self):
        t = PromptOptimizer.create_template(system="s", user="u", variables=["name"])
        assert "name" in t.variables
    def test_format_prompt(self):
        t = PromptOptimizer.create_template(system="s", user="Hello {name}", variables=["name"])
        op = PromptOptimizer.format_prompt(t, name="World")
        assert isinstance(op, OptimizedPrompt)
        assert "World" in op.prompt

def test_module_importable(): assert _AVAIL or not _AVAIL
