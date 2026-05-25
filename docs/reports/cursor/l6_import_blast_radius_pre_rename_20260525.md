# L6 Import Blast-Radius — Pre-Rename (W5.0)

**Date:** 2026-05-25  
**Plan:** [l6-repo-reorganization-mental-model-c4e8f2.md](../../.cursor/plans/l6-repo-reorganization-mental-model-c4e8f2.md)  
**Architecture path:** `PATH_RENAME_CANONICAL`  
**Baseline:** [l6_import_blast_radius_baseline_20260525.md](l6_import_blast_radius_baseline_20260525.md)

---

## Summary (immediate pre-W5.1)

| Metric | W0 baseline | Pre-rename (W5.0) |
|--------|------------:|------------------:|
| Python files with `system_learning` imports | 329 | **330** |
| Import line matches (approx) | 732 | **736** |
| `system_learning/chapters/` exists | false | **false** |
| W1 L6-TAG fail-closed | — | **pass** (292/292) |
| W1 L6-OBS fail-closed | — | **pass** (0 findings) |

---

## Rollback (P6)

```bash
git revert <w5-commit-range>
git checkout <pre-rename-tag> -- system_learning agentic_core/L6_system_learning
python tools/generate/generate_full_adg.py
```

Pre-rename tag: record SHA at W5.1 start in [l6_w5_post_rename_cert_20260525.json](l6_w5_post_rename_cert_20260525.json) when complete.

---

## W5.1 command plan

1. `git rm agentic_core/L6_system_learning/__init__.py` (remove pre-move alias)
2. `git mv system_learning agentic_core/L6_system_learning`
3. `python tools/_oneoff/w5_import_migrate.py` (W5.2 codemod)
