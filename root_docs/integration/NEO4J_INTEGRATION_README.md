# Neo4j Integration for Temporal Knowledge Graph

This document describes the Neo4j integration that has been added to the temporal knowledge graph and multi-hop retrieval stack.

## Overview

Neo4j has been integrated as the graph database backing the graph data design (graph DD) for temporal knowledge graph operations. The integration is designed to be:

- **Additive**: All existing SQLite/NetworkX logic is preserved
- **Graceful**: System continues to work without Neo4j if driver is not installed
- **Mirrored**: All graph writes are mirrored to Neo4j while maintaining existing storage
- **Primary for reads**: factual_qa and trend_analysis use Neo4j as the primary source when available

## Components Added

### 1. Dependencies

- `neo4j>=5.22.0` added to `requirements.txt`

### 2. Core Modules

#### `graph_store_neo4j.py`

- `Neo4jGraphStore` class implementing L4 state layer
- Connection via environment variables: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- Methods:
  - `close()`: Close database connection
  - `run(cypher, params)`: Execute arbitrary Cypher queries
  - `upsert_entity()`: Create/update entities
  - `upsert_relation()`: Create/update temporal relations
  - `update_relation_invalidity()`: Mark relations as invalid
  - `query_factual_temporal()`: Query temporal facts with filters

#### `graph_query.py`

- Simple helper function for ad-hoc Cypher queries
- Wraps `Neo4jGraphStore.run()` method

#### `l2/kg_writer.py`

- Mirrors temporal graph data to Neo4j during ingestion
- Functions:
  - `insert_entity()`: Mirror entities to Neo4j
  - `insert_triplet()`: Mirror triplets as relations
  - `insert_event()`: Handle invalidation events
  - `batch_process_invalidation()`: Batch update invalidations
  - `ingest_transcript()`: Complete transcript mirroring

#### `l2/factual_qa.py`

- Reads from Neo4j for temporal fact queries
- Functions:
  - `factual_qa()`: Query entities with predicates in date ranges
  - `trend_analysis()`: Multi-entity trend analysis

### 3. Ingestion Pipeline Integration

#### `orchestration/kg_ingestion_dag.py`

- Enhanced to mirror writes to Neo4j during ingestion
- Added mirroring hooks for:
  - Entity extraction and resolution stage
  - Triplet extraction stage  
  - Invalidation checks stage
  - Complete KG writes stage
- Graceful fallback if Neo4j unavailable

## Environment Setup

### Required Environment Variables

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your_password"
```

### Installation

```bash
pip install neo4j>=5.22.0
```

## Usage Examples

### Direct Graph Queries

```python
from graph_query import graph_query

# Simple node count
results = graph_query("MATCH (n) RETURN count(n) as count")

# Entity relations
results = graph_query(
    "MATCH (s:Entity {name: $entity})-[r:RELATION]->(o:Entity) "
    "WHERE r.predicate = $predicate RETURN s, r, o",
    {"entity": "Google", "predicate": "WORKED_AT"}
)
```

### Factual QA

```python
from l2.factual_qa import factual_qa

# Query work history
result = factual_qa(
    entity="John Doe",
    start_date_range="2020-01-01T00:00:00Z", 
    end_date_range="2023-01-01T00:00:00Z",
    predicate="WORKED_AT"
)
print(result)
```

### Trend Analysis

```python
from l2.factual_qa import trend_analysis

# Analyze skill trends across companies
result = trend_analysis(
    companies=["Google", "Microsoft", "Apple"],
    topics=["HAS_SKILL", "WORKED_AT"],
    start_date_range="2020-01-01T00:00:00Z",
    end_date_range="2023-01-01T00:00:00Z"
)
print(result)
```

## Data Model

### Entities

- Stored as `:Entity` nodes with properties:
  - `entity_id`: Unique identifier
  - `entity_type`: Type classification
  - `name`: Display name
  - `canonical_id`: Canonical entity reference
  - `aliases`: List of alternative names
  - `confidence`: Match confidence score
  - `created_at`: Creation timestamp

### Relations

- Stored as `:RELATION` edges with properties:
  - `rel_id`: Unique relation identifier
  - `predicate`: Relation type (e.g., "WORKED_AT", "HAS_SKILL")
  - `valid_at`: Validity start time
  - `invalid_at`: Validity end time (null if still valid)
  - `confidence`: Relation confidence
  - `source`: Data source
  - `status`: Active/invalidated status

## Error Handling

The integration is designed to be resilient:

1. **Missing Driver**: Graceful fallback with informative error messages
2. **Connection Issues**: Functions return empty results or error messages
3. **Ingestion Failures**: Neo4j mirroring failures don't break existing pipeline
4. **Type Safety**: Proper Optional typing for nullable Neo4j instances

## Testing

### Unit Tests

- Tests in `tests/unit/l2_execution/test_neo4j_integration.py`
- Covers import handling, graceful degradation, and basic functionality
- Run with: `pytest tests/unit/l2_execution/test_neo4j_integration.py`

### Manual Testing

```bash
# Test imports (should work without Neo4j driver)
python -c "import graph_store_neo4j; import graph_query; import l2.kg_writer; import l2.factual_qa"

# Test factual QA (returns driver not installed message if Neo4j unavailable)
python -c "from l2.factual_qa import factual_qa; print(factual_qa('test', '2020-01-01T00:00:00Z', '2023-01-01T00:00:00Z', 'WORKED_AT'))"
```

## Migration Notes

- **No Breaking Changes**: All existing APIs preserved
- **Gradual Adoption**: Can enable Neo4j incrementally
- **Fallback Support**: System continues working without Neo4j
- **Performance**: Neo4j reads are primary when available, writes are mirrored

## Troubleshooting

### Import Errors

```text
ImportError: Neo4j driver not installed. Install with: pip install neo4j>=5.22.0
```

**Solution**: Install the Neo4j Python driver

### Connection Issues

```text
Unable to query data... Graph database temporarily unavailable.
```

**Solution**: Check Neo4j service and environment variables

### Performance Considerations

- Neo4j mirroring adds minimal overhead to ingestion
- Read performance improved for complex graph queries
- Consider connection pooling for high-throughput scenarios

## Future Enhancements

1. **Connection Pooling**: For high-concurrency scenarios
2. **Cypher Optimization**: Advanced query patterns
3. **Schema Validation**: Enforce graph constraints
4. **Backup/Restore**: Neo4j data management utilities
5. **Monitoring**: Performance metrics and health checks
