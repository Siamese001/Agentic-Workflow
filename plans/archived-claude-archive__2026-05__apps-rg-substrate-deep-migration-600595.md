---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-substrate-deep-migration-600595.md'
original_relative_path: '_archive\\2026-05\\apps-rg-substrate-deep-migration-600595.md'
source_sha256: 76d7a7d28fe9b3efbf2f4405188e1f5cc0a1b27ddc15f80048004db252bfb2af
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-substrate-deep-migration-600595
plan_type: refactor
---

# apps_rg Substrate Deep Migration — Real Adapters + Parity Fixture

Replaces the thin passthrough adapters in `apps_rg/engines/hop_pipeline_adapters.py` (landed in plan `apps-hop-substrate-f7751b` Wave 3) with full `BaseModel`↔`dict` marshaling so the substrate path can become the primary apps_rg runtime.

---

## Context (SCQA)

- **Situation** — apps_rg is "migrated" per the CI gate but its substrate path (`RgHopOrchestrator`) is passthrough: the 7 adapters in `apps_rg/engines/hop_pipeline_adapters.py` emit marker dicts and do not call the real `BaseRGEngine` subclasses. `RgResumeOrchestrator.run()` remains the only runtime path with real Qwen wiring, repo signals, and heal cycle.
- **Complication** — The apps_rg engines inherit from `BaseRGEngine` with `execute(input_data: BaseModel) -> BaseModel`, incompatible with the substrate's `execute(context: dict) -> dict` contract. Making the substrate path primary requires: (a) per-stage marshaling, (b) byte/JSON-equivalence parity test against `RgResumeOrchestrator.run()` so the migration is provably safe, (c) Qwen gateway handoff at HOP3, (d) repo_signals context contribution outside the 7-stage walk.
- **Question** — How do we replace the thin apps_rg adapters with real ones that preserve `RgResumeOrchestrator.run()` behavior byte-for-byte, enabling `RgHopOrchestrator` to become the primary runtime?
- **Answer** — Golden fixture first (capture 3 representative resume inputs → outputs from current `RgResumeOrchestrator.run()`). Then replace adapters one at a time, each gated on a per-stage parity test. Then promote `RgHopOrchestrator` to primary; demote `RgResumeOrchestrator` to a shim that delegates to the substrate.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Golden fixture + parity harness | 3 input/output pairs, harness script | A | ~4K 🟢 |
| Wave 2 | Real adapters per stage | 7 adapters × marshal + call + unmarshal | B | ~8K 🟢 |
| Wave 3 | Qwen + repo_signals context integration | HOP3 gateway handoff; context.contribute_repo_signals | C | ~3K 🟢 |
| Wave 4 | Promote substrate to primary | `RgResumeOrchestrator.run` → shim delegating to `RgHopOrchestrator` | D | ~3K 🟢 |

**Total: ~18K tokens across 4 waves**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Capture 3 golden fixtures from current `RgResumeOrchestrator.run()` | `tests/golden/apps_rg/fixtures/` (NEW) | GAP-1 | ~2K | 🔲 TODO |
| 1.2 | Write parity harness | `tests/golden/apps_rg/test_resume_generation_parity.py` (NEW) | GAP-2 | ~2K | 🔲 TODO |
| 2.1-2.7 | Per-stage real adapter (Clerk, Enrich, Generation, FactCheck, Gate, Optimizer, Diagnostics) | `apps_rg/engines/hop_pipeline_adapters.py` (edit) + per-stage parity test | GAP-3 | ~8K | 🔲 TODO |
| 3.1 | Qwen gateway handoff at HOP3 | `apps_rg/engines/hop_pipeline_adapters.py` HOP3 (edit) | GAP-4 | ~2K | 🔲 TODO |
| 3.2 | repo_signals context contribution | `apps_rg/reasoning/RgHopOrchestrator.py` (edit) | GAP-5 | ~1K | 🔲 TODO |
| 4.1 | `RgResumeOrchestrator.run` becomes shim | edit + deprecation warning | GAP-6 | ~2K | 🔲 TODO |
| 4.2 | Final end-to-end parity run across all 3 fixtures | tests | — | ~1K | 🔲 TODO |

---

## Gap Register

**GAP-1**: No golden fixture exists for apps_rg. Must capture from current runtime before touching anything.
**GAP-2**: Parity harness must compare nested Pydantic structures; JSON-normalize for stable diffs.
**GAP-3**: Each `BaseRGEngine` has its own Pydantic input/output pair — 7 marshaling pairs to implement.
**GAP-4**: `agentic_core/L3_orchestration/inference/qwen_vllm/` gateway is async; substrate is sync. Needs `asyncio.run` wrapper or sync-facade per apps_rg precedent.
**GAP-5**: repo_signals is collected per-run in `RgResumeOrchestrator`, not per-stage. Substrate path needs a pre-HOP1 step to populate context.
**GAP-6**: Existing callers of `RgResumeOrchestrator.run()` must continue working — shim preserves API.

---

## Success Criteria

- [ ] 3 golden fixtures captured, committed, deterministic.
- [ ] 7 real adapters pass per-stage parity (checkpoint output JSON-equivalent to `RgResumeOrchestrator` intermediate state).
- [ ] Full-pipeline parity test green across 3 fixtures.
- [ ] `RgResumeOrchestrator.run()` is a ≤20-line shim delegating to `RgHopOrchestrator`.
- [ ] `apps_rg/engines/hop_pipeline_adapters.py` has zero passthrough `_passthrough` calls remaining.

---

## Rollback Strategy

Per-wave. Thin adapters in HEAD remain the safe fallback until Wave 4 promotes substrate to primary.

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
