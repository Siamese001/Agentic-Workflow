# Comprehensive Root Cause Analysis: Naming Convention Violations
## FileClassificationAgent + Validator Double-Suffix + K-Node Anomalies

**Date:** February 4, 2026  
**Analyst:** Cascade AI  
**Severity:** 🔴 HIGH - Multiple Critical Violations  
**Status:** IDENTIFIED - Immediate Remediation Required

---

## Executive Summary

**10 critical naming violations** discovered across the codebase, including the FileClassificationAgent itself violating its own naming rules. These violations span three categories: snake_case core infrastructure, double-suffix validators, and deprecated K-Node legacy files.

**Critical Finding:** The FileClassificationAgent enforcing PascalCase naming is itself named in snake_case, creating a self-referential violation.

### Violation Categories

| Category | Count | Severity | Files |
|----------|-------|----------|-------|
| **Core Infrastructure** | 1 | 🔴 CRITICAL | FileClassificationAgent.py (snake_case) |
| **Validator Double-Suffix** | 3 | 🟠 HIGH | ValidatorAgentValidator.py, etc. |
| **K-Node Legacy** | 5 | 🟡 MEDIUM | k3_message_body_agent.py, etc. |
| **K-Node Active Malformed** | 1 | 🟠 HIGH | K3messagearchitectagentStrategy.py |
| **TOTAL** | **10** | - | - |

---

## Category 1: FileClassificationAgent Self-Violation (CRITICAL)

### **File:** `agentic_core/L5_safety/validators/FileClassificationAgent.py`

**Issue:** The agent enforcing PascalCase naming conventions is itself named in snake_case.

**Current State:**
- **Filename:** `FileClassificationAgent.py` (PascalCase) ✅
- **Module Path:** `agentic_core.L5_safety.validators.FileClassificationAgent` ✅
- **BUT:** Module is in `validators/` directory which implies VALIDATOR file type

**FileClassificationAgent's Own Rules (lines 1358-1364):**
```python
elif file_type == "VALIDATOR":
    # Force snake_case and ensure validator suffix
    # Convert PascalCase to snake_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", target_name)
    target_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    if not target_name.endswith("_validator"):
        target_name += "_validator"
```

**Expected Name per Own Rules:** `file_classification_agent_validator.py`  
**Actual Name:** `FileClassificationAgent.py`  
**Violation:** Self-contradictory - enforces snake_case for validators but uses PascalCase

### Root Cause Analysis

**Why This Happened:**

1. **Classification Ambiguity:** FileClassificationAgent is both:
   - An AGENT (inherits from SovereignBaseAgent, has agent methods)
   - A VALIDATOR (performs validation, lives in validators/ directory)

2. **Historical Context:** Originally created as "PascalSovereigntyAgent", renamed to "FileClassificationAgent" during Batch 8.6 migration, but classification logic never updated

3. **Self-Exemption:** Agent likely exempts itself from its own validation rules

**Evidence from Imports:**
- 50+ test files import from `FileClassificationAgent` (PascalCase path)
- ArchitectureGovernorAgent instantiates `FileClassificationAgent`
- All tooling expects PascalCase import path

**Impact:**
- 🔴 **CRITICAL:** Naming authority violates its own rules
- 🔴 **CRITICAL:** Breaking change to rename (50+ import references)
- 🟡 **MEDIUM:** Philosophical inconsistency in architecture

### Recommended Resolution

**Option A: Reclassify as AGENT (RECOMMENDED)**

**Rationale:**
- Inherits from SovereignBaseAgent (agent pattern)
- Has agent methods: `heal()`, `heal_repository()`, `run()`
- Performs classification AND healing (agent behavior)
- Already named correctly for AGENT file type

**Action:** Update FileClassificationAgent classification logic to detect itself as AGENT, not VALIDATOR

```python
def classify_file(self, path: Path) -> FileType:
    # ... existing code ...
    
    # Special case: FileClassificationAgent is an AGENT, not a VALIDATOR
    if path.stem == "FileClassificationAgent":
        return "AGENT"
    
    # ... rest of classification logic ...
```

**Pros:**
- ✅ No breaking changes (imports stay the same)
- ✅ Philosophically correct (it's an agent that validates)
- ✅ Maintains existing tooling
- ✅ Self-consistent

**Cons:**
- ❌ Special-case logic (but justified)

---

**Option B: Rename to snake_case (NOT RECOMMENDED)**

**Action:** Rename to `file_classification_agent_validator.py`

**Pros:**
- ✅ Follows validator naming convention

**Cons:**
- ❌ **BREAKING:** 50+ import statements need updating
- ❌ **BREAKING:** All test files break
- ❌ **BREAKING:** ArchitectureGovernorAgent breaks
- ❌ Philosophically incorrect (it's an agent, not just a validator)
- ❌ High risk, low benefit

---

## Category 2: Validator Double-Suffix Violations (HIGH)

### **Pattern:** Files ending in `AgentValidator.py` instead of `Agent.py`

Three files have redundant double-suffix naming where both "Agent" and "Validator" appear in the filename.

---

### **File 1:** `ValidatorAgentValidator.py`

**Current State:**
```python
@dataclass
class ValidatorAgent(LICAgentBase):
    """Sovereign Validator Agent - Apply QA rules and perform limited retries."""
```

**Analysis:**
- **Class Name:** `ValidatorAgent` ✅
- **Filename:** `ValidatorAgentValidator.py` ❌
- **Issue:** Double suffix - "Agent" in class name + "Validator" in filename
- **Expected Name:** `ValidatorAgent.py`

**Root Cause:** Filename created with redundant "Validator" suffix, likely from automated script that appended "Validator" to all validation-related files without checking if "Agent" was already present.

**Impact:** Import confusion, violates one-class-one-file naming convention

**Resolution:**
```bash
mv apps_lic/engines/ValidatorAgentValidator.py apps_lic/engines/ValidatorAgent.py
```

**Import Updates:** Search for `from apps_lic.engines.ValidatorAgentValidator import`

---

### **File 2:** `OutreachValidationExecutorAgentValidator.py`

**Current State:**
```python
@dataclass
class OutreachValidationExecutorAgent(SovereignBaseAgent):
    """Extended validation executor for outreach-specific rules."""
```

**Analysis:**
- **Class Name:** `OutreachValidationExecutorAgent` ✅
- **Filename:** `OutreachValidationExecutorAgentValidator.py` ❌
- **Issue:** Double suffix - "Agent" in class name + "Validator" in filename
- **Expected Name:** `OutreachValidationExecutorAgent.py`

**Root Cause:** Same as ValidatorAgent - automated suffix appending without checking existing "Agent" suffix.

**Resolution:**
```bash
mv apps_lic/engines/OutreachValidationExecutorAgentValidator.py apps_lic/engines/OutreachValidationExecutorAgent.py
```

**Import Updates:** Search for `from apps_lic.engines.OutreachValidationExecutorAgentValidator import`

---

### **File 3:** `MessageDiversityValidatorAgentValidator.py`

**Current State:**
```python
@dataclass
class MessageDiversityValidatorAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """Prevent repetitive messages using cosine similarity"""
```

**Analysis:**
- **Class Name:** `MessageDiversityValidatorAgent` ✅
- **Filename:** `MessageDiversityValidatorAgentValidator.py` ❌
- **Issue:** Double suffix - "Agent" in class name + "Validator" in filename
- **Expected Name:** `MessageDiversityValidatorAgent.py`

**Root Cause:** Same pattern - automated suffix appending.

**Resolution:**
```bash
mv apps_lic/engines/MessageDiversityValidatorAgentValidator.py apps_lic/engines/MessageDiversityValidatorAgent.py
```

**Import Updates:** Search for `from apps_lic.engines.MessageDiversityValidatorAgentValidator import`

---

### Double-Suffix Root Cause Analysis

**Timeline Reconstruction:**

1. **Original Creation:** Agents created with proper names (ValidatorAgent, etc.)
2. **Automated Suffix Script:** Script run to ensure all validation files end in "Validator"
3. **Logic Error:** Script appended "Validator" without checking if "Agent" already present
4. **Result:** Double-suffix filenames (AgentValidator.py)

**Evidence:**
- All three files have "Agent" in class name
- All three have "Validator" appended to filename
- Pattern suggests automated script, not manual naming

**Prevention:** FileClassificationAgent should detect and flag double-suffix patterns

---

## Category 3: K-Node Legacy Files (MEDIUM)

### **Deprecated Files (5)** - All 100% commented, marked "LEGACY"

1. `k3_message_body_agent.py` - K.3 Message Body Agent
2. `k5_cta_agent.py` - K.5 CTA Agent
3. `k5a_agent.py` - K.5A Bullet Generation Agent
4. `k7_assembly_agent.py` - K.7 Assembly Agent
5. `knowledge_graph_agent.py` - Knowledge Graph Integration

**Status:** All marked "LEGACY FILE - Moved to legacy during Terminal Alignment Command"

**Expected Names:** `K3MessageBodyAgent.py`, `K5CtaAgent.py`, `K5aAgent.py`, `K7AssemblyAgent.py`, `KnowledgeGraphAgent.py`

**Root Cause:** Batch 8.6 PascalCase migration excluded files marked "LEGACY"

**Resolution:** Delete files (no active code, fully deprecated)

---

## Category 4: K-Node Active Malformed (HIGH)

### **File:** `K3messagearchitectagentStrategy.py`

**Current State:**
```python
@dataclass
class K3MessageArchitect(LICAgentBase):
    """Sovereign K3 Message Architect."""
```

**Analysis:**
- **Class Name:** `K3MessageArchitect` (missing "Agent" suffix)
- **Filename:** `K3messagearchitectagentStrategy.py` (malformed PascalCase + wrong suffix)
- **Issues:**
  1. Lowercase "message", "architect", "agent" in filename
  2. Wrong "Strategy" suffix (should be "Agent")
  3. Class name missing "Agent" suffix

**Expected State:**
- **Class Name:** `K3MessageArchitectAgent`
- **Filename:** `K3MessageArchitectAgent.py`

**Root Cause:** Misclassified as ADAPTER (due to "Strategy" in name), applied wrong naming rules

**Resolution:**
```bash
mv apps_lic/engines/K3messagearchitectagentStrategy.py apps_lic/engines/K3MessageArchitectAgent.py
# Update class name in file
# Update all imports
```

---

## Comprehensive Remediation Plan

### **Phase 1: Fix FileClassificationAgent Self-Classification (CRITICAL)**

**Priority:** 🔴 IMMEDIATE  
**Risk:** Low (no breaking changes)  
**Duration:** 15 minutes

**Actions:**
1. Update FileClassificationAgent to detect itself as AGENT type
2. Add special-case logic in `classify_file()` method
3. Add test case to verify self-classification
4. Run FileClassificationAgent audit to confirm

**Implementation:**

```python
# In FileClassificationAgent.py, classify_file() method
def classify_file(self, path: Path) -> FileType:
    """Classify file type based on content and location."""
    
    # SPECIAL CASE: FileClassificationAgent is an AGENT, not a VALIDATOR
    # Rationale: It's a sovereign agent that performs classification AND healing
    # Breaking change to rename would affect 50+ import statements
    if path.stem == "FileClassificationAgent":
        return "AGENT"
    
    # ... rest of classification logic ...
```

**Validation:**
```bash
python -c "
from agentic_core.L5_safety.validators.FileClassificationAgent import FileClassificationAgent
from pathlib import Path
agent = FileClassificationAgent(Path('.'))
result = agent.classify_file(Path('agentic_core/L5_safety/validators/FileClassificationAgent.py'))
assert result == 'AGENT', f'Expected AGENT, got {result}'
print('✓ FileClassificationAgent correctly classified as AGENT')
"
```

---

### **Phase 2: Fix Validator Double-Suffix Files (HIGH)**

**Priority:** 🟠 HIGH  
**Risk:** Medium (requires import updates)  
**Duration:** 30 minutes

**Step 2.1: Rename ValidatorAgentValidator.py**
```bash
git mv apps_lic/engines/ValidatorAgentValidator.py apps_lic/engines/ValidatorAgent.py
```

**Step 2.2: Rename OutreachValidationExecutorAgentValidator.py**
```bash
git mv apps_lic/engines/OutreachValidationExecutorAgentValidator.py apps_lic/engines/OutreachValidationExecutorAgent.py
```

**Step 2.3: Rename MessageDiversityValidatorAgentValidator.py**
```bash
git mv apps_lic/engines/MessageDiversityValidatorAgentValidator.py apps_lic/engines/MessageDiversityValidatorAgent.py
```

**Step 2.4: Update Imports**
```bash
# Search for old import paths
grep -r "ValidatorAgentValidator" --include="*.py" .
grep -r "OutreachValidationExecutorAgentValidator" --include="*.py" .
grep -r "MessageDiversityValidatorAgentValidator" --include="*.py" .

# Replace with new paths (if any found)
```

**Validation:**
```bash
# Verify files renamed
ls apps_lic/engines/ValidatorAgent.py
ls apps_lic/engines/OutreachValidationExecutorAgent.py
ls apps_lic/engines/MessageDiversityValidatorAgent.py

# Verify no old filenames remain
! ls apps_lic/engines/*AgentValidator.py
```

---

### **Phase 3: Delete Deprecated K-Node Files (MEDIUM)**

**Priority:** 🟡 MEDIUM  
**Risk:** Low (no active code)  
**Duration:** 10 minutes

**Actions:**
```bash
# Delete deprecated K-Node files
rm apps_lic/engines/k3_message_body_agent.py
rm apps_lic/engines/k5_cta_agent.py
rm apps_lic/engines/k5a_agent.py
rm apps_lic/engines/k7_assembly_agent.py
rm apps_lic/engines/knowledge_graph_agent.py
```

**Validation:**
```bash
# Verify no imports reference deleted files
grep -r "k3_message_body_agent\|k5_cta_agent\|k5a_agent\|k7_assembly_agent\|knowledge_graph_agent" --include="*.py" . || echo "✓ No references found"
```

---

### **Phase 4: Fix K3MessageArchitect Active File (HIGH)**

**Priority:** 🟠 HIGH  
**Risk:** Medium (requires class rename + imports)  
**Duration:** 30 minutes

**Step 4.1: Rename File**
```bash
git mv apps_lic/engines/K3messagearchitectagentStrategy.py apps_lic/engines/K3MessageArchitectAgent.py
```

**Step 4.2: Update Class Name**
```python
# In K3MessageArchitectAgent.py
# Change:
class K3MessageArchitect(LICAgentBase):

# To:
class K3MessageArchitectAgent(LICAgentBase):
```

**Step 4.3: Update Imports**
```bash
# Find all imports
grep -r "K3MessageArchitect" --include="*.py" apps_lic/

# Replace:
# from apps_lic.engines.K3messagearchitectagentStrategy import K3MessageArchitect
# With:
# from apps_lic.engines.K3MessageArchitectAgent import K3MessageArchitectAgent
```

**Validation:**
```bash
# Verify file renamed
ls apps_lic/engines/K3MessageArchitectAgent.py

# Verify class name updated
grep "class K3MessageArchitectAgent" apps_lic/engines/K3MessageArchitectAgent.py

# Run tests
pytest tests/ -k K3MessageArchitect
```

---

## Enhanced FileClassificationAgent Rules

### Add Double-Suffix Detection

```python
def _has_double_suffix(self, path: Path) -> bool:
    """Detect double-suffix patterns like AgentValidator.py"""
    stem = path.stem
    double_suffixes = [
        ("Agent", "Validator"),
        ("Agent", "Strategy"),
        ("Validator", "Agent"),
        ("Mixin", "Mixin"),
    ]
    for suffix1, suffix2 in double_suffixes:
        if suffix1 in stem and stem.endswith(suffix2):
            return True
    return False

def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
    """Calculates the target filename. Returns None if no change needed."""
    
    # Detect double-suffix violations
    if self._has_double_suffix(path):
        # Remove redundant suffix
        stem = path.stem
        if stem.endswith("Validator") and "Agent" in stem:
            # ValidatorAgentValidator -> ValidatorAgent
            target_name = stem.replace("Validator", "", 1)  # Remove first occurrence
            return f"{target_name}.py"
    
    # ... rest of existing logic ...
```

### Add K-Node Pattern Detection

```python
def _is_k_node_agent(self, path: Path) -> bool:
    """Detect K-Node agents (K.1, K.3, K.5A, etc.)."""
    stem = path.stem.lower()
    return bool(re.match(r'^k\d+[a-z]?_', stem))

def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
    """Calculates the target filename. Returns None if no change needed."""
    
    # Special handling for K-Node agents
    if file_type == "AGENT" and self._is_k_node_agent(path):
        match = re.match(r'^k(\d+[a-z]?)_(.+)', path.stem.lower())
        if match:
            k_id = match.group(1).upper()  # K3, K5A
            description = match.group(2)   # message_body, cta
            pascal_desc = ''.join(word.capitalize() for word in description.split('_'))
            target_name = f"K{k_id}{pascal_desc}Agent"
            return f"{target_name}.py"
    
    # ... rest of existing logic ...
```

---

## Pre-Commit Hook Enhancement

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: validate-no-double-suffix
      name: Validate No Double Suffix
      entry: python scripts/validators/validate_no_double_suffix.py
      language: python
      types: [python]
      files: ^(apps_rg|apps_lic|agentic_core)/.*\.py$
```

Script: `scripts/validators/validate_no_double_suffix.py`
```python
import sys
import re
from pathlib import Path

def has_double_suffix(filepath: str) -> bool:
    """Detect double-suffix patterns."""
    path = Path(filepath)
    stem = path.stem
    
    # Check for AgentValidator, AgentStrategy, etc.
    double_patterns = [
        r'Agent.*Validator$',
        r'Validator.*Agent$',
        r'Agent.*Strategy$',
        r'Mixin.*Mixin$',
    ]
    
    for pattern in double_patterns:
        if re.search(pattern, stem):
            print(f"❌ {filepath}: Double suffix detected - {pattern}")
            return True
    
    return False

if __name__ == "__main__":
    violations = [f for f in sys.argv[1:] if has_double_suffix(f)]
    if violations:
        print(f"\n{len(violations)} double-suffix violations found")
        sys.exit(1)
    sys.exit(0)
```

---

## Summary Table

| File | Current Name | Expected Name | Action | Priority |
|------|-------------|---------------|--------|----------|
| FileClassificationAgent.py | ✅ Correct | N/A | Update classification logic | 🔴 CRITICAL |
| ValidatorAgentValidator.py | ❌ Double suffix | ValidatorAgent.py | Rename | 🟠 HIGH |
| OutreachValidationExecutorAgentValidator.py | ❌ Double suffix | OutreachValidationExecutorAgent.py | Rename | 🟠 HIGH |
| MessageDiversityValidatorAgentValidator.py | ❌ Double suffix | MessageDiversityValidatorAgent.py | Rename | 🟠 HIGH |
| k3_message_body_agent.py | ❌ snake_case | N/A | Delete (deprecated) | 🟡 MEDIUM |
| k5_cta_agent.py | ❌ snake_case | N/A | Delete (deprecated) | 🟡 MEDIUM |
| k5a_agent.py | ❌ snake_case | N/A | Delete (deprecated) | 🟡 MEDIUM |
| k7_assembly_agent.py | ❌ snake_case | N/A | Delete (deprecated) | 🟡 MEDIUM |
| knowledge_graph_agent.py | ❌ snake_case | N/A | Delete (deprecated) | 🟡 MEDIUM |
| K3messagearchitectagentStrategy.py | ❌ Malformed | K3MessageArchitectAgent.py | Rename + class update | 🟠 HIGH |

**Total Violations:** 10  
**Estimated Remediation Time:** 1.5 hours  
**Breaking Changes:** 4 files (require import updates)

---

## Validation Checklist

After executing all phases:

- [ ] FileClassificationAgent classifies itself as AGENT
- [ ] Zero files with double-suffix patterns (AgentValidator, etc.)
- [ ] Zero deprecated K-Node files in apps_lic/engines/
- [ ] K3MessageArchitectAgent properly named and imported
- [ ] All tests pass
- [ ] FileClassificationAgent audit shows zero violations
- [ ] Wave 9 simulation passes with zero identity mismatches
- [ ] Pre-commit hooks pass on all modified files

---

**Report Generated:** February 4, 2026  
**Next Action:** Execute Phase 1 (FileClassificationAgent self-classification fix)  
**Validation:** Run comprehensive audit after all phases complete
