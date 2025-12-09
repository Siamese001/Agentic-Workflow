"""
L2 Factual QA - Reads from Neo4j for temporal fact queries

Answers factual questions about temporal career facts using Neo4j as primary source
while maintaining existing interface for backward compatibility.

Layer: L2 (Execution)
"""

from __future__ import annotations

from typing import List, Optional

try:
    from graph_store_neo4j import Neo4jGraphStore
    _graph: Optional[Neo4jGraphStore] = Neo4jGraphStore()
    _NEO4J_AVAILABLE = True
except ImportError:
    _graph = None
    _NEO4J_AVAILABLE = False


def factual_qa(
    entity: str,
    start_date_range: str,
    end_date_range: str,
    predicate: str
) -> str:
    """
    Query temporal facts from Neo4j with original output format.
    
    Args:
        entity: Entity name to search for
        start_date_range: Start of date range (ISO string)
        end_date_range: End of date range (ISO string)
        predicate: Predicate to match (e.g., "WORKED_AT", "HAS_SKILL")
        
    Returns:
        Formatted string with enumerated facts or no-data message
    """
    if not _NEO4J_AVAILABLE:
        return (
            f"Unable to query data for '{entity}' with predicate '{predicate}' "
            f"in the specified date range ({start_date_range} to {end_date_range}). "
            "Neo4j driver not installed. Install with: pip install neo4j>=5.22.0"
        )
        
    try:
        if _graph is not None:
            rows = _graph.query_factual_temporal(
                entity_name=entity,
                predicate=predicate.upper(),
                start=start_date_range,
                end=end_date_range,
            )
        else:
            rows = []

        if not rows:
            return (
                f"No data found for '{entity}' with predicate '{predicate}' "
                f"in the specified date range ({start_date_range} to {end_date_range})."
            )

        lines: List[str] = []
        for i, record in enumerate(rows, start=1):
            s = record["s"]
            r = record["r"]
            o = record["o"]
            
            # Format validity date
            valid_at = r.get('valid_at')
            if valid_at and hasattr(valid_at, 'iso_format'):
                valid_str = valid_at.iso_format()
            elif valid_at:
                valid_str = str(valid_at)
            else:
                valid_str = 'n/a'
            
            triplet = (
                f"{s['name']} – {r['predicate']} – {o['name']} "
                f"[Valid-from: {valid_str}]"
            )
            lines.append(f"{i}. {triplet}")

        return "\n".join(lines)
        
    except Exception:
        # Fallback message if Neo4j unavailable
        return (
            f"Unable to query data for '{entity}' with predicate '{predicate}' "
            f"in the specified date range ({start_date_range} to {end_date_range}). "
            "Graph database temporarily unavailable."
        )


def trend_analysis(
    companies: List[str],
    topics: List[str],
    start_date_range: str,
    end_date_range: str
) -> str:
    """
    Analyze trends across companies and topics using factual_qa.
    
    Maintains original interface while using Neo4j backend.
    """
    if not _NEO4J_AVAILABLE:
        return "Neo4j driver not installed. Install with: pip install neo4j>=5.22.0"
        
    lines: List[str] = []
    
    for company in companies:
        for topic in topics:
            lines.append(f"\n=== {company} - {topic} ===")
            result = factual_qa(company, start_date_range, end_date_range, topic)
            lines.append(result)
    
    return "\n".join(lines)
