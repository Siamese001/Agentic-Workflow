"""Smoke tests for L5 safety detection-signal config exports."""

from __future__ import annotations

import unittest

import pytest

_config = pytest.importorskip(
    "agentic_core.L5_safety.config",
    reason="Requires agentic_core L5 config exports from the monorepo checkout.",
)


def _require_attr(name: str):
    value = getattr(_config, name)
    assert value is not None
    return value


class GeneratedTest(unittest.TestCase):
    """Generated smoke tests for agentic_core.L5_safety.config."""

    def test_to_dict(self):
        to_dict = _require_attr("to_dict")
        self.assertIsNotNone(to_dict)

    def test_severity_init(self):
        severity = _require_attr("Severity")
        self.assertIsNotNone(severity)

    def test_impact_scope_init(self):
        impact_scope = _require_attr("ImpactScope")
        self.assertIsNotNone(impact_scope)


if __name__ == "__main__":
    unittest.main()
