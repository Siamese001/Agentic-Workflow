# P2 HIGH Antipattern Remediation Plan

Systematic elimination of 1,879 HIGH-severity antipatterns across 526 files, ordered by production risk (Prod%) not volume, with micro-waves to derisk each category.

---

## Current State (baseline from ADG 04072026_1401)

| Category | Count | Share | Prod% | Files | Risk Profile |
|---|---|---|---|---|---|
| broad_exception_catch | 1,042 | 55% | 90% | ~350 | Masks real errors; code runs but wrong |
| log_and_swallow | 450 | 23% | 96% | ~150 | Error logged then dropped; caller never knows |
| silent_exception_swallow | 228 | 12% | 94% | ~100 | Error vanishes; zero trace; hardest to debug |
| return_none_swallow | 159 | 8% | 94% | ~80 | Caller gets None; cascading NoneType failures |
| **TOTAL** | **1,879** | 100% | 92% | 526 | Top layer: L_SHARED; hotspot: 12% in top-10 files |

**Priority order by risk-per-instance** (not volume):
1. `silent_exception_swallow` — invisible failures, zero observability
2. `return_none_swallow` — cascading None propagation
3. `log_and_swallow` — false safety (logged ≠ handled)
4. `broad_exception_catch` — highest volume, lowest risk-per-instance

---

## Wave Structure

| Wave | Focus | Count | Micro-Waves | Risk | Checkpoint |
|---|---|---|---|---|---|
| W1 | silent_exception_swallow | 228 | 3 micro-waves | HIGHEST — invisible failures | ADG green, ratchet ≤1651 |
| W2 | return_none_swallow | 159 | 2 micro-waves | HIGH — cascading None | ADG green, ratchet ≤1492 |
| W3 | log_and_swallow | 450 | 4 micro-waves | MEDIUM-HIGH — false safety | ADG green, ratchet ≤1042 |
| W4 | broad_exception_catch | 1,042 | 6 micro-waves | MEDIUM — widest net | ADG green, ratchet = 0 |

**Each micro-wave**: ~50-80 instances, scoped to 1-2 layers, full test pass before next.

---

## Wave 1 — silent_exception_swallow (228 instances, 94% prod)

**Why first**: Errors that vanish without any trace are the most dangerous. You cannot debug what you cannot see. Every one of these is a potential silent data corruption or missed failure.

**Fix pattern**: Replace bare `except: pass` / `except Exception: pass` with either:
- (a) Explicit narrow exception + re-raise or return error metadata
- (b) Logging + re-raise (promote to log_and_swallow is an intermediate step, then fix in W3)
- (c) Remove the try/except if the operation should fail-fast

### Micro-Wave 1.1 — Core layers (L0-L3)
- **Scope**: silent_exception_swallow in L0_routing, L1_cognition, L2_execution, L3_orchestration
- **Estimated count**: ~40-60 (highest architectural risk)
- **Acceptance**: All scoped tests green, ADG ratchet drops, no new P1
- **Rollback**: `git stash` per micro-wave; no cross-file dependency

### Micro-Wave 1.2 — Shared + system_learning (L_SHARED, L_SL)
- **Scope**: silent_exception_swallow in apps_shared/, system_learning/
- **Estimated count**: ~80-100
- **Acceptance**: All scoped tests green, integration tests pass

### Micro-Wave 1.3 — Remaining prod layers (L4-L6, L_PG, L_RUNTIME)
- **Scope**: silent_exception_swallow in remaining production layers
- **Estimated count**: ~70-90
- **Acceptance**: Full test suite green, ADG ratchet at ≤1651

### W1 Checkpoint
- [ ] ADG generation passes
- [ ] P2 ratchet ceiling auto-lowered to ≤1651 (1879 - 228)
- [ ] No new P1 violations introduced
- [ ] All existing tests pass

---

## Wave 2 — return_none_swallow (159 instances, 94% prod)

**Why second**: Each one is a None bomb — the caller gets a None where it expected real data, causing `AttributeError`/`TypeError` far from the source. These are the #1 cause of "impossible" production bugs.

**Fix pattern**: Replace `except: return None` with:
- (a) Raise the exception (fail-fast, caller must handle)
- (b) Return a typed sentinel/error object instead of None
- (c) Return a default value with logging (only if semantically safe)

### Micro-Wave 2.1 — Core + shared layers (L0-L3, L_SHARED)
- **Scope**: return_none_swallow in core architecture + shared
- **Estimated count**: ~80-90
- **Acceptance**: Scoped tests green, no new None-related test failures

### Micro-Wave 2.2 — Remaining prod layers
- **Scope**: return_none_swallow in L4-L6, L_SL, L_PG, L_RUNTIME
- **Estimated count**: ~70-80
- **Acceptance**: Full test suite green, ADG ratchet at ≤1492

### W2 Checkpoint
- [ ] ADG generation passes
- [ ] P2 ratchet ceiling auto-lowered to ≤1492 (1651 - 159)
- [ ] No new None-related failures in test suite
- [ ] Integration tests pass (None propagation is cross-module)

---

## Wave 3 — log_and_swallow (450 instances, 96% prod)

**Why third**: These look safe because they log. But logging an error and then dropping it means the caller has no idea the operation failed. The error is acknowledged but not handled — a false sense of safety.

**Fix pattern**: Replace `except: logger.error(...); pass` with:
- (a) Log + re-raise (let caller decide)
- (b) Log + return error metadata (structured error response)
- (c) Log + raise a domain-specific exception

### Micro-Wave 3.1 — L_SHARED (highest concentration)
- **Scope**: log_and_swallow in apps_shared/
- **Estimated count**: ~100-120
- **Acceptance**: Scoped tests green

### Micro-Wave 3.2 — Core layers (L0-L3)
- **Scope**: log_and_swallow in L0-L3
- **Estimated count**: ~80-100
- **Acceptance**: Core routing + cognition tests green

### Micro-Wave 3.3 — system_learning (L_SL)
- **Scope**: log_and_swallow in system_learning/
- **Estimated count**: ~100-120
- **Acceptance**: ML pipeline tests green

### Micro-Wave 3.4 — Remaining prod (L4-L6, L_PG, L_RUNTIME)
- **Scope**: log_and_swallow in remaining production layers
- **Estimated count**: ~100-120
- **Acceptance**: Full test suite green, ADG ratchet at ≤1042

### W3 Checkpoint
- [ ] ADG generation passes
- [ ] P2 ratchet ceiling auto-lowered to ≤1042 (1492 - 450)
- [ ] Caller-side error handling validated (not just logging)
- [ ] No silent failures in integration tests

---

## Wave 4 — broad_exception_catch (1,042 instances, 90% prod)

**Why last**: Largest volume but lowest risk-per-instance. These catch `Exception` when they should catch a specific type. The code still runs — it just may mask a real error. This wave is the longest and most mechanical.

**Fix pattern**: Replace `except Exception` with:
- (a) Specific exception type(s) that the code actually handles
- (b) `except Exception` + re-raise after cleanup (if truly generic handler)
- (c) Remove try/except if the code should fail-fast

### Micro-Wave 4.1 — Top-10 hotspot files
- **Scope**: 10 files with highest broad_exception_catch count (~120 instances)
- **Estimated count**: ~120 (12% of P2 total)
- **Acceptance**: Hotspot files clean, scoped tests green
- **Rationale**: Maximize early ratchet drop with concentrated effort

### Micro-Wave 4.2 — L_SHARED layer
- **Scope**: broad_exception_catch in apps_shared/ (top layer for P2)
- **Estimated count**: ~150-180
- **Acceptance**: Shared layer tests green

### Micro-Wave 4.3 — L5_safety layer
- **Scope**: broad_exception_catch in L5 (second-highest count)
- **Estimated count**: ~140-160
- **Acceptance**: Safety layer tests green

### Micro-Wave 4.4 — L1-L3 core
- **Scope**: broad_exception_catch in L1_cognition, L2_execution, L3_orchestration
- **Estimated count**: ~200-220
- **Acceptance**: Core layer tests green

### Micro-Wave 4.5 — system_learning + L4
- **Scope**: broad_exception_catch in system_learning/, L4
- **Estimated count**: ~180-200
- **Acceptance**: ML + L4 tests green

### Micro-Wave 4.6 — Remaining (L0, L6, L_PG, L_RUNTIME, non-prod)
- **Scope**: All remaining broad_exception_catch instances
- **Estimated count**: ~150-180
- **Acceptance**: Full test suite green, P2 ratchet = 0

### W4 Checkpoint
- [ ] ADG generation passes
- [ ] P2 ratchet ceiling = 0
- [ ] No `except Exception` without specific justification + guardian comment
- [ ] Full test suite green

---

## Rules

1. **One micro-wave = one commit.** Rollback unit is the micro-wave, not the wave.
2. **ADG must pass between micro-waves.** If ADG shows P2 increase → stop, debug, fix before next micro-wave.
3. **Ratchet auto-lowers.** Each successful ADG run after a micro-wave lowers the ceiling. This is the progress signal.
4. **No weakening tests.** If a test fails after a fix, the fix is wrong — not the test.
5. **Narrow exceptions first.** When replacing `except Exception`, identify the 1-2 specific exceptions that actually occur. Use ADG edge data + grep to find what exceptions are raised.
6. **Guardian exemptions require HITL.** If a `broad_exception_catch` genuinely needs to stay broad (e.g., top-level error boundary), add `# guardian: allow-broad-exception -- <specific justification>` with HITL approval.
7. **No batch find-and-replace.** Each fix must consider the context: what exception types are possible, what the caller expects, what side-effects occur before the try block.

---

## Derisking Strategy

| Risk | Mitigation |
|---|---|
| Fix breaks caller assumptions | Micro-wave scope = 1-2 layers; scoped tests before full suite |
| Narrowing exception type misses a case | Run integration tests after each micro-wave; monitor CI for 48h |
| Volume overwhelm (1,042 in W4) | W4 split into 6 micro-waves of ~150-180 each |
| Guardian exemption sprawl | HITL gate on every new guardian comment; ratchet tracks total |
| Re-raise changes control flow | Review each try/except for finally blocks and cleanup logic |
| Test suite doesn't cover the path | Add regression test for each fix pattern (test the exception path) |

---

## Progress Tracking

After each micro-wave, ADG defect table provides the scoreboard:

| Milestone | P2 Count | P2 Ratchet | Status |
|---|---|---|---|
| Baseline | 1,879 | 1,879 | Current |
| W1 complete | ≤1,651 | auto-lowered | silent_exception_swallow = 0 |
| W2 complete | ≤1,492 | auto-lowered | return_none_swallow = 0 |
| W3 complete | ≤1,042 | auto-lowered | log_and_swallow = 0 |
| W4 complete | 0 | 0 | **P2 clean** |

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| P2 count | 0 | ADG defect table |
| P2 ratchet | 0/0 | ADG ratchet output |
| P1 violations | 0 | ADG P1 gate |
| Test suite | 100% pass | `pytest tests/` |
| Guardian exemptions | Minimal, HITL-approved | `guardian_exemption_gate.py` |
| ADG generation | Passes clean | `python tools/generate_full_adg.py` |

---

## Rollback Strategy

1. Each micro-wave is a single git commit → `git revert <commit>` rolls back one micro-wave
2. P2 ratchet ceiling auto-adjusts up if count increases (but ADG blocks, so this shouldn't happen)
3. If a wave introduces unexpected failures: revert the wave, re-run ADG, verify ratchet restored
4. Worst case: `git reset --hard` to pre-wave baseline commit
