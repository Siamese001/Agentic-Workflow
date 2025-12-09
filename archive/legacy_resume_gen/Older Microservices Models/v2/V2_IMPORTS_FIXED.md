# V2 Architecture - All Imports Fixed to Use _v2 Suffix

## What Was Changed

All supporting modules now use `_v2` suffix consistently across all imports.

## File Structure (Final)

### Main Orchestration (WITH _v2):
- workflow_RES_v2.py
- run_workflow_RES_v2.py

### Supporting Modules (WITH _v2):
- config_RES_v2.py (v17.00) - Configuration + GovernorConfig
- utils_RES_v2.py (v17.00) - Utilities + V2 tools
- rag_RES_v2.py (v17.00) - RAG + LibrarianAgent
- prompts_RES_v2.py (v17.00) - Prompt templates
- validation_RES_v2.py (v17.00) - Validation system
- state_manager_RES_v2.py (v17.00) - State persistence

### Base Modules (NO _v2):
- models_RES.py - Data models (version-agnostic)
- governor.py (v17.00) - Governor agents

## Import Changes Made

### workflow_RES_v2.py
```python
# BEFORE:
from config_RES import CONFIG, AppConfig, ...
from utils_RES import TextUtils, ...
from validation_RES import PreFlightValidator, ...
from rag_RES import EnhancedJobDescriptionAnalyzer, ...
from state_manager_RES import StateSerializer, ...
import prompts_RES

# AFTER:
from config_RES_v2 import CONFIG, AppConfig, ...
from utils_RES_v2 import TextUtils, ...
from validation_RES_v2 import PreFlightValidator, ...
from rag_RES_v2 import EnhancedJobDescriptionAnalyzer, ...
from state_manager_RES_v2 import StateSerializer, ...
import prompts_RES_v2 as prompts_RES
```

### run_workflow_RES_v2.py
```python
# BEFORE:
from config_RES import CONFIG, OUTPUT_DIR, DATA_DIR

# AFTER:
from config_RES_v2 import CONFIG, OUTPUT_DIR, DATA_DIR
```

### validation_RES_v2.py
```python
# BEFORE:
from config_RES import ValidatorConfig, ...
from utils_RES import TextUtils, ...

# AFTER:
from config_RES_v2 import ValidatorConfig, ...
from utils_RES_v2 import TextUtils, ...
```

### state_manager_RES_v2.py
```python
# BEFORE:
from rag_RES import EnhancedJobDescriptionAnalyzer

# AFTER:
from rag_RES_v2 import EnhancedJobDescriptionAnalyzer
```

### prompts_RES_v2.py
```python
# BEFORE:
from config_RES import DATA_DIR

# AFTER:
from config_RES_v2 import DATA_DIR
```

### rag_RES_v2.py
```python
# BEFORE:
from config_RES import RAGConfig, ...
from utils_RES import TelemetryLogger
import prompts_RES

# AFTER:
from config_RES_v2 import RAGConfig, ...
from utils_RES_v2 import TelemetryLogger
import prompts_RES_v2 as prompts_RES
```

### utils_RES_v2.py
```python
# BEFORE:
from config_RES import ReasoningConfig, ...

# AFTER:
from config_RES_v2 import ReasoningConfig, ...
```

## Import Chain (Final)

```
run_workflow_RES_v2.py
  └─→ workflow_RES_v2.py
       ├─→ governor.py (no _v2)
       ├─→ models_RES.py (no _v2)
       ├─→ config_RES_v2.py ✅
       ├─→ utils_RES_v2.py ✅
       ├─→ validation_RES_v2.py ✅
       ├─→ rag_RES_v2.py ✅
       │    ├─→ prompts_RES_v2.py ✅
       │    ├─→ config_RES_v2.py ✅
       │    ├─→ models_RES.py (no _v2)
       │    └─→ utils_RES_v2.py ✅
       └─→ state_manager_RES_v2.py ✅
            └─→ models_RES.py (no _v2)
            └─→ rag_RES_v2.py ✅
```

## Why This Approach?

### Advantages:
✅ **Clear versioning** - Easy to see what's v2
✅ **Side-by-side deployment** - Can keep v1 files alongside v2
✅ **Explicit compatibility** - No ambiguity about versions
✅ **Easier rollback** - Can revert to v1 imports if needed
✅ **Better for development** - Can compare v1 vs v2 implementations

### Files WITHOUT _v2 Suffix:
- **models_RES.py** - Data structures are version-agnostic
- **governor.py** - V2-only component (no v1 equivalent)

## Validation

### Import Test Results:
```bash
cd /mnt/user-data/outputs
python3 -c "from config_RES_v2 import CONFIG; print(CONFIG.governor)"
# ✓ Works - GovernorConfig present
```

## Status: ✅ ALL IMPORTS FIXED

All files now use consistent `_v2` suffix for supporting modules.
Ready for execution with clear version separation.
