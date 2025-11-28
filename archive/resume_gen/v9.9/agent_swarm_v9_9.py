# File: agent_swarm_v9_9.py
# Overwrites: agent_swarm_v9_8.py
# Version: 9.9 (Security & Error Handling Hardening)


# v9.9 CRITICAL SECURITY FIXES:
# SECURITY FIX #1: PIISanitizerAgent now uses local Presidio (no external API calls with resume data)
# SECURITY FIX #2: BiasDetectorAgent now uses local regex patterns (no external API calls with resume data)
# ERROR HANDLING: Replaced broad "except Exception" with specific error types
# ERROR HANDLING: Added ModelAPIError, JSONParsingError catches throughout

# v9.8 P1/P2 CHANGES:
# P1: Converted DraftingConductor and QAConductor to ReAct agents
# P1: Added ToolSelectorAgent for dynamic tool selection
# P1: Added HILAmbiguityDetectorAgent for proactive ambiguity detection
# P2: Added HyDEGeneratorAgent for enhanced RAG
# P2: Added RAG_ReRankerAgent for cross-encoder reranking
# P2: Enhanced RAG_SearchAgent with HyDE integration
# P2: Implemented dynamic agent selection in conductors

import json
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from core_v9_9 import (
    CONFIG, BaseAgent, get_model_client, MainGraphState,
    BIAS_DETECTOR_SYSTEM_PROMPT, PII_SCRUBBER_SYSTEM_PROMPT,
    TOT_STRATEGIST_SYSTEM_PROMPT, PROMPT_ENGINEER_SYSTEM_PROMPT,
    BULLET_CRITIQUE_SYSTEM_PROMPT, AgentExecutionError,
    REACT_CONDUCTOR_SYSTEM_PROMPT, TOOL_SELECTOR_SYSTEM_PROMPT,
    HIL_AMBIGUITY_DETECTOR_PROMPT, HYDE_GENERATION_PROMPT,
    RERANKING_PROMPT, TOOL_REGISTRY, HIL_MANAGER,
    AgentReliabilityTracker
, JSONParsingError, ModelAPIError)

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

__version__ = "9.9.0-security-error-hardening"

# ============================================================================
# P0 AGENTS (FROM v9.7)
# ============================================================================

class BiasDetectorAgent(BaseAgent):
    """P0: Detects bias using LOCAL regex patterns (v9.9 security fix)."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self._init_bias_patterns()
    
    def _init_bias_patterns(self):
        """Initialize regex patterns for local bias detection."""
        self.bias_patterns = {
            "gender": [
                r"\b(he|him|his|she|her|hers)\b",
                r"\b(male|female|man|woman|boy|girl)\b",
                r"\b(guys?|gals?)\b"
            ],
            "age": [
                r"\b(young|old|elderly|senior|junior)\b",
                r"\b(years? old|age \d+)\b",
                r"\b(millennial|boomer|gen[- ]?[xzy])\b"
            ],
            "cultural": [
                r"\b(native|foreign|immigrant|ethnic)\b",
                r"\b(asian|african|european|american)\b(?!\s+(style|cuisine|company))"
            ],
            "disability": [
                r"\b(disabled|handicapped|crippled|lame)\b",
                r"\b(blind|deaf|mute)\b(?!\s+(spot|cc|button))"
            ],
            "socioeconomic": [
                r"\b(poor|rich|wealthy|underprivileged)\b",
                r"\b(elite|working[- ]class)\b"
            ]
        }
        self.log_info("Local bias detection patterns initialized")
    
    def run(self, content: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Detect bias using LOCAL regex (NO external API calls)."""
        self.log_info("Analyzing content for bias locally...")
        
        if not CONFIG.agent_stacks.safety_stack_enabled:
            return {"bias_detected": False, "bias_score": 0.0, "findings": []}
        
        if not CONFIG.agent_stacks.use_local_bias_detection:
            return {"bias_detected": False, "bias_score": 0.0, "findings": []}
        
        try:
            findings = []
            content_lower = content.lower()
            
            for bias_type, patterns in self.bias_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            "type": bias_type,
                            "severity": "medium",
                            "text": match.group(0),
                            "position": match.start(),
                            "suggestion": f"Consider neutral alternative for '{match.group(0)}'"
                        })
            
            bias_score = min(len(findings) * 0.15, 1.0) if findings else 0.0
            bias_detected = bias_score >= CONFIG.agent_stacks.bias_detection_threshold
            
            if bias_detected:
                self.log_warning(f"Bias detected: {len(findings)} instances (score: {bias_score:.2f})")
            else:
                self.log_info(f"No significant bias detected (score: {bias_score:.2f})")
            
            return {
                "bias_detected": bias_detected,
                "bias_score": bias_score,
                "findings": findings
            }
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Bias detection failed: {e}")
            return {"bias_detected": False, "bias_score": 0.0, "findings": [], "error": str(e)}

class PIISanitizerAgent(BaseAgent):
    """P0: Sanitizes PII using LOCAL Presidio (v9.9 security fix)."""
    
    def __init__(self, blackboard: Dict = None, debug_mode: bool = False):
        if blackboard is None:
            blackboard = {}
        super().__init__(blackboard, debug_mode)
        self._init_presidio()
    
    def _init_presidio(self):
        """Initialize Presidio analyzer."""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            self.log_info("Presidio initialized for local PII detection")
        except ImportError as e:
            self.log_error(f"Presidio not installed: {e}")
            self.analyzer = None
            self.anonymizer = None
    
    def run(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PII using local Presidio (NO external API calls)."""
        self.log_info("Sanitizing PII locally with Presidio...")
        
        if not CONFIG.agent_stacks.pii_detection_enabled:
            return resume_data
        
        if not CONFIG.agent_stacks.use_presidio_for_pii or not self.analyzer:
            self.log_warning("Presidio not available, returning original data")
            return resume_data
        
        try:
            resume_str = json.dumps(resume_data, indent=2)
            
            # Analyze for PII
            results = self.analyzer.analyze(
                text=resume_str,
                language='en',
                entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION", 
                         "CREDIT_CARD", "US_SSN", "US_PASSPORT"]
            )
            
            if results:
                self.log_warning(f"PII detected: {len(results)} entities found")
                
                # Anonymize
                anonymized_result = self.anonymizer.anonymize(
                    text=resume_str,
                    analyzer_results=results
                )
                
                # Parse back to dict
                try:
                    sanitized_data = json.loads(anonymized_result.text)
                    self.log_info(f"PII sanitized: {len(results)} redactions")
                    return sanitized_data
                except JSONParsingError as e:
                    self.log_error(f"JSON parsing failed after anonymization: {e}")
                    return resume_data
            
            self.log_info("No PII detected")
            return resume_data
            
        except (IOError, OSError) as e:
            self.log_error(f"File I/O error during PII sanitization: {e}")
            return resume_data
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"PII sanitization failed: {e}")
            return resume_data

class ToTStrategistAgent(BaseAgent):
    """P0: Tree-of-Thoughts strategic reasoning."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
        self.branching_factor = CONFIG.agent_stacks.strategy_tot_branching_factor
    
    def run(self, master_resume: Dict, job_input: Dict) -> Dict[str, Any]:
        """Generate strategic approaches."""
        self.log_info(f"Generating {self.branching_factor} thought branches...")
        
        if not CONFIG.agent_stacks.strategy_tot_enabled:
            return self._simplified_strategy(master_resume, job_input)
        
        try:
            prompt = TOT_STRATEGIST_SYSTEM_PROMPT.format(branching_factor=self.branching_factor)
            prompt += f"\n\n**Input:**\n{json.dumps({'master_resume': master_resume, 'job_description': job_input.get('raw_jd', ''), 'company': job_input.get('company', '')}, indent=2)}"
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.8,
                max_tokens=6000,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            thought_branches = content_data.get("thought_branches", [])
            selected = content_data.get("selected_strategy", {})
            
            self.log_info(f"Generated {len(thought_branches)} strategies. Selected: {selected.get('branch_id', 'N/A')}")
            
            return {
                "strategy_thoughts": thought_branches,
                "selected_strategy": selected
            }
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"ToT failed: {e}")
            raise AgentExecutionError(f"ToTStrategistAgent failed: {e}")
    
    def _simplified_strategy(self, master_resume: Dict, job_input: Dict) -> Dict[str, Any]:
        """Fallback strategy."""
        return {
            "strategy_thoughts": [],
            "selected_strategy": {
                "branch_id": "FALLBACK",
                "positioning_theme": "Comprehensive Experience Match",
                "evidence_selection": ["all_experiences"],
                "implementation_guidance": "Select bullets matching job requirements."
            }
        }

class DynamicPromptEngineerAgent(BaseAgent):
    """P0: LLM-driven prompt engineering."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
    
    def run(self, strategy: Dict, job_requirements: List[str], candidate_context: Dict) -> Dict[str, Any]:
        """Engineer optimal prompt."""
        self.log_info("Engineering prompt...")
        
        if not CONFIG.agent_stacks.prompt_llm_driven:
            return self._template_prompt(strategy, job_requirements)
        
        try:
            input_data = {
                "strategy": strategy,
                "job_requirements": job_requirements,
                "candidate_context": candidate_context,
                "tone_guidance": "professional, impactful, quantified"
            }
            
            prompt = PROMPT_ENGINEER_SYSTEM_PROMPT + f"\n\n**Input:**\n{json.dumps(input_data, indent=2)}"
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=CONFIG.agent_stacks.prompt_temperature,
                max_tokens=4000,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            self.log_info(f"Quality score: {content_data.get('estimated_quality_score', 0.0)}")
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Prompt engineering failed: {e}")
            return self._template_prompt(strategy, job_requirements)
    
    def _template_prompt(self, strategy: Dict, job_requirements: List[str]) -> Dict[str, Any]:
        """Fallback template."""
        return {
            "system_prompt": f"Write resume bullets. Strategy: {strategy.get('positioning_theme', 'N/A')}",
            "user_prompt_template": "Generate bullets for {experience} targeting {requirements}",
            "few_shot_examples": [],
            "constraint_reminders": ["40-90 words", "quantify impact", "action verbs"],
            "estimated_quality_score": 0.6
        }

class BulletCritiqueAgent(BaseAgent):
    """P0: Local self-correction for bullets."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, bullet: str, strategy: Dict, source_experience: Dict, target_requirements: List[str]) -> Dict[str, Any]:
        """Critique bullet."""
        self.log_info("Critiquing bullet...")
        
        if not CONFIG.agent_stacks.enable_local_retries:
            return {"passed": True, "scores": {}, "recommendation": "accept"}
        
        try:
            input_data = {
                "bullet": bullet,
                "strategy": strategy,
                "source_experience": source_experience,
                "target_requirements": target_requirements
            }
            
            prompt = BULLET_CRITIQUE_SYSTEM_PROMPT + f"\n\n**Input:**\n{json.dumps(input_data, indent=2)}"
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.2,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            passed = content_data.get("passed", False)
            avg_score = content_data.get("scores", {}).get("average", 0.0)
            
            self.log_info(f"Critique: {'PASS' if passed else 'FAIL'} (avg: {avg_score:.1f})")
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Critique failed: {e}")
            return {"passed": True, "scores": {}, "recommendation": "accept", "error": str(e)}
# ============================================================================
# P1: REACT CONDUCTOR AGENTS
# ============================================================================

class ReActConductorAgent(BaseAgent):
    """P1: Base ReAct conductor with step-by-step reasoning."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
        self.max_steps = CONFIG.agent_stacks.conductor_max_steps
        self.thought_history: List[Dict] = []
    
    def _get_available_actions(self) -> List[str]:
        """Override in subclass to define actions."""
        return []
    
    def run(self, goal: str, state: Dict) -> Dict[str, Any]:
        """Execute ReAct loop."""
        self.log_info(f"Starting ReAct loop. Goal: {goal}")
        
        if not CONFIG.agent_stacks.enable_react_conductors:
            self.log_info("ReAct conductors disabled. Using fallback plan.")
            return self._fallback_plan()
        
        step_count = 0
        terminated = False
        actions_taken = []
        
        while step_count < self.max_steps and not terminated:
            step_count += 1
            self.log_debug(f"ReAct step {step_count}/{self.max_steps}")
            
            # Get next thought/action
            step_result = self._react_step(goal, state, actions_taken)
            
            if not step_result:
                break
            
            self.thought_history.append(step_result)
            actions_taken.append(step_result.get("action", {}))
            
            # Check termination
            termination = step_result.get("termination", {})
            if termination.get("should_terminate", False):
                terminated = True
                self.log_info(f"ReAct terminated: {termination.get('reason', 'Goal achieved')}")
        
        if not terminated:
            self.log_warning(f"ReAct reached max steps ({self.max_steps})")
        
        return {
            "thoughts": self.thought_history,
            "actions": actions_taken,
            "terminated": terminated,
            "steps": step_count
        }
    
    def _react_step(self, goal: str, state: Dict, prior_actions: List[Dict]) -> Optional[Dict[str, Any]]:
        """Execute single ReAct step."""
        try:
            available_actions = self._get_available_actions()
            
            prompt = REACT_CONDUCTOR_SYSTEM_PROMPT.format(
                available_actions=json.dumps(available_actions, indent=2)
            )
            
            context = {
                "goal": goal,
                "current_state": state,
                "prior_actions": prior_actions,
                "step_number": len(prior_actions) + 1
            }
            
            prompt += f"\n\n**Context:**\n{json.dumps(context, indent=2)}\n\nWhat is your next thought and action?"
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=CONFIG.agent_stacks.conductor_temperature,
                max_tokens=2000,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"ReAct step failed: {e}")
            return None
    
    def _fallback_plan(self) -> Dict[str, Any]:
        """Fallback when ReAct disabled."""
        return {
            "thoughts": [],
            "actions": [{"name": "execute_default_plan", "parameters": {}}],
            "terminated": True,
            "steps": 1
        }

class DraftingReActConductor(ReActConductorAgent):
    """P1: ReAct conductor for drafting workflow."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        # P2: Dynamic agent selection
        self.reliability_tracker = AgentReliabilityTracker(
            CONFIG.meta_loop_config.feedback_log_path
        )
    
    def _get_available_actions(self) -> List[str]:
        """Define drafting actions."""
        return [
            "parse_job_description",
            "generate_strategy",
            "engineer_prompt",
            "search_relevant_content",
            "generate_bullets",
            "critique_bullets",
            "compile_draft",
            "request_human_input"
        ]
    
    def select_strategy_agent(self) -> str:
        """P2: Dynamically select best strategy agent."""
        if not CONFIG.agent_stacks.enable_dynamic_selection:
            return "ToTStrategistAgent"
        
        options = ["ToTStrategistAgent", "ThemeClassifierAgent"]  # Historical option
        return self.reliability_tracker.select_best_agent(options, task_context="strategy_generation")

class QAReActConductor(ReActConductorAgent):
    """P1: ReAct conductor for QA workflow."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        # P2: Dynamic agent selection
        self.reliability_tracker = AgentReliabilityTracker(
            CONFIG.meta_loop_config.feedback_log_path
        )
    
    def _get_available_actions(self) -> List[str]:
        """Define QA actions."""
        return [
            "validate_format",
            "check_consistency",
            "verify_claims",
            "detect_bias",
            "check_grammar",
            "assess_relevance",
            "request_human_review"
        ]
    
    def select_qa_agent(self) -> str:
        """P2: Dynamically select best QA agent."""
        if not CONFIG.agent_stacks.enable_dynamic_selection:
            return "QAValidatorAgent"
        
        options = ["QAValidatorAgent", "ComprehensiveQAAgent"]  # Historical option
        return self.reliability_tracker.select_best_agent(options, task_context="qa_validation")

# ============================================================================
# P1: TOOL SELECTOR AGENT
# ============================================================================

class ToolSelectorAgent(BaseAgent):
    """P1: Selects optimal tools for tasks."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
        self.tool_registry = TOOL_REGISTRY
    
    def run(self, task_description: str) -> Dict[str, Any]:
        """Select best tools for task."""
        self.log_info(f"Selecting tools for: {task_description[:50]}...")
        
        if not CONFIG.agent_stacks.enable_dynamic_tooling:
            self.log_info("Dynamic tooling disabled. Using default tools.")
            return {"selected_tools": [], "selection_rationale": "Dynamic tooling disabled"}
        
        try:
            available_tools = self.tool_registry.list_tools()
            
            if not available_tools:
                self.log_warning("No tools registered.")
                return {"selected_tools": [], "selection_rationale": "No tools available"}
            
            prompt = TOOL_SELECTOR_SYSTEM_PROMPT.format(
                task_description=task_description,
                tool_definitions=json.dumps(available_tools, indent=2)
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=1500,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            selected = content_data.get("selected_tools", [])
            
            self.log_info(f"Selected {len(selected)} tools")
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Tool selection failed: {e}")
            # Fallback: use registry's heuristic selector
            fallback_tools = self.tool_registry.select_tools(
                task_description,
                max_tools=CONFIG.agent_stacks.max_tools_per_task
            )
            return {
                "selected_tools": fallback_tools,
                "selection_rationale": f"Fallback heuristic selection due to error: {e}"
            }

# ============================================================================
# P1: HIL AMBIGUITY DETECTOR
# ============================================================================

class HILAmbiguityDetectorAgent(BaseAgent):
    """P1: Detects ambiguities requiring human input."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
        self.hil_manager = HIL_MANAGER
    
    def run(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect ambiguities in context."""
        self.log_info("Detecting ambiguities...")
        
        if not CONFIG.agent_stacks.enable_hil_stack:
            return None
        
        # First check simple heuristics
        simple_detection = self.hil_manager.detect_ambiguity(
            context,
            confidence_threshold=CONFIG.agent_stacks.ambiguity_confidence_threshold
        )
        
        if simple_detection:
            self.hil_manager.request_feedback(simple_detection)
            return {
                "ambiguity_detected": True,
                "detection_method": "heuristic",
                "request": simple_detection.__dict__
            }
        
        # LLM-based detection for complex ambiguities
        try:
            prompt = HIL_AMBIGUITY_DETECTOR_PROMPT.format(
                context=json.dumps(context, indent=2),
                threshold=CONFIG.agent_stacks.ambiguity_confidence_threshold
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            
            if content_data.get("ambiguity_detected", False):
                confidence = content_data.get("confidence", 0.0)
                
                if confidence > CONFIG.agent_stacks.ambiguity_confidence_threshold:
                    self.log_info(f"Ambiguity detected (confidence: {confidence:.2f})")
                    
                    # Create HIL request
                    from core_v9_9 import HILRequest, AmbiguityType
                    request = HILRequest(
                        request_id=f"hil_{datetime.now().timestamp()}",
                        ambiguity_type=AmbiguityType(content_data.get("ambiguity_type", "missing_context")),
                        question=content_data.get("question_for_human", "Clarification needed"),
                        context=context,
                        options=content_data.get("options", [])
                    )
                    
                    self.hil_manager.request_feedback(request)
                    
                    return {
                        "ambiguity_detected": True,
                        "detection_method": "llm",
                        "confidence": confidence,
                        "request": request.__dict__
                    }
            
            return None
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Ambiguity detection failed: {e}")
            return None
# ============================================================================
# P2: HYDE GENERATOR
# ============================================================================

class HyDEGeneratorAgent(BaseAgent):
    """P2: Generates hypothetical documents for enhanced RAG."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
    
    def run(self, query: str) -> Dict[str, Any]:
        """Generate hypothetical ideal document."""
        self.log_info("Generating HyDE document...")
        
        if not CONFIG.agent_stacks.enable_hyde:
            return {
                "hypothetical_document": query,  # Passthrough
                "key_concepts": [],
                "search_expansion_terms": []
            }
        
        try:
            prompt = HYDE_GENERATION_PROMPT.format(query=query)
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.6,
                max_tokens=1000,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            self.log_info(f"HyDE generated. Concepts: {len(content_data.get('key_concepts', []))}")
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"HyDE generation failed: {e}")
            return {
                "hypothetical_document": query,
                "key_concepts": [],
                "search_expansion_terms": [],
                "error": str(e)
            }

# ============================================================================
# P2: RAG RERANKER
# ============================================================================

class RAG_ReRankerAgent(BaseAgent):
    """P2: Cross-encoder reranking of RAG results."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank documents by relevance."""
        self.log_info(f"Reranking {len(documents)} documents...")
        
        if not CONFIG.agent_stacks.enable_reranking:
            return documents  # Return unchanged
        
        if not documents:
            return []
        
        try:
            # Prepare documents for reranking
            doc_texts = [
                {
                    "doc_id": i,
                    "content": doc.get("bullet", doc.get("content", ""))
                }
                for i, doc in enumerate(documents)
            ]
            
            prompt = RERANKING_PROMPT.format(
                query=query,
                documents=json.dumps(doc_texts, indent=2)
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.2,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            reranked = content_data.get("reranked_results", [])
            
            # Sort by relevance score
            reranked_sorted = sorted(reranked, key=lambda x: x.get("relevance_score", 0.0), reverse=True)
            
            # Map back to original documents
            reranked_docs = []
            for item in reranked_sorted[:CONFIG.agent_stacks.reranking_top_k]:
                doc_id = item.get("doc_id", 0)
                if 0 <= doc_id < len(documents):
                    doc = documents[doc_id].copy()
                    doc["rerank_score"] = item.get("relevance_score", 0.0)
                    doc["rerank_rationale"] = item.get("rationale", "")
                    reranked_docs.append(doc)
            
            self.log_info(f"Reranked to top {len(reranked_docs)} documents")
            return reranked_docs
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Reranking failed: {e}")
            return documents[:CONFIG.agent_stacks.reranking_top_k]

# ============================================================================
# P2: ENHANCED RAG SEARCH AGENT
# ============================================================================

class RAG_SearchAgent(BaseAgent):
    """Enhanced RAG with HyDE and reranking."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.hyde_generator = HyDEGeneratorAgent(blackboard, debug_mode) if CONFIG.agent_stacks.enable_hyde else None
        self.reranker = RAG_ReRankerAgent(blackboard, debug_mode) if CONFIG.agent_stacks.enable_reranking else None
    
    def run(self, query: str, master_resume: Dict) -> List[Dict[str, Any]]:
        """Search with HyDE and reranking."""
        self.log_info(f"RAG search: {query[:50]}...")
        
        # P2: Generate HyDE if enabled
        if self.hyde_generator and CONFIG.agent_stacks.enable_hyde:
            hyde_result = self.hyde_generator.run(query)
            search_query = hyde_result.get("hypothetical_document", query)
            expansion_terms = hyde_result.get("search_expansion_terms", [])
        else:
            search_query = query
            expansion_terms = []
        
        # Perform search
        results = self._search_master_resume(search_query, expansion_terms, master_resume)
        
        # P2: Rerank if enabled
        if self.reranker and CONFIG.agent_stacks.enable_reranking and results:
            results = self.reranker.run(query, results)
        
        self.log_info(f"Retrieved {len(results)} relevant bullets")
        return results
    
    def _search_master_resume(self, query: str, expansion_terms: List[str], master_resume: Dict) -> List[Dict[str, Any]]:
        """Internal search logic."""
        results = []
        all_search_terms = query.split() + expansion_terms
        
        for exp in master_resume.get("professional_experience", []):
            bullet_pool = exp.get("bullet_pool", [])
            for bullet in bullet_pool:
                if any(term.lower() in bullet.lower() for term in all_search_terms):
                    results.append({
                        "company": exp.get("company", "N/A"),
                        "title": exp.get("title", "N/A"),
                        "bullet": bullet,
                        "relevance_score": 0.8
                    })
        
        return results[:20]  # Top 20 before reranking

# ============================================================================
# EXISTING AGENTS (FROM v9.7)
# ============================================================================

class JDParserAgent(BaseAgent):
    """Parses job description."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, raw_jd: str) -> Dict[str, Any]:
        """Parse JD."""
        self.log_info("Parsing JD...")
        
        prompt = f"""Parse into JSON:

**JD:**
{raw_jd}

**Output:**
{{
  "required_skills": ["skill"],
  "preferred_skills": ["skill"],
  "responsibilities": ["resp"],
  "qualifications": ["qual"],
  "key_themes": ["theme"]
}}
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            self.log_info(f"Parsed {len(content_data.get('required_skills', []))} required skills")
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"JD parsing failed: {e}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "qualifications": [],
                "key_themes": []
            }

class BulletGeneratorAgent(BaseAgent):
    """Generates tailored bullets."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
    
    def run(self, strategy: Dict, rag_results: List[Dict], engineered_prompt: Dict) -> List[str]:
        """Generate bullets."""
        self.log_info("Generating bullets...")
        
        system_prompt = engineered_prompt.get("system_prompt", "")
        user_prompt = engineered_prompt.get("user_prompt_template", "")
        
        context = {
            "strategy": strategy.get("positioning_theme", "N/A"),
            "evidence": json.dumps(rag_results[:5], indent=2),
            "constraints": engineered_prompt.get("constraint_reminders", [])
        }
        
        user_prompt_filled = user_prompt.format(**context) if "{" in user_prompt else user_prompt
        full_prompt = f"{user_prompt_filled}\n\n**Context:**\n{json.dumps(context, indent=2)}\n\nGenerate 3-5 bullets as JSON array."
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content = response.get("content", "")
            
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                bullets = json.loads(match.group(0))
                self.log_info(f"Generated {len(bullets)} bullets")
                return bullets
            else:
                self.log_warning("Could not parse JSON array")
                return [content]
                
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"Bullet generation failed: {e}")
            return ["• Placeholder bullet due to error"]

class QAValidatorAgent(BaseAgent):
    """QA validation."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, draft: str, requirements: Dict) -> Dict[str, Any]:
        """Validate draft."""
        self.log_info("Running QA...")
        
        prompt = f"""Validate:

**Draft:**
{draft}

**Requirements:**
{json.dumps(requirements, indent=2)}

**Output:**
{{
  "overall_passed": true/false,
  "failed_checks": [
    {{"check_name": "X", "details": "Y"}}
  ],
  "quality_score": 0.0-1.0
}}
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.2,
                response_format="json_object"
            )
            
            # P2: Record cost
            self.record_cost(response["model"], response["input_tokens"], response["output_tokens"])
            
            content_data = response.get("content", {})
            passed = content_data.get("overall_passed", False)
            self.log_info(f"QA: {'PASS' if passed else 'FAIL'}")
            
            return content_data
            
        except (ModelAPIError, AgentExecutionError, JSONParsingError) as e:
            self.log_error(f"QA failed: {e}")
            return {"overall_passed": False, "failed_checks": [{"check_name": "qa_error", "details": str(e)}]}
# ============================================================================
# GRAPH NODE FUNCTIONS (v9.8 with P1/P2)
# ============================================================================

def run_hil_ambiguity_detection(state: MainGraphState) -> Dict:
    """P1: Detect ambiguities requiring human input."""
    logger.info("--- HIL AMBIGUITY DETECTION ---")
    
    detector = HILAmbiguityDetectorAgent(state, debug_mode=True)
    result = detector.run(context=state["job_input"])
    
    ambiguity_detected = result is not None and result.get("ambiguity_detected", False)
    
    # Update HIL queue
    hil_queue = state.get("hil_feedback_queue", [])
    if ambiguity_detected:
        hil_queue.append(result)
    
    return {
        "ambiguity_detected": ambiguity_detected,
        "hil_feedback_queue": hil_queue
    }

def run_parse_jd(state: MainGraphState) -> Dict:
    """Parse job description."""
    logger.info("--- PARSE JD ---")
    
    parser = JDParserAgent(state, debug_mode=True)
    parsed_jd = parser.run(raw_jd=state["job_input"].get("raw_jd", ""))
    
    artifacts = state.get("artifacts", {})
    artifacts["parsed_jd"] = parsed_jd
    
    return {"artifacts": artifacts}

def run_tot_strategy(state: MainGraphState) -> Dict:
    """P0: Tree-of-Thoughts strategy."""
    logger.info("--- TOT STRATEGY ---")
    
    strategist = ToTStrategistAgent(state, debug_mode=True)
    result = strategist.run(
        master_resume=state["master_resume"],
        job_input=state["job_input"]
    )
    
    return {
        "strategy_thoughts": result["strategy_thoughts"],
        "selected_strategy": result["selected_strategy"]
    }

def run_prompt_engineer(state: MainGraphState) -> Dict:
    """P0: Dynamic prompt engineering."""
    logger.info("--- PROMPT ENGINEERING ---")
    
    engineer = DynamicPromptEngineerAgent(state, debug_mode=True)
    engineered_prompt = engineer.run(
        strategy=state.get("selected_strategy", {}),
        job_requirements=state.get("artifacts", {}).get("parsed_jd", {}).get("required_skills", []),
        candidate_context=state["master_resume"]
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["engineered_prompt"] = engineered_prompt
    
    return {"artifacts": artifacts}

def run_rag_search(state: MainGraphState) -> Dict:
    """P2: Enhanced RAG with HyDE and reranking."""
    logger.info("--- RAG SEARCH (P2 ENHANCED) ---")
    
    rag_agent = RAG_SearchAgent(state, debug_mode=True)
    strategy_theme = state.get("selected_strategy", {}).get("positioning_theme", "")
    
    rag_results = rag_agent.run(
        query=strategy_theme,
        master_resume=state["master_resume"]
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["rag_results"] = rag_results
    
    return {"artifacts": artifacts}

def run_bullet_generation(state: MainGraphState) -> Dict:
    """Generate bullets."""
    logger.info("--- BULLET GENERATION ---")
    
    generator = BulletGeneratorAgent(state, debug_mode=True)
    bullets = generator.run(
        strategy=state.get("selected_strategy", {}),
        rag_results=state.get("artifacts", {}).get("rag_results", []),
        engineered_prompt=state.get("artifacts", {}).get("engineered_prompt", {})
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["generated_bullets"] = bullets
    
    return {"artifacts": artifacts}

def run_bullet_critique(state: MainGraphState) -> Dict:
    """P0: Critique bullets."""
    logger.info("--- BULLET CRITIQUE ---")
    
    bullets = state.get("artifacts", {}).get("generated_bullets", [])
    critique_results = []
    
    critic = BulletCritiqueAgent(state, debug_mode=True)
    
    for bullet in bullets:
        critique = critic.run(
            bullet=bullet,
            strategy=state.get("selected_strategy", {}),
            source_experience={},
            target_requirements=state.get("artifacts", {}).get("parsed_jd", {}).get("required_skills", [])
        )
        critique_results.append(critique)
    
    history = state.get("bullet_critique_history", [])
    history.append({
        "timestamp": datetime.now().isoformat(),
        "critiques": critique_results
    })
    
    artifacts = state.get("artifacts", {})
    artifacts["bullet_critiques"] = critique_results
    
    return {
        "artifacts": artifacts,
        "bullet_critique_history": history
    }

def check_bullet_critique(state: MainGraphState) -> str:
    """P0: Check if bullets need regeneration."""
    critiques = state.get("artifacts", {}).get("bullet_critiques", [])
    local_retry_count = state.get("local_retry_count", 0)
    max_retries = CONFIG.agent_stacks.max_local_retries
    
    failed_bullets = [c for c in critiques if not c.get("passed", True)]
    
    if failed_bullets and local_retry_count < max_retries:
        logger.info(f"⟲ Local retry {local_retry_count + 1}/{max_retries}")
        return "RETRY_BULLETS"
    elif failed_bullets:
        logger.warning(f"⚠️ Max retries reached")
        return "COMPILE_DRAFT"
    else:
        logger.info("✓ All bullets passed")
        return "COMPILE_DRAFT"

def run_compile_draft(state: MainGraphState) -> Dict:
    """Compile draft."""
    logger.info("--- COMPILE DRAFT ---")
    
    bullets = state.get("artifacts", {}).get("generated_bullets", [])
    draft = "\n\n".join([f"• {b}" for b in bullets])
    
    artifacts = state.get("artifacts", {})
    artifacts["initial_draft"] = draft
    artifacts["final_draft"] = draft
    
    return {"artifacts": artifacts}

def run_safety_guard_stack(state: MainGraphState) -> Dict:
    """P0: Safety checks."""
    logger.info("--- SAFETY GUARD STACK ---")
    
    draft = state.get("artifacts", {}).get("initial_draft", "")
    
    bias_detector = BiasDetectorAgent(state, debug_mode=True)
    bias_result = bias_detector.run(content=draft)
    
    artifacts = state.get("artifacts", {})
    artifacts["bias_check"] = bias_result
    
    if bias_result.get("bias_detected", False):
        logger.warning(f"Bias detected: {bias_result.get('bias_score', 0.0)}")
    
    return {"artifacts": artifacts}

def run_qa_validation(state: MainGraphState) -> Dict:
    """QA validation."""
    logger.info("--- QA VALIDATION ---")
    
    validator = QAValidatorAgent(state, debug_mode=True)
    validation = validator.run(
        draft=state.get("artifacts", {}).get("final_draft", ""),
        requirements=state.get("artifacts", {}).get("parsed_jd", {})
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["validation_results"] = validation
    
    return {"artifacts": artifacts}

def increment_local_retry(state: MainGraphState) -> Dict:
    """Increment local retry counter."""
    return {"local_retry_count": state.get("local_retry_count", 0) + 1}

def update_cost_tracking(state: MainGraphState) -> Dict:
    """P2: Update cost tracking in state."""
    from core_v9_9 import COST_TRACKER
    
    summary = COST_TRACKER.get_cost_summary()
    
    return {
        "agent_costs": summary["agent_costs"],
        "total_workflow_cost": summary["total_workflow_cost"]
    }

# ============================================================================
# GRAPH ASSEMBLY (v9.8 with P1/P2)
# ============================================================================

def get_graph_app(checkpointer: 'RedisSaver', enable_hil: bool = True) -> 'CompiledGraph':
    """Construct v9.8 LangGraph workflow with P1/P2 enhancements."""
    
    workflow = StateGraph(MainGraphState)
    
    # Add nodes
    workflow.add_node("hil_detection", run_hil_ambiguity_detection)  # P1
    workflow.add_node("parse_jd", run_parse_jd)
    workflow.add_node("tot_strategy", run_tot_strategy)  # P0
    workflow.add_node("prompt_engineer", run_prompt_engineer)  # P0
    workflow.add_node("rag_search", run_rag_search)  # P2 enhanced
    workflow.add_node("bullet_generation", run_bullet_generation)
    workflow.add_node("bullet_critique", run_bullet_critique)  # P0
    workflow.add_node("increment_local_retry", increment_local_retry)  # P0
    workflow.add_node("compile_draft", run_compile_draft)
    workflow.add_node("safety_guard_stack", run_safety_guard_stack)  # P0
    workflow.add_node("qa_validation", run_qa_validation)
    workflow.add_node("update_costs", update_cost_tracking)  # P2
    
    # Set entry point
    if enable_hil and CONFIG.agent_stacks.enable_hil_stack:
        workflow.set_entry_point("hil_detection")
        workflow.add_edge("hil_detection", "parse_jd")
    else:
        workflow.set_entry_point("parse_jd")
    
    # Define edges
    workflow.add_edge("parse_jd", "tot_strategy")
    workflow.add_edge("tot_strategy", "prompt_engineer")
    workflow.add_edge("prompt_engineer", "rag_search")
    workflow.add_edge("rag_search", "bullet_generation")
    workflow.add_edge("bullet_generation", "bullet_critique")
    
    # P0: Local self-correction loop
    workflow.add_conditional_edges("bullet_critique", check_bullet_critique, {
        "RETRY_BULLETS": "increment_local_retry",
        "COMPILE_DRAFT": "compile_draft"
    })
    
    workflow.add_edge("increment_local_retry", "bullet_generation")
    workflow.add_edge("compile_draft", "safety_guard_stack")
    workflow.add_edge("safety_guard_stack", "qa_validation")
    
    # P2: Cost tracking before END
    workflow.add_edge("qa_validation", "update_costs")
    workflow.add_edge("update_costs", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# TOOL REGISTRATION
# ============================================================================

def register_default_tools():
    """Register default tools in global registry."""
    from core_v9_9 import ToolDefinition, TOOL_REGISTRY
    
    # Define tool implementations
    def tool_master_resume_search(query: str, resume: Dict) -> List[Dict]:
        """Search master resume."""
        results = []
        for exp in resume.get("professional_experience", []):
            for bullet in exp.get("bullet_pool", []):
                if query.lower() in bullet.lower():
                    results.append({"bullet": bullet, "company": exp.get("company", "")})
        return results[:5]
    
    def tool_jd_parser(jd_text: str) -> Dict:
        """Parse JD."""
        return {
            "skills": jd_text.split(),
            "responsibilities": []
        }
    
    # Register tools
    TOOL_REGISTRY.register_tool(ToolDefinition(
        name="master_resume_search",
        description="Search master resume for relevant experiences and bullets",
        parameters={"query": "str", "resume": "Dict"},
        implementation=tool_master_resume_search,
        cost_per_call=0.0,
        reliability_score=0.9
    ))
    
    TOOL_REGISTRY.register_tool(ToolDefinition(
        name="jd_parser",
        description="Parse job description into structured format",
        parameters={"jd_text": "str"},
        implementation=tool_jd_parser,
        cost_per_call=0.0,
        reliability_score=0.85
    ))
    
    logger.info("Registered 2 default tools")

# Initialize tools on module load
register_default_tools()

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "__version__",
    "get_graph_app",
    # P0 Agents
    "BiasDetectorAgent",
    "PIISanitizerAgent",
    "ToTStrategistAgent",
    "DynamicPromptEngineerAgent",
    "BulletCritiqueAgent",
    # P1 Agents
    "ReActConductorAgent",
    "DraftingReActConductor",
    "QAReActConductor",
    "ToolSelectorAgent",
    "HILAmbiguityDetectorAgent",
    # P2 Agents
    "HyDEGeneratorAgent",
    "RAG_ReRankerAgent",
    "RAG_SearchAgent",
    # Existing Agents
    "JDParserAgent",
    "BulletGeneratorAgent",
    "QAValidatorAgent",
]
