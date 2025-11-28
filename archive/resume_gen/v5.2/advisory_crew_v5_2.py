# File: advisory_crew_v5_2.py
# Version: 5.2 Standard (Full Validation Engine Integration)
# Advisory Crew - Orchestration layer maintaining v5.1 architecture
# Integrates with v3.8-enhanced execution specialists

import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Import enhanced execution specialists
from execution_specialists_v5_2 import (
    Library_Specialist,
    Web_Specialist,
    RAG_Synthesizer,
    Content_Generator,
    Gemini_Drafter,
    Claude_Drafter,
    Muse_Drafter,
    ChiefStrategistAgent,
    StrategyValidatorAgent,
    RetryPolicyAgent,
    Meta_Planner,
    HIL_Feedback_Logger,
    HIL_EscalationAgent,
    PromptSelectorAgent,
    ContextAssemblerAgent,
    PromptFormatterAgent,
    Mechanical_Critic,
    Strategic_Critic,
    FactualConsistency_Validator,
    ToneValidator,
    ThematicAlignment_Validator,
    PreFlightValidator,
    Resume_Assembler,
    CoverLetter_Assembler,
    AppTracker_Assembler,
    Auditor_Agent,
)

# Import v3.8 models and utilities
from prompts_RES import build_crl_context_for_section
from models_RES import (
    ImmutableStagingBuffer, ThematicAnalysis, ValidationResult,
    MasterResumeIndex, CompetitiveAnalysisConfig,
    ResumeSection, GovernanceState, AgentSignal, VetoRecord, ExecutionStrategy,
    ValidationSeverity, GateDecision
)
from validation_context import ValidationContext
from config_RES import CONFIG

logger = logging.getLogger(__name__)


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
    # Governor-specific state tracking
    execution_strategy: Optional[ExecutionStrategy] = None
    state: GovernanceState = GovernanceState.INIT
    veto_log: List[VetoRecord] = field(default_factory=list)


class Governor:
    """
    🧑‍✈️ The Governor (formerly AdvisoryCrew).
    Centralized complex autonomous agent that manages the swarm.
    Implements the 'Main Swarm' control flow from the diagram.
    """
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        """Initialize the Governor and the entire agent swarm."""
        self.config = config or CrewConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize all specialists with complexity ratings
        self._initialize_specialists()
        
        self.logger.info(f"🧑‍✈️ Governor initialized with {self._count_specialists()} specialists")
    
    def _initialize_specialists(self):
        """Initialize all specialist agents."""
        # Meta-Loop Agents
        self.meta_planner = Meta_Planner()
        self.hil_logger = HIL_Feedback_Logger()
        self.retry_policy = RetryPolicyAgent(complexity=90)
        
        # Strategy & Governance
        self.chief_strategist = ChiefStrategistAgent(complexity=90)
        self.strategy_validator = StrategyValidatorAgent(complexity=95)
        
        # RAG & Research
        self.library_specialist = Library_Specialist(complexity=50)
        self.web_specialist = Web_Specialist(complexity=60)
        self.rag_synthesizer = RAG_Synthesizer(complexity=70)
        
        # Drafting Swarm
        self.gemini_drafter = Gemini_Drafter(complexity=30)
        self.claude_drafter = Claude_Drafter(complexity=30)
        self.muse_drafter = Muse_Drafter(complexity=30)
        
        # Prompting Stack
        self.prompt_selector = PromptSelectorAgent(complexity=60)
        self.context_assembler = ContextAssemblerAgent(complexity=60)
        self.prompt_formatter = PromptFormatterAgent(complexity=60)

        # Validation & Critics
        self.factual_validator = FactualConsistency_Validator(complexity=40)
        self.tone_validator = ToneValidator(complexity=30)
        self.thematic_validator = ThematicAlignment_Validator(complexity=35)
        self.validator = None # Initialized later with full context
        self.mechanical_critic = Mechanical_Critic(complexity=60)
        self.strategic_critic = Strategic_Critic(complexity=65)
        
        # Assembly specialists
        self.resume_assembler = Resume_Assembler(complexity=25)
        self.cover_letter_assembler = CoverLetter_Assembler(complexity=20)
        self.app_tracker_assembler = AppTracker_Assembler(complexity=15)
        
        # Audit & HIL
        self.auditor = Auditor_Agent(complexity=30)
        self.hil_escalation = HIL_EscalationAgent(complexity=60)
    
    def _count_specialists(self) -> int:
        """Count initialized specialists."""
        return len([
            attr for attr in dir(self)
            if not attr.startswith('_') and (hasattr(getattr(self, attr), 'complexity') or hasattr(getattr(self, attr), 'log_path'))
        ])
    
    def execute_workflow(self, context: CrewContext) -> Dict[str, Any]:
        """
        Executes the autonomous Governor control loop.
        Flow: INIT -> META_LEARNING -> STRATEGY -> EXECUTION_LOOP -> (VETO/HIL) -> FINALIZING -> COMPLETED
        """
        self.logger.info("=" * 80)
        self.logger.info("🧑‍✈️ Governor: Starting Autonomous Workflow")
        self.logger.info("=" * 80)
        
        workflow_results = {'status': 'STARTED', 'start_time': datetime.now().isoformat(), 'phases': {}}
        context.state = GovernanceState.INIT

        # Initialize Full Validation Engine with context
        self.validator = PreFlightValidator(context.master_resume, CONFIG)
        self.logger.info("✅ Governor: Validation Engine online.")
        
        while context.state not in [GovernanceState.COMPLETED, GovernanceState.FAILED]:
            try:
                if context.state == GovernanceState.INIT:
                    self.logger.info("State: INIT -> RAG")
                    workflow_results['phases']['rag'] = self._execute_rag_phase(context)
                    context.state = GovernanceState.META_LEARNING

                elif context.state == GovernanceState.META_LEARNING:
                    # ♾️ Asynchronous Meta-Learning Loop (simplified synchronous call)
                    self.meta_planner.update_rules()
                    context.state = GovernanceState.STRATEGY_SELECTION

                elif context.state == GovernanceState.STRATEGY_SELECTION:
                     # 🧑‍🔬 Chief Strategist & 🧠 Strategy Validator
                     strategy = self.chief_strategist.develop_strategy(context.thematic_analysis)
                     if self.strategy_validator.validate_strategy(strategy):
                         context.execution_strategy = strategy
                         self.logger.info(f"Strategy Selected: {strategy.name}")
                         context.state = GovernanceState.EXECUTION_LOOP
                     else:
                         raise Exception("Strategy VETOED by Validator")

                elif context.state == GovernanceState.EXECUTION_LOOP:
                    self.logger.info("State: EXECUTION_LOOP -> Commanding Swarm")
                    # This is the main generation loop
                    gen_results = self._execute_generation_phase(context)
                    if gen_results['status'] == 'COMPLETED':
                         context.state = GovernanceState.FINALIZING
                    elif gen_results['status'] == 'VETOED':
                         context.state = GovernanceState.VETO_HANDLING
                    else:
                         context.state = GovernanceState.FAILED
                    workflow_results['phases']['generation'] = gen_results

                elif context.state == GovernanceState.VETO_HANDLING:
                    self.logger.warning("State: VETO_HANDLING")
                    # 🤔 RetryPolicyAgent determines next step
                    last_veto = context.veto_log[-1] if context.veto_log else None
                    if last_veto:
                        decision = self.retry_policy.determine_strategy(last_veto, attempt=1)
                        if decision == "ESCALATE":
                            context.state = GovernanceState.HIL_ESCALATION
                        else:
                            self.logger.info(f"Retry Policy: {decision}. Re-entering execution loop.")
                            context.state = GovernanceState.EXECUTION_LOOP

                elif context.state == GovernanceState.HIL_ESCALATION:
                    self.hil_escalation.escalate(asdict(context), "Max retries exceeded")
                    context.state = GovernanceState.FAILED # Stop for now

                elif context.state == GovernanceState.FINALIZING:
                    self.logger.info("State: FINALIZING -> Assembly & Audit")
                    workflow_results['phases']['assembly'] = self._execute_assembly_phase(context)
                    workflow_results['phases']['audit'] = self._execute_audit_phase(context)
                    context.state = GovernanceState.COMPLETED

            except Exception as e:
                self.logger.error(f"Governor crashed in state {context.state.name}: {e}", exc_info=True)
                context.state = GovernanceState.FAILED
                workflow_results['error'] = str(e)
        
        workflow_results['status'] = context.state.name
        workflow_results['end_time'] = datetime.now().isoformat()
        return workflow_results
    
    def _execute_rag_phase(self, context: CrewContext) -> Dict[str, Any]:
        """Execute RAG analysis phase using enhanced specialists."""
        phase_results = {'status': 'STARTED'}
        
        try:
            # Create master resume index (Populated from context)
            master_index = MasterResumeIndex(
                skill_to_experiences={s: [] for s in context.master_resume.get('skills', [])},
                achievement_catalog=context.master_resume.get('professional_experience', []),
                domain_vocabularies={},
                recency_scores={}
            )
            
            # Create competitive config
            comp_config = CompetitiveAnalysisConfig(
                enabled=True,
                min_peer_jds=3
            )
            
            # Execute RAG analysis
            thematic_analysis = self.rag_synthesizer.analyze_job_description(
                job_description=context.job_description,
                company_name=context.company_name,
                job_title=context.job_title,
                master_resume_index=master_index,
                comp_config=comp_config
            )
            
            context.thematic_analysis = thematic_analysis
            
            phase_results['status'] = 'COMPLETED'
            phase_results['signal_quality'] = thematic_analysis.signal_quality_score
            phase_results['primary_theme'] = thematic_analysis.primary_theme
            
        except Exception as e:
            phase_results['status'] = 'FAILED'
            phase_results['error'] = str(e)
            self.logger.error(f"RAG phase failed: {e}")
        
        return phase_results
    
    def _execute_generation_phase(self, context: CrewContext) -> Dict[str, Any]:
        """
        Governor's main execution loop for content generation.
        Commands Drafting Specialists and handles immediate VETO signals.
        """
        phase_results = {'status': 'STARTED'}
        max_retries = context.execution_strategy.max_retries_per_node if context.execution_strategy else 2
        
        try:
            # 1. Define generation plan (which sections to generate)
            generation_plan = [
                ResumeSection.K0_HEADLINE,
                ResumeSection.K1_EXECUTIVE_SUMMARY,
                ResumeSection.K9_COMPETENCIES,
            ]
            
            staging_data = {}
            
            # 2. Governor Loop for each section
            for section in generation_plan:
                self.logger.info(f"Governor: Initiating generation loop for {section.name}")
                current_draft = ""
                signal = AgentSignal.RETRY
                attempts = 0

                while signal == AgentSignal.RETRY and attempts <= max_retries:
                    attempts += 1
                    # A. Command Prompting Stack
                    crl_context = self._build_generation_context(section, context, staging_data)
                    
                    # B. Command Drafting Specialist (using Gemini_Drafter as default)
                    current_draft = self.gemini_drafter.generate_section(section, crl_context, attempts)
                    
                    # B. Tentatively stage for validation
                    temp_staging = staging_data.copy()
                    temp_staging[section.value] = current_draft
                    
                    # C. Consult Validation Engine (Full 30+ Rule Check)
                    temp_buffer = ImmutableStagingBuffer()
                    for k, v in temp_staging.items(): temp_buffer.set(k, v)
                    temp_buffer.lock()

                    # Execute validation only for the current section
                    val_results, gate_decision, _ = self.validator.validate(
                        staging_buffer=temp_buffer,
                        thematic_analysis=context.thematic_analysis,
                        job_description=context.job_description,
                        sections_under_test={section}
                    )
                    
                    if gate_decision == GateDecision.PROCEED:
                        signal = AgentSignal.PASS
                        self.logger.info(f"✅ {section.name} passed validation.")
                    else:
                        signal = AgentSignal.VETO
                        # Find primary failure for the log
                        primary_fail = next((r for r in val_results if not r.passed and r.severity.value >= ValidationSeverity.HIGH.value), None)
                        fail_msg = primary_fail.message if primary_fail else "Validation Failed"
                        
                        veto = VetoRecord("PreFlightValidator", section.name, fail_msg, ValidationSeverity.HIGH, "Regenerate")
                        context.veto_log.append(veto)
                        self.hil_logger.log_veto(veto, {'section': section.name, 'failures': [r.message for r in val_results if not r.passed]})
                        
                        # Ask Policy Agent what to do
                        policy = self.retry_policy.determine_strategy(veto, attempts)
                        if policy == "ESCALATE":
                            return {'status': 'VETOED', 'veto_details': veto}
                        else:
                             signal = AgentSignal.RETRY # Loop again

                if signal == AgentSignal.PASS:
                     staging_data[section.value] = current_draft
                else:
                     self.logger.warning(f"Governor: {section.name} failed all {max_retries} attempts. Proceeding with suboptimal draft.")
                     staging_data[section.value] = current_draft

            # Finalize staging buffer
            context.staging_buffer = ImmutableStagingBuffer()
            for key, value in staging_data.items():
                context.staging_buffer.set(key, value)
            context.staging_buffer.lock()
            
            phase_results['status'] = 'COMPLETED'
            phase_results['sections_generated'] = len(generation_plan)
            
        except Exception as e:
            phase_results['status'] = 'FAILED'
            phase_results['error'] = str(e)
            self.logger.error(f"Generation phase failed: {e}")
        
        return phase_results

    def _build_generation_context(self, section: ResumeSection, context: CrewContext, current_staging: Dict) -> Dict[str, Any]:
        """Uses ContextAssemblerAgent to build prompt context."""
        # Use the v3.8 CRL builder if available, otherwise manual map
        try:
            return build_crl_context_for_section(
                section.name,
                context.thematic_analysis,
                {'experience_sections': []}, # Scaffold stub
                context.master_resume,
                CONFIG
            )
        except Exception as e:
            self.logger.warning(f"CRL builder failed, using fallback: {e}")
            # Fallback to manual context
            return {
                "job_description": context.job_description[:1000],
                "company": context.company_name,
                "title": context.job_title,
                "thematic": str(context.thematic_analysis)[:1000],
                "master_context": str(context.master_resume)[:2000]
            }
    
    def _execute_assembly_phase(self, context: CrewContext) -> Dict[str, Any]:
        """Execute assembly phase to create final artifacts."""
        phase_results = {'status': 'STARTED', 'artifacts': {}}
        
        try:
            # Assemble resume
            resume_content, resume_filename = self.resume_assembler.assemble_resume(
                context.staging_buffer,
                context.company_name,
                context.job_title
            )
            phase_results['artifacts']['resume'] = {
                'filename': resume_filename,
                'size': len(resume_content),
                'sections': resume_content.count('##')
            }
            context.artifacts['resume'] = resume_content
            
            # Assemble cover letter
            cover_letter_content, cover_letter_filename = self.cover_letter_assembler.assemble_cover_letter(
                context.staging_buffer,
                context.company_name,
                context.job_title
            )
            phase_results['artifacts']['cover_letter'] = {
                'filename': cover_letter_filename,
                'size': len(cover_letter_content)
            }
            context.artifacts['cover_letter'] = cover_letter_content
            
            # Create app tracker entry
            tracker_entry = self.app_tracker_assembler.assemble_tracker_entry(
                context.staging_buffer,
                context.company_name,
                context.job_title,
                jd_url="",
                status="Ready"
            )
            phase_results['artifacts']['tracker'] = tracker_entry
            context.artifacts['tracker'] = tracker_entry
            
            phase_results['status'] = 'COMPLETED'
            phase_results['total_artifacts'] = len(phase_results['artifacts'])
            
        except Exception as e:
            phase_results['status'] = 'FAILED'
            phase_results['error'] = str(e)
            self.logger.error(f"Assembly phase failed: {e}")
        
        return phase_results
    
    def _execute_audit_phase(self, context: CrewContext) -> Dict[str, Any]:
        """Execute quality audit phase."""
        phase_results = {'status': 'STARTED'}
        
        try:
            # Generate QA report
            qa_report = self.auditor.generate_qa_report(
                staging_buffer=context.staging_buffer,
                validation_results=context.validation_results,
                thematic_analysis=context.thematic_analysis
            )
            
            phase_results['status'] = 'COMPLETED'
            phase_results['report_size'] = len(qa_report)
            phase_results['sections'] = qa_report.count('##')
            
            context.artifacts['qa_report'] = qa_report
            
            # Extract key metrics from report
            if 'PASS' in qa_report[:100]:
                phase_results['overall_status'] = 'PASS'
            else:
                phase_results['overall_status'] = 'FAIL'
            
        except Exception as e:
            phase_results['status'] = 'FAILED'
            phase_results['error'] = str(e)
            self.logger.error(f"Audit phase failed: {e}")
        
        return phase_results
    
    def _generate_sample_cover_letter(self, context: CrewContext) -> str:
        """Generate a sample cover letter for testing."""
        today = datetime.now().strftime("%B %d, %Y")
        
        return f"""{today}

Hiring Manager
{context.company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {context.job_title} position at {context.company_name}.

With extensive experience in technology leadership and a proven track record of delivering innovative solutions, 
I am excited about the opportunity to contribute to your team's success.

My background aligns well with your requirements, particularly in areas of strategic planning, 
technical architecture, and team leadership. I have successfully led cross-functional teams 
in delivering complex projects on time and within budget.

I would welcome the opportunity to discuss how my experience and skills can contribute to 
{context.company_name}'s continued growth and success. Thank you for considering my application.

Sincerely,

[Candidate Name]"""
    
    def _extract_jd_keywords(self, job_description: str) -> List[str]:
        """Extract keywords from job description."""
        # Simple keyword extraction
        tech_keywords = ['python', 'java', 'aws', 'docker', 'kubernetes', 
                        'machine learning', 'ai', 'cloud', 'agile', 'devops']
        
        jd_lower = job_description.lower()
        found_keywords = [kw for kw in tech_keywords if kw in jd_lower]
        
        return found_keywords


# Alias for backward compatibility if needed, but Governor is preferred
AdvisoryCrew = Governor


class CrewOrchestrator:
    """
    High-level orchestrator for managing multiple crew operations.
    Supports batch processing and parallel execution.
    """
    
    def __init__(self, config: Optional[CrewConfiguration] = None):
        """Initialize crew orchestrator."""
        self.config = config or CrewConfiguration()
        self.crew = Governor(config=self.config)
        self.logger = logging.getLogger(__name__)
    
    def process_job_application(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        master_resume: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single job application through the crew workflow.
        """
        self.logger.info(f"Processing application: {company_name} - {job_title}")
        
        # Create context
        context = CrewContext(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            master_resume=master_resume
        )
        
        # Execute workflow
        results = self.crew.execute_workflow(context)
        
        # Package results
        return {
            'workflow_results': results,
            'artifacts': context.artifacts,
            'validation_results': context.validation_results,
            'thematic_analysis': context.thematic_analysis,
            'metadata': {
                'company': company_name,
                'position': job_title,
                'timestamp': datetime.now().isoformat(),
                'version': 'v5.2'
            }
        }
    
    def process_batch(
        self,
        applications: List[Dict[str, Any]],
        parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple job applications.
        """
        results = []
        
        for app in applications:
            try:
                result = self.process_job_application(
                    job_description=app['job_description'],
                    company_name=app['company_name'],
                    job_title=app['job_title'],
                    master_resume=app['master_resume']
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {app['company_name']}: {e}")
                results.append({
                    'error': str(e),
                    'company': app['company_name'],
                    'status': 'FAILED'
                })
        
        return results


# Export main classes
__all__ = [
    'Governor',
    'AdvisoryCrew',
    'CrewOrchestrator',
    'CrewConfiguration',
    'CrewContext'
]
