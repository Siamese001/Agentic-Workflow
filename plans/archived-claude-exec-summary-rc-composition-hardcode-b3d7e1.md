---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\exec-summary-rc-composition-hardcode-b3d7e1.md'
original_relative_path: 'exec-summary-rc-composition-hardcode-b3d7e1.md'
source_sha256: 00b02a8b5ac999b51094aa1861d80774911c22e14db77e0393fac89364271b00
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: exec-summary-rc-composition-hardcode-b3d7e1

## Objective

Fix the three hard-coded "commercialization" strings that are the **true structural root causes** of
the persistent `X3_REVIEW_JUDGE_SOFT_FAIL` (exit code 4) for the `executive_summary` section.

Previous plan `exec-summary-rc-structural-repair-f4a8c2` addressed **symptoms** (E0 example,
fragment gate, connective tissue). This plan addresses the **root code defects** that survive
all symptom patches.

## Parent Plan Chain

- `exec-summary-rc-structural-repair-f4a8c2` (Notion: 36d27693-f55c-8131-b67c-fc0aa960d9dc)

## Root Cause Evidence

**Discovered during W6 proof run for `exec-summary-rc-structural-repair-f4a8c2`.**

Investigation trace:
1. `provider_response.json` (first pass) — both `executive_strategy_thesis` AND `resume_display_text`
   contained "digital innovation" (W1 fix worked at LLM output level).
2. `synthesis_regen` — both attempts rejected for `$22m` style echo; reverted to first pass.
3. `graph_only_generation_quality_repair` — repaired S1 from "aligns" to "Technology strategy executive".
4. BUT `parsed_output.json.parsed.resume_display_text` = "unifies...commercialization" (WRONG).
5. Traced to `executive_summary_composition_plan.json.target_picture` = "regulatory lineage, and
   **commercialization** into one enterprise IT direction" — hard-coded in Python source.
6. `parsed_output.json` embeds the composition plan, inheriting the `target_picture`.
7. The `target_picture` drives **what text the model puts in `resume_display_text`**, overriding the
   E0 example fix.

## Root Causes

### RC-E: Hard-coded "commercialization" in `target_picture`
- **File**: `apps_rg/runtime/sections/executive_summary_composition.py`
- **Lines**: 515–519
- **Code**: `"regulatory lineage, and commercialization into one enterprise IT direction"`
- **Impact**: This string is emitted into the composition plan JSON, embedded in `parsed_output.json`,
  and sent to X1D judges as the canonical candidate description. The model sees it as the authoritative
  description of what S1 should say.

### RC-F: Hard-coded "commercialization" in S3 brushstroke guidance
- **File**: `apps_rg/runtime/sections/executive_summary_synthesis_contract.py`
- **Lines**: 91–95 (`SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]`)
- **Code**: `"S3: weave platform scale, operating model, and commercialization as connective prose"`
- **Impact**: Explicitly tells the model to weave "commercialization" into S3 prose. Even when S1 is
  correct, the S3 instruction reinforces the pattern for subsequent sentences.

### RC-G: "commercialization" in `SVP_JD_EMPHASIS_THEMES`
- **File**: `apps_rg/runtime/sections/executive_summary_synthesis_contract.py`
- **Lines**: 61–67
- **Code**: `"AI and data platform commercialization"` in emphasis themes tuple
- **Impact**: Tilts the model toward "commercialization" vocabulary throughout the summary as a
  thematic anchor, compounding RC-E and RC-F.

## Scope Containment

**In scope:**
- `executive_summary_composition.py` — `target_picture` string only (line 515-519)
- `executive_summary_synthesis_contract.py` — `SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]` (line 91)
  and `SVP_JD_EMPHASIS_THEMES` (line 66)
- Unit tests for all three changes

**Out of scope:**
- Other resume sections
- Other strategy executive flavors
- `skill_agentic_platform_commercialization` graph skill (skill references are fine)

## Replacement Logic

| Location | Before | After | Rationale |
|---|---|---|---|
| `target_picture` | `regulatory lineage, and commercialization into one enterprise IT direction` | `regulatory lineage, and digital innovation programs into one enterprise IT direction` | Aligns with Brown & Brown JD emphasis on innovation + matches E0 example W1 fix |
| S3 guidance | `weave platform scale, operating model, and commercialization as connective prose` | `weave platform scale, operating model, and platform revenue outcomes as connective prose` | Preserves revenue-outcome substance; removes word that echoes as S1 identity label |
| JD emphasis themes | `"AI and data platform commercialization"` | `"AI and data platform revenue generation"` | Revenue generation is the actual business outcome; avoids "commercialization" vocabulary tilt |

## Waves

### W1: Fix `target_picture` in `executive_summary_composition.py`

**File**: `apps_rg/runtime/sections/executive_summary_composition.py` lines 515–519

Replace the hard-coded `target_picture` string to use "digital innovation programs" instead of
"commercialization".

### W2: Fix S3 guidance in `SENTENCE_ARC_SVP_STRATEGY`

**File**: `apps_rg/runtime/sections/executive_summary_synthesis_contract.py` lines 91

Replace "commercialization" → "platform revenue outcomes" in the S3 arc guidance.

### W3: Fix `SVP_JD_EMPHASIS_THEMES`

**File**: `apps_rg/runtime/sections/executive_summary_synthesis_contract.py` lines 66

Replace "AI and data platform commercialization" → "AI and data platform revenue generation".

### W4: Unit tests

**File**: `tests/unit/apps_rg/test_exec_summary_rc_composition_hardcode_b3d7e1.py`

Tests:
- `test_target_picture_no_commercialization` — target_picture built by `build_executive_summary_composition_plan` for strategy executive must not contain "commercialization"
- `test_target_picture_has_digital_innovation` — target_picture must contain "digital innovation"
- `test_s3_guidance_no_commercialization` — `SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]` must not contain "commercialization"
- `test_s3_guidance_has_revenue_outcomes` — S3 guidance must contain "revenue"
- `test_jd_emphasis_no_commercialization` — `SVP_JD_EMPHASIS_THEMES` must not contain "commercialization"
- `test_jd_emphasis_has_revenue_generation` — themes must contain "revenue generation"
- `test_composition_plan_artifact_no_commercialization` — integration: `build_executive_summary_composition_plan` JSON output must have no "commercialization" in target_picture or sentence_arc guidance fields

### W5: Brown SVP proof re-run

**Command**: `python -m apps_rg --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md`

**Success criterion**: Exit code 0 (X3_ALLOW)

## NOTION_PAGE_ID

36d27693-f55c-8177-acd3-eb29f6fd1a91

## Status

PARTIAL

W1-W4 complete (14/14 unit tests pass). W5 proof run: "commercialization" is verified gone from
all generated artifacts (target_picture, resume_display_text). X3 failure persists for DIFFERENT
quality reasons (achievement stack, S6 synthesis, S4 connector) covered by successor plan
`exec-summary-rc-narrative-quality-c4e9a1` (Notion: 36d27693-f55c-81cb-b868-f2f3ddc3a5aa).
