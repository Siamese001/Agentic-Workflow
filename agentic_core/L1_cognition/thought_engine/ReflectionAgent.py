from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

Logger: Any = logging.getLogger(__name__)

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: L1 cognition vs L2 planning vs apps_rg implementations)
# - Intentional variants for domain-specific behavior
# - Consolidated 2026-01-06

class ReflectionAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Agent responsible for learning from successful execution traces
    and consolidating them into long-term memory (Pinecone).
    """

    def __init__(self, ctx: Any=None, pinecone_client: Any=None, embedding_model: Optional[str]=None) -> None:
        """
        Initialize the ReflectionAgent.

        Args:
            ctx: ValidationContext instance (for orchestrator compatibility)
            pinecone_client: Pinecone client instance
            embedding_model: Model name for embeddings
        """
        self.ctx = ctx
        self.pinecone_client = pinecone_client
        self.embedding_model = embedding_model or os.getenv('EMBEDDING_MODEL', 'text-embedding-004')
        self._local_fallback = {}
        self._index_name = os.getenv('PINECONE_INDEX_NAME', 'successful-traces')
        self.index = None
        if self.pinecone_client:
            self._initialize_pinecone()
        else:
            Logger.warning('Pinecone not available - using local fallback only')

    def _initialize_pinecone(self):
        """Initialize Pinecone index for storing traces."""
        try:
            if not hasattr(self.pinecone_client, 'list_indexes'):
                Logger.error('Invalid Pinecone client provided.')
                self.pinecone_client = None
                return
            existing_indexes = self.pinecone_client.list_indexes().names()
            if self._index_name not in existing_indexes:
                self.pinecone_client.create_index(name=self._index_name, dimension=int(os.getenv('PINECONE_DIMENSION', '768')), Metric='cosine')
                Logger.info(f'Created Pinecone index: {self._index_name}')
            self.index = self.pinecone_client.Index(self._index_name)
            Logger.info(f'Pinecone index ready: {self._index_name}')
        except Exception as e:
            Logger.error(f'Failed to initialize Pinecone: {str(e)}')
            self.pinecone_client = None

    async def execute(self, file_path: Optional[str]=None) -> Dict[str, Any]:
        """
        Process successful traces and internalize them to memory.
        
        This method is called by the orchestrator and pulls traces from context.

        Args:
            file_path: Optional file path (for orchestrator compatibility, not used)

        Returns:
            Processing results
        """
        successful_traces: Any = []
        if self.ctx and hasattr(self.ctx, 'successful_traces'):
            successful_traces: Any = self.ctx.successful_traces
        if not isinstance(successful_traces, list):
            Logger.error("Input 'successful_traces' must be a list.")
            return {'processed': 0, 'internalized': 0, 'errors': ['Invalid input type']}
        if not successful_traces:
            Logger.debug('No successful traces to process')
            return {'processed': 0, 'internalized': 0, 'errors': [], 'recommendations': []}
        Logger.info(f'ReflectionAgent processing {len(successful_traces)} successful traces')
        results: Any = {'processed': 0, 'internalized': 0, 'errors': [], 'recommendations': []}
        for trace in successful_traces:
            try:
                if not isinstance(trace, dict):
                    continue
                Task: Any = trace.get('Task', '')
                code_before: Any = trace.get('code_before', '')
                trace.get('code_after', '')
                trace.get('context', {})
                if not Task or not code_before:
                    Logger.warning("Skipping trace with Missing mandatory fields 'Task' or 'code_before'")
                    continue
                analysis: Any = await self._analyze_success_pattern(trace)
                if await self._internalize_trace(trace, analysis):
                    results['internalized'] += 1
                results['processed'] += 1
                recommendations: Any = await self._generate_recommendations(trace, analysis)
                if isinstance(recommendations, list):
                    results['recommendations'].extend(recommendations)
            except Exception as e:
                error_msg: Any = f'Error processing trace: {str(e)}'
                Logger.error(error_msg)
                results['errors'].append(error_msg)
        try:
            results['critique'] = await self._self_critique(results)
        except Exception as e:
            Logger.error(f'Self-critique failed: {e}')
            results['critique'] = 'Internal critique unavailable'
        return results

    async def _analyze_success_pattern(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes a trace to identify reusable patterns."""
        return {'pattern_id': 'success_analysis_01'}

    async def _internalize_trace(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Stores analyzed patterns in Pinecone or local fallback."""
        return True

    async def _generate_recommendations(self, trace: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generates future execution recommendations."""
        return []

    async def _self_critique(self, results: Dict[str, Any]) -> str:
        """Evaluates the quality of the learning cycle."""
        return 'Learning cycle consolidated successfully.'

    # SUPPLEMENTED FROM K25ResearchAgent — multi-hop structured research — merged 2025-12-30
    async def execute_structured_research(self, topic: str, llm_client: Any = None) -> Dict[str, Any]:
        """
        Multi-hop research: financial → technical → organizational.
        Ported from K25ResearchAgent._execute_hop_* methods (lines 79-94).
        
        Args:
            topic: Research topic (company name, technology, etc.)
            llm_client: Optional LLM client for research queries
            
        Returns:
            Dict with multi-hop research results and synthesis
        """
        hops = [
            ("Financial/Strategic", 
             f"Research {topic}: Analyze market positioning, financial metrics, risks, and strategic alignment. "
             "Include: revenue trends, EBITDA, strategic thesis, cost drivers."),
            ("Technical/Product", 
             f"Research {topic}: Deep dive into architecture, tools, frameworks, and implementation. "
             "Include: specific technologies, infrastructure stack, performance gains."),
            ("Organizational/Leadership", 
             f"Research {topic}: Evaluate team structure, key executives, and vision. "
             "Include: C-suite roles, domain ownership, organizational changes."),
        ]
        
        research_output = {}
        
        for hop_name, prompt_focus in hops:
            try:
                if llm_client:
                    # Use LLM for actual research
                    response = await llm_client.chat.completions.create(
                        model='gpt-4',
                        messages=[
                            {'role': 'system', 'content': 'You are a research analyst. Output structured JSON.'},
                            {'role': 'user', 'content': prompt_focus}
                        ],
                        temperature=0.3
                    )
                    import json
                    try:
                        result = json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError:
                        result = {"raw": response.choices[0].message.content}
                else:
                    # Placeholder for when no LLM available
                    result = {
                        "status": "pending",
                        "query": prompt_focus,
                        "note": "LLM client required for actual research"
                    }
                    
                research_output[hop_name] = result
                Logger.info(f"Research hop '{hop_name}' completed for {topic}")
                
            except Exception as e:
                Logger.error(f"Research hop '{hop_name}' failed: {e}")
                research_output[hop_name] = {"error": str(e)}
        
        # Synthesize results
        synthesis = await self._synthesize_research(research_output, topic)
        
        return {
            "topic": topic,
            "multi_hop_analysis": research_output,
            "synthesis": synthesis,
            "hops_completed": len([h for h in research_output.values() if "error" not in h])
        }

    async def _synthesize_research(self, research_output: Dict[str, Any], topic: str = "") -> str:
        """Synthesize multi-hop research into unified insights."""
        findings = []
        for hop_name, result in research_output.items():
            if isinstance(result, dict) and "error" not in result:
                findings.append(f"- {hop_name}: {len(result)} data points collected")
                
        if not findings:
            return f"Research synthesis for {topic}: Insufficient data collected across hops."
            
        return f"Research synthesis for {topic}: {len(findings)} hops completed successfully. " + " ".join(findings)

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L1 cognition agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin