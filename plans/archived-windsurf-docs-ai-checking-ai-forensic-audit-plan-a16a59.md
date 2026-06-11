---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ai-checking-ai-forensic-audit-plan-a16a59.md'
original_relative_path: 'ai-checking-ai-forensic-audit-plan-a16a59.md'
source_sha256: 399cb88fa17227bf061b88ef72a10bec3248f0c886b7035e2c8e31c858ce5a9f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AI-Checking-AI Forensic Audit Plan

Plan to conduct a comprehensive forensic audit of the Agentic-Workflow repository to identify "AI-Checking-AI" violations where AI agents perform structural, MRO, or layer-zoning validation that should be handled by deterministic Guardian tests.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Forensic Audit Scope

Based on analysis, I will examine approximately 218 agents total, focusing on:

1. **agentic_core**: ~49 agents (L0-L6 core agents)
2. **apps_lic**: ~40 agents (LIC outreach campaign agents)
3. **apps_rg**: ~18 agents (RG resume generation agents)
4. **apps_shared**: ~7 agents (Shared utility agents)
5. **Total Scope**: ~160-180 active agents with heal_repository methods

**Priority Focus Areas:**
- High-Layer Agents (L4-L6) performing validation on lower layers
- Agents with LLM calls making structural decisions
- heal_repository methods using heuristic validation logic
- Missing deterministic links to Guardian test scripts

## Phase 2: Key Violation Patterns Identified

### Pattern 1: LLM-Based Structural Validation
- **CognitiveDispositionAgent**: Uses `llm_generate` to analyze violations and make disposition decisions
- **ConstitutionalReviewerAgent**: Uses LLM to perform "constitutional review" of outputs
- **ConversationalRepairAgent**: Uses LLM to validate and repair code structure

### Pattern 2: Higher-Layer Agents Checking Lower Layers
- **ArchitectureGovernorAgent (L5)**: Validates layer gravity, naming, and hierarchy across ALL territories
- **StructuralValidatorAgent (L5)**: Performs structural validation that should be deterministic
- **ComplexityAnalyzerAgent (L5)**: Analyzes code complexity without deterministic tests

### Pattern 3: Apps Layer Validation Logic

- **apps_lic engines**: 40+ agents with heal_repository methods performing validation
- **apps_rg engines**: 18+ agents with validation logic in resume generation
- **GovernanceShieldAgent**: Uses deterministic validator but still performs AI-checking
- **ContentQualityAgent**: Performs quality validation without Guardian tests

### Pattern 4: Missing Guardian Test Links

- Most agents report "success" without executing Guardian test scripts
- No subprocess calls to deterministic `tests/guardian/` suite
- Healing logic embedded in agents instead of externalized
- Apps layer agents delegate to super().heal_repository() without deterministic tests

## Phase 3: Remediation Strategy

For each violation found:
1. Extract AI-checking logic from agent
2. Replace with subprocess/pytest call to Guardian layer
3. Create new deterministic test script in `tests/guardian/`
4. Provide 4 aggressive test cases

## Phase 4: Expected Deliverables

1. **Violation Report**: Each agent with specific method and violation type
2. **Ultra File Diffs**: Show removal of AI logic and replacement with deterministic calls
3. **Guardian Test Scripts**: New deterministic Python tests for each violation
4. **Test Cases**: 4 test cases per Guardian script
5. **Subatomic Health Score**: Repository health assessment

## Phase 5: Implementation Constraints

- **DO NOT IMPLEMENT** - Generate Markdown report only
- Categorize by agent with individual sections
- Be skeptical - flag any structural decision-making by AI
- Focus on deterministic extraction of validation logic

## Phase 6: Apps Layer Specific Focus

### apps_lic Violations to Examine:

- **CampaignBalanceAgent**: Balance validation logic
- **GovernanceShieldAgent**: Risk scanning validation
- **MessageDiversityValidatorAgent**: Message validation logic
- **OutreachProactiveAgent**: Proactive analysis validation
- **TwoPhaseDeduplicationAgent**: Deduplication validation

### apps_rg Violations to Examine:

- **ATSCompatibilityAgent**: ATS compatibility validation
- **BrandComplianceAgent**: Brand compliance validation
- **ContentQualityAgent**: Content quality validation
- **FactCheckAgent**: Fact-checking validation logic

### apps_shared Violations to Examine:

- **DuplicateCodeDetectorAgent**: Code duplication validation
- **SecurityLevelAgent**: Security validation logic

## Next Steps

Proceed with systematic examination of all agents, prioritizing:
1. L5 safety validators (highest risk)
2. L4 state agents
3. L6 observability agents
4. apps_lic engines (40+ agents)
5. apps_rg engines (18+ agents)
6. apps_shared utilities (7+ agents)

The audit will produce a comprehensive report identifying all AI-Checking-AI violations across the entire repository and providing deterministic remediation paths.

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

