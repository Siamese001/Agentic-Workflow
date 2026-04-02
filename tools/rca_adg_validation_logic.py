# Check the actual validation logic that's failing
print('=== ADG VALIDATION LOGIC INVESTIGATION ===')
print()

# The validation report shows:
# - Numerator: 680363
# - Denominator: 680363
# - Ratio: 1.0
# - Threshold: 1.0
# - Status: FAILED

# This suggests the validation is expecting numerator == denominator for PASS
# But it's failing even though they're equal (both 680363)

# Let's check what the validation is actually checking
print('Validation evidence shows:')
print('  semantic_edge_ratio: 1.0')
print('  semantic_edges: 680363')
print('  total_edges: 680363')
print()

print('The issue might be:')
print('1. The validation expects ALL metrics to be at threshold, not just ratio')
print('2. There\'s a bug in the validation logic')
print('3. The validation is checking something else not shown in evidence')
print()

# Check if there are any metrics below threshold in the evidence
evidence = {
    'callsite_specific_ratio': 1.0,
    'controls_flow_specific_ratio': 1.0,
    'execution_generic_semantic_count': 0,
    'flows_to_specific_ratio': 1.0,
    'semantic_edge_ratio': 1.0,
    'side_effect_specific_ratio': 1.0,
    'temporal_ordering_ratio': 1.0,
}

print('Evidence metrics:')
for metric, value in evidence.items():
    if isinstance(value, float):
        status = '✅' if value >= 0.95 else '❌'
        print(f'  {metric}: {value} {status}')
    else:
        print(f'  {metric}: {value}')

print()
print('All ratios are 1.0 which should pass the 0.95 threshold.')
print('The execution_generic_semantic_count is 0 which should pass the <1% test.')
print()
print('CONCLUSION: This appears to be a bug in the validation logic itself.')
print('The validation is failing even though all metrics are within thresholds.')
