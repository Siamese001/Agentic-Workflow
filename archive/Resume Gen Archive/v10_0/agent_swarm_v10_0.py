# File: agent_swarm_v10_0.py
# Version: 10.0 (Modularity, Caching, Async Performance)
#
# v10.0 MAJOR CHANGES:
# ROW 4: All agents use dependency injection via WorkflowContext
# ROW 5: All LLM calls go through cached async clients
# ROW 6: Async agent execution with parallel bullet critique

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Local Presidio for PII (v9.9 security hardening preserved)
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

from core_v10_0 import (
    BaseAgent, WorkflowContext, MainGraphState,
    ModelAPIError, JSONParsingError, CONFIG
)
from langgraph.graph import StateGraph, END

logger = logging.getLogger("agent_swarm_v10_0")

# ============================================================================
# SAFETY STACK (Local processing - v9.9 security preserved)
# ============================================================================

class PIISanitizerAgent:
    """Local PII detection with Presidio (no external API)"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PIISanitizerAgent")
        if not PRESIDIO_AVAILABLE:
            self.logger.warning("Presidio not available. PII detection disabled.")
            self.analyzer = None
            self.anonymizer = None
        else:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()

    def run(self, resume_data: Dict) -> Dict:
        """Sanitize PII locally"""
        if not self.analyzer:
            self.logger.warning("Skipping PII sanitization (Presidio unavailable)")
            return resume_data
        
        self.logger.info("Running LOCAL PII detection...")
        sanitized = resume_data.copy()
        
        # Analyze text fields
        text_fields = ["name", "email", "phone", "address"]
        for field in text_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                text = sanitized[field]
                results = self.analyzer.analyze(text=text, language="en")
                
                if results:
                    anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results)
                    sanitized[field] = anonymized.text
                    self.logger.info(f"Sanitized {field}: found {len(results)} PII entities")
        
        return sanitized

class BiasDetectorAgent(BaseAgent):
    """Local bias detection with regex (no external API)"""
    
    BIAS_PATTERNS = {
        "gender": [
            r'\b(he|she|his|her|him|himself|herself)\b',
            r'\b(male|female|man|woman|boy|girl)\b',
        ],
        "age": [
            r'\b(young|old|elderly|senior|junior)\b',
            r'\b\d{1,2}[\s\-]?year[\s\-]?old\b',
        ],
        "cultural": [
            r'\b(native|foreign|immigrant|alien)\b',
        ]
    }
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)

    def run(self, text: str) -> Dict[str, Any]:
        """Detect bias using local regex"""
        self.log_info("Running LOCAL bias detection...")
        
        detected_biases = []
        for bias_type, patterns in self.BIAS_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    detected_biases.append({
                        "type": bias_type,
                        "pattern": pattern,
                        "matches": matches
                    })
        
        bias_detected = len(detected_biases) > 0
        
        if bias_detected:
            self.log_warning(f"Detected {len(detected_biases)} potential bias patterns")
        
        return {
            "bias_detected": bias_detected,
            "biases": detected_biases,
            "bias_score": len(detected_biases) / 10.0  # Normalize
        }

# ============================================================================
# ASYNC AGENTS (Row 6: Performance)
# ============================================================================

class AsyncBulletGeneratorAgent(BaseAgent):
    """Async bullet generation"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        model_config = context.config.model_config.get("bullet_generator_model", {})
        self.client = context.get_model_client(
            model_config.get("provider", "anthropic"),
            model_config.get("model_name", "claude-sonnet-4-20250514")
        )
        self.temperature = model_config.get("temperature", 0.7)

    async def run_async(self, resume: Dict, job: Dict, strategy: Dict) -> List[Dict]:
        """Generate bullets asynchronously"""
        self.log_info("Generating bullets (ASYNC)...")
        
        prompt = f"""Generate 5 achievement bullets for:
Company: {job.get('company')}
Role: {job.get('job_title')}
Strategy: {strategy.get('focus', 'impact')}

Resume context: {resume.get('experience', [])}

Return JSON: {{"bullets": [...]}}"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat_completion_async(
                messages=messages,
                temperature=self.temperature,
                response_format="json_object"
            )
            
            bullets = response.get("content", {}).get("bullets", [])
            self.log_info(f"Generated {len(bullets)} bullets")
            return bullets
            
        except (ModelAPIError, JSONParsingError) as e:
            self.log_error(f"Bullet generation failed: {e}")
            return []

class AsyncBulletCritiqueAgent(BaseAgent):
    """Async bullet critique"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        model_config = context.config.model_config.get("critique_model", {})
        self.client = context.get_model_client(
            model_config.get("provider", "google"),
            model_config.get("model_name", "gemini-2.0-flash-exp")
        )

    async def critique_single_bullet(self, bullet: str) -> Dict:
        """Critique one bullet asynchronously"""
        prompt = f"""Critique this achievement bullet:
"{bullet}"

Return JSON:
{{
  "score": 0.0-1.0,
  "issues": [...],
  "suggestions": [...]
}}"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat_completion_async(
                messages=messages,
                temperature=0.2,
                response_format="json_object"
            )
            
            critique = response.get("content", {})
            critique["bullet"] = bullet
            return critique
            
        except (ModelAPIError, JSONParsingError) as e:
            self.log_error(f"Critique failed for bullet: {e}")
            return {"bullet": bullet, "score": 0.5, "issues": [str(e)]}

    async def run_async(self, bullets: List[str]) -> List[Dict]:
        """Critique all bullets in parallel (Row 6: Performance)"""
        self.log_info(f"Critiquing {len(bullets)} bullets in PARALLEL...")
        
        # Row 6: Parallel async critique
        tasks = [self.critique_single_bullet(b) for b in bullets]
        critiques = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        results = []
        for i, critique in enumerate(critiques):
            if isinstance(critique, Exception):
                self.log_error(f"Critique task {i} failed: {critique}")
                results.append({
                    "bullet": bullets[i],
                    "score": 0.5,
                    "issues": [str(critique)]
                })
            else:
                results.append(critique)
        
        avg_score = sum(c.get("score", 0.5) for c in results) / len(results)
        self.log_info(f"Average critique score: {avg_score:.2f}")
        
        return results

# ============================================================================
# STRATEGY STACK
# ============================================================================

class ToTStrategistAgent(BaseAgent):
    """Tree-of-Thoughts strategist"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        model_config = context.config.model_config.get("strategy_model", {})
        self.client = context.get_model_client(
            model_config.get("provider", "anthropic"),
            model_config.get("model_name", "claude-sonnet-4-20250514")
        )
        self.temperature = model_config.get("temperature", 0.8)

    async def run_async(self, job: Dict, resume: Dict) -> Dict:
        """Generate strategy with ToT"""
        self.log_info("Running Tree-of-Thoughts strategy generation...")
        
        branching_factor = self.context.config.agent_stacks.strategy_tot_branching_factor
        
        prompt = f"""Generate {branching_factor} distinct resume strategies for:
Company: {job.get('company')}
Role: {job.get('job_title')}

Return JSON:
{{
  "strategies": [
    {{"id": "S1", "focus": "...", "rationale": "...", "confidence": 0.0-1.0}}
  ]
}}"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat_completion_async(
                messages=messages,
                temperature=self.temperature,
                response_format="json_object"
            )
            
            strategies = response.get("content", {}).get("strategies", [])
            
            # Select best strategy
            if strategies:
                best = max(strategies, key=lambda s: s.get("confidence", 0))
                self.log_info(f"Selected strategy: {best.get('focus')}")
                return {
                    "strategy_thoughts": strategies,
                    "selected_strategy": best
                }
            
            return {"strategy_thoughts": [], "selected_strategy": None}
            
        except (ModelAPIError, JSONParsingError) as e:
            self.log_error(f"Strategy generation failed: {e}")
            return {"strategy_thoughts": [], "selected_strategy": None}

# ============================================================================
# RAG STACK
# ============================================================================

class HyDEGeneratorAgent(BaseAgent):
    """Hypothetical Document Embeddings generator"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        model_config = context.config.model_config.get("hyde_model", {})
        self.client = context.get_model_client(
            model_config.get("provider", "anthropic"),
            model_config.get("model_name", "claude-sonnet-4-20250514")
        )

    async def run_async(self, query: str) -> str:
        """Generate hypothetical document"""
        self.log_info("Generating HyDE document...")
        
        prompt = f"""Generate a hypothetical resume excerpt that would answer:
"{query}"

Write as if it's from an actual resume."""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat_completion_async(
                messages=messages,
                temperature=0.6
            )
            
            hyde_doc = response.get("content", "")
            self.log_info("HyDE document generated")
            return hyde_doc
            
        except ModelAPIError as e:
            self.log_error(f"HyDE generation failed: {e}")
            return query  # Fallback to original query

# ============================================================================
# QA STACK
# ============================================================================

class QAValidatorAgent(BaseAgent):
    """Quality assurance validator"""
    
    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        model_config = context.config.model_config.get("qa_model", {})
        self.client = context.get_model_client(
            model_config.get("provider", "google"),
            model_config.get("model_name", "gemini-2.0-flash-exp")
        )

    async def run_async(self, draft: str, job: Dict) -> Dict:
        """Validate draft quality"""
        self.log_info("Running QA validation...")
        
        prompt = f"""Validate this resume draft for:
Company: {job.get('company')}
Role: {job.get('job_title')}

Draft:
{draft}

Return JSON:
{{
  "overall_passed": true/false,
  "checks": [
    {{"check": "...", "passed": true/false, "details": "..."}}
  ]
}}"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.chat_completion_async(
                messages=messages,
                temperature=0.3,
                response_format="json_object"
            )
            
            validation = response.get("content", {})
            passed = validation.get("overall_passed", False)
            
            self.log_info(f"QA validation: {'PASSED' if passed else 'FAILED'}")
            return validation
            
        except (ModelAPIError, JSONParsingError) as e:
            self.log_error(f"QA validation failed: {e}")
            return {
                "overall_passed": False,
                "checks": [{"check": "validation_error", "passed": False, "details": str(e)}]
            }

# ============================================================================
# LANGGRAPH WORKFLOW (Row 4: Modular state handling)
# ============================================================================

async def run_sanitize_pii(state_dict: Dict) -> Dict:
    """Sanitize PII (preserves v9.9 security)"""
    state = MainGraphState.from_dict(state_dict)
    
    agent = PIISanitizerAgent()
    sanitized = agent.run(state.resume.master_resume)
    
    state.resume.sanitized_resume = sanitized
    return state.to_dict()

async def run_detect_bias(state_dict: Dict, context: WorkflowContext) -> Dict:
    """Detect bias in draft"""
    state = MainGraphState.from_dict(state_dict)
    
    agent = BiasDetectorAgent(context, debug_mode=True)
    draft = state.artifacts.original_draft
    
    if draft:
        result = agent.run(draft)
        if result.get("bias_detected"):
            logger.warning(f"Bias detected: {result.get('biases')}")
    
    return state.to_dict()

async def run_tot_strategy(state_dict: Dict, context: WorkflowContext) -> Dict:
    """Generate strategy with ToT"""
    state = MainGraphState.from_dict(state_dict)
    
    agent = ToTStrategistAgent(context, debug_mode=True)
    result = await agent.run_async(
        {"company": state.job.company, "job_title": state.job.job_title},
        state.resume.sanitized_resume
    )
    
    state.strategy.strategy_thoughts = result.get("strategy_thoughts", [])
    state.strategy.selected_strategy = result.get("selected_strategy")
    
    return state.to_dict()

async def run_generate_bullets(state_dict: Dict, context: WorkflowContext) -> Dict:
    """Generate bullets (async)"""
    state = MainGraphState.from_dict(state_dict)
    
    agent = AsyncBulletGeneratorAgent(context, debug_mode=True)
    bullets = await agent.run_async(
        state.resume.sanitized_resume,
        {"company": state.job.company, "job_title": state.job.job_title},
        state.strategy.selected_strategy or {}
    )
    
    state.artifacts.artifacts["bullets"] = bullets
    return state.to_dict()

async def run_critique_bullets(state_dict: Dict, context: WorkflowContext) -> Dict:
    """Critique bullets in parallel (Row 6: Performance)"""
    state = MainGraphState.from_dict(state_dict)
    
    bullets = state.artifacts.artifacts.get("bullets", [])
    if not bullets:
        logger.warning("No bullets to critique")
        return state.to_dict()
    
    agent = AsyncBulletCritiqueAgent(context, debug_mode=True)
    critiques = await agent.run_async(bullets)
    
    state.quality.bullet_critique_history.extend(critiques)
    
    # Check if retry needed
    avg_score = sum(c.get("score", 0.5) for c in critiques) / len(critiques)
    if avg_score < 0.7 and state.metadata.local_retry_count < CONFIG.agent_stacks.max_local_retries:
        state.metadata.local_retry_count += 1
        logger.info(f"Retry {state.metadata.local_retry_count}: avg score {avg_score:.2f} < 0.7")
        return {"_retry": True, **state.to_dict()}
    
    return state.to_dict()

async def run_qa_validation(state_dict: Dict, context: WorkflowContext) -> Dict:
    """QA validation"""
    state = MainGraphState.from_dict(state_dict)
    
    agent = QAValidatorAgent(context, debug_mode=True)
    validation = await agent.run_async(
        state.artifacts.original_draft,
        {"company": state.job.company, "job_title": state.job.job_title}
    )
    
    state.artifacts.artifacts["validation_results"] = validation
    return state.to_dict()

def check_retry(state_dict: Dict) -> str:
    """Check if retry needed"""
    if state_dict.get("_retry"):
        return "GENERATE_BULLETS"
    return "QA_VALIDATION"

def get_graph_app(checkpointer, context: WorkflowContext, enable_hil: bool = False):
    """Build LangGraph workflow with injected context"""
    workflow = StateGraph(dict)  # Use dict for compatibility
    
    # Add nodes with context injection
    workflow.add_node("SANITIZE_PII", run_sanitize_pii)
    workflow.add_node("TOT_STRATEGY", lambda s: run_tot_strategy(s, context))
    workflow.add_node("GENERATE_BULLETS", lambda s: run_generate_bullets(s, context))
    workflow.add_node("CRITIQUE_BULLETS", lambda s: run_critique_bullets(s, context))
    workflow.add_node("QA_VALIDATION", lambda s: run_qa_validation(s, context))
    workflow.add_node("DETECT_BIAS", lambda s: run_detect_bias(s, context))
    
    # Build flow
    workflow.set_entry_point("SANITIZE_PII")
    workflow.add_edge("SANITIZE_PII", "TOT_STRATEGY")
    workflow.add_edge("TOT_STRATEGY", "GENERATE_BULLETS")
    workflow.add_edge("GENERATE_BULLETS", "CRITIQUE_BULLETS")
    workflow.add_conditional_edges("CRITIQUE_BULLETS", check_retry, {
        "GENERATE_BULLETS": "GENERATE_BULLETS",
        "QA_VALIDATION": "QA_VALIDATION"
    })
    workflow.add_edge("QA_VALIDATION", "DETECT_BIAS")
    workflow.add_edge("DETECT_BIAS", END)
    
    return workflow.compile(checkpointer=checkpointer)

# ============================================================================
# END OF agent_swarm_v10_0.py
# ============================================================================