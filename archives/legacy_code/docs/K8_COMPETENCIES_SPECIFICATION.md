# K.8 Competencies Agent - Complete Specification Blueprint

## Overview

**Agent ID**: K.8 (K.9 in current DAG structure)
**Element**: Leadership Competencies
**Execution Mode**: GVD (Generate → Validate → Display)
**Tier**: Tier 1 Enhancement (35% scoring weight)
**Status**: Blueprint (Execution Framework Required)

---

## Primary Objective

Achieve **≥85% coverage** of all Job Description (JD) keywords that have **NOT** been addressed in previously generated content:
- K.4 (Headline)
- K.5 (Executive Summary)
- K.6 (Unify Bullets)
- K.7 (IBM Bullets)

**Secondary Objective**: Incorporate authentic phrasing patterns extracted from Phase 2 LinkedIn and Industry Framework searches.

---

## Input Requirements

### Required Inputs (from Clerk Scaffold & Prior K-Nodes)

| Input Field | Source | Data Type | Constraint |
|------------|--------|-----------|------------|
| **JD_Keyword_Gap** | K.0/Clerk (Phase 1) | List[str] | 15-25 JD keywords with <2 occurrences in K.4/K.5/K.6/K.7 |
| **Authentic_Phrasing** | K.0 | List[str] | Competency phrasing patterns (e.g., "Built production ML systems at scale") |
| **Base_Competency_Pool** | Clerk (Master Resume) | List[str] | Factual, uncustomized text for plausibility check |
| **K4_Headline** | K.4 Output | str | Required for deduplication check |
| **K5_Summary** | K.5 Output | str | Required for deduplication check |
| **K6_K7_Bullets** | K.6/K.7 Output | List[str] | Required for deduplication check |

---

## Output Schema

### Mandatory Structure

```python
@dataclass
class Competency:
    """Single competency item."""
    title: str  # Keyword-dense noun phrase with 2-3 gap keywords
    description: str  # 24-30 words (ZERO TOLERANCE)
    gap_keywords_covered: List[str]  # Keywords from JD_Keyword_Gap
    authentic_phrasing_used: bool  # True if uses Authentic_Phrasing pattern
    source_plausibility: str  # "authentic" | "synthetic"

@dataclass
class K8Output:
    """K.8 Competencies output."""
    competencies: List[Competency]  # Exactly 6 items
    gap_coverage_percentage: float  # Must be ≥0.85
    total_gap_keywords: int
    covered_gap_keywords: int
    word_count_stats: Dict[str, float]  # mean, std_dev, min, max
```

### Zero-Tolerance Constraints

| Field | Requirement | Enforcement |
|-------|-------------|-------------|
| **Competency Count** | Exactly 6 items | CRITICAL - Regenerate if ≠6 |
| **Title Format** | Keyword-dense noun phrase with 2-3 gap keywords | HIGH - Regenerate if <2 keywords |
| **Description Length** | 24-30 words (ZERO TOLERANCE) | CRITICAL - Regenerate if outside range |
| **Plausibility** | ≥2 items verbatim/near-verbatim from Base_Competency_Pool | CRITICAL - Regenerate if <2 |
| **Gap Coverage** | ≥85% of JD_Keyword_Gap covered | CRITICAL - HALT if <70%, WARN if 70-84% |
| **Word Count Variance** | Max std dev = 3 words across 6 descriptions | CRITICAL - Regenerate if >3 |

---

## Reasoning Configuration

### Hybrid CoT/ToT with Self-Consistency

```python
reasoning_config = {
    "strategy": "SELF_CONSISTENCY",
    "temperature": 0.6,
    "top_p": 0.85,
    "self_consistency_runs": 2,
    "tot_branches": 2,
    "rag_type": "AGENTIC",
    "rag_total_calls": 20,
    "rag_hops": 3,
    "claim_verification_mode": "STRICT",
}
```

**Rationale**:
- Temperature 0.6: Balance between creativity and consistency
- Self-Consistency k=2: Generate 2 candidates, select best
- RAG Agentic: Deep multi-hop retrieval for authentic phrasing
- 20 RAG calls, 3 hops: Intensive research for LinkedIn/Industry patterns

---

## Validation Gates (Critical Path)

### Gate 1: VG_K8_COMPETENCY_WORD_COUNT_COMPLIANCE

**Execution Point**: POST_K8_GENERATION
**Blocking**: True
**Severity**: CRITICAL

**Checks**:
1. **WC_07**: All 6 descriptions must be 24-30 words
2. **Variance Check**: Max std dev across 6 items ≤ 3 words

**Action on Fail**: Trigger Regeneration Engine (Max 2 attempts per item)

**Error Message**:
```
K.8 competency word count violation.
- Competency 1: 32 words (FAIL - max 30)
- Competency 3: 22 words (FAIL - min 24)
- Std Dev: 4.2 words (FAIL - max 3)

Regenerating K.8 output (Attempt 1/2)...
```

---

### Gate 2: VG_K8_GAP_COVERAGE_CHECK

**Execution Point**: POST_K8_GENERATION
**Blocking**: True
**Severity**: CRITICAL

**Checks**:
1. **Gap Coverage**: ≥85% of JD_Keyword_Gap must be covered

**Thresholds**:
- **≥85%**: PASS
- **70-84%**: WARN (proceed with warning)
- **<70%**: CRITICAL HALT

**Action on Fail**:
- If <70%: HALT workflow
- If 70-84%: Proceed with warning in QA report

**Error Message**:
```
K.8 gap coverage: 68% (CRITICAL - below 70% threshold)

Gap Analysis:
- Total gap keywords: 20
- Covered: 13
- Missing: 7 (machine learning, scalability, cloud architecture, ...)

HALT: Cannot proceed with <70% gap coverage.
```

---

### Gate 3: VG_K8_REDUNDANCY_CHECK

**Execution Point**: POST_K8_GENERATION
**Blocking**: True
**Severity**: CRITICAL

**Checks**:
1. **Dedup vs K.5**: Cosine similarity ≤ 0.50
2. **Dedup vs K.6/K.7**: Cosine similarity ≤ 0.60

**Action on Fail**: Regenerate entire K.8 output

**Error Message**:
```
K.8 redundancy violation:
- Similarity to K.5 Summary: 0.62 (FAIL - max 0.50)
- Similarity to K.6/K.7 Bullets: 0.58 (PASS - max 0.60)

Regenerating entire K.8 output to reduce overlap with K.5...
```

---

### Gate 4: VG_K8_PLAUSIBILITY_CHECK

**Execution Point**: POST_K8_GENERATION
**Blocking**: True
**Severity**: CRITICAL

**Checks**:
1. **Authentic Count**: ≥2 competencies must be verbatim/near-verbatim from Base_Competency_Pool

**Action on Fail**: Regenerate K.8 output

**Error Message**:
```
K.8 plausibility violation:
- Authentic competencies: 1 (FAIL - min 2)
- Synthetic competencies: 5

At least 2 competencies must be grounded in Base_Competency_Pool.
Regenerating with explicit plausibility constraint...
```

---

## Regeneration Engine

### Feedback Loop Configuration

```python
regeneration_config = {
    "max_attempts": 2,  # Per competency item
    "checkpoint_saving": True,
    "reversion_capability": True,
    "reversion_policy": "If attempt N fails worse than N-1, revert to N-1",
    "exhaustion_policy": "After 2 attempts, HALT with detailed failure report",
}
```

### Regeneration Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Word Count Violation** | Any description outside 24-30 words | Regenerate specific competency (max 2 attempts) |
| **Variance Violation** | Std dev > 3 words | Regenerate all 6 competencies |
| **Gap Coverage <70%** | Coverage below critical threshold | HALT workflow |
| **Gap Coverage 70-84%** | Coverage below target but above critical | WARN and proceed |
| **Redundancy Violation** | Similarity to K.5 >0.50 or K.6/K.7 >0.60 | Regenerate all 6 competencies |
| **Plausibility Violation** | <2 authentic competencies | Regenerate all 6 competencies |

### Regeneration Prompt Template

```python
regeneration_prompt = f"""
REGENERATION REQUIRED: K.8 Competencies

Validation Failures:
{validation_failures}

Original Output:
{original_competencies}

Constraints for Regeneration:
1. Word Count: ALL descriptions must be 24-30 words (ZERO TOLERANCE)
2. Gap Coverage: Must cover ≥85% of these keywords: {jd_keyword_gap}
3. Deduplication: Similarity to K.5 ≤0.50, to K.6/K.7 ≤0.60
4. Plausibility: ≥2 competencies from Base_Competency_Pool

Regenerate ONLY the failing competencies:
{failing_competency_ids}
"""
```

---

## Execution Framework Requirements

### Required Components (Not Yet Built)

#### 1. ValidationGateExecutor

```python
class ValidationGateExecutor:
    """Execute validation gates with blocking behavior."""

    def execute_gate(
        self,
        gate: ValidationGate,
        content: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Execute a single validation gate.

        Args:
            gate: ValidationGate configuration
            content: Generated content to validate
            context: Execution context with prior outputs

        Returns:
            ValidationResult with pass/fail and details
        """
        pass

    def execute_all_gates(
        self,
        execution_point: str,
        content: Any,
        context: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Execute all gates for an execution point.

        Returns:
            List of validation results
        """
        pass
```

#### 2. FeedbackLoopOrchestrator

```python
class FeedbackLoopOrchestrator:
    """Orchestrate regeneration with feedback loop."""

    async def execute_with_feedback(
        self,
        agent: Agent,
        max_attempts: int = 2
    ) -> AgentResult:
        """Execute agent with feedback loop.

        Args:
            agent: Agent to execute
            max_attempts: Maximum regeneration attempts

        Returns:
            AgentResult with final output or failure
        """
        checkpoints = []

        for attempt in range(1, max_attempts + 1):
            result = await agent.execute()
            validation = await self.validator.validate(result)

            checkpoints.append({
                "attempt": attempt,
                "result": result,
                "validation": validation,
            })

            if validation.passed:
                return result

            # Reversion capability
            if attempt > 1 and validation.score < checkpoints[-2]["validation"].score:
                return checkpoints[-2]["result"]

            # Add exact failures to agent feedback
            agent.add_feedback(validation.failures)

        raise MaxAttemptsExceeded(checkpoints)
```

#### 3. WordCountConstraintValidator

```python
class WordCountConstraintValidator:
    """Validate word count constraints."""

    def validate(
        self,
        text: str,
        constraint: WordCountConstraint
    ) -> ValidationResult:
        """Validate text against word count constraint.

        Args:
            text: Text to validate
            constraint: Word count constraint

        Returns:
            ValidationResult with pass/fail
        """
        word_count = len(text.split())

        if constraint.min and word_count < constraint.min:
            return ValidationResult(
                passed=False,
                message=f"Word count {word_count} < min {constraint.min}",
                actual=word_count,
                expected={"min": constraint.min, "max": constraint.max},
            )

        if constraint.max and word_count > constraint.max:
            return ValidationResult(
                passed=False,
                message=f"Word count {word_count} > max {constraint.max}",
                actual=word_count,
                expected={"min": constraint.min, "max": constraint.max},
            )

        return ValidationResult(passed=True, actual=word_count)
```

#### 4. GapCoverageAnalyzer

```python
class GapCoverageAnalyzer:
    """Analyze JD keyword gap coverage."""

    def calculate_coverage(
        self,
        competencies: List[Competency],
        jd_keyword_gap: List[str]
    ) -> GapCoverageResult:
        """Calculate gap coverage percentage.

        Args:
            competencies: Generated competencies
            jd_keyword_gap: Keywords to cover

        Returns:
            GapCoverageResult with coverage stats
        """
        covered_keywords = set()

        for comp in competencies:
            covered_keywords.update(comp.gap_keywords_covered)

        coverage = len(covered_keywords) / len(jd_keyword_gap)

        return GapCoverageResult(
            coverage_percentage=coverage,
            total_gap_keywords=len(jd_keyword_gap),
            covered_keywords=list(covered_keywords),
            missing_keywords=list(set(jd_keyword_gap) - covered_keywords),
        )
```

---

## Example Execution Flow

### Step 1: Input Preparation

```python
k8_inputs = {
    "JD_Keyword_Gap": [
        "machine learning", "scalability", "cloud architecture",
        "data pipelines", "microservices", "kubernetes",
        "real-time processing", "distributed systems",
        # ... 15-25 total keywords
    ],
    "Authentic_Phrasing": [
        "Built production ML systems at scale with measurable business impact",
        "Led cross-functional teams to deliver enterprise-grade solutions",
        "Architected cloud-native platforms serving millions of users",
    ],
    "Base_Competency_Pool": [
        "Machine Learning & AI: Designed and deployed production ML systems...",
        "Cloud Architecture: Built scalable cloud infrastructure on AWS/GCP...",
        # ... from master resume
    ],
    "K4_Headline": "AI/ML Engineering Leader | Cloud Architecture | Enterprise Scale",
    "K5_Summary": "Seasoned engineering leader with 10+ years...",
    "K6_K7_Bullets": [
        "Led team of 5 engineers to build ML platform...",
        # ... all bullets from K.6 and K.7
    ],
}
```

### Step 2: Generation (Self-Consistency k=2)

```python
# Generate 2 candidates
candidate_1 = await k8_agent.generate(k8_inputs, temperature=0.6)
candidate_2 = await k8_agent.generate(k8_inputs, temperature=0.6)

# Select best based on gap coverage
best_candidate = select_best(candidate_1, candidate_2, metric="gap_coverage")
```

### Step 3: Validation

```python
validation_results = []

# Gate 1: Word Count
wc_result = word_count_validator.validate(best_candidate)
validation_results.append(wc_result)

# Gate 2: Gap Coverage
gap_result = gap_coverage_analyzer.calculate_coverage(
    best_candidate.competencies,
    k8_inputs["JD_Keyword_Gap"]
)
validation_results.append(gap_result)

# Gate 3: Redundancy
redundancy_result = redundancy_checker.check(
    best_candidate,
    k8_inputs["K5_Summary"],
    k8_inputs["K6_K7_Bullets"]
)
validation_results.append(redundancy_result)

# Gate 4: Plausibility
plausibility_result = plausibility_checker.check(
    best_candidate,
    k8_inputs["Base_Competency_Pool"]
)
validation_results.append(plausibility_result)
```

### Step 4: Regeneration (if needed)

```python
if not all(r.passed for r in validation_results):
    failures = [r for r in validation_results if not r.passed]

    # Regenerate with feedback
    regenerated = await feedback_loop.execute_with_feedback(
        k8_agent,
        max_attempts=2,
        failures=failures
    )

    # Re-validate
    validation_results = validate_all(regenerated)
```

### Step 5: Display

```python
if all(r.passed for r in validation_results):
    display_k8_output(best_candidate)
else:
    halt_with_error_report(validation_results)
```

---

## Success Criteria

✅ **All 6 competencies generated**
✅ **All descriptions 24-30 words (ZERO TOLERANCE)**
✅ **Word count std dev ≤ 3 words**
✅ **Gap coverage ≥85%** (WARN if 70-84%, HALT if <70%)
✅ **Similarity to K.5 ≤0.50**
✅ **Similarity to K.6/K.7 ≤0.60**
✅ **≥2 competencies authentic from Base_Competency_Pool**
✅ **2-3 gap keywords per title**

---

## Next Steps for Implementation

1. **Build ValidationGateExecutor** (Priority 1)
   - Implement word count validation
   - Implement gap coverage calculation
   - Implement redundancy checking
   - Implement plausibility verification

2. **Build FeedbackLoopOrchestrator** (Priority 2)
   - Implement regeneration loop
   - Implement checkpoint saving
   - Implement reversion capability

3. **Build K.8 Agent** (Priority 3)
   - Integrate with LLM provider
   - Implement self-consistency generation
   - Implement RAG integration
   - Implement authentic phrasing injection

4. **Integration Testing** (Priority 4)
   - Test with real JD keyword gaps
   - Test regeneration scenarios
   - Test edge cases (gap coverage 69%, 71%, 84%, 86%)
   - Validate word count enforcement

---

## Blueprint Status

**Design**: ✅ Complete
**Configuration**: ✅ Complete
**Execution Framework**: ❌ Not Built
**Agent Implementation**: ❌ Not Built
**Integration**: ❌ Not Built
**Testing**: ❌ Not Built

**Ready for**: Parallel development of execution framework components.
