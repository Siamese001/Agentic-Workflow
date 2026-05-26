# Executive Summary Regen Voice Repair — W2 Receipt

**Plan:** [exec-summary-regen-voice-repair-unblock-e7c4a2.md](../../.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md)  
**Wave:** W2  
**Date:** 2026-05-26

## W2.1 — Composite `delta_class`

When soft judges collectively fail `resume_voice` and (`executive_signal` or `synthesis_quality`), `resolve_delta_class` returns `executive_signal_and_voice_v1` **before** the legacy `resume_voice_humanize` branch.

Eligibility (`_executive_signal_and_voice_composite_eligible`):

- `resume_voice` ∈ major failed dims, and
- `executive_signal` or `synthesis_quality` ∈ major failed dims, and
- ≥2 soft provider keys **or** one judge fails voice + substantive dims on the same panel.

Brown SVP fixture (Gemini `resume_voice`, Anthropic `executive_signal`) → composite.

## W2.2 — Regen delta mapping

| Surface | Behavior |
|---------|----------|
| `format_delta_class_regen_instruction` | Executive arc + metric weave S3–S5 + connective variety + S5 FSA/metric + S6 forward (no Looking ahead) |
| `collect_judge_remediation_delta_lines` (compact) | Composite instruction first; append per-dimension lines when not duplicated; `METRIC_WEAVE_S3_S5` guard |
| Allowlist / budget | S1–S6, max 6 sentence edits |

Voice-only failure (single judge, `resume_voice` only) still routes to `resume_voice_humanize`.

## Proof

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py \
  tests/unit/apps_rg/test_executive_summary_delta_class_routing.py \
  -o addopts= -q
```

**Result:** 27 passed (2026-05-26).
