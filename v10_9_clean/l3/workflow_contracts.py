# workflow_contracts.py
"""
L3 — Workflow Contracts (v10_9)

Defines lightweight orchestration-level structures used by Orchestrator.
These do NOT replace L4 state; they only wrap L2 results for L3 processing.
"""

from __future__ import annotations

from typing import Dict, Any
from pydantic import BaseModel, Field

from ..shared.models import WorkflowPhase


class OrchestrationResult(BaseModel):
    """
    Returned from Orchestrator.run(), contains:
        • workflow id
        • new phase
        • state diff (to be applied by L4)
    """
    workflow_id: str
    phase: WorkflowPhase
    state_patch: Dict[str, Any] = Field(default_factory=dict)
