"""
Executive Strategy Schema Definitions - Pydantic models for K.11, K.12, K.13 agents.

Defines structured outputs for:
- K.11 Shadow Audit: Technical due diligence and SWOT analysis
- K.12 Strategy Roadmap: 30-60-90 day executive plan
- K.13 Interviewer Simulation: Oppositional interview preparation
"""


# ===== K.11 SHADOW AUDIT SCHEMAS =====

class TechStackInference(BaseModel):
    """Inferred technology component from public signals."""
    category: str = Field(
        ...,
        description="e.g., 'Data Warehouse', 'LLM Orchestration', 'CI/CD', 'Frontend Framework'"
    )
    tool_name: str = Field(
        ...,
        description="Inferred tool, e.g., 'Snowflake', 'LangChain', 'GitHub Actions', 'React'"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.0 to 1.0 confidence based on public signals"
    )
    evidence_source: str = Field(
        ...,
        description="Where this was found (e.g.,
            'Engineering Blog 2023',
            'Job posting',
            'GitHub org')"
    )
    maturity_level: Literal["Legacy", "Stable", "Modern", "Cutting-Edge"] = Field(
        ...,
        description="Assessed maturity of the technology"
    )

    @validator('confidence_score')
    def validate_confidence(cls, v):
        """Docstring."""
        if v < 0.3:
            raise ValueError("Confidence score too low for inclusion")
        return v

class TechnicalDebtIndicator(BaseModel):
    """Specific signs of technical debt or issues."""
    area: str = Field(..., description="Area of concern (e.g., 'Data Pipeline', 'Monolith')")
    issue: str = Field(..., description="Specific issue identified")
    severity: Literal["Low",
        "Medium",
        "High",
        "Critical"] = Field(...,
        description="Impact severity")
    evidence: str = Field(..., description="Evidence from public sources")

class TechnicalSWOT(BaseModel):
    """Technical Strengths, Weaknesses, Opportunities, Threats analysis."""
    current_stack: List[TechStackInference] = Field(
        ...,
        min_items=5,
        description="Inferred technology stack"
    )
    suspected_bottlenecks: List[str] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="Likely technical debt or scaling issues based on stack choices"
    )
    gen_ai_maturity_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="1-5 score of actual AI adoption vs hype (1=Buzzword, 5=Production)"
    )
    strategic_opportunity: str = Field(
        ...,
        min_length=50,
        max_length=300,
        description="The 'One Big Thing' the candidate can pitch to fix"
    )
    technical_debt_indicators: List[TechnicalDebtIndicator] = Field(
        default_factory=list,
        description="Specific technical debt findings"
    )
    competitive_advantage: Optional[str] = Field(
        None,
        description="Unique technical advantage they have"
    )

    @validator('strategic_opportunity')
    def validate_opportunity(cls, v):
        """Docstring."""
        if not any(word in v.lower() for word in ['improve',
            'reduce',
            'increase',
            'enable',
            'transform']):
            raise ValueError("Strategic opportunity must be action-oriented")
        return v

# ===== K.12 STRATEGY ROADMAP SCHEMAS =====

class Milestone(BaseModel):
    """Specific milestone in the 30-60-90 day plan."""
    timeframe: Literal["Day 30",
        "Day 60",
        "Day 90"] = Field(...,
        description="When this milestone occurs")
    focus_area: Literal["People",
        "Process",
        "Technology"] = Field(...,
        description="P-P-T framework")
    initiative: str = Field(
        ...,
        min_length=20,
        max_length=200,
        description="The specific action item or project"
    )
    success_metric: str = Field(
        ...,
        min_length=10,
        max_length=100,
        description="Measurable KPI to track success"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        max_items=3,
        description="Prerequisites or dependencies"
    )
    risk_level: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="Risk level of achieving this milestone"
    )

    @validator('success_metric')
    def validate_metric(cls, v):
        """Docstring."""
        # Should contain a number or percentage
        if not any(char.isdigit() for char in v) and '%' not in v:
            raise ValueError("Success metric should be quantifiable")
        return v

class QuickWin(BaseModel):
    """Low-hanging fruit for immediate impact."""
    initiative: str = Field(..., description="Quick win initiative")
    impact: Literal["Low", "Medium", "High"] = Field(..., description="Expected impact")
    effort: Literal["Low", "Medium", "High"] = Field(..., description="Effort required")
    timeline_days: int = Field(..., ge=1, le=30, description="Days to complete")

class StrategyRoadmap(BaseModel):
    """30-60-90 day executive strategy roadmap."""
    executive_summary: str = Field(
        ...,
        min_length=100,
        max_length=500,
        description="High-level vision statement for the role"
    )
    primary_objective: str = Field(
        ...,
        min_length=50,
        max_length=200,
        description="Main objective for the first 90 days"
    )
    milestones: List[Milestone] = Field(
        ...,
        min_items=6,
        max_items=12,
        description="2-4 milestones per timeframe (30/60/90 days)"
    )
    immediate_wins: List[QuickWin] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="Low-hanging fruit to tackle in week 1"
    )
    key_stakeholders: List[str] = Field(
        ...,
        min_items=3,
        max_items=10,
        description="Key stakeholders to engage"
    )
    success_criteria: str = Field(
        ...,
        min_length=50,
        max_length=300,
        description="What success looks like at 90 days"
    )

    @validator('milestones')
    def validate_milestone_distribution(cls, v):
        """Docstring."""
        # Ensure we have milestones for each timeframe
        timeframes = set(m.timeframe for m in v)
        required = {"Day 30", "Day 60", "Day 90"}

        missing = required - timeframes
        if missing:
            raise ValueError(f"Missing milestones for: {missing}")

        return v

# ===== K.13 INTERVIEWER SIMULATION SCHEMAS =====

class InterviewerArchetype(BaseModel):
    """Base interviewer personality archetype."""
    name: str = Field(..., description="Archetype name")
    characteristics: List[str] = Field(..., description="Key personality traits")
    motivations: List[str] = Field(..., description="What drives this interviewer")
    pet_peeves: List[str] = Field(..., description="Things that annoy them")

class PredictedQuestion(BaseModel):
    """Predicted interview question with strategic context."""
    question_text: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The actual question they might ask"
    )
    question_type: Literal[
        "Technical", "Behavioral", "Situational", "Leadership",
        "Cultural", "Strategic", "Problem-Solving"
    ] = Field(..., description="Category of question")
    rationale: str = Field(
        ...,
        min_length=20,
        max_length=200,
        description="Why this interviewer specifically would ask this"
    )
    recommended_angle: str = Field(
        ...,
        min_length=20,
        max_length=300,
        description="The best strategic angle to answer with"
    )
    difficulty: Literal["Easy", "Medium", "Hard", "Killer"] = Field(
        ...,
        description="Difficulty level of this question"
    )
    follow_up_likelihood: Literal["Low", "Medium", "High"] = Field(
        default="Medium",
        description="How likely they are to ask follow-ups"
    )

class InterviewerBias(BaseModel):
    """Specific bias or preference of the interviewer."""
    category: Literal["Technical",
        "Cultural",
        "Experience",
        "Education"] = Field(...,
        description="Type of bias")
    preference: str = Field(..., description="What they prefer")
    aversion: Optional[str] = Field(None, description="What they dislike")
    how_to_leverage: str = Field(..., description="How to use this to your advantage")

class InterviewerProfile(BaseModel):
    """Complete profile of the interviewer for simulation."""
    interviewer_name: str = Field(..., description="Name of the interviewer")
    title: str = Field(..., description="Their job title")
    company_tenure: str = Field(..., description="How long at the company")
    dominant_archetype: Literal[
        "The Builder", "The Academic", "The Politician",
        "The Operator", "The Visionary", "The Pragmatist"
    ] = Field(..., description="Primary interview style")
    key_biases: List[InterviewerBias] = Field(
        ...,
        min_items=2,
        max_items=5,
        description="Biases to align with or avoid"
    )
    kill_chain_questions: List[PredictedQuestion] = Field(
        ...,
        min_items=5,
        max_items=7,
        description="5 hardest questions they will ask"
    )
    conversation_starters: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="Topics they like to open with"
    )
    decision_factors: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="What matters most in their decision"
    )
    red_flags: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="What would immediately disqualify a candidate"
    )

    @validator('kill_chain_questions')
    def validate_question_difficulty(cls, v):
        """Docstring."""
        # Ensure at least 2 "Hard" or "Killer" questions
        hard_questions = [q for q in v if q.difficulty in ["Hard", "Killer"]]
        if len(hard_questions) < 2:
            raise ValueError("Need at least 2 Hard/Killer questions")
        return v

# ===== EXECUTIVE SUMMARY SCHEMA =====

class ExecutiveIntelligenceReport(BaseModel):
    """Combined intelligence report from all three agents."""
    target_company: str = Field(..., description="Company being analyzed")
    position: str = Field(..., description="Position being interviewed for")
    interview_date: Optional[str] = Field(None, description="Scheduled interview date")

    # K.11 Results
    technical_swot: TechnicalSWOT = Field(..., description="Technical analysis")

    # K.12 Results
    strategy_roadmap: StrategyRoadmap = Field(..., description="90-day plan")

    # K.13 Results
    interviewer_profile: Optional[InterviewerProfile] = Field(
        None,
        description="Interviewer simulation (if available)"
    )

    # Executive insights
    key_differentiators: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="Key points that differentiate the candidate"
    )
    risk_mitigation: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="How to address potential concerns"
    )

    generated_at: str = Field(
        default_factory=lambda: "2024-12-13",
        description="Generation timestamp"
    )

# Registry function
def get_executive_schema_registry() -> Dict[str, type]:
    """Get registry of executive strategy schemas.

    Returns:
        Dictionary mapping schema names to Pydantic classes
    """
    return {
        "TechnicalSWOT": TechnicalSWOT,
        "StrategyRoadmap": StrategyRoadmap,
        "InterviewerProfile": InterviewerProfile,
        "ExecutiveIntelligenceReport": ExecutiveIntelligenceReport,
        "TechStackInference": TechStackInference,
        "Milestone": Milestone,
        "PredictedQuestion": PredictedQuestion
    }
