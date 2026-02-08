# EXPORT SURFACE MAP: structure_blueprint_config.py

## Canonical Location
`agentic_core/L5_safety/config/structure_blueprint_config.py`

## Import Sites
**294 matches across 194 files** (high-traffic module)

## Critical Exports (MUST PRESERVE)

### Core Data Structures
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `SOVEREIGN_TERRITORIES` | `Final[Mapping]` | 80 | FCA, LocationValidatorAgent, HierarchyAgent, 50+ tests | YES |
| `CORE_SUBFOLDER_MAP` | `Final[Mapping]` | 1496 | FCA, validators, healing agents | YES (derived) |
| `SUBFOLDER_METADATA` | `Final[Mapping]` | 1500 | FCA, validators | YES (derived) |
| `LAYER_ROOTS` | `Final[frozenset]` | 5711 | FCA, validators, tests | YES |
| `REQUIRED_LCD_SUBFOLDERS` | `Final[frozenset]` | 5716 | FCA, validators, tests | YES |
| `VARIABLE_DEPTH_SUBFOLDERS` | `frozenset` | 1310 | FCA, HierarchyAgent | YES |

### Validation Functions
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `validate_no_nested_lcd` | `function` | 5740 | FCA, tests | YES |
| `is_layer_root` | `function` | 5728 | FCA | YES |
| `is_allowed_subfolder` | `function` | 5733 | FCA | YES |
| `verify_derived_registries` | `function` | 1511 | tests | YES |

### Allowlists (L5/L6 Subprocess)
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `L5_SUBPROCESS_ALLOWLIST` | `Final[frozenset]` | 5779 | FCA, tests | YES |
| `L6_HYBRID_ALLOWLIST` | `Final[frozenset]` | 5791 | FCA, tests | YES |
| `SCRIPTS_FORBIDDEN_PATTERNS` | `Final[Sequence]` | 5800 | FCA | YES |

### Path Constants
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `AGENTIC_CORE_DIR` | `Final[str]` | 1364 | Many | YES |
| `APPS_RG_DIR` | `Final[str]` | 1365 | Many | YES |
| `APPS_LIC_DIR` | `Final[str]` | 1366 | Many | YES |
| `APPS_SHARED_DIR` | `Final[str]` | 1367 | Many | YES |
| `get_validated_project_root` | `function` | 2031 | Many | YES |

### Classification Patterns (COLD - lazy load candidates)
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `APP_SPECIFIC_PATTERNS` | `Final[list[Pattern]]` | 1733 | FCA | NO (lazy) |
| `FORBIDDEN_BACKUP_PATTERNS` | `Final[list[Pattern]]` | 1768 | FCA | NO (lazy) |
| `CLASSIFICATION_SUFFIX_PATTERNS` | `Final[Mapping]` | 2289 | FCA | NO (lazy) |
| `COMPOUND_SUFFIX_CONFLICTS` | `Final[Sequence]` | 2308 | FCA | NO (lazy) |
| `FOLDER_PURITY_RULES` | `Final[Mapping]` | 2386 | FCA | NO (lazy) |

### Semantic Registries (COLD - heavy data)
| Export Name | Type | Line | Callers | Must Stay In-Place |
|-------------|------|------|---------|-------------------|
| `L4_SUBFOLDER_MAP` | `Final[Mapping]` | 1547 | FCA | NO (lazy) |
| `NAMING_CONVENTIONS` | `Final[Mapping]` | 2480 | FCA | NO (lazy) |
| `LAYER_KEYWORD_AFFINITY` | `Final[Mapping]` | 2459 | FCA | NO (lazy) |
| `APP_RG_AST_TERMS` | `Final[frozenset]` | 1798 | FCA | NO (lazy) |
| `APP_LIC_AST_TERMS` | `Final[frozenset]` | 1818 | FCA | NO (lazy) |

## Refactor Strategy

### HOT MODULE (ssot.py) - ~200 lines
- `LAYER_ROOTS`, `REQUIRED_LCD_SUBFOLDERS`, `LEAF_DOMAINS_NO_LCD`
- `validate_no_nested_lcd`, `is_layer_root`, `is_allowed_subfolder`
- `L5_SUBPROCESS_ALLOWLIST`, `L6_HYBRID_ALLOWLIST` (path-based)
- `SCRIPTS_FORBIDDEN_PATTERNS`
- Path constants (`AGENTIC_CORE_DIR`, etc.)
- `get_validated_project_root`, `validate_path_within_project`, `safe_path_join`
- Lazy loaders for cold modules

### COLD MODULE: territories.py - ~1500 lines
- `SOVEREIGN_TERRITORIES` (built from template + overrides)
- `STANDARD_LAYER_STRUCTURE`
- `build_sovereign_territories()` function
- Type definitions (`SubfolderDefinition`, `TerritoryDefinition`)

### COLD MODULE: semantics.py - ~1000 lines
- `NAMING_CONVENTIONS`
- `LAYER_KEYWORD_AFFINITY`
- `APP_RG_AST_TERMS`, `APP_LIC_AST_TERMS`, `APP_RG_STRING_TERMS`, etc.
- `POLYGLOT_DOMAIN_SIGNALS`
- `CORE_TERRITORY_KEYWORDS`
- `SERVICE_CLASS_INDICATORS`

### COLD MODULE: classification.py - ~800 lines
- `CLASSIFICATION_SUFFIX_PATTERNS` (strings, not compiled)
- `COMPOUND_SUFFIX_CONFLICTS`
- `FOLDER_PURITY_RULES`
- `SUFFIX_TO_FOLDER`, `FILETYPE_TO_FOLDER`
- `get_classification_patterns_compiled()` (lazy)
- `get_folder_purity_patterns_compiled()` (lazy)

### COLD MODULE: artifacts.py - ~500 lines
- `APP_SPECIFIC_PATTERNS` (strings, not compiled)
- `FORBIDDEN_BACKUP_PATTERNS` (strings, not compiled)
- `FORBIDDEN_FILENAME_PATTERNS`
- `FORBIDDEN_EPHEMERAL_PATTERNS`
- `get_app_specific_patterns_compiled()` (lazy)

### COLD MODULE: derived.py - ~300 lines
- `_derive_core_subfolder_map()`
- `_derive_subfolder_metadata()`
- `_derive_apps_subfolder_map()`
- `compile_blueprint()` function
- `CompiledBlueprint` dataclass

### SHIM: structure_blueprint_config.py - ~50 lines
- Re-exports all public names from new modules
- Preserves backward compatibility
