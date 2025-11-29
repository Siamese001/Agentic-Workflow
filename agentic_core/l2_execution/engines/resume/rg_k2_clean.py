"""RG K2 Clean - Resume Content Cleaning and Normalization

Incorporated from historical agentic_workflow/l2/rg_k2_clean.py to execute
advanced resume content cleaning with text normalization and content cleanup.

This is the second execution phase in the resume generation pipeline:
K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class CleaningOperation:
    """Individual cleaning operation performed on content."""
    operation_id: str
    operation_type: str  # "normalization", "correction", "enhancement"
    original_text: str
    cleaned_text: str
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleaningMetrics:
    """Metrics from resume content cleaning."""
    total_operations: int
    normalization_improvements: int
    corrections_made: int
    enhancements_applied: int
    content_reduction_pct: float
    quality_improvement_score: float
    processing_time_ms: int


@dataclass
class CleaningOutput:
    """Complete output from K2 cleaning phase."""
    cleaned_sections: List[Dict[str, Any]]
    cleaning_operations: List[CleaningOperation]
    cleaned_content: str
    metrics: CleaningMetrics
    cleaning_plan: Dict[str, Any]
    success: bool
    error_message: str
    processing_trace: List[Dict[str, Any]] = field(default_factory=list)


class RGK2Clean:
    """K2 Resume Content Cleaner - Second hop in sequential processing pipeline.
    
    Executes advanced resume content cleaning with multiple strategies:
    - Text normalization and standardization
    - Grammar and spelling corrections
    - Content enhancement and optimization
    - Duplicate removal and consolidation
    """
    
    def __init__(self, 
                 cleaning_plan: Optional[Dict[str, Any]] = None,
                 telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K2 resume cleaner."""
        self.cleaning_plan = cleaning_plan or {}
        self.telemetry_bus = telemetry_bus
        
        # Cleaning patterns and rules
        self.normalization_rules = {
            "whitespace": [
                (r'\s+', ' '),  # Multiple spaces to single
                (r'\n\s*\n', '\n\n'),  # Multiple newlines to double
                (r'\s*\n\s*', ' '),  # Newlines with spaces to single space
                (r'^\s+|\s+$', ''),  # Trim leading/trailing
            ],
            "punctuation": [
                (r'\s*([.,;:!?])\s*', r'\1 '),  # Space around punctuation
                (r'\s*([()])\s*', r' \1 '),  # Space around parentheses
                (r'\.{3,}', '...'),  # Multiple periods to ellipsis
            ],
            "capitalization": [
                (r'\b(i)\b', 'I'),  # Capitalize standalone 'i'
                (r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper()),  # Capitalize after sentence
            ],
            "bullets": [
                (r'[•·→\*]+', '•'),  # Normalize bullets
                (r'•\s*', '• '),  # Ensure space after bullet
                (r'^\s*•\s*', '• '),  # Bullet at start (without flags for now)
            ]
        }
        
        # Common correction patterns
        self.correction_patterns: Dict[str, List[Tuple[str, str]]] = {
            "common_typos": [
                (r'\bteh\b', 'the'),
                (r'\badn\b', 'and'),
                (r'\brecieve\b', 'receive'),
                (r'\bseperate\b', 'separate'),
                (r'\bdefinately\b', 'definitely'),
                (r'\bgoverment\b', 'government'),
                (r'\boccured\b', 'occurred')
            ],
            "punctuation_errors": [
                (r'\s+,\s*', ', '),  # Space around commas
                (r'\s+\.\s*', '. '),  # Space around periods
                (r'\s+;\s*', '; '),  # Space around semicolons
                (r'\s+:\s*', ': ')  # Space around colons
            ],
            "capitalization_errors": [
                (r'\b(i)\b', 'I'),  # Capitalize standalone 'i'
                (r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', lambda m: m.group(1).capitalize()),  # Days of week
                (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', lambda m: m.group(1).capitalize())  # Months
            ]
        }
        
        # Enhancement rules
        self.enhancement_rules: Dict[str, List[Tuple[str, Union[str, Callable]]]] = {
            "action_verbs": [
                (r'\b(responsible for|handled|managed|did|worked on)\b', lambda m: self._suggest_action_verb(m.group(1))),
                (r'\b(was|were|is|are)\s+(\w+ing)\b', lambda m: f"{m.group(2)}"),  # Remove "was/were" and use present tense
                (r'\b(helped|assisted|supported)\b', lambda m: self._strengthen_verb(m.group(1)))
            ],
            "quantify_achievements": [
                (r'\b(improved|increased|decreased|reduced|enhanced)\s+(\w+)\b', lambda m: f"{m.group(1)} {m.group(2)} by X%"),
                (r'\b(managed|led|supervised|coordinated)\s+(\w+)\b', lambda m: f"{m.group(1)} {m.group(2)} of X people/projects"),
                (r'\b(developed|created|built|designed)\s+(\w+)\b', lambda m: f"{m.group(1)} {m.group(2)} resulting in X")
            ],
            "professional_language": [
                (r'\b(stuff|things|stuff like that)\b', lambda m: self._professional_alternative(m.group(1))),
                (r'\b(very|really|quite)\s+(\w+)\b', lambda m: f"{m.group(2)}"),  # Remove weak intensifiers
                (r'\b(a lot of|lots of|many)\s+(\w+)\b', lambda m: f"numerous {m.group(2)}" or f"multiple {m.group(2)}")
            ]
        }
    
    def clean_resume_content(
        self,
        *,
        extraction_output: Any,  # From K1 extraction
        cleaning_params: Optional[Dict[str, Any]] = None
    ) -> CleaningOutput:
        """Execute resume content cleaning.
        
        Args:
            extraction_output: Output from K1 extraction phase
            cleaning_params: Cleaning strategy and parameters
            
        Returns:
            Complete cleaning output with cleaned content and metrics
        """
        cleaning_params = cleaning_params or {}
        processing_trace = []
        
        try:
            # 1. Initialize cleaning strategy
            strategy = self._initialize_cleaning_strategy(cleaning_params)
            processing_trace.append({
                "step": "strategy_initialization",
                "strategy": strategy,
                "timestamp": "2024-01-01T00:00:01Z"
            })
            
            # 2. Extract sections from K1 output
            sections = self._extract_sections_from_output(extraction_output)
            processing_trace.append({
                "step": "section_extraction",
                "sections_count": len(sections),
                "timestamp": "2024-01-01T00:00:02Z"
            })
            
            # 3. Apply cleaning operations to each section
            cleaned_sections = []
            all_operations: List[CleaningOperation] = []
            
            for section in sections:
                cleaned_section, operations = self._clean_section(section, strategy)
                cleaned_sections.append(cleaned_section)
                all_operations.extend(operations)
            
            processing_trace.append({
                "step": "section_cleaning",
                "operations_performed": len(all_operations),
                "timestamp": "2024-01-01T00:00:03Z"
            })
            
            # 4. Reassemble cleaned content
            cleaned_content = self._reassemble_cleaned_content(cleaned_sections)
            processing_trace.append({
                "step": "content_reassembly",
                "final_length": len(cleaned_content),
                "timestamp": "2024-01-01T00:00:04Z"
            })
            
            # 5. Calculate cleaning metrics
            metrics = self._calculate_cleaning_metrics(
                sections, cleaned_sections, all_operations
            )
            processing_trace.append({
                "step": "metrics_calculation",
                "quality_improvement": metrics.quality_improvement_score,
                "timestamp": "2024-01-01T00:00:05Z"
            })
            
            # 6. Build cleaning output
            cleaning_output = CleaningOutput(
                cleaned_sections=cleaned_sections,
                cleaning_operations=all_operations,
                cleaned_content=cleaned_content,
                metrics=metrics,
                cleaning_plan={
                    "strategy": strategy,
                    "parameters": cleaning_params,
                    "rules_applied": list(self.normalization_rules.keys()) + list(self.correction_patterns.keys())
                },
                success=True,
                error_message="",
                processing_trace=processing_trace
            )
            
            # 7. Record telemetry (best-effort)
            self._safe_record_telemetry(cleaning_output)
            
            return cleaning_output
            
        except Exception as e:
            logger.error(f"Resume cleaning failed: {e}")
            
            error_output = CleaningOutput(
                cleaned_sections=[],
                cleaning_operations=[],
                cleaned_content="",
                metrics=CleaningMetrics(0, 0, 0, 0, 0.0, 0.0, 0),
                cleaning_plan={},
                success=False,
                error_message=str(e),
                processing_trace=processing_trace + [{
                    "step": "error",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:06Z"
                }]
            )
            
            return error_output
    
    def _initialize_cleaning_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize cleaning strategy based on parameters."""
        return {
            "normalization_level": params.get("normalization_level", "standard"),
            "correction_intensity": params.get("correction_intensity", "moderate"),
            "enhancement_level": params.get("enhancement_level", "conservative"),
            "remove_duplicates": params.get("remove_duplicates", True),
            "standardize_format": params.get("standardize_format", True)
        }
    
    def _extract_sections_from_output(self, extraction_output: Any) -> List[Dict[str, Any]]:
        """Extract sections from K1 extraction output."""
        if hasattr(extraction_output, 'extracted_sections'):
            return [
                {
                    "section_id": section.section_id,
                    "section_name": section.section_name,
                    "content": section.content,
                    "confidence": section.confidence_score
                }
                for section in extraction_output.extracted_sections
            ]
        elif isinstance(extraction_output, dict):
            return extraction_output.get("extracted_sections", [])
        else:
            return []
    
    def _clean_section(self, section: Dict[str, Any], strategy: Dict[str, Any]) -> Tuple[Dict[str, Any], List[CleaningOperation]]:
        """Clean individual section content."""
        content = section["content"]
        operations: List[CleaningOperation] = []
        
        # 1. Apply normalization
        if strategy["normalization_level"] != "minimal":
            normalized_content, norm_ops = self._apply_normalization(content)
            operations.extend(norm_ops)
            content = normalized_content
        
        # 2. Apply corrections
        if strategy["correction_intensity"] != "none":
            corrected_content, corr_ops = self._apply_corrections(content)
            operations.extend(corr_ops)
            content = corrected_content
        
        # 3. Apply enhancements
        if strategy["enhancement_level"] != "none":
            enhanced_content, enh_ops = self._apply_enhancements(content)
            operations.extend(enh_ops)
            content = enhanced_content
        
        # 4. Remove duplicates if requested
        if strategy["remove_duplicates"]:
            deduped_content, dedup_ops = self._remove_duplicates(content)
            operations.extend(dedup_ops)
            content = deduped_content
        
        # Build cleaned section
        cleaned_section = {
            "section_id": section["section_id"],
            "section_name": section["section_name"],
            "content": content,
            "original_confidence": section["confidence"],
            "cleaning_confidence": self._calculate_cleaning_confidence(content, operations)
        }
        
        return cleaned_section, operations
    
    def _apply_normalization(self, content: str) -> Tuple[str, List[CleaningOperation]]:
        """Apply text normalization rules."""
        operations: List[CleaningOperation] = []
        normalized_content = content
        
        for rule_type, rules in self.normalization_rules.items():
            for pattern, replacement in rules:
                if callable(replacement):
                    # Handle lambda functions
                    def replace_func(match):
                        return replacement(match)
                    new_content = re.sub(pattern, replace_func, normalized_content)
                else:
                    new_content = re.sub(pattern, replacement, normalized_content)
                
                if new_content != normalized_content:
                    operation = CleaningOperation(
                        operation_id=f"norm_{len(operations)}",
                        operation_type="normalization",
                        original_text=normalized_content,
                        cleaned_text=new_content,
                        confidence_score=0.9,
                        metadata={"rule_type": rule_type, "pattern": pattern}
                    )
                    operations.append(operation)
                    normalized_content = new_content
        
        return normalized_content, operations
    
    def _apply_corrections(self, content: str) -> Tuple[str, List[CleaningOperation]]:
        """Apply spelling and grammar corrections."""
        operations: List[CleaningOperation] = []
        corrected_content = content
        
        for correction_type, patterns in self.correction_patterns.items():
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, corrected_content, flags=re.IGNORECASE)
                
                if new_content != corrected_content:
                    operation = CleaningOperation(
                        operation_id=f"corr_{len(operations)}",
                        operation_type="correction",
                        original_text=corrected_content,
                        cleaned_text=new_content,
                        confidence_score=0.8,
                        metadata={"correction_type": correction_type, "pattern": pattern}
                    )
                    operations.append(operation)
                    corrected_content = new_content
        
        return corrected_content, operations
    
    def _apply_enhancements(self, content: str) -> Tuple[str, List[CleaningOperation]]:
        """Apply content enhancements."""
        operations: List[CleaningOperation] = []
        enhanced_content = content
        
        for enhancement_type, patterns in self.enhancement_rules.items():
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
                
                if new_content != enhanced_content:
                    operation = CleaningOperation(
                        operation_id=f"enh_{len(operations)}",
                        operation_type="enhancement",
                        original_text=enhanced_content,
                        cleaned_text=new_content,
                        confidence_score=0.7,
                        metadata={"enhancement_type": enhancement_type, "pattern": pattern}
                    )
                    operations.append(operation)
                    enhanced_content = new_content
        
        return enhanced_content, operations
    
    def _remove_duplicates(self, content: str) -> Tuple[str, List[CleaningOperation]]:
        """Remove duplicate sentences and phrases."""
        operations: List[CleaningOperation] = []
        deduplicated_content = content
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Remove duplicates while preserving order
        seen_sentences = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if sentence_lower not in seen_sentences:
                seen_sentences.add(sentence_lower)
                unique_sentences.append(sentence)
            else:
                operations.append(CleaningOperation(
                    operation_id=f"dup_{len(operations)}",
                    operation_type="duplicate_removal",
                    original_text=sentence,
                    cleaned_text="",
                    confidence_score=1.0,
                    metadata={"duplicate_type": "sentence"}
                ))
        
        # Reassemble content
        deduplicated_content = '. '.join(unique_sentences)
        if deduplicated_content and not deduplicated_content.endswith('.'):
            deduplicated_content += '.'
        
        return deduplicated_content, operations
    
    def _reassemble_cleaned_content(self, sections: List[Dict[str, Any]]) -> str:
        """Reassemble cleaned sections into final content."""
        content_parts = []
        
        # Sort sections by standard order
        section_order = [
            "contact_info", "summary", "experience", "education", 
            "skills", "projects", "certifications", "achievements"
        ]
        
        ordered_sections = {}
        for section in sections:
            section_name = section["section_name"]
            order_priority = section_order.index(section_name) if section_name in section_order else 99
            ordered_sections[order_priority] = section
        
        for priority in sorted(ordered_sections.keys()):
            section = ordered_sections[priority]
            content_parts.append(f"## {section['section_name'].replace('_', ' ').title()}\n{section['content']}\n")
        
        return '\n'.join(content_parts)
    
    def _calculate_cleaning_confidence(self, content: str, operations: List[CleaningOperation]) -> float:
        """Calculate confidence score for cleaned content."""
        base_confidence = 0.7
        
        # Factor in operation success
        if operations:
            avg_operation_confidence = sum(op.confidence_score for op in operations) / len(operations)
            base_confidence += avg_operation_confidence * 0.2
        
        # Factor in content quality
        quality_score = self._assess_content_quality(content)
        base_confidence += quality_score * 0.1
        
        return min(base_confidence, 1.0)
    
    def _assess_content_quality(self, content: str) -> float:
        """Assess quality of cleaned content."""
        quality_score = 0.0
        
        # Check for proper structure
        if '##' in content:  # Has section headers
            quality_score += 0.2
        
        # Check for proper capitalization
        if re.search(r'[.!?]\s+[A-Z]', content):  # Sentences start with capitals
            quality_score += 0.2
        
        # Check for proper spacing
        if not re.search(r'\s{2,}', content):  # No excessive spaces
            quality_score += 0.2
        
        # Check for professional language
        professional_words = ['managed', 'developed', 'implemented', 'achieved', 'optimized']
        if any(word in content.lower() for word in professional_words):
            quality_score += 0.2
        
        # Length factor
        if len(content) > 200:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    def _calculate_cleaning_metrics(
        self, 
        original_sections: List[Dict[str, Any]], 
        cleaned_sections: List[Dict[str, Any]], 
        operations: List[CleaningOperation]
    ) -> CleaningMetrics:
        """Calculate cleaning performance metrics."""
        total_operations = len(operations)
        
        # Count operation types
        normalization_ops = sum(1 for op in operations if op.operation_type == "normalization")
        correction_ops = sum(1 for op in operations if op.operation_type == "correction")
        enhancement_ops = sum(1 for op in operations if op.operation_type == "enhancement")
        
        # Calculate content reduction
        original_length = sum(len(s["content"]) for s in original_sections)
        cleaned_length = sum(len(s["content"]) for s in cleaned_sections)
        content_reduction_pct = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0.0
        
        # Calculate quality improvement
        quality_improvement = self._calculate_quality_improvement(original_sections, cleaned_sections)
        
        return CleaningMetrics(
            total_operations=total_operations,
            normalization_improvements=normalization_ops,
            corrections_made=correction_ops,
            enhancements_applied=enhancement_ops,
            content_reduction_pct=content_reduction_pct,
            quality_improvement_score=quality_improvement,
            processing_time_ms=150  # Placeholder
        )
    
    def _calculate_quality_improvement(self, original_sections: List[Dict[str, Any]], cleaned_sections: List[Dict[str, Any]]) -> float:
        """Calculate quality improvement score."""
        original_quality = sum(self._assess_content_quality(s["content"]) for s in original_sections) / len(original_sections) if original_sections else 0.0
        cleaned_quality = sum(self._assess_content_quality(s["content"]) for s in cleaned_sections) / len(cleaned_sections) if cleaned_sections else 0.0
        
        return cleaned_quality - original_quality
    
    def _safe_record_telemetry(self, cleaning_output: CleaningOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("rg_k2_clean_executed", {
                    "operations_performed": cleaning_output.metrics.total_operations,
                    "corrections_made": cleaning_output.metrics.corrections_made,
                    "quality_improvement": cleaning_output.metrics.quality_improvement_score,
                    "success": cleaning_output.success
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_cleaning_summary(self, cleaning_output: CleaningOutput) -> Dict[str, Any]:
        """Get a summary of the cleaning execution for debugging/telemetry."""
        return {
            "execution_id": "rg_k2_clean",
            "operations_performed": cleaning_output.metrics.total_operations,
            "corrections_made": cleaning_output.metrics.corrections_made,
            "enhancements_applied": cleaning_output.metrics.enhancements_applied,
            "quality_improvement": cleaning_output.metrics.quality_improvement_score,
            "success": cleaning_output.success
        }





