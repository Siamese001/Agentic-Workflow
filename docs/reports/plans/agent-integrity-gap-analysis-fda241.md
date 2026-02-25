# Agent Integrity Gap Analysis Plan

Perform a comprehensive gap analysis of the current agent scope against the Three-Tier Validation Architecture by cross-referencing the full discovery scan with The Contract, The Blueprint, and The Soul validation tiers.

## Analysis Scope

**Current State Discovery:**
- Agent discovery scan reveals only 2 agents: BootstrapAgent and L0MaintenanceBaseAgent
- Both located in agentic_core/L0_maintenance/scripts/ (not scripts/ as listed in discovery)
- Need to verify if discovery scan is comprehensive or incomplete

**Three-Tier Architecture Audit:**
1. **The Contract (Pre-Commit Hooks):** Minimal fast checks (Ruff linting/formatting, cache purge, clean commit verification)
2. **The Blueprint (Guardian Tests):** Comprehensive architectural integrity validation via tests/guardian/
3. **The Soul (Unit Tests):** Isolated logic tests for specific agents via tests/unit/

## Gap Analysis Methodology

**Phase 1: Registry Verification**
- Validate agent discovery completeness by scanning entire codebase for *Agent.py files
- Cross-reference discovery paths with actual file locations
- Flag "Orphan Agents" - agents in discovery but missing from filesystem

**Phase 2: Three-Tier Compliance Assessment**
- **Contract Tier:** Check pre-commit hook coverage for structural guards
- **Blueprint Tier:** Verify Guardian test existence for each agent
- **Soul Tier:** Identify unit test coverage for agent-specific logic

**Phase 3: SSOT Structure Validation**
- Verify all agent paths comply with structure_blueprint.py
- Check layer assignment correctness (L0-L6)
- Validate base agent location compliance (must be in agentic_core/base_agents/)

**Phase 4: Comprehensive Report Generation**
- Generate markdown report with ultra file diffs
- Include inline comments justifying gap flags
- Create Python validation script for 100% coverage verification

## Expected Deliverables

1. **Comprehensive Agent Integrity Report** (docs/reports/agent_integrity_audit.md)
2. **Registry Coverage Validation Script** (Phase 4 verification)
3. **Gap Analysis Matrix** (Current vs Optimal state comparison)

## Critical Success Factors

- 100% agent registry coverage verification
- SSOT path compliance validation
- Three-tier architecture completeness assessment
- Orphan agent identification and flagging
