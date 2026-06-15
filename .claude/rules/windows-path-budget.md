# Windows Path Budget — stub

> On-demand before nested-artifact Windows runs (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. Windows `MAX_PATH`=260 is an incident boundary: before runs creating nested artifacts (apps_eval `live_adapter`, apps_rg proof/eval) preflight projected absolute paths — hard fail ≥240, warn ≥230; prefer short artifact roots (`artifacts/ae_rg_live`); don't retry a long run before shortening `--out-dir`. Enforced: `scripts/governance/check_windows_path_budget.py`.
