# Root Cause Analysis: LCD+ Migration Failures
## Date: 2026-02-07
## Scope: agentic_core L0-L6 layers

---

## Executive Summary

The LCD+ migration underwent **hundreds of iterations** yet still failed to achieve golden state. This RCA identifies **5 systemic root causes** and proposes **architectural fixes** to prevent recurrence.

**Total Errors Uncovered Post-Implementation:**
- 153 files in wrong LCD folders (agents in enforcement/, types in config/, etc.)
- 67 files with compound suffixes (*_types_config.py, *_validator_util.py)
- 122 files with nested subdirs that should have been dissolved
- ~200 stale import references requiring manual fix

---

## Error Categories Discovered

### Category 1: Agents Misplaced in Non-Reasoning Folders

**Files Affected:** 41 files across L0-L6

| Layer | Wrong Folder | File Count | Example |
|-------|--------------|------------|---------|
| L5_safety | enforcement/ | 16 | `AdversarialRedTeamerAgent.py`, `GitHygieneAgent.py` |
| L5_safety | validators/ | 3 | `DuplicateCodeDetectorAgent.py`, `LocationAgent.py` |
| L4_state | memory/ | 4 | `CartographerAgent.py`, `RedisSovereignAgent.py` |
| L2_execution | enforcement/ | 3 | `EmbeddingSovereignAgent.py` |
| L6_observability | enforcement/ | 1 | `ReportingAgent.py` |

**Root Cause:** FileClassificationAgent correctly identified these as AGENT type, but `enforce_kernel_structure()` and territory routing logic did not enforce that agents MUST go to `reasoning/`. The agent was classifying correctly but not moving correctly.

**Evidence from FileClassificationAgent.py (lines 291-293):**
```python
# Agents -> reasoning/
if filename.endswith("Agent.py"):
    return layer_root / "reasoning" / filename
```
This only triggers for files "at layer root" (line 266 check), NOT for files already in wrong subfolders.

---

### Category 2: Types Misplaced in Config Folder

**Files Affected:** 7 files in L5_safety/config/

| File | Actual Content |
|------|----------------|
| `code_detector_agent_types_config.py` | `@dataclass`, type definitions |
| `code_enforcer_agent_types_config.py` | `@dataclass`, type definitions |
| `code_validator_agent_types_config.py` | `@dataclass`, Pydantic models |
| `resource_manager_agent_types_config.py` | `BaseModel`, enums |
| `safety_detector_agent_types_config.py` | `@dataclass`, type definitions |
| `security_manager_agent_types_config.py` | `BaseModel`, enums |
| `structure_enforcer_agent_types_config.py` | `@dataclass`, type definitions |

**Root Cause:** Files had COMPOUND SUFFIXES (`_types_config.py`). The classifier saw `_config` and placed them in `config/`, ignoring that `_types` indicates type definitions.

**Evidence:** FileClassificationAgent has no compound-suffix detection. It processes suffixes independently:
- Line 276: `if filename.endswith("_config.py")` → config/
- Line 280: `if filename.endswith("_types.py")` → types/

No logic handles `*_types_config.py` — first match wins, which is arbitrary.

---

### Category 3: Compound Suffix Naming Violations

**Files Affected:** 67 files across all layers

| Pattern | Count | Example |
|---------|-------|---------|
| `*_types_config.py` | 21 | `model_provider_types_config.py` |
| `*_validator_util.py` | 10 | `cache_invalidation_validator_util.py` |
| `*_types_validator.py` | 5 | `healing_orchestration_suite_types_validator.py` |
| `*_config_util.py` | 4 | `dashboard_ssot_definitions_config_util.py` |
| `*_validator_script.py` | 4 | `phase5_validator_script.py` |
| Other compounds | 23 | Various |

**Root Cause:** No enforcement of SINGLE-SUFFIX rule. Files accumulated multiple suffixes over iterations as different agents/scripts added their own markers.

**Evidence:** `_sanitize_filename()` in FileClassificationAgent (lines 843-899) strips suffixes but only for RENAMING, not for VALIDATION. No check flags compound suffixes as violations.

---

### Category 4: Nested Subdirectories Not Dissolved

**Files Affected:** 122+ files in nested structures

| Layer | Nested Path | File Count |
|-------|-------------|------------|
| L5_safety | validators/core/ | 112 |
| L5_safety | validators/surgical/ | 3 |
| L5_safety | validators/anti_patterns/ | 7 |
| L4_state | memory/semantic/ | 1 |
| L0_maintenance | scripts/general_scripts/ | 289 |
| L0_maintenance | scripts/ci/ | 2 |

**Root Cause:** LCD+ migration moved files INTO existing nested folders instead of DISSOLVING them. The migration script respected existing folder structure rather than enforcing flat LCD canonical skeleton.

**Evidence:** `enforce_kernel_structure()` only routes files at "layer root" (depth check at line 266). Files already in nested subdirs are skipped entirely.

---

### Category 5: Mixins at Layer Level Instead of Global

**Files Affected:** 5 files

| File | Wrong Location | Correct Location |
|------|----------------|------------------|
| `cst_healer_mixin.py` | L5_safety/validators/surgical/ | agentic_core/mixins/ |
| `ast_enforcement_mixin.py` | L5_safety/utils/ | agentic_core/mixins/ |
| `healing_strategy_mixin.py` | L5_safety/validators/core/ | agentic_core/mixins/ |
| `surgical_healer_mixin.py` | L5_safety/validators/core/ | agentic_core/mixins/ |
| `validator_mixin.py` | L5_safety/validators/core/ | agentic_core/mixins/ |

**Root Cause:** No global mixin routing rule. FileClassificationAgent classifies mixins correctly as MIXIN type but has no territory enforcement that ALL mixins must go to `agentic_core/mixins/`.

**Evidence:** `check_territory_violation()` has no mixin-specific routing. The `app_territory_map` (line 177) maps MIXIN to `["utils", "shared", "mixins"]` — allowing layer-level placement.

---

## FileClassificationAgent Architectural Failures

### Failure 1: Suffix-Only Classification (Rudimentary)

**Current Logic (lines 501-779):**
```python
def classify_file(self, path: Path) -> FileType:
    # Priority queue based on:
    # 1. Path patterns (base_agents/, tests/)
    # 2. Filename patterns (test_*, *Agent.py)
    # 3. AST class name patterns
```

**Problem:** Classification is SUFFIX-DRIVEN, not CONTENT-DRIVEN. A file named `foo_config.py` is classified as CONFIG even if it contains only `@dataclass` type definitions.

**Evidence:** Lines 684-686 show config detection relies on filename patterns:
```python
config_indicators = ["config", "blueprint", "settings", "manifest", "Config", "Settings", "Options"]
```

No deep content analysis to verify the file actually contains configuration (constants, settings dicts, feature flags) vs type definitions.

### Failure 2: No Compound Suffix Detection

**Current Logic:** Processes suffixes independently with first-match-wins.

**Problem:** `*_types_config.py` matches `_config` first (alphabetically or by code order), ignoring `_types`.

**Missing:** A pre-classification step that detects and rejects compound suffixes:
```python
# MISSING LOGIC:
compound_suffixes = [s for s in KNOWN_SUFFIXES if s in filename]
if len(compound_suffixes) > 1:
    raise CompoundSuffixViolation(f"{filename} has multiple suffixes: {compound_suffixes}")
```

### Failure 3: No Content-Based Type Detection

**Current Logic:** `_detect_type_patterns()` exists but is weak:
```python
def _detect_type_patterns(self, tree, path):
    # Checks for TypedDict, Protocol, Enum imports
    # But doesn't weight @dataclass, BaseModel, or class inheritance
```

**Problem:** A file with 500 lines of `@dataclass` definitions and 1 line of `DEFAULT_TIMEOUT = 30` gets classified as CONFIG if named `*_config.py`.

**Missing:** Content-weighted scoring:
```python
# PROPOSED SCORING:
score = {
    'types': count_dataclasses + count_enums + count_basemodels + count_protocols,
    'config': count_constants + count_settings_dicts + count_feature_flags,
    'util': count_standalone_functions,
    'agent': count_agent_classes + count_sovereign_inheritance,
}
return max(score, key=score.get)
```

### Failure 4: Territory Enforcement Only at Layer Root

**Current Logic (line 266):**
```python
# If file is not at layer root, it's already in a subfolder
if file_depth != layer_idx + 1:
    return None
```

**Problem:** Files already in wrong subfolders are SKIPPED. The agent assumes "if it's in a subfolder, it's correct" — which is false.

**Missing:** Recursive territory validation that checks EVERY file regardless of current depth:
```python
# PROPOSED LOGIC:
def validate_file_territory(self, path: Path) -> Optional[Path]:
    file_type = self.classify_file(path)
    correct_folder = self.get_correct_folder_for_type(file_type)
    current_folder = path.parent.name
    if current_folder != correct_folder:
        return self.compute_correct_path(path, correct_folder)
    return None
```

### Failure 5: No Global Mixin Routing

**Current Logic:** Mixins can live in `utils/`, `shared/`, or `mixins/` per `app_territory_map`.

**Problem:** This allows layer-level mixins, violating the constitutional rule that ALL mixins belong in `agentic_core/mixins/`.

**Missing:** Hard routing rule:
```python
# PROPOSED LOGIC:
if file_type == "MIXIN":
    return Path("agentic_core/mixins") / path.name  # ALWAYS global
```

---

## Proposed Fixes

### Fix 1: Content-Weighted Classification Scoring

Replace suffix-based classification with AST-based content scoring:

```python
def classify_file_by_content(self, path: Path) -> FileType:
    """Score file content to determine true type."""
    content = path.read_text()
    tree = ast.parse(content)
    
    scores = {
        'TYPES': 0,
        'CONFIG': 0,
        'AGENT': 0,
        'UTILITY': 0,
        'VALIDATOR': 0,
    }
    
    for node in ast.walk(tree):
        # Type indicators
        if isinstance(node, ast.ClassDef):
            if any(d.id == 'dataclass' for d in node.decorator_list if isinstance(d, ast.Name)):
                scores['TYPES'] += 10
            if node.name.endswith('Agent'):
                scores['AGENT'] += 20
            if 'BaseModel' in [b.id for b in node.bases if isinstance(b, ast.Name)]:
                scores['TYPES'] += 10
            if 'Enum' in [b.id for b in node.bases if isinstance(b, ast.Name)]:
                scores['TYPES'] += 10
            if 'Protocol' in [b.id for b in node.bases if isinstance(b, ast.Name)]:
                scores['TYPES'] += 15
        
        # Config indicators
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    scores['CONFIG'] += 5  # CONSTANT = value
        
        # Utility indicators
        if isinstance(node, ast.FunctionDef) and not self._is_method(node):
            scores['UTILITY'] += 3
        
        # Validator indicators
        if isinstance(node, ast.FunctionDef) and node.name.startswith(('validate_', 'check_')):
            scores['VALIDATOR'] += 5
    
    # Winner takes all
    return max(scores, key=scores.get)
```

### Fix 2: Compound Suffix Pre-Validation

Add a pre-classification gate that rejects compound suffixes:

```python
KNOWN_SUFFIXES = ['_types', '_config', '_validator', '_script', '_util', '_mixin']

def validate_single_suffix(self, filename: str) -> None:
    """Reject files with multiple architectural suffixes."""
    stem = filename[:-3]  # Remove .py
    found_suffixes = [s for s in KNOWN_SUFFIXES if s in stem]
    
    if len(found_suffixes) > 1:
        raise CompoundSuffixViolation(
            f"File '{filename}' has {len(found_suffixes)} suffixes: {found_suffixes}. "
            f"Files must have exactly ONE suffix. Rename to use the primary suffix."
        )
```

### Fix 3: Recursive Territory Enforcement

Remove the "layer root only" restriction:

```python
def enforce_territory_recursive(self, path: Path) -> Optional[Path]:
    """Enforce correct territory for ALL files, not just layer root."""
    file_type = self.classify_file(path)
    
    # Global rules (apply everywhere)
    if file_type == 'MIXIN':
        return Path('agentic_core/mixins') / path.name
    
    # Layer rules
    layer_root = self.get_layer_root(path)
    if not layer_root:
        return None
    
    correct_folder = TYPE_TO_FOLDER.get(file_type)
    if not correct_folder:
        return None
    
    correct_path = layer_root / correct_folder / path.name
    if path != correct_path:
        return correct_path
    
    return None
```

### Fix 4: Update structure_blueprint_config.py

Add explicit suffix-to-folder mapping:

```python
SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {
    '_config.py': 'config',
    '_types.py': 'types',
    '_validator.py': 'validators',
    '_script.py': 'enforcement',
    '_util.py': 'utils',
    '_mixin.py': 'GLOBAL_MIXINS',  # Special: agentic_core/mixins/
    'Agent.py': 'reasoning',
    'Monitor.py': 'reasoning',
    'Inspector.py': 'reasoning',
    'Healer.py': 'reasoning',
    'Guardian.py': 'reasoning',
    'Orchestrator.py': 'reasoning',
    'Strategy.py': 'reasoning',
    'Adapter.py': 'reasoning',
    'Protocol.py': 'types',
    'Error.py': 'types',
}

FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = [
    r'.*_types_config\.py$',
    r'.*_validator_util\.py$',
    r'.*_types_validator\.py$',
    r'.*_config_util\.py$',
    r'.*_validator_script\.py$',
    r'.*_config_script\.py$',
]
```

### Fix 5: Add Classification Confidence Scoring

Return confidence with classification to flag ambiguous files:

```python
@dataclass
class ClassificationResult:
    file_type: FileType
    confidence: float  # 0.0 - 1.0
    signals: list[str]  # Evidence for classification
    warnings: list[str]  # Ambiguity warnings

def classify_file_with_confidence(self, path: Path) -> ClassificationResult:
    scores = self._compute_content_scores(path)
    total = sum(scores.values())
    
    if total == 0:
        return ClassificationResult('UTILITY', 0.5, [], ['No classification signals found'])
    
    winner = max(scores, key=scores.get)
    confidence = scores[winner] / total
    
    warnings = []
    if confidence < 0.6:
        runner_up = sorted(scores, key=scores.get, reverse=True)[1]
        warnings.append(f"Ambiguous: {winner} ({scores[winner]}) vs {runner_up} ({scores[runner_up]})")
    
    return ClassificationResult(winner, confidence, self._get_signals(path), warnings)
```

---

## Recommended Implementation Order

1. **Immediate (P0):** Add compound suffix validation to pre-commit hook
2. **Short-term (P1):** Implement content-weighted scoring in FileClassificationAgent
3. **Medium-term (P2):** Add recursive territory enforcement
4. **Long-term (P3):** Implement confidence scoring and ambiguity flagging

---

## Files Requiring Updates

| File | Changes Required |
|------|------------------|
| `FileClassificationAgent.py` | Add content scoring, compound suffix detection, recursive territory enforcement |
| `structure_blueprint_config.py` | Add SUFFIX_TO_FOLDER mapping, FORBIDDEN_COMPOUND_PATTERNS |
| `LocationAgent.py` | Integrate with new territory enforcement |
| `.pre-commit-config.yaml` | Add compound suffix validation hook |

---

## Conclusion

The LCD+ migration failed repeatedly because FileClassificationAgent uses **rudimentary suffix-based classification** without:
1. Content-weighted scoring
2. Compound suffix detection
3. Recursive territory enforcement
4. Global mixin routing
5. Confidence/ambiguity flagging

The proposed fixes transform classification from "filename pattern matching" to "AST-based content analysis with weighted scoring" — a fundamental architectural upgrade that will prevent future migration failures.

---

*Report generated: 2026-02-07*
*Author: Cascade RCA System*
