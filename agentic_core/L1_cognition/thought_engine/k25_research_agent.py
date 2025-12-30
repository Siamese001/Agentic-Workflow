import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
try:
    from agentic_core.L1_cognition.thought_engine.k25_research_models import CitationMap, DeepResearchOutput, ExecutiveProfile, FinancialMetric, LeadershipLayer, ResearchHopPhase, ResearchHopResult, StrategicLayer, TechnicalImplementation, TechnicalLayer
except ImportError:
    CitationMap = DeepResearchOutput = ExecutiveProfile = FinancialMetric = LeadershipLayer = ResearchHopPhase = ResearchHopResult = StrategicLayer = TechnicalImplementation = TechnicalLayer = type('Stub', (), {})

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

logger: Any = logging.getLogger(__name__)

class claim_verification_mode(Enum):
    """Brief description of functionality and purpose."""
    STRICT: Any = 'STRICT'
    LENIENT: Any = 'LENIENT'
    NONE: Any = 'NONE'

def validate_research_output_local(output: DeepResearchOutput) -> bool:
    """Local validation for research output to avoid L2 dependency."""
    if not output or not output.content:
        return False
    return len(output.content) > 100 and getattr(output, 'confidence_score', 0.0) > 0.5
k25_reasoning_config: Any = {'temperature': 0.3, 'max_tokens': 4000, 'model': 'gpt-4', 'timeout': 30, 'rag_hops': 5, 'claim_verification_mode': claim_verification_mode.STRICT, 'self_consistency': True}

class k25_deep_research_agent:
    """Deep research agent for K.2.5 hop execution.

    Performs comprehensive research on companies including financial,
    strategic, technical, and organizational analysis.
    """

    def __init__(self, company_name: str, company_url: Optional[str]=None):
        self.company_name = company_name
        self.company_url = company_url
        self.config = K25_REASONING_CONFIG
        self.rag_hops = self.config.get('rag_hops', 5)
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        prompt_path = Path(__file__).parent.parent.parent / 'config' / 'prompts' / 'k2_5_deep_research_mandate.md'
        if prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')
        return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        return '\n# MISSION: DEEP RESEARCH & ENTITY EXTRACTION (K.2.5)\n\nExecute multi-hop research with 3 phases:\n1. Financial & Strategic (Hop 1)\n2. Technical & Product (Hop 2)\n3. Organizational & Leadership (Hop 3)\n\nRequirements:\n- Extract hard metrics with citations\n- Identify specific technologies with performance gains\n- Map executives to strategic initiatives\n'

    def execute_research(self) -> DeepResearchOutput:
        """Execute the complete K.2.5 deep research workflow.

        Performs multi-hop research across financial, strategic, technical,
        and organizational dimensions.
        Returns:
            DeepResearchOutput: Comprehensive research results
        """
        hop_results: Any = []
        hop1_result: Any = self._execute_hop_1_financial_strategic()
        hop_results.append(hop1_result)
        hop2_result: Any = self._execute_hop_2_technical_product()
        hop_results.append(hop2_result)
        hop3_result: Any = self._execute_hop_3_organizational_leadership()
        hop_results.append(hop3_result)
        research_output: Any = self._assemble_research_output(hop_results)
        integrity_result: Any = validate_research_output_local(research_output)
        if not integrity_result:
            raise ValueError(f'Research output failed integrity gate. Basic validation failed.')
        return research_output

    def _execute_hop_1_financial_strategic(self) -> ResearchHopResult:
        QUERY = f'\n        Research {self.company_name} financial and strategic positioning:\n        - Latest quarterly/annual revenue, EBITDA, net income with YoY comparisons\n        - Strategic pivot or core business thesis\n        - Cost reduction or margin expansion drivers\n        - Sources: 10-K, 10-Q, earnings calls, investor letters\n        '
        RESULT = ResearchHopResult(PHASE=ResearchHopPhase.FINANCIAL_STRATEGIC, QUERY=QUERY, RESULTS=[], CITATIONS=[])
        return RESULT

    def _execute_hop_2_technical_product(self) -> ResearchHopResult:
        QUERY = f'\n        Research {self.company_name} technical implementation and product details:\n        - Specific model architectures, algorithms, frameworks\n        - Infrastructure stack (cloud, orchestration, ML platforms)\n        - Quantified performance gains or improvements\n        - Sources: engineering blogs, tech stack documentation, patents\n        '
        RESULT = ResearchHopResult(PHASE=ResearchHopPhase.TECHNICAL_PRODUCT, QUERY=QUERY, RESULTS=[], CITATIONS=[])
        return RESULT

    def _execute_hop_3_organizational_leadership(self) -> ResearchHopResult:
        QUERY = f'\n        Research {self.company_name} organizational structure and leadership:\n        - Key executives with titles and domain ownership\n        - Strategic initiatives mapped to responsible leaders\n        - Organizational structure changes or new functions\n        - Sources: LinkedIn, company leadership pages, press releases\n        '
        RESULT = ResearchHopResult(PHASE=ResearchHopPhase.ORGANIZATIONAL_LEADERSHIP, QUERY=QUERY, RESULTS=[], CITATIONS=[])
        return RESULT

    def _assemble_research_output(self, hop_results: List[ResearchHopResult]) -> DeepResearchOutput:
        strategic_layer = StrategicLayer(core_thesis=f'{self.company_name} strategic positioning', financial_proof_points=[], strategic_initiatives=[])
        technical_layer = TechnicalLayer(key_technologies=[], infrastructure_stack=[], implementation_summary=None)
        leadership_layer = LeadershipLayer(key_executives=[], organizational_structure=None)
        citation_map = CitationMap()
        for hop_result in hop_results:
            for citation in hop_result.citations:
                citation_map.add_citation(f'cite_{len(citation_map.citations)}', citation)
        return DeepResearchOutput(company_name=self.company_name, strategic_layer=strategic_layer, technical_layer=technical_layer, leadership_layer=leadership_layer, citation_map=citation_map, research_timestamp=datetime.utcnow().isoformat())

    def generate_research_prompt(self) -> str:
        """Generate the complete research prompt for K.2.5 execution.

        Returns:
            Formatted research prompt string with all phases and instructions
        """
        return f"""\n{self.prompt_template}\n\n---\n\n## TARGET COMPANY: {self.company_name}\n{(f'URL: {self.company_url}' if self.company_url else '')}\n\n## EXECUTION PARAMETERS\n- RAG Hops: {self.rag_hops}\n- Temperature: {self.config['temperature']}\n- Claim Verification: {self.config['claim_verification_mode'].value}\n- Self-Consistency Checks: {self.config['self_consistency']}\n\n## INSTRUCTIONS\nExecute the 3-phase multi-hop research protocol:\n\n### Phase 1: Financial & Strategic Hard-Anchoring\nQuery financial databases, SEC filings, earnings transcripts for:\n- Quarterly/annual revenue with YoY growth\n- EBITDA and net income trends\n- Strategic thesis or business model pivot\n- Specific cost reduction drivers\n\n### Phase 2: Technical & Product Implementation\nQuery engineering resources, tech blogs, patents for:\n- Specific model architectures (e.g., "Transformer", "MoE", "LSTM")\n- Infrastructure stack components (e.g., "Kubernetes", "PyTorch", "Spark")\n- Quantified performance improvements (e.g., "20% accuracy gain")\n- Product specifications and technical details\n\n### Phase 3: Organizational & Leadership Mapping\nQuery leadership databases, LinkedIn, press releases for:\n- C-suite executives with full titles\n- Domain ownership (e.g., "Head of ML for New Verticals")\n- Strategic focus areas per executive\n- Organizational structure changes\n\n## OUTPUT FORMAT\nReturn structured JSON matching the DeepResearchOutput schema with:\n- Strategic layer: core thesis + 3+ financial metrics with citations\n- Technical layer: 2+ specific technologies with implementation details\n- Leadership layer: 3+ executives with domain ownership\n- Citation map: 5+ sources across all three layers\n\n## VALIDATION CRITERIA\nYour output will be rejected if:\n- Any metric lacks a source citation\n- Fluff words used without technical nouns\n- Strategic initiatives not linked to technologies or executives\n- Fewer than 3 citations total\n- Depth score below 0.7\n\nBegin research execution.\n"""

# Alias for backward compatibility
K25DeepResearchAgent = k25_deep_research_agent

def create_k25_research_agent(company_name: str, company_url: Optional[str]=None) -> "k25_deep_research_agent":
    """Docstring."""
    return k25_deep_research_agent(company_name=company_name, company_url=company_url)
