# G6 — Taxonomy Cleanup and Residual G4/G5 Reconciliation

## 1. Sub-wave ID, title, one-line purpose

**G6** — *Taxonomy Cleanup and Residual G4/G5 Reconciliation*. Reconcile residual G4/G5 reporting/taxonomy drift first, then normalize ambiguous, dormant, duplicated, bypassed, and special-case runtime surfaces into a coherent pre-G7 taxonomy.

wave: G6
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## 2. Inputs

- Mandatory Wave G inputs consumed:
  - `docs/wave_g/G0_full_runtime_plan/*`
  - `docs/wave_g/G1_core_runtime_inventory/*`
  - `docs/wave_g/G1b_apps_inventory/*`
  - `docs/wave_g/G2_service_wiring/*`
  - `docs/wave_g/G2b_provider_gateway/*`
  - `docs/wave_g/G3_pipelines/*`
  - `docs/wave_g/G4_storage_infra/*`
  - `docs/wave_g/G4b_control_plane/*`
  - `docs/wave_g/G5_runtime_topology/*`
- Wave F baseline: `docs/wave_e/99_integration_v14/canonical/*` (preferred baseline available and used).
- Phase 0 precondition checks:
  - `python tools/adg/adg_redis_ingest.py --check` → hot
  - `adg_health` → sqlite healthy, redis healthy, snapshot `04182026_0814`

## 3. Outputs

- `README.md`
- `normalization_matrix.md`
- `dormant_and_declared_surfaces.md`
- `duplicate_and_ambiguous_surfaces.md`
- `special_surface_decisions.md`
- `b7_candidate_register.md`

## 4. Phase A reconciliation summary

### A1. G4 storage-taxonomy reconciliation

Reconciled reporting to source-of-truth (`storage_catalogue.yaml`):

- Canonical top-level model fixed to `kind` taxonomy.
- G4 README category summary updated to exact kind counts:
  - `disk_artefact` 16
  - `sqlite` 5
  - `redis` 5
  - `vector` 3
  - `in_process_cache` 1
  - `transient_output` 1
  - `test_only` 1
  - `other` 1
  - total 33
- `artefact_lifecycle.md` category table aligned to same canonical kind model.
- Orphan/vestigial summary made explicit and separate from top-level class model.
- Durability wording clarified: `durability` enum is authoritative; "authoritative durable" is descriptive only.

Phase A files corrected (G4):

- `docs/wave_g/G4_storage_infra/README.md`
- `docs/wave_g/G4_storage_infra/artefact_lifecycle.md`

### A2. G5 runtime-topology sanity reconciliation

Validated and normalized reporting against source-of-truth files:

- Process/runtime surfaces (`process_topology.yaml`): 27
- MCP registry (`mcp_server_registry.md`): 12 with split 9 stdio / 2 binary / 1 external https
- Failure domains (`failure_domains.md`): 8 (`FD-01`..`FD-08`)
- Process category vocabulary normalized to canonical seven labels.
- Ownership vocabulary made explicit (`repo-managed` vs `operator-managed`) in G5 README.
- Snapshot timestamp checked across all G5 artifacts (`04182026_0814`, consistent).

Phase A files corrected (G5):

- `docs/wave_g/G5_runtime_topology/README.md`

## 5. Stop condition

Met.

- Phase A reconciled residual G4/G5 reporting/taxonomy drift without redesigning findings.
- Corrected G4/G5 summary files now match source-of-truth artifacts used for counts/classification.
- All required normalization targets were explicitly evaluated and classified in G6 matrix.
- Every normalization candidate records required fields:
  - `surface_id`
  - `path_or_surface`
  - `current_role`
  - `observed_usage`
  - `evidence`
  - `normalization_decision`
  - `rationale`
  - `downstream_owner`
  - `blocks_G7`
- Downstream ownership is recorded for unresolved/ambiguous items.

## 6. Risks encountered during execution

- Large prior-wave corpus creates drift risk between narrative summaries and source YAML; mitigated by count reconciliation from source files.
- Several surfaces are intentionally hybrid/compatibility paths (`_optional_agentic_core.py`, `bootstrap_runtime.py`) and must be treated as tolerated special-cases, not canonical core topology.
- Cross-cutting `role=other` residual set remains broad (337 modules) and is inherently taxonomy-fragmented without deeper decomposition.
- Memory SQLite triplet and execution-trace duplicate surfaces remain true blockers for fully clean G7 taxonomy closure.

## 7. B7 candidates surfaced, if any

Yes. G6 records five blocker-class candidates in `b7_candidate_register.md`:

- `B7-G6-01` L_CONTRACTS dead-or-unwired decision
- `B7-G6-02` execution-trace duplicate ownership
- `B7-G6-03` memory SQLite triplet canonical-state decision
- `B7-G6-04` residual `role=other` cluster decomposition
- `B7-G6-05` operator-managed vs repo-managed ownership formalization

## 8. Hand-off note for G7

G7 should consume G6 as the taxonomy closure input and apply these actions:

1. Carry forward all `canonical` and `tolerated_special_case` decisions unchanged into the integrated runtime map.
2. Tag each G7 runtime surface with explicit ownership (`repo-managed` or `operator-managed`) to resolve boundary ambiguity.
3. Resolve blocker-class duplicates (`execution_trace_types`, memory SQLite triplet) or keep them as explicit open blockers with owner and acceptance rationale.
4. Decompose the large cross-cutting `role=other` residual set into stable subclusters or mark a bounded deferred backlog.
5. Ensure G7 traceability matrix references G6 decision IDs where taxonomy ambiguity affects atom/edge embodiment mapping.
