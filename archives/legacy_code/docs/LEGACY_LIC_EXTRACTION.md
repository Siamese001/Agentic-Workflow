# Legacy LIC (LinkedIn Outreach) - Valuable Patterns Extracted

## Overview

This document catalogs valuable orchestration patterns, quality controls, and configurations extracted from the legacy LinkedIn Intelligent Composer (LIC) architecture (v10.10, v8.61, v5.6.2, v11.9, LinkedInCanonical v2.90) that augment the new agentic architecture.

**Key Insight**: Like the resume HOPs, the LIC architecture is NOT fully agentic (deterministic routing with controlled LLM generation), but contains **battle-tested quality controls** and **production-hardened constraints** for LinkedIn outreach.

---

## 1. Route Configurations (Message Delivery Channels)

### Route Types

```python
routes = {
    "CONNECTION_REQ": {
        "char_limit": 300,
        "k_nodes_enabled": ["K.1", "K.3", "K.5", "K.6", "K.7"],
        "k_nodes_format": {
            "K.3": "compressed",
            "K.5": "micro",
        },
        "cta_word_limit": 5,
        "signature_format": "simplified",
        "subject_line": False,
        "attachments_allowed": False,
    },
    "INMAIL": {
        "char_limit": 1900,
        "k_nodes_enabled": ["K.1", "K.2", "K.3", "K.4", "K.5", "K.6", "K.7"],
        "constraints": ["job_title_in_first_50_words"],
        "subject_line": True,
        "attachments_allowed": True,
    },
    "SHORT_NEW": {
        "char_limit": {"min": 360, "max": 380},
        "constraints": [
            "no_resume_clause",
            "one_quantified_metric_required",
            "recipient_value_clause_required",
        ],
        "cta_word_limit": 10,
    },
    "FOLLOW_UP": {
        "char_limit": 1500,
        "constraints": [
            "continuity_clause_required",
            "prior_date_reference_required",
            "no_opener_duplication",
            "no_metric_duplication",
        ],
    },
}
```

---

## 2. Archetype Configurations (Recipient Personalization)

### 4-Archetype Standard (from v11.6)

**C_LEVEL** (CEO minus 1 level):
- Temperature: 0.4
- RAG: Agentic, 25 calls, 4 hops
- Self-Consistency: 5 runs
- ToT Branches: 5
- Message Format: ANALYST_LEVEL_PITCH
- Tone: thought_leadership
- **Special Requirement**: Deep Research Query (DRQ) with ≥2 authoritative external sources

**EXECUTIVE** (VP+):
- Temperature: 0.5
- RAG: Hybrid, 17 calls, 3 hops
- Self-Consistency: 4 runs
- ToT Branches: 3
- Message Format: EXECUTIVE_PITCH
- Tone: strategic
- **Special Requirement**: RAG Enrichment Summary mandatory

**SENIOR_TA** (Technical Authority/Staff Engineer):
- Temperature: 0.6
- RAG: Hybrid, 15 calls, 3 hops
- Self-Consistency: 3 runs
- Message Format: TA_PITCH
- Tone: professional_warm
- **Special Requirement**: Mandatory profile-RAG (2 insights from About section)

**RECRUITER**:
- Temperature: 0.7
- RAG: Hybrid, 10 calls, 2 hops
- Self-Consistency: 2 runs
- Message Format: RECRUITER_PITCH
- Tone: job_focused

---

## 3. Archetype Classification (from LinkedInCanonical v2.90)

### CXO Precedence Rule ⭐

```python
# Step 1: Check for CXO-level tokens FIRST
cxo_tokens = ["CEO", "CXO", "CRO", "President", "COO", "CTO", "CIO", "CFO", "CDO", "Chief"]

if any(token in title for token in cxo_tokens):
    archetype = "C_LEVEL"  # IMMEDIATE assignment, skip other checks

# Step 2: Else check Executive tokens
elif any(token in title for token in ["EVP", "SVP", "VP", "Head of", "GM"]):
    archetype = "EXECUTIVE"

# Step 3: Else check TA tokens
elif any(token in title for token in ["Talent Acquisition", "TA", "Recruiter"]):
    archetype = "SENIOR_TA"
```

**Key Insight**: CXO tokens take absolute precedence. If "CXO" appears anywhere in title/headline/about, route to C_LEVEL immediately.

---

## 4. Validation Rules (107 Rules from v10.10)

### Critical Rules (BLOCK immediately)

**LIC-QA-001: Placeholder Detection**
- Severity: CRITICAL
- Description: Detect placeholders like [NAME], {company}
- Enforcement: BLOCK
- Error Code: LIC-E001

**LIC-QA-002: Per-Claim Confidence Threshold**
- Severity: CRITICAL
- Description: Each claim must have confidence ≥ 0.70
- Enforcement: BLOCK
- Error Code: LIC-E002

**LIC-QA-003: Hallucination Detection**
- Severity: CRITICAL
- Description: No claims without supporting RAG evidence
- Enforcement: BLOCK
- Error Code: LIC-E003

**LIC-QA-104: Aggregate Confidence Enforcement**
- Severity: CRITICAL
- Description: Aggregate confidence must be ≥ 0.95
- Enforcement: BLOCK
- Threshold: 0.95

### High Severity Rules (REGENERATE)

**LIC-QA-004: Message Diversity Check**
- Severity: HIGH
- Description: Message must be <0.85 similar to previous messages
- Enforcement: REGENERATE
- Threshold: 0.85

**LIC-QA-005: Job Title Placement (INMAIL)**
- Severity: HIGH
- Description: Job title must appear in first 50 words
- Enforcement: REGENERATE

**LIC-QA-006: Company Name Spelling**
- Severity: HIGH
- Description: Company name must match profile exactly
- Enforcement: REGENERATE
- Threshold: 0.95 (fuzzy match)

**LIC-QA-041: Metric Source Validation**
- Severity: HIGH
- Description: Every metric in K.3 must map to metric_source_map entry
- Enforcement: BLOCK

**LIC-QA-043: Metric Context Validation**
- Severity: HIGH
- Description: Metrics must have keyword context from RAG
- Enforcement: REGENERATE

**LIC-QA-105: Team Whitelist Enforcement**
- Severity: HIGH
- Description: All team mentions must have ≥0.92 similarity to whitelist
- Enforcement: SOFT_REJECT
- Threshold: 0.92

### Medium Severity Rules (REGENERATE, no halt)

**LIC-QA-008: Forbidden Corporate Verbs**
- Forbidden: spearheaded, leveraged, drove, drive, synergized, utilized, facilitated, orchestrated

**LIC-QA-009: Weak Filler Phrases**
- Forbidden: "I hope this message finds you well", "I wanted to reach out", "just reaching out"

---

## 5. Entity Grounding Framework (from v10.10)

### Metric Source Binding

```python
entity_grounding = {
    "metric_source_binding": {
        "enabled": True,
        "constraint": "EVERY metric in K.3 must map to metric_source_map entry",
        "enforcement": "BLOCK",
        "example": {
            "metric": "40% reduction in deployment time",
            "source_map_entry": {
                "metric": "40%",
                "context": "deployment time reduction",
                "source": "resume_bullet_3",
                "rag_evidence": ["CI/CD pipeline", "automation"],
            },
        },
    },
    "team_whitelist": {
        "enabled": True,
        "validation_method": "semantic_similarity_check",
        "threshold": 0.92,
        "enforcement": "SOFT_REJECT",
        "example": {
            "claim": "my team of 5 engineers",
            "whitelist_entry": "engineering team (5 members)",
            "similarity": 0.94,  # PASS
        },
    },
}
```

---

## 6. RAG Signal Quality Scoring (from v11.9)

### Weighted Scoring Formula

```python
rag_signal_quality = {
    "base_score_per_result": 0.15,  # Caps at 0.75 for 5+ results
    "diversity_bonus_per_source_type": 0.10,  # Caps at 0.30
    "gap_penalty": 0.10,  # Per missing gap
    "minimum_threshold": 0.70,
}

# Example calculation:
results = 5  # RAG results
unique_sources = 3  # podcast, blog, LinkedIn
gaps = 1  # Missing company objective

base_score = min(5 * 0.15, 0.75) = 0.75
diversity_bonus = min(3 * 0.10, 0.30) = 0.30
gap_penalty = 1 * 0.10 = 0.10

total_score = 0.75 + 0.30 - 0.10 = 0.95  # PASS (≥0.70)
```

**Trigger**: If signal quality < 0.70, trigger RAG Reflexion Loop for more research.

---

## 7. Adaptive Temperature Escalation (from v11.9)

### Temperature Adjustment per Retry

```python
adaptive_temperature = {
    "initial_temperature": 0.5,
    "max_temperature": 0.9,
    "escalation_per_retry": 0.1,
    "constraint_failure_types": {
        "MECHANICAL": 0.05,  # Word/char count issues
        "CREATIVE": 0.15,  # Placeholder/generic content
        "SEMANTIC": 0.10,  # Forbidden words
        "CONFLICT": 0.0,  # Impossible constraints (manual fix needed)
    },
}

# Example retry sequence:
attempt_1: temp=0.5, fails with placeholder → +0.15 = 0.65
attempt_2: temp=0.65, fails with word count → +0.05 = 0.70
attempt_3: temp=0.70, PASS
```

---

## 8. Message Type Transitions (from v5.6.2)

### Dynamic Regeneration Triggers

**NEW → FOLLOW_UP**:
- Trigger: User indicates prior touchpoint exists
- Action: Regenerate K.3 with continuity references
- Adjustments:
  - Add opening: "Following up on..."
  - Reference prior topic/date
  - Maintain narrative advancement

**SHORT → LONG**:
- Trigger: User requests expanded version
- Action: Expand K.3 with additional context layers
- Expansions:
  - Add 1-2 more specific anchors
  - Expand evidence paragraphs
  - Add K.2 subject line
  - Add K.4 resume attachment

**ANY → JOB_SPECIFIC**:
- Trigger: User confirms job application context
- Action: Enable job-specific RAG and adjust K.3
- Requirements:
  - Execute prescan for application tracker
  - Enable job-focused RAG queries
  - Ensure job_title appears in first 50 words of K.3

---

## 9. Similarity Thresholds

```python
similarity_thresholds = {
    "message_to_previous": 0.85,  # Messages must be <85% similar
    "continuity_jaccard": 0.40,  # Jaccard for FOLLOW_UP
    "continuity_semantic": 0.80,  # Semantic for FOLLOW_UP
    "company_name_fuzzy": 0.95,  # Company name match
    "team_whitelist_semantic": 0.92,  # Team mention match
}
```

---

## 10. Confidence Thresholds

```python
confidence_thresholds = {
    "per_claim_minimum": 0.70,  # Each claim individually
    "aggregate_minimum": 0.95,  # Overall message
    "rag_signal_quality_minimum": 0.70,  # RAG quality
    "archetype_classification_minimum": 0.85,  # Classification confidence
}
```

---

## 11. Circuit Breaker Pattern (from v11.9)

```python
circuit_breaker = {
    "failure_threshold": 3,  # Open after 3 failures
    "timeout_seconds": 60,  # Wait 60s before retry
    "half_open_test_requests": 1,  # Test with 1 request
    "states": ["CLOSED", "OPEN", "HALF_OPEN"],
}

# Error Code: LIC-E012
# Severity: CRITICAL
# Remediation: Wait for circuit breaker timeout or check API
```

---

## 12. Constraint Pre-Flight Test (from v11.9)

### Feasibility Heuristics

```python
constraint_preflight = {
    "CONNECTION_REQ": {
        "min_words_per_element": 8,
        "elements": ["greeting", "hook", "value_prop", "cta"],
        "total_min_words": 32,
        "char_limit": 300,
        "feasibility_check": "32 words * 5 chars/word = 160 chars < 300 ✓",
    },
    "SHORT_NEW": {
        "min_words_per_element": 10,
        "elements": ["greeting", "hook", "metric", "value_clause", "cta", "signature"],
        "total_min_words": 60,
        "char_limit": {"min": 360, "max": 380},
        "feasibility_check": "60 words * 6 chars/word = 360 chars ✓",
    },
}

# Error Code: LIC-E013
# Severity: CRITICAL
# Remediation: Adjust constraints or change route
```

---

## 13. Boot Validator (from v10.10 and v8.61)

### System Startup Validation

```python
boot_validator = {
    "execution": "SYSTEM_STARTUP",
    "blocking": True,
    "validation_suite": {
        "template_validation": [
            "check_greeting_templates",
            "check_cta_templates",
            "check_signature_formats",
            "verify_no_typos",
        ],
        "schema_integrity": [
            "check_json_files",
            "verify_required_fields",
            "check_no_circular_refs",
        ],
        "reference_integrity": [
            "verify_all_refs_resolve",
            "check_no_broken_links",
            "validate_rule_ids_unique",
        ],
        "route_completeness": [
            "verify_all_routes_defined",
            "check_word_limits_set",
            "confirm_constraints_present",
        ],
    },
    "on_failure": "BLOCK_SYSTEM_START",
}
```

---

## 14. CTA Templates (from v10.10)

```python
cta_templates = {
    "CONNECTION_REQ": {
        "template": "Would you be open to a brief chat about {topic}?",
        "word_limit": 5,
        "examples": [
            "Open to a brief chat?",
            "Available for a quick call?",
        ],
    },
    "INMAIL": {
        "template": "Would you be available for a {duration} call {timeframe} to discuss {topic}?",
        "word_limit": 20,
        "examples": [
            "Available for a 15-minute call this week to discuss AI strategy?",
        ],
    },
}
```

---

## 15. Error Code Registry (from v11.9)

### Centralized Error Codes with Remediation

```python
error_codes = {
    "LIC-E001": {
        "severity": "CRITICAL",
        "description": "Placeholder detected in generated message",
        "remediation": "Regenerate with explicit anti-placeholder constraint",
    },
    "LIC-E002": {
        "severity": "CRITICAL",
        "description": "Per-claim confidence below threshold (0.70)",
        "remediation": "Add more RAG sources or remove low-confidence claim",
    },
    "LIC-E004": {
        "severity": "HIGH",
        "description": "Message too similar to previous message (>0.85)",
        "remediation": "Increase temperature or add diversity constraint",
    },
    "LIC-E008": {
        "severity": "MEDIUM",
        "description": "Forbidden corporate verbs detected",
        "remediation": "Regenerate avoiding: spearheaded, leveraged, etc.",
    },
    "LIC-E011": {
        "severity": "HIGH",
        "description": "Signal quality score below threshold (0.70)",
        "remediation": "Trigger RAG reflexion for more research",
    },
}
```

---

## How to Use in Agentic Architecture

### 1. Outreach Agent Configuration

```python
class K3_MessageBodyAgent(Agent):
    def __init__(self, route: Route, archetype: Archetype):
        self.route = route
        self.archetype = archetype

        # Load route config
        route_config = get_route_config(route)
        self.char_limit = route_config.char_limit
        self.constraints = route_config.constraints

        # Load archetype config
        archetype_config = get_archetype_config(archetype)
        self.temperature = archetype_config.temperature
        self.rag_hops = archetype_config.rag_hops
        self.self_consistency = archetype_config.self_consistency_runs

        # Set goal
        self.goal = Goal(
            objective=f"Generate {route.value} message for {archetype.value}",
            constraints=self.constraints,
            quality_gates=[
                "LIC-QA-001",  # Placeholder detection
                "LIC-QA-002",  # Per-claim confidence
                "LIC-QA-003",  # Hallucination detection
                "LIC-QA-041",  # Metric source validation
            ],
        )
```

### 2. Validation Agent Integration

```python
class OutreachValidationAgent(Agent):
    def __init__(self):
        self.rules = VALIDATION_RULES
        self.confidence_thresholds = CONFIDENCE_THRESHOLDS

    async def validate(self, message, phase):
        rules = get_validation_rules(phase)
        results = []

        for rule in rules:
            result = await self.apply_rule(rule, message)
            if rule.severity == ValidationSeverity.CRITICAL and not result.passed:
                return ValidationResult(
                    passed=False,
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    action="BLOCK",
                )
            results.append(result)

        return ValidationResult(passed=all(r.passed for r in results))
```

### 3. Archetype Classification Agent

```python
class ArchetypeClassificationAgent(Agent):
    async def classify(self, title, about):
        # CXO precedence rule
        for token in CXO_PRECEDENCE_TOKENS:
            if token.upper() in title.upper():
                return Archetype.C_LEVEL, 1.0  # Confidence = 1.0

        # Use RAG for authority signals
        rag_signals = await self.rag_tool.retrieve(f"P&L ownership {title}")

        # Classify with confidence
        archetype, confidence = self.classify_with_rag(title, about, rag_signals)

        # Manual override if confidence < 0.85
        if confidence < 0.85:
            archetype = await self.prompt_user_override(archetype, confidence)

        return archetype, confidence
```

---

## Summary of Value Extracted

✅ **Route configurations** with char limits and K-node enablement
✅ **Archetype configs** with temperature, RAG, and self-consistency settings
✅ **CXO precedence rule** for classification
✅ **107 validation rules** with severity and enforcement
✅ **Entity grounding framework** for metric source binding
✅ **RAG signal quality scoring** with weighted formula
✅ **Adaptive temperature escalation** for retries
✅ **Message type transitions** for dynamic regeneration
✅ **Similarity thresholds** for diversity and continuity
✅ **Confidence thresholds** for quality assurance
✅ **Circuit breaker pattern** for API reliability
✅ **Constraint pre-flight test** for feasibility
✅ **Boot validator** for system startup checks
✅ **CTA templates** per route
✅ **Error code registry** with remediation guidance

These patterns are now available in `apps_lic/L3_orchestration/outreach_orchestration_config.py` and can be used to configure agent behavior, validation gates, and quality controls in the agentic LinkedIn outreach architecture.
