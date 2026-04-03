# execute_ssot Agent Registry

**Version:** Wave 4  
**Last Updated:** 2025-01-03  
**Purpose:** Registry of all agents called by execute_ssot with lifecycle mappings

---

## Quick Reference

| Metric | Count |
|--------|-------|
| Total Agents | 50 |
| AGENT (Reasoning) | 27 |
| SCRIPT (Deterministic) | 23 |
| L2 Phases Mapped | 5/5 |
| Flag Conflicts | 0 |

---

## Flag Reference

| Flag | Purpose | UWG Jurisdiction |
|------|---------|------------------|
| `--scan-only` | Disable mutations (dry run) | ✅ UWG respects |
| `--validate` | Validation mode (implies scan-only) | ✅ UWG respects |
| `--interactive` | Human-in-the-loop | ✅ UWG respects |
| `--territory` | Specific territory scan | ✅ UWG respects |
| `--heal` | **REMOVED** | ❌ Was conflicting |

**Note:** UWG has sole jurisdiction over healing decisions. Use `--scan-only` to disable healing.

---

## L2 Lifecycle Phase Mapping

### Discovery Phase (L0-L1)
Agents: RootCustomsAgent, SSOTFolderCleanupAgent, SubAtomicRegistryAgent, ToolsmithAgent, BootstrapAgent

### Validation Phase (L1-L5)
Agents: ASTValidatorAgent, CodeValidatorAgent, ComplexityAnalyzerAgent, ArchitectureGovernorAgent

### Alignment Phase (L1-L3)
Agents: MetaLearningAgent, DomainPlannerAgent, FissionManagerAgent, UnifiedAgent, CognitiveDispositionAgent

### Healing Phase (L2-L5)
Agents: EmbeddingSovereignAgent, RedisSovereignAgent, SovereignMCPGatewayAgent, StructuredEngineAgent, CodeHealerAgent

### Reporting Phase (L4)
Agents: CoverageAgent, BenchmarkingAgent, CostGovernorAgent, StateManagementAgent

---

## PTC (Phase Transition Contract) Emitters

All L2 phases now have lifecycle trace emitters:

```python
# Discovery
_emit_records_execution_trace(..., "execute_ssot.phase.discovery.start")
_emit_records_execution_trace(..., "execute_ssot.phase.discovery.end")

# Validation
_emit_records_execution_trace(..., "execute_ssot.phase.validation.start")
_emit_records_execution_trace(..., "execute_ssot.phase.validation.end")

# Alignment
_emit_records_execution_trace(..., "execute_ssot.phase.alignment.start")
_emit_records_execution_trace(..., "execute_ssot.phase.alignment.end")

# Healing
_emit_records_execution_trace(..., "execute_ssot.phase.healing.start")
_emit_records_execution_trace(..., "execute_ssot.phase.healing.end")

# Reporting
_emit_records_execution_trace(..., "execute_ssot.phase.reporting.start")
_emit_records_execution_trace(..., "execute_ssot.phase.reporting.end")
```

---

## Agent Classification Summary

See full matrix: [ssot_agent_classification_matrix.md](./ssot_agent_classification_matrix.md)

### Key Conversion Candidates (SCRIPT)
- SSOTFolderCleanupAgent → ssot_folder_cleanup_util.py
- RootCustomsAgent → root_customs_util.py
- CodeJanitorAgent → code_janitor_util.py
- CodeValidatorAgent → code_validator_util.py
- StateManagementAgent → state_management_util.py

---

## Consolidation Opportunities

| Pair | Action | Status |
|------|--------|--------|
| CodeHealerAgent + CodeJanitorAgent | Merge | Planned |
| CodeValidatorAgent + CodeDetectorAgent | Merge | Planned |
| BoundaryTestingAgent + AdversarialProbeAgent | Merge | Planned |
| ArchitectureGovernorAgent + ArchitectureGovernorValidatorAgent | Merge | Planned |
| StateManagementAgent + GravityStateAgent | Merge | Planned |

---

## Entrypoint Error Handling

Hardened exception handling in execute_ssot_entrypoint.py:

```python
try:
    _legacy_main(...)
except SystemExit as exc:
    return int(exc.code) if exc.code is not None else 0
except KeyboardInterrupt:
    print("\n[INFO] Interrupted by user")
    return 130
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    return 1
```

---

## Verification Commands

```bash
# Test entrypoint
python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --help

# Test engine imports
python -c "from agentic_core.L0_routing.scripts.execute_ssot_engine import SovereignDecisionEngine"

# Run tests
python -m pytest tests/unit/test_execute_ssot_integration.py -v
```

---

## Success Metrics (Wave 4)

| Metric | Target | Status |
|--------|--------|--------|
| Agents inventoried | 50 | ✅ |
| AGENT/SCRIPT classified | 27/23 | ✅ |
| L2 phases mapped | 5/5 | ✅ |
| Flag conflicts eliminated | 0 | ✅ |
| PTC emitters added | 10+ | ✅ |
| Entrypoint hardened | Yes | ✅ |
| Tests passing | 100% | ✅ |

---

## Next Steps

1. **Phase 2 (Future):** Convert 23 SCRIPT agents to utility scripts
2. **Phase 2 (Future):** Consolidate 5 duplicate agent pairs
3. **Maintenance:** Keep registry updated as agents evolve

