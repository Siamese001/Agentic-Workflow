# API Documentation: heal_policy_types

**Target Audience**: developers, api_users

# heal_policy_types API Documentation

**File**: `heal_policy_types.py`
**Classes**: 5
**Functions**: 4

## Classes

- **ReasoningTier** (inherits from Enum)
- **ScoreBand** (inherits from Enum)
- **HealEscalationInputs**
- **LegacyHealEscalationInputs**
- **HealEscalationDecision**

## Functions

- **classify_score** -> ScoreBand
- **classify_confidence** -> ScoreBand
- **decide_heal_escalation** -> HealEscalationDecision
- **decide_reasoning_tier** -> HealEscalationDecision


## Class: ReasoningTier

**Description**: LLM reasoning tier for agent healing escalation.

**Inherits from**: Enum



## Class: ScoreBand

**Description**: Score band classification (replaces ConfidenceLevel).

**Inherits from**: Enum



## Class: HealEscalationInputs

**Description**: Inputs for heal escalation decision (canonical).

    Attributes:
        score: Routing score S from _route_decision (C+A+F+B+N factors). Primary input.
        enable_llm: Whether LLM escalation is permitted (controls tier activation).
        confidence_value: DEPRECATED — kept for backward compat only, not used for gating.
        task_complexity: DEPRECATED — kept for backward compat only.
        cost_budget: Unused in decision logic.
        latency_budget_ms: Unused in decision logic.
        safety_risk: DEPRECATED — kept for backward compat only.
        prior_failures: DEPRECATED — kept for backward compat only.
    



## Class: LegacyHealEscalationInputs

**Description**: Legacy inputs for heal escalation decision (backward compat).



## Class: HealEscalationDecision

**Description**: Decision result for heal escalation.

    Attributes:
        proceed: Whether healing should proceed
        tier: Reasoning tier (None if proceed=False or no LLM needed)
        rationale: Human-readable explanation
        threshold_used: Short deterministic token for debugging
    



## Function: classify_score

**Parameters**: score
**Returns**: ScoreBand
**Description**: Classify routing score S into score band.

    Args:
        score: Routing score S from _route_decision.

    Returns:
        ScoreBand: DETERMINISTIC, QWEN, or GEMINI.
    



## Function: classify_confidence

**Parameters**: confidence
**Returns**: ScoreBand
**Description**: DEPRECATED: approximate mapping from confidence float to ScoreBand.

    Use classify_score(score) for new code.
    High confidence → low score → DETERMINISTIC.
    



## Function: decide_heal_escalation

**Parameters**: inputs
**Returns**: HealEscalationDecision
**Description**: Score-based escalation decision. Healing always proceeds (proceed=True).

    Routing rules (by score S):
    - S <= 13: DETERMINISTIC — agent-native logic, no LLM needed
    - S 14-26: QWEN tier    — Qwen 2.5 14B advises the healing plan
    - S > 26:  GEMINI tier  — Gemini 2.5 Pro handles complex reasoning

    Args:
        inputs: Heal escalation inputs (score is the canonical field).

    Returns:
        HealEscalationDecision with proceed=True and appropriate tier.
    



## Function: decide_reasoning_tier

**Parameters**: inputs
**Returns**: HealEscalationDecision
**Description**: DEPRECATED legacy function. Always proceeds; routes by complexity.

    Use decide_heal_escalation() with score for new code.
    



## Usage Examples

### Class Usage

```python
# Using ReasoningTier
reasoningtier = ReasoningTier()
```

```python
# Using ScoreBand
scoreband = ScoreBand()
```

```python
# Using HealEscalationInputs
healescalationinputs = HealEscalationInputs()
```

### Function Usage

```python
# Using classify_score
result = classify_score(score)
```

```python
# Using classify_confidence
result = classify_confidence(confidence)
```

```python
# Using decide_heal_escalation
result = decide_heal_escalation(inputs)
```



---
**Generated**: 2026-03-26T09:39:05.519274
**Type**: api_reference
**Quality**: comprehensive
