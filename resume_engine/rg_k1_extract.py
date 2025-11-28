"""RG K1 Extract - Resume Content Extraction

Incorporated from historical agentic_workflow/l2/rg_k1_extract.py to execute
advanced resume content extraction with section identification and parsing.

This is the first execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ExtractedSection:
    """Individual extracted resume section."""
    section_id: str
    section_name: str
    content: str
    start_position: int
    end_position: int
    confidence_score: float
    extraction_method: str  # "rule_based", "semantic", "hybrid"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionMetrics:
    """Metrics from resume content extraction."""
    total_sections: int
    content_length: int
    extraction_confidence: float
    processing_time_ms: int
    sections_by_method: Dict[str, int]
    quality_score: float


@dataclass
class ExtractionOutput:
    """Complete output from K1 extraction phase."""
    extracted_sections: List[ExtractedSection]
    raw_content: str
    normalized_content: str
    metrics: ExtractionMetrics
    extraction_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK1Extract:
    """K1 Resume Content Extractor - First hop in sequential processing pipeline.
    
    Executes advanced resume content extraction with multiple strategies:
    - Section-based parsing for structured resumes
    - Semantic extraction for unstructured content  
    - Hybrid approach combining both methods
    """
    
    def __init__(self, 
                 extraction_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K1 resume extractor."""
        self.extraction_plan = extraction_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Section patterns
        self.section_patterns: Dict[str, Dict[str, Union[str, int, float, bool]]] = {
            "contact_info": {
                "start": r"(?i)(contact|personal information|contact details)",
                "end": r"(?i)(summary|objective|profile)",
                "priority": 1,
                "required": True
            },
            "summary": {
                "start": r"(?i)(summary|objective|profile|professional summary)",
                "end": r"(?i)(experience|work experience|employment)",
                "priority": 2,
                "required": True
            },
            "experience": {
                "start": r"(?i)(experience|work experience|employment|professional experience)",
                "end": r"(?i)(education|academic|qualification)",
                "priority": 3,
                "required": True
            },
            "education": {
                "start": r"(?i)(education|academic|qualification)",
                "end": r"(?i)(skills|technical skills|competencies|technologies)",
                "priority": 4,
                "required": True
            },
            "skills": {
                "start": r"(?i)(skills|technical skills|competencies|technologies)",
                "end": r"(?i)(projects|portfolio|achievements|certifications)",
                "priority": 5,
                "required": False
            },
            "projects": {
                "start": r"(?i)(projects|portfolio|work samples|case studies)",
                "end": r"(?i)(achievements|awards|certifications|references)",
                "priority": 6,
                "required": False
            },
            "achievements": {
                "start": r"(?i)(achievements|awards|recognition|accomplishments)",
                "end": r"(?i)(certifications|references|additional information)",
                "priority": 7,
                "required": False
            },
        }
        
        # Content quality indicators
        self.quality_indicators: Dict[str, str] = {
            "has_contact_info": r"(?i)email|phone|address|linkedin",
            "has_metrics": r"\d+%|\$\d+|\d+\s+(years?|months?)|increased|decreased|reduced",
            "has_action_verbs": r"(?i)managed|led|developed|implemented|created|designed|optimized",
            "has_dates": r"\d{4}|\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}",
            "has_bullet_points": r"•|·|-*|\*|→"
        }
    
    def extract_resume_content(
        self,
        *,
        resume_input: Dict[str, Any],
        extraction_params: Optional[Dict[str, Any]] = None
    ) -> ExtractionOutput:
        """Execute resume content extraction.
        
        Args:
            resume_input: Raw resume content and metadata
            extraction_params: Extraction strategy and parameters
            
        Returns:
            Complete extraction output with sections and metrics
        """
        extraction_params = extraction_params or {}
        processing_trace: List[Dict[str, Any]] = []
        
        try:
            # 1. Initialize extraction strategy
            strategy = self._initialize_extraction_strategy(extraction_params)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Preprocess resume content
            raw_content = resume_input.get("content", "")
            preprocessed_content = self._preprocess_content(raw_content)
            processing_trace.append({
                "step": "content_preprocessing",
                "original_length": len(raw_content),
                "preprocessed_length": len(preprocessed_content),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Execute extraction based on strategy
            if strategy == "section_based":
                sections = self._extract_sections_rule_based(preprocessed_content)
                extraction_method = "rule_based"
            elif strategy == "semantic":
                sections = self._extract_sections_semantic(preprocessed_content)
                extraction_method = "semantic"
            else:  # hybrid
                sections = self._extract_sections_hybrid(preprocessed_content)
                extraction_method = "hybrid"
            
            processing_trace.append({
                "step": "section_extraction",
                "method": extraction_method,
                "sections_found": len(sections),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Normalize extracted content
            normalized_content = self._normalize_extracted_content(sections)
            processing_trace.append({
                "step": "content_normalization",
                "normalized_length": len(normalized_content),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Calculate extraction metrics
            metrics = self._calculate_extraction_metrics(
                sections, raw_content, normalized_content, extraction_method
            )
            processing_trace.append({
                "step": "metrics_calculation",
                "extraction_confidence": metrics.extraction_confidence,
                "quality_score": metrics.quality_score,
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Build extraction output
            extraction_output = ExtractionOutput(
                extracted_sections=sections,
                raw_content=raw_content,
                normalized_content=normalized_content,
                metrics=metrics,
                extraction_plan={
                    "strategy": strategy,
                    "parameters": extraction_params,
                    "section_patterns_used": list(self.section_patterns.keys())
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 7. Record telemetry (best-effort)
            self._safe_record_telemetry(extraction_output)
            
            return extraction_output
            
        except Exception as e:
            logger.error(f"Resume extraction failed: {e}")
            
            error_output = ExtractionOutput(
                extracted_sections=[],
                raw_content=resume_input.get("content", ""),
                normalized_content="",
                metrics=ExtractionMetrics(0, 0, 0.0, 0, {}, 0.0),
                extraction_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:06Z"
                }]
            )
            
            return error_output
    
    def _initialize_extraction_strategy(self, params: Dict[str, Any]) -> str:
        """Initialize extraction strategy based on parameters."""
        return params.get("strategy", "section_based")
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocess resume content for better extraction."""
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Normalize bullet points
        content = re.sub(r'[•·→]', '•', content)
        content = re.sub(r'\*+', '•', content)
        
        # Normalize section separators
        content = re.sub(r'=+', '=', content)
        content = re.sub(r'-+', '-', content)
        
        return content
    
    def _extract_sections_rule_based(self, content: str) -> List[ExtractedSection]:
        """Extract sections using rule-based pattern matching."""
        sections: List[ExtractedSection] = []
        
        for section_name, patterns in self.section_patterns.items():
            start_pattern = patterns["start"]
            end_pattern = patterns["end"]
            
            matches = list(re.finditer(start_pattern, content))
            
            for match in matches:
                start_pos = match.start()
                end_pos = self._find_section_end(content, start_pos, end_pattern)
                
                section_content = content[start_pos:end_pos].strip()
                
                if len(section_content) > 10:  # Minimum content threshold
                    section = ExtractedSection(
                        section_id=f"{section_name}_{len(sections)}",
                        section_name=section_name,
                        content=section_content,
                        start_position=start_pos,
                        end_position=end_pos,
                        confidence_score=self._calculate_section_confidence(section_content, section_name),
                        extraction_method="rule_based",
                        metadata={
                            "pattern_matched": start_pattern,
                            "match_position": start_pos
                        }
                    )
                    sections.append(section)
        
        return self._deduplicate_sections(sections)
    
    def _extract_sections_semantic(self, content: str) -> List[ExtractedSection]:
        """Extract sections using semantic analysis."""
        sections: List[ExtractedSection] = []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_section = None
        current_content: List[str] = []
        
        for i, paragraph in enumerate(paragraphs):
            # Check if paragraph looks like a section header
            if self._is_section_header(paragraph):
                # Save previous section if exists
                if current_section and current_content:
                    section = ExtractedSection(
                        section_id=f"{current_section}_{len(sections)}",
                        section_name=current_section,
                        content='\n'.join(current_content),
                        start_position=0,  # Not applicable for semantic
                        end_position=0,
                        confidence_score=self._calculate_semantic_confidence(current_content, current_section),
                        extraction_method="semantic",
                        metadata={
                            "paragraph_count": len(current_content),
                            "estimated_position": i
                        }
                    )
                    sections.append(section)
                
                # Start new section
                current_section = self._classify_section_type(paragraph)
                current_content = [paragraph]
            else:
                # Add to current section
                if current_section:
                    current_content.append(paragraph)
                else:
                    # Start with default section
                    current_section = "general"
                    current_content = [paragraph]
        
        # Save last section
        if current_section and current_content:
            section = ExtractedSection(
                section_id=f"{current_section}_{len(sections)}",
                section_name=current_section,
                content='\n'.join(current_content),
                start_position=0,
                end_position=0,
                confidence_score=self._calculate_semantic_confidence(current_content, current_section),
                extraction_method="semantic",
                metadata={
                    "paragraph_count": len(current_content),
                    "final_section": True
                }
            )
            sections.append(section)
        
        return sections
    
    def _extract_sections_hybrid(self, content: str) -> List[ExtractedSection]:
        """Extract sections using hybrid approach combining rule-based and semantic."""
        # Try rule-based first
        rule_based_sections = self._extract_sections_rule_based(content)
        
        # If rule-based didn't find enough sections, supplement with semantic
        if len(rule_based_sections) < 3:
            semantic_sections = self._extract_sections_semantic(content)
            
            # Merge sections, preferring rule-based results
            merged_sections = self._merge_sections(rule_based_sections, semantic_sections)
            return merged_sections
        
        return rule_based_sections
    
    def _find_section_end(self, content: str, start_pos: int, end_pattern: str) -> int:
        """Find the end position of a section."""
        remaining_content = content[start_pos:]
        
        # Look for next section header
        match = re.search(end_pattern, remaining_content[50:])  # Skip current header
        if match:
            return start_pos + 50 + match.start()
        
        # If no next section found, end at content boundary
        return len(content)
    
    def _calculate_section_confidence(self, content: str, section_name: str) -> float:
        """Calculate confidence score for an extracted section."""
        confidence = 0.5  # Base confidence
        
        # Length factor
        if len(content) > 100:
            confidence += 0.2
        elif len(content) > 50:
            confidence += 0.1
        
        # Content quality factors
        for indicator, pattern in self.quality_indicators.items():
            if re.search(pattern, content):
                confidence += 0.05
        
        # Section name relevance
        if section_name in ["experience", "summary", "skills"]:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_semantic_confidence(self, content: List[str], section_name: str) -> float:
        """Calculate confidence score for semantic extraction."""
        confidence = 0.4  # Lower base confidence for semantic
        
        # Content length
        total_length = sum(len(c) for c in content)
        if total_length > 200:
            confidence += 0.2
        elif total_length > 100:
            confidence += 0.1
        
        # Paragraph count
        if len(content) > 3:
            confidence += 0.1
        elif len(content) > 1:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _is_section_header(self, text: str) -> bool:
        """Check if text looks like a section header."""
        # Short text with section-like keywords
        if len(text) < 50 and len(text.split()) < 10:
            section_keywords = [
                "experience", "education", "skills", "summary", "projects",
                "certifications", "achievements", "contact", "objective"
            ]
            return any(keyword in text.lower() for keyword in section_keywords)
        
        return False
    
    def _classify_section_type(self, header_text: str) -> str:
        """Classify section type based on header text."""
        header_lower = header_text.lower()
        
        for section_name, patterns in self.section_patterns.items():
            start_pattern = patterns["start"]
            if re.search(start_pattern, header_lower):
                return section_name
        
        return "general"
    
    def _deduplicate_sections(self, sections: List[ExtractedSection]) -> List[ExtractedSection]:
        """Remove duplicate sections, keeping highest confidence ones."""
        seen_sections: Dict[str, ExtractedSection] = {}
        
        for section in sections:
            key = section.section_name
            if key not in seen_sections or section.confidence_score > seen_sections[key].confidence_score:
                seen_sections[key] = section
        
        return list(seen_sections.values())
    
    def _merge_sections(self, rule_based: List[ExtractedSection], semantic: List[ExtractedSection]) -> List[ExtractedSection]:
        """Merge rule-based and semantic sections."""
        merged = {}
        
        # Add rule-based sections first
        for section in rule_based:
            merged[section.section_name] = section
        
        # Add semantic sections that don't overlap
        for section in semantic:
            if section.section_name not in merged:
                merged[section.section_name] = section
        
        return list(merged.values())
    
    def _normalize_extracted_content(self, sections: List[ExtractedSection]) -> str:
        """Normalize extracted sections into consistent format."""
        normalized_parts = []
        
        # Sort sections by standard order
        section_order = [
            "contact_info", "summary", "experience", "education", 
            "skills", "projects", "certifications", "achievements"
        ]
        
        ordered_sections = {}
        for section in sections:
            order_priority = section_order.index(section.section_name) if section.section_name in section_order else 99
            ordered_sections[order_priority] = section
        
        for priority in sorted(ordered_sections.keys()):
            section = ordered_sections[priority]
            normalized_parts.append(f"## {section.section_name.replace('_', ' ').title()}\n{section.content}\n")
        
        return '\n'.join(normalized_parts)
    
    def _calculate_extraction_metrics(
        self, 
        sections: List[ExtractedSection], 
        raw_content: str, 
        normalized_content: str, 
        extraction_method: str
    ) -> ExtractionMetrics:
        """Calculate extraction performance metrics."""
        total_sections = len(sections)
        content_length = len(normalized_content)
        
        # Calculate overall confidence
        if sections:
            extraction_confidence = sum(s.confidence_score for s in sections) / len(sections)
        else:
            extraction_confidence = 0.0
        
        # Calculate quality score
        quality_score = self._calculate_content_quality(normalized_content)
        
        # Count sections by extraction method
        sections_by_method = {extraction_method: total_sections}
        
        return ExtractionMetrics(
            total_sections=total_sections,
            content_length=content_length,
            extraction_confidence=extraction_confidence,
            processing_time_ms=100,  # Placeholder
            sections_by_method=sections_by_method,
            quality_score=quality_score
        )
    
    def _calculate_content_quality(self, content: str) -> float:
        """Calculate overall content quality score."""
        quality_score = 0.0
        
        # Check for quality indicators
        for indicator, pattern in self.quality_indicators.items():
            if re.search(pattern, content):
                quality_score += 0.1
        
        # Length factor
        if len(content) > 500:
            quality_score += 0.2
        elif len(content) > 200:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _safe_record_telemetry(self, extraction_output: ExtractionOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k1_extract_executed", {
                    "sections_extracted": extraction_output.metrics.total_sections,
                    "extraction_confidence": extraction_output.metrics.extraction_confidence,
                    "quality_score": extraction_output.metrics.quality_score,
                    "success": extraction_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_extraction_summary(self, extraction_output: ExtractionOutput) -> Dict[str, Any]:
        """Get a summary of the extraction execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k1_extract",
            "sections_extracted": extraction_output.metrics.total_sections,
            "extraction_confidence": extraction_output.metrics.extraction_confidence,
            "quality_score": extraction_output.metrics.quality_score,
            "processing_time_ms": extraction_output.metrics.processing_time_ms,
            "success": extraction_output.success
        }
