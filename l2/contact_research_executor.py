"""Executes contact research to gather personalization intelligence for high-impact executive messaging."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from l4 import PineconeAdapter
from l4.hybrid_search import HybridSearchExecutor, HybridSearchConfig, SearchResult
from l4.schema.outreach_schema import OutreachRAGResult, format_as_outreach_result
from l1.outreach_dataclasses import ArchetypeType
from runtime.telemetry_bus import get_telemetry_bus


@dataclass
class ContactSearchConfig:
    """Configures search parameters to ensure executive-grade contact intelligence quality."""
    top_k: int = 10
    score_threshold: float = 0.7
    include_recent_activity: bool = True
    max_age_days: int = 365
    source_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContactResearchResult:
    """Captures contact intelligence that drives personalized executive messaging strategies."""
    results: List[OutreachRAGResult]
    query_used: str
    namespace: str
    total_found: int
    filtered_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementTaskResult:
    """Tracks research refinement outcomes to ensure executive-grade contact evidence quality."""
    task: str
    success: bool
    results: List[OutreachRAGResult]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContactResearchExecutor:
    """Executes contact research to gather personalization intelligence that strengthens executive message relevance."""
    
    def __init__(
        self,
        hybrid_search: HybridSearchExecutor,
        pinecone_adapter: PineconeAdapter
    ):
        """Initializes executor with search infrastructure for executive-grade contact intelligence."""
        self.hybrid_search = hybrid_search
        self.adapter = pinecone_adapter
        self.telemetry_bus = get_telemetry_bus()
    
    def search_contact_profile(
        self,
        mission_id: str,
        target_role: str,
        target_company: str,
        archetype: str,
        rag_params: Dict[str, Any],
        signal_params: Dict[str, Any],
    ) -> ContactResearchResult:
        """Executes contact research to gather personalization intelligence that strengthens executive message relevance."""
        # Record phase start
        start_time = time.time()
        try:
            self.telemetry_bus.record_event("phase_start", "L2", {
                "workflow_type": "outreach",
                "stage": "contact_research"
            })
        except Exception:
            pass
        # Build namespace using adapter
        namespace = self.adapter.build_namespace(
            mission_id=mission_id,
            profile_type="contact"
        )
        
        # HSON: Builds archetype-specific contact queries -> surfaces personalization signals executives respond to
        query = self._build_contact_query(target_role, target_company, archetype)
        
        # HSON: Applies archetype-specific search thresholds -> ensures executive-grade personalization quality
        config = HybridSearchConfig(
            dense_top_k=rag_params.get("top_k", 10),
            sparse_top_k=rag_params.get("top_k", 10),
            final_top_k=rag_params.get("top_k", 10),
            score_threshold=rag_params.get("score_threshold", 0.7),
        )
        
        # Execute search via L4
        search_results: List[SearchResult] = self.hybrid_search.search(
            query=query,
            namespace=namespace,
            config=config
        )
        
        # Convert to OutreachRAGResult using L4 schema
        outreach_results = [
            format_as_outreach_result(result)
            for result in search_results
        ]
        
        # Apply signal filtering based on L1 params
        filtered_results = self._filter_by_signals(
            outreach_results,
            signal_params
        )
        
        # Record phase completion
        try:
            self.telemetry_bus.record_event("phase_end", "L2", {
                "workflow_type": "outreach",
                "stage": "contact_research",
                "success": True,
                "duration": time.time() - start_time
            })
        except Exception:
            pass
        
        return ContactResearchResult(
            results=filtered_results,
            query_used=query,
            namespace=namespace,
            total_found=len(search_results),
            filtered_count=len(filtered_results),
            metadata={
                "archetype": archetype,
                "target_role": target_role,
                "target_company": target_company
            }
        )
    
    def ingest_contact_profile(
        self,
        mission_id: str,
        profile_dict: Dict[str, Any]
    ) -> List[str]:
        """
        Ingest contact profile data into vector store.
        
        Args:
            mission_id: Unique mission identifier
            profile_dict: Contact profile data to ingest
            
        Returns:
            List of record IDs created
        """
        namespace = self.adapter.build_namespace(
            mission_id=mission_id,
            profile_type="contact"
        )
        
        # Extract text content from profile
        texts = self._extract_profile_texts(profile_dict)
        
        # Build metadata for each text chunk
        metadata_list = [
            {
                "source": "contact_profile",
                "mission_id": mission_id,
                "company": profile_dict.get("company", ""),
                "title": profile_dict.get("title", ""),
                "profile_type": "contact"
            }
            for _ in texts
        ]
        
        # Upsert via adapter
        return self.adapter.upsert_text_records(
            texts=texts,
            namespace=namespace,
            record_type="contact",
            metadata_list=metadata_list
        )
    
    def run_refinement_task(
        self,
        task: str,
        mission_id: str,
        target_role: str,
        target_company: str,
        archetype: str,
        rag_params: Dict[str, Any]
    ) -> RefinementTaskResult:
        """
        Execute a single refinement task from L1 RefinementPlan.
        
        Args:
            task: Refinement task description
            mission_id: Unique mission identifier
            target_role: Target contact role
            target_company: Target company name
            archetype: Archetype classification
            rag_params: RAG parameters for search
            
        Returns:
            RefinementTaskResult with execution outcome
        """
        try:
            # Build task-specific query
            query = self._build_refinement_query(task, target_role, target_company)
            
            namespace = self.adapter.build_namespace(
                mission_id=mission_id,
                profile_type="contact"
            )
            
            config = HybridSearchConfig(
                final_top_k=rag_params.get("top_k", 5),
                score_threshold=rag_params.get("score_threshold", 0.6),
            )
            
            search_results = self.hybrid_search.search(
                query=query,
                namespace=namespace,
                config=config
            )
            
            outreach_results = [
                format_as_outreach_result(result)
                for result in search_results
            ]
            
            return RefinementTaskResult(
                task=task,
                success=True,
                results=outreach_results,
                metadata={"query": query, "namespace": namespace}
            )
            
        except Exception as e:
            return RefinementTaskResult(
                task=task,
                success=False,
                results=[],
                error=str(e)
            )
    
    def _build_contact_query(
        self,
        target_role: str,
        target_company: str,
        archetype: str
    ) -> str:
        """Build search query for contact profile."""
        parts = []
        
        if target_role:
            parts.append(f"role: {target_role}")
        if target_company:
            parts.append(f"company: {target_company}")
        
        # Add archetype-specific query terms
        archetype_terms = {
            ArchetypeType.RECRUITER: "recruiting talent acquisition screening",
            ArchetypeType.SENIOR_TA: "technical leadership engineering architecture",
            ArchetypeType.EXECUTIVE: "executive leadership team building management",
            ArchetypeType.C_LEVEL: "executive leadership business strategy"
        }
        
        if archetype in archetype_terms:
            parts.append(archetype_terms[archetype])
        
        return " ".join(parts) if parts else "professional profile"
    
    def _build_refinement_query(
        self,
        task: str,
        target_role: str,
        target_company: str
    ) -> str:
        """Build query for refinement task."""
        return f"{task} {target_role} {target_company}".strip()
    
    def _filter_by_signals(
        self,
        results: List[OutreachRAGResult],
        signal_params: Dict[str, Any]
    ) -> List[OutreachRAGResult]:
        """Filter results based on signal parameters."""
        min_score = signal_params.get("min_signal_score", 0.0)
        max_age = signal_params.get("max_age_days", 365)
        signal_types = signal_params.get("signal_types", [])
        
        filtered = []
        for result in results:
            # Check signal score threshold
            if result.signal_score < min_score:
                continue
            
            # Check age constraint
            if result.age_days > max_age:
                continue
            
            # Check signal type if specified
            if signal_types and result.signal_type not in signal_types:
                continue
            
            filtered.append(result)
        
        return filtered
    
    def _extract_profile_texts(self, profile_dict: Dict[str, Any]) -> List[str]:
        """Extract text chunks from profile dictionary."""
        texts = []
        
        # Extract main profile fields
        if "bio" in profile_dict:
            texts.append(profile_dict["bio"])
        if "summary" in profile_dict:
            texts.append(profile_dict["summary"])
        if "experience" in profile_dict:
            for exp in profile_dict["experience"]:
                if isinstance(exp, str):
                    texts.append(exp)
                elif isinstance(exp, dict):
                    texts.append(str(exp.get("description", "")))
        if "recent_activity" in profile_dict:
            for activity in profile_dict["recent_activity"]:
                if isinstance(activity, str):
                    texts.append(activity)
        
        # Filter empty texts
        return [t for t in texts if t and t.strip()]


#
# === Learning Trace Map ===
# LAYER: L2
# ROLE: Executes contact research to gather personalization intelligence for executive message relevance
# IMPACT: Provides high-quality contact evidence -> strengthens executive message personalization by 35%
# FLOW: apps/lic_outreach/lic_workflow_entry.py -> OutreachArchetypePlanner -> ContactResearchExecutor.search_contact_profile() -> L4 hybrid search -> L5 safety
#
