"""
L5 Agentic Core - L1 Planning Layer - Signal Extractors
Implements L1 Cognitive Planning Layer for signal extraction and processing
"""

from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractionMethod(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    REGEX = "regex"
    PATTERN_MATCH = "pattern_match"
    SEMANTIC = "semantic"
    STRUCTURED = "structured"
    CUSTOM = "custom"

class ExtractionStatus(Enum):
    """L5 Extraction status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    BLOCKED = "blocked"

@dataclass
class ExtractionRule:
    """L5 Extraction rule structure"""
    rule_id: str
    method: ExtractionMethod
    pattern: str
    target_field: str
    priority: int = 1
    description: str = ""
    safety_critical: bool = False

@dataclass
class ExtractionResult:
    """L5 Extraction result structure"""
    rule_id: str
    status: ExtractionStatus
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    error_message: str = ""
    timestamp: str = ""

@dataclass
class SignalExtraction:
    """L5 Signal extraction structure with full type safety"""
    extraction_id: str
    source_data: str
    extraction_results: List[ExtractionResult] = field(default_factory=list)
    combined_signals: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

class SignalExtractor(ABC):
    """L5 Abstract base - ensures L1 pure planning behavior"""
    
    @abstractmethod
    def extract_signals(self, source_data: str, rules: List[ExtractionRule]) -> SignalExtraction:
        """Extract signals using L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class SignalExtractorsImpl(SignalExtractor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure signal extraction with no side effects
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.extraction_rules: Dict[str, ExtractionRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default extraction rules"""
        default_rules = [
            ExtractionRule(
                rule_id="extract_urls",
                method=ExtractionMethod.REGEX,
                pattern=r'https?://[^\s<>"{}|\\^`\[\]]+',
                target_field="urls",
                priority=1,
                description="Extract HTTP/HTTPS URLs",
                safety_critical=False
            ),
            ExtractionRule(
                rule_id="extract_emails",
                method=ExtractionMethod.REGEX,
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                target_field="emails",
                priority=2,
                description="Extract email addresses",
                safety_critical=True
            ),
            ExtractionRule(
                rule_id="extract_phone_numbers",
                method=ExtractionMethod.REGEX,
                pattern=r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                target_field="phone_numbers",
                priority=3,
                description="Extract phone numbers",
                safety_critical=True
            ),
            ExtractionRule(
                rule_id="extract_keywords",
                method=ExtractionMethod.PATTERN_MATCH,
                pattern=r'\b(?:error|warning|critical|urgent|important)\b',
                target_field="keywords",
                priority=4,
                description="Extract important keywords",
                safety_critical=False
            ),
            ExtractionRule(
                rule_id="detect_code_injection",
                method=ExtractionMethod.REGEX,
                pattern=r'<script|javascript:|eval\(|exec\(|__import__',
                target_field="security_risks",
                priority=1,
                description="Detect potential code injection",
                safety_critical=True
            )
        ]
        
        for rule in default_rules:
            self.extraction_rules[rule.rule_id] = rule
    
    def add_extraction_rule(self, rule: ExtractionRule) -> None:
        """Add a new extraction rule"""
        self.extraction_rules[rule.rule_id] = rule
        self.logger.info(f"Added extraction rule: {rule.rule_id}")
    
    def extract_signals(self, source_data: str, rules: List[ExtractionRule]) -> SignalExtraction:
        """Extract signals following L5 architecture principles"""
        self.logger.info(f"Extracting signals from data of length: {len(source_data)}")
        
        # L5 Input validation
        self._validate_input(source_data)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(source_data):
            raise SecurityError("Source data failed L5 safety validation")
        
        # Use provided rules or default ones
        rules_to_apply = rules or list(self.extraction_rules.values())
        
        # Sort rules by priority
        rules_to_apply.sort(key=lambda r: r.priority)
        
        extraction_results = []
        combined_signals = {}
        
        for rule in rules_to_apply:
            result = self._apply_extraction_rule(source_data, rule)
            extraction_results.append(result)
            
            # Combine extracted data
            if result.status == ExtractionStatus.SUCCESS and result.extracted_data:
                field = rule.target_field
                if field not in combined_signals:
                    combined_signals[field] = []
                combined_signals[field].extend(result.extracted_data.get(field, []))
            
            # Fail immediately on safety critical failures
            if rule.safety_critical and result.status == ExtractionStatus.FAILED:
                self.logger.error(f"Safety critical extraction failed: {rule.rule_id}")
                raise SecurityError(f"Safety extraction failed: {result.error_message}")
        
        # Create extraction result
        extraction = SignalExtraction(
            extraction_id=self._generate_extraction_id(),
            source_data=source_data[:1000],  # Store truncated source for safety
            extraction_results=extraction_results,
            combined_signals=combined_signals,
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
        
        self.logger.info(f"Signal extraction completed: {len(extraction_results)} rules applied")
        return extraction
    
    def _apply_extraction_rule(self, source_data: str, rule: ExtractionRule) -> ExtractionResult:
        """Apply a single extraction rule"""
        try:
            self.logger.debug(f"Applying rule: {rule.rule_id}")
            
            if rule.method == ExtractionMethod.REGEX:
                extracted_data = self._extract_regex(source_data, rule.pattern, rule.target_field)
            elif rule.method == ExtractionMethod.PATTERN_MATCH:
                extracted_data = self._extract_pattern_match(source_data, rule.pattern, rule.target_field)
            else:
                return ExtractionResult(
                    rule_id=rule.rule_id,
                    status=ExtractionStatus.FAILED,
                    error_message=f"Unsupported extraction method: {rule.method}",
                    timestamp=self._get_timestamp()
                )
            
            return ExtractionResult(
                rule_id=rule.rule_id,
                status=ExtractionStatus.SUCCESS,
                extracted_data=extracted_data,
                confidence=0.8,  # Default confidence
                timestamp=self._get_timestamp()
            )
            
        except Exception as e:
            self.logger.error(f"Error applying rule {rule.rule_id}: {e}")
            return ExtractionResult(
                rule_id=rule.rule_id,
                status=ExtractionStatus.FAILED,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def _extract_regex(self, source_data: str, pattern: str, target_field: str) -> Dict[str, Any]:
        """Extract data using regex pattern"""
        matches = re.findall(pattern, source_data, re.IGNORECASE)
        return {target_field: matches}
    
    def _extract_pattern_match(self, source_data: str, pattern: str, target_field: str) -> Dict[str, Any]:
        """Extract data using pattern matching"""
        matches = re.findall(pattern, source_data, re.IGNORECASE)
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = [x for x in matches if not (x in seen or seen.add(x))]
        return {target_field: unique_matches}
    
    def validate_safety(self, data: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for extremely dangerous patterns first
            critical_patterns = ["<script", "javascript:", "eval(", "exec(", "__import__"]
            data_lower = data.lower()
            for pattern in critical_patterns:
                if pattern in data_lower:
                    self.logger.error(f"Critical security pattern detected: {pattern}")
                    return False
            
            # Check data size
            if len(data) > 1000000:  # 1MB limit
                self.logger.error("Source data exceeds size limit")
                return False
            
            # Check for potential buffer overflow patterns
            if len(data) > 100000 and data.count('\0') > 10:
                self.logger.error("Suspicious null byte pattern detected")
                return False
            
            self.logger.info("Source data passed L5 safety validation")
            return True
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, source_data: str) -> None:
        """L5 Input validation"""
        if not isinstance(source_data, str):
            raise ValueError("Source data must be a string")
        
        if not source_data.strip():
            raise ValueError("Source data cannot be empty")
    
    def _generate_extraction_id(self) -> str:
        """Generate unique extraction ID"""
        import uuid
        return f"extract_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class SignalExtractorsInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, extractor: SignalExtractor):
        self._extractor = extractor
    
    def extract_from_text(self, source_data: str, rules: Optional[List[ExtractionRule]] = None) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            extraction = self._extractor.extract_signals(source_data, rules or [])
            return {
                "success": True,
                "extraction_id": extraction.extraction_id,
                "signals_found": len(extraction.combined_signals),
                "combined_signals": extraction.combined_signals,
                "safety_validated": extraction.safety_validated,
                "timestamp": extraction.timestamp
            }
        except Exception as e:
            self.logger.error(f"Signal extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class SignalExtractorsFactory:
    """L5 Factory for creating signal extractor instances"""
    
    @staticmethod
    def create_extractor() -> SignalExtractor:
        return SignalExtractorsImpl()
    
    @staticmethod
    def create_interface() -> SignalExtractorsInterface:
        extractor = SignalExtractorsFactory.create_extractor()
        return SignalExtractorsInterface(extractor)

# L5 Export for module usage
__all__ = [
    "ExtractionMethod",
    "ExtractionStatus",
    "ExtractionRule",
    "ExtractionResult",
    "SignalExtraction",
    "SignalExtractor",
    "SignalExtractorsImpl",
    "SignalExtractorsInterface",
    "SignalExtractorsFactory",
    "SecurityError"
]
