#!/usr/bin/env python3
"""
Outreach Engine RAG Pipeline v75 - Lift & Shift + Enhanced from LIC
6-stage RAG validation pipeline with HyDE, hybrid recall, cross-encoder reranking, self-RAG, episodic memory, knowledge graph, and few-shot injection
"""

from typing import Dict, List, Optional, Union, Tuple, Union
import re
from datetime import datetime, timedelta

from .models import (
    RAGEvidence, RAGResult, ValidationResult, ValidationSeverity, RAGEngineError
)


class HyDEProcessor:
    """HyDE (Hypothetical Document Embeddings) processor - Enhanced from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.hyde_config = rag_config.get("stage_0_hyde", {})
        self.enabled = self.hyde_config.get("enabled", True)
        self.trigger_conditions = self.hyde_config.get("trigger", {})
        self.constraints = self.hyde_config.get("constraints", {})
        self.validation_rules = self.hyde_config.get("validation", {})
        self.max_retries = self.validation_rules.get("max_retries", 3)
    
    def should_trigger_hyde(self, recipient_profile: Dict[str, object]) -> bool:
        """Determine if HyDE should be triggered based on recipient profile"""
        if not self.enabled:
            return False
        
        about = recipient_profile.get("about", "")
        title = recipient_profile.get("title", "")
        company = recipient_profile.get("company", "")
        
        # Check trigger conditions
        if "recipient_profile.about" in self.trigger_conditions:
            min_length = 50  # Default minimum
            if len(about) < min_length:
                return True
        
        # Additional trigger logic
        if not about or len(about.strip()) < 30:
            return True
        
        return False
    
    def generate_hypothetical_profile(
        self, 
        recipient_profile: Dict[str, object],
        llm_client: Optional[Any] = None
    ) -> Tuple[str, List[ValidationResult]]:
        """Generate hypothetical profile using title + company + domain"""
        validation_results = []
        
        title = recipient_profile.get("title", "")
        company = recipient_profile.get("company", "")
        domain = recipient_profile.get("domain", "")
        
        # Build prompt for hypothetical profile generation
        prompt = f"""
        Generate a brief, professional LinkedIn "About" section for:
        Title: {title}
        Company: {company}
        Domain: {domain}
        
        Requirements:
        - 2-3 sentences maximum
        - Focus on professional responsibilities and expertise
        - NO fabricated employers, dates, or specific achievements
        - Use only the provided title, company, and domain information
        - Professional tone suitable for LinkedIn
        
        Example format:
        "Professional with expertise in [domain] working as [title] at [company]. Focused on [key responsibility areas] and driving [business outcomes]."
        """
        
        # In a real implementation, this would call an LLM
        # For now, return a template-based result
        hypothetical_profile = f"""
        Professional with expertise in {domain} working as {title} at {company}. 
        Focused on delivering strategic value and driving business outcomes in the {domain} space.
        """.strip()
        
        # Validate against forbidden patterns
        validation_results.extend(self._validate_hypothetical_profile(hypothetical_profile))
        
        return hypothetical_profile, validation_results
    
    def _validate_hypothetical_profile(self, profile: str) -> List[ValidationResult]:
        """Validate hypothetical profile against constraints"""
        validation_results = []
        
        forbidden_patterns = self.validation_rules.get("forbidden_patterns", [])
        
        for pattern in forbidden_patterns:
            if re.search(pattern, profile, re.IGNORECASE):
                validation_results.append(ValidationResult(
                    rule_id="HYDE_FORBIDDEN_PATTERN",
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"HyDE profile contains forbidden pattern: {pattern}",
                    details={"profile": profile, "pattern": pattern}
                ))
        
        # Check for fabricated dates
        if re.search(r'\d{4}', profile):
            validation_results.append(ValidationResult(
                rule_id="HYDE_FABRICATED_DATE",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="HyDE profile contains fabricated dates",
                details={"profile": profile}
            ))
        
        return validation_results


class HybridRecall:
    """Hybrid recall system - Lift & Shift from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.recall_config = rag_config.get("stage_1_hybrid_recall", {})
        self.web_search_calls = self.recall_config.get("web_search_calls", 6)
        self.internal_sources = self.recall_config.get("internal_sources", [])
        self.query_types = [
            "recipient background",
            "company initiatives", 
            "industry context",
            "shared connections",
            "recent news",
            "domain expertise"
        ]
    
    def generate_diverse_queries(self, recipient_profile: Dict[str, object], job_context: Optional[Dict] = None) -> List[str]:
        """Generate 6 diverse queries for hybrid recall"""
        queries = []
        name = recipient_profile.get("name", "")
        company = recipient_profile.get("company", "")
        title = recipient_profile.get("title", "")
        domain = recipient_profile.get("domain", "")
        
        # Recipient background
        queries.append(f"{name} {title} {company} professional background experience")
        
        # Company initiatives
        queries.append(f"{company} recent initiatives projects news 2024")
        
        # Industry context
        queries.append(f"{domain} industry trends challenges opportunities 2024")
        
        # Shared connections (if applicable)
        queries.append(f"{name} {company} professional network connections")
        
        # Recent news
        queries.append(f"{company} recent news announcements funding partnerships")
        
        # Domain expertise
        queries.append(f"{title} {domain} expertise skills best practices")
        
        return queries
    
    def simulate_hybrid_recall(self, queries: List[str]) -> List[Dict[str, object]]:
        """Simulate hybrid recall results (in real implementation would call search APIs)"""
        results = []
        
        for i, query in enumerate(queries):
            # Simulate search results with varying relevance
            for j in range(3, 6):  # 3-5 results per query
                result = {
                    "query": query,
                    "content": f"Simulated content for query: {query[:50]}... Result {j+1}",
                    "source": f"source_{i}_{j}",
                    "relevance_score": 0.8 - (j * 0.1),  # Decreasing relevance
                    "authority_score": 0.7 + (j * 0.05),
                    "recency_score": 0.9 - (j * 0.1),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
        
        return results


class CrossEncoderReranker:
    """Cross-encoder reranking - Lift & Shift from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.rerank_config = rag_config.get("stage_2_cross_encoder_reranking", {})
        self.model = self.rerank_config.get("model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.threshold = self.rerank_config.get("threshold", 0.75)
        self.weights = self.rerank_config.get("weights", {})
        self.recency_decay = self.rerank_config.get("recency_decay", "")
        self.anchor_window_days = self.rerank_config.get("anchor_temporal_window_days", 45)
    
    def rerank_results(
        self, 
        raw_results: List[Dict[str, object]], 
        query: str
    ) -> List[RAGEvidence]:
        """Rerank results using cross-encoder scoring"""
        reranked = []
        
        for result in raw_results:
            # Calculate weighted score
            relevance = result.get("relevance_score", 0.5)
            authority = result.get("authority_score", 0.5)
            recency = self._calculate_recency_score(result.get("timestamp", ""))
            
            weighted_score = (
                relevance * self.weights.get("relevance", 0.35) +
                authority * self.weights.get("authority", 0.2) +
                recency * self.weights.get("recency", 0.45)
            )
            
            evidence = RAGEvidence(
                source_type=result.get("source", "unknown"),
                content=result.get("content", ""),
                relevance_score=relevance,
                authority_score=authority,
                recency_score=recency
            )
            
            reranked.append((evidence, weighted_score))
        
        # Sort by weighted score and filter by threshold
        reranked.sort(key=lambda x: x[1], reverse=True)
        filtered_results = [evidence for evidence, score in reranked if score >= self.threshold]
        
        return filtered_results[:8]  # Return top 8 as per specification
    
    def _calculate_recency_score(self, timestamp: str) -> float:
        """Calculate recency score with linear decay"""
        try:
            result_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days_ago = (datetime.now() - result_date).days
            
            if days_ago <= 0:
                return 1.0
            elif days_ago >= self.anchor_window_days:
                return 0.0
            else:
                # Linear decay
                return 1.0 - (days_ago / self.anchor_window_days)
        except (ValueError, TypeError, KeyError):
            return 0.5  # Default for invalid timestamps


class SelfRAGProcessor:
    """Self-RAG processor - Enhanced from LIC (non-hop based)"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.selfrag_config = rag_config.get("stage_3_self_rag", {})
        self.max_iterations = self.selfrag_config.get("max_hops", 6)  # Renamed from hops to iterations
        self.min_iterations = self.selfrag_config.get("min_hops", 2)
        self.gap_triggers = self.selfrag_config.get("hop_trigger", "").split(", ")
    
    def detect_knowledge_gaps(self, current_evidence: List[RAGEvidence], query: str) -> List[str]:
        """Detect knowledge gaps in current evidence"""
        gaps = []
        
        # Check for insufficient evidence
        if len(current_evidence) < 3:
            gaps.append("Insufficient evidence volume")
        
        # Check for low relevance scores
        low_relevance_count = sum(1 for e in current_evidence if e.relevance_score < 0.6)
        if low_relevance_count > len(current_evidence) // 2:
            gaps.append("Low relevance evidence")
        
        # Check for recency issues
        old_evidence_count = sum(1 for e in current_evidence if e.recency_score < 0.5)
        if old_evidence_count > len(current_evidence) // 2:
            gaps.append("Outdated information")
        
        # Check for authority issues
        low_authority_count = sum(1 for e in current_evidence if e.authority_score < 0.6)
        if low_authority_count > len(current_evidence) // 2:
            gaps.append("Low authority sources")
        
        return gaps
    
    def close_knowledge_gaps(self, gaps: List[str], original_query: str) -> List[str]:
        """Generate refined queries to close knowledge gaps"""
        refined_queries = []
        
        for gap in gaps:
            if "insufficient" in gap.lower():
                refined_queries.append(f"{original_query} comprehensive detailed")
            elif "relevance" in gap.lower():
                refined_queries.append(f"{original_query} specific targeted")
            elif "outdated" in gap.lower():
                refined_queries.append(f"{original_query} recent 2024 current")
            elif "authority" in gap.lower():
                refined_queries.append(f"{original_query} official sources expert")
        
        return refined_queries


class EpisodicMemory:
    """Episodic memory retrieval - Lift & Shift from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.episodic_config = rag_config.get("stage_4_episodic_memory", {})
        self.enabled = self.episodic_config.get("enabled", True)
        self.trigger_routes = self.episodic_config.get("trigger", "route == FOLLOW_UP")
        self.max_results = self.episodic_config.get("max_results", 5)
    
    def retrieve_episodic_context(
        self, 
        route: str, 
        sender_id: str, 
        recipient_id: str
    ) -> List[Dict[str, object]]:
        """Retrieve episodic memory from past interactions"""
        if not self.enabled or route != "FOLLOW_UP":
            return []
        
        # In real implementation, would query conversation database
        # For now, return simulated episodic context
        episodic_context = [
            {
                "type": "prior_message",
                "content": "Previous discussion about technical challenges",
                "date": "2024-10-15",
                "relevance": 0.8
            },
            {
                "type": "shared_interest",
                "content": "Common interest in scalable architectures",
                "date": "2024-10-10",
                "relevance": 0.7
            }
        ]
        
        return episodic_context[:self.max_results]


class KnowledgeGraphInjector:
    """Knowledge graph injection - Lift & Shift from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.kg_config = rag_config.get("stage_5_knowledge_graph", {})
        self.enabled = self.kg_config.get("enabled", True)
        self.queries = self.kg_config.get("queries", [])
    
    def inject_knowledge_graph_context(
        self, 
        sender_profile: Dict[str, object], 
        recipient_profile: Dict[str, object]
    ) -> List[Dict[str, object]]:
        """Inject knowledge graph relationship context"""
        if not self.enabled:
            return []
        
        kg_context = []
        
        # Shared connections
        shared_connections = self._find_shared_connections(sender_profile, recipient_profile)
        if shared_connections:
            kg_context.append({
                "type": "shared_connections",
                "content": f"Shared connections: {', '.join(shared_connections)}",
                "relevance": 0.9
            })
        
        # Company relationships
        company_relationships = self._analyze_company_relationships(sender_profile, recipient_profile)
        if company_relationships:
            kg_context.append({
                "type": "company_relationships",
                "content": company_relationships,
                "relevance": 0.8
            })
        
        # Industry overlaps
        industry_overlaps = self._identify_industry_overlaps(sender_profile, recipient_profile)
        if industry_overlaps:
            kg_context.append({
                "type": "industry_overlaps",
                "content": industry_overlaps,
                "relevance": 0.7
            })
        
        return kg_context
    
    def _find_shared_connections(self, sender: Dict, recipient: Dict) -> List[str]:
        """Find shared connections (simulated)"""
        # In real implementation, would query actual network data
        return ["John Smith", "Sarah Johnson"]
    
    def _analyze_company_relationships(self, sender: Dict, recipient: Dict) -> str:
        """Analyze company relationships"""
        sender_company = sender.get("current_company", "")
        recipient_company = recipient.get("company", "")
        
        if sender_company and recipient_company:
            return f"Relationship between {sender_company} and {recipient_company} industry"
        return ""
    
    def _identify_industry_overlaps(self, sender: Dict, recipient: Dict) -> str:
        """Identify industry overlaps"""
        sender_domain = sender.get("domain", "")
        recipient_domain = recipient.get("domain", "")
        
        if sender_domain and recipient_domain and sender_domain == recipient_domain:
            return f"Both in {sender_domain} industry"
        return ""


class FewShotInjector:
    """Few-shot example injector - Lift & Shift from LIC"""
    
    def __init__(self, rag_config: Dict[str, object]):
        self.fewshot_config = rag_config.get("stage_6_few_shot_injection", {})
        self.enabled = self.fewshot_config.get("enabled", True)
        examples_str = self.fewshot_config.get("examples", "3-5")
        # Handle malformed data like "3-5 high" by extracting just the numeric range
        examples_str = examples_str.split()[0]  # Take first part before any spaces
        self.example_count = examples_str.split("-")
    
    def inject_few_shot_examples(self, recipient_type: str) -> List[str]:
        """Inject few-shot examples for similar recipient types"""
        if not self.enabled:
            return []
        
        # Example messages by recipient type
        example_library = {
            "C_LEVEL": [
                "I noticed your company's recent expansion into AI-driven analytics. My experience scaling data platforms at enterprise level could help accelerate your roadmap.",
                "Your leadership in cloud transformation is impressive. I've led similar initiatives that reduced infrastructure costs by 40% while improving performance."
            ],
            "EXECUTIVE": [
                "Your team's focus on operational excellence aligns with my background in process optimization. I've helped teams achieve 25% efficiency gains.",
                "I saw your recent product launch announcement. My experience in go-to-market strategy could help with your expansion plans."
            ],
            "SENIOR_TA": [
                "Your work with microservices architecture is interesting. I've built similar systems that handle 10M+ requests daily with 99.9% uptime.",
                "I noticed your team is using Kubernetes. I've extensive experience with cluster optimization and can share some patterns."
            ],
            "RECRUITER": [
                "Your focus on technical talent matches my background. I've led teams of 15+ engineers and can help assess technical skills.",
                "I see you're working with several startups. My experience across different company sizes could provide valuable context."
            ]
        }
        
        examples = example_library.get(recipient_type, [])
        min_examples = int(self.example_count[0])
        max_examples = int(self.example_count[1]) if len(self.example_count) > 1 else min_examples
        
        return examples[:min(max_examples, len(examples))]


class RAGPipelineV75:
    """Main RAG Pipeline v75 - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, object]):
        self.scenario_rules = lic_capabilities.get("scenario_rules", {})
        self.rag_config = self.scenario_rules.get("rag_pipeline_v75", {})
        
        # Initialize pipeline components
        self.hyde_processor = HyDEProcessor(self.rag_config)
        self.hybrid_recall = HybridRecall(self.rag_config)
        self.reranker = CrossEncoderReranker(self.rag_config)
        self.self_rag = SelfRAGProcessor(self.rag_config)
        self.episodic_memory = EpisodicMemory(self.rag_config)
        self.knowledge_graph = KnowledgeGraphInjector(self.rag_config)
        self.few_shot = FewShotInjector(self.rag_config)
    
    def execute_rag_pipeline(
        self,
        recipient_profile: Dict[str, object],
        sender_profile: Dict[str, object],
        job_context: Optional[Dict] = None,
        route: Optional[str] = None
    ) -> Tuple[RAGResult, List[ValidationResult]]:
        """Execute complete 6-stage RAG pipeline"""
        validation_results = []
        pipeline_start = datetime.now()
        
        # Stage 0: HyDE Processing
        hyde_profile = None
        if self.hyde_processor.should_trigger_hyde(recipient_profile):
            hyde_profile, hyde_validations = self.hyde_processor.generate_hypothetical_profile(recipient_profile)
            validation_results.extend(hyde_validations)
        
        # Stage 1: Hybrid Recall
        queries = self.hybrid_recall.generate_diverse_queries(recipient_profile, job_context)
        raw_results = self.hybrid_recall.simulate_hybrid_recall(queries)
        
        # Stage 2: Cross-Encoder Reranking
        main_query = queries[0] if queries else ""
        reranked_evidence = self.reranker.rerank_results(raw_results, main_query)
        
        # Stage 3: Self-RAG Gap Closure
        gaps = self.self_rag.detect_knowledge_gaps(reranked_evidence, main_query)
        if gaps and len(reranked_evidence) < 8:  # Only iterate if we have room for more evidence
            refined_queries = self.self_rag.close_knowledge_gaps(gaps, main_query)
            for refined_query in refined_queries[:2]:  # Limit iterations
                additional_results = self.hybrid_recall.simulate_hybrid_recall([refined_query])
                additional_reranked = self.reranker.rerank_results(additional_results, refined_query)
                reranked_evidence.extend(additional_reranked[:2])  # Add top 2 from each refined query
        
        # Stage 4: Episodic Memory
        episodic_context = []
        if route:
            episodic_context = self.episodic_memory.retrieve_episodic_context(
                route, 
                sender_profile.get("id", ""), 
                recipient_profile.get("id", "")
            )
        
        # Stage 5: Knowledge Graph Injection
        kg_context = self.knowledge_graph.inject_knowledge_graph_context(sender_profile, recipient_profile)
        
        # Stage 6: Few-Shot Injection
        recipient_type = recipient_profile.get("type", "EXECUTIVE")
        few_shot_examples = self.few_shot.inject_few_shot_examples(recipient_type)
        
        # Calculate processing time
        processing_time = int((datetime.now() - pipeline_start).total_seconds() * 1000)
        
        # Create comprehensive RAG result
        rag_result = RAGResult(
            query=main_query,
            evidence=reranked_evidence,
            confidence_score=self._calculate_overall_confidence(reranked_evidence),
            processing_time_ms=processing_time
        )
        
        # Add contextual information
        rag_result.hyde_profile = hyde_profile
        rag_result.episodic_context = episodic_context
        rag_result.knowledge_graph_context = kg_context
        rag_result.few_shot_examples = few_shot_examples
        
        return rag_result, validation_results
    
    def _calculate_overall_confidence(self, evidence: List[RAGEvidence]) -> float:
        """Calculate overall confidence from evidence"""
        if not evidence:
            return 0.0
        
        # Weighted average of relevance, authority, and recency
        total_score = 0.0
        for ev in evidence:
            total_score += (ev.relevance_score + ev.authority_score + ev.recency_score) / 3
        
        return total_score / len(evidence)
    
    def validate_rag_pipeline(self, rag_result: RAGResult) -> List[ValidationResult]:
        """Validate RAG pipeline results"""
        validation_results = []
        
        # Check evidence count
        if len(rag_result.evidence) < 3:
            validation_results.append(ValidationResult(
                rule_id="INSUFFICIENT_RAG_EVIDENCE",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Only {len(rag_result.evidence)} evidence items found, minimum 3 recommended",
                details={"evidence_count": len(rag_result.evidence)}
            ))
        
        # Check confidence score
        if rag_result.confidence_score < 0.7:
            validation_results.append(ValidationResult(
                rule_id="LOW_RAG_CONFIDENCE",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"RAG confidence {rag_result.confidence_score:.3f} below recommended threshold",
                details={"confidence_score": rag_result.confidence_score}
            ))
        
        return validation_results
    
    def get_pipeline_summary(self) -> Dict[str, object]:
        """Get summary of RAG pipeline configuration"""
        return {
            "pipeline_version": "v75",
            "stages": [
                "HyDE Processing",
                "Hybrid Recall", 
                "Cross-Encoder Reranking",
                "Self-RAG Gap Closure",
                "Episodic Memory",
                "Knowledge Graph Injection",
                "Few-Shot Injection"
            ],
            "hyde_enabled": self.hyde_processor.enabled,
            "max_evidence": 8,
            "reranking_model": self.reranker.model,
            "reranking_threshold": self.reranker.threshold
        }
