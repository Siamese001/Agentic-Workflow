# System Learning Adoption Audit Plan

Comprehensive deterministic audit of system learning adoption across Agentic-Workflow repository to identify why agents are not visibly more intelligent and what wiring is missing.

## Phase 1: System Learning Readiness Audit (Wave 1)
**Objective**: Enumerate agents, map system_learning modules, determine current learning loop behavior

**Tasks**:
1. **Agent Discovery**: Use ripgrep to enumerate all agent classes (found ~101 agents across agentic_core, apps_lic, apps_rg)
2. **System Learning Mapping**: Document current system_learning structure (types/, enforcement/, meta-control/)
3. **Learning Loop Analysis**: Determine if any functional learning loops exist today
4. **Infrastructure Inventory**: Confirm Redis, Pinecone, embedding services configuration

**Key Findings So Far**:
- ~101 agent files identified across core and app layers
- system_learning/ exists but minimal: only determinism.py enforcement and type definitions
- MetaLearningAgent exists but appears isolated
- Infrastructure configured (Redis, Pinecone) but unclear if actively used for learning

## Phase 2: Per-Agent Wiring Assessment (Wave 2)
**Objective**: Analyze each agent for telemetry emission, state hooks, and classify readiness

**Tasks**:
1. **Telemetry Analysis**: Check which agents emit structured events/outcomes
2. **State Hook Identification**: Find agents with configurable state points
3. **Readiness Classification**: Categorize agents as READY/MINOR_WIRING/MAJOR_WIRING
4. **Prioritization**: Identify Top 5 agents for immediate system learning integration

## Phase 3: Infrastructure + Implementation Plan (Wave 3)
**Objective**: Identify required components and create immediate/maturation plans

**Tasks**:
1. **Component Analysis**: Document Redis, Pinecone, embedding service usage patterns
2. **Gap Identification**: Missing learning infrastructure components
3. **Implementation Plan**: 1-day immediate enablement + 2-4 week maturation plan
4. **Safety/Guardrails**: Rollback strategies and human approval boundaries

## Deliverable
Single comprehensive report: `docs/reports/system_learning_findings_and_recommendations.md`

**Converge Confidence Target**: ≥85% (evidence-based, no speculation)
