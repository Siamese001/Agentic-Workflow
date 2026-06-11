---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agent-healing-audit-plan-consolidated-bac987.md'
original_relative_path: 'agent-healing-audit-plan-consolidated-bac987.md'
source_sha256: 6d982a8bba1e1f7ed0c30ae11c15089a940a65ef54c1644511e357d645bb2ef8
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 1: Agent Healing Audit Implementation Plan (Consolidated)

Create a deterministic, repo-wide "healing capability audit" that enumerates Agent classes and their healing methods, defines LLM escalation policy contracts incorporating existing confidence level logic, and produces locked reports with CI-grade tests.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Enhanced Implementation Approach

### 1. Audit Tool Implementation
- **Location**: `tools/governance/agent_heal_audit.py`
- **Method**: AST-based scanning using the existing classification kernel pattern
- **Scope**: Scan agentic_core + apps_* directories for Agent classes
- **Detection**: Identify classes ending with "Agent" and check for `heal()` and `heal_repository()` methods
- **Output**: JSON-serializable deterministic data structure

### 2. Policy Types Module with Existing Confidence Logic
- **Location**: `agentic_core/L5_safety/types/heal_policy_types.py`
- **Enhanced Content**:
  - **ReasoningTier enum**: LOW, HIGH (aligned with existing ModelTier logic)
  - **ConfidenceLevel enum**: LOW, MEDIUM, HIGH, VERY_HIGH (from OutreachLearningAgent)
  - **HealEscalationInputs**: task_complexity, confidence, cost_budget, latency_budget, safety_risk
  - **HealEscalationDecision**: tier + rationale + threshold_used
  - **Pure function**: `decide_reasoning_tier(inputs) -> HealEscalationDecision`

### 3. Incorporated Confidence Level Logic
Based on existing patterns in the codebase:

#### Confidence Thresholds (from OutreachLearningAgent):
- **VERY_HIGH**: confidence >= 0.85
- **HIGH**: confidence >= 0.7
- **MEDIUM**: confidence >= 0.5
- **LOW**: confidence < 0.5

#### Model Tier Mapping (from ModelRouter):
- **LOW Reasoning Tier**: FAST models (gpt-4o-mini, claude-3-haiku, gemini-2.5-flash)
- **HIGH Reasoning Tier**: REASONING models (o1-preview, claude-3-opus, gemini-3-pro-preview)

#### Escalation Policy Logic:
```python
def decide_reasoning_tier(inputs: HealEscalationInputs) -> HealEscalationDecision:
    # Start with LOW tier (fast/cheap models)
    # Escalate to HIGH tier when:
    # - confidence < 0.7 (below HIGH threshold)
    # - task_complexity >= 8 (requires reasoning)
    # - safety_risk >= 7 (high risk)
    # - repeated failures (retry_count > 2)
    # Never escalate for trivial transformations (complexity < 3)
```

### 4. CLI Interface
- **JSON output**: `python -m tools.governance.agent_heal_audit --format json`
- **Markdown output**: `python -m tools.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_audit.md`
- **Determinism**: Byte-identical output across runs unless code changes

### 5. Enhanced Test Implementation
- **Location**: `tests/governance/test_agent_heal_audit.py`
- **Coverage**:
  - Deterministic output verification
  - Report structure validation
  - Complete agent enumeration
  - **Policy contract validation** (confidence thresholds, tier mapping)
  - **Escalation logic testing** (edge cases, boundary conditions)
- **CI-grade**: Strict assertions, structure-based validation

## Key Technical Enhancements

### AST-Based Detection with Existing Patterns
- Leverage existing `classification_kernel.py` patterns for Agent detection
- Parse AST to find class definitions ending with "Agent"
- Scan method definitions within each class for `heal` and `heal_repository`
- Avoid importing runtime modules to prevent side effects

### Enhanced Deterministic Output Structure
```json
{
  "audit_results": [
    {
      "repo_relative_path": "agentic_core/L5_safety/reasoning/CodeHealerAgent.py",
      "class_name": "CodeHealerAgent",
      "has_heal": true,
      "has_heal_repository": true,
      "inheritance": ["SovereignBaseAgent", "HealerMixin"],
      "confidence_capability": true,  # NEW: Has confidence logic
      "model_tier_support": ["LOW", "HIGH"]  # NEW: Supported tiers
    }
  ],
  "summary": {
    "total_agents": 190,
    "missing_heal": 45,
    "missing_heal_repository": 120,
    "missing_both": 30,
    "with_confidence_logic": 12,  # NEW: Agents with confidence levels
    "with_model_routing": 8      # NEW: Agents with tier selection
  },
  "policy_contract": {
    "confidence_thresholds": {
      "VERY_HIGH": 0.85,
      "HIGH": 0.7,
      "MEDIUM": 0.5,
      "LOW": 0.0
    },
    "model_tiers": {
      "LOW": ["gpt-4o-mini", "claude-3-haiku", "gemini-2.5-flash"],
      "HIGH": ["o1-preview", "claude-3-opus", "gemini-3-pro-preview"]
    }
  }
}
```

### Policy Contract (Phase 1 Enhanced Spec)
- **ReasoningTier enum**: LOW/HIGH model tiers (aligned with ModelRouter)
- **ConfidenceLevel enum**: LOW/MEDIUM/HIGH/VERY_HIGH (from OutreachLearningAgent)
- **Escalation logic**: Based on confidence thresholds, task complexity, safety risk
- **Model mapping**: Direct mapping to existing model configurations
- **Pure function signature**: `decide_reasoning_tier() -> HealEscalationDecision`

## File Structure
```
tools/governance/agent_heal_audit.py                    # Main audit CLI tool
agentic_core/L5_safety/types/heal_policy_types.py     # Enhanced policy contracts
tests/governance/test_agent_heal_audit.py              # Comprehensive deterministic tests
docs/reports/governance/agent_heal_audit.md            # Generated markdown report
docs/reports/governance/phase1_agent_heal_audit_evidence.md  # Evidence file
```

## Enhanced Acceptance Criteria Verification
- ✅ CLI runs without side-effectful imports
- ✅ Byte-identical JSON output across runs
- ✅ Markdown report generated at required path with enhanced sections
- ✅ Tests pass with strict deterministic validation including policy contracts
- ✅ Evidence file captures all required outputs
- ✅ **NEW**: Policy contracts incorporate existing confidence level logic
- ✅ **NEW**: Model tier mapping aligns with existing router configurations
- ✅ **NEW**: Escalation policy uses proven thresholds from OutreachLearningAgent
- ✅ No behavioral changes (Phase 1 scope only)

## Integration with Existing Infrastructure

### Leveraging Existing Components:
1. **Classification Kernel**: For AST-based agent detection
2. **ModelRouter Types**: For tier definitions and model configurations
3. **Confidence Logic**: From OutreachLearningAgent for threshold definitions
4. **HardenedGeminiExecutor**: For high-tier model execution patterns
5. **Governance Patterns**: From existing tools/governance structure

### Consistency with Existing Patterns:
- Same enum naming conventions (LOW, HIGH, VERY_HIGH)
- Same confidence thresholds (0.85, 0.7, 0.5 boundaries)
- Same model tier definitions (FAST, BALANCED, REASONING)
- Same escalation logic patterns (complexity + confidence + safety)

## Next Steps
1. Implement audit tool with AST scanning and confidence detection
2. Create enhanced policy types module with existing logic integration
3. Add comprehensive deterministic tests including policy validation
4. Generate evidence file with CLI outputs and policy verification
5. Commit with specified message format

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

