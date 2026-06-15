# Windows Path Budget Enforcement

## Why this exists

Windows classic Win32 file APIs reserve `MAX_PATH` at 260 characters. Even when a
machine has long-path support enabled, every process and dependency in an
artifact pipeline must opt in correctly. This repo treats 260 characters as an
incident boundary, not as usable budget.

Reference: https://learn.microsoft.com/windows/win32/fileio/maximum-file-path-limitation

## Trigger

Before Windows runs that create nested artifacts, the agent must preflight the
projected absolute output paths. This is mandatory for:

- `apps_eval` runs, especially `live_adapter` mode.
- `apps_rg` proof or evaluation runs that create scenario subdirectories.
- Any proof harness expected to emit nested `agentic_core` observability files.

## Budget

- Hard fail projected absolute paths at 240 characters or more.
- Warn at 230 characters or more.
- Prefer short artifact roots such as `artifacts/ae_rg_live`.
- Avoid descriptive nested output roots such as
  `artifacts/apps_eval/independent_apps_rg_live_runtime` for live proof runs.

The budget reserves space for generated run IDs, scenario names, late-added
artifact filenames, and tool-dependent path normalization.

## Required preflight

For `apps_eval` against the `apps_rg` live adapter, run:

```bash
python scripts/governance/check_windows_path_budget.py --out-dir artifacts/ae_rg_live --suite apps_rg.dev.resume_generation
```

If the check fails, shorten `--out-dir` before starting the evaluation. Do not
retry the same run with the same long root.

## Forbidden mitigations

- Do not treat `mkdir` success as proof that final artifact writes will work.
- Do not rely on Git or OS long-path settings as the only mitigation.
- Do not add application-specific path truncation in `agentic_core` to hide a
  too-long caller output root.
- Do not rerun long evaluations before the path budget check passes.

## RCA wording

When reporting this class of failure, say that the output root left insufficient
absolute-path budget for generated run, scenario, and artifact filename segments.
Name the shortest successful output root and the projected maximum path length
when available.

## Codex adapter

Codex backup-agent behavior must mirror this rule by pointing to this file and
to `scripts/governance/check_windows_path_budget.py`. The Codex skill must not
copy this rule body.
