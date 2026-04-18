# Wave G — Execution Plan

Executable plan: ordered sequence, preconditions per step, exit criteria per step, and gate checks between phases. This is the plan an operator executes to run Waves G1 → G7.

## Phase 0 — Pre-flight (before G1 starts)

1. **ADG green light**
   - Run: `python tools/adg/adg_redis_ingest.py --check`
   - Fallback: `adg_health` MCP call.
   - If both red: run `/mcp-failure-rca` and wait for recovery.
2. **ADG snapshot refresh**
   - Run: `/adg-redis-refresh` (regenerates `artifacts/adg/adg_indexed_<ts>.sqlite`).
   - Record the resulting snapshot timestamp — this becomes the `adg_snapshot:` value in every subsequent G catalogue.
3. **Baseline confirmation**
   - Confirm `docs/wave_e/99_integration_v13/canonical/` exists and loads (schema-valid).
   - Confirm `docs/wave_e/F4_edge_exclusion_cleanup/` is present.
   - Note commit hash as "G baseline commit" in `G1_core_runtime_inventory/README.md`.

Exit of Phase 0: ADG snapshot fresh; baseline commit recorded.

## Phase 1 — Core inventory (G1, G1b)

### Step 1 — Execute G1

- Enumerate all `.py` under `agentic_core/`.
- For each: classify `layer` (L0–L6 or CROSS_CUTTING) and `role` (from enum in `output_contracts.md`).
- Record seams used and v1.3 IDs embodied.
- Defer uncertain cases to `unclassified_modules.md`.

Exit of G1: `component_inventory.yaml` contains every `agentic_core/**/*.py` exactly once OR the module is in `unclassified_modules.md`.

### Step 2 — Execute G1b (may start once G1 has L0–L6 coverage)

- For each `apps_*/` directory: enumerate entry points, sub-surfaces, and core bindings.
- Mark `apps_shared/` as `is_library_only: true`.
- Record adapter shim patterns separately in `adapter_patterns.md`.

Exit of G1b: every app has a valid entry in `app_inventory.yaml`.

### Gate 1

- Every `.py` under `agentic_core/` and `apps_*/` is classified or explicitly unclassified.
- No role/layer enum violations.
- YAMLs validate.

## Phase 2 — Wiring, pipelines, providers (G2, G2b, G3, G3b)

### Step 3 — Execute G2

- Use ADG MCP exclusively for import-graph queries.
- Build layer × layer edge matrix.
- Walk the canonical request lifecycle via ADG fan-in/fan-out queries seeded at L0 admit entry point.
- Flag direct cross-layer imports bypassing seams.

Exit of G2: every layer-to-layer edge in ADG is classified as expected / unexpected / violation.

### Step 4 — Execute G2b (parallel to G2 after G1)

- Enumerate every external SDK wrapper and every `os.getenv` / `os.environ[...]` read.
- Record auth mode and retry posture per egress.
- Dual-classify MCP servers as egress + ingress.

Exit of G2b: every egress has protocol, auth mode, retry posture; every env-var read appears in `env_key_consumer_map.md`.

### Step 5 — Execute G3

- Build `pipeline_catalogue.yaml` for each named pipeline (ADG generation, evaluation, healing, replay, memory lifecycle, exit-control, UWG, etc.).
- Document triggers per pipeline.
- Document state machines in `state_machines.md`.

Exit of G3: every pipeline has trigger, stages, terminal condition, source modules.

### Step 6 — Execute G3b

- Specialize G3 for the integrity-critical paths: exit-control, healing, replay, evaluation.
- Produce per-run_id trace contract.
- Cite `GovernedHandoffAgent`, `ExitControlGate.evaluate_sealed()`, `ExecutionTrace`, `RetryConfig` concretely.

Exit of G3b: all four paths (exit, healing, replay, evaluation) have module-grounded walkthroughs.

### Gate 2

- G2 wiring + G2b egress + G3 pipelines + G3b integrity paths all have their YAMLs validated.
- Any B7 candidate signals are labelled `B7-G2-NN` / `B7-G2b-NN` / `B7-G3-NN` / `B7-G3b-NN`.

## Phase 3 — Storage, control plane, ops (G4, G4b, G5)

### Step 7 — Execute G4

- Enumerate every persistent store: SQLite, Redis namespaces, vector collections, disk artefacts.
- Record owner, lifecycle, readers, writers.

Exit of G4: `storage_catalogue.yaml` covers every store surface in `repo_surface_inventory.md` §6.

### Step 8 — Execute G4b (parallel to G4 after G1)

- Map `.windsurf/rules/`, `.windsurf/skills/`, `AGENTS.md` to enforcers where they exist (and mark doctrine-only where they don't).
- Catalogue every config knob with plane / default / consumer / scope / reload policy.
- Cross-reference with G2b env map.
- Inventory prompt surfaces.

Exit of G4b: every rule in `.windsurf/rules/` is mapped; every config knob is catalogued; every env key has consumer + plane; every prompt file is located.

### Step 9 — Execute G5 (parallel to G4/G4b)

- Build MCP server registry from `.windsurf/mcp_config.json` cross-referenced with `tools/mcp/` and `tools/adg/mcp/`.
- Map `.windsurf/hooks.json` to hook scripts.
- Inventory `ops_scripts/**` with one-line role per script (group by subfolder).
- Map `.github/` workflows + `.pre-commit-config.yaml` + `pytest.ini`.
- Document startup/shutdown sequence.
- Index `.windsurf/workflows/*.md` as operator playbook.

Exit of G5: every MCP server has transport + launch command; every ops script has a role.

### Gate 3

- Storage, control plane, and ops envelope all mapped.
- Duplicate-responsibility signals identified during G4 (e.g., two Redis clients) are flagged for G6.

## Phase 4 — Normalization (G6)

### Step 10 — Execute G6

- Consume `unclassified_modules.md` (G1), equivalent G1b residue, duplicate signals from G2/G4/G5.
- Classify every special surface.
- Produce `duplicate_responsibility_register.md` with a proposed canonical owner per pair.
- Record proposed consolidation follow-ups — NO code changes.

Exit of G6: zero surfaces remain unclassified; every duplicate has a proposed owner; `proposed_consolidation_followups.md` lists each item with a proposed wave (G8+) to execute the consolidation.

### Gate 4

- No unclassified surfaces remain anywhere in G1–G5 artefacts.
- Duplicate responsibilities are explicit.

## Phase 5 — Integration (G7)

### Step 11 — Execute G7

- Build `traceability_matrix.yaml` mapping every v1.3 atom → embodying modules and every v1.3 edge → call-chain.
- Any atom or edge with no mapping is recorded in `open_questions.md` with a follow-up owner.
- Collect every B7 candidate from G1–G6 into `b7_candidate_register.md`.
- Write `whole_system_runtime_map.md` as the final integrated map.
- Write `operational_flow_walkthrough.md` as the single walkable end-to-end story (with module citations).

Exit of G7:
- Every v1.3 atom is mapped or explicitly in `open_questions.md`.
- Every v1.3 edge is mapped or explicitly in `open_questions.md`.
- Every G1–G6 artefact is cited at least once in `whole_system_runtime_map.md`.
- `operational_flow_walkthrough.md` cites a module at every stage.

## Stop condition for the full Wave G

Wave G is considered complete when:

1. All Phase-exit conditions above are met.
2. The four "definition of done" criteria in `dependency_and_risk_register.md` §"Definition of 'done' for Wave G as a whole" are satisfied simultaneously.
3. `G7_runtime_map/open_questions.md` lists every residual question with an owner — nothing is hidden.
4. B7 candidate register is the sole place new interaction candidates live; Wave E/F graph is unchanged.

## Operator checklist (quick reference)

```
[ ] Phase 0: ADG fresh; baseline commit recorded
[ ] Phase 1: G1 done; G1b done; Gate 1 passed
[ ] Phase 2: G2 / G2b / G3 / G3b done; Gate 2 passed
[ ] Phase 3: G4 / G4b / G5 done; Gate 3 passed
[ ] Phase 4: G6 done; Gate 4 passed
[ ] Phase 5: G7 done; traceability complete
[ ] Final: DoD criteria 1–4 all green
```

## What G does NOT do

- Does not edit `docs/wave_e/*` (Wave E/F is closed).
- Does not author atoms / edges / sources / exclusions.
- Does not close B7 candidates.
- Does not refactor code (consolidation proposals only, in G6).
- Does not modify `.env` or secrets.
- Does not change MCP configs, hooks, or rules — only inventories them.

When those actions are needed, they are opened as separate waves (Wave H onwards) with their own planning pass.
