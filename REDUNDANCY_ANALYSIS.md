# Repository-Wide Redundancy & Utility Extraction Analysis

**Date:** January 18, 2026  
**Scope:** `agentic_core/` and `scripts/` directories  
**Objective:** Identify repeated code patterns for centralized utility extraction

---

## Executive Summary

Analysis identified **5 major redundancy clusters** affecting **200+ files** with an estimated **2,000+ lines of duplicate code**. Extracting these patterns into centralized utilities will:
- Reduce code duplication by ~40%
- Improve maintainability and consistency
- Eliminate subtle bugs from copy-paste variations
- Standardize critical operations (result handling, file I/O, AST parsing)

---

## Cluster Analysis

### 1. Result Normalization (CRITICAL)

**Pattern Description:** Manual extraction and normalization of `fixed`, `violations`, `violations_found` from agent return dictionaries.

**Code Example:**
```python
# Pattern found in ConsolidatedOrchestratorAgent.py (lines 108-114)
if isinstance(result, dict):
    fixes = result.get('fixed') or result.get('violations_fixed') or result.get('renamed') or 0
    violations = result.get('violations') or result.get('violations_found') or result.get('errors') or 0
else:
    fixes = 0
    violations = 0

# Similar pattern in SSOTOrchestratorAgent.py (lines 254-256)
violations_found = result.get('violations_found', 0)
violations_fixed = result.get('violations_fixed', 0)
status = result.get('status', 'UNKNOWN')
```

**Occurrences:** 43 files with 157 matches
- `HierarchyAgent.py` (35 matches)
- `SSOTOrchestratorAgent.py` (13 matches)
- `DynamicSealAgent.py` (8 matches)
- `mission_controller.py` (7 matches)
- `mission_controller_engine.py` (7 matches)
- Plus 38 additional files

**Proposed Utility:** `agentic_core/utils/result_utils.py`

**Functions:**
```python
@dataclass
class AgentResult:
    """Standardized agent execution result."""
    agent_name: str
    status: str  # 'SUCCESS', 'WARNING', 'ERROR', 'SKIPPED'
    violations_found: int = 0
    violations_fixed: int = 0
    execution_time_ms: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

def normalize_agent_result(
    agent_name: str,
    result: Any,
    execution_time_ms: int = 0
) -> AgentResult:
    """
    Normalize any agent return value to AgentResult.
    
    Handles:
    - None results
    - Dict with various key names (violations/violations_found, fixed/violations_fixed)
    - Non-dict results
    - Missing keys
    """
    pass

def extract_violations(result: Any) -> int:
    """Extract violations count from any result format."""
    pass

def extract_fixes(result: Any) -> int:
    """Extract fixes count from any result format."""
    pass
```

**LOC Savings:** ~600 lines (15 lines × 40 files)

---

### 2. SSOT Discovery Access

**Pattern Description:** Manual loading of `agent_discovery_full.json` with error handling.

**Code Example:**
```python
# Pattern found in discovery_roster_builder.py, ComplianceOrchestratorAgent.py, etc.
discovery_path = project_root / "agent_discovery_full.json"
if discovery_path.exists():
    try:
        with open(discovery_path, 'r', encoding='utf-8') as f:
            discovery_data = json.load(f)
        # Process data...
    except Exception as e:
        Logger.warning(f"Failed to load discovery JSON: {e}")
```

**Occurrences:** 139 files with 240 matches
- Dashboard test files (29 matches in `test_dashboard_end_to_end.py`)
- `dashboard_qa_deep_audit.py` (5 matches)
- `validate_dashboard_data_sourcing.py` (5 matches)
- Plus 136 additional files

**Current Solution:** `agentic_core/utils/ssot_discovery.py` ✅ **ALREADY CREATED**

The utility was created in this session with functions:
- `load_agent_discovery()` - Load with caching
- `get_agent_paths()` - Get file paths
- `get_agents_by_layer()` - Filter by layer
- `get_agent_names()` - Get agent names
- `get_healers()` - Get healer agents

**Action Required:** Refactor remaining 139 files to use the utility instead of manual JSON loading.

**LOC Savings:** ~1,000 lines (8 lines × 125 files, excluding already refactored)

---

### 3. Safe File Operations

**Pattern Description:** Repeated `open()` with encoding and error handling.

**Code Example:**
```python
# Pattern found in 447 files with 975 matches
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except (FileNotFoundError, UnicodeDecodeError) as e:
    Logger.error(f"Failed to read {file_path}: {e}")
    return None

# Or using Path.read_text
try:
    content = file_path.read_text(encoding='utf-8')
except Exception as e:
    Logger.error(f"Failed to read {file_path}: {e}")
```

**Occurrences:** 447 files with 975 matches
- `test_dashboard_end_to_end.py` (46 matches)
- `test_dashboard.py` (15 matches)
- `NamingAgent.py` (14 matches)
- Plus 444 additional files

**Proposed Utility:** `agentic_core/utils/file_utils.py`

**Functions:**
```python
def safe_read_file(
    file_path: Path,
    encoding: str = 'utf-8',
    errors: str = 'replace'
) -> Optional[str]:
    """Safely read file with error handling."""
    pass

def safe_write_file(
    file_path: Path,
    content: str,
    encoding: str = 'utf-8',
    atomic: bool = True
) -> bool:
    """Safely write file with atomic write support."""
    pass

def safe_read_json(
    file_path: Path,
    default: Any = None
) -> Any:
    """Safely read and parse JSON file."""
    pass

def safe_write_json(
    file_path: Path,
    data: Any,
    indent: int = 2,
    atomic: bool = True
) -> bool:
    """Safely write JSON file with atomic write."""
    pass
```

**LOC Savings:** ~400 lines (assuming 2 lines saved per usage in 200 files)

---

### 4. Path-to-Module Conversion

**Pattern Description:** Converting file paths to Python module paths.

**Code Example:**
```python
# Pattern in discovery_roster_builder.py (lines 171-177)
def path_to_module(file_path: str) -> str:
    """Convert file path to Python module path."""
    module_path = file_path.replace('.py', '')
    module_path = module_path.replace('\\', '.').replace('/', '.')
    return module_path

# Pattern in canon_validator_agentic_v2_thin.py (line 393)
module_path = path.replace("/", ".").replace(".py", "")

# Pattern in multiple files with os.sep
module_path = str(rel_path).replace(os.sep, '.').replace('.py', '')
```

**Occurrences:** 45 files with 83 matches
- `full_agent_discovery.py` (8 matches)
- `governance.py` (6 matches)
- `ExecutionCanonBaseAgent.py` (4 matches)
- Plus 42 additional files

**Proposed Utility:** `agentic_core/utils/import_utils.py`

**Functions:**
```python
def path_to_module(
    file_path: Union[str, Path],
    project_root: Optional[Path] = None
) -> str:
    """
    Convert file path to Python module path.
    
    Examples:
        'agentic_core/L5_safety/validators/LocationAgent.py'
        -> 'agentic_core.L5_safety.validators.LocationAgent'
    """
    pass

def module_to_path(
    module_path: str,
    project_root: Optional[Path] = None
) -> Path:
    """Convert Python module path to file path."""
    pass

def safe_import_module(
    module_path: str,
    class_name: Optional[str] = None
) -> Any:
    """Safely import module and optionally get class."""
    pass
```

**LOC Savings:** ~150 lines (3 lines × 50 files)

---

### 5. AST Parsing with Error Handling

**Pattern Description:** Repeated `ast.parse()` calls with encoding and syntax error handling.

**Code Example:**
```python
# Pattern found in 135 files with 197 matches
try:
    source = py_file.read_text(encoding='utf-8', errors='replace')
    tree = ast.parse(source)
except SyntaxError as e:
    Logger.warning(f"Syntax error in {py_file}: {e}")
    return None
except Exception as e:
    Logger.error(f"Failed to parse {py_file}: {e}")
    return None
```

**Occurrences:** 135 files with 197 matches
- `StructuralHealerAgent.py` (9 matches)
- `BudgetManagerAgent.py` (5 matches)
- `find_duplicate_agents.py` (3 matches)
- Plus 132 additional files

**Proposed Utility:** `agentic_core/utils/ast_utils.py`

**Functions:**
```python
def safe_parse_file(
    file_path: Path,
    encoding: str = 'utf-8'
) -> Optional[ast.AST]:
    """Safely parse Python file to AST."""
    pass

def extract_classes(
    tree: ast.AST,
    include_bases: bool = True
) -> List[Dict[str, Any]]:
    """Extract class definitions from AST."""
    pass

def extract_functions(
    tree: ast.AST,
    include_methods: bool = True
) -> List[Dict[str, Any]]:
    """Extract function definitions from AST."""
    pass

def extract_imports(
    tree: ast.AST
) -> Dict[str, List[str]]:
    """Extract import statements from AST."""
    pass

def get_class_methods(
    class_node: ast.ClassDef
) -> List[str]:
    """Get method names from class node."""
    pass
```

**LOC Savings:** ~300 lines (5 lines × 60 files)

---

## Summary Table

| Pattern Description | Occurrences (Files) | Proposed Utility | LOC Savings | Priority |
|---------------------|---------------------|------------------|-------------|----------|
| **Result Normalization** | 43 files, 157 matches | `result_utils.py` | ~600 lines | **CRITICAL** |
| **SSOT Discovery Access** | 139 files, 240 matches | `ssot_discovery.py` ✅ | ~1,000 lines | **HIGH** |
| **Safe File Operations** | 447 files, 975 matches | `file_utils.py` | ~400 lines | **HIGH** |
| **Path-to-Module Conversion** | 45 files, 83 matches | `import_utils.py` | ~150 lines | **MEDIUM** |
| **AST Parsing** | 135 files, 197 matches | `ast_utils.py` | ~300 lines | **MEDIUM** |
| **TOTAL** | **809 files** | **5 utilities** | **~2,450 lines** | - |

---

## Implementation Recommendations

### Phase 1: Critical (Week 1)
1. ✅ **COMPLETED:** `ssot_discovery.py` - Already created and tested
2. **Create `result_utils.py`** - Highest impact, affects orchestration core
3. **Refactor orchestrators** - Update `ConsolidatedOrchestratorAgent`, `SSOTOrchestratorAgent`, `mission_controller`

### Phase 2: High Priority (Week 2)
4. **Create `file_utils.py`** - Standardize file I/O across 447 files
5. **Refactor discovery access** - Update remaining 139 files to use `ssot_discovery.py`

### Phase 3: Medium Priority (Week 3)
6. **Create `import_utils.py`** - Standardize path/module conversion
7. **Create `ast_utils.py`** - Centralize AST parsing logic

### Phase 4: Validation (Week 4)
8. **Run comprehensive test suite** - Ensure all refactoring maintains functionality
9. **Update documentation** - Document new utilities and migration guide
10. **Deprecation warnings** - Add warnings to old patterns

---

## Impact Analysis

### Benefits
- **Code Reduction:** ~2,450 lines of duplicate code eliminated
- **Consistency:** All agents use same result format, file I/O, AST parsing
- **Bug Prevention:** Centralized error handling prevents copy-paste bugs
- **Maintainability:** Single location to fix bugs or add features
- **Testing:** Utilities can be thoroughly unit tested once

### Risks
- **Migration Effort:** 809 files need updates
- **Breaking Changes:** Existing code depends on current patterns
- **Testing Burden:** Must verify all 809 files still work correctly

### Mitigation
- **Incremental Migration:** Update one cluster at a time
- **Backward Compatibility:** Keep old patterns working with deprecation warnings
- **Automated Testing:** Create test suite to verify each migration
- **Documentation:** Provide clear migration guide for each utility

---

## Next Steps

1. **Review this analysis** with team
2. **Prioritize utilities** based on impact and effort
3. **Create implementation plan** with milestones
4. **Start with `result_utils.py`** (highest impact)
5. **Establish testing protocol** for migrations
6. **Document migration patterns** for team

---

## Appendix: Key Files Requiring Refactoring

### Result Normalization (Top 10)
1. `HierarchyAgent.py` (35 matches)
2. `SSOTOrchestratorAgent.py` (13 matches)
3. `DynamicSealAgent.py` (8 matches)
4. `mission_controller.py` (7 matches)
5. `mission_controller_engine.py` (7 matches)
6. `ConstitutionalReviewerAgent.py` (5 matches)
7. `test_orchestration.py` (4 matches)
8. `GravityLeakRepairAgent.py` (4 matches)
9. `ConstitutionalGovernanceGuardrail.py` (4 matches)
10. `IntegrityValidationGuardrail.py` (4 matches)

### SSOT Discovery Access (Top 10)
1. `test_dashboard_end_to_end.py` (29 matches)
2. `dashboard_qa_deep_audit.py` (5 matches)
3. `validate_dashboard_data_sourcing.py` (5 matches)
4. `set_schema_strictness_100.py` (4 matches)
5. `set_typed_documented_100.py` (4 matches)
6. `mandatory_dashboard_tests.py` (4 matches)
7. `audit_dashboard_ssot_flow.py` (3 matches)
8. `generate_modular_dashboard_data.py` (3 matches)
9. `populate_pinecone_embeddings.py` (3 matches)
10. `pre_deploy_check.py` (3 matches)

### Safe File Operations (Top 10)
1. `test_dashboard_end_to_end.py` (46 matches)
2. `test_dashboard.py` (15 matches)
3. `NamingAgent.py` (14 matches)
4. `sprint4_phase2_comprehensive_refactor.py` (11 matches)
5. `extract_final_two_agents.py` (10 matches)
6. `audit_dashboard_naming.py` (9 matches)
7. `dashboard_qa.py` (9 matches)
8. `final_283_extraction.py` (9 matches)
9. `mandatory_dashboard_tests.py` (9 matches)
10. `test_ssot_enforcement.py` (8 matches)

---

**End of Analysis**
