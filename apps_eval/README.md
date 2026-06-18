# apps_eval

`apps_eval` is a deterministic grader harness for two product surfaces only:

- `apps_rg`
- `apps_lic`

It owns exam mechanics: fixtures, app output snapshots, deterministic graders,
scorecards, baseline comparison, sealed eval records, and optional L6 handoff
files. It does not own runtime authority, product state, post-run learning,
drift memory, calibration workflow, or release decisions.

Phase 2 adds a regression flywheel artifact (`regression_flywheel.json`) that
rolls up failure-mode counts, hotspot scenarios, and baseline deltas so the
harness can explain *why* a run failed, not just whether it failed.

Phase 3 adds historical trend scanning and a fail-closed release gate over
persisted `eval_record.json` files. The trend command writes both JSON and
markdown dashboards; the gate command reuses the same snapshot and returns a
distinct exit code for blocked versus regression outcomes.

Phase 4 optionally writes a downstream L6 shadow bridge from `trend-dashboard`
or `release-gate` with `--emit-l6-shadow`. The bridge is a read-only
future-run-only sidecar that inventories the dashboard or gate outputs without
mutating the current run.

When `--emit-l6-handoff` is set, apps_eval also writes `l6_shadow_bridge.json`
and span artifacts beside the eval record. The bridge is observer-only evidence
for core L6 G28 audit-completeness and G29 learning-firewall checks; it cannot
mutate current-run artifacts or perform durable writes.

## apps_lic eval workflow

`apps_lic` remains deterministic-first in this harness, but the live adapter now
passes through the redesign inputs that matter for JD-anchored outreach:

- `message_type_hint`
- `message_modifiers`
- `application_status`
- `desired_next_step`
- `governed_opportunity_facts`
- `c0_required_namespaces`

That keeps the eval surface aligned with the redesigned runtime contract while
still keeping `apps_eval` in the post-run grading lane.

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

Build a trend dashboard from historical records:

```bash
python -m apps_eval trend-dashboard --records-root artifacts/apps_eval/runs --app apps_rg --split dev
```

Emit the optional downstream L6 bridge alongside the dashboard artifacts:

```bash
python -m apps_eval trend-dashboard --records-root artifacts/apps_eval/runs --app apps_rg --split dev --emit-l6-shadow
```

Evaluate the release gate against the same history:

```bash
python -m apps_eval release-gate --records-root artifacts/apps_eval/runs --app apps_rg --split dev
```

Emit the optional downstream L6 bridge alongside the gate artifacts:

```bash
python -m apps_eval release-gate --records-root artifacts/apps_eval/runs --app apps_rg --split dev --emit-l6-shadow
```

Exit codes:

- `0`: pass
- `1`: blocked by insufficient evidence or threshold failure
- `2`: regression detected

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
