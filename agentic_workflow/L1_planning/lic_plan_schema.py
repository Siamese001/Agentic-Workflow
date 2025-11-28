"""
LICPlan Schema (L1 Planning Layer)
Typed container for ALL planning outputs.
"""

class LICPlan:
    """Stub typed container."""

    def __init__(self, message_type, scenario, parameters,
                 retrieval_plan, insight_plan, k_node_plan,
                 constraints, tone_rules, cta_style, assembly_plan):
        self.message_type = message_type
        self.scenario = scenario
        self.parameters = parameters
        self.retrieval_plan = retrieval_plan
        self.insight_plan = insight_plan
        self.k_node_plan = k_node_plan
        self.constraints = constraints
        self.tone_rules = tone_rules
        self.cta_style = cta_style
        self.assembly_plan = assembly_plan
