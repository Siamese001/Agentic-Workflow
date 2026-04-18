# G3.1 — Cross-Wave Reconciliation Report

Cleanup pass across G1, G1b, G2, G2b, and G3 before G4 continues. Scope: reconcile reporting / classification inconsistencies. No substantive finding was changed — only counts and wording were corrected where a direct recount of source-of-truth artefacts proved a mismatch.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611). Same snapshot as G1 through G4.

## 1. Source-of-truth recount summary

| Wave | Source of truth | Recounted value | README previously said | Action |
|---|---|---:|---|---|
| G1 | `component_inventory.yaml::components` (len) | **2014** modules | 2014 | ✓ no change |
| G1 | layer counts (CROSS_CUTTING/L5/L2/L3/L1/L4/L6/L0) | 801 / 382 / 194 / 167 / 152 / 141 / 89 / 88 → sums 2014 | consistent | ✓ no change |
| G1b | `app_inventory.yaml::apps` (len) | **8** apps | 8 | ✓ no change |
| G2 | authored artefacts | 2014 agentic_core modules, 8 apps, 124,904 cross-layer edges, 137 authority breaches | consistent | ✓ no change |
| G2b | `egress_points.yaml::egress_points` (len) | **12** entries | 12 | ✓ no change; breakdown reconciled |
| G2b | `env_key_consumer_map.md` scan totals | 269 reads, 154 unique keys, **114 reader files** | README claimed "≈ 140" reader files | **corrected to 114** |
| G3 | `pipeline_catalogue.yaml::pipelines` (len) | **17** | 17 | ✓ no change |
| G3 | `state_machines.md` SM-01..SM-09 | **9** SMs | 9 | ✓ no change |
| G3 | `pipeline_catalogue.yaml` distinct `kind:` values | 8 values present (`app_entry`, `cli`, `internal_call`, `mcp_tool`, `workflow`, `cli_or_test`, `api`, `import`) | README said "9 trigger classes" with different naming | **YAML normalised**; taxonomy clarified |

## 2. Issue-by-issue disposition

### A. G2b provider-class count drift

**Resolution**: canonical partition of the 12 egress points:

| Class | Count | Members |
|---|---:|---|
| External provider (direct) | **6** | OpenAI, Anthropic, Gemini, Google-CSE, HF-Hub (gated), OTel (optional) |
| &nbsp; of which unconditional external | 4 | OpenAI, Anthropic, Gemini, Google-CSE |
| &nbsp; of which conditional / optional external | 2 | HF-Hub (gated by `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` / `BGE_ALLOW_MODEL_DOWNLOAD`), OTel (env-dependent) |
| Localhost / internal egress | **3** | Qwen vLLM, Redis, Neo4j |
| Stub (declared, not wired) | **1** | Pinecone |
| MCP external URL | **1** | deepwiki |
| MCP loopback bucket | **1** | — (covers 9 stdio-loopback + 2 binary-subprocess MCPs in `mcp_as_transport.md`) |
| **Total** | **12** | |

Sum verified: 6 + 3 + 1 + 1 + 1 = 12. Matches `egress_points.yaml` list length. README and `provider_inventory.md` §10 both updated to this partition.

### B. OTel collector classification

**Resolution**: single classification, applied everywhere.

**Canonical classification**: `conditional external sink (env-dependent)` — sits inside the "External provider (direct)" count of 6. Justification: `egress_points.yaml EGRESS-OTEL-01.notes` already said "External only if endpoint env vars are set. Default configuration ships with no collector bound." README now reflects this by subdividing 6 externals into "4 unconditional + 2 conditional (HF-Hub gated, OTel optional)" — OTel and HF-Hub share the same "conditional" semantics.

### C. MCP transport count consistency

**Resolution**: per `mcp_as_transport.md` §3 matrix:

| Transport | Count | MCP IDs |
|---|---:|---|
| stdio-loopback | **9** | MCP-01/02/03/04/05/06/07/09/10 (adg_sqlite, memory, vector_db, otel_mcp, redis, pytest_mcp, enhanced_http, notion, task_manager) |
| binary-subprocess | **2** | MCP-08 filesystem (Node), MCP-11 GitKraken (gk.exe) |
| https-external | **1** | MCP-12 deepwiki |
| **Total** | **12** | |

Headline statement (now consistent across `README.md §5` and `mcp_as_transport.md §4`): **"11 of 12 MCP servers are locally-launched (9 stdio-loopback + 2 binary-subprocess). deepwiki is the only pure external MCP."**

Previous wording "10 of 12 are stdio-loopback from the repo's perspective" was off-by-one (it conflated stdio with binary-subprocess into "locally-launched" but then counted 10 instead of 11). Fixed in `mcp_as_transport.md §4`.

### D. Baseline reference consistency

**Resolution**: all writable G READMEs already cite `docs/wave_e/99_integration_v14/canonical/*` (commit `4b794d5d46`). Verified via grep:

- `G1/README.md` — v1.4 ✓
- `G1b/README.md` — v1.4 ✓
- `G2/README.md` — v1.4 ✓
- `G2b/README.md` — v1.4 ✓
- `G3/README.md` — v1.4 mentioned in §5 / §6 / §7 ✓

`docs/wave_g/G0_full_runtime_plan/*` still references v1.3 in planning-history context. G0 files are not in this task's writable list and the v1.3 reference is intentionally historical (G0 was authored pre-v1.4 sign-off). **No action.**

No "v1.3 baseline" wording overstates staleness in any writable G file.

### E. G1 / G1b / G2 headline sanity

Recount confirmed:

- G1: 2014 modules = 801 CROSS_CUTTING + 382 L5 + 194 L2 + 167 L3 + 152 L1 + 141 L4 + 89 L6 + 88 L0 (verified via `yaml.safe_load` of `component_inventory.yaml`).
- G1b: 8 apps (verified via `yaml.safe_load` of `app_inventory.yaml`). `is_library_only` field present on each entry.
- G2: 124,904 cross-layer edges, 17 ADG layer partitions, 137 authority breaches, 56 critical write bypasses — these are self-consistent between G2 README, `import_edge_matrix.md`, `boundary_violations.md`.

**No headline mismatch found. No change required.**

### F. G3 trigger-taxonomy consistency

**Resolution**: canonical **9-class taxonomy** declared explicitly in `trigger_matrix.md §intro`:

- **6 pipeline-fired classes** (appear as `kind:` values in `pipeline_catalogue.yaml`): `cli`, `app_entry`, `mcp_tool`, `workflow`, `import`, `internal_call`.
- **3 infrastructural classes** (enumerated in `trigger_matrix.md §§5-7` but NOT used as `kind:` values in YAML): `hook`, `ci`, `operator`.

Earlier drafts used `api` and `cli_or_test` as `kind:` values in 2 pipeline entries. These have been normalised:

| Before | After | Rationale |
|---|---|---|
| `PIPE-JUDGE-EVAL` trigger `kind: api` | `kind: internal_call` (with `name:` clarifying "JudgeOrchestrator.evaluate API call") | `api` is not a top-level trigger class; it's a programmatic in-process call from a caller — that is precisely what `internal_call` means |
| `PIPE-REPLAY` trigger `kind: cli_or_test` | `kind: cli` (with `command:` specifying the runner) | tests invoke the CLI entry; no separate "test" trigger class needed |

After normalisation, `pipeline_catalogue.yaml` has exactly **6 distinct `kind:` values**, matching the taxonomy's pipeline-fired band. README and `trigger_matrix.md` summary updated to match.

### G. G3 headline sanity

Recount confirmed:

| Dimension | Source | Count |
|---|---|---:|
| Pipelines | `pipeline_catalogue.yaml::pipelines` len | 17 |
| State machines | `state_machines.md` SM-01..SM-09 | 9 |
| Mandatory pipeline families covered | 9 task-specified families; PIPE-* bindings | 9 / 9 |
| Partial pipelines | `notes:` contains "PARTIAL" (PIPE-REPLAY, PIPE-SYSTEM-LEARNING) | 2 |
| B7 candidates | B7-G3-01..06 | 6 |
| Trigger classes | canonical taxonomy above | 9 (6 + 3) |

All match what G3 README reports. **No headline mismatch.**

## 3. Files modified in this pass

| File | Change |
|---|---|
| `docs/wave_g/G2b_provider_gateway/README.md` | Summary-counts table expanded to explicit 6/3/1/1/1 partition; inputs fixed "114 reader files"; stop condition clarified |
| `docs/wave_g/G2b_provider_gateway/provider_inventory.md` | §10 summary updated to match the 6/3/1/1/1 = 12 partition |
| `docs/wave_g/G2b_provider_gateway/env_key_consumer_map.md` | Scan totals "≈ 140" → **114 reader files** |
| `docs/wave_g/G2b_provider_gateway/mcp_as_transport.md` | §4 "10 of 12 stdio-loopback" → **"11 of 12 locally-launched (9 stdio + 2 binary)"** |
| `docs/wave_g/G3_pipelines/pipeline_catalogue.yaml` | PIPE-REPLAY `cli_or_test` → `cli`; PIPE-JUDGE-EVAL `api` → `internal_call` |
| `docs/wave_g/G3_pipelines/trigger_matrix.md` | Intro declares canonical 9-class taxonomy; §10 summary clarifies 6+3 split |
| `docs/wave_g/G3_pipelines/README.md` | §Summary-counts "Trigger classes mapped" row clarified with 6+3 split |
| `docs/wave_g/G3_pipelines/reconciliation_report.md` | NEW — this file |

Files NOT changed (no mismatch found or not in scope):

- `docs/wave_g/G1_core_runtime_inventory/README.md` — counts verified, no mismatch.
- `docs/wave_g/G1b_apps_inventory/README.md` — counts verified, no mismatch.
- `docs/wave_g/G2_service_wiring/README.md` — counts verified, no mismatch.
- `docs/wave_g/G2b_provider_gateway/egress_points.yaml` — already canonical source; no schema drift.
- `docs/wave_g/G3_pipelines/state_machines.md` — counts verified, no mismatch.

## 4. Substantive vs reporting-only changes

**No substantive finding changed.** All edits are reporting / count / classification corrections where a direct recount of source-of-truth artefacts proved a mismatch.

- No new B7 candidates surfaced (existing 6 in G3, 6 in G2b, 3 in G2, 2 in G1b, 0 net new).
- No pipeline was added, removed, renamed, or re-scoped.
- No egress point was added, removed, or re-provider'd.
- No env key was added or removed.
- No state machine was added or removed.
- OTel's `auth_mode=none` in egress_points.yaml is unchanged; its classification within "External provider (direct)" with the "conditional / optional" qualifier is a clarification of existing text, not a re-classification of the underlying source row.

## 5. Baseline reference rule (recorded for future waves)

For all future G-wave artefacts:

1. Write Wave F baseline reference as `docs/wave_e/99_integration_v14/canonical/*` (commit `4b794d5d46`, 12 families GREEN, 60 ACTIVE atoms NORMATIVE, 26 NORMATIVE edges).
2. Do not cite `99_integration_v13/` except when explicitly documenting historical planning context (as G0 does).
3. When a wave surfaces an interaction not covered by v1.4, record as a `B7-G<wave>-NN` candidate, not as a v1.4 correction.

## 6. G4 readiness

With this reconciliation complete:

- G1 / G1b / G2 / G2b / G3 source-of-truth files agree with their respective README summaries.
- G2b egress taxonomy is stable (6 external / 3 localhost / 1 stub / 1 MCP-external / 1 MCP-loopback bucket = 12).
- G3 trigger taxonomy is stable (9 classes = 6 pipeline-fired + 3 infrastructural).
- MCP transport counts are consistent (11 of 12 locally-launched, 1 external URL).
- Baseline reference is consistently v1.4 across all writable G READMEs.
- No unresolved counting / classification mismatch remains.

**G4 can proceed cleanly.** G4's own artefacts (already authored in a previous step as `docs/wave_g/G4_storage_infra/`) are not in this pass's writable list and were not modified.
