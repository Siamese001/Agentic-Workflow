"""Architecture Visualizer Agent - Mermaid.js Diagram Generation.

This agent translates text-based architectural descriptions into professional
Mermaid.js diagrams, providing visual proof of system design competency.
"""

import logging
import re



logger = logging.getLogger(__name__)


class DiagramType(str, Enum):
    """Supported Mermaid diagram types."""

    FLOWCHART = "flowchart TD"
    SEQUENCE = "sequenceDiagram"
    C4_COMPONENT = "C4Component"
    GRAPH = "graph TD"


class DiagramNode(BaseModel):
    """Represents a node in a Mermaid diagram."""

    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Display label for the node")
    shape_code: str = Field(..., description="Mermaid shape code (e.g., '[...]', '(...)')")
    node_type: str = Field(default="default", description="Type of node (service, database, etc.)")

    @validator("id")
    def validate_id(cls, v):
        """Ensure node ID is Mermaid-compatible."""
        # Remove spaces and special characters, keep alphanumeric and underscore
        return re.sub(r"[^a-zA-Z0-9_]", "", v)


class DiagramArtifact(BaseModel):
    """A complete Mermaid diagram artifact."""

    mermaid_code: str = Field(..., description="Complete Mermaid diagram code")
    caption: str = Field(..., description="Diagram caption/title")
    diagram_type: DiagramType = Field(..., description="Type of diagram")
    node_count: int = Field(..., description="Number of nodes in diagram")
    complexity_score: float = Field(default=0.0, description="Complexity score (0-1)")


class SimpleAgentBase:
    """Simple base class for standalone agents."""

    def __init__(self, name: str, model_name: str = "gpt-4"):
        """Initialize the agent.

        Args:
            name: Agent name for logging
            model_name: LLM model to use
        """
        self.name = name
        self.model_name = model_name
        logger.info(f"Initialized {self.__class__.__name__}: model={model_name}")


class ArchitectureVisualizerAgent(SimpleAgentBase):
    """Agent that converts text descriptions into Mermaid.js diagrams."""

    def __init__(self, model_name: str = "gpt-4", max_nodes: int = 10):
        """Initialize the Architecture Visualizer Agent.

        Args:
            model_name: LLM model to use for diagram generation
            max_nodes: Maximum number of nodes to prevent visual clutter
        """
        super().__init__(name="Architecture Visualizer", model_name=model_name)
        self.max_nodes = max_nodes

        # Shape mappings for different component types
        self.shape_mappings = {
            "database": "[({label})]",  # Cylinder shape
            "service": "{{{{label}}}}",  # Service shape
            "api": "({label})",  # Stadium shape
            "queue": "([{label}])",  # Double circle
            "user": "([{label}])",  # User shape
            "event": "([{label}])",  # Event shape
            "default": "[{label}]",  # Rectangle
        }

        # Component detection patterns
        self.component_patterns = {
            "database": r"\b(redis|postgres|mysql|mongodb|database|db|cache|store)\b",
            "service": r"\b(service|microservice|api|server|worker|agent)\b",
            "queue": r"\b(queue|kafka|rabbitmq|sqs|pubsub)\b",
            "user": r"\b(user|client|customer|actor)\b",
            "event": r"\b(event|message|trigger|signal)\b",
        }

    async def _extract_system_components(
        self, text: str
    ) -> tuple[list[DiagramNode], list[tuple[str, str]]]:
        """Extract system components and relationships from text.

        Args:
            text: Description of the system architecture

        Returns:
            Tuple of (nodes, relationships)
        """
        # Use LLM to extract components and relationships
        prompt = f"""
        You are a System Architect. Extract the system components and their relationships from this description:

        "{text}"

        Return in JSON format:
        {{
            "components": [
                {{"id": "unique_id", "label": "Display Label", "type": "service|database|queue|user|event"}}
            ],
            "relationships": [
                {{"from": "source_id", "to": "target_id", "label": "connection_label"}}
            ]
        }}

        Keep IDs short and descriptive (e.g., "API", "Redis", "User").
        """

        try:
            response = await self._call_llm(prompt, temperature=0.1)
            # Parse JSON response
            import json

            extracted = json.loads(response.content.strip())

            # Create nodes
            nodes = []
            for comp in extracted.get("components", []):
                node_type = comp.get("type", "default")
                shape_code = self.shape_mappings.get(node_type, self.shape_mappings["default"])

                node = DiagramNode(
                    id=comp["id"], label=comp["label"], shape_code=shape_code, node_type=node_type
                )
                nodes.append(node)

            relationships = [
                (rel["from"], rel["to"], rel.get("label", ""))
                for rel in extracted.get("relationships", [])
            ]

            return nodes, relationships

        except Exception as e:
            logger.error(f"Failed to extract components: {e}")
            return [], []

    def _generate_mermaid_code(
        self,
        nodes: list[DiagramNode],
        relationships: list[tuple[str, str]],
        diagram_type: DiagramType,
    ) -> str:
        """Generate Mermaid code from nodes and relationships.

        Args:
            nodes: List of diagram nodes
            relationships: List of (from, to, label) tuples
            diagram_type: Type of diagram to generate

        Returns:
            Complete Mermaid diagram code
        """
        # Start with diagram type
        lines = [diagram_type.value]

        # Add nodes
        for node in nodes:
            shape = self.shape_mappings.get(node.node_type, self.shape_mappings["default"])
            line = f"    {node.id}{shape.format(label=node.label)}"
            lines.append(line)

        # Add relationships
        for rel in relationships:
            if len(rel) == 2:
                from_node, to_node = rel
                label = ""
            else:
                from_node, to_node, label = rel

            if label:
                line = f"    {from_node} -->|{label}| {to_node}"
            else:
                line = f"    {from_node} --> {to_node}"
            lines.append(line)

        # Add subgraphs for grouping if needed
        if len(nodes) > 5:
            lines.insert(1, "    subgraph Data Plane")
            data_nodes = [n for n in nodes if n.node_type in ["database", "queue"]]
            for i, node in enumerate(data_nodes):
                lines.insert(
                    2 + i,
                    f"        {node.id}{self.shape_mappings.get(node.node_type, self.shape_mappings['default']).format(label=node.label)}",
                )
            lines.insert(2 + len(data_nodes), "    end")

        return "\n".join(lines)

    async def generate_diagram(
        self,
        description: str,
        diagram_type: DiagramType = DiagramType.FLOWCHART,
        caption: str | None = None,
    ) -> DiagramArtifact | None:
        """Generate a Mermaid diagram from text description.

        Args:
            description: Text description of the architecture
            diagram_type: Type of diagram to generate
            caption: Optional caption for the diagram

        Returns:
            DiagramArtifact if successful, None otherwise
        """
        try:
            # Extract components
            nodes, relationships = await self._extract_system_components(description)

            # Check complexity
            if len(nodes) > self.max_nodes:
                logger.warning(
                    f"System too complex ({len(nodes)} nodes), generating high-level diagram"
                )
                # Simplify to high-level components only
                nodes = nodes[: self.max_nodes]
                relationships = relationships[: self.max_nodes]

            # Generate Mermaid code
            mermaid_code = self._generate_mermaid_code(nodes, relationships, diagram_type)

            # Calculate complexity score
            complexity = min(1.0, len(nodes) / self.max_nodes)

            # Create artifact
            artifact = DiagramArtifact(
                mermaid_code=mermaid_code,
                caption=caption or "System Architecture Diagram",
                diagram_type=diagram_type,
                node_count=len(nodes),
                complexity_score=complexity,
            )

            logger.info(f"Generated {diagram_type} diagram with {len(nodes)} nodes")
            return artifact

        except Exception as e:
            logger.error(f"Failed to generate diagram: {e}")
            return None

    def render_artifact(self, artifact: DiagramArtifact) -> str:
        """Render diagram artifact as Markdown.

        Args:
            artifact: Diagram artifact to render

        Returns:
            Formatted Markdown string
        """
        return f"""### {artifact.caption}

```mermaid
{artifact.mermaid_code}
```

*Nodes: {artifact.node_count} | Complexity: {artifact.complexity_score:.1%}*
"""

    async def visualize_bullet(self, bullet_text: str) -> str | None:
        """Convert a resume bullet describing a system into a diagram.

        Args:
            bullet_text: Resume bullet point describing a system

        Returns:
            Rendered Markdown diagram if bullet describes a system
        """
        # Check if bullet describes a system
        system_keywords = ["architecture", "system", "pipeline", "built", "designed", "implemented"]
        if not any(keyword in bullet_text.lower() for keyword in system_keywords):
            return None

        # Generate diagram
        artifact = await self.generate_diagram(
            description=bullet_text, caption="Technical Architecture"
        )

        if artifact:
            return self.render_artifact(artifact)

        return None

    async def _call_llm(self, prompt: str, temperature: float = 0.3) -> LLMResponse:
        """Call the LLM with the given prompt.

        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        try:
            # Import here to avoid circular imports

            # Get Anthropic client
            client = get_client(Provider.ANTHROPIC)

            # Call LLM
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl(response.content[0].text)

        except Exception as e:
            logger.error(f"LLM call failed: {e}")

            # Return fallback response
            class LLMResponseImpl:
                def __init__(self, content: str):
                    self.content = content

            return LLMResponseImpl('{"components": [], "relationships": []}')