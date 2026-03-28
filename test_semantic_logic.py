# Test the semantic stamping logic directly
from agentic_core.adg.extraction.static_scanner import Edge, _stamp_semantic_types_with_stats

# Create test edges like the problematic ones
test_edges = [
    Edge(
        from_name="ADG::Module::test",
        to_name="ADG::Symbol::test.symbol",
        relation_type="reads_runtime_state",
        edge_kind="reads_runtime_state",
        source_file="test.py",
        line_no=1,
        symbol="test.symbol",
        semantic_type="",  # Empty to trigger stamping
    ),
    Edge(
        from_name="ADG::Module::test",
        to_name="ADG::Symbol::test.symbol",
        relation_type="reads_policy_state",
        edge_kind="reads_policy_state",
        source_file="test.py",
        line_no=1,
        symbol="test.symbol",
        semantic_type="",  # Empty to trigger stamping
    ),
    Edge(
        from_name="ADG::Module::test",
        to_name="ADG::Symbol::test.symbol",
        relation_type="belongs_to_layer",
        edge_kind="layer_membership",
        source_file="test.py",
        line_no=1,
        symbol="test.symbol",
        semantic_type="",  # Empty to trigger stamping
    ),
]

# Test the stamping function
stamped_edges, stats = _stamp_semantic_types_with_stats(test_edges)

print('=== Semantic Stamping Test Results ===')
print(f'Input edges: {len(test_edges)}')
print(f'Output edges: {len(stamped_edges)}')
print()
print('Stats:')
for key, value in stats.items():
    print(f'  {key}: {value}')
print()

print('Stamped edges:')
for edge in stamped_edges:
    print(f'  {edge.relation_type} -> {edge.semantic_type}')

# Check if layer_membership works
layer_edge = stamped_edges[2]
if layer_edge.semantic_type == "layer_membership":
    print('✅ layer_membership correctly mapped')
else:
    print(f'❌ layer_membership failed: got {layer_edge.semantic_type}')
