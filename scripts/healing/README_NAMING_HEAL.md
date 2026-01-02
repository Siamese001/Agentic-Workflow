# Autonomous Naming Law Healing

## Overview

`NamingAgent` is now **fully autonomous** and self-orchestrating. No external scripts needed.

## Usage

### Via NamingAgent directly (Python/REPL)

```python
from pathlib import Path
from agentic_core.utils.core_extensions.NamingAgent import NamingAgent

naming = NamingAgent(Path.cwd())

# Dry run (safe preview)
summary = naming.heal_repository(dry_run=True, execute=False)

# Execute renames
summary = naming.heal_repository(dry_run=False, execute=True)
```

### Via test script

```bash
# Dry run
python scripts/test_naming_heal.py

# Execute
python scripts/test_naming_heal.py --execute
```

## What It Does

1. **Scans** entire repository for agent file naming violations
2. **Detects** agent classes in non-`*Agent.py` files
3. **Proposes** perfect renames using actual class names from AST
4. **Enforces** `Agent` suffix (e.g., `MissionController` → `MissionControllerAgent.py`)
5. **Blocks** global uniqueness collisions automatically
6. **Flags** multi-agent files for manual splitting

## Results (Current State)

| Metric | Count |
|--------|-------|
| Would rename | 59 files |
| Collisions blocked | 6 files |
| Multi-agent (need split) | 16 files |
| Skipped (compliant) | 1297 files |

## Architecture

**Before:** External script `naming_law_heal.py` drove the agent  
**After:** Agent is autonomous via `heal_repository()` method

**Benefits:**
- Zero file sprawl
- Single source of truth
- Reusable by other agents
- Defense-in-depth safety (`dry_run=True` by default)

## Deprecated Files

- `scripts/healing/naming_law_heal.py.archived` - Old external script (kept for reference)
- `scripts/heal_agent_naming.py` - Legacy version
- `scripts/heal_agent_naming_v2.py` - Intermediate version

All functionality now in `NamingAgent.heal_repository()`.
