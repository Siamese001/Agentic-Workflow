"""Smoke tests for L5 safety contract-stage config exports."""

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

    def test_enforce(self):
        enforce = _require_attr("enforce")
        self.assertIsNotNone(enforce)

    def test_add_contract(self):
        add_contract = _require_attr("add_contract")
        self.assertIsNotNone(add_contract)

    def test_contract_stage_init(self):
        contract_stage = _require_attr("ContractStage")
        self.assertIsNotNone(contract_stage)

    def test_cognitive_contract_init(self):
        cognitive_contract = _require_attr("CognitiveContract")
        self.assertIsNotNone(cognitive_contract)


if __name__ == "__main__":
    unittest.main()
