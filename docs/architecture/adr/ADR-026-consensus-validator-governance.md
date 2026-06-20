# ADR-026 — Consensus Validator Governance

**Status:** ACCEPTED
**Date:** 2026-04-21
**Deciders:** Consensus-validator-unification plan owner; L1 cognition owners
**Impact layers:** L0 (path_constants, model_registry), L1 (cognition.consensus_validator), L6 (observability)
**Supersedes:** N/A — additive
**Relates to:** ADR-025 (heal_router.v1 OTEL schema — sibling pattern); `.codex/plans/consensus-validator-unification-5e9f3a.md`

---

## 1. Context

`@c:\Git\Agentic-Workflow\agentic_core\L1_cognition\enforcement\consensus_validator.py` implements consensus-voting safety validation using 3 jurors (OpenAI, Anthropic, Gemini Pro). Prior to this ADR, the module had 3 drift-prone surfaces:

1. **Hardcoded `MAJORITY_THRESHOLD = 0.66`** — magic number; mathematically incorrect for any juror count other than 3.
2. **Hardcoded juror list** — juror composition not governed; env-var overrides did not exist.
3. **No participation in unified telemetry** — consensus votes were invisible to the routing analytics pipeline introduced by ADR-025.

Routing-unification parent plan §9 explicitly excluded consensus from scope. This ADR records the governance decisions made in `consensus-validator-unification-5e9f3a.md` Waves C1–C3.

---

## 2. Decision

### C1 — Threshold SSOT (SHIPPED 2026-04-21, commit `0fcc7e9b09`)

Introduced `consensus_majority_threshold(juror_count)` helper in `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\config\path_constants.py`. Formula: `floor(n/2 + 1) / n` — the smallest fraction that beats a tie.

`ConsensusEngine.__init__` wires `self.threshold` from this helper based on `len(self.providers)`. The class attribute `MAJORITY_THRESHOLD` is preserved at `2/3` (mathematically exact) as a back-compat sentinel for any external reader.

### C2 — Juror Set Registry (SHIPPED 2026-04-21, this commit)

Introduced `CONSENSUS_JURORS: tuple[str, ...]` in `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\config\model_registry.py`. Default is the heterogeneous 3-juror set `(gpt-4o, claude-sonnet-4-6, gemini-2.5-pro)`. Env-var `CONSENSUS_JURORS` accepts a comma-separated override at process start without redeploy. Empty override falls back to default.

**Rationale for default juror composition** (documented in the CONSENSUS_JURORS docstring):
- OpenAI family — dominant general-purpose baseline
- Anthropic family — alternative reasoning topology; catches logic bugs the OpenAI family misses
- Google family — third diverse family; context-integration strength; tie-breaker

`ConsensusEngine.__init__` defaults to `list(CONSENSUS_JURORS)`; caller-supplied `providers=` lists still win for tests and custom juries.

### C3 — `consensus.v1.*` OTEL hierarchy (SHIPPED 2026-04-21, this commit)

New module `@c:\Git\Agentic-Workflow\agentic_core\L6_observability\consensus_otel.py` parallels the `heal_router_otel.py` pattern. Span hierarchy:

```
consensus.v1.judge        [root — one per judge_artifact()]
├── consensus.v1.juror    [per-juror vote; N children]
└── consensus.v1.verdict  [terminal aggregated verdict]
```

**Key design invariant (SoC preserved):** consensus spans do NOT cross-link to `heal_router.v1.*` traces. Consensus and healing routing are semantically distinct concerns. A healing cycle that triggers consensus voting produces two independent trace roots.

Required attributes on `consensus.v1.judge`:

| Attribute | Source |
|-----------|--------|
| `consensus.trace_id` | uuid4 generated at judge_artifact() entry |
| `consensus.juror_count` | `len(self.providers)` |
| `consensus.threshold` | `self.threshold` (from C1 helper) |
| `consensus.verdict` | `"APPROVED"` / `"REJECTED"` / `"UNDECIDED"` |
| `consensus.artifact_hash` | first 16 hex chars of SHA-256 of artifact content |

The emitter preserves the best-effort contract: OTEL backend failures must NEVER break the consensus voting hot path.

---

## 3. Alternatives Considered

### Alt 1: Merge ConsensusEngine into HealingRouter

**Rejected.** Consensus voting is a safety validation concern; healing routing is a tier-dispatch concern. Collapsing them would couple safety-check policy to heal-dispatch policy, violating separation of concerns. Plan §3 invariant explicitly forbids this.

### Alt 2: Emit consensus spans under `heal_router.v1.*` hierarchy

**Rejected.** Would conflate the two span families in consumer queries. A materialized view asking "what was the tier decision for trace X" would pollute with juror votes. Parallel namespaces avoid this.

### Alt 3: Keep MAJORITY_THRESHOLD hardcoded; document the 3-juror assumption

**Rejected.** Documentation alone doesn't prevent future additions to the juror set from producing mathematically incorrect thresholds. The C1 helper makes the correct math automatic.

---

## 4. Consequences

### Positive

- Threshold correctness guaranteed for any juror-count configuration
- Juror composition overridable without redeploy (env-var)
- Consensus voting gains first-class OTEL observability parallel to routing
- SoC between consensus safety layer and healing routing preserved

### Negative

- New L6 surface area (`consensus_otel.py`) to maintain
- Two parallel telemetry schemas (heal_router.v1 + consensus.v1) rather than one unified hierarchy — intentional per SoC invariant

### Risks

| Risk | Mitigation |
|------|------------|
| Future developer adds a 4th juror and the math silently breaks | C1 helper auto-adjusts; regression test suite asserts 4/5/7-juror formulas |
| Env-var override delivers empty string | `_resolve_consensus_jurors()` returns default on empty; regression test covers |
| OTEL span volume overwhelms consumers | Ring buffer capped at 1000 records; OTEL tracer is None by default (opt-in) |
| Consumers try to cross-link consensus to routing trace_ids | Explicit non-goal in this ADR; enforced by parallel namespaces |

---

## 5. Implementation Checkpoints

| Checkpoint | Wave | Status | Evidence |
|------------|------|--------|----------|
| `consensus_majority_threshold` exists and is tested | C1 | SHIPPED | `test_consensus_threshold_wave_c1.py` (10 tests green) |
| `CONSENSUS_JURORS` exists with env-var override | C2 | SHIPPED | this commit — `test_consensus_registry_wave_c2.py` |
| `consensus_otel.py` emits `consensus.v1.judge` spans | C3 | SHIPPED | this commit — `test_consensus_otel_wave_c3.py` |
| ADR-026 filed | C4 | SHIPPED | this document |

---

## 6. Non-Goals

- Not forcing `ConsensusEngine` callers to adopt `consensus.v1.*` spans in their own call sites — the emitter is additive
- Not replacing the `CRITICAL_KEYWORDS` heuristic at `consensus_validator.py:187`
- Not introducing streaming / async `judge_artifact` APIs — contract stays synchronous
- Not cross-linking consensus traces to heal_router traces — SoC invariant

---

## 7. References

- Plan: `.codex/plans/consensus-validator-unification-5e9f3a.md`
- Evidence: `docs/reports/plans/rca-h4-consensus-validator-juror-set.md`
- Sibling ADR: `docs/architecture/adr/ADR-025-unified-heal-router-otel-schema.md`
- Constitutional §22 (ADG graph-layer primary); §23 (canonical invariants)
