"""GraphRAG Fusion - Combining Vector and Graph Retrieval.

This module implements the fusion of vector similarity search with knowledge graph
traversal to enable multi-hop reasoning and relationship-based queries.
"""

import asyncio
import logging
import re

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries for GraphRAG."""

    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    FUSION = "fusion"
    MULTI_HOP = "multi_hop"


@dataclass
class FusionResult:
    """Result of GraphRAG fusion query."""

    query: str
    query_type: QueryType
    vector_results: list[dict[str, Any]] = None
    graph_results: GraphContext = None
    fused_context: str = ""
    sources: list[str] = None
    confidence: float = 0.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.vector_results is None:
            self.vector_results = []
        if self.graph_results is None:
            self.graph_results = GraphContext()
        if self.sources is None:
            self.sources = []
        if self.metadata is None:
            self.metadata = {}


class CypherQueryGenerator:
    """Generates Cypher queries from natural language patterns."""

    def __init__(self):
        """Initialize the query generator with patterns."""
        # Common query patterns
        self.patterns = {
            # Skills and experience
            "skills_match": r"(?:what|which) skills do (?:i|you|candidate) have (?:for|in|related to) (.+)",
            "experience_with": r"(?:experience|worked|used) (?:with|on) (.+)",
            "projects_using": r"projects (?:using|with|involving) (.+)",
            # Company and role relationships
            "role_at_company": r"(?:role|position|job) (?:at|in) (.+)",
            "company_tech_stack": r"(?:tech stack|technology|technologies) (?:at|used by) (.+)",
            "team_collaboration": r"(?:worked|collaborated) (?:with|on) (.+)",
            # Career progression
            "career_path": r"(?:career|progression|advancement) (?:path|track) (?:for|to) (.+)",
            "skill_to_role": r"(.+) skills (?:lead to|for|required for) (.+) role",
            # Project relationships
            "project_outcomes": r"(?:outcome|result|impact) (?:of|from) (.+) project",
            "technologies_for": r"(?:technologies|tech) (?:for|to|needed for) (.+)",
        }

        # Cypher templates for each pattern
        self.templates = {
            "skills_match": """
                MATCH (e:Entity)-[:HAS_SKILL]->(s:Skill)
                WHERE s.name =~ $skill_pattern
                OPTIONAL MATCH (e)-[:WORKED_ON]->(p:Project)
                RETURN e.name as entity,
                       collect(DISTINCT s.name) as skills,
                       collect(DISTINCT p.name) as projects
                LIMIT 10
            """,
            "experience_with": """
                MATCH (e:Entity)-[:WORKED_WITH]->(t:Technology)
                WHERE t.name =~ $tech_pattern
                OPTIONAL MATCH (e)-[:WORKED_ON]->(p:Project)
                RETURN e.name as entity,
                       t.name as technology,
                       collect(DISTINCT p.name) as projects
                LIMIT 10
            """,
            "projects_using": """
                MATCH (p:Project)-[:USES_TECH]->(t:Technology)
                WHERE t.name =~ $tech_pattern
                OPTIONAL MATCH (e:Entity)-[:WORKED_ON]->(p)
                RETURN p.name as project,
                       collect(DISTINCT t.name) as technologies,
                       collect(DISTINCT e.name) as contributors
                LIMIT 10
            """,
            "role_at_company": """
                MATCH (e:Entity)-[:WORKED_AT]->(c:Company)
                WHERE c.name =~ $company_pattern
                OPTIONAL MATCH (e)-[:HAD_ROLE]->(r:Role)
                RETURN e.name as entity,
                       c.name as company,
                       collect(DISTINCT r.name) as roles
                LIMIT 10
            """,
            "company_tech_stack": """
                MATCH (c:Company)-[:USES_TECH]->(t:Technology)
                WHERE c.name =~ $company_pattern
                RETURN c.name as company,
                       collect(DISTINCT t.name) as tech_stack
                LIMIT 10
            """,
            "team_collaboration": """
                MATCH (e1:Entity)-[:COLLABORATED_WITH]->(e2:Entity)
                WHERE e1.name =~ $entity_pattern OR e2.name =~ $entity_pattern
                OPTIONAL MATCH (e1)-[:WORKED_ON]->(p:Project)<-[:WORKED_ON]-(e2)
                RETURN e1.name as collaborator1,
                       e2.name as collaborator2,
                       collect(DISTINCT p.name) as shared_projects
                LIMIT 10
            """,
            "career_path": """
                MATCH path = (e:Entity)-[:NEXT_ROLE*]->(r:Role)
                WHERE e.name =~ $entity_pattern
                RETURN [node in nodes(path) | node.name] as career_progression
                LIMIT 5
            """,
            "skill_to_role": """
                MATCH (s:Skill)-[:REQUIRED_FOR]->(r:Role)
                WHERE s.name =~ $skill_pattern AND r.name =~ $role_pattern
                RETURN s.name as skill,
                       r.name as role,
                       collect(DISTINCT r.level) as levels
                LIMIT 10
            """,
            "project_outcomes": """
                MATCH (p:Project)-[:RESULTED_IN]->(o:Outcome)
                WHERE p.name =~ $project_pattern
                RETURN p.name as project,
                       collect(DISTINCT o.name) as outcomes,
                       collect(DISTINCT o.metric) as metrics
                LIMIT 10
            """,
            "technologies_for": """
                MATCH (d:Domain)-[:REQUIRES_TECH]->(t:Technology)
                WHERE d.name =~ $domain_pattern
                RETURN d.name as domain,
                       collect(DISTINCT t.name) as technologies
                LIMIT 10
            """,
        }

    def generate_query(self, natural_query: str) -> tuple[str, dict[str, Any], str]:
        """Generate Cypher query from natural language.

        Args:
            natural_query: Natural language query

        Returns:
            Tuple of (cypher_query, parameters, query_type)
        """
        natural_lower = natural_query.lower()

        # Try to match patterns
        for pattern_name, pattern in self.patterns.items():
            match = re.search(pattern, natural_lower)
            if match:
                template = self.templates[pattern_name]

                # Extract parameters
                if pattern_name == "skill_to_role":
                    skill_pattern = f"(?i).*{match.group(1)}.*"
                    role_pattern = f"(?i).*{match.group(2)}.*"
                    params = {"skill_pattern": skill_pattern, "role_pattern": role_pattern}
                else:
                    entity = match.group(1).strip()
                    entity_pattern = f"(?i).*{entity}.*"

                    # Map to appropriate parameter
                    if "skill" in pattern_name:
                        params = {"skill_pattern": entity_pattern}
                    elif "tech" in pattern_name:
                        params = {"tech_pattern": entity_pattern}
                    elif "company" in pattern_name:
                        params = {"company_pattern": entity_pattern}
                    elif "project" in pattern_name:
                        params = {"project_pattern": entity_pattern}
                    elif "domain" in pattern_name:
                        params = {"domain_pattern": entity_pattern}
                    elif "entity" in pattern_name:
                        params = {"entity_pattern": entity_pattern}
                    else:
                        params = {"entity_pattern": entity_pattern}

                return template, params, pattern_name

        # Fallback: general entity search
        fallback_template = """
            MATCH (e:Entity)
            WHERE e.name =~ $entity_pattern
            OPTIONAL MATCH (e)-[r]-(related)
            RETURN e.name as entity,
                   labels(e) as types,
                   collect(DISTINCT related.name)[0..5] as related_entities
            LIMIT 10
        """

        entity_pattern = f"(?i).*{natural_lower.split()[-1]}.*"
        return fallback_template, {"entity_pattern": entity_pattern}, "entity_search"


class GraphRAGFusion:
    """Fuses vector and graph retrieval for enhanced RAG."""

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphAgent | None = None,
        vector_retriever: callable | None = None,
        enable_fusion: bool = True,
        confidence_threshold: float = 0.6,
    ):
        """Initialize GraphRAG fusion.

        Args:
            knowledge_graph: KnowledgeGraphAgent instance
            vector_retriever: Function for vector retrieval
            enable_fusion: Whether to enable fusion (vs. vector-only)
            confidence_threshold: Minimum confidence for fusion results
        """
        self.knowledge_graph = knowledge_graph
        self.vector_retriever = vector_retriever
        self.enable_fusion = enable_fusion
        self.confidence_threshold = confidence_threshold
        self.query_generator = CypherQueryGenerator()

        # Statistics
        self.stats = {
            "total_queries": 0,
            "vector_only": 0,
            "graph_only": 0,
            "fusion_queries": 0,
            "multi_hop_queries": 0,
            "graph_fallbacks": 0,
        }

        logger.info(f"Initialized GraphRAGFusion - Fusion: {enable_fusion}")

    async def query(
        self, natural_query: str, query_type: QueryType | None = None, max_results: int = 5
    ) -> FusionResult:
        """Execute a GraphRAG fusion query.

        Args:
            natural_query: Natural language query
            query_type: Type of query (auto-detected if None)
            max_results: Maximum results to return

        Returns:
            FusionResult with combined results
        """
        self.stats["total_queries"] += 1

        # Auto-detect query type if not specified
        if query_type is None:
            query_type = self._detect_query_type(natural_query)

        # Execute based on query type
        if query_type == QueryType.VECTOR_ONLY:
            return await self._vector_only_query(natural_query, max_results)
        elif query_type == QueryType.GRAPH_ONLY:
            return await self._graph_only_query(natural_query, max_results)
        else:
            return await self._fusion_query(natural_query, query_type, max_results)

    def _detect_query_type(self, query: str) -> QueryType:
        """Detect query type from natural language.

        Args:
            query: Natural language query

        Returns:
            Detected QueryType
        """
        query_lower = query.lower()

        # Check for relationship indicators
        relationship_words = [
            "relationship",
            "connection",
            "between",
            "related to",
            "worked with",
            "collaborated",
            "team",
            "together",
        ]

        # Check for multi-hop indicators
        multi_hop_words = [
            "path",
            "journey",
            "progression",
            "through",
            "via",
            "leads to",
            "resulted in",
            "caused",
        ]

        # Check for graph-specific patterns
        graph_patterns = ["nodes", "edges", "graph", "network", "hops", "traverse", "connected"]

        if any(word in query_lower for word in multi_hop_words):
            return QueryType.MULTI_HOP
        elif any(word in query_lower for word in relationship_words):
            return QueryType.FUSION
        elif any(word in query_lower for word in graph_patterns):
            return QueryType.GRAPH_ONLY
        else:
            return QueryType.VECTOR_ONLY

    async def _vector_only_query(self, query: str, max_results: int) -> FusionResult:
        """Execute vector-only query.

        Args:
            query: Query string
            max_results: Maximum results

        Returns:
            FusionResult with vector results
        """
        self.stats["vector_only"] += 1

        try:
            if self.vector_retriever:
                # Call vector retriever
                vector_results = await self.vector_retriever(query, max_results)
            else:
                vector_results = []

            return FusionResult(
                query=query,
                query_type=QueryType.VECTOR_ONLY,
                vector_results=vector_results,
                sources=["vector_search"],
                confidence=0.8,
            )

        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return FusionResult(
                query=query,
                query_type=QueryType.VECTOR_ONLY,
                sources=["vector_error"],
                confidence=0.0,
            )

    async def _graph_only_query(self, query: str, max_results: int) -> FusionResult:
        """Execute graph-only query.

        Args:
            query: Query string
            max_results: Maximum results

        Returns:
            FusionResult with graph results
        """
        self.stats["graph_only"] += 1

        try:
            if self.knowledge_graph:
                # Generate Cypher query
                cypher, params, pattern_type = self.query_generator.generate_query(query)

                # Execute via knowledge graph
                # Note: This would need async support in KnowledgeGraphAgent
                graph_context = self.knowledge_graph.query_context(
                    params.get("entity_pattern", "").replace("(?i).*", "").replace(".*", ""),
                    hops=2,
                    limit=max_results,
                )

                return FusionResult(
                    query=query,
                    query_type=QueryType.GRAPH_ONLY,
                    graph_results=graph_context,
                    sources=["graph_search"],
                    confidence=graph_context.confidence,
                    metadata={"cypher_pattern": pattern_type},
                )
            else:
                self.stats["graph_fallbacks"] += 1
                return FusionResult(
                    query=query,
                    query_type=QueryType.GRAPH_ONLY,
                    sources=["graph_unavailable"],
                    confidence=0.0,
                )

        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            # Fallback to vector
            return await self._vector_only_query(query, max_results)

    async def _fusion_query(
        self, query: str, query_type: QueryType, max_results: int
    ) -> FusionResult:
        """Execute fusion query combining vector and graph.

        Args:
            query: Query string
            query_type: Type of fusion query
            max_results: Maximum results

        Returns:
            FusionResult with fused results
        """
        if query_type == QueryType.MULTI_HOP:
            self.stats["multi_hop_queries"] += 1
        else:
            self.stats["fusion_queries"] += 1

        # Run vector and graph queries in parallel
        vector_task = self._vector_only_query(query, max_results)
        graph_task = self._graph_only_query(query, max_results)

        vector_result, graph_result = await asyncio.gather(
            vector_task, graph_task, return_exceptions=True
        )

        # Handle exceptions
        if isinstance(vector_result, Exception):
            vector_result = FusionResult(query=query, query_type=QueryType.VECTOR_ONLY)
        if isinstance(graph_result, Exception):
            graph_result = FusionResult(query=query, query_type=QueryType.GRAPH_ONLY)

        # Fuse results
        fused_context = self._fuse_results(
            vector_result.vector_results, graph_result.graph_results, query_type
        )

        # Combine sources
        combined_sources = vector_result.sources + graph_result.sources

        # Calculate combined confidence
        combined_confidence = max(vector_result.confidence, graph_result.confidence)

        return FusionResult(
            query=query,
            query_type=query_type,
            vector_results=vector_result.vector_results,
            graph_results=graph_result.graph_results,
            fused_context=fused_context,
            sources=combined_sources,
            confidence=combined_confidence,
            metadata={
                "vector_confidence": vector_result.confidence,
                "graph_confidence": graph_result.confidence,
                "graph_metadata": graph_result.metadata,
            },
        )

    def _fuse_results(
        self,
        vector_results: list[dict[str, Any]],
        graph_context: GraphContext,
        query_type: QueryType,
    ) -> str:
        """Fuse vector and graph results into context.

        Args:
            vector_results: Results from vector search
            graph_context: Results from graph search
            query_type: Type of query

        Returns:
            Fused context string
        """
        context_parts = []

        # Add unstructured text from vector results
        if vector_results:
            context_parts.append("## Unstructured Knowledge")
            for i, result in enumerate(vector_results[:3], 1):
                text = ""
                if isinstance(result, dict):
                    text = result.get("text", result.get("content", ""))
                else:
                    text = str(result)
                context_parts.append(f"{i}. {text[:200]}...")

        # Add structured relationships from graph
        if graph_context and graph_context.entities:
            context_parts.append("\n## Structured Relationships")

            # Add entities
            if graph_context.entities:
                context_parts.append("### Key Entities:")
                for entity in graph_context.entities[:5]:
                    name = entity.get("name", entity.get("entity_name", "Unknown"))
                    score = entity.get("influence_score", entity.get("score", 0))
                    context_parts.append(f"- {name} (relevance: {score:.2f})")

            # Add relationships
            if graph_context.relationships:
                context_parts.append("\n### Relationships:")
                for rel in graph_context.relationships[:5]:
                    source = rel.get("source", rel.get("start", "Unknown"))
                    target = rel.get("target", rel.get("end", "Unknown"))
                    rel_type = rel.get("type", "related_to")
                    context_parts.append(f"- {source} --[{rel_type}]--> {target}")

        return "\n".join(context_parts)

    def get_stats(self) -> dict[str, Any]:
        """Get fusion statistics.

        Returns:
            Dictionary with stats
        """
        return {
            **self.stats,
            "fusion_enabled": self.enable_fusion,
            "graph_available": self.knowledge_graph is not None,
            "vector_available": self.vector_retriever is not None,
        }


# Global instance
_graphrag_fusion: GraphRAGFusion | None = None


def get_graphrag_fusion(**kwargs) -> GraphRAGFusion:
    """Get or create global GraphRAG fusion instance.

    Args:
        **kwargs: Arguments for GraphRAGFusion

    Returns:
        GraphRAGFusion instance
    """
    global _graphrag_fusion

    if _graphrag_fusion is None:
        _graphrag_fusion = GraphRAGFusion(**kwargs)

    return _graphrag_fusion


# Convenience function
async def graphrag_query(
    query: str, query_type: QueryType | None = None, max_results: int = 5, **kwargs
) -> FusionResult:
    """Convenience function for GraphRAG query.

    Args:
        query: Natural language query
        query_type: Type of query
        max_results: Maximum results
        **kwargs: Additional arguments

    Returns:
        FusionResult
    """
    fusion = get_graphrag_fusion(**kwargs)
    return await fusion.query(query, query_type, max_results)
