# W2 Receipt — governance-dedup-closeout-e8a4c2

**Wave:** W2 — CI native config and index drift  
**Date:** 2026-05-26  
**Status:** PASS

## W2.1 — Legacy reference allowlist

| Artifact | Purpose |
|----------|---------|
| [legacy_reference_allowlist.yaml](../../.cursor/legacy_reference_allowlist.yaml) | Sanctioned `.windsurf` / `Windsurf` / `mcp_config.json` mentions in active Cursor paths |
| [migration_allowlist.json](../../.cursor/migration_allowlist.json) | Extended `_legacy_cursor/**` + yaml path self-allow |
| [check_cursor_native_config.py](../../.cursor/scripts/check_cursor_native_config.py) | Loads yaml globs via minimal parser (no PyYAML) |

**Before:** 31 `active_legacy_reference` failures  
**After:** `check_cursor_native_config.py --strict` → **PASS**

## W2.2 — RULES_INDEX drift gate

| Change | Detail |
|--------|--------|
| `generate_rules_index.py --check` | Strips `**Generated**:` header line and embedded `"generated_at"` JSON field before compare |
| `RULES_INDEX.md` | Regenerated via `--write` (governance SSOT map from W1) |

**Commands:**
```bash
python .cursor/scripts/check_cursor_native_config.py --strict  # exit 0
python .cursor/scripts/generate_rules_index.py --check         # exit 0
```

## Marker

```
WAVE_COMPLETE: plan=governance-dedup-closeout-e8a4c2 wave=2 note="legacy allowlist yaml, native config PASS, rules index check PASS"
```

## Next wave

**W3** — Plan sprawl archive (target ≤20 active top-level plans).
