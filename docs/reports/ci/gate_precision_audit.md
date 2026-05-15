# Post-ADG Gate Precision Audit — W4 P4.5

**Plan**: `.windsurf/plans/adg-three-bucket-unified-c4f8e2.md` (W4 P4.5)
**Date**: 2026-04-30
**Auditor**: Cursor Agent (in-process negative-test harness)
**Harness**: `tests/unit/ops_scripts/ci/test_gate_precision_audit.py` (13 tests)
**Fixtures**: `tests/fixtures/negative/`

## Executive summary

| # | Gate | Verdict | Precise | Hollow gap | P4.6 action |
|---|------|:-------:|:-------:|:----------:|:------------|
| 1 | `check_expected_wiring` | **PRECISE** | ✅ | — | No rewrite required |
| 2 | `check_config_references` | **PRECISE** | ✅ | — | No rewrite required |
| 3 | `check_lifecycle_pairs` | **PRECISE** | ✅ | — | Eligible for graph-layer port (advisory; not hollow) |
| 4 | `check_exception_contract` | **PARTIAL** | ⚠️ | Symbol-mismatch blind spot | **Call-chain resolution or retarget to public entry in contract spec** |
| 5 | `check_test_harness_coverage` | **PRECISE** | ✅ | — | Eligible for graph-layer port (advisory; not hollow) |

**Headline finding**: 4 of 5 gates are functionally precise. The single partial
result is `check_exception_contract`, whose symbol-matching algorithm cannot
follow call chains. This was discovered and fixed per-contract during W4 P4.4
(raiser_symbol retargeted from private internal → public entry for the two
warn-severity contracts). The systemic fix — teach the gate to resolve
`get_instance() → _create_instance() → _initialize()` call chains — remains
scheduled for W4 P4.6.

## Methodology

Each gate's core violation-detection function is called **in-process** with
a synthetic known-bad fixture. The harness asserts the gate correctly
distinguishes bad input from good. This approach deliberately isolates the
**checking algorithm** from CLI/config wiring — the latter is covered by
separate tests and by the gates' own `main()` smoke paths.

Fixtures live at `tests/fixtures/negative/` with a README explaining each
file's intentional defect. The harness at
`tests/unit/ops_scripts/ci/test_gate_precision_audit.py` has 13 tests: 2
per gate (one known-bad, one control) plus a known-hollow pin and a
summary printer.

## Per-gate findings

### 1. `check_expected_wiring` — PRECISE

**Checks**: yaml rows declaring `entry_module::entry_symbol` must call
`required_call` somewhere in their AST subtree.

**Known-bad fixtures**:

| Fixture | Expected behavior | Actual |
|---|---|:-:|
| Nonexistent `entry_module` (`agentic_core/L_NONEXISTENT/fake_module.py`) | returns non-empty error list | ✅ |
| Real module + real symbol + nonexistent `required_call` (`absolutely_never_called_p45_audit_only`) | returns non-empty error list | ✅ |

**Verdict**: Gate correctly detects both defect classes the contract enforces.
No rewrite required.

### 2. `check_config_references` — PRECISE

**Checks**: `os.getenv`, `os.environ.get`, `os.environ[]` calls with flag
names absent from `.env.example` + `config_references_allowlist.yaml`.

**Known-bad fixture**: `tests/fixtures/negative/config_refs/undeclared_flag_fixture.py`
declares all 3 patterns with deliberately-undeclared flag names.

| Pattern | Detected flag | Actual |
|---|---|:-:|
| `os.getenv("P45_FAKE_FLAG_DO_NOT_DECLARE", "...")` | ✅ yes | ✅ |
| `os.environ.get("P45_FAKE_FLAG_ENVIRON_GET", "...")` | ✅ yes | ✅ |
| `os.environ["P45_FAKE_FLAG_SUBSCRIPT"]` | ✅ yes | ✅ |

**Verdict**: All three read-pattern branches of the AST scanner correctly
return the flag name. Precise.

### 3. `check_lifecycle_pairs` — PRECISE

**Checks**: `opener` calls (e.g. `sqlite3.connect`) must be matched by a
declared closer (`.close()`, `with_stmt`, or `attr:self.<name>`) in the
enclosing function or class.

**Known-bad fixture**: `tests/fixtures/negative/lifecycle_pairs/unclosed_sqlite_fixture.py`
contains two helpers:

| Helper | Closer present? | Gate flags? | Correct? |
|---|:-:|:-:|:-:|
| `_leaking_connect_use` | ❌ none | ✅ flagged | ✅ |
| `_properly_closed_connect_use` | ✅ `with_stmt` | ❌ not flagged | ✅ |

**Verdict**: Gate correctly distinguishes leaks from properly-closed calls.
No false positives, no false negatives on the canonical pattern.

**Note**: Eligible for graph-layer port in P4.6 (could use `flows_to` +
`writes_to` semantic edges to trace connection lifecycle beyond single-function
scope), but the current AST-based implementation is correct for its declared
scope. Advisory upgrade, not a hollow-gate fix.

### 4. `check_exception_contract` — PARTIAL (systemic gap)

**Checks**: For each declared `raiser_symbol`, at least `require_n_handlers`
callers (resolved via ADG import-fan-in) must have an `except
<exception_class>` clause in the function that calls `raiser_symbol`.

**Known-bad fixtures**:

| Fixture | Expected | Actual | Verdict |
|---|---|---|:-:|
| Caller with no try/except, calls `raiser_symbol_fn` directly | NOT satisfied | NOT satisfied | ✅ PRECISE |
| Caller with `try: raiser_symbol_fn() except ValueError:` | SATISFIED | SATISFIED | ✅ PRECISE |
| Caller invokes public wrapper `public_wrapper()`; contract names private `_private_raiser` | **should** be SATISFIED (call chain) | **NOT satisfied** | ⚠️ HOLLOW (pinned) |

**Root cause**: `_caller_satisfies` walks the caller's AST looking for
`ast.Call` nodes whose trailing identifier matches `last_seg` (last segment
of `raiser_symbol`). It does **not** follow call chains — so when a contract
declares the raiser as a private helper that external callers never invoke
directly (they call a public wrapper which internally propagates the
exception), the gate's symbol matcher returns False for every caller and
reports 0/N handlers.

**Impact on real contracts** (measured during W4 P4.4):

| Contract id | Before P4.4 (symbol=private) | After P4.4 (symbol=public) |
|---|:-:|:-:|
| `semcache-initialize-critical-infra` | 0/10 (HOLLOW) | 5/10 (PASS) |
| `register-embedding-client-value-error` | 0/3 (HOLLOW) | 3/3 (PASS) |

**Remediation** — two paths:

1. **Per-contract** (done in P4.4): retarget `raiser_symbol` to the public
   entry that external callers invoke. Low-risk, fast, but depends on
   contract authors knowing their raiser's call chain.
2. **Systemic** (P4.6): teach `_caller_satisfies` to follow `calls` edges
   through one or two levels of indirection, OR ingest a transitive-exception-
   propagation relation during ADG build. Higher-value fix; unblocks
   contracts where the private → public mapping is non-obvious.

**Verdict**: **PARTIAL**. Gate is precise when the contract spec is correct.
It is **hollow** when the contract names a private raiser — but this failure
mode is now DISCOVERABLE via the P4.4 `raiser_symbol` sanity check (callers
found vs ADG import-fan-in report).

### 5. `check_test_harness_coverage` — PRECISE

**Checks**: Production modules (under declared globs) not imported by any
`tests/` or `*/tests/*` file are flagged as uncovered (modulo baseline +
allowlist).

**Known-bad fixtures** (synthetic ADG snapshots):

| Scenario | Expected | Actual |
|---|---|:-:|
| Module imported from `tests/unit/...` | appears in `covered_set` | ✅ |
| Module imported only by `agentic_core/...` (prod-only) | NOT in `covered_set` | ✅ |
| Module imported from nested `apps_*/tests/...` | appears in `covered_set` | ✅ |

**Verdict**: SQL query `src.resolved_path LIKE 'tests/%' OR src.resolved_path
LIKE '%/tests/%'` correctly captures both top-level and nested test
directories. Path-to-repo-relative conversion works correctly when ADG
nodes store repo-relative POSIX paths (the production format).

## Cross-gate observations

### The symbol-resolution blind spot is systemic

The `check_exception_contract` gap is a specific instance of a broader
pattern: gates that resolve "caller" by walking ADG import-fan-in AND then
filtering by AST call-name are blind to any indirection. The same risk
applies — in principle — to `check_expected_wiring`, though the audit found
no current contract triggers it.

**Recommendation for P4.6**: when rewriting gates on graph-layer primitives,
use `resolves_callsite` semantic edges (from the graph-layer surface exposed
in W3 P3.3) instead of ad-hoc AST symbol matching. The ADG already knows
which call sites resolve to which target symbols — including through
indirection.

### Baseline ratchets are working correctly

`check_lifecycle_pairs` and `check_test_harness_coverage` both use a
frozen-debt baseline at `ops_scripts/ci/baselines/*.json`. The audit
confirmed the ratchet math (new violations only) is correct by inspection;
no synthetic ratchet test was needed because the baseline mechanism is
standard JSON diffing.

### No gate produces silent false negatives with correct contracts

For all 5 gates tested, when the contract/fixture pair is well-formed, the
gate detects the intended violation. The `check_exception_contract` hollow
case is **contract-spec-driven**: the gate does what its spec says, but the
spec's symbol name can be wrong. This is different from — and less severe
than — a gate whose algorithm fails on correct input.

## Follow-ups

| Follow-up | Target | Blocking? |
|---|---|:-:|
| Teach `_caller_satisfies` to follow 1-2 levels of call-chain indirection | P4.6 | No — per-contract workaround exists |
| Port `check_lifecycle_pairs` to `flows_to` + `writes_to` semantic edges | P4.6 | No — current impl is precise |
| Port `check_test_harness_coverage` to `mv_dependency_cone_risk` for blast-radius-aware prioritization | P4.6 | No — current impl is precise |
| Add `raiser_symbol` sanity check to contract gate: warn if N(callers via ADG) ≥ 3 but N(satisfying via AST) == 0 | P4.6 or separate | No — advisory signal |

## Appendix: test commands

```bash
# Run the full audit harness
python -m pytest tests/unit/ops_scripts/ci/test_gate_precision_audit.py -v

# Print the summary only
python -m pytest tests/unit/ops_scripts/ci/test_gate_precision_audit.py -v -k summary -s

# Regenerate this report after any gate-logic change
# (manual — no automated rebuild; audit findings require human interpretation)
```
