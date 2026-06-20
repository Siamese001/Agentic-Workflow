# ADG Audit Pipeline

> **SSOT entrypoint**: `python tools/adg/run_full_adg_audit.py`
> **Plan**: `.codex/plans/adg-audit-pipeline-integration-7f2c93.md`
> **Status**: Implemented 2026-05-03 (Waves W1–W5)

The ADG audit pipeline is a two-stage, certifiable flow that binds
`tools/generate/generate_full_adg.py` (snapshot + gate chain) to
`tools/adg/three_bucket_gap_report.py` (seven-class defect
reconciliation) via a manifest contract. The wrapper is the single
fail-closed consumer that local devs and CI both invoke.

## Why This Exists

Before this pipeline:

- Missing post-ADG gate scripts **silently skipped** (`return` on missing script).
- No machine-readable proof of which gates ran, with what status.
- The gap report defaulted to `_latest_snapshot()` — race-prone in CI.
- `--require-runtime-proof` did not exist; runtime-thin reports were
  indistinguishable from certification-clean.

After this pipeline: every gate run is recorded, every skip is either
intentional (diagnostic mode) or a hard failure (certification mode),
and runtime-proof status is a deterministic gate, not a vibe check.

## Two-Stage Flow

```
Stage 1:  tools/generate/generate_full_adg.py
          ├─ pre-flight: mcp_config_drift, wal_checkpoint, locked_files
          ├─ build: syntax, integrity, p2_ratchet, ...
          ├─ post-commit-validation: p0, p1_ratchet, dead_imports, ...
          ├─ post-ADG-subprocess: wiring, config-ref, lifecycle, except-contract, test-coverage
          └─ EMITS:
             ├─ artifacts/adg/adg_indexed_<ts>.sqlite     (snapshot)
             ├─ artifacts/adg/adg_gate_invocation_manifest_<ts>.json
             └─ artifacts/adg/adg_generation_manifest_<ts>.json

Stage 2:  tools/adg/three_bucket_gap_report.py --snapshot <sqlite_path>
          ├─ seven-class defect reconciliation
          └─ EMITS:
             ├─ docs/reports/adg/THREE_BUCKET_GAP_REPORT.json
             └─ docs/reports/adg/THREE_BUCKET_GAP_REPORT.md

Wrapper:  tools/adg/run_full_adg_audit.py
          ├─ runs Stage 1 with ADG_CERTIFICATION_MODE=1 (in certification mode)
          ├─ reads generation manifest → resolves exact sqlite_path
          ├─ cross-checks gate invocation manifest against REQUIRED_GATES registry
          ├─ enforces --require-runtime-proof against generation_manifest.runtime_proof_status
          ├─ runs Stage 2 against the explicit snapshot path
          └─ EMITS:
             └─ docs/reports/adg/AUDIT_PIPELINE_RECEIPT.json
```

## Manifest Contract

### Gate invocation manifest (`adg_gate_invocation_manifest_<ts>.json`)

Proves which gates ran with which status. Schema:

| Field | Type | Meaning |
|---|---|---|
| `timestamp` | str (ISO-8601 Z) | When the manifest was written |
| `generator_entrypoint` | str | Relative path to generator |
| `sqlite_path` | str \| null | Snapshot produced by this run |
| `generation_exit_code` | int \| null | Generator's exit code |
| `certification_status` | `"clean"` \| `"failed"` \| `"diagnostic_only"` | |
| `gates` | list[GateRecord] | Every invocation |
| `unexpected_skips` | list[GateRecord] | Subset with status=`missing_script` |
| `failed_gates` | list[GateRecord] | Subset with status ∈ `{fail, timed_out, missing_script}` |
| `deferred_failures` | list[GateRecord] | Subset with status=`deferred_fail` |

Each `GateRecord` has: `name, phase, kind, blocking_mode, status,
exit_code, duration_s, started_at_utc, finished_at_utc, script_rel,
message`.

### Generation manifest (`adg_generation_manifest_<ts>.json`)

Snapshot handoff contract — the wrapper reads this to find the exact
sqlite path. Schema:

| Field | Type | Meaning |
|---|---|---|
| `timestamp` | str | |
| `sqlite_path` / `snapshot_path` | str \| null | The canonical snapshot |
| `commit_sha` | str \| null | |
| `repo_state_hash` | str \| null | |
| `generation_exit_code` | int | |
| `p0_status` | str | `pass` / `deferred_fail` / `unknown` |
| `gate_manifest_path` | str | Pointer to paired gate manifest |
| `runtime_proof_status` | `"attested"` \| `"view_present_zero_attested"` \| `"view_absent"` | |
| `runtime_attested_edge_count` | int | |
| `registry_bucket_edge_count` | int | |
| `created_at_utc` | str | |
| `certification_status` | str | |

Also written: `adg_generation_manifest_latest.json` (local dev
convenience). **CI MUST NOT read `latest.json`** — the wrapper resolves
by timestamped filename with mtime-validated recency.

## Runtime Proof Rule

`runtime_proof_status` has three states:

- **`attested`**: `v_runtime_proof` exists AND at least one row has
  `attesting_trace_count >= 1`. Certification-clean eligible.
- **`view_present_zero_attested`**: view exists but all rows have zero
  attestation. NOT certification-clean — the OTel exporter hasn't
  populated traces yet.
- **`view_absent`**: the view is missing entirely. Pre-runtime-ADG
  schema OR never-generated. NOT certification-clean.

`--require-runtime-proof` fails the run with exit 2 if status is not
`attested`. Leave the flag OFF in local dev until OTel pipelines are
wired; turn it ON in certification CI once `v_runtime_proof` is
populated end-to-end.

## Diagnostic vs Certification Mode

| Behavior | `--mode diagnostic` | `--mode certification` (default) |
|---|---|---|
| `ADG_CERTIFICATION_MODE` env | unset | `1` |
| Missing gate script | SKIP (logged) | FAIL (exit 2) |
| Generator exit != 0 | tolerated if `--diagnostic-allow-failed-generator` | FAIL |
| Required gate absent from manifest | tolerated | FAIL |
| Runtime-thin report (`--require-runtime-proof` off) | markdown banner | markdown banner |
| Runtime-thin report (`--require-runtime-proof` on) | gate fails anyway | FAIL |
| `certification_status` in receipt | `diagnostic_only` | `clean` or `failed` |

Markdown reports get a loud banner when runtime is not attested:

```
> ⚠ DIAGNOSTIC ONLY — RUNTIME-THIN (runtime_proof_status=view_absent).
> This report was produced without runtime attestation; do NOT treat as
> certification-clean.
```

## Enforcement planes (ADR-081)

Four planes integrate old ADG CI into the certification spine:

| Plane | SSOT | Blocks certification |
|-------|------|----------------------|
| 1 Generator | `tools/generate/_required_gates.py` | Yes (invocation manifest) |
| 2 Snapshot | `ops_scripts/ci/adg_gate_manifest.yaml` | Yes (`run_adg_three_graph_tests --strict`) |
| 3 Dispatcher | `python -m ops_scripts.ci.adg_gates.run` | Yes when `ADG_CERTIFICATION_MODE=1` |
| 4 Satellite | Contract gates, AUDIT, M-gates | Selective |

Rollup artifact: `artifacts/adg/adg_enforcement_report_<ts>.json`.  
`check_adg_certified.py --rollup` reads it (default).  
Gate ownership: [ADG_Gate_Ownership.md](ADG_Gate_Ownership.md).

### CI commands

```bash
# Full certification
python tools/adg/run_full_adg_audit.py --mode certification --format both

# PR quick (committed snapshot)
python ops_scripts/ci/run_adg_three_graph_quick_gate.py

# Changed-files subset
python ops_scripts/ci/run_adg_three_graph_tests.py --suite changed --strict --snapshot <path>
```

## Required-Gate Registry

`tools/generate/_required_gates.py` is the declarative proof contract.
Every entry marked `required_in_manifest=True` must appear in the gate
invocation manifest at certification time, or the wrapper fails.

Adding a gate: append to `REQUIRED_GATES`. Removing is a breaking change
and requires an ADR.

## Local Commands

```powershell
# Full certification audit (default)
python tools/adg/run_full_adg_audit.py --mode certification --format both

# Same, with runtime-proof enforcement (requires OTel-populated snapshot)
python tools/adg/run_full_adg_audit.py --mode certification --require-runtime-proof

# Diagnostic dev-loop (tolerate generator failures, still produce report)
python tools/adg/run_full_adg_audit.py --mode diagnostic --diagnostic-allow-failed-generator

# Regression tests
python -m pytest tests/unit/tools_adg/ -v -p no:xdist
```

## CI Integration

`.github/workflows/adg-ci-gates.yml` invokes the wrapper so the
manifests are produced and cross-checked on every push. See the
"ADG Audit Pipeline (wrapper)" step for the exact invocation.

## Known Limitations

1. **Runtime-proof is opt-in.** Until OTel exporters emit into
   `runtime_adg_store` and the generator ingests them,
   `--require-runtime-proof` fails by construction. The wrapper's
   default leaves the flag off so local dev isn't blocked.
2. **atexit safety net.** If `generate_full_adg.py` segfaults before
   `main()` calls `recorder.finalize()`, the `atexit` hook writes a
   best-effort partial manifest. The wrapper detects this via
   `status=fail` records with `message="in-flight at process exit"`.
3. **Required-gate registry maintenance.** Adding a new gate to the
   generator without updating `_required_gates.py` means certification
   cannot see it as required. This is intentional — the registry is the
   proof contract.

## Cross-references

- `docs/guides/ADG_MCP_MIGRATION.md` — MCP-layer consumers of the
  snapshot
- `docs/reference/_primers/AST Dependency Graphs (ADG)/` — ADG mental
  model
- ADR-080 — runtime certification trust levels (see Fort Knox doctrine)
