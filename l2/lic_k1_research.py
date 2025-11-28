from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ResearchOutput:
    hyde_profile: Optional[str]
    rag_sources: List[Dict[str, Any]]
    enriched_context: Dict[str, Any]
    signal_score: float

class LIC_K1_Research:
    def __init__(self, retrieval_plan: Dict[str, Any]):
        self.plan = retrieval_plan
        
    def execute_hyde_enrichment(self, recipient_profile: Dict[str, Any]) -> Optional[str]:
        if not self.plan["hyde_enabled"]:
            return None
            
        trigger_met = (
            recipient_profile.get("about") is None or 
            len(recipient_profile.get("about", "")) < 50
        )
        
        trigger = self.plan["hyde_trigger"]
        if trigger != "missing_about_or_short" or not trigger_met:
            return None
            
        title = recipient_profile.get("title", "")
        company = recipient_profile.get("company", "")
        
        hyde_profile = "Professional with expertise in " + title + " at " + company + ". "
        hyde_profile += "Focuses on strategic initiatives and team leadership. "
        hyde_profile += "Experienced in driving business outcomes and technical innovation."
        
        return hyde_profile
    
    def execute_hybrid_recall(self, recipient_profile: Dict[str, Any], hyde_profile: Optional[str]) -> List[Dict[str, Any]]:
        sources = []
        
        web_queries = [
            f"{recipient_profile.get('title', '')} {recipient_profile.get('company', '')} initiatives",
            f"{recipient_profile.get('company', '')} recent news",
            f"{recipient_profile.get('title', '')} industry trends",
            f"{recipient_profile.get('company', '')} technology stack",
            f"{recipient_profile.get('title', '')} challenges",
            f"{recipient_profile.get('company', '')} competitors"
        ]
        
        for i, query in enumerate(web_queries):
            sources.append({
                "query": query,
                "source_type": "web_search",
                "relevance_score": 0.8 + (i * 0.02),
                "content": f"Research content for {query}",
                "url": f"https://example.com/source{i+1}"
            })
            
        internal_sources = [
            {
                "source_type": "project_knowledge",
                "content": "Internal knowledge about similar roles",
                "relevance_score": 0.9
            },
            {
                "source_type": "conversation_search", 
                "content": "Previous conversation patterns",
                "relevance_score": 0.85
            }
        ]
        
        return sources + internal_sources
    
    def execute_cross_encoder_reranking(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        reranked = []
        
        for source in sources:
            base_score = source["relevance_score"]
            
            if source["source_type"] == "web_search":
                recency_weight = 0.45
                authority_weight = 0.2
                relevance_weight = 0.35
            else:
                recency_weight = 0.3
                authority_weight = 0.4
                relevance_weight = 0.3
                
            final_score = (
                base_score * relevance_weight +
                0.7 * authority_weight +
                0.8 * recency_weight
            )
            
            if final_score >= self.plan["reranking_threshold"]:
                source["reranked_score"] = final_score
                reranked.append(source)
                
        return sorted(reranked, key=lambda x: x["reranked_score"], reverse=True)[:8]
    
    def execute_self_rag(self, sources: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        enriched_sources = []
        max_hops = self.plan["self_rag_max_hops"]
        
        for source in sources[:max_hops]:
            enriched_source = source.copy()
            enriched_source["self_rag_hops"] = min(3, max_hops)
            enriched_source["gap_analysis"] = "Knowledge gaps identified and addressed"
            enriched_sources.append(enriched_source)
            
        return enriched_sources
    
    def calculate_signal_quality(self, sources: List[Dict[str, Any]]) -> float:
        if not sources:
            return 0.0
            
        signal_weights = {
            "web_search": 1.2,
            "project_knowledge": 1.8,
            "conversation_search": 1.5
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for source in sources:
            weight = signal_weights.get(source["source_type"], 1.0)
            score = source.get("reranked_score", source.get("relevance_score", 0.5))
            weighted_score += score * weight
            total_weight += weight
            
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def execute(self, recipient_profile: Dict[str, Any], message_context: Dict[str, Any]) -> ResearchOutput:
        hyde_profile = self.execute_hyde_enrichment(recipient_profile)
        
        raw_sources = self.execute_hybrid_recall(recipient_profile, hyde_profile)
        
        reranked_sources = self.execute_cross_encoder_reranking(raw_sources)
        
        enriched_sources = self.execute_self_rag(reranked_sources, message_context.get("topic", ""))
        
        signal_score = self.calculate_signal_quality(enriched_sources)
        
        enriched_context = {
            "recipient": recipient_profile,
            "hyde_profile": hyde_profile,
            "primary_sources": enriched_sources[:3],
            "supporting_sources": enriched_sources[3:8],
            "signal_quality": signal_score
        }
        
        return ResearchOutput(
            hyde_profile=hyde_profile,
            rag_sources=enriched_sources,
            enriched_context=enriched_context,
            signal_score=signal_score
        )
