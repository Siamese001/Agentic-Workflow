# Downstream ADG Consumer Mode Matrix

**Status**: Phase 1 audit (W4 work — full audit + mode declarations deferred)
**Last reviewed**: 2026-04-29

This matrix identifies ADG consumers across the repo and assigns each one a
**mode** under the three-bucket authority model:

* **proof_mode** → consumes `proof_view` only. Used for governance / hotspot
  / coverage / refactor-impact / layer-boundary claims. Output is treated as
  authoritative.
* **risk_mode** → consumes `risk_view` only. Used for cleanup backlog,
  missing-trace detection, dependency-uncertainty analysis. Output is
  labeled "risk", never as proof.
* **inventory_mode** → consumes `inventory_view`. Used for debugging /
  audits / migrations / before-after comparison. Output is labeled
  "inventory", never as proof.

A consumer that does not declare a mode silently risks consuming unresolved /
unknown / partial / external / test-only edges as proof — a constitutional
violation under the new authority model.

## Phase 1 (W1) — declared modes

The following consumers had their mode locked in by virtue of CI gate
behavior the prior 2026-04-28 commit landed:

| Consumer | Path | Mode | Claim type | View used | Influenced by unresolved? | Status |
|---|---|---|---|---|---|---|
| G-EDGE-AUTHORITY | `ops_scripts/ci/check_edge_authority_well_formed.py` | proof_mode | "every edge has a valid authority" | full `edges` (closed-enum) | No (it asserts no NULL) | Compliant |
| G-UNRESOLVED-RATCHET | `ops_scripts/ci/check_unresolved_edges_ratchet.py` | risk_mode | "unresolved-edge count must not grow" | `mv_edges_unresolved` | Yes (this is its purpose) | Compliant — labels output as risk |
| G-DANGLING-IMPORT | `ops_scripts/ci/check_dangling_imports.py` | risk_mode | "broken target imports" | filesystem AST (not via SQLite) | Yes | Compliant — risk surface |
| G-CALL-MULTIPLICITY | `ops_scripts/ci/check_call_multiplicity.py` | inventory_mode | "files with N+ top-level calls" | filesystem AST (not via SQLite) | N/A | Compliant — inventory surface |

## Phase 1 (W1) — undeclared modes (W4 work)

The consumers below were identified via static grep for `FROM edges`,
`FROM mv_edges_*`, `FROM edge_view`, and `adg_*` MCP tool usage. Each one
**will need an explicit mode declaration** before ADG_CERTIFIED can pass.

### Tier A — high-impact production consumers

| Consumer | Path | Inferred mode | Claim type | View used today | Action needed |
|---|---|---|---|---|---|
| ADG MCP server | `tools/adg/mcp/server.py` | inventory_mode (mixed) | Serves arbitrary queries | raw `edges`/`nodes`/`violations` | Declare per-tool mode (proof_view for `adg_node`, inventory_view for `adg_edge_fanin`) |
| Validation gates | `tools/generate/validation/gates.py` (45 matches) | proof_mode (intent) | Layer-boundary, forbidden-deps | raw `edges` + manual filters | Migrate to `proof_view`; verify no unresolved leaks |
| Infra wiring views | `tools/generate/infra_wiring_views.py` (16 MVs) | proof_mode (governance) | Wiring/seam violations | raw `edges` | Add `WHERE authority_status IN PROOF_STATUSES` to each MV definition |
| Materialized views — phase A | `tools/generate/materialized_views/phase_a_path_authority.py` | proof_mode | Path-authority & blast-radius | raw `edges` | Migrate to `proof_view` |
| Materialized views — phase C | `tools/generate/materialized_views/phase_c_trace_drift_debt.py` | risk_mode (likely) | Trace drift | raw `edges` + `violations` | Declare risk_mode; label output |
| Reporting analysis | `tools/generate/reporting/analysis.py`, `reports.py` | proof_mode (intent) | Hotspot / chokepoint reports | raw `edges` | Migrate to `proof_view` |
| ADG consistency verifier | `ops_scripts/verification/verify_adg_consistency.py` (23 matches) | inventory_mode | Schema/structure assertions | raw `edges`/`meta` | Declare inventory_mode |
| Behavioral coverage ratios | `ops_scripts/verification/report_behavioral_coverage_ratios.py` | proof_mode (intent) | Coverage adequacy | raw `edges` | Migrate to `proof_view`; coverage cannot include unknowns as proof |
| Low-confidence zones | `ops_scripts/verification/verify_low_confidence_zones.py` | risk_mode | Confidence < threshold | raw `edges` + `confidence_score` | Already risk-shaped; declare explicitly |
| Pre-prompt classifier | `.windsurf/scripts/pre_prompt_classifier.py` | inventory_mode (sentinel-only) | Health probe | `meta` table | Declare inventory_mode |
| ADG integration engine | `agentic_core/L3_orchestration/reasoning/engines/adg_integration.py` | proof_mode (T2/T3 routing) | Blast radius for routing | raw `edges` | Migrate to `proof_view` for routing decisions |

### Tier B — analysis / debugging tools

| Consumer | Path | Inferred mode | View used today |
|---|---|---|---|
| `tools/adg/analysis/materialized_views.py` | inventory_mode | raw `edges` |
| `infrastructure/utils/adg_violations.py` | proof_mode (governance) | `violations` table |
| `tools/analysis/_qwen_adoption_audit.py` | inventory_mode | raw `edges` |
| `tools/graph/sqlite_helpers.py` (15 matches) | inventory_mode (helper lib) | raw `edges` |
| `tools/debug/_dead_dup_scan.py` | inventory_mode | raw `edges` |
| `tests/unit/tools/adg/test_adg_snapshot_rotation.py` | inventory_mode (test) | raw `edges`/`meta` |

### Tier C — archived (already excluded)

The following directories contain archived consumers and are NOT counted
toward the certification surface:

* `tools/archive/adg_root_oneshots_w5.10/`
* `tools/archive/tools_graveyard_w5.12/`
* `tools/archive/ops_scripts_ci_oneshots_w4.2/`
* `archives/`
* `tests/_archived_obsolete/`

These contain hundreds of legacy SQL queries against `edges`/`mv_edges_*`
but are not part of the active CI surface.

## Mode-mismatch CI gate (W4)

The W4 gate `ops_scripts/ci/check_consumer_mode_declared.py` (NOT YET
WRITTEN) will:

1. Scan every Python file under `tools/`, `ops_scripts/`, `agentic_core/`,
   `apps_*/` for `FROM edges`, `FROM mv_edges_*`, `FROM edge_view`,
   `FROM proof_view`, `FROM risk_view`, `FROM inventory_view`, and
   `adg_*` MCP tool usage.
2. For each match, look for a `# adg-mode: proof | risk | inventory`
   declaration within the same function or file-level docstring.
3. Fail if any consumer file has ADG-edge access but no mode declaration.

This gate is the deterministic enforcement layer for "no consumer may
silently use all edges as proof." It is W4 work; until it lands, this
matrix is the manual record.

## Forbidden-mode patterns (constitutional)

The following patterns MUST NEVER ship in proof_mode consumers:

```python
# FORBIDDEN: silently uses all edges as proof
con.execute("SELECT COUNT(*) FROM edges WHERE relation_type = 'imports'")

# FORBIDDEN: counts unresolved/dynamic as proof
con.execute("SELECT * FROM edge_view WHERE from_layer = 'L0' AND to_layer = 'L3'")
```

The required pattern for proof_mode consumers:

```python
# adg-mode: proof
con.execute("SELECT COUNT(*) FROM proof_view WHERE relation_type = 'imports'")

# adg-mode: proof — strict
con.execute(
    "SELECT * FROM edges WHERE authority_status IN ('AUTHORITATIVE','AUTHORITATIVE_RUNTIME','AUTHORITATIVE_REGISTRY') "
    "AND relation_type = 'imports'"
)
```

## Outstanding scope (W4)

* **Full consumer inventory**: a one-time scan to enumerate every consumer
  with line-level evidence; the static grep above hit 416 files (mostly
  archived) and the live surface is closer to ~80 files.
* **Per-file mode declarations**: every live consumer needs the
  `# adg-mode: ...` comment.
* **CI gate**: `check_consumer_mode_declared.py` to enforce.
* **Migration of MV definitions**: 16 MVs in `infra_wiring_views.py` need
  `WHERE authority_status IN PROOF_STATUSES` filters.
* **MCP server per-tool mode**: `tools/adg/mcp/server.py` exposes
  `adg_violations`, `adg_edge_fanin`, `adg_edge_fanout`, `adg_node`,
  `adg_p0_wave_plan` — each needs to declare which view it queries.

## How a consumer earns a proof_mode declaration

1. Author confirms the consumer's claim type is governance / hotspot /
   coverage / refactor-impact / layer-boundary.
2. Author migrates the SQL to query `proof_view` (or `WHERE authority_status
   IN PROOF_STATUSES`).
3. Author adds the `# adg-mode: proof` comment at the call site or in the
   function docstring.
4. Author runs the regression test ensuring the consumer's output does not
   shrink unexpectedly under the new view (some shrinkage is expected
   because unresolved/dynamic/test-only/external edges are excluded).
5. CI gate passes.
