#!/usr/bin/env python3
"""Script to mark deprecated tests with skip markers."""
from pathlib import Path

deprecated_tests = [
    'tests/unit/test_apps_cv_adversarial_hardening_test_cv_a001.py',
    'tests/unit/test_apps_cv_adversarial_hardening_test_cv_a002.py',
    'tests/unit/test_apps_cv_conftest.py',
    'tests/unit/test_apps_cv_integration_logic_test_cv_i002.py',
    'tests/unit/test_apps_cv_integration_logic_test_cv_i004.py',
    'tests/unit/test_apps_cv_protocol_compliance_test_cv_p001.py',
    'tests/unit/test_apps_cv_unit_mocks_test_cv_u001.py',
    'tests/unit/test_apps_cv_unit_mocks_test_cv_u003.py',
    'tests/unit/test_apps_cv_unit_mocks_test_cv_u004.py',
    'tests/unit/test_apps_lic_test_lic_memory_mappings.py',
    'tests/unit/test_apps_lic_test_lic_safety_planner.py',
    'tests/unit/test_apps_shared_test_sdk_latency.py',
    'tests/unit/test_agentic_core_test_fission_mission.py',
    'tests/unit/test_agentic_core_test_tool_request_builder.py',
    'tests/unit/test_canon_validator_equivalence.py',
    'tests/unit/test_canon_validator_sandbox_core_unsafe.py',
    'tests/unit/test_canon_validator_sandbox_level1_level2_level3_level4_level5_level6_too_deep.py',
    'tests/unit/test_canon_validator_sandbox_main.py',
    'tests/unit/test_canon_validator_zlm.py',
    'tests/unit/test_golden_prompts_test_lic_outreach.py',
]

skip_marker = """import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Test requires external modules")

"""

for test_file in deprecated_tests:
    path = Path(test_file)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        if 'pytestmark = pytest.mark.skip' not in content:
            new_content = skip_marker + content
            path.write_text(new_content, encoding='utf-8')
            print(f'Marked: {test_file}')

print('Done')
