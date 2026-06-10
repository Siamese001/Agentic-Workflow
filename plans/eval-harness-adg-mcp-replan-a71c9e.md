---
plan_id: eval-harness-adg-mcp-replan-a71c9e
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "TBD before W2 implementation"
dod_exempt: false
supersedes: [eval-harness-spine-adg-closeout-6f2a9c]
---

# Eval Harness ADG MCP Replan

Recreate the eval-harness rectification plan with ADG MCP transport health as the first-class prerequisite: Codex must prove an open ADG MCP transport, not merely a healthy local backend, before execution waves claim ADG-backed closure.

> **plan_id discipline**: `plan_id` matches the filename stem `eval-harness-adg-mcp-replan-a71c9e`. Wave markers use `plan=eval-harness-adg-mcp-replan-a71c9e`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-10

---

## Context (SCQA)

- **Situation** - The proposed eval harness wraps the runtime spine at four seams: whole-spine replay, X1D judge calibration, L6 exhaust-to-corpus promotion, and X2 micro-evals. The repo already has partial assets for those seams: capability regression tooling, X1D panel runners, X2 validators, exit evaluation surfaces, and L6 flywheel components. The ADG backend is healthy through the repo-local handler path with snapshot `06082026_1212`, SQLite healthy, Redis healthy, and graph projection fresh.
- **Complication** - The exposed Codex ADG MCP transport is closed: `mcp__adg_sqlite.adg_runtime_info`, `adg_health`, and `adg_reopen_connections` return `Transport closed`. Local handler calls can prove backend health but do not prove the agent-facing MCP transport. The previous plan captured this as a caveat; this successor makes it a blocking W1 prerequisite.
- **Question** - How do we rectify the proposed eval harness gaps while ensuring ADG evidence comes from an open, agent-facing MCP transport or an explicitly marked degraded fallback?
- **Answer** - First reopen and prove Codex ADG MCP transport lifecycle, then use ADG to order the harness work: whole-spine replay, X2 micro-evals, X1D calibration trust, L6 corpus flywheel, and CI/UWG promotion binding.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Open and prove ADG MCP transport | ~8K | Codex host can be restarted or transport lifecycle can be supervised externally | TODO | `mcp__adg_sqlite.adg_health` returns full mode, runtime PID/nonce recorded, local fallback not needed |
| W2 | W2.1, W2.2, W2.3 | ADG-backed harness gap matrix | ~10K | ADG snapshot `06082026_1212` or newer remains queryable | TODO | Gap matrix maps harness seams to ADG nodes/views, with stale/fallback markers explicit |
| W3 | W3.1, W3.2, W3.3 | Whole-spine replay harness | ~35K | Existing apps spine fixtures can run offline without provider leakage | TODO | Pinned scenarios replay U0-to-L6 receipts and enforce pass-rate/baseline gates |
| W4 | W4.1, W4.2, W4.3 | X2 and X1D trust suites | ~30K | Human-label corpus can be staged incrementally | TODO | X2 micro-evals fail closed; X1D judges carry calibration snapshot and stale/no-quorum disqualification |
| W5 | W5.1, W5.2, W5.3 | L6 corpus flywheel and promotion binding | ~28K | L6 exhaust packages are sealed and trace-bound | TODO | L6 findings graduate through review; CI/UWG promotion cites regression and judge receipts |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Reopen Codex ADG MCP transport | TODO |
| W1.2 | Prove SQLite, Redis, graph projection, and runtime identity | TODO |
| W1.3 | Add transport-lifecycle gap evidence and fallback rules | TODO |
| W2.1 | Query ADG eval/replay/exit/gateway views through MCP | TODO |
| W2.2 | Map proposed harness seams to target nodes and files | TODO |
| W2.3 | Publish ADG gap matrix artifact | TODO |
| W3.1 | Define pinned scenario and replay receipt schemas | TODO |
| W3.2 | Implement whole-spine offline replay runner | TODO |
| W3.3 | Add baseline comparison and promotion threshold gates | TODO |
| W4.1 | Build X2 micro-eval fixture families | TODO |
| W4.2 | Align X1D calibration metric and threshold semantics | TODO |
| W4.3 | Bind judge snapshot IDs to every X1D score | TODO |
| W5.1 | Wire L6 exhaust packages into staged corpus candidates | TODO |
| W5.2 | Add review/graduation workflow for capability suites | TODO |
| W5.3 | Bind CI/UWG/Notion evidence and closeout checks | TODO |

---

## Transport State At Plan Creation

`mcp__adg_sqlite` transport status:
- `adg_runtime_info`: `Transport closed`
- `adg_health`: `Transport closed`
- `adg_reopen_connections`: `Transport closed`

Repo-local backend fallback status:
- `health.status`: `ok`
- `mode`: `full`
- `sqlite`: `healthy`
- `redis`: `healthy`
- `snapshot`: `06082026_1212`
- `sqlite_path`: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06082026_1212.sqlite`
- `graph_projection`: available and fresh
- `local reopen`: `reopened=true`, `noop=true`, because snapshot path and mtime were unchanged

Decision:
- Local handler health is acceptable only as `DEGRADED_FALLBACK`.
- W1 cannot be marked complete until the Codex-exposed MCP transport itself returns `adg_health` and `adg_runtime_info`.
- If Codex does not expose host-level MCP restart controls, W1 must document the required external restart path and prove it with changed PID/nonce.

---

## Out Of Scope

- Letting offline eval waive a live X2, X1D, X3, Exit, or UWG verdict.
- Replacing app-specific validators with one generic evaluator.
- Treating local SQLite reads as equivalent to an open MCP transport.
- Auto-promoting L6 findings into golden suites without review.
- Re-adding unrelated dormant MCP servers as part of this plan.

---

## Wave 1 - Open And Prove ADG MCP Transport

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - Transport health and process lifecycle work only.

**Phases**:
- **W1.1** - Reopen Codex ADG MCP transport | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Prove SQLite, Redis, graph projection, and runtime identity | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** - Add transport-lifecycle gap evidence and fallback rules | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `mcp__adg_sqlite.adg_runtime_info` returns `status=ok` with PID, startup nonce, stack fingerprint, snapshot ID, and Redis enabled.
- `mcp__adg_sqlite.adg_health` returns `mode=full`, `sqlite=healthy`, `redis=healthy`, and fresh graph projection.
- `mcp__adg_sqlite.adg_reopen_connections` and `adg_reload` behavior are documented as backend lifecycle, not host process restart.
- If host restart is external, the exact restart procedure is documented and verified by changed PID/nonce.

---

## Wave 2 - ADG-Backed Harness Gap Matrix

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** - Query ADG eval/replay/exit/gateway views through MCP | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Map proposed harness seams to target nodes and files | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** - Publish ADG gap matrix artifact | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Matrix covers the four proposed seams: whole-spine replay, X1D judge calibration, L6 exhaust corpus, and X2 micro-evals.
- Matrix includes ADG evidence for eval coverage, replay links, exit disposition, determinism/provenance drift, and gateway bypass checks.
- Every row records whether evidence came from open MCP or `DEGRADED_FALLBACK`.

---

## Wave 3 - Whole-Spine Replay Harness

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** - Define pinned scenario and replay receipt schemas | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Implement whole-spine offline replay runner | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** - Add baseline comparison and promotion threshold gates | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Pinned scenarios include SHA-256 fixture identity for JD, briefing, context, policy, and expected receipt class.
- Replay runner executes the runtime spine path rather than only reclassifying stored labels.
- Promotion blocks unless pass-rate and baseline regression checks meet configured thresholds.

---

## Wave 4 - X2 And X1D Trust Suites

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** - Build X2 micro-eval fixture families | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Align X1D calibration metric and threshold semantics | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** - Bind judge snapshot IDs to every X1D score | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- X2 micro-evals include fixtures for numeric precision, sentence-count boundaries, leakage/self-check separation, and mock/unknown hard lines.
- X1D calibration chooses one statistic or an explicit conversion between raw agreement and Cohen kappa.
- Stale judges, no quorum, missing calibration snapshot, and provider-mode mismatch cannot clear X1D.

---

## Wave 5 - L6 Corpus Flywheel And Promotion Binding

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** - Wire L6 exhaust packages into staged corpus candidates | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - Add review/graduation workflow for capability suites | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** - Bind CI/UWG/Notion evidence and closeout checks | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- L6 packages graduate only after review and deterministic replay evidence.
- CI gates require harness evidence for touched spine surfaces.
- UWG and Notion status updates cite regression receipt, X1D calibration receipt, and ADG MCP transport receipt.

---

## Execution Details

### W1.1 - Reopen Codex ADG MCP Transport
**Scope**: Restore the agent-facing MCP transport, not just local backend imports.

**Commands**:
```bash
python -c "print('Use Codex MCP host restart or app restart; then verify with mcp__adg_sqlite.adg_runtime_info')"
```

### W1.2 - Prove Backend Through MCP
**Scope**: Verify runtime identity and health through the exposed ADG MCP.

**Commands**:
```bash
# MCP calls: adg_runtime_info, adg_health, adg_status, adg_nodes_by_layer
```

### W1.3 - Document Fallback Boundary
**Scope**: Make direct SQLite/local handler use visible.

**Commands**:
```bash
python -c "import os,json; os.environ['PYTHONPATH']='.'; from tools.adg.mcp import tool_handlers as h; print(json.dumps(h.adg_health(), default=str))"
```

### W2.1 - Query ADG Views
**Scope**: Use MCP first for views and only fall back with a marker.

**Commands**:
```bash
# MCP preferred: adg_violations, adg_nodes_by_file, adg_edge_fanin, adg_edge_fanout
```

### W2.2 - Map Harness Seams
**Scope**: Tie each proposed seam to concrete runtime files, tests, and ADG nodes.

**Commands**:
```bash
rg -n "X1D|X2|flywheel|replay|capability_regression|exit_eval" tools agentic_core apps_rg apps_shared tests
```

### W2.3 - Publish Matrix
**Scope**: Write evidence artifact under `docs/reports/eval/`.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W3.1 - Replay Schema
**Scope**: Define fixture and receipt schemas.

**Commands**:
```bash
python -m py_compile tools/eval/run_capability_regression.py
```

### W3.2 - Replay Runner
**Scope**: Execute runtime spine offline with provider-safe fixtures.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q
```

### W3.3 - Baseline Gates
**Scope**: Compare candidate to baseline and enforce thresholds.

**Commands**:
```bash
python tools/eval/run_capability_regression.py --help
```

### W4.1 - X2 Micro-Evals
**Scope**: Add targeted validator fixtures.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "x2 or validator"
```

### W4.2 - X1D Calibration Alignment
**Scope**: Align kappa/agreement semantics and stale judge disqualification.

**Commands**:
```bash
rg -n "kappa|agreement|calibration|judge" .github tools agentic_core apps_rg tests
```

### W4.3 - Judge Snapshot Binding
**Scope**: Ensure every score carries calibration snapshot and provider mode.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "x1d or judge"
```

### W5.1 - L6 Exhaust Staging
**Scope**: Route shadow eval packages into reviewable corpus candidates.

**Commands**:
```bash
rg -n "flywheel|shadow|exhaust|graduate" agentic_core tools tests
```

### W5.2 - Review And Graduation
**Scope**: Add review packets and deterministic promotion rules.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests -q -k "flywheel or corpus or eval"
```

### W5.3 - Promotion Binding
**Scope**: Bind CI/UWG/Notion evidence to the same receipt schema.

**Commands**:
```bash
python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/eval-harness-adg-mcp-replan-a71c9e.md
python scripts/governance/verify_codex_backup.py
```

---

## Gap Register

**GAP-1: Codex ADG MCP transport is closed**
- Evidence: `adg_runtime_info`, `adg_health`, and `adg_reopen_connections` return `Transport closed`.
- Impact: agent-facing ADG evidence cannot be claimed even though local backend health is green.

**GAP-2: Backend health and transport health are conflated**
- Local handler reports full health, but the exposed MCP channel is dead.
- Impact: plans can overstate ADG availability unless evidence source is recorded.

**GAP-3: Whole-spine replay is not yet the harness runner**
- Existing regression flow scores stored fixtures rather than replaying the full runtime spine.
- Impact: promotion can pass without proving U0-to-L6 behavior.

**GAP-4: Baseline comparison is not structurally enforced**
- Proposed rig requires promotion blocked unless pass-rate and baseline criteria hold.
- Impact: absolute pass-rate can hide regressions.

**GAP-5: X2 micro-evals are not first-class**
- Validator edge cases exist in scattered tests rather than a named gate suite.
- Impact: fact-checker/gate regressions may not block promotion.

**GAP-6: X1D calibration metric semantics drift**
- Raw agreement and kappa thresholds appear in separate surfaces.
- Impact: stale or under-calibrated judges may count toward quorum.

**GAP-7: L6 exhaust-to-corpus is not end-to-end**
- Shadow eval findings do not automatically produce reviewable, trace-bound corpus candidates.
- Impact: repeated session failures are not reliably frozen into regression scenarios.

**GAP-8: Replay and exit disposition coverage are not ADG-visible enough**
- App spine adapters and exit surfaces have replay/disposition gaps in ADG evidence.
- Impact: harness seams cannot be proven structurally.

---

## Definition of Done

DoD-1: ADG MCP transport is open and proven through Codex.
- Evidence: `mcp__adg_sqlite.adg_runtime_info` and `mcp__adg_sqlite.adg_health` return `status=ok`; PID/nonce and snapshot ID are recorded.
- Status: TODO

DoD-2: ADG backend remains healthy after transport restart.
- Evidence: `adg_health` reports `mode=full`, `sqlite=healthy`, `redis=healthy`, and fresh graph projection.
- Status: TODO

DoD-3: Harness gap matrix is ADG-backed.
- Evidence: `docs/reports/eval/*` artifact maps four proposed seams to ADG nodes/views and records evidence source.
- Status: TODO

DoD-4: Replay runner executes the runtime spine.
- Evidence: smoke command exits 0 and produces replay receipts for at least one pinned scenario.
- Status: TODO

DoD-5: X2/X1D trust gates fail closed.
- Evidence: targeted pytest selectors for X2 and X1D pass and include stale/no-quorum/mock/unknown hard-line cases.
- Status: TODO

DoD-6: L6 findings can graduate into reviewed regression scenarios.
- Evidence: review packet and staged corpus candidate artifacts exist, with no direct auto-promotion.
- Status: TODO

DoD-7: Plan and Notion registration are valid.
- Evidence: format validator passes and Plans DB row has `Status=Not Started`, `Exists On Disk=true`, and `Plan File Path=plans/eval-harness-adg-mcp-replan-a71c9e.md`.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=eval-harness-adg-mcp-replan-a71c9e wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=eval-harness-adg-mcp-replan-a71c9e decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=eval-harness-adg-mcp-replan-a71c9e reason="<summary>" added="<waves/phases>" authorized="yes"
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
| eval-harness-spine-adg-closeout-6f2a9c | Recreated with Codex ADG MCP transport as a first-class W1 prerequisite after repeated `Transport closed` failures. |

---

## Marker Quick Reference

Wave lifecycle markers:
```
PLAN_CREATED: slug=eval-harness-adg-mcp-replan-a71c9e path=plans/eval-harness-adg-mcp-replan-a71c9e.md status=Not Started
WAVE_START: plan=eval-harness-adg-mcp-replan-a71c9e wave=<N>
WAVE_COMPLETE: plan=eval-harness-adg-mcp-replan-a71c9e wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=eval-harness-adg-mcp-replan-a71c9e phase=<W1.1>
PLAN_COMPLETE: plan=eval-harness-adg-mcp-replan-a71c9e note="<final outcome>"
```
