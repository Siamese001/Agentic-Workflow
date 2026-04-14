"""Behavioral tests for ast_validator_agent_adg validator."""

from __future__ import annotations

from agentic_core.ast_validator_agent_adg import ASTValidatorAgentAdg, validate_ast_validator_agent_adg


def test_ast_validator_helper_returns_valid_contract():
    assert validate_ast_validator_agent_adg(ASTValidatorAgentAdg(strict_mode=False)).strict_mode is False
