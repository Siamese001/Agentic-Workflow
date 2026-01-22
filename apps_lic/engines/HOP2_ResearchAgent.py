# File: workflow_LIC.py
# Description: Complete workflow orchestration v13.0 - Pure Agentic Architecture
# REFACTOR: All v12.0 agents replaced with HOP-based state architecture

__version__ = "13.0"

import asyncio
import json
import os
from datetime import datetime


# Models

# Core infrastructure

# ============================================================================
# HOP-2: RESEARCH AGENT (Refactored from S2_SupervisorAgent)
# ============================================================================


class HOP2_ResearchAgent:
    """
    v13.0: Research Agent - Vector-store-first with fallback RAG

    BREAKING CHANGE from v12.0:
    - OLD: All research at runtime (60-80s)
    - NEW: Query vector store first (<1s), fallback RAG only for gaps

    Single Responsibility: Synthesize research context

    Input:  state/1_profile_analysis.json
    Output: state/2_research_context.json
    """

    def __init__(
        self,
        config: dict[str, Any],
        memory_store: VectorMemoryStore,
        search_client: GoogleSearchClient,
        llm_client: GeminiLLMClient,
    ):
        """
        Initialize with externalized config and live API clients

        Args:
            config: Loaded from config/agent_specs_LIC.json
            memory_store: Pre-populated vector database
            search_client: Google Search API client (fallback only)
            llm_client: Gemini LLM client
        """
        self.config = config["research_agent"]
        self.memory_store = memory_store
        self.search_client = search_client
        self.llm_client = llm_client

        self.vector_params = self.config["vector_store_query_params"]
        self.fallback_params = self.config["fallback_rag_params"]
        self.critique_params = self.config["cache_critique_params"]

    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-2: Research synthesis with vector-first strategy

        Args:
            state_mgr: State manager for this mission

        Returns:
            Path to output state file
        """
        print(f"\n{'=' * 80}")
        print("HOP-2: RESEARCH AGENT (Vector-Store-First)")
        print(f"{'=' * 80}\n")

        # Read HOP-1 state
        profile_state = state_mgr.read_state("HOP-1")
        company = profile_state["recipient_company"]
        recipient = profile_state["recipient_name"]
        archetype = profile_state["archetype"]

        # STEP 1: Query vector store (fast, pre-computed)
        print("STEP 1: Querying vector store (cached intelligence)...")
        cached_context = await self._query_vector_store(company, recipient, archetype)
        print(f"  ✓ Retrieved {len(cached_context['all_results'])} cached documents")

        # STEP 2: Run cache critique
        print("\nSTEP 2: Evaluating cache quality...")
        is_sufficient, gaps = self._critique_cache(cached_context)

        if is_sufficient:
            print(f"  ✓ Cache is sufficient (confidence: {cached_context['cache_confidence']:.2f})")
            final_context = cached_context
        else:
            print(f"  ⚠ Cache has gaps: {gaps}")
            print("\nSTEP 3: Running fallback RAG to fill gaps...")

            # STEP 3: Fallback RAG (only if needed)
            fallback_context = await self._run_fallback_rag(company, recipient, gaps)
            print(f"  ✓ Retrieved {len(fallback_context['rag_results'])} additional sources")

            # Merge contexts
            final_context = self._merge_contexts(cached_context, fallback_context)

        # Prepare output state
        output_state = {
            "recipient_insights": final_context["recipient_insights"],
            "company_context": final_context["company_context"],
            "strategic_brief": final_context["strategic_brief"],
            "rag_results": final_context["all_results"],
            "signal_score": final_context["signal_score"],
            "cache_hit": is_sufficient,
            "fallback_used": not is_sufficient,
            "total_sources": len(final_context["all_results"]),
        }

        # Write to state
        output_path = state_mgr.write_state("HOP-2", output_state)

        print("\n✓ Research Complete")
        print(f"  Total sources: {output_state['total_sources']}")
        print(f"  Signal score: {output_state['signal_score']:.2f}")
        print(f"  Cache hit: {output_state['cache_hit']}\n")

        return output_path

    async def _query_vector_store(
        self, company: str, recipient: str, archetype: str
    ) -> dict[str, Any]:
        """Query vector store for pre-computed intelligence"""

        # Query by company
        company_results = self.memory_store.query_by_company(
            company_name=company,
            query_text="strategic priorities initiatives roadmap platform",
            n_results=self.vector_params["n_results"],
        )

        # Query by executive
        exec_results = self.memory_store.query_by_executive(
            executive_name=recipient,
            query_text="recent posts presentations LinkedIn about background",
            n_results=10,
        )

        # Get strategic briefs (highest priority)
        strategic_briefs = self.memory_store.get_strategic_briefs(
            company_name=company, max_age_days=90
        )

        # Extract insights
        recipient_insights = [r["text"][:200] for r in exec_results[:5]]
        company_context = [r["text"][:200] for r in company_results[:5]]
        strategic_brief_text = "\n".join([s["text"] for s in strategic_briefs])

        # Calculate signal score
        all_results = company_results + exec_results + strategic_briefs
        signal_score = self._calculate_signal_score(all_results)

        # Cache confidence
        cache_confidence = self._calculate_cache_confidence(
            company_results, exec_results, strategic_briefs
        )

        return {
            "recipient_insights": recipient_insights,
            "company_context": company_context,
            "strategic_brief": strategic_brief_text,
            "all_results": all_results,
            "signal_score": signal_score,
            "cache_confidence": cache_confidence,
        }

    def _critique_cache(self, cached_context: dict[str, Any]) -> tuple[bool, list[str]]:
        """Evaluate if cached context is sufficient"""

        min_confidence = self.critique_params["min_confidence_score"]
        min_recency = self.critique_params["min_recency_days"]
        min_recipient_count = self.critique_params["min_recipient_specific_count"]

        gaps = []

        # Check strategic brief
        has_strategic_brief = len(cached_context["strategic_brief"]) > 100
        if not has_strategic_brief:
            gaps.append("strategic_brief")

        # Check recency
        recent_sources = [
            r
            for r in cached_context["all_results"]
            if r.get("metadata", {}).get("age_days", 999) < min_recency
        ]
        has_recent = len(recent_sources) >= 3
        if not has_recent:
            gaps.append("recent_news")

        # Check recipient-specific data
        has_recipient_data = len(cached_context["recipient_insights"]) >= min_recipient_count
        if not has_recipient_data:
            gaps.append("recipient_profile")

        # Check overall confidence
        confidence_ok = cached_context["cache_confidence"] >= min_confidence
        if not confidence_ok:
            gaps.append("low_confidence")

        is_sufficient = len(gaps) == 0

        return is_sufficient, gaps

    async def _run_fallback_rag(
        self, company: str, recipient: str, gaps: list[str]
    ) -> dict[str, Any]:
        """Run fallback RAG only for identified gaps"""

        fallback_results = []

        for gap in gaps:
            if gap == "strategic_brief":
                query = f"{company} strategic priorities 2025 roadmap"
                results = self.search_client.search(query, num_results=3)
                fallback_results.extend(self._format_search_results(results, "STRATEGIC_BRIEF"))

            elif gap == "recent_news":
                query = f"{company} recent news announcements"
                results = self.search_client.search(query, num_results=3)
                fallback_results.extend(
                    self._format_search_results(results, "NEWS_ARTICLE_COMPANY")
                )

            elif gap == "recipient_profile":
                query = f"{recipient} {company} LinkedIn profile"
                results = self.search_client.search(query, num_results=2)
                fallback_results.extend(
                    self._format_search_results(results, "RECIPIENT_LINKEDIN_ABOUT")
                )

            # Rate limit
            await asyncio.sleep(1)

        return {"rag_results": fallback_results}

    def _merge_contexts(self, cached: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
        """Merge cached and fallback contexts"""

        merged = cached.copy()
        merged["all_results"].extend(fallback.get("rag_results", []))

        # Recalculate signal score
        merged["signal_score"] = self._calculate_signal_score(merged["all_results"])

        return merged

    def _calculate_signal_score(self, results: list[dict[str, Any]]) -> float:
        """Calculate aggregate signal quality score"""
        if not results:
            return 0.0

        # Simple average of source weights
        scores = [r.get("metadata", {}).get("source_weight", 0.5) for r in results]
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_cache_confidence(
        self, company_results: list[dict], exec_results: list[dict], strategic_briefs: list[dict]
    ) -> float:
        """Calculate confidence in cached data"""

        # Weighted score
        has_strategic = 1.0 if strategic_briefs else 0.0
        has_company = min(1.0, len(company_results) / 10)
        has_exec = min(1.0, len(exec_results) / 5)

        confidence = has_strategic * 0.5 + has_company * 0.3 + has_exec * 0.2

        return confidence

    def _format_search_results(self, results: list[dict], source_type: str) -> list[dict[str, Any]]:
        """Format search results for consistency"""

        formatted = []
        for result in results:
            formatted.append(
                {
                    "text": result.get("snippet", ""),
                    "metadata": {
                        "source_type": source_type,
                        "source_url": result.get("link", ""),
                        "title": result.get("title", ""),
                        "age_days": 0,
                        "source_weight": 1.0,
                    },
                }
            )

        return formatted


# ============================================================================
# HOP-5: GENERATION AGENT (Refactored from GenerationOrchestrator)
# ============================================================================


class HOP5_GenerationAgent:
    """
    v13.0: Generation Agent - N-candidate generation only

    BREAKING CHANGE from v12.0:
    - OLD: Generation + validation + retry logic all in one
    - NEW: Only generates N candidates, writes to state
    - Validation moved to HOP-6
    - Retry decision moved to HOP-7

    Single Responsibility: Generate message candidates

    Input:  state/2_research_context.json, state/3_sender_grounding.json, state/4.5_scaffold.json
    Output: state/5_generated_drafts.json
    """

    def __init__(
        self, config: dict[str, Any], llm_client: GeminiLLMClient, tool: CodeInterpreterTool
    ):
        """
        Initialize with externalized config

        Args:
            config: Loaded from config/agent_specs_LIC.json
            llm_client: Gemini LLM client
            tool: Code interpreter for fast scoring
        """
        self.config = config["generation_agent"]
        self.llm_client = llm_client
        self.tool = tool

        # Load prompts from config
        with open("config/prompts_LIC.json") as f:
            self.prompts = json.load(f)

    async def execute(self, state_mgr: StateManager, temperature: float = None) -> str:
        """
        Execute HOP-5: Generate message candidates

        Args:
            state_mgr: State manager for this mission
            temperature: Optional temperature override for retry

        Returns:
            Path to output state file
        """
        print(f"\n{'=' * 80}")
        print("HOP-5: GENERATION AGENT")
        print(f"{'=' * 80}\n")

        # Read state
        research = state_mgr.read_state("HOP-2")
        grounding = state_mgr.read_state("HOP-3")
        scaffold = state_mgr.read_state("HOP-4.5")

        archetype = scaffold["archetype"]
        route = scaffold["route"]

        # Determine N candidates (C_LEVEL uses 3, others use 1)
        n_candidates = self.config["c_level_n_candidates"] if archetype == "C_LEVEL" else 1

        # Get temperature (use override if provided, else from config)
        if temperature is None:
            temperature = self._get_base_temperature(archetype)

        print(f"Generating {n_candidates} candidate(s) at temperature {temperature:.2f}...")

        # Generate candidates
        candidates = []

        for i in range(n_candidates):
            print(f"  Generating candidate {i + 1}/{n_candidates}...")

            draft_text = await self._generate_single_draft(
                research=research, grounding=grounding, scaffold=scaffold, temperature=temperature
            )

            candidates.append(
                {
                    "candidate_id": i + 1,
                    "text": draft_text,
                    "word_count": len(draft_text.split()),
                    "char_count": len(draft_text),
                    "temperature": temperature,
                }
            )

        # If multiple candidates, use tool-augmented scoring (Fast Loop)
        if n_candidates > 1:
            print(f"\nScoring {n_candidates} candidates (Fast Loop)...")
            scored = self._score_candidates_with_tool(candidates, research)
            selected_candidate = scored[0]
            print(
                f"  ✓ Selected candidate {selected_candidate['candidate_id']} (score: {selected_candidate['total_score']:.3f})"
            )
        else:
            selected_candidate = candidates[0]
            scored = [selected_candidate]

        # Prepare output state
        output_state = {
            "candidates": candidates,
            "scored_candidates": scored if n_candidates > 1 else None,
            "selected_draft": selected_candidate,
            "n_candidates": n_candidates,
            "generation_temperature": temperature,
            "generation_attempts": 1,  # Incremented by orchestrator on retry
            "archetype": archetype,
            "route": route,
        }

        # Write to state
        output_path = state_mgr.write_state("HOP-5", output_state)

        print("\n✓ Generation Complete")
        print(f"  Selected draft: {selected_candidate['word_count']} words")
        print(f"  Temperature: {temperature:.2f}\n")

        return output_path

    async def _generate_single_draft(
        self,
        research: dict[str, Any],
        grounding: dict[str, Any],
        scaffold: dict[str, Any],
        temperature: float,
    ) -> str:
        """Generate a single message draft"""

        # Load strategic alignment prompt template
        template = self.prompts["strategic_alignment_prompt_template"]["template"]

        # Extract context
        strategic_brief = research.get("strategic_brief", "")

        # Get sender capabilities (top 5)
        sender_summary = self._extract_sender_summary(grounding)

        # Get recipient priorities (top 5)
        recipient_summary = self._extract_recipient_summary(research, strategic_brief)

        # Load voice profile
        voice = self._load_voice_profile()

        # Fill template
        prompt = template.format(
            persona=voice.get("persona", "Strategic AI Leader"),
            principles="\n".join([f"- {p}" for p in voice.get("communication_principles", [])]),
            sender_summary=sender_summary,
            recipient_summary=recipient_summary,
            word_count_min=scaffold["constraints"]["word_range"][0],
            word_count_max=scaffold["constraints"]["word_range"][1],
            forbidden=", ".join(voice.get("forbidden_phrases", [])[:10]),
            route=scaffold["route"],
            archetype=scaffold["archetype"],
            adversarial_constraints="",  # TODO: Add if needed
        )

        # Generate with LLM
        loop = asyncio.get_event_loop()
        draft_text = await loop.run_in_executor(None, self.llm_client.generate, prompt)

        return draft_text.strip()

    def _score_candidates_with_tool(
        self, candidates: list[dict[str, Any]], research: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Score candidates using CodeInterpreterTool (Fast Loop)

        BREAKING CHANGE from v12.0:
        - OLD: LLM synthesis (~30s, $0.05)
        - NEW: Deterministic code scoring (<1s, $0.00)
        """

        strategic_brief = research.get("strategic_brief", "")

        # Use code tool for scoring
        scored = self.tool.execute(
            "run_scoring_competition",
            candidates=[c["text"] for c in candidates],
            strategic_brief=strategic_brief,
        )

        # Merge scores back with candidates
        for i, score_result in enumerate(scored):
            score_result["candidate_id"] = candidates[score_result["candidate_index"]][
                "candidate_id"
            ]
            score_result["word_count"] = candidates[score_result["candidate_index"]]["word_count"]
            score_result["temperature"] = candidates[score_result["candidate_index"]]["temperature"]

        return scored

    def _extract_sender_summary(self, grounding: dict[str, Any]) -> str:
        """Extract top 5 sender capabilities"""

        sender_grounding = grounding.get("sender_grounding", {})
        achievements = sender_grounding.get("quantifiable_achievements", [])
        products = sender_grounding.get("products", [])

        summary_lines = []

        # Top 5 achievements
        for achievement in achievements[:5]:
            summary_lines.append(f"- {achievement[:150]}")

        # Products
        for product in products[:2]:
            summary_lines.append(f"- Product: {product}")

        return (
            "\n".join(summary_lines) if summary_lines else "- Professional with relevant experience"
        )

    def _extract_recipient_summary(self, research: dict[str, Any], strategic_brief: str) -> str:
        """Extract top 5 recipient priorities"""

        summary_lines = []

        # Strategic brief is highest priority
        if strategic_brief:
            brief_lines = strategic_brief.split("\n")[:5]
            summary_lines.extend([f"- {line[:150]}" for line in brief_lines if line.strip()])

        # Fallback to insights
        if not summary_lines:
            insights = research.get("recipient_insights", [])
            summary_lines = [f"- {insight[:150]}" for insight in insights[:5]]

        return "\n".join(summary_lines) if summary_lines else "- Professional at target company"

    def _load_voice_profile(self) -> dict[str, Any]:
        """Load sender voice profile"""
        if os.path.exists("sender_voice_profile.json"):
            with open("sender_voice_profile.json") as f:
                return json.load(f)
        return {}

    def _get_base_temperature(self, archetype: str) -> float:
        """Get base temperature for archetype from config"""
        temp_config = self.config.get("base_temperatures", {})
        return temp_config.get(archetype, 0.50)


# ============================================================================
# HOP-6: VALIDATION AGENT (Refactored from ValidationAgent)
# ============================================================================


class HOP6_ValidationAgent:
    """
    v13.0: Validation Agent - Rule-based validation from config

    BREAKING CHANGE from v12.0:
    - OLD: Hardcoded validation rules in Python
    - NEW: All rules loaded from config/validator_rules_LIC.json
    - Uses ValidationToolkit for fast, deterministic checks

    Single Responsibility: Validate generated message

    Input:  state/5_generated_drafts.json, state/2_research_context.json
    Output: state/6_validation_report.json
    """

    def __init__(self, config: dict[str, Any], toolkit: ValidationToolkit):
        """
        Initialize with externalized config

        Args:
            config: Loaded from config/agent_specs_LIC.json
            toolkit: Validation toolkit for deterministic checks
        """
        self.config = config["validation_agent"]
        self.toolkit = toolkit

        # Load validation rules from config
        with open("config/validator_rules_LIC.json") as f:
            self.rules = json.load(f)

    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-6: Validate generated message

        Args:
            state_mgr: State manager for this mission

        Returns:
            Path to output state file
        """
        print(f"\n{'=' * 80}")
        print("HOP-6: VALIDATION AGENT")
        print(f"{'=' * 80}\n")

        # Read state
        generation = state_mgr.read_state("HOP-5")
        research = state_mgr.read_state("HOP-2")
        grounding = state_mgr.read_state("HOP-3")

        draft = generation["selected_draft"]
        text = draft["text"]

        print(f"Validating draft ({draft['word_count']} words)...")

        # Run validation rules
        validation_results = self._validate_draft(text, draft, research, grounding)

        # Aggregate results
        critical_issues = sum(
            1 for r in validation_results if r["severity"] == "CRITICAL" and not r["passed"]
        )
        high_issues = sum(
            1 for r in validation_results if r["severity"] == "HIGH" and not r["passed"]
        )
        medium_issues = sum(
            1 for r in validation_results if r["severity"] == "MEDIUM" and not r["passed"]
        )

        passed = critical_issues == 0 and high_issues == 0

        # Prepare output state
        output_state = {
            "validation_results": validation_results,
            "passed": passed,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "total_rules_checked": len(validation_results),
        }

        # Write to state
        output_path = state_mgr.write_state("HOP-6", output_state)

        if passed:
            print("\n✓ Validation PASSED")
        else:
            print("\n✗ Validation FAILED")

        print(f"  Critical: {critical_issues}")
        print(f"  High: {high_issues}")
        print(f"  Medium: {medium_issues}\n")

        return output_path

    def _validate_draft(
        self, text: str, draft: dict[str, Any], research: dict[str, Any], grounding: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Run all validation rules from config"""

        results = []

        # 1. Placeholder check (CRITICAL)
        patterns = self.rules["content_cleanliness_rules"]["placeholder_patterns"]["patterns"]
        for pattern in patterns:
            import re

            if re.search(pattern, text):
                results.append(
                    {
                        "passed": False,
                        "severity": "CRITICAL",
                        "rule_id": "LIC-QA-PLACEHOLDERS",
                        "message": f"Placeholder detected: {pattern}",
                    }
                )
                break

        # 2. Forbidden verbs (MEDIUM)
        forbidden_verbs = self.rules["content_cleanliness_rules"]["forbidden_verbs"]["list"]
        is_clean, violations = self.toolkit.check_forbidden_patterns(
            text=text, forbidden_patterns=[f"(?i)\\b{v}\\b" for v in forbidden_verbs]
        )

        if not is_clean:
            results.append(
                {
                    "passed": False,
                    "severity": "MEDIUM",
                    "rule_id": "LIC-QA-FORBIDDEN-VERBS",
                    "message": f"Forbidden verbs detected: {violations[:3]}",
                }
            )

        # 3. Filler phrases (MEDIUM)
        filler_patterns = self.rules["content_cleanliness_rules"]["filler_patterns"]["patterns"]
        is_clean, violations = self.toolkit.check_forbidden_patterns(
            text=text, forbidden_patterns=filler_patterns
        )

        if not is_clean:
            results.append(
                {
                    "passed": False,
                    "severity": "MEDIUM",
                    "rule_id": "LIC-QA-FILLERS",
                    "message": f"Filler phrases detected: {violations[:3]}",
                }
            )

        # 4. Word count validation (HIGH)
        target = draft.get("word_count_target", 200)
        is_valid, details = self.toolkit.check_word_count_range(
            text=text, target=target, tolerance=0.15
        )

        if not is_valid:
            results.append(
                {
                    "passed": False,
                    "severity": "HIGH",
                    "rule_id": "LIC-QA-WORD-COUNT",
                    "message": f"Word count {details['word_count']} outside range {details['min_words']}-{details['max_words']}",
                }
            )

        # 5. ASCII only (HIGH)
        is_ascii, non_ascii = self.toolkit.check_ascii_only(text)

        if not is_ascii:
            results.append(
                {
                    "passed": False,
                    "severity": "HIGH",
                    "rule_id": "LIC-QA-055",
                    "message": f"Non-ASCII characters detected: {non_ascii[:3]}",
                }
            )

        # 6. Strategic alignment (CRITICAL) - v12.0 LIC-QA-201
        strategic_brief = research.get("strategic_brief", "")
        if strategic_brief:
            min_overlap = self.rules["strategic_alignment_validation"]["min_keyword_overlap"]

            # Extract keywords from brief and message
            import re

            brief_words = set(
                w.lower().strip(".,!?;:") for w in strategic_brief.split() if len(w) > 4
            )
            message_words = set(w.lower().strip(".,!?;:") for w in text.split() if len(w) > 4)

            overlap = brief_words & message_words

            if len(overlap) < min_overlap:
                results.append(
                    {
                        "passed": False,
                        "severity": "CRITICAL",
                        "rule_id": "LIC-QA-201",
                        "message": f"Strategic alignment failure: Only {len(overlap)} keyword overlap (need {min_overlap}+)",
                        "details": {"failure_classifier": "FACTUAL_FAILURE"},
                    }
                )

        # 7. Sender grounding validation (CRITICAL)
        sender_grounding_data = grounding.get("sender_grounding", {})
        team_keywords = self.rules["sender_grounding_validation"]["team_keywords"]
        product_keywords = self.rules["sender_grounding_validation"]["product_keywords"]

        text_lower = text.lower()

        has_team_claim = any(kw in text_lower for kw in team_keywords)
        if has_team_claim and not sender_grounding_data.get("team_members"):
            results.append(
                {
                    "passed": False,
                    "severity": "CRITICAL",
                    "rule_id": "LIC-QA-105-TEAM",
                    "message": "Team claims without whitelist",
                }
            )

        has_product_claim = any(kw in text_lower for kw in product_keywords)
        if has_product_claim and not sender_grounding_data.get("products"):
            results.append(
                {
                    "passed": False,
                    "severity": "CRITICAL",
                    "rule_id": "LIC-QA-105-PRODUCT",
                    "message": "Product claims without whitelist",
                }
            )

        # If all checks passed, add a success result
        if not results:
            results.append(
                {
                    "passed": True,
                    "severity": "INFO",
                    "rule_id": "ALL-CHECKS",
                    "message": "All validation checks passed",
                }
            )

        return results


# ============================================================================
# HOP-8: QA REPORT AGENT (New - Enhancement 6)
# ============================================================================


class HOP8_QAReportAgent:
    """
    v13.0: QA Report Agent - Persistent markdown report generation

    NEW in v13.0:
    - Reads ALL state files from workflow
    - Synthesizes comprehensive QA report
    - Outputs persistent markdown file

    Single Responsibility: Generate audit trail report

    Input:  state/* (all state files)
    Output: outputs/QA_Report.md
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize with externalized config

        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        self.config = config["qa_report_agent"]
        self.sections = self.config["report_sections"]
        self.scoring_weights = self.config["scoring_weights"]

    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-8: Generate comprehensive QA report

        Args:
            state_mgr: State manager for this mission

        Returns:
            Path to QA report file
        """
        print(f"\n{'=' * 80}")
        print("HOP-8: QA REPORT GENERATION")
        print(f"{'=' * 80}\n")

        # Read all state files
        states = {}
        for hop_id in ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5", "HOP-6", "HOP-7"]:
            if state_mgr.state_exists(hop_id):
                states[hop_id] = state_mgr.read_state(hop_id)

        print(f"Synthesizing report from {len(states)} state files...")

        # Generate markdown report
        report = self._generate_markdown_report(states, state_mgr.mission_id)

        # Write report to outputs/
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        report_path = output_dir / f"QA_Report_{state_mgr.mission_id}.md"

        with open(report_path, "w") as f:
            f.write(report)

        print(f"\n✓ QA Report Generated: {report_path}\n")

        return str(report_path)

    def _generate_markdown_report(self, states: dict[str, Any], mission_id: str) -> str:
        """Generate comprehensive markdown report"""

        lines = []

        # Header
        lines.append("# LIC v13.0 QA Report")
        lines.append(f"\n**Mission ID**: `{mission_id}`")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n---\n")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary\n")

        validation = states.get("HOP-6", {})
        passed = validation.get("passed", False)

        if passed:
            lines.append("**Status**: ✅ **PASS** - Message ready for production")
        else:
            lines.append("**Status**: ❌ **FAIL** - Message requires revision")

        lines.append(f"\n**Critical Issues**: {validation.get('critical_issues', 0)}")
        lines.append(f"**High Issues**: {validation.get('high_issues', 0)}")
        lines.append(f"**Medium Issues**: {validation.get('medium_issues', 0)}")
        lines.append("\n")

        # 2. Archetype & Route Selection
        lines.append("## 2. Archetype & Route Selection\n")

        profile = states.get("HOP-1", {})
        routing = states.get("HOP-4", {})

        lines.append(f"**Archetype**: {profile.get('archetype', 'N/A')}")
        lines.append(f"**Confidence**: {profile.get('confidence', 0):.2f}")
        lines.append(f"**Reasoning**: {profile.get('reasoning', 'N/A')}")
        lines.append(f"\n**Route**: {routing.get('route', 'N/A')}")
        lines.append(f"**Route Reasoning**: {routing.get('reasoning', 'N/A')}")
        lines.append("\n")

        # 3. Research Quality Assessment
        lines.append("## 3. Research Quality Assessment\n")

        research = states.get("HOP-2", {})

        lines.append(f"**Total Sources**: {research.get('total_sources', 0)}")
        lines.append(f"**Signal Score**: {research.get('signal_score', 0):.2f}")
        lines.append(
            f"**Cache Hit**: {'Yes' if research.get('cache_hit', False) else 'No (Fallback RAG used)'}"
        )
        lines.append(
            f"**Fallback Used**: {'Yes' if research.get('fallback_used', False) else 'No'}"
        )
        lines.append("\n")

        # 4. Generation Strategy
        lines.append("## 4. Generation Strategy\n")

        generation = states.get("HOP-5", {})

        lines.append(f"**Candidates Generated**: {generation.get('n_candidates', 1)}")
        lines.append(f"**Temperature**: {generation.get('generation_temperature', 0.5):.2f}")
        lines.append(f"**Generation Attempts**: {generation.get('generation_attempts', 1)}")
        lines.append("\n")

        # 5. Validation Results
        lines.append("## 5. Validation Results\n")

        results = validation.get("validation_results", [])

        lines.append(f"**Total Rules Checked**: {len(results)}")
        lines.append("\n### Failed Checks:\n")

        failed = [r for r in results if not r.get("passed", True)]
        if failed:
            for result in failed:
                lines.append(
                    f"- **{result['rule_id']}** ({result['severity']}): {result['message']}"
                )
        else:
            lines.append("_No failed checks_")

        lines.append("\n")

        # 6. Loop Execution Details
        lines.append("## 6. Loop Execution Details\n")

        gate = states.get("HOP-7", {})

        lines.append(f"**Factual Loops (S6→S2)**: {gate.get('factual_loop_count', 0)}")
        lines.append(f"**Creative Retries (S5)**: {gate.get('creative_retry_count', 0)}")
        lines.append(f"**Gate Decision**: {gate.get('decision', 'N/A')}")
        lines.append("\n")

        # 7. Final Message
        lines.append("## 7. Final Generated Message\n")

        draft = generation.get("selected_draft", {})

        lines.append(f"**Word Count**: {draft.get('word_count', 0)}")
        lines.append(f"**Character Count**: {draft.get('char_count', 0)}")
        lines.append("\n```")
        lines.append(draft.get("text", "N/A"))
        lines.append("```\n")

        # 8. Quality Score
        lines.append("## 8. Overall Quality Score\n")

        score = self._calculate_quality_score(states)

        lines.append(f"**Final Score**: {score:.1f}/100")
        lines.append("\n---")
        lines.append("\n*Generated by LIC v13.0 QA Report Agent*")

        return "\n".join(lines)

    def _calculate_quality_score(self, states: dict[str, Any]) -> float:
        """Calculate overall quality score"""

        research = states.get("HOP-2", {})
        validation = states.get("HOP-6", {})
        gate = states.get("HOP-7", {})

        # Research quality (0-30 points)
        research_score = min(30, research.get("signal_score", 0.5) * 30)

        # Strategic alignment (0-30 points)
        passed = validation.get("passed", False)
        critical = validation.get("critical_issues", 0)
        alignment_score = 30 if passed and critical == 0 else 0

        # Validation pass rate (0-20 points)
        results = validation.get("validation_results", [])
        passed_count = sum(1 for r in results if r.get("passed", False))
        total_count = len(results) if results else 1
        validation_score = (passed_count / total_count) * 20

        # Loop efficiency (0-10 points)
        factual_loops = gate.get("factual_loop_count", 0)
        creative_retries = gate.get("creative_retry_count", 0)
        loop_penalty = (factual_loops * 3) + (creative_retries * 2)
        loop_score = max(0, 10 - loop_penalty)

        # Generation quality (0-10 points)
        generation = states.get("HOP-5", {})
        draft = generation.get("selected_draft", {})
        word_count = draft.get("word_count", 0)
        in_range = 150 <= word_count <= 300
        generation_score = 10 if in_range else 5

        total_score = (
            research_score + alignment_score + validation_score + loop_score + generation_score
        )

        return total_score


# ============================================================================
# HOP ORCHESTRATOR (Refactored from WorkflowOrchestrator)
# ============================================================================


class HOPOrchestrator:
    """
    v13.0: HOP-based Workflow Orchestrator

    BREAKING CHANGE from v12.0:
    - OLD: Monolithic orchestrator with in-memory object passing
    - NEW: "Foreman" pattern - iterates through HOPs, all I/O via state files
    - Implements S6→S2 meta-loop (Factual failure)
    - Implements S5 retry (Creative failure)

    The Orchestrator is configuration-driven and agent-agnostic.
    """

    def __init__(self):
        """Initialize orchestrator with all dependencies"""

        # Load configuration
        with open("config/agent_specs_LIC.json") as f:
            self.config = json.load(f)

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config["circuit_breaker"]["failure_threshold"],
            timeout_seconds=self.config["circuit_breaker"]["timeout_seconds"],
        )

        # Initialize API clients
        self.search_client = GoogleSearchClient(self.circuit_breaker)
        self.llm_client = GeminiLLMClient(self.circuit_breaker)

        # Initialize memory store
        self.memory_store = VectorMemoryStore()

        # Initialize tools
        self.code_tool = CodeInterpreterTool()
        self.validation_toolkit = ValidationToolkit()

        # Initialize HOP agents
        self.agents = {
            "HOP-2": HOP2_ResearchAgent(
                self.config, self.memory_store, self.search_client, self.llm_client
            ),
            "HOP-5": HOP5_GenerationAgent(self.config, self.llm_client, self.code_tool),
            "HOP-6": HOP6_ValidationAgent(self.config, self.validation_toolkit),
            "HOP-8": HOP8_QAReportAgent(self.config),
        }

        # Get HOP execution order from config
        self.hop_execution_order = self.config["hop_execution_order"]["hops"]

        print(f"[HOPOrchestrator] Initialized with {len(self.agents)} agents")

    async def execute_workflow(self, mission: OutreachMission) -> dict[str, Any]:
        """
        Execute complete workflow using HOP architecture

        Args:
            mission: Mission specification

        Returns:
            Workflow result dictionary
        """
        print(f"\n{'=' * 80}")
        print("HOP WORKFLOW ORCHESTRATOR v13.0")
        print(f"Mission ID: {mission.mission_id}")
        print(f"{'=' * 80}")

        start_time = datetime.now()

        # Initialize state manager
        state_mgr = StateManager(mission_id=mission.mission_id)

        # Track loop counts
        factual_loop_count = 0
        creative_retry_count = 0
        max_factual_loops = 2
        max_creative_retries = 3

        try:
            # Main execution loop
            while True:
                # Execute HOPs in sequence
                for hop_spec in self.hop_execution_order:
                    hop_id = hop_spec["hop_id"]

                    # Skip if agent not implemented
                    if hop_id not in self.agents:
                        print(f"\n⚠ {hop_id} - Agent not implemented, skipping")
                        continue

                    agent = self.agents[hop_id]

                    try:
                        # Execute agent
                        await agent.execute(state_mgr)

                    except FactualGapError as e:
                        # S6→S2 Meta-Loop triggered
                        factual_loop_count += 1

                        if factual_loop_count >= max_factual_loops:
                            print(f"\n✗ Max factual loops ({max_factual_loops}) reached - HALTING")
                            raise ValueError(f"Max factual loops exceeded: {e}")

                        print(f"\n⚠ Factual gap detected: {e}")
                        print(
                            f"→ Triggering S6→S2 meta-loop (attempt {factual_loop_count}/{max_factual_loops})"
                        )

                        # Loop back to HOP-2 (research)
                        break

                    except Exception as e:
                        print(f"\n✗ Error in {hop_id}: {e}")
                        raise

                # Check if we need to retry due to creative failure
                if state_mgr.state_exists("HOP-7"):
                    gate = state_mgr.read_state("HOP-7")
                    decision = gate.get("decision")

                    if decision == "CREATIVE_FAILURE":
                        creative_retry_count += 1

                        if creative_retry_count >= max_creative_retries:
                            print(
                                f"\n✗ Max creative retries ({max_creative_retries}) reached - HALTING"
                            )
                            raise ValueError("Max creative retries exceeded")

                        print("\n⚠ Creative failure detected")
                        print(
                            f"→ Retrying HOP-5 with escalated temperature (attempt {creative_retry_count}/{max_creative_retries})"
                        )

                        # Escalate temperature
                        base_temp = 0.50
                        new_temp = min(0.95, base_temp + (creative_retry_count * 0.15))

                        # Re-run HOP-5 with higher temperature
                        await self.agents["HOP-5"].execute(state_mgr, temperature=new_temp)

                        # Re-run HOP-6 validation
                        await self.agents["HOP-6"].execute(state_mgr)

                        continue

                    elif decision == "PASS":
                        # Workflow complete
                        break
                else:
                    # No gate decision yet, continue
                    break

        except Exception as e:
            print(f"\n✗ Workflow failed: {e}")

            return {
                "mission_id": mission.mission_id,
                "status": "failed",
                "error": str(e),
                "workflow_time": (datetime.now() - start_time).total_seconds(),
            }

        # Get workflow results
        workflow_time = (datetime.now() - start_time).total_seconds()

        validation = state_mgr.read_state("HOP-6") if state_mgr.state_exists("HOP-6") else {}
        generation = state_mgr.read_state("HOP-5") if state_mgr.state_exists("HOP-5") else {}

        passed = validation.get("passed", False)
        draft = generation.get("selected_draft", {})

        print(f"\n{'=' * 80}")
        print("WORKFLOW COMPLETE")
        print(f"Status: {'PASS' if passed else 'FAIL'}")
        print(f"Time: {workflow_time:.1f}s")
        print(f"Factual loops: {factual_loop_count}")
        print(f"Creative retries: {creative_retry_count}")
        print(f"{'=' * 80}\n")

        return {
            "mission_id": mission.mission_id,
            "status": "success" if passed else "failed_validation",
            "production_ready": passed,
            "message": draft.get("text", ""),
            "word_count": draft.get("word_count", 0),
            "workflow_time": workflow_time,
            "factual_loop_count": factual_loop_count,
            "creative_retry_count": creative_retry_count,
            "validation_summary": {
                "passed": passed,
                "critical_issues": validation.get("critical_issues", 0),
                "high_issues": validation.get("high_issues", 0),
            },
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


async def main():
    """Main execution entry point"""

    # Create sample mission
    mission = OutreachMission(
        mission_id="demo_v13_001",
        sender_profile={
            "name": "Amit Ayer",
            "title": "Chief AI Officer",
            "company": "Unify Consulting",
        },
        recipient_profile={
            "name": "Sarah Johnson",
            "title": "VP of Engineering",
            "company": "Tech Giants Corp",
        },
        job_description={
            "title": "Head of AI Platform",
            "company": "Tech Giants Corp",
            "location": "San Francisco, CA",
        },
        connection_status="not_connected",
        prior_message_count=0,
    )

    # Execute workflow
    orchestrator = HOPOrchestrator()
    result = await orchestrator.execute_workflow(mission)

    print("\n" + "=" * 80)
    print("WORKFLOW RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())