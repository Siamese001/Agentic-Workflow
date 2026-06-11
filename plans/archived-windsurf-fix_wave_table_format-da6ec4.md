---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\fix_wave_table_format-da6ec4.md'
original_relative_path: 'fix_wave_table_format-da6ec4.md'
source_sha256: 04d5a627a11d082c06078e51b4a7f42f8ce7ceebc349e4dd5e4d4b6b27f62143
recovered_status: LOST_RECOVERED
last_commit: '20f413ffbf5'
last_commit_date: '2026-04-01 14:39:03 -0400'
created_date: '2026-03-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Fix Wave Table Format

## Wave Structure

| Waves | Metric | Scope | Checkpoint | [Tokens |]
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---

## Issue
The wave table generation tool created tables with format:
```
| Waves | Metric | Scope | Checkpoint | Tokens |
```

But the validation expects:
```
| Waves | Metric | Scope | Checkpoint | [Tokens |]
```

## Solution
Update the `generate_wave_table()` function in `tools/add_wave_tables_to_legacy_plans.py` to match the expected pattern.

## New Wave Table Format
```python
def generate_wave_table() -> str:
    """Generate a standard wave table template."""
    return """## Wave Structure

| Waves | Metric | Scope | Checkpoint | [Tokens |]
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---

"""
```

## Commands to Execute
```bash
# Update the tool
# (Edit tools/add_wave_tables_to_legacy_plans.py)

# Re-run wave table generation
python tools/add_wave_tables_to_legacy_plans.py --type execution --execute
```

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

