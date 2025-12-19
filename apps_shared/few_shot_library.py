"""
Few-Shot Library - Prompt Enhancement Patterns for L5+ Autonomy.

Implements the Canon Validator few-shot injection pattern with
domain-specific examples for Resume Engine and Outreach Engine.

Canon Validator Patterns Implemented:
- FEW_SHOT_SHERLOCK: Root cause analysis examples
- FEW_SHOT_GITOPS: Branch/commit naming examples
- FEW_SHOT_STRATEGIC: Strategic planning examples
- FEW_SHOT_REFLECTION_STRATEGY: Self-critique examples
- FEW_SHOT_GLOBAL_REFACTOR: Cross-file refactoring examples

Domain-Specific Extensions:
- FEW_SHOT_RESUME_BULLETS: Achievement bullet improvement
- FEW_SHOT_OUTREACH_PERSONALIZATION: Message personalization
- FEW_SHOT_EXECUTIVE_SUMMARY: Executive summary generation
- FEW_SHOT_METRIC_BINDING: Metric to evidence binding
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FewShotExample:
    """A single few-shot example."""

    input_text: str
    output_text: str
    explanation: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def format(self, include_explanation: bool = False) -> str:
        """Format the example for prompt injection."""
        result = f"Input: {self.input_text}\nOutput: {self.output_text}"
        if include_explanation and self.explanation:
            result += f"\nExplanation: {self.explanation}"
        return result


# =============================================================================
# CANON VALIDATOR CORE PATTERNS
# =============================================================================

FEW_SHOT_SHERLOCK = """
<sherlock_examples>
Example 1: ImportError in test_utils.py
Root cause: Missing __init__.py in parent directory
Fix: Added __init__.py with proper exports
Reasoning: The test file couldn't import the module because Python didn't recognize the directory as a package.

Example 2: AttributeError 'NoneType' has no attribute 'execute'
Root cause: Dependency injection failed - service not registered
Fix: Added service registration in container initialization
Reasoning: The service was expected but never instantiated due to missing DI configuration.

Example 3: KeyError 'user_id' in process_request
Root cause: Schema mismatch between API versions
Fix: Added backward-compatible field mapping with fallback
Reasoning: The upstream service changed field names without versioning.
</sherlock_examples>
"""

FEW_SHOT_GITOPS = """
<gitops_examples>
Branch naming:
- healing/auto_1702847293 - Automated healing branch with timestamp
- fix/import-resolution-utils - Specific fix for import issues
- refactor/consolidate-validators - Refactoring task

Commit messages:
- "fix(imports): resolve circular dependency in utils module"
- "refactor(validation): consolidate duplicate gate logic"
- "feat(signals): add HIGH_RISK signal emission on quality drop"
- "chore(deps): update pinecone-client to 5.0.0"
</gitops_examples>
"""

FEW_SHOT_STRATEGIC = """
<strategic_planning_examples>
Example 1: High signal count with TEST_FAILURE
Analysis: Tests failing after recent changes to validation logic
Strategy:
1. Identify modified files in last cycle
2. Run targeted tests on those files
3. If still failing, rollback and try alternative approach
Priority: HIGH - blocking convergence

Example 2: Quality score degradation trend
Analysis: Quality dropped from 0.85 to 0.72 over 3 cycles
Strategy:
1. Review prompt temperature settings
2. Check if few-shot examples are still relevant
3. Consider adding domain-specific constraints
Priority: MEDIUM - not blocking but concerning

Example 3: Multiple agents reporting similar issues
Analysis: DependencySentinel and SafetyInspector both flagging same files
Strategy:
1. Consolidate findings to avoid duplicate work
2. Prioritize by severity
3. Fix root cause rather than symptoms
Priority: HIGH - indicates systemic issue
</strategic_planning_examples>
"""

FEW_SHOT_REFLECTION_STRATEGY = """
<reflection_examples>
Cycle 3 Reflection:
- Signals reduced from 5 to 2 ✓
- No new regressions ✓
- Quality improved 0.72 → 0.78 ✓
- Strategy: Temperature reduction worked
Decision: CONTINUE_NEXT_CYCLE

Cycle 5 Reflection:
- Signals increased from 2 to 4 ✗
- TEST_FAILURE appeared (regression) ✗
- Quality dropped 0.78 → 0.65 ✗
- Strategy: Aggressive refactoring caused instability
Decision: ROLLBACK_LAST_CHANGE_AND_RETRY

Cycle 8 Reflection:
- Same 3 signals persisting across cycles ✗
- No improvement despite multiple strategies ✗
- Consecutive failures: 4
Decision: ESCALATE_TO_HUMAN_WITH_REPORT
</reflection_examples>
"""

FEW_SHOT_GLOBAL_REFACTOR = """
<global_refactor_examples>
Example 1: Consolidating duplicate validation logic
Files affected: validators/base.py, validators/resume.py, validators/outreach.py
Change: Extract common validation to shared base class
Impact: Reduced code duplication by 40%, single source of truth

Example 2: Migrating to new signal system
Files affected: All orchestrators and agents
Change: Replace ad-hoc error handling with SignalBus emission
Impact: Unified error handling, better observability

Example 3: Adding type hints across module
Files affected: 15 files in apps_shared/
Change: Add PEP 484 type hints to all public functions
Impact: Better IDE support, catch type errors early
</global_refactor_examples>
"""

# =============================================================================
# RESUME ENGINE SPECIFIC PATTERNS
# =============================================================================

FEW_SHOT_RESUME_BULLETS = """
<resume_bullet_examples>
Example 1: Weak bullet with vague impact
Input: "Managed team and improved processes"
Output: "Led cross-functional team of 12 engineers, delivering $2.3M infrastructure modernization project 15% under budget while reducing deployment time by 60%"
Explanation: Added team size, specific project, quantified budget impact, and measurable outcome.

Example 2: Missing metrics
Input: "Improved sales performance significantly"
Output: "Increased quarterly sales by 34% ($1.2M) through strategic account management and implementation of data-driven targeting, resulting in 28% higher customer retention"
Explanation: Added percentage, dollar amount, methodology, and secondary metric.

Example 3: Technical achievement without business context
Input: "Built microservices architecture"
Output: "Architected event-driven microservices platform processing 50K+ transactions/second, reducing system latency by 75% and enabling $5M annual cost savings through improved resource utilization"
Explanation: Added scale metrics, performance improvement, and business value.

Example 4: Leadership without scope
Input: "Led digital transformation initiative"
Output: "Spearheaded enterprise-wide digital transformation across 5 business units (2,000+ employees), delivering 40% operational efficiency gains and $8M annual savings through process automation and cloud migration"
Explanation: Added scope (units, employees), quantified efficiency gains, and total impact.
</resume_bullet_examples>
"""

FEW_SHOT_EXECUTIVE_SUMMARY = """
<executive_summary_examples>
Example 1: Technical Leader
Input context: Software architect with 15 years experience, cloud expertise, team leadership
Output: "Strategic technology leader with 15+ years architecting enterprise-scale cloud solutions. Proven track record of building and mentoring high-performing engineering teams while delivering $50M+ in documented business value through digital transformation initiatives. Expert in translating complex technical challenges into scalable, cost-effective solutions that drive measurable business outcomes."

Example 2: Product Manager
Input context: PM with B2B SaaS experience, data-driven, cross-functional leadership
Output: "Results-driven Product Manager with deep B2B SaaS expertise, specializing in data-informed product strategy that drives user engagement and revenue growth. Track record of launching 12+ successful products generating $25M ARR, while leading cross-functional teams of 30+ across engineering, design, and marketing. Combines technical fluency with business acumen to identify market opportunities and deliver customer-centric solutions."

Example 3: Operations Executive
Input context: COO background, scaling startups, process optimization
Output: "Operational excellence leader with proven success scaling high-growth startups from Series A to IPO-readiness. Expert in building scalable processes, optimizing unit economics, and driving 3x revenue growth while maintaining operational efficiency. Known for building world-class teams and establishing the operational infrastructure that enables sustainable hypergrowth."
</executive_summary_examples>
"""

FEW_SHOT_METRIC_BINDING = """
<metric_binding_examples>
Example 1: Revenue metric
Metric: "$2.3M revenue increase"
Evidence ID: EXP-2023-Q4-SALES
Binding: "Drove $2.3M revenue increase [EXP-2023-Q4-SALES] through implementation of predictive analytics platform"
Validation: ✓ Metric linked to verifiable experience record

Example 2: Efficiency metric
Metric: "60% reduction in processing time"
Evidence ID: PROJ-AUTOMATION-2022
Binding: "Achieved 60% reduction in processing time [PROJ-AUTOMATION-2022] by redesigning workflow automation pipeline"
Validation: ✓ Metric linked to specific project

Example 3: Team metric
Metric: "Team of 25 engineers"
Evidence ID: ROLE-ENGINEERING-DIRECTOR
Binding: "Built and led team of 25 engineers [ROLE-ENGINEERING-DIRECTOR] across 3 product lines"
Validation: ✓ Metric linked to role record

INVALID Example:
Metric: "Significant cost savings"
Evidence ID: None
Issue: Vague metric with no evidence binding - REJECT
</metric_binding_examples>
"""

# =============================================================================
# OUTREACH ENGINE SPECIFIC PATTERNS
# =============================================================================

FEW_SHOT_OUTREACH_PERSONALIZATION = """
<outreach_personalization_examples>
Example 1: C-Level Executive
Context: CEO of fintech startup, recently raised Series B, expanding engineering
Input: Generic outreach about job opportunity
Output: "Hi [Name], Congratulations on the Series B - the $45M raise positions [Company] perfectly for the infrastructure scaling challenges ahead. Having led similar growth phases at [Previous Company], I've seen firsthand how critical the next 18 months of technical decisions are. I'd welcome the chance to discuss how my experience building platforms that scaled from 10K to 2M users could support your expansion goals."
Personalization elements: Funding milestone, growth stage awareness, relevant experience mapping

Example 2: VP of Engineering
Context: VP Eng at enterprise SaaS, recent acquisition, team integration challenges
Input: Generic networking request
Output: "Hi [Name], The [Acquirer] integration must be keeping your team busy - merging engineering cultures while maintaining velocity is one of the toughest challenges in our field. I led a similar integration at [Company] where we consolidated 4 engineering teams (120+ engineers) while actually improving our release cadence. Would love to share some lessons learned over coffee."
Personalization elements: Current challenge acknowledgment, directly relevant experience, low-commitment ask

Example 3: Recruiter
Context: Senior recruiter at FAANG, hiring for ML platform team
Input: Application follow-up
Output: "Hi [Name], Following up on my application for the ML Platform role. I noticed the team recently open-sourced [Project] - the approach to distributed training optimization aligns closely with work I led at [Company] that reduced training costs by 40%. I've attached a brief technical summary of that project. Happy to discuss how this experience maps to your team's current challenges."
Personalization elements: Team awareness, technical relevance, value-add attachment
</outreach_personalization_examples>
"""

FEW_SHOT_OUTREACH_HOOKS = """
<outreach_hook_examples>
Example 1: Achievement-based hook
"Your team's work on [specific project] caught my attention - the approach to [technical detail] is exactly the kind of innovation I've been focused on."

Example 2: Mutual connection hook
"[Mutual connection] mentioned you're building out the [team/initiative] - their description of the technical challenges immediately resonated with my experience at [Company]."

Example 3: Content-based hook
"Your recent talk at [Conference] on [topic] articulated something I've been thinking about for years. The point about [specific insight] particularly resonated."

Example 4: Company milestone hook
"Congratulations on [milestone] - that kind of growth creates fascinating scaling challenges. I've navigated similar inflection points at [Company] and would love to exchange notes."

Example 5: Industry insight hook
"The shift toward [trend] that [Company] is leading will reshape how we think about [domain]. Having worked on early implementations of this at [Company], I'm excited about where you're taking it."
</outreach_hook_examples>
"""

FEW_SHOT_OUTREACH_CTA = """
<outreach_cta_examples>
Example 1: Low commitment (networking)
"Would you have 15 minutes for a virtual coffee? I'm genuinely curious about your approach to [specific challenge]."

Example 2: Medium commitment (opportunity discussion)
"If you're open to it, I'd welcome a conversation about how my experience with [relevant skill] could support [Company]'s goals. Would next week work for a brief call?"

Example 3: High commitment (formal application)
"I've formally applied through your careers page, but wanted to reach out directly given the strong alignment between my background and this role. I'm available for an initial conversation at your convenience."

Example 4: Value-add CTA
"I've put together a brief analysis of [relevant topic] based on my experience - happy to share if useful. Either way, would enjoy connecting."

Example 5: Referral request
"If this isn't the right fit, I'd appreciate any guidance on who else at [Company] might be working on [area]. Always looking to expand my network in this space."
</outreach_cta_examples>
"""

# =============================================================================
# VALIDATION AND QUALITY PATTERNS
# =============================================================================

FEW_SHOT_QUALITY_CRITIQUE = """
<quality_critique_examples>
Example 1: Resume bullet critique
Input: "Responsible for managing customer relationships"
Issues:
- Passive voice ("responsible for")
- No quantification
- Vague scope
Improved: "Cultivated relationships with 50+ enterprise accounts ($15M portfolio), achieving 95% retention rate and 40% upsell conversion"

Example 2: Outreach message critique
Input: "I saw your company is hiring and I think I'd be a good fit"
Issues:
- No personalization
- No value proposition
- Generic opener
Improved: "Your recent expansion into [market] aligns with my 5 years building [relevant product] at [Company]. I'd bring specific expertise in [skill] that could accelerate your [goal]."

Example 3: Executive summary critique
Input: "Experienced professional with strong skills in various areas"
Issues:
- No specificity
- No metrics
- No unique value proposition
Improved: "Data engineering leader with 12 years building petabyte-scale analytics platforms. Track record of reducing infrastructure costs by 50% while improving query performance 10x at companies including [Notable Companies]."
</quality_critique_examples>
"""

# =============================================================================
# LIBRARY ACCESS FUNCTIONS
# =============================================================================

class FewShotLibrary:
    """
    Central library for few-shot examples.

    Provides easy access to all few-shot patterns with filtering
    and combination capabilities.
    """

    # Core Canon Validator patterns
    SHERLOCK = FEW_SHOT_SHERLOCK
    GITOPS = FEW_SHOT_GITOPS
    STRATEGIC = FEW_SHOT_STRATEGIC
    REFLECTION_STRATEGY = FEW_SHOT_REFLECTION_STRATEGY
    GLOBAL_REFACTOR = FEW_SHOT_GLOBAL_REFACTOR

    # Resume Engine patterns
    RESUME_BULLETS = FEW_SHOT_RESUME_BULLETS
    EXECUTIVE_SUMMARY = FEW_SHOT_EXECUTIVE_SUMMARY
    METRIC_BINDING = FEW_SHOT_METRIC_BINDING

    # Outreach Engine patterns
    OUTREACH_PERSONALIZATION = FEW_SHOT_OUTREACH_PERSONALIZATION
    OUTREACH_HOOKS = FEW_SHOT_OUTREACH_HOOKS
    OUTREACH_CTA = FEW_SHOT_OUTREACH_CTA

    # Quality patterns
    QUALITY_CRITIQUE = FEW_SHOT_QUALITY_CRITIQUE

    @classmethod
    def get_all_patterns(cls) -> Dict[str, str]:
        """Get all available patterns."""
        return {
            "sherlock": cls.SHERLOCK,
            "gitops": cls.GITOPS,
            "strategic": cls.STRATEGIC,
            "reflection_strategy": cls.REFLECTION_STRATEGY,
            "global_refactor": cls.GLOBAL_REFACTOR,
            "resume_bullets": cls.RESUME_BULLETS,
            "executive_summary": cls.EXECUTIVE_SUMMARY,
            "metric_binding": cls.METRIC_BINDING,
            "outreach_personalization": cls.OUTREACH_PERSONALIZATION,
            "outreach_hooks": cls.OUTREACH_HOOKS,
            "outreach_cta": cls.OUTREACH_CTA,
            "quality_critique": cls.QUALITY_CRITIQUE,
        }

    @classmethod
    def get_resume_patterns(cls) -> Dict[str, str]:
        """Get Resume Engine specific patterns."""
        return {
            "resume_bullets": cls.RESUME_BULLETS,
            "executive_summary": cls.EXECUTIVE_SUMMARY,
            "metric_binding": cls.METRIC_BINDING,
            "quality_critique": cls.QUALITY_CRITIQUE,
        }

    @classmethod
    def get_outreach_patterns(cls) -> Dict[str, str]:
        """Get Outreach Engine specific patterns."""
        return {
            "outreach_personalization": cls.OUTREACH_PERSONALIZATION,
            "outreach_hooks": cls.OUTREACH_HOOKS,
            "outreach_cta": cls.OUTREACH_CTA,
            "quality_critique": cls.QUALITY_CRITIQUE,
        }

    @classmethod
    def get_autonomy_patterns(cls) -> Dict[str, str]:
        """Get core autonomy patterns (Canon Validator)."""
        return {
            "sherlock": cls.SHERLOCK,
            "gitops": cls.GITOPS,
            "strategic": cls.STRATEGIC,
            "reflection_strategy": cls.REFLECTION_STRATEGY,
            "global_refactor": cls.GLOBAL_REFACTOR,
        }

    @classmethod
    def inject_into_prompt(
        cls,
        base_prompt: str,
        patterns: List[str],
        position: str = "prefix"
    ) -> str:
        """
        Inject few-shot patterns into a prompt.

        Args:
            base_prompt: The base prompt to enhance
            patterns: List of pattern names to inject
            position: "prefix" or "suffix"

        Returns:
            Enhanced prompt with few-shot examples
        """
        all_patterns = cls.get_all_patterns()

        injections = []
        for pattern_name in patterns:
            if pattern_name in all_patterns:
                injections.append(all_patterns[pattern_name])

        if not injections:
            return base_prompt

        injection_text = "\n\n".join(injections)

        if position == "prefix":
            return f"{injection_text}\n\n{base_prompt}"
        else:
            return f"{base_prompt}\n\n{injection_text}"


# Convenience function for quick access
def get_few_shot(pattern_name: str) -> Optional[str]:
    """Get a specific few-shot pattern by name."""
    patterns = FewShotLibrary.get_all_patterns()
    return patterns.get(pattern_name)
