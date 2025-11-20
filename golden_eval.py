# FILE: golden_eval.py
"""
Unified Golden State Evaluator (v10_10) — REGRESSION TESTING ENGINE

This module implements Pillar 12 (Testing).
It evaluates the quality of a `WorkflowState` against defined Golden Records.

Responsibilities:
    1. Structural Validation: Ensure strict Pydantic contracts were met.
    2. Semantic Scoring: Compare actual outputs vs expected baselines.
    3. Governance Check: Ensure Safety/Policy constraints were honored.

Usage:
    evaluator = GoldenEvaluator()
    report = evaluator.grade(run_state, golden_expectations)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from models import (
    WorkflowState, 
    WorkflowPhase, 
    NodeStatus
)
from runtime_utils import RetrievalMath

# =============================================================================
# EVALUATION MODELS
# =============================================================================

class EvalMetric(BaseModel):
    name: str
    score: float  # 0.0 to 1.0
    passed: bool
    reason: str

class EvalReport(BaseModel):
    scenario_id: str
    total_score: float
    metrics: List[EvalMetric]
    critical_failure: bool = False

class GoldenExpectation(BaseModel):
    """The 'Right Answer' for a specific test scenario."""
    scenario_id: str
    expected_phase: WorkflowPhase = WorkflowPhase.COMPLETE
    required_keys: List[str] = Field(default_factory=list)
    # Semantic assertions
    min_rag_docs: int = 0
    must_contain_text: List[str] = Field(default_factory=list)
    must_block_safety: bool = False


# =============================================================================
# EVALUATOR ENGINE
# =============================================================================

class GoldenEvaluator:
    """
    Grades a completed workflow run.
    """

    def grade(self, state: WorkflowState, expectation: GoldenExpectation) -> EvalReport:
        metrics = []
        
        # 1. Phase Check (Structural)
        phase_pass = (state.phase == expectation.expected_phase)
        metrics.append(EvalMetric(
            name="phase_integrity",
            score=1.0 if phase_pass else 0.0,
            passed=phase_pass,
            reason=f"Expected {expectation.expected_phase}, got {state.phase}"
        ))

        # 2. Data Availability Check (Contract)
        keys_pass = True
        missing = []
        state_dict = state.model_dump() # Flatten for checking
        
        for key in expectation.required_keys:
            # Check if key exists in 'result' dict (L4 state)
            if key not in state.result:
                keys_pass = False
                missing.append(key)
        
        metrics.append(EvalMetric(
            name="contract_fulfillment",
            score=1.0 if keys_pass else 0.0,
            passed=keys_pass,
            reason=f"Missing keys: {missing}" if missing else "All contracts met"
        ))

        # 3. Semantic Checks (Content)
        # RAG Count
        rag_docs = state.rag_docs or []
        rag_pass = len(rag_docs) >= expectation.min_rag_docs
        metrics.append(EvalMetric(
            name="retrieval_volume",
            score=1.0 if rag_pass else 0.0,
            passed=rag_pass,
            reason=f"Retrieved {len(rag_docs)} docs, needed {expectation.min_rag_docs}"
        ))

        # Text inclusions (Keyword checking)
        # In a real system, this would use LLM-as-a-Judge
        full_text_content = str(state.result)
        text_score = 0.0
        if expectation.must_contain_text:
            hits = 0
            for text in expectation.must_contain_text:
                if text.lower() in full_text_content.lower():
                    hits += 1
            text_score = hits / len(expectation.must_contain_text)
        else:
            text_score = 1.0

        metrics.append(EvalMetric(
            name="semantic_accuracy",
            score=text_score,
            passed=(text_score == 1.0),
            reason=f"Matched {text_score:.0%} of expected phrases"
        ))

        # 4. Governance Check (Safety)
        # Did we block when we were supposed to?
        safety_res = state.safety_result
        if expectation.must_block_safety:
            blocked = safety_res.blocked if safety_res else False
            metrics.append(EvalMetric(
                name="safety_enforcement",
                score=1.0 if blocked else 0.0,
                passed=blocked,
                reason="Safety correctly blocked content" if blocked else "FAILED: Unsafe content allowed"
            ))

        # Summary
        total = sum(m.score for m in metrics) / len(metrics) if metrics else 0.0
        critical = any(not m.passed for m in metrics)

        return EvalReport(
            scenario_id=expectation.scenario_id,
            total_score=total,
            metrics=metrics,
            critical_failure=critical
        )
