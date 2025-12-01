"""
L5 Agentic Core - L2 Execution Layer - Text Parser
Implements L2 Pure Execution Layer for safe text parsing operations
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
import json

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseMode(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    TOKENIZE = "tokenize"
    SENTENCE_SPLIT = "sentence_split"
    PARAGRAPH_SPLIT = "paragraph_split"
    EXTRACT_PATTERNS = "extract_patterns"
    CLEAN_TEXT = "clean_text"
    NORMALIZE = "normalize"

class ParseStatus(Enum):
    """L5 Parse status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_INPUT = "invalid_input"
    PATTERN_ERROR = "pattern_error"
    TOO_LARGE = "too_large"

@dataclass
class ParseConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_input_length: int = 100000  # 100KB
    max_tokens: int = 10000
    max_line_length: int = 1000
    allowed_patterns: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=lambda: ["<script", "javascript:", "eval("])
    require_safety: bool = True
    safety_level: str = "strict"

@dataclass
class Token:
    """L5 Token structure with full type safety"""
    text: str
    position: int
    length: int
    token_type: str = "word"
    safety_validated: bool = False

@dataclass
class ParseResult:
    """L5 Parse result structure"""
    parse_mode: ParseMode
    original_text: str = ""
    tokens: List[Token] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class ParseResponse:
    """L5 Parse response structure"""
    parse_id: str
    status: ParseStatus
    result: Optional[ParseResult] = None
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class TextParser(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def parse(self, text: str, mode: ParseMode, constraints: ParseConstraints) -> ParseResponse:
        """Parse text with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, text: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class TextParserImpl(TextParser):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure text parsing execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ParseConstraints] = None):
        self.constraints = constraints or ParseConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse(self, text: str, mode: ParseMode, constraints: Optional[ParseConstraints] = None) -> ParseResponse:
        """Parse text following L5 architecture principles"""
        parse_constraints = constraints or self.constraints
        parse_id = self._generate_parse_id()
        
        self.logger.info(f"Parsing text with mode: {mode.value}")
        
        # L5 Input validation
        self._validate_input(text, mode)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(text):
            raise SecurityError("Text failed L5 safety validation")
        
        try:
            # Check input size
            if len(text) > parse_constraints.max_input_length:
                return ParseResponse(
                    parse_id=parse_id,
                    status=ParseStatus.TOO_LARGE,
                    error_message=f"Text too large: {len(text)} > {parse_constraints.max_input_length}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Parse based on mode
            if mode == ParseMode.TOKENIZE:
                result = self._tokenize(text, parse_constraints)
            elif mode == ParseMode.SENTENCE_SPLIT:
                result = self._split_sentences(text, parse_constraints)
            elif mode == ParseMode.PARAGRAPH_SPLIT:
                result = self._split_paragraphs(text, parse_constraints)
            elif mode == ParseMode.EXTRACT_PATTERNS:
                result = self._extract_patterns(text, parse_constraints)
            elif mode == ParseMode.CLEAN_TEXT:
                result = self._clean_text(text, parse_constraints)
            elif mode == ParseMode.NORMALIZE:
                result = self._normalize_text(text, parse_constraints)
            else:
                raise ValueError(f"Unsupported parse mode: {mode}")
            
            # Create parse response
            response = ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.SUCCESS,
                result=result,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Text parsing completed: {mode.value}")
            return response
            
        except Exception as e:
            self.logger.error(f"Text parsing error: {e}")
            return ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _tokenize(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Tokenize text into words and punctuation"""
        tokens = []
        position = 0
        
        # Use regex to find tokens
        token_pattern = r'\b\w+\b|[^\w\s]'
        matches = list(re.finditer(token_pattern, text))
        
        for match in matches:
            token_text = match.group()
            
            # Skip empty tokens
            if not token_text.strip():
                continue
            
            # Validate token safety
            if not self._validate_token_safety(token_text, constraints):
                continue
            
            token = Token(
                text=token_text,
                position=match.start(),
                length=len(token_text),
                token_type=self._get_token_type(token_text),
                safety_validated=True
            )
            tokens.append(token)
        
        # Limit token count
        tokens = tokens[:constraints.max_tokens]
        
        return ParseResult(
            parse_mode=ParseMode.TOKENIZE,
            original_text=text,
            tokens=tokens,
            metadata={
                "token_count": len(tokens),
                "character_count": len(text),
                "word_count": len([t for t in tokens if t.token_type == "word"])
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _split_sentences(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Split text into sentences"""
        # Simple sentence splitting
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text.strip())
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            cleaned = sentence.strip()
            if cleaned and len(cleaned) > 5:  # Filter very short fragments
                # Validate sentence safety
                if self._validate_text_safety(cleaned, constraints):
                    cleaned_sentences.append(cleaned)
        
        return ParseResult(
            parse_mode=ParseMode.SENTENCE_SPLIT,
            original_text=text,
            sentences=cleaned_sentences,
            metadata={
                "sentence_count": len(cleaned_sentences),
                "average_sentence_length": sum(len(s) for s in cleaned_sentences) / len(cleaned_sentences) if cleaned_sentences else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _split_paragraphs(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Split text into paragraphs"""
        # Split by double newlines or paragraph markers
        paragraph_pattern = r'\n\s*\n|\r\n\s*\r\n'
        paragraphs = re.split(paragraph_pattern, text.strip())
        
        # Clean and filter paragraphs
        cleaned_paragraphs = []
        for paragraph in paragraphs:
            cleaned = paragraph.strip()
            if cleaned and len(cleaned) > 10:  # Filter very short fragments
                # Validate paragraph safety
                if self._validate_text_safety(cleaned, constraints):
                    cleaned_paragraphs.append(cleaned)
        
        return ParseResult(
            parse_mode=ParseMode.PARAGRAPH_SPLIT,
            original_text=text,
            paragraphs=cleaned_paragraphs,
            metadata={
                "paragraph_count": len(cleaned_paragraphs),
                "average_paragraph_length": sum(len(p) for p in cleaned_paragraphs) / len(cleaned_paragraphs) if cleaned_paragraphs else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _extract_patterns(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Extract patterns from text"""
        patterns = []
        
        # Default patterns
        default_patterns = {
            "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "urls": r'https?://[^\s<>"{}|\\^`[\]]+',
            "phone_numbers": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            "dates": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            "numbers": r'\b\d+(?:\.\d+)?\b'
        }
        
        # Use allowed patterns if specified
        patterns_to_use = default_patterns
        if constraints.allowed_patterns:
            patterns_to_use = {k: v for k, v in default_patterns.items() if k in constraints.allowed_patterns}
        
        # Extract each pattern
        for pattern_name, pattern_regex in patterns_to_use.items():
            try:
                matches = re.findall(pattern_regex, text)
                if matches:
                    patterns.append({
                        "pattern_type": pattern_name,
                        "matches": matches,
                        "count": len(matches)
                    })
            except re.error as e:
                self.logger.error(f"Pattern error for {pattern_name}: {e}")
        
        return ParseResult(
            parse_mode=ParseMode.EXTRACT_PATTERNS,
            original_text=text,
            patterns=patterns,
            metadata={
                "pattern_types": len(patterns),
                "total_matches": sum(p["count"] for p in patterns)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _clean_text(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Clean text by removing unwanted characters"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove non-printable characters except newlines
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
        
        # Remove blocked patterns
        for pattern in constraints.blocked_patterns:
            cleaned = re.sub(re.escape(pattern), '', cleaned, flags=re.IGNORECASE)
        
        # Validate cleaned text safety
        if not self._validate_text_safety(cleaned, constraints):
            raise SecurityError("Cleaned text failed safety validation")
        
        return ParseResult(
            parse_mode=ParseMode.CLEAN_TEXT,
            original_text=text,
            metadata={
                "original_length": len(text),
                "cleaned_length": len(cleaned),
                "characters_removed": len(text) - len(cleaned)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _normalize_text(self, text: str, constraints: ParseConstraints) -> ParseResult:
        """Normalize text (case, accents, etc.)"""
        # Basic normalization
        normalized = text.strip()
        
        # Normalize case (to lowercase for consistency)
        normalized = normalized.lower()
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove special characters (keep letters, numbers, and basic punctuation)
        normalized = re.sub(r'[^\w\s.,!?;:()-]', '', normalized)
        
        # Validate normalized text safety
        if not self._validate_text_safety(normalized, constraints):
            raise SecurityError("Normalized text failed safety validation")
        
        return ParseResult(
            parse_mode=ParseMode.NORMALIZE,
            original_text=text,
            metadata={
                "original_length": len(text),
                "normalized_length": len(normalized),
                "case_normalized": True,
                "whitespace_normalized": True
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _get_token_type(self, token: str) -> str:
        """Determine token type"""
        if re.match(r'\w+', token):
            return "word"
        elif token in [".", "!", "?"]:
            return "sentence_ending"
        elif token in [",", ";", ":"]:
            return "separator"
        elif token in ["(", ")", "[", "]", "{", "}"]:
            return "bracket"
        else:
            return "punctuation"
    
    def _validate_token_safety(self, token: str, constraints: ParseConstraints) -> bool:
        """Validate individual token safety"""
        # Check for blocked patterns
        for pattern in constraints.blocked_patterns:
            if pattern in token.lower():
                return False
        
        # Check token length
        if len(token) > constraints.max_line_length:
            return False
        
        return True
    
    def _validate_text_safety(self, text: str, constraints: ParseConstraints) -> bool:
        """Validate text safety"""
        # Check for blocked patterns
        for pattern in constraints.blocked_patterns:
            if pattern in text.lower():
                return False
        
        # Check line length
        lines = text.split('\n')
        for line in lines:
            if len(line) > constraints.max_line_length:
                return False
        
        return True
    
    def validate_safety(self, text: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check text size
            if len(text) > self.constraints.max_input_length:
                self.logger.error("Text exceeds maximum size")
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            text_lower = text.lower()
            for pattern in dangerous_patterns:
                if pattern in text_lower:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check for suspicious content
            if text.count('\0') > 0:  # Null bytes
                self.logger.error("Null bytes detected in text")
                return False
            
            # Check for extremely long words
            words = text.split()
            for word in words:
                if len(word) > 1000:
                    self.logger.error("Extremely long word detected")
                    return False
            
            self.logger.info("Text passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, text: str, mode: ParseMode) -> None:
        """L5 Input validation"""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not isinstance(mode, ParseMode):
            raise ValueError("Mode must be a ParseMode enum")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
    
    def _generate_parse_id(self) -> str:
        """Generate unique parse ID"""
        import uuid
        return f"parse_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class TextParserInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, parser: TextParser):
        self._parser = parser
    
    def parse_text(self, text: str, mode: str = "tokenize", max_length: int = 100000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            parse_mode = ParseMode(mode)
            constraints = ParseConstraints(max_input_length=max_length)
            
            response = self._parser.parse(text, parse_mode, constraints)
            
            if response.result:
                return {
                    "success": response.status == ParseStatus.SUCCESS,
                    "parse_id": response.parse_id,
                    "parse_mode": response.result.parse_mode.value,
                    "tokens": [
                        {
                            "text": token.text,
                            "position": token.position,
                            "length": token.length,
                            "token_type": token.token_type,
                            "safety_validated": token.safety_validated
                        }
                        for token in response.result.tokens
                    ],
                    "sentences": response.result.sentences,
                    "paragraphs": response.result.paragraphs,
                    "patterns": response.result.patterns,
                    "metadata": response.result.metadata,
                    "safety_validated": response.result.safety_validated,
                    "timestamp": response.result.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "status": response.status.value,
                    "safety_validated": response.safety_validated
                }
        except Exception as e:
            self.logger.error(f"Text parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class TextParserFactory:
    """L5 Factory for creating text parser instances"""
    
    @staticmethod
    def create_parser(constraints: Optional[ParseConstraints] = None) -> TextParser:
        return TextParserImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ParseConstraints] = None) -> TextParserInterface:
        parser = TextParserFactory.create_parser(constraints)
        return TextParserInterface(parser)

# L5 Export for module usage
__all__ = [
    "ParseMode",
    "ParseStatus",
    "ParseConstraints",
    "Token",
    "ParseResult",
    "ParseResponse",
    "TextParser",
    "TextParserImpl",
    "TextParserInterface",
    "TextParserFactory",
    "SecurityError"
]
