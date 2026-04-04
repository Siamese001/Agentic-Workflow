# Architecture Remediation Plan

**Repository:** C:\Git\Agentic-Workflow  
**Generated:** 2026-04-03  
**Based on:** architecture_gap_audit.md + architecture_gap_matrix.csv  

---

## Remediation Overview

| Phase | Duration | Focus | Key Deliverables |
|-------|----------|-------|------------------|
| Emergency Hardening | 2 weeks | Block violations | Runtime prohibition, circuit breakers |
| UWG Integration | 4 weeks | Write path compliance | UWG facades, WriteGovernorMixin |
| Layer Isolation | 3 weeks | Break coupling | Remove cross-layer imports |
| L5 Enforcement | 2 weeks | HITL security | Re-clearance gates, airlock |
| Validation | 1 week | Compliance verification | ADG scanner, test suite |

**Total Duration:** 12 weeks (parallel tracks possible for 8-week timeline)

---

## Phase 1: Emergency Hardening (Weeks 1-2)

**Goal:** Block critical violations immediately without full refactoring

### Week 1: Runtime Prohibition Extension

**Task 1.1: Extend Mutation Prohibition to apps_***
```python
# File: agentic_core/L0_routing/enforcement/mutation_prohibition.py
# Add to FORBIDDEN_WRITE_LAYERS:
FORBIDDEN_WRITE_LAYERS: frozenset[str] = frozenset({"L0", "L4", "L6", "apps_lic", "apps_rg", "apps_exec"})
```

**Action:**
1. Modify `assert_no_persistent_write()` to detect apps_* package paths
2. Add stack inspection to identify caller package
3. Raise `PermissionError` for any write from apps_* without UWG

**Files Modified:**
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py`
- `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py`

**Validation:**
```bash
python -c "from apps_lic.types.lic_vector_memory_types import VectorMemory; vm = VectorMemory(); vm.persist()"
# Should raise: PermissionError: MUTATION_PROHIBITED:layer=apps_lic
```

---

### Week 2: UWG Shim Injection

**Task 1.2: Create UWG Interceptor Shim**

Create file: `agentic_core/L2_execution/enforcement/uwg_interceptor_shim.py`

```python
"""Emergency shim to intercept file operations and route through UWG."""

import builtins
from pathlib import Path
from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway

_original_open = builtins.open
_original_path_write_text = Path.write_text
_original_path_write_bytes = Path.write_bytes

def _intercepted_open(file, mode='r', *args, **kwargs):
    """Intercept file open in write mode, route through UWG."""
    if 'w' in mode or 'a' in mode:
        # Check if caller is from apps_* and not going through UWG
        gateway = get_write_gateway()
        if gateway.replay_mode:
            return _original_open(file, mode, *args, **kwargs)
        # Route through UWG write_file instead
        return _UwgFileProxy(file, mode)
    return _original_open(file, mode, *args, **kwargs)

def install_uwg_interceptor():
    """Install interceptor globally (emergency use only)."""
    builtins.open = _intercepted_open
    Path.write_text = _intercepted_write_text
    Path.write_bytes = _intercepted_write_bytes
```

**Action:**
1. Implement shim that intercepts all file operations
2. Route intercepted writes through `get_write_gateway().write_through()`
3. Install at system startup for emergency mode

**Files Created:**
- `agentic_core/L2_execution/enforcement/uwg_interceptor_shim.py`

**Risk:** Performance degradation (estimated 20-30% write slowdown)

---

## Phase 2: UWG Integration (Weeks 3-6)

**Goal:** Proper UWG integration throughout apps_* packages

### Week 3-4: WriteGovernorMixin Rollout

**Task 2.1: Add Mixin to apps_lic Agents**

For each agent in `apps_lic/reasoning/`:

```python
# Before:
class OutreachLearningAgent:
    def persist_state(self, data):
        with open("state.json", "w") as f:
            json.dump(data, f)

# After:
from agentic_core.L2_execution.enforcement.write_governor_mixin import WriteGovernorMixin

class OutreachLearningAgent(WriteGovernorMixin):
    def persist_state(self, data):
        self.governed_write("state.json", json.dumps(data))
```

**Files to Modify:**
1. `apps_lic/reasoning/OutreachLearningAgent.py`
2. `apps_lic/reasoning/LicHealingOrchestrator.py`
3. `apps_lic/reasoning/LicCodeInterpreter.py`
4. `apps_lic/reasoning/OutreachSignalRouterAgent.py`
5. `apps_lic/reasoning/ExecutiveStrategyAgent.py`
6. `apps_lic/reasoning/GovernanceShieldAgent.py`
7. `apps_lic/reasoning/HOPPipelineExecutor.py`
8. `apps_lic/reasoning/ValidatorAgent.py`

**Validation:**
```python
# Test that governed_write is called
with patch.object(WriteGovernorMixin, 'governed_write') as mock_write:
    agent = OutreachLearningAgent()
    agent.persist_state({"test": "data"})
    mock_write.assert_called_once()
```

---

### Week 5-6: L4 Storage Provider UWG Injection

**Task 2.2: Refactor L4 State Storage**

```python
# File: agentic_core/L4_state/storage/filesystem_store.py
# Before:
class FilesystemStore:
    def write(self, key: str, data: bytes) -> None:
        path = self._resolve_path(key)
        path.write_bytes(data)  # Direct write!

# After:
from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway

class FilesystemStore:
    def __init__(self, uwg_gateway=None):
        self._uwg = uwg_gateway or get_write_gateway()
    
    def write(self, key: str, data: bytes, *, replay_key: str, signature: str, plan_hash: str) -> None:
        path = self._resolve_path(key)
        self._uwg.write_to_store(self._store, path, data, 
                                 replay_key=replay_key, 
                                 signature=signature,
                                 plan_hash=plan_hash)
```

**Files to Modify:**
1. `agentic_core/L4_state/storage/filesystem_store.py`
2. `agentic_core/L4_state/memory/blob_storage_provider.py`
3. `agentic_core/L4_state/authority/memory_authority.py`
4. `agentic_core/L4_state/authority/run_scoped_state_authority.py`

**Dependencies:**
- UWG must support 4-field requirement (replay_key, signature, plan_hash, store)
- All L4 callers must provide hash chain

---

## Phase 3: Layer Isolation (Weeks 7-9)

**Goal:** Break bidirectional cross-layer coupling

### Week 7: Remove agentic_core → apps_* Imports

**Task 3.1: Break Circular Dependencies**

**File:** `agentic_core/utils/workflow_engines/apps_engines_aliases.py`

**Options:**
1. **Option A (Recommended):** Move to `apps_shared/compat/apps_engines_aliases.py`
2. **Option B:** Delete and update all importers
3. **Option C:** Convert to dynamic import with deprecation warning

**Implementation:**
```python
# New location: apps_shared/compat/apps_engines_aliases.py
import warnings

warnings.warn(
    "apps_engines_aliases is deprecated. Use direct imports from apps_lic.reasoning.*",
    DeprecationWarning,
    stacklevel=2
)

# Aliases remain for backward compatibility
from apps_lic.reasoning.CampaignBalanceAgent import CampaignBalanceAgent
# ... etc
```

**Files to Update:**
- All 25 files importing from `agentic_core.utils.workflow_engines.apps_engines_aliases`
- Found in: `agentic_core/L5_safety/`, `agentic_core/L0_routing/`, `agentic_core/L3_orchestration/`

---

### Week 8: Create L2 Facade Layer

**Task 3.2: Implement L2ExecutionAgent Facades**

Create file: `apps_shared/gateways/agentic_core_facade.py`

```python
"""L2 Facade for apps_* → agentic_core access.

All apps_* access to agentic_core must go through this facade.
Enforces L2 execution contract and UWG mediation.
"""

from agentic_core.L2_execution.contracts.l2_execution_contract import L2ExecutionAgent
from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway

class AgenticCoreFacade(L2ExecutionAgent):
    """L2-wrapped facade for agentic_core access."""
    
    def __init__(self):
        super().__init__(agent_id="AgenticCoreFacade")
        self._uwg = get_write_gateway()
    
    def l2_init(self, context):
        """Initialize with UWG binding."""
        context.metadata['uwg'] = self._uwg
        return L2PhaseResult(phase=L2ExecutionPhase.INIT, success=True)
    
    def l2_execute(self, context):
        """Execute core operation with UWG mediation."""
        operation = context.inputs.get('operation')
        # Route through UWG
        return L2PhaseResult(phase=L2ExecutionPhase.EXECUTE, success=True)
    
    def l2_synthesize(self, context):
        """Synthesize result with trace metadata."""
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE, 
            success=True,
            metadata={'replay_key': self._generate_replay_key(context)}
        )
```

**Files Created:**
- `apps_shared/gateways/agentic_core_facade.py`
- `apps_shared/gateways/l2_gateway_base.py`
- `apps_shared/gateways/__init__.py`

---

### Week 9: Route apps_* Calls Through Facade

**Task 3.3: Update apps_lic to Use Facade**

```python
# File: apps_lic/utils/lic_agent_base_util.py
# Before:
from agentic_core.adg.analysis.layer_authority import LayerAuthorityChecker

# After:
from apps_shared.gateways.agentic_core_facade import AgenticCoreFacade

def check_layer_authority(layer):
    facade = AgenticCoreFacade()
    return facade.execute_operation('check_authority', layer=layer)
```

**Files to Modify:**
- `apps_lic/utils/lic_agent_base_util.py` (10 imports)
- `apps_lic/engines/lic_spine_adapter.py` (6 imports)
- `apps_lic/reasoning/OutreachSignalRouterAgent.py` (6 imports)
- `apps_lic/reasoning/LicHealingOrchestrator.py` (5 imports)
- All other apps_* files with agentic_core imports

---

## Phase 4: L5 Enforcement (Weeks 10-11)

**Goal:** Implement HITL re-clearance and exit control

### Week 10: L5ReClearanceGate Implementation

**Task 4.1: Create Re-Clearance Gate**

Create file: `agentic_core/L5_safety/enforcement/hitl_re_clearance_gate.py`

```python
"""L5 Re-Clearance Gate for HITL modifications.

Canonical requirement: No human change bypasses L5 re-clear.
Implements the HITL Airlock + Re-Clearance flow.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class ReClearanceStatus(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    MODIFIED = auto()  # Requires another pass

@dataclass(frozen=True)
class ReClearanceDecision:
    status: ReClearanceStatus
    reason_code: str
    modified_diff: Optional[dict] = None
    policy_validation_hash: str = ""
    l5_signature: str = ""

class L5ReClearanceGate:
    """Gate that validates human modifications before execution."""
    
    def __init__(self, policy_validator, signature_verifier):
        self._policy_validator = policy_validator
        self._signature_verifier = signature_verifier
    
    def re_clear_human_modification(
        self,
        original_proposal: dict,
        human_modification: dict,
        human_identity: str,
        policy_context: dict,
        blueprint_hash: str,
        policy_hash: str
    ) -> ReClearanceDecision:
        """
        Re-clear human modification through L5.
        
        Canonical flow:
        1. Materialize packet with evidence
        2. Validate modification against policy
        3. Check blueprint_hash/policy_hash continuity
        4. Generate L5 signature if approved
        5. Return decision with diff
        """
        # Step 1: Compute diff
        diff = self._compute_diff(original_proposal, human_modification)
        
        # Step 2: Policy validation
        policy_result = self._policy_validator.validate_diff(
            diff, 
            policy_context,
            blueprint_hash=blueprint_hash,
            policy_hash=policy_hash
        )
        
        if not policy_result.is_valid:
            return ReClearanceDecision(
                status=ReClearanceStatus.REJECTED,
                reason_code=policy_result.rejection_reason
            )
        
        # Step 3: Generate signature
        l5_sig = self._signature_verifier.sign_modification(
            diff, 
            human_identity,
            blueprint_hash,
            policy_hash
        )
        
        # Step 4: Return approved decision
        return ReClearanceDecision(
            status=ReClearanceStatus.APPROVED,
            reason_code="L5_RE_CLEARANCE_APPROVED",
            modified_diff=diff,
            policy_validation_hash=policy_result.validation_hash,
            l5_signature=l5_sig
        )
```

**Files Created:**
- `agentic_core/L5_safety/enforcement/hitl_re_clearance_gate.py`
- `agentic_core/L5_safety/enforcement/hitl_airlock.py`

---

### Week 11: Integrate Re-Clearance into HITL Paths

**Task 4.2: Update HITL Orchestrators**

```python
# File: apps_lic/reasoning/LicHealingOrchestrator.py
# Add to healing flow:

from agentic_core.L5_safety.enforcement.hitl_re_clearance_gate import L5ReClearanceGate

class LicHealingOrchestrator:
    def handle_hitl_intervention(self, proposal, human_input):
        # Canonical: HITL requires L5 re-clearance
        gate = L5ReClearanceGate()
        
        decision = gate.re_clear_human_modification(
            original_proposal=proposal,
            human_modification=human_input,
            human_identity=self._get_human_identity(),
            policy_context=self._get_active_policy(),
            blueprint_hash=self._get_blueprint_hash(),
            policy_hash=self._get_policy_hash()
        )
        
        if decision.status == ReClearanceStatus.REJECTED:
            self._escalate_to_denial(decision.reason_code)
            return
        
        if decision.status == ReClearanceStatus.APPROVED:
            # Only proceed with L5-approved diff
            self._restart_with_approved_diff(
                decision.modified_diff,
                l5_signature=decision.l5_signature
            )
```

**Files to Modify:**
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_rg/reasoning/RgHealingOrchestrator.py`

---

## Phase 5: Validation (Week 12)

**Goal:** Verify compliance and establish continuous monitoring

### Task 5.1: ADG-Based Compliance Scanner

Create file: `tools/adg/architecture_compliance_scanner.py`

```python
"""ADG-based architecture compliance scanner.

Validates repository against canonical architecture invariants.
"""

from tools.adg.core.adg_mcp_client import AdgMcpClient

class ArchitectureComplianceScanner:
    """Scanner for architecture gap detection."""
    
    def scan_direct_writes(self) -> list[Violation]:
        """Find writes outside UWG."""
        # Query ADG for writes_through edges
        # Compare to all file write operations
        pass
    
    def scan_cross_layer_imports(self) -> list[Violation]:
        """Find bidirectional layer coupling."""
        # Query ADG for imports relation
        # Identify agentic_core <-> apps_* cycles
        pass
    
    def scan_missing_re_clearance(self) -> list[Violation]:
        """Find HITL without L5 re-clearance."""
        # Query for HITL patterns without l5_signature
        pass
    
    def generate_compliance_report(self) -> dict:
        """Generate comprehensive compliance report."""
        return {
            'direct_writes': self.scan_direct_writes(),
            'cross_layer_imports': self.scan_cross_layer_imports(),
            'missing_re_clearance': self.scan_missing_re_clearance(),
            'compliance_score': self._compute_score()
        }
```

---

### Task 5.2: Continuous Compliance CI Gate

Add to `.github/workflows/architecture-compliance.yml`:

```yaml
name: Architecture Compliance

on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run ADG Compliance Scanner
        run: |
          python tools/adg/architecture_compliance_scanner.py \
            --fail-on-critical \
            --generate-report
      
      - name: Upload Compliance Report
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: artifacts/compliance_report.json
```

---

## Remediation Summary

| Gap ID | Remediation | Status Target | Owner |
|--------|-------------|---------------|-------|
| C1-001..007 | UWG Integration | Week 4 | L2 Execution Team |
| C2-001..006 | Layer Isolation | Week 9 | Architecture Team |
| C3-001..003 | L5 Re-Clearance | Week 11 | L5 Safety Team |
| C4-001..004 | L4 Storage Refactor | Week 6 | L4 State Team |
| G-L0-001..003 | Explicit Disposition | Week 2 | L0 Routing Team |
| G-APPS-001..006 | apps_* Compliance | Week 9 | Apps Team |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance degradation from UWG shim | High | Medium | Implement caching; benchmark weekly |
| Breaking changes to apps_* functionality | High | High | Feature flags; gradual rollout; rollback plan |
| L4 storage refactor data loss | Medium | Critical | Backup before migration; checksum validation |
| L5 re-clearance UX friction | Medium | Medium | Clear error messages; async processing |
| Circular dependency break cascade | High | Medium | Dependency graph analysis; staged removal |

---

## Success Criteria

**Phase 1:**
- [ ] All direct writes from apps_* raise PermissionError
- [ ] UWG shim intercepts 100% of file operations

**Phase 2:**
- [ ] 100% of L2 agents use WriteGovernorMixin
- [ ] L4 storage providers inject UWG
- [ ] All writes include replay_key, signature, plan_hash

**Phase 3:**
- [ ] Zero agentic_core → apps_* imports
- [ ] All apps_* → agentic_core calls go through L2 facade

**Phase 4:**
- [ ] HITL paths enforce L5 re-clearance
- [ ] Airlock pattern implemented

**Phase 5:**
- [ ] ADG scanner detects 0 CRITICAL violations
- [ ] CI gate blocks non-compliant changes
- [ ] Compliance score > 95%

---

## Rollback Procedures

**If UWG Shim Causes Critical Failures:**
```python
# Emergency rollback
from agentic_core.L2_execution.enforcement.uwg_interceptor_shim import uninstall_uwg_interceptor
uninstall_uwg_interceptor()  # Restores original builtins.open
```

**If Layer Isolation Breaks apps_***
```bash
# Revert to aliases
git revert HEAD~2 --agentic_core/utils/workflow_engines/apps_engines_aliases.py
```

---

**End of Remediation Plan**
