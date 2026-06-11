---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\retrieval-eval-cron-and-dashboard.md'
original_relative_path: 'retrieval-eval-cron-and-dashboard.md'
source_sha256: 029ff897cd9126e7a04dfa9a8313ac4237d8066547a413b6c14f153df3e7e3ea
recovered_status: LOST_RECOVERED
last_commit: '2dd2ba7efc3'
last_commit_date: '2026-05-15 14:13:16 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W5.2 — Nightly Retrieval-Eval CI + Notion Dashboard

**Plan**: `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Wave/Phase**: W5.2
**Date**: 2026-04-24
**Status**: Spec — implementation deferred
**Relates-to**: ADR-061 (golden set + RAGAS harness), ADR-055 (provenance), ADR-060 (reflective retrieval)
**Tier**: T2 (spec, no code changes)

---

## 1. Purpose

ADR-061 declares **what** the retrieval golden set + RAGAS harness measure. This document specifies **how** the harness gets scheduled, monitored, and surfaced to humans. Three pieces:

1. **Cron entry** — what runs, when, where the artifacts land.
2. **Regression-detection logic** — how a "regression" is defined deterministically.
3. **Notion dashboard** — what humans see, where, and on what cadence.

## 2. Cron Entry

`tools/eval/cron_retrieval_eval.py` (new) is the single entry point.

| Mode | Cadence | Wall-clock budget | Cells covered |
|---|---|---:|---|
| `--slice` | nightly 03:00 UTC | ≤ 5 min | diagonal: ADR-recommended cell + each axis default |
| `--full`  | weekly Sunday 04:00 UTC | ≤ 60 min | full sweep (4 × 6 × 2 × 4 = 192 cells per ADR-061 §4) |
| `--smoke` | on every commit touching `tools/eval/`, `agentic_core/knowledge/retrieval/`, or `data/eval/golden/` | ≤ 90 s | 10-pair fixture, RAGAS off |
| `--ad-hoc` | manual | bounded by `--cells` flag | operator-chosen subset |

Scheduling on Windows: `schtasks` registers the nightly + weekly entries pointing at the repo's pwsh activator. On WSL/Linux: `cron` or `systemd --user` timer. The script is OS-agnostic; the registration script
`ops_scripts/cron/install_retrieval_eval_cron.py` (new) handles both.

Pre-flight gate (cron will not start if any are red):
- `mcp1_adg_health` returns healthy.
- `data/eval/golden/retrieval/*.jsonl` files present, all rows schema-valid.
- `config/retrieval/calibration_manifest.yaml` present, hash matches the prior green run within an allowed-drift window.

## 3. Artifacts Layout

```
artifacts/eval/retrieval/
├── runs/
│   ├── <run_id>.json                  # full per-cell metrics, replay_id, calibration manifest hash
│   └── <run_id>.summary.md            # human-readable; linked from Notion
├── history.jsonl                      # one line per run (run_id, mode, started_at, gates_passed, regressions[])
├── current_baseline.json              # last-known-green per metric; updated atomically on green run
└── badges/
    └── nightly.json                   # for any future README badge consumer
```

`run_id` = `<UTC-timestamp>_<mode>_<calibration_hash[:8]>`. Stable, sortable, dedup-safe.

## 4. Regression-Detection Logic

A "regression" is **never** a single-run metric drop — that would alarm-storm on grader stochasticity. The detector uses a 3-run rolling median against `current_baseline.json`:

```
regression(metric) iff
  median(last_3_runs[metric]) <  baseline[metric] - tolerance[metric]
```

Per-metric tolerances (ADR-061 §5 acceptance gates):

| Metric | Tolerance |
|---|---|
| Recall@20 | -2 percentage points |
| Recall@5  | -3 percentage points |
| MRR@10    | -0.03 |
| nDCG@10   | -0.03 |
| Context-precision | -0.03 |
| Context-recall    | -0.03 |
| Abstain-precision (reflective on) | -0.05 |
| Provenance-mismatch count | strict zero |

A green run **promotes** itself to `current_baseline.json` only if **all gates pass**. A run with any regression freezes the baseline (no demotion) and posts to Notion.

Manual override: `--accept-baseline=<run_id>` — operator endorses a non-green run as the new baseline (e.g. after a deliberate model swap). Logged with operator initials in `history.jsonl`.

## 5. Notion Dashboard Surfaces

Two existing Notion surfaces are used; one new page is added.

### 5.1 Wave/Phase Convergence — regression rows
On regression, post a row with:
- Phase Title: `[EVAL-REGRESSION] <metric_name> on <golden_corpus>`
- Phase ID: derived from `run_id`
- Wave ID: `W-EVAL`
- Sub-Wave: `EVAL-AUTO`
- Status: `Todo`
- Plan File: `chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
- Evidence: median value, baseline value, delta, replay command, run_id, summary.md path.
- P-Band: P2 if any ADR acceptance gate fails; else P3.
- Auto-routing: identical pattern to `post_cursor_agent_deferred_scope_capture.py` (§Hook reuse below).

### 5.2 Backlog Snapshot — eval health pin
The pre-rendered Backlog Snapshot page (per AGENTS.md) gains a top section:
- Last green nightly: `<run_id>` at `<timestamp>`
- Open eval regressions: `<count>` with links to rows
- Next scheduled full sweep: `<timestamp>`
The `tools/notion/snapshot_renderer.py` is extended to read `current_baseline.json` and `history.jsonl` to populate this section. Ships as a one-shot patch; no new database.

### 5.3 New page: Retrieval-Eval Trends (optional, deferred)
A weekly-rendered narrative page summarizing trend lines per metric. Source: `history.jsonl` last 30 entries, rendered by an extension to `snapshot_renderer.py`. Defer until W5.2 v1 is stable; not required for v1 acceptance.

## 6. Hook Reuse — No New Hook

`post_cursor_agent_adr_registry_capture.py` (W1.2 follow-up) is the model: a fail-open Python script that detects a marker, queries Notion for dedup, posts on miss. The eval-regression poster is a **non-hook** scheduled-task companion that:

- Reads `history.jsonl` after the cron run finishes.
- Issues one `mcp6_API-post-page` per regression via the Notion REST API directly (not via MCP — same urllib pattern as the existing capture hooks). Rationale: the cron runs outside Cursor Agent's response envelope, so the SDK race the MCP serialization rule guards against doesn't apply.

Implementation lives at `tools/eval/post_eval_regressions_to_notion.py` (new). Imports nothing new; mirrors `post_cursor_agent_adr_registry_capture.py`'s urllib-only stance.

## 7. CI Integration (`--smoke`)

Smoke runs gate every commit touching the retrieval surface. Wired into the existing pre-commit + CI pipeline:

`.pre-commit-config.yaml`:
```
- id: retrieval-eval-smoke
  name: retrieval eval smoke
  entry: python tools/eval/cron_retrieval_eval.py --smoke
  language: system
  files: ^(tools/eval/|agentic_core/knowledge/retrieval/|data/eval/golden/)
  pass_filenames: false
```

GitHub Actions (`adg-ci-gates.yml` or sibling workflow): step matching the same trigger paths. Smoke gate failure blocks merge.

## 8. Operational Knobs

| Env var | Default | Effect |
|---|---|---|
| `RETRIEVAL_EVAL_DISABLE` | `0` | `1` skips all cron runs (fail-open) |
| `RAGAS_FULL` | `0` | `1` enables LLM-faithfulness step (weekly only) |
| `RETRIEVAL_EVAL_NOTION_OFF` | `0` | `1` skips Notion posts (artifacts still written) |
| `RETRIEVAL_EVAL_OPERATOR` | `<user>` | recorded in `history.jsonl` for ad-hoc / accept-baseline events |

## 9. Failure Modes & Mitigations

| Failure | Detection | Mitigation |
|---|---|---|
| Golden set file missing | Pre-flight gate | Cron skips, posts `[EVAL-INFRA]` row with Phase Title pointing at the missing file |
| ADG MCP unhealthy | Pre-flight gate | Cron skips; not a regression event |
| GPU box offline | Cron timeout | Run aborts; `history.jsonl` records `aborted_no_gpu`; baseline unchanged |
| Notion API down | urllib raises | Posts queue locally in `artifacts/eval/retrieval/notion_pending.jsonl`; next run drains queue |
| Stochastic LLM grader noise (RAGAS_FULL) | 3-run median | Suppresses single-run flake; consistent 3-run dip alerts |
| Operator-induced baseline drift | `--accept-baseline` flag misuse | Audit trail in `history.jsonl`; quarterly review of accept-baseline events |

## 10. Acceptance

This spec is implemented and accepted when:

1. Cron entries registered on the GPU host; `python tools/eval/cron_retrieval_eval.py --smoke` exits 0 in pre-commit.
2. One green nightly run produces `current_baseline.json` with non-empty per-metric values.
3. One synthetic regression (manually injected by lowering a top-K cap) is detected and posted to Wave/Phase Convergence within one cycle.
4. Backlog Snapshot regeneration includes the eval-health section.

## 11. References

- ADR-061 — golden set + RAGAS harness contract
- AGENTS.md — Notion Workspace Map, auto-routing rules
- `.windsurf/scripts/post_cursor_agent_adr_registry_capture.py` — urllib-only Notion poster pattern reused here
- `tools/notion/snapshot_renderer.py` — backlog snapshot regeneration
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
