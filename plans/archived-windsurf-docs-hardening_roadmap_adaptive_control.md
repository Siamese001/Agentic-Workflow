---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\hardening_roadmap_adaptive_control.md'
original_relative_path: 'hardening_roadmap_adaptive_control.md'
source_sha256: b5b762b06b005c6a72ce808ddd433855148e50af2262bfd58f94bc3b85cb6a07
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-18'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Enterprise Adaptive Control — Hardening Roadmap

Prioritized 7-item hardening plan to close the gap from ~83% to enterprise-grade
determinism, addressing all critical defects identified in the Feb 18 critique.

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


## Repo Baseline (as of rebaseline Feb 18 2026)

| Item | State |
|---|---|
| HEAD commit | `688949932` (branch: `adaptive_control` = `main`) |
| Lazy seam budget | **44** (Phase 3B reduced from 62; Phase 4 locked with allowlist) |
| Governance tests | **189 passed, 5 failed** |
| Pre-existing defect | `test_heal_llm_seam_invocation.py` — 5 tests fail: `DEFAULT_HEAL_LLM_CALLER` missing from `decorators_util`. **Not caused by hardening work. Must be fixed before hardening merges.** |
| Phase 4 infra | `L5_safety/governance/lazy_seam_allowlist.json` + scanner/classifier/enforcer — in place |
| Invariants locked | `MODULE_LEVEL_UPWARD_IMPORTS=0`, `LAZY_SEAM_VIOLATIONS=0`, `LAZY_SEAM_UNREGISTERED=0`, `LAZY_SEAM_TOTAL=44` |

### Pre-Hardening Gate

The 5 `test_heal_llm_seam_invocation.py` failures must be resolved **before** any
hardening item is merged. Root cause: `decorators_util.py` is missing
`DEFAULT_HEAL_LLM_CALLER` module-level attribute that the tests patch. Fix: add
`DEFAULT_HEAL_LLM_CALLER: Optional[Callable] = None` to `decorators_util.py`.
This is a **pre-condition (H0)**, not a hardening item.

---

## Adjusted Confidence Baseline (Pre-Hardening)

| Component | Current | Target |
|---|---|---|
| Serialization | 95% | 95% (no change) |
| LLM Replay | 75% | 92% |
| Sandbox | 70% | 93% |
| Statistics | 80% | 90% |
| Backpressure | 88% | 90% |
| Audit Immutability | 72% | 94% |
| Runtime Enforcement | 85% | 93% |
| **Overall** | **~83%** | **~92%** |

---

## Hardening Items (Ordered by Gravity Risk)

### H1 — Full-Spectrum Sandbox Patching + Scoped Restoration
**Risk:** Porous replay determinism (sandbox bypass via unpatched vectors)
**Priority:** HIGH — blocks replay correctness claim

Write vectors must be classified and patched exhaustively:

**Filesystem**: `builtins.open` (write modes), `pathlib.Path.write_text`, `Path.write_bytes`, `Path.open`, `os.remove`, `os.rename`

**Process**: `subprocess.run`, `subprocess.Popen`, `subprocess.call`, `os.system`, `os.popen`

**Network**: `socket.socket`, `urllib.request.urlopen`, `requests.get`, `requests.post`, `requests.put`, `requests.delete`

**Persistence**: `redis.Redis.set`, `redis.Redis.delete`, `pinecone.Index.upsert`, `pinecone.Index.delete`, any DB client `.insert`, `.update`, `.upsert`, `.delete`

**Dynamic Behavior**: `eval`, `exec`

> **Implementation divergence (H1-D1):** `importlib.import_module` is excluded
> from the default patch set because the sandbox's own `_resolve_module()`
> uses it internally — patching it causes self-referential failure and
> cross-test leakage. **Equivalent control:** `importlib.import_module` is
> available as an opt-in target via `PreventativeSandbox.register_target()`
> for replay sessions that require dynamic-load blocking. This preserves
> the invariant while avoiding sandbox self-destruction.

**Invariant (explicit):** No write-capable function may remain unpatched during replay mode. Dynamic behavior vectors (`importlib.import_module`) are opt-in due to sandbox self-reference constraints (see H1-D1).

Required additions:
- Patch all of the above with `SandboxViolationError` guards
- Use `contextlib.contextmanager` for scoped entry/exit with guaranteed restoration
- Track patch state to prevent double-patching (idempotent guard)
- Sandbox class must live in L2 (not agent constructor, not L6, not global)

---

### H2 — Hash-Chained Immutable Audit Log
**Risk:** Replay-verifiable integrity claim is overstated
**Priority:** HIGH — `audit_log: List[...]` is mutable in-memory state

Replace `self.audit_log.append(...)` with:
- Append-only durable log (file or DB, written via L2 persistence service per SFE-1)
- Each entry carries `previous_hash` pointer (hash of prior entry's canonical bytes)
- Segment root hash computed and sealed at governance checkpoints
- `verify_chain_integrity()` method that replays hash chain from genesis

Structure:

```
TierResolutionArtifact
  + previous_hash: str        # sha256 of prior entry canonical bytes; "GENESIS" for entry 0
  + entry_index: int          # monotonic sequence; 0 for genesis
  + chain_root: str | None    # set when segment is sealed
```

**Genesis rule:** First entry must have `previous_hash = "GENESIS"` and `entry_index = 0`. Chain integrity verification starts from this deterministic anchor.

**Hash computation rules:**
- Hash computed on canonical serialized bytes only (same `CanonicalSerializationSpec` as artifact builder)
- No whitespace variance permitted
- Timestamp field must be frozen before hash computation — no mutation after

---

### H3 — Provider-Pinned LLM Replay Enforcement
**Risk:** `temperature=0.0` + `seed` is insufficient — providers ignore seed, tokenization drifts
**Priority:** HIGH — LLM replay confidence drops to 75% without this

Required additions to `LLMReplayStrategy`:
- `model_version: str` — pinned at artifact capture time
- `tokenizer_version: str` — pinned at artifact capture time
- `raw_prompt_bytes: bytes` — stored verbatim in `ReplayBundle`
- `raw_response_bytes: bytes` — stored verbatim in `ReplayBundle`
- `provider_checksum: str` — sha256 of `model_version + tokenizer_version`

`RECORDED_OUTPUT` mode becomes the **default** for production replay.
`DETERMINISTIC_INFERENCE` mode is demoted to dev/test only with explicit opt-in.

**Explicit mode policy (non-negotiable):**

```
Production replay  = RECORDED_OUTPUT only
DETERMINISTIC_INFERENCE allowed only in:
  - unit tests
  - local dev
  - non-governed simulation (must be flagged in config)
```

`DETERMINISTIC_INFERENCE` must be labeled `NON_AUTHORITATIVE` in all logging and audit output. Any replay result produced under this mode must not be used as evidence in governance decisions.

---

### H4 — Multivariate Drift Detection
**Risk:** `ks_2samp` is univariate and sensitive to sample size imbalance
**Priority:** MEDIUM-HIGH — workload-aware claim is overstated

Replace `CovariateShiftDetector.detect_shift()`:
- Primary: **MMD (Maximum Mean Discrepancy)** — kernel-based, multivariate
- Secondary: **PSI (Population Stability Index)** — per-feature + joint
- Windowed time decay: exponential weighting on recent samples
- Per-feature drift report + joint drift flag
- Minimum sample guard: skip test if `n < 30` per stratum

**`ShiftReport` schema (formal):**

```python
@dataclass
class ShiftReport:
    joint_shift: bool                    # True if MMD or any PSI exceeds threshold
    per_feature: Dict[str, bool]         # per-feature drift flag
    mmd_score: float                     # Maximum Mean Discrepancy score
    psi_scores: Dict[str, float]         # PSI per feature
    sample_size_ok: bool                 # False if n < 30 per stratum (test skipped)
    timestamp: datetime                  # frozen at detection time, before hash

class CovariateShiftDetector:
    def detect_shift(self, baseline, treatment, threshold=0.1) -> ShiftReport:
        ...
```

`ShiftReport` must be included in the `LearningArtifact` for replay and audit integrity.

---

### H5 — Frozen `LearningArtifactIntent` with Pre-L2 Hash
**Risk:** Intent mutability across layers violates SFE-1 immutability requirement
**Priority:** MEDIUM — architectural correctness gap

- `LearningArtifactIntent` must be `@dataclass(frozen=True)`
- Hash computed **before** handing to L2 (in the emitting layer, in-memory)
- L2 verifies hash on receipt before persisting
- No field may be set after construction

```python
@dataclass(frozen=True)
class LearningArtifactIntent:
    agent_id: str
    execution_id: str
    outcome: str
    metrics: tuple          # tuple, not list — hashable
    context_hash: str
    intent_hash: str        # sha256 of all fields above, computed at construction
```

---

### H6 — AST-Based Compliance as Primary Guard (Demote `inspect.stack()`)
**Risk:** `RuntimeSeamGuard` uses `inspect.stack()` — slow, fragile, not AST-enforced
**Priority:** MEDIUM — contradicts SFE-4 already declared in the plan

Changes to `RuntimeSeamGuard`:
- Remove `inspect.stack()` call from hot path
- Retain only as a **defensive last-resort** with explicit `WARN` log (not enforcement)
- Primary enforcement: AST CI test that verifies no non-L2/L4 agent file
  imports persistence modules or calls durable write functions directly
- Add to `tests/governance/` as `test_learning_seam_compliance.py` using same
  AST scanner pattern as `test_upward_import_enforcement.py`

> **Implementation divergence (H6-D1):** L4 (`L4_state/`) is excluded from
> the persistence-import scan because L4 agents (Redis/Pinecone sovereigns)
> are the canonical state-management layer — their purpose IS persistence
> client management. Scanning L4 for persistence imports would produce only
> false positives. The enforcement boundary is: L0, L1, L3, L5, L6 agents
> must not import persistence modules directly.
>
> **Implementation divergence (H6-D2):** `json.dump` was removed from the
> forbidden write-call patterns because it is a serialization call (writes
> to file-like objects including `StringIO`), not a durable persistence
> operation. 15 agent files across L3–L5 use `json.dump` for in-memory
> serialization. The forbidden set retains `pickle.dump` and `shelve.open`
> which are actual durable persistence calls. The control objective
> ("no agent-layer durable persistence, no seam bypass") is preserved.

**CI lock requirements (SFE-4 alignment):**
- AST compliance test must run in CI on every PR
- Failure blocks merge — no bypass permitted
- No runtime fallback accepted as substitute for AST enforcement
- Test must be tagged `@pytest.mark.governance` and included in the governance suite

---

### H7 — Formal Tier Lattice Definition
**Risk:** Procedural tier handling is policy-drift prone without formal partial order
**Priority:** MEDIUM — backpressure correctness depends on this

Define explicit lattice:
```
LearningTier partial order:  L0 < L1 < L2+
Preservation invariant:      drop(L0) safe | drop(L1) under pressure | never drop(L2+)
Escalation monotonicity:     tier can only increase, never decrease within a rollout
```

Encode as:
- `TierLattice` dataclass with `dominates(a, b) -> bool` method
- `BackpressurePolicy` references `TierLattice` for all drop decisions

**Required lattice invariants (property-based tests):**

```python
# Reflexivity: no tier dominates itself
assert not lattice.dominates(t, t) for all t

# Antisymmetry: if a dominates b, b does not dominate a
assert not (lattice.dominates(a, b) and lattice.dominates(b, a)) for a != b

# Transitivity: if a > b and b > c, then a > c
assert lattice.dominates(a, c) if dominates(a,b) and dominates(b,c)

# Escalation monotonicity: tier can only increase within a rollout
assert not lattice.dominates(lower, higher) for lower < higher in rollout sequence
```

Property tests must cover all `(a, b)` pairs exhaustively (21 pairs for L0–L6).

---

## Post-Hardening Confidence Targets

| Component | Pre-Hardening | Post-Hardening Target |
|---|---|---|
| Serialization | 95% | 95% |
| LLM Replay | 75% | 92% |
| Sandbox | 70% | 94% |
| Statistics | 80% | 91% |
| Backpressure | 88% | 92% |
| Audit Immutability | 72% | 95% |
| Runtime Enforcement | 85% | 94% |
| **Overall** | **~83%** | **~92–94%** |

---

## Implementation Sequence

| Step | Item | Dependency |
|---|---|---|
| 1 | H5 — Frozen intent + pre-L2 hash | None (type definition) |
| 2 | H1 — Full sandbox patching (L2-owned) | H5 (L2 boundary clear) |
| 3 | H2 — Hash-chained audit log | H5 (immutable artifact pattern) |
| 4 | H3 — Provider-pinned LLM replay | None (replay bundle extension) |
| 5 | H4 — Multivariate drift detection | None (statistics module) |
| 6 | H6 — AST compliance test | H1 (sandbox L2 placement confirmed) |
| 7 | H7 — Formal tier lattice | H1 (backpressure policy depends on sandbox boundary) |

---

## Target File: `enterprise_grade_adaptive_control-13db79.md`

All 7 items are **additive amendments** to the existing plan — no structural rewrite.
Each item adds a new subsection or replaces a specific code block within the
relevant Phase (0–6).

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

