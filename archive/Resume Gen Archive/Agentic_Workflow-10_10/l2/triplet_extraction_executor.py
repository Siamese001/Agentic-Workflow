"""
Triplet extraction executor for résumé processing knowledge graphs.

Implements L2 executor for transforming unstructured text into structured knowledge graph triplets for résumé enhancement.

Layer: L2 (Execution)
Responsibilities:
- Execute triplet extraction based on L1 plans for résumé data processing
- Parse LLM outputs into structured triplets for résumé knowledge graphs
- Perform entity linking on extracted entities for résumé enhancement
- Return extraction results for workflow coordination

Non-responsibilities:
- Extraction planning (L1)
- Triplet storage (L4)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, UTC
import json
import re

from l4.triplet_store import Triplet, TemporalType, create_triplet, PREDICATES
from l4.entity_resolution import (
    EntityRegistry,
    EntityType,
    EntityMention,
    create_mention,
)


@dataclass
class ExtractionPlan:
    """
    Plan for triplet extraction in résumé processing workflows (from L1).
    
    Defines extraction strategy for converting résumé text to knowledge graph data.
    """
    
    source_text: str
    source_id: str
    extraction_type: str = "general"  # general, resume, job_posting
    
    # Configuration
    extract_skills: bool = True
    extract_experience: bool = True
    extract_education: bool = True
    extract_relationships: bool = True
    
    # Entity resolution
    resolve_entities: bool = True
    min_confidence: float = 0.5
    
    # Context
    user_id: Optional[str] = None
    job_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedStatement:
    """
    Statement extracted from résumé processing text before triplet conversion.
    
    Represents intermediate extraction results for résumé knowledge graph construction.
    """
    
    text: str
    statement_type: str  # skill, experience, education, relationship
    confidence: float
    evidence_span: Tuple[int, int]  # Start and end positions in source
    temporal_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """
    Result of triplet extraction for résumé processing workflows.
    
    Provides structured knowledge graph data extracted from résumé enhancement text.
    """
    
    source_id: str
    triplets: List[Triplet]
    statements: List[ExtractedStatement]
    entity_mentions: List[EntityMention]
    
    # Statistics
    total_extracted: int = 0
    resolved_entities: int = 0
    extraction_time_ms: int = 0
    
    # Errors
    errors: List[str] = field(default_factory=list)


class TripletExtractionExecutor:
    """
    Executor for triplet extraction from résumé processing text.
    
    Uses pattern matching and heuristics for extraction in résumé enhancement workflows.
    In production, this would integrate with an LLM for more sophisticated extraction.
    """
    
    def __init__(
        self,
        entity_registry: Optional[EntityRegistry] = None,
    ):
        """Initialize executor.
        
        Args:
            entity_registry: L4 EntityRegistry for entity resolution
        """
        self.entity_registry = entity_registry or EntityRegistry()
        
        # Skill patterns
        self._skill_patterns = [
            r'(?:proficient|experienced|skilled|expert)\s+(?:in|with)\s+([A-Za-z0-9\s,\+\#]+)',
            r'(?:knowledge|expertise|experience)\s+(?:in|of|with)\s+([A-Za-z0-9\s,\+\#]+)',
            r'(?:technologies|skills|tools):\s*([A-Za-z0-9\s,\+\#\-\/]+)',
            r'([A-Z][a-zA-Z\+\#]*(?:\s+[A-Z][a-zA-Z\+\#]*)*)\s+developer',
        ]
        
        # Experience patterns
        self._experience_patterns = [
            r'(?:worked|employed|served)\s+(?:at|for|with)\s+([A-Za-z0-9\s\-&\.]+?)(?:\s+(?:as|for)|\.|,|$)',
            r'(?:at|@)\s+([A-Z][A-Za-z0-9\s\-&\.]+?)(?:\s+(?:as|since|from)|\.|,|$)',
            r'([A-Z][A-Za-z0-9\s\-&\.]+?)\s+\d{4}\s*[-–]\s*(?:\d{4}|present|current)',
        ]
        
        # Education patterns
        self._education_patterns = [
            r'(?:degree|diploma|certificate)\s+(?:in|from)\s+([A-Za-z\s]+)',
            r'(?:graduated|attended)\s+(?:from)?\s*([A-Za-z\s]+(?:University|College|Institute))',
            r'([A-Z][A-Za-z\s]+(?:University|College|Institute))',
        ]
        
        # Temporal patterns
        self._temporal_patterns = [
            (r'(\d{4})\s*[-–]\s*(?:present|current|now)', 'ongoing'),
            (r'(\d{4})\s*[-–]\s*(\d{4})', 'range'),
            (r'(?:since|from)\s+(\d{4})', 'since'),
            (r'(?:in|during)\s+(\d{4})', 'point'),
        ]
    
    def execute(self, plan: ExtractionPlan) -> ExtractionResult:
        """Execute triplet extraction based on plan.
        
        Args:
            plan: Extraction plan from L1
            
        Returns:
            Extraction result with triplets
        """
        start_time = datetime.now(UTC)
        
        triplets: List[Triplet] = []
        statements: List[ExtractedStatement] = []
        entity_mentions: List[EntityMention] = []
        errors: List[str] = []
        
        # Determine subject entity
        subject = plan.user_id or f"doc_{plan.source_id}"
        
        try:
            # Extract skills
            if plan.extract_skills:
                skill_triplets, skill_statements = self._extract_skills(
                    plan.source_text, subject, plan
                )
                triplets.extend(skill_triplets)
                statements.extend(skill_statements)
            
            # Extract experience
            if plan.extract_experience:
                exp_triplets, exp_statements = self._extract_experience(
                    plan.source_text, subject, plan
                )
                triplets.extend(exp_triplets)
                statements.extend(exp_statements)
            
            # Extract education
            if plan.extract_education:
                edu_triplets, edu_statements = self._extract_education(
                    plan.source_text, subject, plan
                )
                triplets.extend(edu_triplets)
                statements.extend(edu_statements)
            
            # Resolve entities if enabled
            resolved_count = 0
            if plan.resolve_entities:
                for triplet in triplets:
                    # Resolve object entity
                    mention = create_mention(
                        text=triplet.object,
                        entity_type=self._infer_entity_type(triplet.predicate),
                        source_document_id=plan.source_id,
                    )
                    entity_mentions.append(mention)
                    
                    result = self.entity_registry.resolve(mention, plan.min_confidence)
                    if result.resolved_entity:
                        triplet.object = result.resolved_entity.canonical_name
                        triplet.confidence *= result.confidence
                        resolved_count += 1
            
        except Exception as e:
            errors.append(f"Extraction error: {str(e)}")
        
        end_time = datetime.now(UTC)
        extraction_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return ExtractionResult(
            source_id=plan.source_id,
            triplets=triplets,
            statements=statements,
            entity_mentions=entity_mentions,
            total_extracted=len(triplets),
            resolved_entities=resolved_count,
            extraction_time_ms=extraction_time_ms,
            errors=errors,
        )
    
    def _extract_skills(
        self,
        text: str,
        subject: str,
        plan: ExtractionPlan,
    ) -> Tuple[List[Triplet], List[ExtractedStatement]]:
        """Extract skill-related triplets.
        
        Args:
            text: Source text
            subject: Subject entity
            plan: Extraction plan
            
        Returns:
            Tuple of (triplets, statements)
        """
        triplets: List[Triplet] = []
        statements: List[ExtractedStatement] = []
        seen_skills: set = set()
        
        for pattern in self._skill_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                skill_text = match.group(1).strip()
                
                # Split on common delimiters
                skills = re.split(r'[,;/]|\band\b', skill_text)
                
                for skill in skills:
                    skill = skill.strip()
                    if not skill or len(skill) < 2:
                        continue
                    
                    skill_lower = skill.lower()
                    if skill_lower in seen_skills:
                        continue
                    seen_skills.add(skill_lower)
                    
                    # Create statement
                    statement = ExtractedStatement(
                        text=f"{subject} has skill {skill}",
                        statement_type="skill",
                        confidence=0.8,
                        evidence_span=(match.start(), match.end()),
                    )
                    statements.append(statement)
                    
                    # Create triplet
                    triplet = create_triplet(
                        subject=subject,
                        predicate=PREDICATES["has_skill"],
                        obj=skill,
                        temporal_type=TemporalType.DYNAMIC,
                        confidence=0.8,
                        source=plan.source_id,
                        metadata={"extraction_type": plan.extraction_type},
                    )
                    triplets.append(triplet)
        
        return triplets, statements
    
    def _extract_experience(
        self,
        text: str,
        subject: str,
        plan: ExtractionPlan,
    ) -> Tuple[List[Triplet], List[ExtractedStatement]]:
        """Extract experience-related triplets.
        
        Args:
            text: Source text
            subject: Subject entity
            plan: Extraction plan
            
        Returns:
            Tuple of (triplets, statements)
        """
        triplets: List[Triplet] = []
        statements: List[ExtractedStatement] = []
        seen_companies: set = set()
        
        for pattern in self._experience_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                company = match.group(1).strip()
                
                if not company or len(company) < 2:
                    continue
                
                company_lower = company.lower()
                if company_lower in seen_companies:
                    continue
                seen_companies.add(company_lower)
                
                # Extract temporal information
                temporal_info = self._extract_temporal_info(text, match.start(), match.end())
                
                # Create statement
                statement = ExtractedStatement(
                    text=f"{subject} worked at {company}",
                    statement_type="experience",
                    confidence=0.75,
                    evidence_span=(match.start(), match.end()),
                    temporal_hints=temporal_info,
                )
                statements.append(statement)
                
                # Create triplet
                triplet = create_triplet(
                    subject=subject,
                    predicate=PREDICATES["worked_at"],
                    obj=company,
                    temporal_type=TemporalType.DYNAMIC,
                    confidence=0.75,
                    source=plan.source_id,
                    valid_from=temporal_info.get("start_date"),
                    metadata={
                        "extraction_type": plan.extraction_type,
                        "temporal_info": temporal_info,
                    },
                )
                triplets.append(triplet)
        
        return triplets, statements
    
    def _extract_education(
        self,
        text: str,
        subject: str,
        plan: ExtractionPlan,
    ) -> Tuple[List[Triplet], List[ExtractedStatement]]:
        """Extract education-related triplets.
        
        Args:
            text: Source text
            subject: Subject entity
            plan: Extraction plan
            
        Returns:
            Tuple of (triplets, statements)
        """
        triplets: List[Triplet] = []
        statements: List[ExtractedStatement] = []
        seen_institutions: set = set()
        
        for pattern in self._education_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                institution = match.group(1).strip()
                
                if not institution or len(institution) < 3:
                    continue
                
                inst_lower = institution.lower()
                if inst_lower in seen_institutions:
                    continue
                seen_institutions.add(inst_lower)
                
                # Create statement
                statement = ExtractedStatement(
                    text=f"{subject} attended {institution}",
                    statement_type="education",
                    confidence=0.7,
                    evidence_span=(match.start(), match.end()),
                )
                statements.append(statement)
                
                # Create triplet
                triplet = create_triplet(
                    subject=subject,
                    predicate=PREDICATES["attended"],
                    obj=institution,
                    temporal_type=TemporalType.STATIC,  # Education is typically static
                    confidence=0.7,
                    source=plan.source_id,
                    metadata={"extraction_type": plan.extraction_type},
                )
                triplets.append(triplet)
        
        return triplets, statements
    
    def _extract_temporal_info(
        self,
        text: str,
        start: int,
        end: int,
    ) -> Dict[str, Any]:
        """Extract temporal information near a match.
        
        Args:
            text: Source text
            start: Start of match
            end: End of match
            
        Returns:
            Dictionary with temporal information
        """
        # Look at surrounding context
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context = text[context_start:context_end]
        
        temporal_info: Dict[str, Any] = {}
        
        for pattern, temporal_type in self._temporal_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                temporal_info["type"] = temporal_type
                if temporal_type == "ongoing":
                    temporal_info["start_year"] = int(match.group(1))
                    temporal_info["is_current"] = True
                elif temporal_type == "range":
                    temporal_info["start_year"] = int(match.group(1))
                    temporal_info["end_year"] = int(match.group(2))
                elif temporal_type == "since":
                    temporal_info["start_year"] = int(match.group(1))
                elif temporal_type == "point":
                    temporal_info["year"] = int(match.group(1))
                break
        
        return temporal_info
    
    def _infer_entity_type(self, predicate: str) -> EntityType:
        """Infer entity type from predicate.
        
        Args:
            predicate: Triplet predicate
            
        Returns:
            Inferred entity type
        """
        predicate_to_type = {
            "has_skill": EntityType.SKILL,
            "proficient_in": EntityType.SKILL,
            "certified_in": EntityType.CERTIFICATION,
            "worked_at": EntityType.ORGANIZATION,
            "held_role": EntityType.ROLE,
            "attended": EntityType.EDUCATION,
            "graduated_from": EntityType.EDUCATION,
        }
        return predicate_to_type.get(predicate, EntityType.UNKNOWN)


# =============================================================================
# Extraction Plan Helpers
# =============================================================================

def create_extraction_plan(
    source_text: str,
    source_id: str,
    extraction_type: str = "general",
    user_id: Optional[str] = None,
    job_id: Optional[str] = None,
) -> ExtractionPlan:
    """Create an extraction plan.
    
    Args:
        source_text: Text to extract from
        source_id: Source document ID
        extraction_type: Type of extraction
        user_id: Optional user ID
        job_id: Optional job ID
        
    Returns:
        ExtractionPlan
    """
    return ExtractionPlan(
        source_text=source_text,
        source_id=source_id,
        extraction_type=extraction_type,
        user_id=user_id,
        job_id=job_id,
    )


__all__ = [
    "ExtractionPlan",
    "ExtractedStatement",
    "ExtractionResult",
    "TripletExtractionExecutor",
    "create_extraction_plan",
]
