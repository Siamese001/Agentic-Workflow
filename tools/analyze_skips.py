import json

with open('artifacts/current_skip_analysis.json') as f:
    data = json.load(f)

# Find actual skipped tests
skipped_tests = []
for test in data['tests']:
    if test['is_skipped']:
        skipped_tests.append({
            'node_id': test['node_id'],
            'file_path': test['file_path'],
            'skip_reason': test['skip_reason'],
            'line_number': test['line_number']
        })

print(f'Actual skipped tests from AST analysis: {len(skipped_tests)}')
for skip in skipped_tests[:10]:
    print(f'  {skip["node_id"]} - {skip["skip_reason"]}')

# Save skipped tests list
with open('artifacts/skipped_tests_list.json', 'w') as f:
    json.dump(skipped_tests, f, indent=2)
