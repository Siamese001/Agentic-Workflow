# Executive Summary Regen Voice Repair — W3 Receipt

**Plan:** [exec-summary-regen-voice-repair-unblock-e7c4a2.md](../../.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md)  
**Wave:** W3  
**Date:** 2026-05-26

## W3.1 — Incremental regen anchor

| Behavior | Detail |
|----------|--------|
| Snapshot | After judge-regen prepare, lane stores `_regen_attempt_parsed_snapshot` |
| Next cycle | `retry_qwen_for_judge_remediation(..., incremental_anchor_parsed=...)` |
| Core runner | `anchor_output_text` = full JSON of prior attempt (`format_regen_anchor_assistant_content`) |
| Publish | Scratch baseline unchanged on X2/G5/G3 reject; only regen assistant anchor advances |
| Thread | `extend_regen_thread_after_success` on X2 fail when `output_changed` (was missing) |

Receipt fields: `regen_anchor_source` = `incremental_prior_attempt` | `publish_baseline`.

## W3.2 — Incremental delta lines

| Line type | Purpose |
|-----------|---------|
| `PRIOR_ATTEMPT_SUMMARY` | Per-sentence diff vs scratch baseline |
| `STILL_FAILING_AFTER_PRIOR_ATTEMPT` | Dimensions/findings persisting vs prior-cycle judges |
| Filtered verbatim feedback | Drops connective/Additionally findings fixed in prior attempt |

## Proof

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_regen_incremental.py \
  tests/unit/apps_rg/test_executive_summary_regen_incremental_anchor.py \
  tests/unit/apps_rg/test_same_authority_regen_delegation.py \
  tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py \
  tests/unit/apps_rg/test_executive_summary_delta_class_routing.py \
  -o addopts= -q
```

**Result:** 17 passed (2026-05-26).
