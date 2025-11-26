# File: workflow_LIC.py
# Description: Complete workflow orchestration with live API integration
# Version: 12.0 - Strategic Alignment Engine

__version__ = "12.0"

import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Live API clients
from llm_clients import GeminiLLMClient
from retrieval_clients import GoogleSearchClient

# RAG agents (FIXED: import from rag_LIC, not rag_LIC_LIVE)
from rag_LIC import S2_SupervisorAgent

# Core models and utilities
from models_LIC import (
    OutreachMission, ProfileAnalysis, ResearchContext, MessageScaffold,
    GeneratedMessage, ValidationResult, QAReport, Archetype, Route,
    AgentStatus, ValidationSeverity, FactualGapError, FailureClassifier
)
from utils_LIC import CircuitBreaker, AdaptiveTemperatureController
from config_LIC import CONFIG_REGISTRY
from validation_LIC import ValidationAgent

# ============================================================================
# STAGE 1: PROFILE ANALYSIS AGENT
# ============================================================================

class ProfileAnalysisAgent:
    """
    Analyzes recipient profile to determine archetype classification
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
    
    def analyze_profile(self, mission: OutreachMission) -> ProfileAnalysis:
        """
        Classify recipient into archetype based on profile signals
        """
        self.status = AgentStatus.RUNNING
        
        title = mission.recipient_profile.get('title', '').lower()
        company = mission.recipient_profile.get('company', '').lower()
        
        # C_LEVEL indicators
        c_level_titles = ['ceo', 'cto', 'cfo', 'coo', 'chief', 'president', 'founder']
        if any(indicator in title for indicator in c_level_titles):
            archetype = Archetype.C_LEVEL
            confidence = 0.95
            reasoning = f"Title '{title}' indicates C-level executive"
            key_indicators = [title]
        
        # EXECUTIVE indicators
        elif any(indicator in title for indicator in ['vp', 'vice president', 'director', 'head of', 'lead']):
            archetype = Archetype.EXECUTIVE
            confidence = 0.90
            reasoning = f"Title '{title}' indicates executive/director level"
            key_indicators = [title]
        
        # RECRUITER indicators
        elif any(indicator in title for indicator in ['recruiter', 'talent', 'hiring', 'hr']):
            archetype = Archetype.RECRUITER
            confidence = 0.92
            reasoning = f"Title '{title}' indicates recruiting/talent acquisition"
            key_indicators = [title]
        
        # SENIOR_TA (Technical Authority) indicators
        elif any(indicator in title for indicator in ['principal', 'staff', 'senior', 'architect', 'tech lead', 'engineering manager']):
            archetype = Archetype.SENIOR_TA
            confidence = 0.88
            reasoning = f"Title '{title}' indicates senior technical authority"
            key_indicators = [title]
        
        # Default to EXECUTIVE if uncertain
        else:
            archetype = Archetype.EXECUTIVE
            confidence = 0.60
            reasoning = f"Default classification based on ambiguous title '{title}'"
            key_indicators = [title]
        
        self.status = AgentStatus.COMPLETED
        
        return ProfileAnalysis(
            archetype=archetype,
            confidence=confidence,
            reasoning=reasoning,
            key_indicators=key_indicators,
            needs_manual_override=(confidence < 0.75)
        )

# ============================================================================
# STAGE 3: ROUTING AGENT
# ============================================================================

class RoutingAgent:
    """
    Determines optimal message route based on connection status and context
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
    
    def determine_route(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis
    ) -> Tuple[Route, str]:
        """
        Select route based on connection status and prior message count
        """
        self.status = AgentStatus.RUNNING
        
        connection_status = mission.connection_status
        prior_messages = mission.prior_message_count
        
        # Route override if specified
        if mission.route_override:
            reasoning = f"Manual route override: {mission.route_override.value}"
            return mission.route_override, reasoning
        
        # Follow-up logic
        if prior_messages > 0:
            route = Route.FOLLOW_UP
            reasoning = f"Follow-up message (prior count: {prior_messages})"
        
        # Not connected - use CONNECTION_REQ
        elif connection_status == "not_connected":
            route = Route.CONNECTION_REQ
            reasoning = "Not connected - using LinkedIn connection request"
        
        # 1st degree connection - use INMAIL
        elif connection_status in ["1st", "connected"]:
            route = Route.INMAIL
            reasoning = "1st degree connection - using LinkedIn InMail"
        
        # Have email - use EMAIL
        elif connection_status == "email_available":
            route = Route.EMAIL
            reasoning = "Email available - using email outreach"
        
        # Default to INMAIL
        else:
            route = Route.INMAIL
            reasoning = f"Default routing for status: {connection_status}"
        
        self.status = AgentStatus.COMPLETED
        return route, reasoning

# ============================================================================
# STAGE 4: SCAFFOLD AGENT
# ============================================================================

class ScaffoldAgent:
    """
    Creates structural scaffold for message generation
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
    
    def create_scaffold(
        self,
        route: Route,
        archetype: Archetype,
        context: ResearchContext
    ) -> MessageScaffold:
        """
        Build message scaffold with sections and constraints
        """
        self.status = AgentStatus.RUNNING
        
        # Get constraints from config
        constraints = CONFIG_REGISTRY.get_route_constraints(route, archetype)
        
        # Define sections based on route
        sections = self._define_sections(route, constraints)
        
        # Check if we have enough context for sophisticated CTA
        context_aware_cta = len(context.rag_results) >= 5
        
        scaffold = MessageScaffold(
            route=route,
            archetype=archetype,
            sections=sections,
            constraints=constraints,
            locked_sections=set(),
            context_aware_cta=context_aware_cta
        )
        
        self.status = AgentStatus.COMPLETED
        return scaffold
    
    def _define_sections(self, route: Route, constraints: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Define required sections based on route"""
        
        if route == Route.CONNECTION_REQ:
            return {
                "greeting": {
                    "word_range": constraints.get("greeting_word_range", (2, 4)),
                    "required": True
                },
                "body": {
                    "word_range": (constraints.get("body_min_words", 25), constraints["word_range"][1]),
                    "required": True
                },
                "signature": {
                    "word_range": constraints.get("signature_word_range", (2, 4)),
                    "required": True
                }
            }
        
        elif route == Route.INMAIL:
            return {
                "subject": {
                    "word_range": constraints.get("subject_word_range", (4, 8)),
                    "required": constraints.get("subject_required", True)
                },
                "greeting": {
                    "word_range": constraints.get("greeting_word_range", (2, 5)),
                    "required": True
                },
                "body": {
                    "word_range": (constraints.get("body_min_words", 120), constraints["word_range"][1]),
                    "required": True
                },
                "cta": {
                    "word_range": constraints.get("cta_word_range", (5, 12)),
                    "required": True
                },
                "signature": {
                    "word_range": constraints.get("signature_word_range", (2, 6)),
                    "required": True
                }
            }
        
        elif route == Route.EMAIL:
            return {
                "subject": {
                    "word_range": constraints.get("subject_word_range", (4, 10)),
                    "required": constraints.get("subject_required", True)
                },
                "greeting": {
                    "word_range": constraints.get("greeting_word_range", (2, 6)),
                    "required": True
                },
                "body": {
                    "word_range": (constraints.get("body_min_words", 150), constraints["word_range"][1]),
                    "required": True
                },
                "cta": {
                    "word_range": constraints.get("cta_word_range", (6, 15)),
                    "required": True
                },
                "signature": {
                    "word_range": constraints.get("signature_word_range", (3, 8)),
                    "required": True
                }
            }
        
        else:  # FOLLOW_UP
            return {
                "subject": {
                    "word_range": constraints.get("subject_word_range", (4, 8)),
                    "required": constraints.get("subject_required", True)
                },
                "greeting": {
                    "word_range": constraints.get("greeting_word_range", (2, 4)),
                    "required": True
                },
                "body": {
                    "word_range": (constraints.get("body_min_words", 100), constraints["word_range"][1]),
                    "required": True
                },
                "cta": {
                    "word_range": constraints.get("cta_word_range", (5, 10)),
                    "required": True
                },
                "signature": {
                    "word_range": constraints.get("signature_word_range", (2, 5)),
                    "required": True
                }
            }

# ============================================================================
# CONSTRAINT FEASIBILITY CHECKER
# ============================================================================

class ConstraintFeasibilityChecker:
    """
    Pre-flight check for constraint feasibility
    """
    
    def check_feasibility(
        self,
        route: Route,
        archetype: Archetype,
        required_elements: List[str]
    ) -> Tuple[bool, str]:
        """
        Check if constraints are feasible given available context
        """
        constraints = CONFIG_REGISTRY.get_route_constraints(route, archetype)
        target_words = CONFIG_REGISTRY.get_target_word_count(archetype, route)
        
        # Minimum element count check
        min_words_per_element = 3
        min_total_words = len(required_elements) * min_words_per_element
        
        if target_words < min_total_words:
            return False, f"Target word count ({target_words}) insufficient for {len(required_elements)} required elements"
        
        # CONNECTION_REQ special case - very tight constraints
        if route == Route.CONNECTION_REQ and len(required_elements) > 4:
            return False, "Too many required elements for CONNECTION_REQ (max 4)"
        
        return True, "Constraints feasible"

# ============================================================================
# STAGE 7: QA AGENT
# ============================================================================

class QAAgent:
    """
    Generates comprehensive QA report from validation results
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
    
    def generate_qa_report(
        self,
        mission: OutreachMission,
        validation_results: List[ValidationResult]
    ) -> QAReport:
        """
        Generate QA report from validation results
        """
        self.status = AgentStatus.RUNNING
        
        critical_issues = sum(1 for r in validation_results if not r.passed and r.severity == ValidationSeverity.CRITICAL)
        high_issues = sum(1 for r in validation_results if not r.passed and r.severity == ValidationSeverity.HIGH)
        errors = sum(1 for r in validation_results if not r.passed and r.severity == ValidationSeverity.MEDIUM)
        warnings = sum(1 for r in validation_results if not r.passed and r.severity == ValidationSeverity.INFO)
        
        # Pass if no critical or high severity issues
        passed = (critical_issues == 0 and high_issues == 0)
        
        report = QAReport(
            mission_id=mission.mission_id,
            validation_results=validation_results,
            critical_issues=critical_issues,
            high_issues=high_issues,
            errors=errors,
            warnings=warnings,
            passed=passed,
            timestamp=datetime.now().isoformat()
        )
        
        self.status = AgentStatus.COMPLETED
        return report

# ============================================================================
# SELF-CONSISTENCY SYNTHESIZER
# ============================================================================

class SelfConsistencySynthesizer:
    """
    N-candidate generation with synthesis for C_LEVEL archetype
    Uses live LLM calls for candidate generation and synthesis
    """
    
    def __init__(self, llm_client: GeminiLLMClient):
        self.llm_client = llm_client
        self.n_candidates = 3
    
    async def synthesize_c_level_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate N candidates and synthesize the best elements
        Only used for C_LEVEL archetype
        """
        if scaffold.archetype != Archetype.C_LEVEL:
            raise ValueError("Self-consistency synthesis only for C_LEVEL")
        
        # Generate N candidates
        candidates = []
        for i in range(self.n_candidates):
            candidate = await self._generate_single_candidate(
                scaffold, context, profile_analysis, temperature + (i * 0.05)
            )
            candidates.append(candidate)
        
        # Synthesize best elements
        synthesized = await self._synthesize_candidates(candidates, context)
        return synthesized
    
    async def _generate_single_candidate(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate single candidate using live LLM call
        """
        prompt = self._build_candidate_prompt(scaffold, context, profile_analysis)
        
        # Execute LLM call (non-blocking)
        loop = asyncio.get_event_loop()
        try:
            candidate = await loop.run_in_executor(
                None, self.llm_client.generate, prompt
            )
            return candidate
        except Exception as e:
            print(f"     WARNING: Candidate generation failed: {e}")
            return f"Fallback candidate due to LLM error: {str(e)[:50]}"
    
    def _build_candidate_prompt(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis
    ) -> str:
        """Build prompt for single candidate generation"""
        
        # Extract key context
        recipient_name = context.recipient_insights[0] if context.recipient_insights else "Executive"
        company = context.company_context[0] if context.company_context else "organization"
        
        # RAG summary
        rag_summary = "\n".join([
            f"- {r.text[:100]}..." for r in context.rag_results[:10]
        ])
        
        prompt = f"""You are writing a C-level executive outreach message.

RECIPIENT: {recipient_name}
COMPANY: {company}

RESEARCH FINDINGS:
{rag_summary}

REQUIREMENTS:
- Target: {CONFIG_REGISTRY.get_target_word_count(Archetype.C_LEVEL, scaffold.route)} words
- Route: {scaffold.route.value}
- Tone: Strategic, peer-to-peer, focused on business impact
- NO placeholders
- Use specific metrics from research

Write a compelling message that demonstrates strategic alignment and thought leadership.
Output ONLY the message, no preamble."""
        
        return prompt
    
    async def _synthesize_candidates(self, candidates: List[str], context: ResearchContext) -> str:
        """
        Synthesize best elements from N candidates using live LLM
        """
        candidates_text = "\n\n---CANDIDATE---\n\n".join([
            f"CANDIDATE {i+1}:\n{c}" for i, c in enumerate(candidates)
        ])
        
        prompt = f"""You are synthesizing the best elements from multiple message candidates.

{candidates_text}

Your task: Create a single, superior message that combines:
- The strongest opening
- The most compelling body (value proposition + personalization)
- The best call-to-action

Output ONLY the synthesized message, no preamble or explanation."""
        
        # Execute LLM call
        loop = asyncio.get_event_loop()
        try:
            synthesized = await loop.run_in_executor(
                None, self.llm_client.generate, prompt
            )
            return synthesized
        except Exception as e:
            print(f"     WARNING: LLM synthesis failed: {e}. Using longest candidate.")
            return max(candidates, key=len)

# ============================================================================
# GENERATION ORCHESTRATOR
# ============================================================================

class GenerationOrchestrator:
    """
    Enhanced with live LLM generation
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker, llm_client: GeminiLLMClient):
        self.circuit_breaker = circuit_breaker
        self.llm_client = llm_client
        self.status = AgentStatus.IDLE
        self.feasibility_checker = ConstraintFeasibilityChecker()
        self.temp_controller = AdaptiveTemperatureController()
        self.synthesizer = SelfConsistencySynthesizer(llm_client)
    
    async def generate_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        validation_agent: ValidationAgent
    ) -> GeneratedMessage:
        """
        Generate with pre-flight, adaptive temp, and S6->S2 failure classification
        """
        self.status = AgentStatus.RUNNING
        
        # Constraint Pre-Flight Test
        required_elements = [
            f"Recipient name: {context.recipient_insights[0] if context.recipient_insights else 'N/A'}",
            f"Company: {context.company_context[0] if context.company_context else 'N/A'}",
            "Value proposition",
            "Call to action"
        ]
        
        feasible, reason = self.feasibility_checker.check_feasibility(
            scaffold.route,
            scaffold.archetype,
            required_elements
        )
        
        if not feasible:
            raise ValueError(f"Constraint pre-flight failed: {reason}")
        
        # S5 Generation/Retry Loop
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            
            temperature = self.temp_controller.get_temperature(
                "full_message",
                scaffold.archetype,
                attempt
            )
            
            # Generate message
            content = await self._generate_content(
                scaffold,
                context,
                profile_analysis,
                temperature
            )
            
            # Calculate metrics
            word_count = len(content.split())
            char_count = len(content)
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            message = GeneratedMessage(
                content=content,
                word_count=word_count,
                char_count=char_count,
                route=scaffold.route,
                archetype=scaffold.archetype,
                generation_temperature=temperature,
                generation_attempts=attempt,
                locked_sections=scaffold.locked_sections.copy(),
                checksum=checksum
            )
            
            # Validate with S6
            validation_results = validation_agent.validate_message(message, context)
            
            # Check if passed
            critical_failures = [r for r in validation_results if not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            
            if not critical_failures:
                # Success!
                self.temp_controller.record_success("full_message", scaffold.archetype, temperature)
                self.status = AgentStatus.COMPLETED
                return message
            
            # Failure Classification
            print(f"     S5: Generation attempt {attempt} failed validation...")
            failure_type, failure_report = self._classify_failure(critical_failures)

            if failure_type == FailureClassifier.FACTUAL_FAILURE:
                print(f"     S5 REASON: Factual failure detected. {failure_report}")
                print(f"     S5 ACTION: Halting generation retry. Triggering S6->S2 re-planning loop.")
                raise FactualGapError(critical_failures)
            else:
                print(f"     S5 REASON: Creative failure detected. {failure_report}")
                print(f"     S5 ACTION: Retrying with escalated temperature.")
        
        # Failed after max attempts
        self.status = AgentStatus.FAILED
        raise ValueError(f"Failed to generate valid message after {max_attempts} creative attempts")

    def _classify_failure(self, failures: List[ValidationResult]) -> Tuple[FailureClassifier, str]:
        """
        v12.0: Classify S6 failures to decide retry strategy
        LIC-QA-201 (strategic alignment) triggers FACTUAL_FAILURE
        """
        FACTUAL_RULES = {
            "LIC-QA-201",  # NEW v12.0: Strategic alignment failure
            "LIC-QA-106", "LIC-QA-105", "LIC-QA-043", "LIC-QA-003",
        }

        for f in failures:
            if f.rule_id in FACTUAL_RULES:
                return FailureClassifier.FACTUAL_FAILURE, f"({f.rule_id}) {f.message}"
            
            # Check details for failure_classifier override
            if f.details and isinstance(f.details, dict):
                if f.details.get("failure_classifier") == FailureClassifier.FACTUAL_FAILURE.value:
                    return FailureClassifier.FACTUAL_FAILURE, f"({f.rule_id}) {f.message}"

        return FailureClassifier.CREATIVE_FAILURE, f"({failures[0].rule_id}) {failures[0].message}"

    async def _generate_content(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate message content using live LLM calls
        """
        # C_LEVEL uses N-candidate synthesis
        if scaffold.archetype == Archetype.C_LEVEL:
            return await self.synthesizer.synthesize_c_level_message(
                scaffold, context, profile_analysis, temperature
            )
        
        # Standard generation for other archetypes
        prompt = self._build_generation_prompt(scaffold, context, profile_analysis)
        
        # Execute LLM call (non-blocking)
        loop = asyncio.get_event_loop()
        try:
            content = await loop.run_in_executor(
                None, self.llm_client.generate, prompt
            )
            return content
        except Exception as e:
            print(f"     WARNING: LLM generation call failed: {e}")
            return self._fallback_generation(scaffold, context, profile_analysis)
    
    def _build_generation_prompt(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis
    ) -> str:
        """
        v12.0: Strategic Alignment Generation Prompt
        Aligns sender capabilities with recipient strategic priorities
        """
        
        # 1. Load Sender Voice Profile
        voice_profile = self._load_voice_profile()
        persona = voice_profile.get('persona', 'Strategic AI Leader')
        principles = "\n".join([f"- {p}" for p in voice_profile.get('communication_principles', [])])
        forbidden = ", ".join(voice_profile.get('forbidden_phrases', []))

        # 2. Extract Sender Grounding from Context
        # InternalAgent has tagged RAGResults by source
        sender_caps = [
            r.text for r in context.rag_results 
            if r.source_type in ["MASTER_RESUME", "SENDER_KNOWLEDGE_BASE"]
        ]
        # Simple summarization for the prompt (top 5 capabilities)
        sender_summary = "\n".join([f"- {cap[:150]}..." for cap in sender_caps[:5]])
        
        # Fallback if no sender grounding
        if not sender_summary:
            sender_summary = "- Professional with relevant experience in the field"

        # 3. Extract Recipient Priorities from Context
        # Strategic brief results are the highest signal
        recipient_needs = [
            r.text for r in context.rag_results 
            if r.source_type == "STRATEGIC_BRIEF"
        ]
        # Simple summarization for the prompt (top 5 priorities)
        recipient_summary = "\n".join([f"- {need[:150]}..." for need in recipient_needs[:5]])
        
        # Fallback to other high-value context if no strategic brief
        if not recipient_summary:
            recipient_needs = [
                r.text for r in context.rag_results 
                if r.source_type in ["RECIPIENT_LINKEDIN_ABOUT", "COMPANY_BLOG_ANNOUNCEMENT", "NEWS_ARTICLE_COMPANY"]
            ]
            recipient_summary = "\n".join([f"- {need[:150]}..." for need in recipient_needs[:5]])
        
        if not recipient_summary:
            recipient_summary = f"- {context.recipient_insights[0] if context.recipient_insights else 'Professional at target company'}\n- {context.company_context[0] if context.company_context else 'Works in relevant industry'}"

        # 4. Get Constraints from Config
        word_count_target = CONFIG_REGISTRY.get_target_word_count(scaffold.archetype, scaffold.route)
        
        # 5. Adversarial constraints
        avoid_claims = ""
        if context.adversarial_findings:
            avoid_claims = f"\n\nCRITICAL - DO NOT USE: These claims were flagged as weak by adversarial review:\n" + "\n".join([f"  × {finding}" for finding in context.adversarial_findings])

        # 6. Build the Final Prompt
        prompt = f"""You are an expert at crafting executive-level strategic outreach. Your persona is "{persona}".

Your communication principles are:
{principles}

---
MY CAPABILITIES (GROUND TRUTH):
{sender_summary}

---
THEIR PRIORITIES (GROUND TRUTH):
{recipient_summary}

---
THE MISSION:
You will draft a peer-to-peer message for the target defined in `mission_input_LIC.json`.

CRITICAL REQUIREMENTS:
- The message MUST align my specific capabilities with their stated strategic priorities.
- The message MUST be between {word_count_target - 30} and {word_count_target + 30} words.
- The message MUST NOT contain any of these forbidden phrases: {forbidden}
- The message MUST be confident, direct, and assume a peer-to-peer relationship.
- DO NOT use flattery. DO NOT use social hooks. Focus only on strategic, data-driven alignment.
- Use specific metrics from MY CAPABILITIES when relevant.
- Reference specific initiatives/priorities from THEIR PRIORITIES when possible.
- NO placeholders like [TOPIC], [COMPANY], [NAME] - use actual names and specifics.

ROUTE CONTEXT:
- Message type: {scaffold.route.value}
- Recipient archetype: {scaffold.archetype.value}
{avoid_claims}

Draft the complete message. Output ONLY the message content, no preamble or explanation.
"""
        return prompt
    
    def _load_voice_profile(self) -> Dict[str, Any]:
        """Load sender_voice_profile.json if available"""
        filepath = "sender_voice_profile.json"
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _fallback_generation(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis
    ) -> str:
        """Simple fallback template if LLM call fails"""
        recipient_name = "Valued Professional"
        company = context.company_context[0] if context.company_context else "your organization"
        
        tone = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "message_tone")
        verbs = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "verb_preference")
        
        if scaffold.route == Route.CONNECTION_REQ:
            return f"Hi {recipient_name}, I'm reaching out to {verbs[0] if verbs else 'connect'} regarding opportunities at {company}. Looking forward to connecting."
        elif scaffold.route == Route.INMAIL:
            return f"Dear {recipient_name},\n\nI'm writing to {verbs[0] if verbs else 'discuss'} the exciting opportunity at {company}. With my background in AI and machine learning, I believe I can contribute significantly to your team's goals.\n\nI'd appreciate the opportunity to {verbs[1] if len(verbs) > 1 else 'connect'} and learn more.\n\nBest regards"
        else:
            return f"Dear {recipient_name}, Reaching out regarding {company}. Best regards"

# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """
    Complete workflow orchestrator with live API integration
    """
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        
        # Create live API clients
        self.llm_client = GeminiLLMClient(self.circuit_breaker)
        self.search_client = GoogleSearchClient(self.circuit_breaker)
        
        # Initialize agents with injected clients
        self.profile_agent = ProfileAnalysisAgent(self.circuit_breaker)
        
        # S2_SupervisorAgent accepts both clients
        self.research_orchestrator = S2_SupervisorAgent(
            self.circuit_breaker,
            self.llm_client,
            self.search_client
        )
        
        self.routing_agent = RoutingAgent(self.circuit_breaker)
        self.scaffold_agent = ScaffoldAgent(self.circuit_breaker)
        
        # GenerationOrchestrator accepts llm_client
        self.generation_orchestrator = GenerationOrchestrator(
            self.circuit_breaker,
            self.llm_client
        )
        
        self.validation_agent = ValidationAgent(self.circuit_breaker)
        self.qa_agent = QAAgent(self.circuit_breaker)
        
        self.events: List[Dict[str, Any]] = []
    
    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """
        Execute complete workflow with S6->S2 meta-loop
        """
        start_time = datetime.now()
        MAX_META_LOOPS = 3
        
        profile_analysis: Optional[ProfileAnalysis] = None
        corrected_profile_analysis: Optional[ProfileAnalysis] = None
        context: Optional[ResearchContext] = None
        route: Optional[Route] = None
        scaffold: Optional[MessageScaffold] = None
        message: Optional[GeneratedMessage] = None
        qa_report: Optional[QAReport] = None
        
        try:
            # Stage 1: Profile Analysis
            print("\n[S1] Profile Analysis...")
            profile_analysis = self.profile_agent.analyze_profile(mission)
            print(f"     Archetype: {profile_analysis.archetype.value} (confidence: {profile_analysis.confidence:.2f})")
            
            # Manual Override Check
            if profile_analysis.needs_manual_override:
                print(f"\n     ⚠️  Low confidence ({profile_analysis.confidence:.2f}). Manual override recommended.")
                override = input(f"     Confirm archetype {profile_analysis.archetype.value}? (y/n): ").strip().lower()
                
                if override != 'y':
                    print("     Available archetypes: C_LEVEL, EXECUTIVE, SENIOR_TA, RECRUITER")
                    new_archetype = input("     Enter correct archetype: ").strip().upper()
                    try:
                        profile_analysis.archetype = Archetype[new_archetype]
                        profile_analysis.confidence = 1.0
                        profile_analysis.reasoning = "Manual override by user"
                        print(f"     Updated to: {profile_analysis.archetype.value}")
                    except KeyError:
                        print(f"     Invalid archetype. Keeping {profile_analysis.archetype.value}")
            
            corrected_profile_analysis = profile_analysis
            refinement_context_from_s6: List[ValidationResult] = None
            
            # S6 -> S2 META-LOOP
            for meta_attempt in range(1, MAX_META_LOOPS + 1):
                print(f"\n{'='*40}")
                print(f"META-LOOP ATTEMPT {meta_attempt}/{MAX_META_LOOPS}")
                print(f"{'='*40}")

                try:
                    # Stage 2: Research
                    print("\n[S2] Research Orchestration...")
                    context, corrected_profile_analysis = await self.research_orchestrator.conduct_research(
                        mission,
                        corrected_profile_analysis,
                        refinement_context=refinement_context_from_s6
                    )
                    
                    if corrected_profile_analysis.archetype != profile_analysis.archetype and meta_attempt == 1:
                        print(f"     ✨ Archetype corrected: {profile_analysis.archetype.value} → {corrected_profile_analysis.archetype.value}")
                    
                    print(f"     RAG Results: {len(context.rag_results)}")
                    print(f"     Reflexion Iterations: {context.reflexion_iterations}")
                    
                    # Stage 3: Routing
                    print("\n[S3] Route Determination...")
                    route, routing_reasoning = self.routing_agent.determine_route(mission, corrected_profile_analysis)
                    print(f"     Route: {route.value}")
                    
                    # Stage 4: Scaffold
                    print("\n[S4] Scaffold Creation...")
                    scaffold = self.scaffold_agent.create_scaffold(route, corrected_profile_analysis.archetype, context)
                    
                    # Stage 5+6: Generation with Validation
                    print("\n[S5+S6] Generation with Validation...")
                    message = await self.generation_orchestrator.generate_message(
                        scaffold,
                        context,
                        corrected_profile_analysis,
                        self.validation_agent
                    )
                    
                    print(f"     S5: Generation SUCCEEDED in meta-attempt {meta_attempt}.")
                    break
                
                except FactualGapError as e:
                    print(f"\n     🔥 S6->S2 RE-PLANNING (Meta-Attempt {meta_attempt+1}) due to factual failure...")
                    refinement_context_from_s6 = e.args[0]
                    
                    if meta_attempt == MAX_META_LOOPS:
                        raise Exception(f"Factual failure not resolved after {MAX_META_LOOPS} meta-loops")
                    
                    continue
            
            # Stage 7: Final QA Report
            print("\n[S7] QA Report Generation...")
            final_validation_results = self.validation_agent.validate_message(message, context)
            qa_report = self.qa_agent.generate_qa_report(mission, final_validation_results)
            
            end_time = datetime.now()
            workflow_time = (end_time - start_time).total_seconds()
            
            result = {
                "status": "success",
                "production_ready": qa_report.passed,
                "workflow_time": workflow_time,
                "message": message.content,
                "route": route.value,
                "archetype": corrected_profile_analysis.archetype.value,
                "word_count": message.word_count,
                "generation_attempts": message.generation_attempts,
                "qa_summary": {
                    "critical_issues": qa_report.critical_issues,
                    "high_issues": qa_report.high_issues,
                    "errors": qa_report.errors,
                    "warnings": qa_report.warnings
                },
                "qa_report": self._format_qa_report(qa_report)
            }
            
            # Stage 8: Post-Send Tracking
            if qa_report.passed:
                await self._execute_post_send_tracking(mission, message, result)
            
            return result
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "production_ready": False
            }
    
    def _format_qa_report(self, qa_report: QAReport) -> str:
        """Format QA report for display"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("QA VALIDATION REPORT")
        lines.append("="*80)
        
        if qa_report.passed:
            lines.append("\n✅ ALL VALIDATIONS PASSED")
        else:
            lines.append("\n❌ VALIDATION FAILURES DETECTED")
        
        critical = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.CRITICAL]
        high = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.HIGH]
        medium = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.MEDIUM]
        info = [r for r in qa_report.validation_results if r.severity == ValidationSeverity.INFO]
        
        if critical:
            lines.append(f"\n🔴 CRITICAL ISSUES ({len(critical)}):")
            for r in critical:
                lines.append(f"   - [{r.rule_id}] {r.message}")
        
        if high:
            lines.append(f"\n🟠 HIGH SEVERITY ({len(high)}):")
            for r in high:
                lines.append(f"   - [{r.rule_id}] {r.message}")
        
        if medium:
            lines.append(f"\n🟡 MEDIUM SEVERITY ({len(medium)}):")
            for r in medium:
                lines.append(f"   - [{r.rule_id}] {r.message}")
        
        if info:
            lines.append(f"\n🔵 INFO ({len(info)}):")
            for r in info:
                lines.append(f"   - [{r.rule_id}] {r.message}")
        
        lines.append("\n" + "="*80)
        return "\n".join(lines)
    
    async def _execute_post_send_tracking(
        self,
        mission: OutreachMission,
        message: GeneratedMessage,
        result: Dict[str, Any]
    ):
        """
        Post-send tracking with message_ledger.json update
        """
        print("\n" + "="*80)
        print("POST-SEND TRACKING")
        print("="*80)
        
        sent = input("\nDid you send this message? (Y/N): ").strip().upper()
        
        if sent == "Y":
            # Generate App Tracker JSON
            tracker = {
                "mission_id": mission.mission_id,
                "timestamp": datetime.now().isoformat(),
                "recipient": {
                    "name": mission.recipient_profile.get("name"),
                    "title": mission.recipient_profile.get("title"),
                    "company": mission.recipient_profile.get("company")
                },
                "job": {
                    "title": mission.job_description.get("title"),
                    "company": mission.job_description.get("company")
                },
                "message": {
                    "route": message.route.value,
                    "archetype": message.archetype.value,
                    "word_count": message.word_count,
                    "checksum": message.checksum,
                    "content_preview": message.content[:100]
                },
                "status": "sent",
                "follow_up_date": (datetime.now() + timedelta(days=3)).isoformat()
            }
            
            # Save application tracker
            tracker_path = Path(f"tracker_{mission.mission_id}.json")
            with open(tracker_path, 'w') as f:
                json.dump(tracker, f, indent=2)
            
            print(f"\n✅ Application tracker saved: {tracker_path}")
            
            # Update message_ledger.json
            self._update_message_ledger(message)
    
    def _update_message_ledger(self, message: GeneratedMessage):
        """
        Update message_ledger.json with sent message for diversity validation
        """
        ledger_path = "message_ledger.json"
        
        # Load existing ledger
        ledger = []
        if os.path.exists(ledger_path):
            try:
                with open(ledger_path, 'r') as f:
                    ledger = json.load(f)
            except Exception as e:
                print(f"     WARNING: Could not load message ledger: {e}")
                ledger = []
        
        # Add new entry
        ledger.append({
            "timestamp": datetime.now().isoformat(),
            "checksum": message.checksum,
            "content": message.content,
            "word_count": message.word_count,
            "route": message.route.value,
            "archetype": message.archetype.value
        })
        
        # Save updated ledger
        try:
            with open(ledger_path, 'w') as f:
                json.dump(ledger, f, indent=2)
            print(f"✅ Message ledger updated: {ledger_path}")
        except Exception as e:
            print(f"     WARNING: Could not save message ledger: {e}")