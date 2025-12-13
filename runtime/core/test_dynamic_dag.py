"""Test suite for Dynamic DAG Manager and mutation capabilities."""

import pytest
import networkx as nx
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from .dynamic_dag_manager import (
    DAGManager,
    DAGMutator,
    DAGMutation,
    MutationAction,
    HopSpec,
    MutationResult,
    DAGConfig,
    get_dag_manager
)

from .subatomic_hop import (
    SubatomicHop,
    SubatomicHopConfig,
    HopState,
    MutationRequired
)

from .reflection_engine import (
    MutationRequest,
    ReflectionEngine,
    ReflectionConfig
)

class TestDAGMutator:
    """Test suite for DAGMutator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = DAGConfig(max_depth=5, max_fan_out=3)
        self.mutator = DAGMutator(self.config)
        self.graph = nx.DiGraph()

        # Create a simple test graph
        self.graph.add_node("node1", depth=0)
        self.graph.add_node("node2", depth=1)
        self.graph.add_node("node3", depth=2)
        self.graph.add_edge("node1", "node2")
        self.graph.add_edge("node2", "node3")

    def test_initialization(self):
        """Test DAGMutator initialization."""
        assert self.mutator.config.max_depth == 5
        assert self.mutator.config.max_fan_out == 3
        assert len(self.mutator.mutation_history) == 0

    def test_spawn_predecessor_success(self):
        """Test successful predecessor spawning."""
        hop_spec = HopSpec(hop_function="test_function", hop_id="new_node")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="node2",
            new_hop_spec=hop_spec,
            reason="Need additional data",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is True
        assert "new_node" in self.graph.nodes
        assert ("new_node", "node2") in self.graph.edges
        assert result.affected_nodes == ["new_node", "node2"]

        # Verify graph is still a DAG
        assert nx.is_directed_acyclic_graph(self.graph)

    def test_spawn_successor_success(self):
        """Test successful successor spawning."""
        hop_spec = HopSpec(hop_function="test_function", hop_id="new_node")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_SUCCESSOR,
            target_hop_id="node2",
            new_hop_spec=hop_spec,
            reason="Need additional processing",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is True
        assert "new_node" in self.graph.nodes
        assert ("node2", "new_node") in self.graph.edges
        assert ("new_node", "node3") in self.graph.edges  # Edge moved

        # Verify graph is still a DAG
        assert nx.is_directed_acyclic_graph(self.graph)

    def test_skip_successor_success(self):
        """Test successful successor skipping."""
        mutation = DAGMutation(
            action=MutationAction.SKIP_SUCCESSOR,
            target_hop_id="node2",
            reason="Node not needed",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is True
        assert ("node1", "node3") in self.graph.edges  # Bridge created
        assert self.graph.nodes["node3"]["skipped_by"] == "node1"

        # Verify graph is still a DAG
        assert nx.is_directed_acyclic_graph(self.graph)

    def test_replace_node_success(self):
        """Test successful node replacement."""
        hop_spec = HopSpec(hop_function="new_function", hop_id="replacement")

        mutation = DAGMutation(
            action=MutationAction.REPLACE_NODE,
            target_hop_id="node2",
            new_hop_spec=hop_spec,
            reason="Upgrade node",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is True
        assert "replacement" in self.graph.nodes
        assert ("node1", "replacement") in self.graph.edges
        assert ("replacement", "node3") in self.graph.edges
        assert self.graph.nodes["node2"]["replaced"] is True

        # Verify graph is still a DAG
        assert nx.is_directed_acyclic_graph(self.graph)

    def test_depth_constraint_violation(self):
        """Test that depth constraints are enforced."""
        # Create a node at max depth
        self.graph.add_node("deep_node", depth=4)

        hop_spec = HopSpec(hop_function="test_function")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="deep_node",
            new_hop_spec=hop_spec,
            reason="Would exceed depth",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is False
        assert "exceed max depth" in result.message.lower()

    def test_fan_out_constraint_violation(self):
        """Test that fan-out constraints are enforced."""
        # Add many successors to node1
        for i in range(3):
            self.graph.add_node(f"successor_{i}", depth=1)
            self.graph.add_edge("node1", f"successor_{i}")

        hop_spec = HopSpec(hop_function="test_function")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_SUCCESSOR,
            target_hop_id="node1",
            new_hop_spec=hop_spec,
            reason="Would exceed fan-out",
            requester_hop_id="node1"
        )

        result = self.mutator.apply_mutation(self.graph, mutation)

        assert result.success is False
        assert "exceed max fan-out" in result.message.lower()

    def test_cycle_detection(self):
        """Test that cycles are prevented."""
        # Create a cycle-inducing mutation
        hop_spec = HopSpec(hop_function="test_function", hop_id="cycle_node")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="node1",
            new_hop_spec=hop_spec,
            reason="Would create cycle",
            requester_hop_id="node3"
        )

        # Manually add edge that would create cycle
        self.graph.add_edge("cycle_node", "node3")

        result = self.mutator.apply_mutation(self.graph, mutation)

        # Should fail due to cycle
        assert not result.success or "cycle" in result.message.lower()

    def test_mutation_history(self):
        """Test mutation history tracking."""
        hop_spec = HopSpec(hop_function="test_function")

        mutation = DAGMutation(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="node2",
            new_hop_spec=hop_spec,
            reason="Test",
            requester_hop_id="node1"
        )

        self.mutator.apply_mutation(self.graph, mutation)

        history = self.mutator.get_mutation_history()
        assert len(history) == 1
        assert history[0].success is True
        assert history[0].mutation_id == mutation.mutation_id

class TestDAGManager:
    """Test suite for DAGManager class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = DAGConfig(max_depth=5)
        self.manager = DAGManager(self.config)

        # Register test functions
        def test_function(x):
            return {"result": x * 2}

        def scraper_function(url):
            return {"scraped": f"Data from {url}"}

        self.manager.register_function("test_function", test_function)
        self.manager.register_function("scraper_function", scraper_function)

    def test_initialization(self):
        """Test DAGManager initialization."""
        assert self.manager.config.max_depth == 5
        assert isinstance(self.manager.graph, nx.DiGraph)
        assert len(self.manager.execution_queue) == 0
        assert len(self.manager.function_registry) == 2

    def test_function_registration(self):
        """Test function registration."""
        def new_function():
            return "test"

        self.manager.register_function("new_function", new_function)

        assert "new_function" in self.manager.function_registry
        assert self.manager.function_registry["new_function"] == new_function

    def test_add_node(self):
        """Test adding nodes to DAG."""
        config = SubatomicHopConfig(hop_id="test_hop")
        hop = SubatomicHop(lambda x: x, config)

        self.manager.add_node(hop)

        assert "test_hop" in self.manager.graph.nodes
        assert "test_hop" in self.manager.node_registry
        assert "test_hop" in self.manager.execution_queue

    def test_add_node_with_predecessors(self):
        """Test adding nodes with predecessors."""
        config1 = SubatomicHopConfig(hop_id="hop1")
        config2 = SubatomicHopConfig(hop_id="hop2")

        hop1 = SubatomicHop(lambda x: x, config1)
        hop2 = SubatomicHop(lambda x: x, config2)

        self.manager.add_node(hop1)
        self.manager.add_node(hop2, predecessors=["hop1"])

        assert ("hop1", "hop2") in self.manager.graph.edges
        assert "hop2" not in self.manager.execution_queue  # Has predecessor

    def test_create_mutation_request(self):
        """Test creating mutation requests."""
        mutation = self.manager.create_mutation_request(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="target",
            hop_function="scraper_function",
            reason="Need data",
            requester_hop_id="requester",
            url="http://example.com"
        )

        assert mutation.action == MutationAction.SPAWN_PREDECESSOR
        assert mutation.target_hop_id == "target"
        assert mutation.new_hop_spec.hop_function == "scraper_function"
        assert mutation.new_hop_spec.parameters["url"] == "http://example.com"

    def test_request_mutation_success(self):
        """Test successful mutation request."""
        # Add initial node
        config = SubatomicHopConfig(hop_id="target")
        hop = SubatomicHop(lambda x: x, config)
        self.manager.add_node(hop)

        # Create and apply mutation
        mutation = self.manager.create_mutation_request(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="target",
            hop_function="scraper_function",
            reason="Need scraped data",
            requester_hop_id="target"
        )

        result = self.manager.request_mutation(mutation)

        assert result.success is True
        assert "scraper_function" in self.manager.graph.nodes
        assert self.manager.stats["spawned_predecessors"] == 1
        assert "scraper_function" in self.manager.execution_queue

    def test_pause_and_resume_node(self):
        """Test pausing and resuming nodes."""
        config = SubatomicHopConfig(hop_id="test_hop")
        hop = SubatomicHop(lambda x: x, config)
        self.manager.add_node(hop)

        # Pause node
        assert self.manager.pause_node("test_hop") is True
        assert hop.state == HopState.PAUSED

        # Resume node
        assert self.manager.resume_node("test_hop") is True
        assert hop.state == HopState.RUNNING
        assert "test_hop" in self.manager.execution_queue

    def test_get_next_node(self):
        """Test getting next node from queue."""
        config = SubatomicHopConfig(hop_id="test_hop")
        hop = SubatomicHop(lambda x: x, config)
        self.manager.add_node(hop)

        next_hop = self.manager.get_next_node()
        assert next_hop == hop
        assert len(self.manager.execution_queue) == 0

        # Queue empty
        next_hop = self.manager.get_next_node()
        assert next_hop is None

    def test_graph_statistics(self):
        """Test graph statistics."""
        config1 = SubatomicHopConfig(hop_id="hop1")
        config2 = SubatomicHopConfig(hop_id="hop2")

        hop1 = SubatomicHop(lambda x: x, config1)
        hop2 = SubatomicHop(lambda x: x, config2)

        self.manager.add_node(hop1)
        self.manager.add_node(hop2, predecessors=["hop1"])

        stats = self.manager.get_graph_stats()

        assert stats["node_count"] == 2
        assert stats["edge_count"] == 1
        assert stats["queue_size"] == 1
        assert stats["registered_functions"] == 2

    def test_visualize_graph(self):
        """Test graph visualization data."""
        config = SubatomicHopConfig(hop_id="test_hop")
        hop = SubatomicHop(lambda x: x, config)
        self.manager.add_node(hop)

        viz = self.manager.visualize_graph()

        assert "nodes" in viz
        assert "edges" in viz
        assert len(viz["nodes"]) == 1
        assert viz["nodes"][0]["id"] == "test_hop"

class TestMutationIntegration:
    """Test suite for mutation integration with SubatomicHop."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = DAGConfig(max_depth=5)
        self.manager = DAGManager(self.config)

        # Register functions
        def resume_writer(data):
            if "job_description" not in data:
                # Request mutation
                raise MutationRequired(MutationRequest(
                    action="SPAWN_PREDECESSOR",
                    reason="Missing job description",
                    hop_function="jd_scraper",
                    parameters={"url": "http://example.com/job"}
                ))
            return {"resume": f"Resume for {data['job_description']}"}

        def jd_scraper(url):
            return {"job_description": f"Scraped from {url}"}

        self.manager.register_function("resume_writer", resume_writer)
        self.manager.register_function("jd_scraper", jd_scraper)

    @pytest.mark.asyncio
    async def test_mutation_during_execution(self):
        """Test mutation triggered during hop execution."""
        # Add initial node
        config = SubatomicHopConfig(hop_id="writer")
        writer_hop = SubatomicHop(
            self.manager.function_registry["resume_writer"],
            config
        )

        # Set DAG manager
        writer_hop.dag_manager = self.manager
        self.manager.add_node(writer_hop)

        # Execute and expect mutation
        try:
            await writer_hop.run(data={"skills": ["Python"]})
            assert False, "Should have raised MutationRequired"
        except MutationRequired as e:
            # Apply mutation
            mutation = self.manager.create_mutation_request(
                action=MutationAction.SPAWN_PREDECESSOR,
                target_hop_id="writer",
                hop_function="jd_scraper",
                reason=e.mutation_request.reason,
                requester_hop_id="writer",
                url="http://example.com/job"
            )

            result = self.manager.request_mutation(mutation)
            assert result.success is True

            # Verify scraper was added
            assert "jd_scraper" in self.manager.graph.nodes
            assert writer_hop.state == HopState.PAUSED

    def test_global_dag_manager(self):
        """Test global DAG manager instance."""
        manager1 = get_dag_manager()
        manager2 = get_dag_manager()

        # Should return same instance
        assert manager1 is manager2

class TestMutationScenarios:
    """Test realistic mutation scenarios."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = DAGManager()

        # Register realistic functions
        def resume_generator(profile, job_description):
            if not job_description:
                raise MutationRequired(MutationRequest(
                    action="SPAWN_PREDECESSOR",
                    reason="No job description provided",
                    hop_function="job_scraper",
                    parameters={"company": profile.get("company")}
                ))
            return {"resume": f"Tailored resume for {job_description}"}

        def job_scraper(company):
            return {"job_description": f"Job description for {company}"}

        def cover_letter_writer(resume, job_description):
            if len(job_description) < 50:
                raise MutationRequired(MutationRequest(
                    action="SPAWN_PREDECESSOR",
                    reason="Job description too brief",
                    hop_function="job_enricher",
                    parameters={"description": job_description}
                ))
            return {"cover_letter": f"Cover letter based on {job_description}"}

        def job_enricher(description):
            return {"job_description": description + " (enriched with more details)"}

        self.manager.register_function("resume_generator", resume_generator)
        self.manager.register_function("job_scraper", job_scraper)
        self.manager.register_function("cover_letter_writer", cover_letter_writer)
        self.manager.register_function("job_enricher", job_enricher)

    @pytest.mark.asyncio
    async def test_resume_generation_pipeline(self):
        """Test resume generation with missing job description."""
        # Create initial pipeline
        resume_config = SubatomicHopConfig(hop_id="resume")
        resume_hop = SubatomicHop(
            self.manager.function_registry["resume_generator"],
            resume_config
        )
        resume_hop.dag_manager = self.manager
        self.manager.add_node(resume_hop)

        # Execute and trigger mutation
        try:
            await resume_hop.run(profile={"company": "Acme"})
            assert False, "Should have raised MutationRequired"
        except MutationRequired:
            pass

        # Apply mutation
        mutation = self.manager.create_mutation_request(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="resume",
            hop_function="job_scraper",
            reason="Need job description",
            requester_hop_id="resume",
            company="Acme"
        )

        result = self.manager.request_mutation(mutation)
        assert result.success is True

        # Verify structure
        assert "job_scraper" in self.manager.graph.nodes
        assert ("job_scraper", "resume") in self.manager.graph.edges

    @pytest.mark.asyncio
    async def test_nested_mutations(self):
        """Test multiple mutations in sequence."""
        # Create pipeline: cover_letter -> resume
        resume_config = SubatomicHopConfig(hop_id="resume")
        resume_hop = SubatomicHop(
            self.manager.function_registry["resume_generator"],
            resume_config
        )

        cover_config = SubatomicHopConfig(hop_id="cover_letter")
        cover_hop = SubatomicHop(
            self.manager.function_registry["cover_letter_writer"],
            cover_config
        )

        self.manager.add_node(resume_hop)
        self.manager.add_node(cover_hop, predecessors=["resume"])

        # Trigger first mutation (resume needs job)
        try:
            await resume_hop.run(profile={"company": "Acme"})
        except MutationRequired:
            pass

        mutation1 = self.manager.create_mutation_request(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="resume",
            hop_function="job_scraper",
            reason="Need job description",
            requester_hop_id="resume",
            company="Acme"
        )

        self.manager.request_mutation(mutation1)

        # Now cover letter will also need enrichment
        cover_hop.dag_manager = self.manager

        try:
            await cover_hop.run(
                resume={"resume": "test"},
                job_description="Brief"
            )
        except MutationRequired:
            pass

        mutation2 = self.manager.create_mutation_request(
            action=MutationAction.SPAWN_PREDECESSOR,
            target_hop_id="cover_letter",
            hop_function="job_enricher",
            reason="Need job enrichment",
            requester_hop_id="cover_letter",
            description="Brief"
        )

        result2 = self.manager.request_mutation(mutation2)
        assert result2.success is True

        # Verify final structure
        assert self.manager.graph.number_of_nodes() == 4
        assert nx.is_directed_acyclic_graph(self.manager.graph)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
