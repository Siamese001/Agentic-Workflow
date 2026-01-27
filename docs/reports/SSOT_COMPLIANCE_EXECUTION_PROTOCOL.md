# SOVEREIGN SSOT COMPLIANCE EXECUTION PROTOCOL

## Multi-Agent Orchestration for Structure Blueprint Alignment

**ROLE**: You are the Sovereign Architecture Orchestrator responsible for executing agents in the precise order required to achieve 100% SSOT compliance with `structure_blueprint.py`.

**EXECUTION SEQUENCE**: Execute the following agents in EXACT order on each subfolder, starting with `prompt_governance` and proceeding through all territories defined in `SOVEREIGN_REGISTRY`.

---

## PHASE 0: PRE-EXECUTION VALIDATION

**Step 0.1**: Verify SSOT Source

```python
# Confirm structure_blueprint.py is accessible and valid
import sys
import logging
from pathlib import Path

# Configure Sovereign Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SOVEREIGN] - %(levelname)s - %(message)s')
logger = logging.getLogger("SSOT_Orchestrator")

try:
    from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY, CORE_SUBFOLDER_MAP
    if not SOVEREIGN_REGISTRY:
        raise ValueError("SOVEREIGN_REGISTRY is empty. Critical SSOT failure.")
    logger.info(f"SSOT Loaded: {len(SOVEREIGN_REGISTRY)} territories defined")
except ImportError as e:
    logger.critical(f"Failed to load structure blueprint: {e}")
    sys.exit(1)
```

**Step 0.2**: Initialize Agent Registry

```python
# Import all required agents in execution order
try:
    from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent
    from agentic_core.L5_safety.validators.LocationAgent import LocationAgent  
    from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
    from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import ArchitectureGovernorAgent
    from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
    logger.info("All Sovereign Agents initialized successfully.")
except ImportError as e:
    logger.critical(f"Agent registry corruption detected: {e}")
    sys.exit(1)
```

---

## PHASE 1: TERRITORIAL DISCOVERY & DRIFT DETECTION

**Target**: `prompt_governance` (first territory)

**Step 1.1**: Execute FilesystemSSOTReconcilerAgent

```python
# PHASE 1.1: Detect drift between blueprint and reality
reconciler = FilesystemSSOTReconcilerAgent()
drift_report = reconciler.execute_detailed_analysis(
    target_path="agentic_core/prompt_governance",
    auto_apply=False  # Detection only first
)

print("🔍 DRIFT DETECTION RESULTS:")
print(f"  Missing folders: {len(drift_report['missing_folders'])}")
print(f"  Unauthorized folders: {len(drift_report['unauthorized_folders'])}")
print(f"  Structure violations: {len(drift_report['violations'])}")

logger.info("🔍 DRIFT DETECTION RESULTS:")
logger.info(f"  Missing folders: {len(drift_report.get('missing_folders', []))}")
logger.info(f"  Unauthorized folders: {len(drift_report.get('unauthorized_folders', []))}")
logger.info(f"  Structure violations: {len(drift_report.get('violations', []))}")

# CRITICAL ANALYSIS: Immediate halt on catastrophic drift to prevent cascading errors
if len(drift_report.get('violations', [])) > 10:
    logger.critical("Excessive structural violations detected. Halting for manual review.")
    sys.exit(1)
```

**Step 1.2**: Validate Territory Compliance

```python
# PHASE 1.2: LocationAgent validates territorial boundaries
location_validator = LocationAgent(root_path=Path("agentic_core"))
location_report = location_validator.validate_territory_compliance(
    territory="prompt_governance"
)

print("📍 TERRITORIAL VALIDATION:")
print(f"  Depth compliance: {location_report['depth_valid']}")
print(f"  Boundary compliance: {location_report['boundaries_valid']}")
print(f"  Root protection: {location_report['root_protected']}")

logger.info("📍 TERRITORIAL VALIDATION:")
logger.info(f"  Depth compliance: {location_report['depth_valid']}")
logger.info(f"  Boundary compliance: {location_report['boundaries_valid']}")

if not location_report['root_protected']:
    logger.critical("ROOT PROTECTION BREACHED. Immediate lockdown required.")
    sys.exit(1)
```

---

## PHASE 2: STRUCTURAL ALIGNMENT

**Step 2.1**: Execute HierarchyAgent for Structure Creation

```python
# PHASE 2.1: Create missing L2/L3 structure
hierarchy_agent = HierarchyAgent()
structure_proposal = hierarchy_agent.analyze_and_propose(
    target_path="agentic_core/prompt_governance",
    blueprint_reference=CORE_SUBFOLDER_MAP.get('prompt_governance', {})
)

print("🏗️ STRUCTURE PROPOSAL:")
print(f"  Folders to create: {len(structure_proposal['create_folders'])}")
print(f"  Files to relocate: {len(structure_proposal['relocate_files'])}")
print(f"  Cleanup actions: {len(structure_proposal['cleanup_actions'])}")

logger.info("🏗️ STRUCTURE PROPOSAL:")
logger.info(f"  Folders to create: {len(structure_proposal['create_folders'])}")
logger.info(f"  Files to relocate: {len(structure_proposal['relocate_files'])}")

if not structure_proposal:
    logger.warning("No structure proposal generated (possible agent failure).")
```

**Step 2.2**: Apply Structural Changes (with confirmation)

```python
# PHASE 2.2: Execute structural alignment
if structure_proposal['has_changes']:
    # CRITICAL: Force interactive confirmation unless overridden by strict ENV flag
    confirmation = input("⚠️ Apply structural changes? Type 'EXECUTE' to confirm: ")
    if confirmation == 'EXECUTE':
        alignment_result = hierarchy_agent.execute_structure_alignment(
            proposal=structure_proposal,
            auto_apply=True
        )
        if not alignment_result['success']:
            logger.error(f"Alignment failed: {alignment_result.get('error', 'Unknown error')}")
            sys.exit(1)
        logger.info(f"✅ Alignment completed successfully.")
    else:
        logger.warning("⏸️ Structural alignment skipped by user.")
```

---

## PHASE 3: ARCHITECTURAL VALIDATION

**Step 3.1**: Execute ArchitectureGovernorAgent

```python
# PHASE 3.1: Universal architecture governance
arch_governor = ArchitectureGovernorAgent()
governance_report = arch_governor.comprehensive_territory_audit(
    target_territories=["prompt_governance"],
    check_layer_boundaries=True,
    check_naming_conventions=True,
    check_orphaned_agents=True
)

print("🛡️ ARCHITECTURE GOVERNANCE RESULTS:")
print(f"  Layer boundary violations: {len(governance_report['layer_violations'])}")
print(f"  Naming violations: {len(governance_report['naming_violations'])}")
print(f"  Orphaned agents: {len(governance_report['orphaned_agents'])}")

logger.info("🛡️ ARCHITECTURE GOVERNANCE RESULTS:")

violations_count = (len(governance_report['layer_violations']) + 
                    len(governance_report['naming_violations']))
                    
if violations_count > 0:
    logger.error(f"❌ FOUND {violations_count} ARCHITECTURE VIOLATIONS")
else:
    logger.info("✅ No architecture violations found.")
```

**Step 3.2**: Execute SystemArchitectAgent

```python
# PHASE 3.2: Core architecture integrity check
system_architect = SystemArchitectAgent()
architecture_report = system_architect.validate_core_architecture(
    target_path="agentic_core/prompt_governance"
)

print("🏛️ CORE ARCHITECTURE VALIDATION:")
print(f"  Import structure valid: {architecture_report['imports_valid']}")
print(f"  Module dependencies valid: {architecture_report['dependencies_valid']}")
print(f"  Design patterns compliant: {architecture_report['patterns_compliant']}")

logger.info("🏛️ CORE ARCHITECTURE VALIDATION:")

if not architecture_report['imports_valid']:
    logger.error("Invalid import structure detected in core modules.")
    # Critical fail for imports as this breaks runtime
    sys.exit(1)
```

---

## PHASE 4: HEALING & CORRECTION

**Step 4.1**: Auto-Heal Detected Violations

```python
# PHASE 4.1: Execute healing for detected issues
healing_plan = arch_governor.generate_healing_plan(governance_report)

if healing_plan['requires_healing']:
    print("🔧 HEALING PLAN GENERATED:")
    print(f"  Naming fixes: {len(healing_plan['naming_fixes'])}")
    print(f"  Structure fixes: {len(healing_plan['structure_fixes'])}")
    print(f"  Import fixes: {len(healing_plan['import_fixes'])}")
    
    logger.info("🔧 HEALING PLAN GENERATED:")
    logger.info(f"  Naming fixes: {len(healing_plan['naming_fixes'])}")
    
    healing_confirmation = input("Execute healing plan? (y/N): ")
    if healing_confirmation.lower() == 'y':
        healing_result = arch_governor.execute_healing_plan(healing_plan)
        logger.info(f"✅ Healing completed: {healing_result['success']}")
        
        # Re-verify immediately after healing
        post_heal_audit = arch_governor.comprehensive_territory_audit(["prompt_governance"])
        if post_heal_audit['violations']:
            logger.critical("Healing failed to resolve all violations.")
            sys.exit(1)
```

---

## PHASE 5: FINAL VALIDATION & LOCKDOWN

**Step 5.1**: Post-Compliance Validation

```python
# PHASE 5.1: Re-run all validations to confirm compliance
final_reconciler = FilesystemSSOTReconcilerAgent()
final_drift_check = final_reconciler.execute_detailed_analysis(
    target_path="agentic_core/prompt_governance",
    auto_apply=False
)

final_location = LocationAgent(root_path=Path("agentic_core"))
final_location_check = final_location.validate_territory_compliance(
    territory="prompt_governance"
)

print("🎯 FINAL COMPLIANCE CHECK:")
print(f"  Drift resolved: {len(final_drift_check['violations']) == 0}")
print(f"  Location compliant: {final_location_check['overall_compliant']}")
print(f"  Architecture clean: {len(governance_report['violations']) == 0}")

logger.info("🎯 FINAL COMPLIANCE CHECK:")
drift_resolved = len(final_drift_check.get('violations', [])) == 0

if not drift_resolved:
    logger.critical("❌ FINAL VALIDATION FAILED: DRIFT STILL EXISTS")
    sys.exit(1)
    
logger.info("✅ Territory secured and compliant.")
```

**Step 5.2**: Generate Compliance Certificate

```python
# PHASE 5.2: Issue compliance certificate
import json

compliance_certificate = {
    'territory': 'prompt_governance',
    'timestamp': datetime.now().isoformat(),  # Ensure datetime is imported
    'ssot_version': 'structure_blueprint.py',
    'drift_free': drift_resolved,
    'architecturally_compliant': final_location_check['overall_compliant'],
    'agents_executed': [
        'FilesystemSSOTReconcilerAgent',
        'LocationAgent', 
        'HierarchyAgent',
        'ArchitectureGovernorAgent',
        'SystemArchitectAgent'
    ]
}

logger.info("📜 COMPLIANCE CERTIFICATE ISSUED:")
print(json.dumps(compliance_certificate, indent=2))
```

---

## PHASE 6: TERRITORIAL EXPANSION

**Repeat Phases 1-5 for each additional territory in SOVEREIGN_REGISTRY:**

```python
# Execute same sequence for all other territories
territories = [
    'agentic_core/base_agents',
    'agentic_core/L1_cognition', 
    'agentic_core/L2_execution',
    'agentic_core/L3_orchestration',
    'agentic_core/L4_state',
    'agentic_core/L5_safety',
    'agentic_core/L6_observability',
    'apps_lic',
    'apps_rg',
    # ... all other territories from SOVEREIGN_REGISTRY
]

for territory in territories:
    print(f"\n🚀 PROCESSING TERRITORY: {territory}")
    # Repeat Phases 1-5 for each territory
    execute_territory_compliance(territory)
```

---

## EXECUTION COMMANDS

**To run this orchestration:**

```bash
# Navigate to project root
cd c:/Git/Agentic-Workflow

# Execute the SSOT compliance protocol
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Execute the complete protocol above
exec(open('ssot_compliance_protocol.py').read())
"
```

**Critical Execution Rules:**

1. **NEVER skip phases** - each phase builds on the previous
2. **ALWAYS validate before healing** - ensure changes are safe
3. **CONFIRM major changes** - structural alignment requires approval
4. **DOCUMENT all actions** - maintain audit trail in L4 Ledger
5. **STOP on critical errors** - don't proceed with unresolved violations

**Expected Outcome**: 100% SSOT compliance across all territories with zero drift, perfect naming conventions, and architectural integrity maintained.
