# Intelligence Ledgers — Ten-Ledger Rollout

**Plan ID**: `intelligence-ledgers-ten-a7c3e2`
**Status**: Draft — pending operator approval
**Created**: 2026-04-24
**Tier**: T3 (cross-layer: hooks, schemas, skills, calibration scripts, Notion, rules)
**ADG Snapshot**: `adg_indexed_04242026_0513.sqlite` (healthy, SQLite + Redis green)

## Goal

Instrument ten high-leverage agentic-intelligence feedback loops, each patterned after the existing Author-Gate decision ledger (SQLite rows + deterministic scorer + weekly calibration + consulting skill), so every non-trivial decision Cascade makes produces a **(prediction, outcome, latency, metadata)** row that future sessions can query for precedent.

## Non-Goals

- No change to existing Author-Gate decision ledger (`.windsurf/state/refactor_decisions/`) except reuse of its schema/migration patterns.
- No runtime L5 Author-Gate (ADR-023) coupling — this is harness-side telemetry.
- No new MCP server — all ledgers are local SQLite behind existing post-hooks.
- No deletion of any existing capture / audit script.

## Success Criteria (plan-wide)

1. Ten SQLite ledgers exist under `artifacts/ledgers/<ledger-name>.sqlite`, each with DDL in `.windsurf/schemas/`.
2. Every ledger has: writer hook (or wrapper), integrity checker, weekly calibration script, consulting skill, Notion Calibration-DB row.
3. Pre-commit gates enforce schema drift + required-column invariants (reuse `apply_ledger_schema.py` pattern).
4. Each ledger consulted by Cascade at least once in a dogfood session before sign-off.
5. No regression on existing `post_cascade_*` hook chain latency (>20% budget).
6. Weekly calibration report aggregates all ten ledgers into a single Markdown under `docs/reports/calibration/<YYYY-Www>.md`.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W0** | W0.1, W0.2, W0.3 | Shared infrastructure — ledger base schema, writer-hook framework, consulting-skill template, storage convention, Notion Calibration DB | 18,000 | 🟢 | Todo | Base `ledger_base.schema.sql`, `tools/ledgers/writer.py`, `tools/ledgers/consulter.py`, Notion DB created and mapped in AGENTS.md |
| **W1** | W1.1, W1.2 | Priority ledgers — Tool-Routing (§1), Refactor-Outcome (§2) | 22,000 | 🟢 | Todo | Both ledgers writing rows in live sessions; precedent injected into Author-Gate packets |
| **W2** | W2.1, W2.2 | Classification & reliability — Prompt-Classifier (§3), MCP-Invocation (§6) | 20,000 | 🟢 | Todo | Classifier confusion matrix generated; MCP SLO dashboard rendered from rows |
| **W3** | W3.1, W3.2 | Calibration heavyweights — Hotspot-vs-Defect (§4), Deferred-Scope scorer calibration (§5) | 24,000 | 🟡 (needs 30-day window before §4 warms up) | Todo | Formula coefficients proposed for re-weighting in ADR draft |
| **W4** | W4.1, W4.2, W4.3, W4.4 | Safety & efficiency — Guardian-Exemption (§7), Progress-ETA (§8), Memory-Recall hit-rate (§9), Test-Selection efficacy (§10) | 28,000 | 🟢 | Todo | All four writing rows; weekly report surfaces at least one exemption flagged for re-review |
| **W5** | W5.1, W5.2, W5.3 | Governance & unification — unified weekly calibration report, consulting-skills rollout audit, sunset/retirement criteria per ledger, ADR | 14,000 | 🟢 | Todo | ADR filed; `RULES_INDEX.md` + AGENTS.md updated; pre-commit gate enforces ledger-write discipline |

**Total estimated tokens**: ~126,000 (spread across 6 waves; no single wave exceeds RED 🔴 threshold of 32k).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| **W0.1** | Ledger base schema + storage convention | `.windsurf/schemas/ledger_base.schema.sql` (new), `tools/ledgers/__init__.py` (new), `tools/ledgers/schema_registry.py` (new), `artifacts/ledgers/.gitkeep` (new), `.gitignore` patch | Need shared columns (`event_id`, `event_kind`, `ts_utc`, `repo_area`, `prediction_json`, `outcome_json`, `latency_ms`, `score`, `metadata_json`) that every ledger inherits; decide whether one DB per family or one unified | 6,000 | Todo |
| **W0.2** | Writer-hook framework + consulter skill template | `tools/ledgers/writer.py` (new — thread-safe append, FTS5 on `event_kind`), `tools/ledgers/consulter.py` (new — precedent lookup w/ strong/suggestive verdict shape), `.windsurf/skills/ledger-consulter/SKILL.md` (new — reusable template), migration util extending `apply_ledger_schema.py` | Mirror existing `refactor-decision-memory` skill shape; atomic-write + file-lock for concurrent post-hook writes | 7,000 | Todo |
| **W0.3** | Notion Calibration DB + AGENTS.md mapping | New Notion database under workspace; row-per-ledger with fields (Ledger Name, Purpose, Writer Hook, Consulting Skill, Row Count, Last Calibrated, Formula Version, Status); patch `AGENTS.md` Notion Workspace Map block; regenerate Quick Reference | Requires one-time Notion API create-database call; DB ID must be committed to `mcp_config.json` referenced docs | 5,000 | Todo |
| **W1.1** | Tool-Routing ledger (§1) | `artifacts/ledgers/tool_routing.sqlite`, `.windsurf/schemas/tool_routing_ledger.schema.sql`, extend `post_cascade_adg_audit.py` to log **all** retrieval tool calls (not just violations), add `tools/ledgers/calibration/tool_routing_calibration.py`, consulting skill `ledger-consulter-tool-routing` | Captures `(query_features, tool_chosen, backend_used, latency_ms, result_count, fallback_triggered, classification_correct)`. Hardest part: classifying `query_features` deterministically — reuse `pre_prompt_classifier.py` signal set. | 11,000 | Todo |
| **W1.2** | Refactor-Outcome ledger (§2) | `artifacts/ledgers/refactor_outcome.sqlite`, `.windsurf/schemas/refactor_outcome_ledger.schema.sql`, new `post_commit_outcome_binder.py` extension (existing file at `.windsurf/scripts/post_commit_outcome_binder.py` — reuse), ADG-snapshot diff to compute `actual_p2_delta`, rollback detector (git log grep within 7d) | Needs snapshot diff tool; links plan slug → wave → commit SHA → P-count delta. `post_commit_outcome_binder.py` already exists — extend not replace. | 11,000 | Todo |
| **W2.1** | Prompt-Classifier accuracy ledger (§3) | `artifacts/ledgers/prompt_classifier.sqlite`, schema DDL, extend `pre_prompt_classifier.py` to write *prediction* row at prompt-start, extend `post_cascade_*` flow to write *outcome* row at response-end (counts edited files, lines, layers from git diff against session-start HEAD), calibration script builds confusion matrix | Session start/end correlation needs stable session_id — reuse `_session_id_shared.py` | 10,000 | Todo |
| **W2.2** | MCP-Invocation ledger (§6) | `artifacts/ledgers/mcp_invocation.sqlite`, schema DDL, wrap every `mcp*_` call via `post_mcp_audit.py` (already exists — extend), record `(server_id, tool_name, latency_ms, retries, hang_bypass_triggered, payload_bytes, response_bytes)`. SLO dashboard generator. | Must not add overhead to critical MCP path — write rows async via queue; reuse `mcp_serialization_violations.jsonl` plumbing. | 10,000 | Todo |
| **W3.1** | Hotspot-vs-Defect ledger (§4) | `artifacts/ledgers/hotspot_defect.sqlite`, schema DDL, new weekly job `ops_scripts/calibration/hotspot_defect_join.py` that joins `mv_hotspot_centrality` top-100 against SC/AP backlog additions and git churn over trailing 30 days, ADR-draft generator that proposes new `layer_multiplier`/`surface_boost` coefficients | Requires 30-day observation window before first useful report — mark WAITING until W0+30d. Can seed from historical git log + ADG snapshot archive. | 12,000 | Todo |
| **W3.2** | Deferred-Scope scorer calibration ledger (§5) | `artifacts/ledgers/deferred_scope_calibration.sqlite`, schema DDL, cron job that polls Wave/Phase Convergence Notion DB for Status flips, records `(row_id, computed_P_band, impact_score, days_to_done, was_reprioritized)`. Calibration script proposes band-threshold tuning. | Need Notion read-only poll on schedule; store last-seen row signature to detect status transitions. | 12,000 | Todo |
| **W4.1** | Guardian-Exemption outcome ledger (§7) | `artifacts/ledgers/guardian_exemption.sqlite`, schema DDL, one-time backfill script scans repo for all `# guardian: allow-*` comments and creates rows, pre-commit hook records NEW exemptions at creation time, post-RCA hook attempts to link RCAs to nearest upstream exemption. | Linking RCA→exemption is heuristic (file + line proximity, stack trace grep); accept precision ≥70%, recall secondary. | 9,000 | Todo |
| **W4.2** | Progress-ETA calibration ledger (§8) | `artifacts/ledgers/progress_eta.sqlite`, schema DDL, extend `tools/progress_display.py` `ProgressReporter.done()` to write final row with predicted_eta vs actual, calibration script computes per-operation overrun ratio. | Only covers operations using `ProgressReporter` — `tqdm` operations excluded v1 unless we wrap. | 6,000 | Todo |
| **W4.3** | Memory-Recall hit-rate ledger (§9) | `artifacts/ledgers/memory_recall.sqlite`, schema DDL, extend `mem_recall_session_start` wrapper to tag recalled entity names into session context, post-response hook scores which entity names appeared in the response text / tool-call args | Entity-name → reference heuristic is weak for paraphrased recall; accept best-effort substring + embedding match (reuse `vector_db`). | 7,000 | Todo |
| **W4.4** | Test-Selection efficacy ledger (§10) | `artifacts/ledgers/test_selection.sqlite`, schema DDL, extend `/adg-test-triage-gate` workflow to record selection rationale, post-test-run capture `pytest --json-report` output, on-failure job maps failing test → file → change-set and answers "was this test in the triage selection?" | Precision needs ground truth — a test that would have caught regression. Approximate via `git bisect`-style replay or accept post-hoc retraining only. | 6,000 | Todo |
| **W5.1** | Unified weekly calibration report | `docs/reports/calibration/<YYYY-Www>.md` generator extending `.windsurf/scripts/generate_calibration_report.py`, aggregates all ten ledgers | Output must stay <6KB for Notion page embed (reuse snapshot-renderer pattern). | 5,000 | Todo |
| **W5.2** | Consulting-skills rollout audit | Verify each of the 10 skills is registered in skills index, linked from at least one always_on rule or workflow, and actually consulted at least once (check ledger-consulter logs) | Some skills may be auto-invoked only by narrow patterns — dogfood session required. | 4,000 | Todo |
| **W5.3** | Governance ADR + rule-index update + sunset criteria | New ADR `ADR-NNN-intelligence-ledgers.md`, update `.windsurf/RULES_INDEX.md` with ledger-consulter family, update `AGENTS.md`, define retirement criteria per ledger (e.g., §6 MCP-Invocation sunsets when MCP race closes, matching §25) | Sunset criteria must be observable and testable. | 5,000 | Todo |

---

## Gap Register

| Gap ID | Description | Severity | Mitigation | Status |
|---|---|---|---|---|
| G1 | §4 Hotspot-vs-Defect requires ≥30d observation window before first real output | Medium | Seed from ADG snapshot archive + git log + SC/AP backlog historical rows; produce backward-looking baseline in W3.1 | Open |
| G2 | §9 Memory-Recall requires fuzzy match between entity name and response text | Low | Accept substring + vector_db semantic match; report precision/recall; tolerate false negatives v1 | Open |
| G3 | §7 Guardian→RCA linkage is heuristic | Medium | Document confidence band per link (direct/probable/weak); don't auto-retire exemptions — surface to operator | Open |
| G4 | Writer-hook framework adds latency to post_cascade chain | Medium | Async queue; hard cap 20% p95 budget; kill-switch env var `LEDGER_WRITER_BYPASS=1` | Open |
| G5 | Windsurf 2.0.67 `post_cascade_response` dispatcher bug may still intermittently drop events | Medium | Reuse `defer.py` / `manual_post_cascade_replay.py` bypass pattern; writer is idempotent on `event_id` | Known upstream |
| G6 | Notion Calibration DB creation requires one-time human-approved API call | Low | Phase W0.3 includes explicit approval step; document DB ID commit to AGENTS.md | Open |
| G7 | Ten parallel SQLite files increase artifact sprawl | Low | Single `artifacts/ledgers/` directory; `.gitignore` excludes `*.sqlite` but tracks `.keep` + schemas | Open |
| G8 | `tqdm`-based progress bars excluded from §8 v1 | Low | Document exclusion; add `tqdm` wrapper in W4.2+1 if demand shown | Open |

---

## ADG_GRAPH_LAYER_EVIDENCE

Ledger writers and consulters will attach to existing L6 observability and L0 routing surfaces. The following ADG graph-layer primitives (materialized views and P-views on snapshot `adg_indexed_04242026_0513.sqlite`) drive **where** hooks plug in and **which** modules become consulters.

### Materialized views consulted (≥3 required; 6 cited)

| MV | Use in this plan |
|---|---|
| `mv_hotspot_centrality` | W3.1 Hotspot-vs-Defect joins top-100 rows against 30-day defect additions to re-weight impact formula. |
| `mv_graph_reverse_dependency_hotspots` | W1.1 Tool-Routing: identifies which ADG nodes are most queried so we know which consumers to update when routing rules change. |
| `mv_debt_concentration_hotspots` | W1.2 Refactor-Outcome: baseline "expected debt reduction per wave" signal for predicted vs actual P-count delta. |
| `mv_exemptions_near_critical_paths` | W4.1 Guardian-Exemption: pre-populates high-risk exemptions for the backfill script; these rows seed the ledger. |
| `mv_path_criticality_rollup` | W3.1: cross-reference for layer_multiplier re-weighting proposal. |
| `mv_critical_path_segments` | W2.2 MCP-Invocation: identifies MCP call sites on critical paths that need strict latency SLOs. |

### Semantic edges relied on

- `flows_to` — used by W1.2 to confirm a changed file's downstream blast radius actually shifted after a wave.
- `emits_side_effect` — used by W4.1 to score exemption risk (side-effecting swallow sites rank higher).
- `writes_to` — used by W2.2 to identify MCP calls that mutate persistent state (require stricter SLO).
- `resolves_callsite` — used by W4.4 test-selection efficacy (which tests actually cover a call site).
- `controls_flow` — used by W3.1 to tighten "defect-prone" definition (violations gated by flow control vs isolated nodes).

### P-view cross-references

| P-view | Relevance |
|---|---|
| `v_p0_apps_direct_infra` | W3.1 baseline: historical defect density in this partition informs coefficient tuning. |
| `v_p1_mis_layered_infra` | W1.2 refactor-outcome test bed: most completed waves targeted this partition; actual deltas are measurable. |
| `v_p2_duplicated_adapters` | W4.4 test-selection: duplicated adapters complicate triage — natural stress test. |
| `v_p3_isolated_experimental` | Explicitly excluded from §4 formula tuning (low real-world risk signal). |

### Layer criticality applied

- Hooks write to `L6_observability` (writer) and `L0_routing` (consulter). Both stay read-only against L1–L5.
- `layer_multiplier` re-weighting proposal (W3.1) is the primary doctrinal output; changes to multipliers require ADR (captured in W5.3).

### Provenance stamp

```
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04242026_0513.sqlite
```

---

## ADG_HOTSPOT_REPORT

This plan adds instrumentation rather than refactoring a hotspot cluster. However, the **writer-hook family** becomes a new centrality node — it will be imported by every `post_cascade_*` hook. Track its fan-in to ensure it does not itself become a P-grade defect magnet.

| Proposed Node | Archetype | Predicted Fan-In at Completion | Layer | Surface Intersections | Mitigation |
|---|---|---:|---|---|---|
| `tools/ledgers/writer.py` | CENTRAL_DEPENDENCY | ~12 (one per hook + one per calibration) | L6 | Observability, State (writes ledger SQLite) | Keep writer dependency-free (only stdlib sqlite3); no reverse imports into L0–L5 |
| `tools/ledgers/consulter.py` | ORCHESTRATOR (for precedent queries) | ~10 (one per consulting skill) | L6 | Observability, State | Pure-read; no side effects beyond optional FTS5 cache warm |
| Ten `.windsurf/schemas/*_ledger.schema.sql` | STATE_NODE | — | N/A (data) | State | DDL under CI drift gate (reuse `apply_ledger_schema.py`) |
| Ten consulting skills | (supporting) | 1 each, into Cascade prompt context | L6 | Observability | Skills don't execute code — templates only |

No SAFETY_GATEKEEPER archetype — this plan is deliberately **observational**, not enforcement.

---

## Sequencing Notes

- **W0 must complete before W1–W4** (shared schema + writer required).
- **W1, W2, W4.2–W4.4 can execute in parallel** after W0 (independent ledgers).
- **W3.1 starts observation window at W0 completion** but first real calibration report waits 30 days — plan flags this as ⏳ background.
- **W3.2 can start immediately** (uses existing Notion DB, no observation lag).
- **W4.1 backfill is one-shot** but ongoing capture depends on W0 writer.
- **W5 is strictly terminal** — depends on rows existing in ≥8/10 ledgers.

## Rollback Checkpoints

Each phase is independently revertable:
- W0 deliverables: pure additions under `tools/ledgers/`, `.windsurf/schemas/`, `artifacts/ledgers/`. Revert = `git rm` + Notion DB archive (not delete — preserve history).
- Any ledger writer: guarded by `LEDGER_WRITER_BYPASS=<ledger_name>` env var for emergency disable.
- Any consulting skill: delete from `.windsurf/skills/` — rule engine degrades gracefully (skills are optional disclosure).
- Calibration scripts: scheduled jobs; disable by removing cron entry.
- Pre-commit gates added in W5: can be removed by editing `.pre-commit-config.yaml`.

## Risks

| Risk | Likelihood | Impact | Owner Mitigation |
|---|---|---|---|
| Hook chain latency regresses >20% | Medium | Medium | Async queue + kill-switch (G4) |
| Ten new SQLite files confuse operators | Medium | Low | Single `artifacts/ledgers/` dir + unified report (W5.1) |
| Calibration reports go unread | High | Low | Notion Calibration DB surfaces directly in Backlog Snapshot regeneration (W5.3) |
| Consulting skills inject too much context into prompts | Medium | Medium | Per-skill token cap (≤500 tokens per precedent block); top-3 matches only |
| Windsurf dispatcher bug drops writer events | Known | Medium | Idempotent writer + `manual_post_cascade_replay.py` fallback (G5) |
| §4 formula re-weighting destabilizes existing priority scoring | Low (gated by ADR) | High | Shadow mode for 2 weeks before cutover; ADR requires explicit Author-Gate approval |

## Acceptance Gates

| Gate | Verification |
|---|---|
| Schema drift | `python .windsurf/scripts/apply_ledger_schema.py --check` returns 0 for every ledger |
| Writer contract | New `ops_scripts/ci/check_ledger_writer_contract.py` — verifies every post-hook that emits a ledger event also writes `event_id` and `latency_ms` |
| Row presence | Each ledger has ≥50 rows within 7 days of W0 completion (writer actually firing) |
| Consulting coverage | Each skill consulted at least once per dogfood session (verified via ledger meta-row) |
| Notion sync | Calibration DB row count == 10; every row links to ledger schema file + writer script |
| Latency budget | `post_cascade_heartbeat.jsonl` p95 duration unchanged ± 20% vs pre-W0 baseline |
| ADR filed | `docs/architecture/adr/ADR-NNN-intelligence-ledgers.md` exists; Notion ADR Registry row created |

---

## Deferred Scope

- Ledger cross-joins (e.g., "refactor waves where tool-routing was mis-predicted → do they have worse outcome?") — captured below for Wave/Phase Convergence.
- Visualization dashboard (Grafana / Streamlit) — out of scope v1; Markdown report sufficient.
- Retention policy (row expiration, archival) — define in W5.3 ADR but not implemented v1.
- Cross-workspace ledger sync (multiple machines) — explicitly out of scope; ledgers are per-clone.

DEFERRED_SCOPE: plan=intelligence-ledgers-ten-a7c3e2 wave=W6 phase=W6.1 layer=L6 fan_in=0 surface=Observability coverage_gap_pct=100.0 est_tokens=8000 reason=Cross-ledger join analytics deferred to follow-up wave
DEFERRED_SCOPE: plan=intelligence-ledgers-ten-a7c3e2 wave=W6 phase=W6.2 layer=L6 fan_in=0 surface=Observability coverage_gap_pct=100.0 est_tokens=6000 reason=Retention and archival policy for ledger rows deferred post-ADR
DEFERRED_SCOPE: plan=intelligence-ledgers-ten-a7c3e2 wave=W6 phase=W6.3 layer=L6 fan_in=0 surface=Observability coverage_gap_pct=100.0 est_tokens=10000 reason=Visualization dashboard Streamlit or Grafana deferred to v2

---

## References

- Existing decision-ledger precedent: `.windsurf/schemas/decision_ledger.schema.sql`, `.windsurf/scripts/apply_ledger_schema.py`, `.windsurf/scripts/capture_author_gate.py`, `.windsurf/scripts/author_gate_ledger_integrity.py`, `.windsurf/scripts/generate_calibration_report.py`
- Consulting-skill precedent: `.windsurf/skills/refactor-decision-memory/SKILL.md`
- Calibration-runner precedent: `ops_scripts/calibration/weekly_refresh.py`
- Writer-hook precedent: `.windsurf/scripts/post_cascade_adg_audit.py`, `.windsurf/scripts/post_cascade_deferred_scope_capture.py`, `.windsurf/scripts/post_mcp_audit.py`, `.windsurf/scripts/post_commit_outcome_binder.py`
- Constitutional rules touched: §17 (Memory Lifecycle), §22 (Graph-Layer Primary), §24 (Deferred-Scope Capture), §26 (Windsurf Config Schema), ADR-023 terminology boundary
- Workspace map (Notion DBs): `AGENTS.md` §Notion Workspace Map
- Upstream watch: `anthropics/claude-agent-sdk-typescript#41` (affects W2.2 SLO interpretation)
