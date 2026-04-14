"""Smoke tests for L5 safety agent-info enforcement exports."""

from __future__ import annotations

import unittest

import pytest

_enforcement = pytest.importorskip(
    "agentic_core.L5_safety.enforcement",
    reason="Requires L5 safety enforcement exports from the monorepo checkout.",
)


def _require_attr(name: str):
    value = getattr(_enforcement, name)
    assert value is not None
    return value


class GeneratedTest(unittest.TestCase):
    """Generated smoke tests for agentic_core.L5_safety.enforcement."""

    def test_extract_layer(self):
        extract_layer = _require_attr("extract_layer")
        self.assertIsNotNone(extract_layer)

    def test_find_agent_classes(self):
        find_agent_classes = _require_attr("find_agent_classes")
        self.assertIsNotNone(find_agent_classes)

    def test_agent_info_init(self):
        agent_info = _require_attr("AgentInfo")
        self.assertIsNotNone(agent_info)

    def test_ast_normalizer_init(self):
        ast_normalizer = _require_attr("ASTNormalizer")
        self.assertIsNotNone(ast_normalizer)

    def test_ast_normalizer_reset(self):
        ast_normalizer = _require_attr("ASTNormalizer")
        self.assertTrue(hasattr(ast_normalizer, "reset"))


if __name__ == "__main__":
    unittest.main()
