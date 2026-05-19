# W3R — Graph baseline orphan remediation receipt

**Plan:** [cursor-governance-two-tier-b4e8f2.md](../../.cursor/plans/cursor-governance-two-tier-b4e8f2.md)  
**Generated:** 2026-05-19

## STATUS: PASS

## ROOT_CAUSE

After W3 plan archive, `ops_scripts/ci/baselines/graph_layer_evidence_baseline.json` still listed ~508 grandfathered **top-level** `.cursor/plans/*.md` paths. Integrity validation required each entry to exist at that exact path. Archived plans moved to `.cursor/plans/_archive/2026-05/<basename>.md`, producing **507** `baseline_orphan_entry` failures. Active scan also targeted `.windsurf/plans` instead of `.cursor/plans` SSOT.

## Orphan counts

| Metric | Value |
|--------|------:|
| ORPHAN_REFERENCE_COUNT_BEFORE | 507 |
| ORPHAN_REFERENCE_COUNT_AFTER | 0 |

## Plan inventory

| Metric | Value |
|--------|------:|
| ACTIVE_PLANS_COUNT (top-level, excl. README/template) | 10 |
| ARCHIVED_PLANS_COUNT (W3 manifest moves) | 490 |
| Archive folder | `.cursor/plans/_archive/2026-05/` |

## FILES_CHANGED

- [check_graph_layer_evidence.py](../../ops_scripts/ci/check_graph_layer_evidence.py)
- [l2-rationalization-waves-c8e4f1.md](../../.cursor/plans/l2-rationalization-waves-c8e4f1.md) — §22 ADG sections
- [exec-summary-graph-only-b5a963.md](../../.cursor/plans/exec-summary-graph-only-b5a963.md) — §22 ADG sections
- [graph-skills-hardening-f3a8c1.md](../../.cursor/plans/graph-skills-hardening-f3a8c1.md) — §22 ADG sections

## COMMANDS_RUN

| Command | Exit |
|---------|-----:|
| `python ops_scripts/ci/check_graph_layer_evidence.py` | 0 |
| Orphan probe (pre-W3R top-level-only logic) | 507 → 0 |

## NON_CLAIMS

- No unarchive; no archive deletes; gate thresholds unchanged.
- W4/W5 not claimed here.
- Pre-existing `10C` pilot proof-evidence failures in `run_contract_gates.py` are isolated from W3R.
