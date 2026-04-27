# L2 Execute Doctrine Gap Fill — `.windsurf/plans/l2-execute-doc-gap-fill-9c2a31.md`

**Status:** Done — shipped in commits `d92857f4d7` (W1-W5 baseline) + `5f0a14a521` (matrix + runtime proof) + `878cc2a913` (W6 hardening) + W7 exhaustive (this commit)
**Owner:** Cascade
**Source spec:** `docs/reference/04_L2_Execute/04.1` … `04.8` + parent `04_L2_Execute_detailed.md` + executive `04_L2_Execute_exec.md`

## Goal

Close the implementation gaps in `agentic_core/L2_execution/` against the new
L2 Execute reference doctrine (10 docs, 04.x series) without disturbing the
already-shipped v3/v4 receipt infrastructure.

## Discovery summary (existing vs gap)

**EXISTING (do not duplicate):**
- `types/l2_v3_receipts.py` — `PrepReceipt`, `ValidationReceipt`, `AttemptReceipt`,
  `HealReceipt`, `DispatchReceipt`, `LineageRoot`, `DeterminismBundle`, all enums
  (`ResultClass`, `TerminalStamp`, `RepairStatus`, `DispatchTarget`,
  `ExecutionLane`, `HealOutcomeStamp`, `ValidationOutcome`)
- `types/l2_v4_contracts.py` — `WorkOrderInputs`, `FrozenExecutionContext`,
  `ReplayBindings`, `WriteLockAssertion`, `PrepOutput`, `ApprovedWorkOrder`,
  `SealedRejectionPacket`, `ValidationOutput`, `TelemetryBundle`,
  `BudgetSnapshot`, `CapabilityScopeSummary`, `FAILURE_MATRIX`,
  `EXECUTION_LANE_CONSTRAINTS`, `repair_decision`, `revalidate_repaired_packet`,
  `verify_sealed_artifact_contract`, `L2_FULL_INVARIANTS`
- `types/sealed_l2_artifact.py` — `SealedL2Artifact`, `TerminalClassification`,
  `ValidationCounters`, `ReplayMetadata`
- `bounded_executor.py` — `execute()`, `CapabilityToken`, `SandboxEnvelope`,
  `L2SealedArtifact` (executor-side shape)
- `types/ptc_tool_contracts_types.py` — `ToolCall`, `ToolResult` (light PTC)
- `types/capability_token_v4_types.py`, `types/sandbox_envelope_types.py`,
  enforcement / healers / audit / capability folders.

**GAPS to fill (this plan):**
1. **04.1 Entry/Authority/Boundary** — no `L2ExecutionRequest`, no
   `ExecutionAuthorityContext`, no `L2BoundaryAssertion`, no entry-time
   `packet_normalizer`. Confirmed by grep (0 hits).
2. **04.7 PTC sandbox** — no `PTCExecutionProfile`, no `PTCScriptEnvelope`,
   no `PTCSandboxReceipt`. Existing `ToolCall`/`ToolResult` only cover
   single-tool result shape, not the script/sandbox/context-isolation
   contract.
3. **04.8 OTEL span vocabulary** — no central constants for
   `l2.e1.prep.*`, `l2.e2.valid.*`, `l2.e3.exec.*`, `l2.e4.heal.*`,
   `l2.e5.seal.*`, `l2.ptc.*` span names or their required attribute set.
   Confirmed by grep (0 hits).
4. **04.8 Anti-bypass enforcement guards** — no centralized module that
   asserts the §15 forbidden L2 outputs (no `ALLOW_FINISH`, no
   `route_changed`, no direct L4 write, no direct human call,
   no silent provider swap).

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | W1.1 | 04.1 Entry contracts + packet normalizer + tests | ~6k | Done — 18/18 |
| W2 | W2.1 | 04.7 PTC profile + script envelope + sandbox receipt + tests | ~5k | Done — 17/17 |
| W3 | W3.1 | 04.8 OTEL span constants + required-attribute schema + tests | ~3k | Done — 18/18 |
| W4 | W4.1 | 04.8 Anti-bypass guards + tests | ~4k | Done — 55/55 |
| W5 | W5.1 | Verify (pytest), commit, push | ~1k | Done — commit `d92857f4d7` |
| W6 | W6.1 | Hardening pass — edge-case test suite + 1 impl improvement (camelCase L4-write detection) | ~4k | Done — 217/217 |
| W7 | W7.1 | **Exhaustive coverage pass** — every doc requirement gets ≥1 direct test (full PTC matrix, 7 conditional OTEL attrs, all optional fields, 1000× replay determinism) | ~5k | Done — 237/237 |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|-------------|--------|
| W1.1 | 04.1 Entry contracts | new `types/l2_execution_request.py`, new `entry/__init__.py`, new `entry/packet_normalizer.py`; tests in `tests/unit/agentic_core/L2_execution/test_l2_entry_pipeline.py` | Must compose with existing `WorkOrderInputs`/`PrepOutput`; must reject unsigned/route-mutated packets; must emit `L2BoundaryAssertion` | 6k | Done — 18/18 |
| W2.1 | 04.7 PTC contracts | new `types/ptc_execution_profile.py`, `types/ptc_script_envelope.py`, `types/ptc_sandbox_receipt.py`; tests in `tests/unit/agentic_core/L2_execution/test_ptc_execution_contracts.py` | Must isolate raw tool results (`SANDBOX_ONLY`); must enforce `fail_closed_on_untranscripted_io`; must require `script_digest` + `sandbox_profile_ref` | 5k | Done — 17/17 |
| W3.1 | 04.8 OTEL spans | new `observability/l2_spans.py`; tests in `tests/unit/agentic_core/L2_execution/test_l2_otel_span_vocabulary.py` | All 6 phase groups + required-attribute set; central registry for downstream emitters | 3k | Done — 18/18 |
| W4.1 | 04.8 Anti-bypass | new `enforcement/anti_bypass_guards.py`; tests in `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py` | Must reject 16 forbidden L2 outputs; functional guard, not just a list | 4k | Done — 55/55 |
| W5.1 | Verify + ship | run new tests + adjacent existing L2 tests; commit + push | Existing test surface must remain green; subprocess gate; no PowerShell | 1k | Done — commit `d92857f4d7` |
| W6.1 | Hardening pass | new `tests/unit/agentic_core/L2_execution/test_l2_doctrine_edge_cases.py` (217 cases). Promotes every `__post_init__` invariant to direct test coverage. Found and fixed: `assert_no_direct_l4_write` missed camelCase variants (`DurableWrite`); upgraded matcher to be normalization-robust. | Coverage rule: every post_init invariant has direct edge-case test; every closed-vocabulary enum rejects raw-string substitution; every numeric field rejects out-of-range; every required string rejects empty; every fail-closed coupling matrix exercised. | 4k | Done — 217/217 |
| W7.1 | Exhaustive coverage | new `tests/unit/agentic_core/L2_execution/test_l2_doctrine_exhaustive.py` (237 cases). Closes the residual "covered by aggregator"/"single-test" rows so every doc requirement has ≥1 direct test. Adds: full PTCSandboxReceipt 6×3×2×2 = 72 status×result_class matrix, 7 conditional OTEL attribute tests, all 6 optional `L2ExecutionRequest` fields, all 3 optional authority fields, 12 type-guard sweeps for None/wrong-type input, 1000× replay determinism, 12-case boundary-bit power-set sample, every `EntryRejectionReason` (12) constructed individually, every `BypassReason` (16) value-uniqueness asserted. | Discovery: 5 of the new tests caught wrong fact-key names in initial draft (`retrieval_authority` vs `c0_retrieval_authority`, `target` vs `write_target`, etc.) — closes a hidden documentation drift between aggregator dispatch keys and individual guard parameter names. | 5k | Done — 237/237 |

## File Manifest

**New files:**
- `agentic_core/L2_execution/types/l2_execution_request.py`
- `agentic_core/L2_execution/entry/__init__.py`
- `agentic_core/L2_execution/entry/packet_normalizer.py`
- `agentic_core/L2_execution/types/ptc_execution_profile.py`
- `agentic_core/L2_execution/types/ptc_script_envelope.py`
- `agentic_core/L2_execution/types/ptc_sandbox_receipt.py`
- `agentic_core/L2_execution/observability/__init__.py` (if missing)
- `agentic_core/L2_execution/observability/l2_spans.py`
- `agentic_core/L2_execution/enforcement/anti_bypass_guards.py`
- `tests/unit/agentic_core/L2_execution/test_l2_entry_pipeline.py`
- `tests/unit/agentic_core/L2_execution/test_ptc_execution_contracts.py`
- `tests/unit/agentic_core/L2_execution/test_l2_otel_span_vocabulary.py`
- `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py`

**Modified files:**
- None expected. Plan is strictly additive. If integration with `__init__.py`
  is needed, it will be done in W5 only after all new modules pass tests.

## Acceptance Criteria

- All four new test modules pass.
- No existing L2 tests regress (`tests/unit/agentic_core/L2_execution/`).
- No new `except Exception` without guardian comment.
- All subprocess calls (if any) use `subprocess.run(argv, shell=False, timeout=...)`.
- Anti-bypass guards reject all 16 forbidden patterns enumerated in 04.8 §3.
- OTEL span constants are exhaustively typed and unit-asserted.
- Commit + push to `origin/main`.

## ADG Provenance
ADG Provenance: backend=skipped (T3 additive new-file gap fill, no
dependency-blast-radius query needed; existing v3/v4 receipt graph already
mapped during W1 of plan `l2-execute-best-practices-gap-b7c4e2`).
