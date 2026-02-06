from __future__ import annotations

"""
LicS2SupervisorAgent - Extracted for one-class-per-file pattern.

Originally from: campaign_rag.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, healer, memory, orchestrator, state, validator
# This boosts alignment detection — review and integrate appropriately

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class LicS2SupervisorAgent(SovereignBaseAgent):
    """
    v12.0: Updated coordination logic for strategic alignment workflow.
    Now manages entity extraction + validation flow.
    """

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Validate strategic alignment research workflow components.

        Checks that all sub-agents (LicInternalAgent, LicRecipientAgent,
        LicOrganizationAgent) are properly configured and operational.

        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes.
            depth: Current recursion depth for cycle detection.
            max_depth: Maximum recursion depth allowed.
            _call_path: Set of agent names in current call chain.

        Returns:
            Dict with violations_found, violations_fixed, errors, skipped.
        """
        super().heal_repository(**kwargs)

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 1,
                "skipped": 0,
                "cycle_detected": True,
            }
        if depth > max_depth:
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "errors": 0,
                "skipped": 1,
                "depth_limited": True,
            }
        _call_path.add(agent_name)

        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0

        try:
            # Validate sub-agent configurations
            sub_agents = [
                ("internal_agent", self.internal_agent),
                ("recipient_agent", self.recipient_agent),
                ("organization_agent", self.organization_agent),
            ]

            for _name, agent in sub_agents:
                if agent is None:
                    violations_found += 1
                elif not hasattr(agent, "circuit_breaker"):
                    violations_found += 1

            # Validate LLM client
            if self.llm_client is None:
                violations_found += 1

            # Validate scoring components
            if self.signal_scorer is None or self.claim_scorer is None:
                violations_found += 1

            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": errors,
                "skipped": skipped,
                "agent": agent_name,
                "dry_run": dry_run,
            }

        finally:
            _call_path.discard(agent_name)

    def __init__(
        self,
        circuit_breaker: CircuitBreaker,
        search_client: GoogleSearchClient,
        llm_client: GeminiLLMClient,
    ) -> None:
        self.circuit_breaker = circuit_breaker
        self.internal_agent = LicInternalAgent(circuit_breaker)
        self.recipient_agent = LicRecipientAgent(circuit_breaker, search_client)
        self.organization_agent = LicOrganizationAgent(circuit_breaker, search_client)
        self.llm_client = llm_client
        self.signal_scorer = SignalQualityScorer()
        self.claim_scorer = ClaimConfidenceScorer()
        self.rag_reflexion = RAGReflexionSystem()
        self.status = AgentStatus.IDLE

    async def orchestrate_research(
        self,
        mission: OutreachMission,
        profile_analysis: ProfileAnalysis,
        refinement_context: Optional[List] = None,
    ) -> Tuple[ResearchContext, ProfileAnalysis]:
        """
        v12.0: Orchestrate strategic alignment research.
        Flow:
        1. LicInternalAgent loads strategic brief + sender grounding
        2. Extract entities from strategic brief
        3. Validate entities with RecipientAgent/LicOrganizationAgent
        4. Run reflexion loop if needed
        """
        self.status = AgentStatus.RUNNING

        # Phase 1: Internal grounding (strategic brief + sender data)
        internal_report = self.internal_agent.get_internal_context(mission)
        rag_results = internal_report["rag_results"]
        prior_applications = internal_report["prior_applications"]
        brief_entities = internal_report.get("brief_entities", [])

        # Phase 2: Entity validation
        if brief_entities:
            staleness_warnings = []
            for entity in brief_entities[:5]:  # Validate up to 5 entities
                if entity["type"] == "person":
                    validation = await self.recipient_agent.validate_entity(
                        entity["name"], entity["context"], mission
                    )
                    rag_results.extend(validation["rag_results"])
                    if validation.get("staleness_warning"):
                        staleness_warnings.append(validation["staleness_warning"])
                elif entity["type"] == "initiative":
                    validation = await self.organization_agent.validate_initiative(entity["name"], mission)
                    rag_results.extend(validation["rag_results"])
                    if validation.get("staleness_warning"):
                        pass

        # Phase 3: Light supplemental RAG (minimal - strategic brief is primary)
        # Only run if no strategic brief found
        if not any(r.SourceType == "STRATEGIC_BRIEF" for r in rag_results):
            recipient_report = await self.recipient_agent.get_profile(mission)
            org_report = await self.organization_agent.get_organization_context(mission)
            rag_results.extend(recipient_report["rag_results"])
            rag_results.extend(org_report["rag_results"])

        # Phase 4: Reflexion loop (if triggered by S6 failure or critique)
        reflexion_iterations = 0
        while reflexion_iterations < 2:
            critique = self.rag_reflexion.critique_rag_sufficiency(
                rag_results, profile_analysis.Archetype, iteration=reflexion_iterations + 1
            )

            if refinement_context and reflexion_iterations == 0:
                failure_rule = refinement_context[0].rule_id
                failure_msg = refinement_context[0].message
                Task = f"S6 Validation Failed ({failure_rule}): {failure_msg}. Find new evidence to resolve this."
                critique.is_sufficient = False
                critique.refinement_tasks = [Task]

            if critique.is_sufficient:
                break

            reflexion_iterations += 1
            Task = critique.refinement_tasks[0]

            refinement_report = None
            if any(kw in Task.lower() for kw in ["recipient", "github", "linkedin"]):
                refinement_report = await self.recipient_agent.run_refinement_task(Task, mission)
            else:
                refinement_report = await self.organization_agent.run_refinement_task(Task, mission)

            rag_results.extend(refinement_report["rag_results"])

        # Phase 5: Extract sender grounding whitelists
        sender_grounding = self._extract_sender_grounding(rag_results, mission)

        # Phase 6: Build ResearchContext
        context = ResearchContext(
            recipient_insights=[
                f"Title: {mission.recipient_profile.get('title')}",
                f"Company: {mission.recipient_profile.get('company')}",
                f"Archetype: {profile_analysis.Archetype.value}",
            ],
            company_context=[
                f"Company: {mission.JobDescription.get('company')}",
                f"Job: {mission.JobDescription.get('title')}",
            ],
            recent_activity=[],
            rag_results=rag_results,
            reflexion_iterations=reflexion_iterations,
            prior_applications=prior_applications,
            mission_context={
                "job_title": mission.JobDescription.get("title", ""),
                "company": mission.JobDescription.get("company", ""),
                "sender_teams": mission.sender_profile.get("teams", []),
            },
            sender_context=[],
            sender_grounding=sender_grounding,
        )

        # Phase 7: Archetype critique
        # corrected_profile_analysis = self._critique_archetype_classification(
        # TODO: Fix incomplete function call
        corrected_profile_analysis = None  # Placeholder
        # Phase 8: Adversarial check
        adversarial_findings = await self._run_adversarial_check(context)
        context.adversarial_findings = adversarial_findings
        if adversarial_findings:
            pass

        self.status = AgentStatus.COMPLETED

        return context, corrected_profile_analysis

    async def _run_adversarial_check(self, context: ResearchContext) -> List[str]:
        # ... (rest of the code remains the same)

        rag_summary = "\n".join([f"- {r.SourceType}: {r.text[:100]}..." for r in context.rag_results[:10]])

        critique_prompt = f"""You are an adversarial reviewer. Review the following research findings and identify any weak or unsupported claims:

{rag_summary}

List any findings that appear:
1. Tangential or loosely connected to the core message
2. Overly generic without specific evidence
3. Could be refuted with minimal scrutiny

Return a numbered list of weaknesses (max 3). Format: "1. [weakness]"
"""

        loop = asyncio.get_event_loop()
        try:
            findings_text = await loop.run_in_executor(None, self.llm_client.generate, critique_prompt)

            findings = [f.strip() for f in findings_text.split("\n") if f.strip() and len(f.strip()) > 10]

            return findings[:3]

        except Exception:
            return []

    def _extract_sender_grounding(
        self, rag_results: List[RAGResult], mission: OutreachMission
    ) -> SenderGroundingWhitelists:
        """Extract sender grounding whitelists from RAG."""
        grounding = SenderGroundingWhitelists()

        for result in rag_results:
            text_lower = result.text.lower()

            if any(
                marker in text_lower for marker in ["team member", "colleague", "worked with", "collaborator"]
            ):
                names = self._extract_names_from_text(result.text)
                grounding.team_members.extend(names)
                if names:
                    grounding.raw_evidence["team_members"] = grounding.raw_evidence.get(
                        "team_members", []
                    ) + [result.text[:200]]

            if any(marker in text_lower for marker in ["product", "platform", "solution", "service"]):
                products = self._extract_capitalized_phrases(result.text)
                grounding.products.extend(products)
                if products:
                    grounding.raw_evidence["products"] = grounding.raw_evidence.get("products", []) + [
                        result.text[:200]
                    ]

            if any(marker in text_lower for marker in ["client", "customer", "case study", "project for"]):
                cases = self._extract_capitalized_phrases(result.text)
                grounding.case_studies.extend(cases)
                if cases:
                    grounding.raw_evidence["case_studies"] = grounding.raw_evidence.get(
                        "case_studies", []
                    ) + [result.text[:200]]

        grounding.team_members = list(set(grounding.team_members))
        grounding.products = list(set(grounding.products))
        grounding.case_studies = list(set(grounding.case_studies))

        return grounding

    def _extract_names_from_text(self, text: str) -> List[str]:
        """Extract person names from text."""
        words = text.split()
        names = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    full_name = f"{word} {words[i + 1]}"
                    names.append(full_name)
        return names

    def _extract_capitalized_phrases(self, text: str) -> List[str]:
        """Extract capitalized phrases."""
        words = text.split()
        phrases = []
        current_phrase = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                current_phrase.append(word)
            else:
                if len(current_phrase) >= 2:
                    phrases.append(" ".join(current_phrase))
                current_phrase = []
        if len(current_phrase) >= 2:
            phrases.append(" ".join(current_phrase))
        return phrases

    def _critique_archetype_classification(
        self, provisional_analysis: ProfileAnalysis, context: ResearchContext
    ) -> ProfileAnalysis:
        """Agentic self-correction of Archetype classification."""
        all_text = " ".join([r.text for r in context.rag_results]).lower()

        if provisional_analysis.Archetype != Archetype.C_LEVEL:
            if any(term in all_text for term in ["strategic vision", "board member", "company direction"]):
                critique = "RAG evidence suggests C_LEVEL status (strategic indicators)"
                provisional_analysis.Archetype = Archetype.C_LEVEL
                provisional_analysis.confidence = 0.90
                provisional_analysis.critique_history.append(critique)

        if provisional_analysis.Archetype != Archetype.RECRUITER:
            if any(term in all_text for term in ["talent acquisition", "hiring manager", "recruitment"]):
                critique = "RAG evidence suggests RECRUITER role (hiring indicators)"
                provisional_analysis.Archetype = Archetype.RECRUITER
                provisional_analysis.confidence = 0.88
                provisional_analysis.critique_history.append(critique)

        return provisional_analysis

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by LicS2SupervisorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - LicS2SupervisorAgent supervises LIC S2 compliance
        try:
            return {
                "status": "skipped",
                "details": f"LicS2SupervisorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"LicS2SupervisorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
