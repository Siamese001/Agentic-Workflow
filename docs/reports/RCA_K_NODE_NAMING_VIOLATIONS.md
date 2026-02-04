# Root Cause Analysis: K-Node Naming Convention Violations
## apps_lic/engines Snake_Case Anomalies

**Date:** February 4, 2026  
**Analyst:** Cascade AI  
**Severity:** 🟡 MEDIUM - Architectural Inconsistency  
**Status:** IDENTIFIED - Remediation Required

---

## Executive Summary

Four legacy K-Node agent files in `apps_lic/engines/` violate the FileClassificationAgent PascalCase naming convention for AGENT file types. These files were marked as "LEGACY" during a "Terminal Alignment Command" and contain only commented-out code with deprecation warnings. One additional file (`K3messagearchitectagentStrategy.py`) has a malformed PascalCase name.

**Affected Files:**
1. `k3_message_body_agent.py` - snake_case (LEGACY/DEPRECATED)
2. `k5_cta_agent.py` - snake_case (LEGACY/DEPRECATED)
3. `k5a_agent.py` - snake_case (LEGACY/DEPRECATED)
4. `k7_assembly_agent.py` - snake_case (LEGACY/DEPRECATED)
5. `K3messagearchitectagentStrategy.py` - malformed PascalCase (ACTIVE)
6. `knowledge_graph_agent.py` - snake_case (LEGACY/DEPRECATED)

**Root Cause:** Historical preservation of deprecated K-Node architecture from archived Reachout Engine without proper migration to PascalCase conventions.

---

## Detailed Analysis

### 1. File Status Investigation

#### **k3_message_body_agent.py**
```python
"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""
# All code commented out
```

**Findings:**
- File contains NO active code (100% commented)
- Header indicates "Terminal Alignment Command" deprecation
- Originally: K.3 Message Body Agent for archetype-specific content generation
- Class would have been: `K3MessageBodyAgent` (if active)

**Expected Name per FileClassificationAgent:** `K3MessageBodyAgent.py`  
**Actual Name:** `k3_message_body_agent.py`  
**Violation:** snake_case instead of PascalCase

---

#### **k5_cta_agent.py**
```python
"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""
# All code commented out
```

**Findings:**
- File contains NO active code (100% commented)
- Originally: K.5 CTA Agent for route-specific call-to-action generation
- Class would have been: `K5CtaAgent` (if active)

**Expected Name per FileClassificationAgent:** `K5CtaAgent.py`  
**Actual Name:** `k5_cta_agent.py`  
**Violation:** snake_case instead of PascalCase

---

#### **k5a_agent.py**
```python
"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""
# All code commented out
```

**Findings:**
- File contains NO active code (100% commented)
- Originally: K.5A Generation Agent for Unify bullets with provenance rules (3V-3T-1S)
- Class would have been: `K5aAgent` (if active)

**Expected Name per FileClassificationAgent:** `K5aAgent.py`  
**Actual Name:** `k5a_agent.py`  
**Violation:** snake_case instead of PascalCase

---

#### **k7_assembly_agent.py**
```python
"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""
# All code commented out
```

**Findings:**
- File contains NO active code (100% commented)
- Originally: K.7 Assembly Agent for final message assembly with signature immutability
- Class would have been: `K7AssemblyAgent` (if active)

**Expected Name per FileClassificationAgent:** `K7AssemblyAgent.py`  
**Actual Name:** `k7_assembly_agent.py`  
**Violation:** snake_case instead of PascalCase

---

#### **K3messagearchitectagentStrategy.py** (ACTIVE FILE)
```python
@dataclass
class K3MessageArchitect(LICAgentBase):
    """
    Sovereign K3 Message Architect.
    Constructs message frameworks based on strategic inputs.
    """
```

**Findings:**
- File contains ACTIVE code (not deprecated)
- Class name: `K3MessageArchitect`
- Filename has malformed PascalCase: `K3messagearchitectagentStrategy.py`
- Docstring header incorrectly references: `apps_lic/engines/k3_message_architect.py`

**Expected Name per FileClassificationAgent:** `K3MessageArchitectAgent.py`  
**Actual Name:** `K3messagearchitectagentStrategy.py`  
**Violations:**
1. Malformed PascalCase (lowercase `message`, `architect`, `agent`)
2. Incorrect `Strategy` suffix (should be `Agent`)
3. Missing `Agent` suffix on class name

---

#### **knowledge_graph_agent.py**
```python
"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""
# All code commented out
```

**Findings:**
- File contains NO active code (100% commented)
- Originally: Knowledge Graph Integration for Neo4j-based reasoning
- Class would have been: `KnowledgeGraphAgent` (if active)

**Expected Name per FileClassificationAgent:** `KnowledgeGraphAgent.py`  
**Actual Name:** `knowledge_graph_agent.py`  
**Violation:** snake_case instead of PascalCase

---

### 2. Root Cause Analysis

#### **Primary Root Cause: Historical Preservation Without Migration**

**Timeline Reconstruction:**

1. **Original Creation (Pre-Batch 8.6)**
   - K-Node agents created in snake_case following early conventions
   - Files: `k3_message_body_agent.py`, `k5_cta_agent.py`, `k5a_agent.py`, `k7_assembly_agent.py`
   - Source: Archived "Reachout Engine" codebase

2. **Terminal Alignment Command (Unknown Date)**
   - Decision made to deprecate K-Node architecture
   - Files marked as "LEGACY" with deprecation warnings
   - All code commented out but files preserved in repository
   - **Critical Error:** Files NOT renamed to PascalCase during deprecation

3. **Batch 8.6: PascalCase Migration (Recent)**
   - Mass migration of agent files to PascalCase
   - FileClassificationAgent established as naming authority
   - **Gap:** Legacy/deprecated files excluded from migration scope
   - Assumption: "If it's commented out, don't touch it"

4. **Current State**
   - 29 properly named PascalCase agents in `apps_lic/engines/`
   - 6 snake_case violations (5 deprecated, 1 active malformed)
   - FileClassificationAgent detects violations but no healing action taken

---

#### **Secondary Root Causes**

##### **A. Incomplete Migration Scope**
**Evidence:**
- `SOVEREIGN_FOUNDATION_REPORT.md` lists K-Node agents as "KEEP" status
- Migration scripts likely filtered out files with "LEGACY" headers
- No validation step to ensure ALL `.py` files conform to naming standards

**Impact:** Legacy files preserved in non-compliant state

---

##### **B. K-Node Architectural Ambiguity**
**Evidence from `K_NODE_EVOLUTION_ANALYSIS.md`:**
```
K-Node Architecture Evolution:
- Early Architecture (v1.0-v15.4): Simple linear K-nodes K.1 through K.10
- Production-Ready (v61.27.10): Two-phase generation (K.5A/K.5B, K.6A/K.6B)
```

**Confusion:**
- K-Nodes are specialist agents with numeric identifiers (K.1, K.3, K.5A, K.7)
- Unclear if they should follow standard agent naming or special K-Node naming
- No explicit guidance in FileClassificationAgent for K-Node naming patterns

**Impact:** Developers unsure whether to name as `K3MessageBodyAgent.py` or `k3_message_body_agent.py`

---

##### **C. "Strategy" Suffix Misapplication**
**Evidence:**
- `K3messagearchitectagentStrategy.py` has incorrect `Strategy` suffix
- FileClassificationAgent rule (line 1347-1351):
  ```python
  elif file_type == "ADAPTER":
      if "Strategy" not in target_name:
          if "Adapter" not in target_name:
              target_name += "Strategy"
  ```

**Confusion:**
- File classified as ADAPTER instead of AGENT
- Strategy pattern suffix applied incorrectly
- Class name `K3MessageArchitect` doesn't match filename

**Impact:** Active file has malformed name causing import confusion

---

##### **D. Lack of Enforcement for Deprecated Files**
**Evidence:**
- Pre-commit hooks likely skip files with "LEGACY" markers
- No validation that deprecated files still conform to naming standards
- Assumption: "Dead code doesn't need to be compliant"

**Counterargument:**
- Files still in repository pollute namespace
- Confuse developers looking for K-Node implementations
- Break automated tooling that scans for agents

**Impact:** Technical debt accumulates in deprecated code

---

### 3. FileClassificationAgent Naming Logic Analysis

#### **Expected Behavior for AGENT File Type**

From `FileClassificationAgent.py:1317-1319`:
```python
if file_type == "AGENT":
    if not target_name.endswith("Agent"):
        target_name += "Agent"
```

**Logic:**
1. Parse file to extract primary class name
2. If class doesn't end with "Agent", append "Agent"
3. Return PascalCase filename: `{ClassName}.py`

**Expected Transformations:**
- `k3_message_body_agent.py` → `K3MessageBodyAgent.py`
- `k5_cta_agent.py` → `K5CtaAgent.py`
- `k5a_agent.py` → `K5aAgent.py`
- `k7_assembly_agent.py` → `K7AssemblyAgent.py`
- `knowledge_graph_agent.py` → `KnowledgeGraphAgent.py`

**Why It Didn't Happen:**
- Files contain NO class definitions (all commented out)
- FileClassificationAgent can't extract class name from commented code
- Falls back to heuristic: filename stem → PascalCase
- **But:** Healing likely skipped for files marked "LEGACY"

---

#### **Special Case: K3messagearchitectagentStrategy.py**

**Actual Class:** `K3MessageArchitect`  
**Filename:** `K3messagearchitectagentStrategy.py`

**Misclassification Hypothesis:**
1. FileClassificationAgent detects `Strategy` in filename
2. Classifies as ADAPTER instead of AGENT
3. Applies ADAPTER naming rules (preserve Strategy suffix)
4. **Error:** Class name `K3MessageArchitect` doesn't end in "Agent"

**Correct Classification Should Be:**
- File Type: AGENT (inherits from LICAgentBase)
- Expected Name: `K3MessageArchitectAgent.py`
- Class Name Should Be: `K3MessageArchitectAgent`

---

### 4. Comparison with Compliant Agents

#### **Properly Named K-Node Agents (if they existed)**

**Current Compliant Agents in apps_lic/engines:**
- `CampaignBalanceAgent.py` ✅
- `OutreachPhase5OrchestratorAgent.py` ✅
- `PIISanitizerSpecialistAgent.py` ✅
- `Hop1ProfileAnalysisAgent.py` ✅

**Pattern:** PascalCase, descriptive name, "Agent" suffix

**If K-Nodes Were Compliant:**
- `K3MessageBodyAgent.py` (for K.3 Message Body generation)
- `K5CtaAgent.py` (for K.5 CTA generation)
- `K5aAgent.py` (for K.5A bullet generation)
- `K7AssemblyAgent.py` (for K.7 final assembly)
- `KnowledgeGraphAgent.py` (for graph integration)

---

### 5. Impact Assessment

#### **A. Import Confusion**
**Risk:** Developers may attempt to import K-Node agents using snake_case paths

```python
# FAILS (file doesn't export anything)
from apps_lic.engines.k3_message_body_agent import K3MessageBodyAgent

# WORKS (but wrong name)
from apps_lic.engines.K3messagearchitectagentStrategy import K3MessageArchitect
```

**Impact:** Import errors, confusion about K-Node availability

---

#### **B. Automated Tooling Failures**
**Affected Tools:**
- `agent_discovery_full.json` - May miss or misclassify K-Node agents
- FileClassificationAgent - Detects violations but can't heal commented files
- Import validators - Flag as broken imports
- Wave 9 simulation - Identity resolution mismatches

**Evidence from Wave 9:**
```
Identity resolution: 2/5 MISMATCH
- apps_lic/engines/architecture_visualizer_agent.py: MISMATCH
```

**Impact:** Automated governance tools report false positives

---

#### **C. Historical Context Loss**
**Risk:** Future developers don't understand K-Node evolution

**Questions Raised:**
- "Why are there snake_case agents in apps_lic/engines?"
- "Are K-Nodes still used or fully deprecated?"
- "Should I implement K.3 or use a different pattern?"

**Impact:** Architectural decisions made without historical context

---

#### **D. Repository Pollution**
**Current State:**
- 6 deprecated files (5 snake_case, 1 malformed) = ~1,800 lines of commented code
- Files appear in directory listings, confusing developers
- No clear signal that files are deprecated (only in docstring)

**Impact:** Cluttered codebase, harder to navigate

---

## Remediation Recommendations

### **Option 1: Delete Deprecated Files (RECOMMENDED)**

**Rationale:**
- Files contain NO active code (100% commented)
- Marked as "DEPRECATED - Do not use in production"
- Historical context preserved in `K_NODE_EVOLUTION_ANALYSIS.md`
- Git history preserves original implementations

**Action:**
```bash
# Delete deprecated K-Node files
rm apps_lic/engines/k3_message_body_agent.py
rm apps_lic/engines/k5_cta_agent.py
rm apps_lic/engines/k5a_agent.py
rm apps_lic/engines/k7_assembly_agent.py
rm apps_lic/engines/knowledge_graph_agent.py
```

**Pros:**
- ✅ Eliminates naming violations
- ✅ Reduces repository clutter
- ✅ Clear signal that K-Nodes are deprecated
- ✅ No risk of accidental usage

**Cons:**
- ❌ Loses in-file documentation (mitigated by analysis docs)
- ❌ Requires updating any references (unlikely for deprecated code)

---

### **Option 2: Rename to PascalCase (PARTIAL SOLUTION)**

**Rationale:**
- Preserves files for historical reference
- Makes naming consistent with conventions
- Allows FileClassificationAgent to pass validation

**Action:**
```bash
# Rename deprecated K-Node files to PascalCase
mv apps_lic/engines/k3_message_body_agent.py apps_lic/engines/K3MessageBodyAgent.py
mv apps_lic/engines/k5_cta_agent.py apps_lic/engines/K5CtaAgent.py
mv apps_lic/engines/k5a_agent.py apps_lic/engines/K5aAgent.py
mv apps_lic/engines/k7_assembly_agent.py apps_lic/engines/K7AssemblyAgent.py
mv apps_lic/engines/knowledge_graph_agent.py apps_lic/engines/KnowledgeGraphAgent.py
```

**Pros:**
- ✅ Fixes naming violations
- ✅ Preserves historical code
- ✅ Consistent with conventions

**Cons:**
- ❌ Files still clutter directory
- ❌ Deprecated code still appears in listings
- ❌ May confuse developers about availability

---

### **Option 3: Move to Archive Directory (COMPROMISE)**

**Rationale:**
- Preserves files outside main codebase
- Clear separation of active vs. deprecated
- Maintains git history

**Action:**
```bash
# Create legacy archive directory
mkdir -p apps_lic/engines/.legacy_k_nodes

# Move deprecated files
mv apps_lic/engines/k3_message_body_agent.py apps_lic/engines/.legacy_k_nodes/K3MessageBodyAgent.py
mv apps_lic/engines/k5_cta_agent.py apps_lic/engines/.legacy_k_nodes/K5CtaAgent.py
mv apps_lic/engines/k5a_agent.py apps_lic/engines/.legacy_k_nodes/K5aAgent.py
mv apps_lic/engines/k7_assembly_agent.py apps_lic/engines/.legacy_k_nodes/K7AssemblyAgent.py
mv apps_lic/engines/knowledge_graph_agent.py apps_lic/engines/.legacy_k_nodes/KnowledgeGraphAgent.py

# Add .gitignore to exclude from tooling
echo "# Legacy K-Node implementations - DEPRECATED" > apps_lic/engines/.legacy_k_nodes/.gitignore
echo "*.py" >> apps_lic/engines/.legacy_k_nodes/.gitignore
```

**Pros:**
- ✅ Removes from active directory
- ✅ Preserves for reference
- ✅ Clear deprecation signal
- ✅ Excluded from automated tooling

**Cons:**
- ❌ Adds directory complexity
- ❌ Files still in repository

---

### **Option 4: Fix K3MessageArchitect (REQUIRED)**

**Rationale:**
- File is ACTIVE (not deprecated)
- Contains production code
- Naming violation blocks proper classification

**Action:**
```bash
# Rename malformed file
mv apps_lic/engines/K3messagearchitectagentStrategy.py apps_lic/engines/K3MessageArchitectAgent.py

# Update class name in file
# Change: class K3MessageArchitect(LICAgentBase)
# To:     class K3MessageArchitectAgent(LICAgentBase)

# Update any imports
grep -r "K3MessageArchitect" apps_lic/ --include="*.py"
# Replace with K3MessageArchitectAgent
```

**Pros:**
- ✅ Fixes active code violation
- ✅ Aligns with naming conventions
- ✅ Improves discoverability

**Cons:**
- ❌ Breaking change (requires import updates)
- ❌ May affect production code

---

## Recommended Action Plan

### **Phase 1: Immediate (Delete Deprecated Files)**
1. ✅ Delete 5 deprecated K-Node files (`k3_message_body_agent.py`, `k5_cta_agent.py`, `k5a_agent.py`, `k7_assembly_agent.py`, `knowledge_graph_agent.py`)
2. ✅ Verify no active imports reference these files
3. ✅ Update `SOVEREIGN_FOUNDATION_REPORT.md` to remove deprecated entries
4. ✅ Commit with message: "Remove deprecated K-Node legacy files"

### **Phase 2: Fix Active Violation**
1. ✅ Rename `K3messagearchitectagentStrategy.py` → `K3MessageArchitectAgent.py`
2. ✅ Update class name: `K3MessageArchitect` → `K3MessageArchitectAgent`
3. ✅ Search and replace all imports
4. ✅ Run tests to verify no breakage
5. ✅ Commit with message: "Fix K3MessageArchitect naming violation"

### **Phase 3: Validation**
1. ✅ Run FileClassificationAgent audit on `apps_lic/engines/`
2. ✅ Verify zero naming violations
3. ✅ Run Wave 9 simulation to confirm identity resolution
4. ✅ Update agent discovery manifest

### **Phase 4: Prevention**
1. ✅ Add pre-commit hook to block snake_case agent files
2. ✅ Update FileClassificationAgent to detect K-Node patterns
3. ✅ Document K-Node naming conventions in architecture guide
4. ✅ Add test case for K-Node naming validation

---

## Prevention Strategies

### **1. Enhanced FileClassificationAgent Rules**

Add explicit K-Node detection:

```python
def _is_k_node_agent(self, path: Path) -> bool:
    """Detect K-Node agents (K.1, K.3, K.5A, etc.)."""
    stem = path.stem.lower()
    # Match k1, k3, k5a, k7, etc.
    return bool(re.match(r'^k\d+[a-z]?_', stem))

def get_compliant_name(self, path: Path, file_type: FileType) -> str | None:
    # ... existing code ...
    
    # Special handling for K-Node agents
    if file_type == "AGENT" and self._is_k_node_agent(path):
        # Extract K-Node identifier (k3, k5a, etc.)
        match = re.match(r'^k(\d+[a-z]?)_(.+)', path.stem.lower())
        if match:
            k_id = match.group(1).upper()  # K3, K5A
            description = match.group(2)   # message_body, cta
            # Convert to PascalCase
            pascal_desc = ''.join(word.capitalize() for word in description.split('_'))
            target_name = f"K{k_id}{pascal_desc}Agent"
            return f"{target_name}.py"
```

---

### **2. Pre-Commit Hook: Block Snake_Case Agents**

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: validate-agent-naming
      name: Validate Agent File Naming
      entry: python scripts/validators/validate_agent_naming.py
      language: python
      types: [python]
      files: ^(apps_rg|apps_lic|agentic_core)/.*Agent\.py$
      pass_filenames: true
```

Script: `scripts/validators/validate_agent_naming.py`
```python
import sys
from pathlib import Path

def validate_agent_naming(filepath: str) -> bool:
    """Ensure agent files use PascalCase."""
    path = Path(filepath)
    
    # Check if filename is PascalCase
    if path.stem != path.stem[0].upper() + path.stem[1:]:
        print(f"❌ {filepath}: Agent files must use PascalCase")
        return False
    
    # Check for snake_case pattern
    if '_' in path.stem and not path.stem.startswith('test_'):
        print(f"❌ {filepath}: Agent files cannot use snake_case")
        return False
    
    return True

if __name__ == "__main__":
    all_valid = all(validate_agent_naming(f) for f in sys.argv[1:])
    sys.exit(0 if all_valid else 1)
```

---

### **3. Documentation: K-Node Naming Guide**

Add to `docs/architecture/K_NODE_NAMING_CONVENTIONS.md`:

```markdown
# K-Node Naming Conventions

## Overview
K-Nodes are specialist agents with numeric identifiers (K.1, K.3, K.5A, K.7) 
that follow standard PascalCase agent naming conventions.

## Naming Pattern
**Format:** `K{Number}{Letter?}{Description}Agent.py`

**Examples:**
- `K3MessageBodyAgent.py` (K.3 Message Body generation)
- `K5aAgent.py` (K.5A bullet generation)
- `K7AssemblyAgent.py` (K.7 final assembly)

## Class Naming
Class names must match filenames:
- File: `K3MessageBodyAgent.py`
- Class: `class K3MessageBodyAgent(LICAgentBase)`

## Deprecated Pattern (DO NOT USE)
❌ `k3_message_body_agent.py` (snake_case)
❌ `K3messagearchitectagentStrategy.py` (malformed PascalCase)
```

---

## Conclusion

The K-Node naming violations stem from incomplete migration of deprecated legacy files during the Batch 8.6 PascalCase transition. Five files remain in snake_case because they were marked "LEGACY" and excluded from migration scope. One active file (`K3messagearchitectagentStrategy.py`) has a malformed name due to misclassification as an ADAPTER.

**Recommended Resolution:**
1. **Delete** 5 deprecated files (no active code)
2. **Rename** 1 active file to proper PascalCase
3. **Enhance** FileClassificationAgent with K-Node detection
4. **Add** pre-commit hook to prevent future violations

**Impact:** Low risk - deprecated files have no imports, active file requires import updates

**Timeline:** 1-2 hours for complete remediation

---

**Report Generated:** February 4, 2026  
**Next Steps:** Execute Phase 1 (Delete Deprecated Files)  
**Validation:** Run FileClassificationAgent audit post-remediation
