# ADG Prompt Assembly Inventory
**Stage 1 Discovery — Scan-only, no code changes**
**Date:** 2026-04-11 | **ADG Snapshot:** `04102026_1817` | **Nodes:** 77,143 | **Edges:** 622,595

---

## 1. Executive Summary

The repository has a **fully-built but narrowly-wired** ADG prompt assembly layer. A structured `tools/adg/prompt_assembly/` package exists with eight packet types, typed contracts, retrieval adapters, an evidence shaper, a token budgeter, and a CLI. However it is **only wired to the ADG toolchain** (developer/CI use) — it is **not connected to the live runtime prompt pipeline** (`C0 → PA → L2` path described in the architecture documents). Separately, the ADG graph itself tracks prompt governance via `generates_prompt` (39 edges), `consumes_prompt` (41 edges), and `assembles_into` edges across a `L_PG` layer of 122 modules. A `PromptAuthorityReport`, `PromptDriftReport`, and `PromptImpactReport` analysis infrastructure exists in `agentic_core/adg/analysis/` but is invoked only during ADG generation — not at runtime dispatch. The `C0EvidenceContract` typed contract exists in `agentic_core/L3_orchestration/` but has no confirmed live binding to any prompt assembler. The gap is clear: **the architectural prompt assembly lane (C5 substrate) has no single integration point that pulls live ADG outputs and converts them into a `PromptEnvelope` for runtime dispatch**.

---

## 2. ADG Generation Flow

### 2.1 Primary Entrypoints

| Script | Role | Output |
|--------|------|--------|
| `tools/generate_full_adg.py` | Legacy compatibility shim | Delegates to canonical entrypoint |
| `tools/generate/generate_full_adg.py` | **Canonical ADG generation entrypoint** | 5-file output set + reports + Redis ingest |
| `tools/generate/generate_static_adg.py` | Static-only ADG pass | Subset of canonical |
| `tools/generate/generate_runtime_adg.py` | Runtime-trace enriched ADG | Overlay on canonical |

### 2.2 Canonical 5-File Output Model (per run)

| Artifact | Tier | Path Pattern | Content |
|----------|------|-------------|---------|
| `adg_snapshot_<ts>.json` | T1 — CI-light | `artifacts/adg/adg_snapshot_<ts>.json` | Metrics, counts, layer distribution, top hotspots |
| `adg_indexed_<ts>.sqlite` | T2 — Primary queryable | `artifacts/adg/adg_indexed_<ts>.sqlite` | All 18 edge types, nodes, violations — ~287 MB |
| `adg_file_graph_<ts>.json` | T3 — File graph | `artifacts/adg/adg_file_graph_<ts>.json` | imports, exports, dead_imports, covers, influences, in_cycle |
| `adg_symbol_graph_<ts>.json` | T3 — Symbol graph | `artifacts/adg/adg_symbol_graph_<ts>.json` | calls, implements, reads_from, writes_to, instantiates |
| `adg_governance_graph_<ts>.json` | T3 — Governance graph | `artifacts/adg/adg_governance_graph_<ts>.json` | violates, antipattern, generates_prompt, consumes_prompt |

### 2.3 Internal State Files (not part of 5-file model)

| File | Purpose |
|------|---------|
| `adg_graphsnap_<ts>.json` | E7 drift detection — previous-run snapshot (~61 MB uncompressed) |
| `adg_run_<ts>.zip` | Full archive of all artifacts (~50 MB) |
| `artifacts/adg/cache/scan_result_cache.json` | Incremental scan cache |

### 2.4 Standardized JSON Reports (per run)

| Report File | Content |
|-------------|---------|
| `adg_snapshot_<ts>.json` | Snapshot metrics (also canonical output T1) |
| `provenance_report_<ts>.json` | Scanner digest, commit SHA, repo state hash |
| `closure_validation_report_<ts>.json` | Import closure validation results |
| `edge_density_report_<ts>.json` | Edge density by relation type |
| `layer_coverage_report_<ts>.json` | Layer assignment coverage, unknown modules |
| `adg_burndown_table.json` | P0/P1/P2/P3 defect counts, by-kind breakdown, guardian diff |
| `repair_log_<ts>.json` | Auto-repair actions taken during generation |
| `sc_ap_config.json` | Structural conformance / anti-pattern config |

### 2.5 Watchlist and Scoring Outputs

| File | Purpose |
|------|---------|
| `adg_anomaly_watchlist_<ts>.json` | High-signal anomaly watch items |
| `adg_graph_watchlist_<ts>.json` | Graph-native intelligence watchlist (P5 output) |
| `adg_shadow_learning_<ts>.json` | Shadow learning signals from graph analysis |
| `artifacts/infra_wiring_scorecard.json` | Infrastructure wiring compliance score |

### 2.6 Ratchet Files (stable, non-timestamped)

| File | Content |
|------|---------|
| `artifacts/adg/p1_ratchet.json` | P1 anti-pattern ceiling |
| `artifacts/adg/p2_ratchet.json` | P2 anti-pattern ceiling |
| `artifacts/adg/adg_burndown_table.json` | Latest burndown (overwritten per run) |

### 2.7 Packets Directory (empty — not yet populated at runtime)

```
artifacts/adg/packets/   ← empty; no PromptEnvelope files written at generation time
```

---

## 3. Prompt Assembly Package — File-by-File Inventory

### Root: `tools/adg/prompt_assembly/`

| File | Role | Key Exports |
|------|------|-------------|
| `README.md` | Architecture doc | Packet types, CLI usage, PromptEnvelope block order |
| `__init__.py` | Public API surface | `build_packet`, `list_packet_types`, `PromptEnvelope`, `PromptAssemblyStatus` |
| `__main__.py` | Module entry | Delegates to `cli.py:main()` |
| `contracts.py` | **Core typed contracts** | `EvidenceItem`, `EvidenceBundle`, `ContradictionFlag`, `PromptEnvelope`, `PromptAssemblyStatus` |
| `cli.py` | **CLI entrypoint** | `main()` — `--packet`, `--all`, `--list`, `--format`, `--output`, `--sqlite`, `--from-node`, `--to-node`, `--top-n` |

### Subdirectory: `retrieval/`

| File | Role | Key Class / Methods |
|------|------|---------------------|
| `adapters.py` | **6 retrieval adapters** | `SQLiteAdapter` (7 fetch methods), `ReportAdapter` (6 fetch methods), `RatchetAdapter` (3 fetch methods), `GraphDBAdapter` (3 fetch methods), `InfraWiringAdapter`, `StructuralAdapter` (3 fetch methods) |

**SQLiteAdapter fetch methods:** `fetch_violations`, `fetch_antipatterns_by_severity`, `fetch_unresolved_imports`, `fetch_fan_in_hotspots`, `fetch_fan_out_hotspots`, `fetch_node_edge_counts`, `fetch_infra_wiring_views`

**ReportAdapter fetch methods:** `fetch_provenance`, `fetch_closure`, `fetch_edge_density`, `fetch_layer_coverage`, `fetch_snapshot`, `fetch_sc_ap_config`

**RatchetAdapter fetch methods:** `fetch_p1_ratchet`, `fetch_p2_ratchet`, `fetch_burndown`

**GraphDBAdapter fetch methods:** `fetch_blast_radius`, `fetch_violating_path`, `fetch_neighborhood` (all tagged `is_derived=True`)

**StructuralAdapter fetch methods:** `fetch_burndown`, `fetch_centrality`, `fetch_seams`

### Subdirectory: `shaping/`

| File | Role |
|------|------|
| `evidence_shaper.py` | Dedupe → normalize → reconcile → contradiction-retain → coverage/gap. Never drops contradictions. Returns `EvidenceBundle`. |

### Subdirectory: `packets/`

| File | Role | Key Content |
|------|------|-------------|
| `registry.py` | **Central template store** | 8 `PacketTemplate` entries in `TEMPLATES` dict; `TokenBudget` dataclass; shared policy/abstain/refine blocks; `get_template()`, `list_packet_types()` |
| `builders.py` | **8 builder functions** | `build_packet()` dispatcher; one builder per packet type |

### Subdirectory: `budgeting/`

| File | Role |
|------|------|
| `token_budgeter.py` | Token estimation, stratification, overflow handling (trim optional → narrow must-use → summarize → abstain) |

---

## 4. Registered Packet Types (8 families)

| Packet Type | Must-Use Sources | Optional Sources | Token Budget | Purpose |
|-------------|-----------------|-----------------|-------------|---------|
| `determinism_rca` | `provenance_report`, `closure_report`, `sqlite` | `graph_db` | 8,000 | Digest mismatches, reconciliation failures |
| `p0_failure` | `sqlite`, `closure_report`, `sc_ap_config` | `graph_db` | 6,000 | Hard-fail violations (layer, cycles, dynamic_exec) |
| `ratchet_review` | `ratchet`, `burndown`, `sqlite` | `structural` | 6,000 | P1/P2 counts vs baseline ceilings |
| `unknown_unresolved_triage` | `layer_coverage_report`, `sqlite` | `graph_db` | 6,000 | Classify unknown modules, unresolved imports |
| `hotspot_investigation` | `sqlite`, `structural` | `graph_db` | 8,000 | High fan-in/fan-out nodes, risk surfaces |
| `infrastructure_boundary` | `infra_view`, `sqlite` | `graph_db` | 6,000 | Infra spread, write-path bypass risks |
| `graph_path_explanation` | `graph_db`, `sqlite` | `structural` | 6,000 | Violating paths, first illegal hop, blast-radius |
| `executive_summary` | `snapshot`, `burndown`, `closure_report`, `ratchet` | `structural`, `graph_db` | 4,000 | One-run summary, blockers, next wave |

---

## 5. PromptEnvelope Block Order (canonical)

All packets follow this strict 10-block ordering (never trimmed except optional evidence):

1. `system_block` — operator mode / role
2. `policy_block` — invariants (shared `_SHARED_POLICY` across all 8 types)
3. `task_block` — consumer instruction
4. `must_use_evidence` — canonical evidence (SQLite, JSON reports, ratchet)
5. `optional_evidence` — derived evidence (GraphDB), tagged `is_derived=True`
6. `contradiction_flags` — explicit source disagreements (never hidden)
7. `abstain_instructions` — when/how to refuse if evidence insufficient
8. `refine_instructions` — what to request for better evidence
9. `output_schema` — typed JSON response schema
10. `replay_metadata` — snapshot IDs, commit SHAs, digests

---

## 6. Structural Analysis Functions (`tools/adg/structural_outputs.py`)

Four analysis modes consumed by `StructuralAdapter` and directly via CLI:

| Mode | Function | Output |
|------|----------|--------|
| `burndown` | `burndown_table(conn)` | Violation counts by layer pair, layer totals |
| `blast-radius` | `blast_radius(conn, target, top_n)` | Transitive fan-in depth for target or top-N hotspots |
| `seams` | `seam_detection(conn)` | Cross-layer boundary edges grouped by layer pair |
| `centrality` | `centrality(conn, top_n)` | Top-N modules by fan-in with centrality score |

**CLI:** `python tools/adg/structural_outputs.py --mode [burndown|blast-radius|seams|centrality|all] [--json]`

---

## 7. ADG Graph Prompt Governance Plane

The ADG graph itself tracks prompt governance via the `L_PG` layer (122 modules in current snapshot):

| Edge Type | Count (snapshot 04102026_1817) | Meaning |
|-----------|-------------------------------|---------|
| `generates_prompt` | 39 | Module emits a prompt slot |
| `consumes_prompt` | 41 | Module reads/uses a prompt template |
| `assembles_into` | (counted in governance graph) | Module participates in prompt assembly |

**Prompt slot authority hierarchy (S0 > D0 > I0 > C0 > U0)** is enforced by `detect_prompt_authority_violations()` in `agentic_core/adg/analysis/prompt_authority.py`.

**Identity kinds tracked in SQLite:**
- `prompt_slot`: 19 nodes
- `prompt_template`: 10 nodes

---

## 8. Prompt Governance Analysis Modules (`agentic_core/adg/analysis/` and `applications/`)

| Module | ADG Engine ID | Purpose |
|--------|--------------|---------|
| `prompt_authority.py` | E21 | Detect authority hierarchy violations (U0_MUTATES_S0, MISSING_D0_FENCE, etc.) |
| `prompt_drift_config.py` | E25 | Cross-snapshot diff of generates_prompt / consumes_prompt / assembles_into edges |
| `applications/prompt_impact.py` | E24 | Blast radius of prompt-generating module changes |
| `applications/prompt_impact_config.py` | — | Config companion for E24 |
| `analysis/prompt_authority_types.py` | — | Type companions for E21 |

---

## 9. C0 Evidence Contract (Runtime Side)

`agentic_core/L3_orchestration/types/c0_evidence_contract_types.py`

- **Layer authority:** L3_orchestration (C0 context engine / retrieval plane)
- **Contract:** `C0EvidenceContract(retrieval_id, request_id, coverage_score, abstain_hint, cited_spans, evidence_hmac)`
- **Abstain threshold:** `coverage_score < 0.30` → `abstain_hint=True`
- **HMAC:** HMAC-SHA256 over canonical evidence payload
- **Constraint:** Prompt assembler MUST NOT build a `PromptEnvelope` if `C0ContractViolation` is raised

**Gap:** No confirmed code path wires `C0EvidenceContract` output into the `tools/adg/prompt_assembly` package's retrieval adapters or packet builders. These are two separate prompt assembly subsystems with no integration bridge.

---

## 10. CLI Entrypoint Summary

| Command | Usage |
|---------|-------|
| List all packet types | `python -m tools.adg.prompt_assembly --list` |
| Build single packet (JSON) | `python -m tools.adg.prompt_assembly --packet executive_summary` |
| Build single packet (Markdown) | `python -m tools.adg.prompt_assembly --packet ratchet_review --format markdown` |
| Build all packets | `python -m tools.adg.prompt_assembly --all` |
| Write to directory | `python -m tools.adg.prompt_assembly --all --output artifacts/adg/packets/` |
| Custom SQLite source | `python -m tools.adg.prompt_assembly --packet hotspot_investigation --sqlite path/to/db.sqlite` |
| Graph path packet | `python -m tools.adg.prompt_assembly --packet graph_path_explanation --from-node A --to-node B` |

---

## 11. Infra Wiring SQL Views (in-SQLite)

Queried by `SQLiteAdapter.fetch_infra_wiring_views()` — five views expected in SQLite:

- `v_infra_spread`
- `v_write_bypass`
- `v_provider_bypass`
- `v_infra_callers`
- `v_process_boundary`

These are materialized by `tools/generate/infra_wiring_views.py` during generation.

---

## 12. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `adg_file_graph_<ts>.json`, `adg_symbol_graph_<ts>.json` not found in artifact dir | **Inferred** — only latest SQLite and snapshot present; split artifacts may have been archived |
| `InfraWiringAdapter` class referenced in README but not seen in `adapters.py` full read | **Partially confirmed** — only 5 classes confirmed fully; infra wiring handled via `SQLiteAdapter.fetch_infra_wiring_views()` |
| `artifacts/adg/packets/` directory is empty | **Confirmed** — no PromptEnvelope files written at generation time |
| `sc_ap_config.json` expected at `artifacts/adg/sc_ap_config.json` | **Unconfirmed** — not listed in artifact dir listing |
| Live runtime binding of `C0EvidenceContract` to a prompt assembler | **Not confirmed** — type exists at L3, no wiring to `tools/adg/prompt_assembly` found |
