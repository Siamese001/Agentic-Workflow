# File: validation.py
# Description: Validation agents, rules, and utilities for the LIC workflow.
# REFACTOR: v12.0 - Added Strategic Alignment validation and Voice Profile validation

__version__ = "12.0"

import re
import json
import os
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models_LIC import (
    ValidationSeverity, ValidationResult, GeneratedMessage, 
    ResearchContext, MessageClaim, RAGResult
)

# ============================================================================
# NEW v11.6: GLOBAL ERROR CODE REGISTRY (GAP 6.1)
# ============================================================================

class ErrorCodeRegistry:
    """Centralized error codes with remediation guidance"""
    
    CODES = {
        "LIC-E001": {
            "severity": "CRITICAL",
            "description": "Placeholder detected in generated message",
            "remediation": "Regenerate with explicit anti-placeholder constraint"
        },
        "LIC-E002": {
            "severity": "CRITICAL",
            "description": "Per-claim confidence below threshold (0.70)",
            "remediation": "Add more RAG sources or remove low-confidence claim"
        },
        "LIC-E003": {
            "severity": "CRITICAL",
            "description": "Hallucinated claim without supporting evidence",
            "remediation": "Remove claim or add supporting RAG evidence"
        },
        "LIC-E004": {
            "severity": "HIGH",
            "description": "Message too similar to previous message (>0.85)",
            "remediation": "Increase temperature or add diversity constraint"
        },
        "LIC-E005": {
            "severity": "HIGH",
            "description": "Job title not in first 50 words",
            "remediation": "Regenerate with job title positioning constraint"
        },
        "LIC-E006": {
            "severity": "HIGH",
            "description": "Company name misspelled",
            "remediation": "Use exact company name from profile"
        },
        "LIC-E007": {
            "severity": "HIGH",
            "description": "Non-ASCII characters detected",
            "remediation": "Replace Unicode with ASCII equivalents"
        },
        "LIC-E008": {
            "severity": "MEDIUM",
            "description": "Forbidden corporate verbs detected",
            "remediation": "Regenerate avoiding: spearheaded, leveraged, etc."
        },
        "LIC-E009": {
            "severity": "MEDIUM",
            "description": "Weak filler phrases detected",
            "remediation": "Remove: 'I hope', 'I wanted to', 'just reaching out'"
        },
        "LIC-E010": {
            "severity": "HIGH",
            "description": "Metric lacks supporting keyword context from RAG",
            "remediation": "Add RAG evidence keywords around metric or remove metric"
        },
        "LIC-E011": {
            "severity": "HIGH",
            "description": "Signal quality score below threshold (0.70)",
            "remediation": "Trigger RAG reflexion for more research"
        },
        "LIC-E012": {
            "severity": "CRITICAL",
            "description": "Circuit breaker OPEN - API unavailable",
            "remediation": "Wait for circuit breaker timeout or check API"
        },
        "LIC-E013": {
            "severity": "CRITICAL",
            "description": "Constraint pre-flight check failed",
            "remediation": "Adjust constraints or change route"
        },
        "LIC-E014": {
            "severity": "CRITICAL",
            "description": "Forbidden voice phrase detected",
            "remediation": "Regenerate avoiding sender_voice_profile forbidden phrases"
        },
        "LIC-E015": {
            "severity": "CRITICAL",
            "description": "Strategic alignment failure - no keyword overlap with strategic brief",
            "remediation": "Trigger S6->S2 meta-loop to re-research strategic brief alignment"
        }
    }
    
    @classmethod
    def get_error(cls, code: str) -> Dict[str, str]:
        return cls.CODES.get(code, {"severity": "UNKNOWN", "description": "Unknown error", "remediation": "Contact support"})

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
        route: 'models.Route',
        archetype: 'models.Archetype',
        required_elements: List[str]
    ) -> Tuple[bool, str]:
        """
        Pre-flight check: can we satisfy these constraints?
        (Simplified version - full implementation would use LLM)
        """
        # This function needs access to ConfigRegistry, but to avoid circular
        # imports, we'll use hardcoded fallbacks if the import fails.
        try:
            from config_LIC import CONFIG_REGISTRY
            constraints = CONFIG_REGISTRY.get_route_constraints(route, archetype)
        except ImportError:
            constraints = {"word_target": 200, "word_range": (150, 250), "route": route}
        
        # Simple heuristic: check if number of required elements fits in word budget
        word_budget = constraints.get("word_target", constraints["word_range"][1])
        words_per_element = word_budget // (len(required_elements) + 2)  # +2 for greeting/signature
        
        # CONNECTION_REQ requires stricter checking (more constrained format)
        min_words_per_element = 8 if route.value == "CONNECTION_REQ" else 5
        
        if words_per_element < min_words_per_element:
            return False, f"Too many required elements ({len(required_elements)}) for {route.value} word budget ({word_budget})"
        
        return True, "Constraints are feasible"

# ============================================================================
# NEW v11.6: CONTENT CLEANLINESS VALIDATORS (FEATURE 3.1, 3.2, 3.3)
# ============================================================================

class ContentCleanlinessValidator:
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
    
    def validate_verbs(self, text: str) -> Tuple[bool, str]:
        """Validate forbidden verbs"""
        found = self.detect_forbidden_verbs(text)
        
        if len(found) > self.MAX_VIOLATIONS:
            return False, f"Forbidden verbs detected: {', '.join(found)}"
        
        return True, "No forbidden verbs"
    
    def validate_fillers(self, text: str) -> Tuple[bool, str]:
        """Validate filler phrases"""
        found = self.detect_fillers(text)
        
        if found:
            patterns_found = [f[1] for f in found]
            return False, f"Weak filler phrases detected: {', '.join(patterns_found)}"
        
        return True, "No filler phrases"

class ASCIIEnforcer:
    """
    Enforce ASCII-only characters
    FEATURE 3.3 from SUPREME_SPELL
    """
    
    UNICODE_REPLACEMENTS = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2026': '...',  # ellipsis
    }
    
    def clean_text(self, text: str) -> str:
        """Replace common Unicode with ASCII"""
        for unicode_char, ascii_char in self.UNICODE_REPLACEMENTS.items():
            text = text.replace(unicode_char, ascii_char)
        return text
    
    def validate(self, text: str) -> Tuple[bool, str]:
        """Check for non-ASCII characters"""
        try:
            text.encode('ascii')
            return True, "All characters are ASCII"
        except UnicodeEncodeError as e:
            problematic_char = text[e.start]
            return False, f"Non-ASCII character detected: '{problematic_char}' at position {e.start}"

# ============================================================================
# NEW v11.6: SIGNAL QUALITY SCORING (FEATURE 1.1)
# ============================================================================

class SignalQualityScorer:
    """
    Score RAG signal quality based on source quality and recency
    FEATURE 1.1 from SUPREME_SPELL
    """
    
    SOURCE_WEIGHTS = {
        "RECIPIENT_LINKEDIN_ABOUT": 1.0,
        "RECIPIENT_RECENT_POST": 0.95,
        "RECIPIENT_COMMENT": 0.85,
        "COMPANY_BLOG_ANNOUNCEMENT": 0.90,
        "COMPANY_PRESS_RELEASE": 0.85,
        "NEWS_ARTICLE": 0.75,
        "INDUSTRY_REPORT": 0.70,
        "CONFERENCE_TALK": 0.80,
        "GITHUB_ACTIVITY": 0.75,
        "TWITTER_POST": 0.60,
        "GENERIC_SEARCH": 0.40,
    }
    
    RECENCY_DECAY_DAYS = 90
    MIN_SIGNAL_THRESHOLD = 0.70
    
    def calculate_signal_score(
        self,
        rag_results: List[RAGResult],
        message_content: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate aggregate signal quality score
        
        Returns:
            (score, breakdown_dict)
        """
        if not rag_results:
            return 0.0, {"reason": "No RAG results"}
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        source_breakdown = {}
        
        for rag_result in rag_results:
            # Base weight from source type
            base_weight = self.SOURCE_WEIGHTS.get(
                rag_result.source_type,
                0.50
            )
            
            # Apply recency decay
            recency_factor = self._calculate_recency_factor(rag_result.age_days)
            
            # Apply recipient-specificity boost
            specificity_factor = 1.2 if rag_result.recipient_specific else 1.0
            
            # Final weight
            final_weight = base_weight * recency_factor * specificity_factor
            
            weighted_sum += final_weight
            total_weight += 1.0
            
            source_breakdown[rag_result.source] = {
                "base_weight": base_weight,
                "recency_factor": recency_factor,
                "specificity_factor": specificity_factor,
                "final_weight": final_weight
            }
        
        if total_weight == 0:
            return 0.0, {"reason": "No valid weights"}
        
        aggregate_score = weighted_sum / total_weight
        
        breakdown = {
            "aggregate_score": aggregate_score,
            "total_sources": len(rag_results),
            "source_breakdown": source_breakdown
        }
        
        return aggregate_score, breakdown
    
    def _calculate_recency_factor(self, age_days: int) -> float:
        """Calculate recency decay factor"""
        if age_days <= 7:
            return 1.0
        elif age_days <= 30:
            return 0.95
        elif age_days <= 90:
            return 0.85
        elif age_days <= 180:
            return 0.70
        else:
            return 0.50
    
    def validate_minimum_signal(self, score: float) -> bool:
        """Check if signal meets minimum threshold"""
        return score >= self.MIN_SIGNAL_THRESHOLD

# ============================================================================
# NEW v11.6: PER-CLAIM CONFIDENCE SCORING (FEATURE 1.2)
# ============================================================================

class ClaimConfidenceScorer:
    """
    Score individual message claims based on RAG evidence
    FEATURE 1.2 from SUPREME_SPELL / GAP 1.2
    """
    
    MIN_CLAIM_CONFIDENCE = 0.70
    
    def score_message_claims(
        self,
        message_content: str,
        rag_results: List[RAGResult]
    ) -> Tuple[List[MessageClaim], float]:
        """
        Extract claims from message and score each based on RAG support
        
        Returns:
            (claims_list, aggregate_confidence)
        """
        # Extract claims (sentences that make factual assertions)
        claims = self._extract_claims(message_content)
        
        # Build RAG keyword universe
        rag_keywords = set()
        for rag_result in rag_results:
            rag_keywords.update([kw.lower() for kw in rag_result.extracted_keywords])
        
        scored_claims = []
        total_confidence = 0.0
        
        for claim_text in claims:
            confidence, supporting_sources = self._score_claim(
                claim_text,
                rag_results,
                rag_keywords
            )
            
            scored_claims.append(MessageClaim(
                text=claim_text,
                confidence=confidence,
                supporting_sources=supporting_sources,
                source_weights=[r.source_weight for r in rag_results if r.source in supporting_sources]
            ))
            
            total_confidence += confidence
        
        aggregate_confidence = total_confidence / len(scored_claims) if scored_claims else 0.0
        
        return scored_claims, aggregate_confidence
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from message (simple sentence split)"""
        sentences = re.split(r'[.!?]+', text)
        claims = [s.strip() for s in sentences if s.strip() and len(s.split()) > 3]
        return claims
    
    def _score_claim(
        self,
        claim: str,
        rag_results: List[RAGResult],
        rag_keywords: set
    ) -> Tuple[float, List[str]]:
        """
        Score a single claim based on RAG evidence overlap
        
        Returns:
            (confidence_score, supporting_source_list)
        """
        claim_words = set(claim.lower().split())
        
        # Calculate keyword overlap
        overlap = claim_words & rag_keywords
        overlap_ratio = len(overlap) / len(claim_words) if claim_words else 0.0
        
        # Find supporting sources
        supporting_sources = []
        for rag_result in rag_results:
            rag_words = set(rag_result.text.lower().split())
            claim_rag_overlap = claim_words & rag_words
            if len(claim_rag_overlap) >= 2:  # At least 2 words in common
                supporting_sources.append(rag_result.source)
        
        # Base confidence from overlap
        base_confidence = min(1.0, overlap_ratio * 1.5)
        
        # Boost if we have supporting sources
        if supporting_sources:
            source_boost = min(0.3, len(supporting_sources) * 0.1)
            confidence = min(1.0, base_confidence + source_boost)
        else:
            confidence = base_confidence * 0.5  # Penalize if no sources
        
        return confidence, supporting_sources
    
    def validate_claims(
        self,
        claims: List[MessageClaim],
        aggregate_confidence: float
    ) -> Tuple[bool, str]:
        """Validate all claims meet minimum confidence"""
        low_confidence_claims = [
            c for c in claims 
            if c.confidence < self.MIN_CLAIM_CONFIDENCE
        ]
        
        if low_confidence_claims:
            claim_summaries = [f"'{c.text[:50]}...' ({c.confidence:.2f})" for c in low_confidence_claims]
            return False, f"Low confidence claims: {'; '.join(claim_summaries)}"
        
        if aggregate_confidence < self.MIN_CLAIM_CONFIDENCE:
            return False, f"Aggregate confidence {aggregate_confidence:.2f} below threshold {self.MIN_CLAIM_CONFIDENCE}"
        
        return True, "All claims validated"

# ============================================================================
# LIVE v11.10: MESSAGE DIVERSITY VALIDATOR WITH PERSISTENT LEDGER
# ============================================================================

class MessageDiversityValidator:
    """
    Message diversity validation with persistent ledger
    FEATURE 1.3 from SUPREME_SPELL
    **LIVE IMPLEMENTATION**: Reads/writes message_ledger.json
    """
    
    SIMILARITY_THRESHOLD = 0.85
    LEDGER_FILE = "message_ledger.json"
    
    def __init__(self):
        self.session_history: List[str] = []
        self.vectorizer = TfidfVectorizer()
        self.ledger_path = Path(self.LEDGER_FILE)
        self.persistent_history: List[Dict[str, Any]] = []
        
        # Load persistent ledger on init
        self._load_ledger()
    
    def _load_ledger(self):
        """Load message ledger from disk"""
        if self.ledger_path.exists():
            try:
                with open(self.ledger_path, 'r') as f:
                    data = json.load(f)
                    self.persistent_history = data.get("messages", [])
                    print(f"[MessageDiversityValidator] Loaded {len(self.persistent_history)} messages from ledger")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[MessageDiversityValidator] Warning: Could not load ledger: {e}")
                self.persistent_history = []
        else:
            print(f"[MessageDiversityValidator] No existing ledger found - starting fresh")
            self.persistent_history = []
    
    def save_to_ledger(self, message: str, mission_id: str, recipient_name: str):
        """
        Save a message to the persistent ledger
        Called by WorkflowOrchestrator after successful generation
        """
        entry = {
            "message": message,
            "mission_id": mission_id,
            "recipient_name": recipient_name,
            "timestamp": str(datetime.now()),
            "word_count": len(message.split())
        }
        
        self.persistent_history.append(entry)
        
        # Write to disk
        try:
            ledger_data = {
                "messages": self.persistent_history,
                "total_count": len(self.persistent_history)
            }
            with open(self.ledger_path, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            print(f"[MessageDiversityValidator] Saved message to ledger (total: {len(self.persistent_history)})")
        except IOError as e:
            print(f"[MessageDiversityValidator] ERROR: Could not save ledger: {e}")
    
    def check_diversity(self, new_message: str) -> Tuple[bool, float, List[str]]:
        """
        Check if new message is sufficiently different from:
        1. Session history (current run)
        2. Persistent ledger (all past runs)
        
        Returns:
            (is_diverse, max_similarity, similar_messages)
        """
        all_messages = self.session_history.copy()
        
        # Add messages from persistent ledger
        for entry in self.persistent_history:
            all_messages.append(entry["message"])
        
        if not all_messages:
            return True, 0.0, []
        
        # Calculate similarities
        all_messages_with_new = all_messages + [new_message]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_messages_with_new)
            new_message_vector = tfidf_matrix[-1]
            history_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(new_message_vector, history_vectors)[0]
            max_similarity = float(np.max(similarities))
            
            if max_similarity > self.SIMILARITY_THRESHOLD:
                # Find which message(s) are too similar
                similar_indices = np.where(similarities > self.SIMILARITY_THRESHOLD)[0]
                similar_messages = [all_messages[i][:100] + "..." for i in similar_indices]
                return False, max_similarity, similar_messages
            
            return True, max_similarity, []
        
        except Exception as e:
            print(f"[MessageDiversityValidator] Error calculating similarity: {e}")
            return True, 0.0, []
    
    def add_to_history(self, message: str):
        """Add message to session history"""
        self.session_history.append(message)

# ============================================================================
# LIVE v11.10: VALIDATION AGENT WITH SENDER GROUNDING
# ============================================================================

class ValidationAgent:
    """
    S6 Validation Agent - comprehensive message validation
    **LIVE IMPLEMENTATION**: Validates sender claims against grounding files
    """
    
    def __init__(self):
        self.status = "IDLE"
        self.content_validator = ContentCleanlinessValidator()
        self.ascii_enforcer = ASCIIEnforcer()
        self.signal_scorer = SignalQualityScorer()
        self.claim_scorer = ClaimConfidenceScorer()
        self.diversity_validator = MessageDiversityValidator()
        
        # Load sender grounding data
        self.sender_grounding = self._load_sender_grounding()
        
        # v12.0: Load sender voice profile
        self.sender_voice_profile = self._load_voice_profile()
    
    def _load_sender_grounding(self) -> Dict[str, List[str]]:
        """
        LIVE: Load sender grounding data from files
        Returns whitelists for: team_members, products, case_studies
        """
        grounding = {
            "team_members": [],
            "products": [],
            "case_studies": [],
            "metrics": []
        }
        
        # Load sender_knowledge_base.json
        kb_path = Path("sender_knowledge_base.json")
        if kb_path.exists():
            try:
                with open(kb_path, 'r') as f:
                    kb_data = json.load(f)
                    
                    # Extract team members
                    for member in kb_data.get("whitelisted_team_members", []):
                        if isinstance(member, dict):
                            grounding["team_members"].append(member.get("name", ""))
                        else:
                            grounding["team_members"].append(str(member))
                    
                    # Extract products
                    for product in kb_data.get("whitelisted_products", []):
                        if isinstance(product, dict):
                            grounding["products"].append(product.get("name", ""))
                        else:
                            grounding["products"].append(str(product))
                    
                    # Extract case studies
                    for case_study in kb_data.get("whitelisted_case_studies", []):
                        if isinstance(case_study, dict):
                            grounding["case_studies"].append(case_study.get("client", ""))
                        else:
                            grounding["case_studies"].append(str(case_study))
                    
                    print(f"[ValidationAgent] Loaded sender KB: {len(grounding['team_members'])} team members, "
                          f"{len(grounding['products'])} products, {len(grounding['case_studies'])} case studies")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ValidationAgent] Warning: Could not load sender_knowledge_base.json: {e}")
        
        # Load master_resume.json for metrics
        resume_path = Path("master_resume.json")
        if resume_path.exists():
            try:
                with open(resume_path, 'r') as f:
                    resume_data = json.load(f)
                    
                    # Extract metrics from bullet_pool
                    for bullet in resume_data.get("bullet_pool", []):
                        bullet_text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                        # Find metrics in bullet text
                        metrics = re.findall(r'\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand)\b', bullet_text, re.IGNORECASE)
                        grounding["metrics"].extend(metrics)
                    
                    print(f"[ValidationAgent] Loaded {len(grounding['metrics'])} metrics from master resume")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ValidationAgent] Warning: Could not load master_resume.json: {e}")
        
        return grounding
    
    def _load_voice_profile(self) -> Dict[str, Any]:
        """
        v12.0: Load sender voice profile for forbidden phrase validation
        """
        voice_path = Path("sender_voice_profile.json")
        if not voice_path.exists():
            print("[ValidationAgent] Warning: sender_voice_profile.json not found - voice validation disabled")
            return {"forbidden_phrases": []}
        
        try:
            with open(voice_path, 'r') as f:
                voice_data = json.load(f)
                forbidden = voice_data.get("forbidden_phrases", [])
                print(f"[ValidationAgent] Loaded {len(forbidden)} forbidden phrases from voice profile")
                return {"forbidden_phrases": forbidden}
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ValidationAgent] Warning: Could not load sender_voice_profile.json: {e}")
            return {"forbidden_phrases": []}
    
    def validate_message(
        self,
        message: GeneratedMessage,
        context: ResearchContext
    ) -> List[ValidationResult]:
        """
        Execute all validation rules
        Returns list of ValidationResults sorted by severity
        """
        self.status = "RUNNING"
        results = []
        
        # ========================================
        # CRITICAL SEVERITY RULES (Must Halt)
        # ========================================
        
        # v12.0 NEW: Voice Profile Validation (LIC-QA-200)
        # Must be first - these are foundational communication principles
        if self.sender_voice_profile["forbidden_phrases"]:
            message_lower = message.content.lower()
            for forbidden_phrase in self.sender_voice_profile["forbidden_phrases"]:
                if forbidden_phrase.lower() in message_lower:
                    results.append(ValidationResult(
                        passed=False,
                        severity=ValidationSeverity.HIGH,  # HIGH not CRITICAL - allow creative retry
                        rule_id="LIC-QA-200-VOICE",
                        message=f"Forbidden voice phrase detected: '{forbidden_phrase}'",
                        details=ErrorCodeRegistry.get_error("LIC-E014")
                    ))
        
        # v12.0 NEW: Strategic Alignment Validation (LIC-QA-201)
        # This is the MASTER RULE for v12.0 - ensures message aligns with strategic brief
        strategic_brief_results = [r for r in context.rag_results if r.source_type == "STRATEGIC_BRIEF"]
        if strategic_brief_results:
            # Extract all keywords from strategic brief
            brief_keywords = set()
            for result in strategic_brief_results:
                brief_keywords.update([kw.lower() for kw in result.extracted_keywords])
            
            # Extract keywords from message
            message_words = set(message.content.lower().split())
            message_keywords = {w.strip('.,!?;:') for w in message_words if len(w) > 4}
            
            # Calculate overlap
            overlap = brief_keywords & message_keywords
            
            # Require minimum 3 keyword overlap for strategic alignment
            if len(overlap) < 3:
                from models_LIC import FailureClassifier
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-201",
                    message=f"Factual failure: Message does not align with target's strategic priorities. Only {len(overlap)} keywords overlap with strategic brief (need 3+).",
                    details={
                        **ErrorCodeRegistry.get_error("LIC-E015"),
                        "failure_classifier": FailureClassifier.FACTUAL_FAILURE.value  # Triggers S6->S2 meta-loop
                    }
                ))
        
        # S5.S6_BlockPlaceholders (FEATURE 1.2)
        placeholder_patterns = [r'\[.*?\]', r'{.*?}', r'<.*?>', r'PLACEHOLDER', r'TODO', r'XXX']
        for pattern in placeholder_patterns:
            if re.search(pattern, message.content):
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-PLACEHOLDERS",
                    message=f"Placeholder detected: {pattern}",
                    details=ErrorCodeRegistry.get_error("LIC-E001")
                ))
        
        # S5.S6_BlockHallucinatedClaims (FEATURE 1.2 / GAP 1.2)
        if self.claim_scorer:
            claims, aggregate_conf = self.claim_scorer.score_message_claims(message.content, context.rag_results)
            claims_passed, claims_msg = self.claim_scorer.validate_claims(claims, aggregate_conf)
            if not claims_passed:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-106",
                    message=f"Per-claim confidence validation failed: {claims_msg}",
                    details=ErrorCodeRegistry.get_error("LIC-E002")
                ))
        
        # S5.S6_BlockMessageRepetition (FEATURE 1.3)
        is_diverse, similarity, similar_msgs = self.diversity_validator.check_diversity(message.content)
        if not is_diverse:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                rule_id="LIC-QA-MESSAGE-DIVERSITY",
                message=f"Message too similar to previous message (similarity: {similarity:.2f})",
                details=ErrorCodeRegistry.get_error("LIC-E004")
            ))
        else:
            self.diversity_validator.add_to_history(message.content)
        
        # LIVE: S5.S6_ValidateSenderClaims (GAP 1.8 / LIC-QA-105)
        team_keywords = ["my team", "our team", "we built", "we developed", "our work", "we created"]
        product_keywords = ["our product", "our platform", "our system", "our solution"]
        case_keywords = ["we helped", "client", "case study"]
        
        message_lower = message.content.lower()
        
        # Validate team claims
        has_team_claim = any(keyword in message_lower for keyword in team_keywords)
        if has_team_claim:
            if not self.sender_grounding["team_members"]:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-105-TEAM",
                    message="Message contains team claims but sender_knowledge_base.json has no team whitelist",
                    details=ErrorCodeRegistry.get_error("LIC-E003")
                ))
            else:
                # Check if specific team member names mentioned are in whitelist
                for team_member in self.sender_grounding["team_members"]:
                    if team_member.lower() in message_lower:
                        break
                # If claim is generic ("my team") without specific names, that's OK if whitelist exists
        
        # Validate product claims
        has_product_claim = any(keyword in message_lower for keyword in product_keywords)
        if has_product_claim:
            if not self.sender_grounding["products"]:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-105-PRODUCT",
                    message="Message contains product claims but sender_knowledge_base.json has no product whitelist",
                    details=ErrorCodeRegistry.get_error("LIC-E003")
                ))
        
        # Validate case study claims
        has_case_claim = any(keyword in message_lower for keyword in case_keywords)
        if has_case_claim:
            if not self.sender_grounding["case_studies"]:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="LIC-QA-105-CASE",
                    message="Message contains case study claims but sender_knowledge_base.json has no case study whitelist",
                    details=ErrorCodeRegistry.get_error("LIC-E003")
                ))
        
        # ========================================
        # HIGH SEVERITY RULES (Must Halt)
        # ========================================
        
        # S5.S6_ValidateJobTitlePlacement (GAP 1.6 / LIC-QA-075)
        if message.route.value == "INMAIL":
            first_50_words = " ".join(message.content.split()[:50]).lower()
            job_title = context.mission_context.get("job_title", "").lower()
            if job_title and job_title not in first_50_words:
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.HIGH,
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
                        severity=ValidationSeverity.HIGH,
                        rule_id="LIC-QA-049",
                        message=f"Company name '{company_rag}' not found or misspelled in message",
                        details=ErrorCodeRegistry.get_error("LIC-E006")
                    ))
        
        # S5.S6_ValidateSafeCharacters (GAP 1.10)
        ascii_passed, ascii_msg = self.ascii_enforcer.validate(message.content)
        if not ascii_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.HIGH,
                rule_id="LIC-QA-055",
                message=ascii_msg,
                details=ErrorCodeRegistry.get_error("LIC-E007")
            ))
        
        # ========================================
        # MEDIUM SEVERITY RULES (Regenerate, No Halt)
        # ========================================
        
        # S5.S6_BlockCorporateClichés (FEATURE 3.1)
        verbs_passed, verbs_msg = self.content_validator.validate_verbs(message.content)
        if not verbs_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-FORBIDDEN-VERBS",
                message=verbs_msg,
                details=ErrorCodeRegistry.get_error("LIC-E008")
            ))
        
        # S5.S6_BlockWeakLanguage (FEATURE 3.2)
        fillers_passed, fillers_msg = self.content_validator.validate_fillers(message.content)
        if not fillers_passed:
            results.append(ValidationResult(
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                rule_id="LIC-QA-WEAK-LANGUAGE",
                message=fillers_msg,
                details=ErrorCodeRegistry.get_error("LIC-E009")
            ))
        
        # S5.S6_ValidateMetricContext (GAP 1.4 / LIC-QA-043 / LIC-QA-107)
        metric_pattern = r'\b\d+%|\b\d+x\b|\b\d+\s*(million|billion|thousand)\b'
        metrics_in_message = re.findall(metric_pattern, message.content, re.IGNORECASE)
        
        if metrics_in_message:
            # Check if metrics are in whitelist from master_resume.json
            for metric in metrics_in_message:
                metric_str = str(metric)
                
                # Check if metric is in sender grounding
                metric_in_whitelist = any(metric_str in str(m) for m in self.sender_grounding["metrics"])
                
                if not metric_in_whitelist:
                    # Check RAG support as fallback
                    rag_keywords = set()
                    for rag_result in context.rag_results:
                        rag_keywords.update(rag_result.extracted_keywords)
                    
                    metric_context = self._get_context_around_metric(message.content, metric_str)
                    context_words = set(metric_context.lower().split())
                    
                    has_rag_support = bool(context_words & rag_keywords)
                    if not has_rag_support:
                        results.append(ValidationResult(
                            passed=False,
                            severity=ValidationSeverity.HIGH,
                            rule_id="LIC-QA-043",
                            message=f"Metric '{metric}' not in master_resume.json and lacks supporting keyword context from RAG",
                            details=ErrorCodeRegistry.get_error("LIC-E010")
                        ))
        
        # S5.S6_ValidateSignalQuality (FEATURE 1.1)
        if self.signal_scorer:
            signal_score, _ = self.signal_scorer.calculate_signal_score(context.rag_results, message.content)
            if not self.signal_scorer.validate_minimum_signal(signal_score):
                results.append(ValidationResult(
                    passed=False,
                    severity=ValidationSeverity.HIGH,
                    rule_id="LIC-QA-SIGNAL-QUALITY",
                    message=f"Signal quality score {signal_score:.2f} below threshold 0.70",
                    details=ErrorCodeRegistry.get_error("LIC-E011")
                ))
        
        self.status = "COMPLETED"
        return results
    
    def _get_context_around_metric(self, text: str, metric: str) -> str:
        """Extract 10 words around a metric for context validation"""
        words = text.split()
        for i, word in enumerate(words):
            if metric in word:
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