$ git rev-parse HEAD
e196056593b12215c3518364b120da6453020662

$ python -c "
import ast
import re
from pathlib import Path
from collections import Counter

LAYER_ORDER = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6, 'L7': 7}
layer_pat = re.compile(r'L(\d)_')

def get_layer(path_str):
    m = layer_pat.search(path_str)
    return f'L{m.group(1)}' if m else None

def extract_imports(file_path):
    try:
        tree = ast.parse(file_path.read_text(encoding='utf-8', errors='replace'))
    except:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports

violations = []
for py_file in Path('agentic_core').rglob('*.py'):
    path_str = str(py_file).replace('\\\\', '/')
    source_layer = get_layer(path_str)
    if not source_layer:
        continue
    for imp in extract_imports(py_file):
        target_layer = get_layer(imp)
        if target_layer and LAYER_ORDER.get(target_layer, 99) > LAYER_ORDER.get(source_layer, 99):
            violations.append(imp)

print(f'UPWARD_VIOLATION_COUNT: {len(violations)}')
print()
print('TOP 15 UPWARD TARGETS:')
for i, (target, count) in enumerate(Counter(violations).most_common(15), 1):
    print(f'  {i:2}. [{count:3}] {target}')
"
UPWARD_VIOLATION_COUNT: 97

TOP 15 UPWARD TARGETS:
   1. [  4] agentic_core.L5_safety.reasoning.CodeValidatorAgent
   2. [  4] agentic_core.L5_safety.core_kernel.classification_kernel
   3. [  3] agentic_core.L5_safety.reasoning.NamingAgent
   4. [  3] agentic_core.L5_safety.reasoning.StructureEnforcerAgent
   5. [  3] agentic_core.L5_safety.enforcement.activation_gate
   6. [  3] agentic_core.L5_safety.reasoning.CodeEnforcerAgent
   7. [  3] agentic_core.L5_safety.validators.GovernanceAgent
   8. [  2] agentic_core.L3_orchestration.Orchestrator
   9. [  2] agentic_core.L5_safety.validators.healing_strategy
  10. [  2] agentic_core.L5_safety.validators.AutonomyGuardianAgent
  11. [  2] agentic_core.L4_state.reasoning.CheckpointManagerAgent
  12. [  2] agentic_core.L5_safety.validators.HygieneGuardianAgent
  13. [  2] agentic_core.L5_safety.validators.canonical_truth_validator
  14. [  2] agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent
  15. [  2] agentic_core.L4_state.reasoning.RedisSovereignAgent

$ git grep -n "agentic_core\.L5_safety\.reasoning\.CodeValidatorAgent" agentic_core/L0_* agentic_core/L1_* agentic_core/L2_* agentic_core/L3_* agentic_core/L4_* apps_* tests
agentic_core/L0_routing/scripts/check_syntax_util.py:10:from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py:17:from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py:214:    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent
agentic_core/L3_orchestration/enforcement/safety_strategy.py:85:                from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (

$ pre-commit run -a
T0: Trailing Whitespace..................................................Passed
T0: End-of-File Fixer....................................................Passed
T0: Enforce LF Line Endings..............................................Passed
T0: Check Merge Conflict Markers.........................................Passed
T1: Python Syntax Validation.............................................Passed
T2a: Ruff Lint & Auto-Fix................................................Passed
T2b: Ruff Format.........................................................Passed
T3a: Anti-Pattern Landmine Detection.....................................Passed
T3b: Report Location SSOT Check..........................................Passed
T3c: Reject Tracked Generated Artifacts..................................Passed
T3e: Pycache Purge.......................................................Passed
T3f: Module Collision Guard..............................................Passed
T3h: Evidence Contract Validator.........................................Passed
T3i: Guard pytest.ini scope changes......................................Passed
T3g: Governance Policy Validation........................................Passed
T3h: Guard apps_shared instructional layer imports.......................Passed

$ git grep -n "agentic_core\.L5_safety\.reasoning\.CodeValidatorAgent" agentic_core/L0_* agentic_core/L1_* agentic_core/L2_* agentic_core/L3_* agentic_core/L4_* || echo "NO LOWER-LAYER IMPORTS"
NO LOWER-LAYER IMPORTS

$ python -m pytest -q --tb=no
0.17s call     tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[DagRuntimeInspectorAgent]
0.03s call     tests/unit_min_deps/test_marker_registry_contract.py::TestAllUsedMarkersRegistered::test_no_unregistered_markers

(5 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 62 passed in 2.87s ==============================

$ python -c "
import ast
import re
from pathlib import Path
from collections import Counter

LAYER_ORDER = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6, 'L7': 7}
layer_pat = re.compile(r'L(\d)_')

def get_layer(path_str):
    m = layer_pat.search(path_str)
    return f'L{m.group(1)}' if m else None

def extract_imports(file_path):
    try:
        tree = ast.parse(file_path.read_text(encoding='utf-8', errors='replace'))
    except:
        return []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports

violations = []
for py_file in Path('agentic_core').rglob('*.py'):
    path_str = str(py_file).replace('\\\\', '/')
    source_layer = get_layer(path_str)
    if not source_layer:
        continue
    for imp in extract_imports(py_file):
        target_layer = get_layer(imp)
        if target_layer and LAYER_ORDER.get(target_layer, 99) > LAYER_ORDER.get(source_layer, 99):
            violations.append(imp)

print(f'UPWARD_VIOLATION_COUNT: {len(violations)}')
print()
print('TOP 15 UPWARD TARGETS:')
for i, (target, count) in enumerate(Counter(violations).most_common(15), 1):
    print(f'  {i:2}. [{count:3}] {target}')
"
UPWARD_VIOLATION_COUNT: 93

TOP 15 UPWARD TARGETS:
   1. [  4] agentic_core.L5_safety.core_kernel.classification_kernel
   2. [  3] agentic_core.L5_safety.reasoning.NamingAgent
   3. [  3] agentic_core.L5_safety.reasoning.StructureEnforcerAgent
   4. [  3] agentic_core.L5_safety.enforcement.activation_gate
   5. [  3] agentic_core.L5_safety.reasoning.CodeEnforcerAgent
   6. [  3] agentic_core.L5_safety.validators.GovernanceAgent
   7. [  2] agentic_core.L3_orchestration.Orchestrator
   8. [  2] agentic_core.L5_safety.validators.healing_strategy
   9. [  2] agentic_core.L5_safety.validators.AutonomyGuardianAgent
  10. [  2] agentic_core.L4_state.reasoning.CheckpointManagerAgent
  11. [  2] agentic_core.L5_safety.validators.HygieneGuardianAgent
  12. [  2] agentic_core.L5_safety.validators.canonical_truth_validator
  13. [  2] agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent
  14. [  2] agentic_core.L4_state.reasoning.RedisSovereignAgent
  15. [  2] agentic_core.L4_state.reasoning.PineconeSovereignAgent
