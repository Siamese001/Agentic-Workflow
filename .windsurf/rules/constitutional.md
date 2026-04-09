---
trigger: always_on
---
# Agentic Workflow — Sovereign Architecture Rules (Constitutional)

> ⛔ **CONSTITUTIONAL FLOOR — READ FIRST**
> 0. **No PowerShell.** All commands via `subprocess.run(argv, shell=False)`. §3.2.
> 1. **No test skipping.** No `pytest.mark.skip`, no `xfail` without `strict=True`, no weakening assertions. §1.4.
> 2. **No editing while exploring.** All five repair gates (§8.1) must pass before any edit.
> 3. **No agent deletion without authorization.** Deleting *Agent.py files requires AGENT-DELETION-AUTHORIZED marker, justification, replacement, deprecation period (90 days), and zero references. §1.6.
> 4. **CI enforces all of this.** `python ops_scripts/ci/run_contract_gates.py`
> 5. **ADG ARTIFACTS MUST BE FULLY INGESTED BEFORE ANY QUERY OR REFACTORING.** The directory `artifacts/adg` contains the canonical ADG artifacts. ALL operating modes MUST ingest these before any query, analysis, or code change: (1) `adg_indexed_<timestamp>.sqlite` — PRIMARY queryable DB; (2) `adg_snapshot_<timestamp>.json` — metrics/counts; (3) `adg_file_graph_<timestamp>.json` + `adg_symbol_graph_<timestamp>.json` — import/call chains; (4) `adg_governance_graph_<timestamp>.json` — layer violations. NEVER begin work without loading these. Regenerate after refactoring: `python tools/generate_full_adg.py`.
> 6. **HITL (Human-In-The-Loop) DISCIPLINE.** When facing decisions with genuine ambiguity, run the confidence-gated pipeline: generate candidates → score (0.00–1.00) → filter at threshold 0.72 → apply dominance rule → surface 1–N options. Surface only options that clear the threshold and are materially distinct. A single dominant option (≥ 0.85, gap ≥ 0.12 to next) surfaces alone. No candidate above threshold → emit LOW_CONFIDENCE_AMBIGUITY and route to clarify/replan/abstain. NEVER pad options to reach a count. NEVER use generic pros/cons — use executive-grade §HITL-10 option shape. Wait for explicit user selection before proceeding. Workflow: `/hitl-decision-gate`. Rule: `.windsurf/rules/hitl-enforcement.md`.
> 7. **RCA AUTO-CLOSURE.** When creating an RCA document, AUTOMATICALLY execute corrective actions and update RCA status to RESOLVED with evidence artifacts. NEVER create RCA and leave it unresolved. User should not have to ask for closure.
> 8. **GUARDIAN EXEMPTION DISCIPLINE.** NEVER add `# guardian: allow-*` to silence the anti-pattern scanner without a real, specific justification. The format is `# guardian: allow-<type> -- <specific justification>`. Generic words ("needed", "required", "temporary", "legacy") are FORBIDDEN as justifications. Every new exemption in production code (`agentic_core/`, `apps_*/`, `system_learning/`) requires explicit HITL approval before the comment is added. The `guardian_exemption_gate.py` ratchet enforces this at commit time — new exemptions that exceed the ceiling will BLOCK the commit. Cascade MUST present a HITL prompt before adding any guardian comment. Gate: `ops_scripts/ci/guardian_exemption_gate.py`. Init after approval: `ADG_EXEMPTION_INIT=1 python ops_scripts/ci/guardian_exemption_gate.py`.
> 9. **SVP ENGINEERING PERSONA — ARCHITECTURAL DECISIONS.** When facing high-level design choices (technology selection, dependency reduction, infrastructure consolidation, migration strategies), explicitly invoke the "SVP Engineering" persona. This persona prioritizes: (a) operational simplicity — reduce moving parts, (b) dependency hygiene — eliminate redundant libraries, (c) archival over deletion — preserve history in `tools/archive/`, (d) documentation — ADRs in `docs/architecture/adr/`, (e) zero-regression validation — full test pass before commit. Apply this lens to all T3 architectural decisions.
> 10. **ZERO-LOSS REFACTOR DISCIPLINE.** When removing `_emit_*` boilerplate, trace instrumentation, or synthetic scaffolding from a file, the resulting file MUST be checked by the hollow file detector. If the file has zero behavioral FunctionDefs/ClassDefs after the removal, the file MUST be deleted entirely — not left as an empty shell. Gate: `ops_scripts/ci/zero_loss_refactor_verifier.py`. Pre-commit hook: T25 hollow-file-gate.
> 11. **TERMINAL PROCESS LIFECYCLE MANAGEMENT.** All terminal processes spawned via `run_command` or `subprocess` MUST be explicitly terminated when the query completes. Non-blocking commands MUST set `WaitMsBeforeAsync` or implement explicit process cleanup. Hanging terminal processes after query finish = CONSTITUTIONAL VIOLATION. Gate: `ops_scripts/ci/check_terminal_cleanup.py`.
> 12. **NO IMPORTS FROM ARCHIVES/ IN PRODUCTION CODE.** The `archives/` directory is a backup graveyard — imports from it are FORBIDDEN in production code (`agentic_core/`, `apps_*/`, `system_learning/`). During module migration, imports MUST be updated to canonical locations, not left pointing to archived copies. CI blocks any commit with active `from archives.` or `import archives.` statements. Gate: `ops_scripts/ci/check_no_archives_imports.py`.
> 13. **MCP GREEN LIGHT PREREQUISITE.** Before beginning ANY T2/T3 work, check ADG health in priority order: (1) **Preferred** — check Redis hot cache sentinel (`python tools/adg/adg_redis_ingest.py --check`); if hot, proceed immediately. (2) **Fallback** — if Redis is down or cache is cold, call `mcp1_adg_health`. If `mcp1_adg_health` is unhealthy, run `/mcp-failure-rca` and wait for recovery. NEVER begin multi-file work when BOTH Redis cache is cold AND ADG MCP is unhealthy. Hard gate enforced at session start by `pre_prompt_classifier.py` (Redis-first probe, ADG MCP fallback, exits 2 only if both are red).
> 14. **SUBPROCESS TIMEOUT DISCIPLINE.** ALL subprocess calls MUST include `timeout=`. No exceptions. `subprocess.run(argv, shell=False, timeout=30)` is the REQUIRED pattern. Omitting `timeout=` is a constitutional violation — runaway subprocesses are PP-9 zombie sources. PowerShell (`powershell`, `pwsh`) is FORBIDDEN — use `subprocess.run(argv, shell=False)`. Reinforced at runtime by `pre_run_command` hook (Wave 1 Phase 1.1). Policy SSOT: `global_rules.md` Section Subprocess Timeout Discipline.
> 15. **EXCEPTION HANDLING — COLUMN 5 PRECISE EXCEPTIONS.** Catch specific exception types with specific recovery. `except:` (bare) is FORBIDDEN. `except Exception` without `# guardian: allow-broad-exception -- <specific justification>` is FORBIDDEN. Guardian exemptions require HITL approval (§8). Enforced by `pre_write_gate.py` (Wave 1 Phase 1.2). Reference: `docs/reference/Python/Error & Exception Handling.md`.

## §0. DEFAULT ANALYSIS MODE — Tier-Aware

**DEFAULT = AST DEPENDENCY GRAPH, scaled to change complexity.**

### Tier Classification

| Tier | Scope | ADG Requirement | Evidence |
|------|-------|----------------|----------|
| **T0 — Question** | No code changes (explain, review, advise) | Use ADG hot cache if available. No ceremony. | None required |
| **T1 — Trivial** | ≤1 file, ≤20 lines, obvious scope (typo, docstring, config value, add assertion) | Verify with scoped tests. ADG cache query optional. | No `DEPENDENCY_GRAPH` section needed |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG cache for blast radius. Run scoped tests. | Brief scope note with graph justification |
| **T3 — Architectural** | >5 files, cross-layer, governance, or new feature | Full AST dependency graph protocol. Invoke skill `graph-analysis`. | Full `## DEPENDENCY_GRAPH` section mandatory |

### Core Principle (all tiers)

AST dependency graph is the **PRIMARY** analysis primitive. Text search is secondary confirmation only.

### T2/T3 Protocol

1. **Build/query AST dependency graph FIRST** — invoke skill `graph-analysis`
2. **Use graph as PRIMARY evidence** — text search only for literal/constant confirmation
3. **Block work if graph cannot be built** — fail-closed, record errors, mark conclusions partial, STOP
4. **Document graph in evidence** — `## DEPENDENCY_GRAPH` section mandatory for T3; brief scope note for T2

### FORBIDDEN (all tiers)

- ❌ Assuming relationships without graph proof (T2/T3: hard fail; T0/T1: best-effort cache query)
- ❌ Silent fallback from AST failure to text search (§2.3)
- ❌ Claiming "no dependencies" without graph analysis

### Tier Override

User may explicitly override tier: "this is just a simple fix" → T1. "full analysis please" → T3. When in doubt, default to T2.

---

## §1. TESTING FRAMEWORK

**ENFORCEMENT:** skill `testing-framework` for ALL code generation.

### 1.1 Coverage Requirements

**Zero-tolerance coverage:** Every changed line of logic MUST have deterministic tests. Use dependency graph to find existing coverage edges and identify gaps. No exceptions.

**Required test dimensions (mandatory for every changed surface):**
- **Edge cases:** null/None/missing field, empty input, malformed structure, boundary values, unauthorized input, stale/replay state, dependency failure, negative and recovery paths
- **State transitions:** valid→valid, invalid→attempted, repeated, interrupted, replayed
- **Determinism:** identical input → identical output; replay independence from wall clock, randomness, execution order
- **Fail-closed:** invalid preconditions block operation; no side-effects before block
- **Matrix:** test all interacting gates (feature flag × input validity, retry × confidence, policy × mutation, etc.)

**Regression testing:** Every bug fix MUST include a minimal reproducer and an adjacent near-miss case. Mutation-sensitive tests MUST fail if guard clauses are removed or comparisons flip.

### 1.2 Quality Standards

**Test-first discipline:** Tests MUST exist before logic changes are committed. Write them first.

**Deterministic tests only:** No random inputs, no time-dependent behavior, no external mutable state. Fix seeds and inject timestamps.

**Mock discipline:** Mocks ONLY for: external services that cannot run locally, hardware interfaces, filesystem permissions in CI. Mocks MUST NOT bypass validation, signature checks, routing gates, replay enforcement, or side-effect guards.

**Permission Testing Guidelines (Cross-Platform):**
- **NO platform-specific skips** — `@pytest.mark.skipif(os.name == 'nt')` or `pytest.skip("Unix only")` are FORBIDDEN for permission tests
- **Use mocking for permission errors** — Mock `builtins.open`, `pathlib.Path.mkdir`, or `os.chmod` to simulate permission denied scenarios
- **Verify graceful error handling** — Tests should verify that implementation returns error metadata (e.g., `{"error": "Permission denied"}`) rather than crashing
- **Cross-platform permission simulation:**
  - File read permission denied: `patch("builtins.open", side_effect=PermissionError(13, "Permission denied"))`
  - Directory creation denied: `patch.object(Path, "mkdir", side_effect=PermissionError(13, "Permission denied"))`
  - Disk full simulation: `patch.object(Path, "mkdir", side_effect=OSError(28, "No space left on device"))`
- **Required assertions:** Verify that error metadata contains permission-related keywords; verify system continues operating after permission errors; verify recovery works after permissions are restored

**Ingress-path rule:** Tests MUST target the real entrypoint or enforcement choke point. Test doubles MUST NOT bypass validation, routing gates, replay enforcement, or side-effect guards.

**Three quality gates (enforced in priority order):**
1. **No silent errors** — every error path must have test coverage that verifies explicit error metadata
2. **Cross-platform compatibility** — tests MUST NOT assume Unix-only features or skip on Windows
3. **Deterministic replay** — identical inputs → identical outputs, always

---

## §2. ADG FRAMEWORK

### 2.1 Graph-First Evidence

All T2/T3 decisions MUST use ADG as primary evidence. Plain text search is FORBIDDEN as primary evidence (may be used for confirmation only).

**MANDATORY ADG MCP TOOLS — use these, not grep:**

| Query Need | Required Tool | FORBIDDEN Alternative |
|------------|---------------|-----------------------|
| Find nodes by layer | `mcp0_adg_nodes_by_layer` | `grep_search`, `find_by_name` |
| Find nodes by file | `mcp0_adg_nodes_by_file` | `grep_search`, `read_file` scan |
| Outgoing dependencies | `mcp0_adg_edge_fanout` | `grep_search` for imports |
| Incoming dependents | `mcp0_adg_edge_fanin` | `grep_search` for references |
| Node details | `mcp0_adg_node` | `grep_search` for class/def |
| ADG health | `mcp0_adg_health` | any text fallback |

`grep_search` is **CATEGORICALLY FORBIDDEN** for dependency analysis, import tracing, or call-site discovery. It may only be used for literal string confirmation of a fact already established by ADG.

### 2.2 Scope Determination

Before any edit: query ADG for upstream/downstream. Declare exact file list with graph justification.

Required sequence:
1. `mcp0_adg_health` — confirm MCP is healthy
2. `mcp0_adg_nodes_by_file` or `mcp0_adg_nodes_by_layer` — locate entry points
3. `mcp0_adg_edge_fanout` / `mcp0_adg_edge_fanin` — trace blast radius
4. Declare exact file list with node IDs as evidence

### 2.3 Fail-Closed Rule

If ADG MCP returns an error or is unavailable:
1. **STOP immediately** — do not proceed with the work
2. Run `/mcp-failure-rca` workflow to diagnose and fix the MCP
3. Record the MCP failure as UNRESOLVED in evidence
4. **NEVER silently fall back to `grep_search` or text search**
5. Wait for MCP to be healthy before continuing

**The correct response to a broken MCP is to fix the MCP, not to use grep.**

MCP-down escalation steps:
```
1. python ops_scripts/ci/mcp_health_monitor.py --probe
2. Check ~/adg_mcp_server.log for errors
3. Remove-Item -Recurse -Force tools/adg/core/__pycache__
4. Restart ADG MCP server in Windsurf (Ctrl+Shift+P → Restart MCP)
5. Re-run mcp0_adg_health to confirm recovery
```

---

## §3. EVIDENCE AND DOCUMENTATION

### 3.1 Evidence Files

Every phase produces one evidence file under `docs/reports/plans/`. Evidence files are raw captures, not summaries. Format: `YYYYMMDD-HHMMSS-<phase>.md`.

### 3.2 Fact Classification

| Classification | Meaning |
|---------------|---------|
| `DIRECTLY_OBSERVED` | You ran the command, saw the output |
| `DERIVED` | Computed from direct observations |
| `INFERRED` | Logical consequence, no direct observation |
| `EXTERNAL` | Provided by user/external system |
| `ASSUMED` | Working hypothesis, explicitly flagged |
| `UNRESOLVED` | Known gap, explicitly listed |

**MANDATORY:** Every phase artifact MUST include `FACT_CLASSIFICATION` section with all six categories. Empty `UNRESOLVED` = claim of completeness.

### 3.3 Required Evidence Sections

Every evidence file MUST include:
- `## EXECUTION_SUMMARY` — What was done, tool calls made, files touched
- `## FACT_CLASSIFICATION` — Directly observed facts, derived facts, inferred facts, external inputs, assumptions, unresolved gaps
- `## ARTIFACTS` — Generated files, modified files, with absolute paths
- `## UNRESOLVED` — Explicit gaps that remain (empty if none)

**VIOLATIONS:**
- ❌ Omitting UNRESOLVED facts — silence is not proof of absence
- ❌ Upgrading DERIVED to DIRECTLY OBSERVED without re-running primary source
- ❌ Claiming phase complete while UNRESOLVED items remain

### 3.4 Artifact Links

Every artifact reference in a response MUST use backtick citation format: `` `@<absolute_path>` ``. Plain text paths = CONSTITUTIONAL VIOLATION.

### 3.5 Artifact Location

- **Plans** MUST be saved to `.windsurf/plans/<name>-<6hex>.md` (SSOT — see `plan-location.md`)
- **Evidence and phase reports** MUST be saved to `docs/reports/plans/`
- `docs/reports/plans/` is for evidence/reports ONLY — never for execution plans
- The archived history of `plan-location.md` is preserved in `tools/archive/.windsurf/rules/plan-location.md` for reference; the active rule remains `.windsurf/rules/plan-location.md`

All Python file I/O MUST use `encoding="utf-8"`. Evidence files are raw execution captures, ASCII-only.

### 3.6 RCA Auto-Closure Discipline

**When creating an RCA document, Cascade MUST:**

1. **Document the violation** — incident summary, root cause, impact
2. **Execute corrective actions IMMEDIATELY** — do not wait for user prompt
3. **Update RCA status** — mark as RESOLVED with timestamp
4. **Document evidence artifacts** — specific files changed, tests added
5. **Mark preventive measures** — completed items with [x]

**RCA Status Lifecycle:**
- ❌ OPEN — violation documented, corrective actions NOT executed
- 🔄 IN PROGRESS — corrective actions partially executed  
- ✅ RESOLVED — all immediate corrective actions completed with evidence

**FORBIDDEN:** Creating RCA and leaving it unresolved. User should never have to ask for closure.

---

## §4. SCOPE AND DETERMINISM

### 4.1 Scope Discipline

Scope expansion mid-phase = STOP and produce plan artifact. No implicit scope creep.

### 4.2 Determinism Requirements

Every operation MUST be reproducible. Required:
- Fixed seeds for any randomness
- Explicit timestamps (injected, not wall-clock dependent)
- No dependency on execution order
- No external mutable state

**Side-effect discipline:** All side effects (file writes, network calls, state mutations) MUST be:
1. Explicitly declared in phase evidence
2. Reversible (rollback plan documented)
3. Idempotent (re-running produces same result)

---

## §5. CI ENFORCEMENT

### 5.1 Pre-Commit Gates

All commits MUST pass:
- T1: Testing framework gates
- T2: ADG build verification
- T3: Fact classification completeness
- T4: Scope drift detection
- T5: Determinism checks

### 5.2 CI Pipeline

`python ops_scripts/ci/run_contract_gates.py` enforces all constitutional rules.

### 5.3 Gate Failure Response

Gate failure = STOP. No bypass, no "just this once". Fix the violation, re-run gates.

---

## §6. GOVERNANCE FRAMEWORK

### 6.1 Layer Sovereignty

L0-L6 semantics are locked. Cross-layer violations = HARD FAIL. See `structure_blueprint.py` for canonical definitions.

### 6.2 Agent Governance

One canonical agent class per file. Semantic duplicate agents forbidden. Agents invoked via canonical Python functions only.

### 6.3 Registry Hygiene

Agent registry SSOT: `agent_discovery_full.json`. Conflicting sources = execution BLOCKED.

---

## §7. ACCEPTANCE DISCIPLINE

### 7.1 Repair Class Taxonomy

| Class | When to Use | Evidence Required |
|-------|-------------|-------------------|
| `production_bug_fix` | Logic error in code under test | Failing test + root cause + fix verification |
| `stale_reference_fix` | Test references outdated symbol/path | ADG showing reference no longer exists |
| `broken_test_fix` | Test itself is broken (not code) | Test intent preserved, mechanics fixed |
| `policy_regression_fix` | Threshold/policy drift | Policy change justification + ADG impact |

### 7.2 Scoped Convergence

For any repair targeting specific failures:

1. Gather all failures in the scoped surface (use ADG, not naive collection)
2. Cluster by root cause (not symptom)
3. Target highest-fan-out fixes first
4. Verify each fix with scoped re-run
5. Iterate until scoped surface is green
6. Document convergence: what was fixed, what remains, why

**Convergence is NOT complete when:**
- Fixed the one failure you looked at, but others remain
- Scoped re-run wasn't performed
- Root cause wasn't addressed (just patched the symptom)

### 7.3 Repair Run Completion (Six Conditions)

1. All §7.2 scoped convergence conditions met
2. Every ADG-reachable dependent of repaired surface executed and passed
3. Full pytest suite green — zero failures, errors, unexpected skips
4. Full-suite run timestamp LATER THAN last repair commit timestamp
5. No new failures introduced (count ≤ pre-repair baseline)
6. Final summary artifact in `docs/reports/plans/` (evidence artifact) with empty `Unresolved`

---

## §8. ARCHITECTURE LOCKS

### 8.1 Canonical Semantics and SSOT

L0–L6 semantics MUST match repository SSOT (`structure_blueprint.py`). Agent registry SSOT: `agent_discovery_full.json`. Conflicting SSOT sources = execution BLOCKED.

### 8.2 Boundary Enforcement

Layer inversion detection MUST be AST-based. Cycles = HARD FAIL. Duplicate mixins forbidden. Cross-layer mutation violating sovereignty = HARD FAIL. Path shape alone is insufficient evidence.

### 8.3 Tooling/Runtime Boundary

`tools/evidence/` and `ops_scripts/ci/` MUST NOT import `apps_*`.

### 8.4 Agent Discipline

Agents invoked via canonical Python functions only. One canonical agent class per file. Semantic duplicate agents forbidden.

---

## §9. EXECUTION MODALITY

Execution occurs strictly by defined phase. Each phase produces one evidence file. Scope expansion → STOP and produce plan artifact.

### 9.1 Repair Gate — No Editing While Exploring

**Editing is FORBIDDEN until ALL five gates pass:**

| Gate | Requirement |
|---|---|
| G1 | Failure capture exists for every failing test (§2.5) |
| G2 | Root cause clusters exist (`adg_failure_clusters.json` is fresh) |
| G3 | Each proposed repair maps to one or more exact failing nodeids |
| G4 | Repair class declared (§2.5) |
| G5 | No UNRESOLVED facts in phase evidence for targeted cluster |

Mixing exploration and repair in the same step = HARD FAIL.

### 9.2 Stabilize Before Refactor

Structural refactors FORBIDDEN while: active scoped failures > 0, UNRESOLVED facts exist, registered skips have expired/missing resolution plans, full-suite not green.

**Priority order:** Correctness → Determinism → Governance integrity → Reproducible green scoped runs → Structural refactors.

---

## §10. PLAN DOCUMENTATION STANDARDS

**ENFORCEMENT:** All plan documents in `.windsurf/plans/` MUST follow this structure.

### 10.1 Required Plan Header Table

Every plan MUST include a waves table at the top with the following columns:

| Column | Requirement |
|--------|-------------|
| **Wave** | Sequential wave number (1, 2, 3...) |
| **Phase IDs** | Comma-separated phase identifiers (P0, P1, P2...) |
| **Focus** | Brief description of wave's primary objective |
| **Est. Tokens** | Token estimate from ContextWindowEstimator |
| **Assumptions** | Key assumptions driving the estimate |
| **Status** | 🟢 GREEN (≤150K), 🟡 YELLOW (150-175K), 🔴 RED (>175K) |
| **Success Criteria** | Measurable outcomes for the wave |

**Table Format Example:**
```markdown
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **Wave 1** | P0, P1, P2 | Inventory & Archive | 80,285 | 644 files + 90 scripts | 🟢 GREEN | All files inventoried |
```

**SSOT Terminology Requirement:**
- **Waves** = Single source of truth term for execution grouping (Wave 1, Wave 2, etc.)
- **P0, P1, P2...** = Component identifiers within waves
- **Phases** = Only used when referring to historical "phase-named" problems
- All plans MUST use consistent "Waves" terminology throughout

### 10.2 Token Estimation Workflow Requirement

**MANDATORY WORKFLOW:** Every plan MUST run the token estimator workflow before finalization:

```bash
# Run token optimization analysis
python tools/evidence/_run_token_optimizer_plan.py

# Run wave packing optimization
python tools/adg/wave_packer.py
```

**Requirements:**
- Token estimates MUST use `ContextWindowEstimator` with conservative 1.1× bias
- Each wave MUST target 150-160K tokens maximum
- Total tokens per wave MUST include: input + 12K output + 8K safety buffer
- Status colors MUST reflect: GREEN (≤150K), YELLOW (150-175K), RED (>175K)

### 10.3 Plan Validation Checklist

Before committing any plan document:
- ✅ Waves table present at top with all required columns
- ✅ Token estimator workflow executed with results included
- ✅ All waves have GREEN status (YELLOW requires HITL approval, RED forbidden)
- ✅ Success criteria are measurable and specific
- ✅ Assumptions are clearly documented
- ✅ Consistent "Waves" terminology used throughout (SSOT compliance)

**Enforcement:** Plans missing required table or token estimation will be rejected during review.

---

## §13. MCP GREEN LIGHT PREREQUISITE

### 13.1 Rule

Before beginning ANY T2/T3 work, the ADG health check MUST pass in this priority order:

```
1. (Preferred) Check Redis hot cache:
       python tools/adg/adg_redis_ingest.py --check
   → exit 0 (HOT): proceed immediately — Redis is the fast in-memory path
   → exit 1 (COLD): continue to step 2

2. (Fallback) If Redis is down or cache is cold, call mcp1_adg_health
   → healthy: proceed (ADG available via SQLite fallback)
   → unhealthy: STOP → run /mcp-failure-rca → wait for recovery

3. BLOCKED only when BOTH Redis is cold AND mcp1_adg_health is red.
```

**NEVER begin multi-file work when both Redis cache is cold AND ADG MCP is unhealthy.**
Redis is the preferred ADG source — faster, in-memory, no file lock contention. SQLite is the canonical fallback. ADG staleness is NOT a blocker — the snapshot is valid until manually refreshed via `python tools/generate_full_adg.py` (which auto-ingests to Redis on completion).

### 13.2 Scope

| Tier | MCP Green Light Required? |
|------|--------------------------|
| T0 — Question | ❌ Not required (no code changes) |
| T1 — Trivial | ⚠️ Recommended (ADG cache query optional) |
| T2 — Scoped | ✅ **REQUIRED** before any file edits |
| T3 — Architectural | ✅ **REQUIRED** before any analysis or edits |

### 13.3 Runtime Enforcement

This behavioral rule is reinforced at runtime by:
- **`pre_prompt_classifier.py`**: Redis sentinel probe first → ADG MCP fallback → exits 2 only if both are red
- **`pre_mcp_gate.py`**: blocks ADG calls when SQLite is locked or unreadable (staleness is advisory-only)
- **`adg_redis_ingest.py`**: auto-invoked by `generate_full_adg.py` to keep Redis hot after every refresh

### 13.4 Recovery Escalation

If Redis cache is cold:
```
python tools/adg/adg_redis_ingest.py --force
```

If `mcp1_adg_health` is also unhealthy:
```
1. python ops_scripts/ci/mcp_health_monitor.py --probe
2. Check ~/adg_mcp_server.log for errors
3. Run /mcp-failure-rca workflow
4. Re-run mcp1_adg_health to confirm recovery before proceeding
```

---

## §14. SUBPROCESS TIMEOUT DISCIPLINE

### 14.1 Rule

ALL subprocess calls MUST include `timeout=`. No exceptions.

```python
subprocess.run(argv, shell=False, timeout=30)    # REQUIRED
subprocess.run(argv, shell=False)                 # FORBIDDEN — no timeout
subprocess.run(cmd, shell=True)                   # FORBIDDEN — shell=True
subprocess.run(["powershell", ...])               # FORBIDDEN — PowerShell
```

Omitting `timeout=` creates zombie processes (PP-9) and session hangs.

### 14.2 Recommended Timeouts

| Operation | Recommended Timeout |
|-----------|-------------------|
| Quick validation / health check | 10s |
| File operations, git commands | 30s |
| Test runs (single file) | 60s |
| ADG generation, full scans | 180s |
| Network / MCP calls | 30s |

### 14.3 Runtime Enforcement

- **Wave 1 Phase 1.1**: `pre_run_command` hook blocks PowerShell commands
- **Policy SSOT**: `global_rules.md` Section Subprocess Timeout Discipline
- **CI gate**: `ops_scripts/ci/check_terminal_cleanup.py` (Constitutional §11)

---

## §15. EXCEPTION HANDLING — COLUMN 5 PRECISE EXCEPTIONS

### 15.1 Rule

All exception handling MUST catch **specific** exception types with **specific** recovery actions.

```python
# REQUIRED — precise exception type, explicit recovery
try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    log.error("Malformed JSON payload: %s", exc)
    return default_value

# FORBIDDEN — bare except (catches KeyboardInterrupt, SystemExit, etc.)
except:
    pass

# FORBIDDEN — broad except without guardian
except Exception:
    pass

# ALLOWED — broad except WITH explicit guardian and specific justification
except Exception as exc:  # guardian: allow-broad-exception -- third-party plugin raises unknown types
    log.warning("Plugin error (untyped): %s", exc)
```

### 15.2 Exception Vocabulary

Use these standard exception types. Never invent custom exceptions for standard conditions:

| Condition | Use |
|-----------|-----|
| File not found | `FileNotFoundError` |
| Invalid JSON | `json.JSONDecodeError` |
| Missing dict key | `KeyError` |
| Type mismatch | `TypeError`, `ValueError` |
| Subprocess failure | `subprocess.CalledProcessError`, `subprocess.TimeoutExpired` |
| Network error | `OSError`, `ConnectionError` |
| Permission denied | `PermissionError` |
| Import failure | `ImportError`, `ModuleNotFoundError` |

### 15.3 Guardian Exemption Protocol

When `except Exception` is genuinely unavoidable:

1. Add `# guardian: allow-broad-exception -- <specific justification>` on the same line
2. Justification MUST be specific — generic words ("needed", "temporary") are FORBIDDEN
3. HITL approval required before adding any guardian comment (Constitutional §8)
4. Gate: `ops_scripts/ci/guardian_exemption_gate.py` enforces the ratchet ceiling

### 15.4 Enforcement

- **Wave 1 Phase 1.2**: `pre_write_gate.py` blocks bare `except:` and `except Exception` without guardian
- **Policy SSOT**: `global_rules.md` §Exception Handling: Column 5 Precise Exceptions
- **Reference**: `docs/reference/Python/Error & Exception Handling.md`
