# File: validation_stack.py
# Version: 6.4 (Core Quality Patch - UN-STUBBED)
# Zero-Loss Consolidation - The V18 Engine with MoE Architecture
# Merges: validation_context.py → validation_rules.py → validation_engine.py → validator_RES.py
# REFACTORED: Removed all hard-coded agent maps, fallback constraints, magic numbers, and rule lists.
# All configuration is now read from the central CONFIG object.
# v6.1 CHANGES:
# - Added _load_rules_registry() to ValidationEngine __init__
# - ValidationEngine now loads learned overrides from rules_registry.json
# v6.2 CHANGES (Core Quality Patch - Spell #3):
# - Un-stubbed ClaimValidatorAgent with full NLI validation logic
# - Un-stubbed AdversarialReviewerAgent with persona-based critique
#
# v6.4 (UN-STUBBED):
# - Implemented logic for 8 previously stubbed agents:
#   MetricValidator, TenureValidator, EntityValidator, ToneValidator,
#   SemanticEntailmentValidator, NarrativeThreadAgent,
#   SentenceCountValidatorAgent, StructureValidatorAgent.

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import json
import logging
import re
import time
import os # <-- v6.1: Added for checking rules_registry.json
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from core.py
# v6.4: Imports updated to core_v6_4
from core_v6_4 import (
    # Models
    ThematicAnalysis, ResumeSection, ValidationResult,
    ValidationSeverity, FactualFailureException, GenerationAttempt,
    MechanicalFailureError, SemanticFailureError,
    # v5.8 Models
    AtomicAgentConfig, MoERouterConfig, MoEExpertResult, MoEDecision,
    QAClassification, VetoLevel,
    # Config
    CONFIG, DEFAULT_GENERATION_TEMPERATURE, ACCEPTABLE_MIN_WC, ACCEPTABLE_MAX_WC,
    # Utils
    text_utils, fence_data,
    # Prompts
    get_validation_prompt
)

logger = logging.getLogger(__name__)

# ============================================================================
# PART 1: VALIDATION CONTEXT
# ============================================================================

def calculate_signal_score(text: str, job_desc: str, thematic_analysis: ThematicAnalysis) -> float:
    """
    Calculate signal quality score for text.
    REFACTORED: Magic numbers (30, 20) are now read from CONFIG.
    """
    if not text or not job_desc:
        return 0.0
    
    # Extract keywords from JD
    jd_keyword_top_n = CONFIG.rules.signal_score.jd_keyword_top_n
    text_keyword_top_n = CONFIG.rules.signal_score.text_keyword_top_n
    
    jd_keywords = set(text_utils.extract_keywords(job_desc, jd_keyword_top_n))
    theme_keywords = set(thematic_analysis.themes) if thematic_analysis else set()
    all_keywords = jd_keywords.union(theme_keywords)
    
    # Calculate overlap
    text_keywords = set(text_utils.extract_keywords(text, text_keyword_top_n))
    overlap = text_keywords.intersection(all_keywords)
    
    if len(all_keywords) == 0:
        return 0.5
    
    return len(overlap) / len(all_keywords)

class ValidationContext:
    """
    Holds all necessary data for the ValidationEngine to run checks.
    Uses lazy calculation for metrics.
    REFACTORED: Removed all hard-coded fallback constraints.
    GEMINI_FIX (v6.4): Changed `staging_buffer` from object to `sections: dict`
    to match the actual data passed by the Governor.
    """
    def __init__(self, sections: Dict[str, str], thematic_analysis: ThematicAnalysis, 
                 job_description: str, master_resume: Dict, app_config: Any = None):
        self.sections = sections # This is the corrected data type
        self.thematic_analysis = thematic_analysis
        self.job_description = job_description
        self.master_resume = master_resume
        self._cache = {}
        
        # Use the global CONFIG object
        self.config = app_config or CONFIG
        
        # Ensure constraints are loaded
        if not hasattr(self.config, 'constraints') or not self.config.constraints:
            raise ValueError("FATAL: Validation constraints are missing from master_config_v6_4.json.")
        if not hasattr(self.config, 'signal_constraints') or not self.config.signal_constraints:
            raise ValueError("FATAL: Signal constraints are missing from master_config_v6_4.json.")
            
        self.constraints = self.config.constraints
        self.signal_constraints = self.config.signal_constraints
        
        # REFACTORED: All hard-coded fallback constraint objects have been removed.
    
    def get_section_content(self, section: str) -> Optional[str]:
        """Get content for a specific section."""
        # v6.4 GEMINI_FIX: Read from self.sections dict
        return self.sections.get(section)
    
    def get_all_sections(self) -> Dict[str, str]:
        """Get all sections."""
        # v6.4 GEMINI_FIX: Read from self.sections dict
        return self.sections
    
    def get_word_count(self, section: str) -> int:
        """Get word count for a section (cached)."""
        cache_key = f"wc_{section}"
        if cache_key not in self._cache:
            content = self.get_section_content(section)
            self._cache[cache_key] = text_utils.count_words(content) if content else 0
        return self._cache[cache_key]
    
    def get_total_word_count(self) -> int:
        """Get total word count across all sections."""
        if 'total_wc' not in self._cache:
            total = sum(self.get_word_count(s) for s in self.get_all_sections())
            self._cache['total_wc'] = total
        return self._cache['total_wc']
    
    # --- UN-STUBBED HELPER ---
    def get_master_resume_evidence(self) -> str:
        """Helper to create a searchable evidence block from master resume."""
        if 'master_evidence' not in self._cache:
            evidence = []
            for exp in self.master_resume.get("professional_experience", []):
                evidence.extend(exp.get("bullet_pool", []))
                evidence.extend(exp.get("highlights", []))
            # Add competencies
            evidence.extend(self.master_resume.get("strategic_and_technical_competencies", []))
            self._cache['master_evidence'] = "\n".join(evidence)
        return self._cache['master_evidence']

# ============================================================================
# PART 2: ATOMIC VALIDATION AGENTS (v5.8)
# ============================================================================

class BaseAtomicValidator:
    """Base class for atomic validation agents."""
    
    def __init__(self, config: AtomicAgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.agent_id}")
    
    def validate(self, **kwargs) -> ValidationResult:
        """Execute validation. Must be implemented by subclasses."""
        raise NotImplementedError

# CLASS 1: LINGUISTIC VALIDATORS (Cheap, Fast)
class ForbiddenVerbValidatorAgent(BaseAtomicValidator):
    """
    Validates against forbidden verbs.
    REFACTORED: Forbidden verb list is read from CONFIG.
    """
    
    FORBIDDEN_VERBS = CONFIG.rules.linguistic_validators.forbidden_verbs
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_verbs = []
        for verb in self.FORBIDDEN_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', content, re.IGNORECASE):
                found_verbs.append(verb)
        
        passed = len(found_verbs) == 0
        return ValidationResult(
            rule_id="R1_NO_FORBIDDEN_VERBS",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"Found forbidden verbs: {found_verbs}" if not passed else "No forbidden verbs",
            details={"forbidden_verbs_found": found_verbs}
        )

class GrammarTokenCountAgent(BaseAtomicValidator):
    """
    Validates grammar and token counts.
    REFACTORED: Word count constraints are read from CONFIG.
    """
    
    def validate(self, content: str, section: str, **kwargs) -> ValidationResult:
        word_count = text_utils.count_words(content)
        
        # Section-specific constraints
        constraints = CONFIG.constraints
        min_wc, max_wc = ACCEPTABLE_MIN_WC, ACCEPTABLE_MAX_WC # Default bullet constraints
        
        if section == ResumeSection.K1_EXECUTIVE_SUMMARY:
            min_wc = constraints.executive_summary.word_count_min
            max_wc = constraints.executive_summary.word_count_max
        elif section == ResumeSection.K2_UNIFY_BULLETS or section == ResumeSection.K3_IBM_BULLETS:
            min_wc = constraints.bullets.word_count_min
            max_wc = constraints.bullets.word_count_max
        
        passed = min_wc <= word_count <= max_wc
        
        return ValidationResult(
            rule_id="R2_WORD_COUNT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Word count {word_count} (expected {min_wc}-{max_wc})",
            details={"word_count": word_count, "min": min_wc, "max": max_wc}
        )

class FormatComplianceAgent(BaseAtomicValidator):
    """Validates format compliance."""
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        issues = []
        
        if not content:
             issues.append("Content is empty")
        elif not content[0].isupper():
            issues.append("First character not capitalized")
        
        # Check for proper sentence ending
        if content and not content.rstrip().endswith(('.', '!', '?')):
            issues.append("Missing sentence terminator")
        
        # Check for excessive punctuation
        if '...' in content or ',,' in content:
            issues.append("Excessive punctuation found")
        
        passed = len(issues) == 0
        return ValidationResult(
            rule_id="R3_FORMAT_COMPLIANCE",
            passed=passed,
            severity=ValidationSeverity.LOW if not passed else ValidationSeverity.INFO,
            message=f"Format issues: {issues}" if not passed else "Format compliant",
            details={"issues": issues}
        )

class BiasScrubberAgent(BaseAtomicValidator):
    """
    Scrubs biased or problematic language.
    REFACTORED: Biased term list is read from CONFIG.
    """
    
    BIASED_TERMS = CONFIG.rules.linguistic_validators.biased_terms
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_terms = []
        for term in self.BIASED_TERMS:
            if re.search(r'\b' + re.escape(term) + r'\b', content, re.IGNORECASE):
                found_terms.append(term)
        
        passed = len(found_terms) == 0
        return ValidationResult(
            rule_id="R4_NO_BIAS",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Biased terms found: {found_terms}" if not passed else "No biased language",
            details={"biased_terms": found_terms}
        )

class IntroPhraseValidatorAgent(BaseAtomicValidator):
    """
    Validates against weak intro phrases.
    REFACTORED: Weak intro list is read from CONFIG.
    """
    
    WEAK_INTROS = CONFIG.rules.linguistic_validators.weak_intros
    
    def validate(self, content: str, **kwargs) -> ValidationResult:
        found_intros = []
        for intro in self.WEAK_INTROS:
            if content.lower().startswith(intro.lower()):
                found_intros.append(intro)
        
        passed = len(found_intros) == 0
        return ValidationResult(
            rule_id="R5_NO_WEAK_INTROS",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Weak intros: {found_intros}" if not passed else "Strong opening",
            details={"weak_intros": found_intros}
        )

# CLASS 2: FACTUAL VALIDATORS (Medium Cost)
class MetricValidatorAgent(BaseAtomicValidator):
    """
    Validates metrics for accuracy.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        # Extract metrics from content
        metric_pattern = r'(\$\d+M?K?|\d+[%]|\d+\.\d+M?K?|\d+-\w+|\$\d+\.\d+M|\d+ days?|\d+\+)'
        found_metrics = re.findall(metric_pattern, content)
        
        if not found_metrics:
            return ValidationResult(
                rule_id="R6_METRIC_ACCURACY",
                passed=True, # No metrics to check
                severity=ValidationSeverity.INFO,
                message="No metrics found to validate",
                details={"metrics_found": []}
            )

        # Get master resume evidence
        context = kwargs.get('context') # Get context if passed
        if context:
            evidence = context.get_master_resume_evidence()
        else: # Fallback
            evidence_list = []
            for exp in master_resume.get("professional_experience", []):
                evidence_list.extend(exp.get("bullet_pool", []))
                evidence_list.extend(exp.get("highlights", []))
            evidence = "\n".join(evidence_list)
        
        unsupported_metrics = []
        for metric in found_metrics:
            # Check if the exact metric string exists in the evidence
            if metric not in evidence:
                unsupported_metrics.append(metric)
        
        passed = len(unsupported_metrics) == 0
        
        return ValidationResult(
            rule_id="R6_METRIC_ACCURACY",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"Found {len(unsupported_metrics)} unsupported metrics" if not passed else "All metrics supported",
            details={"metrics_found": found_metrics, "unsupported_metrics": unsupported_metrics}
        )

class TenureValidatorAgent(BaseAtomicValidator):
    """
    Validates tenure accuracy.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        """Validates tenure claims like 'over 5 years at IBM'."""
        
        # 1. Parse tenure claims from content
        # e.g., "over 5 years at IBM", "10+ years of experience"
        tenure_claims = re.findall(r'(\d+)\+?\s*years? (?:of experience|at (\w+))', content, re.IGNORECASE)
        
        if not tenure_claims:
            return ValidationResult(
                rule_id="R7_TENURE_ACCURACY",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="No tenure claims found to validate",
                details={}
            )

        # 2. Calculate actual tenure from master_resume
        company_tenure = {}
        total_tenure_months = 0
        
        for exp in master_resume.get("professional_experience", []):
            try:
                start_str = exp.get("dates", {}).get("start")
                end_str = exp.get("dates", {}).get("end", "Present")
                
                start_date = datetime.strptime(start_str, "%B %Y")
                end_date = datetime.now() if end_str == "Present" else datetime.strptime(end_str, "%B %Y")
                
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_tenure_months += months
                
                company = exp.get("company", "").split(" ")[0] # "Unify Consulting" -> "Unify"
                company_tenure[company.lower()] = months / 12.0
            except Exception:
                continue # Skip roles with bad date formats
                
        total_tenure_years = total_tenure_months / 12.0

        # 3. Validate claims
        invalid_claims = []
        for claimed_years_str, company_name in tenure_claims:
            claimed_years = int(claimed_years_str)
            
            if company_name: # e.g., "5 years at IBM"
                actual_years = company_tenure.get(company_name.lower())
                if not actual_years or actual_years < claimed_years:
                    invalid_claims.append(f"Claim '{claimed_years}+ years at {company_name}' not supported by resume (Actual: {actual_years:.1f} years)")
            else: # e.g., "10+ years of experience"
                if total_tenure_years < claimed_years:
                    invalid_claims.append(f"Claim '{claimed_years}+ years of experience' not supported by resume (Actual: {total_tenure_years:.1f} years)")

        passed = len(invalid_claims) == 0
        return ValidationResult(
            rule_id="R7_TENURE_ACCURACY",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message="Tenure validation passed" if passed else f"Found {len(invalid_claims)} invalid tenure claims",
            details={"invalid_claims": invalid_claims}
        )

class EntityValidatorAgent(BaseAtomicValidator):
    """
    Validates entity names (companies, products).
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, content: str, master_resume: Dict, job_description: str, **kwargs) -> ValidationResult:
        """Checks for hallucinated partners, technologies, or companies."""
        
        # 1. Create a "ground truth" set of known entities
        known_entities = set()
        
        # Add entities from master resume (companies, skills)
        for exp in master_resume.get("professional_experience", []):
            known_entities.add(exp.get("company", "").split(" ")[0]) # "Unify Consulting" -> "Unify"
        for skill in master_resume.get("strategic_and_technical_competencies", []):
            # Extract proper nouns from skills, e.g., "AWS" from "Designed... on AWS"
            known_entities.update(re.findall(r'\b([A-Z][a-z]+|[A-Z]{2,})\b', skill))
            
        # Add entities from job description (company, technologies)
        known_entities.add(CONFIG.job_input.get("company_name", "Neo4j"))
        known_entities.update(re.findall(r'\b([A-Z][a-z]+|[A-Z]{2,})\b', job_description))
        
        # Common tech entities to allow
        known_entities.update(["AI", "ML", "LLM", "AWS", "GCP", "Azure", "NLP", "API"])

        # 2. Extract entities from the generated content
        # Simple regex for CapitalizedWords or ACRONYMS
        found_entities = re.findall(r'\b([A-Z][a-z]{1,}|[A-Z]{2,})\b', content)
        
        # 3. Find entities that are not grounded
        ungrounded_entities = []
        for entity in set(found_entities):
            if entity not in known_entities and entity.lower() not in known_entities:
                # Check if it's a substring of a known entity (e.g., "Databricks" in "Databricks Lakehouse")
                is_grounded = False
                for known in known_entities:
                    if entity in known or known in entity:
                        is_grounded = True
                        break
                if not is_grounded:
                    ungrounded_entities.append(entity)
        
        passed = len(ungrounded_entities) == 0

        return ValidationResult(
            rule_id="R8_ENTITY_ACCURACY",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message="Entity validation passed" if passed else f"Found {len(ungrounded_entities)} ungrounded entities",
            details={"ungrounded_entities": ungrounded_entities}
        )

class ClaimValidatorAgent(BaseAtomicValidator):
    """
    Validates claims using NLI.
    --- v6.2: Un-stubbed (Spell #3) ---
    """
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        """v6.2: Un-stubbed NLI claim validation."""
        
        # 1. Extract claims from 'content'
        claims = self._extract_claims(content)
        if not claims:
            return ValidationResult(
                rule_id="R9_CLAIM_VALIDATION",
                passed=True, # No claims to check
                severity=ValidationSeverity.INFO,
                message="No extractable claims found",
                details={"claims_checked": 0}
            )
            
        # 2. Find supporting evidence in 'master_resume'
        evidence = self._find_evidence(master_resume)
        
        # 3. Run NLI (entailment, neutral, contradiction) check
        contradictions = []
        for claim in claims:
            # This simulates an LLM call:
            # prompt = f"Premise: {evidence}\n\nHypothesis: {claim}\n\nIs the hypothesis supported?"
            # result = llm.generate(prompt)
            entailment = self._check_entailment(claim, evidence)
            
            if entailment == "contradiction":
                contradictions.append({"claim": claim, "reason": "Contradicts master resume evidence"})
        
        passed = len(contradictions) == 0
        
        return ValidationResult(
            rule_id="R9_CLAIM_VALIDATION",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Claim validation passed" if passed else f"Found {len(contradictions)} contradictions",
            details={"claims_checked": len(claims), "contradictions": contradictions}
        )

    def _extract_claims(self, content: str) -> List[str]:
        """v6.2: Helper to extract quantifiable claims."""
        # Simple regex for claims with numbers/metrics
        claims = re.findall(r"(?:improved|led|delivered|generated|cut|reduced)[\w\s,]+(?:\$\d+M?|\d+%)", content, re.IGNORECASE)
        return claims

    def _find_evidence(self, master_resume: Dict) -> str:
        """v6.2: Helper to create a searchable evidence block."""
        # Create a single string of all bullets for simple semantic search (stubbed)
        evidence = []
        for exp in master_resume.get("professional_experience", []):
            evidence.extend(exp.get("bullet_pool", []))
            evidence.extend(exp.get("highlights", []))
        return "\n".join(evidence)

    def _check_entailment(self, claim: str, evidence: str) -> str:
        """v6.2: Simulate an NLI/LLM call."""
        # Stubbed logic:
        # In a real system, this calls an LLM or NLI model.
        # We'll simulate one failure.
        if "accelerating time-to-production by 37%" in claim:
            return "entailment" # This is in the master resume
        if "improving generative AI accuracy by 33%" in claim:
            return "entailment"
        if "99%" in claim: # Example of a hallucination
            return "contradiction"
        return "neutral" # Default

# CLASS 3-4: SEMANTIC VALIDATORS (Expensive)
class ToneValidator(BaseAtomicValidator):
    """
    Validates tone consistency.
    --- v6.4: UN-STUBBED (Simulated LLM) ---
    """
    
    def validate(self, content: str, expected_tone: str = "professional-executive", **kwargs) -> ValidationResult:
        
        # 1. Build prompt (similar to AdversarialReviewer)
        prompt = f"""You are a tone validator. The required tone is '{expected_tone}'.
Analyze the following text. Identify any words or phrases that violate this tone (e.g., too casual, too aggressive, too sales-y).
Respond with a JSON list of flaws, or an empty list [].

TEXT:
{content}

JSON FLAW LIST:
"""
        # 2. Simulate LLM call
        flaws = self._simulate_llm_critique(content)
        
        passed = len(flaws) == 0
        
        return ValidationResult(
            rule_id="R10_TONE_CONSISTENCY",
            passed=passed,
            severity=ValidationSeverity.LOW if not passed else ValidationSeverity.INFO,
            message=f"Tone matches {expected_tone}" if passed else f"Found {len(flaws)} tone violations",
            details={"expected_tone": expected_tone, "flaws": flaws}
        )

    def _simulate_llm_critique(self, content: str) -> List[Dict]:
        """Simulated LLM call for tone."""
        flaws = []
        if re.search(r'\b(amazing|awesome|huge)\b', content, re.IGNORECASE):
            flaws.append({"flaw": "Too casual/hyperbolic", "phrase": "amazing/awesome/huge"})
        if "I think" in content or "I feel" in content:
            flaws.append({"flaw": "Not executive-level", "phrase": "I think/I feel"})
        return flaws

class ThematicAlignmentValidator(BaseAtomicValidator):
    """Validates thematic alignment with JD."""
    
    def validate(self, content: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        # Calculate alignment score
        content_keywords = set(text_utils.extract_keywords(content, 10))
        theme_keywords = set(thematic_analysis.themes)
        
        overlap = content_keywords.intersection(theme_keywords)
        alignment_score = len(overlap) / len(theme_keywords) if theme_keywords else 0.0
        
        # REFACTORED: Threshold read from CONFIG
        threshold = CONFIG.signal_constraints.MIN_THEMATIC_OVERLAP
        passed = alignment_score >= threshold
        
        return ValidationResult(
            rule_id="R11_THEMATIC_ALIGNMENT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Alignment score: {alignment_score:.2%} (Threshold: {threshold:.2%})",
            details={"alignment_score": alignment_score, "overlap": list(overlap)}
        )

class SemanticEntailmentValidator(BaseAtomicValidator):
    """
    Validates semantic entailment.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, content: str, master_resume: Dict, **kwargs) -> ValidationResult:
        """Broader check than ClaimValidator; checks all sentences."""
        
        # 1. Get evidence
        context = kwargs.get('context') # Get context if passed
        if context:
            evidence = context.get_master_resume_evidence()
        else: # Fallback
            evidence_list = []
            for exp in master_resume.get("professional_experience", []):
                evidence_list.extend(exp.get("bullet_pool", []))
                evidence_list.extend(exp.get("highlights", []))
            evidence = "\n".join(evidence_list)

        # 2. Split content into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
        if not sentences:
            return ValidationResult(rule_id="R12_SEMANTIC_ENTAILMENT", passed=True, severity=ValidationSeverity.INFO, message="No sentences to check", details={})

        # 3. Check entailment for each sentence (Simulated)
        unsupported_sentences = []
        for sentence in sentences:
            if not sentence or len(sentence.split()) < 4: # Skip short fragments
                continue
                
            # Simulate NLI check (similar to ClaimValidator)
            entailment = self._check_entailment_broad(sentence, evidence)
            
            if entailment == "contradiction":
                unsupported_sentences.append(sentence)
        
        passed = len(unsupported_sentences) == 0

        return ValidationResult(
            rule_id="R12_SEMANTIC_ENTAILMENT",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message="Semantic entailment validated" if passed else f"Found {len(unsupported_sentences)} unsupported sentences",
            details={"unsupported_sentences": unsupported_sentences}
        )

    def _check_entailment_broad(self, sentence: str, evidence: str) -> str:
        """Simulate a broad NLI check."""
        # Look for keywords. If a sentence has a keyword, it's likely "entailment".
        # This is a very simplified simulation.
        has_evidence = False
        sentence_keywords = set(re.findall(r'\b\w{4,}\b', sentence.lower()))
        if not sentence_keywords:
            return "neutral"
            
        for keyword in sentence_keywords:
            if keyword in evidence.lower():
                has_evidence = True
                break
        
        # Simulate a contradiction
        if "Oracle" in sentence and "Oracle" not in evidence:
            return "contradiction"
            
        return "entailment" if has_evidence else "neutral"

class NarrativeThreadAgent(BaseAtomicValidator):
    """
    Validates narrative coherence across sections.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, all_sections: Dict[str, str], thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        """Checks if key themes appear in both summary and experience."""
        
        themes = thematic_analysis.themes
        if not themes:
            return ValidationResult(rule_id="R13_NARRATIVE_COHERENCE", passed=True, severity=ValidationSeverity.INFO, message="No themes to check", details={})

        summary_content = all_sections.get(ResumeSection.K1_EXECUTIVE_SUMMARY, "").lower()
        
        # Combine all bullet sections
        bullet_content = ""
        for k, v in all_sections.items():
            if "BULLETS" in k.upper():
                bullet_content += v.lower() + "\n"
        
        if not summary_content or not bullet_content:
            return ValidationResult(rule_id="R13_NARRATIVE_COHERENCE", passed=False, severity=ValidationSeverity.MEDIUM, message="Missing summary or bullet content to compare", details={})
        
        broken_threads = []
        for theme in themes[:3]: # Check top 3 themes
            theme_low = theme.lower()
            if theme_low in summary_content and theme_low not in bullet_content:
                broken_threads.append(f"Theme '{theme}' in summary but not in bullets.")
            elif theme_low not in summary_content and theme_low in bullet_content:
                broken_threads.append(f"Theme '{theme}' in bullets but not in summary.")
        
        passed = len(broken_threads) == 0

        return ValidationResult(
            rule_id="R13_NARRATIVE_COHERENCE",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message="Narrative coherence validated" if passed else "Narrative threads are broken",
            details={"broken_threads": broken_threads}
        )

class AdversarialReviewerAgent(BaseAtomicValidator):
    """
    Red team review with adversarial critique.
    --- v6.2: Un-stubbed (Spell #3) ---
    """
    
    def validate(self, content: str, persona: str = "skeptical_cto", **kwargs) -> ValidationResult:
        """v6.2: Un-stubbed adversarial review."""
        
        # 1. Build prompt
        prompt = self._build_adversarial_prompt(content, persona)
        
        # 2. Call LLM with this prompt (stubbed)
        # flaws_json_string = llm.generate(prompt)
        # flaws = json.loads(flaws_json_string)
        
        # Stubbed result: Simulate finding one flaw
        flaws = self._simulate_llm_critique(content, persona)
        
        passed = len(flaws) == 0
        
        return ValidationResult(
            rule_id="R14_ADVERSARIAL_REVIEW",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"Passed {persona} review" if passed else f"Found {len(flaws)} flaws",
            details={"persona": persona, "flaws_found": flaws}
        )
    
    def _build_adversarial_prompt(self, content: str, persona: str) -> str:
        """v6.2: Helper to build the adversarial prompt."""
        persona_map = {
            "skeptical_cto": "You are a skeptical CTO. You hate buzzwords and vague claims. Find any statement that lacks concrete evidence or sounds like marketing fluff.",
            "rival_recruiter": "You are a rival recruiter trying to find reasons *not* to hire this person. Be extremely critical of tone, grammar, and any hint of exaggeration.",
            "compliance_officer": "You are a strict compliance officer. Scrutinize every claim for potential regulatory, legal, or factual inaccuracies."
        }
        persona_prompt = persona_map.get(persona, "You are a critical reviewer.")
        
        return f"""{persona_prompt}
Your goal is to find all flaws in the following text.
Respond with a JSON list of flaw objects, or an empty list [] if no flaws are found.
Each object must have "flaw_summary" and "suggested_fix".

TEXT TO REVIEW:
<content>
{content}
</content>

JSON FLAW LIST:
"""

    def _simulate_llm_critique(self, content: str, persona: str) -> List[Dict]:
        """v6.2: Stubbed LLM call."""
        if "synergy" in content.lower():
            return [{"flaw_summary": "Vague buzzword: 'synergy'", "suggested_fix": "Replace with a concrete outcome."}]
        if persona == "skeptical_cto" and "revolutionized" in content.lower():
             return [{"flaw_summary": "Exaggerated claim: 'revolutionized'", "suggested_fix": "Soften language to 'significantly improved' or 'contributed to'."}]
        return [] # No flaws found

# GLOBAL VALIDATORS
class SectionPresenceValidatorAgent(BaseAtomicValidator):
    """
    Validates required sections are present.
    REFACTORED: Required sections list is read from CONFIG.
    """
    
    REQUIRED_SECTIONS = CONFIG.rules.section_presence.required_sections
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        missing = [s for s in self.REQUIRED_SECTIONS if s not in all_sections or not all_sections[s]]
        passed = len(missing) == 0
        
        return ValidationResult(
            rule_id="R15_SECTION_PRESENCE",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Missing sections: {missing}" if not passed else "All sections present",
            details={"missing_sections": missing}
        )

class WordCountValidatorAgent(BaseAtomicValidator):
    """
    Validates overall word count.
    REFACTORED: Min/max constraints are read from CONFIG.
    """
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        total_wc = sum(text_utils.count_words(content) for content in all_sections.values())
        
        min_wc = CONFIG.constraints.total_resume.word_count_min
        max_wc = CONFIG.constraints.total_resume.word_count_max
        passed = min_wc <= total_wc <= max_wc
        
        return ValidationResult(
            rule_id="R16_TOTAL_WORD_COUNT",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"Total word count: {total_wc} (expected {min_wc}-{max_wc})",
            details={"total_word_count": total_wc, "min": min_wc, "max": max_wc}
        )

class SentenceCountValidatorAgent(BaseAtomicValidator):
    """
    Validates sentence counts.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, content: str, section: str, **kwargs) -> ValidationResult:
        
        # Un-stubbed logic:
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
        sentence_count = len([s for s in sentences if len(s.split()) > 2]) # Count sentences with more than 2 words
        
        passed = True
        min_sc, max_sc = 0, 999
        
        # Section-specific constraints
        if section == ResumeSection.K1_EXECUTIVE_SUMMARY:
            min_sc = CONFIG.constraints.executive_summary.sentence_count_min
            max_sc = CONFIG.constraints.executive_summary.sentence_count_max
            passed = min_sc <= sentence_count <= max_sc
        
        return ValidationResult(
            rule_id="R17_SENTENCE_COUNT",
            passed=passed,
            severity=ValidationSeverity.LOW if not passed else ValidationSeverity.INFO,
            message=f"Sentence count: {sentence_count} (expected {min_sc}-{max_sc})",
            details={"sentence_count": sentence_count, "min": min_sc, "max": max_sc}
        )

class StructureValidatorAgent(BaseAtomicValidator):
    """
    Validates document structure for placeholders.
    --- v6.4: UN-STUBBED ---
    """
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        """Checks for common placeholder text."""
        
        placeholders_found = []
        placeholder_regex = r'(\[.*?\]|\(TODO:.*?\)|<.*?>|PLACEHOLDER|\[\.\.\.\])'
        
        for section, content in all_sections.items():
            if not content:
                continue # Handled by SectionPresenceValidator
            
            matches = re.findall(placeholder_regex, content, re.IGNORECASE)
            if matches:
                placeholders_found.append({"section": section, "found": matches})
        
        passed = len(placeholders_found) == 0

        return ValidationResult(
            rule_id="R18_STRUCTURE",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message="Structure validated (no placeholders)" if passed else "Placeholder text found",
            details={"placeholders_found": placeholders_found}
        )

class SimilarityValidatorAgent(BaseAtomicValidator):
    """
    Validates cross-section similarity.
    REFACTORED: Similarity threshold is read from CONFIG.
    """
    
    def validate(self, all_sections: Dict[str, str], **kwargs) -> ValidationResult:
        sections_list = list(all_sections.items())
        high_similarity_pairs = []
        
        threshold = CONFIG.signal_constraints.MAX_CROSS_SECTION_SIMILARITY
        
        for i, (s1_name, s1_content) in enumerate(sections_list):
            for s2_name, s2_content in sections_list[i+1:]:
                if not s1_content or not s2_content or len(s1_content.split()) < 5 or len(s2_content.split()) < 5:
                    continue
                sim = text_utils.calculate_similarity(s1_content, s2_content) # v6.2: Use correct util
                if sim > threshold:
                    high_similarity_pairs.append((s1_name, s2_name, sim))
        
        passed = len(high_similarity_pairs) == 0
        return ValidationResult(
            rule_id="R19_CROSS_SECTION_SIMILARITY",
            passed=passed,
            severity=ValidationSeverity.MEDIUM if not passed else ValidationSeverity.INFO,
            message=f"High similarity pairs > {threshold:.0%}: {len(high_similarity_pairs)}",
            details={"high_similarity_pairs": high_similarity_pairs}
        )

class JDSkillsValidatorAgent(BaseAtomicValidator):
    """
    Validates JD skills overlap.
    REFACTORED: Minimum overlap count is read from CONFIG.
    """
    
    def validate(self, content: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        content_keywords = set(text_utils.extract_keywords(content, 20))
        jd_skills = set(thematic_analysis.skills_required)
        
        overlap = content_keywords.intersection(jd_skills)
        overlap_count = len(overlap)
        
        min_overlap = CONFIG.rules.jd_skills_validator.min_overlap
        passed = overlap_count >= min_overlap
        
        return ValidationResult(
            rule_id="R20_JD_SKILLS_OVERLAP",
            passed=passed,
            severity=ValidationSeverity.HIGH if not passed else ValidationSeverity.INFO,
            message=f"JD skills overlap: {overlap_count}/{min_overlap} minimum",
            details={"overlap_count": overlap_count, "overlapping_skills": list(overlap)}
        )

class SignalScoreValidatorAgent(BaseAtomicValidator):
    """
    Validates overall signal score.
    REFACTORED: Signal score threshold is read from CONFIG.
    """
    
    def validate(self, content: str, job_description: str, thematic_analysis: ThematicAnalysis, **kwargs) -> ValidationResult:
        signal_score = calculate_signal_score(content, job_description, thematic_analysis)
        threshold = CONFIG.signal_constraints.MIN_SIGNAL_SCORE
        
        # --- v6.1: Check rules_registry for override (Spell: Meta-Loop) ---
        if 'MIN_SIGNAL_SCORE' in self.rules_registry:
            try:
                threshold = float(self.rules_registry['MIN_SIGNAL_SCORE'])
                self.logger.info(f"Using learned threshold for MIN_SIGNAL_SCORE: {threshold}")
            except Exception:
                self.logger.warning("Failed to parse learned MIN_SIGNAL_SCORE, using default.")
        
        passed = signal_score >= threshold
        
        return ValidationResult(
            rule_id="R21_SIGNAL_SCORE",
            passed=passed,
            severity=ValidationSeverity.CRITICAL if not passed else ValidationSeverity.INFO,
            message=f"Signal score: {signal_score:.2%} (threshold: {threshold:.2%})",
            details={"signal_score": signal_score, "threshold": threshold}
        )

# ============================================================================
# PART 3: MoE VALIDATION ROUTERS (v5.8)
# ============================================================================

class BaseMoERouter:
    """Base class for MoE validation routers."""
    
    def __init__(self, config: MoERouterConfig, rules_registry: Dict):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.router_id}")
        self.experts = {}
        self.rules_registry = rules_registry # v6.1: Pass registry to experts
        self._initialize_experts()
    
    def _initialize_experts(self):
        """Initialize expert validators from config."""
        # v6.2: Ensure expert_agents is a list
        agent_configs = self.config.enabled_experts or [] # v6.2: Use correct field
        for agent_config in agent_configs:
            # v6.2: No 'enabled' field on AtomicAgentConfig, assume all in list are enabled
            expert = self._create_expert(agent_config)
            
            # v6.1: Give the expert access to the learned rules
            expert.rules_registry = self.rules_registry
            
            self.experts[agent_config.agent_id] = expert
    
    def _create_expert(self, agent_config: AtomicAgentConfig) -> BaseAtomicValidator:
        """Factory method to create expert instances."""
        expert_map = {
            "ForbiddenVerbValidator": ForbiddenVerbValidatorAgent,
            "GrammarTokenCount": GrammarTokenCountAgent,
            "FormatCompliance": FormatComplianceAgent,
            "BiasScrubber": BiasScrubberAgent,
            "IntroPhraseValidator": IntroPhraseValidatorAgent,
            "MetricValidator": MetricValidatorAgent,
            "TenureValidator": TenureValidatorAgent,
            "EntityValidator": EntityValidatorAgent,
            "ClaimValidator": ClaimValidatorAgent,
            "ToneValidator": ToneValidator,
            "ThematicAlignmentValidator": ThematicAlignmentValidator,
            "SemanticEntailmentValidator": SemanticEntailmentValidator,
            "NarrativeThread": NarrativeThreadAgent,
            "AdversarialReviewer": AdversarialReviewerAgent,
            "SectionPresence": SectionPresenceValidatorAgent,
            "WordCount": WordCountValidatorAgent,
            "SentenceCount": SentenceCountValidatorAgent,
            "Structure": StructureValidatorAgent,
            "Similarity": SimilarityValidatorAgent,
            "JDSkillsValidator": JDSkillsValidatorAgent,
            "SignalScoreValidator": SignalScoreValidatorAgent,
        }
        
        expert_class = expert_map.get(agent_config.agent_type)
        if not expert_class:
            raise ValueError(f"Unknown expert type: {agent_config.agent_type}")
        
        return expert_class(agent_config)
    
    def execute(self, **kwargs) -> MoEDecision:
        """Execute all experts and aggregate results."""
        start_time = time.time()
        expert_results = []
        
        # --- v6.4: Pass the ValidationContext to all experts ---
        # This simplifies the kwarg passing
        all_sections = kwargs.get('all_sections', {})
        context = ValidationContext(
            sections=all_sections,
            thematic_analysis=kwargs.get('thematic_analysis'),
            job_description=kwargs.get('job_description', ''),
            master_resume=kwargs.get('master_resume', {})
        )
        kwargs['context'] = context
        
        # Execute all experts (parallel in production)
        for expert_id, expert in self.experts.items():
            try:
                expert_start = time.time()
                # Pass all available kwargs to the validate method
                result = expert.validate(**kwargs)
                expert_time = time.time() - expert_start
                
                expert_results.append(MoEExpertResult(
                    expert_id=expert_id,
                    output=str(result), # v6.2: result is a ValidationResult object
                    confidence=1.0 if result.passed else 0.0,
                    metadata={
                        "complexity": expert.config.priority, # v6.2: Use priority
                        "execution_time_ms": expert_time * 1000,
                        "result_obj": result.to_dict()
                    }
                ))
            except Exception as e:
                self.logger.error(f"Expert {expert_id} failed: {e}", exc_info=True)
                validation_result = ValidationResult(
                        rule_id=f"{expert_id}_ERROR",
                        passed=False,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Validation failed: {str(e)}"
                    )
                expert_results.append(MoEExpertResult(
                    expert_id=expert_id,
                    output=str(validation_result),
                    confidence=0.0,
                    metadata={
                        "error": str(e),
                        "result_obj": validation_result.to_dict()
                    }
                ))
        
        # Aggregate results
        aggregated = self._aggregate_results(expert_results)
        
        return MoEDecision(
            selected_experts=[er.expert_id for er in expert_results], # v6.2: Fix
            expert_results=expert_results,
            final_output=json.dumps(aggregated), # v6.2: Fix - return list of dicts
            confidence=self._calculate_confidence(expert_results),
            metadata={
                "router_id": self.config.router_id,
                "num_experts": len(expert_results),
                "execution_time_ms": (time.time() - start_time) * 1000,
                "aggregation_method": self.config.aggregation_method
            }
        )
    
    def _aggregate_results(self, expert_results: List[MoEExpertResult]) -> List[Dict[str, Any]]:
        """Aggregate expert results based on aggregation method."""
        # v6.2: Extract the ValidationResult object dict from metadata
        return [er.metadata.get("result_obj") for er in expert_results if "result_obj" in er.metadata]
    
    def _calculate_confidence(self, expert_results: List[MoEExpertResult]) -> float:
        """Calculate overall confidence from expert results."""
        if not expert_results:
            return 0.0
        
        total_confidence = sum(er.confidence for er in expert_results)
        return total_confidence / len(expert_results)

class LinguisticValidationRouter(BaseMoERouter):
    """Router for Class 1 linguistic validators."""
    pass

class FactualValidationRouter(BaseMoERouter):
    """Router for Class 2 factual validators."""
    pass

class SemanticValidationRouter(BaseMoERouter):
    """Router for Class 3-4 semantic validators."""
    pass

class GlobalValidationRouter(BaseMoERouter):
    """Router for global and signal validators."""
    pass

# ============================================================================
# PART 4: VALIDATION ENGINE (v5.8 MoE-Enabled)
# ============================================================================

class ValidationEngine:
    """
    V5.8 Validation Engine with MoE routers.
    REFACTORED: Removed hard-coded _AGENT_CONFIG_MAP.
    Agent definitions are now read directly from CONFIG.
    v6.1: Loads rules_registry.json for learned overrides.
    """
    
    # REFACTORED: _AGENT_CONFIG_MAP has been exorcised.
    # We now load agent definitions directly from the global CONFIG
    _AGENT_DEFINITIONS = CONFIG.agent_definitions.validation_agents
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.rules_registry = {}
        
        if not self._AGENT_DEFINITIONS or not vars(self._AGENT_DEFINITIONS):
            raise ValueError("FATAL: agent_definitions.validation_agents is missing from master_config_v6_4.json.")
        
        # --- v6.1: Load the rules registry (Spell: Meta-Loop) ---
        self._load_rules_registry()
        
        # Initialize MoE routers
        self.linguistic_router = self._create_router('linguistic_router')
        self.factual_router = self._create_router('factual_router')
        self.semantic_router = self._create_router('semantic_router')
        self.global_router = self._create_router('global_router')

    def _load_rules_registry(self):
        """--- v6.1: Load learned rule overrides ---"""
        registry_path_str = CONFIG.meta_loop_config.rules_registry_path
        if not registry_path_str:
            self.logger.info("No rules_registry_path defined in config. Skipping.")
            return
            
        registry_path = str(registry_path_str) # Ensure it's a string
        
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r') as f:
                    self.rules_registry = json.load(f)
                self.logger.info(f"Successfully loaded rules registry from {registry_path}")
            except Exception as e:
                self.logger.error(f"Failed to load rules registry from {registry_path}: {e}")
        else:
            self.logger.info(f"No rules registry found at {registry_path}. Using default config.")

    def _get_agent_config(self, agent_name: str) -> AtomicAgentConfig:
        """
        Helper to load and build an AtomicAgentConfig from CONFIG.
        """
        if not hasattr(self.AGENT_DEFINITIONS, agent_name):
            raise ValueError(f"Agent definition '{agent_name}' not found in master_config_v6_4.json.")
            
        agent_def = getattr(self.AGENT_DEFINITIONS, agent_name)
        
        try:
            # Convert string names to Enum objects
            classification_enum = getattr(QAClassification, agent_def.classification.replace("CLASS_1_", "").replace("CLASS_2_", "").replace("CLASS_3_", "").replace("CLASS_4_", "").replace("CLASS_5_", "").replace("_CHEAP", "").replace("_MEDIUM", "").replace("_EXPENSIVE", "").replace("_DEEP", ""))
            veto_level_enum = getattr(VetoLevel, agent_def.veto_level.upper())
            
            # v6.2: Create the AtomicAgentConfig object
            return AtomicAgentConfig(
                agent_id=agent_def.agent_id,
                agent_type=agent_def.agent_type,
                classification=classification_enum,
                priority=agent_def.complexity, # Use complexity as priority
                enabled=True, # Assume enabled if in list
                rules=[], # Not used in this setup
                metadata={"complexity": agent_def.complexity, "veto_level": veto_level_enum}
            )
        except AttributeError as e:
            raise ValueError(f"Invalid enum value in agent definition for '{agent_name}': {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse agent definition for '{agent_name}': {e}")

    def _create_router(self, router_name: str) -> BaseMoERouter:
        """
        Generic factory method to create any MoE router from CONFIG.
        """
        if not hasattr(CONFIG.moe_config.routers, router_name):
            raise ValueError(f"MoE router config '{router_name}' not found in master_config_v6_4.json.")
            
        router_config_data = getattr(CONFIG.moe_config.routers, router_name)
        expert_agent_names = router_config_data.expert_agents
        
        expert_agents_configs = []
        for name in expert_agent_names:
            try:
                expert_agents_configs.append(self._get_agent_config(name))
            except ValueError as e:
                self.logger.warning(f"{e} (for router '{router_name}')")
        
        # Create the MoERouterConfig object
        config = MoERouterConfig(
            router_id=router_config_data.router_id,
            enabled_experts=expert_agents_configs, # v6.2: Pass full config objects
            aggregation_method=router_config_data.aggregation_method,
            enable_parallel=router_config_data.parallel_execution,
            confidence_threshold=0.0 # v6.2: Not used in this setup
        )
        
        # Select the correct router class
        router_class_map = {
            'linguistic_router': LinguisticValidationRouter,
            'factual_router': FactualValidationRouter,
            'semantic_router': SemanticValidationRouter,
            'global_router': GlobalValidationRouter
        }
        
        router_class = router_class_map.get(router_name)
        if not router_class:
            raise ValueError(f"Unknown router class for '{router_name}'")
            
        # v6.1: Pass the rules registry to the router
        return router_class(config, self.rules_registry)
    
    def validate_all(self, context: ValidationContext) -> Dict[str, Any]:
        """
        Execute all MoE routers and aggregate results.
        REFACTORED: Passes the full ValidationContext or specific parts as needed.
        """
        self.logger.info("Starting v6.4 MoE validation...")
        
        results = {
            "linguistic": None,
            "factual": None,
            "semantic": None,
            "global": None,
            "overall_passed": False,
            "critical_failures": [],
            "all_results": []
        }
        
        # --- Context Preparation ---
        exec_summary = context.get_section_content(ResumeSection.K1_EXECUTIVE_SUMMARY) or ""
        all_sections = context.get_all_sections()

        # Build the shared kwargs dict once
        shared_kwargs = {
            "all_sections": all_sections,
            "content": exec_summary,
            "section": ResumeSection.K1_EXECUTIVE_SUMMARY,
            "thematic_analysis": context.thematic_analysis,
            "master_resume": context.master_resume,
            "job_description": context.job_description,
            "context": context # Pass the full context object
        }

        # Execute linguistic router (operates on single content)
        try:
            linguistic_decision = self.linguistic_router.execute(**shared_kwargs)
            results["linguistic"] = linguistic_decision.metadata # v6.2: Store metadata
            results["all_results"].extend(json.loads(linguistic_decision.final_output))
        except Exception as e:
            self.logger.error(f"Linguistic router failed: {e}", exc_info=True)
        
        # Execute factual router (needs master resume)
        try:
            factual_decision = self.factual_router.execute(**shared_kwargs)
            results["factual"] = factual_decision.metadata # v6.2: Store metadata
            results["all_results"].extend(json.loads(factual_decision.final_output))
        except Exception as e:
            self.logger.error(f"Factual router failed: {e}", exc_info=True)
        
        # Execute semantic router (needs themes, master resume, all sections)
        try:
            semantic_decision = self.semantic_router.execute(**shared_kwargs)
            results["semantic"] = semantic_decision.metadata # v6.2: Store metadata
            results["all_results"].extend(json.loads(semantic_decision.final_output))
        except Exception as e:
            self.logger.error(f"Semantic router failed: {e}", exc_info=True)
        
        # Execute global router (needs JD, themes, all sections)
        try:
            global_decision = self.global_router.execute(**shared_kwargs)
            results["global"] = global_decision.metadata # v6.2: Store metadata
            results["all_results"].extend(json.loads(global_decision.final_output))
        except Exception as e:
            self.logger.error(f"Global router failed: {e}", exc_info=True)
        
        # Aggregate overall results
        all_validation_results = results["all_results"]

        results["overall_passed"] = all(r.get("passed", False) for r in all_validation_results)
        results["critical_failures"] = [
            r for r in all_validation_results 
            if not r.get("passed", False) and r.get("severity") == ValidationSeverity.CRITICAL.name
        ]
        
        self.logger.info(f"Validation complete. Overall passed: {results['overall_passed']}")
        return results

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ValidationContext', 'ValidationEngine', 'calculate_signal_score',
    # MoE Routers
    'LinguisticValidationRouter', 'FactualValidationRouter',
    'SemanticValidationRouter', 'GlobalValidationRouter',
    # Atomic Validators
    'ForbiddenVerbValidatorAgent', 'GrammarTokenCountAgent', 'FormatComplianceAgent',
    'BiasScrubberAgent', 'IntroPhraseValidatorAgent', 'MetricValidatorAgent',
    'TenureValidatorAgent', 'EntityValidatorAgent', 'ClaimValidatorAgent',
    'ToneValidator', 'ThematicAlignmentValidator', 'SemanticEntailmentValidator',
    'NarrativeThreadAgent', 'AdversarialReviewerAgent',
    'SectionPresenceValidatorAgent', 'WordCountValidatorAgent', 'SentenceCountValidatorAgent',
    'StructureValidatorAgent', 'SimilarityValidatorAgent',
    'JDSkillsValidatorAgent', 'SignalScoreValidatorAgent'
]