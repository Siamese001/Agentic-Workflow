---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\mcp-phase1-baseline-governance-14e1d1.md'
original_relative_path: 'mcp-phase1-baseline-governance-14e1d1.md'
source_sha256: 32b085f2144f5032c1801abb921d6a98b7b05b829e7d70377458f4a3ee5791dd
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 1 — MCP Baseline Governance Lock
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Deterministic Inventory & Structural Validation

**Phase Objective:** Establish authoritative MCP baseline with evidence-driven classification, not optimization.
**Scope:** Inventory only - no removals, no additions, no architectural changes.
**Evidence File:** `docs/reports/mcp_phase1_baseline.md`

---

## I. Execution Plan (Three Waves)

### WAVE 1 — Deterministic Inventory Snapshot

**Objective:** Machine-generated authoritative inventory of all MCP servers.

**Tasks:**
1. **Enumerate Configured MCP Servers**
   - Scan `mcp_registry.py` for official registry entries
   - Cross-reference with `MCP_COMPLETE_CONFIGURATION.md` for installed servers
   - Identify gaps between registry and actual installation

2. **Tool Count Per Server**
   - Extract tool lists from MCP server configurations
   - Document total tool capacity (not MCP slot usage)
   - Clarify constraint model: servers vs tools

3. **Installation Status Verification**
   - Cross-check registry vs actual Windsurf configuration
   - Identify dormant/orphan MCPs (0 tools or 0 calls)
   - Document conditional MCPs (e.g., Redis with config flag)

**Output:** Server count, tool count, installation status matrix

---

### WAVE 2 — Usage & Dependency Graph

**Objective:** Static analysis of actual MCP usage patterns across codebase.

**Tasks:**
1. **Static Tool Invocation Scan**
   - Search all `call_tool("mcpX_*")` patterns
   - Map tool → file → governance layer (L0-L6)
   - Identify direct SDK bypasses (non-MCP calls)

2. **Call Frequency Analysis**
   - Count invocations per tool across codebase
   - Identify high-frequency vs low-frequency tools
   - Flag zero-usage tools (30-day static analysis)

3. **Dependency Mapping**
   - Map MCP tools to sovereign architecture layers
   - Identify critical path dependencies
   - Document capability overlaps between MCPs

**Output:** Usage matrix, dependency graph, frequency analysis

---

### WAVE 3 — Classification & Safe Candidates

**Objective:** Evidence-backed classification of each MCP server.

**Classification Criteria:**
- **Critical:** Core sovereign functionality, no alternatives
- **High Value:** Frequently used, strategic capabilities
- **Redundant:** Capabilities covered by other MCPs
- **Dormant:** Zero usage in 
- **Experimental:** Limited use, optional capabilities

**Safety Validation:**
- Zero invocation verification before "Dormant" classification
- Capability overlap proof before "Redundant" classification
- Governance layer impact assessment

**Output:** Classification table with evidence links

---

## II. Hardened Constraints & Governance

### Corrected Constraint Model

**MCP Limit:** 100 servers (not tools)
**Tool Count:** Per-server capacity, does not affect MCP slot count
**Optimization Target:** Server elimination, not tool trimming

### Evidence Requirements

**For Each Classification:**
- invocation count (static analysis)
- file dependency list
- governance layer impact
- capability overlap proof (if redundant)
- alternative coverage proof (if removable)

### Forbidden Operations in Phase 1

- NO MCP server removals
- NO new MCP additions
- NO architectural changes
- NO configuration modifications
- NO speculative recommendations

---

## III. Data Collection Methods

### Authoritative Sources

1. **Primary:** `agentic_core/L2_execution/config/mcp_registry.py`
2. **Secondary:** `docs/project/MCP_COMPLETE_CONFIGURATION.md`
3. **Tertiary:** Static code analysis for usage patterns

### Search Patterns

```bash
# MCP tool invocations
rg "call_tool.*mcp[0-9]+" --type py -A 1 -B 1

# Direct SDK bypasses
rg "openai\.|anthropic\.|pinecone\.|redis\." --type py -A 1 -B 1

# MCP server references
rg "mcp.*server|MCP.*server" --type md -A 2 -B 2
```

### Validation Methods

- Cross-reference registry vs installation
- Verify tool counts per server
- Map usage to governance layers
- Identify capability overlaps

---

## IV. Expected Deliverables

### Single Evidence File

**Location:** `docs/reports/mcp_phase1_baseline.md`

**Contents:**
1. **Authoritative Server Inventory**
   - Total server count (baseline)
   - Tool count per server
   - Installation status

2. **Usage Analysis**
   - Invocation frequency matrix
   - File dependency mapping
   - Governance layer distribution

3. **Classification Table**
   - Evidence-backed categories
   - Safety validation proofs
   - No speculative recommendations

4. **Constraint Clarification**
   - Correct MCP limit model
   - Tool vs server distinction
   - Actual optimization targets

---

## V. Success Criteria

### Quantitative
- Authoritative server count established
- 100% tool inventory per server
- Zero speculative classifications

### Qualitative
- Evidence-backed every classification
- Clear constraint model documentation
- No architectural changes performed

### Governance Alignment
- All findings referenced to sovereign layers
- Dependency mapping complete
- Safety validation for all classifications

---

## VI. Post-Phase 1 Readiness

After Phase 1 completion, the repository will have:
- Authoritative baseline for optimization decisions
- Evidence-backed understanding of actual MCP usage
- Clear classification of safe removal/consolidation candidates
- Correct understanding of MCP constraint model

**Phase 2** (if approved): Evidence-based optimization with validated safety boundaries.

---

**Phase Status:** Ready for execution
**Risk Level:** LOW (read-only analysis)
**Governance Compliance:** Full evidence collection only

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

