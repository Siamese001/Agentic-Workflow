# Sovereign Contract Guard - JSON Output Documentation

## Overview

The Sovereign Contract Guard test suite now outputs comprehensive JSON logs for integration with CI/CD pipelines and automated analysis tools.

## JSON Output Structure

### File Generation

- **Default filename**: `sovereign_contract_guard_YYYYMMDD_HHMMSS.json`
- **Custom filename**: Use `--json-output custom_name.json` parameter
- **Location**: Current working directory

### JSON Schema

```json
{
  "metadata": {
    "timestamp": "2026-01-29T11:29:08.941935",
    "test_suite": "SovereignContractGuard",
    "version": "1.0.0",
    "project_root": "C:\\Git\\Agentic-Workflow",
    "validators_dir": "C:\\Git\\Agentic-Workflow\\agentic_core\\L5_safety\\validators"
  },
  "summary": {
    "total_classes_found": 225,
    "total_classes_tested": 225,
    "import_validation": {
      "successful": 18,
      "failed": 207,
      "success_rate": 0.08,
      "missing_subatomic_mixin": 0
    },
    "signature_validation": {
      "valid": 0,
      "missing_heal_method": 225,
      "legacy_signatures": 0,
      "success_rate": 0.0
    },
    "mro_validation": {
      "valid": 11,
      "shadowing_detected": 11,
      "missing_mixins": 4,
      "success_rate": 0.0489
    },
    "mock_execution": {
      "successful": 4,
      "dict_returns": 4,
      "success_rate": 0.0178
    },
    "overall_success_rate": 0.0367
  },
  "detailed_results": {
    "import_validation": [...],
    "signature_validation": [...],
    "mro_audit": [...],
    "mock_execution": [...]
  },
  "failed_agents": {
    "import_failures": [
      {
        "class_name": "AgentFactory",
        "file_path": "C:\\Git\\Agentic-Workflow\\agentic_core\\L5_safety\\validators\\AgentFactoryAgent.py",
        "error": "No module named 'agentic_core.base_agents'",
        "error_line": 13,
        "missing_dependencies": ["agentic_core.base_agents"]
      }
    ],
    "signature_violations": [...],
    "mro_violations": [...],
    "execution_failures": [...]
  },
  "compliance_status": {
    "passes_100_percent_requirement": false,
    "individual_pillar_status": {
      "import_validation": false,
      "signature_enforcement": false,
      "mro_audit": false,
      "mock_execution": false
    }
  }
}
```

## Key Sections for Analysis

### 1. `failed_agents.import_failures`

**Critical for identifying integration issues:**

- **class_name**: Agent that failed to import
- **file_path**: Exact file location
- **error**: Specific error message
- **error_line**: Line number where error occurred
- **missing_dependencies**: List of missing modules

### 2. `failed_agents.signature_violations`

**Critical for signature compliance:**

- **class_name**: Agent with signature issues
- **error**: Description of signature problem
- **is_legacy**: True if using legacy `heal(path)` signature
- **signature**: Actual signature found

### 3. `failed_agents.mro_violations`

**Critical for inheritance issues:**

- **class_name**: Agent with MRO problems
- **shadowing_detected**: True if attribute shadowing found
- **shadowing_details**: Specific shadowing information
- **missing_mixins**: Required mixins not in MRO
- **mro**: Full method resolution order

### 4. `compliance_status`

**Critical for CI/CD gates:**

- **passes_100_percent_requirement**: Boolean for overall compliance
- **individual_pillar_status**: Status of each validation pillar

## Usage Examples

### Command Line

```bash
# Default JSON output
python tests/integration/test_sovereign_contract_guard.py

# Custom JSON filename
python tests/integration/test_sovereign_contract_guard.py --json-output ci_validation_report.json

# Pytest with JSON output
python -m pytest tests/integration/test_sovereign_contract_guard.py -v
```

### CI/CD Integration

```bash
#!/bin/bash
# Example CI/CD validation script

echo "Running Sovereign Contract Guard validation..."
python tests/integration/test_sovereign_contract_guard.py --json-output validation_report.json

# Check compliance status
if jq -r '.compliance_status.passes_100_percent_requirement' validation_report.json | grep -q true; then
    echo "✅ Sovereign contract compliance PASSED"
    exit 0
else
    echo "❌ Sovereign contract compliance FAILED"
    echo "Import failures: $(jq '.failed_agents.import_failures | length' validation_report.json)"
    echo "Signature violations: $(jq '.failed_agents.signature_violations | length' validation_report.json)"
    echo "MRO violations: $(jq '.failed_agents.mro_violations | length' validation_report.json)"
    echo "Execution failures: $(jq '.failed_agents.execution_failures | length' validation_report.json)"
    exit 1
fi
```

### Python Integration

```python
import json

# Load and analyze results
with open('sovereign_contract_report.json', 'r') as f:
    results = json.load(f)

# Check specific failure types
import_failures = results['failed_agents']['import_failures']
missing_base_agents = [f for f in import_failures if 'agentic_core.base_agents' in f.get('missing_dependencies', [])]

print(f"Agents missing base_agents: {len(missing_base_agents)}")
for failure in missing_base_agents:
    print(f"  - {failure['class_name']}: {failure['error']}")
```

## Integration with execute_ssot.py

The JSON output provides exact diagnostic information needed to fix `execute_ssot.py` integration failures:

1. **Import Path Issues**: Identifies missing modules and exact line numbers
2. **Signature Mismatches**: Flags agents needing `heal(violation)` updates
3. **Mixin Dependencies**: Shows missing `SubatomicTestingMixin` requirements
4. **Runtime Failures**: Reveals instantiation and execution problems

This enables targeted fixes rather than manual debugging, significantly reducing remediation time.
