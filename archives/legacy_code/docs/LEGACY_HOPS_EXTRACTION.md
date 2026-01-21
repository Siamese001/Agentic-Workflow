# Legacy HOPs Architecture - Valuable Patterns Extracted

## Overview

This document catalogs valuable orchestration patterns, quality controls, and configurations extracted from the legacy deterministic HOPs architecture (Job_Workflow v1.9.2, v54.00, v61.27.9) that augment the new agentic architecture.

**Key Insight**: While the HOPs are NOT agentic (deterministic state machine with single LLM call), they contain **battle-tested quality controls** and **production-hardened constraints** that should inform agent behavior in the new architecture.

---

## 1. Reasoning Configurations per K-Node

### Temperature Settings (Production-Tested)

```python
# From HOP-3 Phase A (v1.9.2)
temperatures = {
    "K.0": 0.3,   # Thematic analysis - conservative
    "K.1": 0.9,   # Executive summary - highly creative
    "K.4": 0.8,   # Headline - creative
    "K.5A": 0.7,  # Unify bullets - balanced
    "K.5B": 0.85, # Unify overview - creative
    "K.6A": 0.7,  # IBM bullets - balanced
    "K.6B": 0.85, # IBM overview - creative
    "K.7": 0.2,   # Prior experience - conservative
    "K.8": 0.75,  # Competencies - balanced
    "K.9": 0.8,   # Cover letter - creative
    "K.11": 0.1,  # Skills - deterministic
}
```

### RAG Configurations (from v54.00)

**K.2.5 (Competitive Positioning)** - Most intensive RAG:
- Temperature: 0.3
- RAG Type: Agentic
- RAG Total Calls: 24
- RAG Hops: 3
- Self-Consistency: 6 runs
- ToT Branches: 5
- ToT Depth: 4

**K.10 (Cover Letter)** - Deep multi-hop RAG:
- Temperature: 0.4
- RAG Type: Agentic
- RAG Total Calls: 25
- RAG Hops: 4
- Self-Consistency: 3 runs

**K.11 (Skills)** - No RAG, deterministic:
- Temperature: 0.2
- RAG Type: Internal
- RAG Total Calls: 0
- Self-Consistency: 3 runs

---

## 2. Word Count Constraints (GLOBAL_ENFORCEMENT_SPEC)

### Strict Enforcement Rules

```python
word_counts = {
    "K.1_executive_summary": {
        "min": 118,
        "max": 135,
        "scope": "total",
    },
    "K.4_headline": {
        "max": 4,  # per segment
        "char_min": 60,
        "char_max": 90,
    },
    "K.5A_unify_bullets": {
        "min": 28,
        "max": 33,
        "scope": "per_bullet",
        "count": 7,  # exactly 7 bullets
    },
    "K.6A_ibm_bullets": {
        "min": 24,
        "max": 30,
        "scope": "per_bullet",
        "count": 6,  # exactly 6 bullets
    },
    "K.8_competencies": {
        "min": 24,
        "max": 30,
        "scope": "per_competency",
        "count": 6,  # exactly 6 competencies
    },
}
```

---

## 3. Validation Gates (Production-Hardened)

### Critical Gates from v61.27.9

**VG_CLERK_SCAFFOLD_INTEGRITY**:
- Execution Point: POST_CLERK_EXTRACTION_PRE_ARTIST_PHASE
- Blocking: True
- Checks:
  - Master resume file present
  - File parse validation
  - Critical fields extracted
  - Bullet pool adequate (min 20 bullets)
  - Overview baselines extracted

**VG_PRODUCTION_READY_PROOF**:
- Execution Point: PRE_FILE_WRITE
- Blocking: True
- Checks:
  - Tag sanitization (no debug tags in output)
  - Overview customization (max 74% similarity to master)
  - Round numbers (max 2 across resume)
  - Synthetic plausibility

**VG_SUMMARY_GROUNDING_CHECK**:
- Execution Point: POST_K1_GENERATION
- Blocking: True
- Checks:
  - All claims grounded in source
  - No hallucinated facts
  - Word count compliance (118-135)

---

## 4. Provenance Rules (Authenticity Control)

### Bullet Provenance Patterns

```python
provenance = {
    "K.5A": "3V-3T-1S",  # 3 Verbatim, 3 Transformed, 1 Synthetic
    "K.6A": "2V-3T-1S",  # 2 Verbatim, 3 Transformed, 1 Synthetic
}

authenticity_ratios = {
    "executive": {"positioning": 0.8, "authenticity": 0.2},
    "bullets": {"positioning": 0.5, "authenticity": 0.5},
    "skills": {"positioning": 0.8, "authenticity": 0.2},
}
```

**Key Insight**: Bullets should be 50/50 positioning vs authenticity, while executive summary and skills lean heavily toward positioning (80%).

---

## 5. Feedback Loop Pattern (from HOP-3)

### Regeneration Logic

```python
feedback_loop = {
    "max_attempts": 5,
    "checkpoint_saving": True,
    "reversion_capability": True,
    "reversion_policy": "If attempt N fails worse than N-1, revert to N-1",
    "exhaustion_policy": "After 5 attempts, HALT with detailed failure report",
}

regeneration_prompt_includes = [
    "Original enriched scaffold",
    "EXACT validation failures with actual vs expected values",
    "Instructions to fix ONLY failing sections",
    "XML template for failing sections only",
]
```

**Example**: "K.1 has 100 words (expected 118-135). K.5A bullet 3 has 25 words (expected 28-33). Regenerate ONLY K.1 and K.5A bullet 3."

---

## 6. Similarity Thresholds (Redundancy Detection)

```python
similarity_thresholds = {
    "overview_to_master_natural": 0.75,  # Must be < 75% similar
    "overview_to_master_synthetic": 0.65,
    "overview_to_bullet": 0.65,
    "inter_bullet": 0.7,  # Bullets must be < 70% similar to each other
    "headline_to_summary": 0.6,
    "inter_competency": 0.65,
}
```

**Validation Method**: `cosine_similarity + levenshtein_distance + keyword_match`

---

## 7. Industry Adjacency Validation (from v1.9.2)

### Adjacency Map

```python
industry_adjacency = {
    "LegalTech": ["FinTech", "RegTech", "Compliance", "Enterprise SaaS"],
    "FinTech": ["LegalTech", "RegTech", "Banking", "Insurance", "Payments"],
    "HealthTech": ["Biotech", "MedTech", "Insurance", "Healthcare"],
    # ...
}

confidence_thresholds = {
    "high": 0.9,      # Use target industry directly
    "moderate": 0.7,  # Use transitional phrasing
    "low": 0.5,       # Use candidate's actual industry + warn
}
```

**Headline Strategy**:
- High confidence (≥0.9): "LegalTech Executive"
- Moderate (0.7-0.9): "FinTech Executive Transitioning to LegalTech"
- Low (<0.7): Use candidate's actual industry + HIGH severity warning

---

## 8. Round Number Detection (from v61.27.9)

### Contextual Exclusions

```python
round_number_config = {
    "max_total_across_resume": 2,
    "exclusions": ["100%", "24/7", "365"],
    "contextual_exclusions": [
        {
            "pattern": "100%",
            "context": ["uptime", "SLA", "availability", "compliance"],
            "detection_method": "PHRASE_MATCH_WITHIN_10_WORDS",
        },
        {
            "pattern": "50%",
            "context": ["reduction", "improvement", "cost savings"],
            "detection_method": "PHRASE_MATCH_WITHIN_10_WORDS",
        },
    ],
    "variation_range": [-3, 3],  # Suggest 47% instead of 50%
}
```

**Logic**: Round numbers are flagged UNLESS they appear within 10 words of context keywords (e.g., "100% uptime" is allowed, "100% improvement" is flagged).

---

## 9. Executive Summary Structure Rules

```python
executive_summary_rules = {
    "sentence_count": 6,  # Exactly 6 sentences
    "style": "narrative_arc",
    "forbidden_content": ["bullet-like", "numbered_list"],
}
```

**Validation**: Must be narrative prose, not bullet points.

---

## 10. Staging Buffer Immutability Pattern

### Immutability Enforcement (from HOP-4)

```python
staging_buffer_pattern = {
    "creation": "HOP-4",
    "lock_point": "After HOP-4 completion",
    "access_mode": "READ_ONLY for all downstream hops",
    "scope_isolation": "artist_output deleted before validation gates",
    "hash_chain": "H0→H1→H2→H3→H4→...→H8 for audit trail",
}
```

**Key Insight**: Once staging buffer is created, it becomes immutable. Validation gates can only read from it, never modify.

---

## 11. File Complexity Gates (from v61.27.9)

```python
file_complexity_thresholds = {
    "total_file_count_max": 5,
    "total_file_size_mb_max": 10,
    "on_exceed": "HALT_AND_PROMPT_STAGED_LOADING",
}

staged_loading_protocol = {
    "stage_1_required": ["master_resume", "jd_url_or_text"],
    "stage_2_required": ["App_Schema_v4.json", "SaaS_Roles.json", "Hyphenation_Rules.json"],
}
```

**Rationale**: Prevent overwhelming the system with too many files at once.

---

## 12. Competency Ranking Rules

```python
competency_ranking = {
    "pos_1": ["tier_1"],           # First competency must be tier 1
    "pos_2": ["tier_1", "tier_2"], # Second can be tier 1 or 2
    "pos_3": ["tier_1", "tier_2"], # Third can be tier 1 or 2
}
```

**Enforcement**: Top competencies must be highest tier.

---

## 13. Differentiator Distribution

```python
differentiator_distribution = {
    "K.1": 2,   # 2 differentiators in executive summary
    "K.4": 1,   # 1 in headline
    "K.5A": 5,  # 5 in Unify bullets
    "K.5B": 2,  # 2 in Unify overview
    "K.6A": 3,  # 3 in IBM bullets
    "K.6B": 1,  # 1 in IBM overview
    "K.8": 2,   # 2 in competencies
    "K.9": 3,   # 3 in cover letter
    "TOTAL": 20,  # Exactly 20 differentiators across resume
}
```

**Purpose**: Ensure even distribution of competitive positioning keywords.

---

## How to Use in Agentic Architecture

### 1. Agent Goal Configuration

Each K-node agent should have goals informed by these constraints:

```python
class K1_SummaryAgent(Agent):
    def __init__(self):
        self.goal = Goal(
            objective="Generate executive summary",
            constraints=[
                WordCountConstraint(min=118, max=135),
                SentenceCountConstraint(exact=6),
                StyleConstraint(type="narrative_arc"),
                DifferentiatorConstraint(count=2),
            ],
            quality_gates=[
                "VG_SUMMARY_GROUNDING_CHECK",
                "VG_HALLUCINATION_CHECK",
            ],
        )
        self.reasoning_config = ReasoningConfig(
            temperature=0.9,  # From legacy
            rag_type=RAGType.HYBRID,
            rag_total_calls=5,
            self_consistency=5,
        )
```

### 2. Validation Agent Integration

```python
class ValidationAgent(Agent):
    def __init__(self):
        self.gates = load_validation_gates()

    async def validate(self, content, execution_point):
        gates = get_gates_for_point(execution_point)
        for gate in gates:
            result = await self.run_gate(gate, content)
            if gate.blocking and not result.passed:
                return ValidationResult(
                    passed=False,
                    gate_id=gate.gate_id,
                    message=gate.halt_message,
                    action="REGENERATE" if gate.on_fail == "REGENERATE" else "HALT",
                )
```

### 3. Feedback Loop Agent

```python
class FeedbackLoopOrchestrator:
    async def execute_with_feedback(self, agent, max_attempts=5):
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
                return checkpoints[-2]["result"]  # Revert to previous

            # Regenerate with exact failures
            agent.add_feedback(validation.failures)

        raise MaxAttemptsExceeded(checkpoints)
```

---

## Summary of Value Extracted

✅ **Production-tested temperature settings** per K-node
✅ **RAG configurations** (type, hops, total calls) per K-node
✅ **Word/char count constraints** with exact min/max values
✅ **Validation gates** with blocking behavior and halt messages
✅ **Provenance rules** for authenticity control
✅ **Feedback loop patterns** with regeneration logic
✅ **Similarity thresholds** for redundancy detection
✅ **Industry adjacency validation** with confidence thresholds
✅ **Round number detection** with contextual exclusions
✅ **Staging buffer immutability** pattern
✅ **Competency ranking** rules
✅ **Differentiator distribution** requirements

These patterns are now available in `apps_rg/L3_orchestration/resume_orchestration_config.py` and can be used to configure agent behavior, validation gates, and quality controls in the agentic architecture.
