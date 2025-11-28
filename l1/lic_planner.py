from typing import Dict, Any
from .lic_plan_schema import (
    LICPlan, RoutingPlan, RetrievalPlan, InsightPlan, KNodePlan,
    TonePlan, CTAPlan, ConstraintPlan, ValidatorPlan, FamilyPlan,
    ScenarioPlan, SeniorityPlan, TemplatePlan, MissionPlan,
    RouteType
)

class LICPlanner:
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        
    def build_routing_plan(self, message_type: str, message_context: Dict[str, Any]) -> RoutingPlan:
        routing_config = self.spec["routing"][message_type]
        return RoutingPlan(
            route=RouteType(message_type),
            conditions=routing_config["conditions"],
            constraints=routing_config["constraints"]
        )
    
    def build_parameter_plan(self) -> Dict[str, Any]:
        return self.spec["parameters"]
    
    def build_retrieval_plan(self) -> RetrievalPlan:
        rag_config = self.spec["retrieval"]["rag_pipeline_v75"]
        return RetrievalPlan(
            hyde_enabled=rag_config["stage_0_hyde"]["enabled"],
            hyde_trigger=rag_config["stage_0_hyde"]["trigger"],
            web_search_calls=rag_config["stage_1_hybrid_recall"]["web_search_calls"],
            internal_sources=rag_config["stage_1_hybrid_recall"]["internal_sources"],
            reranking_model=rag_config["stage_2_cross_encoder_reranking"]["model"],
            reranking_threshold=rag_config["stage_2_cross_encoder_reranking"]["threshold"],
            self_rag_max_hops=rag_config["stage_3_self_rag"]["max_hops"],
            episodic_memory_enabled=rag_config["stage_4_episodic_memory"]["enabled"],
            knowledge_graph_enabled=rag_config["stage_5_knowledge_graph"]["enabled"],
            few_shot_enabled=rag_config["stage_6_few_shot_injection"]["enabled"]
        )
    
    def build_insight_plan(self) -> InsightPlan:
        signal_config = self.spec["insights"]["signal_quality_scorer"]
        confidence_config = self.spec["insights"]["claim_confidence_scorer"]
        return InsightPlan(
            signal_weights=signal_config["source_weights"],
            min_signal_threshold=signal_config["minimum_signal_threshold"],
            per_claim_min_confidence=confidence_config["per_claim_minimum"],
            aggregate_min_confidence=confidence_config["aggregate_minimum"],
            confidence_enforcement=confidence_config["enforcement"]
        )
    
    def build_knode_plan(self) -> KNodePlan:
        knode_config = self.spec["k_nodes"]
        return KNodePlan(
            hop_order=knode_config["hop_execution_order"],
            assembly_policy=knode_config["assembly_engine"]["policy"],
            validation_gates=knode_config["assembly_engine"]["validation_gates"]
        )
    
    def build_constraint_plan(self) -> ConstraintPlan:
        constraint_config = self.spec["constraints"]
        return ConstraintPlan(
            forbidden_verbs=constraint_config["content_cleanliness"]["forbidden_verbs"],
            filler_patterns=constraint_config["content_cleanliness"]["filler_patterns"],
            placeholder_patterns=constraint_config["content_cleanliness"]["placeholder_patterns"],
            word_count_tolerance=constraint_config["structural_validation"]["word_count_tolerance"],
            ascii_rules=constraint_config["ascii_hygiene"]["rules"]
        )
    
    def build_tone_plan(self) -> TonePlan:
        tone_config = self.spec["tone"]
        return TonePlan(
            archetype_mappings=tone_config["archetype_tone_mappings"],
            language_adaptation=tone_config["language_matcher"]
        )
    
    def build_cta_plan(self) -> CTAPlan:
        cta_config = self.spec["cta"]
        return CTAPlan(
            archetype_styles=cta_config["archetype_specific"],
            date_window_rules=cta_config["date_window_engine"]
        )
    
    def build_validator_plan(self) -> ValidatorPlan:
        validator_config = self.spec["validators"]
        return ValidatorPlan(
            error_codes=validator_config["error_code_registry"],
            severity_thresholds=validator_config["validation_severity_thresholds"],
            master_gate=validator_config["master_validation_gate"]
        )
    
    def build_family_plan(self) -> FamilyPlan:
        family_config = self.spec["families"]
        return FamilyPlan(
            archetype_templates=family_config["archetype_generation_templates"],
            signature_formats=family_config["signature_formats"]
        )
    
    def build_scenario_plan(self) -> ScenarioPlan:
        scenario_config = self.spec["scenarios"]["entity_grounding_framework"]
        return ScenarioPlan(
            entity_grounding=scenario_config["pre_generation_extraction"],
            team_whitelist=scenario_config["team_whitelist"],
            generation_constraints=scenario_config["generation_constraints"]
        )
    
    def build_seniority_plan(self) -> SeniorityPlan:
        seniority_config = self.spec["seniority"]
        return SeniorityPlan(
            taxonomy=seniority_config["recipient_classifier_taxonomy"],
            classification_rules=seniority_config["deterministic_classification_v1"],
            default_archetype=seniority_config["default_archetype"],
            default_confidence=seniority_config["default_confidence"]
        )
    
    def build_template_plan(self) -> TemplatePlan:
        template_config = self.spec["templates"]
        return TemplatePlan(
            cta_templates=template_config["cta_templates"],
            system_prompt=template_config["generation_system_prompt"],
            greeting_templates=template_config["greeting_templates"]
        )
    
    def build_mission_plan(self) -> MissionPlan:
        mission_config = self.spec["mission"]
        return MissionPlan(
            sender_structure=mission_config["sender_profile_structure"],
            recipient_structure=mission_config["recipient_profile_structure"],
            job_description_structure=mission_config["job_description_structure"],
            message_context_structure=mission_config["message_context_structure"]
        )
    
    def build_complete_plan(self, message_type: str, message_context: Dict[str, Any]) -> LICPlan:
        return LICPlan(
            routing=self.build_routing_plan(message_type, message_context),
            parameters=self.build_parameter_plan(),
            retrieval=self.build_retrieval_plan(),
            insights=self.build_insight_plan(),
            k_nodes=self.build_knode_plan(),
            constraints=self.build_constraint_plan(),
            tone=self.build_tone_plan(),
            cta=self.build_cta_plan(),
            validators=self.build_validator_plan(),
            families=self.build_family_plan(),
            scenarios=self.build_scenario_plan(),
            seniority=self.build_seniority_plan(),
            templates=self.build_template_plan(),
            mission=self.build_mission_plan()
        )
