# ADG post-run action dispatch — operator playbook

SSOT for humans and Cursor agents after a full ADG run. Plan: [adg-action-dispatch-c9e4a2.md](../../.cursor/plans/adg-action-dispatch-c9e4a2.md).

**Charter:** No auto-repair from artifacts. No TRACK mass cleanup in one session. No gate weakening. Queue rows (W1+) are dispatch hints only — patches require ADG_REPAIR_LITMUS.

---

## 1. Fifteen-minute triage ladder

Stop at the first step you will execute **this session** (one seam only).

| Step | When | What to open | Action |
|------|------|--------------|--------|
| **A** | Always first | [adg_burndown_report.md](../../artifacts/adg/adg_burndown_report.md) | Read **Fix now** (FIX) and overall BLOCKED/PASS |
| **B** | After W1 ships | Latest `artifacts/adg/adg_action_queue_<ts>.json` or CLI markdown | Take `actions[0]`; check `emit_status` and `provenance.degraded` |
| **C** | FIX gates remain | §4 Top Blockers + smallest REGR delta | One gate per session; block before regr; ascending findings |
| **D** | P0 layer violations | `artifacts/adg/issues/p0_remediation_wave_plan_<ts>.md` | One file from wave 1 only |
| **E** | FIX empty | `adg_refactor_accelerator_<ts>.json` → `candidates[0]` | Only when no FIX; use `impacted_tests` |
| **F** | TRACK only | — | **Defer** — new plan wave + `DEFERRED_SCOPE`; never same-day mass fix |

### Verdict clusters (burndown)

| Cluster | Meaning | Session rule |
|---------|---------|--------------|
| **FIX** | FAIL / REGR / SEED — ADG not fully green | Address now (one gate or one file) |
| **TRACK** | DEBT / OPEN / ADVIS — CI OK, backlog remains | Plan wave only; not in action queue (W1+) |
| **CLEAR** | PASS — zero findings | Skip |

### Manual FIX order (pre-W1 or if queue missing)

Use when `adg_action_queue_*.json` is absent. Sort: P0 block → P0 regr → P1 regr by **smallest +N delta**, then finding count.

**Baseline example (2026-05-25 snapshot):**

| Session rank | Gate | Verdict | Findings | Why this order |
|-------------|------|---------|----------|----------------|
| 1 | `10_infra_wiring` | FAIL (block) | 2 | P0 halt |
| 2 | `1_critical_path_integrity` | FAIL (block) | 1 | P0 halt |
| 3 | `O_tool_call_parity_ratchet` | REGR | 316 (+1) | Smallest regression |
| 4 | `Q2_cyclomatic_complexity_ratchet` | REGR | 911 (+1) | Next smallest delta |
| 5 | Defer | `S4_unused_imports_ratchet` | 10701 (+2) | Hygiene — separate plan wave |

---

## 2. Question → artifact routing (P7-first)

Match timestamp to `adg_indexed_<ts>.sqlite`. Prefer run zip / `artifacts/adg/` over stale root copies.

| Question | Primary artifact | Secondary / live MCP |
|----------|------------------|----------------------|
| What do I fix **first**? | `adg_action_queue_<ts>.json` (W1+) | Burndown § Fix now |
| Which **files** to refactor? | `adg_refactor_accelerator_<ts>.json` → `candidates[]` | `adg_mv_hotspot_centrality` |
| Top **blast radius**? | `adg_structural_outputs_<ts>.json` → `blast_radius` | `adg_blast_radius` |
| Top **centrality**? | `adg_structural_outputs_<ts>.json` → `centrality` | `mv_hotspot_centrality` |
| **Burndown** totals? | `adg_structural_outputs_<ts>.json` → `burndown` | `adg_burndown_table.json` |
| **Tests** for a module? | `adg_refactor_accelerator_<ts>.json` → `impacted_tests` | `artifacts/adg_test_surface_map.json` |
| **P0 wave** file list? | `artifacts/adg/issues/p0_remediation_wave_plan_<ts>.md` | `adg_p0_wave_plan` |
| Layer / gravity signals? | `adg_graphdb_queries_<ts>.json` | `adg_p_view_query`, `v_p0_*` |
| App-scoped fan-in? | `docs/reports/adg/apps_<app>_hotspots_<ts>.md` | App filter on MV queries |

**Stale inputs:** Do not use `artifacts/adg_failure_clusters.json` for ranking unless its `snapshot_ts` matches `adg_gate_results_*.json`. Repair loops may read clusters manually with that check.

**Forbidden for structural questions:** grep for imports/deps — use ADG MCP per [adg-sqlite skill](../../.cursor/skills/adg-sqlite/SKILL.md).

---

## 3. Testing hotspots (gate + module + tests)

A testing hotspot is **not** fan-in alone. Require all three:

1. **Gate signal** — e.g. `E1_trace_stub_module`, `G2_seam_test_export_coherence`, `8_trace_replay_eval` (REGR in 2026-05-25 run).
2. **Module rank** — `refactor_accelerator` candidate or `mv_debt_concentration_hotspots` for that path.
3. **Scoped proof** — `impacted_tests` from accelerator or `adg_test_surface_map.json`.

```bash
# After selecting module from accelerator (example)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest <impacted_test_node_ids> -q
```

During repair: **no** full `pytest tests/unit` — scoped IDs only ([adg-analysis-procedures.mdc](../../.cursor/rules/adg-analysis-procedures.mdc) §5).

---

## 4. ADG_REPAIR_LITMUS (before any patch)

Copy into plan/receipt before editing:

```markdown
## ADG_REPAIR_LITMUS
Cluster: <gate_id or queue rank N>
Root module: <single definition file>
Scoped tests: <pytest node id 1>, <node id 2>
Blast radius: <test → import → module path from ADG MCP>
Snapshot: adg_indexed_<ts>.sqlite
ADG Provenance: backend=<sqlite|redis_cache>, snapshot=<file>
```

Fix **root module** (definition node), not every call site.

---

## 5. TRACK → plan mapping (deferral, not dispatch)

TRACK gates must **not** become same-day cleanup. Route to plan waves:

| TRACK gate (examples) | Plan action |
|----------------------|-------------|
| `G_REACH_l0_reachability` (2792) | Dedicated orphan burndown plan; MV query by layer |
| `S2_uwg_bypass_ratchet` (1600) | Sovereignty plan; `v_p0_*` write-bypass views |
| `E1_trace_stub_module` (1036) | Test-theater plan; accelerator + E1 gate |
| `8_trace_replay_eval` (when REGR) | FIX first (+N); then eval coverage plan |

Emit when deferring:

```
DEFERRED_SCOPE: plan=<slug> wave=<N> phase=<M> layer=<L*> fan_in=<N> surface=<...> coverage_gap_pct=<N> est_tokens=<N> reason=<gate backlog>
```

Priority band: `tools/priority/deferred_scope_scorer.py` — never hand-assign P1–P5.

---

## 6. Commands reference

### Always available (W0)

```bash
python tools/reports/adg_burndown_report.py
python tools/reports/adg_burndown_canvas.py
```

Open [artifacts/adg/adg_burndown_report.md](../../artifacts/adg/adg_burndown_report.md) with Markdown preview (`Ctrl+Shift+V`).

### Action queue (W1 — available)

```bash
set PYTHONPATH=<repo_root>
python tools/reports/adg_action_queue.py --latest --top 10 --format markdown
python tools/reports/adg_action_queue.py --latest
```

Output: `artifacts/adg/adg_action_queue_<ts>.json` — stderr `NEXT_ACTION=...`

stderr from full gen (W1.2):

- `NEXT_ACTION=artifacts/adg/adg_action_queue_<ts>.json`
- `NEXT_ACTION_DEGRADED=1` when optional inputs missing
- `NEXT_ACTION_ERROR=...` — queue failed; **does not** mean ADG passed

### Live MCP (during patch)

```
adg_health → adg_p0_wave_plan → adg_mv_hotspot_centrality(limit=20)
adg_blast_radius(node_id=..., hops=2)
```

---

## 7. What not to do

| Anti-pattern | Why |
|--------------|-----|
| Read GraphDB JSON for “what’s next” | Diagnostic bulk; use queue or burndown FIX |
| Burn down a TRACK gate in one session | Thousands of findings; plan wave only |
| Use stale `adg_failure_clusters.json` | Wrong ordering vs current snapshot |
| Auto-apply queue rows as patches | Charter: human/agent + litmus required |
| Weaken gates / ratchets to go green | Forbidden |
| Create Notion rows for all 17 TRACK gates | W3: FIX only, optional |

---

## 8. Notion FIX backlog sync (W3, optional)

When `NOTION_TOKEN` is set and you want FIX gates in Backlog Items:

```bash
python tools/notion/adg_fix_backlog_sync.py --latest --dry-run
python tools/notion/adg_fix_backlog_sync.py --latest --apply
```

- Missing token → exit **0**, stderr `SKIP_NOTION_TOKEN_MISSING`
- **FIX gates only** — never TRACK; idempotency key `gate_id+snapshot_ts`
- Not part of ADG certification or `generate_full_adg`

---

## 9. Related docs

- Plan: [.cursor/plans/adg-action-dispatch-c9e4a2.md](../../.cursor/plans/adg-action-dispatch-c9e4a2.md)
- Index: [adg_action_dispatch_plan_index.md](adg_action_dispatch_plan_index.md)
- Procedures: [adg-analysis-procedures.mdc](../../.cursor/rules/adg-analysis-procedures.mdc)
- Post-run rule: [adg-post-run-burndown.mdc](../../.cursor/rules/adg-post-run-burndown.mdc)
- P-band burn-down: [adg-p-band-burn-down-discipline.mdc](../../.cursor/rules/adg-p-band-burn-down-discipline.mdc)
