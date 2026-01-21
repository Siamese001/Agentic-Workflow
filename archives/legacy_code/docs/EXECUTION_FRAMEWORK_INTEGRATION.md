# Execution Framework Integration Guide

## Overview

This guide demonstrates how to integrate the **ValidationGateExecutor** and **FeedbackLoopOrchestrator** with the orchestration configuration files to create a fully functional agentic execution framework.

---

## Core Components

### 1. ValidationGateExecutor

**Location**: `runtime/shared/validation_executor.py`

**Purpose**: Execute validation gates with config integration, scope-aware word counting, and hard stops for critical failures.

**Key Features**:
- ✅ Loads validation gates from `resume_orchestration_config.py` and `outreach_orchestration_config.py`
- ✅ Supports scope-based validation (`per_bullet`, `per_segment`, `per_competency`, etc.)
- ✅ Implements hard stops for CRITICAL failures
- ✅ Differentiator distribution checking
- ✅ Gap coverage analysis
- ✅ Similarity/deduplication checks
- ✅ Placeholder and hallucination detection

### 2. FeedbackLoopOrchestrator

**Location**: `runtime/shared/feedback_loop_orchestrator.py`

**Purpose**: Manage adaptive regeneration with intelligent failure correction and temperature escalation.

**Key Features**:
- ✅ Max 5 regeneration attempts with checkpoint saving
- ✅ Adaptive temperature escalation based on failure type
- ✅ Reversion policy (revert if attempt N worse than N-1)
- ✅ Detailed failure feedback for regeneration prompts
- ✅ Message type transition support

---

## Integration Example: K.8 Competencies

### Step 1: Load Configuration

```python
from apps_rg.L3_orchestration.resume_orchestration_config import (
    VALIDATION_GATES,
    GLOBAL_WORD_COUNTS,
    DIFFERENTIATOR_DISTRIBUTION,
    SIMILARITY_THRESHOLDS,
    FEEDBACK_LOOP_CONFIG,
    ADAPTIVE_TEMPERATURE_CONFIG,
    K8_COMPETENCIES_CONFIG,
)
from runtime.shared.validation_executor import ValidationGateExecutor
from runtime.shared.feedback_loop_orchestrator import FeedbackLoopOrchestrator

# Initialize executor
validator = ValidationGateExecutor(
    validation_gates=VALIDATION_GATES,
    word_count_constraints=GLOBAL_WORD_COUNTS,
    differentiator_distribution=DIFFERENTIATOR_DISTRIBUTION,
    similarity_thresholds=SIMILARITY_THRESHOLDS,
)

# Initialize orchestrator
orchestrator = FeedbackLoopOrchestrator(
    max_attempts=FEEDBACK_LOOP_CONFIG["max_attempts"],
    checkpoint_saving=FEEDBACK_LOOP_CONFIG["checkpoint_saving"],
    reversion_enabled=FEEDBACK_LOOP_CONFIG["reversion_capability"],
    adaptive_temperature_config=ADAPTIVE_TEMPERATURE_CONFIG,
)
```

### Step 2: Define Generator Function

```python
async def generate_k8_competencies(context: Dict[str, Any], temperature: float) -> str:
    """Generate K.8 competencies with LLM.

    Args:
        context: Generation context with inputs
        temperature: Temperature for generation

    Returns:
        Generated competencies as string
    """
    from runtime.shared.multi_provider_clients import get_client, Provider

    # Get LLM client
    client = get_client(Provider.ANTHROPIC)

    # Build prompt with context
    prompt = build_k8_prompt(context, temperature)

    # Call LLM
    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def build_k8_prompt(context: Dict[str, Any], temperature: float) -> str:
    """Build K.8 generation prompt.

    Args:
        context: Generation context
        temperature: Current temperature

    Returns:
        Formatted prompt
    """
    jd_keyword_gap = context.get("JD_Keyword_Gap", [])
    authentic_phrasing = context.get("Authentic_Phrasing", [])

    # Check for regeneration feedback
    if "validation_failures" in context:
        return build_regeneration_prompt(context)

    # Initial generation prompt
    prompt = f"""Generate exactly 6 Strategic & Technical Competencies for a resume.

PRIMARY OBJECTIVE: Achieve ≥85% coverage of these JD keywords NOT yet used in K.4/K.5/K.6/K.7:
{', '.join(jd_keyword_gap)}

CONSTRAINTS (ZERO TOLERANCE):
1. Exactly 6 competencies
2. Each description: 24-30 words (STRICT)
3. Each title: 2-3 keywords from gap list
4. ≥2 competencies must use authentic phrasing from base pool
5. Max std dev across 6 descriptions: 3 words

AUTHENTIC PHRASING PATTERNS (use these):
{chr(10).join(f'- {p}' for p in authentic_phrasing[:5])}

FORMAT:
1. [Title]: [Description 24-30 words]
2. [Title]: [Description 24-30 words]
...

Temperature: {temperature:.2f}
"""

    return prompt


def build_regeneration_prompt(context: Dict[str, Any]) -> str:
    """Build regeneration prompt with exact failures.

    Args:
        context: Context with validation_failures

    Returns:
        Regeneration prompt
    """
    failure_summary = context.get("failure_summary", "")
    previous_content = context.get("previous_content", "")

    prompt = f"""REGENERATION REQUIRED

{failure_summary}

PREVIOUS OUTPUT:
{previous_content}

INSTRUCTIONS:
1. Fix ONLY the failing sections listed above
2. Maintain all other content unchanged
3. Ensure ALL constraints are met:
   - Word count: 24-30 per description
   - Std dev: ≤3 words
   - Gap coverage: ≥85%
   - Plausibility: ≥2 authentic

Generate the corrected version:
"""

    return prompt
```

### Step 3: Define Validator Function

```python
async def validate_k8_competencies(
    content: str,
    context: Dict[str, Any]
) -> ValidationResult:
    """Validate K.8 competencies.

    Args:
        content: Generated competencies
        context: Validation context

    Returns:
        ValidationResult
    """
    # Execute all K.8 validation gates
    results = validator.execute_all_gates(
        execution_point="POST_K8_GENERATION",
        content=content,
        k_node_id="K.9",  # K.8 is K.9 in current DAG
        context=context,
    )

    # Combine results
    all_passed = all(r.passed for r in results)
    all_failures = []
    for r in results:
        all_failures.extend(r.failures)

    # Return combined result
    if all_passed:
        return ValidationResult(
            status=ValidationStatus.PASS,
            gate_id="K8_COMBINED",
            execution_point="POST_K8_GENERATION",
            score=1.0,
        )
    else:
        # Find worst result
        worst = min(results, key=lambda r: r.score)
        return ValidationResult(
            status=worst.status,
            gate_id="K8_COMBINED",
            execution_point="POST_K8_GENERATION",
            failures=all_failures,
            action=worst.action,
            score=worst.score,
            message=worst.message,
        )
```

### Step 4: Execute with Feedback Loop

```python
async def execute_k8_with_feedback(initial_context: Dict[str, Any]) -> RegenerationResult:
    """Execute K.8 generation with feedback loop.

    Args:
        initial_context: Initial context with all required inputs

    Returns:
        RegenerationResult with final competencies
    """
    result = await orchestrator.execute_with_feedback(
        generator=generate_k8_competencies,
        validator=validate_k8_competencies,
        initial_context=initial_context,
        k_node_id="K.9",
    )

    if result.success:
        logger.info(f"K.8 generation successful after {result.attempts} attempts")
    elif result.reverted:
        logger.warning(f"K.8 reverted to better attempt after {result.attempts} attempts")
    else:
        logger.error(f"K.8 exhausted all {result.attempts} attempts")
        failure_report = orchestrator.generate_failure_report(result, "K.9")
        logger.error(failure_report)

    return result
```

### Step 5: Complete Execution Flow

```python
async def main():
    """Complete K.8 execution example."""

    # Prepare context
    context = {
        "JD_Keyword_Gap": [
            "machine learning", "scalability", "cloud architecture",
            "data pipelines", "microservices", "kubernetes",
            "real-time processing", "distributed systems",
            "MLOps", "feature engineering", "model deployment",
            "A/B testing", "data quality", "monitoring",
            "cost optimization", "security", "compliance",
        ],
        "Authentic_Phrasing": [
            "Built production ML systems at scale with measurable business impact",
            "Led cross-functional teams to deliver enterprise-grade solutions",
            "Architected cloud-native platforms serving millions of users",
        ],
        "Base_Competency_Pool": [
            "Machine Learning & AI: Designed and deployed production ML systems...",
            "Cloud Architecture: Built scalable cloud infrastructure on AWS/GCP...",
            "Data Engineering: Architected real-time data pipelines...",
        ],
        "K4_Headline": "AI/ML Engineering Leader | Cloud Architecture | Enterprise Scale",
        "K5_Summary": "Seasoned engineering leader with 10+ years...",
        "K6_K7_Bullets": [
            "Led team of 5 engineers to build ML platform...",
            "Architected microservices infrastructure on Kubernetes...",
        ],
    }

    # Execute with feedback loop
    result = await execute_k8_with_feedback(context)

    if result.success or result.reverted:
        print("✅ K.8 Competencies Generated:")
        print(result.final_content)
        print(f"\nAttempts: {result.attempts}")
        print(f"Final Score: {result.final_validation.score:.2f}")
    else:
        print("❌ K.8 Generation Failed")
        print(orchestrator.generate_failure_report(result, "K.9"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Validation Gate Execution Flow

### Execution Points

```python
execution_points = {
    "POST_CLERK_EXTRACTION_PRE_ARTIST_PHASE": [
        "VG_CLERK_SCAFFOLD_INTEGRITY",
    ],
    "POST_K1_GENERATION": [
        "VG_SUMMARY_GROUNDING_CHECK",
    ],
    "POST_K4_GENERATION": [
        "VG_HEADLINE_CHARACTER_COMPLIANCE",
    ],
    "POST_K8_GENERATION": [
        "VG_K8_COMPETENCY_WORD_COUNT_COMPLIANCE",
        "VG_K8_GAP_COVERAGE_CHECK",
        "VG_K8_REDUNDANCY_CHECK",
        "VG_K8_PLAUSIBILITY_CHECK",
    ],
    "PRE_FILE_WRITE": [
        "VG_PRODUCTION_READY_PROOF",
    ],
}
```

### Hard Stop Behavior

```python
# Example: Critical failure triggers immediate BLOCK
result = validator.execute_gate(
    gate_id="VG_K8_COMPETENCY_WORD_COUNT_COMPLIANCE",
    content=generated_content,
    k_node_id="K.9",
    execution_point="POST_K8_GENERATION",
    context=context,
)

if result.status == ValidationStatus.BLOCK:
    # HALT immediately - do not continue
    raise ValidationError(result.message)
```

---

## Adaptive Temperature Escalation

### Failure Type Classification

```python
failure_types = {
    "MECHANICAL": 0.05,  # Word count, char count → small increase
    "CREATIVE": 0.15,    # Placeholder, redundancy → large increase
    "SEMANTIC": 0.10,    # Forbidden words → medium increase
    "CONFLICT": 0.0,     # Impossible constraints → no increase (manual fix)
}
```

### Temperature Progression Example

```
Attempt 1: temp=0.6, fails with word count (MECHANICAL) → +0.05 = 0.65
Attempt 2: temp=0.65, fails with placeholder (CREATIVE) → +0.15 = 0.80
Attempt 3: temp=0.80, fails with redundancy (CREATIVE) → +0.15 = 0.95 (capped at 0.9)
Attempt 4: temp=0.9, PASS
```

---

## Reversion Policy

### Example Scenario

```
Attempt 1: score=0.65 (word count violations)
Attempt 2: score=0.80 (improved, only 1 violation)
Attempt 3: score=0.55 (worse! added placeholder)

→ REVERT to Attempt 2 (score 0.80 > 0.55)
```

### Implementation

```python
if checkpoint.score < prev_checkpoint.score:
    logger.info(f"Reverting to attempt {attempt-1}")
    return RegenerationResult(
        success=True,
        final_content=prev_checkpoint.content,
        attempts=attempt,
        checkpoints=checkpoints,
        final_validation=prev_checkpoint.validation_result,
        reverted=True,
    )
```

---

## Message Type Transitions (Outreach)

### Example: SHORT_NEW → LONG_NEW

```python
# Apply transition
content, context = orchestrator.apply_message_transition(
    current_route="SHORT_NEW",
    target_route="LONG_NEW",
    content=current_content,
    context=current_context,
)

# Context now includes:
# - expansion_requirements: ["Add 1-2 more specific anchors", ...]
# - add_subject_line: True
# - add_resume_attachment: True
```

---

## Critical Grounding Checks

### Metric Grounding (LIC-QA-041)

```python
# Every metric must map to metric_source_map
context["metric_source_map"] = {
    "40% reduction": {
        "source": "resume_bullet_3",
        "rag_evidence": ["CI/CD pipeline", "automation"],
    },
}

# Validator checks each metric in content
result = validator.execute_gate(
    gate_id="VG_METRIC_GROUNDING",
    content=message_content,
    k_node_id="K.3",
    execution_point="POST_K3_GENERATION",
    context=context,
)
```

### Overview Customization (Strictly <75%)

```python
# Must be STRICTLY less than 0.75 (not ≤)
result = validator.execute_gate(
    gate_id="VG_OVERVIEW_CUSTOMIZATION",
    content=overview_content,
    k_node_id="K.5B",
    execution_point="POST_K5B_GENERATION",
    context={
        "master_baseline": original_overview,
    },
)

# Similarity of exactly 0.75 = FAIL
# Similarity of 0.74 = PASS
```

---

## Next Steps

1. **Implement LLM Integration**: Connect generator functions to actual LLM providers
2. **Build K-Node Agents**: Create agent classes that use these executors
3. **Add RAG Integration**: Implement multi-hop RAG for context enrichment
4. **Create Orchestrator**: Build top-level orchestrator that manages K-node DAG execution
5. **Integration Testing**: Test complete flow with real resume/outreach data

---

## Status

**Execution Framework**: ✅ Complete
**Config Integration**: ✅ Complete
**Validation Logic**: ✅ Complete
**Feedback Loop**: ✅ Complete
**LLM Integration**: ❌ Pending
**Agent Implementation**: ❌ Pending
**RAG Integration**: ❌ Pending
**End-to-End Testing**: ❌ Pending
