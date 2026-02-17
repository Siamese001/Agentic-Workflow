# Phase 7: Structure Blueprint Import Canonicalization

## Summary

**Status:** ✅ COMPLETE for L0-eligible constants
**Date:** 2026-02-17
**Commits:** 8 batches (Batches 4-11)

## What Was Done

### L0 Constants Module Created
`agentic_core/L0_routing/config/structure_blueprint_data.py` now contains 16 literal-only constants:

| Constant | Type | Description |
|----------|------|-------------|
| `SCRIPTS_FORBIDDEN_PATTERNS` | `Sequence[str]` | Regex patterns for forbidden script filenames |
| `L5_SUBPROCESS_ALLOWLIST` | `Sequence[str]` | Paths allowed to use subprocess in L5 |
| `L6_HYBRID_ALLOWLIST` | `Sequence[str]` | Paths allowed hybrid patterns in L6 |
| `FOLDER_PURITY_RULES` | `Mapping[str, Sequence[str]]` | Regex patterns per folder type |
| `APP_DOMAIN_PREFIXES` | `Sequence[str]` | App-specific file prefixes |
| `LAYER_KEYWORD_AFFINITY` | `Mapping[str, Sequence[str]]` | Keywords per layer |
| `SUFFIX_TO_FOLDER` | `Mapping[str, str]` | Suffix to folder mapping |
| `INTERFACE_FILENAME_PATTERN` | `str` | Regex for interface files |
| `GLOBAL_INTERFACES_FOLDER` | `str` | Path to interfaces folder |
| `FORBIDDEN_EPHEMERAL_PATTERNS` | `Sequence[str]` | Patterns for ephemeral scripts |
| `EPHEMERAL_PATTERN_EXEMPTIONS` | `Sequence[str]` | Exemptions for ephemeral check |
| `CANONICAL_LOCATION_PRIORITY` | `Sequence[str]` | Priority order for canonical locations |
| `DUPLICATE_DETECTION_EXEMPT` | `Sequence[str]` | Files exempt from duplicate detection |
| `LAYER_PREFIX_PATTERN` | `str` | Regex for layer prefixes |
| `AST_PLACEMENT_SIGNALS` | `Sequence[str]` | AST class name indicators |
| `SOVEREIGN_TERRITORIES` | `Mapping[str, Mapping[str, str]]` | Root territory definitions |

### Files Fixed
- ~60 files updated to import from `agentic_core.L0_routing.config` instead of `agentic_core.L5_safety.config.structure_blueprint_config`
- All test files, source files, and scripts that imported L0-eligible constants

### L0-Eligible Violations: 0 Remaining
All imports of the 16 L0-eligible constants have been canonicalized.

## Remaining Work (Non-Fixable)

**302 remaining imports** cannot be moved to L0 because they import:

### Functions (require L5 governance logic)
- `validate_no_nested_lcd()` - Validation function
- `get_validated_project_root()` - Path validation function
- `is_allowed_subfolder()` - Validation function
- `get_correct_app_path()` - Routing function
- `is_app_specific_file()` - Classification function

### Complex Constants (computed or reference functions)
- `CORE_SUBFOLDER_MAP` - Complex nested mapping with validation rules
- `FILETYPE_TO_FOLDER` - Routing table with computed values
- `STANDARD_LAYER_STRUCTURE` - Structure definition
- `SUBFOLDER_METADATA` - Metadata with descriptions
- `REQUIRED_LCD_SUBFOLDERS` - Structure requirements
- `LEAF_DOMAINS_NO_LCD` - Domain classification
- `ROOT_PROTECTED_FILES` - Protection rules
- `SERVICE_CLASS_INDICATORS` - Classification signals
- `KNOWN_ARCHITECTURAL_SUFFIXES` - Suffix patterns
- And ~20 more complex constants

These must remain in L5 as they involve governance logic, validation, or computed values.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| L0-eligible imports from L5 | ~60 | 0 |
| Files fixed | 0 | ~60 |
| Constants moved to L0 | 0 | 16 |
| Non-fixable L5 imports | 302 | 302 (expected) |

## Next Steps

1. **Phase 8:** Consider creating `structure_blueprint_functions.py` in L5 to separate functions from config
2. **Phase 9:** Evaluate moving more constants to L0 if they become literal-only
3. **Ongoing:** Monitor for new violations via pre-commit hooks
