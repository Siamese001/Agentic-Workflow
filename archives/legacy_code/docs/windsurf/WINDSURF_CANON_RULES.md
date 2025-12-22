# Windsurf Canon Enforcement Rules

## 🎯 **Overview**

This document defines the hardened enforcement rules for Windsurf AI to maintain the 50-Key Canon Folder Mapping Specification with **Zero-Loss Merge** integrity.

---

## 🛡️ **Core Mandates**

### **1. Key-to-Folder Integrity**

**Rule:** Every file's location must strictly match its assigned Key (0-50).

**Enforcement:**
- Before editing or moving any file, determine applicable keys via `get_applicable_keys_for_file()`
- If a file's logic spans multiple keys, trigger **L3 Fission Event** to split it
- Never merge logic from different keys into a single file

**Example Violations:**
- ❌ Mixing Key 21 (Instructional) with Key 24 (Negative) prompts in one file
- ❌ Placing config logic (Keys 0-10) in `agentic_core/` (Keys 40-42)

---

### **2. Sovereign Directory Protection**

**Rule:** Directories `agentic_core/`, `prompt_governance/`, and `schemas/` are Sovereign and must maintain strict 3-level depth.

**Enforcement:**
- Max depth: `[L1] Root → [L2] Category → [L3] Function → [FILE]`
- Any single-child subfolders must be flattened
- Sovereign directories NEVER import from `apps_*`

**Example Structure:**
```
✅ CORRECT:
agentic_core/L5_safety/guardrails/zero_loss_monitor.py

❌ WRONG (4 levels):
agentic_core/L5_safety/guardrails/monitors/zero_loss_monitor.py

❌ WRONG (single-child):
agentic_core/L5_safety/guardrails/
  └── monitors/ (only contains one file)
```

---

### **3. The Anti-Single-Child Rule (L6 Compliance)**

**Rule:** Any L2 or L3 folder containing only one sub-item must be collapsed into its parent to maintain flat-velocity.

**Enforcement:**
- Run `check_single_child_violations()` during validation
- Auto-flatten detected violations
- Use descriptive filenames instead of nested folders

**Example Fix:**
```
❌ BEFORE (Nested Void):
prompt_governance/logic/negative/
  └── constraints.md (only file)

✅ AFTER (Flattened):
prompt_governance/logic/negative_constraints.md
```

---

### **4. Import Waterfall Rule (Key 40 Critical)**

**Rule:** Strictly enforce the Dependency Waterfall. Reverse imports trigger a **Critical Key 40 violation**.

**Waterfall Hierarchy:**
```
Sovereign (Top)
  ├── agentic_core/     → Can import: NOTHING from apps
  ├── prompt_governance/ → Can import: NOTHING from apps
  └── schemas/          → Can import: NOTHING from apps

Application Layer (Middle)
  └── apps_shared/      → Can import: agentic_core, schemas

Domain Layer (Bottom)
  ├── apps_rg/          → Can import: agentic_core, schemas, apps_shared
  └── apps_lic/         → Can import: agentic_core, schemas, apps_shared
```

**Enforcement:**
- Run `check_import_waterfall_violations()` on all Python files
- Block commits with sovereign → apps imports
- Report as **CRITICAL Key 40 violation**

**Example Violations:**
```python
# ❌ CRITICAL VIOLATION in agentic_core/L5_safety/guardrail.py
from apps_shared.signal_bus import EventBus  # FORBIDDEN

# ✅ CORRECT in apps_rg/agents/resume_architect.py
from agentic_core.L5_safety import SafetyGuardrail  # ALLOWED
```

---

### **5. UTF-8 Global Standard**

**Rule:** All file operations must enforce `encoding='utf-8'` and `errors='replace'`.

**Enforcement:**
- File reads: `open(path, 'r', encoding='utf-8', errors='replace')`
- File writes: `open(path, 'w', encoding='utf-8', errors='ignore')`
- Prevents crashes on invalid UTF-8 sequences

---

### **6. Fission Threshold Enforcement**

**Rule:** If a Python file exceeds 200 lines, trigger an **L3 Fission Event**.

**Enforcement:**
- Monitor file length on save
- Suggest fission via `FissionManager`
- Move extracted sub-modules to `apps_*/core_modules/fission/`
- Update all imports with UTF-8 integrity

**Example:**
```
File: apps_rg/core/resume_parser.py (350 lines)
Action: Split into:
  - apps_rg/core/resume_parser.py (router, 50 lines)
  - apps_rg/core_modules/fission/pdf_extractor.py (150 lines)
  - apps_rg/core_modules/fission/text_cleaner.py (150 lines)
```

---

### **7. Negative Logic Isolation (Keys 24-25)**

**Rule:** Constraint-based prompts must be physically separated from instructional prompts to prevent "Context Drowning."

**Enforcement:**
- Instructional prompts → `prompt_governance/logic/instructional/` (Keys 21-23)
- Negative constraints → `prompt_governance/logic/negative/` (Keys 24-25)
- Never merge these in the same file

**Rationale:** AI agents fail when positive directives conflict with negative constraints in the same context window.

---

### **8. Void Enforcement (Keys 0-10)**

**Rule:** Files must only exist in the 12 Approved Root Folders. Anything else is "The Void."

**Approved Root Folders (ONLY 12):**
1. `agentic_core/`
2. `prompt_governance/`
3. `schemas/`
4. `apps_shared/`
5. `apps_rg/`
6. `apps_lic/`
7. `config/`
8. `observability/`
9. `scripts/`
10. `tests/`
11. `data/` (out of scope, static only)
12. `archives/` (out of scope, legacy only)

**❌ FORBIDDEN:** Any folder with numerical prefix (`01_*`, `02_*`, `03_*`, etc.) is **NOT APPROVED**. These were temporary Light Canon workarounds and must be migrated to approved folders.

**Enforcement:**
- Detect `.py` files in `data/` or `archives/`
- Raise **Critical Key 0 violation**
- Move to appropriate folder:
  - Core logic → `agentic_core/L2_execution/tools/`
  - App logic → `apps_*/core/`

---

## 🧬 **Validation Checks**

### **Pre-Commit Checks**

Run these before allowing any commit:

1. **Void Compliance**: `enforce_void_compliance(files, project_root)`
2. **Single-Child Detection**: `check_single_child_violations(project_root)`
3. **Import Waterfall**: `check_import_waterfall_violations(file, project_root)`
4. **Key Mapping**: `get_applicable_keys_for_file(file, project_root)`
5. **Fission Threshold**: Check LOC < 200 for all Python files

### **Runtime Checks**

During canon validator execution:

1. Filter files by `ALLOWED_ROOT_FOLDERS`
2. Map files to applicable keys
3. Store keys in `ctx.current_file_applicable_keys`
4. Agents validate only applicable keys
5. Report violations by key and folder

---

## 📊 **Hardening Additions to 50-Key Spec**

| Key Area | Hardening Change | Rationale |
|----------|------------------|-----------|
| **Keys 40-42** | Add **Import Sentinel** check | Prevents architectural "entanglement" where core logic depends on apps |
| **Key 46** | Add **Idempotency** check | Ensures maintenance scripts don't break structure if run twice |
| **Keys 24-25** | Add **Contradiction Check** | AI agents fail when instructional (Key 21) conflicts with negative (Key 24) |
| **All Keys** | Add **Single-Child Detection** | Prevents "Nested Void" antipattern that reduces flat-velocity |

---

## 🛠️ **Windsurf Integration**

### **Auto-Healing Behaviors**

Windsurf is authorized to:

1. **Auto-Flatten**: Collapse single-child directories automatically
2. **Import Blocking**: Prevent sovereign → apps imports at edit time
3. **Fission Suggestion**: Prompt for file splitting when LOC > 200
4. **Void Migration**: Move misplaced files to correct folders

### **Forbidden Actions**

Windsurf must NEVER:

1. Create files in project root (except Sacred Root files)
2. Merge different key ranges into one file
3. Import from apps in sovereign directories
4. Create folders deeper than L3
5. Delete logic without fission backup

---

## 📚 **Reference Implementation**

### **Key Mapper Function**

```python
def get_applicable_keys_for_file(file_path: Path, project_root: Path) -> Set[int]:
    """
    SSOT: Maps file paths to the 50-Key Canon Specification.
    Enforces architectural boundaries and validation scope.
    """
    # Implementation in agentic_core/runtime/void_compliance.py
```

### **Validation Functions**

```python
# Check single-child violations
violations = check_single_child_violations(project_root)

# Check import waterfall violations
violations = check_import_waterfall_violations(file_path, project_root)

# Enforce void compliance
valid_files, violations = enforce_void_compliance(files, project_root)
```

---

## 🎯 **Success Criteria**

A project is **Canon-Compliant** when:

1. ✅ All files in `ALLOWED_ROOT_FOLDERS`
2. ✅ No single-child directories
3. ✅ No sovereign → apps imports
4. ✅ All files < 200 LOC (or fissioned)
5. ✅ Max 3-level depth in all folders
6. ✅ Files mapped to correct keys
7. ✅ Negative logic isolated from instructional
8. ✅ UTF-8 encoding enforced globally

---

## 🚀 **Usage**

### **For Windsurf AI**

Before any file operation:
1. Check applicable keys
2. Verify folder compliance
3. Check import waterfall
4. Validate depth and single-child rules
5. Proceed only if all checks pass

### **For Developers**

Run validation:
```powershell
python apps_shared/canon_validator_agentic_v2.py --target agentic_core
```

Check compliance:
```python
from agentic_core.runtime import (
    check_single_child_violations,
    check_import_waterfall_violations,
)

# Check structure
violations = check_single_child_violations(Path("c:/Git/Agentic-Workflow"))
print(f"Single-child violations: {len(violations)}")

# Check imports
violations = check_import_waterfall_violations(
    Path("c:/Git/Agentic-Workflow/agentic_core/L5_safety/guardrail.py"),
    Path("c:/Git/Agentic-Workflow")
)
print(f"Import violations: {violations}")
```

---

## 📖 **Related Documentation**

- **50-Key Specification**: `docs/architecture/50_KEY_FOLDER_MAPPING.md`
- **L6 Enforcement**: `docs/architecture/L6_VOID_COMPLIANCE_ENFORCEMENT.md`
- **Implementation**: `agentic_core/runtime/void_compliance.py`
- **Validator**: `apps_shared/canon_validator_agentic_v2.py`
