# L6 Void Compliance Enforcement Strategy

## 🎯 **Objective**

Enforce logical folder separation in the 50-key canon validation system to ensure:
1. Files only exist in **ALLOWED_ROOT_FOLDERS**
2. Canon keys are **scoped to specific folders**
3. Agents only check **relevant keys** based on file location
4. **Forbidden folders** (archives, data, cache) are excluded from validation

---

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    L6 RUNTIME LAYER                         │
│              (Self-Maintenance & Compliance)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  void_compliance.py                                         │
│  ├── ALLOWED_ROOT_FOLDERS (10 approved folders)            │
│  ├── FORBIDDEN_ROOT_FOLDERS (out-of-scope folders)         │
│  ├── KEY_TO_FOLDER_MAP (51 key → folder mappings)          │
│  └── Enforcement Functions:                                │
│      • validate_file_location()                            │
│      • get_applicable_keys_for_file()                      │
│      • enforce_void_compliance()                           │
│      • get_folder_scope_summary()                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  canon_validator_agentic_v2.py                             │
│  ├── Import L6 runtime components                          │
│  ├── Filter files by ALLOWED_ROOT_FOLDERS                  │
│  ├── Determine applicable keys per file                    │
│  ├── Store keys in ctx.current_file_applicable_keys        │
│  └── Agents filter checks based on applicable keys         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **Folder-to-Key Mapping**

### **Keys 0-10: Global Configuration (THE LAW)**
**Folder:** `config/`
- Environment variables (`.env`, `.env.production`)
- Mission defaults (token caps, line limits)
- Model registry (Gemini/Claude configs)

### **Keys 11-30: Agent Governance (THE LAW - Partitioned Prompts)**
**Folders:** `prompt_governance/personas/` (Keys 11-20), `prompt_governance/instructions/` (Keys 21-30)
- Agent personality prompts (`.md` files)
- Task-specific directives
- "The Surgeon" prompt for ArchitectureGovernor

### **Keys 31-50: Data Contracts & Schemas (THE CONTRACTS)**
**Folders:** `schemas/canon/` (31-33), `schemas/validation/` (34-36), `schemas/events/` (37-39)
- Fission blueprint schemas
- Validation report formats
- Signal bus event schemas

### **Keys 40-42: Core Architecture (THE BRAIN)**
**Folder:** `agentic_core/` (all L1-L5 layers)
- Key 40: Architecture checks (depth, nesting)
- Key 41: Atomicity checks (file size, LOC)
- Key 42: Complexity checks (cyclomatic, cognitive)

### **Keys 43-45: Application Code (TARGET DOMAINS)**
**Folders:** `apps_shared/`, `apps_rg/`, `apps_lic/`
- Domain-specific business logic
- Application orchestrators
- Fission output (`*_modules/`)

### **Keys 46-50: Infrastructure & Telemetry**
- Key 46: `scripts/` (deployment, maintenance)
- Key 47: `tests/` (unit, integration, e2e)
- Keys 48-50: `observability/` (logs, metrics, traces)

---

## 🛡️ **Enforcement Mechanisms**

### **1. File Discovery Filter (Pre-Validation)**

```python
# In canon_validator_agentic_v2.py
discovered_files = [p for p in target_path.rglob("*.py") if p.is_file()]

# === L6 RUNTIME: Void Compliance Enforcement ===
valid_files, violations = enforce_void_compliance(discovered_files, project_root_path)

if violations:
    print(f"⚠️  [VOID COMPLIANCE] {len(violations)} files in forbidden/unknown folders")
    for file_path, reason in violations[:5]:
        print(f"   [X] {file_path.name}: {reason}")
```

**Result:** Files in `archives/`, `data/`, `cache/`, etc. are **excluded** from validation.

---

### **2. Key-to-File Mapping (Per-File Routing)**

```python
# In canon_validator_agentic_v2.py (main loop)
for idx, file_path in enumerate(ctx.python_files, 1):
    file_path_obj = Path(file_path)

    # === L6 RUNTIME: Determine Applicable Keys ===
    applicable_keys = get_applicable_keys_for_file(file_path_obj, project_root_path)

    print(f"🔍 [{idx}/{total}] {file_name} [Keys: {sorted(applicable_keys)}]")
```

**Example Output:**
```
🔍 [1/13] safety_guardrail.py [Keys: [40, 41, 42]]  # agentic_core/L5_safety
🔍 [2/13] mission_defaults.yaml [Keys: [0, 1, 2]]   # config/
🔍 [3/13] main.py [Keys: [43, 44, 45]]              # apps_rg/
```

---

### **3. Agent-Level Key Filtering (Selective Validation)**

```python
# In canon_validator_agentic_v2.py (agent execution)
# Store applicable keys in context for agents to filter
ctx.current_file_applicable_keys = applicable_keys

for agent in file_validators:
    # Agent can check: if key_num in ctx.current_file_applicable_keys
    await agent.execute(file_path)
```

**Agent Implementation Example:**
```python
# In agentic_core/agents/governance.py
class ArchitectureGovernor:
    async def execute(self, file_path: str):
        # Check if this file should be validated for architecture keys
        applicable_keys = getattr(self.ctx, 'current_file_applicable_keys', set())

        # Keys 40-42 are architecture-related
        if not applicable_keys or any(k in [40, 41, 42] for k in applicable_keys):
            # Run architecture checks
            self._check_depth(file_path)
            self._check_atomicity(file_path)
            self._check_complexity(file_path)
        else:
            # Skip - not applicable to this file's location
            pass
```

---

## 📊 **Folder Scope Summary**

The validator prints a distribution summary at startup:

```
[SCOPE] Folder distribution:
   • agentic_core: 221 files
   • apps_shared: 45 files
   • apps_rg: 38 files
   • apps_lic: 32 files
   • config: 12 files
   • prompt_governance: 8 files
   • schemas: 15 files
   • scripts: 24 files
   • tests: 67 files
   • observability: 19 files
```

---

## 🚫 **Forbidden Folders (Auto-Excluded)**

```python
FORBIDDEN_ROOT_FOLDERS = {
    "data",           # Static assets (out of scope)
    "archives",       # Deprecated code (out of scope)
    "cache",          # Temporary files
    ".git",           # Version control
    ".venv", "venv",  # Virtual environments
    "__pycache__",    # Python cache
    ".pytest_cache",  # Test cache
    ".ruff_cache",    # Linter cache
    "node_modules",   # JS dependencies
}
```

**Violation Output:**
```
⚠️  [VOID COMPLIANCE] 3 files in forbidden/unknown folders:
   [X] old_validator.py: VOID VIOLATION: File in forbidden folder 'archives' (out of scope)
   [X] test_data.json: VOID VIOLATION: File in forbidden folder 'data' (out of scope)
   [X] cached_result.py: VOID VIOLATION: File in forbidden folder 'cache' (out of scope)
```

---

## 🎯 **Benefits**

### **1. Logical Separation**
- Configuration keys (0-10) only check `config/` files
- Prompt keys (11-30) only check `prompt_governance/` files
- Schema keys (31-39) only check `schemas/` files
- Architecture keys (40-42) check all `agentic_core/` files

### **2. Performance Optimization**
- Agents skip irrelevant files (e.g., don't check config files for architecture violations)
- Reduces unnecessary API calls to Gemini
- Faster validation cycles

### **3. Maintainability**
- Single source of truth: `KEY_TO_FOLDER_MAP`
- Easy to add new folders or keys
- Clear separation of concerns

### **4. Security**
- Prevents validation of sensitive files in `data/` or `archives/`
- Path traversal protection (L5 safety layer)
- Containment within `ALLOWED_ROOT_FOLDERS`

---

## 🔧 **Usage**

### **Run Validator with Enforcement**
```powershell
$env:PYTHONUTF8=1
python apps_shared/canon_validator_agentic_v2.py --target agentic_core
```

### **Expected Output**
```
[*] MISSION START: Validating agentic_core
   [OK] SubAtomicEngine active (Model: gemini-2.5-flash)
   [OK] SafetyGuardrail active (Limit: 110 lines)
   [OK] Context hardened: 221 Python files in 10 allowed folders
   [SCOPE] Folder distribution:
      • agentic_core: 221 files
   [L3] Orchestration: 7 validators, 2 monitors
   [>] Starting Linear Execution Sweep...

🔍 [1/221] action_node.py (351 LOC) [Keys: [40, 41, 42]]
⚠️  [FISSION TRIGGER] action_node.py (351 lines). Engaging Auto-Fission.
...
```

---

## 📚 **Files Modified**

1. **`agentic_core/runtime/void_compliance.py`** (NEW)
   - 200 lines
   - Defines ALLOWED_ROOT_FOLDERS, KEY_TO_FOLDER_MAP
   - Implements enforcement functions

2. **`agentic_core/runtime/__init__.py`** (NEW)
   - 15 lines
   - Exports L6 runtime components

3. **`apps_shared/canon_validator_agentic_v2.py`** (MODIFIED)
   - Added L6 runtime imports
   - Added void compliance filtering (lines 132-150)
   - Added key-to-file mapping (lines 221-230)
   - Added context key storage (line 277)

---

## 🚀 **Next Steps**

1. **Agent Updates**: Modify each agent to check `ctx.current_file_applicable_keys` before running validations
2. **Testing**: Run full validation on `agentic_core` to verify key filtering works
3. **Documentation**: Update agent documentation to explain key-based filtering
4. **Monitoring**: Add metrics to track key-specific violation rates

---

## 📖 **References**

- **L1-L5 Architecture**: See `docs/architecture/L1_L5_LAYERS.md`
- **Canon Keys**: See `schemas/canon/50_KEY_SPECIFICATION.md`
- **Fission Protocol**: See `docs/architecture/ATOMIC_FISSION_PROTOCOL.md`
