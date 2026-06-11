---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-anomaly-scan-report-a1f3b9.md'
original_relative_path: 'adg-anomaly-scan-report-a1f3b9.md'
source_sha256: 395c8d60827468abc8ee39089a6bcc5baeff76d0f87bb264fcc3f1d7092cd944
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Anomaly Scan Report v2 — Full Reingest
**Generated:** 2026-03-14
**ADG Build Timestamp:** 03142026_0512
**SQLite:** `artifacts/adg/adg_indexed_03142026_0512.sqlite`
**Redis:** localhost:6379 DB-0 — HOT (confirmed via `adg:meta`)
**Mode:** READ-ONLY discovery. Zero mutations performed.
**Version note:** v2 replaces v1. Previous report had 4 false negatives (A-02, A-04, new A-05 violates edge, systemic gating gaps) and one false positive (previous A-08). All findings here are evidence-first from direct Redis + SQLite extraction.

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


## Redis Hot Cache Verification

| Field | Value |
|-------|-------|
| `adg:meta.timestamp` | 03142026_0512 |
| `adg:meta.node_count` | 8,229 modules |
| `adg:meta.total_entities` | 65,742 |
| `adg:meta.total_relations` | 224,975 |
| `adg:violations` LIST | **0 entries** (pre-aggregated violation list empty) |
| `adg:drift:*` keys | **0 keys** (drift score TTL expired) |

### Layer Population
```
L0=366  L1=103  L2=310  L3=204  L4=142  L5=608  L6=47
L_APP=1324  L_OPS=420  L_SHARED=371  L_TOOLS=420
L_RUNTIME=154  L_SL=264  L_PG=84  L_TEST=3,341
Prod total: 4,830 modules
```

### Full Edge Type Census (complete — no sampling)
```
reads_from          66,680    writes_to            4,882
imports             48,777    dead_imports          4,401
reads_from          36,449    reads_env               819
calls               18,504    uses_wall_clock         884
decorated_by        16,764    reads_policy_state    1,317
covers               7,859    dispatches_healing_run   71
writes_to (w/ sub)   4,882    orchestrates_healing     75
antipattern          1,531    execution_terminates_at_uwg 44
reads_runtime_state    459    gated_by_confidence       29
accesses_credential    361    guards_replay             28
validated_by_safety_plane 18  validated_by_registry      3
violates                 5    heals                      2
```

---

## Anomaly Summary Table

| ID | Sev | Bucket | File(s) | ADG Evidence |
|----|-----|--------|---------|-------------|
| **A-01** | **P0** | Mutation boundary | `validators/GovernanceAgent.py` | 11 writes_to: mkdir (529,843), safe_move (552), hierarchy_agent.run (862), import_agent.run (894), open/f.write (178,327,604,683,714) |
| **A-02** | **P0** | Mutation boundary | `validators/PascalSovereigntyAgent.py` | 11 writes_to: src.rename (454,481), temp.rename (492,499), temp_path.rename (520), file_path.rename (666,686), path.write_text (335), open (652), agent.run (824) |
| **A-03** | **P0** | Mutation boundary | `validators/dependencygraph_validator.py` | UWG import confirmed; 7 writes_to: _wg.makedirs (228), _wg.open_write (229,303), open (91,197,218,317) |
| **A-04** | **P0** | Mutation boundary | `validators/CodeJanitorAgent.py` | 7 writes_to: open×6 (73,94,128,168,215,228), f.write (229); reads_env (197) |
| **A-05** | **P1** | Mutation boundary | `validators/report_location_validator.py`, `validators/structure_drift_validator.py` | UWG import confirmed (ADG symbol `agentic_core.L2_execution.tools.write_gateway`); structure_drift: writes_to open (75) |
| **A-06** | **P1** | Layer boundary | 5 files | 5 ADG `violates` edges — see detail below |
| **A-07** | **P1** | Role classification | `reasoning/GovernanceAgent.py` + `validators/GovernanceAgent.py` | 2 modules both defining class `GovernanceAgent`; reasoning: 8 writes_to, validators: 11 writes_to |
| **A-08** | **P1** | Mutation boundary | `reasoning/StructuralValidatorAgent.py` | 2 writes_to: os.fdopen (218), tf.write (219) — temp file write inside validator |
| **A-09** | **P1** | Systemic: replay gating | L5 healing path | **0** `guards_replay` edges in ALL L5 prod; LocationHealerAgent: 7 uses_wall_clock + 6 reads_env; root_hygiene_healer: 2 uses_wall_clock; hierarchy_healer: 1 uses_wall_clock |
| **A-10** | **P1** | Script complexity | `L0/scripts/execute_ssot.py` | 43 writes_to + 21 reads_env + 16 reads_runtime_state + 13 accesses_credential + 10 uses_wall_clock + 43 antipattern + 1 orchestrates_healing; fan-out hotspot #2 (1,010 outbound edges) |
| **A-11** | **P2** | Systemic: confidence gating | All prod L0–L5 healing agents | **0** `gated_by_confidence` edges in prod L0–L5; only L_SL/pipeline_factory.py (4 edges); 25 test edges only |
| **A-12** | **P2** | Mutation boundary | `validators/global_mutation_validator.py`, `validators/path_fragility_validator.py` | self._check_call (lines 75, 90): subprocess spawn from validators/ territory |
| **A-13** | **P2** | Validator-healer split | `reasoning/GravityLeakHealerAgent.py` | No `GravityLeakValidatorAgent`; `gravity_validator.py` covers general gravity, not leak-domain |
| **A-14** | **P2** | Mutation boundary | `reasoning/CodeValidatorAgent.py` | 4 writes_to via `open` (147,179,230,282) — ADG cannot determine open mode; "Validator" name |
| ~~A-15~~ | ~~STRUCK~~ | ~~False positive~~ | ~~Four validator-only domains (gravity, file_classification, filesystem_ssot, arch_governor)~~ | ~~All 4 have L2 healers in HEALER_REGISTRY. L5→L2 two-tier architecture by design.~~ |
| ~~A-16~~ | ~~STRUCK~~ | ~~False positive~~ | ~~reasoning/file_classification_validator.py (3 writes_to)~~ | ~~classifier.run() called with validate_only=True; ADG cannot resolve flag state~~ |

---

## Phase 1 — Evidence Census

### Redis Hot Cache Stats
- **Total Redis keys:** confirmed hot (DB-0)
- **Edge relation count confirmed:** 85 distinct relation types, 224,975 total edges
- **Anomaly signals in graph:** `violates`=5, `antipattern`=1,531, `dead_imports`=4,401

### Antipattern Distribution (top signals)
```
for_retry:       L0=1813, L5=1132, L_APP=698, L_OPS=219, L3=190, L_SHARED=131, L2=118
except:bare:     L0=835,  L5=309,  L2=52,     L4=43,     L_APP=76, L_OPS=42
except:Exception:L5=168,  L_APP=101, L_SL=77
CURRENT_PHASE:   L0=56  (global mutable state antipattern)
_RG_SPECS_CACHE: L_APP=65  (module-level cache antipattern)
```

### Validated_by_registry Coverage (only 3 total)
- `L0/enforcement/boot_sequence.py` (AgentRegistry, line 37)
- `apps_shared/types/AgentRole.py` (AgentRegistry, line 318)
- `apps_shared/utils/agent_interface_util.py` (AgentRegistry, line 307)

**No healer, validator, or orchestrator validates itself via registry.** Registry validation is limited to agent role/boot infrastructure only.

### guards_replay Coverage
- **Prod:** `L1/enforcement/react_strategy.py` (4 edges), `L_TOOLS/adg/runtime/determinism_control.py` (10 edges)
- **L5 prod:** **0 edges**
- **L2 healers prod:** **0 edges**
- Conclusion: the healing execution path at L5/L2 has no ADG-confirmed replay guard.

---

## Phase 2 — Mutation Boundary Violations (validators/ Territory)

**Contract:** All files in `L5_safety/validators/` MUST be certify-only. Zero writes_to, zero UWG imports, zero subprocess mutations.

**Actual — writes_to census from ADG (prod files only):**
```
n=11  validators/GovernanceAgent.py
n=11  validators/PascalSovereigntyAgent.py
n= 7  validators/dependencygraph_validator.py
n= 7  validators/CodeJanitorAgent.py
n= 1  validators/utility_silent_swallower_validator.py
n= 1  validators/structure_drift_validator.py
n= 1  validators/path_fragility_validator.py
n= 1  validators/intelligence_query_validator.py
n= 1  validators/global_mutation_validator.py
```
**9 out of N files in validators/ have writes_to edges.** Violated: 100% of surveyed mutation-capable files are misplaced.

---

### [A-01] `validators/GovernanceAgent.py` — Full Healer in validators/ Territory
**Severity: P0**

**Evidence (ADG writes_to edges):**
| Line | Symbol | Type |
|------|--------|------|
| 178 | `open` | file open |
| 327 | `open` | file open |
| 328 | `f.write` | file write |
| 529 | `scripts_dir.mkdir` | directory creation |
| 552 | `self.gatekeeper.safe_move` | file move |
| 604 | `open` | file open |
| 683 | `open` | file open |
| 714 | `open` | file open |
| 843 | `self._backup_dir.mkdir` | directory creation |
| 862 | `self.hierarchy_agent.run` | delegates to sub-agent (healer) |
| 894 | `self.import_agent.run` | delegates to sub-agent (healer) |

This is not a validator with minor side-effects — it creates directories, moves files, writes files, and orchestrates sub-healer runs. The territory contract for `validators/` is pure read/certify only.

**Previous report classification:** P2 (under-severity). **Correct severity: P0.**

**Fix:**
1. Move authoritative copy to `reasoning/` (or keep the existing `reasoning/GovernanceAgent.py` as canonical)
2. Create a thin `validators/GovernanceValidatorAgent.py` that delegates to the certify-only `validate()` path only, no writes
3. Remove `validators/GovernanceAgent.py`

**Verification:** ADG re-scan of `validators/GovernanceAgent.py` → zero `writes_to` edges

---

### [A-02] `validators/PascalSovereigntyAgent.py` — File Renamer in validators/ Territory
**Severity: P0**

**Evidence (ADG writes_to edges):**
| Line | Symbol | Type |
|------|--------|------|
| 152 | `self.resolve_collision_and_rename` | rename dispatch |
| 335 | `path.write_text` | file write |
| 454 | `src.rename` | file rename |
| 481 | `src.rename` | file rename |
| 492 | `temp.rename` | file rename |
| 499 | `temp.rename` | file rename |
| 520 | `temp_path.rename` | file rename |
| 652 | `open` | file open |
| 666 | `file_path.rename` | file rename |
| 686 | `file_path.rename` | file rename |
| 824 | `agent.run` | delegates to sub-agent |

Also: `reads_env` at line 132 (`self.verify_environment`).

This agent renames production files from within `validators/`. File renames are irreversible filesystem mutations. This is a healer, not a validator, misplaced in the wrong territory.

**Fix:**
1. Move to `reasoning/PascalSovereigntyHealerAgent.py`
2. Create `validators/PascalSovereigntyValidatorAgent.py` (scan-only, no renames)
3. Wire new validator to HEALER_REGISTRY via its `check_id`

---

### [A-03] `validators/dependencygraph_validator.py` — Direct UWG Access from validators/
**Severity: P0**

**Evidence:**
- ADG `imports` edge: `agentic_core.L2_execution.tools.write_gateway` (confirmed via SQLite)
- `writes_to` edges: `_wg.makedirs` (line 228), `_wg.open_write` (lines 229, 303), `open` (91, 197, 218, 317)
- `reads_env`: 4 edges

The `validators/` contract prohibits UWG imports. This file bypasses the registry-based dispatch pattern by calling UWG directly, circumventing replay_mode and the mutation ledger for those operations.

**Fix:**
1. Strip all `_wg.*` calls from this module
2. If write operations are needed, this is a healer — move mutation logic to `L2_execution/healers/dependencygraph_healer.py`
3. Keep only read/certify logic in `validators/dependencygraph_validator.py`

---

### [A-04] `validators/CodeJanitorAgent.py` — File Writer in validators/
**Severity: P0**

**Evidence:**
- `writes_to`: `open` (lines 73, 94, 128, 168, 215, 228), `f.write` (line 229)
- `reads_env`: `os.getenv` (line 197)

Writes files from `validators/` territory. Name uses "Agent" suffix not "Validator", suggesting mis-classification at creation time.

**Fix:**
1. Identify which `open()` calls are read vs write — split into read-only scan path and mutation path
2. Mutation path → create `L2_execution/healers/code_janitor_healer.py`
3. Rename remaining read-only file to `validators/code_janitor_validator.py`

---

### [A-05] `validators/report_location_validator.py` + `validators/structure_drift_validator.py` — UWG Imports
**Severity: P1**

**Evidence (ADG `imports` edges, symbol-level):**
- `report_location_validator.py` → `agentic_core.L2_execution.tools.write_gateway`
- `structure_drift_validator.py` → `agentic_core.L2_execution.tools.write_gateway`
- `structure_drift_validator.py`: `writes_to` `open` (line 75)

UWG is present as an import even if calls are currently gated — having the import in a `validators/` file means a single un-gated call site away from a contract violation. Import hygiene must be enforced at the territory level.

**Fix:**
1. Remove UWG imports from both files
2. If report writing is needed → extract to `L2_execution/healers/`

---

### [A-08] `reasoning/StructuralValidatorAgent.py` — Temp File Write Inside Validator
**Severity: P1**

**Evidence:**
- `writes_to`: `os.fdopen` (line 218), `tf.write` (line 219) — tempfile creation and write

While temp files are not persistent, creating and writing temp files inside a validator breaks the pure read guarantee. Validators MUST be side-effect free even transiently, to support safe concurrent scan execution.

**Fix:** Use in-memory buffer (`io.StringIO`) instead of `tempfile.NamedTemporaryFile` for any AST/syntax analysis that currently requires a file handle.

---

### [A-12] `validators/global_mutation_validator.py` + `validators/path_fragility_validator.py` — Subprocess Spawn
**Severity: P2**

**Evidence:**
- `global_mutation_validator.py`: `writes_to` → `self._check_call` (line 75)
- `path_fragility_validator.py`: `writes_to` → `self._check_call` (line 90)

ADG classifies `_check_call` as `writes_to` because subprocess execution can mutate external state. These validators may only be running read-only introspection subprocesses — but subprocess execution from a `validators/` file requires explicit justification (e.g., `# guardian: allow-subprocess-introspection`).

**Fix:** Verify subprocess is read-only (e.g., `git diff --name-only`). If read-only: add guardian allowlist comment. If mutating: extract to healer.

---

## Phase 3 — Layer Boundary Violations (all 5 violates edges)

### [A-06] Five ADG `violates` Edges
**Severity: P1**

**Complete list (none were pre-aggregated in `adg:violations`):**

| Source | Direction | Line | Target Layer |
|--------|-----------|------|-------------|
| `L0/artifacts/deterministic_routing_gateway.py` | L0 → L_RUNTIME | 24 | L_RUNTIME symbol |
| `L0/policy/route_policy_governor.py` | L0 → L_RUNTIME | 27 | L_RUNTIME symbol |
| `L0/scripts/_ssot_reporting.py` | L0 → L2 | 13 | L2 healing config constant |
| `L0/scripts/_ssot_routing.py` | L0 → L2 | 16 | L2 healing config constant |
| **`L2/determinism/execution_proof_emitter.py`** | **L2 → L_RUNTIME** | **24** | **L_RUNTIME symbol** |

**Note:** The 5th edge (`execution_proof_emitter.py`) was NOT present in the previous report. It was missed because the previous scan only checked L0 modules. The ADG `violates` edge from L2 to L_RUNTIME is equally invalid — L2 must not import L_RUNTIME symbols.

**Fix per violation:**
1. `deterministic_routing_gateway.py` + `route_policy_governor.py` → Extract the specific L_RUNTIME constants into an L0-accessible `L0_routing/config/runtime_seam_constants.py`; inject via constructor
2. `_ssot_reporting.py` + `_ssot_routing.py` → Extract the L2 healing constants they need into an `L0_routing/config/` module; remove direct L2 import
3. `execution_proof_emitter.py` → Extract L_RUNTIME type used at line 24 into a shared type module at `L2_execution/types/` or `apps_shared/`

**Verification:** Post-fix ADG re-ingest → zero `violates` edges

---

## Phase 4 — Role Classification Failures

### [A-07] `GovernanceAgent` Duplicated in Two Territories
**Severity: P1**

**Evidence:**
- `agentic_core/L5_safety/reasoning/GovernanceAgent.py` — 8 writes_to edges
- `agentic_core/L5_safety/validators/GovernanceAgent.py` — 11 writes_to edges
- Both modules define a class named `GovernanceAgent`
- Both have `heal()` methods

**Additional finding:** BOTH copies perform mutations. Neither is a pure validator. The `validators/` copy has MORE writes_to edges than the `reasoning/` copy. This means the `validators/` copy was likely diverged from `reasoning/` and gained additional mutation responsibilities over time.

**Fix (dependency-ordered):**
1. Determine canonical authoritative copy (likely `reasoning/` given layer semantics)
2. Diff the two files — identify whether `validators/` copy has unique logic
3. Merge unique logic into `reasoning/GovernanceAgent.py`
4. Delete `validators/GovernanceAgent.py`
5. Create `validators/GovernanceValidatorAgent.py` — pure read-only delegation stub
6. Update all importers

---

### [A-13] `GravityLeakHealerAgent` — No Certify-Only Validator Pair
**Severity: P2**

**Evidence:**
- `reasoning/GravityLeakHealerAgent.py` — healer confirmed (writes via `_wg`, implements `heal_violations()`)
- `reasoning/gravity_validator.py` — validates general layer gravity violations via `StructuralValidatorAgent`
- No `GravityLeakValidatorAgent` or `gravity_leak_validator.py` exists
- The domains are distinct: `gravity_validator.py` detects layer inversion imports; `GravityLeakHealerAgent` heals gravity-leak-specific patterns (different detection kernel in `gravity_leak_config.py`)

**Fix:**
1. Create `reasoning/gravity_leak_validator.py` with `GravityLeakValidatorAgent` (certify-only)
2. Delegate to `GravityLeakDetector.scan()` with `dry_run=True`
3. Emit `check_dict` with `check_id = "gravity_leak"` for HEALER_REGISTRY dispatch

---

### [A-14] `reasoning/CodeValidatorAgent.py` — "Validator" Name with 4 writes_to
**Severity: P2**

**Evidence:**
- `writes_to`: `open` at lines 147, 179, 230, 282 — ADG cannot determine `'r'` vs `'w'` mode
- Located in `reasoning/` (not `validators/`), so territory contract is not violated
- However: the "Validator" name suffix signals read-only contract to callers

**Risk:** If any `open()` call is write-mode, this is a mutation boundary violation with misleading naming. Requires live AST read to confirm.

**Fix (pending AST verification):**
- If all `open()` calls are read-mode: add `# validator: read-only open` guardian comment per call site
- If any are write-mode: rename to `CodeValidatorHealerAgent.py` or split into validator+healer

---

## Phase 5 — Systemic Gating Gaps

### [A-09] L5 Healing Path — Zero `guards_replay` Edges (Systemic)
**Severity: P1**

**Evidence:**
```
guards_replay edges in L5 prod:        0
guards_replay edges in L2 healers:     0
guards_replay edges in prod total:    14  (only react_strategy.py + determinism_control.py)
```

**Concrete non-determinism in healers (confirmed uses_wall_clock):**
| File | uses_wall_clock | reads_env |
|------|----------------|-----------|
| `L5/reasoning/LocationHealerAgent.py` | 7 | 6 |
| `L5/reasoning/root_hygiene_healer.py` | 2 | 0 |
| `L5/reasoning/hierarchy_healer.py` | 1 | 0 |
| `L2/healers/qwen_circuit_breaker.py` | 2 | 0 |
| `L2/healers/vllm_process_manager.py` | 2 | 0 |
| `L2/healers/healing_tier_config.py` | 0 | 2 |

**Impact:** Running the healing pipeline twice with the same input will produce different backup directory names/timestamps. Any replay or determinism verification of a healing run will fail because wall clock values change between runs.

**Fix:**
1. Inject a `HealingClock` abstraction (injectable mock in tests, `time.time` in prod) into all L5 healers
2. Add `guards_replay` edge signal to `LocationHealerAgent`, `root_hygiene_healer`, `hierarchy_healer` via `ReplayGuard` wrapper
3. Alternatively: ensure all timestamp generation in healing path uses UWG's replay hash as seed

---

### [A-11] Confidence Gating — Zero Prod Healing Agents Gate by Confidence (Systemic)
**Severity: P2**

**Evidence:**
```
gated_by_confidence edges (prod L0–L5): 0
gated_by_confidence edges (L_SL):       4  (pipeline_factory.py only)
gated_by_confidence edges (L_TEST):    25  (tests only)
```

`HealingConfidenceScorer` exists and is tested, but **no prod healing agent uses it** to gate dispatch decisions. `healing_tier_router.py` does compute scores internally — but the `gated_by_confidence` ADG edge is emitted when a caller checks the score before proceeding. Zero prod callers do this check at the call site.

**Impact:** Healing tier selection (`LOCAL_AGENT`, `QWEN_VLLM`, `GEMINI_2_5_PRO`) proceeds regardless of confidence score. Low-confidence healing operations are not blocked or escalated.

**Fix:**
1. In `remediation_dispatcher.py` — before dispatching to a tier-2/tier-3 healer, check `HealingConfidenceScorer.score()` and gate on minimum threshold
2. Add `gated_by_confidence` edge in ADG scanner for this call site

---

## Phase 6 — Script Complexity Anomaly

### [A-10] `execute_ssot.py` — Hyper-Connected L0 Entry Point
**Severity: P1**

**Evidence (complete edge census for this file):**
```
reads_from              374    (highest in file)
imports                 203    (fan-out hotspot #2 in entire repo: 1,010 total outbound)
calls                   100
invokes_getattr_dynamic  65
exports                  59
antipattern              43    (for_retry, except:bare, except:OSError, etc.)
writes_to                43    (direct filesystem mutations)
reads_env                21    (non-deterministic env reads)
reads_runtime_state      16
invokes_dynamic          15
accesses_credential      13    (13 distinct credential accesses)
uses_wall_clock          10
reads_policy_state        8
orchestrates_healing      1    (healing orchestration)
execution_terminates_at_uwg 1
```

This is the most complex non-test file in the codebase after `sovereign_severity_types.py` (type registry). It combines:
- Direct writes (43) — mutations
- Credential access (13) — security surface
- Wall clock (10) — replay non-determinism
- Healing orchestration (1) — dispatches healing
- Antipatterns (43) — retry loops, bare excepts

No single file should combine all these behaviors. The script has accumulated responsibilities beyond its L0 routing scope.

**Fix:**
1. Extract credential access into `L0_routing/config/credential_provider.py`
2. Extract healing orchestration call into `L0_routing/healing/ssot_heal_dispatcher.py`
3. Replace `writes_to` direct calls with UWG-gated writes where not already gated
4. Add `--dry-run` / `replay_mode` flag at `__main__` entry point
5. Enforce: `execute_ssot.py` should have zero `accesses_credential` edges (injected via config)

---

## Fix Dependency Order

```
1. A-07 (GovernanceAgent dedup) — blocks A-01 (validators/ cleanup)
2. A-01 → remove validators/GovernanceAgent.py (after A-07 dedup)
3. A-02 — standalone (PascalSovereigntyAgent territory move)
4. A-03 — standalone (dependencygraph_validator UWG strip)
5. A-04 — standalone (CodeJanitorAgent split)
6. A-05 — standalone (UWG import removal from 2 files)
7. A-06 (violates L0→L2) → requires extraction of constants to L0-accessible config
8. A-06 (violates L2→L_RUNTIME) → separate extraction, independent of L0 fixes
9. A-08 — standalone (StructuralValidatorAgent tempfile → in-memory)
10. A-09 — requires HealingClock abstraction before touching healer files
11. A-10 — decomposition, large change, do last
12. A-11 — add confidence gate to remediation_dispatcher.py (standalone)
13. A-12 — guardian comment audit (standalone, low risk)
14. A-13 — create gravity_leak_validator.py stub (standalone)
15. A-14 — pending AST verification of open() modes
```

---

## Verification Plan per Fix Batch

| Batch | Verification |
|-------|-------------|
| A-01, A-02, A-03, A-04, A-05 | Re-ingest ADG → zero `writes_to` from `validators/` prod (excluding tests). Zero UWG imports in `validators/`. |
| A-06 | Re-ingest ADG → zero `violates` edges |
| A-07 | Grep repo: zero duplicate `class GovernanceAgent` definitions |
| A-08 | Re-ingest ADG → `StructuralValidatorAgent.py` has zero `writes_to` |
| A-09 | `HealingClock` injection: replay test produces identical output on two runs with same seed |
| A-10 | Re-ingest ADG → `execute_ssot.py` `writes_to` < 10, `accesses_credential` = 0 |
| A-11 | Re-ingest ADG → `gated_by_confidence` edges in `remediation_dispatcher.py` > 0 |
| A-12 | Guardian comment audit passes for `_check_call` sites |
| A-13 | `gravity_leak_validator.py` exists; zero `write_gateway` imports; covers edge from test |
| A-14 | AST confirmation: all `open()` calls in `CodeValidatorAgent.py` use `'r'` mode |

---

## False Positives from v1 (Struck)

| Previous ID | Reason |
|-------------|--------|
| v1/A-08 — Four validator-only domains | All 4 have L2 healers in `HEALER_REGISTRY`. Architecture is two-tier by design: L5 validator emits check_dict → L2 healer via `remediation_dispatcher.py`. Confirmed via healer_registry_types.py. |
| v1/A-07 (GravityLeakHealerAgent) | Carried forward as A-13 (lower severity), same finding |
| file_classification_validator.py writes_to | 3 `writes_to` via `classifier.run()` with `validate_only=True` set beforehand; ADG cannot resolve conditional flag state. Low confidence — not promoted to anomaly. |

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

