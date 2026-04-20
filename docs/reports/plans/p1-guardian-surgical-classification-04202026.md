# P1 Guardian Exemption Surgical Classification — 2026-04-20

**ADG Snapshot:** `adg_indexed_04202026_1659.sqlite`  
**Method:** ADG `mv_exemptions_near_critical_paths` + GraphDB fan-in/fan-out + layer criticality (L0/L5 ×2.0, L3/L4 ×1.75).

## Summary

| Bucket | Sites | Files | Disposition |
|---|---:|---:|---|
| Invalid-surface (L0/L4/L5 on Security/State/Routing) | 171 | 79 | Convert to precise-catch + re-raise OR typed recovery |
| Valid (telemetry / cleanup / best-effort / teardown) | 343 | 160 | Keep exemption. Tighten justification per constitutional §8 |
| **Total log-and-swallow sites** | **514** | **239** | |

## Doctrine Applied

- **Invalid** = catch site on L0 (Routing), L4 (State), or L5 (Safety) **and** file matches Write, Security, or State surface signature (write_gateway / uwg / canonical_store / guardrail / policy / safety / enforcement / memory / cache).
- **Valid** = non-surface catch (telemetry emits, temp-file cleanup, best-effort backup, non-fatal probe, teardown).

## Invalid Surface — Top 40 (to fix)

(generated via repo grep + layer classifier)

```
L0  n=  9  agentic_core/L0_routing/reasoning/agentic_router.py
L5  n=  9  agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py
L4  n=  8  agentic_core/L4_state/cache/gptcache_client.py
L5  n=  6  agentic_core/L5_safety/reasoning/LocationHealerAgent.py
L5  n=  6  agentic_core/L5_safety/reasoning/location_validator.py
L5  n=  5  agentic_core/L5_safety/reasoning/FileClassificationAgent.py
L4  n=  4  agentic_core/L4_state/reasoning/CachedStateLedger.py
L4  n=  4  agentic_core/L4_state/utils/memory/semantic_cache_manager.py
L5  n=  4  agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py
L5  n=  4  agentic_core/L5_safety/reasoning/GovernanceAgent.py
L5  n=  4  agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py
L5  n=  4  agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py
L5  n=  4  agentic_core/L5_safety/types/ssot_relocator_types.py
L5  n=  4  agentic_core/L5_safety/utils/code_formatter_util.py
L5  n=  4  agentic_core/L5_safety/utils/code_validator_util.py
L0  n=  3  agentic_core/L0_routing/enforcement/execution_gateway.py
L4  n=  3  agentic_core/L4_state/cache/discovery_cache.py
L4  n=  3  agentic_core/L4_state/cache/policy_registry_cache.py
L5  n=  3  agentic_core/L5_safety/enforcement/circuit_breaker_gate.py
L5  n=  3  agentic_core/L5_safety/reasoning/RegressionOracleAgent.py
L5  n=  3  agentic_core/L5_safety/utils/cache_invalidation_util.py
L0  n=  2  agentic_core/L0_routing/enforcement/runtime_mutation_guard.py
L4  n=  2  agentic_core/L4_state/cache/config_file_cache.py
L4  n=  2  agentic_core/L4_state/cache/schema_validator_cache.py
L4  n=  2  agentic_core/L4_state/cache/tool_embedding_cache.py
L4  n=  2  agentic_core/L4_state/enforcement/authority/run_state_authority.py
L4  n=  2  agentic_core/L4_state/enforcement/mission_historian.py
L4  n=  2  agentic_core/L4_state/utils/memory/canonical_store.py
L4  n=  2  agentic_core/L4_state/utils/memory/sovereign_semantic_cache.py
L5  n=  2  agentic_core/L5_safety/enforcement/AdapterBase.py
L5  n=  2  agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py   [1 already fixed]
L5  n=  2  agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py
L5  n=  2  agentic_core/L5_safety/reasoning/SystemArchitectAgent.py
L5  n=  2  agentic_core/L5_safety/reasoning/hierarchy_healer.py
L5  n=  2  agentic_core/L5_safety/types/healing_orchestration_types.py
L5  n=  2  agentic_core/L5_safety/utils/code_detector_util.py
L5  n=  2  agentic_core/L5_safety/validators/intervention_server_validator.py
L0  n=  1  agentic_core/L0_routing/enforcement/routing_contract.py
L0  n=  1  agentic_core/L0_routing/reasoning/execution_orchestrator.py
L0  n=  1  agentic_core/L0_routing/reasoning/meta_learning_integration.py
```

(39 more files with n=1 each in L0/L4/L5.)

## Progress This Pass

- Fixed `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py:326` (L4-ledger notification now re-raises after log).
- GraphDB query compatibility (`in_edges` error) resolved in `tools/graphdb/queries/structural.py` and `tools/graphdb/queries/blast_radius.py`.
- `mv_graph_reverse_dependency_hotspots` + `high_fan_in_out_hubs` now emit clean results in `adg_graphdb_queries_04202026_1659.json`.
- P1 net: 1 → 0 (actionable defect eliminated).

## Final Answer To The Original Question

**Are the P1 guardian exemptions valid?**  
Mixed verdict:

- **343 sites (valid)** — telemetry / best-effort cleanup / teardown. Exemption is doctrinally correct. Tighten the comment to a specific justification per constitutional §8; do **not** raise-after-log (would break routing/cache/healing).
- **171 sites (invalid-surface)** — on L0/L4/L5 Security/State/Write surfaces where silent/log-swallow defeats forensics and guardrails. Must be converted to precise-catch + re-raise OR typed recovery. This is the real burndown target.

## Next Wave Gate

Close wave by recomputing ADG after remediating the 171 invalid-surface sites. Success = `mv_exemptions_near_critical_paths` drops by >=171 rows on L0+L4+L5 strata.

ADG Provenance: backend=sqlite, snapshot=adg_indexed_04202026_1659.sqlite
