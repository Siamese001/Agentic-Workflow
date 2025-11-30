from agentic_core.l1_planning.planners.lic_plan_schema import LICPlan, PlanSchema

def test_schema_initialization():
    """Test LICPlan initialization with current architecture"""
    # Test default initialization
    p = LICPlan()
    assert p.plan_id == ""
    assert p.content == ""
    assert p.metadata == {}
    
    # Test parameterized initialization
    p2 = LICPlan(plan_id="test_plan", content="test content", metadata={"key": "value"})
    assert p2.plan_id == "test_plan"
    assert p2.content == "test content"
    assert p2.metadata == {"key": "value"}

def test_plan_schema_operations():
    """Test PlanSchema functionality"""
    schema = PlanSchema()
    
    # Test plan creation
    plan = schema.create_plan("test_id", "test_content")
    assert plan.plan_id == "test_id"
    assert plan.content == "test_content"
    assert plan.validate() is True
    
    # Test schema info
    info = schema.get_schema_info()
    assert "version" in info
    assert "required_fields" in info





