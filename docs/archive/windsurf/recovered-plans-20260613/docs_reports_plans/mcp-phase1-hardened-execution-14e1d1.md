# Phase 1 — MCP Baseline Governance Lock (Hardened)
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Deterministic Inventory with Evidence-Backed Classification

**Objective:** Produce deterministic, evidence-backed MCP baseline with zero subjective classification.
**Scope:** Read-only analysis - no removals, no additions, no configuration changes.
**Evidence File:** `docs/reports/mcp_phase1_baseline.md` with exact schema compliance.

---

## I. Corrected Structural Foundations

### Constraint Model (Hardened)
- **MCP Limit:** 100 servers (not tools)
- **Tool Count:** Per-server capacity, irrelevant to slot usage
- **Static vs Runtime:** Explicit distinction required
- **Evidence Required:** Table-backed only, no narrative

### Runtime Active Definition (Deterministic)
Runtime Active = server that satisfies at least one:
- Present in active Windsurf runtime configuration file
- Instantiated via MCP loader
- Imported and registered at startup
- Documentation references do not qualify

### Tool Count Derivation Rule
Tool count must be extracted from:
- Registry declaration block
- Tool registration list in MCP definition
- Programmatic enumeration if available
- Manual counting from documentation prohibited

### Governance Layer Mapping (Deterministic Rule)
Layer determined by hierarchy:
1. **Directory prefix `agentic_core/LX_`** → authoritative
2. **If not present:** Trace call chain to invoking layer
3. **If still ambiguous:** Mark as "Unresolved"
- No inference beyond this rule set

### Static Invocation Counting Rules
Count only executable references:
- **Exclude:** `tests/`, `docs/`, `*.md`, commented lines
- **Include:** Production code paths only
- Double-count prevention via path filtering

---

## II. Wave Execution (Three Deterministic Waves)

### WAVE 1 — Registry & Runtime Reconciliation

**Objective:** Authoritative server inventory with validation.

**Required Analysis:**
1. **Registry-declared MCP servers** (`mcp_registry.py`)
2. **Runtime-configured MCP servers** (`MCP_COMPLETE_CONFIGURATION.md`)
3. **Delta analysis:**
   - Declared but inactive
   - Active but undeclared
   - Conditional servers (config-gated)

**Mandatory Output Table:**

| Server ID | Declared | Runtime Active | Tool Count | Conditional | Notes |
|-----------|----------|----------------|------------|-------------|-------|
| pinecone | ✅ | ✅ | 4 | ❌ | L4 vector database |
| redis | ✅ | ✅ | 4 | ✅ | REDIS_MCP_ENABLED flag |
| ... | ... | ... | ... | ... | ... |

---

### WAVE 2 — Deterministic Static Invocation Map

**Objective:** Precise usage mapping without runtime claims.

**Required Scans:**
1. **MCP Tool Invocations** (Production paths only)
   ```bash
   rg "call_tool.*mcp[0-9]+" --type py -A 1 -B 1 | grep -v "tests/" | grep -v "docs/"
   ```

2. **SDK Bypass Detection (Expanded)**
   ```bash
   # Direct SDK imports
   rg "import (openai|anthropic|pinecone|redis|psycopg|asyncpg)" --type py --exclude-dir tests

   # Wrapped clients
   rg "from.*(openai|anthropic|pinecone|redis).*client" --type py --exclude-dir tests

   # HTTP to model endpoints
   rg "https://api.(openai|anthropic|pinecone).io" --type py --exclude-dir tests
   ```

**Mandatory Output Tables:**

**Tool Invocation Matrix**

| Tool | Static Invocation Count | Files | Governance Layer |
|------|-------------------------|-------|------------------|
| mcp8_search-records | 15 | 3 | L4 |
| mcp9_get | 8 | 2 | L4 |
| ... | ... | ... | ... |

**SDK Bypass Matrix**

| SDK | Import Count | Files | Layer |
|-----|--------------|-------|-------|
| openai | 23 | 7 | L1, L5 |
| pinecone | 41 | 12 | L1, L4 |
| redis | 19 | 5 | L4 |
| ... | ... | ... | ... |

---

### WAVE 3 — Evidence-Backed Classification

**Objective:** Deterministic classification with formal criteria.

**Classification Rules (Hardened):**

**Critical**
Must satisfy ALL:
- Static invocation ≥1 in production path
- Not test-only usage
- Required for sovereign architecture continuity
- No parameter-equivalent alternative
- Removal would cause deterministic break

**High Value**
- Used ≥1 time AND strategic (vector, cache, FS, browser)
- Or Critical criteria not fully met

**Dormant**
- Zero static invocation in production paths

**Redundant**
Must satisfy ALL:
- Zero unique capabilities
- Full parameter coverage match
- Equivalent return type
- No layer regression

**Unverified**
- Classification criteria not fully met
- Explicit missing proof reason required

**Mandatory Classification Table:**

| Server | Classification | Static Invocation Count | Layer Coverage | Evidence Reference |
|--------|----------------|-------------------------|----------------|-------------------|
| pinecone | Critical | 41 | L1, L4 | Tool matrix + SDK bypass |
| playwright | High Value | 0 | L2 | Capability analysis |
| puppeteer | Redundant | 0 | L2 | Playwright coverage proof |
| redis | Critical | 19 | L4 | Tool matrix + conditional |
| ... | ... | ... | ... | ... |

---

## III. Required Evidence File Schema

**File:** `docs/reports/mcp_phase1_baseline.md`

**Exact Required Sections:**

### 1. Registry vs Runtime Matrix
- Table format as specified in Wave 1
- Delta analysis with evidence links

### 2. Tool Invocation Matrix
- Table format as specified in Wave 2
- Static invocation counts only

### 3. SDK Bypass Matrix
- Table format as specified in Wave 2
- Expanded bypass detection results

### 4. Governance Layer Distribution Table
| Layer | Server Count | Tool Count | Invocation Count |
|-------|--------------|------------|------------------|
| L0 | 0 | 0 | 0 |
| L1 | 1 | 1 | 23 |
| L2 | 3 | 35+ | 0 |
| L4 | 4 | 12 | 68 |
| L5 | 0 | 0 | 0 |
| L6 | 1 | 2 | 5 |

### 5. Classification Table
- Table format as specified in Wave 3
- Evidence references for each classification

### 6. Constraint Model Clarification
- MCP limit = 100 servers
- Tool count ≠ MCP slot usage
- Static vs runtime distinction
- Optimization targets clarified

---

## IV. Hard Gates & Forbidden Operations

### Absolutely Forbidden
- NO removal recommendations
- NO addition suggestions
- NO configuration changes
- NO architectural speculation
- NO narrative justifications without table evidence
- NO use of word "optimization"

### Required Evidence Standards
- All classifications must reference table evidence
- No subjective language ("appears", "likely", "probably")
- Zero inference on ambiguous data
- "Unverified" classification for incomplete proof

---

## V. Risk Assessment

**Phase Risk Level: LOW** (if compliance maintained)
- Read-only operations only
- Deterministic search patterns
- Table-backed evidence only
- No structural changes

**Failure Modes:**
- Subjective classification → Invalid results
- Missing evidence tables → Incomplete baseline
- Constraint confusion → Wrong optimization targets

---

## VI. Success Criteria

### Quantitative
- 100% registry reconciliation completed
- All static invocations mapped (production paths only)
- All classifications meet criteria OR labeled Unverified with explicit reason

### Qualitative
- Evidence-backed every classification
- Deterministic governance layer mapping
- Clear constraint model documentation

### Compliance
- No forbidden operations performed
- Exact schema compliance
- All hard gates respected

---

**Phase Status:** Structurally sound for execution
**Compliance Requirement:** Full adherence to hardened specification
**Next Step:** Execute Wave 1 registry reconciliation

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

