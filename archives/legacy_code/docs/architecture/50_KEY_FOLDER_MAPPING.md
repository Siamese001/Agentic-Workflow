# 50-Key Canon Folder Mapping Specification

## 🎯 **Overview**

This document defines the canonical mapping between the 50 validation keys and the project's folder structure, enforcing logical separation and scope boundaries.

**Hardening Status:** This specification includes L6 runtime enforcement with anti-single-child detection, import waterfall validation, and self-validation priority for sovereign directories.

**⚠️ CRITICAL:** Only the **12 Approved Root Folders** listed below are valid. Any folder with a numerical prefix (e.g., `01_`, `02_`, etc.) is **NOT APPROVED** and will be rejected by void compliance enforcement.

---

## 🛡️ **Hardening Rules**

### **1. Anti-Single-Child Rule (L6 Compliance)**

**Rule:** Any L2 or L3 folder containing only one sub-item must be collapsed into its parent to maintain flat-velocity.

**Enforcement:** `check_single_child_violations()` detects and reports these violations during validation.

**Example:**
```
❌ VIOLATION: prompt_governance/logic/negative/ contains only constraints.md
✅ CORRECT: prompt_governance/logic/negative_constraints.md
```

### **2. Import Waterfall Rule (Key 40 Critical)**

**Rule:** Strictly enforce the Dependency Waterfall. Sovereign directories (agentic_core, prompt_governance, schemas) must NEVER import from apps_*.

**Waterfall:**
- Sovereign → Can import: NOTHING from apps
- apps_shared → Can import: agentic_core, schemas
- apps_rg/apps_lic → Can import: agentic_core, schemas, apps_shared

**Enforcement:** `check_import_waterfall_violations()` scans Python files for forbidden imports.

**Violation Example:**
```python
# ❌ CRITICAL in agentic_core/L5_safety/guardrail.py
from apps_shared.signal_bus import EventBus  # FORBIDDEN
```

### **3. Self-Validation Priority (Keys 40-42)**

**Rule:** The Brain (agentic_core) has "Self-Validation" priority. The validator must validate itself before validating apps domains.

**Enforcement:** Run canon validator on `agentic_core/` first in CI/CD pipelines.

---

## 📋 **Complete Key-to-Folder Mapping**

### **Keys 0-10: Global Configuration (THE SETTINGS)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 0 | `config/` | Root configuration | `.env`, `pyproject.toml` |
| 1 | `config/models/` | Model configurations | `gemini_params.yaml`, `model_router.json` |
| 2 | `config/policy/` | Policy configurations | `token_budgets.yaml`, `fission_rules.yaml` |
| 3-10 | `config/` | General configuration | Various config files |

**Validation Focus:**
- Environment variable completeness
- Configuration schema validation
- Model parameter bounds
- Policy constraint enforcement

---

### **Keys 11-20: Agent Personas (THE LAW - Identity/Soul)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 11 | `prompt_governance/personas/architectural/` | Architectural agent personas | `key_11_surgeon.md`, `architect_persona.md` |
| 12 | `prompt_governance/personas/operational/` | Operational agent personas | `key_12_janitor.md`, `healer_persona.md` |
| 13 | `prompt_governance/personas/architectural/` | Architectural personas | Additional architect variants |
| 14 | `prompt_governance/personas/operational/` | Operational personas | Additional operational variants |
| 15-20 | Alternating architectural/operational | Agent identity definitions | Persona markdown files |

**Validation Focus:**
- Persona consistency (voice, tone, constraints)
- Role boundary enforcement
- Capability declarations
- Behavioral constraints

---

### **Keys 21-25: Instructional Logic (THE LAW - Task Directives)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 21-23 | `prompt_governance/logic/instructional/` | Positive directives | `task_directives.md`, `workflow_logic.md` |
| 24-25 | `prompt_governance/logic/negative/` | Negative constraints | `constraints.md`, `exclusion_list.md` |

**Validation Focus:**
- Instruction clarity and completeness
- Constraint non-contradiction
- Directive scope boundaries
- Exclusion list coverage

---

### **Keys 26-30: Security Prompts (THE LAW - Shield/Guardrails)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 26-27 | `prompt_governance/security/defensive/` | Defensive security | `system_integrity.md`, `safety_rules.md` |
| 28-29 | `prompt_governance/security/injections/` | Adversarial testing | `jailbreak_tests.md`, `adversarial_cases.md` |
| 30 | `prompt_governance/security/defensive/` | Additional defensive rules | Security policies |

**Validation Focus:**
- Injection pattern detection
- Safety rule completeness
- Adversarial case coverage
- Defense mechanism integrity

---

### **Keys 31-35: Canon Schemas (THE CONTRACTS - Mission Contracts)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 31-32 | `schemas/canon/blueprints/` | Fission blueprints | `fission_blueprint.json`, `module_map.py` |
| 33-34 | `schemas/canon/reports/` | Validation reports | `validation_report.json`, `audit_log.py` |
| 35 | `schemas/canon/` | General canon schemas | Root canon definitions |

**Validation Focus:**
- Blueprint schema compliance
- Report format validation
- Contract versioning
- Data structure integrity

---

### **Keys 36-39: API Schemas (THE CONTRACTS - Communication Contracts)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 36-37 | `schemas/api/internal/` | Internal communication | `bus_events.py`, `inter_agent_msg.py` |
| 38-39 | `schemas/api/external/` | External interfaces | `tool_spec_v1.json`, `openai_schema.py` |

**Validation Focus:**
- API contract versioning
- Message schema validation
- Event bus integrity
- External interface compliance

---

### **Keys 40-42: Core Architecture (THE BRAIN - All L1-L5 Layers)**

| Key | Folder Path | Purpose | Validation Type |
|-----|-------------|---------|-----------------|
| 40 | `agentic_core/` | Architecture checks | Depth, nesting, hierarchy |
| 41 | `agentic_core/` | Atomicity checks | File size, LOC, modularity |
| 42 | `agentic_core/` | Complexity checks | Cyclomatic, cognitive complexity |

**Applies to ALL L1-L5 subfolders:**
- `agentic_core/L1_cognition/`
- `agentic_core/L2_execution/`
- `agentic_core/L3_orchestration/`
- `agentic_core/L4_state/`
- `agentic_core/L5_safety/`
- `agentic_core/runtime/` (L6)

**Validation Focus:**
- Max depth: 3 levels (Light Canon)
- Max LOC: 200 lines per file
- Cyclomatic complexity thresholds
- Cognitive complexity bounds
- **Import Waterfall**: No sovereign → apps imports (CRITICAL)
- **Single-Child Detection**: No folders with only one item

---

### **Keys 43-45: Application Code (TARGET DOMAINS)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 43 | `apps_shared/`, `apps_rg/`, `apps_lic/` | Application core logic | `signal_bus.py`, `pdf_parser.py` |
| 44 | `apps_shared/`, `apps_rg/`, `apps_lic/` | Application agents | `resume_architect.py`, `post_specialist.py` |
| 45 | `apps_shared/`, `apps_rg/`, `apps_lic/` | Application utilities | `text_cleaner.py`, `token_counter.py` |

**Validation Focus:**
- Domain-specific logic isolation
- Agent role clarity
- Utility function atomicity
- Cross-app code reuse patterns

---

### **Key 46: Execution Utilities (THE LABOR)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 46 | `scripts/` | Operational tooling | `cleanup_backups.py`, `setup_env.ps1` |

**Applies to subfolders:**
- `scripts/maintenance/`
- `scripts/deployment/`

**Validation Focus:**
- Script idempotency
- Error handling completeness
- Dependency declarations
- Platform compatibility

---

### **Key 47: Test Coverage (QA)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 47 | `tests/` | Functional verification | All test files |

**Applies to subfolders:**
- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`
- `tests/adversarial/`

**Validation Focus:**
- Test coverage thresholds
- Assertion quality
- Fixture integrity
- Test isolation

---

### **Keys 48-50: Telemetry (THE TELEMETRY)**

| Key | Folder Path | Purpose | Example Files |
|-----|-------------|---------|---------------|
| 48 | `observability/logs/` | Execution traces | `execution_trace.log`, `error_stack.txt` |
| 49 | `observability/metrics/` | Performance metrics | `token_usage.csv`, `latency_stats.json` |
| 50 | `observability/` | General observability | Root telemetry files |

**Validation Focus:**
- Log format consistency
- Metric schema validation
- Trace completeness
- PII redaction in logs

---

## 🏗️ **Folder Hierarchy Specification**

### **L1-L3 Depth Structure**

```
[L1] Root Folder (e.g., agentic_core/)
  └── [L2] Category Folder (e.g., L1_cognition/)
      └── [L3] Functional Folder (e.g., planning/)
          └── [FILES] Implementation files (e.g., dag_generator.py)
```

**Light Canon Rule:** Max 3 levels deep for non-sovereign directories.

**Sovereign Directories** (exempt from depth limit):
- `agentic_core/`
- `apps_lic/`, `apps_rg/`, `apps_shared/`
- `schemas/`, `prompt_governance/`
- `observability/`, `config/`
- `data/`, `archives/`

---

## 📊 **Detailed Subfolder Breakdown**

### **agentic_core/ (THE BRAIN)**

```
agentic_core/
├── L1_cognition/              # [L2] High-level strategy
│   ├── planning/              # [L3] DAG generation, task decomposition
│   └── reflection/            # [L3] Critique, healing logic
├── L2_execution/              # [L2] Tool & Engine logic
│   ├── engines/               # [L3] Pydantic sanitizer, IO wrapper
│   └── tools/                 # [L3] Git sentinel, search orchestrator
├── L3_orchestration/          # [L2] Mission Workflow
│   ├── workflows/             # [L3] Swarm scheduler, mission runner
│   └── fission/               # [L3] Complexity analyzer, split executor
├── L4_state/                  # [L2] Context & Memory
│   ├── context/               # [L3] Omni context, validation context
│   └── persistence/           # [L3] SQLite checkpoint, genealogy logger
├── L5_safety/                 # [L2] Guardrails & Security
│   ├── guardrails/            # [L3] Zero-loss monitor, line limit guard
│   └── security/              # [L3] PII redactor, injection classifier
└── runtime/                   # [L2] L6: Self-Maintenance
    ├── compliance/            # [L3] Void compliance, hierarchy linter
    └── automation/            # [L3] Backup rotator, env validator
```

### **prompt_governance/ (THE LAW)**

```
prompt_governance/
├── personas/                  # [L2] Identity/Soul
│   ├── architectural/         # [L3] Surgeon, Architect personas
│   └── operational/           # [L3] Janitor, Healer personas
├── logic/                     # [L2] Instruction Types
│   ├── instructional/         # [L3] Task directives, workflow logic
│   └── negative/              # [L3] Constraints, exclusion lists
└── security/                  # [L2] Shield/Guardrails
    ├── defensive/             # [L3] System integrity, safety rules
    └── injections/            # [L3] Jailbreak tests, adversarial cases
```

### **schemas/ (THE CONTRACTS)**

```
schemas/
├── canon/                     # [L2] Mission contracts
│   ├── blueprints/            # [L3] Fission blueprints, module maps
│   └── reports/               # [L3] Validation reports, audit logs
└── api/                       # [L2] Communication contracts
    ├── internal/              # [L3] Bus events, inter-agent messages
    └── external/              # [L3] Tool specs, OpenAI schemas
```

### **tests/ (QA)**

```
tests/
├── unit/                      # [L2] Atomic Isolated Tests
│   ├── core/                  # [L3] Core component tests
│   └── apps/                  # [L3] Application tests
├── integration/               # [L2] Component Interplay Tests
│   ├── scenarios/             # [L3] Integration scenarios
│   └── fixtures/              # [L3] Mock data, VCR cassettes
├── e2e/                       # [L2] Full System Missions
│   ├── resume_workflow/       # [L3] RG pipeline tests
│   └── lic_workflow/          # [L3] LIC post cycle tests
└── adversarial/               # [L2] Security & Safety Testing
    ├── injections/            # [L3] Jailbreak, prompt leak tests
    └── zero_loss/             # [L3] Deletion prevention tests
```

---

## 🛡️ **Enforcement Mechanism**

### **Runtime Validation Flow**

1. **File Discovery**: Scan target scope for Python files
2. **Void Compliance**: Filter by `ALLOWED_ROOT_FOLDERS`
3. **Key Mapping**: Determine applicable keys via `get_applicable_keys_for_file()`
4. **Agent Filtering**: Agents check `ctx.current_file_applicable_keys`
5. **Selective Validation**: Only run checks for applicable keys

### **Example Enforcement**

```python
# File: agentic_core/L5_safety/guardrails/zero_loss_monitor.py
# Location: agentic_core/L5_safety/guardrails/
# Applicable Keys: [40, 41, 42] (Architecture, Atomicity, Complexity)

# File: prompt_governance/personas/architectural/key_11_surgeon.md
# Location: prompt_governance/personas/architectural/
# Applicable Keys: [11] (Architectural Personas)

# File: schemas/canon/blueprints/fission_blueprint.json
# Location: schemas/canon/blueprints/
# Applicable Keys: [31, 32] (Canon Blueprints)
```

---

## 📖 **Usage Guidelines**

### **For Developers**

1. **Placement**: Consult this mapping before creating new files
2. **Validation**: Run canon validator to verify compliance
3. **Refactoring**: Use key mappings to guide file migrations

### **For Agents**

1. **Key Filtering**: Check `ctx.current_file_applicable_keys` before validation
2. **Scope Awareness**: Only validate keys relevant to file location
3. **Reporting**: Include applicable keys in violation reports

### **For Validators**

1. **Pre-Flight**: Verify folder structure matches specification
2. **Runtime**: Enforce key-to-folder mappings dynamically
3. **Post-Mission**: Report violations by key and folder

---

## 🔧 **Maintenance**

### **Adding New Keys**

1. Update `KEY_TO_FOLDER_MAP` in `agentic_core/runtime/void_compliance.py`
2. Update this documentation
3. Add validation logic to relevant agents
4. Update tests to cover new key

### **Adding New Folders**

1. Determine appropriate L1/L2/L3 level
2. Update `ALLOWED_ROOT_FOLDERS` if L1
3. Map to existing keys or create new keys
4. Update folder hierarchy diagrams

### **Deprecating Keys**

1. Mark as deprecated in `KEY_TO_FOLDER_MAP`
2. Add migration path in documentation
3. Update agents to skip deprecated keys
4. Remove after grace period

---

## 📚 **References**

- **Enforcement Implementation**: `agentic_core/runtime/void_compliance.py`
- **Validator Integration**: `apps_shared/canon_validator_agentic_v2.py`
- **Architecture Overview**: `docs/architecture/L6_VOID_COMPLIANCE_ENFORCEMENT.md`
- **Light Canon Rule**: `docs/architecture/LIGHT_CANON_SPECIFICATION.md`
