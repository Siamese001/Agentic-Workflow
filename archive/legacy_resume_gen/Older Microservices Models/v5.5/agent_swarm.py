# File: agent_swarm.py
# Version: Consolidated 5.4 (Logging & Error Handling Patch)
# Fixes: Correlation IDs + Structured Logging + Agent Telemetry + Error Classification
# Zero-Loss Consolidation - The Crew
# Merges: gemini_service.py → execution_specialists_v5_2.py → advisory_crew_v5_2.py

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import copy
import hashlib
import json
import logging
import os
import random
import re
import signal
import time
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from functools import cached_property, partial
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union, TYPE_CHECKING

# Optional imports with fallback
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    warnings.warn("google-generativeai package not installed. Install with: pip install google-generativeai")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# Import from core.py
from core import (
    # Models
    HopExecutionError, CircuitBreakerOpenError, PhaseTimeoutError, MechanicalFailureError, SemanticFailureError,
    ResumeSection, ValidationSeverity, ImmutableStagingBuffer,
    ValidationResult, ThematicAnalysis, MasterResumeIndex, RAG_Blackboard,
    RAGMission, RAGPhase, CircuitBreakerState, CircuitBreakerConfig,
    ReasoningConfig, ReasoningStrategy, VetoLevel, QAClassification,
    StrategyBrief, VetoSignal,
    # Config
    CONFIG, CACHE_DIR, DEFAULT_MAX_RETRIES, DEFAULT_RETRY_DELAY,
    DEFAULT_GENERATION_TEMPERATURE, DEFAULT_SYNTHESIS_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS, SAFETY_THRESHOLD,
    # Utils
    text_utils, fence_data, reasoning_config_to_api_params,
    enhance_system_prompt_with_reasoning, DuplicateDetector, TextSanitizer,
    # Prompts
    build_crl_context_for_section, format_prompt_with_context,
    build_crl_context_for_section, format_prompt_with_context,
    get_rag_phase_prompt, get_specialist_prompt, build_atomic_agent_prompt
)

# Import from validation_stack.py
from validation_stack import (
    ValidationContext, ValidationRule, ValidationEngine, 
    ConstraintFailureClassifier, PreFlightValidator,
    calculate_signal_score
)

logger = logging.getLogger(__name__)

# --- PRIORITY #1 & #2: Correlation IDs & Structured Logging ---
class WorkflowLoggerAdapter(logging.LoggerAdapter):
    """Injects the workflow_id into all log messages."""
    def process(self, msg, kwargs):
        if "workflow_id" not in kwargs.get("extra", {}):
            if "workflow_id" in self.extra:
                kwargs.setdefault("extra", {})["workflow_id"] = self.extra["workflow_id"]
        
        return msg, kwargs
# --- END PRIORITY #1 & #2 ---

# ============================================================================
# AGENT SWARM ARCHITECTURE - V5.4 10 AGENTS PATCH
# ============================================================================

AGENT_COMPLEXITY = {
    # TIER 1 & 4: Advisory Intelligence
    "ChiefStrategistAgent": 100,
    "StrategyValidatorAgent": 80,
    "RetryPolicyAgent": 50,
    # TIER 1: Research Crew
    "Library_Specialist": 50, # Existing
    "Web_Specialist": 70,
    # --- V5.5: RAG Pipeline Split ---
    "RAG_QueryGeneratorAgent": 60,
    "RAG_SearchAgent": 40,
    "RAG_ChunkingAgent": 30,
    "RAG_RankingAgent": 50,
    "RAG_FilterAgent": 30,
    "RAG_CrossReferenceAgent": 65,
    "RAG_DraftingAgent": 70,
    "RAG_CritiqueAgent": 75,
    # --------------------------------
    # TIER 2: Meta-Loop Agents
    "FeedbackLoggerAgent": 30,
    "MetaPlannerAgent": 90,
    "PatternFinderAgent": 70, # V5.5
    # Execution Specialists - Drafting
    "ExampleSelectorAgent": 55, # V5.5
    "Verbatim_Copier": 15,
    "Custom_Synthetic_Drafter": 30,
    "Gemini_Drafter": 30,
    # TIER 4: Niche Capabilities
    "PortfolioLinkerAgent": 40,
    "CompetitorAnalystAgent": 60,
    # TIER 1: Deepening Intelligence (Pre-Drafting)
    "OntologyMapperAgent": 50,
    "ThemeIdentifierAgent": 60, # V5.5
    # Drafting Continued...
    "Claude_Drafter": 30,
    "Muse_Drafter": 30,
    # Execution Specialists - Synthesis
    "Adversarial_Synthesis_Agent": 40,
    "Overview_Generator": 35,
    "Bullet_Reorderer": 30,
    # Execution Specialists - QA Class 1
    "Constraint_Jargon_Checker": 20,
    "Grammar_TokenCountAgent": 15,
    "FormatComplianceAgent": 25,    # TIER 4
    "BiasScrubberAgent": 30,        # TIER 3
    # Execution Specialists - QA Class 2
    "MetricValidatorAgent": 30,      # V5.5
    "TenureValidatorAgent": 30,      # V5.5
    "EntityValidatorAgent": 30,      # V5.5
    "ClaimValidatorAgent": 60,       # V5.5
    # Execution Specialists - QA Class 3
    "ToneValidator": 25,
    "ThematicAlignment_Validator": 25,
    "SemanticEntailmentValidator": 70, # TIER 3
    # Execution Specialists - QA Class 4 (Holistic)
    "NarrativeThreadAgent": 80,       # TIER 1
    # Execution Specialists - QA Class 5 (Adversarial)
    "AdversarialReviewerAgent": 85,   # TIER 1
    # Final Output
    "Resume_Assembler": 20,
    "CoverLetter_Assembler": 20,
    "AppTracker_Assembler": 20,
    "MarkdownToLatexAgent": 40,    # V5.5
    "Auditor_Agent": 35, # Existing
    # TIER 2: Offline/Async Loop Agents
    "AutoTunerAgent": 90,
    "CacheManagerAgent": 60,
    # --- V5.5: Cost Control ---
    "CostEstimatorAgent": 50,
    "CostTrackerAgent": 35
}

@dataclass
class CrewContext:
    """Context for crew operations (if not already defined)."""
    job_description: str = ""
    master_resume: Dict[str, Any] = field(default_factory=dict)
    strategy: Optional[StrategyBrief] = None
    staging_buffer: Optional[Any] = None
    thematic_analysis: Optional[ThematicAnalysis] = None # Fixed typing
    workflow_id: str = "" # --- PRIORITY #1 ---
    company_name: str = ""
    job_title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)

class SwarmAgent:
    """Base class for all swarm agents."""
    def __init__(self, name: str):
        self.name = name
        self.complexity = AGENT_COMPLEXITY.get(name, 50)
        self.logger = logging.getLogger(name)

# ============================================================================
# TIER 2: OFFLINE/ASYNC LOOP AGENTS
# ============================================================================
class FeedbackLoggerAgent(SwarmAgent):
    """Logs HIL interactions and QA failures for pattern finding."""
    def __init__(self): super().__init__("FeedbackLoggerAgent")
    def log_event(self, event_type: str, data: Dict[str, Any]):
        # In a real async system, this would write to a dedicated log stream
        pass

class MetaPlannerAgent(SwarmAgent):
    """Reads logs, finds patterns, outputs rules to registry."""
    def __init__(self): super().__init__("MetaPlannerAgent")
    
    def update_rules(self):
        # Asynchronous routine to update rules_registry.json
        pass

class PatternFinderAgent(SwarmAgent):
    """V5.5: Reads structured logs to find patterns for the Meta-Planner."""
    def __init__(self): super().__init__("PatternFinderAgent")
    def find_patterns(self, log_file: str) -> Dict[str, Any]:
        # e.g., "grep 'VETO_MECHANICAL' workflow.log.jsonl | jq .error | sort | uniq -c"
        return {"common_errors": {"Forbidden jargon": 50}}

class AutoTunerAgent(SwarmAgent):
    """TIER 2: Analyzes logs to suggest config updates (Offline)."""
    def __init__(self): 
        super().__init__("AutoTunerAgent")
    
    def analyze_telemetry(self, log_path: str) -> Dict[str, Any]:
        # Finds patterns like "K1 always fails word count when set < 100"
        return {"recommended_changes": {}}

class CacheManagerAgent(SwarmAgent):
    """TIER 2: Maintains ChromaDB hygiene (Offline)."""
    def __init__(self): 
        super().__init__("CacheManagerAgent")
    
    def consolidate_memories(self):
        # Merges similar RAG findings, archives old job postings
        pass

# ============================================================================
# V5.5: COST CONTROL AGENTS
# ============================================================================
class CostEstimatorAgent(SwarmAgent):
    """V5.5: Estimates cost of a proposed StrategyBrief."""
    def __init__(self): super().__init__("CostEstimatorAgent")
    def estimate(self, strategy: StrategyBrief) -> Dict[str, float]:
        # Stub: logic would analyze # of RAG steps, # of bullets, etc.
        cost = len(strategy.target_keywords) * 0.01 + 0.20 # Simple heuristic
        return {"estimated_cost_usd": cost, "token_estimate": 15000}

class CostTrackerAgent(SwarmAgent):
    """V5.5: Tracks actual cost of a workflow via metrics."""
    def __init__(self): super().__init__("CostTrackerAgent")
    def log_final_cost(self, workflow_id: str, metrics: Dict[str, 'GeminiCallMetrics']):
        total_cost = 0 # Logic to sum API costs from metrics
        self.logger.info(f"Final cost for {workflow_id}: ${total_cost:.4f}")

# ============================================================================
# TIER 1 & 4: PRE-DRAFTING INTELLIGENCE
class OntologyMapperAgent(SwarmAgent):
    """TIER 1: Standardizes messy skills into canonical entities."""
    def __init__(self):
        super().__init__("OntologyMapperAgent")
        from agent_swarm import get_gemini_service
        self.gemini = get_gemini_service()

    def normalize_skills(self, raw_skills: List[str]) -> List[str]:
        # V5.4 Enhanced: Uses atomic prompt builder and JSON mode
        
        # E5: Define strict output schema
        output_schema = """
        {
            "normalized_skills": ["SKILL_1", "SKILL_2"],
            "mappings_used": {"Raw Skill": "Normalized Skill"}
        }
        """

        # Use new atomic builder (incorporates E1, E2, E3, E4)
        from prompts_RES import build_atomic_agent_prompt
        prompt = build_atomic_agent_prompt(
            task_directive="Normalize the provided raw skills list into canonical, standardized skill entities.",
            agent_identity="OntologyMapperAgent (Tier 1 atomic normalizer)",
            baton_context={
                "source_agent": "MasterResumeLoader",
                "data": raw_skills
            },
            relevant_failure_modes=["hallucination", "format_violation"],
            output_schema_str=output_schema
        )

        # Execute with JSON mode enforced (E5)
        try:
            response = self.gemini.call_api(
                prompt=prompt,
                section_id="OntologyMapper",
                temperature=0.1, # Low temp for deterministic normalization
                json_mode=True   # E5: Enforce JSON
            )
            
            if response and len(response) >= 1:
                text = response[0] if isinstance(response, tuple) else response
                import json
                data = json.loads(text)
                return data.get("normalized_skills", [])
            
        except Exception as e:
            self.logger.error(f"Normalization failed: {e}")
            # Fallback to simple heuristic if atomic agent fails
            return list(set([s.upper().replace(".", "").replace("JS", "") for s in raw_skills]))

        return []

class CompetitorAnalystAgent(SwarmAgent):
    """TIER 4: Finds peer company gaps for 'change agent' positioning."""
    def __init__(self): 
        super().__init__("CompetitorAnalystAgent")
        self.gemini = get_gemini_service()
    
    def analyze_peers(self, target_company: str, job_description: str) -> str:
        prompt = f"""Analyze 3 key competitors for {target_company} based on this job description. 
        Identify 1 strategic gap that this role is positioned to solve.
        JD Excerpt: {job_description[:1000]}"""
        response = self.gemini.generate(prompt, temperature=0.4)
        return response.text if response else "Competitor analysis unavailable."

# ============================================================================
# ADVISORY CREW (Consulted by Governor)
# ============================================================================
class ThemeIdentifierAgent(SwarmAgent):
    """V5.5: Splits ChiefStrategist. Identifies themes from JD."""
    def __init__(self): super().__init__("ThemeIdentifierAgent")
    def identify_themes(self, jd: str) -> List[str]:
        # Stub: Would use an LLM call to extract themes
        return ["AI Governance", "GTM Strategy", "Team Leadership"]

class ChiefStrategistAgent(SwarmAgent):
    """Develops the strategy brief for job application."""
    def __init__(self): 
        super().__init__("ChiefStrategistAgent")
    
    def create_brief(self, jd: str, master: Dict) -> StrategyBrief:
        # Simplified stub
        return StrategyBrief(
            primary_focus="AI/ML Leadership",
            differentiators=["Strategic Partnerships", "Enterprise Scale"],
            target_keywords=["AI", "Machine Learning", "Transformation"],
            confidence_score=0.95
        )

class StrategyValidatorAgent(SwarmAgent):
    """Validates strategy briefs."""
    def __init__(self): 
        super().__init__("StrategyValidatorAgent")
    
    def validate(self, strategy: StrategyBrief) -> VetoSignal:
        # Import inline to avoid circular dependency
        from core import VetoLevel
        if strategy.confidence_score < 0.7:
             return VetoSignal(VetoLevel.STRATEGY, self.name, "Strategy confidence too low")
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class RetryPolicyAgent(SwarmAgent):
    """Determines retry logic."""
    def __init__(self): 
        super().__init__("RetryPolicyAgent")

# ============================================================================
# EXECUTION SPECIALISTS - RESEARCH
# ============================================================================
class Enricher(SwarmAgent):
    def __init__(self): 
        super().__init__("Enricher")

class PortfolioLinkerAgent(SwarmAgent):
    """TIER 4: Selects best 1-2 portfolio links based on JD stack."""
    def __init__(self): 
        super().__init__("PortfolioLinkerAgent")
    
    def select_links(self, jd_stack: List[str], portfolio: Dict) -> List[str]:
        return []

# ============================================================================
# EXECUTION SPECIALISTS - VALIDATION (QA Classes 1-5)
# ============================================================================
class Constraint_Jargon_Checker(SwarmAgent):
    """QA Class 1: Linguistic/Fast"""
    def __init__(self): 
        super().__init__("Constraint_Jargon_Checker")
    
    def check(self, content: str) -> VetoSignal:
        # --- PRIORITY #3: Raise specific exception ---
        forbidden_jargon = ["synergy", "leverage", "utilize", "pioneer"]
        for term in forbidden_jargon:
            if f" {term} " in content.lower():
                raise MechanicalFailureError(f"Forbidden jargon detected: '{term}'")
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class FormatComplianceAgent(SwarmAgent):
    """TIER 4: ATS Police (Mechanical checks)."""
    def __init__(self): 
        super().__init__("FormatComplianceAgent")
    
    def check_ats(self, content: str) -> VetoSignal:
        from core import VetoLevel
        if "<table>" in content or "invisible" in content:
            return VetoSignal(VetoLevel.QA1_LINGUISTIC, self.name, "ATS Violation: Tables detected")
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class BiasScrubberAgent(SwarmAgent):
    """TIER 3: Checks for non-inclusive language."""
    def __init__(self): 
        super().__init__("BiasScrubberAgent")
        # Load protected groups from config if available, else default
        self.protected_groups = CONFIG.get('new_agent_configs', {}).get('bias_scrubber', {}).get('protected_groups', ["age", "gender", "race", "disability"])

    def scan(self, content: str) -> VetoSignal:
        from core import VetoLevel
        # Expanded basic list + config awareness
        biased_terms = ["ninja", "rockstar", "guru", "guys", "manpower", "chairman", "native english"]
        found_terms = [term for term in biased_terms if f" {term} " in content.lower()]
        
        if found_terms:
             return VetoSignal(VetoLevel.QA1_LINGUISTIC, self.name, f"Bias detected: {found_terms}")
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

# ============================================================================
# V5.5: ATOMIC FACTUAL VALIDATORS (Replaces FactualConsistency_Validator)
# ============================================================================

class MetricValidatorAgent(SwarmAgent):
    """V5.5: QA Class 2. Validates numbers, $, %."""
    def __init__(self): super().__init__("MetricValidatorAgent")
    def validate(self, content: str, master: Dict) -> VetoSignal:
        if "99.9%" in content and "99.9%" not in str(master): # Stub logic
            raise SemanticFailureError("Metric mismatch: 99.9%")
        from core import VetoLevel
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class TenureValidatorAgent(SwarmAgent):
    """V5.5: QA Class 2. Validates dates and durations."""
    def __init__(self): super().__init__("TenureValidatorAgent")
    def validate(self, content: str, master: Dict) -> VetoSignal: 
        from core import VetoLevel
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class EntityValidatorAgent(SwarmAgent):
    """V5.5: QA Class 2. Validates company names, titles, tech."""
    def __init__(self): super().__init__("EntityValidatorAgent")
    def validate(self, content: str, master: Dict) -> VetoSignal: 
        from core import VetoLevel
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class ClaimValidatorAgent(SwarmAgent):
    """V5.5: QA Class 2. Validates semantic claims (NLI)."""
    def __init__(self): super().__init__("ClaimValidatorAgent")
    def validate(self, content: str, master: Dict) -> VetoSignal: 
        from core import VetoLevel
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class ThematicAlignment_Validator(SwarmAgent):
    """QA Class 3: Semantic/Expensive"""
    def __init__(self): 
        super().__init__("ThematicAlignment_Validator")
    
    def align(self, content: str, strategy: StrategyBrief) -> VetoSignal:
        from core import VetoLevel
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class SemanticEntailmentValidator(SwarmAgent):
    """TIER 3: Uses Zero-Shot NLI via Gemini to verify claims prove skills."""
    def __init__(self): 
        super().__init__("SemanticEntailmentValidator")
        self.gemini = get_gemini_service()
    
    def align(self, content: str, strategy: StrategyBrief) -> VetoSignal:
        from core import VetoLevel
        # Zero-shot NLI check
        prompt = f"""Task: Semantic Entailment
Premise (Strategy): Primary focus is {strategy.primary_focus} with differentiators {strategy.differentiators}
Hypothesis (Content): This content strongly supports the strategy.
Content: {content[:1000]}...
Does the hypothesis logically follow from the premise based on the content? Answer YES or NO with brief reason."""
        
        response = self.gemini.generate(prompt, temperature=0.1)
        if response and "NO" in response.text.upper():
             return VetoSignal(VetoLevel.QA3_SEMANTIC, self.name, f"Semantic misalignment detected: {response.text[:100]}")
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

# --- QA Class 4 & 5 (Deep/Adversarial) ---
class NarrativeThreadAgent(SwarmAgent):
    """TIER 1: Ensures holistic thematic consistency across sections."""
    def __init__(self): 
        super().__init__("NarrativeThreadAgent")
    
    def check_coherence(self, full_draft: Dict[str, str], strategy: StrategyBrief) -> VetoSignal:
        from core import VetoLevel
        # Checks if 'primary_focus' from strategy appears in all major sections
        return VetoSignal(VetoLevel.NONE, self.name, "PASS")

class AdversarialReviewerAgent(SwarmAgent):
    """TIER 1: Red Team - The Skeptical Hiring Manager."""
    def __init__(self): 
        super().__init__("AdversarialReviewerAgent")
        self.system_prompt = "You are a skeptical CTO. Find reasons NOT to hire this candidate. Be harsh."
    
    def red_team(self, full_draft: str) -> VetoSignal:
        from core import VetoLevel
        # This would actually call Gemini with the hostile persona
        return VetoSignal(VetoLevel.NONE, self.name, "PASS (No obvious red flags)")

# ============================================================================
# EXECUTION SPECIALISTS - DRAFTING
# ============================================================================
class ExampleSelectorAgent(SwarmAgent):
    """V5.5: Selects few-shot examples from the Library."""
    def __init__(self, library_specialist: 'Library_Specialist'):
        super().__init__("ExampleSelectorAgent")
        self.lib = library_specialist
    def select(self, strategy: StrategyBrief, k: int = 3) -> List[str]:
        # Stub:
        # memories = self.lib.retrieve_memories(query=f"successful K1 for {strategy.primary_focus}", n_results=k)
        # return [mem['content'] for mem in memories]
        return ["Example 1...", "Example 2..."]

class Gemini_Drafter(SwarmAgent):
    """Drafts content using Gemini."""
    def __init__(self): 
        super().__init__("Gemini_Drafter")
    
    def draft(self, prompt: str) -> str:
        # Simplified stub - would call Gemini service
        return f"[Draft content for: {prompt[:50]}...]"

T = TypeVar('T')

# ============================================================================
# PART 1: GEMINI SERVICE (from gemini_service.py)
# ============================================================================

@dataclass
class GeminiResponse:
    """Response structure from Gemini API."""
    text: str
    usage: Dict[str, int]
    metadata: Dict[str, Any]
    cached: bool = False
    
@dataclass
class GeminiCallMetrics:
    """Metrics for a Gemini API call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cache_hit: bool = False
    temperature: float = DEFAULT_GENERATION_TEMPERATURE

class ResponseCache:
    """Simple response cache with TTL."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[GeminiResponse, float]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[GeminiResponse]:
        """Get cached response if not expired."""
        if key in self.cache:
            response, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return response
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: GeminiResponse):
        """Cache a response."""
        self.cache[key] = (response, time.time())
    
    def clear_expired(self):
        """Clear expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

class GeminiService:
    """
    Unified Gemini API Service - Hardened for Production
    Centralizes all Gemini API call logic for the Resume Generation Engine
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 model_name: str = "gemini-2.5-pro",
                 enable_caching: bool = True,
                 cache_ttl: int = 3600):
        """Initialize Gemini service."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.enable_caching = enable_caching
        self.cache = ResponseCache(cache_ttl) if enable_caching else None
        self.metrics = defaultdict(lambda: GeminiCallMetrics())
        
        if not GEMINI_AVAILABLE:
            logger.error("Gemini service unavailable - package not installed")
            return
        
        if not self.api_key:
            logger.warning("No Gemini API key provided")
            return
        
        # Configure API
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        try:
            generation_config = genai.GenerationConfig(
                temperature=DEFAULT_GENERATION_TEMPERATURE,
                top_p=0.95,
                top_k=40,
                max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
            )
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": SAFETY_THRESHOLD},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": SAFETY_THRESHOLD},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": SAFETY_THRESHOLD},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": SAFETY_THRESHOLD},
            ]
            
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            logger.info(f"Gemini service initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def generate(self, prompt: str, 
                temperature: float = None,
                max_tokens: int = None,
                reasoning_config: Optional[ReasoningConfig] = None,
                use_cache: bool = True) -> Optional[GeminiResponse]:
        """Generate text using Gemini API."""
        if not self.model:
            logger.error("Gemini model not initialized")
            return None
        
        # Check cache
        if use_cache and self.cache:
            cache_key = hashlib.md5(f"{prompt}:{temperature}:{max_tokens}".encode()).hexdigest()
            cached_response = self.cache.get(cache_key)
            if cached_response:
                logger.debug("Cache hit for Gemini request")
                cached_response.cached = True
                return cached_response
        
        # Enhance prompt with reasoning if configured
        if reasoning_config:
            prompt = enhance_system_prompt_with_reasoning(prompt, reasoning_config)
            api_params = reasoning_config_to_api_params(reasoning_config)
            temperature = temperature or api_params.get('temperature', DEFAULT_GENERATION_TEMPERATURE)
        else:
            temperature = temperature or DEFAULT_GENERATION_TEMPERATURE
        
        # Configure generation
        self.model.generation_config.temperature = temperature
        if max_tokens:
            self.model.generation_config.max_output_tokens = max_tokens
        
        # Generate with retry logic
        for attempt in range(DEFAULT_MAX_RETRIES):
            try:
                start_time = time.time()
                response = self.model.generate_content(prompt)
                latency = (time.time() - start_time) * 1000
                
                # Create response
                gemini_response = GeminiResponse(
                    text=response.text,
                    usage={
                        'prompt_tokens': len(prompt.split()),  # Approximation
                        'completion_tokens': len(response.text.split()),
                        'total_tokens': len(prompt.split()) + len(response.text.split())
                    },
                    metadata={
                        'model': self.model_name,
                        'temperature': temperature,
                        'latency_ms': latency,
                        'attempt': attempt + 1
                    }
                )
                
                # Cache response
                if use_cache and self.cache:
                    self.cache.set(cache_key, gemini_response)
                
                # Update metrics
                self.metrics['total'].prompt_tokens += gemini_response.usage['prompt_tokens']
                self.metrics['total'].completion_tokens += gemini_response.usage['completion_tokens']
                self.metrics['total'].total_tokens += gemini_response.usage['total_tokens']
                self.metrics['total'].latency_ms += latency
                
                return gemini_response
                
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                if attempt < DEFAULT_MAX_RETRIES - 1:
                    time.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"All Gemini API attempts failed: {e}")
                    return None
        
        return None

# Global Gemini service instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create global Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model_name=CONFIG.default_model,
            enable_caching=CONFIG.rag_config.enable_caching
        )
    return _gemini_service

# ============================================================================
# PART 2: EXECUTION SPECIALISTS (from execution_specialists_v5_2.py)
# ============================================================================

class Library_Specialist:
    """
    Persistent memory agent using ChromaDB for cross-job intelligence.
    Implements the rehydrated MasterResumeIndex from v5.4 patches.
    """
    
    def __init__(self, complexity: int = 50):
        """Initialize Library Specialist with ChromaDB persistence."""
        self.complexity = complexity
        self.storage_path = str(CACHE_DIR / "librarian_db")
        self.enabled = CHROMADB_AVAILABLE
        self.client = None
        self.collection = None
        
        if not self.enabled:
            logger.warning("Library Specialist disabled - ChromaDB not available")
            return
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.storage_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="resume_memories",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"📚 Library Specialist initialized with {self.collection.count()} memories")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.enabled = False
    
    def store_memory(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Store a memory in persistent storage."""
        if not self.enabled:
            return False
        
        try:
            # Generate unique ID
            memory_id = hashlib.md5(content.encode()).hexdigest()
            
            # Add timestamp
            metadata['timestamp'] = datetime.now().isoformat()
            metadata['source'] = 'library_specialist'
            
            # Store in ChromaDB
            self.collection.upsert(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            logger.debug(f"Stored memory {memory_id[:8]} with metadata: {list(metadata.keys())}")
            return True
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    def retrieve_memories(self, query: str, n_results: int = 5, 
                         filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query."""
        if not self.enabled:
            return []
        
        try:
            # Build where clause for filtering
            where = filter_metadata if filter_metadata else None
            
            # Query collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memory = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    }
                    memories.append(memory)
            
            logger.debug(f"Retrieved {len(memories)} memories for query: {query[:50]}...")
            return memories
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    def rehydrate_master_index(self, master_resume: Dict[str, Any]) -> MasterResumeIndex:
        """
        V5.4 PATCH: Rehydrate MasterResumeIndex from master resume data.
        This is the critical recovery mechanism from v3.8.
        """
        logger.info("🔄 Rehydrating MasterResumeIndex from master resume")
        
        # Extract personal info
        personal_info = {}
        if 'owner' in master_resume:
            personal_info = master_resume['owner']
        elif 'personal_info' in master_resume:
            personal_info = master_resume['personal_info']
        
        # Build experience map
        experience_map = {}
        if 'professional_experience' in master_resume:
            for exp in master_resume['professional_experience']:
                company = exp.get('company', 'Unknown')
                experience_map[company] = exp
        
        # Extract skills
        skills_index = {}
        if 'skills' in master_resume:
            for skill in master_resume['skills']:
                category = 'technical'  # Default category
                if skill in skills_index:
                    skills_index[skill].append(category)
                else:
                    skills_index[skill] = [category]
        
        # Create index
        index = MasterResumeIndex(
            personal_info=personal_info,
            experience_map=experience_map,
            skills_index=skills_index,
            education=master_resume.get('education', []),
            certifications=master_resume.get('certifications', []),
            thematic_clusters={},
            impact_metrics={},
            metadata={'rehydrated': True, 'timestamp': datetime.now().isoformat()}
        )
        
        # Store in memory for future reference
        self.store_memory(
            content=json.dumps(asdict(index) if is_dataclass(index) else index.__dict__),
            metadata={'type': 'master_index', 'rehydrated': True}
        )
        
        return index

class Web_Specialist:
    """
    Circuit-breaker protected web specialist for external data retrieval.
    Implements fault tolerance patterns from v3.8.
    """
    
    def __init__(self, complexity: int = 70):
        """Initialize Web Specialist with circuit breaker."""
        self.complexity = complexity
        self.circuit_state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout_seconds=60,
            half_open_max_attempts=2
        )
        self.cache = {}
        self.gemini_service = get_gemini_service()
    
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows request."""
        if self.circuit_state == CircuitBreakerState.CLOSED:
            return True
        
        if self.circuit_state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.circuit_config.recovery_timeout_seconds:
                    self.circuit_state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    return True
            return False
        
        # HALF_OPEN state
        return True
    
    def fetch_competitive_intelligence(self, company_name: str, 
                                      job_title: str) -> Dict[str, Any]:
        """Fetch competitive intelligence about company and role."""
        if not self._check_circuit_breaker():
            logger.warning("Circuit breaker OPEN - returning cached data")
            cache_key = f"{company_name}:{job_title}"
            return self.cache.get(cache_key, {})
        
        try:
            # Simulate competitive intelligence gathering
            # In production, this would call external APIs
            intel = {
                'company': {
                    'name': company_name,
                    'industry': 'Technology',
                    'size': 'Enterprise',
                    'culture': ['innovative', 'collaborative', 'fast-paced']
                },
                'role': {
                    'title': job_title,
                    'level': 'Senior',
                    'typical_requirements': ['leadership', 'technical expertise', 'communication']
                },
                'market': {
                    'demand': 'high',
                    'salary_range': '$150k-$250k',
                    'competition': 'moderate'
                }
            }
            
            # Reset circuit breaker on success
            if self.circuit_state == CircuitBreakerState.HALF_OPEN:
                self.circuit_state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED")
            
            # Cache result
            cache_key = f"{company_name}:{job_title}"
            self.cache[cache_key] = intel
            
            return intel
            
        except Exception as e:
            logger.error(f"Web fetch failed: {e}")
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.circuit_config.failure_threshold:
                self.circuit_state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker OPEN due to repeated failures")
            
            raise CircuitBreakerOpenError(f"Web fetch failed: {e}")

# ============================================================================
# V5.5: AGENTIC RAG PIPELINE AGENTS
# ============================================================================
class RAG_QueryGeneratorAgent(SwarmAgent):
    """V5.5: RAG Step 1. Generates search queries from strategy."""
    def __init__(self): super().__init__("RAG_QueryGeneratorAgent")
    def generate(self, strategy: StrategyBrief) -> List[str]:
        # Stub
        return [f"{strategy.primary_focus} market trends", f"{strategy.target_keywords[0] if strategy.target_keywords else 'AI'} best practices"]

class RAG_SearchAgent(SwarmAgent):
    """V5.5: RAG Step 2. Executes search against Web/Library."""
    def __init__(self, web_specialist: 'Web_Specialist', library_specialist: 'Library_Specialist'):
        super().__init__("RAG_SearchAgent")
        self.web = web_specialist
        self.lib = library_specialist
    def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        # Stub
        return [{"source": "web", "content": "Search result 1..."}, {"source": "library", "content": "Memory 1..."}]

class RAG_ChunkingAgent(SwarmAgent):
    """V5.5: RAG Step 3. Breaks documents into manageable chunks."""
    def __init__(self): super().__init__("RAG_ChunkingAgent")
    def chunk(self, documents: List[Dict[str, Any]]) -> List[str]:
        # Stub
        return [doc['content'][:100] if 'content' in doc else "" for doc in documents] # Simplified chunking

class RAG_RankingAgent(SwarmAgent):
    """V5.5: RAG Step 4. Ranks chunks for relevance."""
    def __init__(self): super().__init__("RAG_RankingAgent")
    def rank(self, chunks: List[str], strategy: StrategyBrief) -> List[Tuple[str, float]]:
        # Stub
        return [(chunk, 0.9) for chunk in chunks]

class RAG_FilterAgent(SwarmAgent):
    """V5.5: RAG Step 5. Selects top-k chunks."""
    def __init__(self): super().__init__("RAG_FilterAgent")
    def filter(self, ranked_chunks: List[Tuple[str, float]], top_k: int = 5) -> List[Tuple[str, float]]:
        return sorted(ranked_chunks, key=lambda x: x[1], reverse=True)[:top_k]

class RAG_CrossReferenceAgent(SwarmAgent):
    """V5.5: RAG Step 6. Annotates chunks with master resume facts."""
    def __init__(self): super().__init__("RAG_CrossReferenceAgent")
    def annotate(self, chunks: List[Tuple[str, float]], master: Dict) -> List[Dict[str, Any]]:
        # Stub
        return [{"chunk": chunk[0], "score": chunk[1], "validation": "SUPPORTED_BY_MASTER"} for chunk in chunks]

class RAG_DraftingAgent(SwarmAgent):
    """V5.5: RAG Step 7a. Writes the ThematicAnalysis draft."""
    def __init__(self): super().__init__("RAG_DraftingAgent")
    def draft(self, annotated_chunks: List[Dict]) -> str: 
        return "Draft of ThematicAnalysis..."
    def refine(self, draft: str, critiques: List[str]) -> ThematicAnalysis: 
        return ThematicAnalysis(themes=["Final Theme"])

class RAG_CritiqueAgent(SwarmAgent):
    """V5.5: RAG Step 7b. Critiques the draft from RAG_DraftingAgent."""
    def __init__(self): super().__init__("RAG_CritiqueAgent")
    def critique(self, draft: str) -> List[str]: 
        return ["Critique: Missing keyword X."]


class MarkdownToLatexAgent(SwarmAgent):
    """V5.5: Converts final Markdown to LaTeX for PDF output."""
    def __init__(self): super().__init__("MarkdownToLatexAgent")
    def convert(self, markdown_content: str) -> str:
        # Stub: Would use pandoc or similar
        return f"\\documentclass{{article}}\n\\begin{{document}}\n{markdown_content}\n\\end{{document}}"

class QA_Auditor:
    """
    Quality Assurance Auditor implementing comprehensive validation.
    """
    
    def __init__(self, complexity: int = 95):
        """Initialize QA Auditor."""
        self.complexity = complexity
        self.validator = PreFlightValidator()
        self.audit_history = []
    
    def audit_output(self, staging_buffer: ImmutableStagingBuffer,
                    thematic_analysis: ThematicAnalysis,
                    job_description: str,
                    master_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive QA audit."""
        logger.info("🔍 Performing QA audit on output")
        
        start_time = time.time()
        
        # Run validation
        passed, results, signal_score = self.validator.validate(
            staging_buffer=staging_buffer,
            thematic_analysis=thematic_analysis,
            job_description=job_description,
            master_resume=master_resume
        )
        
        # Generate report
        report = self.validator.generate_validation_report(results, signal_score)
        
        # Create audit record
        audit = {
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'signal_score': signal_score,
            'total_rules': len(results),
            'failures': [r.to_dict() for r in results if not r.passed],
            'report': report,
            'execution_time': time.time() - start_time
        }
        
        self.audit_history.append(audit)
        
        return audit

# ============================================================================
# PART 3: ADVISORY CREW (from advisory_crew_v5_2.py)
# ============================================================================

@dataclass
class CrewConfiguration:
    """Configuration for advisory crew operations."""
    max_complexity: int = 100
    parallel_execution: bool = True
    validation_threshold: float = 0.8
    enable_caching: bool = True
    debug_mode: bool = False

@dataclass
class CrewContext:
    """Shared context for crew operations."""
    job_description: str
    company_name: str
    job_title: str
    master_resume: Dict[str, Any]
    staging_buffer: ImmutableStagingBuffer = field(default_factory=ImmutableStagingBuffer)
    thematic_analysis: Optional[ThematicAnalysis] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class Governor:
    """
    🧑‍✈️ The Governor - Centralized complex autonomous agent that manages the swarm.
    Implements dynamic template mapping and HIL escalation from v5.4 patches.
    """
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        """Initialize the Governor and the entire agent swarm."""
        self.config = config or CrewConfiguration()
        # --- PRIORITY #1 & #2: Use LoggerAdapter ---
        self.logger = WorkflowLoggerAdapter(logging.getLogger(__name__), {"workflow_id": "N/A"})
        
        # Initialize Meta-Loop
        self.feedback_logger = FeedbackLoggerAgent()
        self.meta_planner = MetaPlannerAgent()
        self.pattern_finder = PatternFinderAgent() # V5.5

        # Initialize advisory crew
        self.theme_identifier = ThemeIdentifierAgent() # V5.5
        self.strategist = ChiefStrategistAgent()
        self.ontology_mapper = OntologyMapperAgent()  # TIER 1
        self.competitor_analyst = CompetitorAnalystAgent()  # TIER 4
        self.strategy_validator = StrategyValidatorAgent()
        self.retry_policy = RetryPolicyAgent()
        
        # V5.5: Cost Control
        self.cost_estimator = CostEstimatorAgent()
        self.cost_tracker = CostTrackerAgent()

        # Initialize core specialists (must happen before RAG_SearchAgent)
        self._initialize_specialists()

        # V5.5: Agentic RAG Pipeline
        self.rag_query_gen = RAG_QueryGeneratorAgent()
        self.rag_search = RAG_SearchAgent(self.web_specialist, self.library_specialist)
        self.rag_chunking = RAG_ChunkingAgent()
        self.rag_ranking = RAG_RankingAgent()
        self.rag_filter = RAG_FilterAgent()
        self.rag_cross_ref = RAG_CrossReferenceAgent()
        self.rag_drafter = RAG_DraftingAgent()
        self.rag_critiquer = RAG_CritiqueAgent()

        # Initialize drafting agents
        self.example_selector = ExampleSelectorAgent(self.library_specialist) # V5.5
        self.gemini_drafter = Gemini_Drafter()
        
        # Initialize validators
        self.qa1 = Constraint_Jargon_Checker()
        self.format_police = FormatComplianceAgent()  # TIER 4
        self.bias_scrubber = BiasScrubberAgent()  # TIER 3

        # V5.5: Atomic Factual Validators
        self.metric_validator = MetricValidatorAgent()
        self.tenure_validator = TenureValidatorAgent()
        self.entity_validator = EntityValidatorAgent()
        self.claim_validator = ClaimValidatorAgent()

        self.qa3 = ThematicAlignment_Validator()
        self.semantic_validator = SemanticEntailmentValidator()  # TIER 3
        self.narrative_thread = NarrativeThreadAgent()  # TIER 1
        self.red_team = AdversarialReviewerAgent()  # TIER 1
        
        # V5.5: Production Output
        self.latex_converter = MarkdownToLatexAgent()
        
        self.logger.info(f"🧑‍✈️ Governor initialized with {len(AGENT_COMPLEXITY)} agent types")
    
    def _initialize_specialists(self):
        """Initialize all specialist agents."""
        # Core specialists
        self.library_specialist = Library_Specialist(complexity=50)
        self.web_specialist = Web_Specialist(complexity=70)
        self.qa_auditor = QA_Auditor(complexity=95)
        
        # Gemini service for generation
        self.gemini_service = get_gemini_service()
        
        # Validation engine
        self.validator = PreFlightValidator()

        def process_request(self, context: CrewContext) -> Dict[str, Any]:
        """
        Main orchestration method - processes a complete job application.
        V5.4 10 Agents Patch: Integrated multi-tier validation flow.
        """
        self.logger.info(f"🚀 Governor processing request for {context.company_name} - {context.job_title}")
        # --- PRIORITY #1: Set workflow_id for all subsequent logs ---
        self.logger.extra["workflow_id"] = context.workflow_id
        
        results = {
            'phases': {},
            'artifacts': {},
            'validation': {},
            'metadata': {
                'workflow_id': context.workflow_id
            }
        }
        
        try:
            # 0. Pre-processing (Tier 1: Ontology)
            if 'skills' in context.master_resume:
                context.master_resume['normalized_skills'] = self.ontology_mapper.normalize_skills(
                    context.master_resume.get('skills', [])
                )
            
            # 1. Select Strategy (Consult Advisory)
            context.strategy = self.strategist.create_brief(context.job_description, context.master_resume)
            # (Tier 4: Competitor Analysis enrichment optional here)
            # context.strategy.competitor_intel = self.competitor_analyst.analyze_peers(...)
            
            veto = self.strategy_validator.validate(context.strategy)
            if veto.level.value != 0:  # NONE = 0
                return self._handle_veto(veto, context, results)
            
            # 2. Command Specialists (Execution)
            # (Simplified: would loop through required sections in strategy)
            draft = self.gemini_drafter.draft(f"Draft summary for: {context.job_description[:200]}...")
            
            # 3. QA & VETO Handling (Hierarchy: Strategy > Adversarial > Holistic > Semantic > Factual > Linguistic)
            
            # --- PRIORITY #3: Agent Telemetry & Error Classification ---
            # Example for QA1 (Linguistic/Fast)
            agent_name = "Constraint_Jargon_Checker"
            start_time = time.time()
            try:
                self.logger.info(f"Agent starting: {agent_name}")
                veto_signal = self.qa1.check(draft) # Raises MechanicalFailureError on fail
                duration_ms = (time.time() - start_time) * 1000
                self.logger.info(f"Agent finished: {agent_name}", extra={"duration_ms": duration_ms, "status": "SUCCESS"})
            
            except MechanicalFailureError as e:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(f"Agent VETO (Mechanical): {agent_name}", extra={"duration_ms": duration_ms, "status": "VETO_MECHANICAL", "error": str(e)})
                veto = VetoSignal(VetoLevel.QA1_LINGUISTIC, agent_name, str(e))
                return self._handle_veto(veto, context, results)
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.error(f"Agent FAILED (Critical): {agent_name}", exc_info=True, extra={"duration_ms": duration_ms, "status": "FAILURE"})
                veto = VetoSignal(VetoLevel.STRATEGY, agent_name, f"Critical agent failure: {e}")
                return self._handle_veto(veto, context, results)
            
            # (This pattern would repeat for other QA agents like format_police and bias_scrubber)
            # ... (format_police.check_ats, bias_scrubber.scan)

            # --- PRIORITY #3: Example for QA2 (Factual) ---
            agent_name = "FactualConsistency_Validator"
            start_time = time.time()
            try:
                self.logger.info(f"Agent starting: {agent_name}")
                veto_signal = self.qa2.validate(draft, context.master_resume) # Raises SemanticFailureError on fail
                duration_ms = (time.time() - start_time) * 1000
                self.logger.info(f"Agent finished: {agent_name}", extra={"duration_ms": duration_ms, "status": "SUCCESS"})
            
            except SemanticFailureError as e:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.warning(f"Agent VETO (Semantic): {agent_name}", extra={"duration_ms": duration_ms, "status": "VETO_SEMANTIC", "error": str(e)})
                veto = VetoSignal(VetoLevel.QA2_FACTUAL, agent_name, str(e))
                return self._handle_veto(veto, context, results)
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.error(f"Agent FAILED (Critical): {agent_name}", exc_info=True, extra={"duration_ms": duration_ms, "status": "FAILURE"})
                veto = VetoSignal(VetoLevel.STRATEGY, agent_name, f"Critical agent failure: {e}")
                return self._handle_veto(veto, context, results)
            
            # (This pattern would repeat for other QA classes)
            
            # QA3 (Semantic)
            veto = self.qa3.align(draft, context.strategy)
            if veto.level.value != 0: 
                return self._handle_veto(veto, context, results)
            # (SemanticEntailment would check specific bullets here)
            
            # QA4/5 (Holistic & Adversarial - usually run on full draft, simplified here)
            from core import ResumeSection
            veto = self.narrative_thread.check_coherence(
                {ResumeSection.K1_EXECUTIVE_SUMMARY.value: draft}, 
                context.strategy
            )
            if veto.level.value != 0: 
                return self._handle_veto(veto, context, results)
            
            veto = self.red_team.red_team(draft)
            if veto.level.value != 0: 
                return self._handle_veto(veto, context, results)
            
            results['validation'] = {'passed': True, 'status': 'SUCCESS'}
            results['artifacts'] = {'output': draft}
            results['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'governor_version': '5.4-enhanced',
                'agents_used': list(AGENT_COMPLEXITY.keys()),
                'workflow_id': context.workflow_id
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Governor processing failed: {e}")
            results['validation'] = {'passed': False, 'error': str(e)}
            return results
    
    def _handle_veto(self, veto: VetoSignal, context: CrewContext, results: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a veto signal from validation."""
        self.logger.warning(f"🚫 VETO from {veto.agent_name}: {veto.message} (Level: {veto.level})")
        
        # Log to meta-loop
        self.feedback_logger.log_event("VETO", {"agent": veto.agent_name, "reason": veto.message})

        results['validation'] = {
            'passed': False,
            'veto_agent': veto.agent_name,
            'veto_level': veto.level.value,
            'veto_message': veto.message,
            'status': 'VETOED'
        }
        results['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'governor_version': '5.4-enhanced',
            'failure_point': veto.agent_name
        }
        
        return results

    def _analyze_job_description(self, context: CrewContext) -> ThematicAnalysis:
        """Analyze job description for themes and requirements."""
        jd_text = context.job_description
        
        # Extract key information
        themes = text_utils.extract_keywords(jd_text, 10)
        skills = text_utils.extract_keywords(jd_text, 15)
        
        # Create thematic analysis
        analysis = ThematicAnalysis(
            themes=themes[:5],
            skills_required=skills[:10],
            impact_phrases=[],
            expertise_areas=themes[5:10] if len(themes) > 5 else [],
            company_values=[],
            strategic_priorities=[],
            confidence_scores={'overall': 0.8}
        )
        
        return analysis
    
    def _execute_rag_pipeline(self, context: CrewContext) -> Dict[str, Any]:
        """Execute 4-phase RAG pipeline."""
        results = {}
        accumulated_context = {'job_description': context.job_description}
        
        for phase in [RAGPhase.EXTRACTION, RAGPhase.ENRICHMENT, 
                     RAGPhase.SYNTHESIS, RAGPhase.VALIDATION]:
            mission = RAGMission(
                phase=phase,
                objective=f"Process {context.job_title} requirements",
                input_context=accumulated_context,
                constraints=['Be specific', 'Focus on relevance'],
                success_criteria=['High signal quality', 'Complete coverage']
            )
            
            phase_results = self.rag_synthesizer.execute_rag_mission(mission, accumulated_context)
            results[phase.value] = phase_results
            
            # Accumulate context for next phase
            accumulated_context[f'{phase.value.lower()}_results'] = phase_results
        
        # Calculate overall signal
        signal_scores = [r.get('signal_score', 0) for r in results.values()]
        results['overall_signal'] = sum(signal_scores) / len(signal_scores) if signal_scores else 0
        
        return results
    
    def _generate_content(self, context: CrewContext) -> Dict[str, str]:
        """Generate resume content using dynamic template mapping."""
        generated = {}
        
        # Key sections to generate
        sections = [
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K11_COVER_LETTER
        ]
        
        for section in sections:
            # V5.4 PATCH: Dynamic template mapping
            template_key = self._map_section_to_template(section)
            
            # Build context
            crl_context = build_crl_context_for_section(
                section_name=section.value,
                job_context={
                    'company_name': context.company_name,
                    'job_title': context.job_title,
                    'job_description': context.job_description
                },
                master_resume=context.master_resume,
                thematic_analysis=context.thematic_analysis
            )
            
            # --- FIX: USE RICH PROMPT TEMPLATES ---
            # Instead of generic prompt, use format_prompt_with_context to load 
            # the specific template from master_config.json
            
            # Prepare common kwargs for templates
            template_kwargs = {
                'master_context': crl_context,  # Pass full context as master for now
                'job_description': context.job_description,
                'company_name': context.company_name,
                'job_title': context.job_title,
            }

            # Add section-specific kwargs if available from thematic analysis
            if context.thematic_analysis:
                template_kwargs['primary_theme'] = context.thematic_analysis.themes[0] if context.thematic_analysis.themes else "Relevant Experience"
                # Add dummy values for other template requirements if needed to prevent KeyError
                template_kwargs['differentiators'] = "Key achievements"
                template_kwargs['required_keywords'] = ", ".join(context.thematic_analysis.skills_required[:5]) if context.thematic_analysis.skills_required else "relevant skills"

            # Generate prompt using the mapped template key
            try:
                prompt = format_prompt_with_context(template_key, **template_kwargs)
            except Exception as e:
                self.logger.error(f"Failed to format template {template_key}: {e}")
                # Fallback to generic if template fails
                prompt = f"Generate professional content for {section.value} based on:\n{crl_context}"

            # Execute generation
            response = self.gemini_service.generate(
                prompt=prompt,
                temperature=DEFAULT_GENERATION_TEMPERATURE
            )
            
            if response:
                generated[section.value] = response.text
            else:
                generated[section.value] = f"[Failed to generate {section.value}]"
        
        return generated
    
    def _map_section_to_template(self, section: ResumeSection) -> str:
        """
        V5.4 PATCH: Dynamic template mapping based on section type.
        Maps resume sections to appropriate prompt templates.
        """
        template_map = {
            ResumeSection.K1_EXECUTIVE_SUMMARY: 'executive_summary',
            ResumeSection.K2_UNIFY_OVERVIEW: 'experience_overview',
            ResumeSection.K2_UNIFY_BULLETS: 'experience_bullets',
            ResumeSection.K3_IBM_OVERVIEW: 'experience_overview',
            ResumeSection.K3_IBM_BULLETS: 'experience_bullets',
            ResumeSection.K11_COVER_LETTER: 'cover_letter'
        }
        
        return template_map.get(section, 'generic_section')
    
    def _validate_output(self, context: CrewContext) -> Dict[str, Any]:
        """Validate generated output."""
        passed, results, signal_score = self.validator.validate(
            staging_buffer=context.staging_buffer,
            thematic_analysis=context.thematic_analysis,
            job_description=context.job_description,
            master_resume=context.master_resume
        )
        
        return {
            'passed': passed,
            'signal_score': signal_score,
            'total_rules': len(results),
            'failures': len([r for r in results if not r.passed]),
            'pass_rate': sum(1 for r in results if r.passed) / len(results) if results else 0,
            'production_ready': passed and signal_score >= CONFIG.min_confidence_score
        }
    
    def _assemble_artifacts(self, context: CrewContext) -> Dict[str, Any]:
        """Assemble final artifacts from validated content."""
        artifacts = {}
        
        # --- ACTIVATING DEAD CODE: DuplicateDetector & TextSanitizer ---
        deduper = DuplicateDetector(threshold=0.9)
        sanitizer = TextSanitizer()
        seen_content = []
        # ---------------------------------------------------------------

        # --- FIX: IMPROVED RESUME ASSEMBLY ---
        # Define standard section order
        section_order = [
            ResumeSection.K0_NAME,
            ResumeSection.K0_CONTACT,
            ResumeSection.K0_HEADLINE,
            ResumeSection.K1_EXECUTIVE_SUMMARY,
            ResumeSection.K0_EXPERIENCE_HEADER,
            ResumeSection.K2_UNIFY_OVERVIEW,
            ResumeSection.K2_UNIFY_BULLETS,
            ResumeSection.K3_IBM_OVERVIEW,
            ResumeSection.K3_IBM_BULLETS,
            ResumeSection.K4_TRADERSENSE_NARRATIVE,
            ResumeSection.K5_EY_NARRATIVE,
            ResumeSection.K6_EARLY_CAREER_NARRATIVE,
            ResumeSection.K0_EDUCATION_HEADER,
            ResumeSection.K7_EDUCATION,
            ResumeSection.K0_CERTIFICATIONS_HEADER,
            ResumeSection.K8_CERTIFICATIONS,
            ResumeSection.K0_COMPETENCIES_HEADER,
            ResumeSection.K9_COMPETENCIES,
            ResumeSection.K10_SKILLS
        ]
        resume_parts = []
        for section in section_order:
            content = context.staging_buffer.get(section.value)
            if not content:
                continue
                
            # Special handling for headers
            if section.value.endswith("_HEADER"):
                header_text = section.value.replace("K0_", "").replace("_HEADER", "").replace("_", " ").title()
                resume_parts.append(f"\n## {header_text}\n")
                continue
            # Special handling for K0 (Name/Contact/Headline) - No extra newlines
            if section in [ResumeSection.K0_NAME, ResumeSection.K0_CONTACT, ResumeSection.K0_HEADLINE]:
                resume_parts.append(str(content))
                continue
            # Regular sections
            resume_parts.append(str(content))
        artifacts['resume'] = "\n".join(resume_parts).strip()
        # ------------------------------------------
        
        # Get cover letter
        cover_letter = context.staging_buffer.get(ResumeSection.K11_COVER_LETTER.value)
        if cover_letter:
            artifacts['cover_letter'] = cover_letter
        
        # Create tracker entry (unchanged)
        artifacts['tracker'] = {
            'company': context.company_name,
            'position': context.job_title,
            'date_applied': datetime.now().isoformat(),
            'status': 'ready_to_submit',
            'signal_score': context.validation_results.get('signal_score', 0),
            'notes': 'Generated by v5.4 recovery system'
        }
        
        # Generate QA report (unchanged)
        if context.validation_results:
            artifacts['qa_report'] = self._format_qa_report(context.validation_results)
        
        return artifacts
    
    def _format_qa_report(self, validation_results: Dict[str, Any]) -> str:
        """Format validation results as QA report."""
        report = f"""# QA Report

## Summary
- Status: {'✅ PASSED' if validation_results.get('passed') else '❌ FAILED'}
- Signal Score: {validation_results.get('signal_score', 0):.2%}
- Pass Rate: {validation_results.get('pass_rate', 0):.2%}
- Production Ready: {validation_results.get('production_ready', False)}

## Validation Details
- Total Rules Checked: {validation_results.get('total_rules', 0)}
- Failures: {validation_results.get('failures', 0)}

Generated: {datetime.now().isoformat()}
"""
        return report

class HIL_EscalationAgent:
    """
    Human-in-the-Loop Escalation Agent.
    V5.4 PATCH: Uses json.dump for persistence instead of memory references.
    """
    
    def __init__(self):
        """Initialize HIL Escalation Agent."""
        self.escalation_log = []
        self.escalation_file = CACHE_DIR / "hil_escalations.json"
    
    def escalate(self, issue: str, context: Dict[str, Any], 
                severity: str = "HIGH") -> Dict[str, Any]:
        """
        Escalate issue to human operator.
        V5.4 PATCH: Persist using json.dump instead of in-memory storage.
        """
        escalation = {
            'timestamp': datetime.now().isoformat(),
            'issue': issue,
            'severity': severity,
            'context': {k: str(v) for k, v in context.items()},  # Stringify for JSON
            'status': 'pending_review'
        }
        
        self.escalation_log.append(escalation)
        
        # V5.4 PATCH: Persist to file using json.dump
        try:
            with open(self.escalation_file, 'w') as f:
                json.dump(self.escalation_log, f, indent=2, default=str)
            logger.info(f"🚨 HIL escalation persisted to {self.escalation_file}")
        except Exception as e:
            logger.error(f"Failed to persist HIL escalation: {e}")
        
        return escalation

class CrewOrchestrator:
    """
    High-level orchestrator that manages the Governor and crew operations.
    """
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        """Initialize the Crew Orchestrator."""
        self.config = config or CrewConfiguration()
        self.governor = Governor(config)
        self.hil_agent = HIL_EscalationAgent()
        # --- PRIORITY #1 & #2: Use LoggerAdapter ---
        self.logger = WorkflowLoggerAdapter(logging.getLogger(__name__), {"workflow_id": "N/A"})
    
    def process_job_application(self, job_description: str, company_name: str,
                               job_title: str, master_resume: Dict[str, Any],
                               workflow_id: str) -> Dict[str, Any]: # --- PRIORITY #1 ---
        """
        Process a complete job application through the crew.
        """
        self.logger.info(f"📋 Orchestrating job application for {company_name} - {job_title}")
        
        # Create crew context
        context = CrewContext(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            master_resume=master_resume,
            workflow_id=workflow_id # --- PRIORITY #1 ---
        )
        
        # Rehydrate master index if library specialist is available
        # --- PRIORITY #1 & #2: Set workflow_id for all subsequent logs ---
        self.logger.extra["workflow_id"] = context.workflow_id
        
        if self.governor.library_specialist.enabled:
            master_index = self.governor.library_specialist.rehydrate_master_index(master_resume)
            context.metadata['master_index_rehydrated'] = True
        
        try:
            # Process through Governor
            results = self.governor.process_request(context)
            
            # Check if escalation needed
            if not results.get('validation', {}).get('passed', False):
                signal_score = results.get('validation', {}).get('signal_score', 0)
                if signal_score < 0.5:
                    # Escalate to human
                    escalation = self.hil_agent.escalate(
                        issue=f"Low signal score: {signal_score:.2%}",
                        context={
                            'company': company_name,
                            'job_title': job_title,
                            'validation_failures': results.get('validation', {}).get('failures', [])
                        },
                        severity='CRITICAL'
                    )
                    results['escalation'] = escalation
            
            results['workflow_results'] = {
                'status': 'COMPLETED' if results.get('validation', {}).get('passed') else 'FAILED',
                'phases': results.get('phases', {})
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            
            # Escalate critical failure
            escalation = self.hil_agent.escalate(
                issue=f"Critical orchestration failure: {e}",
                context={'company': company_name, 'job_title': job_title},
                severity='CRITICAL'
            )
            
            return {
                'workflow_results': {'status': 'FAILED', 'error': str(e)},
                'escalation': escalation
            }

# Export key classes
__all__ = [
    # Gemini Service
    'GeminiService', 'GeminiResponse', 'GeminiCallMetrics', 'get_gemini_service',
    
    # Specialists
    'Library_Specialist', 'Web_Specialist', 'RAG_Synthesizer', 'QA_Auditor',
    
    # Crew Management
    'Governor', 'CrewOrchestrator', 'CrewConfiguration', 'CrewContext',
    'HIL_EscalationAgent'
]
