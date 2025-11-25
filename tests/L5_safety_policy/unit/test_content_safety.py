"""
L5 Safety/Policy Layer Unit Tests - Content Safety

Tests for content safety validation and filtering without planning logic.
Focuses on harmful content detection, PII protection, and content sanitization.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import re
import time

# Mark all tests in this module as L5 safety/policy unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l5, pytest.mark.safety_policy]


class SafetyLevel(Enum):
    """Safety classification levels."""
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"


class ContentType(Enum):
    """Types of content for safety checking."""
    TEXT = "text"
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    USER_INPUT = "user_input"
    SYSTEM_OUTPUT = "system_output"


@dataclass(frozen=True)
class MockSafetyResult:
    """Mock safety validation result."""
    content_id: str
    safety_level: SafetyLevel
    risk_score: float
    detected_issues: List[str]
    filtered_content: Optional[str]
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class MockSafetyPolicy:
    """Mock safety policy for testing."""
    policy_id: str
    policy_name: str
    content_types: List[ContentType]
    rules: List[Dict[str, Any]]
    enabled: bool


class TestHarmfulContentDetection:
    """Test detection of harmful and inappropriate content."""
    
    def test_toxic_content_detection(self):
        """Test detection of toxic and harmful content."""
        
        class ToxicContentDetector:
            def __init__(self):
                self.toxic_patterns = {
                    "hate_speech": [
                        r"\b(hate|discriminat|racist|sexist|homophobic|transphobic)\b",
                        r"\b(slur|derogatory|offensive)\s+(term|word|language)\b"
                    ],
                    "violence": [
                        r"\b(kill|murder|harm|violence|threat|attack)\b",
                        r"\b(weapon|gun|knife|bomb|explosive)\b"
                    ],
                    "self_harm": [
                        r"\b(suicide|self.harm|kill myself|end my life)\b",
                        r"\b(depression|anxiety|mental health crisis)\b"
                    ],
                    "illegal_content": [
                        r"\b(illegal|fraud|scam|money laundering)\b",
                        r"\b(drug|narcotic|substance abuse)\b"
                    ]
                }
                self.risk_thresholds = {
                    "hate_speech": 0.8,
                    "violence": 0.7,
                    "self_harm": 0.9,
                    "illegal_content": 0.6
                }
            
            def analyze_content(self, content: str) -> MockSafetyResult:
                """Analyze content for toxic patterns."""
                detected_issues = []
                total_risk = 0.0
                issue_count = 0
                
                content_lower = content.lower()
                
                for category, patterns in self.toxic_patterns.items():
                    category_risk = 0.0
                    category_matches = 0
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content_lower, re.IGNORECASE)
                        category_matches += len(matches)
                        
                        # Risk based on number of matches
                        if matches:
                            category_risk += min(len(matches) * 0.2, 1.0)
                    
                    if category_risk > 0:
                        detected_issues.append(f"{category}_detected")
                        total_risk += category_risk
                        issue_count += 1
                
                # Calculate overall risk score
                overall_risk = total_risk / len(self.toxic_patterns) if self.toxic_patterns else 0.0
                
                # Determine safety level
                safety_level = self._determine_safety_level(overall_risk, detected_issues)
                
                return MockSafetyResult(
                    content_id=f"content_{int(time.time())}",
                    safety_level=safety_level,
                    risk_score=overall_risk,
                    detected_issues=detected_issues,
                    filtered_content=self._filter_content(content, detected_issues),
                    metadata={
                        "analysis_time": time.time(),
                        "categories_detected": len(detected_issues)
                    }
                )
            
            def _determine_safety_level(self, risk_score: float, issues: List[str]) -> SafetyLevel:
                """Determine safety level based on risk score and issues."""
                if risk_score >= 0.8:
                    return SafetyLevel.BLOCKED
                elif risk_score >= 0.5:
                    return SafetyLevel.WARNING
                elif any("self_harm" in issue for issue in issues):
                    return SafetyLevel.REVIEW_REQUIRED
                else:
                    return SafetyLevel.SAFE
            
            def _filter_content(self, content: str, issues: List[str]) -> Optional[str]:
                """Filter content based on detected issues."""
                if not issues:
                    return content
                
                # Simple filtering - replace problematic words
                filtered = content
                replacement_map = {
                    "hate_speech_detected": "[HATE_SPEECH_REMOVED]",
                    "violence_detected": "[VIOLENCE_REMOVED]",
                    "self_harm_detected": "[SELF_HARM_REMOVED]",
                    "illegal_content_detected": "[ILLEGAL_CONTENT_REMOVED]"
                }
                
                for issue in issues:
                    if issue in replacement_map:
                        filtered += f" {replacement_map[issue]}"
                
                return filtered
        
        # Test toxic content detection
        detector = ToxicContentDetector()
        
        # Test content samples
        test_content = [
            "This is a safe and professional resume content.",
            "I hate working with certain types of people and want to harm them.",
            "I feel depressed and want to end my life.",
            "I have experience with illegal activities and fraud.",
            "Professional developer with 5 years of experience in software engineering."
        ]
        
        detection_results = []
        for content in test_content:
            result = detector.analyze_content(content)
            detection_results.append({
                "content": content,
                "safety_level": result.safety_level,
                "risk_score": result.risk_score,
                "detected_issues": result.detected_issues
            })
        
        # Validate detection results
        assert len(detection_results) == 5
        
        # Check safe content
        safe_results = [r for r in detection_results if r["safety_level"] == SafetyLevel.SAFE]
        assert len(safe_results) == 2
        
        # Check harmful content detection
        blocked_results = [r for r in detection_results if r["safety_level"] == SafetyLevel.BLOCKED]
        assert len(blocked_results) >= 1
        
        # Check specific issue detection
        hate_speech_result = next(r for r in detection_results if "hate" in r["content"].lower())
        assert "hate_speech_detected" in hate_speech_result["detected_issues"]
        assert hate_speech_result["safety_level"] in [SafetyLevel.BLOCKED, SafetyLevel.WARNING]
        
        self_harm_result = next(r for r in detection_results if "depressed" in r["content"].lower())
        assert "self_harm_detected" in self_harm_result["detected_issues"]
        assert self_harm_result["safety_level"] == SafetyLevel.REVIEW_REQUIRED
    
    def test_bias_detection(self):
        """Test detection of biased content."""
        
        class BiasDetector:
            def __init__(self):
                self.bias_patterns = {
                    "gender_bias": [
                        r"\b(male|female|men|women)\s+(only|required|preferred)\b",
                        r"\b(sexist|gender discriminatory)\b"
                    ],
                    "age_bias": [
                        r"\b(young|old|age)\s+(only|required|preferred)\b",
                        r"\b(age discrimination|ageist)\b"
                    ],
                    "racial_bias": [
                        r"\b(white|black|asian|hispanic)\s+(only|required|preferred)\b",
                        r"\b(racial discrimination|racist)\b"
                    ],
                    "disability_bias": [
                        r"\b(disabled|handicapped)\s+(discrimination|bias)\b",
                        r"\b(ableism|disability discrimination)\b"
                    ]
                }
            
            def detect_bias(self, content: str) -> Dict[str, Any]:
                """Detect biased language in content."""
                detected_biases = []
                bias_scores = {}
                
                content_lower = content.lower()
                
                for bias_type, patterns in self.bias_patterns.items():
                    type_score = 0.0
                    matches = []
                    
                    for pattern in patterns:
                        found = re.findall(pattern, content_lower, re.IGNORECASE)
                        matches.extend(found)
                        type_score += len(found) * 0.3
                    
                    if type_score > 0:
                        detected_biases.append(bias_type)
                        bias_scores[bias_type] = min(type_score, 1.0)
                
                overall_bias_score = sum(bias_scores.values()) / len(self.bias_patterns) if self.bias_patterns else 0.0
                
                return {
                    "detected_biases": detected_biases,
                    "bias_scores": bias_scores,
                    "overall_bias_score": overall_bias_score,
                    "requires_review": len(detected_biases) > 0
                }
        
        # Test bias detection
        detector = BiasDetector()
        
        # Test content with various biases
        biased_content = [
            "Looking for male candidates only for this position.",
            "Prefer young applicants under 30 for this role.",
            "White employees preferred for management positions.",
            "No discrimination based on race, gender, or age.",
            "Qualified candidates from all backgrounds encouraged to apply."
        ]
        
        bias_results = []
        for content in biased_content:
            result = detector.detect_bias(content)
            bias_results.append({
                "content": content,
                "detected_biases": result["detected_biases"],
                "overall_bias_score": result["overall_bias_score"],
                "requires_review": result["requires_review"]
            })
        
        # Validate bias detection
        assert len(bias_results) == 5
        
        # Check gender bias detection
        gender_bias_result = next(r for r in bias_results if "male candidates only" in r["content"].lower())
        assert "gender_bias" in gender_bias_result["detected_biases"]
        assert gender_bias_result["requires_review"] is True
        
        # Check age bias detection
        age_bias_result = next(r for r in bias_results if "young applicants" in r["content"].lower())
        assert "age_bias" in age_bias_result["detected_biases"]
        
        # Check unbiased content
        unbiased_results = [r for r in bias_results if not r["requires_review"]]
        assert len(unbiased_results) == 2
    
    def test_inappropriate_language_detection(self):
        """Test detection of inappropriate or unprofessional language."""
        
        class InappropriateLanguageDetector:
            def __init__(self):
                self.inappropriate_patterns = {
                    "profanity": [
                        r"\b(damn|hell|shit|fuck|crap)\b",
                        r"\b(asshole|bastard|bitch)\b"
                    ],
                    "unprofessional": [
                        r"\b(lazy|stupid|idiotic|useless)\b",
                        r"\b(whatever|doesn't matter|who cares)\b"
                    ],
                    "discriminatory_slurs": [
                        r"\b(slur|derogatory term|offensive name)\b"
                    ]
                }
            
            def scan_content(self, content: str) -> MockSafetyResult:
                """Scan content for inappropriate language."""
                issues_found = []
                severity_score = 0.0
                
                content_lower = content.lower()
                
                for category, patterns in self.inappropriate_patterns.items():
                    category_issues = []
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content_lower, re.IGNORECASE)
                        category_issues.extend(matches)
                    
                    if category_issues:
                        issues_found.append(f"{category}_detected")
                        # Calculate severity based on category
                        if category == "discriminatory_slurs":
                            severity_score += 0.9
                        elif category == "profanity":
                            severity_score += 0.5
                        else:
                            severity_score += 0.3
                
                # Determine safety level
                if severity_score >= 0.8:
                    safety_level = SafetyLevel.BLOCKED
                elif severity_score >= 0.5:
                    safety_level = SafetyLevel.WARNING
                elif severity_score > 0:
                    safety_level = SafetyLevel.REVIEW_REQUIRED
                else:
                    safety_level = SafetyLevel.SAFE
                
                return MockSafetyResult(
                    content_id=f"inappropriate_check_{int(time.time())}",
                    safety_level=safety_level,
                    risk_score=severity_score,
                    detected_issues=issues_found,
                    filtered_content=self._clean_content(content, issues_found),
                    metadata={"severity_score": severity_score}
                )
            
            def _clean_content(self, content: str, issues: List[str]) -> str:
                """Clean inappropriate content."""
                if not issues:
                    return content
                
                # Simple cleaning - replace with placeholders
                cleaned = re.sub(r'\b(damn|hell|shit|fuck|crap|asshole|bastard|bitch)\b', '[PROFANITY]', content, flags=re.IGNORECASE)
                cleaned = re.sub(r'\b(lazy|stupid|idiotic|useless)\b', '[UNPROFESSIONAL]', cleaned, flags=re.IGNORECASE)
                
                return cleaned
        
        # Test inappropriate language detection
        detector = InappropriateLanguageDetector()
        
        test_content = [
            "Professional software engineer with excellent skills.",
            "This damn project is so stupid and useless.",
            "I am a hard-working and dedicated professional.",
            "The lazy bastard can't do anything right.",
            "Experienced developer with strong technical background."
        ]
        
        results = []
        for content in test_content:
            result = detector.scan_content(content)
            results.append({
                "content": content,
                "safety_level": result.safety_level,
                "detected_issues": result.detected_issues,
                "filtered": result.filtered_content
            })
        
        # Validate results
        assert len(results) == 5
        
        # Check safe content
        safe_results = [r for r in results if r["safety_level"] == SafetyLevel.SAFE]
        assert len(safe_results) == 3
        
        # Check inappropriate content detection
        warning_results = [r for r in results if r["safety_level"] == SafetyLevel.WARNING]
        assert len(warning_results) >= 1
        
        # Check content filtering
        profanity_result = next(r for r in results if "damn" in r["content"].lower())
        assert "[PROFANITY]" in profanity_result["filtered"]


class TestPIIProtection:
    """Test Personally Identifiable Information protection."""
    
    def test_pii_detection(self):
        """Test detection of PII in content."""
        
        class PIIDetector:
            def __init__(self):
                self.pii_patterns = {
                    "email": [
                        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                    ],
                    "phone": [
                        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                        r'\b\+?1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                    ],
                    "ssn": [
                        r'\b\d{3}-\d{2}-\d{4}\b',
                        r'\b\d{9}\b'
                    ],
                    "credit_card": [
                        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
                    ],
                    "address": [
                        r'\b\d+\s+[\w\s]+,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}\b'
                    ],
                    "name": [
                        r'\b(Mr|Mrs|Ms|Dr)\.\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'
                    ]
                }
            
            def detect_pii(self, content: str) -> Dict[str, Any]:
                """Detect PII in content."""
                detected_pii = {}
                pii_instances = []
                
                for pii_type, patterns in self.pii_patterns.items():
                    type_instances = []
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            type_instances.append({
                                "type": pii_type,
                                "value": match.group(),
                                "start": match.start(),
                                "end": match.end()
                            })
                    
                    if type_instances:
                        detected_pii[pii_type] = len(type_instances)
                        pii_instances.extend(type_instances)
                
                return {
                    "pii_detected": len(detected_pii) > 0,
                    "pii_types": list(detected_pii.keys()),
                    "pii_counts": detected_pii,
                    "total_pii_instances": len(pii_instances),
                    "pii_instances": pii_instances
                }
        
        # Test PII detection
        detector = PIIDetector()
        
        # Content with various PII types
        pii_content = [
            "Contact me at john.doe@example.com or call 555-123-4567.",
            "My SSN is 123-45-6789 and I live at 123 Main St, Anytown, NY 12345.",
            "Credit card: 4532-1234-5678-9012, email: jane.smith@company.org",
            "Professional software engineer with 10 years experience.",
            "Dr. John Smith can be reached at john.smith@university.edu"
        ]
        
        pii_results = []
        for content in pii_content:
            result = detector.detect_pii(content)
            pii_results.append({
                "content": content,
                "pii_detected": result["pii_detected"],
                "pii_types": result["pii_types"],
                "total_instances": result["total_pii_instances"]
            })
        
        # Validate PII detection
        assert len(pii_results) == 5
        
        # Check email detection
        email_results = [r for r in pii_results if "email" in r["pii_types"]]
        assert len(email_results) == 3
        
        # Check phone detection
        phone_results = [r for r in pii_results if "phone" in r["pii_types"]]
        assert len(phone_results) == 1
        
        # Check SSN detection
        ssn_results = [r for r in pii_results if "ssn" in r["pii_types"]]
        assert len(ssn_results) == 1
        
        # Check safe content (no PII)
        safe_results = [r for r in pii_results if not r["pii_detected"]]
        assert len(safe_results) == 1
    
    def test_pii_masking(self):
        """Test masking and redaction of PII."""
        
        class PIIMasker:
            def __init__(self):
                self.pii_patterns = {
                    "email": r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
                    "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
                    "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
                }
                self.mask_replacements = {
                    "email": "[EMAIL_REDACTED]",
                    "phone": "[PHONE_REDACTED]",
                    "ssn": "[SSN_REDACTED]",
                    "credit_card": "[CREDIT_CARD_REDACTED]"
                }
            
            def mask_pii(self, content: str, mask_types: List[str] = None) -> str:
                """Mask PII in content."""
                if mask_types is None:
                    mask_types = list(self.pii_patterns.keys())
                
                masked_content = content
                
                for pii_type in mask_types:
                    if pii_type in self.pii_patterns:
                        pattern = self.pii_patterns[pii_type]
                        replacement = self.mask_replacements.get(pii_type, f"[{pii_type.upper()}_REDACTED]")
                        masked_content = re.sub(pattern, replacement, masked_content)
                
                return masked_content
            
            def mask_with_preservation(self, content: str, preserve_domains: bool = True) -> str:
                """Mask PII while preserving some information."""
                masked = content
                    
                # Mask emails but preserve domain
                email_pattern = r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
                if preserve_domains:
                    masked = re.sub(email_pattern, r'[USERNAME]@\2', masked)
                else:
                    masked = re.sub(email_pattern, '[EMAIL_REDACTED]', masked)
                
                # Mask phone numbers
                phone_pattern = r'\b(\d{3})[-.]?(\d{3})[-.]?(\d{4})\b'
                masked = re.sub(phone_pattern, r'\1-XXX-\3', masked)
                
                return masked
        
        # Test PII masking
        masker = PIIMasker()
        
        test_content = "Contact John at john.doe@example.com or call 555-123-4567. SSN: 123-45-6789"
        
        # Test full masking
        fully_masked = masker.mask_pii(test_content)
        assert "[EMAIL_REDACTED]" in fully_masked
        assert "[PHONE_REDACTED]" in fully_masked
        assert "[SSN_REDACTED]" in fully_masked
        assert "john.doe" not in fully_masked
        assert "555-123-4567" not in fully_masked
        
        # Test selective masking
        email_only_masked = masker.mask_pii(test_content, ["email"])
        assert "[EMAIL_REDACTED]" in email_only_masked
        assert "555-123-4567" in email_only_masked  # Phone not masked
        
        # Test preservation masking
        preserved_masked = masker.mask_with_preservation(test_content, preserve_domains=True)
        assert "[USERNAME]@example.com" in preserved_masked
        assert "555-XXX-4567" in preserved_masked
    
    def test_pii_risk_assessment(self):
        """Test risk assessment for PII exposure."""
        
        class PIIRiskAssessor:
            def __init__(self):
                self.risk_weights = {
                    "email": 0.3,
                    "phone": 0.4,
                    "ssn": 0.9,
                    "credit_card": 0.9,
                    "address": 0.7,
                    "name": 0.2
                }
            
            def assess_pii_risk(self, pii_detection_result: Dict[str, Any]) -> Dict[str, Any]:
                """Assess risk level based on detected PII."""
                pii_types = pii_detection_result.get("pii_types", [])
                pii_counts = pii_detection_result.get("pii_counts", {})
                
                total_risk = 0.0
                high_risk_items = []
                
                for pii_type in pii_types:
                    weight = self.risk_weights.get(pii_type, 0.5)
                    count = pii_counts.get(pii_type, 1)
                    
                    # Risk increases with count but has diminishing returns
                    item_risk = weight * min(count * 0.7, 1.0)
                    total_risk += item_risk
                    
                    if weight >= 0.7:  # High-risk PII types
                        high_risk_items.append(pii_type)
                    
                    # Normalize risk score
                    max_possible_risk = sum(self.risk_weights.values())
                    normalized_risk = min(total_risk / max_possible_risk, 1.0)
                    
                    # Determine risk level
                    if normalized_risk >= 0.7:
                        risk_level = "HIGH"
                    elif normalized_risk >= 0.4:
                        risk_level = "MEDIUM"
                    elif normalized_risk > 0:
                        risk_level = "LOW"
                    else:
                        risk_level = "NONE"
                    
                    return {
                        "risk_level": risk_level,
                        "risk_score": normalized_risk,
                        "high_risk_items": high_risk_items,
                        "requires_immediate_action": len(high_risk_items) > 0
                    }
        
        # Test PII risk assessment
        assessor = PIIRiskAssessor()
        
        # Test scenarios
        test_scenarios = [
            {
                "pii_types": ["email"],
                "pii_counts": {"email": 1},
                "expected_risk": "LOW"
            },
            {
                "pii_types": ["email", "phone"],
                "pii_counts": {"email": 2, "phone": 1},
                "expected_risk": "MEDIUM"
            },
            {
                "pii_types": ["ssn", "credit_card"],
                "pii_counts": {"ssn": 1, "credit_card": 1},
                "expected_risk": "HIGH"
            },
            {
                "pii_types": [],
                "pii_counts": {},
                "expected_risk": "NONE"
            }
        ]
        
        risk_results = []
        for scenario in test_scenarios:
            risk_assessment = assessor.assess_pii_risk(scenario)
            risk_results.append({
                "scenario": scenario,
                "risk_level": risk_assessment["risk_level"],
                "risk_score": risk_assessment["risk_score"],
                "high_risk_items": risk_assessment["high_risk_items"],
                "expected_risk": scenario["expected_risk"],
                "correct": risk_assessment["risk_level"] == scenario["expected_risk"]
            })
        
        # Validate risk assessment
        assert all(result["correct"] for result in risk_results)
        
        # Check high-risk scenarios
        high_risk_results = [r for r in risk_results if r["risk_level"] == "HIGH"]
        assert len(high_risk_results) == 1
        
        high_risk_scenario = high_risk_results[0]
        assert "ssn" in high_risk_scenario["high_risk_items"]
        assert "credit_card" in high_risk_scenario["high_risk_items"]


class TestContentSanitization:
    """Test content sanitization and safe output generation."""
    
    def test_content_sanitization_pipeline(self):
        """Test complete content sanitization pipeline."""
        
        class ContentSanitizer:
            def __init__(self):
                self.sanitization_steps = [
                    "pii_detection",
                    "toxic_content_check",
                    "bias_detection",
                    "format_validation"
                ]
            
            def sanitize_content(self, content: str, content_type: ContentType) -> MockSafetyResult:
                """Run complete sanitization pipeline."""
                issues = []
                sanitized_content = content
                total_risk = 0.0
                
                # Step 1: PII detection and masking
                pii_result = self._detect_and_mask_pii(sanitized_content)
                if pii_result["pii_detected"]:
                    issues.extend([f"pii_{pii_type}" for pii_type in pii_result["pii_types"]])
                    sanitized_content = pii_result["masked_content"]
                    total_risk += 0.3
                
                # Step 2: Toxic content check
                toxic_result = self._check_toxic_content(sanitized_content)
                if toxic_result["toxic_detected"]:
                    issues.extend(toxic_result["toxic_types"])
                    total_risk += 0.5
                
                # Step 3: Bias detection
                bias_result = self._detect_bias(sanitized_content)
                if bias_result["bias_detected"]:
                    issues.append("bias_detected")
                    total_risk += 0.2
                
                # Step 4: Format validation
                format_result = self._validate_format(sanitized_content, content_type)
                if not format_result["valid"]:
                    issues.append("format_invalid")
                    total_risk += 0.1
                
                # Determine overall safety level
                safety_level = self._determine_safety_level(total_risk, issues)
                
                return MockSafetyResult(
                    content_id=f"sanitized_{int(time.time())}",
                    safety_level=safety_level,
                    risk_score=total_risk,
                    detected_issues=issues,
                    filtered_content=sanitized_content if total_risk < 0.8 else None,
                    metadata={
                        "sanitization_steps": self.sanitization_steps,
                        "content_type": content_type.value
                    }
                )
            
            def _detect_and_mask_pii(self, content: str) -> Dict[str, Any]:
                """Detect and mask PII."""
                email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                
                pii_detected = False
                pii_types = []
                masked_content = content
                
                if re.search(email_pattern, content):
                    pii_detected = True
                    pii_types.append("email")
                    masked_content = re.sub(email_pattern, "[EMAIL_REDACTED]", masked_content)
                
                if re.search(phone_pattern, content):
                    pii_detected = True
                    pii_types.append("phone")
                    masked_content = re.sub(phone_pattern, "[PHONE_REDACTED]", masked_content)
                
                return {
                    "pii_detected": pii_detected,
                    "pii_types": pii_types,
                    "masked_content": masked_content
                }
            
            def _check_toxic_content(self, content: str) -> Dict[str, Any]:
                """Check for toxic content."""
                toxic_patterns = ["hate", "kill", "violence", "threat"]
                toxic_types = []
                
                content_lower = content.lower()
                for pattern in toxic_patterns:
                    if pattern in content_lower:
                        toxic_types.append(f"toxic_{pattern}")
                
                return {
                    "toxic_detected": len(toxic_types) > 0,
                    "toxic_types": toxic_types
                }
            
            def _detect_bias(self, content: str) -> Dict[str, Any]:
                """Detect biased content."""
                bias_patterns = ["only male", "only female", "age discrimination"]
                content_lower = content.lower()
                
                bias_detected = any(pattern in content_lower for pattern in bias_patterns)
                
                return {
                    "bias_detected": bias_detected
                }
            
            def _validate_format(self, content: str, content_type: ContentType) -> Dict[str, Any]:
                """Validate content format."""
                if content_type == ContentType.EMAIL:
                    valid = "@" in content and "." in content.split("@")[-1]
                elif content_type == ContentType.PHONE:
                    valid = bool(re.search(r'\d', content))
                else:
                    valid = len(content.strip()) > 0
                
                return {
                    "valid": valid
                }
            
            def _determine_safety_level(self, risk_score: float, issues: List[str]) -> SafetyLevel:
                """Determine safety level based on risk and issues."""
                if risk_score >= 0.8:
                    return SafetyLevel.BLOCKED
                elif risk_score >= 0.5:
                    return SafetyLevel.WARNING
                elif risk_score >= 0.3:
                    return SafetyLevel.REVIEW_REQUIRED
                else:
                    return SafetyLevel.SAFE
        
        # Test sanitization pipeline
        sanitizer = ContentSanitizer()
        
        # Test content requiring sanitization
        test_content = [
            ("Contact me at john.doe@example.com or call 555-123-4567", ContentType.USER_INPUT),
            ("I hate working with lazy people", ContentType.USER_INPUT),
            ("Professional software engineer", ContentType.RESUME),
            ("Male candidates only for this position", ContentType.JOB_DESCRIPTION)
        ]
        
        sanitization_results = []
        for content, content_type in test_content:
            result = sanitizer.sanitize_content(content, content_type)
            sanitization_results.append({
                "original_content": content,
                "content_type": content_type,
                "safety_level": result.safety_level,
                "risk_score": result.risk_score,
                "detected_issues": result.detected_issues,
                "sanitized_content": result.filtered_content
            })
        
        # Validate sanitization results
        assert len(sanitization_results) == 4
        
        # Check PII masking
        pii_result = next(r for r in sanitization_results if "@" in r["original_content"])
        assert "pii_email" in pii_result["detected_issues"]
        assert "[EMAIL_REDACTED]" in pii_result["sanitized_content"]
        
        # Check toxic content detection
        toxic_result = next(r for r in sanitization_results if "hate" in r["original_content"].lower())
        assert "toxic_hate" in toxic_result["detected_issues"]
        assert toxic_result["safety_level"] in [SafetyLevel.WARNING, SafetyLevel.BLOCKED]
        
        # Check safe content
        safe_result = next(r for r in sanitization_results if r["safety_level"] == SafetyLevel.SAFE)
        assert safe_result["original_content"] == "Professional software engineer"
    
    def test_safe_content_generation(self):
        """Test generation of safe content alternatives."""
        
        class SafeContentGenerator:
            def __init__(self):
                self.unsafe_replacements = {
                    "contact_info": {
                        "email": "[Please use application messaging system]",
                        "phone": "[Please use application messaging system]",
                        "address": "[Address will be provided upon request]"
                    },
                    "inappropriate_language": {
                        "profanity": "[Professional language]",
                        "insults": "[Professional description]"
                    },
                    "discriminatory_language": {
                        "gender_bias": "[All qualified candidates]",
                        "age_bias": "[Candidates of all experience levels]",
                        "racial_bias": "[Candidates from all backgrounds]"
                    }
                }
            
            def generate_safe_alternative(self, unsafe_content: str, detected_issues: List[str]) -> str:
                """Generate safe alternative for unsafe content."""
                safe_content = unsafe_content
                
                # Replace contact information
                if any("pii_" in issue for issue in detected_issues):
                    safe_content = self._replace_contact_info(safe_content)
                
                # Replace inappropriate language
                if any("toxic" in issue for issue in detected_issues):
                    safe_content = self._replace_inappropriate_language(safe_content)
                
                # Replace discriminatory language
                if "bias_detected" in detected_issues:
                    safe_content = self._replace_discriminatory_language(safe_content)
                
                return safe_content
            
            def _replace_contact_info(self, content: str) -> str:
                """Replace contact information with safe alternatives."""
                email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                
                safe_content = re.sub(email_pattern, self.unsafe_replacements["contact_info"]["email"], content)
                safe_content = re.sub(phone_pattern, self.unsafe_replacements["contact_info"]["phone"], safe_content)
                
                return safe_content
            
            def _replace_inappropriate_language(self, content: str) -> str:
                """Replace inappropriate language with professional alternatives."""
                profanity_pattern = r'\b(damn|hell|shit|fuck|crap)\b'
                insult_pattern = r'\b(lazy|stupid|idiotic|useless)\b'
                
                safe_content = re.sub(profanity_pattern, self.unsafe_replacements["inappropriate_language"]["profanity"], content, flags=re.IGNORECASE)
                safe_content = re.sub(insult_pattern, self.unsafe_replacements["inappropriate_language"]["insults"], safe_content, flags=re.IGNORECASE)
                
                return safe_content
            
            def _replace_discriminatory_language(self, content: str) -> str:
                """Replace discriminatory language with inclusive alternatives."""
                gender_pattern = r'\b(male|female)\s+(candidates?|applicants?|only|required|preferred)\b'
                age_pattern = r'\b(young|old)\s+(candidates?|applicants?|only|required|preferred)\b'
                
                safe_content = re.sub(gender_pattern, self.unsafe_replacements["discriminatory_language"]["gender_bias"], content, flags=re.IGNORECASE)
                safe_content = re.sub(age_pattern, self.unsafe_replacements["discriminatory_language"]["age_bias"], safe_content, flags=re.IGNORECASE)
                
                return safe_content
        
        # Test safe content generation
        generator = SafeContentGenerator()
        
        # Test unsafe content and their safe alternatives
        unsafe_examples = [
            {
                "content": "Contact me at john.doe@example.com or call 555-123-4567",
                "issues": ["pii_email", "pii_phone"],
                "expected_replacement": "[Please use application messaging system]"
            },
            {
                "content": "This damn project is managed by lazy people",
                "issues": ["toxic_damn", "toxic_lazy"],
                "expected_replacement": "[Professional language]"
            },
            {
                "content": "Male candidates only preferred for this role",
                "issues": ["bias_detected"],
                "expected_replacement": "[All qualified candidates]"
            }
        ]
        
        generation_results = []
        for example in unsafe_examples:
            safe_alternative = generator.generate_safe_alternative(
                example["content"], 
                example["issues"]
            )
            
            generation_results.append({
                "original": example["content"],
                "issues": example["issues"],
                "safe_alternative": safe_alternative,
                "contains_replacement": example["expected_replacement"] in safe_alternative
            })
        
        # Validate safe content generation
        assert all(result["contains_replacement"] for result in generation_results)
        
        # Check that unsafe elements are removed
        pii_result = generation_results[0]
        assert "john.doe@example.com" not in pii_result["safe_alternative"]
        assert "555-123-4567" not in pii_result["safe_alternative"]
        
        profanity_result = generation_results[1]
        assert "damn" not in profanity_result["safe_alternative"].lower()
        assert "lazy" not in profanity_result["safe_alternative"].lower()
