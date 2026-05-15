# Boundary Violation Examples

## Layer Gravity Violation

```python
# FORBIDDEN: L3 importing from L5
from agentic_core.L5_safety.config import some_config

# CORRECT: use same or lower layer
from agentic_core.L3_orchestration.config import some_config
```

## Dead Import Violation

```python
# FORBIDDEN: import never used
import os  # os is never referenced in this file

# CORRECT: remove the unused import
```

## Shim Violation

```python
# FORBIDDEN: using old path without shim
from old_module import SomeClass

# CORRECT during transition period: use shim
from old_module._shim import SomeClass  # deprecated — use new_location

# CORRECT after migration: use canonical path
from new_location.canonical_module import SomeClass
```

## Archive Import Violation

```python
# FORBIDDEN: importing from archives/
from archives.old_feature.utils import helper

# CORRECT: find and import from canonical location
from agentic_core.L2_execution.utils import helper
```

## Runtime Import Violation

```python
# FORBIDDEN: structural import inside function body
def process():
    import json  # structural import at runtime
    return json.loads(data)

# CORRECT: module-level import
import json

def process():
    return json.loads(data)
```
