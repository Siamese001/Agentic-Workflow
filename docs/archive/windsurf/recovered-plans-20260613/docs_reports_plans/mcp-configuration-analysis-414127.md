# MCP Configuration Analysis & Implementation Plan

**Generated:** 2026-03-26  
**Scope:** Review existing MCPs, diagnose Sequential Thinking issue, recommend custom MCPs  
**Status:** Analysis complete, implementation plan ready  

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


## Current MCP Configuration Status

### Currently Enabled (6 servers)

| MCP | Status | Notes |
|-----|--------|-------|
| `filesystem` | ✅ Working | Global npm, optimized performance |
| `sequential-thinking` | ❌ Broken | ESM path resolution issue (see RCA) |
| `adg_redis` | ✅ Working | Custom Python, 17 ADG-specific tools |
| `memory` | ✅ Working | Custom Python, SQLite-backed persistence |
| `tavily` | ✅ Working | Global npm, requires API key |
| `brave-search` | ✅ Working | Global npm, requires API key |

### Disabled (3 servers)

| MCP | Status | Reason |
|-----|--------|--------|
| `redis` | ❌ Disabled | Replaced by custom adg_redis |
| `firecrawl` | ❌ Disabled | Needs FIRECRAWL_API_KEY |
| `playwright` | ❌ Disabled | Currently disabled |

---

## RCA: Sequential Thinking MCP Failure

### Root Cause
**Windows ESM path resolution issue in Node.js**

### Evidence Chain
1. **Package exists:** `@modelcontextprotocol/server-sequential-thinking@2025.12.18` ✅
2. **File exists:** `dist/index.js` present and readable ✅  
3. **Dependencies resolved:** SDK imports work from within package directory ✅
4. **Failure point:** `ERR_UNSUPPORTED_ESM_URL_SCHEME` when launching from repo root ❌

### Technical Issue
Windsurf launches the server without setting `cwd`, causing Node.js to fail resolving Windows absolute paths in ESM imports when executed from outside the package directory.

### Fix
Add explicit `cwd` to mcp_config.json:

```json
"sequential-thinking": {
  "command": "node",
  "args": ["C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js"],
  "cwd": "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-sequential-thinking",
  "disabled": false,
  "env": {
    "DISABLE_THOUGHT_LOGGING": "false"
  }
}
```

---

## Recommended Custom MCPs

### 1. OpenTelemetry Runtime ADG MCP

**Priority:** HIGH (Phase 1)  
**Value:** Closes static↔runtime ADG loop, makes 58+ edge types observable at execution time

#### Why Needed
- Your `lifecycle_trace_contract.py` emitters are already structured telemetry waiting for a collector
- Runtime ADG SQLite exists but lacks ingestion bridge from live execution
- Static ADG captures "what system is", runtime ADG needs "what system did"

#### Scope
ADG-semantic projection layer over OpenTelemetry traces (NOT a full OTLP backend)

#### Tool Surface (8-10 tools)
```python
# Core operations
- otel_status()          # Collector health + last-ingested timestamp
- otel_trace(cid)        # Fetch trace by CID as ADG-compatible edge list
- otel_spans_by_agent(agent_class)  # Spans for specific agent class/instance

# Advanced queries  
- otel_healing_chain(trace_id)      # Follow healing dispatch→outcome→escalation
- otel_policy_decisions(time_window) # Path A/B/C/D verdicts with safety plane
- otel_metrics_summary()             # Aggregated counters for runtime edge types
- otel_anomalies()                   # Spans flagged by circuit breaker/safety plane

# Integration
- otel_ingest_to_runtime_adg()      # Push collected spans to runtime_adg_*.sqlite
```

#### Integration Points
- Leverages `apps_shared/utils/open_telemetry_tracing_adapter_util.py`
- Connects to `system_learning/runtime_adg/` infrastructure  
- Uses existing `RuntimeADGSnapshot` and `FileBackedVersionStore`
- Emits to `runtime_adg_*.sqlite` in L4 sovereign territory

---

### 2. Guardian Governance MCP

**Priority:** HIGH (Phase 2)  
**Value:** Centralizes access to 17+ guardian scripts and governance agents

#### Why Needed
- 17+ guardian scripts in `agentic_core/L0_routing/scripts/run_guardian_*.py`
- AutonomyGuardian/HygieneGuardian agents in L5_safety
- No unified query interface for governance status
- Manual script execution for governance validation

#### Scope
Query and trigger governance validations from Windsurf chat

#### Tool Surface (6-8 tools)
```python
# Status and reporting
- guardian_status()       # Which guardians passed/failed recently
- guardian_report()       # Latest guardian execution results
- guardian_manifest()     # Sovereignty/hygiene manifest status

# Execution
- guardian_run(name)      # Execute specific guardian (e.g., hierarchy_compliance)
- guardian_healing(failure_id)  # Trigger healing for failed guardians
- guardian_audit(time_window)   # Governance decision audit trail

# Advanced
- guardian_impact_analysis(change_set)  # Predict governance impact of changes
```

#### Integration Points
- Wraps existing `run_guardian_*.py` scripts
- Interfaces with `AutonomyGuardianAgent` and `HygieneGuardianAgent`
- Uses `guardian_report.json` and telemetry events
- Connects to healing infrastructure for automated remediation

---

### 3. Pytest Test Orchestration MCP

**Priority:** HIGH (Phase 2)  
**Value:** ADG-aware test execution with impact analysis

#### Why Needed
- 6,293 modules require intelligent test selection
- ADG impact analysis exists (`adg_incremental_update.py`) but not integrated
- Test governance (Constitutional Rule #3) needs enforcement
- No centralized test execution with ADG context

#### Scope
Run tests with ADG impact analysis and governance validation

#### Tool Surface (4-6 tools)
```python
# Status and health
- pytest_status()           # Test health, coverage, recent failures
- pytest_coverage_analysis() # Coverage by ADG layer/edge type

# Smart execution
- pytest_run_adg_impact(file_list)    # Run tests for ADG-impacted modules only
- pytest_run_guardians()              # Run governance test suite
- pytest_run_smoke()                  # Quick smoke test with critical path

# Analysis
- pytest_failure_analysis(test_run_id) # Root cause with ADG context
```

#### Integration Points
- Uses existing `pytest.ini` configuration
- Integrates with `adg_incremental_update.py` for impact analysis
- Connects to test coverage and ADG edge mapping
- Enforces Constitutional Rule #3 (no test skipping)

---

### 4. System Learning Meta-Learning MCP

**Priority:** MEDIUM (Phase 3)  
**Value:** Access runtime execution evidence and learning patterns

#### Why Needed
- 37+ runtime ADG snapshots in `system_learning/meta_learning/runtime_adg_snapshots/`
- Meta-learning pipelines need query interface
- Cross-repo learning exists but not accessible from chat
- Pattern detection results are siloed

#### Scope
Query runtime execution evidence and learning patterns

#### Tool Surface (5-7 tools)
```python
# Runtime ADG access
- runtime_adg_status()           # Snapshot count, freshness, health
- runtime_adg_query(filters)      # Query snapshots by trace/agent/time
- runtime_adg_compare(run1, run2) # Diff execution patterns

# Meta-learning
- meta_learning_insights(pattern_type)  # Pattern detection results
- learning_pipeline_status()     # Pipeline health and progress

# Integration
- cross_repo_import(repo_url)    # Incorporate external repo learning
```

#### Integration Points
- Uses `system_learning/runtime_adg/` infrastructure
- Connects to `system_learning/meta_learning/` pipelines
- Leverages existing cross-repo importer
- Accesses `FileBackedVersionStore` for snapshot storage

---

## Implementation Plan

### Phase 1: Immediate Fixes & High-Value MCP

**Week 1: Sequential Thinking Fix**
- [ ] Fix ESM path resolution with explicit `cwd`
- [ ] Test Windsurf integration
- [ ] Verify tool availability

**Week 1-2: OpenTelemetry Runtime ADG MCP**
- [ ] Create `tools/otel/otel_mcp_server.py`
- [ ] Implement 8 core tools (status, trace, spans_by_agent, etc.)
- [ ] Wire to `open_telemetry_tracing_adapter_util.py`
- [ ] Configure ingestion to `runtime_adg_*.sqlite`
- [ ] Add to mcp_config.json
- [ ] Test with sample execution traces

### Phase 2: Governance & Testing Integration

**Week 3: Guardian Governance MCP**
- [ ] Create `tools/governance/guardian_mcp_server.py`
- [ ] Implement 6 tools (status, run, report, healing, etc.)
- [ ] Wrap existing guardian scripts
- [ ] Interface with L5_safety guardian agents
- [ ] Add to mcp_config.json

**Week 4: Pytest Test Orchestration MCP**
- [ ] Create `tools/testing/pytest_mcp_server.py`
- [ ] Implement ADG-aware test selection
- [ ] Integrate with `adg_incremental_update.py`
- [ ] Add governance test enforcement
- [ ] Add to mcp_config.json

### Phase 3: Specialized Learning Access

**Week 5: System Learning Meta-Learning MCP**
- [ ] Create `tools/learning/meta_learning_mcp_server.py`
- [ ] Implement runtime ADG query tools
- [ ] Connect to meta-learning pipelines
- [ ] Add cross-repo learning interface
- [ ] Add to mcp_config.json

---

## Technical Architecture

### Custom MCP Pattern
All custom MCPs follow the established pattern:

```python
# tools/[domain]/[domain]_mcp_server.py
from mcp.server.fastmcp import FastMCP
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import [...emitters...]

mcp = FastMCP("[domain]-mcp")

@mcp.tool()
def operation_name(param: str) -> dict:
    """Tool description."""
    # Implementation
    return result

if __name__ == "__main__":
    mcp.run()
```

### Configuration Pattern
```json
"[domain]": {
  "command": "python",
  "args": ["tools/[domain]/[domain]_mcp_server.py"],
  "cwd": "C:\\Git\\Agentic-Workflow",
  "disabled": false,
  "env": {
    "DOMAIN_VAR": "value"
  }
}
```

### Integration Principles
- **SSOT Compliance:** Store in sovereign territories only
- **ADG Native:** Use existing ADG infrastructure
- **FastMCP:** Leverage FastMCP for rapid development
- **Lifecycle Tracing:** All MCPs emit lifecycle trace events
- **Error Handling:** Graceful degradation when dependencies missing

---

## Expected Outcomes

### Immediate (Phase 1)
- ✅ Sequential Thinking MCP working
- ✅ Runtime ADG automatically populated from execution traces
- ✅ Static↔runtime ADG loop closed

### Short-term (Phase 2)  
- ✅ Unified governance interface from chat
- ✅ ADG-aware test execution
- ✅ Automated governance validation

### Medium-term (Phase 3)
- ✅ Runtime evidence accessible from chat
- ✅ Meta-learning insights on demand
- ✅ Cross-repo learning integration

### Success Metrics
- **MCP Uptime:** All custom MCPs >95% available
- **Runtime ADG Coverage:** >80% of execution traces captured
- **Governance Efficiency:** 50% reduction in manual guardian runs
- **Test Intelligence:** 70% reduction in full test suite runs via ADG impact analysis

---

## Risk Mitigation

### Technical Risks
- **Dependency Conflicts:** Isolate MCP dependencies in separate environments
- **Performance:** Implement caching and pagination for large datasets
- **Error Propagation:** Graceful degradation when upstream services fail

### Operational Risks  
- **MCP Sprawl:** Limit to 4 custom MCPs, consolidate related functionality
- **Maintenance:** Use established patterns and shared infrastructure
- **Security:** Validate all inputs, enforce sovereign territory boundaries

---

**Next Steps:**  
1. Fix Sequential Thinking MCP (immediate)
2. Begin OpenTelemetry Runtime ADG MCP implementation  
3. Schedule Phase 2 planning session

---

*This plan lives in docs/reports/plans/ per Constitutional Rule #0*

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

