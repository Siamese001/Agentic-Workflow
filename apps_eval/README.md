# apps_eval

`apps_eval` is a deterministic grader harness for two product surfaces only:

- `apps_rg`
- `apps_lic`

It owns exam mechanics: fixtures, app output snapshots, deterministic graders,
scorecards, baseline comparison, sealed eval records, and optional L6 handoff
files. It does not own runtime authority, product state, post-run learning,
drift memory, calibration workflow, or release decisions.

Default runs grade snapshots:

```bash
python -m apps_eval run --suite apps_rg.dev.resume_generation --mode snapshot --deterministic-only
python -m apps_eval run --suite apps_lic.dev.outreach_message --mode snapshot --deterministic-only
```

Live adapter mode is deliberately narrow:

- `apps_rg`: `agentic_core.runtime.entry.apps_rg_dispatch:dispatch_apps_rg_run`
- `apps_lic`: `apps_lic.runtime.dispatch.canonical_dispatch:build_cli_ingress_raw`
- `apps_lic`: `apps_lic.runtime.dispatch.canonical_dispatch:run_canonical_apps_lic_spine`

Holdout suites require `APPS_EVAL_RELEASE_GATE=1` and do not expose
development-readable scenarios.
