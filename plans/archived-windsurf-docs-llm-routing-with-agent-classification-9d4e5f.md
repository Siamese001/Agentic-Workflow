---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-with-agent-classification-9d4e5f.md'
original_relative_path: 'llm-routing-with-agent-classification-9d4e5f.md'
source_sha256: a2c9017a3aebee57026c7e42bb0853dc44225e3f4f6c58f60f7a1c91ae95d9e5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing with Agent Classification: Scan, Classify, Then Implement

Perform a comprehensive scan of all agents to classify LLM healing needs, then implement the hardened routing architecture with proper agent classifications.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 0 — Agent Classification Scan (NEW)

Before any implementation, scan all agents to determine LLM healing requirements:

### 0.1 Scan All Agents
```python
# Scan scope:
- agentic_core/*Agent.py (97 agents)
- apps_rg/engines/*.py (48 engines)
- apps_lic/*Agent.py (44 agents)
- apps_shared/*Agent.py (11 agents)

# Classification criteria:
1. Has @standard_heal decorator?
2. Has heal_repository() method?
3. Has direct llm_generate() calls?
4. Complexity of healing logic (simple rule fixes vs complex reasoning)
5. Domain (syntax, structure, logic, strategy, generation)
```

### 0.2 Classification Matrix

| Agent Type | LLM Healing Needed | ReasoningClass | Rationale |
|------------|-------------------|---------------|-----------|
| Syntax fixers | NO | DETERMINISTIC | Simple regex/AST fixes |
| Structure validators | NO | DETERMINISTIC | Rule-based checks |
| Complex orchestrators | YES | STRATEGIC/ORCHESTRATOR | Need reasoning for coordination |
| Content generators | YES | LIGHT/STRATEGIC | Production generation, not healing |
| Threat analyzers | YES | STRATEGIC | Complex pattern recognition |
| File movers | NO | DETERMINISTIC | Simple deterministic operations |

### 0.3 Expected Classification Results

**agentic_core (97 agents):**
- LLM healing: ~30 agents (complex orchestrators, threat agents, strategic planners)
- Deterministic: ~67 agents (validators, linters, simple fixers)

**apps_rg (48 engines):**
- LLM generation: ~5 engines (bullet/message generation)
- No healing needed: ~43 engines (data processing, validation)

**apps_lic (44 agents):**
- Mostly deprecated legacy stubs
- Active agents: ~10 need evaluation

**apps_shared (11 agents):**
- Infrastructure/utilities, no LLM needed

---

## Phase 1 — Core Infrastructure (from converged spec)

Implement the hardened gateway architecture with L4 anchoring and deterministic defaults.

---

## Phase 2 — Apply Classifications

### 2.1 Update Agent Classes
Based on scan results, add appropriate `AGENT_REASONING_CLASS`:

```python
# Example classifications
class FissionManagerAgent(SovereignBaseAgent):
    AGENT_REASONING_CLASS = ReasoningClass.ORCHESTRATOR  # Complex orchestration

class NamingAgent(SovereignBaseAgent):
    AGENT_REASONING_CLASS = ReasoningClass.DETERMINISTIC  # Simple rules

class BulletGenerationTask(BaseRGEngine):
    AGENT_REASONING_CLASS = ReasoningClass.LIGHT  # Fast generation
```

### 2.2 Healing vs Generation Decision

| Use Case | Path | ReasoningClass | Notes |
|----------|------|---------------|-------|
| Fix syntax error | route_healing() | HEALER | Only for actual healing |
| Generate content | route_generation() | LIGHT/STRATEGIC | Production calls |
| Complex orchestration | route_generation() | ORCHESTRATOR | Planning/coordination |
| Simple validation | None | DETERMINISTIC | No LLM needed |

---

## Phase 3 — Implementation with Classification Results

### 3.1 Agents needing LLM healing (~30)
- Add `@standard_heal` if missing
- Set appropriate `AGENT_REASONING_CLASS`
- Ensure healing logic can handle LLM responses

### 3.2 Agents with deterministic healing (~67)
- Set `AGENT_REASONING_CLASS = DETERMINISTIC`
- Keep or add `@standard_heal` (will route to LOCAL_AGENT)
- No LLM calls will be made

### 3.3 apps_rg generation engines (~5)
- Use `route_generation()` not `route_healing()`
- Set `ALLOW_STOCHASTIC = False` (deterministic generation)
- Add trace ID propagation

---

## Detailed Classification Criteria

### LLM Healing Indicators:
✅ Has complex conditional logic in heal methods
✅ Handles ambiguous or context-dependent fixes
✅ Requires understanding of code semantics
✅ Deals with architectural decisions
✅ Has @standard_heal + complex implementation

### Deterministic Healing Indicators:
✅ Simple pattern matching/replacement
✅ Fixed rule applications
✅ File moves/renames
✅ Syntax corrections
✅ Validation only

### Production Generation (apps_rg):
✅ Content creation (bullets, messages)
✅ Template filling
✅ Data transformation with reasoning
✅ Strategic planning

---

## Scan Execution Plan

```python
# _temp_agent_classification_scan.py
scan_results = {
    "agentic_core": {
        "total": 97,
        "llm_healing": [],
        "deterministic": [],
        "needs_review": []
    },
    "apps_rg": {
        "total": 48,
        "llm_generation": [],
        "no_llm": []
    },
    "apps_lic": {
        "total": 44,
        "active": [],
        "deprecated": []
    },
    "apps_shared": {
        "total": 11,
        "infrastructure": []
    }
}
```

Output: Markdown table with classifications and rationale for each agent.

---

## Updated Implementation Steps

1. **Run classification scan** → Generate agent classification table
2. **Review classifications** → Manual validation of edge cases
3. **Implement infrastructure** → Gateway, policy, CI
4. **Apply classifications** → Update agent classes with correct ReasoningClass
5. **Migrate direct callers** → 3 specific agents
6. **Verify with tests** → Ensure deterministic agents never call LLM

---

## Success Criteria

1. ✓ All agents classified with documented rationale
2. ✓ LLM healing only where genuinely needed
3. ✓ Deterministic healing for simple cases
4. ✓ Production generation properly separated
5. ✓ CI enforces correct classifications
6. ✓ Zero cost from unnecessary LLM calls

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Over-classifying agents | Conservative defaults (DETERMINISTIC) |
| Missing complex cases | Manual review of scan results |
| apps_rg broken | Fix call_llm() before classification |
| Future drift | CI enforcement of ReasoningClass |

This approach ensures we implement LLM routing only where it adds value, keeping simple operations deterministic and fast.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

