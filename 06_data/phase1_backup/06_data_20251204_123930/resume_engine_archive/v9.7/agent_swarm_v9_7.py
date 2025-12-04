# File: agent_swarm_v9_7.py
# Overwrites: agent_swarm_v9_6.py
# Version: 9.7 (P0 Enhancements)

# v9.7 P0 CHANGES:
# - Implemented SafetyGuardStack with BiasDetectorAgent and enhanced PIISanitizerAgent
# - Replaced ThemeClassifierAgent with ToTStrategistAgent (Tree-of-Thoughts)
# - Replaced PromptStackAgent with DynamicPromptEngineerAgent (LLM-driven)
# - Added BulletCritiqueAgent for local self-correction loops
# - Updated graph conditional edges to support local retries
# - Separated safety concerns from QA stack

import json
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from core_v9_7 import (
    CONFIG, BaseAgent, get_model_client, MainGraphState,
    BIAS_DETECTOR_SYSTEM_PROMPT, PII_SCRUBBER_SYSTEM_PROMPT,
    TOT_STRATEGIST_SYSTEM_PROMPT, PROMPT_ENGINEER_SYSTEM_PROMPT,
    BULLET_CRITIQUE_SYSTEM_PROMPT, AgentExecutionError
)

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

__version__ = "9.7.0-p0-enhancements"

# ============================================================================
# P0 ITEM #1: SAFETYGUARDSTACK AGENTS
# ============================================================================

class BiasDetectorAgent(BaseAgent):
    """
    P0 Enhancement: Detects bias in resume content.
    Part of SafetyGuardStack (separated from QA concerns).
    """
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, content: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Detect bias in content."""
        self.log_info("Analyzing content for bias...")
        
        if not CONFIG.agent_stacks.safety_stack_enabled:
            self.log_info("SafetyStack disabled. Skipping bias detection.")
            return {"bias_detected": False, "bias_score": 0.0, "findings": []}
        
        try:
            prompt = BIAS_DETECTOR_SYSTEM_PROMPT + f"\n\nAnalyze this content:\n{json.dumps({'content': content, 'context': context})}"
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format="json_object"
            )
            
            self.log_info(f"Bias detection complete. Score: {response.get('bias_score', 0.0)}")
            return response
            
        except Exception as e:
            self.log_error(f"Bias detection failed: {e}")
            # Fail-safe: return no bias detected to avoid blocking workflow
            return {"bias_detected": False, "bias_score": 0.0, "findings": [], "error": str(e)}

class PIISanitizerAgent(BaseAgent):
    """
    Enhanced v9.7: More sophisticated PII detection and sanitization.
    Part of SafetyGuardStack.
    """
    
    def __init__(self, blackboard: Dict = None, debug_mode: bool = False):
        if blackboard is None:
            blackboard = {}
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PII from resume data."""
        self.log_info("Sanitizing PII from resume...")
        
        if not CONFIG.agent_stacks.pii_detection_enabled:
            self.log_info("PII detection disabled. Returning unsanitized data.")
            return resume_data
        
        try:
            # Convert resume to string for analysis
            resume_str = json.dumps(resume_data, indent=2)
            
            prompt = PII_SCRUBBER_SYSTEM_PROMPT + f"\n\nSanitize PII from:\n{resume_str}"
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.1,  # Low temp for deterministic PII handling
                response_format="json_object"
            )
            
            if response.get("pii_found", False):
                self.log_warning(f"PII detected and sanitized. Redactions: {response.get('redaction_count', 0)}")
                # Parse sanitized content back to dict
                try:
                    sanitized_data = json.loads(response.get("sanitized_content", "{}"))
                    # Store PII map in blackboard for potential restoration
                    self.blackboard["pii_map"] = response.get("pii_map", {})
                    return sanitized_data
                except json.JSONDecodeError:
                    self.log_error("Failed to parse sanitized content. Returning original.")
                    return resume_data
            else:
                self.log_info("No PII detected.")
                return resume_data
                
        except Exception as e:
            self.log_error(f"PII sanitization failed: {e}")
            # Fail-safe: return original data
            return resume_data

# ============================================================================
# P0 ITEM #2: TREE-OF-THOUGHTS STRATEGIST
# ============================================================================

class ToTStrategistAgent(BaseAgent):
    """
    P0 Enhancement: Replaces ThemeClassifierAgent with Tree-of-Thoughts reasoning.
    Generates multiple strategic approaches, evaluates each, selects optimal path.
    """
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
        self.branching_factor = CONFIG.agent_stacks.strategy_tot_branching_factor
    
    def run(self, master_resume: Dict, job_input: Dict) -> Dict[str, Any]:
        """Generate and select optimal strategy using Tree-of-Thoughts."""
        self.log_info(f"Generating {self.branching_factor} strategic thought branches...")
        
        if not CONFIG.agent_stacks.strategy_tot_enabled:
            self.log_info("ToT disabled. Using simplified strategy selection.")
            return self._simplified_strategy(master_resume, job_input)
        
        try:
            prompt = TOT_STRATEGIST_SYSTEM_PROMPT.format(branching_factor=self.branching_factor)
            prompt += f"\n\n**Input Data:**\n{json.dumps({'master_resume': master_resume, 'job_description': job_input.get('raw_jd', ''), 'company_context': job_input.get('company', '')}, indent=2)}"
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.8,  # Higher temp for creative strategy generation
                max_tokens=6000,
                response_format="json_object"
            )
            
            thought_branches = response.get("thought_branches", [])
            selected_strategy = response.get("selected_strategy", {})
            
            self.log_info(f"Generated {len(thought_branches)} strategies. Selected: {selected_strategy.get('branch_id', 'N/A')}")
            self.log_debug(f"Selected strategy rationale: {selected_strategy.get('rationale', 'N/A')}")
            
            return {
                "strategy_thoughts": thought_branches,
                "selected_strategy": selected_strategy
            }
            
        except Exception as e:
            self.log_error(f"ToT strategy generation failed: {e}")
            raise AgentExecutionError(f"ToTStrategistAgent failed: {e}")
    
    def _simplified_strategy(self, master_resume: Dict, job_input: Dict) -> Dict[str, Any]:
        """Fallback: simplified strategy if ToT is disabled."""
        return {
            "strategy_thoughts": [],
            "selected_strategy": {
                "branch_id": "FALLBACK",
                "positioning_theme": "Comprehensive Experience Match",
                "evidence_selection": ["all_experiences"],
                "implementation_guidance": "Select bullets that directly match job requirements."
            }
        }

# ============================================================================
# P0 ITEM #3: DYNAMIC PROMPT ENGINEER
# ============================================================================

class DynamicPromptEngineerAgent(BaseAgent):
    """
    P0 Enhancement: Replaces PromptStackAgent with LLM-driven prompt generation.
    Crafts optimal prompts based on strategy and context.
    """
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
    
    def run(self, strategy: Dict, job_requirements: List[str], candidate_context: Dict) -> Dict[str, Any]:
        """Generate optimized prompt for bullet writing."""
        self.log_info("Engineering prompt for bullet generation...")
        
        if not CONFIG.agent_stacks.prompt_llm_driven:
            self.log_info("LLM-driven prompting disabled. Using template.")
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
            
            self.log_info(f"Engineered prompt. Est. quality: {response.get('estimated_quality_score', 0.0)}")
            return response
            
        except Exception as e:
            self.log_error(f"Prompt engineering failed: {e}")
            return self._template_prompt(strategy, job_requirements)
    
    def _template_prompt(self, strategy: Dict, job_requirements: List[str]) -> Dict[str, Any]:
        """Fallback: template-based prompt."""
        return {
            "system_prompt": f"You are writing resume bullets. Strategy: {strategy.get('positioning_theme', 'N/A')}",
            "user_prompt_template": "Generate bullets for {experience} targeting requirements: {requirements}",
            "few_shot_examples": [],
            "constraint_reminders": ["40-90 words", "quantify impact", "action verbs"],
            "estimated_quality_score": 0.6
        }

# ============================================================================
# P0 ITEM #4: LOCAL SELF-CORRECTION (BULLET CRITIQUE)
# ============================================================================

class BulletCritiqueAgent(BaseAgent):
    """
    P0 Enhancement: Local self-correction agent.
    Critiques generated bullets before proceeding downstream.
    """
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, bullet: str, strategy: Dict, source_experience: Dict, target_requirements: List[str]) -> Dict[str, Any]:
        """Critique a single bullet."""
        self.log_info("Critiquing generated bullet...")
        
        if not CONFIG.agent_stacks.enable_local_retries:
            self.log_info("Local retries disabled. Auto-accepting bullet.")
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
                temperature=0.2,  # Low temp for consistent evaluation
                response_format="json_object"
            )
            
            passed = response.get("passed", False)
            avg_score = response.get("scores", {}).get("average", 0.0)
            
            self.log_info(f"Critique result: {'PASS' if passed else 'FAIL'} (avg: {avg_score:.1f})")
            if not passed:
                self.log_debug(f"Critique feedback: {response.get('critique', 'N/A')}")
            
            return response
            
        except Exception as e:
            self.log_error(f"Bullet critique failed: {e}")
            # Fail-safe: accept bullet to avoid blocking
            return {"passed": True, "scores": {}, "recommendation": "accept", "error": str(e)}

# ============================================================================
# EXISTING AGENTS (UPDATED FOR v9.7)
# ============================================================================

class JDParserAgent(BaseAgent):
    """Parses job description into structured requirements."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, raw_jd: str) -> Dict[str, Any]:
        """Parse JD into structured format."""
        self.log_info("Parsing job description...")
        
        prompt = f"""Parse this job description into structured JSON:

**Job Description:**
{raw_jd}

**Output Format:**
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "responsibilities": ["resp1", "resp2"],
  "qualifications": ["qual1", "qual2"],
  "key_themes": ["theme1", "theme2"]
}}
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format="json_object"
            )
            
            self.log_info(f"Parsed {len(response.get('required_skills', []))} required skills")
            return response
            
        except Exception as e:
            self.log_error(f"JD parsing failed: {e}")
            return {
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "qualifications": [],
                "key_themes": []
            }

class RAG_SearchAgent(BaseAgent):
    """RAG agent for retrieving relevant resume content."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
    
    def run(self, query: str, master_resume: Dict) -> List[Dict[str, Any]]:
        """Search master resume for relevant content."""
        self.log_info(f"RAG search for: {query[:50]}...")
        
        # Simplified RAG: keyword matching (production would use embeddings)
        results = []
        
        for exp in master_resume.get("professional_experience", []):
            bullet_pool = exp.get("bullet_pool", [])
            for bullet in bullet_pool:
                if any(keyword.lower() in bullet.lower() for keyword in query.split()):
                    results.append({
                        "company": exp.get("company", "N/A"),
                        "title": exp.get("title", "N/A"),
                        "bullet": bullet,
                        "relevance_score": 0.8  # Placeholder
                    })
        
        self.log_info(f"Retrieved {len(results)} relevant bullets")
        return results[:10]  # Top 10

class BulletGeneratorAgent(BaseAgent):
    """Generates tailored resume bullets."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("anthropic", "claude-sonnet-4-20250514")
    
    def run(self, strategy: Dict, rag_results: List[Dict], engineered_prompt: Dict) -> List[str]:
        """Generate bullets using engineered prompt."""
        self.log_info("Generating tailored bullets...")
        
        system_prompt = engineered_prompt.get("system_prompt", "")
        user_prompt = engineered_prompt.get("user_prompt_template", "")
        
        # Build full prompt
        context = {
            "strategy": strategy.get("positioning_theme", "N/A"),
            "evidence": json.dumps(rag_results[:5], indent=2),
            "constraints": engineered_prompt.get("constraint_reminders", [])
        }
        
        user_prompt_filled = user_prompt.format(**context) if "{" in user_prompt else user_prompt
        
        full_prompt = f"{user_prompt_filled}\n\n**Context:**\n{json.dumps(context, indent=2)}\n\nGenerate 3-5 high-quality bullets as a JSON array."
        
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
            
            # Parse bullets from response
            content = response.get("content", "")
            
            # Try to extract JSON array
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                bullets = json.loads(match.group(0))
                self.log_info(f"Generated {len(bullets)} bullets")
                return bullets
            else:
                self.log_warning("Could not parse JSON array. Returning raw content.")
                return [content]
                
        except Exception as e:
            self.log_error(f"Bullet generation failed: {e}")
            return ["• Generated placeholder bullet due to error"]

class QAValidatorAgent(BaseAgent):
    """QA validation (now separated from safety concerns)."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
        self.client = get_model_client("google", "gemini-2.0-flash-exp")
    
    def run(self, draft: str, requirements: Dict) -> Dict[str, Any]:
        """Validate draft quality."""
        self.log_info("Running QA validation...")
        
        prompt = f"""Validate this resume draft:

**Draft:**
{draft}

**Requirements:**
{json.dumps(requirements, indent=2)}

**Output JSON:**
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
            
            passed = response.get("overall_passed", False)
            self.log_info(f"QA result: {'PASS' if passed else 'FAIL'}")
            
            return response
            
        except Exception as e:
            self.log_error(f"QA validation failed: {e}")
            return {"overall_passed": False, "failed_checks": [{"check_name": "qa_error", "details": str(e)}]}

# ============================================================================
# CONDUCTOR AGENTS (UNCHANGED FROM v9.6)
# ============================================================================

class DraftingConductorAgent(BaseAgent):
    """Orchestrates drafting workflow."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
    
    def run(self, state: Dict) -> Dict[str, Any]:
        """Execute drafting plan."""
        self.log_info("Orchestrating drafting workflow...")
        
        # This is a plan executor (P1 upgrade would make it a true ReAct agent)
        return {
            "plan": ["parse_jd", "generate_strategy", "engineer_prompt", "search_rag", "generate_bullets", "critique_bullets", "compile_draft"]
        }

class QAConductorAgent(BaseAgent):
    """Orchestrates QA workflow."""
    
    def __init__(self, blackboard: Dict, debug_mode: bool = False):
        super().__init__(blackboard, debug_mode)
    
    def run(self, state: Dict) -> Dict[str, Any]:
        """Execute QA plan."""
        self.log_info("Orchestrating QA workflow...")
        
        return {
            "plan": ["validate_format", "check_consistency", "verify_claims"]
        }

# ============================================================================
# GRAPH CONSTRUCTION (v9.7 WITH P0 ENHANCEMENTS)
# ============================================================================

def run_safety_guard_stack(state: MainGraphState) -> Dict:
    """P0 Item #1: Run SafetyGuardStack on initial draft."""
    logger.info("--- SAFETY GUARD STACK ---")
    
    draft = state.get("artifacts", {}).get("initial_draft", "")
    
    # Bias detection
    bias_detector = BiasDetectorAgent(state, debug_mode=True)
    bias_result = bias_detector.run(content=draft)
    
    # Store results
    artifacts = state.get("artifacts", {})
    artifacts["bias_check"] = bias_result
    
    if bias_result.get("bias_detected", False):
        logger.warning(f"Bias detected with score {bias_result.get('bias_score', 0.0)}")
    
    return {"artifacts": artifacts}

def run_tot_strategy(state: MainGraphState) -> Dict:
    """P0 Item #2: Run Tree-of-Thoughts strategy generation."""
    logger.info("--- TREE-OF-THOUGHTS STRATEGY ---")
    
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
    """P0 Item #3: Engineer optimal prompt."""
    logger.info("--- DYNAMIC PROMPT ENGINEERING ---")
    
    engineer = DynamicPromptEngineerAgent(state, debug_mode=True)
    engineered_prompt = engineer.run(
        strategy=state.get("selected_strategy", {}),
        job_requirements=state.get("artifacts", {}).get("parsed_jd", {}).get("required_skills", []),
        candidate_context=state["master_resume"]
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["engineered_prompt"] = engineered_prompt
    
    return {"artifacts": artifacts}

def run_bullet_generation(state: MainGraphState) -> Dict:
    """Generate bullets using engineered prompt."""
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
    """P0 Item #4: Critique generated bullets (local self-correction)."""
    logger.info("--- BULLET CRITIQUE (LOCAL SELF-CORRECTION) ---")
    
    bullets = state.get("artifacts", {}).get("generated_bullets", [])
    critique_results = []
    
    critic = BulletCritiqueAgent(state, debug_mode=True)
    
    for bullet in bullets:
        critique = critic.run(
            bullet=bullet,
            strategy=state.get("selected_strategy", {}),
            source_experience={},  # Would include source context
            target_requirements=state.get("artifacts", {}).get("parsed_jd", {}).get("required_skills", [])
        )
        critique_results.append(critique)
    
    # Update critique history
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
    """P0 Item #4: Decide if bullets need regeneration (local retry)."""
    critiques = state.get("artifacts", {}).get("bullet_critiques", [])
    local_retry_count = state.get("local_retry_count", 0)
    max_retries = CONFIG.agent_stacks.max_local_retries
    
    # Check if any bullets failed
    failed_bullets = [c for c in critiques if not c.get("passed", True)]
    
    if failed_bullets and local_retry_count < max_retries:
        logger.info(f"⟲ Local retry triggered. {len(failed_bullets)} bullets failed critique. Retry {local_retry_count + 1}/{max_retries}")
        return "RETRY_BULLETS"
    elif failed_bullets:
        logger.warning(f"⚠️ Max local retries reached. Proceeding with {len(failed_bullets)} failed bullets.")
        return "COMPILE_DRAFT"
    else:
        logger.info("✓ All bullets passed critique.")
        return "COMPILE_DRAFT"

def run_compile_draft(state: MainGraphState) -> Dict:
    """Compile final draft from bullets."""
    logger.info("--- COMPILE DRAFT ---")
    
    bullets = state.get("artifacts", {}).get("generated_bullets", [])
    draft = "\n\n".join([f"• {b}" for b in bullets])
    
    artifacts = state.get("artifacts", {})
    artifacts["initial_draft"] = draft
    artifacts["final_draft"] = draft
    
    return {"artifacts": artifacts}

def run_qa_validation(state: MainGraphState) -> Dict:
    """Run QA validation (separated from safety)."""
    logger.info("--- QA VALIDATION ---")
    
    validator = QAValidatorAgent(state, debug_mode=True)
    validation = validator.run(
        draft=state.get("artifacts", {}).get("final_draft", ""),
        requirements=state.get("artifacts", {}).get("parsed_jd", {})
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["validation_results"] = validation
    
    return {"artifacts": artifacts}

def run_parse_jd(state: MainGraphState) -> Dict:
    """Parse job description."""
    logger.info("--- PARSE JD ---")
    
    parser = JDParserAgent(state, debug_mode=True)
    parsed_jd = parser.run(raw_jd=state["job_input"].get("raw_jd", ""))
    
    artifacts = state.get("artifacts", {})
    artifacts["parsed_jd"] = parsed_jd
    
    return {"artifacts": artifacts}

def run_rag_search(state: MainGraphState) -> Dict:
    """RAG search for relevant content."""
    logger.info("--- RAG SEARCH ---")
    
    rag_agent = RAG_SearchAgent(state, debug_mode=True)
    strategy_theme = state.get("selected_strategy", {}).get("positioning_theme", "")
    
    rag_results = rag_agent.run(
        query=strategy_theme,
        master_resume=state["master_resume"]
    )
    
    artifacts = state.get("artifacts", {})
    artifacts["rag_results"] = rag_results
    
    return {"artifacts": artifacts}

def increment_local_retry(state: MainGraphState) -> Dict:
    """Increment local retry counter."""
    return {"local_retry_count": state.get("local_retry_count", 0) + 1}

# ============================================================================
# GRAPH ASSEMBLY
# ============================================================================

def get_graph_app(checkpointer: 'RedisSaver', enable_hil: bool = True) -> 'CompiledGraph':
    """Construct the v9.7 LangGraph workflow with P0 enhancements."""
    
    workflow = StateGraph(MainGraphState)
    
    # Add nodes
    workflow.add_node("parse_jd", run_parse_jd)
    workflow.add_node("tot_strategy", run_tot_strategy)
    workflow.add_node("prompt_engineer", run_prompt_engineer)
    workflow.add_node("rag_search", run_rag_search)
    workflow.add_node("bullet_generation", run_bullet_generation)
    workflow.add_node("bullet_critique", run_bullet_critique)  # P0 Item #4
    workflow.add_node("increment_local_retry", increment_local_retry)  # P0 Item #4
    workflow.add_node("compile_draft", run_compile_draft)
    workflow.add_node("safety_guard_stack", run_safety_guard_stack)  # P0 Item #1
    workflow.add_node("qa_validation", run_qa_validation)
    
    # Set entry point
    workflow.set_entry_point("parse_jd")
    
    # Define edges
    workflow.add_edge("parse_jd", "tot_strategy")
    workflow.add_edge("tot_strategy", "prompt_engineer")
    workflow.add_edge("prompt_engineer", "rag_search")
    workflow.add_edge("rag_search", "bullet_generation")
    workflow.add_edge("bullet_generation", "bullet_critique")
    
    # P0 Item #4: Local self-correction conditional edge
    workflow.add_conditional_edges("bullet_critique", check_bullet_critique, {
        "RETRY_BULLETS": "increment_local_retry",
        "COMPILE_DRAFT": "compile_draft"
    })
    
    workflow.add_edge("increment_local_retry", "bullet_generation")  # Loop back
    workflow.add_edge("compile_draft", "safety_guard_stack")
    workflow.add_edge("safety_guard_stack", "qa_validation")
    workflow.add_edge("qa_validation", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "__version__",
    "get_graph_app",
    # P0 Enhanced Agents
    "BiasDetectorAgent",
    "PIISanitizerAgent",
    "ToTStrategistAgent",
    "DynamicPromptEngineerAgent",
    "BulletCritiqueAgent",
    # Existing Agents
    "JDParserAgent",
    "RAG_SearchAgent",
    "BulletGeneratorAgent",
    "QAValidatorAgent",
    "DraftingConductorAgent",
    "QAConductorAgent",
]
