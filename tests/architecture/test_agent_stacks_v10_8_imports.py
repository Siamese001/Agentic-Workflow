"""Smoke-tests for the v10.8 stack scaffolding."""

from __future__ import annotations

import pytest

from agent_stacks_v10_8 import (
    BulletExecutionStack,
    DraftingExecutionStack,
    HILStackV10_8,
    QAValidationStack,
    RAGExecutionStack,
    SafetyStackV10_8,
    StateAdapterStack,
    StrategyStackV10_8,
)


@pytest.mark.parametrize(
    "stack_cls",
    [
        RAGExecutionStack,
        QAValidationStack,
        DraftingExecutionStack,
        BulletExecutionStack,
        StrategyStackV10_8,
        SafetyStackV10_8,
        HILStackV10_8,
    ],
)
def test_stack_instantiation(stack_cls, mock_workflow_context):
    stack = stack_cls(mock_workflow_context)
    assert stack is not None


def test_state_adapter_stack_instantiation(mock_workflow_context):
    adapter = StateAdapterStack(mock_workflow_context)
    assert adapter.context is mock_workflow_context
