# Consolidation Artifacts — Baseline Management

All JSON baselines in this directory are **versioned, committed, and reviewed like code**.
They are consumed by CI gates in `ops_scripts/ci/` and `.github/workflows/agent-sprawl-check.yml`.

## Baseline Files

| File | Gate Script | Purpose |
| ---- | ----------- | ------- |
| `mro_diamond_baseline.json` | `ops_scripts/ci/mro_contract_check.py` | MRO diamond ceiling (ratcheting) |
| `mro_diamond_baseline.json` | `ops_scripts/ci/mro_new_diamond_check.py` | Entry-level new-diamond prevention |
| `active_set_snapshot.json` | `ops_scripts/ci/active_set_snapshot_check.py` | Active set drift detection |
| `centrality_baseline.json` | `ops_scripts/ci/centrality_gate.py` | Known-above-threshold gravity nodes |
| `executor_dispatch_snapshot.json` | `tests/core/test_executor_dispatch_snapshot.py` | Canonical dispatch keys per executor |
| `target_manifest_v3.json` | `artifacts/consolidation/validate_target_manifest.py` | Consolidation targeting manifest |

## Update Procedures

### MRO Diamond Baseline

**When**: A PR removes redundant mixin inheritance, lowering the diamond count.

1. Run `python ops_scripts/ci/mro_contract_check.py` — it will PASS with `INFO: consider updating`.
2. Update `mro_diamond_baseline.json`: set `"total"` to the new count, remove resolved entries.
3. Optionally commit with tag `MRO_BASELINE_LOWERED:<old>-><new>` for clarity.

**Policy**: Improvements are never blocked. Increases require `MRO_BASELINE_BUMP:<reason>`.

#### Auto-Lower (Local Only)

To auto-lower the baseline after removing diamonds:

```bash
AUTO_LOWER_MRO_BASELINE=1 python ops_scripts/ci/mro_contract_check.py
```

This rewrites the JSON with the reduced count and removes resolved entries.

**IMPORTANT**: `AUTO_LOWER_MRO_BASELINE=1` is **forbidden in CI**.
If `CI=true` or `GITHUB_ACTIONS=true`, the gate will HARD FAIL.
Baseline changes must be committed as intentional, reviewable diffs.

#### New Diamond Prevention

`mro_new_diamond_check.py` prevents reintroduction at the entry level.
Even if the total count stays within the ceiling, any diamond not already
in the baseline JSON will cause a HARD FAIL.

To add a new diamond intentionally:
1. Add the entry to `mro_diamond_baseline.json`.
2. Commit with tag `MRO_BASELINE_BUMP:<reason>`.

### Active Set Snapshot

**When**: A PR changes the active agent set (add/remove/rename agents).

1. Run `python ops_scripts/ci/active_set_snapshot_check.py` — it will FAIL with drift details.
2. Commit with tag `ACTIVE_SET_SNAPSHOT_BUMP:<reason>` — the gate auto-updates the snapshot.

**Policy**: Silent drift is a merge blocker.

### Centrality Baseline

**When**: A new module appears above the general threshold (15 importers) or an existing one is resolved.

1. Run `python ops_scripts/ci/centrality_gate.py` — it will FAIL with `NEW GRAVITY NODE`.
2. If the new node is intentional, add it to `centrality_baseline.json` under `known_above_threshold`.
3. Commit with message containing `CENTRALITY_BASELINE_BUMP:<reason>`.

**Policy**: New gravity nodes require justification. Resolved nodes should be removed from the baseline.

### Executor Dispatch Snapshot

**When**: An executor gains, removes, or renames dispatch keys.

1. Run `python -m pytest tests/core/test_executor_dispatch_snapshot.py` — it will FAIL with `Drift`.
2. Update `executor_dispatch_snapshot.json` with the new keys.
3. Commit with message containing `DISPATCH_SNAPSHOT_BUMP:<reason>`.

**Policy**: Snapshot drift without the bump tag is a merge blocker.

### Quarantine Ceiling

**When**: A new test must be quarantined or skipped.

1. Add entry to `tests/_quarantine/QUARANTINE_MANIFEST.json` and/or `docs/reports/plans/KNOWN_FAILING_TESTS.md`.
2. Update the ceiling in the manifest if needed.
3. Commit with message containing `QUARANTINE_CEILING_BUMP:<reason>`.

**Policy**: Ceilings must never increase without the bump tag. Decreases are always welcome.

## Required Commit Tags

| Tag | When Required |
| --- | ------------- |
| `MRO_BASELINE_BUMP:<reason>` | MRO baseline increase (ceiling raised) |
| `MRO_BASELINE_LOWERED:<old>-><new>` | MRO baseline decrease (improvement) |
| `CENTRALITY_BASELINE_BUMP:<reason>` | Centrality baseline changes |
| `DISPATCH_SNAPSHOT_BUMP:<reason>` | Dispatch snapshot changes |
| `QUARANTINE_CEILING_BUMP:<reason>` | Skip/quarantine ceiling increases |
| `ACTIVE_SET_SNAPSHOT_BUMP:<reason>` | Active set fingerprint changed |
| `AGENT_COUNT_BUMP:<reason>` | Active agent count exceeds cap (149, discovery-aligned) |

## Reviewing Baseline Changes

When reviewing a PR that modifies any baseline:

1. Verify the commit message contains the appropriate bump tag.
2. Verify the change is a **decrease** (ratchet direction) or has clear justification.
3. Verify the CI gates pass with the updated baseline.
4. Verify no other baselines were silently modified.
