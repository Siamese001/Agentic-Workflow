# Judge Calibration Cadence — stub

> On-demand during eval/judge work (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged. Every LLM judge is recalibrated against human labels on a bounded cadence (trace-grader weekly / rubric biweekly / pairwise monthly); a stale (>cadence×1.5), over-`unknown_budget`, <0.7-agreement, or `rubric_version`-changed judge is DISQUALIFIED from driving §5/§6D. Ledger: `data/judge_calibration/<id>/<week>.json`. Detail: `config/judges/rubrics.yaml`, ADR-032/036. Bypass: `JUDGE_CALIBRATION_CADENCE_BYPASS=1`.
