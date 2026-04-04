# L4 & UWG State ADG Hardening Execution Plan

Comprehensive ADG ingestion and gap remediation for L4 State Management and Universal Write Gateway (UWG) governance visibility.

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|---------------|--------|------------------|
| Wave 1 | L4-W1-1, L4-W1-2, L4-W1-3 | UWG Ingress Gate schema + emitters + scanner visitor | 8,500 | ADG SQLite exists, schema.py has UWG_TERMINATION_SYMBOLS | 🟡 IN PROGRESS | 100% UWG ingress coverage, 19/19 scanner tests pass |
| Wave 2 | L4-W2-1, L4-W2-2, L4-W2-3 | Mutation Record Assembly schema + emitters + visitor | 9,200 | Wave 1 complete, lifecycle_trace_contract.py has P2 emitters | 🟢 PENDING | Mutation diff/HMAC/packaging coverage, no regressions |
| Wave 3 | L4-W3-1, L4-W3-2, L4-W3-3 | Authoritative Commit + L4 Read Surface | 7,800 | Wave 2 complete, builder_types.py mutable | 🟢 PENDING | Materialized views, version alias swap coverage |
| Wave 4 | L4-W4-1, L4-W4-2, L4-W4-3 | Outbound Read Bridges (C0/L1, L0, L5, L3, L6) | 6,500 | Wave 3 complete, L4_state module structure stable | 🟢 PENDING | All 5 outbound bridge types covered |

**Total: 32,000 tokens across 4 waves, YELLOW** (medium complexity, multi-file changes)

---

## Gap Register

### GAP-1: UWG Ingress Gate Coverage (HIGH PRIORITY)
The L4 & UWG State reference document specifies 7 sequential stages in the UWG/L4 pipeline. Stage 2 (UWG Ingress Gate) and Stage 3 (Validation Gate) require ADG coverage for:

- **verify_signature** — No ADG relation type or frozenset exists
- **verify_active_policy_hash** — POLICY_HASH_SYMBOLS exists but no UWG-specific validation
- **check_allowed_capability_set** — No capability set validation frozenset at UWG boundary
- **scope/RBAC/blast_radius** — MUTATION_TRANSPORT_CLASSES has BlastRadiusChecker but no UWG integration

**Impact**: UWG ingress operations are invisible to ADG governance queries. Cannot trace mutations back to policy validation.

### GAP-2: Mutation Record Assembly Coverage (HIGH PRIORITY)
Stage 4 (Mutation Record Assembly) requires 4 operations with no current ADG coverage:

- **Generate Before/After Diff** — RFC6902_DIFF_SYMBOLS exists but no `generates_diff` relation type
- **Compute Replay Key** — REPLAY_KEY_METHODS exists but no mutation-specific replay key frozenset
- **Apply HMAC Seal** — No HMAC seal frozenset or relation type
- **Package ExecutionTrace Artifact** — EXECUTION_TRACE_CLASSES exists but no packaging frozenset

**Impact**: Mutation provenance incomplete. Cannot verify mutation integrity via ADG queries.

### GAP-3: Authoritative Commit Coverage (MEDIUM PRIORITY)
Stage 5 (Authoritative Commit) operations lack ADG coverage:

- **Claim sole write lock** — No `claims_write_lock` relation type or frozenset
- **Execute durable commit** — `commits_mutation` relation exists but no durable commit frozenset
- **Hash chain append** — `mutation_signature`, `parent_snapshot_hash` relation types exist but no hash chain frozenset
- **Rollback/heal on fail** — HEALING_ORCHESTRATOR_CLASSES exists but no rollback-specific coverage

**Impact**: Commit durability and rollback operations invisible to ADG. Cannot trace L4 master ledger state changes.

### GAP-4: L4 Read Surface Materialization (MEDIUM PRIORITY)
Stage 6 operations lack ADG coverage:

- **Generate Materialized Read Views** — No `materializes_read_view` relation type
- **Retrieval surface refresh** — RETRIEVAL_SYMBOLS exists but no refresh frozenset
- **Versioned alias swap** — No `swaps_version_alias` relation type or frozenset
- **Telemetry/audit sync** — P4 observability emitters exist but no L4-specific sync frozenset

**Impact**: L4 read surface operations invisible. Cannot trace how mutations propagate to read views.

### GAP-5: Outbound Read Bridges (LOW PRIORITY)
Stage 7 (Outbound Read Bridges) lacks ADG coverage for:

- **C0/L1 context builds** — JIT_CONTEXT_CLASSES exists but no `reads_l4_surface` frozenset
- **L0 policy_hash receipt** — POLICY_HASH_SYMBOLS exists but no L0 receipt frozenset
- **L5 constitution boundaries** — SAFETY_PLANE_CLASSES exists but no L5 L4-read frozenset
- **L3 DAG workflow rules** — No L3 reads L4 frozenset
- **L6 execution trace ingestion** — P4 emitters exist but no L6 L4-ingest frozenset

**Impact**: Cross-layer L4 state consumption invisible to ADG.

---

## Execution Plan

### Phase 1 — UWG Ingress Gate Coverage (Wave 1)
**Scope**: Add schema frozensets, lifecycle trace emitters, and static scanner visitor for UWG ingress validation.

**Files to modify**:
1. `agentic_core/adg/schema.py` — Add 4 frozensets, 4 relation types
2. `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` — Add 4 logger + emitter functions
3. `agentic_core/adg/extraction/static_scanner.py` — Add `_UWGIngressGateVisitor` (G34)

**Commands**:
```bash
# Pre-check: Verify current ADG state
python tools/adg/adg_query_bridge.py violations --severity HIGH

# Post-check: Verify new edges exist
python tools/adg/adg_query_bridge.py nodes-in-layer --layer L4
```

**New Schema Additions**:
- `VALIDATES_UWG_INTENT_SYMBOLS`: frozenset for signature/policy validation at UWG
- `CHECKS_POLICY_HASH_AT_UWG_SYMBOLS`: frozenset for UWG policy hash checks
- `CHECKS_CAPABILITY_SET_SYMBOLS`: frozenset for allowed capability validation
- `UWG_BLAST_RADIUS_SYMBOLS`: frozenset for blast radius at UWG boundary

**New Relation Types**:
- `validates_uwg_intent`
- `checks_policy_hash_at_uwg`
- `checks_capability_set`
- `validates_blast_radius_at_uwg`

**Acceptance**:
- [ ] 4 new frozensets added to schema.py with `__all__` entries
- [ ] 4 new relation types added to RelationType Literal
- [ ] 4 new loggers added to lifecycle_trace_contract.py
- [ ] 4 new emitter functions implemented with self-bootstrap calls
- [ ] `_UWGIngressGateVisitor` implemented and registered
- [ ] 19/19 scanner tests pass
- [ ] ADG regeneration shows new edges (target: 50+ edges per relation type)

---

### Phase 2 — Mutation Record Assembly (Wave 2)
**Scope**: Add schema frozensets, lifecycle trace emitters, and scanner visitor for mutation record assembly operations.

**Files to modify**:
1. `agentic_core/adg/schema.py` — Add 4 frozensets, 4 relation types
2. `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` — Add 4 logger + emitter functions
3. `agentic_core/adg/extraction/static_scanner.py` — Add `_MutationRecordAssemblyVisitor` (G35)

**Commands**:
```bash
# Verify Wave 1 coverage
python tools/adg/accelerators/adg_coverage_reporter.py --relation validates_uwg_intent

# Regenerate ADG
python tools/generate_full_adg.py --force
```

**New Schema Additions**:
- `GENERATES_MUTATION_DIFF_SYMBOLS`: frozenset for Before/After diff generation
- `COMPUTES_MUTATION_REPLAY_KEY_SYMBOLS`: frozenset for replay key computation
- `APPLIES_HMAC_SEAL_SYMBOLS`: frozenset for HMAC seal application
- `PACKAGES_EXECUTION_TRACE_SYMBOLS`: frozenset for ExecutionTrace packaging

**New Relation Types**:
- `generates_mutation_diff`
- `computes_mutation_replay_key`
- `applies_hmac_seal`
- `packages_execution_trace`

**Acceptance**:
- [ ] 4 new frozensets added with `__all__` entries
- [ ] 4 new relation types added
- [ ] 4 new emitters with self-bootstrap calls
- [ ] `_MutationRecordAssemblyVisitor` implemented
- [ ] 19/19 scanner tests pass, no Wave 1 regressions

---

### Phase 3 — Authoritative Commit + L4 Read Surface (Wave 3)
**Scope**: Add coverage for durable commit operations and L4 read surface materialization.

**Files to modify**:
1. `agentic_core/adg/schema.py` — Add 4 frozensets, 4 relation types
2. `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` — Add 4 logger + emitter functions
3. `agentic_core/adg/extraction/static_scanner.py` — Add `_L4CommitAndMaterializeVisitor` (G36)

**Commands**:
```bash
# Verify cumulative coverage
python tools/adg/accelerators/adg_coverage_reporter.py --layer L4
```

**New Schema Additions**:
- `CLAIMS_WRITE_LOCK_SYMBOLS`: frozenset for sole write lock claiming
- `PERFORMS_DURABLE_COMMIT_SYMBOLS`: frozenset for durable commit execution
- `APPENDS_HASH_CHAIN_SYMBOLS`: frozenset for hash chain append
- `MATERIALIZES_READ_VIEW_SYMBOLS`: frozenset for read view generation

**New Relation Types**:
- `claims_write_lock`
- `performs_durable_commit`
- `appends_hash_chain`
- `materializes_read_view`

**Acceptance**:
- [ ] 4 new frozensets added
- [ ] 4 new relation types added
- [ ] 4 new emitters with self-bootstrap
- [ ] `_L4CommitAndMaterializeVisitor` implemented
- [ ] 19/19 scanner tests pass

---

### Phase 4 — Outbound Read Bridges (Wave 4)
**Scope**: Add coverage for cross-layer L4 state consumption (Stage 7).

**Files to modify**:
1. `agentic_core/adg/schema.py` — Add 5 frozensets, 5 relation types
2. `agentic_core/L_CONTRACTS/lifecycle_trace_contract.py` — Add 5 logger + emitter functions
3. `agentic_core/adg/extraction/static_scanner.py` — Add `_L4OutboundBridgeVisitor` (G37)

**Commands**:
```bash
# Final coverage verification
python tools/adg/accelerators/adg_coverage_reporter.py --report l4_uwg_complete
python -m pytest tests/adg/ -v --tb=short
```

**New Schema Additions**:
- `READS_MATERIALIZED_SURFACE_SYMBOLS`: C0/L1 context from L4
- `RECEIVES_POLICY_HASH_SYMBOLS`: L0 policy_hash receipt
- `PULLS_CONSTITUTION_BOUNDARIES_SYMBOLS`: L5 constitution reads
- `READS_DAG_RULES_FROM_L4_SYMBOLS`: L3 DAG rules from L4
- `INGESTS_L4_EXECUTION_TRACE_SYMBOLS`: L6 audit ingestion

**New Relation Types**:
- `reads_materialized_surface`
- `receives_policy_hash`
- `pulls_constitution_boundaries`
- `reads_dag_rules_from_l4`
- `ingests_l4_execution_trace`

**Acceptance**:
- [ ] 5 new frozensets added
- [ ] 5 new relation types added
- [ ] 5 new emitters with self-bootstrap
- [ ] `_L4OutboundBridgeVisitor` implemented
- [ ] 19/19 scanner tests pass
- [ ] All 20 new relation types have >20 edges each in ADG

---

## Rules

1. **Never widen denominator frozensets** — EXECUTION_TRACE_CLASSES and GUARDRAIL_CLASS_NAMES remain locked
2. **Always self-bootstrap** — Every new emitter function must call itself at module level for scanner visibility
3. **Follow P0-P4 naming** — Use `_emit_` prefix for all emitter functions
4. **Scanner test non-regression** — 19/19 tests must pass after each wave
5. **ADG regeneration between waves** — Run `python tools/generate_full_adg.py --force` after each wave
6. **Layer gravity compliance** — L4 scanner visitors only reference L0-L4 symbols

---

## Success Criteria

- [ ] All 20 new relation types defined in schema.py RelationType
- [ ] All 17 new frozensets defined in schema.py with `__all__` entries
- [ ] All 17 new emitter functions in lifecycle_trace_contract.py with self-bootstrap
- [ ] 4 new scanner visitors implemented (G34-G37)
- [ ] 19/19 scanner tests pass with no regressions
- [ ] ADG shows >100 new L4/UWG-specific edges per wave
- [ ] GitHub sync completed after each wave with commit messages following pattern: `L4-UWG-W{wave}-{phase}: {description}`

---

## Implementation Commands

```bash
# Wave 1 implementation
python agentic_core/planning/token_estimator.py --file agentic_core/adg/schema.py --operation extend
python tools/generate_full_adg.py --force
python -m pytest tests/adg/test_static_scanner.py -v

# Wave 2 implementation
python tools/generate_full_adg.py --force
python -m pytest tests/adg/test_static_scanner.py -v

# Wave 3 implementation
python tools/generate_full_adg.py --force
python -m pytest tests/adg/test_static_scanner.py -v

# Wave 4 implementation
python tools/generate_full_adg.py --force
python -m pytest tests/adg/ -v

# Final verification
python tools/adg/accelerators/adg_coverage_reporter.py --comprehensive
```

---

## Rollback Strategy

If scanner tests fail or ADG shows unexpected edge count drops:

1. **Immediate**: Run `python tools/adg/repair/adg_rollback.py --to-last-known-good`
2. **Per-wave**: Revert specific wave commits using `git revert HEAD~{N}..HEAD`
3. **Diagnostic**: Check `artifacts/adg/repair_log_*.json` for failure patterns
4. **Fallback**: Use backup ADG from `artifacts/adg/_archive/` (if available)

---

## Acceptance Criteria (Quantitative)

| Metric | Target | Verification |
|--------|--------|------------|
| UWG ingress edge coverage | ≥50 edges per new relation | `adg_query_bridge.py --relation validates_uwg_intent` |
| Mutation assembly coverage | ≥50 edges per new relation | `adg_query_bridge.py --relation generates_mutation_diff` |
| Commit/materialize coverage | ≥30 edges per new relation | `adg_query_bridge.py --relation claims_write_lock` |
| Outbound bridge coverage | ≥20 edges per new relation | `adg_query_bridge.py --relation reads_materialized_surface` |
| Scanner test pass rate | 19/19 (100%) | `pytest tests/adg/test_static_scanner.py` |
| ADG total edge count | No decrease from baseline | Compare to adg_indexed_04012026_2238.sqlite |

---

*Plan generated: 2026-04-02*
*ADG baseline: adg_indexed_04012026_2238.sqlite (244.6 MB)*
*Reference: docs/reference/L4 & UWG - State.md*
