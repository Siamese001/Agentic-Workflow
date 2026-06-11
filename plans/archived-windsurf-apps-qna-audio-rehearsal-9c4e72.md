---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-qna-audio-rehearsal-9c4e72.md'
original_relative_path: 'apps-qna-audio-rehearsal-9c4e72.md'
source_sha256: a908c05a23f3578f7c9c19dd0b9a8e91d313176cbe3def859f4066daa7b9532d
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna Audio Rehearsal Integration

**Slug**: `apps-qna-audio-rehearsal-9c4e72`
**Status**: not-started (scaffold only)
**Owner**: TBD
**Created**: 2026-04-30
**Parent**: `apps-qna-rag-skills-alignment-7d2c4e` (Wave 5 NEXT_STEP origin)
**Depends on**: `apps-qna-realtime-copilot-3a8b1f` Wave 1 (audio capture + STT)

## Goal

A focused **self-drilling** loop on top of the realtime companion's audio
+ STT primitives: candidate practices an answer aloud, the system scores
delivery against the matching primary card's expected `answer_shape`, and
emits a per-answer score plus pathology codes.

This is narrower than the full realtime copilot — it has no live-routing
surface, no TUI, no ongoing-session model. It is a **drill** harness.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------:|--------|------------------|
| 1 | 1.1 | Per-answer drill harness | 3000 | Todo | `python -m apps_qna drill --route architecture` records, transcribes, prints score |
| 2 | 2.1 | Answer-shape grader | 3000 | Todo | Grader matches transcript against the route's `answer_shape` segments and reports coverage |
| 3 | 3.1 | Drill log + card 22 auto-append | 2000 | Todo | Each drill appends a row to a per-session log + draft entry to card 22 |
| 4 | 4.1 | Calibration: 10 sample drills | 2000 | Todo | Score distribution looks reasonable on 10 candidate-recorded answers |

**Total est. tokens**: ~10k

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|----------|-------|-------|-------------|------------:|--------|
| 1.1 | Drill harness CLI | `apps_qna/scripts/run_qna.py` (drill subcommand), `apps_qna/drill/` package | Reuse STT engine from realtime-copilot Wave 1; record-N-seconds knob | 3000 | Todo |
| 2.1 | Answer-shape grader | `apps_qna/drill/answer_grader.py` | Each `answer_shape` element is a free-text label; matching needs synonym tolerance | 3000 | Todo |
| 3.1 | Drill log writer | `apps_qna/drill/log_writer.py`, log path `reports/qna/<slug>/drills/<utc>.jsonl` | Idempotent; merges into card 22 without trampling user edits | 2000 | Todo |
| 4.1 | Calibration sample | `apps_qna/drill/calibration/` fixture, eval script | Need 10 candidate-recorded answers (privacy-safe) | 2000 | Todo |

## Gap Register

- **G-DRILL-1**: STT engine selection inherited from realtime-copilot Wave 1 — must be locked there first.
- **G-DRILL-2**: Answer-shape grader is the hardest piece — `answer_shape` items are short labels ("Situation", "Task", "Action", "Result") for STAR but free prose for architecture; synonym lists vary per route.
- **G-DRILL-3**: No labeled training data; grader must be heuristic-first (token overlap + segment ordering), LLM-judge optional.

## Dependencies

- `apps_qna.router.semantic_router.SemanticRouter` (already delivered)
- `apps_qna.config.route_registry` (already delivered)
- `apps_qna_realtime/audio/{stt,capture}.py` (from realtime-copilot plan Wave 1)
- `apps_qna/PATHOLOGY_TAXONOMY.md` (already delivered)

## CLI sketch

```bash
# Drill the architecture answer for 90 seconds with a target spoken delivery
python -m apps_qna drill \
    --route architecture \
    --duration-seconds 90 \
    --pack reports/qna/drew-clements

# Output (sample):
# Recording 90 s ... done
# Transcript: <auto-emitted>
# Route hit:  architecture (expected: architecture) ✓
# Answer-shape coverage: 4/5 (missed: "Product and scale layer.")
# Pathology codes: P-LATENCY (12 s start delay)
# Logged: reports/qna/drew-clements/drills/2026-04-30T15-22Z.jsonl
```

## Verification

- pytest: harness runs end-to-end with a pre-recorded WAV fixture (no live mic).
- Manual: 10 candidate-recorded sample drills → eyeball score distribution.
- Card 22 auto-append: idempotent across two consecutive drills of the same route.

## Provenance

ADG Provenance: not applicable (greenfield app extension).

## Out-of-Scope (NEXT_STEP)

- LLM-judge grading (deferred until heuristic baseline is calibrated)
- Multi-route drill batches in one invocation
- Spaced-repetition scheduling of drills
