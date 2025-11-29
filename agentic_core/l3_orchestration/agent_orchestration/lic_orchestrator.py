from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from l1.lic_planner import LICPlanner
from l2.lic_k1_research import LIC_K1_Research
from l2.lic_k2_insights import LIC_K2_Insights
from l2.lic_k3_draft import LIC_K3_Draft
from l2.lic_k4_regen import LIC_K4_Regen
from l2.lic_k5_validation import LIC_K5_Validation
from l2.lic_k6_cta import LIC_K6_CTA
from l2.lic_k7_assembly import LIC_K7_Assembly

@dataclass
class OrchestratorOutput:
    final_message: str
    execution_trace: List[Dict[str, Any]]
    k_node_outputs: Dict[str, Any]
    success: bool
    error_message: str

class LICOrchestrator:
    def __init__(self, atomic_spec: Dict[str, Any]):
        self.spec = atomic_spec
        self.planner = LICPlanner(atomic_spec)
        
    def _execute_k1_research(self, k1_research, message_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            recipient = message_context.get("recipient", {})
            research_output = k1_research.execute(recipient, message_context)
            
            return {
                "k1_research": asdict(research_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k1_research": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k2_insights(self, k2_insights, k1_output: Dict[str, Any], message_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if k1_output.get("status") != "SUCCESS":
                return {
                    "k2_insights": None,
                    "status": "SKIPPED",
                    "error": "K1 research failed"
                }
                
            research_data = k1_output.get("k1_research", {})
            insight_output = k2_insights.execute(research_data)
            
            return {
                "k2_insights": asdict(insight_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k2_insights": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k3_draft(self, k3_draft, k1_output: Dict[str, Any], k2_output: Dict[str, Any], message_context: Dict[str, Any], sender_info: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if k1_output.get("status") != "SUCCESS":
                return {
                    "k3_draft": None,
                    "status": "SKIPPED",
                    "error": "K1 research failed"
                }
                
            research_data = k1_output.get("k1_research", {})
            draft_output = k3_draft.execute(research_data, message_context, sender_info)
            
            return {
                "k3_draft": asdict(draft_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k3_draft": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k4_regen(self, k4_regen, k3_output: Dict[str, Any], k2_output: Dict[str, Any], message_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if k3_output.get("status") != "SUCCESS":
                return {
                    "k4_regen": None,
                    "status": "SKIPPED",
                    "error": "K3 draft failed"
                }
                
            draft_data = k3_output.get("k3_draft", {})
            insight_data = k2_output.get("k2_insights", {})
            archetype = message_context.get("recipient_type", "EXECUTIVE")
            
            regen_output = k4_regen.execute(draft_data, insight_data, archetype)
            
            return {
                "k4_regen": asdict(regen_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k4_regen": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k5_validation(self, k5_validation, k3_output: Dict[str, Any], k4_output: Dict[str, Any], k2_output: Dict[str, Any], k1_output: Dict[str, Any], message_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if k3_output.get("status") != "SUCCESS":
                return {
                    "k5_validation": None,
                    "status": "SKIPPED",
                    "error": "K3 draft failed"
                }
                
            draft_data = k3_output.get("k3_draft", {})
            regen_data = k4_output.get("k4_regen", {})
            insight_data = k2_output.get("k2_insights", {})
            research_data = k1_output.get("k1_research", {})
            
            if regen_data and regen_data.get("regenerated_draft"):
                final_draft = regen_data["regenerated_draft"]
            else:
                final_draft = draft_data
                
            validation_output = k5_validation.execute(final_draft, insight_data, research_data, message_context)
            
            return {
                "k5_validation": asdict(validation_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k5_validation": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k6_cta(self, k6_cta, message_context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            archetype = message_context.get("recipient_type", "EXECUTIVE")
            cta_output = k6_cta.execute(message_context, archetype)
            
            return {
                "k6_cta": asdict(cta_output),
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k6_cta": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def _execute_k7_assembly(self, k7_assembly, all_k_outputs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            assembly_output = k7_assembly.execute(all_k_outputs)
            
            return {
                "k7_assembly": assembly_output,
                "status": "SUCCESS",
                "error": None
            }
        except Exception as e:
            return {
                "k7_assembly": None,
                "status": "FAILED",
                "error": str(e)
            }
    
    def execute_full_pipeline(self, message_type: str, message_context: Dict[str, Any], sender_info: Dict[str, Any]) -> OrchestratorOutput:
        execution_trace = []
        k_node_outputs = {}
        
        try:
            plan = self.planner.build_complete_plan(message_type, message_context)
            
            k1_research = LIC_K1_Research(asdict(plan.retrieval))
            k1_result = self._execute_k1_research(k1_research, message_context)
            execution_trace.append({"node": "K1", "status": k1_result["status"], "error": k1_result.get("error")})
            k_node_outputs.update(k1_result)
            
            k2_insights = LIC_K2_Insights(asdict(plan.insights))
            k2_result = self._execute_k2_insights(k2_insights, k1_result, message_context)
            execution_trace.append({"node": "K2", "status": k2_result["status"], "error": k2_result.get("error")})
            k_node_outputs.update(k2_result)
            
            k3_draft = LIC_K3_Draft(asdict(plan.templates), asdict(plan.tone))
            k3_result = self._execute_k3_draft(k3_draft, k1_result, k2_result, message_context, sender_info)
            execution_trace.append({"node": "K3", "status": k3_result["status"], "error": k3_result.get("error")})
            k_node_outputs.update(k3_result)
            
            k4_regen = LIC_K4_Regen(asdict(plan.validators), asdict(plan.constraints))
            k4_result = self._execute_k4_regen(k4_regen, k3_result, k2_result, message_context)
            execution_trace.append({"node": "K4", "status": k4_result["status"], "error": k4_result.get("error")})
            k_node_outputs.update(k4_result)
            
            k5_validation = LIC_K5_Validation(asdict(plan.validators), asdict(plan.constraints))
            k5_result = self._execute_k5_validation(k5_validation, k3_result, k4_result, k2_result, k1_result, message_context)
            execution_trace.append({"node": "K5", "status": k5_result["status"], "error": k5_result.get("error")})
            k_node_outputs.update(k5_result)
            
            k6_cta = LIC_K6_CTA(asdict(plan.cta))
            k6_result = self._execute_k6_cta(k6_cta, message_context)
            execution_trace.append({"node": "K6", "status": k6_result["status"], "error": k6_result.get("error")})
            k_node_outputs.update(k6_result)
            
            k7_assembly = LIC_K7_Assembly(asdict(plan.k_nodes), asdict(plan.validators))
            k7_result = self._execute_k7_assembly(k7_assembly, k_node_outputs)
            execution_trace.append({"node": "K7", "status": k7_result["status"], "error": k7_result.get("error")})
            k_node_outputs.update(k7_result)
            
            final_assembly = k7_result.get("k7_assembly")
            if final_assembly and final_assembly.validation_status == "VALID":
                return OrchestratorOutput(
                    final_message=final_assembly.final_message,
                    execution_trace=execution_trace,
                    k_node_outputs=k_node_outputs,
                    success=True,
                    error_message=""
                )
            else:
                return OrchestratorOutput(
                    final_message="",
                    execution_trace=execution_trace,
                    k_node_outputs=k_node_outputs,
                    success=False,
                    error_message="Final validation failed"
                )
                
        except Exception as e:
            return OrchestratorOutput(
                final_message="",
                execution_trace=execution_trace,
                k_node_outputs=k_node_outputs,
                success=False,
                error_message=f"Pipeline execution failed: {str(e)}"
            )
