# File: workflow.py
# Description: Core workflow orchestration for the LIC agentic system.

__version__ = "11.10"

import asyncio
import hashlib
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Set

# Local module imports
from models import (
    OutreachMission, ProfileAnalysis, Archetype, AgentStatus, ResearchContext,
    Route, MessageScaffold, GeneratedMessage, ValidationResult, QAReport,
    ValidationSeverity, FactualGapError, FailureClassifier
)
from config import CONFIG_REGISTRY
from utils import CircuitBreaker, AdaptiveTemperatureController
from rag import S2_SupervisorAgent
from validation import ValidationAgent, ConstraintFeasibilityChecker

# ============================================================================
# S1: PROFILE ANALYSIS AGENT
# ============================================================================

class ProfileAnalysisAgent:
    """
    NEW v11.6: Hardened archetype classification with 4-archetype standard
    Implements deterministic classification logic from v10.22
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
    
    def analyze_profile(self, mission: OutreachMission) -> ProfileAnalysis:
        """
        NEW v11.6: Hardened static classification with 5-node decision tree
        """
        self.status = AgentStatus.RUNNING
        
        recipient = mission.recipient_profile
        title = recipient.get("title", "").lower()
        
        # Node 1: C_LEVEL detection (CEO, CTO, CFO, COO, CMO, CPO)
        c_level_titles = ["ceo", "cto", "cfo", "coo", "cmo", "cpo", "chief"]
        if any(c_title in title for c_title in c_level_titles):
            confidence = 0.95
            archetype = Archetype.C_LEVEL
            reasoning = f"Title '{recipient.get('title')}' contains C-level indicator"
            key_indicators = ["C-level title"]
        
        # Node 2: EXECUTIVE detection (VP, SVP, EVP, Head of, Director)
        elif any(exec_title in title for exec_title in ["vp", "vice president", "svp", "evp", "head of", "director"]):
            confidence = 0.90
            archetype = Archetype.EXECUTIVE
            reasoning = f"Title '{recipient.get('title')}' indicates executive level"
            key_indicators = ["Executive title"]
        
        # Node 3: RECRUITER detection (Recruiter, Talent, Hiring, HR)
        elif any(rec_term in title for rec_term in ["recruit", "talent", "hiring", "human resources", "hr"]):
            confidence = 0.92
            archetype = Archetype.RECRUITER
            reasoning = f"Title '{recipient.get('title')}' indicates recruiting/talent role"
            key_indicators = ["Recruiting title"]
        
        # Node 4: SENIOR_TA detection (Staff, Principal, Distinguished, Fellow, Senior)
        elif any(ta_term in title for ta_term in ["staff", "principal", "distinguished", "fellow", "senior engineer", "senior architect"]):
            confidence = 0.85
            archetype = Archetype.SENIOR_TA
            reasoning = f"Title '{recipient.get('title')}' indicates senior technical authority"
            key_indicators = ["Senior technical title"]
        
        # Node 5: Default to SENIOR_TA for ambiguous technical roles
        else:
            confidence = 0.70
            archetype = Archetype.SENIOR_TA
            reasoning = "Defaulting to SENIOR_TA for ambiguous title"
            key_indicators = ["Ambiguous title"]
        
        needs_manual_override = confidence < 0.85
        self.status = AgentStatus.COMPLETED
        
        return ProfileAnalysis(
            archetype=archetype,
            confidence=confidence,
            reasoning=reasoning,
            key_indicators=key_indicators,
            needs_manual_override=needs_manual_override
        )

# ============================================================================
# S3: ROUTING AGENT
# ============================================================================

class RoutingAgent:
    """
    NEW v11.6: Hardened deterministic routing with 5-node tree (GAP 2.1)
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
        NEW v11.6: 5-node deterministic routing tree from v10.22
        """
        self.status = AgentStatus.RUNNING
        
        if mission.route_override:
            reasoning = f"Node 1: Manual route override to {mission.route_override.value}"
            self.status = AgentStatus.COMPLETED
            return mission.route_override, reasoning
        
        job_confirmed = bool(mission.job_description.get("title"))
        if job_confirmed:
            reasoning = "Node 2: Job application confirmed → INMAIL for maximum detail"
            self.status = AgentStatus.COMPLETED
            return Route.INMAIL, reasoning
        
        if mission.connection_status == "connected" and mission.prior_message_count > 0:
            reasoning = f"Node 3: Existing relationship ({mission.prior_message_count} prior messages) → FOLLOW_UP"
            self.status = AgentStatus.COMPLETED
            return Route.FOLLOW_UP, reasoning
        
        if mission.connection_status == "not_connected" and mission.prior_message_count == 0:
            reasoning = "Node 4: New recipient, no connection → CONNECTION_REQ"
            self.status = AgentStatus.COMPLETED
            return Route.CONNECTION_REQ, reasoning
        
        reasoning = "Node 5: Fallback to INMAIL for safety"
        self.status = AgentStatus.COMPLETED
        return Route.INMAIL, reasoning

# ============================================================================
# S4: SCAFFOLD AGENT
# ============================================================================

class ScaffoldAgent:
    """Generate message scaffold"""
    
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
        Create structural scaffold
        NEW v11.9: Context-aware CTA generation (SPEC 3)
        """
        self.status = AgentStatus.RUNNING
        
        constraints = CONFIG_REGISTRY.get_route_constraints(route, archetype)
        
        context_aware_cta = self._should_use_context_aware_cta(route, archetype)
        cta_required = self._is_cta_required(route, archetype)
        
        sections = {
            "greeting": {
                "required": True,
                "word_range": constraints.get("greeting_word_range", (2, 4))
            },
            "body": {
                "required": True,
                "min_words": constraints.get("body_min_words", 50)
            },
            "cta": {
                "required": cta_required,
                "word_range": constraints.get("cta_word_range", (5, 10)) if cta_required else (0, 0),
                "context_aware": context_aware_cta
            },
            "signature": {
                "required": True,
                "word_range": constraints.get("signature_word_range", (2, 4))
            }
        }
        
        self.status = AgentStatus.COMPLETED
        
        return MessageScaffold(
            route=route,
            archetype=archetype,
            sections=sections,
            constraints=constraints,
            context_aware_cta=context_aware_cta
        )
    
    def _should_use_context_aware_cta(self, route: Route, archetype: Archetype) -> bool:
        """NEW v11.9: Determine if context-aware CTA should be used"""
        if route == Route.CONNECTION_REQ:
            return False
        if archetype == Archetype.SENIOR_TA:
            return True
        return False
    
    def _is_cta_required(self, route: Route, archetype: Archetype) -> bool:
        """NEW v11.9: Determine if CTA is required"""
        if route == Route.CONNECTION_REQ:
            return False
        return True

# ============================================================================
# S5: GENERATION AGENT
# ============================================================================

class SelfConsistencySynthesizer:
    """
    NEW v11.7: N-candidate generation with synthesis for C_LEVEL archetype
    """
    
    def __init__(self):
        self.n_candidates = 3  # Generate 3 candidates for C_LEVEL
    
    async def synthesize_c_level_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate N candidates and synthesize the best elements
        """
        if scaffold.archetype != Archetype.C_LEVEL:
            raise ValueError("Self-consistency synthesis only for C_LEVEL")
        
        candidates = []
        for i in range(self.n_candidates):
            candidate = await self._generate_single_candidate(
                scaffold, context, profile_analysis, temperature + (i * 0.05)
            )
            candidates.append(candidate)
        
        synthesized = self._synthesize_candidates(candidates, context)
        return synthesized
    
    async def _generate_single_candidate(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """Generate a single candidate message (mocked)"""
        recipient_name = "Esteemed Executive"
        company = context.company_context[0] if context.company_context else "your organization"
        
        tone = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "message_tone")
        verbs = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "verb_preference")
        
        adversarial_constraints = ""
        if context.adversarial_findings:
            adversarial_constraints = f"\n\n[ADVERSARIAL_CHECK: AVOID CLAIMS: {', '.join(context.adversarial_findings)}]"
        
        content = f"Dear {recipient_name},\n\nI hope this finds you well. I'm reaching out regarding the strategic opportunity at {company}. Given your leadership in driving organizational transformation, I believe my background in AI/ML innovation could contribute meaningfully to your vision.\n\nI would welcome the chance to {verbs[0] if verbs else 'discuss'} how my experience aligns with {company}'s strategic objectives.\n\nRespectfully yours{adversarial_constraints}"
        
        return content
    
    def _synthesize_candidates(self, candidates: List[str], context: ResearchContext) -> str:
        """
        Synthesize the best elements from N candidates (mocked)
        """
        return max(candidates, key=len)


class GenerationOrchestrator:
    """
    NEW v11.10: Enhanced with S6->S2 failure classification (Enhancement 4)
    """
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
        self.status = AgentStatus.IDLE
        self.feasibility_checker = ConstraintFeasibilityChecker()
        self.temp_controller = AdaptiveTemperatureController()
        self.synthesizer = SelfConsistencySynthesizer()
    
    async def generate_message(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        validation_agent: 'validation.ValidationAgent'
    ) -> GeneratedMessage:
        """
        NEW v11.10: Generate with pre-flight, adaptive temp, and
        S6->S2 failure classification.
        """
        self.status = AgentStatus.RUNNING
        
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
        
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            
            temperature = self.temp_controller.get_temperature(
                "full_message",
                scaffold.archetype,
                attempt
            )
            
            content = await self._generate_content(
                scaffold,
                context,
                profile_analysis,
                temperature
            )
            
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
            
            validation_results = validation_agent.validate_message(message, context)
            
            critical_failures = [r for r in validation_results if not r.passed and r.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
            
            if not critical_failures:
                self.temp_controller.record_success("full_message", scaffold.archetype, temperature)
                self.status = AgentStatus.COMPLETED
                return message
            
            print(f"     S5: Generation attempt {attempt} failed validation...")
            failure_type, failure_report = self._classify_failure(critical_failures)

            if failure_type == FailureClassifier.FACTUAL_FAILURE:
                print(f"     S5 REASON: Factual failure detected. {failure_report}")
                print(f"     S5 ACTION: Halting generation retry. Triggering S6->S2 re-planning loop.")
                raise FactualGapError(critical_failures)
            else:
                print(f"     S5 REASON: Creative failure detected. {failure_report}")
                print(f"     S5 ACTION: Retrying with escalated temperature.")
        
        self.status = AgentStatus.FAILED
        raise ValueError(f"Failed to generate valid message after {max_attempts} creative attempts")

    def _classify_failure(self, failures: List[ValidationResult]) -> Tuple[FailureClassifier, str]:
        """
        NEW v11.10: Classify S6 failures to decide retry strategy.
        Checks both rule_id and error_code for robustness.
        """
        FACTUAL_RULES = {
            # Rule IDs
            "LIC-QA-106", # Per-claim confidence
            "LIC-QA-105", # Sender claims (hallucinated team)
            "LIC-QA-043", # Metric lacks context
            "LIC-QA-003", # Hallucinated claim (in case 106 fails)
            # Error Codes (from ErrorCodeRegistry)
            "LIC-E002",   # Per-claim confidence below threshold
            "LIC-E003",   # Hallucinated claim without evidence
            "LIC-E010",   # Metric lacks supporting keyword context
        }

        for f in failures:
            # Check both rule_id and error_code (if present in details)
            error_code = f.details.get("error_code") if f.details else None
            if f.rule_id in FACTUAL_RULES or error_code in FACTUAL_RULES:
                identifier = f.rule_id if f.rule_id in FACTUAL_RULES else error_code
                return FailureClassifier.FACTUAL_FAILURE, f"({identifier}) {f.message}"

        return FailureClassifier.CREATIVE_FAILURE, f"({failures[0].rule_id}) {failures[0].message}"


    async def _generate_content(
        self,
        scaffold: MessageScaffold,
        context: ResearchContext,
        profile_analysis: ProfileAnalysis,
        temperature: float
    ) -> str:
        """
        Generate message content (mocked)
        """
        if scaffold.archetype == Archetype.C_LEVEL:
            return await self.synthesizer.synthesize_c_level_message(
                scaffold, context, profile_analysis, temperature
            )
        
        recipient_name = "Valued Professional"
        company = context.company_context[0] if context.company_context else "your organization"
        
        tone = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "message_tone")
        verbs = CONFIG_REGISTRY.get_tone_mapping(scaffold.archetype, "verb_preference")

        adversarial_constraints = ""
        if context.adversarial_findings:
            adversarial_constraints = f"\n\n[ADVERSARIAL_CHECK: AVOID CLAIMS: {', '.join(context.adversarial_findings)}]"
        
        if scaffold.route == Route.CONNECTION_REQ:
            content = f"Hi {recipient_name}, I'm reaching out to {verbs[0] if verbs else 'connect'} regarding opportunities at {company}. Looking forward to connecting.{adversarial_constraints}"
        elif scaffold.route == Route.INMAIL:
            content = f"Dear {recipient_name},\n\nI hope this message finds you well. I'm writing to {verbs[0] if verbs else 'discuss'} the exciting opportunity at {company}. With my background in AI and machine learning, I believe I can contribute significantly to your team's goals.\n\nI'd appreciate the opportunity to {verbs[1] if len(verbs) > 1 else 'connect'} and learn more.\n\nBest regards{adversarial_constraints}"
        elif scaffold.route == Route.FOLLOW_UP:
            content = f"Hi {recipient_name}, Following up on our previous conversation about {company}. I remain very interested in the opportunity and would love to {verbs[0] if verbs else 'continue'} our discussion. Best regards{adversarial_constraints}"
        else:
            content = f"Dear {recipient_name}, Reaching out regarding {company}. Best regards{adversarial_constraints}"
        
        return content

# ============================================================================
# S7: QA AGENT
# ============================================================================

class QAAgent:
    """
    NEW v11.6: Enhanced QA report generation
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
        NEW v11.6: Generate comprehensive QA report grouped by severity (GAP 1.11)
        """
        self.status = AgentStatus.RUNNING
        
        critical_issues = sum(1 for r in validation_results if r.severity == ValidationSeverity.CRITICAL)
        high_issues = sum(1 for r in validation_results if r.severity == ValidationSeverity.HIGH)
        errors = sum(1 for r in validation_results if r.severity == ValidationSeverity.MEDIUM)
        warnings = sum(1 for r in validation_results if r.severity == ValidationSeverity.INFO)
        
        passed = critical_issues == 0 and high_issues == 0
        
        self.status = AgentStatus.COMPLETED
        
        return QAReport(
            mission_id=mission.mission_id,
            validation_results=validation_results,
            critical_issues=critical_issues,
            high_issues=high_issues,
            errors=errors,
            warnings=warnings,
            passed=passed,
            timestamp=datetime.now().isoformat()
        )

# ============================================================================
# S0: WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """
    NEW v11.10: Updated to manage the S6->S2 "Meta-Loop" (Enhancement 4)
    """
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        
        # Initialize agents
        self.profile_agent = ProfileAnalysisAgent(self.circuit_breaker)
        self.research_orchestrator = S2_SupervisorAgent(self.circuit_breaker)
        self.routing_agent = RoutingAgent(self.circuit_breaker)
        self.scaffold_agent = ScaffoldAgent(self.circuit_breaker)
        self.generation_orchestrator = GenerationOrchestrator(self.circuit_breaker)
        self.validation_agent = ValidationAgent(self.circuit_breaker)
        self.qa_agent = QAAgent(self.circuit_breaker)
        
        self.events: List[Dict[str, Any]] = []
    
    async def execute_workflow(self, mission: OutreachMission) -> Dict[str, Any]:
        """
        Execute complete workflow
        NEW v11.10: Now contains the S6->S2 "Meta-Loop" (Enhancement 4)
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
            # Stage 1: Profile Analysis (Runs once)
            print("\n[S1] Profile Analysis...")
            profile_analysis = self.profile_agent.analyze_profile(mission)
            print(f"     Archetype: {profile_analysis.archetype.value} (confidence: {profile_analysis.confidence:.2f})")
            
            if profile_analysis.needs_manual_override:
                print(f"\n     ⚠️  Low confidence ({profile_analysis.confidence:.2f}). Manual override recommended.")
                # Skipping interactive input for modularity
            
            corrected_profile_analysis = profile_analysis

            # ---
            # NEW v11.10: S6 -> S2 META-LOOP (Enhancement 4)
            # ---
            refinement_context_from_s6: List[ValidationResult] = None
            
            for meta_attempt in range(1, MAX_META_LOOPS + 1):
                print(f"\n{'='*40}")
                print(f"META-LOOP ATTEMPT {meta_attempt}/{MAX_META_LOOPS}")
                print(f"{'='*40}")

                try:
                    # Stage 2: Research (Re-runs on meta-loop)
                    print("\n[S2] Research Orchestration...")
                    context, corrected_profile_analysis = await self.research_orchestrator.conduct_research(
                        mission,
                        corrected_profile_analysis,
                        refinement_context=refinement_context_from_s6
                    )
                    
                    if corrected_profile_analysis.archetype != profile_analysis.archetype and meta_attempt == 1:
                        print(f"     ✨ Archetype corrected: {profile_analysis.archetype.value} → {corrected_profile_analysis.archetype.value}")
                        print(f"     Reason: {corrected_profile_analysis.critique_history[-1] if corrected_profile_analysis.critique_history else 'N/A'}")
                    
                    print(f"     RAG Results: {len(context.rag_results)}")
                    print(f"     Reflexion Iterations (Internal S2): {context.reflexion_iterations}")
                    print(f"     Prior Applications: {len(context.prior_applications)}")
                    if context.adversarial_findings:
                        print(f"     Adversarial Flags: {context.adversarial_findings}")
                    
                    # Stage 3: Routing (Re-runs on meta-loop)
                    print("\n[S3] Route Determination...")
                    route, routing_reasoning = self.routing_agent.determine_route(mission, corrected_profile_analysis)
                    print(f"     Route: {route.value}")
                    print(f"     Reasoning: {routing_reasoning}")
                    
                    # Stage 4: Scaffold (Re-runs on meta-loop)
                    print("\n[S4] Scaffold Creation...")
                    scaffold = self.scaffold_agent.create_scaffold(route, corrected_profile_analysis.archetype, context)
                    print(f"     Target Words: {CONFIG_REGISTRY.get_target_word_count(corrected_profile_analysis.archetype, route)}")
                    
                    # Stage 5+6: Generation with Validation Loop
                    print("\n[S5+S6] Generation with Validation...")
                    
                    message = await self.generation_orchestrator.generate_message(
                        scaffold,
                        context,
                        corrected_profile_analysis,
                        self.validation_agent
                    )
                    
                    print(f"     S5: Generation SUCCEEDED in meta-attempt {meta_attempt}.")
                    print(f"     Generated: {message.word_count} words in {message.generation_attempts} creative attempts")
                    break # SUCCESS! Exit the meta-loop.
                
                except FactualGapError as e:
                    print(f"\n     🔥 S6->S2 RE-PLANNING (Meta-Attempt {meta_attempt+1}) due to factual failure...")
                    refinement_context_from_s6 = e.args[0]
                    failure_msg = refinement_context_from_s6[0].message
                    print(f"     Failure Context: {failure_msg}")
                    
                    if meta_attempt == MAX_META_LOOPS:
                        print("     FATAL: Factual failure not resolved after max re-planning loops.")
                        raise Exception(f"Factual failure not resolved after {MAX_META_LOOPS} meta-loops: {failure_msg}")
                    
                    continue
            
            # ---
            # END S6 -> S2 META-LOOP
            # ---

            # Stage 7: Final QA Report
            print("\n[S7] QA Report Generation...")
            final_validation_results = self.validation_agent.validate_message(message, context)
            qa_report = self.qa_agent.generate_qa_report(mission, final_validation_results)
            print(f"     Critical: {qa_report.critical_issues}, High: {qa_report.high_issues}, Medium: {qa_report.errors}")
            
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
                    "warnings": qa_report.warnings,
                    "locked_sections_count": len(message.locked_sections),
                    "reflexion_cycles_used": context.reflexion_iterations,
                    "adaptive_retries_count": message.generation_attempts - 1
                },
                "qa_report": self._format_qa_report(qa_report)
            }
            
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
        NEW v11.6: Post-send tracking and app tracker generation (GAP 10.1, 10.2)
        (Modified for non-interactive execution)
        """
        print("\n" + "="*80)
        print("POST-SEND TRACKING (SIMULATED)")
        print("="*80)
        
        # Simulate 'Y' input
        sent = "Y"
        print("\nSimulating message sent: Y")
        
        if sent == "Y":
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
                    "checksum": message.checksum
                },
                "status": "sent",
                "follow_up_date": (datetime.now() + timedelta(days=3)).isoformat()
            }
            
            tracker_filename = f"tracker_{mission.mission_id}.json"
            print(f"\n✅ Application tracker data generated (would be saved as {tracker_filename}):")
            print(tracker)