# Wave Completion Discipline

> ⛔ Always-on rule: Markers required at wave boundaries.

## Required Markers

At wave boundaries, Cascade MUST emit:

**End of wave:**
```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<succinct summary>"
```

**Start of plan (Wave 1):**
```
python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>
```

**End of plan:**
```
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

## Why

Markers trigger automatic updates to:
- On-disk plan `.md` (Wave Structure table status: 🟢 → ✅)
- Notion Plans DB (Summary column append + Status)

Missing markers cause stale plans and NP4 skew violations.

## Bypass

`WAVE_COMPLETION_AUDIT_BYPASS=1` — disables audit hook advisory.
