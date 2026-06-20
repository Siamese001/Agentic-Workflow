---
plan_id: eval-harness-adg-mcp-open-replan-9c1f2a
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "TBD before W2 implementation"
dod_exempt: false
supersedes: [eval-harness-adg-mcp-replan-a71c9e, eval-harness-spine-adg-closeout-6f2a9c]
---

# Eval Harness ADG MCP Open Replan

Rectify the proposed offline eval harness against the runtime spine using the live, open ADG MCP transport as the evidence authority.

> **plan_id discipline**: `plan_id` matches the filename stem `eval-harness-adg-mcp-open-replan-9c1f2a`. Wave markers use `plan=eval-harness-adg-mcp-open-replan-9c1f2a`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** - The proposed eval harness wraps the production runtime spine at four offline seams: whole-spine replay, X1D judge calibration, L6 exhaust-to-corpus promotion, and X2 micro-evals. After Codex restart, the direct ADG MCP channel is open: `adg_health` and `adg_status` return `status=ok`, and `adg_nodes_by_layer(L6)` returns through Redis.
- **Complication** - The original eval assets did not form the proposed harness: replay was not whole-spine, baseline comparison was not structurally bound, X2 micro-evals were not first-class, X1D calibration metrics drifted between raw agreement and kappa, L6 findings did not reliably graduate into reviewed corpus scenarios, and promotion evidence lacked direct ADG MCP proof.
- **Question** - How do we close the eval-harness gaps while preserving the hard line that offline eval informs promotion and trust but never waives a live X2, X1D, X3, Exit, or UWG verdict?
- **Answer** - Completed: ADG-backed gap matrix, whole-spine replay receipts, X2 micro-eval fixtures, X1D calibration trust, L6 corpus graduation, and CI/UWG promotion binding are in place. Final promotion evidence now passes with direct ADG MCP health.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | ADG MCP evidence baseline and gap matrix | ~10K | ADG MCP stays open or failures are marked as degraded fallback | DONE | Matrix maps four harness seams to ADG nodes/views and records direct MCP health plus PID/snapshot evidence |
| W2 | W2.1, W2.2, W2.3 | Whole-spine replay rig | ~35K | Existing proof fixtures can run offline without provider leakage | DONE | Pinned scenarios execute U0-to-L6 and emit comparable replay receipts |
| W3 | W3.1, W3.2, W3.3 | X2 micro-evals and X1D calibration trust | ~32K | Human-label corpus can be staged incrementally | DONE | X2 edge fixtures fail closed; X1D judges require fresh calibrated quorum |
| W4 | W4.1, W4.2, W4.3 | L6 exhaust-to-corpus flywheel | ~26K | L6 packages can be sealed and trace-bound before review | DONE | Session findings become reviewable corpus candidates and graduate deterministically |
| W5 | W5.1, W5.2, W5.3 | CI/UWG/Notion promotion binding | ~24K | Promotion can require harness artifacts without blocking unrelated changes | DONE | CI and UWG cite replay, calibration, and ADG MCP transport receipts |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Capture live ADG MCP transport receipt | DONE |
| W1.2 | Query ADG eval/replay/exit/gateway views | DONE |
| W1.3 | Publish harness seam gap matrix | DONE |
| W2.1 | Define pinned scenario and replay receipt schemas | DONE |
| W2.2 | Implement whole-spine offline replay runner | DONE |
| W2.3 | Add baseline comparison and pass-rate promotion gates | DONE |
| W3.1 | Build X2 micro-eval fixture families | DONE |
| W3.2 | Align X1D calibration metric semantics | DONE |
| W3.3 | Bind judge snapshot IDs to every X1D score | DONE |
| W4.1 | Ingest L6 exhaust into staged corpus candidates | DONE |
| W4.2 | Add review packets and graduation workflow | DONE |
| W4.3 | Seed scenarios from known session findings | DONE |
| W5.1 | Add eval-harness CI triggers and gates | DONE |
| W5.2 | Bind UWG promotion evidence | DONE |
| W5.3 | Sync Notion and final verification evidence | DONE |

---

## ADG MCP Evidence At Plan Creation

Transport receipt:
- `adg_runtime_info.status`: `ok`
- PID: `44244`
- Startup nonce: `ffd0af1e3137`
- Combined stack fingerprint: `29b299ba80`
- Snapshot ID: `06082026_1212`
- Redis enabled: `true`

Health receipt:
- `mode`: `full`
- `sqlite`: `healthy`
- `redis`: `healthy`
- `cache_hit_capable`: `true`
- `graph_projection.available`: `true`
- `graph_projection.stale`: `false`
- SQLite path: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite`
- Node count: `182313`
- Edge count: `1072457`

Query receipt:
- `adg_nodes_by_layer(layer=L6, limit=3)` returned `status=ok`.
- `backend_used=redis`, proving the Redis hot path is live for the ADG MCP.

### W1 Attempt Log - 2026-06-10

- Direct Codex MCP call `mcp__adg_sqlite.adg_health` failed with `Transport closed`.
- Earlier W1 direct probes for `adg_runtime_info`, `adg_status`, `adg_nodes_by_layer`, and `adg_violations` also failed with `Transport closed`.
- Out-of-band supervisor check `tools/mcp/check_adg_sqlite_transport.py --json` returned `status=open`, SQLite `status=ok`, Redis `status=healthy`, snapshot `06082026_1212`, node count `182313`, edge count `1072457`.
- Process evidence showed supervised ADG launcher/server processes including launcher PIDs `44324`/`45204` and server PID `45032`.
- Degraded SQLite fallback sampled ADG views `mv_runtime_spine_gaps`, `mv_replay_surface_gaps`, `mv_trace_replay_eval_gaps`, `mv_exit_disposition_coverage`, `mv_gateway_bypass_paths`, and `mv_eval_coverage_by_path`.
- W1 matrix artifact: `docs/reports/eval/eval_harness_adg_mcp_w1_transport_matrix_9c1f2a.md`.
- Decision: W1 is blocked on agent-facing MCP transport. Backend transport is open out-of-band, but Codex MCP tools still return `Transport closed`.

### W1 Reopen Closeout - 2026-06-10

- After Codex restart, direct `mcp__adg_sqlite.adg_health` returned `status=ok`, SQLite `healthy`, Redis `healthy`, cache hit capable, snapshot `06082026_1212`, node count `182313`, edge count `1072457`.
- Direct `mcp__adg_sqlite.adg_status` returned `status=ok` for snapshot `06082026_1212`.
- Direct `mcp__adg_sqlite.adg_nodes_by_layer(layer=L6, limit=3)` returned `status=ok` with `backend_used=redis`.
- Out-of-band helper `tools/mcp/check_adg_sqlite_transport.py --json` returned `status=open` and supervisor PID `47756`.
- The current Codex-exposed ADG tool list does not include `adg_runtime_info`; final receipts record `runtime_info_available=false` rather than fabricating a startup nonce.

---

## Out Of Scope

- Letting offline eval override a live runtime gate verdict.
- Treating mock/fake provider receipts as live X1D proof.
- Auto-promoting L6 findings into golden suites without human review.
- Replacing app-specific validators with a single generic judge.
- Reopening unrelated dormant MCP servers.

---

## Wave 1 - ADG MCP Evidence Baseline And Gap Matrix

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - Evidence capture and matrix artifact only.

**Phases**:
- **W1.1** - Capture live ADG MCP transport receipt | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Query ADG eval/replay/exit/gateway views | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Publish harness seam gap matrix | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Runtime receipt records direct MCP health, PID when available from supervisor/runtime info, snapshot ID, SQLite path, Redis state, node count, and edge count.
- ADG evidence uses MCP first; any local SQLite fallback is marked `DEGRADED_FALLBACK`.
- Matrix maps every proposed seam to concrete files, ADG nodes, views, and test/proof targets.

---

## Wave 2 - Whole-Spine Replay Rig

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Define pinned scenario and replay receipt schemas | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Implement whole-spine offline replay runner | ~15K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** - Add baseline comparison and pass-rate promotion gates | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Scenario fixtures carry SHA-256 identity for JD, briefing, policies, expected receipt class, and provider mode.
- Replay runner executes the runtime spine rather than reclassifying stored labels.
- Candidate-vs-baseline comparison can block promotion even when absolute pass-rate is high.

**W2 Closeout - 2026-06-10**:
- User authorization recorded by command `W2`; W2 `AUTHORIZATION_STATUS` set to `GRANTED`.
- Implementation landed in worktree `C:\Git\eval-harness` on branch `eval-harness`.
- Added `tools/eval/whole_spine_replay.py` with scenario identity hashing, command execution through `subprocess.run(..., shell=False)`, runtime receipt validation, and optional baseline comparison.
- Added `tests/unit/tools/eval/test_whole_spine_replay.py`.
- No `agentic_core` files were edited; CoreAddition Author-Gate receipt was not consumed for W2 eval-tooling-only work.
- W2 evidence report: `docs/reports/eval/eval_harness_w2_whole_spine_replay_9c1f2a.md`.
- Verification: focused pytest `3 passed`; `py_compile` passed for `tools/eval/run_capability_regression.py` and `tools/eval/whole_spine_replay.py`; CLI `--help` passed.
- Caveat: W1 remains blocked because direct Codex ADG MCP calls still return `Transport closed`.

---

## Wave 3 - X2 Micro-Evals And X1D Calibration Trust

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Build X2 micro-eval fixture families | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Align X1D calibration metric semantics | ~11K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.3** - Bind judge snapshot IDs to every X1D score | ~11K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- X2 fixtures cover numeric precision, sentence boundaries, leakage/self-check separation, unknown hard-lines, and mock-not-allow behavior.
- X1D calibration chooses a single statistic or documents a conversion between raw agreement and Cohen kappa.
- Stale judge, missing calibration snapshot, no quorum, and provider-mode mismatch cannot clear X1D.

**W3 Closeout - 2026-06-10**:
- User authorization recorded by command `W3`; W3 `AUTHORIZATION_STATUS` set to `GRANTED`.
- Implementation landed in worktree `C:\Git\eval-harness` on branch `eval-harness`.
- Added `tools/eval/x2_micro_eval.py` and canonical fixtures at `data/eval/x2_micro/fixtures.json`.
- Added `tools/eval/x1d_calibration_trust.py` with canonical metric `quadratic_weighted_kappa`.
- Added focused tests `tests/unit/tools/eval/test_x2_micro_eval.py` and `tests/unit/tools/eval/test_x1d_calibration_trust.py`.
- No `agentic_core` files were edited; CoreAddition Author-Gate receipt was not consumed for W3 eval-tooling-only work.
- W3 evidence report: `docs/reports/eval/eval_harness_w3_x2_x1d_trust_9c1f2a.md`.
- Verification: focused pytest `9 passed`; `py_compile` passed for both new tools; X2 fixture CLI passed with five required families; X1D trust CLI help passed.
- Caveat: W1 remains blocked because direct Codex ADG MCP calls still return `Transport closed`.

---

## Wave 4 - L6 Exhaust-To-Corpus Flywheel

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D

**Phases**:
- **W4.1** - Ingest L6 exhaust into staged corpus candidates | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** - Add review packets and graduation workflow | ~9K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.3** - Seed scenarios from known session findings | ~9K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- L6 packages include trace, gate, judge, and exit evidence before staging.
- Graduation requires review and deterministic replay evidence.
- Known failures such as token truncation, zero judge rows, and decimal false-positive cases become frozen scenarios.

**W4 Closeout - 2026-06-10**:
- User authorization recorded by command `W4`; W4 `AUTHORIZATION_STATUS` set to `GRANTED`.
- Implementation landed in worktree `C:\Git\eval-harness` on branch `eval-harness`.
- Added `tools/eval/l6_corpus_graduation.py` with stage, review-packet, and graduate commands.
- Added known failure seeds at `data/eval/l6_corpus/known_failure_seeds.json`.
- Added focused tests `tests/unit/tools/eval/test_l6_corpus_graduation.py`.
- No `agentic_core` files were edited; CoreAddition Author-Gate receipt was not consumed for W4 eval-tooling-only work.
- W4 evidence report: `docs/reports/eval/eval_harness_w4_l6_corpus_graduation_9c1f2a.md`.
- Verification: focused pytest `7 passed`; `py_compile` passed; CLI staging smoke emitted a staged `decimal_false_positive` candidate.
- Caveat: W1 remains blocked because direct Codex ADG MCP calls still return `Transport closed`.

---

## Wave 5 - CI/UWG/Notion Promotion Binding

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: E

**Phases**:
- **W5.1** - Add eval-harness CI triggers and gates | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** - Bind UWG promotion evidence | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.3** - Sync Notion and final verification evidence | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- CI triggers cover touched runtime spine, X2, X1D, L6, replay, and promotion files.
- UWG promotion cites replay receipt, calibration receipt, ADG transport receipt, and baseline comparison receipt.
- Notion status changes only after filesystem SSOT and verification artifacts are current.

**W5 Closeout - 2026-06-10**:
- User authorization recorded by command `W5`; W5 `AUTHORIZATION_STATUS` set to `GRANTED`.
- Implementation landed in worktree `C:\Git\eval-harness` on branch `eval-harness`.
- Added `tools/eval/eval_harness_promotion_gate.py`, `ops_scripts/ci/check_eval_harness_promotion_evidence.py`, `docs/runbooks/eval_harness_promotion_binding.md`, and `tests/unit/tools/eval/test_eval_harness_promotion_gate.py`.
- The promotion gate requires whole-spine replay, X2 micro-eval, X1D trust, L6 graduation, and direct ADG transport receipts before promotion can pass.
- Final passing gate report: `C:\Git\eval-harness\artifacts\eval\promotion\w5_final\final_gate_report.json`.
- Final evidence manifest: `C:\Git\eval-harness\artifacts\eval\promotion\w5_final\evidence_manifest.json`.
- W5 evidence report: `docs/reports/eval/eval_harness_w5_promotion_binding_9c1f2a.md`.
- Verification: focused pytest `6 passed` with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; `py_compile` passed; CI wrapper `--help` passed; final promotion gate report passed with all five evidence checks green and complete trigger coverage.
- Plan validation: `check_plan_format_compliance.py --strict` passed with `0 FAIL, 0 ERROR, 0 WARN`.
- Notion Plans row synced at `https://app.notion.com/p/37b27693f55c813b93a5f0e1d3ef310f`.
- No `agentic_core` files were edited; CoreAddition Author-Gate receipt was not consumed for W5 eval-tooling-only work.
- Closeout: overall plan status is `DONE`; direct Codex ADG MCP calls now return `status=ok`.

---

## Execution Details

### W1.1 - Capture Live ADG MCP Transport Receipt
**Scope**: Prove agent-facing ADG MCP availability.

**Commands**:
```bash
# MCP calls: adg_runtime_info, adg_health, adg_status, adg_nodes_by_layer
```

### W1.2 - Query ADG Views
**Scope**: Query structural gaps through MCP before local fallback.

**Commands**:
```bash
# MCP preferred: adg_violations, adg_nodes_by_file, adg_edge_fanin, adg_edge_fanout
```

### W1.3 - Publish Harness Matrix
**Scope**: Create `docs/reports/eval/` artifact mapping seams to ADG evidence.

**Commands**:
```bash
python scripts/governance/verify_codex_primary.py
```

### W2.1 - Replay Schema
**Scope**: Define pinned scenario and receipt contracts.

**Commands**:
```bash
python -m py_compile tools/eval/run_capability_regression.py
```

### W2.2 - Replay Runner
**Scope**: Execute the runtime spine offline using safe fixtures.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "replay or capability"
```

### W2.3 - Baseline Gates
**Scope**: Enforce pass-rate and candidate-vs-baseline checks.

**Commands**:
```bash
python tools/eval/run_capability_regression.py --help
```

### W3.1 - X2 Micro-Evals
**Scope**: Build named fixture suite for gate boundaries.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "x2 or validator"
```

### W3.2 - X1D Calibration Alignment
**Scope**: Align calibration statistic and threshold semantics.

**Commands**:
```bash
rg -n "kappa|agreement|calibration|judge" .github tools agentic_core apps_rg tests
```

### W3.3 - Judge Snapshot Binding
**Scope**: Require calibration snapshot identity on all X1D scores.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "x1d or judge"
```

### W4.1 - L6 Exhaust Staging
**Scope**: Convert L6 exhaust packages into staged candidates.

**Commands**:
```bash
rg -n "flywheel|shadow|exhaust|graduate" agentic_core tools tests
```

### W4.2 - Review And Graduation
**Scope**: Add review packet and deterministic graduation path.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "flywheel or corpus or eval"
```

### W4.3 - Seed Known Failures
**Scope**: Freeze known session failures into regression scenarios.

**Commands**:
```bash
rg -n "truncation|judge-refresh|99.99|merged bullets|judge rows" docs tests tools artifacts
```

### W5.1 - CI Gates
**Scope**: Expand trigger surface and fail-closed promotion checks.

**Commands**:
```bash
python ops_scripts/ci/run_contract_gates.py --help
```

### W5.2 - UWG Evidence
**Scope**: Bind promotion claims to harness receipts.

**Commands**:
```bash
rg -n "UWG|promotion|regression|calibration" .github tools docs agentic_core
```

### W5.3 - Final Verification
**Scope**: Validate plan, adapter docs, and focused tests.

**Commands**:
```bash
python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/eval-harness-adg-mcp-open-replan-9c1f2a.md
python scripts/governance/verify_codex_primary.py
```

---

## Gap Register

**GAP-1: Whole-spine replay is not yet the eval runner**
- Existing assets do not yet prove a full U0-to-L6 replay for pinned scenarios.
- Impact: promotion can pass without proving runtime-spine behavior.

**GAP-2: Baseline comparison is not structurally bound**
- Proposed harness requires candidate-vs-baseline evidence, not just absolute current pass-rate.
- Impact: regressions can hide behind high aggregate pass-rate.

**GAP-3: X2 micro-evals are not first-class**
- Gate edge fixtures are scattered rather than a named harness suite.
- Impact: validator regressions may not block promotion.

**GAP-4: X1D calibration metric semantics drift**
- Raw agreement and Cohen kappa appear in separate surfaces.
- Impact: under-calibrated or stale judges may count toward quorum.

**GAP-5: L6 exhaust-to-corpus is not end-to-end**
- Shadow eval packages do not reliably become reviewed regression scenarios.
- Impact: repeated session failures may not be frozen into the suite.

**GAP-6: Replay and exit disposition coverage are incomplete**
- ADG evidence shows replay-link and exit-disposition gaps on important spine surfaces.
- Impact: the proposed hard line cannot be audited structurally.

**GAP-7: CI/UWG promotion binding is incomplete**
- Promotion does not yet require the full set of replay, calibration, ADG transport, and baseline receipts.
- Impact: harness evidence can remain advisory instead of gating.

---

## Definition of Done

DoD-1: ADG MCP transport receipt is current.
- Evidence: direct `adg_health`, `adg_status`, and Redis-backed `adg_nodes_by_layer` return `status=ok`; supervisor PID and snapshot are recorded in the final ADG receipt.
- Status: DONE

DoD-2: Harness gap matrix is ADG-backed.
- Evidence: `docs/reports/eval/*` maps seams to ADG MCP evidence and marks any fallback.
- Status: DONE

DoD-3: Whole-spine replay smoke run works.
- Evidence: replay command exits 0 and emits a receipt for at least one pinned scenario.
- Status: DONE

DoD-4: X2 and X1D trust suites fail closed.
- Evidence: focused pytest selectors cover hard-line and stale/no-quorum cases.
- Status: DONE

DoD-5: L6 findings graduate only through review.
- Evidence: staged corpus candidate and review packet artifacts exist; no direct auto-promotion.
- Status: DONE

DoD-6: CI/UWG promotion requires harness evidence.
- Evidence: CI gate and UWG docs/checks require replay, calibration, ADG transport, and baseline receipts.
- Status: DONE

DoD-7: Plan and Notion registration are valid.
- Evidence: format validator passes and Plans DB row is synced after filesystem SSOT updates.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=eval-harness-adg-mcp-open-replan-9c1f2a wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=eval-harness-adg-mcp-open-replan-9c1f2a decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=eval-harness-adg-mcp-open-replan-9c1f2a reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| eval-harness-adg-mcp-replan-a71c9e | Recreated after the Codex ADG MCP transport opened successfully. |
| eval-harness-spine-adg-closeout-6f2a9c | Earlier plan captured the same harness scope before the transport-open evidence was available. |

---

## Marker Quick Reference

Wave lifecycle markers:
```
PLAN_CREATED: slug=eval-harness-adg-mcp-open-replan-9c1f2a path=plans/eval-harness-adg-mcp-open-replan-9c1f2a.md status=Not Started
WAVE_START: plan=eval-harness-adg-mcp-open-replan-9c1f2a wave=<N>
WAVE_COMPLETE: plan=eval-harness-adg-mcp-open-replan-9c1f2a wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=eval-harness-adg-mcp-open-replan-9c1f2a phase=<W1.1>
PLAN_COMPLETE: plan=eval-harness-adg-mcp-open-replan-9c1f2a note="<final outcome>"
```
