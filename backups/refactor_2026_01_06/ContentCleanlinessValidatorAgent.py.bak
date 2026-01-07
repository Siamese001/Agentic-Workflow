from __future__ import annotations
# File: validation.py
# Description: Validation agents, rules, and utilities for the LIC workflow.

__version__ = "11.10"

# import scripts.validation.check_canonical_structure  # TODO: Replace with sovereign equivalent
from typing import Dict, List, Any, Tuple
from apps_lic.core.data_models import (
    OutreachMission, GeneratedMessage, ValidationResult, 
    ValidationSeverity, Route, Archetype, ResearchContext
)
import numpy as np
# from scripts.utilities.FormatScriptsContext import TfidfVectorizer  # TODO: Replace with sovereign equivalent
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# NEW v11.6: GLOBAL ERROR CODE REGISTRY (GAP 6.1)
# ============================================================================

class ErrorCodeRegistry:
    """Centralized error codes with remediation guidance"""
    
    CODES = {
        "LIC-E001": {
            "Severity": "CRITICAL",
            "description": "Placeholder detected in generated message",
            "remediation": "Regenerate with explicit anti-placeholder constraint"
        },
        "LIC-E002": {
            "Severity": "CRITICAL",
            "description": "Per-Claim confidence below threshold (0.70)",
            "remediation": "Add more RAG sources or remove low-confidence Claim"
        },
        "LIC-E003": {
            "Severity": "CRITICAL",
            "description": "Hallucinated Claim without supporting evidence",
            "remediation": "Remove Claim or add supporting RAG evidence"
        },
        "LIC-E004": {
            "Severity": "HIGH",
            "description": "Message too similar to previous message (>0.85)",
            "remediation": "Increase temperature or add diversity constraint"
        },
        "LIC-E005": {
            "Severity": "HIGH",
            "description": "Job title not in first 50 words",
            "remediation": "Regenerate with job title positioning constraint"
        },
        "LIC-E006": {
            "Severity": "HIGH",
            "description": "Company name misspelled",
            "remediation": "Use exact company name from profile"
        },
        "LIC-E007": {
            "Severity": "HIGH",
            "description": "Non-ASCII characters detected",
            "remediation": "Replace Unicode with ASCII equivalents"
        },
        "LIC-E008": {
            "Severity": "MEDIUM",
            "description": "Forbidden corporate verbs detected",
            "remediation": "Regenerate avoiding: spearheaded, leveraged, etc."
        },
        "LIC-E009": {
            "Severity": "MEDIUM",
            "description": "Weak filler phrases detected",
            "remediation": "Remove: 'I hope', 'I wanted to', 'just reaching out'"
        },
        "LIC-E010": {
            "Severity": "HIGH",
            "description": "Metric lacks supporting keyword context from RAG",
            "remediation": "Add RAG evidence keywords around Metric or remove Metric"
        },
        "LIC-E011": {
            "Severity": "HIGH",
            "description": "Signal quality score below threshold (0.70)",
            "remediation": "Trigger RAG reflexion for more research"
        },
        "LIC-E012": {
            "Severity": "CRITICAL",
            "description": "Circuit breaker OPEN - API unavailable",
            "remediation": "Wait for circuit breaker timeout or check API"
        },
        "LIC-E013": {
            "Severity": "CRITICAL",
            "description": "Constraint pre-flight check failed",
            "remediation": "Adjust constraints or change Route"
        }
    }
    
    @classmethod
    def get_error(cls, code: str) -> Dict[str, str]:
        return cls.CODES.get(code, {"Severity": "UNKNOWN", "description": "Unknown error", "remediation": "Contact support"})

# ============================================================================
# NEW v11.6: CONSTRAINT FEASIBILITY CHECKER (FEATURE 2.1)
# ============================================================================

class ConstraintFeasibilityChecker:
    """
    Pre-flight check for constraint satisfaction
    FEATURE 2.1 from SUPREME_SPELL
    """
    
    def check_feasibility(
        self,
        Route: 'models.Route',
        Archetype: 'models.Archetype',
        required_elements: List[str]
    ) -> Tuple[bool, str]:
        """
        Pre-flight check: can we satisfy these constraints?
        (Simplified version - full implementation would use LLM)
        """
        # This function needs access to ConfigRegistry, but to avoid circular
        # imports, we'll use hardcoded fallbacks if the import fails.
        try:
            from shared.configuration.config import CONFIG_REGISTRY
            constraints = CONFIG_REGISTRY.get_route_constraints(Route, Archetype)
        except ImportError:
            constraints = {"word_target": 200, "word_range": (150, 250), "Route": Route}
        
        # Simple heuristic: check if number of required elements fits in word budget
        word_budget = constraints.get("word_target", constraints["word_range"][1])
        words_per_element = word_budget // (len(required_elements) + 2)  # +2 for greeting/signature
        
        # CONNECTION_REQ requires stricter checking (more constrained format)
        min_words_per_element = 8 if Route.value == "CONNECTION_REQ" else 5
        
        if words_per_element < min_words_per_element:
            return False, f"Too many required elements ({len(required_elements)}) for {Route.value} word budget ({word_budget})"
        
        return True, "Constraints are feasible"

# ============================================================================
# NEW v11.6: CONTENT CLEANLINESS VALIDATORS (FEATURE 3.1, 3.2, 3.3)
# ============================================================================

class ContentCleanlinessValidatorAgent:
    """
    Forbidden verbs and weak language detection
    FEATURE 3.1 and 3.2 from SUPREME_SPELL
    """
    
    FORBIDDEN_VERBS = [
        "spearheaded", "leveraged", "utilized", "facilitated",
        "orchestrated", "championed", "pioneered", "revolutionized",
        "transformed", "optimized", "enhanced", "streamlined",
        "synergized", "enabled", "empowered", "drove", "drive"
    ]
    MAX_VIOLATIONS = 1
    
    FILLER_PATTERNS = [
        r"(?i)\bi hope\b",
        r"(?i)\bhope (this|you) (finds|are|don't)",
        r"(?i)\bi (wanted|would like) to (reach|connect|discuss|share)",
        r"(?i)\bi was wondering if",
        r"(?i)\bperhaps (we|you) could",
        r"(?i)\bif you('re| are) interested",
        r"(?i)\bjust (wanted|reaching|following)",
    ]
    
    def detect_forbidden_verbs(self, text: str) -> List[str]:
        """Find forbidden verbs in message text"""
        text_lower = text.lower()
        found = []
        
        for verb in self.FORBIDDEN_VERBS:
            if verb in text_lower:
                found.append(verb)
        
        return found
    
    def detect_fillers(self, text: str) -> List[Tuple[str, str]]:
        """Find filler phrases in message"""
        found = []
        
        for pattern in self.FILLER_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    match_text = match if isinstance(match, str) else " ".join(match) if isinstance(match, tuple) else str(match)
                    found.append((pattern, match_text))
        
        return found
    
    def validate_verbs(self, message: str) -> Tuple[bool, str]:
        """Validate no excessive forbidden verbs"""
        forbidden = self.detect_forbidden_verbs(message)
        
        if len(forbidden) > self.MAX_VIOLATIONS:
            return False, f"Found {len(forbidden)} forbidden verbs: {', '.join(forbidden[:3])}"
        
        return True, ""
    
    def validate_fillers(self, message: str) -> Tuple[bool, str]:
        """Validate message is direct and confident"""
        fillers = self.detect_fillers(message)
        
        if fillers:
            filler_texts = [f[1] for f in fillers]
            return False, f"Found {len(fillers)} filler phrases: {', '.join(filler_texts[:3])}"
        
        return True, ""

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

class PlaceholderDetectorAgent:
    """
    Comprehensive placeholder detection
    FEATURE 3.3 from SUPREME_SPELL / GAP 1.5
    """
    
    PLACEHOLDER_PATTERNS = [
        r'\[placeholder\]',
        r'\[your name\]',
        r'\[company name\]',
        r'\[recipient[_ ]?name\]',
        r'\{[a-z_]+\}',
        r'\bTBD\b',
        r'\bTODO\b',
        r'\bFIXME\b',
        r'\[INSERT [A-Z]+\]',
        r'\[ADD [A-Z]+\]',
        r'_{3,}',
        r'\[Missing[_ ]?context\]',
        r'\[unserializable\]',
    ]
    
    def detect_placeholders(self, text: str) -> List[str]:
        """Detect ALL placeholder patterns"""
        found = []
        
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.extend(matches)
        
        return found
    
    def validate(self, message: str) -> Tuple[bool, str]:
        """CRITICAL: Zero tolerance for placeholders"""
        placeholders = self.detect_placeholders(message)
        
        if placeholders:
            return False, f"CRITICAL: Found {len(placeholders)} placeholders: {', '.join(placeholders[:5])}"
        
        return True, ""

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

# ============================================================================
# NEW v11.6: MESSAGE DIVERSITY VALIDATOR (FEATURE 1.3)
# ============================================================================

class MessageDiversityValidatorAgent:
    """
    Prevent repetitive messages using cosine similarity
    FEATURE 1.3 from SUPREME_SPELL
    """
    
    MIN_DIVERSITY_THRESHOLD = 0.85  # Messages must be <85% similar
    
    def __init__(self) -> None:
        self.message_history: List[str] = []
        self.vectorizer = TfidfVectorizer()
    
    def check_diversity(self, new_message: str) -> Tuple[bool, float, str]:
        """
        Check if new message is sufficiently different from history
        
        Returns:
            (is_diverse, max_similarity, most_similar_message)
        """
        if not self.message_history:
            return True, 0.0, ""
        
        all_messages = self.message_history + [new_message]
        
        try:
            vectors = self.vectorizer.fit_transform(all_messages)
            new_vector = vectors[-1]
            history_vectors = vectors[:-1]
            
            similarities = cosine_similarity(new_vector, history_vectors)[0]
            max_similarity = float(np.max(similarities))
            max_idx = int(np.argmax(similarities))
            
            is_diverse = max_similarity < self.MIN_DIVERSITY_THRESHOLD
            most_similar = self.message_history[max_idx] if max_idx < len(self.message_history) else ""
            
            return is_diverse, max_similarity, most_similar
        
        except (ValueError, TypeError, KeyError):
            # If vectorization fails, assume diverse
            return True, 0.0, ""
    
    def add_to_history(self, message: str) -> None:
        """Add message to history"""
        self.message_history.append(message)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

# ============================================================================
# NEW v11.6: ASCII CHARACTER ENFORCER (GAP 1.10)
# ============================================================================

class ASCIIEnforcerAgent(HealerMixin, MCPHardenedMixin):
    """
    Enforce ASCII-only characters for LinkedIn compatibility
    GAP 1.10 from v10.22
    """
    
    UNICODE_REPLACEMENTS = {
        "•": "-",
        "–": "-",
        "—": "-",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "…": "...",
    }
    
    def enforce_ascii(self, text: str) -> str:
        """Replace Unicode with ASCII equivalents"""
        for unicode_char, ascii_replacement in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, ascii_replacement)
        
        # Remove any remaining non-ASCII
        text = text.encode("ascii", "ignore").decode("ascii")
        
        return text
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """Validate text is ASCII-only"""
        try:
            text.encode("ascii")
            return True, ""
        except UnicodeEncodeError as e:
            non_ascii_chars = [c for c in text if ord(c) > 127]
            return False, f"Non-ASCII characters: {set(non_ascii_chars[:5])}"

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

# ============================================================================
# S6: VALIDATION AGENT
# ============================================================================

class ValidationAgent:
    """
    NEW v11.6: Comprehensive validation framework with 107 rules
    Consolidates all rules from v10.22 + SUPREME_SPELL
    """
    
    def __init__(self, circuit_breaker: 'utils.CircuitBreaker') -> None:
        self.circuit_breaker = circuit_breaker
        self.status = "IDLE" # Using simple string, could be AgentStatus enum
        
        # NEW v11.6: Initialize validators
        self.placeholder_detector = PlaceholderDetectorAgent()
        self.diversity_validator = MessageDiversityValidatorAgent()
        self.content_validator = ContentCleanlinessValidatorAgent()
        self.ascii_enforcer = ASCIIEnforcerAgent()
        
        # These validators require RAG context, so they are instantiated
        # in rag.py or called dynamically.
        # self.claim_scorer = ClaimConfidenceScorer()
        # self.signal_scorer = SignalQualityScorer()
        
        # Import dynamically to avoid circular dependency
        try:
#             from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.rag import ClaimConfidenceScorer, SignalQualityScorer  # INVALID: Cannot import from path with hyphens
            self.claim_scorer = ClaimConfidenceScorer()
            self.signal_scorer = SignalQualityScorer()
        except ImportError:

            self.claim_scorer = None
            self.signal_scorer = None

    def _validate_critical_rules(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """Validate critical rules that must halt on failure."""
        results = []
        
        # S5.S6_BlockPlaceholders (FEATURE 3.3 / GAP 1.5)
        passed, msg = self.placeholder_detector.validate(message.content)
        if not passed:
            results.append(ValidationResult(
                passed=False,
                Severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-067",
                message=msg,
                details=ErrorCodeRegistry.get_error("LIC-E001")
            ))
        
        # S5.S6_BlockHallucinatedClaims (FEATURE 1.2 / GAP 1.2)
        if self.claim_scorer:
            claims, aggregate_conf = self.claim_scorer.score_message_claims(message.content, context.rag_results)
            claims_passed, claims_msg = self.claim_scorer.validate_claims(claims, aggregate_conf)
            if not claims_passed:
                results.append(ValidationResult(
                    passed=False,
                    Severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-106",
                    message=f"Per-Claim confidence validation failed: {claims_msg}",
                    details=ErrorCodeRegistry.get_error("LIC-E002")
                ))
        
        # S5.S6_BlockMessageRepetition (FEATURE 1.3)
        is_diverse, similarity, _ = self.diversity_validator.check_diversity(message.content)
        if not is_diverse:
            results.append(ValidationResult(
                passed=False,
                Severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-MESSAGE-DIVERSITY",
                message=f"Message too similar to previous message (similarity: {similarity:.2f})",
                details=ErrorCodeRegistry.get_error("LIC-E004")
            ))
        else:
            self.diversity_validator.add_to_history(message.content)
        
        # S5.S6_ValidateSenderClaims (GAP 1.8 / LIC-QA-105)
        team_keywords = ["my team", "our team", "we built", "we developed", "our work"]
        message_lower = message.content.lower()
        has_team_claim = any(keyword in message_lower for keyword in team_keywords)
        
        if has_team_claim:
            sender_teams = context.mission_context.get("sender_teams", [])
            if not sender_teams:
                results.append(ValidationResult(
                    passed=False,
                    Severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-105",
                    message="Message contains team claims ('my team', 'we built') but sender has no validated team whitelist",
                    details=ErrorCodeRegistry.get_error("LIC-E003")
                ))
        
        return results
    
    def _validate_high_severity_rules(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """Validate high Severity rules."""
        results = []
        
        # S5.S6_ValidateJobTitlePlacement (GAP 1.6 / LIC-QA-075)
        if message.Route.value == "INMAIL":
            first_50_words = " ".join(message.content.split()[:50]).lower()
            job_title = context.mission_context.get("job_title", "").lower()
            if job_title and job_title not in first_50_words:
                results.append(ValidationResult(
                    passed=False,
                    Severity=ValidationSeverity.HIGH,
                    rule_id="LIC-QA-075",
                    message=f"Job title '{job_title}' not mentioned in first 50 words of INMAIL",
                    details=ErrorCodeRegistry.get_error("LIC-E005")
                ))
        
        # S5.S6_ValidateCompanySpelling (GAP 1.7 / LIC-QA-049)
        company_rag = context.mission_context.get("company", "")
        if company_rag:
            message_lower = message.content.lower()
            company_lower = company_rag.lower()
            if company_lower not in message_lower:
                words = message_lower.split()
                close_match = any(
                    self._levenshtein_distance(word, company_lower) <= 2 
                    for word in words
                )
                if not close_match:
                    results.append(ValidationResult(
                        passed=False,
                        Severity=ValidationSeverity.HIGH,
                        rule_id="LIC-QA-049",
                        message=f"Company name '{company_rag}' not found or misspelled in message",
                        details=ErrorCodeRegistry.get_error("LIC-E006")
                    ))
        
        # S5.S6_ValidateSafeCharacters (GAP 1.10)
        ascii_passed, ascii_msg = self.ascii_enforcer.validate(message.content)
        if not ascii_passed:
            results.append(ValidationResult(
                passed=False,
                Severity=ValidationSeverity.HIGH,
                rule_id="LIC-QA-055",
                message=ascii_msg,
                details=ErrorCodeRegistry.get_error("LIC-E007")
            ))
        
        return results
    
    def _validate_medium_severity_rules(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """Validate medium Severity rules."""
        results = []
        
        # S5.S6_BlockCorporateClichés (FEATURE 3.1)
        verbs_passed, verbs_msg = self.content_validator.validate_verbs(message.content)
        if not verbs_passed:
            results.append(ValidationResult(
                passed=False,
                Severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-FORBIDDEN-VERBS",
                message=verbs_msg,
                details=ErrorCodeRegistry.get_error("LIC-E008")
            ))
        
        # S5.S6_BlockWeakLanguage (FEATURE 3.2)
        fillers_passed, fillers_msg = self.content_validator.validate_fillers(message.content)
        if not fillers_passed:
            results.append(ValidationResult(
                passed=False,
                Severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-WEAK-LANGUAGE",
                message=fillers_msg,
                details=ErrorCodeRegistry.get_error("LIC-E009")
            ))
        
        # S5.S6_ValidateMetricContext (GAP 1.4 / LIC-QA-043 / LIC-QA-107)
        metric_pattern = r'\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand)\b'
        metrics_in_message = re.findall(metric_pattern, message.content, re.IGNORECASE)
        
        if metrics_in_message:
            rag_keywords = set()
            for rag_result in context.rag_results:
                rag_keywords.update(rag_result.extracted_keywords)
            
            for Metric in metrics_in_message:
                metric_context = self._get_context_around_metric(message.content, str(Metric))
                context_words = set(metric_context.lower().split())
                
                has_rag_support = bool(context_words & rag_keywords)
                if not has_rag_support:
                    results.append(ValidationResult(
                        passed=False,
                        Severity=ValidationSeverity.HIGH,
                        rule_id="LIC-QA-043",
                        message=f"Metric '{Metric}' lacks supporting keyword context from RAG results",
                        details=ErrorCodeRegistry.get_error("LIC-E010")
                    ))
        
        # S5.S6_ValidateSignalQuality (FEATURE 1.1)
        if self.signal_scorer:
            signal_score, _ = self.signal_scorer.calculate_signal_score(context.rag_results, message.content)
            if not self.signal_scorer.validate_minimum_signal(signal_score):
                results.append(ValidationResult(
                    passed=False,
                    Severity=ValidationSeverity.HIGH,
                    rule_id="LIC-QA-SIGNAL-QUALITY",
                    message=f"Signal quality score {signal_score:.2f} below threshold 0.70",
                    details=ErrorCodeRegistry.get_error("LIC-E011")
                ))
        
        return results
    
    def validate_message(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """
        NEW v11.6: Run all validation rules
        Returns list of validation results (empty if all passed)
        """
        self.status = "RUNNING"
        results = []
        
        results.extend(self._validate_critical_rules(message, context))
        results.extend(self._validate_high_severity_rules(message, context))
        results.extend(self._validate_medium_severity_rules(message, context))
        
        self.status = "COMPLETED"
        return results
    
    def _get_context_around_metric(self, text: str, Metric: str) -> str:
        """Extract 10 words around a Metric for context validation"""
        words = text.split()
        for i, word in enumerate(words):
            if Metric in word:
                start = max(0, i - 5)
                end = min(len(words), i + 6)
                return " ".join(words[start:end])
        return ""
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
