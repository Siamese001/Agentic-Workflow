"""Behavioral tests for ast_validator_agent_adg strict mode."""

from __future__ import annotations

from agentic_core.ast_validator_agent_adg import ASTValidatorAgentAdg


def test_ast_validator_agent_defaults_to_strict_mode():
    assert ASTValidatorAgentAdg().validate().strict_mode is True
