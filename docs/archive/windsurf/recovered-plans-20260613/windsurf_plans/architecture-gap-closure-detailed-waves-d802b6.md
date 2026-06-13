# Architecture Gap Closure - Detailed Wave & Microwave Plan

Expanded execution plan with 10 waves broken into 26 microwaves (each <=5 files), covering all 50 architecture gaps with granular ADG-backed validation gates.

---

## Wave & Microwave Summary Table

| Wave | Microwaves | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|------------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | M1.1, M1.2 | EM-1, EM-2 | Emergency Runtime Prohibition | ~18,000 | Mutation prohibition works | 🟢 GREEN | apps_* writes blocked |
| W2 | M2.1, M2.2, M2.3 | UWG-1, UWG-2, UWG-3 | Critical apps_* UWG Integration | ~22,000 | WriteGovernorMixin ready | 🟢 GREEN | 7 critical files migrated |
| W3 | M3.1, M3.2 | UWG-4, UWG-5 | L4 Storage UWG Injection | ~25,000 | UWG 4-field API stable | 🟢 GREEN | L4 providers use UWG |
| W4 | M4.1, M4.2, M4.3 | ISO-1, ISO-2, ISO-3 | Break Circular Dependencies | ~20,000 | apps_engines_aliases isolated | 🟢 GREEN | 25 cross-layer imports removed |
| W5 | M5.1, M5.2, M5.3 | ISO-4, ISO-5, ISO-6 | L2 Facade Layer Creation | ~24,000 | Facade pattern defined | 🟢 GREEN | 15 apps_* files use facades |
| W6 | M6.1, M6.2, M6.3 | L5-1, L5-2, L5-3 | HITL Re-Clearance Gates | ~21,000 | L5ReClearanceGate implemented | 🟢 GREEN | 3 HITL paths secured |
| W7 | M7.1, M7.2 | HASH-1, HASH-2 | Hash Continuity Wiring | ~19,000 | blueprint_hash API available | 🟢 GREEN | 4 hash chains complete |
| W8 | M8.1, M8.2 | ORCH-1, ORCH-2 | L3 Orchestration Fixes | ~17,000 | Replay engine validated | 🟢 GREEN | 2 orchestrators compliant |
| W9 | M9.1, M9.2 | FALL-1, FALL-2 | Silent Fallback Removal | ~15,000 | Explicit disposition gates | 🟢 GREEN | 3 routers fixed |
| W10 | M10.1, M10.2, M10.3, M10.4 | AUD-1, AUD-2, AUD-3, AUD-4 | Remaining Gaps + Validation | ~16,000 | ADG scanner operational | 🟢 GREEN | 12 remaining gaps closed |

**Total: 26 Microwaves across 10 Waves (~197,000 tokens)**

---

## Wave 1 — Emergency Runtime Prohibition

### Microwave M1.1: Extend Mutation Prohibition (EM-1)
**Scope**: Modify mutation prohibition to detect and block apps_* package writes
**Files**: 2
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py` (modify)
- `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py` (modify)

**ADG Targets**:
- Add `blocks_direct_write` edges for 7 C1 gap files
- Target: 7 edges minimum

**Commands**:
```bash
# Step 1: Extend FORBIDDEN_WRITE_LAYERS constant
python tools/refactor/extend_forbidden_layers.py --add apps_lic --add apps_rg --add apps_exec

# Step 2: Add stack inspection to detect caller package
python tools/refactor/add_stack_inspection.py --file mutation_prohibition.py --detect-package apps_*

# Step 3: Add prohibition event emission
python tools/refactor/add_prohibition_telemetry.py --file write_gateway_enforcer.py

# Validate
python -c "from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write; assert_no_persistent_write('apps_lic', 'test')"  # Should pass check only
```

**Evidence**:
- [ ] FORBIDDEN_WRITE_LAYERS includes apps_lic, apps_rg, apps_exec
- [ ] `_get_caller_package()` function added with stack frame inspection
- [ ] Prohibition events emit to telemetry

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
edges = client.adg_edge_fanout("mutation_prohibition", "blocks_direct_write", limit=10)
assert len(edges) >= 7, f"M1.1: Expected 7+ blocks_direct_write edges, got {len(edges)}"
```

---

### Microwave M1.2: Create UWG Interceptor Shim (EM-2)
**Scope**: Build emergency shim that intercepts file operations and routes through UWG
**Files**: 1 (create)
- `agentic_core/L2_execution/enforcement/uwg_interceptor_shim.py` (create)

**ADG Targets**:
- Shim registers as L2 enforcement module
- Target: `applies_guardrail` edge from shim to UWG

**Commands**:
```bash
# Step 1: Create interceptor shim
python tools/codegen/create_interceptor_shim.py --output agentic_core/L2_execution/enforcement/uwg_interceptor_shim.py

# Step 2: Implement builtins.open override
python tools/refactor/add_open_interceptor.py --file uwg_interceptor_shim.py

# Step 3: Implement Path.write_text/bytes override
python tools/refactor/add_path_interceptor.py --file uwg_interceptor_shim.py

# Step 4: Add install/uninstall functions
python tools/refactor/add_shim_lifecycle.py --file uwg_interceptor_shim.py

# Validate
python -c "
from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import install_uwg_interceptor, uninstall_uwg_interceptor
install_uwg_interceptor()
print('Shim installed')
uninstall_uwg_interceptor()
print('Shim uninstalled')
"
```

**Evidence**:
- [ ] `_original_open`, `_original_path_write_text`, `_original_path_write_bytes` saved
- [ ] `install_uwg_interceptor()` function operational
- [ ] `uninstall_uwg_interceptor()` function operational
- [ ] Interceptor routes writes through `get_write_gateway().write_through()`

**Completion Gate**:
```python
# Test shim interception
import builtins
from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import install_uwg_interceptor
install_uwg_interceptor()
assert builtins.open.__name__ == '_intercepted_open', "M1.2: Shim not intercepting open()"
```

**Wave 1 Completion**: All 7 C1 files now raise `PermissionError` on direct write attempts

---

## Wave 2 — Critical apps_* UWG Integration

### Microwave M2.1: Add WriteGovernorMixin to Types (UWG-1)
**Scope**: Add mixin to vector memory and trace registry types
**Files**: 3
- `apps_lic/types/lic_vector_memory_types.py`
- `apps_lic/types/TraceRegistry.py`
- `apps_lic/types/state_checkpoint_types.py`

**ADG Targets**:
- `writes_through` edges: 3
- `applies_guardrail` edges: 3

**Commands**:
```bash
# Step 1: Add WriteGovernorMixin inheritance
python tools/refactor/add_mixin.py --files wave2_types_files.txt --mixin WriteGovernorMixin --import-from agentic_core.L2_execution.enforcement.write_governor_mixin

# Step 2: Replace open()/write() with governed_write()
python tools/refactor/replace_file_writes.py --files wave2_types_files.txt --method governed_write

# Step 3: Replace json.dump with governed_json_write
python tools/refactor/replace_json_writes.py --files wave2_types_files.txt --method governed_write_json

# Step 4: Replace pickle with governed_pickle
python tools/refactor/replace_pickle_writes.py --files wave2_types_files.txt --method governed_write_pickle

# Validate
pytest tests/apps_lic/types/test_uwg_integration.py::TestVectorMemoryUWG -v
pytest tests/apps_lic/types/test_uwg_integration.py::TestTraceRegistryUWG -v
```

**Evidence**:
- [ ] All 3 type classes inherit from WriteGovernorMixin
- [ ] `governed_write()` calls replace all direct writes
- [ ] Vector memory persistence routed through UWG
- [ ] TraceRegistry persistence routed through UWG
- [ ] Checkpoint operations routed through UWG

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
for file in ['lic_vector_memory_types.py', 'TraceRegistry.py', 'state_checkpoint_types.py']:
    nodes = client.adg_nodes_by_file(f"apps_lic/types/{file}")
    for node in nodes:
        edges = client.adg_edge_fanout(node['id'], "writes_through")
        assert len(edges) >= 1, f"M2.1: {file} missing writes_through edges"
```

---

### Microwave M2.2: Add WriteGovernorMixin to Reasoning Agents (UWG-2)
**Scope**: Add mixin to healing and learning agents
**Files**: 2
- `apps_lic/reasoning/OutreachLearningAgent.py`
- `apps_lic/reasoning/LicHealingOrchestrator.py`

**ADG Targets**:
- `writes_through` edges: 2
- `applies_guardrail` edges: 2
- `validated_by_safety_plane` edges: 2

**Commands**:
```bash
# Step 1: Add WriteGovernorMixin inheritance
python tools/refactor/add_mixin.py --files wave2_reasoning_files.txt --mixin WriteGovernorMixin

# Step 2: Replace persist_state methods
python tools/refactor/replace_persist_methods.py --files wave2_reasoning_files.txt --method governed_write

# Step 3: Update healing orchestrator checkpoint logic
python tools/refactor/update_healing_checkpoints.py --file LicHealingOrchestrator.py --gateway governed_write

# Validate
pytest tests/apps_lic/reasoning/test_outreach_learning_uwg.py -v
pytest tests/apps_lic/reasoning/test_healing_orchestrator_uwg.py -v
```

**Evidence**:
- [ ] OutreachLearningAgent uses governed_write for learning persistence
- [ ] LicHealingOrchestrator uses governed_write for healing state
- [ ] Both agents emit execution trace metadata
- [ ] Checkpoints include replay_key

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify OutreachLearningAgent
edges = client.adg_edge_fanout("apps_lic.reasoning.OutreachLearningAgent", "writes_through")
assert len(edges) >= 1, "M2.2: OutreachLearningAgent missing writes_through"
# Verify LicHealingOrchestrator
edges = client.adg_edge_fanout("apps_lic.reasoning.LicHealingOrchestrator", "writes_through")
assert len(edges) >= 1, "M2.2: LicHealingOrchestrator missing writes_through"
```

---

### Microwave M2.3: Add WriteGovernorMixin to Utils and Interpreter (UWG-3)
**Scope**: Add mixin to manifest manager and code interpreter
**Files**: 2
- `apps_lic/utils/manifest_manager_util.py`
- `apps_lic/reasoning/LicCodeInterpreter.py`

**ADG Targets**:
- `writes_through` edges: 2
- `applies_guardrail` edges: 2
- `blocks_direct_write` edges: 0 (should be clean)

**Commands**:
```bash
# Step 1: Add WriteGovernorMixin inheritance
python tools/refactor/add_mixin.py --files wave2_utils_interpreter_files.txt --mixin WriteGovernorMixin

# Step 2: Replace manifest writes
python tools/refactor/replace_manifest_writes.py --file manifest_manager_util.py --method governed_write_json

# Step 3: Replace code interpreter persistence
python tools/refactor/add_interpreter_sandbox.py --file LicCodeInterpreter.py --write-method governed_write

# Validate
pytest tests/apps_lic/utils/test_manifest_manager_uwg.py -v
pytest tests/apps_lic/reasoning/test_code_interpreter_sandbox.py -v
```

**Evidence**:
- [ ] ManifestManager uses governed_write_json
- [ ] LicCodeInterpreter uses governed_write for code results
- [ ] Sandbox enforcement prevents arbitrary writes
- [ ] All writes emit execution trace

**Completion Gate**:
```python
# Check no blocks_direct_write edges remain for these files
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
for file in ['manifest_manager_util.py', 'LicCodeInterpreter.py']:
    nodes = client.adg_nodes_by_file(f"apps_lic/*/{file}")
    for node in nodes:
        edges = client.adg_edge_fanout(node['id'], "blocks_direct_write")
        assert len(edges) == 0, f"M2.3: {file} still has blocks_direct_write edges"
```

**Wave 2 Completion**: All 7 C1 gap files migrated to WriteGovernorMixin, ADG shows `writes_through` edges

---

## Wave 3 — L4 Storage UWG Injection

### Microwave M3.1: Filesystem Store UWG Integration (UWG-4)
**Scope**: Refactor filesystem store to inject UWG dependency
**Files**: 2
- `agentic_core/L4_state/storage/filesystem_store.py`
- `agentic_core/L4_state/storage/__init__.py` (add UWG export)

**ADG Targets**:
- `writes_via_uwg` edges: 1
- `reads_from` edges maintained (broad-read OK)

**Commands**:
```bash
# Step 1: Add UWG constructor parameter
python tools/refactor/inject_uwg_constructor.py --file filesystem_store.py --param-name uwg_gateway

# Step 2: Replace Path.write_bytes with UWG.write_to_store
python tools/refactor/replace_storage_writes.py --file filesystem_store.py --method write_to_store

# Step 3: Update store initialization to accept UWG
python tools/refactor/update_store_init.py --file filesystem_store.py --inject-uwg

# Validate
pytest tests/L4_state/storage/test_filesystem_store_uwg.py -v
```

**Evidence**:
- [ ] `FilesystemStore.__init__()` accepts `uwg_gateway` parameter
- [ ] `write()` method uses `self._uwg.write_to_store()`
- [ ] All writes include replay_key, signature, plan_hash, store
- [ ] No direct `path.write_bytes()` calls remain

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify writes_via_uwg edge
edges = client.adg_edge_fanout("agentic_core.L4_state.storage.filesystem_store.FilesystemStore", "writes_via_uwg")
assert len(edges) >= 1, "M3.1: FilesystemStore missing writes_via_uwg edge"
```

---

### Microwave M3.2: Memory Authority & Blob Provider UWG Integration (UWG-5)
**Scope**: Refactor authority and blob providers to use UWG
**Files**: 2
- `agentic_core/L4_state/memory/blob_storage_provider.py`
- `agentic_core/L4_state/authority/memory_authority.py`
- `agentic_core/L4_state/authority/run_scoped_state_authority.py` (bonus, optional)

**ADG Targets**:
- `writes_via_uwg` edges: 2-3
- `applies_guardrail` edges: 2-3

**Commands**:
```bash
# Step 1: Add UWG constructor injection
python tools/refactor/inject_uwg_constructor.py --files wave3_authority_files.txt --param-name uwg

# Step 2: Replace blob writes with UWG
python tools/refactor/replace_blob_writes.py --file blob_storage_provider.py --method write_blob_via_uwg

# Step 3: Replace authority writes with UWG
python tools/refactor/replace_authority_writes.py --file memory_authority.py --method write_authority_via_uwg

# Step 4: Update run_scoped_state_authority
python tools/refactor/update_state_authority.py --file run_scoped_state_authority.py --uwg-method governed_write

# Validate
pytest tests/L4_state/memory/test_blob_storage_uwg.py -v
pytest tests/L4_state/authority/test_memory_authority_uwg.py -v
```

**Evidence**:
- [ ] BlobStorageProvider accepts UWG in constructor
- [ ] MemoryAuthority accepts UWG in constructor
- [ ] All blob writes routed through UWG
- [ ] All authority writes routed through UWG
- [ ] RunScopedStateAuthority uses UWG for state checkpoints

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify all L4 authorities have writes_via_uwg
for cls in ['BlobStorageProvider', 'MemoryAuthority', 'RunScopedStateAuthority']:
    edges = client.adg_edge_fanout(f"agentic_core.L4_state.{cls}", "writes_via_uwg")
    assert len(edges) >= 1, f"M3.2: {cls} missing writes_via_uwg edge"
```

**Wave 3 Completion**: L4 storage providers fully UWG-compliant, strict-write via UWG enforced

---

## Wave 4 — Break Circular Dependencies

### Microwave M4.1: Relocate apps_engines_aliases (ISO-1)
**Scope**: Move aliases module from agentic_core to apps_shared
**Files**: 1 (move) + 3 (update importers)
- `agentic_core/utils/workflow_engines/apps_engines_aliases.py` → `apps_shared/compat/apps_engines_aliases.py`
- Update importers in agentic_core/L5_safety/config/structure_blueprint/ssot.py
- Update importers in agentic_core/L0_routing/scripts/execution_context.py
- Update importers in agentic_core/L3_orchestration/engines/orchestrator.py

**ADG Targets**:
- Remove `imports` edges from agentic_core to apps_lic/apps_rg
- Add `imports` edges to apps_shared instead

**Commands**:
```bash
# Step 1: Move module
python tools/refactor/move_module.py \
  --from agentic_core/utils/workflow_engines/apps_engines_aliases.py \
  --to apps_shared/compat/apps_engines_aliases.py \
  --add-deprecation-warning

# Step 2: Add backward compat shim at old location
python tools/codegen/create_compat_shim.py \
  --location agentic_core/utils/workflow_engines/apps_engines_aliases.py \
  --forward-to apps_shared.compat.apps_engines_aliases

# Step 3: Update internal agentic_core importers
python tools/refactor/update_imports.py \
  --old-path agentic_core.utils.workflow_engines.apps_engines_aliases \
  --new-path apps_shared.compat.apps_engines_aliases \
  --files wave4_importer_files.txt

# Validate
python -c "from apps_shared.compat.apps_engines_aliases import CampaignBalanceAgent; print('Import OK')"
```

**Evidence**:
- [ ] Module moved to apps_shared/compat/
- [ ] Deprecation warning added to old location
- [ ] All agentic_core importers updated
- [ ] No agentic_core code imports from apps_lic/apps_rg directly

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Check no imports from agentic_core to apps_lic/apps_rg
nodes = client.adg_nodes_by_layer("agentic_core")
for node in nodes:
    edges = client.adg_edge_fanout(node['id'], "imports")
    for edge in edges:
        if 'apps_lic' in edge['target'] or 'apps_rg' in edge['target']:
            assert False, f"M4.1: agentic_core.{node['id']} imports {edge['target']}"
```

---

### Microwave M4.2: Remove agentic_core → apps_* Direct Imports (ISO-2)
**Scope**: Clean up remaining direct imports from agentic_core to apps_*
**Files**: 3
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` (7 imports)
- `agentic_core/L0_routing/scripts/execution_context.py` (5 imports)
- `agentic_core/L3_orchestration/engines/sovereign_orchestrator.py` (3 imports)

**ADG Targets**:
- Remove remaining cross-layer import edges
- Target: 0 imports from agentic_core to apps_*

**Commands**:
```bash
# Step 1: Identify all direct imports
python tools/analysis/find_cross_imports.py --from agentic_core --to apps_* --output wave4_cross_imports.json

# Step 2: Replace with facade calls
python tools/refactor/convert_to_facade_calls.py --imports-file wave4_cross_imports.json --facade apps_shared.gateways.AgenticCoreFacade

# Step 3: Verify no direct imports remain
python tools/analysis/find_cross_imports.py --from agentic_core --to apps_* --verify-zero

# Validate
pytest tests/architecture/test_no_cross_imports.py -v
```

**Evidence**:
- [ ] ssot.py uses facade instead of direct imports
- [ ] execution_context.py uses facade instead of direct imports
- [ ] sovereign_orchestrator.py uses facade instead of direct imports
- [ ] Zero imports from agentic_core to apps_*

**Completion Gate**:
```python
import subprocess
result = subprocess.run(
    ['grep', '-r', 'from apps_lic\\|from apps_rg\\|from apps_exec', 'agentic_core/'],
    capture_output=True, text=True
)
# Filter out test files and comments
actual_imports = [line for line in result.stdout.split('\n') if line and not line.strip().startswith('#')]
assert len(actual_imports) == 0, f"M4.2: Found {len(actual_imports)} remaining imports"
```

---

### Microwave M4.3: Update apps_* to Use Facade (ISO-3)
**Scope**: Update apps_* files to use new facade instead of direct agentic_core imports
**Files**: 3
- `apps_lic/utils/lic_agent_base_util.py` (10 imports → facade)
- `apps_lic/engines/lic_spine_adapter.py` (6 imports → facade)
- `apps_lic/reasoning/OutreachSignalRouterAgent.py` (6 imports → facade)

**ADG Targets**:
- Add `routes_through` edges from apps_* to facade layer
- Target: 3+ facade routing edges

**Commands**:
```bash
# Step 1: Update lic_agent_base_util
python tools/refactor/convert_imports_to_facade.py --file lic_agent_base_util.py --facade apps_shared.gateways.AgenticCoreFacade

# Step 2: Update lic_spine_adapter
python tools/refactor/convert_imports_to_facade.py --file lic_spine_adapter.py --facade apps_shared.gateways.AgenticCoreFacade

# Step 3: Update OutreachSignalRouterAgent
python tools/refactor/convert_imports_to_facade.py --file OutreachSignalRouterAgent.py --facade apps_shared.gateways.AgenticCoreFacade

# Validate
pytest tests/apps_lic/test_facade_usage.py -v
```

**Evidence**:
- [ ] lic_agent_base_util.py routes through AgenticCoreFacade
- [ ] lic_spine_adapter.py routes through AgenticCoreFacade
- [ ] OutreachSignalRouterAgent.py routes through AgenticCoreFacade
- [ ] All direct agentic_core imports removed from these files

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify routes_through edges to facade
for file in ['lic_agent_base_util.py', 'lic_spine_adapter.py', 'OutreachSignalRouterAgent.py']:
    nodes = client.adg_nodes_by_file(f"apps_lic/*/{file}")
    for node in nodes:
        edges = client.adg_edge_fanout(node['id'], "routes_through")
        facade_edges = [e for e in edges if 'facade' in e['target'].lower()]
        assert len(facade_edges) >= 1, f"M4.3: {file} not routing through facade"
```

**Wave 4 Completion**: Circular dependencies broken, zero agentic_core → apps_* imports remain

---

## Wave 5 — L2 Facade Layer Creation

### Microwave M5.1: Create L2 Facade Base Classes (ISO-4)
**Scope**: Create base classes for facade layer
**Files**: 3 (create)
- `apps_shared/gateways/l2_gateway_base.py` (L2ExecutionAgent base)
- `apps_shared/gateways/__init__.py` (exports)
- `apps_shared/gateways/gateway_exceptions.py` (custom exceptions)

**ADG Targets**:
- `belongs_to_layer` edges for facade layer
- `implements` edges for L2 contract compliance

**Commands**:
```bash
# Step 1: Create L2 gateway base class
python tools/codegen/create_l2_base.py \
  --template L2ExecutionAgent \
  --output apps_shared/gateways/l2_gateway_base.py

# Step 2: Add __init__.py exports
python tools/codegen/create_init_exports.py \
  --files "l2_gateway_base.py,gateway_exceptions.py" \
  --output apps_shared/gateways/__init__.py

# Step 3: Create custom exceptions
python tools/codegen/create_exceptions.py \
  --types "GatewayError,RoutingError,ValidationError" \
  --output apps_shared/gateways/gateway_exceptions.py

# Validate
python -c "from apps_shared.gateways.l2_gateway_base import L2GatewayBase; print('Base OK')"
```

**Evidence**:
- [ ] L2GatewayBase inherits from L2ExecutionAgent
- [ ] l2_init(), l2_execute(), l2_synthesize() methods defined
- [ ] All methods emit execution trace
- [ ] Exceptions include GatewayError, RoutingError, ValidationError

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify belongs_to_layer edge
nodes = client.adg_nodes_by_file("apps_shared/gateways/l2_gateway_base.py")
for node in nodes:
    edges = client.adg_edge_fanout(node['id'], "belongs_to_layer")
    assert len(edges) >= 1, "M5.1: L2GatewayBase missing layer assignment"
```

---

### Microwave M5.2: Create AgenticCoreFacade (ISO-5)
**Scope**: Implement main facade class
**Files**: 1 (create) + 2 (enhance)
- `apps_shared/gateways/agentic_core_facade.py` (create)
- `apps_shared/gateways/l2_gateway_base.py` (enhance with UWG binding)
- `apps_shared/gateways/__init__.py` (add AgenticCoreFacade export)

**ADG Targets**:
- `writes_through` edges from facade
- `routes_through` edges to agentic_core
- `applies_guardrail` edges

**Commands**:
```bash
# Step 1: Create main facade
python tools/codegen/create_facade.py \
  --target agentic_core \
  --base-class apps_shared.gateways.L2GatewayBase \
  --output apps_shared/gateways/agentic_core_facade.py

# Step 2: Add UWG binding to base class
python tools/refactor/add_uwg_binding.py --file l2_gateway_base.py --gateway-method governed_write

# Step 3: Export from __init__
python tools/refactor/add_export.py --file __init__.py --symbol AgenticCoreFacade

# Validate
pytest tests/apps_shared/gateways/test_agentic_core_facade.py -v
```

**Evidence**:
- [ ] AgenticCoreFacade inherits from L2GatewayBase
- [ ] All l2_* methods implemented
- [ ] UWG binding available via `self._uwg`
- [ ] Routes calls to agentic_core through UWG
- [ ] Emits execution trace for all operations

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify writes_through edges
edges = client.adg_edge_fanout("apps_shared.gateways.AgenticCoreFacade", "writes_through")
assert len(edges) >= 1, "M5.2: AgenticCoreFacade missing writes_through"
```

---

### Microwave M5.3: Create Specialized Facades (ISO-6)
**Scope**: Create additional specialized facades for specific use cases
**Files**: 3 (create)
- `apps_shared/gateways/l4_storage_facade.py` (L4 access)
- `apps_shared/gateways/l5_safety_facade.py` (L5 validation)
- `apps_shared/gateways/l0_routing_facade.py` (L0 routing)

**ADG Targets**:
- `reads_from` edges (for L4 facade)
- `routes_through` edges (for L0 facade)
- `validated_by_safety_plane` edges (for L5 facade)

**Commands**:
```bash
# Step 1: Create L4 storage facade
python tools/codegen/create_facade.py \
  --target agentic_core.L4_state \
  --base-class apps_shared.gateways.L2GatewayBase \
  --output apps_shared/gateways/l4_storage_facade.py

# Step 2: Create L5 safety facade
python tools/codegen/create_facade.py \
  --target agentic_core.L5_safety \
  --base-class apps_shared.gateways.L2GatewayBase \
  --output apps_shared/gateways/l5_safety_facade.py

# Step 3: Create L0 routing facade
python tools/codegen/create_facade.py \
  --target agentic_core.L0_routing \
  --base-class apps_shared.gateways.L2GatewayBase \
  --output apps_shared/gateways/l0_routing_facade.py

# Validate
pytest tests/apps_shared/gateways/test_specialized_facades.py -v
```

**Evidence**:
- [ ] L4StorageFacade for read-only L4 access
- [ ] L5SafetyFacade for policy validation
- [ ] L0RoutingFacade for route requests
- [ ] All facades inherit from L2GatewayBase
- [ ] All facades emit execution trace

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify facade layer
facades = ['L4StorageFacade', 'L5SafetyFacade', 'L0RoutingFacade']
for facade in facades:
    nodes = client.adg_nodes_by_file(f"apps_shared/gateways/{facade.lower()}.py")
    assert len(nodes) > 0, f"M5.3: {facade} not found in ADG"
```

**Wave 5 Completion**: L2 facade layer fully operational, 12 apps_* files routing through facades

---

## Wave 6 — HITL Re-Clearance Gates

### Microwave M6.1: Create L5ReClearanceGate Core (L5-1)
**Scope**: Implement the re-clearance gate class
**Files**: 2 (create)
- `agentic_core/L5_safety/enforcement/hitl_re_clearance_gate.py`
- `agentic_core/L5_safety/enforcement/hitl_types.py` (types/enum)

**ADG Targets**:
- `applies_guardrail` edges
- `validates_policy` edges

**Commands**:
```bash
# Step 1: Create HITL types
python tools/codegen/create_hitl_types.py \
  --enums "ReClearanceStatus,DispositionType" \
  --dataclasses "ReClearanceDecision,HumanModification,PolicyContext" \
  --output agentic_core/L5_safety/enforcement/hitl_types.py

# Step 2: Create L5ReClearanceGate
python tools/codegen/create_l5_gate.py \
  --template re_clearance \
  --types-file hitl_types.py \
  --output agentic_core/L5_safety/enforcement/hitl_re_clearance_gate.py

# Step 3: Add re_clear_human_modification method
python tools/refactor/add_re_clear_method.py \
  --file hitl_re_clearance_gate.py \
  --method-name re_clear_human_modification

# Validate
pytest tests/L5_safety/test_re_clearance_gate.py -v
```

**Evidence**:
- [ ] ReClearanceStatus enum (PENDING, APPROVED, REJECTED, MODIFIED)
- [ ] ReClearanceDecision dataclass
- [ ] L5ReClearanceGate class implemented
- [ ] re_clear_human_modification() method operational
- [ ] Policy validation integrated
- [ ] Signature generation for approved modifications

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify applies_guardrail edges
edges = client.adg_edge_fanout("agentic_core.L5_safety.enforcement.L5ReClearanceGate", "applies_guardrail")
assert len(edges) >= 1, "M6.1: L5ReClearanceGate missing applies_guardrail"
```

---

### Microwave M6.2: Create HITL Airlock (L5-2)
**Scope**: Implement the airlock pattern for HITL isolation
**Files**: 2 (create)
- `agentic_core/L5_safety/enforcement/hitl_airlock.py`
- `agentic_core/L5_safety/enforcement/airlock_exceptions.py`

**ADG Targets**:
- `observes_runtime_state` edges
- `gated_by_confidence` edges

**Commands**:
```bash
# Step 1: Create airlock exceptions
python tools/codegen/create_exceptions.py \
  --types "AirlockViolation,ModificationRejected,ReClearanceRequired" \
  --output agentic_core/L5_safety/enforcement/airlock_exceptions.py

# Step 2: Create HITLAirlock class
python tools/codegen/create_airlock.py \
  --gate-class L5ReClearanceGate \
  --output agentic_core/L5_safety/enforcement/hitl_airlock.py

# Step 3: Add materialize_packet method
python tools/refactor/add_materialize_method.py --file hitl_airlock.py

# Validate
pytest tests/L5_safety/test_hitl_airlock.py -v
```

**Evidence**:
- [ ] HITLAirlock class implemented
- [ ] Materialize packet with evidence
- [ ] Airlock states: LOCKED, MATERIALIZED, CLEARED, REJECTED
- [ ] Integration with L5ReClearanceGate
- [ ] Exception hierarchy for airlock violations

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify observes_runtime_state edges
edges = client.adg_edge_fanout("agentic_core.L5_safety.enforcement.HITLAirlock", "observes_runtime_state")
assert len(edges) >= 1, "M6.2: HITLAirlock missing observes_runtime_state"
```

---

### Microwave M6.3: Integrate into HITL Orchestrators (L5-3)
**Scope**: Add airlock/re-clearance to HITL paths
**Files**: 3
- `apps_lic/reasoning/LicHealingOrchestrator.py` (enhance HITL methods)
- `apps_lic/reasoning/HOPPipelineExecutor.py` (enhance pipeline HITL)
- `apps_rg/reasoning/RgHealingOrchestrator.py` (enhance RG healing)

**ADG Targets**:
- `validated_by_safety_plane` edges: 3
- `gated_by_confidence` edges: 3

**Commands**:
```bash
# Step 1: Add airlock to LicHealingOrchestrator
python tools/refactor/add_airlock_to_orchestrator.py \
  --file LicHealingOrchestrator.py \
  --airlock-class agentic_core.L5_safety.enforcement.HITLAirlock

# Step 2: Add airlock to HOPPipelineExecutor
python tools/refactor/add_airlock_to_executor.py \
  --file HOPPipelineExecutor.py \
  --gate-class L5ReClearanceGate

# Step 3: Add airlock to RgHealingOrchestrator
python tools/refactor/add_airlock_to_orchestrator.py \
  --file RgHealingOrchestrator.py \
  --airlock-class HITLAirlock

# Validate
pytest tests/apps_lic/reasoning/test_healing_hitl_airlock.py -v
pytest tests/apps_lic/reasoning/test_hop_pipeline_airlock.py -v
pytest tests/apps_rg/reasoning/test_rg_healing_airlock.py -v
```

**Evidence**:
- [ ] LicHealingOrchestrator uses HITLAirlock for HITL interventions
- [ ] HOPPipelineExecutor validates through L5ReClearanceGate
- [ ] RgHealingOrchestrator has airlock pattern
- [ ] All HITL paths compute policy_validation_hash
- [ ] All HITL paths generate l5_signature

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify validated_by_safety_plane edges for HITL orchestrators
orchestrators = [
    "apps_lic.reasoning.LicHealingOrchestrator",
    "apps_lic.reasoning.HOPPipelineExecutor",
    "apps_rg.reasoning.RgHealingOrchestrator"
]
for orch in orchestrators:
    edges = client.adg_edge_fanout(orch, "validated_by_safety_plane")
    assert len(edges) >= 1, f"M6.3: {orch} missing validated_by_safety_plane"
```

**Wave 6 Completion**: All 3 HITL paths enforce L5 re-clearance, ADG shows validation edges

---

## Wave 7 — Hash Continuity Wiring

### Microwave M7.1: Add Hash Freeze to L3/L2 (HASH-1)
**Scope**: Wire blueprint_hash, policy_hash freeze at entry points
**Files**: 3
- `agentic_core/L3_orchestration/engines/prompt_chain_engine.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `agentic_core/L2_execution/wrappers/l2_agent_wrappers.py`

**ADG Targets**:
- `signs_execution_trace` edges with hash metadata
- `pulls_context` edges with frozen hash

**Commands**:
```bash
# Step 1: Add blueprint_hash freeze to prompt_chain_engine
python tools/refactor/add_hash_freeze.py \
  --file prompt_chain_engine.py \
  --hash-type blueprint_hash \
  --freeze-at-entry

# Step 2: Add policy_hash to HOPPipelineExecutor
python tools/refactor/add_hash_continuity.py \
  --file HOPPipelineExecutor.py \
  --hash-type policy_hash \
  --propagate-chain

# Step 3: Add trace lineage to l2_agent_wrappers
python tools/refactor/add_trace_lineage.py \
  --file l2_agent_wrappers.py \
  --lineage-type hash_chain

# Validate
pytest tests/architecture/test_hash_freeze.py -v
```

**Evidence**:
- [ ] blueprint_hash frozen at L3 entry
- [ ] policy_hash propagated through HOP pipeline
- [ ] Trace lineage includes hash chain
- [ ] All hashes signed in execution trace
- [ ] Hash validation on context pull

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify signs_execution_trace with hash metadata
for file in ['prompt_chain_engine.py', 'HOPPipelineExecutor.py', 'l2_agent_wrappers.py']:
    nodes = client.adg_nodes_by_file(file)
    for node in nodes:
        edges = client.adg_edge_fanout(node['id'], "signs_execution_trace")
        # Check for hash metadata in edges
        hash_edges = [e for e in edges if 'hash' in str(e.get('metadata', {})).lower()]
        assert len(hash_edges) >= 1, f"M7.1: {file} missing hash in execution trace"
```

---

### Microwave M7.2: Add Replay Key to Healing (HASH-2)
**Scope**: Add replay_key chain to healing orchestrator
**Files**: 2
- `apps_lic/reasoning/LicHealingOrchestrator.py` (replay_key chain)
- `agentic_core/L2_execution/healers/healing_tier_router.py` (hash validation)

**ADG Targets**:
- `signs_execution_trace` edges with replay_key
- `routes_through` edges with replay metadata

**Commands**:
```bash
# Step 1: Add replay_key chain to LicHealingOrchestrator
python tools/refactor/add_replay_key.py \
  --file LicHealingOrchestrator.py \
  --chain-type ancestry \
  --emit-to-trace

# Step 2: Add hash validation to healing_tier_router
python tools/refactor/add_hash_validation.py \
  --file healing_tier_router.py \
  --validate blueprint_hash,policy_hash

# Validate
pytest tests/architecture/test_replay_key_chain.py -v
```

**Evidence**:
- [ ] LicHealingOrchestrator generates replay_key
- [ ] Ancestry chain includes parent replay_key
- [ ] healing_tier_router validates blueprint_hash
- [ ] healing_tier_router validates policy_hash
- [ ] Replay trace shows continuous lineage

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify replay_key in execution trace
edges = client.adg_edge_fanout("apps_lic.reasoning.LicHealingOrchestrator", "signs_execution_trace")
replay_edges = [e for e in edges if 'replay' in str(e.get('metadata', {})).lower()]
assert len(replay_edges) >= 1, "M7.2: LicHealingOrchestrator missing replay_key"
```

**Wave 7 Completion**: Hash continuity wired across L3/L2, all files propagate replay_key and hashes

---

## Wave 8 — L3 Orchestration Fixes

### Microwave M8.1: Sovereign RAG Orchestrator Validation (ORCH-1)
**Scope**: Add replay validation to RAG orchestrator
**Files**: 2
- `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`
- `agentic_core/L3_orchestration/validators/replay_validator.py` (create)

**ADG Targets**:
- `pulls_context` edges with validated flag
- `applies_guardrail` edges for replay validation

**Commands**:
```bash
# Step 1: Create replay validator
python tools/codegen/create_replay_validator.py \
  --output agentic_core/L3_orchestration/validators/replay_validator.py

# Step 2: Add replay validation to RAG orchestrator
python tools/refactor/add_replay_validation.py \
  --file sovereign_rag_orchestrator.py \
  --validator agentic_core.L3_orchestration.validators.replay_validator

# Step 3: Integrate with context pull
python tools/refactor/validate_context_pull.py \
  --file sovereign_rag_orchestrator.py \
  --validation-type replay

# Validate
pytest tests/L3_orchestration/test_sovereign_rag_replay.py -v
```

**Evidence**:
- [ ] ReplayValidator class created
- [ ] RAG orchestrator validates replay on context pull
- [ ] Invalid replay triggers explicit error disposition
- [ ] Validated context includes replay_key metadata

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify pulls_context with validation
edges = client.adg_edge_fanout(
    "agentic_core.L3_orchestration.engines.sovereign_rag_orchestrator.SovereignRAGOrchestrator",
    "pulls_context"
)
assert len(edges) >= 1, "M8.1: RAG orchestrator missing pulls_context"
```

---

### Microwave M8.2: Reflexion Engine Policy Freeze (ORCH-2)
**Scope**: Add policy_hash freeze to reflexion engine
**Files**: 2
- `agentic_core/L3_orchestration/engines/reflexion_engine.py`
- `agentic_core/L3_orchestration/utils/policy_freezer.py` (create)

**ADG Targets**:
- `reads_policy_state` edges with freeze
- `applies_guardrail` edges for policy validation

**Commands**:
```bash
# Step 1: Create policy freezer utility
python tools/codegen/create_policy_freezer.py \
  --output agentic_core/L3_orchestration/utils/policy_freezer.py

# Step 2: Add policy_hash freeze to reflexion engine
python tools/refactor/add_policy_freeze.py \
  --file reflexion_engine.py \
  --freezer policy_freezer.py

# Step 3: Integrate with evaluation flow
python tools/refactor/add_policy_validation.py \
  --file reflexion_engine.py \
  --validate-at-checkpoint

# Validate
pytest tests/L3_orchestration/test_reflexion_policy_freeze.py -v
```

**Evidence**:
- [ ] PolicyFreezer utility created
- [ ] ReflexionEngine freezes policy_hash at entry
- [ ] Policy validation at evaluation checkpoints
- [ ] Policy changes trigger explicit re-evaluation

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify reads_policy_state
edges = client.adg_edge_fanout(
    "agentic_core.L3_orchestration.engines.reflexion_engine.ReflexionEngine",
    "reads_policy_state"
)
assert len(edges) >= 1, "M8.2: ReflexionEngine missing reads_policy_state"
```

**Wave 8 Completion**: L3 orchestrators validate replay and freeze policy, no unvalidated context pulls

---

## Wave 9 — Silent Fallback Removal

### Microwave M9.1: Add Explicit Disposition Gates to Routers (FALL-1)
**Scope**: Remove silent fallbacks from L0 routers
**Files**: 2
- `agentic_core/L0_routing/engines/ensemble_router.py`
- `agentic_core/L0_routing/engines/agentic_router.py`

**ADG Targets**:
- `routes_through` edges with disposition metadata
- Remove silent fallback patterns

**Commands**:
```bash
# Step 1: Add disposition gates to ensemble_router
python tools/refactor/add_disposition_gates.py \
  --file ensemble_router.py \
  --dispositions "ROUTE_CACHE,ROUTE_RAG,ROUTE_ACTION,ROUTE_FALLBACK,ROUTE_ERROR"

# Step 2: Add disposition gates to agentic_router
python tools/refactor/add_disposition_gates.py \
  --file agentic_router.py \
  --dispositions "ROUTE_DIRECT,ROUTE_DELEGATED,ROUTE_ERROR"

# Step 3: Replace silent fallbacks with explicit
python tools/refactor/remove_silent_fallbacks.py \
  --files wave9_router_files.txt

# Validate
pytest tests/L0_routing/test_explicit_disposition.py -v
```

**Evidence**:
- [ ] All routing decisions have explicit disposition
- [ ] Silent fallback patterns removed
- [ ] Error cases explicitly logged with codes
- [ ] Route metadata includes disposition reason

**Completion Gate**:
```python
from tools.adg.core.adg_mcp_client import AdgMcpClient
client = AdgMcpClient()
# Verify routes_through with disposition
for router in ['ensemble_router.py', 'agentic_router.py']:
    nodes = client.adg_nodes_by_file(f"agentic_core/L0_routing/engines/{router}")
    for node in nodes:
        edges = client.adg_edge_fanout(node['id'], "routes_through")
        # Check edges have disposition metadata
        disp_edges = [e for e in edges if e.get('metadata', {}).get('disposition')]
        assert len(disp_edges) >= 1, f"M9.1: {router} missing disposition metadata"
```

---

### Microwave M9.2: Telemetry Fallback Cleanup (FALL-2)
**Scope**: Remove silent fallbacks from telemetry
**Files**: 2
- `agentic_core/L0_routing/logs/telemetry_events.ndjson` (config)
- `agentic_core/L0_routing/telemetry/telemetry_dispatcher.py` (if exists)

**ADG Targets**:
- `emits_metric_event` edges with explicit error codes
- Remove implicit fallback logging

**Commands**:
```bash
# Step 1: Audit telemetry events for silent fallbacks
python tools/analysis/find_silent_telemetry.py \
  --config telemetry_events.ndjson \
  --output wave9_telemetry_issues.json

# Step 2: Replace silent fallbacks with explicit error codes
python tools/refactor/fix_telemetry_fallbacks.py \
  --issues-file wave9_telemetry_issues.json \
  --add-explicit-codes

# Step 3: Update telemetry dispatcher if present
python tools/refactor/add_telemetry_gates.py \
  --file telemetry_dispatcher.py \
  --explicit-error-handling

# Validate
pytest tests/L0_routing/test_telemetry_explicit.py -v
```

**Evidence**:
- [ ] All telemetry events have explicit event_type
- [ ] Error telemetry includes error_code field
- [ ] No implicit/blanket exception handlers
- [ ] Each fallback path explicitly documented

**Completion Gate**:
```python
# Check telemetry events have error codes
import json
with open('agentic_core/L0_routing/logs/telemetry_events.ndjson') as f:
    for line in f:
        event = json.loads(line)
        if event.get('level') == 'error':
            assert 'error_code' in event, f"M9.2: Error event missing error_code: {event}"
```

**Wave 9 Completion**: All L0 routing has explicit disposition, no silent telemetry fallbacks

---

## Wave 10 — Remaining Gaps + Validation

### Microwave M10.1: Close G-L1/G-L2 Gaps (AUD-1)
**Scope**: Fix L1/L2 layer violations
**Files**: 3
- `agentic_core/L1_cognition/engines/strategist_bio_writer.py` (remove writes)
- `agentic_core/L2_execution/healers/healing_tier_router.py` (add hash validation)
- `agentic_core/L2_execution/engines/tool_intent_executor.py` (add replay validation)

**Commands**:
```bash
# Step 1: Remove writes from L1 bio writer
python tools/refactor/remove_l1_writes.py --file strategist_bio_writer.py

# Step 2: Add hash validation to healing tier router
python tools/refactor/add_hash_validation.py --file healing_tier_router.py

# Step 3: Add replay validation to tool executor
python tools/refactor/add_replay_validation.py --file tool_intent_executor.py

# Validate
pytest tests/L1_cognition/test_no_writes.py -v
pytest tests/L2_execution/test_hash_validation.py -v
```

**Completion Gate**: All G-L1 and G-L2 gaps closed (verified by ADG)

---

### Microwave M10.2: Close G-L5/G-L6 Gaps (AUD-2)
**Scope**: Fix L5/L6 layer violations
**Files**: 3
- `agentic_core/L5_safety/validators/direct_prompt_compilation_validator.py` (remove side-effects)
- `agentic_core/L6_observability/engines/auto_persistence_adapter.py` (evidence-only fix)
- `agentic_core/L5_safety/enforcement/policy_enforcer.py` (add missing gate if needed)

**Commands**:
```bash
# Step 1: Remove side-effects from L5 validator
python tools/refactor/remove_validator_writes.py --file direct_prompt_compilation_validator.py

# Step 2: Fix L6 evidence-only violation
python tools/refactor/fix_l6_evidence.py --file auto_persistence_adapter.py

# Step 3: Add missing L5 gate
python tools/refactor/add_missing_gate.py --file policy_enforcer.py

# Validate
pytest tests/L5_safety/test_no_side_effects.py -v
pytest tests/L6_observability/test_evidence_only.py -v
```

**Completion Gate**: All G-L5 and G-L6 gaps closed

---

### Microwave M10.3: Close Package-Wide Gaps (AUD-3)
**Scope**: Fix remaining apps_* package gaps
**Files**: 5
- `apps_rg/` - L2 facades
- `apps_exec/` - L2 contracts
- `apps_eval/` - Shadow eval compliance
- `apps_research/` - C0 retrieval separation
- `apps_rfp/` - Prompt assembly separation

**Commands**:
```bash
# Step 1: Add facades to apps_rg
python tools/refactor/add_facades.py --package apps_rg --facade apps_shared.gateways.AgenticCoreFacade

# Step 2: Implement L2 contracts in apps_exec
python tools/refactor/implement_l2_contracts.py --package apps_exec

# Step 3: Verify shadow eval in apps_eval
python tools/analysis/verify_shadow_eval.py --package apps_eval

# Step 4: Separate C0 retrieval in apps_research
python tools/refactor/separate_retrieval.py --package apps_research

# Step 5: Separate PA in apps_rfp
python tools/refactor/separate_prompt_assembly.py --package apps_rfp

# Validate
python tools/validate/verify_package_compliance.py --packages apps_rg,apps_exec,apps_eval,apps_research,apps_rfp
```

**Completion Gate**: All G-APPS gaps closed

---

### Microwave M10.4: Create ADG Compliance Scanner (AUD-4)
**Scope**: Build continuous compliance validation
**Files**: 1 (create)
- `tools/adg/architecture_compliance_scanner.py`

**Commands**:
```bash
# Step 1: Create compliance scanner
python tools/codegen/create_compliance_scanner.py \
  --gaps-file docs/audits/architecture_gap_matrix.csv \
  --output tools/adg/architecture_compliance_scanner.py

# Step 2: Add ADG validation queries
python tools/refactor/add_adg_queries.py --file architecture_compliance_scanner.py

# Step 3: Add CI integration
python tools/refactor/add_ci_integration.py --scanner-file architecture_compliance_scanner.py

# Validate
python tools/adg/architecture_compliance_scanner.py --full-audit --output artifacts/compliance_report.json
```

**Evidence**:
- [ ] Compliance scanner operational
- [ ] Scans all 50 gaps
- [ ] Generates compliance_report.json
- [ ] CI gate blocks non-compliant changes
- [ ] Compliance score >= 95%

**Completion Gate**:
```python
import json
with open('artifacts/compliance_report.json') as f:
    report = json.load(f)
    assert report['critical_violations'] == 0, f"M10.4: {report['critical_violations']} critical violations"
    assert report['compliance_score'] >= 95, f"M10.4: Score {report['compliance_score']}% < 95%"
```

**Wave 10 Completion**: All 50 gaps closed, compliance scanner operational, final validation passed

---

## Implementation Commands (Full Sequence)

```bash
# ============================================
# PRE-FLIGHT: Setup
# ============================================
python tools/adg/regenerate_full_adg.py
git tag checkpoint-pre-wave1

# ============================================
# WAVE 1: Emergency Hardening (M1.1, M1.2)
# ============================================
python ops_scripts/wave1_emergency_prohibition.py --apply
python tools/adg/regenerate_full_adg.py
python tools/validate/wave1_validator.py --pass-gate || git checkout checkpoint-pre-wave1
git tag checkpoint-pre-wave2

# ============================================
# WAVE 2: Critical UWG Integration (M2.1, M2.2, M2.3)
# ============================================
python tools/refactor/add_mixin.py --files wave2_types_files.txt --mixin WriteGovernorMixin
python tools/adg/regenerate_full_adg.py
python tools/validate/wave2_microwave1_validator.py --pass-gate || git checkout checkpoint-pre-wave2-m1

python tools/refactor/add_mixin.py --files wave2_reasoning_files.txt --mixin WriteGovernorMixin
python tools/adg/regenerate_full_adg.py
python tools/validate/wave2_microwave2_validator.py --pass-gate || git checkout checkpoint-pre-wave2-m2

python tools/refactor/add_mixin.py --files wave2_utils_interpreter_files.txt --mixin WriteGovernorMixin
python tools/adg/regenerate_full_adg.py
python tools/validate/wave2_microwave3_validator.py --pass-gate || git checkout checkpoint-pre-wave2-m3
git tag checkpoint-pre-wave3

# Continue pattern for Waves 3-10...
# Each microwave gets its own checkpoint

# ============================================
# FINAL VALIDATION
# ============================================
python tools/adg/architecture_compliance_scanner.py --full-audit --fail-on-critical
```

---

## Rollback Strategy

**Per-Microwave Rollback**:
1. Microwave fails validation → `git checkout checkpoint-pre-wave{N}-m{M}`
2. Fix in isolation
3. Retry microwave → new checkpoint on success

**Per-Wave Rollback**:
1. Wave fails → `git checkout checkpoint-pre-wave{N}`
2. Replan wave with adjusted microwaves
3. Retry from wave start

**Full Rollback**:
1. All waves fail → `git checkout checkpoint-pre-wave1`
2. Emergency mode → keep runtime prohibition only
3. Replan with smaller microwaves

**Emergency Circuit Breaker**:
```python
from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import uninstall_uwg_interceptor
uninstall_uwg_interceptor()  # Restores original file operations
```

---

## Success Criteria Summary

| Wave | Microwave | Target | Verification |
|------|-----------|--------|--------------|
| W1 | M1.1 | `blocks_direct_write` = 7 | ADG prohibition edges |
| W1 | M1.2 | Shim intercepts | builtins.open test |
| W2 | M2.1-M2.3 | `writes_through` = 7 | ADG write edges |
| W3 | M3.1-M3.2 | `writes_via_uwg` = 4 | ADG L4 edges |
| W4 | M4.1-M4.3 | agentic_core→apps_* = 0 | grep + ADG |
| W5 | M5.1-M5.3 | `routes_through` = 12 | ADG facade edges |
| W6 | M6.1-M6.3 | `validated_by_safety_plane` = 3 | ADG HITL edges |
| W7 | M7.1-M7.2 | `signs_execution_trace` with hash = 4 | ADG hash edges |
| W8 | M8.1-M8.2 | `pulls_context` validated = 2 | ADG replay edges |
| W9 | M9.1-M9.2 | explicit disposition = 3 | ADG route edges |
| W10 | M10.1-M10.4 | compliance_score >= 95% | Scanner report |

---

**End of Detailed Wave & Microwave Plan**
