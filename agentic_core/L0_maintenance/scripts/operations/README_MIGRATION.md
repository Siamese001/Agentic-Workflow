# Sovereign Migration Script

## Purpose
Automates the migration of shallow files (Depth 1) from `agentic_core/` root to proper L-layer structure (Depth 3+), ensuring compliance with Key 41 (min depth 3) and Key 49 (max depth 5).

## Features
- **SSOT Integration**: Uses `void_compliance.py` heuristics for intelligent placement
- **Dry-Run Mode**: Safe preview before executing moves
- **Audit Logging**: Complete mission audit trail in `observability/logs/migrations/`
- **Package Integrity**: Auto-creates `__init__.py` markers
- **Naming Validation**: Enforces Key 49 naming conventions pre-move
- **Conflict Detection**: Prevents overwrites of existing files

## Usage

### Dry Run (Recommended First)
```bash
# Preview all migrations without executing
python scripts/operations/sovereign_migration.py

# Preview specific files only
python scripts/operations/sovereign_migration.py --files action_node.py orchestrator.py
```

### Live Execution
```bash
# Execute all migrations
python scripts/operations/sovereign_migration.py --live

# Execute specific files only
python scripts/operations/sovereign_migration.py --live --files action_node.py
```

### Custom Project Root
```bash
python scripts/operations/sovereign_migration.py --project-root /path/to/project --live
```

## Migration Logic

### Content-Based Placement (SSOT)
The script analyzes file content to determine the correct L-layer:

| Pattern Detected | Target Layer | Reasoning |
|-----------------|--------------|-----------|
| `planner`, `strategy`, `reasoning`, `mission` | `L1_cognition` | Strategic planning logic |
| `node`, `execute` | `L2_thought_nodes` | Atomic execution units |
| `router`, `orchestrator`, `fission`, `hop` | `L3_orchestration` | Flow control |
| `pinecone`, `redis`, `storage`, `cache` | `L4_state` | Persistence layer |
| `safety`, `guardrail`, `filter` | `L5_safety` | Security controls |
| *Default* | `L1_cognition` | Safe fallback |

### Example Migrations
```
action_node.py          → agentic_core/L2_thought_nodes/execution/action_node.py
orchestrator.py         → agentic_core/L3_orchestration/routing/orchestrator.py
consensus_engine.py     → agentic_core/L1_cognition/strategy/consensus_engine.py
```

## Audit Log Format
```json
{
  "migration_timestamp": "2025-12-22T20:39:00",
  "total_operations": 25,
  "operations": [
    {
      "timestamp": "2025-12-22T20:39:01",
      "operation": "move",
      "source": "C:/Git/Agentic-Workflow/agentic_core/action_node.py",
      "destination": "C:/Git/Agentic-Workflow/agentic_core/L2_thought_nodes/execution/action_node.py",
      "success": true,
      "reason": "Node execution detected"
    }
  ]
}
```

## Safety Guarantees
1. **Dry-run default**: Must explicitly use `--live` to execute
2. **Conflict prevention**: Refuses to overwrite existing files
3. **Naming validation**: Blocks moves that violate Key 49 conventions
4. **Audit trail**: Every operation logged for rollback
5. **Package integrity**: Ensures all parent `__init__.py` exist

## Post-Migration Steps
1. **Verify imports**: Update any hardcoded import paths in other files
2. **Run canon validator**: `python canon_validator_agentic_v2.py --harden`
3. **Check tests**: Ensure test suite still passes
4. **Commit atomically**: Single commit with audit log

## Rollback Procedure
If migration causes issues:
```bash
# Review audit log
cat observability/logs/migrations/migration_YYYYMMDD_HHMMSS.json

# Manual rollback using git
git checkout HEAD -- agentic_core/

# Or use audit log to reverse moves programmatically
python scripts/operations/rollback_migration.py --audit-log <path>
```

## Current Shallow Files (22 total)
```
action_node.py
action_registry.py
agent_capabilities.py
agent_logic.py
agent_logic_connectivity.py
canon_agents_core.py
canon_agents_pattern.py
canon_agents_quality.py
canon_agents_structural.py
canon_agents_syntax.py
canon_base_agent.py
canon_orchestrator.py
cognitive_node.py
consensus_engine.py
constants.py
core_utils.py
core_utils_wrapper.py
orchestrator.py
orchestrator_main.py
proactive_audit.py
test_action_registry.py
test_orphan.py
```

## Integration with Canon Validator
After migration, the canon validator will show:
```
[KEY 41] DEPTH ENFORCEMENT: ✓ PASS (0 violations)
  - Min depth 3: All files properly nested in L-layers
  - Max depth 5: No excessive nesting
```

## Troubleshooting

### "File outside project root"
- Ensure `--project-root` points to repository root
- Check that `agentic_core/` exists at that location

### "Naming violation"
- File uses forbidden patterns (e.g., `utils.py`, `temp.py`)
- File lacks high-signal keywords (see Key 49 requirements)
- Rename file before migration or add to protected list

### "Destination already exists"
- Target location already has a file with same name
- Review existing file and decide: rename, merge, or skip

## Development Notes
- Script location: `scripts/operations/sovereign_migration.py`
- SSOT reference: `agentic_core/runtime/void_compliance.py`
- Audit logs: `observability/logs/migrations/`
- Requires: Python 3.8+, no external dependencies
