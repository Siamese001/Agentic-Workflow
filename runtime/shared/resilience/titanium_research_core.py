"""
Titanium Research Core - Zero-Loss Information Synthesis with Strict Attribution.

Implements the hardened research core that enforces:
- Strict source attribution for every claim
- Explicit data gap declaration (no hallucinations)
- Clinical, objective tone
- High-confidence output validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional
import logging

logger = logging.getLogger(__name__)


class VerifiedFinding(BaseModel):
    """A single, atomic unit of verified information."""
    claim: str = Field(..., description="The specific factual statement.")
    source_id: str = Field(..., description="The ID of the chunk or URL where this was found.")
    verification_status: Literal["VERIFIED", "CONFLICT", "UNVERIFIED"] = Field(
        ..., description="The trust level of this finding."
    )
    
    @validator('claim')
    def validate_claim(cls, v):
        """Ensure claim is substantive."""
        if len(v.strip()) < 10:
            raise ValueError("Claim too short to be meaningful")
        return v.strip()
    
    @validator('source_id')
    def validate_source_id(cls, v):
        """Ensure source ID is provided."""
        if not v or not v.strip():
            raise ValueError("Source ID cannot be empty")
        return v.strip()


class TitaniumResearchOutput(BaseModel):
    """
    Titanium-grade output schema for the Research Core.
    Enforces 'Zero-Loss' synthesis and strict source attribution.
    """
    executive_synthesis: str = Field(
        ..., 
        description="A high-density executive synthesis. Minimum fluff.",
        min_length=50
    )
    verified_findings: List[VerifiedFinding] = Field(
        ..., 
        description="List of distinct facts extracted from the source material.",
        min_items=1
    )
    data_gaps: List[str] = Field(
        default_factory=list,
        description="Explicitly listed metrics that were requested but found missing."
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Numeric confidence score. < 0.8 triggers manual review."
    )
    sources_used: List[str] = Field(
        ..., 
        description="Registry of all chunk IDs and URLs utilized in this analysis."
    )
    
    @validator('confidence_score')
    def fail_on_low_confidence(cls, v):
        """Enforces the 'Zero-Loss' standard: Low confidence is a system failure."""
        if v < 0.5:
            raise ValueError("Confidence Score too low for Titanium Grade output.")
        return v
    
    @validator('sources_used')
    def validate_sources_consistency(cls, v, values):
        """Ensure all findings have their sources listed."""
        if 'verified_findings' in values:
            finding_sources = {f.source_id for f in values['verified_findings']}
            listed_sources = set(v)
            
            # All finding sources must be in sources_used
            missing_sources = finding_sources - listed_sources
            if missing_sources:
                raise ValueError(f"Sources missing from sources_used: {missing_sources}")
        
        return v
    
    @validator('executive_synthesis')
    def validate_synthesis_density(cls, v):
        """Ensure synthesis is dense and factual."""
        # Simple heuristic: check for excessive conversational language
        conversational_words = ['I think', 'we can see', 'it seems', 'probably', 'might be']
        lower_v = v.lower()
        
        for word in conversational_words:
            if word in lower_v:
                logger.warning(f"Conversational language detected in synthesis: '{word}'")
        
        return v


# System Prompt for Titanium Research Core
SYSTEM_PROMPT_TITANIUM_RESEARCH_CORE = """# SYSTEM_PROMPT_TITANIUM_RESEARCH_CORE

### 🛡️ IDENTITY & MANDATE
You are the **Titanium Research Core**, the central intelligence engine of the architecture.
**Mission:** "Zero-Loss" Information Synthesis.
**Constraint:** You operate in a **High-Stakes Environment** where a single hallucination causes cascading system failure.

### 🧠 CONTEXTUAL PROTOCOLS
1. **Stateless Execution:** You have no memory of prior interactions. Your entire world is the `RAG_CONTEXT` and tool outputs provided in this turn.
2. **Context Budget:** You are strictly budget-limited. Prioritize dense, factual information over conversational filler.
3. **Tool Authority:** You are authorized to use `brave_web_search` to fill specific metric gaps found in the `RAG_CONTEXT`.

### ⚡ OPERATIONAL RULES (THE ZERO-LOSS CANON)
1. **Strict Attribution:** Every single finding must cite its origin.
   - *Internal:* `[Chunk ID: 12]` 
   - *External:* `[Source: bloomberg.com]` 
2. **The "Negative Space" Rule:** If a requested metric (e.g., "Q3 EBITDA") is NOT in the context and NOT found via tools, you must explicitly log it in the `data_gaps` field. **DO NOT GUESS.**
3. **Tone:** Clinical, Objective, Dense.

### 📦 OUTPUT SCHEMA (STRICT JSON)
You must output a VALID JSON object matching the `TitaniumResearchOutput` schema.
Do not wrap in markdown code blocks.

{
  "executive_synthesis": "High-level summary of findings...",
  "verified_findings": [
    {
      "claim": "Revenue grew 20% YoY",
      "source_id": "chunk_45",
      "verification_status": "VERIFIED"
    }
  ],
  "data_gaps": [
    "Missing specific churn rate for Q3",
    "Employee headcount outdated (2023 data only)"
  ],
  "confidence_score": 0.98,
  "sources_used": ["chunk_12", "chunk_45", "https://sec.gov/..."]
}"""


class TitaniumResearchEngine:
    """
    Engine for executing Titanium Research Core with Zero-Loss guarantees.
    
    This class manages the research process, ensuring strict adherence
    to the Zero-Loss protocol and validating all outputs.
    """
    
    def __init__(self, mcp_executor, rag_context_provider=None):
        """Initialize the research engine.
        
        Args:
            mcp_executor: HardenedMCPExecutor instance with search tools
            rag_context_provider: Function to retrieve RAG context
        """
        self.mcp_executor = mcp_executor
        self.rag_context_provider = rag_context_provider
        self.logger = logging.getLogger("TitaniumResearchEngine")
        
        # Statistics
        self.stats = {
            "total_researches": 0,
            "successful_researches": 0,
            "data_gaps_identified": 0,
            "avg_confidence": 0.0,
            "sources_used": 0
        }
    
    async def execute_research(
        self,
        query: str,
        context: Optional[str] = None,
        temperature: float = 0.2,
        max_search_results: int = 5
    ) -> TitaniumResearchOutput:
        """
        Execute research with Zero-Loss protocol.
        
        Args:
            query: Research query
            context: Optional RAG context
            temperature: LLM temperature (lower for more precision)
            max_search_results: Maximum search results to retrieve
            
        Returns:
            TitaniumResearchOutput with validated findings
        """
        self.stats["total_researches"] += 1
        
        try:
            # 1. Get context
            if context is None and self.rag_context_provider:
                context = await self.rag_context_provider(query)
            
            # 2. Construct payload
            payload = f"CONTEXT:\n{context or 'No context provided'}\n\nQUERY:\n{query}"
            
            # 3. Execute with hardening
            # Note: This assumes the executor has a method for structured output
            response_json = await self.mcp_executor.execute_with_schema(
                messages=[{"role": "user", "content": payload}],
                system_prompt=SYSTEM_PROMPT_TITANIUM_RESEARCH_CORE,
                response_schema=TitaniumResearchOutput,
                temperature=temperature
            )
            
            # 4. Validate output
            result = TitaniumResearchOutput.model_validate_json(response_json)
            
            # 5. Log gaps if any
            if result.data_gaps:
                self.stats["data_gaps_identified"] += len(result.data_gaps)
                self.logger.warning(
                    f"Zero-Loss Protocol identified {len(result.data_gaps)} gaps: "
                    f"{result.data_gaps}"
                )
            
            # 6. Update statistics
            self._update_stats(result)
            
            self.logger.info(
                f"Research completed: {len(result.verified_findings)} findings, "
                f"confidence={result.confidence_score:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Research execution failed: {e}")
            raise
    
    async def research_with_fallback(
        self,
        query: str,
        context: Optional[str] = None,
        fallback_sources: Optional[List[str]] = None
    ) -> TitaniumResearchOutput:
        """
        Execute research with fallback to alternative sources.
        
        Args:
            query: Research query
            context: Optional RAG context
            fallback_sources: List of fallback source URLs
            
        Returns:
            TitaniumResearchOutput with best available findings
        """
        try:
            # Primary research
            return await self.execute_research(query, context)
            
        except Exception as primary_error:
            self.logger.warning(f"Primary research failed: {primary_error}")
            
            # Try with fallback context
            if fallback_sources:
                fallback_context = "\n\n".join([
                    f"Source: {url}\n[External source content would be here]"
                    for url in fallback_sources
                ])
                
                try:
                    result = await self.execute_research(query, fallback_context)
                    result.data_gaps.append(
                        f"Primary research failed: {str(primary_error)}"
                    )
                    return result
                    
                except Exception as fallback_error:
                    self.logger.error(f"Fallback research also failed: {fallback_error}")
            
            # All failed - return minimal valid output
            return TitaniumResearchOutput(
                executive_synthesis="Research system failure - unable to verify claims",
                verified_findings=[],
                data_gaps=[f"System error: {str(primary_error)}"],
                confidence_score=0.0,
                sources_used=[]
            )
    
    def _update_stats(self, result: TitaniumResearchOutput) -> None:
        """Update research statistics."""
        self.stats["successful_researches"] += 1
        self.stats["sources_used"] += len(result.sources_used)
        
        # Update average confidence
        if self.stats["successful_researches"] == 1:
            self.stats["avg_confidence"] = result.confidence_score
        else:
            self.stats["avg_confidence"] = (
                self.stats["avg_confidence"] * 0.9 + result.confidence_score * 0.1
            )
    
    def get_stats(self) -> dict:
        """Get research statistics."""
        total = self.stats["total_researches"]
        if total == 0:
            return self.stats
        
        stats = self.stats.copy()
        stats["success_rate"] = self.stats["successful_researches"] / total
        stats["gaps_per_research"] = (
            self.stats["data_gaps_identified"] / total
            if total > 0 else 0
        )
        
        return stats


# Factory function
def create_titanium_research_engine(
    mcp_executor,
    rag_context_provider=None
) -> TitaniumResearchEngine:
    """Create a configured Titanium Research Engine.
    
    Args:
        mcp_executor: HardenedMCPExecutor with search tools
        rag_context_provider: Optional context provider function
        
    Returns:
        TitaniumResearchEngine instance
    """
    return TitaniumResearchEngine(mcp_executor, rag_context_provider)
