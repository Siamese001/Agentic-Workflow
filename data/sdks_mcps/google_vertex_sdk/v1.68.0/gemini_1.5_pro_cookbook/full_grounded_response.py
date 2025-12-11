"""Google Vertex AI v1.68.0 - Gemini 1.5 Pro Grounded Response with Citations
Production client for generating responses with Google Search grounding and citation metadata.
"""

import os
import json
from typing import List, Dict, object, Optional
from vertexai.generative_models import GenerativeModel, Part, Tool
from vertexai.generative_models import grounding as vertex_grounding


class GroundedResponseGenerator:
    """Generates responses with Google Search grounding and citation tracking."""
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model = GenerativeModel("gemini-1.5-pro-002")
    
    def create_grounding_tool(self) -> Tool:
        """Create Google Search grounding tool."""
        return Tool.from_google_search_retrieval(
            vertex_grounding.GoogleSearchRetrieval(
                dynamic_retrieval_config=vertex_grounding.DynamicRetrievalConfig(
                    mode="MODE_DYNAMIC",
                    dynamic_threshold=0.7  # Threshold for automatic grounding
                )
            )
        )
    
    def generate_grounded_response(
        self,
        prompt: str,
        enable_grounding: bool = True,
        max_output_tokens: int = 2048,
        temperature: float = 0.4,
        include_citations: bool = True
    ) -> Dict[str, object]:
        """Generate response with optional grounding and citation extraction.
        
        Args:
            prompt: Input prompt for generation
            enable_grounding: Whether to enable Google Search grounding
            max_output_tokens: Maximum tokens in response
            temperature: Sampling temperature
            include_citations: Whether to extract and include citations
            
        Returns:
            Dictionary with response, grounding metadata, and citations
        """
        # Configure tools
        tools = [self.create_grounding_tool()] if enable_grounding else []
        
        # Generate response
        response = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
            },
            tools=tools,
            stream=False
        )
        
        # Extract grounding information
        grounding_metadata = None
        citations = []
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding_metadata = {
                    "grounding_score": candidate.grounding_metadata.grounding_score,
                    "grounding_supports": []
                }
                
                # Extract grounding supports
                if hasattr(candidate.grounding_metadata, 'grounding_supports'):
                    for support in candidate.grounding_metadata.grounding_supports:
                        grounding_support = {
                            "segment": support.grounding_chunk.segment.text if support.grounding_chunk.segment else "",
                            "score": support.grounding_score,
                            "sources": []
                        }
                        
                        # Extract sources
                        if hasattr(support, 'grounding_chunk') and support.grounding_chunk.web:
                            for source in support.grounding_chunk.web:
                                grounding_support["sources"].append({
                                    "uri": source.uri,
                                    "title": source.title,
                                    "snippet": source.snippet
                                })
                        
                        grounding_metadata["grounding_supports"].append(grounding_support)
        
        # Extract citations if requested
        if include_citations and grounding_metadata:
            citations = self._extract_citations(grounding_metadata)
        
        return {
            "content": response.text,
            "model": "gemini-1.5-pro-002",
            "grounding_enabled": enable_grounding,
            "grounding_metadata": grounding_metadata,
            "citations": citations,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                "candidates_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None
            }
        }
    
    def _extract_citations(self, grounding_metadata: Dict[str, object]) -> List[Dict[str, object]]:
        """Extract structured citations from grounding metadata."""
        citations = []
        seen_sources = set()
        
        for support in grounding_metadata.get("grounding_supports", []):
            for source in support.get("sources", []):
                if source["uri"] not in seen_sources:
                    citation = {
                        "uri": source["uri"],
                        "title": source["title"],
                        "snippet": source["snippet"][:200] + "..." if len(source["snippet"]) > 200 else source["snippet"],
                        "confidence": support["score"],
                        "referenced_text": support["segment"][:100] + "..." if len(support["segment"]) > 100 else support["segment"]
                    }
                    citations.append(citation)
                    seen_sources.add(source["uri"])
        
        return citations
    
    def format_response_with_citations(
        self,
        response_data: Dict[str, object],
        citation_format: str = "footnote"
    ) -> str:
        """Format response with inline citations.
        
        Args:
            response_data: Response data from generate_grounded_response
            citation_format: Format style ("footnote", "parenthetical", "markdown")
            
        Returns:
            Formatted response string with citations
        """
        content = response_data["content"]
        citations = response_data["citations"]
        
        if not citations:
            return content
        
        if citation_format == "footnote":
            # Add footnote markers and references
            formatted = content
            for i, citation in enumerate(citations, 1):
                # Simple approach: add citation numbers at end of relevant sentences
                # In production, you'd use more sophisticated text alignment
                formatted = formatted.replace(".", f" [{i}].", 1)
            
            formatted += "\n\nReferences:\n"
            for i, citation in enumerate(citations, 1):
                formatted += f"[{i}] {citation['title']}. {citation['uri']}\n"
        
        elif citation_format == "parenthetical":
            # Add parenthetical citations
            formatted = content
            for citation in citations:
                title = citation["title"][:30] + "..." if len(citation["title"]) > 30 else citation["title"]
                formatted += f" ({title}, {citation['uri']})"
        
        elif citation_format == "markdown":
            # Add markdown-style citations
            formatted = content
            formatted += "\n\n## Sources\n"
            for citation in citations:
                formatted += f"- [{citation['title']}]({citation['uri']}) - {citation['snippet']}\n"
        
        return formatted


def research_company_with_grounding(
    company_name: str,
    research_aspects: List[str] = None
) -> Dict[str, object]:
    """Research company using Gemini with Google Search grounding.
    
    Args:
        company_name: Name of company to research
        research_aspects: Specific aspects to research (funding, products, news, etc.)
        
    Returns:
        Grounded research results with citations
    """
    if research_aspects is None:
        research_aspects = ["overview", "recent developments", "market position", "key people"]
    
    generator = GroundedResponseGenerator()
    
    research_prompt = f"""Research {company_name} and provide comprehensive information about:
    
    {chr(10).join(f"- {aspect.title()}" for aspect in research_aspects)}
    
    Focus on recent developments, market position, and key insights that would be valuable for business development or recruitment purposes. Include specific data points, metrics, and recent news.
    
    Structure the response with clear sections for each aspect."""
    
    result = generator.generate_grounded_response(
        prompt=research_prompt,
        enable_grounding=True,
        temperature=0.3,
        max_output_tokens=3000
    )
    
    # Format with markdown citations
    formatted_response = generator.format_response_with_citations(
        result, 
        citation_format="markdown"
    )
    
    return {
        "company": company_name,
        "research_aspects": research_aspects,
        "grounded_response": formatted_response,
        "grounding_score": result["grounding_metadata"]["grounding_score"] if result["grounding_metadata"] else None,
        "citation_count": len(result["citations"]),
        "raw_response": result
    }


if __name__ == "__main__":
    # Example usage
    test_companies = [
        "Anthropic",
        "OpenAI", 
        "Google DeepMind"
    ]
    
    print("Google Vertex AI - Grounded Response Demo")
    print("=" * 50)
    
    for company in test_companies:
        print(f"\nResearching: {company}")
        print("-" * 30)
        
        try:
            research = research_company_with_grounding(company)
            
            print(f"Grounding Score: {research['grounding_score']}")
            print(f"Citations: {research['citation_count']}")
            print(f"\n{research['grounded_response'][:500]}...")
            
        except Exception as e:
            print(f"Error researching {company}: {e}")
    
    # Test citation formatting
    print(f"\n{'='*50}")
    print("Testing Citation Formats:")
    
    generator = GroundedResponseGenerator()
    test_response = generator.generate_grounded_response(
        "What are the latest developments in AI large language models?",
        enable_grounding=True
    )
    
    formats = ["footnote", "parenthetical", "markdown"]
    for fmt in formats:
        print(f"\n--- {fmt.upper()} FORMAT ---")
        formatted = generator.format_response_with_citations(test_response, fmt)
        print(formatted[:300] + "..." if len(formatted) > 300 else formatted)
