#!/usr/bin/env python3
"""Analyze the test inventory results."""

import json


def analyze_inventory():
    with open('tools/test_enforcement/test_inventory.json') as f:
        inventory = json.load(f)

    print('📊 INVENTORY SUMMARY:')
    print(f"  Total tests: {inventory['metadata']['total_tests']}")
    print(f"  Test files: {inventory['metadata']['total_test_files']}")

    print('\nSkip patterns found:')
    for skip_type, count in inventory['summary']['skip_types'].items():
        print(f'  {skip_type}: {count}')

    print('\nBehavior distribution:')
    for behavior, count in inventory['summary']['behaviors'].items():
        print(f'  {behavior}: {count}')

    # Show some examples of problematic patterns
    print('\n🔍 SAMPLE IMPORTERROR SKIPS:')
    import_error_tests = [t for t in inventory['tests'] if t['skip_type'] == 'import_error']
    for test in import_error_tests[:5]:
        print(f"  {test['file_path']}:{test['test_name']} -> {test['dependency']}")

    print('\n🔍 SAMPLE RUNTIME CONDITION SKIPS:')
    runtime_tests = [t for t in inventory['tests'] if t['skip_type'] == 'runtime_condition']
    for test in runtime_tests[:5]:
        print(f"  {test['file_path']}:{test['test_name']} -> {test['skip_reason']}")

if __name__ == "__main__":
    analyze_inventory()
