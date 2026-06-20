# SSOT Folder Routing — pointer stub

> Demoted from the always-on surface to cut context (plan `always-on-rule-surface-cut-c7f3a1`).
> Loads on demand when creating new files. Enforcement unchanged (fires regardless).

**Invariant (kept):** every NEW Python file lands in its canonical SSOT folder — `check_*`/`*_gate.py`
→ `ops_scripts/ci/`; calibration/binder/poller → `ops_scripts/calibration/`; `purge_*`/`cleanup_*` →
`ops_scripts/maintenance/`; `pre_*`/`post_*` hooks → `.codex/governance/scripts/`; else →
`tools/<domain>/`. Hook-prefix files misrouted = silent disable. Pre-existing files exempt.
Constitutional §31.

**Full detail (on demand):** sibling `plan-location.md`.
**Enforcement (prose-independent):** `pre_write_gate.py` (fail-closed) +
`ops_scripts/ci/check_ssot_folder_routing.py` (T7q). Bypass: `SSOT_FOLDER_BYPASS=1`.
