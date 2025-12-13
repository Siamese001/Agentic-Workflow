"""
Executive Agent Orchestrator - Chief of Staff level competitive intelligence.

Implements three specialized agents:
- K.11 Shadow Audit: Technical due diligence from public signals
- K.12 Strategy Roadmap: 30-60-90 day execution plan
- K.13 Interviewer Simulation: Oppositional interview preparation

Uses Instructor for structured output and integrates with hardened infrastructure.
"""

import os
import logging

try:
    import instructor
    from openai import OpenAI
    from anthropic import Anthropic
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False
    logging.warning("Instructor not available. Executive agents will use mock responses.")

    TechnicalSWOT,
    StrategyRoadmap,
    InterviewerProfile,
    get_executive_schema_registry
)
# Import hardened infrastructure
# from ..resilience.hardened_openai_executor import HardenedOpenAIExecutor
# from ..resilience.hardened_brave_search import HardenedBraveSearch

logger = logging.getLogger(__name__)

class DataSourceProvider:
    """Interface for external data sources used by executive agents."""

    def __init__(self, brave_search_tool=None):
        """Initialize with optional search tool.

        Args:
            brave_search_tool: Optional HardenedBraveSearch instance
        """
        self.brave_search = brave_search_tool
        self.logger = logging.getLogger("DataSourceProvider")

    async def search_engineering_blog(self, company_name: str) -> str:
        """Search for company's engineering blog posts.

        Args:
            company_name: Company to search for

        Returns:
            Aggregated blog content
        """
        if not self.brave_search:
            return f"[MOCK] Engineering blog content for {company_name}: Recent posts mention migrat
    ion to microservices..."

        queries = [
            f"{company_name} engineering blog",
            f"{company_name} technical blog architecture",
            f"{company_name} engineering posts 2023 2024"
        ]

        results = []
        for query in queries:
            try:
                search_result = await self.brave_search.execute_search(query, count=3)
                if search_result.get("results"):
                    for item in search_result["results"][:2]:
                        results.append(f"Title: {item['title']}\nSnippet: {item['description']}")
            except Exception as e:
                self.logger.error(f"Search failed for {query}: {e}")

        return "\n\n".join(results) if results else f"No engineering blog found for {company_name}"

    async def scan_github_organization(self, company_name: str) -> str:
        """Scan company's GitHub for tech insights.

        Args:
            company_name: Company to scan

        Returns:
            Technology insights from GitHub
        """
        if not self.brave_search:
            return f"[MOCK] GitHub scan for {company_name}: Primary repos use Python, React, Kuberne
    tes..."

        query = f"site:github.com {company_name} organization repositories"

        try:
            search_result = await self.brave_search.execute_search(query, count=5)

            if search_result.get("results"):
                insights = []
                for item in search_result["results"]:
                    insights.append(f"Repo: {item['title']}\n{item['description']}")
                return "\n\n".join(insights)

        except Exception as e:
            self.logger.error(f"GitHub scan failed: {e}")

        return f"No GitHub organization found for {company_name}"

    async def get_interviewer_profile(self, linkedin_url: str) -> str:
        """Get interviewer's professional background.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Professional background and interests
        """
        if not self.brave_search:
            return "[MOCK] Interviewer profile: 15 years at company, technical background, loves sys
    tem design..."

        # Extract name from URL if possible
        name = linkedin_url.split('/')[-1] if linkedin_url else "unknown"

        query = f'"{name}" {linkedin_url} background experience interests'

        try:
            search_result = await self.brave_search.execute_search(query, count=3)

            if search_result.get("results"):
                profile_info = []
                for item in search_result["results"]:
                    profile_info.append(item['description'])
                return " ".join(profile_info)

        except Exception as e:
            self.logger.error(f"Profile search failed: {e}")

        return f"Limited profile information available for {name}"

class ExecutiveAgentOrchestrator:
    """
    Orchestrates executive strategy agents with structured output.

    Uses Instructor for reliable structured output and integrates
    with the hardened infrastructure for resilience.
    """

    def __init__(self, data_source_provider: Optional[DataSourceProvider] = None):
        """Initialize the orchestrator.

        Args:
            data_source_provider: Optional data source provider
        """
        self.data_sources = data_source_provider or DataSourceProvider()
        self.schema_registry = get_executive_schema_registry()

        # Initialize LLM clients with Instructor if available
        if INSTRUCTOR_AVAILABLE:
            self._initialize_clients()
        else:
            self.openai_client = None
            self.anthropic_client = None
            logger.warning("Running in mock mode - install instructor for full functionality")

        # Statistics
        self.stats = {
            "k11_executions": 0,
            "k12_executions": 0,
            "k13_executions": 0,
            "total_cost_estimate": 0.0,
            "total_tokens_used": 0
        }

        self.logger = logging.getLogger("ExecutiveAgentOrchestrator")

    def _initialize_clients(self):
        """Initialize LLM clients with Instructor patching."""
        try:
            # Initialize OpenAI client
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = instructor.patch(OpenAI(api_key=openai_key))

            # Initialize Anthropic client
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = instructor.from_anthropic(Anthropic(api_key=anthropic_key))

            if not self.openai_client and not self.anthropic_client:
                raise ValueError("No API keys found for OpenAI or Anthropic")

        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {e}")
            self.openai_client = None
            self.anthropic_client = None

    def _get_client_and_model(self, node_config: Dict[str, Any]):
        """Get appropriate client and model based on configuration.

        Args:
            node_config: Node configuration with infrastructure settings

        Returns:
            Tuple of (client, model_name)
        """
        infra = node_config.get("infrastructure_config", {})
        model = infra.get("primary_model", "gpt-4o")

        if not INSTRUCTOR_AVAILABLE:
            return None, model

        # Route to appropriate client
        if "claude" in model.lower() and self.anthropic_client:
            return self.anthropic_client, model
        elif self.openai_client:
            return self.openai_client, model
        else:
            raise ValueError(f"No client available for model: {model}")

    async def execute_k11_shadow_audit(
        """Docstring."""
        self,
        company_name: str,
        config: Dict[str, Any]
    ) -> TechnicalSWOT:
        """
        K.11: Technical Due Diligence (Shadow Audit)

        Analyzes target company's engineering blog, GitHub, and leadership
        interviews to infer technical maturity and debt.

        Args:
            company_name: Target company name
            config: Node configuration

        Returns:
            TechnicalSWOT analysis
        """
        self.logger.info(f"Executing K.11 Shadow Audit for {company_name}")
        self.stats["k11_executions"] += 1

        # Gather external data
        blog_content = await self.data_sources.search_engineering_blog(company_name)
        github_insights = await self.data_sources.scan_github_organization(company_name)

        # Combine search context
        search_context = f"""
        Engineering Blog Analysis:
        {blog_content}

        GitHub Organization Insights:
        {github_insights}
        """

        if not INSTRUCTOR_AVAILABLE:
            # Return mock response
            return TechnicalSWOT(
                current_stack=[
                    {
                        "category": "Frontend",
                        "tool_name": "React",
                        "confidence_score": 0.9,
                        "evidence_source": "Engineering Blog 2023",
                        "maturity_level": "Modern"
                    },
                    {
                        "category": "Backend",
                        "tool_name": "Python/Django",
                        "confidence_score": 0.8,
                        "evidence_source": "GitHub repos",
                        "maturity_level": "Stable"
                    },
                    {
                        "category": "Data",
                        "tool_name": "PostgreSQL",
                        "confidence_score": 0.7,
                        "evidence_source": "Job postings",
                        "maturity_level": "Stable"
                    }
                ],
                suspected_bottlenecks=[
                    "Legacy monolith architecture slowing deployment",
                    "Limited automated testing coverage",
                    "On-premise data warehouse limiting scalability"
                ],
                gen_ai_maturity_score=2,
                strategic_opportunity="Lead migration to modern MLOps stack with automated CI/CD"
            )

        # Execute with structured output
        client, model = self._get_client_and_model(config)
        temperature = config["infrastructure_config"].get("temperature_override", 0.2)

        system_prompt = f"""
        You are a Technical Due Diligence Officer performing a 'Shadow Audit' of {company_name}.

        Your mission: Reconstruct the unstated technical reality from public signals.

        Analyze the provided search results to infer:
        1. Their ACTUAL technology stack (not what marketing claims)
        2. Technical debt and bottlenecks (read between the lines)
        3. Real AI/ML maturity vs buzzword compliance
        4. The ONE strategic opportunity a new leader could champion

        Be skeptical but professional. Look for:
        - Migration posts that reveal legacy systems
        - Job requirements that show current stack
        - GitHub activity that indicates engineering practices
        - Blog posts that hint at challenges

        Your analysis will help a candidate prepare for a senior technical leadership role.
        """

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=TechnicalSWOT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Public Signals Analysis:\n{search_context}"}
                ],
                temperature=temperature,
                max_tokens=2000
            )

            self.logger.info(f"K.11 completed successfully for {company_name}")
            return result

        except Exception as e:
            self.logger.error(f"K.11 execution failed: {e}")
            raise

    async def execute_k12_strategy(
        """Docstring."""
        self,
        job_description: str,
        technical_swot: TechnicalSWOT,
        config: Dict[str, Any]
    ) -> StrategyRoadmap:
        """
        K.12: 30-60-90 Day Strategy Architect

        Synthesizes identified gaps and technical reality into a tactical
        executive roadmap using People-Process-Technology framework.

        Args:
            job_description: Job description text
            technical_swot: Results from K.11 analysis
            config: Node configuration

        Returns:
            StrategyRoadmap with 30-60-90 day plan
        """
        self.logger.info("Executing K.12 Strategy Roadmap")
        self.stats["k12_executions"] += 1

        if not INSTRUCTOR_AVAILABLE:
            # Return mock response
            return StrategyRoadmap(
                executive_summary="Transform engineering organization to deliver scalable AI-powered
    solutions while improving developer productivity and system reliability.",
                primary_objective="Establish modern MLOps infrastructure and high-performing enginee
    ring culture",
                milestones=[
                    {
                        "timeframe": "Day 30",
                        "focus_area": "People",
                        "initiative": "Conduct team assessments and establish 1:1s with all engineer
    s",
                        "success_metric": "100% team assessment completion",
                        "risk_level": "Low"
                    },
                    {
                        "timeframe": "Day 30",
                        "focus_area": "Process",
                        "initiative": "Implement daily standups and sprint planning",
                        "success_metric": "Sprint velocity baseline established",
                        "risk_level": "Low"
                    },
                    {
                        "timeframe": "Day 60",
                        "focus_area": "Technology",
                        "initiative": "Deploy CI/CD pipeline for main applications",
                        "success_metric": "Deployment frequency increased by 50%",
                        "risk_level": "Medium"
                    },
                    {
                        "timeframe": "Day 90",
                        "focus_area": "Technology",
                        "initiative": "Launch first ML model in production",
                        "success_metric": "Model serving with <100ms latency",
                        "risk_level": "High"
                    }
                ],
                immediate_wins=[
                    {
                        "initiative": "Fix top 3 production bugs",
                        "impact": "High",
                        "effort": "Low",
                        "timeline_days": 7
                    },
                    {
                        "initiative": "Set up monitoring dashboard",
                        "impact": "Medium",
                        "effort": "Low",
                        "timeline_days": 14
                    }
                ],
                key_stakeholders=["CTO", "VP Engineering", "Product Lead", "Engineering Managers"],
                success_criteria="90% deployment success rate, 40% reduction in incident response ti
    me"
            )

        # Execute with structured output
        client, model = self._get_client_and_model(config)
        temperature = config["infrastructure_config"].get("temperature_override", 0.5)

        system_prompt = """
        You are an incoming Chief of Staff / Head of AI creating a 30-60-90 day plan.

        CRITICAL CONSTRAINTS:
        1. Use the People-Process-Technology framework
        2. Address the bottlenecks identified in the Technical SWOT
        3. Focus on quick wins that build credibility
        4. Each milestone must have measurable success metrics
        5. Plan must be realistic for a new leader

        Your roadmap will demonstrate strategic thinking and execution capability
        to secure the role and hit the ground running.
        """

        user_content = f"""
        Job Description (Key Requirements):
        {job_description[:2000]}...

        Technical Audit Findings:
        Bottlenecks: {technical_swot.suspected_bottlenecks}
        Strategic Opportunity: {technical_swot.strategic_opportunity}
        AI Maturity: {technical_swot.gen_ai_maturity_score}/5
        Current Stack: {[stack.tool_name for stack in technical_swot.current_stack]}

        Create a compelling 30-60-90 day plan that addresses these realities.
        """

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=StrategyRoadmap,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=3000
            )

            self.logger.info("K.12 completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"K.12 execution failed: {e}")
            raise

    async def execute_k13_simulation(
        """Docstring."""
        self,
        interviewer_linkedin: str,
        resume_text: str,
        config: Dict[str, Any]
    ) -> InterviewerProfile:
        """
        K.13: Oppositional Interview Simulation

        Simulates the specific interviewer's questioning style based on
        their public digital footprint and background.

        Args:
            interviewer_linkedin: LinkedIn profile URL
            resume_text: Candidate's resume text
            config: Node configuration

        Returns:
            InterviewerProfile with predicted questions
        """
        self.logger.info("Executing K.13 Interviewer Simulation")
        self.stats["k13_executions"] += 1

        # Get interviewer background
        interviewer_data = await self.data_sources.get_interviewer_profile(interviewer_linkedin)

        if not INSTRUCTOR_AVAILABLE:
            # Return mock response
            return InterviewerProfile(
                interviewer_name="Senior Engineering Manager",
                title="Director of Engineering",
                company_tenure="5 years",
                dominant_archetype="The Builder",
                key_biases=[
                    {
                        "category": "Technical",
                        "preference": "Hands-on coding experience",
                        "aversion": "Pure management without technical depth",
                        "how_to_leverage": "Emphasize recent technical contributions"
                    }
                ],
                kill_chain_questions=[
                    {
                        "question_text": "Tell me about a time you had to make a difficult technical
    trade-off",
                        "question_type": "Technical",
                        "rationale": "Wants to see technical judgment and decision-making",
                        "recommended_angle": "Focus on systematic evaluation and business impact",
                        "difficulty": "Hard",
                        "follow_up_likelihood": "High"
                    }
                ],
                conversation_starters=["Tell me about your background", "What brings you here today?
    "],
                decision_factors=["Technical depth", "Leadership experience", "Culture fit"],
                red_flags=["Arrogance", "Blaming others", "No concrete examples"]
            )

        # Execute with structured output
        client, model = self._get_client_and_model(config)
        temperature = config["infrastructure_config"].get("temperature_override", 0.7)

        system_prompt = """
        You are a Psychological Profiler for Executive Search.

        Your task: Analyze the interviewer's background to predict their interview style.

        Identify:
        1. Their dominant archetype (Builder, Academic, Politician, etc.)
        2. Key biases and preferences
        3. The 5 hardest questions they will ask
        4. How to strategically answer each question

        This is NOT about helping someone fake their personality.
        It's about understanding the interviewer to communicate effectively.

        Be insightful but ethical. Focus on communication strategies, not deception.
        """

        user_content = f"""
        Interviewer Background:
        {interviewer_data}

        Candidate Resume (Key Points):
        {resume_text[:2000]}...

        Analyze the interviewer and predict their questioning approach.
        Focus on questions that test the candidate's fit for THIS specific role.
        """

        try:
            result = client.chat.completions.create(
                model=model,
                response_model=InterviewerProfile,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=2500
            )

            self.logger.info("K.13 completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"K.13 execution failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dictionary with execution stats
        """
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset all statistics."""
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0

# Factory function
def create_executive_orchestrator(
    """Docstring."""
    brave_search_tool=None,
    data_source_provider: Optional[DataSourceProvider] = None
) -> ExecutiveAgentOrchestrator:
    """Create a configured executive agent orchestrator.

    Args:
        brave_search_tool: Optional Brave Search tool
        data_source_provider: Optional custom data source provider

    Returns:
        ExecutiveAgentOrchestrator instance
    """
    if data_source_provider is None:
        data_source_provider = DataSourceProvider(brave_search_tool)

    return ExecutiveAgentOrchestrator(data_source_provider)
