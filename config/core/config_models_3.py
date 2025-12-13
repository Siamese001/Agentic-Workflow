"""Dataclass models for config."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class PromptAddendumConfig:
    """Configuration for reasoning prompt addendums."""
    HEADER: str = '\n\n**REASONING IMPLEMENTATION DIRECTIVES (v16.40):**\n\n'
    FOOTER: str = '\nAll directives MUST be followed in the output.\n'
    COT_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [(5, '• MANDATORY: Explore at least {cot} distinct reasoning paths before reaching a conclusion.\n'), (4, '• Explore {cot} different reasoning paths; compare and synthesize insights.\n'), (0, '• Consider multiple reasoning approaches before concluding.\n')])
    TOT_B_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [(5, '• MANDATORY: At each decision point, systematically evaluate {tot_b} different branches/alternatives.\n'), (4, '• Explore {tot_b} decision branches at critical junctures; document tradeoffs.\n'), (0, '• Consider multiple decision branches at key steps.\n')])
    TOT_D_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [(5, '• MANDATORY: Reasoning depth must be {tot_d}+ levels deep with explicit layer separation.\n'), (4, '• Provide {tot_d}-level deep reasoning: foundation → intermediate → advanced → synthesis.\n'), (3, '• Provide {tot_d}-level reasoning with clear progression of thinking.\n'), (0, '• Structure reasoning with clear logical progression.\n')])
    REFLEXION_DIRECTIVES: List[Tuple[int, str]] = field(default_factory=lambda: [(3, '• MANDATORY: Review your answer {max_loops} times, refining on each pass. Document improvements.\n'), (2, '• Review your answer {max_loops} times; improve if refinements are identified.\n'), (1, '• Review and refine your answer at least once.\n')])

@dataclass
class AppConfig:
    """Master application configuration containing all sub-configs."""
    paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    rag: RAGConfig = field(default_factory=lambda: RAGConfig())
    content_constraints: ContentConstraintsConfig = field(default_factory=lambda: ContentConstraintsConfig())
    signal_constraints: SignalControlConfig = field(default_factory=lambda: SignalControlConfig())
    artist: ArtistConfig = field(default_factory=lambda: ArtistConfig.from_json())
    validator: ValidatorConfig = field(default_factory=lambda: ValidatorConfig.from_json())
    prompts: PromptsConfig = field(default_factory=lambda: PromptsConfig.from_json())
    web_rag: WebRagConfig = field(default_factory=WebRagConfig)
    enricher: EnricherConfig = field(default_factory=EnricherConfig)
    comp_config: CompetitiveAnalysisConfig = field(default_factory=CompetitiveAnalysisConfig)

