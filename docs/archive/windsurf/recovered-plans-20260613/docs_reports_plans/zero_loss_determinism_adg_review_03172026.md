# Zero Loss Determinism & Replay Core — ADG Review (03/17/2026)

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## ADG Snapshot (adg_indexed_03172026_1249.sqlite)
- **Nodes**: 68,911
- **Edges**: 1,009,287
- **Timestamp**: 03/17/2026 12:49

## Determinism & Replay Edge Analysis

### Core Determinism Signals (from ADG)
| Relation Type | Count | Document Coverage |
|---|---|---|
| `emits_determinism_digest` | 3,701 | ✅ Extensively documented (lines 67-123) |
| `uses_wall_clock` | 756 | ✅ Documented as FORBIDDEN (line 47) |
| `uses_uuid` | 609 | ⚠️ Mentioned in ReplayGuard (line 57) but not in main flow |
| `validated_by_safety_plane` | 549 | ✅ Documented (L5 Safety, line 20) |
| `accesses_credential` | 381 | ❌ Not mentioned in determinism context |
| `records_execution_trace` | 329 | ✅ Core contract (lines 8, 64, 143) |
| `snapshots_state` | 194 | ✅ Documented (line 145) |
| `signs_execution_trace` | 133 | ✅ Documented (line 143) |
| `emits_replay_key` | 21 | ✅ Documented (lines 67, 143, 145) |

### Implementation Reality Check

**✅ STRENGTHS — Document aligns with ADG reality:**

1. **Digest Emission (3,701 edges)** — Document correctly emphasizes digest as the primary determinism proof artifact. The singleton emission guard (DeterminismDigestEmitter, line 72) is implemented and widely used.

2. **Wall-Clock Prohibition (756 edges)** — ADG confirms 756 `uses_wall_clock` violations exist. Document correctly identifies this as FORBIDDEN (line 47) and prescribes SemanticClock as SOLE authority (line 48).

3. **Execution Trace (329 edges)** — Document's ExecutionTrace contract (line 143) matches implementation. The trace includes `replay_key`, `plan_hash`, `transcript_hash` as documented.

4. **ReplayGuard Implementation** — ADG shows multiple ReplayGuard classes:
   - `agentic_core/L2_execution/determinism/replay_guard.py` (primary)
   - `agentic_core/L1_cognition/types/react_trace_types.py` (reasoning)
   - `agentic_core/mixins/replay_guard_mixin.py` (base mixin)

   Document correctly describes it as a context manager patching stdlib (lines 56-59).

5. **UWG Chokepoint (5,133 writes_to edges)** — Document's description of UWG as "THE PRISON GUARD" (line 40) intercepting ALL writes is accurate. ADG shows 5,133 `writes_to` edges, all flowing through governance.

**⚠️ GAPS — Document vs ADG reality:**

1. **UUID Usage (609 edges)** — Document mentions uuid in ReplayGuard (line 57) but doesn't explain WHY 609 uuid usages exist. Are these:
   - Legitimate (trace_id generation)?
   - Violations (non-deterministic ID generation)?
   - Captured in transcript?

   **Recommendation**: Add explicit UUID policy section explaining when uuid is permitted (e.g., trace_id generation outside replay paths) vs forbidden (inside deterministic execution).

2. **Credential Access (381 edges)** — ADG shows 381 `accesses_credential` edges. Document doesn't address:
   - Are credentials part of the determinism surface?
   - Do credential rotations break digest stability?
   - Should credentials be in ReplayEnvelope (line 145)?

   **Recommendation**: Add section on credential handling in deterministic replay (likely: credentials are NOT part of digest, but credential USAGE must be transcripted).

3. **Low Replay Key Count (21 edges)** — Document emphasizes `replay_key` as critical (lines 67, 143, 145), but ADG shows only 21 `emits_replay_key` edges vs 3,701 `emits_determinism_digest` edges.

   **Possible explanations**:
   - Replay keys are emitted only at orchestration boundaries (not per-module)?
   - Digest emission is more granular than replay key emission?

   **Recommendation**: Clarify the emission cardinality relationship between digest and replay_key. Is it 1:1 or N:1?

4. **SemanticClock Implementation Fragmentation** — ADG shows multiple SemanticClock implementations:
   - `agentic_core/L0_routing/types/determinism_types.py` (canonical dataclass)
   - `agentic_core/adg/runtime/determinism_control.py` (runtime implementation)
   - `agentic_core/L6_observability/engines/semantic_clock_validator.py` (validator)

   Document presents SemanticClock as singular (line 48).

   **Recommendation**: Add note that SemanticClock has multiple implementation layers (L0 type definition, L2 runtime, L6 validation) but all enforce the same "SOLE temporal authority" invariant.

**❌ MISSING — Critical ADG signals not in document:**

1. **Network I/O Transcript** — Document mentions "un-transcripted network calls -> HARD FAIL" (lines 54, 129) but doesn't show the positive case: HOW are network calls transcripted? What's the data structure?

   **Recommendation**: Add NetworkTranscript contract showing captured fields (url, method, headers, request_body, response_body, timestamp_semantic).

2. **Replay Mode Flag Propagation** — Document mentions `replay_mode = True` (lines 76, 134) but doesn't explain:
   - Where is this flag set?
   - How does it propagate through layers?
   - What happens if L2 is in replay mode but L3 isn't?

   **Recommendation**: Add replay mode lifecycle diagram showing flag initialization (L3/L5), propagation (SandboxEnvelope), and enforcement (L2 UWG/ReplayGuard).

3. **Digest Mismatch Recovery** — Document says "Mismatch => FAIL" (line 82) but doesn't specify:
   - What layer detects the mismatch?
   - Does it trigger L2.3 Healing Loop (mentioned line 44)?
   - Is there a DigestMismatchException type?

   **Recommendation**: Add failure mode section explaining digest mismatch detection, exception type, and healing pathway.

## Document Quality Assessment

### Structure: ✅ EXCELLENT
- Vertical topology diagram (lines 1-84) clearly separates ingestion/observability (top), routing/orchestration (middle), execution core (bottom), and state bus (side).
- ASCII art is readable and information-dense.
- Clear separation between DETERMINISM CHOKEPOINT components (UWG, SemanticClock, Network Interceptor, ReplayGuard).

### Accuracy: ⚠️ MOSTLY ACCURATE with gaps
- Core concepts (UWG, SemanticClock, ReplayGuard, Digest) match implementation.
- Missing details on UUID policy, credential handling, network transcript structure, and replay mode propagation.

### Completeness: ⚠️ 85% COMPLETE
- Covers P0-P5 determinism infrastructure well.
- Missing operational details (failure modes, edge cases, multi-layer coordination).

### Actionability: ⚠️ MODERATE
- Good for understanding WHAT the system does.
- Insufficient for implementing NEW deterministic components (missing contracts, missing propagation rules).

## Recommended Updates

### Priority 1 (Critical Gaps)
1. **Add UUID Policy Section** — Explain when uuid is permitted vs forbidden, referencing the 609 ADG edges.
2. **Add Network Transcript Contract** — Show the data structure for captured network I/O.
3. **Add Replay Mode Lifecycle** — Diagram showing flag initialization, propagation, and enforcement across layers.

### Priority 2 (Clarity Improvements)
4. **Clarify Replay Key vs Digest Cardinality** — Explain why 21 replay_key edges vs 3,701 digest edges.
5. **Add Credential Handling Policy** — Explain whether credentials are in/out of determinism surface.
6. **Add Digest Mismatch Recovery** — Explain failure detection, exception type, and healing pathway.

### Priority 3 (Implementation Details)
7. **Add SemanticClock Multi-Layer Note** — Clarify that SemanticClock has L0/L2/L6 implementations with shared invariant.
8. **Add ReplayGuard Patch Surface** — List ALL patched stdlib surfaces (currently only shows time, random, uuid on line 57).

## Conclusion

The **Zero Loss Determinism & Replay Core** document is a **high-quality architectural reference** that accurately captures the core determinism infrastructure. The ADG data confirms that the described components (UWG, SemanticClock, ReplayGuard, DeterminismDigestEmitter) are implemented and widely used.

**Key strengths**:
- Accurate description of UWG chokepoint (5,133 writes_to edges confirm governance)
- Correct emphasis on digest emission (3,701 edges confirm widespread usage)
- Clear prohibition of wall-clock (756 violations confirm this is a real enforcement target)

**Key gaps**:
- Missing UUID policy (609 edges unexplained)
- Missing credential handling policy (381 edges unexplained)
- Missing network transcript contract (mentioned but not specified)
- Missing replay mode propagation mechanism (flag mentioned but not explained)

**Overall Grade: A- (90%)**
- Deduct 5% for missing UUID/credential policies
- Deduct 5% for missing operational details (failure modes, replay mode lifecycle)

**Recommendation**: Update document with Priority 1 items before next architecture review. Current version is suitable for executive/architect consumption but insufficient for implementation teams building new deterministic components.

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

