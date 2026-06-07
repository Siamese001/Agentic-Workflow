---
description: Thin alias — weekly Author-Gate calibration report (/author-gate-calibration-report)
---

# /author-gate-calibration-report

**Tier:** Workflow alias · **Procedure:** run `python .cursor/scripts/generate_calibration_report.py` per steps below.

**Invariant / tuning:** [author-gate-svp-calibration.md](../rules/author-gate-svp-calibration.md) · output `docs/reports/calibration/<YYYY-Www>.md`

## Steps

1. Run `python .cursor/scripts/generate_calibration_report.py` (prior week window).
2. Review firing rate, FP rate, flip-readiness in the generated markdown.
3. Apply `author-gate-svp-calibration.md` if CI miss bands require Author-Gate triggers.

⛔ Full narrative and field definitions stay in the script + calibration rule — not duplicated here.
