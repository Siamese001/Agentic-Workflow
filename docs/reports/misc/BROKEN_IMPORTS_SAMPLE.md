# Sample of Broken Imports (5 Representative Files)

**Total Broken Imports:** 212 files across 197 Python modules
**Pattern:** All import from `agentic_core.observability.SovereignBaseAgent`
**Required Fix:** Change to `agentic_core.base_agents.SovereignBaseAgent`

---

## Sample File 1: L5 Safety Validator (HierarchyAgent)

**File:** `agentic_core/L5_safety/validators/HierarchyAgent.py`
**Line:** 7
**Category:** Core L5 Safety Agent

### Current (Broken):
```python
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
```

### Corrected:
```python
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
```

### Context:
```python
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, prompt, state, workflow
from __future__ import annotations
# This boosts alignment detection — review and integrate appropriately

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent  # ❌ BROKEN

from dataclasses import dataclass

"""
HierarchyAgent - Unified Hierarchy Management
Consolidates HierarchyEnforcerAgent and HierarchyHealerAgent into a single agent.
```

---

## Sample File 2: L5 Safety Validator (LocationAgent)

**File:** `agentic_core/L5_safety/validators/LocationAgent.py`
**Line:** 2
**Category:** Core L5 Safety Agent

### Current (Broken):
```python
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
```

### Corrected:
```python
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
```

### Context:
```python
from __future__ import annotations
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent  # ❌ BROKEN

"""
LocationAgent: Sovereign territorial gatekeeper (Canon Key 6 territory)

Enforces:
- Root folder whitelist (from ROOT_WHITELIST)
- Exact depth per sovereign root (SOVEREIGN_REGISTRY['depth'])
- Forbidden root folders and numbered patterns
```

---

## Sample File 3: L1 Cognition Base Agent

**File:** `agentic_core/L1_cognition/thought_engine/L1CognitionBase.py`
**Lines:** 18-20
**Category:** Layer Base Agent

### Current (Broken):
```python
from agentic_core.observability.SovereignBaseAgent import (
    SovereignBaseAgent,  # NEW: Root inheritance
)
```

### Corrected:
```python
from agentic_core.base_agents.SovereignBaseAgent import (
    SovereignBaseAgent,  # NEW: Root inheritance
)
```

### Context:
```python
import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L1_cognition.thought_engine.validation_protocol import ValidationProtocol

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.observability.SovereignBaseAgent import (  # ❌ BROKEN
    SovereignBaseAgent,  # NEW: Root inheritance
)
```

---

## Sample File 4: L6 Observability Agent (DocstringComplianceAgent)

**File:** `agentic_core/L6_observability/DocstringComplianceAgent.py`
**Line:** 7
**Category:** L6 Observability Agent (Recently Moved)

### Current (Broken):
```python
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
```

### Corrected:
```python
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
```

### Context:
```python
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, workflow
from __future__ import annotations
# This boosts alignment detection — review and integrate appropriately

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent  # ❌ BROKEN

import ast
```

**Note:** This file was just moved from `agentic_core/observability/` to `agentic_core/L6_observability/` as part of the governance fix, but still has the broken import.

---

## Sample File 5: Unit Test (HierarchyAgent Phase 1)

**File:** `tests/unit/test_hierarchy_agent_phase1.py`
**Line:** 14
**Category:** Test File

### Current (Broken):
```python
from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
```

### Corrected:
```python
# No direct change needed - this import is correct
# The error occurs because HierarchyAgent internally imports SovereignBaseAgent from wrong location
```

### Context:
```python
"""
Phase 1 Tests for HierarchyAgent Universal Scope and Auto-Approve

Tests verify:
1. Auto-approve bypasses interactive prompts
2. Universal scope scans all SOVEREIGN_REGISTRY roots
3. Dry-run safety prevents physical changes
"""

from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent  # ✅ CORRECT
```

### Error Chain:
```
test_hierarchy_agent_phase1.py:14
  → imports HierarchyAgent
    → HierarchyAgent.py:7 imports from agentic_core.observability.SovereignBaseAgent  # ❌ BROKEN
      → ModuleNotFoundError: No module named 'agentic_core.observability.SovereignBaseAgent'
```

**Note:** This demonstrates the cascading failure - even files with correct imports fail because their dependencies have broken imports.

---

## Import Pattern Analysis

### Broken Pattern (212 occurrences):
```python
from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent
```

### Correct Pattern (Required):
```python
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
```

### Affected File Categories:

1. **Layer Base Agents (L0-L6):** ~7 files
   - `L0MaintenanceBaseAgent.py`
   - `L1CognitionBase.py`
   - `L2ExecutionBase.py`
   - `L3OrchestrationBase.py`
   - `L4StateBase.py`
   - (L5 has no base agent)
   - (L6 has no base agent)

2. **L5 Safety Validators:** ~100+ files
   - `HierarchyAgent.py`
   - `LocationAgent.py`
   - `LocationHealerAgent.py`
   - `LocationValidatorAgent.py`
   - All other validators in `L5_safety/validators/`

3. **Concrete Agents (L0-L6):** ~80+ files
   - All agents that inherit from layer base agents

4. **Test Files:** ~20+ files
   - Unit tests
   - Integration tests
   - Verification scripts

5. **Utility/MCP Files:** ~5 files
   - MCP clients
   - Infrastructure utilities

---

## Automated Fix Command

### Unix/Linux/Mac:
```bash
find . -name "*.py" -type f -exec sed -i 's/from agentic_core\.observability\.SovereignBaseAgent/from agentic_core.base_agents.SovereignBaseAgent/g' {} +
```

### Windows (PowerShell):
```powershell
Get-ChildItem -Path . -Filter *.py -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from agentic_core\.observability\.SovereignBaseAgent', 'from agentic_core.base_agents.SovereignBaseAgent' | Set-Content $_.FullName
}
```

### Python Script (Cross-Platform):
```python
import os
from pathlib import Path

project_root = Path("C:/Git/Agentic-Workflow")
old_import = "from agentic_core.observability.SovereignBaseAgent"
new_import = "from agentic_core.base_agents.SovereignBaseAgent"

for py_file in project_root.rglob("*.py"):
    try:
        content = py_file.read_text(encoding='utf-8')
        if old_import in content:
            updated = content.replace(old_import, new_import)
            py_file.write_text(updated, encoding='utf-8')
            print(f"✅ Fixed: {py_file.relative_to(project_root)}")
    except Exception as e:
        print(f"❌ Error: {py_file.relative_to(project_root)} - {e}")
```

---

## Verification After Fix

### 1. Re-run Agent Discovery:
```bash
python -m agentic_core.L0_maintenance.scripts.full_agent_discovery
```

**Expected:** 278 agents, 0 Unknown layers, 0 import errors

### 2. Run HierarchyAgent Tests:
```bash
python -m pytest tests/unit/test_hierarchy_agent_phase1.py tests/unit/test_hierarchy_agent_phase2.py tests/unit/test_hierarchy_agent_phase3.py tests/unit/test_hierarchy_agent_root_healing.py -v
```

**Expected:** All tests pass (12 tests total)

### 3. Run Full Test Suite:
```bash
python -m pytest tests/ -v
```

**Expected:** 100% pass rate

---

## Summary

**Files Sampled:** 5 representative files
**Import Pattern:** Consistent across all 212 files
**Fix Complexity:** Simple find-and-replace operation
**Risk Level:** Low (mechanical change, no logic modification)
**Estimated Fix Time:** 2-3 minutes (automated script)
**Verification Time:** 5-10 minutes (test suite execution)

**Next Action:** Execute automated fix script to update all 212 import statements.
