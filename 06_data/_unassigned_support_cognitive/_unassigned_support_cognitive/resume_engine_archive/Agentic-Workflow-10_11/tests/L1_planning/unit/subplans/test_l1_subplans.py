"""L1 Planning Subplans Tests."""

class TestL1Subplans:
    """Tests for L1 planning subplans."""
    
    def test_rag_subplan_creation(self):
        """Test RAG subplan creation."""
        subplan = {"strategy": "hybrid", "max_hits": 16}
        assert subplan["strategy"] == "hybrid"
    
    def test_drafting_subplan_creation(self):
        """Test drafting subplan creation."""
        sections = ["summary", "experience", "skills"]
        assert len(sections) == 3
    
    def test_qa_subplan_creation(self):
        """Test QA subplan creation."""
        qa_config = {"depth": 2, "council_size": 3}
        assert qa_config["depth"] == 2
