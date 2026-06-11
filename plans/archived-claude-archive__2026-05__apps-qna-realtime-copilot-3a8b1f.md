---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-qna-realtime-copilot-3a8b1f.md'
original_relative_path: '_archive\\2026-05\\apps-qna-realtime-copilot-3a8b1f.md'
source_sha256: 60b7c08692e548b585cb3a6b0f070f54348aebf4e12bcdda61fc64ffa08705fe
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna Real-Time Copilot Companion App

**Slug**: `apps-qna-realtime-copilot-3a8b1f`
**Status**: not-started (scaffold only)
**Owner**: TBD
**Created**: 2026-04-30
**Parent**: `apps-qna-rag-skills-alignment-7d2c4e` (Wave 5 NEXT_STEP origin)

> ⛔ **This plan has an unresolved ethics conflict that must be addressed before
> any code lands.** Card 18 (`apps_qna/templates/18_ethics_and_disclosure.md.j2`)
> explicitly states this prep tool is **not** a real-time copilot. Implementing
> a real-time companion contradicts that boundary unless the disclosure stance
> is rewritten and an ADR captures the new norm. **Phase 0 (Ethics ADR) is
> mandatory before any other phase starts.**

## Goal

A rehearsal-time companion that supports the candidate during **mock
interviews and self-drilling**, distinct from the live-interview prep cards.
Voice-driven; no covert assistance during real interviews.

## Use cases (in scope)

- Solo rehearsal: candidate practices answers aloud; companion times each
  answer and surfaces drift codes (P-DRIFT, P-LATENCY, P-OVERPOLISH) per
  `apps_qna/PATHOLOGY_TAXONOMY.md`.
- Mock interview with peer interviewer: companion records, transcribes, and
  scores delivery against the routing manifest.
- Post-rehearsal review: replay timeline + delta-sheet auto-fill into card
  22 (Learnings).

## Use cases (explicitly out of scope)

- ❌ Live-interview audio capture
- ❌ Hidden earpiece / covert text feed
- ❌ Real-time AI generation visible to the candidate during a live interview

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| 0 | 0.1 | Ethics ADR + card 18 reconciliation | 3000 | Todo | ADR merged; card 18 reconciled or split into prep-card / rehearsal-companion sections |
| 1 | 1.1, 1.2 | Audio capture + STT pipeline | 5000 | Todo | Local STT (whisper.cpp or vosk) round-trips a 60-s sample with WER < 0.10 on prepared text |
| 2 | 2.1 | Routing-manifest scorer integration | 3000 | Todo | `SemanticRouter` (Wave 6 of parent plan) wired to score live transcript chunks |
| 3 | 3.1, 3.2 | Pathology detector + delta capture | 4000 | Todo | At least 4 of 9 pathology codes detected automatically from transcript+timing |
| 4 | 4.1 | UI / TUI for replay + review | 3000 | Todo | Rich-based TUI shows route timeline, drift markers, per-answer score |
| 5 | 5.1 | Card 22 auto-fill from review session | 2000 | Todo | After a rehearsal, a draft delta sheet is appended to card 22 |

**Total est. tokens**: ~20k

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|------------:|--------|
| 0.1 | Ethics ADR | `docs/architecture/adr/ADR-NNN-rehearsal-companion-ethics.md`, `apps_qna/templates/18_ethics_and_disclosure.md.j2` | Reconcile prep-vs-companion boundary; explicit disclosure stance; covert-use threat model | 3000 | Todo |
| 1.1 | Local STT engine selection | `apps_qna_realtime/audio/stt.py`, integration test fixtures | whisper.cpp vs vosk vs faster-whisper; latency/WER tradeoff | 3000 | Todo |
| 1.2 | Mic capture loop | `apps_qna_realtime/audio/capture.py` | Cross-platform (sounddevice on Windows; pulseaudio on Linux) | 2000 | Todo |
| 2.1 | Live router | `apps_qna_realtime/router_live.py` | Stream tokens → BoW window → semantic_router.route() | 3000 | Todo |
| 3.1 | Pathology detector | `apps_qna_realtime/pathology.py` | P-LATENCY (timing), P-DRIFT (route shift mid-answer), P-OVERPOLISH (perplexity heuristic) | 2500 | Todo |
| 3.2 | Pathology test fixtures | recorded sample sessions | Need anonymized rehearsal recordings | 1500 | Todo |
| 4.1 | TUI | `apps_qna_realtime/ui/tui.py` (rich.live) | Real-time render without flicker; review mode | 3000 | Todo |
| 5.1 | Card 22 auto-fill | `apps_qna_realtime/learnings_writer.py` | Idempotent append; preserves user edits | 2000 | Todo |

## Gap Register

- **G-RTCO-1**: Card 18 conflict (Wave 0 mandatory).
- **G-RTCO-2**: Local STT dependency selection — none currently in pyproject.
- **G-RTCO-3**: Sample audio fixtures need to be authored; no privacy-safe corpus exists.
- **G-RTCO-4**: Pathology detection thresholds need calibration data — circular dependency with the rehearsal sessions themselves.

## Dependencies

- `apps_qna.router.semantic_router.SemanticRouter` (delivered in parent plan Wave 6)
- `apps_qna.validators.token_budget` (cards stay under cap)
- `apps_qna/PATHOLOGY_TAXONOMY.md` (drift codes)

## Architecture sketch

```text
mic ─► capture loop ─► STT engine ─► token stream
                                          │
                                          ▼
                                  rolling-window BoW
                                          │
                                          ▼
                              SemanticRouter.route()
                                          │
                                          ▼
                              pathology detector
                                  │            │
                                  ▼            ▼
                              TUI live    learnings writer (post-session)
                                          │
                                          ▼
                              card 22 delta sheet
```

## Verification

- Wave 0: ADR review by user; explicit `card 18 status: reconciled` line in commit body.
- Each subsequent wave: pytest unit + integration tests; manual smoke with one rehearsal recording.

## Provenance

ADG Provenance: not applicable (greenfield app, no cross-layer refactoring).

## Out-of-Scope (NEXT_STEP)

- Cloud-hosted STT (privacy boundary)
- Multi-candidate / multi-tenant mode
- Integration with calendar / interview-scheduling tools


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_qna real-time copilot scaffold

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_dependency_cone_risk` — blast-radius / cone risk for refactor candidates.
3. `mv_hotspot_centrality` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `resolves_callsite` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.

**Rationale**: Real-time copilot composes existing semantic_router + pack_loader; refactor risk = orchestrator coupling growth.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_qna real-time copilot scaffold (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_qna real-time copilot scaffold` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

