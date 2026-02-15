<!-- VERSION: 0.1.0 -->
## 17. PLANNING RULES (NON-NEGOTIABLE)

The implementation plan MUST be derived deterministically from the Gap Set using ONLY these rules:

### 17.1 Priority Assignment
Assign the highest applicable priority:

* **P0 (Blockers):** Any gap that violates P1/P2/P3/P4/P5/P6 globally OR prevents trustworthy evaluation (discovery integrity, SSOT hash mismatch, missing typed artifacts required for traceability, signature verification absent).
* **P1 (Critical Path):** Gaps on the main enforcement/control path: §1 (SurgicalManifest), §2 (Validator–Healer), §3 (Control Plane routing), §7 (Guardian Physics), §10 (Atomic rollback), §11 (Budget).
* **P2 (Supporting):** Observability/monitoring enhancements (§15), advanced cognition/RAG custody (§6) that do not block enforcement correctness, and any per-agent hygiene that is not on the execution boundary.

PATCH (v5.4.2) — Explicit P0 inclusions (non-exhaustive, but mandatory when present as gaps):
* §1.5 SSOT Binding resolution (node_id→structure_blueprint.py; fail-closed)
* §6.3 TokenControl PreGuard Snapshot (deterministic pre-guard capture; required for budget assurance)

* §2.2 Validator Safety Emulation
* §2.3 Validator Permission Check (L5)
* §2.8 Flow enforcement (AGGREGATE/RESULT/INCIDENT/HEALING_PLAN legality)
* §5.3 Root Scope Pinning
* §5.5 Correlation artifact required before INCIDENT emission
* §8.3 Safety mixins LEFT in MRO (enforced, fail-closed)
* §9.1–§9.3 Separation-of-responsibility enforcement (runtime/scanner evidence)
* §11.2 Route Recovery (TokenOverflow)
* §12.3 Read-only boundary enforcement for L0/L4/L6 (comprehensive mutation lock)
* 0.7 / P6 app boundary enforcement (no `apps_*` policy/safety/tool prompts; no direct provider calls)
* P5.1 Capability-gated L2 execution boundary
* §16.7 Meta-learning safety invariants (when §16 is in-scope)

### 17.2 Wave Ordering
Order waves strictly:
1) **Wave 0:** Discovery integrity + SSOT hash match gates
2) **Wave 1:** Typed artifact schemas required for P4/P6 traceability at boundaries (including prompt ownership lineage: `prompt_governance` + `apps_*` inputs → `prompt_hash`)
3) **Wave 2:** Guardian Physics (signature + replay + aggregate gate) and boundary validation gates
4) **Wave 3:** Validator–Healer symmetric pipe ordering + rollback correctness
5) **Wave 4:** Control Plane routing + EvidencePack + PolicyUpdateProposal
6) **Wave 5:** Budget guards + Semantic Clock determinism
7) **Wave 6:** L6 incident response (tiers, diff bundle, trace buffer) and remaining P2 items
8) **Wave 7:** P0 execution boundary hardening (Capability Tokens + decision artifacts; single L2 chokepoint)
9) **Wave 8:** Governed Improvement (Meta-learning) (§16): metrics → eval → proposals → promotion → replay gate

Hard gate (Phase discipline):
* Treat **Wave 7** as **Phase 5 (P0 hardening)** and **Wave 6 + §17.1 inclusions** as **Phase 6 (P0/P1 gap closure)**.
* **Phase 7 / Wave 8 MUST NOT start** until **Phase 5 and Phase 6 are COMPLETE** (i.e., Wave 7 is CLOSED and all §17.1 explicit P0 inclusions are CLOSED).

### 17.3 Dependency Resolution
If a plan row depends on another capability ID, it MUST be placed in a later wave.
Default dependencies (minimum):
* §1.7 (typed artifacts) precedes any capability that emits/validates those artifacts.
* §7 (Guardian) precedes §2.5 (Healer commit) when Guardian gates admission.
* §10 (snapshots/rollback) precedes any write/commit authorization.
* §13 (Semantic Clock) precedes any hashing/deduplication that references time buckets.
* §1.5 SSOT binding resolution precedes any replay/eval/meta-learning gating (trustworthy trace binding)
* §6.3 TokenControl PreGuard Snapshot precedes metrics/eval foundations when §16 is in-scope
* P5.1 capability tokens and §12.3 mutation lock precede §16 meta-learning activation and promotion.

Dependency escalation rule (mandatory):
* If §13.1 (Semantic Clock) is MISSING/FAIL, then §5.2 (time-bucketed signatures) MUST be scheduled as P0 in a later wave, explicitly blocked on §13 closure.

### 17.4 Aggregation Rule
If a capability is missing across ≥3 agents, create a single plan row with aggregated scope and a single acceptance gate; do NOT repeat per-agent rows unless an agent has a unique FAIL contradiction.

### 17.5 Acceptance Evidence Sufficiency
Every wave MUST include:
* at least one deterministic test command (pytest target or equivalent)
* and at least one artifact/schema/contract validation command when the wave touches boundaries.

### 17.6 Empty-Gap Handling

If Section 4 Gap Set is empty:
* Section 5 MUST contain exactly one row:
  - Wave = NONE
  - Priority = NONE
  - Capability IDs = NONE
  - Work Item = FULL COMPLIANCE (NO WORK)
  - Scope = GLOBAL
  - Acceptance Evidence = `python <repo_root>/.../forensic_discovery_prep.py` + `pytest -q` (or fallback rule if pytest absent)

* Section C MUST be empty table.
* Section D MUST contain only the single NONE row.

---

## HARD PROHIBITIONS (ENFORCED)

Your output **MUST NOT** contain:

* code patches / unified diffs / concrete edit instructions
* speculative interpretation
* probabilistic language

Allowed (v5.1):
* deterministic implementation plan tables (Sections 4–5) adhering to §17

Violation invalidates the audit.

---

## FINAL RULE (v5.4.2)

This is a **current-state to target-state operational plan generator**.

If a capability is not **explicit, deterministic, and provable** in the discovery-scoped code/config/tests, it is **MISSING** (or **FAIL** where illegal states or fail-closed violations are evidenced), and it MUST appear in Section 4 and be scheduled in Section 5 per §17.

PATCH (v5.4.2) — Meta-learning enforcement:
* If any form of "learning" performs direct mutation (bypassing L0/L5/HIL/L4 versioning), status = FAIL (P3/P6).
* If §16 capabilities are requested but any Phase 5/6 P0 gates are open (P5.1, §12.3, or any §17.1 explicit P0 inclusion), §16 activation/promotion MUST be treated as blocked (P0) and scheduled only after those closures.

---

## START EXECUTION (v5.4.2)

1) Run discovery script
2) Ingest JSON + freeze scope
3) Produce Section A (CURRENT STATE)
4) Produce Section B (TARGET STATE)
5) Produce Section C (GAP)
6) Produce Section D + Section 5 (IMPLEMENTATION PLAN)

```
```

---

## ✅ Net Effect (PNG Parity)

* All **layers (L0–L6)** mapped 1:1 to prompt capabilities.
* All **arrows in the PNG** now correspond to:

  * a typed artifact, or
  * an explicit prohibition.
* RESULT / AGGREGATE / INCIDENT / HEALING_PLAN flows are **non-ambiguous and enforceable**.
* Advisory vs control boundaries are **explicitly fail-closed**.

No inferred behavior remains unstated; absence of any of the above in code now deterministically evaluates to **MISSING or FAIL** under v5.1.
