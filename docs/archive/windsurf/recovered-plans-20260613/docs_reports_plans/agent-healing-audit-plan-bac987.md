# Phase 1: Agent Healing Audit Implementation Plan

Create a deterministic, repo-wide "healing capability audit" that enumerates Agent classes and their healing methods, defines LLM escalation policy contracts, and produces locked reports with CI-grade tests.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Implementation Approach

### 1. Audit Tool Implementation
- **Location**: `tools/governance/agent_heal_audit.py`
- **Method**: AST-based scanning using the existing classification kernel pattern
- **Scope**: Scan agentic_core + apps_* directories for Agent classes
- **Detection**: Identify classes ending with "Agent" and check for `heal()` and `heal_repository()` methods
- **Output**: JSON-serializable deterministic data structure

### 2. Policy Types Module
- **Location**: `agentic_core/L5_safety/types/heal_policy_types.py`
- **Content**: Typed contracts for LLM escalation policy (Phase 1 spec only)
- **Structure**: ReasoningTier enum, HealEscalationInputs/Decision dataclasses, pure function signature

### 3. CLI Interface
- **JSON output**: `python -m tools.governance.agent_heal_audit --format json`
- **Markdown output**: `python -m tools.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_audit.md`
- **Determinism**: Byte-identical output across runs unless code changes

### 4. Test Implementation
- **Location**: `tests/governance/test_agent_heal_audit.py`
- **Coverage**: Deterministic output verification, report structure validation, complete agent enumeration
- **CI-grade**: Strict assertions, no hardcoded counts (structure-based validation)

## Key Technical Decisions

### AST-Based Detection
- Leverage existing `classification_kernel.py` patterns for Agent detection
- Parse AST to find class definitions ending with "Agent"
- Scan method definitions within each class for `heal` and `heal_repository`
- Avoid importing runtime modules to prevent side effects

### Deterministic Output Structure
```json
{
  "audit_results": [
    {
      "repo_relative_path": "agentic_core/L5_safety/reasoning/CodeHealerAgent.py",
      "class_name": "CodeHealerAgent",
      "has_heal": true,
      "has_heal_repository": true,
      "inheritance": ["SovereignBaseAgent", "HealerMixin"]
    }
  ],
  "summary": {
    "total_agents": 190,
    "missing_heal": 45,
    "missing_heal_repository": 120,
    "missing_both": 30
  }
}
```

### Policy Contract (Phase 1 Spec)
- Define escalation policy types without API implementation
- ReasoningTier enum: LOW/HIGH model tiers
- Decision logic based on complexity, confidence, cost, latency, safety
- Pure function signature for `decide_reasoning_tier()`

## File Structure
```
tools/governance/agent_heal_audit.py           # Main audit CLI tool
agentic_core/L5_safety/types/heal_policy_types.py  # Policy contract types
tests/governance/test_agent_heal_audit.py     # Deterministic tests
docs/reports/governance/agent_heal_audit.md   # Generated markdown report
docs/reports/governance/phase1_agent_heal_audit_evidence.md  # Evidence file
```

## Acceptance Criteria Verification
- ✅ CLI runs without side-effectful imports
- ✅ Byte-identical JSON output across runs
- ✅ Markdown report generated at required path
- ✅ Tests pass with strict deterministic validation
- ✅ Evidence file captures all required outputs
- ✅ No behavioral changes (Phase 1 scope only)

## Next Steps
1. Implement audit tool with AST scanning
2. Create policy types module with typed contracts
3. Add comprehensive deterministic tests
4. Generate evidence file with CLI outputs
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

