# apps_eval

`apps_eval` is a deterministic grader harness for two product surfaces only:

- `apps_rg`
- `apps_lic`

It owns exam mechanics: fixtures, app output snapshots, deterministic graders,
scorecards, baseline comparison, sealed eval records, and optional L6 handoff
files. It does not own runtime authority, product state, post-run learning,
drift memory, calibration workflow, or release decisions.

When `--emit-l6-handoff` is set, apps_eval also writes `l6_shadow_bridge.json`
and span artifacts beside the eval record. The bridge is observer-only evidence
for core L6 G28 audit-completeness and G29 learning-firewall checks; it cannot
mutate current-run artifacts or perform durable writes.

Default runs grade snapshots:

```bash
python -m apps_eval run --suite apps_rg.dev.resume_generation --mode snapshot --deterministic-only
python -m apps_eval run --suite apps_lic.dev.outreach_message --mode snapshot --deterministic-only
```

## apps_rg eval workflow

Create a new development scenario fixture:

```bash
python -m apps_eval scaffold-apps-rg-scenario resume_tailor_new_case --description "Checks a new resume tailoring behavior."
```

Review the generated files under `apps_eval/fixtures/dev/apps_rg/<scenario_id>/`, adjust the
request, expectations, snapshot, and `resume.md`, then add the scenario id to
`apps_eval/registry/suites.yaml`.

Validate fixture shape and snapshot hashes:

```bash
python -m apps_eval validate-suite apps_rg.dev.resume_generation
```

Run the deterministic snapshot suite:

```bash
python -m apps_eval run --suite apps_rg.dev.resume_generation --mode snapshot --deterministic-only
```

Run every registered `apps_rg` development suite and review one matrix summary:

```bash
python -m apps_eval run-matrix --app apps_rg --split dev --mode snapshot --deterministic-only
```

Compare a record to a named baseline:

```bash
python -m apps_eval compare-baseline --record artifacts/apps_eval/runs/.../eval_record.json --name apps_rg.dev.resume_generation
```

Promote a reviewed passing record as the named baseline:

```bash
python -m apps_eval promote-baseline --record artifacts/apps_eval/runs/.../eval_record.json --name apps_rg.dev.resume_generation
```

Run the narrow live adapter only when runtime inputs and path budget are ready:

```bash
python -m apps_eval run --suite apps_rg.dev.resume_generation --mode live_adapter --no-deterministic-only
```

Live adapter mode is deliberately narrow:

- `apps_rg`: `agentic_core.runtime.entry.apps_rg_dispatch:dispatch_apps_rg_run`
- `apps_lic`: `apps_lic.runtime.dispatch.canonical_dispatch:build_cli_ingress_raw`
- `apps_lic`: `apps_lic.runtime.dispatch.canonical_dispatch:run_canonical_apps_lic_spine`

Holdout suites require `APPS_EVAL_RELEASE_GATE=1` and do not expose
development-readable scenarios.
