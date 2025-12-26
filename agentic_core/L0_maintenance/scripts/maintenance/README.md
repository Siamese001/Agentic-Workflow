# Maintenance Scripts - SSOT Synchronization

This directory contains maintenance scripts for keeping the codebase synchronized with the Single Source of Truth (SSOT) defined in `structure_blueprint.py`.

## Scripts

### `generate_hooks.py` - Pre-commit Hook Generator

Dynamically generates `.pre-commit-config.yaml` patterns from the SSOT to eliminate hardcoded folder lists and prevent configuration drift.

#### Usage

**List current sovereign roots:**
```bash
python scripts/maintenance/generate_hooks.py --list
```

**Preview changes (dry-run):**
```bash
python scripts/maintenance/generate_hooks.py --dry-run
```

**Apply changes:**
```bash
python scripts/maintenance/generate_hooks.py
```

#### What It Does

1. Reads `SOVEREIGN_REGISTRY` from `structure_blueprint.py`
2. Generates dynamic regex patterns for:
   - `exclude:` patterns (sovereign roots + data/archives)
   - `files:` patterns (sovereign roots only)
3. Updates `.pre-commit-config.yaml` with SSOT-derived patterns

#### When to Run

- **After adding a new sovereign root** to `structure_blueprint.py`
- **After removing a sovereign root** from the registry
- **During SSOT audits** to ensure pre-commit config is synchronized
- **Before committing structural changes** to validate configuration

#### Example Output

```
[*] Syncing Pre-commit Config with SSOT...
   [SSOT] Sovereign Roots: agentic_core, apps_rg, apps_lic, apps_shared, tests
   [PATTERN] Exclude: ^(agentic_core|apps_rg|apps_lic|apps_shared|tests|data|archives)/
   [PATTERN] Files: ^(agentic_core|apps_rg|apps_lic|apps_shared|tests)/.*\.py$
   [OK] Found config at: .pre-commit-config.yaml
   [✓] Updated 3 pattern(s) in .pre-commit-config.yaml
   [SUCCESS] Pre-commit config synchronized with SSOT
```

## SSOT Architecture

The maintenance scripts follow the SSOT hierarchy:

```
structure_blueprint.py (SSOT)
    ↓
void_compliance.py (Derives enforcement rules)
    ↓
generate_hooks.py (Generates configuration)
    ↓
.pre-commit-config.yaml (Generated patterns)
```

### Key Principles

1. **Never hardcode structural facts** - Always derive from `structure_blueprint.py`
2. **Generate, don't duplicate** - Configuration files should be generated from SSOT
3. **Validate synchronization** - Run generators after any structural changes
4. **Document legacy** - Mark static files with `[SSOT] LEGACY` notices

## Adding New Maintenance Scripts

When creating new maintenance scripts:

1. Import from `structure_blueprint.py` for structural facts
2. Import from `void_compliance.py` for derived enforcement rules
3. Add `--dry-run` and `--list` options for safety
4. Document in this README
5. Add to the validation pipeline

## Related Files

- `agentic_core/config/P1_core/structure_blueprint.py` - Master SSOT
- `agentic_core/runtime/shared/void_compliance.py` - Enforcement layer
- `agentic_core/L0_maintenance/scripts/.pre-commit-config.yaml` - Generated config
- `sovereign_manifest.json` - Legacy documentation (marked for deprecation)
