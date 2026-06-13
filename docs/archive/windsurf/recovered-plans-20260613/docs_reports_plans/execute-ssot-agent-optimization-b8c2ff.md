# execute_ssot Agent Optimization Plan

A 4-wave quick-win plan to consolidate duplicate agents, fix conflicting heal flags, and standardize L2 lifecycle alignment for execute_ssot.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1.1-P1.3 | Agent Audit & Classification | 15K 🟢 | ADG available, tests pass | PENDING | Inventory complete, classification matrix delivered |
| Wave 2 | P2.1-P2.4 | Flag Consolidation & Script Conversion | 18K 🟢 | No new agent creation | PENDING | Conflicting flags eliminated, scripts converted |
| Wave 3 | P3.1-P3.3 | L2 Lifecycle Alignment | 12K 🟢 | PTC schema stable | PENDING | L2 subphases mapped, gaps identified |
| Wave 4 | P4.1-P4.2 | Standardization & Hardening | 10K 🟢 | Tests green | PENDING | Entrypoint hardened, docs updated |

**Total: ~55K tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: Agent/Script Confusion**
Many "agents" in execute_ssot are actually deterministic scripts with no reasoning. Examples: SSOTFolderCleanupAgent, RootCustomsAgent. These should be converted to utility scripts to reduce cognitive overhead.
- Impact: ~12 agents misclassified, causing unnecessary complexity

**GAP-2: Conflicting Heal Flags**
UWG has heal jurisdiction, but individual agents also have `--heal`, `--no-heal`, `--scan-only` flags that override. This creates inconsistent behavior.
- Impact: Users confused about which flag takes precedence; heal may not run when expected

**GAP-3: L2 Lifecycle Misalignment**
The L2 Execution Staff lifecycle (from agentic_process_mapping_v28.md) has subphases: Discovery, Validation, Alignment, Healing, Reporting. Current execute_ssot agents don't cleanly map to these phases.
- Impact: PTC (Phase Transition Contracts) may not be enforced correctly

**GAP-4: Duplicate/Overlapping Agents**
- CodeHealerAgent vs CodeJanitorAgent (both clean up code)
- CodeValidatorAgent vs CodeDetectorAgent (both validate)
- BoundaryTestingAgent vs AdversarialProbeAgent (both test boundaries)
- Impact: Redundant code, maintenance burden

---

## Execution Plan

### Wave 1 — Agent Audit & Classification

**Scope**: 
1. Catalog all agents called by execute_ssot
2. Analyze each agent for reasoning complexity (decision trees, LLM calls, uncertainty handling)
3. Classify as AGENT (needs reasoning) or SCRIPT (deterministic)
4. Map agents to L2 lifecycle phases

**Commands**:
```bash
# P1.1 - Run agent discovery
python tools/adg/adg_query.py --module agentic_core.L0_routing.scripts._ssot_phases --output-format json > /tmp/ssot_agents.json

# P1.2 - Analyze agent complexity
python -c "
import json
agents = json.load(open('/tmp/ssot_agents.json'))
for agent in agents:
    # Check for LLM calls, reasoning patterns
    pass
" > /tmp/agent_classification.md

# P1.3 - Generate classification matrix
cat > docs/reports/ssot_agent_classification.md << 'EOF'
| Agent | Layer | Current Classification | Proposed | Reasoning Complexity | L2 Phase |
|-------|-------|------------------------|----------|---------------------|----------|
EOF
```

**Acceptance**: 
- [ ] Complete inventory of all agents called by execute_ssot
- [ ] Classification matrix with AGENT/SCRIPT determination
- [ ] Gap analysis showing which agents should be converted to scripts

---

### Wave 2 — Flag Consolidation & Script Conversion

**Scope**:
1. Consolidate heal flags to single source of truth (UWG)
2. Convert misclassified agents to scripts
3. Update execute_ssot_entrypoint to use unified flag schema
4. Remove per-agent heal overrides

**Commands**:
```bash
# P2.1 - Fix conflicting flags in execute_ssot_entrypoint.py
# Remove --heal/--no-heal from entrypoint, rely on UWG only

# P2.2 - Convert agents to scripts (examples)
# SSOTFolderCleanupAgent → ssot_folder_cleanup_util.py
# RootCustomsAgent → root_customs_util.py

# P2.3 - Update imports and references
python tools/adg/update_imports.py --from SSOTFolderCleanupAgent --to ssot_folder_cleanup_util

# P2.4 - Validation
python -m pytest tests/unit/test_execute_ssot_*.py -v
```

**Acceptance**:
- [ ] No conflicting heal flags (single UWG jurisdiction)
- [ ] Converted agents run as scripts without regression
- [ ] Tests pass for all modified components

---

### Wave 3 — L2 Lifecycle Alignment

**Scope**:
1. Map current execute_ssot phases to L2 lifecycle
2. Identify missing PTC enforcement points
3. Add missing lifecycle trace contracts
4. Ensure all subphases have entry/exit hooks

**Commands**:
```bash
# P3.1 - Phase mapping analysis
python -c "
# Read agentic_process_mapping_v28.md L2 section
# Map execute_ssot phases to:
#   [1] DISCOVERY → Discovery phase
#   [2] VALIDATION → Validation phase
#   [3] ALIGNMENT → Alignment phase
#   [4] HEALING → Healing phase
#   [5] REPORTING → Reporting phase
"

# P3.2 - Add missing PTC emitters
# Add _emit_phase_transition() calls at phase boundaries

# P3.3 - Lifecycle trace contract validation
python -m pytest tests/sovereign_hardening/test_ssot_pipeline_protocol.py -v -k lifecycle
```

**Acceptance**:
- [ ] L2 subphases mapped to execute_ssot phases
- [ ] PTC emitters added at all phase transitions
- [ ] Lifecycle tests pass

---

### Wave 4 — Standardization & Hardening

**Scope**:
1. Standardize agent base classes and initialization
2. Harden execute_ssot_entrypoint with better error handling
3. Update documentation
4. Final integration tests

**Commands**:
```bash
# P4.1 - Standardize entrypoint
# Add explicit exception handling, remove SystemExit swallowing

# P4.2 - Documentation updates
cat > docs/reference/execute_ssot_agents.md << 'EOF'
# execute_ssot Agent Registry
## L2 Lifecycle Mapping
## Script vs Agent Classification
## Flag Reference
EOF

# Final validation
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --help
python -m pytest tests/unit/test_execute_ssot_integration.py -v
```

**Acceptance**:
- [ ] Entrypoint hardened with clear error handling
- [ ] Documentation reflects new agent classifications
- [ ] All tests pass
- [ ] Smoke test successful

---

## Rules

1. **No new agents created** - Only convert existing agents to scripts or consolidate
2. **Backward compatibility** - All existing CLI flags must still work (may deprecate with warnings)
3. **Test-first** - Add tests before modifying behavior
4. **ADG validation** - Run ADG checks after each wave to verify no structural regressions
5. **UWG heal jurisdiction** - All heal decisions flow through UWG, no per-agent overrides

---

## Success Criteria

- [ ] Agent inventory complete with AGENT/SCRIPT classification
- [ ] Conflicting heal flags eliminated (single UWG source)
- [ ] L2 lifecycle phases mapped with PTC enforcement
- [ ] Documentation updated with agent registry
- [ ] All tests pass (no regressions)
- [ ] execute_ssot_entrypoint smoke test passes

---

## Implementation Commands

```bash
# Full implementation sequence
# Wave 1
python tools/adg/adg_query.py --module agentic_core.L0_routing.scripts._ssot_phases

# Wave 2
python tools/refactor/convert_agent_to_script.py --agent SSOTFolderCleanupAgent
python tools/refactor/convert_agent_to_script.py --agent RootCustomsAgent

# Wave 3
python tools/lifecycle/add_ptc_emitters.py --module execute_ssot_engine.py

# Wave 4
python -m pytest tests/unit/test_execute_ssot_integration.py -v
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --help
```

---

## Rollback Strategy

If things go wrong:
1. Revert to last known good commit: `git reset --hard a18189a090`
2. Restore agent files from backup if conversion failed
3. Re-enable old flags if consolidation causes issues
4. Run full test suite to verify rollback success

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Agents converted to scripts | ≥3 | Count files in scripts/ vs reasoning/ |
| Conflicting flags eliminated | 0 | grep -c "heal.*override\|no-heal" |
| L2 phases mapped | 5/5 | Check _emit_phase_transition calls |
| Test pass rate | 100% | pytest results |
| Entrypoint smoke test | PASS | --help returns 0 |

