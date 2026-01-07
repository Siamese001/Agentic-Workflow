"""
ValidationAgent - Extracted for one-class-per-file pattern.

Originally from: ContentCleanlinessValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

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
