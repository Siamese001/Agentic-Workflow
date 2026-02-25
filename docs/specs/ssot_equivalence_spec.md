# SSOT Equivalence Specification

> Authoritative contract for the zero-loss migration of `execute_ssot.py` and
> `execute_ssot_entrypoint.py` into the PNG-aligned Guardian pipeline.
>
> Source: `docs/specs/execute_ssot_bucket_map.json` (98 entries, 7 buckets).

## 1. Scope

### Legacy entrypoints under comparison

| File | Invocation |
|---|---|
| `execute_ssot_entrypoint.py` | `python -m agentic_core.L0_maintenance.scripts.execute_ssot_entrypoint --legacy [ARGS]` |
| `execute_ssot.py` | Imported by entrypoint; never invoked directly in CI. |

### Definition of equivalence

The new Guardian pipeline is **equivalent** to the legacy pipeline when, given
the same repo state as input:

1. The **detection set** (violations/checks discovered) is identical.
2. The **repo-state end condition** (tracked file tree after execution) is identical.
3. Every **artifact** the legacy pipeline emits has a mapped counterpart in the
   new pipeline that carries at least the same informational content.
4. All **ALLOWED_DELTA** items are explicitly enumerated and accepted.

## 2. Artifacts

### Legacy outputs

| Artifact | Path / Mechanism |
|---|---|
| Runtime state JSON | `runtime_state.json` (written by `RuntimeStateManager.save`) |
| Compliance report JSON | `logs/compliance_reports/*.json` (written by `save_comprehensive_reports`) |
| Compliance report Markdown | `logs/compliance_reports/*.md` (written by `save_comprehensive_reports`) |
| V15 surgical manifest | In-memory dict; optionally serialized by `_v15_build_ssot_manifest` |
| V15 gateway audit trail | Logged by `_v15_ssot_gateway_audit` |
| Agent discovery cache | `agent_discovery_full.json` (written by `discover_agents_from_registry`) |
| Stdout/stderr logs | Console output via `logging` + `print_execution_plan` |

### New pipeline artifact types

| Type | Description |
|---|---|
| `AGGREGATE` | `GuardianResult` combining all check outcomes (replaces `ReconciliationManifest.finalize`) |
| `RESULT` | Individual `GuardianCheck` per detection unit (replaces `ReconciliationViolation`) |
| `HEALING_PLAN` | `HealResult` per remediation action (replaces inline heal dispatch) |
| `INCIDENT` | Structured error/exception record (new; no legacy equivalent) |
| `TELEMETRY` | Runtime state + V15 manifest (replaces `RuntimeStateManager` + `_v15_build_ssot_manifest`) |

## 3. Required Invariants

All invariants must hold for the new pipeline to be accepted as equivalent.

1. **Detection set equivalence** — The set of `check_id` values emitted by the
   new pipeline must be a superset of the legacy violation identifiers for the
   same repo state. No legacy detection may be silently dropped.

2. **Repo-state end condition equivalence** — After execution, `git diff` and
   the file tree (relative paths + SHA-256) must be identical between legacy
   and new pipeline runs on the same input state.

3. **Guardian side-effect prohibition** — L5_GUARDIAN bucket units must be
   scan-only. They must not write to tracked repo files. Verified by asserting
   `git status --porcelain` is empty after guardian-only execution.

4. **L2-only write permission** — Only L2_HEALER_PIPE bucket units may modify
   tracked repo files. All other buckets must be write-free.

5. **Post-heal revalidation** — After any L2 healing action, the corresponding
   L5_GUARDIAN detection must re-run and confirm the violation is resolved.
   The new pipeline must not skip post-heal validation.

6. **Idempotency** — Running the new pipeline twice on an already-clean repo
   must produce identical repo state and identical artifact content (modulo
   timestamps in TELEMETRY).

7. **Artifact schema validity** — Every emitted artifact must validate against
   its schema: `GuardianResult` for AGGREGATE, `GuardianCheck` for RESULT,
   `HealResult` for HEALING_PLAN.

8. **Phase ordering preservation** — The new pipeline must execute detection
   before remediation, and remediation before certification, matching the
   legacy 5-phase ordering.

9. **Agent roster coverage** — Every agent key in `CANONICAL_ROSTER_KEYS` must
   be reachable in the new pipeline. No agent may be silently excluded.

10. **Graceful shutdown equivalence** — SIGINT/SIGTERM during execution must
    produce a clean exit with partial telemetry written, matching legacy
    `GracefulExitHandler` behavior.

11. **Non-interactive enforcement** — The new pipeline must block interactive
    `input()` calls in CI, matching `NonInteractiveGuard` behavior.

12. **Territory input validation** — Territory arguments must be validated
    against the same regex/injection rules as `validate_territory_input`.

## 4. Allowed Deltas

The following legacy behaviors are **explicitly retired** and do NOT require
parity in the new pipeline:

1. **Confidence scoring retired** — `ConfidenceScore`, its threshold properties,
   and all confidence predicates (`is_high_confidence`, `is_medium_confidence`,
   `is_low_confidence`) are removed. The new pipeline uses deterministic
   policy rules instead of floating-point confidence thresholds.

2. **Autonomous/cognitive decision engines retired** —
   `AutonomousDecisionEngine`, `EnhancedAutonomousDecisionEngine`, and their
   methods (`_calculate_semantic_similarity`, `_calculate_pattern_confidence`,
   `calculate_healing_confidence`, `should_proceed_with_healing`,
   `analyze_violations_with_cognitive_disposition`) are removed. These relied
   on non-deterministic heuristics and optional LLM arbitration.

3. **Sovereign decision engine partially retired** —
   `SovereignDecisionEngine` class and `__init__` are retired. The
   deterministic sub-units (`request_sovereignty_token`,
   `release_sovereignty_token`) migrate to L2_HEALER_PIPE as standalone
   lock primitives.

4. **Report format differences** — Markdown report layout may differ between
   legacy and new pipeline. This delta is allowed ONLY IF the new AGGREGATE
   artifact contains all fields present in the legacy JSON report. Field
   names may differ; values must be semantically equivalent.

5. **Timestamp and duration fields** — Exact timestamps and durations in
   TELEMETRY artifacts are inherently non-deterministic and are excluded
   from strict equality comparison.

## 5. Mapping Table

| Legacy Concept | New Artifact / Source |
|---|---|
| `ReconciliationViolation` | `GuardianCheck` in RESULT |
| `ReconciliationManifest` | `GuardianResult` in AGGREGATE |
| `ReconciliationManifest.finalize()` | `GuardianResult.to_dict()` |
| `execute_phase1_discovery` detections | L5_GUARDIAN RESULT checks (discovery scope) |
| `execute_phase2_reconciliation` heals | L2_HEALER_PIPE HEALING_PLAN entries |
| `execute_phase3_validation` re-scan | L5_GUARDIAN RESULT checks (post-heal scope) |
| `execute_phase4_healing_impl` governor | L2_HEALER_PIPE HEALING_PLAN (governor scope) |
| `execute_phase5_final_impl` reports | L6_OBSERVABILITY AGGREGATE + TELEMETRY |
| `RuntimeStateManager` state writes | L6_OBSERVABILITY TELEMETRY |
| `_v15_build_ssot_manifest` | L6_OBSERVABILITY TELEMETRY (V15 section) |
| `EXECUTION_PLAN` / `AGENT_DEPENDENCIES` | `L0_ROUTER` phase_spec config |
| `discover_agents_from_registry` | `L0_ROUTER` guardian_registry |
| `PreFlightValidator.run_checks` | CI_GATE RESULT (preflight scope) |
| `ASTCodeQualityValidator.check_file_quality` | L5_GUARDIAN RESULT (AST quality scope) |
| `try_summon_orchestrator` | L3_HIL `ConsolidatedOrchestratorAgent` |
| `GracefulExitHandler` | L0_ROUTER signal_handler enforcement |
