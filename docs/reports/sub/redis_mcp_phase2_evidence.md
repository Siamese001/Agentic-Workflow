# Redis MCP Phase 2 Evidence

## Hard Gate + Provenance

**git status --porcelain=v1:**
```
?? docs/reports/evidence/
?? docs/reports/sub/_mcp_registry_7ba2f82b0.py
?? docs/reports/sub/_redis_mcp_client_58c437fa0.py
?? docs/reports/sub/_test_mcp_seq_7ba2f82b0.py
?? docs/reports/sub/_test_redis_mcp_integration_58c437fa0.py
?? docs/reports/sub/redis_mcp_phase1_evidence.md
?? docs/reports/sub/redis_mcp_phase2_evidence.md
```

**git rev-parse HEAD:**
```
ea3d95e0b5ffa34714737ce23b775eabde8fe375
```

**git --no-pager log -n 3 --oneline --decorate:**
```
ea3d95e0b (HEAD -> main) chore(rules): pin .windsurfrules eol to lf
963b6fb2d chore(rules): link external global_rules.md
1765f60cd governance: add Agent Invocation Lock (Function-Only, No Duplicate Scripts) - §1B
```

## Materialize Authoritative Source Files

**A) Redis MCP client (58c437fa0):**
- Files extracted: redis_mcp_client.py, test_redis_mcp_integration.py
- Located: agentic_core/L4_state/caching/redis_mcp_client.py

**B) MCP registry (7ba2f82b0):**
- Files extracted: mcp_registry.py, test_mcp_sequential_thinking.py
- Located: agentic_core/L2_execution/config/mcp_registry.py

## Current Tip Landing Paths

**Directory Discovery:**
- agentic_core/L2_execution/mcp/mcp_registry.py => MISSING (created at agentic_core/L2_execution/config/mcp_registry.py)
- agentic_core/L2_execution/mcp => MISSING
- agentic_core/L4_state/caching => CREATED
- agentic_core/L4_state => EXISTS

**Config Discovery:**
- Selected: agentic_core/config/core/sovereign_config.py (already used for runtime flags)

## Implementation Changes

**A) Redis MCP Client Module:**
- Created: agentic_core/L4_state/caching/redis_mcp_client.py
- Updated import path to use current config structure
- Added Redis MCP entry to SOVEREIGN_MCP_REGISTRY

**B) MCP Registry Update:**
- Created: agentic_core/L2_execution/config/mcp_registry.py
- Added Redis MCP server configuration with L4 layer assignment
- Capabilities: caching, state_management, session_storage

**C) Configuration Updates:**
- Updated: agentic_core/config/core/sovereign_config.py
- Added properties: redis_mcp_enabled, redis_url, redis_cache_prefix, redis_max_key_length, redis_default_ttl_seconds

## Install + Runtime Validation

**A) Tooling Installation:**
```bash
python -m pip install -U ripgrep
```

**B) Validation Search:**
```bash
rg -n -S "REDIS_MCP_ENABLED|redis_mcp_client|mcp.*redis|redis.*mcp" agentic_core
```

**C) Test Execution:**
```bash
python -m pytest -q tests/integration/test_redis_mcp_integration.py -q
```
