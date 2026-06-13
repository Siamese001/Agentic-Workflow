# RCA: Token Context Not Maximized to 200K for SWE 1.5

**Date:** 2026-03-27
**Severity:** MEDIUM — Performance Optimization Gap
**Status:** ✅ RESOLVED — 2026-03-27

---

## Violation / Issue

The token optimization tools and plan validation skills were using legacy context window limits (150K for GREEN, 170K for YELLOW) instead of maximizing the 200K context window available for the SWE 1.5 model. This led to unnecessary wave splitting and sub-optimal context utilization.

---

## Root Cause

**Proximate cause:** Hardcoded threshold values in `tools/evidence/_run_token_optimizer_plan.py`, `tools/adg/wave_packer.py`, and `.windsurf/skills/plan-validation/main.py`.

**Systemic cause:** Thresholds were set during an earlier phase when 150K was the conservative target, and they were not updated when the model capability/target was ratcheted to 200K.

---

## Corrective Actions Taken

### 1. Updated Token Optimizer Thresholds ✅
Modified `tools/evidence/_run_token_optimizer_plan.py` to use:
- **GREEN**: ≤ 180,000 tokens (was 150,000)
- **YELLOW**: ≤ 200,000 tokens (was 170,000)

### 2. Updated Wave Packer Thresholds ✅
Modified `tools/adg/wave_packer.py` (in `run_optimization`) to align with the new 180K/200K thresholds.

### 3. Updated Plan Validation Skill ✅
Modified `.windsurf/skills/plan-validation/main.py` to raise issues only if an estimate exceeds 200K (was 175K).

---

## Preventive Measures

- [x] Thresholds updated across all relevant tools
- [x] Verification run performed using `tools/evidence/_run_token_optimizer_plan.py`
- [x] Documentation updated via this RCA

---

## Evidence

- **Updated Optimizer:** `tools/evidence/_run_token_optimizer_plan.py` (lines 272)
- **Updated Packer:** `tools/adg/wave_packer.py` (lines 203)
- **Updated Skill:** `.windsurf/skills/plan-validation/main.py` (lines 59-63)
- **Verification Output:** `python tools/evidence/_run_token_optimizer_plan.py` now shows 151,100 tokens as **GREEN**.

---

## Status

✅ **RESOLVED** — All tools and skills now support 200K context maximization.
✅ **RCA AUTO-CLOSED** per Constitutional Rule #9.
