# ADR-033: SC-1 Gravity — Flip to Enforce Mode

- **Status**: Accepted
- **Date**: 2026-04-23
- **Deciders**: Cursor Agent (P2 Wave 8.1 execution) — user-directed
- **Impact Layers**: L0, L1, L2, L3, L4, L5, L6 (gravity crosses all)
- **Supersedes**: — (SC-1 has been in audit mode since 2026-04-17)

## Context

SC-1 (gravity import / illegal layer reach) detects cross-layer edges
that violate the layered architecture — e.g., an L0 routing module
reaching *down* into L2 execution without a guardian-annotated lazy
import, or an L2 executor reaching *up* into L0 routing types outside
the SSOT read pattern.

The check was promoted from research to `enabled: true, audit_mode: true`
on 2026-04-17. In audit mode violations are recorded in the
`violations` table but do not cause `tools/generate_full_adg.py` to
exit non-zero. For six days the backlog was **63 violations** — tracked
but not blocking.

## Investigation (P2 W1–W2, 2026-04-23)

- **W1**: Built `tools/reports/sc1_triage.py` classifying all 63 rows
  by source layer and incoming fan-in into P0/P1/P2 bands. Result:
  4 P0 (all L0→L2, all already had `# guardian: allow-layer-violation`
  markers), 0 P1, 59 P2.
- **W2**: Root cause was **not** a missing annotation backlog. The
  `tools/adg/core/guardian_filter.py` exemption window only covered
  `[line_no - 1, line_no]`, missing markers placed on the closing `)`
  of multi-line `from X import (...)` blocks. Expanding the window to
  `[line_no - 1, line_no + 4]` exempted 54 of the 63 rows immediately.
  The remaining 9 were L2 healers legitimately importing model-ID
  constants from `agentic_core.L0_routing.config.model_registry`
  (SSOT constants) and the L6 OTel heal-router emitter — annotated
  with `guardian: allow-layer-violation`. Net: 63 → 0.
- **W3**: Regression test
  `tests/unit/tools/generate/test_sc1_zero_baseline.py` locks the
  baseline at 0 and guards the filter-window behavior.
- **W4**: Migrated the SC/AP config SSOT from `artifacts/adg/` (git-
  ignored) to `config/sc_ap_config.json` (tracked), with explicit
  `baseline_violations: 0` and `baseline_snapshot` fingerprint so any
  drift is visible.

## Decision

**Flip SC-1 to enforce mode** in `config/sc_ap_config.json`:

```json
{
  "SC-1": {
    "enabled": true,
    "audit_mode": false,
    "promoted_date": "2026-04-17",
    "enforce_date": "2026-04-23",
    "baseline_violations": 0,
    "baseline_snapshot": "adg_indexed_04222026_2106.sqlite"
  }
}
```

In enforce mode, any new SC-1 gravity violation (a cross-layer edge
without a guardian marker in the exemption window) causes
`tools/generate_full_adg.py` to exit non-zero, which in turn fails the
ADG snapshot job and any downstream gate that consumes the snapshot.

## Consequences

### Positive
- Constitutional architecture boundaries become CI-enforced, not
  advisory. Authors must explicitly mark legitimate cross-layer reads
  with `guardian: allow-layer-violation` to pass.
- Zero-baseline locked by regression test + config snapshot fingerprint.
- The `--no-verify` bypass loophole is closed by
  `.github/workflows/subprocess-timeout-gate.yml` (parallel change,
  same session) and the SC/AP gate runs server-side on every PR.

### Negative / Costs
- New legitimate cross-layer imports require an Author-Gate-style
  annotation. Cost: 1 comment line per new edge.
- A malformed guardian marker (wrong phrase, wrong window) now blocks
  merges instead of just audit-logging. Mitigation: the window covers
  5 lines (`line_no - 1` through `line_no + 4`) which handles the
  overwhelming majority of single/multi-line import shapes.

### Reversibility

**Fully reversible**: Set `audit_mode` back to `true` in
`config/sc_ap_config.json` and re-run the ADG job. No code changes
required to revert. This is why the decision is flipped in config,
not in code.

## Enforcement

- **Primary**: `_DEFAULT_SC_AP_CONFIG` merged with live overrides
  in `tools/generate/validation/gates.py` (`_load_sc_ap_config`).
- **Regression**: `tests/unit/tools/generate/test_sc1_zero_baseline.py`.
- **Guardian filter**: `tools/adg/core/guardian_filter.py` (window:
  `[line_no - 1, line_no + 4]`).
- **Triage tool**: `tools/reports/sc1_triage.py` classifies any future
  drift by P-band and impact score.

## References

- Plan: `.windsurf/plans/<p2-w8.1-sc1-*>.md`
- Commits: `03c5698d38` (W1), `ac81b14039` (W2), `a6c4bf9d7d` (W3),
  `e0b60ed9e4` (W4), this ADR (W5).
- Filter: `tools/adg/core/guardian_filter.py`
- Gate: `tools/generate/validation/gates.py:_query_sc1_gravity`
