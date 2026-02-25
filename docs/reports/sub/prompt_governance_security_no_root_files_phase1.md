# Prompt Governance Security No-Root-Files Phase 1 Evidence

## Wave 1.1 — Inventory (No Code Changes)

### 1. Current Governed Folder Roots

**FOLDER_PURITY_RULES keys (23):**
reasoning, validators, config, types, utils, scripts, enforcement, dashboards, engines, tools, base_agents, mixins, interfaces, agent_configs, healers, caching, memory, security, golden_evaluation, exceptions, core_kernel

**FOLDER_ALIASES keys (2):**
knowledge -> reasoning, validation -> validators

**INFRASTRUCTURE_PROFILES keys (3):**
runtime, meta_control, policy

**Total governed folder roots: 28**

### 2. Current Root Files Under prompt_governance/security

```
__init__.py (allowed)
injection_detector.py (root file - violation)
output_schema_validator.py (root file - violation)
pii_scrubber.py (root file - violation)
```

Subfolders:
- adversarial/
- utils/ (already contains injection_scan_util.py, normalization_util.py)

### 3. Baseline pytest

Pre-existing failures (not related to this phase)

---

## Wave 1.2 — Implement Global No-Root-Files Invariant (SSOT Engine)

### 1. Implementation in FileClassificationAgent._enforce_folder_purity()

```python
# [GOVERNANCE: GLOBAL NO ROOT FILES INVARIANT]
# Compute the set of governed folder roots:
# 1) Direct keys in FOLDER_PURITY_RULES
# 2) Resolved via FOLDER_ALIASES
# 3) Designated in INFRASTRUCTURE_PROFILES
# For ANY governed folder root, FAIL if any direct child is a file.
is_governed = (
    resolved_folder in FOLDER_PURITY_RULES
    or resolved_folder in INFRASTRUCTURE_PROFILES
    or folder_name in FOLDER_ALIASES
)
if is_governed:
    # This file is directly under a governed folder root => FAIL
    return {"type": "NO_ROOT_FILES_VIOLATION", ...}
```

### 2. Tests Added (5 new tests)

- test_folder_purity_rules_governed
- test_folder_aliases_governed
- test_infrastructure_profiles_governed
- test_security_has_approved_subfolders
- test_global_invariant_covers_all_governed_roots

### 3. Test Results (15 passed)

```
tests/enforcement/test_folder_purity_governance.py - 15 passed in 0.03s
```

---

## Wave 1.3 — Apply to prompt_governance/security (Domain-Pure Remediation)

### 1. Files Moved

```bash
git mv injection_detector.py -> detectors/injection_detector.py
git mv pii_scrubber.py -> detectors/pii_scrubber.py
git mv output_schema_validator.py -> validators/output_schema_validator.py
```

### 2. Created __init__.py files

- `agentic_core/prompt_governance/security/detectors/__init__.py`
- `agentic_core/prompt_governance/security/validators/__init__.py`

### 3. Imports Updated (10 files)

- agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
- agentic_core/prompt_governance/core/governance_hub.py
- agentic_core/prompt_governance/core/prompt_assembler.py
- agentic_core/prompt_governance/security/utils/injection_scan_util.py
- tests/agentic_core/prompt_governance/security/test_injection_detector.py
- tests/agentic_core/prompt_governance/security/test_pii_scrubber.py
- tests/unit/agentic_core/prompt_governance/security/test_injection_normalization_util.py
- tests/unit/agentic_core/prompt_governance/security/test_injection_signatures_v2.py
- tests/unit/agentic_core/prompt_governance/security/test_injection_wiring_non_fenced_joinpoints.py
- tests/unit/agentic_core/prompt_governance/security/test_output_schema_validation_gate.py

### 4. Verification: prompt_governance/security root contains directories only

```
__init__.py (allowed)
adversarial/
detectors/
utils/
validators/
```

### 5. rg proof: No remaining old import paths

```
grep "prompt_governance\.security\.(injection_detector|pii_scrubber|output_schema_validator)" -> No results found
```

### 6. Test Results (15 passed)

```
tests/enforcement/test_folder_purity_governance.py - 15 passed in 0.03s
```
