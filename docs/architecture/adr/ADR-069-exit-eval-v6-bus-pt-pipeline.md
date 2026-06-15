# ADR-069 — Exit-Eval v6 BUS P/T → regression dataset pipeline runtime types (Wave 4)

**Status**: Accepted (scoped runtime types complete)
**Date**: 2026-04-26
**Wave**: exit-eval-v6 deferred-scope Wave 4 (final wave)
**Promotes**: 32 design rows → OK + 3 ADR-069 acceptance rows

**Current-state note (2026-06-15):** This ADR intentionally covers BUS P/T pipeline runtime data shapes, constants, and invariant guards. Anonymization, curation UI, storage backend, and scheduled runners are separate subsystem work, not incomplete ADR-069 scope.

---

## Context

`docs/reference/05_Exit_Evaluation_and_Control/runtime_to_regression_dataset_flow.md` defines the post-runtime pipeline that promotes BUS P/T runtime exhaust into a curated, versioned regression dataset:

```
BUS P/T  →  Candidate Pool (filtered)  →  Curation Gate (human + auto)  →  Golden Set (versioned)  →  X1A baselines + offline suites
```

All stages run **after** the runtime boundary; no stage mutates the current run.

Wave 4 implements the **runtime data shapes** (BusTRow, CandidatePoolEntry, CurationDecision, GoldenSetVersion, etc.), the **promotion heuristic constants and scoring function**, the **graduation predicate**, the **retention policy constants**, and the **invariant guards** (`assert_anonymization_fail_closed`, `assert_no_runtime_mutation`).

The actual storage backend, anonymization implementation, SME curation UI, and consumption runners (capability/regression/adversarial nightly runners) are out of scope — these are full subsystems each requiring a separate plan.

## Decision

Add `agentic_core/L3_orchestration/exit_eval/v6/bus_pt_pipeline.py` with these exports:

| Symbol | Spec section | Purpose |
|---|---|---|
| `GoldenSetTrack` enum | §3.4 | The 3 directories: `capability`, `regression`, `adversarial` |
| `BUS_PT_DEFAULT_RETENTION_DAYS = 90` | §5 | Default raw-bus retention window |
| `CANDIDATE_POOL_RETENTION_DAYS = 30` | §5 | Re-curation window |
| `GOLDEN_SET_RETENTION_INDEFINITE = True` | §5 | Indefinite retention flag |
| `PROMOTION_HEURISTIC_WEIGHTS: dict[signal, weight]` | §3.2 | The 8-signal weighted heuristic table |
| `promotion_score(signals) -> float` | §3.2 | Compute weighted score from observed signals |
| `BusTRow` | §3.1 | Per-run trajectory + env snapshot + disposition; `actor` field tags judge runs (§H2 link) |
| `CandidatePoolEntry` | §3.2 | Filtered/dedup'd candidate after BUS processing |
| `CurationVerdict` enum | §3.3 | `PROMOTE`/`REJECT`/`QUARANTINE` |
| `CurationDecision` | §3.3 | Curator-emitted decision with audit fields (curator_id, decision_at_ms) |
| `GoldenSetVersion` | §3.4 | Immutable version tag with case_count + published_at_ms |
| `GRADUATION_PASSK_THRESHOLD = 0.95` | §3.4 | Capability→regression threshold |
| `GRADUATION_K = 10` | §3.4 | Trial count |
| `GRADUATION_WINDOW = "weekly"` | §3.4 | Cadence |
| `graduates_to_regression(pass_k, k, window_count) -> bool` | §3.4 | Mechanical predicate |
| `assert_anonymization_fail_closed(entry)` | §6.2 | Tripwire — non-anonymized entry MUST NOT proceed |
| `assert_no_runtime_mutation(stage)` | §6.1 | No-op marker recording adherence |

### Key invariants enforced at type level

1. **§3.3 PROMOTE requires track** — `CurationDecision.__post_init__` raises if `verdict=PROMOTE` and `track is None`.
2. **§3.3 PROMOTE requires anonymization confirm** — also raises if `confirmed_anonymization is False`.
3. **§3.3 REJECT requires reason** — `rejection_reason` non-empty.
4. **§3.3 QUARANTINE requires reason** — `quarantine_reason` non-empty.
5. **§6.2 fail-closed** — `assert_anonymization_fail_closed` raises on `entry.anonymized=False`.
6. **§6.3 immutability** — `GoldenSetVersion.immutable=True` default; corrections produce a new version.
7. **§3.4 graduation mechanical** — `graduates_to_regression` requires `pass_k ≥ 0.95 AND k ≥ 10`. No "trust the trend" fallback.
8. **§H2 actor tagging** — `BusTRow.actor` defaults to `"agent"`; judge runs tagged `"judge"` per v4_hardening §H2.1.

## Why anonymization, curation UI, storage backend, runners stay DESIGN

| Concern | Why deferred |
|---|---|
| §4 anonymization implementation (key ceremony, deterministic, log_redacted, fail_closed) | Anonymization is a separate subsystem with its own threat model, key management, and SME-gated reversal flow. The `assert_anonymization_fail_closed` tripwire enforces the runtime invariant; the actual redaction lives elsewhere. |
| §3.3 SME curation UI/workflow | Frontend tooling is out of scope for runtime types. CurationDecision is the contract every curator surface produces. |
| §3.4 golden-set storage backend | Filesystem-vs-DB-vs-Object-Storage choice is an ops decision. GoldenSetVersion is the durable contract. |
| §3.5 consumption runners (capability_offline, regression_pre_deploy, adversarial_offline, x1a_pinned_baseline) | Each is a scheduled job with its own deployment shape. Matrix design rows describe the contract their writers will conform to. |
| §5 rejected_audit_only | Storage retention policy implementation detail; the constant is a doc-level statement |
| §3.2 dedup ALGORITHM | The dedup KEY (`trajectory_class, normalized_input_hash, output_class`) is now a typed field on CandidatePoolEntry; the dedup runner is a separate component |

## Implementation summary

| File | Change |
|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/bus_pt_pipeline.py` | NEW — 17 public symbols |
| `agentic_core/L3_orchestration/exit_eval/v6/__init__.py` | Re-export 17 symbols + add to `__all__` |
| `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_bus_pt_pipeline.py` | NEW — 40 unit tests |
| `tools/analysis/exit_v6_requirements_registry.yaml` | 32 row promotions DESIGN→OK + 3 ADR-069 acceptance rows |

## Test posture

- 522 v6 tests pass (was 482 after Wave 3; +40 BUS P/T tests)
- 0 v6 regressions
- All §3.3 verdict invariants verified (REJECT requires reason, PROMOTE requires track + anon confirm, QUARANTINE requires reason)
- §3.4 graduation predicate has boundary tests (exactly 0.95 with k=10 graduates; 0.94 and k=9 don't)
- §3.2 promotion-score sums to 13.8 when all 8 signals fire (canonical value)

## Final cross-wave summary (Waves 1-5 combined)

| Wave | What | Commit | Net effect |
|---|---|---|---|
| Wave 1 | X3F break-glass disposition (resolves H3 X3E divergence) | `e65fe5773d` | +1 ADR (065), +25 tests, 1 GAP closed |
| Wave 5 | Historical gap closure (G3 + G8 promoted to OK) | `26881d9845` (mixed) | +1 ADR (066), 2 design→OK |
| Wave 2 | H5 OTEL attrs + H6 pass^k math + H8 fault codes | `21b0ef5f41` | +1 ADR (067), +57 tests, 23 design→OK + 6 acceptance |
| Wave 3 | Grader composition runtime types | `da87e7cb19` | +1 ADR (068), +31 tests, 30 design→OK + 2 acceptance |
| Wave 4 | BUS P/T pipeline runtime types | this commit | +1 ADR (069), +40 tests, 32 design→OK + 3 acceptance |

Final matrix delta vs initial Wave-0 baseline:

| Metric | Wave-0 | Wave-4 | Delta |
|---|---:|---:|---:|
| Total reqs | 571 | ~590 | +19 acceptance rows |
| **PASS** | 356 | ~474 | **+118** |
| **DESIGN** | 214 | ~115 | **−99** |
| **GAP** | 1 | 0 | **−1** |
| Tests | 369 | 522 | +153 |
| ADRs | 0 | 5 | +5 |

## Linked

- Spec: `docs/reference/05_Exit_Evaluation_and_Control/runtime_to_regression_dataset_flow.md`
- Wave 1: `docs/architecture/adr/ADR-065-x3f-break-glass-allow-disposition.md`
- Wave 2: `docs/architecture/adr/ADR-067-exit-eval-v6-hardening-tractable-subset.md`
- Wave 3: `docs/architecture/adr/ADR-068-exit-eval-v6-grader-composition.md`
- Wave 5: `docs/architecture/adr/ADR-066-exit-eval-v6-historical-gap-closure.md`
- Code: `agentic_core/L3_orchestration/exit_eval/v6/bus_pt_pipeline.py`
- Tests: `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_bus_pt_pipeline.py`
- Matrix: `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`
