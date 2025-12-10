"""
runtime/shared/creative_brief.py
Creative Brief Constraints for Content Generation

Ported from legacy resume gen Job_Workflow_v61.27.json
Implements structured constraints for creative content generation:
  - Word count limits (min/max)
  - Character count limits
  - Structural requirements
  - Forbidden patterns
  - Voice and tense requirements
  - Provenance strategies
"""


import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union


# =============================================================================
# ENUMERATIONS
# =============================================================================

class VoiceType(Enum):
    """Voice types for content generation."""
    FIRST_PERSON = "first_person"
    SECOND_PERSON = "second_person"
    THIRD_PERSON = "third_person"
    THIRD_PERSON_IMPLIED = "third_person_implied"  # No explicit pronouns


class TenseType(Enum):
    """Tense types for content generation."""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    MIXED = "mixed"


class ProvenanceType(Enum):
    """Provenance types for content sourcing."""
    VERBATIM = "Verbatim"      # Direct copy from source
    ADAPTED = "Adapted"        # Modified from source
    SYNTHETIC = "Synthetic"    # Generated new content


class SourcingStrategy(Enum):
    """Strategies for sourcing content."""
    INTERNAL_FIRST = "Internal-First"  # Map -> Adapt -> Gap-Fill
    JD_FIT_BASED = "JD Fit-Based Dynamic Model"
    HYBRID = "Hybrid"
    EXTERNAL_ONLY = "External-Only"


# =============================================================================
# CONSTRAINT DATA CLASSES
# =============================================================================

@dataclass
class WordCountConstraint:
    """Word count constraint with min/max bounds."""
    min_words: int
    max_words: int
    
    def validate(self, text: str) -> Tuple[bool, int, str]:
        """
        Validate text against word count constraint.
        
        Returns:
            Tuple of (is_valid, actual_count, message)
        """
        word_count = len(text.split())
        
        if word_count < self.min_words:
            return (False, word_count, f"Too few words: {word_count} < {self.min_words}")
        elif word_count > self.max_words:
            return (False, word_count, f"Too many words: {word_count} > {self.max_words}")
        else:
            return (True, word_count, f"Word count OK: {word_count}")
    
    def __repr__(self) -> str:
        return f"WordCount({self.min_words}-{self.max_words})"


@dataclass
class CharCountConstraint:
    """Character count constraint."""
    max_chars: int
    min_chars: int = 0
    
    def validate(self, text: str) -> Tuple[bool, int, str]:
        """Validate text against character count constraint."""
        char_count = len(text)
        
        if char_count < self.min_chars:
            return (False, char_count, f"Too few chars: {char_count} < {self.min_chars}")
        elif char_count > self.max_chars:
            return (False, char_count, f"Too many chars: {char_count} > {self.max_chars}")
        else:
            return (True, char_count, f"Char count OK: {char_count}")


@dataclass
class StructureConstraint:
    """Structural constraint for content format."""
    structure: str  # e.g., "Domain | Leadership | Value Prop"
    delimiter: str = "|"
    segment_word_limit: Optional[int] = None
    exclusions: List[str] = field(default_factory=lambda: [
        "and", "a", "an", "the", "in", "on", "at", "for", "to", "of"
    ])
    
    def validate(self, text: str) -> Tuple[bool, List[str], str]:
        """
        Validate text against structural constraint.
        
        Returns:
            Tuple of (is_valid, segments, message)
        """
        segments = [s.strip() for s in text.split(self.delimiter)]
        expected_segments = [s.strip() for s in self.structure.split(self.delimiter)]
        
        if len(segments) != len(expected_segments):
            return (
                False,
                segments,
                f"Wrong segment count: {len(segments)} != {len(expected_segments)}"
            )
            
        # Check segment word limits if specified
        if self.segment_word_limit:
            for i, segment in enumerate(segments):
                # Count words excluding exclusions
                words = [w for w in segment.split() if w.lower() not in self.exclusions]
                if len(words) > self.segment_word_limit:
                    return (
                        False,
                        segments,
                        f"Segment {i+1} exceeds word limit: {len(words)} > {self.segment_word_limit}"
                    )
                    
        return (True, segments, f"Structure OK: {len(segments)} segments")


@dataclass
class ForbiddenPatternConstraint:
    """Constraint for forbidden patterns in content."""
    patterns: List[str]
    case_sensitive: bool = False
    
    def validate(self, text: str) -> Tuple[bool, List[str], str]:
        """
        Validate text against forbidden patterns.
        
        Returns:
            Tuple of (is_valid, found_patterns, message)
        """
        found = []
        check_text = text if self.case_sensitive else text.lower()
        
        for pattern in self.patterns:
            check_pattern = pattern if self.case_sensitive else pattern.lower()
            if check_pattern in check_text:
                found.append(pattern)
                
        if found:
            return (False, found, f"Forbidden patterns found: {found}")
        else:
            return (True, [], "No forbidden patterns found")


@dataclass
class VoiceConstraint:
    """Constraint for voice type in content."""
    voice: VoiceType
    
    # Pronouns by voice type
    FIRST_PERSON_PRONOUNS = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
    SECOND_PERSON_PRONOUNS = {"you", "your", "yours", "yourself", "yourselves"}
    THIRD_PERSON_PRONOUNS = {"he", "she", "it", "him", "her", "his", "hers", "its", "they", "them", "their", "theirs"}
    
    def validate(self, text: str) -> Tuple[bool, List[str], str]:
        """Validate text against voice constraint."""
        words = set(re.findall(r'\b\w+\b', text.lower()))
        violations = []
        
        if self.voice == VoiceType.THIRD_PERSON_IMPLIED:
            # No first or second person pronouns allowed
            first_person_found = words & self.FIRST_PERSON_PRONOUNS
            second_person_found = words & self.SECOND_PERSON_PRONOUNS
            violations = list(first_person_found | second_person_found)
            
        elif self.voice == VoiceType.THIRD_PERSON:
            # No first or second person pronouns
            first_person_found = words & self.FIRST_PERSON_PRONOUNS
            second_person_found = words & self.SECOND_PERSON_PRONOUNS
            violations = list(first_person_found | second_person_found)
            
        elif self.voice == VoiceType.FIRST_PERSON:
            # Should have first person pronouns, no second person
            second_person_found = words & self.SECOND_PERSON_PRONOUNS
            violations = list(second_person_found)
            
        if violations:
            return (False, violations, f"Voice violations: {violations}")
        else:
            return (True, [], f"Voice OK: {self.voice.value}")


# =============================================================================
# SECTION BRIEF CONFIGURATIONS
# =============================================================================

@dataclass
class HeadlineBrief:
    """Creative brief for headline generation."""
    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(8, 12))
    char_count: CharCountConstraint = field(default_factory=lambda: CharCountConstraint(90))
    structure: StructureConstraint = field(default_factory=lambda: StructureConstraint(
        structure="Domain | Leadership | Value Prop",
        segment_word_limit=3,
    ))
    guidance: str = "Must incorporate differentiator keywords from the Competitive Analysis."
    
    def validate(self, text: str) -> Dict[str, object]:
        """Validate headline against all constraints."""
        results = {}
        
        wc_valid, wc_count, wc_msg = self.word_count.validate(text)
        results["word_count"] = {"valid": wc_valid, "count": wc_count, "message": wc_msg}
        
        cc_valid, cc_count, cc_msg = self.char_count.validate(text)
        results["char_count"] = {"valid": cc_valid, "count": cc_count, "message": cc_msg}
        
        st_valid, st_segments, st_msg = self.structure.validate(text)
        results["structure"] = {"valid": st_valid, "segments": st_segments, "message": st_msg}
        
        results["all_valid"] = wc_valid and cc_valid and st_valid
        return results


@dataclass
class ExecutiveSummaryBrief:
    """Creative brief for executive summary generation."""
    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(120, 140))
    voice: VoiceConstraint = field(default_factory=lambda: VoiceConstraint(VoiceType.THIRD_PERSON_IMPLIED))
    forbidden_patterns: ForbiddenPatternConstraint = field(default_factory=lambda: ForbiddenPatternConstraint([
        "I have",
        "My expertise",
        "At [COMPANY], I",
    ]))
    guidance: str = "Subtly incorporate the primary theme while maintaining professional executive biography voice."
    
    def validate(self, text: str) -> Dict[str, object]:
        """Validate executive summary against all constraints."""
        results = {}
        
        wc_valid, wc_count, wc_msg = self.word_count.validate(text)
        results["word_count"] = {"valid": wc_valid, "count": wc_count, "message": wc_msg}
        
        v_valid, v_violations, v_msg = self.voice.validate(text)
        results["voice"] = {"valid": v_valid, "violations": v_violations, "message": v_msg}
        
        fp_valid, fp_found, fp_msg = self.forbidden_patterns.validate(text)
        results["forbidden_patterns"] = {"valid": fp_valid, "found": fp_found, "message": fp_msg}
        
        results["all_valid"] = wc_valid and v_valid and fp_valid
        return results


@dataclass
class ExperienceBulletsBrief:
    """Creative brief for experience bullets generation."""
    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(28, 33))
    overview_word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(25, 33))
    provenance_strategy: SourcingStrategy = SourcingStrategy.JD_FIT_BASED
    provenance_map: Dict[str, str] = field(default_factory=lambda: {
        "default": "10V-0A-0S",  # 10 Verbatim, 0 Adapted, 0 Synthetic
    })
    selection_logic: str = "Multi-factor scoring: (JD Keyword Overlap * 0.5) + (Metric Impact * 0.3) + (Uniqueness * 0.2)"
    guidance: str = "Must use generic technology terms (e.g., 'cloud data platform' instead of 'Snowflake')."
    
    def validate(self, text: str, is_overview: bool = False) -> Dict[str, object]:
        """Validate bullet against constraints."""
        results = {}
        
        constraint = self.overview_word_count if is_overview else self.word_count
        wc_valid, wc_count, wc_msg = constraint.validate(text)
        results["word_count"] = {"valid": wc_valid, "count": wc_count, "message": wc_msg}
        
        # Check for period at end
        ends_with_period = text.strip().endswith('.')
        results["punctuation"] = {"valid": ends_with_period, "message": "Ends with period" if ends_with_period else "Missing period"}
        
        results["all_valid"] = wc_valid and ends_with_period
        return results
    
    def parse_provenance_code(self, code: str) -> Dict[str, int]:
        """
        Parse provenance code like '4V-3T-0S'.
        
        Returns:
            Dict with verbatim, adapted, synthetic counts
        """
        result = {"verbatim": 0, "adapted": 0, "synthetic": 0}
        
        parts = code.split('-')
        for part in parts:
            if part.endswith('V'):
                result["verbatim"] = int(part[:-1])
            elif part.endswith('T') or part.endswith('A'):
                result["adapted"] = int(part[:-1])
            elif part.endswith('S'):
                result["synthetic"] = int(part[:-1])
                
        return result


@dataclass
class CompetenciesBrief:
    """Creative brief for competencies/skills generation."""
    title: str = "Strategic & Technical Competencies"
    count: int = 6
    word_count_per_desc: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(24, 30))
    sourcing_strategy: SourcingStrategy = SourcingStrategy.INTERNAL_FIRST
    
    def validate(self, competencies: List[str]) -> Dict[str, object]:
        """Validate competencies list."""
        results = {
            "count": {"valid": len(competencies) == self.count, "actual": len(competencies), "expected": self.count},
            "word_counts": [],
            "all_valid": True,
        }
        
        for i, comp in enumerate(competencies):
            wc_valid, wc_count, wc_msg = self.word_count_per_desc.validate(comp)
            results["word_counts"].append({
                "index": i,
                "valid": wc_valid,
                "count": wc_count,
                "message": wc_msg,
            })
            if not wc_valid:
                results["all_valid"] = False
                
        if len(competencies) != self.count:
            results["all_valid"] = False
            
        return results


@dataclass
class CoverLetterBrief:
    """Creative brief for cover letter generation."""
    structure: str = "1-intro-2-body"
    word_count_per_para: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(85, 100))
    min_specific_details: int = 4
    forbidden_patterns: ForbiddenPatternConstraint = field(default_factory=lambda: ForbiddenPatternConstraint([
        "At [COMPANY], I...",
        "During my time at...",
    ]))
    signature_generation_policy: str = "DYNAMIC_FROM_OWNER_CONTACT"
    
    def validate(self, paragraphs: List[str]) -> Dict[str, object]:
        """Validate cover letter paragraphs."""
        results = {
            "paragraphs": [],
            "forbidden_patterns": {"valid": True, "found": []},
            "all_valid": True,
        }
        
        full_text = " ".join(paragraphs)
        
        # Check forbidden patterns
        fp_valid, fp_found, fp_msg = self.forbidden_patterns.validate(full_text)
        results["forbidden_patterns"] = {"valid": fp_valid, "found": fp_found, "message": fp_msg}
        
        # Check each paragraph
        for i, para in enumerate(paragraphs):
            wc_valid, wc_count, wc_msg = self.word_count_per_para.validate(para)
            results["paragraphs"].append({
                "index": i,
                "valid": wc_valid,
                "count": wc_count,
                "message": wc_msg,
            })
            if not wc_valid:
                results["all_valid"] = False
                
        if not fp_valid:
            results["all_valid"] = False
            
        return results


@dataclass
class SkillsListBrief:
    """Creative brief for optimized skills list."""
    count: int = 12
    sourcing_strategy: str = "Top 12 JD Skills & Cross-Check"
    logic: str = "1. Extract top 12 skills from JD. 2. Cross-reference against master resume. 3. Prioritize intersection."
    
    def validate(self, skills: List[str]) -> Dict[str, object]:
        """Validate skills list."""
        return {
            "count": {"valid": len(skills) == self.count, "actual": len(skills), "expected": self.count},
            "unique": {"valid": len(skills) == len(set(skills)), "duplicates": len(skills) - len(set(skills))},
            "all_valid": len(skills) == self.count and len(skills) == len(set(skills)),
        }


# =============================================================================
# MASTER CREATIVE BRIEF
# =============================================================================

@dataclass
class CreativeBrief:
    """
    Master Creative Brief containing all section configurations.
    
    This is the central configuration for all creative content generation,
    ensuring consistency and adherence to defined constraints.
    """
    headline: HeadlineBrief = field(default_factory=HeadlineBrief)
    executive_summary: ExecutiveSummaryBrief = field(default_factory=ExecutiveSummaryBrief)
    experience_bullets: ExperienceBulletsBrief = field(default_factory=ExperienceBulletsBrief)
    competencies: CompetenciesBrief = field(default_factory=CompetenciesBrief)
    cover_letter: CoverLetterBrief = field(default_factory=CoverLetterBrief)
    skills_list: SkillsListBrief = field(default_factory=SkillsListBrief)
    
    def validate_all(self, content: Dict[str, object]) -> Dict[str, object]:
        """
        Validate all content against the creative brief.
        
        Args:
            content: Dict with keys matching section names
            
        Returns:
            Dict with validation results for each section
        """
        results = {}
        
        if "headline" in content:
            results["headline"] = self.headline.validate(content["headline"])
            
        if "executive_summary" in content:
            results["executive_summary"] = self.executive_summary.validate(content["executive_summary"])
            
        if "experience_bullets" in content:
            bullets = content["experience_bullets"]
            if isinstance(bullets, list):
                results["experience_bullets"] = [
                    self.experience_bullets.validate(b) for b in bullets
                ]
                
        if "competencies" in content:
            results["competencies"] = self.competencies.validate(content["competencies"])
            
        if "cover_letter_paragraphs" in content:
            results["cover_letter"] = self.cover_letter.validate(content["cover_letter_paragraphs"])
            
        if "skills" in content:
            results["skills_list"] = self.skills_list.validate(content["skills"])
            
        # Calculate overall validity
        all_valid = True
        for section, result in results.items():
            if isinstance(result, dict) and "all_valid" in result:
                if not result["all_valid"]:
                    all_valid = False
            elif isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and not item.get("all_valid", True):
                        all_valid = False
                        
        results["overall_valid"] = all_valid
        return results
    
    def to_dict(self) -> Dict[str, object]:
        """Convert creative brief to dictionary for serialization."""
        return {
            "headline": {
                "word_count": [self.headline.word_count.min_words, self.headline.word_count.max_words],
                "char_count_max": self.headline.char_count.max_chars,
                "structure": self.headline.structure.structure,
                "guidance": self.headline.guidance,
            },
            "executive_summary": {
                "word_count": [self.executive_summary.word_count.min_words, self.executive_summary.word_count.max_words],
                "voice": self.executive_summary.voice.voice.value,
                "forbidden_patterns": self.executive_summary.forbidden_patterns.patterns,
                "guidance": self.executive_summary.guidance,
            },
            "experience_bullets": {
                "word_count": [self.experience_bullets.word_count.min_words, self.experience_bullets.word_count.max_words],
                "provenance_strategy": self.experience_bullets.provenance_strategy.value,
                "selection_logic": self.experience_bullets.selection_logic,
                "guidance": self.experience_bullets.guidance,
            },
            "competencies": {
                "title": self.competencies.title,
                "count": self.competencies.count,
                "word_count_per_desc": [
                    self.competencies.word_count_per_desc.min_words,
                    self.competencies.word_count_per_desc.max_words,
                ],
                "sourcing_strategy": self.competencies.sourcing_strategy.value,
            },
            "cover_letter": {
                "structure": self.cover_letter.structure,
                "word_count_per_para": [
                    self.cover_letter.word_count_per_para.min_words,
                    self.cover_letter.word_count_per_para.max_words,
                ],
                "min_specific_details": self.cover_letter.min_specific_details,
                "forbidden_patterns": self.cover_letter.forbidden_patterns.patterns,
            },
            "skills_list": {
                "count": self.skills_list.count,
                "sourcing_strategy": self.skills_list.sourcing_strategy,
                "logic": self.skills_list.logic,
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> CreativeBrief:
        """Create CreativeBrief from dictionary."""
        brief = cls()
        
        if "headline" in data:
            h = data["headline"]
            if "word_count" in h:
                brief.headline.word_count = WordCountConstraint(h["word_count"][0], h["word_count"][1])
            if "char_count_max" in h:
                brief.headline.char_count = CharCountConstraint(h["char_count_max"])
            if "structure" in h:
                brief.headline.structure = StructureConstraint(structure=h["structure"])
            if "guidance" in h:
                brief.headline.guidance = h["guidance"]
                
        if "executive_summary" in data:
            es = data["executive_summary"]
            if "word_count" in es:
                brief.executive_summary.word_count = WordCountConstraint(es["word_count"][0], es["word_count"][1])
            if "forbidden_patterns" in es:
                brief.executive_summary.forbidden_patterns = ForbiddenPatternConstraint(es["forbidden_patterns"])
            if "guidance" in es:
                brief.executive_summary.guidance = es["guidance"]
                
        if "experience_bullets" in data:
            eb = data["experience_bullets"]
            if "word_count" in eb:
                brief.experience_bullets.word_count = WordCountConstraint(eb["word_count"][0], eb["word_count"][1])
            if "guidance" in eb:
                brief.experience_bullets.guidance = eb["guidance"]
                
        if "competencies" in data:
            c = data["competencies"]
            if "count" in c:
                brief.competencies.count = c["count"]
            if "word_count_per_desc" in c:
                brief.competencies.word_count_per_desc = WordCountConstraint(
                    c["word_count_per_desc"][0], c["word_count_per_desc"][1]
                )
                
        if "skills_list" in data:
            sl = data["skills_list"]
            if "count" in sl:
                brief.skills_list.count = sl["count"]
                
        return brief


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_default_brief() -> CreativeBrief:
    """Create a creative brief with default settings."""
    return CreativeBrief()


def create_strict_brief() -> CreativeBrief:
    """Create a creative brief with stricter constraints."""
    brief = CreativeBrief()
    
    # Tighter word counts
    brief.headline.word_count = WordCountConstraint(8, 10)
    brief.executive_summary.word_count = WordCountConstraint(125, 135)
    brief.experience_bullets.word_count = WordCountConstraint(28, 32)
    
    # More forbidden patterns
    brief.executive_summary.forbidden_patterns.patterns.extend([
        "I am",
        "I was",
        "My role",
    ])
    
    return brief


def create_flexible_brief() -> CreativeBrief:
    """Create a creative brief with more flexible constraints."""
    brief = CreativeBrief()
    
    # Wider word count ranges
    brief.headline.word_count = WordCountConstraint(6, 15)
    brief.executive_summary.word_count = WordCountConstraint(100, 160)
    brief.experience_bullets.word_count = WordCountConstraint(20, 40)
    
    return brief
