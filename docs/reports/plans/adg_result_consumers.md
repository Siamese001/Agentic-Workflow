# ADG Result Consumers Map
**Stage 1 Discovery — Scan-only, no code changes**
**Date:** 2026-04-11 | **ADG Snapshot:** `04102026_1817`

---

## 1. Consumer Classification

ADG results are consumed across six consumer families:

| Family | Consumer Count | Primary ADG Artifact Consumed |
|--------|---------------|-------------------------------|
| A. ADG Generation Pipeline (validation gates) | 8 gate modules | SQLite, burndown, ratchet JSON |
| B. Prompt Assembly Package | 6 adapters | SQLite, JSON reports, ratchet, structural outputs, graph DB |
| C. Prompt Governance Analysis (internal ADG) | 4 analysis modules | `ScanResult` in-memory object |
| D. CI / Ops Gates | 3 gate runners | SQLite, JSON phase artifacts, cluster JSON |
| E. MCP / Live Query Tools | 3 query scripts | Redis hot cache, SQLite |
| F. Windsurf Workflow / IDE Tooling | 2 workflows | Redis hot cache |

**No confirmed live runtime consumer wires ADG outputs into an L2 execution prompt path.**

---

## 2. Family A — ADG Generation Validation Gates

These execute *inside* `tools/generate/generate_full_adg.py` during each ADG run. They consume the freshly-built `ScanResult`, in-memory artifact, and the persisted SQLite.

### `tools/generate/validation/gates.py`

| Gate Function | ADG Artifact Consumed | Output |
|--------------|----------------------|--------|
| `_check_p0_violations` | `ScanResult.edges` — `violates`, `dynamic_exec`, `invokes_provider` | Exit 1 if P0 threshold breached |
| `_check_p1_ratchet` | `artifacts/adg/p1_ratchet.json` vs current counts | Exit 1 if ratchet exceeded |
| `_check_p2_ratchet` | `artifacts/adg/p2_ratchet.json` vs current counts | Exit 1 if ratchet exceeded |
| `_check_agentic_antipatterns` | `ScanResult.edges` — `antipattern` edges | Reports patterns in critical layers |
| `_check_artifact_consistency` | 5-file set (SQLite, graphs, snapshot) | Cross-checks digest and counts |
| `_check_artifact_validity` | All generated files | File exists + size + parseable |
| `_check_dead_production_imports` | `ScanResult.edges` — `dead_import` edges | Dead import count in prod code |
| `_check_structural_conformance` | `sc_ap_config.json` + SQLite | Structural policy compliance |
| `_check_sqlite_integrity` | SQLite `PRAGMA integrity_check` | DB file health |

**Entry point:** `tools/generate/validation/__init__.py` — called inline from `generate_full_adg()`.

---

## 3. Family B — Prompt Assembly Retrieval Adapters

These consume ADG artifacts to produce `EvidenceItem` objects for packet building.

| Adapter | Source File | ADG Artifacts Consumed |
|---------|------------|----------------------|
| `SQLiteAdapter` | `tools/adg/prompt_assembly/retrieval/adapters.py` | `adg_indexed_<ts>.sqlite` — violations table, anti-patterns, imports, fan-in/out, infra views |
| `ReportAdapter` | Same | `provenance_report_*.json`, `closure_validation_report_*.json`, `edge_density_report_*.json`, `layer_coverage_report_*.json`, `adg_snapshot_*.json`, `sc_ap_config.json` |
| `RatchetAdapter` | Same | `p1_ratchet.json`, `p2_ratchet.json`, `adg_burndown_table.json` |
| `GraphDBAdapter` | Same | NetworkX projection of SQLite — in-memory graph, not a file |
| `InfraWiringAdapter` | Same | Infra wiring views from SQLite |
| `StructuralAdapter` | Same | `structural_outputs.py` burndown/centrality/seams — driven from SQLite |

**Downstream of adapters:**
1. `evidence_shaper.py` → `EvidenceBundle`
2. `packets/builders.py` → `PromptEnvelope`
3. `cli.py` → JSON or Markdown file output

**Current invocation:** CLI only (`python -m tools.adg.prompt_assembly`). No programmatic caller found in production code.

---

## 4. Family C — Prompt Governance Analysis Modules

These are called during ADG generation. They consume `ScanResult` in-memory (not file artifacts) and contribute to the governance graph outputs.

| Module | Called From | ADG Input | Output |
|--------|------------|-----------|--------|
| `agentic_core/adg/analysis/prompt_authority.py` (E21) | `tools/generate/generate_full_adg.py` (via `_generate_standardized_reports`) | `ScanResult.edges` — `generates_prompt`, `assembles_into` | `PromptAuthorityReport` → serialized to JSON report |
| `agentic_core/adg/analysis/prompt_drift_config.py` (E25) | `tools/generate/generate_full_adg.py` (drift detection phase) | `ScanResult` (current) + prior snapshot | `PromptDriftReport` → serialized to JSON report |
| `agentic_core/adg/applications/prompt_impact.py` (E24) | Called on-demand / analysis phase | `ScanResult.edges` — `generates_prompt`, `consumes_prompt`, `assembles_into` | `PromptImpactReport` |
| `agentic_core/adg/applications/prompt_impact_config.py` | Companion to E24 | Config data | Config |

**Artifact output path (inferred):** `artifacts/adg/prompt_authority_report_<ts>.json`, `artifacts/adg/prompt_drift_report_<ts>.json` — **unconfirmed** (not seen in artifact dir listing).

---

## 5. Family D — CI and Ops Gates

### `tools/adg/adg_ci_gate.py`

| Command | ADG Artifact Consumed | Gating Behavior |
|---------|----------------------|-----------------|
| `check-phase` | `artifacts/adg/adg_current_phase.json` | Blocks full suite if phase not converged |
| `check-cluster` | `artifacts/adg/adg_failure_clusters.json` | Blocks test run if clusters not resolved |
| `check-surface` | `artifacts/adg/adg_test_surface_map.json` | Restricts test scope to ADG-predicted surface |
| `check-semantic` | `artifacts/adg/adg_semantic_graph.json` | Validates semantic reuse graph |

**Invocation:** Pre-commit hook and CI pipeline (`python tools/adg/adg_ci_gate.py <command>`).

### `ops_scripts/ci/_adg_ci_gates.py`

Broader CI gate runner. Aggregates multiple checks including P0 authority, determinism, write-sovereignty, lifecycle, trace-replay.

| Gate Module | ADG Artifact Consumed |
|-------------|----------------------|
| `gate_p0_authority.py` | SQLite violations, authority edges |
| `gate_p0_determinism.py` | Provenance report, closure report, digest comparison |
| `gate_p0_write_sovereignty.py` | UWG edge counts in SQLite |
| `gate_p0_critical_path.py` | Critical-layer violation counts |
| `gate_p0_capability_egress.py` | Capability/egress edges |
| `gate_p0_text_to_action.py` | Text-to-action pattern detection |
| `gate_p1_lifecycle.py` | P1 ratchet, lifecycle edge health |
| `gate_p1_trace_replay.py` | Trace replay edges in SQLite |
| `gate_policy.py` | Policy compliance edges |
| `gate_ssot_catalog.py` | SSOT catalog consistency |
| `gate_m_gates.py` | M-series modularization gates |
| `p0_runner.py` | **Orchestrates all P0 gates** |
| `p3_trend_runner.py` | P3 style trend tracking |

**Entry:** `ops_scripts/ci/run_contract_gates.py` → `python ops_scripts/ci/run_contract_gates.py`
**Invocation:** CI pipeline, pre-commit hook.

### `tools/adg/adg_stale_guard.py`

| Command | Purpose |
|---------|---------|
| `python tools/adg/adg_stale_guard.py` | Exit 0 if ADG fresh, exit 1 if stale vs. latest git commit |
| `--warn` | Warn but always exit 0 |
| `--json` | Machine-readable output |
| `--files` | List files changed since last Redis ingest |

**ADG Artifacts Consumed:** Redis hot cache timestamp vs. `git log --since=<ingest_ts>` on `*.py` files.

---

## 6. Family E — MCP / Live Query Tools

### `tools/adg/queries/adg_redis_live_query.py`

- **Consumer:** Redis hot cache via `adg:edge:*:<relation_type>` key pattern
- **Reads:** `generates_prompt`, `consumes_prompt`, and 13 other alignment edge types
- **Output:** Tabulated alignment edge source nodes — developer/analysis use

### `tools/adg/queries/adg_align_query.py` through `adg_align_query7.py`

- **Consumer:** SQLite direct — concept absence check on prod nodes
- **Reads:** `L_PG` nodes for prompt governance concepts, layer membership
- **Output:** Human-readable gap analysis — developer use

### `tools/adg/adg_ci_gate.py` (CLI mode)

- **Consumer:** `artifacts/adg/adg_failure_clusters.json`, `adg_current_phase.json`, `adg_test_surface_map.json`
- **Output:** Gating verdicts

---

## 7. Family F — Windsurf Workflow / IDE Tooling

### `.windsurf/workflows/adg-redis-refresh.md`

- **Invokes:** `python tools/generate_full_adg.py` → `python tools/adg/adg_redis_ingest.py`
- **Consumes:** All 5-file artifact set + reports
- **Produces:** Redis hot cache for ADG MCP tools

### `.windsurf/workflows/adg-repair-loop.md`

- **Invokes:** ADG gates, repair scripts
- **Consumes:** `adg_burndown_table.json`, `p1_ratchet.json`, `adg_failure_clusters.json`
- **Output:** Guided repair workflow

---

## 8. L3 Orchestration — C0 Context Engine

### `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py`

| Type | Role |
|------|------|
| `C0EvidenceContract` | Output contract of the C0 retrieval pass |
| `CitedSpan` | A single retrieved evidence span |
| `C0ContractViolation` | Raised on invalid contract — blocks prompt assembly |

**Relationship to ADG outputs:** This contract is the *intended* upstream input to a prompt assembler at runtime. It carries `coverage_score`, `cited_spans`, and `evidence_hmac`. However, **no confirmed wiring** from this type to `tools/adg/prompt_assembly` adapters or builders exists. The L3 contract and the L_TOOLS prompt assembly package are currently two disconnected subsystems.

---

## 9. Materialized Views as ADG Consumers

`tools/generate/materialized_views/` produces extended views from the `ScanResult` and SQLite:

| Phase | Module | Output |
|-------|--------|--------|
| A | `phase_a_path_authority.py` | Path + authority analysis view |
| B | `phase_b_capability_tool_task.py` | Capability/tool/task graph view — includes `generates_prompt` edge analysis |
| C | `phase_c_trace_drift_debt.py` | Trace, drift, debt view |
| D | `phase_d_snapshot_regression.py` | Snapshot regression view |
| E | `phase_e_graph_intelligence.py` | Graph intelligence view |

**Invocation:** `tools/generate/materialized_views/orchestrator.py` called from `generate_full_adg.py` as `_materialize_adg_views`.

---

## 10. Shadow Learning / System Learning

### `agentic_core/adg/runtime/behavioral_index.py`

- Consumes `generates_prompt` / `consumes_prompt` edges from SQLite
- Builds behavioral index for L6 shadow evaluation
- Tagged in ADG governance graph

### `tools/generate/reporting/analysis.py` and `reports.py`

- Consume the in-memory `ScanResult` + ADG artifact object
- Produce `adg_burndown_table.json`, summary tables, the 8 standardized reports

---

## 11. Consumer Map Summary Table

| Consumer | Artifact Consumed | Format | Trigger |
|----------|------------------|--------|---------|
| `generate_full_adg.py` validation gates | SQLite, ratchet JSON, ScanResult | SQLite + JSON | On every ADG generation run |
| `tools/adg/prompt_assembly` adapters | SQLite, 6 JSON reports, ratchet, structural | File read | CLI invocation only |
| `prompt_authority.py` (E21) | ScanResult in-memory | In-process | ADG generation |
| `prompt_drift_config.py` (E25) | ScanResult (current + prior) | In-process | ADG generation |
| `prompt_impact.py` (E24) | ScanResult | In-process | On-demand analysis |
| `adg_ci_gate.py` | 4 JSON phase artifacts | JSON file | Pre-commit / CI |
| `ops_scripts/ci/_adg_ci_gates.py` | SQLite, ratchet, provenance report | SQLite + JSON | CI pipeline |
| `adg_stale_guard.py` | Redis hot cache timestamp | Redis HASH | Pre-query guard |
| `adg_redis_live_query.py` | Redis hot cache edges | Redis SCAN | Developer query |
| `adg_align_query*.py` | SQLite direct | SQLite | Developer query |
| `materialized_views/` (5 phases) | ScanResult + ADG artifact | In-process | ADG generation |
| `behavioral_index.py` | SQLite generates_prompt edges | SQLite | L6 shadow eval |
| `.windsurf/workflows` | Redis + 5-file artifact set | CLI invocation | IDE / developer |
| `C0EvidenceContract` (L3) | Live retrieval (not ADG files) | In-process | **Not wired to PA** |

---

## 12. What Is NOT a Confirmed Consumer

| Item | Status |
|------|--------|
| L2 execution agent consuming a `PromptEnvelope` | **Not confirmed** — no `build_packet()` call in `L2_execution/` |
| L5 exit control consuming a `PromptEnvelope` | **Not confirmed** |
| PR review tooling reading ADG packets | **Not confirmed** |
| Remediation agents reading ADG packets | **Not confirmed** |
| Any runtime agent importing `tools.adg.prompt_assembly` | **Not confirmed** — only tests and CLI confirmed |
