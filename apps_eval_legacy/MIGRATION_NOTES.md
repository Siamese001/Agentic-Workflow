# apps_eval Migration Notes

## Why This Exists

The old `apps_eval` package mixed evaluation harness concerns with agent-like
scaffold, reasoning/orchestration layers, HOP terminology, platform-wide test
suites, MetaLearningBus publishing, Exit/runtime authority, and L6 promotion
adjacent logic.

The reset separates responsibilities:

- `apps_eval`: fixtures, rubrics, deterministic graders, scorecards,
  regression comparison, sealed eval artifacts, optional L6 handoff artifacts.
- `apps_rg` and `apps_lic`: product runtimes under test.
- L6: post-run learning, drift tracking, RCA, calibration workflow, and
  promotion/regret decisions.

## Quarantined Source

The original package was moved to:

`apps_eval_legacy/original_tree/apps_eval/`

Use it only as historical reference. New code must not import it.

