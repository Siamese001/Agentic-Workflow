---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\fca-dry-run-report-b2e2e7.md'
original_relative_path: 'fca-dry-run-report-b2e2e7.md'
source_sha256: d24811292f6c6558e9852188d963da5e1b0260b022a1a25045710f8da5330bc3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# FCA Dry-Run Report on agentic_core/

Run `FileClassificationAgent` on `agentic_core/` in dry-run mode, capturing every proposed move, rename, folder-purity eviction, layer-alignment violation, and classification finding into a structured report at `docs/reports/plans/fca_dry_run_agentic_core.md`.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Approach

The FCA has two complementary scan passes. Both will be run:

1. **Main Audit** (`_orchestrate_audit`) — scans all `.py` files and proposes:
   - **Renames** (naming convention violations)
   - **Territory moves** (file in wrong LCD subfolder)
   - **Folder-purity evictions** (e.g. non-agent in reasoning/)
   - **Compound-suffix splits** (dual classification tags)
   - **Forbidden patterns** (stuttering, leading `_`, triple `_`)
   - **Layer purity** (cognitive contamination, passive agent naming)
   - **Fake config detection** (active logic in `_config.py`)
   - **Ephemeral script detection** (numbered phase/wave scripts)
   - **Cross-layer naming** (file name contains wrong layer indicator)
   - **Cross-domain** (app-domain code in agentic_core/)

2. **Layer Alignment** (`validate_layer_alignment`) — per-file checks for:
   - `AGENT_OUTSIDE_REASONING`
   - `AGENT_LAYER_MISPLACEMENT` (infra imports suggest wrong layer)
   - `NON_AGENT_IN_REASONING`
   - `CONFIG_SUFFIX_MISSING`
   - `AGENT_NAMING_SNAKE_CASE`
   - `OBSERVABILITY_OUTSIDE_L6`
   - `SCRIPTS_PURITY_VIOLATION`
   - `NESTED_LCD_SUBTREE`

## Steps

1. **Write runner script** (`_fca_dry_run.py`) that:
   - Instantiates FCA with `dry_run=True, validate_only=True, project_root=PROJECT_ROOT`
   - Runs `_orchestrate_audit(agentic_core/)` capturing logger output
   - Iterates all `.py` files calling `validate_layer_alignment()` + `classify_file()`
   - Collects all findings into categorized lists
   - Writes JSON + markdown report

2. **Execute the script** (read-only, no file mutations)

3. **Write report** to `docs/reports/plans/fca_dry_run_agentic_core.md` with:
   - Summary table (violation type → count)
   - Per-violation-type sections with file paths and proposed actions
   - Proposed moves as `old_path → new_path` diffs

## Output Location

`docs/reports/plans/fca_dry_run_agentic_core.md` (SSOT location per constitutional lock §0)

## Risk

Zero — `dry_run=True` + `validate_only=True` means no files are modified.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

